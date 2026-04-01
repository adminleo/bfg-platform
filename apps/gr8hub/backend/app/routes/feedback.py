"""
360° Feedback API Routes

Endpoints:
  POST   /feedback/rounds                    Create a new feedback round
  GET    /feedback/rounds                    List user's feedback rounds
  GET    /feedback/rounds/{round_id}         Get round details
  POST   /feedback/rounds/{round_id}/raters  Add raters to a round
  POST   /feedback/rounds/{round_id}/launch  Launch the round (send invitations)
  GET    /feedback/rater/{access_token}      Rater entry point (validates token)
  POST   /feedback/rater/{access_token}/consent  GDPR consent
  POST   /feedback/responses                 Submit a completed response
  GET    /feedback/rounds/{round_id}/results Get aggregated results
"""

import secrets
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.feedback import (
    FeedbackRound, FeedbackRoundStatus,
    FeedbackRater, RaterPerspective, RaterStatus,
    FeedbackResponse,
)
from app.schemas.feedback import (
    CreateFeedbackRoundRequest, AddRatersRequest, ConsentRequest,
    SubmitResponseRequest, FeedbackRoundResponse, FeedbackRoundSummary,
    FeedbackResultResponse, RaterResponse,
)

router = APIRouter(prefix="/feedback", tags=["360° Feedback"])


# ── Rounds ───────────────────────────────────────────────────

@router.post("/rounds", response_model=FeedbackRoundResponse)
async def create_round(data: CreateFeedbackRoundRequest, db: AsyncSession = Depends(get_db)):
    """Create a new 360° feedback round."""
    round = FeedbackRound(
        target_user_id=data.target_user_id,
        created_by_id=data.target_user_id,  # For now, self-initiated
        title=data.title,
        min_raters_per_group=data.min_raters_per_group,
    )
    if data.competencies:
        round.competencies = data.competencies

    db.add(round)
    await db.commit()
    await db.refresh(round)
    return round


@router.get("/rounds", response_model=list[FeedbackRoundSummary])
async def list_rounds(user_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """List all feedback rounds for a user."""
    result = await db.execute(
        select(FeedbackRound).where(FeedbackRound.target_user_id == user_id)
    )
    rounds = result.scalars().all()

    summaries = []
    for r in rounds:
        total = len(r.raters) if r.raters else 0
        completed = sum(1 for rt in (r.raters or []) if rt.status == RaterStatus.COMPLETED)
        summaries.append(FeedbackRoundSummary(
            id=r.id,
            title=r.title,
            status=r.status.value,
            total_raters=total,
            completed_raters=completed,
            created_at=r.created_at,
        ))
    return summaries


@router.get("/rounds/{round_id}", response_model=FeedbackRoundResponse)
async def get_round(round_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Get details of a feedback round including raters."""
    result = await db.execute(
        select(FeedbackRound).where(FeedbackRound.id == round_id)
    )
    round = result.scalar_one_or_none()
    if not round:
        raise HTTPException(status_code=404, detail="Feedback round not found")
    return round


# ── Raters ───────────────────────────────────────────────────

@router.post("/rounds/{round_id}/raters", response_model=list[RaterResponse])
async def add_raters(round_id: uuid.UUID, data: AddRatersRequest, db: AsyncSession = Depends(get_db)):
    """Add raters to a feedback round."""
    result = await db.execute(
        select(FeedbackRound).where(FeedbackRound.id == round_id)
    )
    round = result.scalar_one_or_none()
    if not round:
        raise HTTPException(status_code=404, detail="Feedback round not found")
    if round.status not in (FeedbackRoundStatus.DRAFT, FeedbackRoundStatus.ACTIVE):
        raise HTTPException(status_code=400, detail="Round is not accepting new raters")

    created_raters = []
    for r in data.raters:
        try:
            perspective = RaterPerspective(r.perspective)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid perspective: {r.perspective}. Must be one of: self, supervisor, peer, report, external"
            )

        rater = FeedbackRater(
            round_id=round_id,
            email=r.email,
            name=r.name,
            perspective=perspective,
            access_token=secrets.token_urlsafe(48),
        )
        db.add(rater)
        created_raters.append(rater)

    await db.commit()
    for rater in created_raters:
        await db.refresh(rater)
    return created_raters


@router.post("/rounds/{round_id}/launch")
async def launch_round(round_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Launch the feedback round — activates invitations."""
    result = await db.execute(
        select(FeedbackRound).where(FeedbackRound.id == round_id)
    )
    round = result.scalar_one_or_none()
    if not round:
        raise HTTPException(status_code=404, detail="Feedback round not found")
    if round.status != FeedbackRoundStatus.DRAFT:
        raise HTTPException(status_code=400, detail="Round already launched")

    # Validate minimum raters
    perspectives = {}
    for rater in round.raters:
        p = rater.perspective.value
        perspectives.setdefault(p, 0)
        perspectives[p] += 1

    # Check anonymity: groups that require anonymity must have >= threshold raters
    anonymous_groups = {"peer", "report", "external"}
    for group in anonymous_groups:
        count = perspectives.get(group, 0)
        if count > 0 and count < round.anonymity_threshold:
            raise HTTPException(
                status_code=400,
                detail=f"Group '{group}' has {count} raters but needs at least {round.anonymity_threshold} for anonymity"
            )

    round.status = FeedbackRoundStatus.ACTIVE
    await db.commit()

    return {
        "status": "launched",
        "round_id": str(round_id),
        "total_raters": len(round.raters),
        "perspectives": perspectives,
        "message": "Invitations activated. Raters can now access the feedback via their access tokens.",
    }


# ── Rater access ─────────────────────────────────────────────

@router.get("/rater/{access_token}")
async def rater_entry(access_token: str, db: AsyncSession = Depends(get_db)):
    """Rater entry point — validates access token and returns round info."""
    result = await db.execute(
        select(FeedbackRater).where(FeedbackRater.access_token == access_token)
    )
    rater = result.scalar_one_or_none()
    if not rater:
        raise HTTPException(status_code=404, detail="Invalid access token")

    # Load the round
    round_result = await db.execute(
        select(FeedbackRound).where(FeedbackRound.id == rater.round_id)
    )
    round = round_result.scalar_one_or_none()

    if round.status != FeedbackRoundStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="This feedback round is not currently active")

    return {
        "rater_id": str(rater.id),
        "rater_name": rater.name,
        "perspective": rater.perspective.value,
        "round_id": str(rater.round_id),
        "round_title": round.title,
        "gdpr_consented": rater.gdpr_consented,
        "gdpr_consent_text": round.gdpr_consent_text,
        "status": rater.status.value,
        "competencies": round.competencies,
    }


@router.post("/rater/{access_token}/consent")
async def rater_consent(access_token: str, data: ConsentRequest, db: AsyncSession = Depends(get_db)):
    """Record GDPR consent for a rater."""
    result = await db.execute(
        select(FeedbackRater).where(FeedbackRater.access_token == access_token)
    )
    rater = result.scalar_one_or_none()
    if not rater:
        raise HTTPException(status_code=404, detail="Invalid access token")

    if not data.gdpr_consented:
        raise HTTPException(status_code=400, detail="GDPR consent is required to participate")

    rater.gdpr_consented = True
    rater.gdpr_consented_at = datetime.utcnow()
    rater.status = RaterStatus.STARTED
    rater.started_at = datetime.utcnow()
    await db.commit()

    return {"status": "consent_recorded", "rater_id": str(rater.id)}


# ── Responses ────────────────────────────────────────────────

@router.post("/responses")
async def submit_response(data: SubmitResponseRequest, db: AsyncSession = Depends(get_db)):
    """Submit a completed feedback response."""
    # Validate rater
    rater_result = await db.execute(
        select(FeedbackRater).where(FeedbackRater.id == data.rater_id)
    )
    rater = rater_result.scalar_one_or_none()
    if not rater:
        raise HTTPException(status_code=404, detail="Rater not found")
    if not rater.gdpr_consented:
        raise HTTPException(status_code=400, detail="GDPR consent required before submitting")
    if rater.status == RaterStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Response already submitted")

    response = FeedbackResponse(
        rater_id=rater.id,
        round_id=rater.round_id,
        competency_scores=data.competency_scores,
        scil_scores=data.scil_scores,
        qualitative_feedback=data.qualitative_feedback,
        conversation=data.conversation,
    )
    db.add(response)

    rater.status = RaterStatus.COMPLETED
    rater.completed_at = datetime.utcnow()
    await db.commit()

    # Check if all raters are done → trigger analysis
    round_result = await db.execute(
        select(FeedbackRound).where(FeedbackRound.id == rater.round_id)
    )
    round = round_result.scalar_one_or_none()

    all_completed = all(
        r.status in (RaterStatus.COMPLETED, RaterStatus.DECLINED, RaterStatus.EXPIRED)
        for r in round.raters
    )
    if all_completed:
        round.status = FeedbackRoundStatus.ANALYSIS
        await db.commit()

    return {
        "status": "submitted",
        "round_status": round.status.value,
        "all_raters_done": all_completed,
    }


# ── Results ──────────────────────────────────────────────────

@router.get("/rounds/{round_id}/results", response_model=FeedbackResultResponse)
async def get_results(round_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Get aggregated 360° feedback results with Johari Window."""
    round_result = await db.execute(
        select(FeedbackRound).where(FeedbackRound.id == round_id)
    )
    round = round_result.scalar_one_or_none()
    if not round:
        raise HTTPException(status_code=404, detail="Feedback round not found")

    # If still collecting, return progress
    if round.status in (FeedbackRoundStatus.DRAFT, FeedbackRoundStatus.ACTIVE):
        completion = {}
        for rater in round.raters:
            p = rater.perspective.value
            completion.setdefault(p, {"total": 0, "completed": 0})
            completion[p]["total"] += 1
            if rater.status == RaterStatus.COMPLETED:
                completion[p]["completed"] += 1

        return FeedbackResultResponse(
            round_id=round.id,
            status=round.status.value,
            rater_completion=completion,
        )

    # If analysis needed, compute results
    if round.status == FeedbackRoundStatus.ANALYSIS:
        await _compute_results(round, db)

    return FeedbackResultResponse(
        round_id=round.id,
        status=round.status.value,
        aggregated_scores=round.aggregated_scores,
        scil_scores_self=round.scil_scores_self,
        scil_scores_others=round.scil_scores_others,
        johari_window=round.johari_window,
        qualitative_summary=round.qualitative_summary,
    )


async def _compute_results(round: FeedbackRound, db: AsyncSession):
    """Compute aggregated results for a completed round."""
    # Simple aggregation (agent-based analysis can be added later)

    self_scores = {}
    other_scores_by_perspective: dict[str, list[dict]] = {}

    for rater in round.raters:
        if rater.status != RaterStatus.COMPLETED or not rater.response:
            continue

        scores = rater.response.competency_scores
        if rater.perspective == RaterPerspective.SELF:
            self_scores = scores
        else:
            p = rater.perspective.value
            other_scores_by_perspective.setdefault(p, [])
            other_scores_by_perspective[p].append(scores)

    # Aggregate all non-self scores
    all_other_scores = []
    for group_scores in other_scores_by_perspective.values():
        all_other_scores.extend(group_scores)

    if all_other_scores:
        all_comps = set()
        for s in all_other_scores:
            all_comps.update(s.keys())

        aggregated = {}
        for comp in all_comps:
            vals = [s.get(comp, 0) for s in all_other_scores if comp in s]
            aggregated[comp] = round_val(sum(vals) / len(vals)) if vals else 0

        round.aggregated_scores = aggregated
    else:
        aggregated = {}
        round.aggregated_scores = {}

    # Compute Johari Window
    if self_scores and aggregated:
        johari = {"public": [], "blind_spot": [], "hidden": [], "unknown": []}
        threshold = 1.5
        all_comps = set(self_scores.keys()) | set(aggregated.keys())

        for comp in all_comps:
            s = self_scores.get(comp, 5.0)
            o = aggregated.get(comp, 5.0)
            diff = s - o

            if abs(diff) <= threshold:
                if (s + o) / 2 >= 6.0:
                    johari["public"].append(comp)
                else:
                    johari["unknown"].append(comp)
            elif diff > threshold:
                johari["hidden"].append(comp)
            else:
                johari["blind_spot"].append(comp)

        round.johari_window = johari

    # Map to SCIL scores
    from app.agents_bridge import map_to_scil
    if self_scores:
        round.scil_scores_self = map_to_scil(self_scores)
    if aggregated:
        round.scil_scores_others = map_to_scil(aggregated)

    round.status = FeedbackRoundStatus.COMPLETED
    round.completed_at = datetime.utcnow()
    await db.commit()


def round_val(v: float) -> float:
    return round(v, 1)
