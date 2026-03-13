"""Booking routes — Coach availability and session booking management.

Endpoints:
    # Coach: Availability
    GET    /bookings/slots              - List coach's availability slots
    POST   /bookings/slots              - Create a new slot
    PATCH  /bookings/slots/{id}         - Update a slot
    DELETE /bookings/slots/{id}         - Delete a slot

    # Coachee: Available times
    GET    /bookings/available/{coach_id} - Get available booking times

    # Booking CRUD
    POST   /bookings                    - Create a booking request
    GET    /bookings                    - List user's bookings
    GET    /bookings/upcoming           - Upcoming bookings
    GET    /bookings/{id}               - Booking detail
    POST   /bookings/{id}/confirm       - Coach confirms booking
    POST   /bookings/{id}/cancel        - Cancel booking
    POST   /bookings/{id}/complete      - Complete booking with notes

    # Briefing
    GET    /bookings/{id}/briefing      - Get session briefing
    POST   /bookings/{id}/briefing/regenerate - Regenerate briefing
"""

import logging
from datetime import datetime, date, time as dt_time
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from bfg_core.auth.rbac import require_role
from bfg_core.models.booking import (
    AvailabilitySlot, Booking, SessionBriefing,
    BookingStatus, BriefingStatus,
)
from bfg_core.models.user import User

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class CreateSlotRequest(BaseModel):
    day_of_week: int  # 0=Monday, 6=Sunday
    start_time: str   # "09:00"
    end_time: str     # "12:00"
    duration_minutes: int = 60
    recurrence: str = "weekly"
    notes: str | None = None


class UpdateSlotRequest(BaseModel):
    start_time: str | None = None
    end_time: str | None = None
    duration_minutes: int | None = None
    recurrence: str | None = None
    notes: str | None = None
    is_active: bool | None = None


class CreateBookingRequest(BaseModel):
    coach_id: str
    scheduled_at: str  # ISO datetime
    topic: str | None = None
    coachee_notes: str | None = None
    slot_id: str | None = None


class CompleteBookingRequest(BaseModel):
    coach_notes: str | None = None
    summary: str | None = None


class SlotResponse(BaseModel):
    id: str
    day_of_week: int
    start_time: str
    end_time: str
    duration_minutes: int
    recurrence: str
    notes: str | None
    is_active: bool
    created_at: str


class AvailableTimeResponse(BaseModel):
    date: str
    time: str
    datetime: str
    duration_minutes: int
    slot_id: str


class BookingResponse(BaseModel):
    id: str
    coach_id: str
    coachee_id: str
    coach_name: str | None = None
    coachee_name: str | None = None
    scheduled_at: str
    duration_minutes: int
    status: str
    topic: str | None
    coachee_notes: str | None
    coach_notes: str | None
    meeting_link: str | None
    completed_at: str | None
    summary: str | None
    has_briefing: bool = False
    created_at: str


class BriefingResponse(BaseModel):
    id: str
    status: str
    content: str | None
    coachee_profile_summary: str | None
    scil_highlights: dict | None
    suggested_topics: list | None
    suggested_exercises: list | None
    previous_session_notes: str | None
    training_progress_summary: str | None
    generated_at: str | None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _format_slot(slot: AvailabilitySlot) -> SlotResponse:
    return SlotResponse(
        id=str(slot.id),
        day_of_week=slot.day_of_week,
        start_time=slot.start_time.strftime("%H:%M"),
        end_time=slot.end_time.strftime("%H:%M"),
        duration_minutes=slot.session_duration_minutes,
        recurrence=slot.recurrence.value,
        notes=slot.notes,
        is_active=slot.is_active,
        created_at=slot.created_at.isoformat(),
    )


async def _format_booking(booking: Booking, db: AsyncSession) -> BookingResponse:
    coach = await db.get(User, booking.coach_id)
    coachee = await db.get(User, booking.coachee_id)

    return BookingResponse(
        id=str(booking.id),
        coach_id=str(booking.coach_id),
        coachee_id=str(booking.coachee_id),
        coach_name=coach.full_name if coach else None,
        coachee_name=coachee.full_name if coachee else None,
        scheduled_at=booking.scheduled_at.isoformat(),
        duration_minutes=booking.duration_minutes,
        status=booking.status.value,
        topic=booking.topic,
        coachee_notes=booking.coachee_notes,
        coach_notes=booking.coach_notes,
        meeting_link=booking.meeting_link,
        completed_at=booking.completed_at.isoformat() if booking.completed_at else None,
        summary=booking.summary,
        has_briefing=booking.briefing is not None,
        created_at=booking.created_at.isoformat(),
    )


# ---------------------------------------------------------------------------
# Route Factory
# ---------------------------------------------------------------------------

def create_booking_routes(get_db, get_current_user, booking_service):
    """Factory to create booking routes.

    Args:
        get_db: FastAPI dependency for DB session
        get_current_user: FastAPI dependency for authenticated user
        booking_service: callable returning BookingService (lazy init)
    """
    router = APIRouter(prefix="/bookings", tags=["bookings"])

    def _svc():
        return booking_service() if callable(booking_service) else booking_service

    # -- Coach: Availability Slots --

    @router.get("/slots", response_model=list[SlotResponse])
    async def list_slots(
        user=Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ):
        """List coach's availability slots."""
        require_role(user, "coach", "admin")
        svc = _svc()
        slots = await svc.get_coach_slots(user.id, db)
        return [_format_slot(s) for s in slots]

    @router.post("/slots", response_model=SlotResponse, status_code=status.HTTP_201_CREATED)
    async def create_slot(
        body: CreateSlotRequest,
        user=Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ):
        """Create a new availability slot."""
        require_role(user, "coach", "admin")
        svc = _svc()

        start = dt_time.fromisoformat(body.start_time)
        end = dt_time.fromisoformat(body.end_time)

        if body.day_of_week < 0 or body.day_of_week > 6:
            raise HTTPException(status_code=400, detail="day_of_week muss 0-6 sein")

        slot = await svc.create_slot(
            coach_id=user.id,
            day_of_week=body.day_of_week,
            start_time=start,
            end_time=end,
            duration_minutes=body.duration_minutes,
            recurrence=body.recurrence,
            notes=body.notes,
            db=db,
        )
        return _format_slot(slot)

    @router.patch("/slots/{slot_id}", response_model=SlotResponse)
    async def update_slot(
        slot_id: str,
        body: UpdateSlotRequest,
        user=Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ):
        """Update an availability slot."""
        require_role(user, "coach", "admin")
        svc = _svc()

        updates = body.model_dump(exclude_none=True)
        if "start_time" in updates:
            updates["start_time"] = dt_time.fromisoformat(updates["start_time"])
        if "end_time" in updates:
            updates["end_time"] = dt_time.fromisoformat(updates["end_time"])
        if "duration_minutes" in updates:
            updates["session_duration_minutes"] = updates.pop("duration_minutes")

        slot = await svc.update_slot(UUID(slot_id), user.id, updates, db)
        if not slot:
            raise HTTPException(status_code=404, detail="Slot nicht gefunden")
        return _format_slot(slot)

    @router.delete("/slots/{slot_id}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_slot(
        slot_id: str,
        user=Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ):
        """Delete (deactivate) an availability slot."""
        require_role(user, "coach", "admin")
        svc = _svc()
        ok = await svc.delete_slot(UUID(slot_id), user.id, db)
        if not ok:
            raise HTTPException(status_code=404, detail="Slot nicht gefunden")

    # -- Coachee: Available Times --

    @router.get("/available/{coach_id}", response_model=list[AvailableTimeResponse])
    async def get_available_times(
        coach_id: str,
        start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
        end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
        user=Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ):
        """Get available booking times for a coach."""
        svc = _svc()
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)

        if (end - start).days > 30:
            raise HTTPException(status_code=400, detail="Maximal 30 Tage Zeitraum")

        times = await svc.get_available_times(UUID(coach_id), start, end, db)
        return [AvailableTimeResponse(**t) for t in times]

    # -- Booking CRUD --

    @router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
    async def create_booking(
        body: CreateBookingRequest,
        user=Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ):
        """Create a new booking request."""
        svc = _svc()
        try:
            booking = await svc.create_booking(
                coachee_id=user.id,
                coach_id=UUID(body.coach_id),
                scheduled_at=datetime.fromisoformat(body.scheduled_at),
                topic=body.topic,
                coachee_notes=body.coachee_notes,
                slot_id=UUID(body.slot_id) if body.slot_id else None,
                db=db,
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        return await _format_booking(booking, db)

    @router.get("", response_model=list[BookingResponse])
    async def list_bookings(
        role: str = Query(None, description="Filter by role: coach or coachee"),
        status_filter: str = Query(None, description="Filter by status"),
        user=Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ):
        """List user's bookings."""
        svc = _svc()
        if role == "coach":
            bookings = await svc.get_coach_bookings(user.id, status_filter, db)
        else:
            bookings = await svc.get_coachee_bookings(user.id, db)

        return [await _format_booking(b, db) for b in bookings]

    @router.get("/upcoming", response_model=list[BookingResponse])
    async def upcoming_bookings(
        limit: int = Query(5, ge=1, le=20),
        user=Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ):
        """Get upcoming bookings."""
        svc = _svc()
        bookings = await svc.get_upcoming_bookings(user.id, db, limit)
        return [await _format_booking(b, db) for b in bookings]

    @router.get("/{booking_id}", response_model=BookingResponse)
    async def get_booking(
        booking_id: str,
        user=Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ):
        """Get booking detail."""
        svc = _svc()
        booking = await svc.get_booking_detail(UUID(booking_id), user.id, db)
        if not booking:
            raise HTTPException(status_code=404, detail="Buchung nicht gefunden")
        return await _format_booking(booking, db)

    @router.post("/{booking_id}/confirm", response_model=BookingResponse)
    async def confirm_booking(
        booking_id: str,
        user=Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ):
        """Confirm a booking request (coach only)."""
        svc = _svc()
        try:
            booking = await svc.confirm_booking(UUID(booking_id), user.id, db)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        if not booking:
            raise HTTPException(status_code=404, detail="Buchung nicht gefunden")
        return await _format_booking(booking, db)

    @router.post("/{booking_id}/cancel", response_model=BookingResponse)
    async def cancel_booking(
        booking_id: str,
        user=Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ):
        """Cancel a booking."""
        svc = _svc()
        try:
            booking = await svc.cancel_booking(UUID(booking_id), user.id, db)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        if not booking:
            raise HTTPException(status_code=404, detail="Buchung nicht gefunden")
        return await _format_booking(booking, db)

    @router.post("/{booking_id}/complete", response_model=BookingResponse)
    async def complete_booking(
        booking_id: str,
        body: CompleteBookingRequest,
        user=Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ):
        """Complete a booking with session notes."""
        svc = _svc()
        booking = await svc.complete_booking(
            UUID(booking_id), user.id,
            coach_notes=body.coach_notes,
            summary=body.summary,
            db=db,
        )
        if not booking:
            raise HTTPException(status_code=404, detail="Buchung nicht gefunden")
        return await _format_booking(booking, db)

    # -- Briefing --

    @router.get("/{booking_id}/briefing", response_model=BriefingResponse)
    async def get_briefing(
        booking_id: str,
        user=Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ):
        """Get session briefing (coach only)."""
        svc = _svc()
        briefing = await svc.get_briefing(UUID(booking_id), user.id, db)
        if not briefing:
            raise HTTPException(status_code=404, detail="Briefing nicht gefunden")

        return BriefingResponse(
            id=str(briefing.id),
            status=briefing.status.value,
            content=briefing.content,
            coachee_profile_summary=briefing.coachee_profile_summary,
            scil_highlights=briefing.scil_highlights,
            suggested_topics=briefing.suggested_topics,
            suggested_exercises=briefing.suggested_exercises,
            previous_session_notes=briefing.previous_session_notes,
            training_progress_summary=briefing.training_progress_summary,
            generated_at=briefing.generated_at.isoformat() if briefing.generated_at else None,
        )

    @router.post("/{booking_id}/briefing/regenerate", response_model=BriefingResponse)
    async def regenerate_briefing(
        booking_id: str,
        user=Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ):
        """Regenerate session briefing."""
        svc = _svc()
        briefing = await svc.regenerate_briefing(UUID(booking_id), user.id, db)
        if not briefing:
            raise HTTPException(status_code=404, detail="Buchung nicht gefunden")

        return BriefingResponse(
            id=str(briefing.id),
            status=briefing.status.value,
            content=briefing.content,
            coachee_profile_summary=briefing.coachee_profile_summary,
            scil_highlights=briefing.scil_highlights,
            suggested_topics=briefing.suggested_topics,
            suggested_exercises=briefing.suggested_exercises,
            previous_session_notes=briefing.previous_session_notes,
            training_progress_summary=briefing.training_progress_summary,
            generated_at=briefing.generated_at.isoformat() if briefing.generated_at else None,
        )

    return router
