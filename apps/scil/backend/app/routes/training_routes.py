"""Training routes — Daily micro-training plan management.

Endpoints:
    GET    /training/today         - Get today's training
    GET    /training/plans         - List user's training plans
    POST   /training/plans         - Generate a new plan from SCIL results
    GET    /training/plans/{id}    - Plan detail with all days
    POST   /training/days/{id}/start    - Start a training day
    POST   /training/days/{id}/complete - Complete a training day
    GET    /training/stats         - User training statistics
    GET    /training/content       - Content library
"""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from bfg_core.models.training import (
    TrainingPlan, TrainingDay, TrainingProgress,
    DayStatus, PlanStatus, ContentArea,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class GeneratePlanRequest(BaseModel):
    result_id: str | None = None
    total_weeks: int = 4
    days_per_week: int = 5


class CompleteDayRequest(BaseModel):
    reflection: str | None = None
    rating: int | None = None
    answers: dict | None = None


class ContentItemResponse(BaseModel):
    id: str
    slug: str
    title: str
    description: str
    content_type: str
    area: str
    target_frequency: str | None
    difficulty: int
    duration_minutes: int
    body: dict
    tags: list
    author: str | None = None
    author_bio: str | None = None
    author_image_url: str | None = None
    is_premium: bool = False
    price_cents: int | None = None
    sort_order: int = 0
    lesson_count: int = 0


class TrainingDayResponse(BaseModel):
    id: str
    week_number: int
    day_number: int
    title: str
    coaching_note: str | None
    area: str
    status: str
    scheduled_date: str | None
    content: ContentItemResponse | None
    progress: dict | None


class PlanSummaryResponse(BaseModel):
    id: str
    title: str
    description: str | None
    total_weeks: int
    days_per_week: int
    status: str
    overall_progress: float
    current_week: int
    focus_areas: dict
    started_at: str | None
    completed_at: str | None
    created_at: str


class PlanDetailResponse(PlanSummaryResponse):
    ai_rationale: str | None
    days: list[TrainingDayResponse]


class TodayResponse(BaseModel):
    has_training: bool
    plan_id: str | None = None
    plan_title: str | None = None
    day: TrainingDayResponse | None = None
    stats: dict | None = None


class StatsResponse(BaseModel):
    total_completed_days: int
    total_time_minutes: int
    average_rating: float | None
    current_streak: int
    active_plan: dict | None


class ProgressResponse(BaseModel):
    id: str
    day_id: str
    started_at: str | None
    completed_at: str | None
    time_spent_minutes: int
    reflection: str | None
    rating: int | None
    ai_feedback: str | None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _format_content(c) -> ContentItemResponse:
    """Convert a LearningContent model to response format."""
    try:
        lesson_count = len(c.lessons) if c.lessons else 0
    except Exception:
        # lessons relationship may not be loaded (async lazy-load issue)
        lesson_count = 0
    return ContentItemResponse(
        id=str(c.id),
        slug=c.slug,
        title=c.title,
        description=c.description,
        content_type=c.content_type.value,
        area=c.area.value,
        target_frequency=c.target_frequency,
        difficulty=c.difficulty,
        duration_minutes=c.duration_minutes,
        body=c.body or {},
        tags=c.tags or [],
        author=c.author,
        author_bio=c.author_bio,
        author_image_url=c.author_image_url,
        is_premium=c.is_premium if hasattr(c, "is_premium") else False,
        price_cents=c.price_cents if hasattr(c, "price_cents") else None,
        sort_order=c.sort_order if hasattr(c, "sort_order") else 0,
        lesson_count=lesson_count,
    )


def _format_day(day: TrainingDay) -> TrainingDayResponse:
    """Convert a TrainingDay model to response format."""
    content = None
    if day.content:
        content = _format_content(day.content)

    progress = None
    if day.progress:
        progress = {
            "id": str(day.progress.id),
            "started_at": day.progress.started_at.isoformat() if day.progress.started_at else None,
            "completed_at": day.progress.completed_at.isoformat() if day.progress.completed_at else None,
            "time_spent_minutes": day.progress.time_spent_minutes,
            "reflection": day.progress.reflection,
            "rating": day.progress.rating,
            "ai_feedback": day.progress.ai_feedback,
        }

    return TrainingDayResponse(
        id=str(day.id),
        week_number=day.week_number,
        day_number=day.day_number,
        title=day.title,
        coaching_note=day.coaching_note,
        area=day.area.value,
        status=day.status.value,
        scheduled_date=day.scheduled_date.isoformat() if day.scheduled_date else None,
        content=content,
        progress=progress,
    )


def _format_plan_summary(plan: TrainingPlan) -> PlanSummaryResponse:
    """Convert a TrainingPlan model to summary response."""
    return PlanSummaryResponse(
        id=str(plan.id),
        title=plan.title,
        description=plan.description,
        total_weeks=plan.total_weeks,
        days_per_week=plan.days_per_week,
        status=plan.status.value,
        overall_progress=plan.overall_progress,
        current_week=plan.current_week,
        focus_areas=plan.focus_areas or {},
        started_at=plan.started_at.isoformat() if plan.started_at else None,
        completed_at=plan.completed_at.isoformat() if plan.completed_at else None,
        created_at=plan.created_at.isoformat(),
    )


# ---------------------------------------------------------------------------
# Route Factory
# ---------------------------------------------------------------------------

def create_training_routes(get_db, get_current_user, training_service):
    """Factory to create training routes.

    Args:
        get_db: FastAPI dependency for DB session
        get_current_user: FastAPI dependency for authenticated user
        training_service: callable returning TrainingService (lazy init)
    """
    router = APIRouter(prefix="/training", tags=["training"])

    def _svc():
        return training_service() if callable(training_service) else training_service

    # -- Today's Training --
    @router.get("/today", response_model=TodayResponse)
    async def get_today_training(
        user=Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ):
        """Get today's training for the current user."""
        svc = _svc()
        result = await svc.get_today_training(user.id, db)

        if not result:
            stats = await svc.get_user_stats(user.id, db)
            return TodayResponse(
                has_training=False,
                stats=stats,
            )

        plan = result["plan"]
        day = result["day"]

        return TodayResponse(
            has_training=True,
            plan_id=str(plan.id),
            plan_title=plan.title,
            day=_format_day(day),
            stats=await svc.get_user_stats(user.id, db),
        )

    # -- List Plans --
    @router.get("/plans", response_model=list[PlanSummaryResponse])
    async def list_plans(
        user=Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ):
        """List all training plans for the current user."""
        svc = _svc()
        plans = await svc.get_user_plans(user.id, db)
        return [_format_plan_summary(p) for p in plans]

    # -- Generate Plan --
    @router.post("/plans", response_model=PlanDetailResponse, status_code=status.HTTP_201_CREATED)
    async def generate_plan(
        body: GeneratePlanRequest,
        user=Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ):
        """Generate a new personalized training plan from SCIL results."""
        svc = _svc()

        result_id = UUID(body.result_id) if body.result_id else None
        plan = await svc.generate_plan(
            user_id=user.id,
            result_id=result_id,
            total_weeks=body.total_weeks,
            days_per_week=body.days_per_week,
            db=db,
        )

        return PlanDetailResponse(
            id=str(plan.id),
            title=plan.title,
            description=plan.description,
            total_weeks=plan.total_weeks,
            days_per_week=plan.days_per_week,
            status=plan.status.value,
            overall_progress=plan.overall_progress,
            current_week=plan.current_week,
            focus_areas=plan.focus_areas or {},
            ai_rationale=plan.ai_rationale,
            started_at=plan.started_at.isoformat() if plan.started_at else None,
            completed_at=plan.completed_at.isoformat() if plan.completed_at else None,
            created_at=plan.created_at.isoformat(),
            days=[_format_day(d) for d in plan.days],
        )

    # -- Plan Detail --
    @router.get("/plans/{plan_id}", response_model=PlanDetailResponse)
    async def get_plan_detail(
        plan_id: str,
        user=Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ):
        """Get detailed view of a training plan with all days."""
        svc = _svc()
        plan = await svc.get_plan_detail(UUID(plan_id), user.id, db)
        if not plan:
            raise HTTPException(status_code=404, detail="Trainingsplan nicht gefunden")

        return PlanDetailResponse(
            id=str(plan.id),
            title=plan.title,
            description=plan.description,
            total_weeks=plan.total_weeks,
            days_per_week=plan.days_per_week,
            status=plan.status.value,
            overall_progress=plan.overall_progress,
            current_week=plan.current_week,
            focus_areas=plan.focus_areas or {},
            ai_rationale=plan.ai_rationale,
            started_at=plan.started_at.isoformat() if plan.started_at else None,
            completed_at=plan.completed_at.isoformat() if plan.completed_at else None,
            created_at=plan.created_at.isoformat(),
            days=[_format_day(d) for d in plan.days],
        )

    # -- Start Day --
    @router.post("/days/{day_id}/start", response_model=ProgressResponse)
    async def start_day(
        day_id: str,
        user=Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ):
        """Start a training day."""
        svc = _svc()
        try:
            progress = await svc.start_day(UUID(day_id), user.id, db)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        return ProgressResponse(
            id=str(progress.id),
            day_id=str(progress.day_id),
            started_at=progress.started_at.isoformat() if progress.started_at else None,
            completed_at=progress.completed_at.isoformat() if progress.completed_at else None,
            time_spent_minutes=progress.time_spent_minutes,
            reflection=progress.reflection,
            rating=progress.rating,
            ai_feedback=progress.ai_feedback,
        )

    # -- Complete Day --
    @router.post("/days/{day_id}/complete", response_model=ProgressResponse)
    async def complete_day(
        day_id: str,
        body: CompleteDayRequest,
        user=Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ):
        """Complete a training day with optional reflection."""
        svc = _svc()
        try:
            progress = await svc.complete_day(
                day_id=UUID(day_id),
                user_id=user.id,
                db=db,
                reflection=body.reflection,
                rating=body.rating,
                answers=body.answers,
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        return ProgressResponse(
            id=str(progress.id),
            day_id=str(progress.day_id),
            started_at=progress.started_at.isoformat() if progress.started_at else None,
            completed_at=progress.completed_at.isoformat() if progress.completed_at else None,
            time_spent_minutes=progress.time_spent_minutes,
            reflection=progress.reflection,
            rating=progress.rating,
            ai_feedback=progress.ai_feedback,
        )

    # -- Stats --
    @router.get("/stats", response_model=StatsResponse)
    async def get_stats(
        user=Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ):
        """Get training statistics for the current user."""
        svc = _svc()
        stats = await svc.get_user_stats(user.id, db)
        return StatsResponse(**stats)

    # -- Content Library --
    @router.get("/content", response_model=list[ContentItemResponse])
    async def get_content_library(
        area: str | None = Query(None, description="Filter by SCIL area"),
        user=Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ):
        """Get available training content library."""
        svc = _svc()
        content = await svc.get_content_library(db, area=area)
        return [_format_content(c) for c in content]

    # -- Enrollment: Enroll in content --
    @router.post("/enroll/{content_id}")
    async def enroll_in_content(
        content_id: str,
        user=Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ):
        """Enroll in a training content. Free content is immediate; premium requires purchase."""
        svc = _svc()
        try:
            enrollment = await svc.enroll(user.id, UUID(content_id), db)
        except ValueError as e:
            raise HTTPException(status_code=403, detail=str(e))
        return {
            "id": str(enrollment.id),
            "content_id": str(enrollment.content_id),
            "status": enrollment.status.value,
            "enrolled_at": enrollment.enrolled_at.isoformat(),
        }

    # -- Enrollment: List user's enrollments --
    @router.get("/enrollments")
    async def list_enrollments(
        user=Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ):
        """List all training enrollments for the current user."""
        svc = _svc()
        enrollments = await svc.get_user_enrollments(user.id, db)
        result = []
        for e in enrollments:
            item = {
                "id": str(e.id),
                "content_id": str(e.content_id),
                "status": e.status.value,
                "enrolled_at": e.enrolled_at.isoformat(),
                "completed_at": e.completed_at.isoformat() if e.completed_at else None,
            }
            try:
                if e.content:
                    item["content_title"] = e.content.title
                    item["content_area"] = e.content.area.value
                    item["content_type"] = e.content.content_type.value
            except Exception:
                pass
            result.append(item)
        return result

    # -- Enrollment: Check enrollment for specific content --
    @router.get("/enrollments/{content_id}")
    async def check_enrollment(
        content_id: str,
        user=Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ):
        """Check enrollment status for a specific training content."""
        svc = _svc()
        enrollment = await svc.get_enrollment(user.id, UUID(content_id), db)
        if not enrollment:
            return {"enrolled": False}
        return {
            "enrolled": True,
            "id": str(enrollment.id),
            "status": enrollment.status.value,
            "enrolled_at": enrollment.enrolled_at.isoformat(),
            "completed_at": enrollment.completed_at.isoformat() if enrollment.completed_at else None,
        }

    # -- Enrollment: Complete enrollment --
    @router.post("/enrollments/{content_id}/complete")
    async def complete_enrollment(
        content_id: str,
        user=Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ):
        """Mark a training enrollment as completed."""
        svc = _svc()
        try:
            enrollment = await svc.complete_enrollment(user.id, UUID(content_id), db)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        return {
            "id": str(enrollment.id),
            "content_id": str(enrollment.content_id),
            "status": enrollment.status.value,
            "completed_at": enrollment.completed_at.isoformat() if enrollment.completed_at else None,
        }

    return router
