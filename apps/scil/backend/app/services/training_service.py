"""Training Service — Generates personalized training plans from SCIL results.

Uses AIService to create individualized micro-training plans based on:
- SCIL polygon scores (strengths and development areas)
- Available learning content library
- User's training history and preferences
"""

import json
import logging
from datetime import datetime, date, timedelta
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from bfg_core.models.diagnostic import DiagnosticResult
from bfg_core.models.training import (
    LearningContent, ContentArea,
    TrainingPlan, PlanStatus,
    TrainingDay, DayStatus,
    TrainingProgress,
)
from bfg_core.services.ai_service import AIService

logger = logging.getLogger(__name__)

# Area-to-frequency mapping (same as SCIL items)
AREA_FREQUENCIES = {
    "sensus": ["S01", "S02", "S03", "S04"],
    "corpus": ["C01", "C02", "C03", "C04"],
    "intellektus": ["I01", "I02", "I03", "I04"],
    "lingua": ["L01", "L02", "L03", "L04"],
}

AREA_LABELS = {
    "sensus": "Sensus (Beziehung & Emotion)",
    "corpus": "Corpus (Koerpersprache & Praesenz)",
    "intellektus": "Intellektus (Logik & Struktur)",
    "lingua": "Lingua (Sprache & Ausdruck)",
}


class TrainingService:
    """Service for generating and managing personalized training plans."""

    def __init__(
        self,
        session_factory: async_sessionmaker,
        ai_service: AIService | None = None,
    ):
        self._session_factory = session_factory
        self._ai_service = ai_service

    # ------------------------------------------------------------------
    # Plan Generation
    # ------------------------------------------------------------------

    async def generate_plan(
        self,
        user_id: UUID,
        result_id: UUID | None = None,
        total_weeks: int = 4,
        days_per_week: int = 5,
        db: AsyncSession | None = None,
    ) -> TrainingPlan:
        """Generate a personalized training plan from SCIL diagnostic results.

        If result_id is provided, uses those results. Otherwise, uses the
        user's most recent completed diagnostic result.
        """
        own_session = db is None
        if own_session:
            db = self._session_factory()

        try:
            # 1. Get diagnostic result
            scores_data = None
            if result_id:
                result = await db.get(DiagnosticResult, result_id)
                if result:
                    scores_data = result.scores
            else:
                # Get latest result for user
                stmt = (
                    select(DiagnosticResult)
                    .where(DiagnosticResult.user_id == user_id)
                    .order_by(DiagnosticResult.created_at.desc())
                    .limit(1)
                )
                row = await db.execute(stmt)
                result = row.scalar_one_or_none()
                if result:
                    scores_data = result.scores
                    result_id = result.id

            # 2. Analyze scores to determine focus areas
            focus_areas = self._analyze_focus_areas(scores_data)

            # 3. Get available content
            content_stmt = select(LearningContent).where(LearningContent.is_active == True)  # noqa: E712
            content_result = await db.execute(content_stmt)
            all_content = content_result.scalars().all()

            # 4. Generate plan with AI (or fallback to rule-based)
            ai_rationale = None
            plan_title = "Dein persoenlicher SCIL-Trainingsplan"
            plan_description = None

            if self._ai_service and self._ai_service.is_configured() and scores_data:
                try:
                    ai_result = await self._generate_ai_plan(
                        scores_data, focus_areas, total_weeks, days_per_week, user_id
                    )
                    plan_title = ai_result.get("title", plan_title)
                    plan_description = ai_result.get("description")
                    ai_rationale = ai_result.get("rationale")
                    # AI may refine focus areas
                    if "focus_areas" in ai_result:
                        focus_areas.update(ai_result["focus_areas"])
                except Exception as e:
                    logger.warning("AI plan generation failed, using rule-based: %s", e)

            # 5. Create plan
            plan = TrainingPlan(
                user_id=user_id,
                result_id=result_id,
                title=plan_title,
                description=plan_description,
                total_weeks=total_weeks,
                days_per_week=days_per_week,
                status=PlanStatus.ACTIVE,
                focus_areas=focus_areas,
                ai_rationale=ai_rationale,
                started_at=datetime.utcnow(),
            )
            db.add(plan)
            await db.flush()

            # 6. Generate training days
            await self._generate_days(
                db, plan, all_content, focus_areas, total_weeks, days_per_week
            )

            # 7. Unlock first day
            first_day_stmt = (
                select(TrainingDay)
                .where(TrainingDay.plan_id == plan.id)
                .order_by(TrainingDay.week_number, TrainingDay.day_number)
                .limit(1)
            )
            first_day_result = await db.execute(first_day_stmt)
            first_day = first_day_result.scalar_one_or_none()
            if first_day:
                first_day.status = DayStatus.AVAILABLE

            await db.commit()
            await db.refresh(plan)
            return plan

        finally:
            if own_session:
                await db.close()

    def _analyze_focus_areas(self, scores_data: dict | None) -> dict:
        """Analyze SCIL scores to determine primary/secondary focus areas."""
        if not scores_data:
            return {
                "primary": "sensus",
                "secondary": "lingua",
                "strengths": ["corpus", "intellektus"],
                "area_scores": {},
            }

        # Calculate area averages
        area_averages = {}
        for area, freqs in AREA_FREQUENCIES.items():
            area_scores_data = scores_data.get(area, {})
            if area_scores_data:
                values = [v for v in area_scores_data.values() if isinstance(v, (int, float))]
                area_averages[area] = sum(values) / len(values) if values else 2.0
            else:
                area_averages[area] = 2.0

        # Sort: lowest average = most need for development
        sorted_areas = sorted(area_averages.items(), key=lambda x: x[1])

        return {
            "primary": sorted_areas[0][0],
            "secondary": sorted_areas[1][0],
            "strengths": [sorted_areas[2][0], sorted_areas[3][0]],
            "area_scores": area_averages,
        }

    async def _generate_ai_plan(
        self,
        scores_data: dict,
        focus_areas: dict,
        total_weeks: int,
        days_per_week: int,
        user_id: UUID,
    ) -> dict:
        """Use AI to generate a personalized plan description and rationale."""
        scores_summary = json.dumps(focus_areas.get("area_scores", {}), indent=2)

        prompt = f"""Du bist ein SCIL-Coach und erstellst einen personalisierten Trainingsplan.

SCIL-Ergebnisse des Teilnehmers:
- Bereichs-Durchschnitte: {scores_summary}
- Entwicklungsbereich (primaer): {AREA_LABELS.get(focus_areas['primary'], focus_areas['primary'])}
- Entwicklungsbereich (sekundaer): {AREA_LABELS.get(focus_areas['secondary'], focus_areas['secondary'])}
- Staerken: {', '.join(AREA_LABELS.get(s, s) for s in focus_areas.get('strengths', []))}

Erstelle einen {total_weeks}-woechigen Trainingsplan mit {days_per_week} Einheiten pro Woche.

Antworte NUR als JSON:
{{
    "title": "Kurzer motivierender Titel (max 50 Zeichen)",
    "description": "2-3 Saetze Beschreibung des Plans",
    "rationale": "Begruendung warum dieser Fokus fuer den Teilnehmer sinnvoll ist (2-3 Saetze)"
}}"""

        system = "Du bist ein erfahrener SCIL-Coach. Antworte immer auf Deutsch und ausschliesslich als valides JSON."

        response = await self._ai_service.generate(
            prompt, system=system, max_tokens=500, temperature=0.7,
            user_id=user_id, intent="training_plan_generation",
        )

        try:
            # Try to parse JSON from response
            # Handle potential markdown code blocks
            cleaned = response.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1]
                cleaned = cleaned.rsplit("```", 1)[0]
            return json.loads(cleaned)
        except (json.JSONDecodeError, IndexError):
            logger.warning("Failed to parse AI plan response: %s", response[:200])
            return {}

    async def _generate_days(
        self,
        db: AsyncSession,
        plan: TrainingPlan,
        all_content: list[LearningContent],
        focus_areas: dict,
        total_weeks: int,
        days_per_week: int,
    ):
        """Generate training days with content assignments."""
        # Build content pools per area
        content_by_area: dict[str, list[LearningContent]] = {}
        for c in all_content:
            area_key = c.area.value
            content_by_area.setdefault(area_key, []).append(c)

        # Weekly distribution: focus on development areas
        primary = focus_areas.get("primary", "sensus")
        secondary = focus_areas.get("secondary", "lingua")
        strengths = focus_areas.get("strengths", ["corpus", "intellektus"])

        # Distribution per week: 2 primary, 1 secondary, 1 strength rotation, 1 general
        week_pattern = [primary, primary, secondary, strengths[0] if strengths else "general", "general"]

        start_date = date.today()
        content_usage: dict[str, int] = {}  # track how many times content is used

        for week in range(1, total_weeks + 1):
            for day_idx in range(days_per_week):
                day_num = day_idx + 1
                area_key = week_pattern[day_idx % len(week_pattern)]

                # Rotate strengths
                if area_key in strengths and week % 2 == 0 and len(strengths) > 1:
                    area_key = strengths[1]

                # Pick content for this area (least-used first)
                area_pool = content_by_area.get(area_key, [])
                if not area_pool:
                    area_pool = content_by_area.get("general", [])

                selected_content = None
                if area_pool:
                    # Sort by usage count, pick least used
                    sorted_pool = sorted(
                        area_pool,
                        key=lambda c: content_usage.get(str(c.id), 0)
                    )
                    selected_content = sorted_pool[0]
                    content_usage[str(selected_content.id)] = (
                        content_usage.get(str(selected_content.id), 0) + 1
                    )

                # Calculate scheduled date (skip weekends)
                day_offset = (week - 1) * 7 + day_idx
                scheduled = start_date + timedelta(days=day_offset)
                # Skip to Monday if on weekend
                while scheduled.weekday() >= 5:
                    scheduled += timedelta(days=1)

                try:
                    area_enum = ContentArea(area_key)
                except ValueError:
                    area_enum = ContentArea.GENERAL

                title = selected_content.title if selected_content else f"Tag {day_num}"
                coaching_note = self._generate_coaching_note(
                    week, day_num, area_key, focus_areas
                )

                training_day = TrainingDay(
                    plan_id=plan.id,
                    content_id=selected_content.id if selected_content else None,
                    week_number=week,
                    day_number=day_num,
                    title=title,
                    coaching_note=coaching_note,
                    area=area_enum,
                    status=DayStatus.LOCKED,
                    scheduled_date=scheduled,
                )
                db.add(training_day)

    def _generate_coaching_note(
        self, week: int, day: int, area: str, focus_areas: dict
    ) -> str:
        """Generate a coaching note for a training day."""
        area_label = AREA_LABELS.get(area, area)
        is_primary = area == focus_areas.get("primary")
        is_strength = area in focus_areas.get("strengths", [])

        if week == 1 and day == 1:
            return (
                f"Willkommen zu deinem SCIL-Training! Heute starten wir mit "
                f"{area_label}. Nimm dir bewusst Zeit fuer diese Uebung."
            )
        elif is_primary:
            return (
                f"Heute arbeiten wir an deinem Entwicklungsbereich {area_label}. "
                f"Kleine Schritte fuehren zu grossen Veraenderungen."
            )
        elif is_strength:
            return (
                f"{area_label} ist eine deiner Staerken! "
                f"Heute vertiefst du diese Kompetenz weiter."
            )
        else:
            return (
                f"Heute beschaeftigen wir uns mit {area_label}. "
                f"Bleib neugierig und offen fuer neue Perspektiven."
            )

    # ------------------------------------------------------------------
    # Plan Management
    # ------------------------------------------------------------------

    async def get_user_plans(
        self, user_id: UUID, db: AsyncSession
    ) -> list[TrainingPlan]:
        """Get all training plans for a user."""
        stmt = (
            select(TrainingPlan)
            .where(TrainingPlan.user_id == user_id)
            .order_by(TrainingPlan.created_at.desc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_plan_detail(
        self, plan_id: UUID, user_id: UUID, db: AsyncSession
    ) -> TrainingPlan | None:
        """Get a plan with all its days and progress."""
        stmt = (
            select(TrainingPlan)
            .where(TrainingPlan.id == plan_id, TrainingPlan.user_id == user_id)
        )
        result = await db.execute(stmt)
        plan = result.scalar_one_or_none()
        return plan

    async def get_today_training(
        self, user_id: UUID, db: AsyncSession
    ) -> dict | None:
        """Get today's training day for the user's active plan."""
        # Find active plan
        plan_stmt = (
            select(TrainingPlan)
            .where(
                TrainingPlan.user_id == user_id,
                TrainingPlan.status == PlanStatus.ACTIVE,
            )
            .order_by(TrainingPlan.created_at.desc())
            .limit(1)
        )
        plan_result = await db.execute(plan_stmt)
        plan = plan_result.scalar_one_or_none()
        if not plan:
            return None

        # Find available or in-progress day
        day_stmt = (
            select(TrainingDay)
            .where(
                TrainingDay.plan_id == plan.id,
                TrainingDay.status.in_([DayStatus.AVAILABLE, DayStatus.IN_PROGRESS]),
            )
            .order_by(TrainingDay.week_number, TrainingDay.day_number)
            .limit(1)
        )
        day_result = await db.execute(day_stmt)
        day = day_result.scalar_one_or_none()
        if not day:
            return None

        # Get progress if exists
        progress = None
        if day:
            prog_stmt = (
                select(TrainingProgress)
                .where(
                    TrainingProgress.day_id == day.id,
                    TrainingProgress.user_id == user_id,
                )
            )
            prog_result = await db.execute(prog_stmt)
            progress = prog_result.scalar_one_or_none()

        return {
            "plan": plan,
            "day": day,
            "content": day.content,
            "progress": progress,
        }

    # ------------------------------------------------------------------
    # Progress Tracking
    # ------------------------------------------------------------------

    async def start_day(
        self, day_id: UUID, user_id: UUID, db: AsyncSession
    ) -> TrainingProgress:
        """Mark a training day as started."""
        day = await db.get(TrainingDay, day_id)
        if not day:
            raise ValueError("Trainingstag nicht gefunden")

        # Verify ownership
        plan = await db.get(TrainingPlan, day.plan_id)
        if not plan or plan.user_id != user_id:
            raise ValueError("Zugriff verweigert")

        if day.status not in (DayStatus.AVAILABLE, DayStatus.IN_PROGRESS):
            raise ValueError("Dieser Trainingstag ist noch nicht verfuegbar")

        # Update day status
        day.status = DayStatus.IN_PROGRESS

        # Create or get progress
        prog_stmt = (
            select(TrainingProgress)
            .where(
                TrainingProgress.day_id == day_id,
                TrainingProgress.user_id == user_id,
            )
        )
        prog_result = await db.execute(prog_stmt)
        progress = prog_result.scalar_one_or_none()

        if not progress:
            progress = TrainingProgress(
                day_id=day_id,
                user_id=user_id,
                started_at=datetime.utcnow(),
            )
            db.add(progress)

        await db.commit()
        await db.refresh(progress)
        return progress

    async def complete_day(
        self,
        day_id: UUID,
        user_id: UUID,
        db: AsyncSession,
        reflection: str | None = None,
        rating: int | None = None,
        answers: dict | None = None,
    ) -> TrainingProgress:
        """Mark a training day as completed and record reflection."""
        day = await db.get(TrainingDay, day_id)
        if not day:
            raise ValueError("Trainingstag nicht gefunden")

        plan = await db.get(TrainingPlan, day.plan_id)
        if not plan or plan.user_id != user_id:
            raise ValueError("Zugriff verweigert")

        # Update day
        day.status = DayStatus.COMPLETED

        # Update progress
        prog_stmt = (
            select(TrainingProgress)
            .where(
                TrainingProgress.day_id == day_id,
                TrainingProgress.user_id == user_id,
            )
        )
        prog_result = await db.execute(prog_stmt)
        progress = prog_result.scalar_one_or_none()

        if not progress:
            progress = TrainingProgress(
                day_id=day_id,
                user_id=user_id,
                started_at=datetime.utcnow(),
            )
            db.add(progress)

        progress.completed_at = datetime.utcnow()
        progress.reflection = reflection
        progress.rating = rating
        progress.answers = answers

        if progress.started_at:
            delta = progress.completed_at - progress.started_at
            progress.time_spent_minutes = max(1, int(delta.total_seconds() / 60))

        # Generate AI feedback on reflection if available
        if reflection and self._ai_service and self._ai_service.is_configured():
            try:
                feedback = await self._generate_reflection_feedback(
                    reflection, day, plan, user_id
                )
                progress.ai_feedback = feedback
            except Exception as e:
                logger.warning("AI feedback generation failed: %s", e)

        # Unlock next day
        await self._unlock_next_day(db, plan, day)

        # Update plan progress
        await self._update_plan_progress(db, plan)

        await db.commit()
        await db.refresh(progress)
        return progress

    async def _generate_reflection_feedback(
        self,
        reflection: str,
        day: TrainingDay,
        plan: TrainingPlan,
        user_id: UUID,
    ) -> str:
        """Generate AI coaching feedback on a user's reflection."""
        area_label = AREA_LABELS.get(day.area.value, day.area.value)

        prompt = f"""Du bist ein einfuehlsamer SCIL-Coach. Ein Teilnehmer hat gerade eine Trainingseinheit zum Thema "{day.title}" ({area_label}) abgeschlossen.

Die Reflexion des Teilnehmers:
"{reflection}"

Gib kurzes, ermutigendes und konstruktives Feedback (2-3 Saetze).
Beziehe dich auf konkrete Punkte aus der Reflexion.
Gib einen kleinen Tipp fuer die Praxis."""

        system = "Du bist ein erfahrener SCIL-Coach. Antworte auf Deutsch, warm und professionell."

        return await self._ai_service.generate(
            prompt, system=system, max_tokens=200, temperature=0.7,
            user_id=user_id, intent="training_reflection_feedback",
        )

    async def _unlock_next_day(
        self, db: AsyncSession, plan: TrainingPlan, completed_day: TrainingDay
    ):
        """Unlock the next locked day in the plan."""
        next_stmt = (
            select(TrainingDay)
            .where(
                TrainingDay.plan_id == plan.id,
                TrainingDay.status == DayStatus.LOCKED,
            )
            .order_by(TrainingDay.week_number, TrainingDay.day_number)
            .limit(1)
        )
        next_result = await db.execute(next_stmt)
        next_day = next_result.scalar_one_or_none()

        if next_day:
            next_day.status = DayStatus.AVAILABLE

    async def _update_plan_progress(
        self, db: AsyncSession, plan: TrainingPlan
    ):
        """Update overall plan progress based on completed days."""
        total_days = plan.total_weeks * plan.days_per_week
        completed_stmt = (
            select(func.count())
            .select_from(TrainingDay)
            .where(
                TrainingDay.plan_id == plan.id,
                TrainingDay.status == DayStatus.COMPLETED,
            )
        )
        completed_result = await db.execute(completed_stmt)
        completed_count = completed_result.scalar() or 0

        plan.overall_progress = completed_count / total_days if total_days > 0 else 0.0

        # Check if plan is complete
        if completed_count >= total_days:
            plan.status = PlanStatus.COMPLETED
            plan.completed_at = datetime.utcnow()

    # ------------------------------------------------------------------
    # Content Library
    # ------------------------------------------------------------------

    async def get_content_library(
        self, db: AsyncSession, area: str | None = None
    ) -> list[LearningContent]:
        """Get available learning content, optionally filtered by area."""
        stmt = select(LearningContent).where(LearningContent.is_active == True)  # noqa: E712
        if area:
            try:
                stmt = stmt.where(LearningContent.area == ContentArea(area))
            except ValueError:
                pass
        stmt = stmt.order_by(LearningContent.area, LearningContent.difficulty)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_user_stats(
        self, user_id: UUID, db: AsyncSession
    ) -> dict:
        """Get training statistics for a user."""
        # Total completed days
        completed_stmt = (
            select(func.count())
            .select_from(TrainingProgress)
            .where(
                TrainingProgress.user_id == user_id,
                TrainingProgress.completed_at.isnot(None),
            )
        )
        completed_result = await db.execute(completed_stmt)
        total_completed = completed_result.scalar() or 0

        # Total time spent
        time_stmt = (
            select(func.sum(TrainingProgress.time_spent_minutes))
            .where(
                TrainingProgress.user_id == user_id,
                TrainingProgress.completed_at.isnot(None),
            )
        )
        time_result = await db.execute(time_stmt)
        total_minutes = time_result.scalar() or 0

        # Average rating
        rating_stmt = (
            select(func.avg(TrainingProgress.rating))
            .where(
                TrainingProgress.user_id == user_id,
                TrainingProgress.rating.isnot(None),
            )
        )
        rating_result = await db.execute(rating_stmt)
        avg_rating = rating_result.scalar()

        # Current streak (consecutive days with completions)
        streak = await self._calculate_streak(user_id, db)

        # Active plan progress
        active_plan_stmt = (
            select(TrainingPlan)
            .where(
                TrainingPlan.user_id == user_id,
                TrainingPlan.status == PlanStatus.ACTIVE,
            )
            .order_by(TrainingPlan.created_at.desc())
            .limit(1)
        )
        active_result = await db.execute(active_plan_stmt)
        active_plan = active_result.scalar_one_or_none()

        return {
            "total_completed_days": total_completed,
            "total_time_minutes": total_minutes,
            "average_rating": round(float(avg_rating), 1) if avg_rating else None,
            "current_streak": streak,
            "active_plan": {
                "id": str(active_plan.id),
                "title": active_plan.title,
                "progress": active_plan.overall_progress,
                "current_week": active_plan.current_week,
            } if active_plan else None,
        }

    async def _calculate_streak(self, user_id: UUID, db: AsyncSession) -> int:
        """Calculate the current consecutive-day training streak."""
        stmt = (
            select(TrainingProgress.completed_at)
            .where(
                TrainingProgress.user_id == user_id,
                TrainingProgress.completed_at.isnot(None),
            )
            .order_by(TrainingProgress.completed_at.desc())
        )
        result = await db.execute(stmt)
        dates = [
            r[0].date() if isinstance(r[0], datetime) else r[0]
            for r in result.all()
        ]

        if not dates:
            return 0

        streak = 1
        today = date.today()

        # Only count streak if most recent completion was today or yesterday
        if dates[0] < today - timedelta(days=1):
            return 0

        for i in range(1, len(dates)):
            if dates[i] >= dates[i - 1] - timedelta(days=1):
                streak += 1
            else:
                break

        return streak
