"""
Import Route — Import proprietary diagnostic results

Users can import their results from MBTI, DISC, Insights, Reiss, Lumina,
9 Levels, CAPTain, Hogan, CliftonStrengths, PCM, HBDI, Biostruktur,
Profilingvalues etc.

We ONLY store numeric scores. We do NOT import items, report texts,
or any copyrighted material.
"""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.feedback import ImportedResult
from app.schemas.feedback import ImportResultRequest, ImportResultResponse, AvailableImportTool

router = APIRouter(prefix="/import", tags=["Import"])


# ── Available import tools with their score schemas ──────────

IMPORT_TOOLS: list[dict] = [
    {
        "slug": "mbti",
        "name": "MBTI® (Myers-Briggs Type Indicator)",
        "description": "Import your 4-letter type code and preference scores.",
        "score_fields": [
            {"key": "type", "label": "Type Code (e.g. INTJ)", "type": "text"},
            {"key": "E_I", "label": "E-I Score (-10 to 10)", "type": "number"},
            {"key": "S_N", "label": "S-N Score (-10 to 10)", "type": "number"},
            {"key": "T_F", "label": "T-F Score (-10 to 10)", "type": "number"},
            {"key": "J_P", "label": "J-P Score (-10 to 10)", "type": "number"},
        ],
        "example": {"type": "INTJ", "E_I": -3.2, "S_N": 2.8, "T_F": -4.5, "J_P": -2.1},
    },
    {
        "slug": "disc",
        "name": "DISC / DiSG® / persolog®",
        "description": "Import your D-I-S-C profile scores (0-100).",
        "score_fields": [
            {"key": "D", "label": "Dominance (0-100)", "type": "number"},
            {"key": "I", "label": "Influence (0-100)", "type": "number"},
            {"key": "S", "label": "Steadiness (0-100)", "type": "number"},
            {"key": "C", "label": "Conscientiousness (0-100)", "type": "number"},
        ],
        "example": {"D": 78, "I": 45, "S": 32, "C": 65},
    },
    {
        "slug": "insights",
        "name": "Insights Discovery®",
        "description": "Import your 4 colour energy scores.",
        "score_fields": [
            {"key": "fiery_red", "label": "Fiery Red (0-100)", "type": "number"},
            {"key": "sunshine_yellow", "label": "Sunshine Yellow (0-100)", "type": "number"},
            {"key": "earth_green", "label": "Earth Green (0-100)", "type": "number"},
            {"key": "cool_blue", "label": "Cool Blue (0-100)", "type": "number"},
        ],
        "example": {"fiery_red": 72, "sunshine_yellow": 58, "earth_green": 34, "cool_blue": 65},
    },
    {
        "slug": "reiss",
        "name": "Reiss Motivation Profile®",
        "description": "Import your 16 basic desire scores (-2 to +2).",
        "score_fields": [
            {"key": f"motive_{i}", "label": f"Motive {i} (-2 to +2)", "type": "number"}
            for i in range(1, 17)
        ],
        "example": {"motive_1": 1.5, "motive_2": -0.8, "motive_3": 2.0},
    },
    {
        "slug": "lumina",
        "name": "Lumina Spark®",
        "description": "Import your 24 quality scores.",
        "score_fields": [
            {"key": "quality_score", "label": "JSON with 24 qualities", "type": "json"},
        ],
        "example": {"discipline": 72, "reliable": 68, "cautious": 45},
    },
    {
        "slug": "9levels",
        "name": "9 Levels®",
        "description": "Import your 9 value system level scores.",
        "score_fields": [
            {"key": f"level_{i}", "label": f"Level {i} (0-100)", "type": "number"}
            for i in range(1, 10)
        ],
        "example": {"level_1": 15, "level_5": 82, "level_7": 65},
    },
    {
        "slug": "captain",
        "name": "CAPTain®",
        "description": "Import your potential analysis scores.",
        "score_fields": [
            {"key": "potential_scores", "label": "JSON with potential dimensions", "type": "json"},
        ],
        "example": {"leadership_potential": 78, "team_orientation": 65},
    },
    {
        "slug": "hogan",
        "name": "Hogan Assessments (HPI / HDS / MVPI)",
        "description": "Import your Hogan personality, derailer, and values scores.",
        "score_fields": [
            {"key": "hpi", "label": "HPI Scores (JSON)", "type": "json"},
            {"key": "hds", "label": "HDS Derailer Scores (JSON)", "type": "json"},
            {"key": "mvpi", "label": "MVPI Values Scores (JSON)", "type": "json"},
        ],
        "example": {"hpi": {"adjustment": 62}, "hds": {"bold": 45}, "mvpi": {"recognition": 78}},
    },
    {
        "slug": "cliftonstrengths",
        "name": "CliftonStrengths® (Gallup)",
        "description": "Import your Top 5-34 strengths ranking.",
        "score_fields": [
            {"key": "top_strengths", "label": "Ordered list of strengths", "type": "json"},
        ],
        "example": {"top_strengths": ["Strategic", "Learner", "Achiever", "Ideation", "Input"]},
    },
    {
        "slug": "pcm",
        "name": "PCM® (Process Communication Model)",
        "description": "Import your 6 personality type scores.",
        "score_fields": [
            {"key": "thinker", "label": "Thinker (0-100)", "type": "number"},
            {"key": "persister", "label": "Persister (0-100)", "type": "number"},
            {"key": "harmonizer", "label": "Harmonizer (0-100)", "type": "number"},
            {"key": "imaginer", "label": "Imaginer (0-100)", "type": "number"},
            {"key": "rebel", "label": "Rebel (0-100)", "type": "number"},
            {"key": "promoter", "label": "Promoter (0-100)", "type": "number"},
        ],
        "example": {"thinker": 85, "persister": 60, "harmonizer": 45, "imaginer": 30, "rebel": 70, "promoter": 55},
    },
    {
        "slug": "hbdi",
        "name": "HBDI® (Herrmann Brain Dominance Instrument)",
        "description": "Import your 4-quadrant thinking preference scores.",
        "score_fields": [
            {"key": "A_analytical", "label": "Quadrant A - Analytical (0-200)", "type": "number"},
            {"key": "B_practical", "label": "Quadrant B - Practical (0-200)", "type": "number"},
            {"key": "C_relational", "label": "Quadrant C - Relational (0-200)", "type": "number"},
            {"key": "D_experimental", "label": "Quadrant D - Experimental (0-200)", "type": "number"},
        ],
        "example": {"A_analytical": 120, "B_practical": 85, "C_relational": 90, "D_experimental": 105},
    },
    {
        "slug": "biostruktur",
        "name": "Biostruktur-Analyse® (Structogram)",
        "description": "Import your 3-colour profile.",
        "score_fields": [
            {"key": "green", "label": "Green / Limbic (0-100)", "type": "number"},
            {"key": "red", "label": "Red / Brain Stem (0-100)", "type": "number"},
            {"key": "blue", "label": "Blue / Cerebral (0-100)", "type": "number"},
        ],
        "example": {"green": 55, "red": 30, "blue": 65},
    },
    {
        "slug": "profilingvalues",
        "name": "Profilingvalues®",
        "description": "Import your value profile scores.",
        "score_fields": [
            {"key": "value_scores", "label": "JSON with value dimensions", "type": "json"},
        ],
        "example": {"empathy": 82, "responsibility": 75, "self_direction": 68},
    },
]


@router.get("/tools", response_model=list[AvailableImportTool])
async def list_import_tools():
    """List all available tools for result import."""
    return IMPORT_TOOLS


@router.get("/tools/{slug}")
async def get_import_tool(slug: str):
    """Get details of a specific import tool including expected score fields."""
    for tool in IMPORT_TOOLS:
        if tool["slug"] == slug:
            return tool
    raise HTTPException(status_code=404, detail=f"Import tool '{slug}' not found")


@router.post("/results", response_model=ImportResultResponse)
async def import_result(data: ImportResultRequest, user_id: uuid.UUID | None = None, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    """Import a result from a proprietary diagnostic tool."""
    # Validate source tool exists
    valid_slugs = {t["slug"] for t in IMPORT_TOOLS}
    if data.source_tool not in valid_slugs:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown source tool: {data.source_tool}. Available: {sorted(valid_slugs)}"
        )

    if not data.consent_given:
        raise HTTPException(
            status_code=400,
            detail="DSGVO consent is required before importing results."
        )

    # Validate scores are not empty
    if not data.scores:
        raise HTTPException(status_code=400, detail="Scores cannot be empty.")

    # In production: get user_id from JWT token. For dev, use query param or first user.
    if not user_id:
        from app.models.user import User
        result = await db.execute(select(User).limit(1))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=400, detail="No users found. Please register first.")
        user_id = user.id

    imported = ImportedResult(
        user_id=user_id,
        source_tool=data.source_tool,
        source_tool_name=data.source_tool_name,
        scores=data.scores,
        original_test_date=data.original_test_date,
        provider_name=data.provider_name,
        notes=data.notes,
        consent_given=data.consent_given,
    )
    db.add(imported)
    await db.commit()
    await db.refresh(imported)
    return imported


@router.get("/results", response_model=list[ImportResultResponse])
async def list_imported_results(user_id: uuid.UUID, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    """List all imported results for a user."""
    result = await db.execute(
        select(ImportedResult).where(ImportedResult.user_id == user_id)
    )
    return result.scalars().all()


@router.delete("/results/{result_id}")
async def delete_imported_result(result_id: uuid.UUID, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    """Delete an imported result (DSGVO right to deletion)."""
    result = await db.execute(
        select(ImportedResult).where(ImportedResult.id == result_id)
    )
    imported = result.scalar_one_or_none()
    if not imported:
        raise HTTPException(status_code=404, detail="Imported result not found")

    await db.delete(imported)
    await db.commit()
    return {"status": "deleted", "id": str(result_id)}
