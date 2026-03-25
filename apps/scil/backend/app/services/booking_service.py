"""Booking Service — Manages coaching session bookings and AI briefing generation.

Handles:
- Coach availability slot CRUD
- Coachee booking flow (request → confirm → complete)
- AI-generated session briefings for coaches
- iCal feed generation
"""

import json
import logging
from datetime import datetime, timedelta, date, time as dt_time
from uuid import UUID

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import selectinload

from bfg_core.models.booking import (
    AvailabilitySlot, SlotRecurrence,
    Booking, BookingStatus,
    SessionBriefing, BriefingStatus,
)
from bfg_core.models.diagnostic import DiagnosticResult
from bfg_core.models.training import TrainingPlan, TrainingProgress
from bfg_core.models.coach import CoachAssignment, AssignmentStatus
from bfg_core.models.user import User
from bfg_core.services.ai_service import AIService

logger = logging.getLogger(__name__)


class BookingService:
    """Service for managing coaching session bookings."""

    def __init__(
        self,
        session_factory: async_sessionmaker,
        ai_service: AIService | None = None,
    ):
        self._session_factory = session_factory
        self._ai_service = ai_service

    # ------------------------------------------------------------------
    # Availability Slots (Coach)
    # ------------------------------------------------------------------

    async def get_coach_slots(
        self, coach_id: UUID, db: AsyncSession
    ) -> list[AvailabilitySlot]:
        """Get all availability slots for a coach."""
        stmt = (
            select(AvailabilitySlot)
            .where(
                AvailabilitySlot.coach_id == coach_id,
                AvailabilitySlot.is_active == True,  # noqa: E712
            )
            .order_by(AvailabilitySlot.day_of_week, AvailabilitySlot.start_time)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def create_slot(
        self,
        coach_id: UUID,
        day_of_week: int,
        start_time: dt_time,
        end_time: dt_time,
        duration_minutes: int = 60,
        recurrence: str = "weekly",
        notes: str | None = None,
        db: AsyncSession | None = None,
    ) -> AvailabilitySlot:
        """Create a new availability slot for a coach."""
        slot = AvailabilitySlot(
            coach_id=coach_id,
            day_of_week=day_of_week,
            start_time=start_time,
            end_time=end_time,
            session_duration_minutes=duration_minutes,
            recurrence=SlotRecurrence(recurrence),
            notes=notes,
        )
        db.add(slot)
        await db.commit()
        await db.refresh(slot)
        return slot

    async def update_slot(
        self,
        slot_id: UUID,
        coach_id: UUID,
        updates: dict,
        db: AsyncSession,
    ) -> AvailabilitySlot | None:
        """Update an availability slot."""
        slot = await db.get(AvailabilitySlot, slot_id)
        if not slot or slot.coach_id != coach_id:
            return None

        for key, value in updates.items():
            if hasattr(slot, key) and key not in ("id", "coach_id", "created_at"):
                setattr(slot, key, value)

        await db.commit()
        await db.refresh(slot)
        return slot

    async def delete_slot(
        self, slot_id: UUID, coach_id: UUID, db: AsyncSession
    ) -> bool:
        """Deactivate an availability slot."""
        slot = await db.get(AvailabilitySlot, slot_id)
        if not slot or slot.coach_id != coach_id:
            return False

        slot.is_active = False
        await db.commit()
        return True

    # ------------------------------------------------------------------
    # Available Times (Coachee view)
    # ------------------------------------------------------------------

    async def get_available_times(
        self,
        coach_id: UUID,
        start_date: date,
        end_date: date,
        db: AsyncSession,
    ) -> list[dict]:
        """Get available booking times for a coach within a date range."""
        # Get coach's active slots
        slots = await self.get_coach_slots(coach_id, db)

        # Get existing bookings in the range
        bookings_stmt = (
            select(Booking)
            .where(
                Booking.coach_id == coach_id,
                Booking.scheduled_at >= datetime.combine(start_date, dt_time.min),
                Booking.scheduled_at <= datetime.combine(end_date, dt_time.max),
                Booking.status.in_([BookingStatus.REQUESTED, BookingStatus.CONFIRMED]),
            )
        )
        bookings_result = await db.execute(bookings_stmt)
        existing_bookings = bookings_result.scalars().all()

        # Build booked datetime set
        booked_times = set()
        for b in existing_bookings:
            booked_times.add(b.scheduled_at.replace(second=0, microsecond=0))

        # Generate available times
        available = []
        current_date = start_date
        while current_date <= end_date:
            weekday = current_date.weekday()
            for slot in slots:
                if slot.day_of_week != weekday:
                    continue

                # Generate time slots from start_time to end_time
                slot_start = datetime.combine(current_date, slot.start_time)
                slot_end = datetime.combine(current_date, slot.end_time)
                duration = timedelta(minutes=slot.session_duration_minutes)

                current_time = slot_start
                while current_time + duration <= slot_end:
                    if current_time.replace(second=0, microsecond=0) not in booked_times:
                        available.append({
                            "date": current_date.isoformat(),
                            "time": current_time.strftime("%H:%M"),
                            "datetime": current_time.isoformat(),
                            "duration_minutes": slot.session_duration_minutes,
                            "slot_id": str(slot.id),
                        })
                    current_time += duration

            current_date += timedelta(days=1)

        return available

    # ------------------------------------------------------------------
    # Booking Flow
    # ------------------------------------------------------------------

    async def create_booking(
        self,
        coachee_id: UUID,
        coach_id: UUID,
        scheduled_at: datetime,
        topic: str | None = None,
        coachee_notes: str | None = None,
        slot_id: UUID | None = None,
        db: AsyncSession | None = None,
    ) -> Booking:
        """Create a new booking request."""
        # Verify coach-coachee relationship
        assignment_stmt = (
            select(CoachAssignment)
            .where(
                CoachAssignment.coach_id == coach_id,
                CoachAssignment.coachee_id == coachee_id,
                CoachAssignment.status.in_([
                    AssignmentStatus.ACTIVE,
                    AssignmentStatus.PENDING,
                ]),
            )
        )
        assignment_result = await db.execute(assignment_stmt)
        if not assignment_result.scalar_one_or_none():
            raise ValueError("Keine aktive Coach-Zuweisung gefunden")

        # Check for conflicts
        conflict_stmt = (
            select(Booking)
            .where(
                Booking.coach_id == coach_id,
                Booking.scheduled_at == scheduled_at,
                Booking.status.in_([BookingStatus.REQUESTED, BookingStatus.CONFIRMED]),
            )
        )
        conflict_result = await db.execute(conflict_stmt)
        if conflict_result.scalar_one_or_none():
            raise ValueError("Dieser Zeitslot ist bereits gebucht")

        booking = Booking(
            coach_id=coach_id,
            coachee_id=coachee_id,
            slot_id=slot_id,
            scheduled_at=scheduled_at,
            topic=topic,
            coachee_notes=coachee_notes,
            status=BookingStatus.REQUESTED,
        )
        db.add(booking)
        await db.commit()
        await db.refresh(booking)

        # Trigger briefing generation (async, non-blocking)
        try:
            await self._generate_briefing(booking.id, db)
        except Exception as e:
            logger.warning("Briefing generation failed: %s", e)

        return booking

    async def confirm_booking(
        self, booking_id: UUID, coach_id: UUID, db: AsyncSession
    ) -> Booking | None:
        """Coach confirms a booking request."""
        booking = await db.get(Booking, booking_id)
        if not booking or booking.coach_id != coach_id:
            return None

        if booking.status != BookingStatus.REQUESTED:
            raise ValueError("Buchung kann nicht bestaetigt werden")

        booking.status = BookingStatus.CONFIRMED
        await db.commit()
        await db.refresh(booking)
        return booking

    async def cancel_booking(
        self, booking_id: UUID, user_id: UUID, db: AsyncSession
    ) -> Booking | None:
        """Cancel a booking (by either coach or coachee)."""
        booking = await db.get(Booking, booking_id)
        if not booking:
            return None

        if booking.coach_id != user_id and booking.coachee_id != user_id:
            return None

        if booking.status in (BookingStatus.CANCELLED, BookingStatus.COMPLETED):
            raise ValueError("Buchung kann nicht storniert werden")

        booking.status = BookingStatus.CANCELLED
        await db.commit()
        await db.refresh(booking)
        return booking

    async def complete_booking(
        self,
        booking_id: UUID,
        coach_id: UUID,
        coach_notes: str | None = None,
        summary: str | None = None,
        db: AsyncSession | None = None,
    ) -> Booking | None:
        """Mark a booking as completed with session notes."""
        booking = await db.get(Booking, booking_id)
        if not booking or booking.coach_id != coach_id:
            return None

        booking.status = BookingStatus.COMPLETED
        booking.completed_at = datetime.utcnow()
        booking.coach_notes = coach_notes
        booking.summary = summary
        await db.commit()
        await db.refresh(booking)
        return booking

    # ------------------------------------------------------------------
    # Booking Queries
    # ------------------------------------------------------------------

    async def get_coach_bookings(
        self,
        coach_id: UUID,
        status_filter: str | None = None,
        db: AsyncSession | None = None,
    ) -> list[Booking]:
        """Get all bookings for a coach."""
        stmt = (
            select(Booking)
            .where(Booking.coach_id == coach_id)
            .options(
                selectinload(Booking.briefing),
                selectinload(Booking.slot),
            )
            .order_by(Booking.scheduled_at.desc())
        )
        if status_filter:
            try:
                stmt = stmt.where(Booking.status == BookingStatus(status_filter))
            except ValueError:
                pass

        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_coachee_bookings(
        self,
        coachee_id: UUID,
        db: AsyncSession,
    ) -> list[Booking]:
        """Get all bookings for a coachee."""
        stmt = (
            select(Booking)
            .where(Booking.coachee_id == coachee_id)
            .options(
                selectinload(Booking.briefing),
                selectinload(Booking.slot),
            )
            .order_by(Booking.scheduled_at.desc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_booking_detail(
        self,
        booking_id: UUID,
        user_id: UUID,
        db: AsyncSession,
    ) -> Booking | None:
        """Get booking detail (accessible by coach or coachee)."""
        booking = await db.get(Booking, booking_id)
        if not booking:
            return None
        if booking.coach_id != user_id and booking.coachee_id != user_id:
            return None
        return booking

    async def get_upcoming_bookings(
        self,
        user_id: UUID,
        db: AsyncSession,
        limit: int = 5,
    ) -> list[Booking]:
        """Get upcoming bookings for a user (as coach or coachee)."""
        now = datetime.utcnow()
        stmt = (
            select(Booking)
            .where(
                or_(Booking.coach_id == user_id, Booking.coachee_id == user_id),
                Booking.scheduled_at >= now,
                Booking.status.in_([BookingStatus.REQUESTED, BookingStatus.CONFIRMED]),
            )
            .options(
                selectinload(Booking.briefing),
                selectinload(Booking.slot),
            )
            .order_by(Booking.scheduled_at)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    # ------------------------------------------------------------------
    # AI Briefing Generation
    # ------------------------------------------------------------------

    async def _generate_briefing(
        self, booking_id: UUID, db: AsyncSession
    ):
        """Generate an AI briefing for a coaching session."""
        booking = await db.get(Booking, booking_id)
        if not booking:
            return

        # Create briefing record
        briefing = SessionBriefing(
            booking_id=booking_id,
            status=BriefingStatus.GENERATING,
        )
        db.add(briefing)
        await db.flush()

        if not self._ai_service or not self._ai_service.is_configured():
            briefing.status = BriefingStatus.PENDING
            await db.commit()
            return

        try:
            # Gather coachee data
            coachee = await db.get(User, booking.coachee_id)
            coachee_name = coachee.full_name if coachee else "Unbekannt"

            # Get latest diagnostic result
            result_stmt = (
                select(DiagnosticResult)
                .where(DiagnosticResult.user_id == booking.coachee_id)
                .order_by(DiagnosticResult.created_at.desc())
                .limit(1)
            )
            result_row = await db.execute(result_stmt)
            diag_result = result_row.scalar_one_or_none()

            # Get training progress
            plan_stmt = (
                select(TrainingPlan)
                .where(
                    TrainingPlan.user_id == booking.coachee_id,
                )
                .order_by(TrainingPlan.created_at.desc())
                .limit(1)
            )
            plan_row = await db.execute(plan_stmt)
            training_plan = plan_row.scalar_one_or_none()

            # Get previous booking notes
            prev_stmt = (
                select(Booking)
                .where(
                    Booking.coachee_id == booking.coachee_id,
                    Booking.coach_id == booking.coach_id,
                    Booking.status == BookingStatus.COMPLETED,
                )
                .order_by(Booking.completed_at.desc())
                .limit(3)
            )
            prev_row = await db.execute(prev_stmt)
            previous_bookings = prev_row.scalars().all()

            # Build prompt
            scil_info = ""
            if diag_result and diag_result.scores:
                scil_info = f"SCIL-Ergebnisse: {json.dumps(diag_result.scores, indent=2)}"
                if diag_result.summary:
                    scil_info += f"\nZusammenfassung: {diag_result.summary}"

            training_info = ""
            if training_plan:
                training_info = (
                    f"Trainingsplan: {training_plan.title}, "
                    f"Fortschritt: {training_plan.overall_progress:.0%}, "
                    f"Fokus: {training_plan.focus_areas}"
                )

            prev_notes = ""
            for pb in previous_bookings:
                if pb.summary or pb.coach_notes:
                    prev_notes += f"\n- {pb.completed_at}: {pb.summary or pb.coach_notes}"

            prompt = f"""Erstelle ein Briefing fuer eine Coaching-Session.

Coachee: {coachee_name}
Thema: {booking.topic or 'Nicht angegeben'}
Coachee-Notizen: {booking.coachee_notes or 'Keine'}

{scil_info}

{training_info}

Vorherige Sessions:{prev_notes if prev_notes else ' Keine'}

Erstelle ein strukturiertes Briefing als JSON:
{{
    "coachee_profile_summary": "2-3 Saetze zum Profil",
    "scil_highlights": {{"strengths": [...], "development_areas": [...]}},
    "suggested_topics": ["Thema 1", "Thema 2", "Thema 3"],
    "suggested_exercises": ["Uebung 1", "Uebung 2"],
    "previous_session_notes": "Zusammenfassung vorheriger Sessions",
    "training_progress_summary": "Aktueller Trainingsstand",
    "content": "Ausfuehrliches Briefing in Markdown (3-5 Absaetze)"
}}"""

            system = "Du bist ein erfahrener SCIL-Coaching-Berater. Erstelle professionelle Session-Briefings auf Deutsch als valides JSON."

            response = await self._ai_service.generate(
                prompt, system=system, max_tokens=800, temperature=0.7,
                user_id=booking.coach_id, intent="session_briefing",
            )

            try:
                cleaned = response.strip()
                if cleaned.startswith("```"):
                    cleaned = cleaned.split("\n", 1)[1]
                    cleaned = cleaned.rsplit("```", 1)[0]
                data = json.loads(cleaned)

                briefing.content = data.get("content")
                briefing.coachee_profile_summary = data.get("coachee_profile_summary")
                briefing.scil_highlights = data.get("scil_highlights")
                briefing.suggested_topics = data.get("suggested_topics")
                briefing.suggested_exercises = data.get("suggested_exercises")
                briefing.previous_session_notes = data.get("previous_session_notes")
                briefing.training_progress_summary = data.get("training_progress_summary")
                briefing.status = BriefingStatus.READY
                briefing.generated_at = datetime.utcnow()
            except (json.JSONDecodeError, IndexError):
                # If JSON parsing fails, save raw text as content
                briefing.content = response
                briefing.status = BriefingStatus.READY
                briefing.generated_at = datetime.utcnow()

        except Exception as e:
            logger.error("Briefing generation error: %s", e)
            briefing.status = BriefingStatus.FAILED

        await db.commit()

    async def get_briefing(
        self, booking_id: UUID, coach_id: UUID, db: AsyncSession
    ) -> SessionBriefing | None:
        """Get the briefing for a booking (coach only)."""
        booking = await db.get(Booking, booking_id)
        if not booking or booking.coach_id != coach_id:
            return None

        stmt = (
            select(SessionBriefing)
            .where(SessionBriefing.booking_id == booking_id)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def regenerate_briefing(
        self, booking_id: UUID, coach_id: UUID, db: AsyncSession
    ) -> SessionBriefing | None:
        """Regenerate the briefing for a booking."""
        booking = await db.get(Booking, booking_id)
        if not booking or booking.coach_id != coach_id:
            return None

        # Delete existing briefing
        stmt = select(SessionBriefing).where(SessionBriefing.booking_id == booking_id)
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            await db.delete(existing)
            await db.flush()

        await self._generate_briefing(booking_id, db)

        # Fetch the new one
        result2 = await db.execute(stmt)
        return result2.scalar_one_or_none()
