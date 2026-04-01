import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.diagnostic import Diagnostic, DiagnosticCategory


SEED_DIAGNOSTICS = [
    # ── 1. SCIL Profile (eigenes IP) ──
    {
        "slug": "scil",
        "name": "S.C.I.L. Profile — Wirkungskompetenz",
        "description": "Misst Ihre kommunikative Wirkung über 4 Frequenzbereiche (Sensus, Corpus, Intellektus, Lingua) mit 16 Interaktionsfaktoren.",
        "category": DiagnosticCategory.COMMUNICATION,
        "scientific_basis": "Entwickelt von Andreas Bornhäusser mit Universität Duisburg-Essen. 30+ Jahre Forschung, 140.000+ Teilnehmer.",
        "config": {
            "frequencies": {
                "sensus": ["inner_presence", "conviction", "moment_focus", "emotionality"],
                "corpus": ["appearance", "gesture", "facial_expression", "spatial_presence"],
                "intellektus": ["analytics", "goal_orientation", "structure", "objectivity"],
                "lingua": ["voice", "articulation", "eloquence", "imagery"],
            }
        },
        "min_questions": 24,
        "max_questions": 100,
    },
    # ── 2. Big Five / OCEAN (IPIP = Public Domain) ──
    {
        "slug": "big_five",
        "name": "Big Five — Persönlichkeitsprofil (OCEAN)",
        "description": "Der wissenschaftliche Goldstandard der Persönlichkeitsdiagnostik. Misst Offenheit, Gewissenhaftigkeit, Extraversion, Verträglichkeit und Neurotizismus.",
        "category": DiagnosticCategory.PERSONALITY,
        "scientific_basis": "IPIP-NEO-120/300. Public Domain (3.329 Items frei nutzbar). Kulturübergreifend validiert.",
        "config": {
            "dimensions": ["openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"],
            "facets_per_dimension": 6,
        },
        "min_questions": 20,
        "max_questions": 300,
    },
    # ── 3. Werteprofil (Schwartz) ──
    {
        "slug": "values_schwartz",
        "name": "Werteprofil (Schwartz)",
        "description": "Identifiziert Ihre 19 universellen Grundwerte und deren Hierarchie. Zeigt, was Sie wirklich antreibt.",
        "category": DiagnosticCategory.VALUES,
        "scientific_basis": "Schwartz PVQ-RR. Kulturübergreifend validiert über 80+ Länder. CC BY-NC-ND 3.0, eigene Items für Konstrukt.",
        "config": {"values_count": 19},
        "min_questions": 20,
        "max_questions": 57,
    },
    # ── 4. Emotionale Intelligenz (eigene Items) ──
    {
        "slug": "eq_trait",
        "name": "Emotionale Intelligenz (Trait-EI)",
        "description": "Misst 15 Facetten Ihrer emotionalen Intelligenz in 4 Faktoren: Wohlbefinden, Selbstkontrolle, Emotionalität, Soziabilität.",
        "category": DiagnosticCategory.EMOTIONAL_INTELLIGENCE,
        "scientific_basis": "Eigene Items für EI-Konstrukt (Konstrukt ist frei). 15 Facetten in 4 Faktoren, inspiriert von TEIQue.",
        "config": {
            "factors": ["wellbeing", "self_control", "emotionality", "sociability"],
            "facets": 15,
        },
        "min_questions": 20,
        "max_questions": 153,
    },
    # ── 5. Resilienz (eigene Items, APA-Framework) ──
    {
        "slug": "resilience",
        "name": "Resilienz-Profil",
        "description": "Erfasst Ihre psychische Widerstandsfähigkeit und Erholungsfähigkeit über 5 Dimensionen.",
        "category": DiagnosticCategory.RESILIENCE,
        "scientific_basis": "Eigene Items basierend auf APA-Resilienz-Framework. CD-RISC ist proprietär — wir nutzen eigene Formulierungen.",
        "config": {
            "dimensions": [
                "personal_competence", "trust_tolerance",
                "positive_acceptance", "control", "meaning_making",
            ]
        },
        "min_questions": 10,
        "max_questions": 25,
    },
    # ── 6. 360° Feedback (eigene Implementierung) ──
    {
        "slug": "feedback_360",
        "name": "360° Feedback — Multi-Rater-Assessment",
        "description": "KI-geführtes konversationelles 360°-Feedback mit 5 Perspektiven, SCIL-Mapping und Johari-Window.",
        "category": DiagnosticCategory.LEADERSHIP,
        "scientific_basis": "Eigene Implementierung. Open Frameworks verfügbar (Open360, Apache 2.0). STAR-Methodik.",
        "config": {
            "perspectives": ["self", "supervisor", "peer", "report", "external"],
            "competencies": [
                "persuasion", "analytical_thinking", "empathy", "presence",
                "strategic_thinking", "storytelling", "team_leadership", "clarity",
            ],
            "min_raters_per_group": 3,
        },
        "min_questions": 12,
        "max_questions": 20,
    },
    # ── 7. Stressbewältigung (eigene Items) ──
    {
        "slug": "stress_coping",
        "name": "Stressbewältigungs-Profil",
        "description": "Analysiert Ihr Stressverhalten und Ihre bevorzugten Coping-Strategien in 6 Dimensionen.",
        "category": DiagnosticCategory.RESILIENCE,
        "scientific_basis": "Eigene Items. Konstrukt frei (nicht persolog® Stress-Modell). Basiert auf Lazarus & Folkman Transactional Model.",
        "config": {
            "dimensions": [
                "problem_focused_coping", "emotion_focused_coping",
                "social_support", "avoidance", "proactive_coping", "meaning_making",
            ]
        },
        "min_questions": 18,
        "max_questions": 40,
    },
    # ── 8. Teamrollen (Big-Five-basiert, eigenes Modell) ──
    {
        "slug": "team_roles",
        "name": "Teamrollen-Profil",
        "description": "Entdecken Sie Ihr Beitragsprofil in Teams. Big-Five-basiert abgeleitet — eigenes Modell.",
        "category": DiagnosticCategory.TEAM,
        "scientific_basis": "Eigene Items und Modell. Big-Five-basiert ableitbar. Belbin® ist geschützt — eigenes Modell.",
        "config": {
            "roles": [
                "strategist", "innovator", "coordinator", "implementer",
                "communicator", "analyst", "supporter", "finisher",
            ]
        },
        "min_questions": 20,
        "max_questions": 48,
    },
    # ── 9. Kommunikationsstil (NLP-basiert, eigen) ──
    {
        "slug": "communication_style",
        "name": "Kommunikationsstil-Analyse",
        "description": "NLP-basierte Analyse Ihrer Kommunikationspräferenzen aus realer Interaktion mit dem KI-Agenten.",
        "category": DiagnosticCategory.COMMUNICATION,
        "scientific_basis": "Eigene Implementierung. NLP-basierte Analyse aus realer Kommunikation.",
        "config": {
            "dimensions": [
                "directness", "formality", "emotionality", "detail_orientation",
                "persuasion_style", "listening_quality",
            ]
        },
        "min_questions": 15,
        "max_questions": 30,
    },
    # ── 10. Motivation / SDT (Deci & Ryan) ──
    {
        "slug": "motivation_sdt",
        "name": "Motivationsprofil (Self-Determination)",
        "description": "Misst Ihre intrinsische und extrinsische Motivation nach Self-Determination Theory (Deci & Ryan).",
        "category": DiagnosticCategory.MOTIVATION,
        "scientific_basis": "Self-Determination Theory (Deci & Ryan). Wissenschaftlich offen. Eigene Items.",
        "config": {
            "dimensions": [
                "intrinsic_motivation", "identified_regulation",
                "introjected_regulation", "external_regulation",
                "amotivation",
            ],
            "needs": ["autonomy", "competence", "relatedness"],
        },
        "min_questions": 18,
        "max_questions": 42,
    },
    # ── 11. Denkstilpräferenzen (eigenes Modell) ──
    {
        "slug": "thinking_styles",
        "name": "Denkstilpräferenzen",
        "description": "4-Quadranten Denkmuster — eigenes Modell inspiriert von Whole Brain Thinking (HBDI® ist geschützt).",
        "category": DiagnosticCategory.COGNITION,
        "scientific_basis": "Eigene Items und Modell. HBDI® ist geschützt — eigenes 4-Quadranten-Modell mit ausreichender kreativer Distanz.",
        "config": {
            "quadrants": [
                "analytical", "practical", "relational", "experimental",
            ]
        },
        "min_questions": 20,
        "max_questions": 40,
    },
    # ── 12. Kognitive Flexibilität (IRT-basiert, eigen) ──
    {
        "slug": "cognitive_flexibility",
        "name": "Kognitive Flexibilität",
        "description": "IRT-basierte adaptive Denkaufgaben zur Messung Ihrer mentalen Agilität und Umstellfähigkeit.",
        "category": DiagnosticCategory.COGNITION,
        "scientific_basis": "Item Response Theory (IRT). Eigene Implementierung mit adaptivem Algorithmus.",
        "config": {
            "dimensions": [
                "task_switching", "creative_flexibility",
                "cognitive_inhibition", "perspective_taking",
            ],
            "adaptive": True,
        },
        "min_questions": 15,
        "max_questions": 30,
    },
]


async def seed_diagnostics(db: AsyncSession):
    """Seed the diagnostics table if empty."""
    result = await db.execute(select(Diagnostic).limit(1))
    if result.scalar_one_or_none():
        return  # Already seeded

    for diag_data in SEED_DIAGNOSTICS:
        diag = Diagnostic(**diag_data)
        db.add(diag)

    await db.commit()
