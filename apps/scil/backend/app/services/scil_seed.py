"""SCIL Seed Data — creates the SCIL diagnostic entry on startup.

Idempotent: checks if 'scil' slug exists before inserting.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bfg_core.models.diagnostic import Diagnostic, DiagnosticCategory


SCIL_DIAGNOSTIC_ID = uuid.UUID("00000000-0000-4000-a000-000000000001")

SCIL_CONFIG = {
    "framework": "S.C.I.L. Performance Strategie",
    "author": "Andreas Bornhaeusser",
    "measures": "Wirkungskompetenz (Aussenwirkung), NICHT Persoenlichkeit",
    "areas": {
        "sensus": {
            "label": "Sensus",
            "description": "Beziehung & Emotion",
            "color": "#E74C3C",
            "frequencies": [
                {"key": "innere_praesenz", "label": "Innere Praesenz"},
                {"key": "innere_ueberzeugung", "label": "Innere Ueberzeugung"},
                {"key": "prozessfokussierung", "label": "Prozessfokussierung"},
                {"key": "emotionalitaet", "label": "Emotionalitaet"},
            ],
        },
        "corpus": {
            "label": "Corpus",
            "description": "Koerpersprache & Praesenz",
            "color": "#F39C12",
            "frequencies": [
                {"key": "erscheinungsbild", "label": "Erscheinungsbild"},
                {"key": "mimik", "label": "Mimik"},
                {"key": "gestik", "label": "Gestik"},
                {"key": "raeumliche_praesenz", "label": "Raeumliche Praesenz"},
            ],
        },
        "intellektus": {
            "label": "Intellektus",
            "description": "Logik & Struktur",
            "color": "#3498DB",
            "frequencies": [
                {"key": "sachlichkeit", "label": "Sachlichkeit"},
                {"key": "analytik", "label": "Analytik"},
                {"key": "struktur", "label": "Struktur"},
                {"key": "zielorientierung", "label": "Zielorientierung"},
            ],
        },
        "lingua": {
            "label": "Lingua",
            "description": "Sprache & Ausdruck",
            "color": "#2ECC71",
            "frequencies": [
                {"key": "stimme", "label": "Stimme"},
                {"key": "artikulation", "label": "Artikulation"},
                {"key": "beredsamkeit", "label": "Beredsamkeit"},
                {"key": "bildhaftigkeit", "label": "Bildhaftigkeit"},
            ],
        },
    },
    "scoring": {
        "scale_min": 0,
        "scale_max": 4,
        "subscale_min": 1,
        "subscale_max": 9,
        "levels": {
            "a": {"label": "Ausgepragte Staerke", "range": [3.5, 4.0]},
            "b": {"label": "Staerkenpotenzial", "range": [2.5, 3.5]},
            "c": {"label": "Durchschnittliche Staerke", "range": [1.5, 2.5]},
            "d": {"label": "Relative Staerke", "range": [0.5, 1.5]},
            "e": {"label": "Schwache Auspraegung", "range": [0.0, 0.5]},
        },
    },
    "charisma_hypothesis": (
        "Maximale Balance aller 16 Frequenzen auf hohem Niveau "
        "= hoechste Interaktionskompetenz"
    ),
}


async def seed_scil_diagnostic(session: AsyncSession) -> Diagnostic:
    """Seed the SCIL diagnostic entry if it doesn't exist yet."""
    result = await session.execute(
        select(Diagnostic).where(Diagnostic.slug == "scil")
    )
    existing = result.scalar_one_or_none()
    if existing:
        # Update min/max questions if changed (e.g. 15→100 migration)
        if existing.min_questions != 100 or existing.max_questions != 120:
            existing.min_questions = 100
            existing.max_questions = 120
            existing.config = SCIL_CONFIG
            await session.commit()
            await session.refresh(existing)
        return existing

    diagnostic = Diagnostic(
        id=SCIL_DIAGNOSTIC_ID,
        slug="scil",
        name="S.C.I.L. Performance Strategie",
        description=(
            "Die S.C.I.L. Performance Strategie misst Wirkungskompetenz in 16 Frequenzen "
            "ueber vier Bereiche: Sensus, Corpus, Intellektus und Lingua. "
            "Entwickelt von Andreas Bornhaeusser."
        ),
        category=DiagnosticCategory.COMMUNICATION,
        scientific_basis=(
            "Empirisch validiert: Retest-Reliabilitaet ueber 6 Monate, "
            "Kriteriumsvaliditaet mit 1.080 Selbst-/Fremdvergleichen. "
            "Keine geschlechts-/alters-/berufsgruppenspezifischen Signifikanzen."
        ),
        version="2.0",
        config=SCIL_CONFIG,
        min_questions=100,
        max_questions=120,
        available_tiers=["S", "M", "L", "XL"],
    )
    session.add(diagnostic)
    await session.commit()
    await session.refresh(diagnostic)
    return diagnostic
