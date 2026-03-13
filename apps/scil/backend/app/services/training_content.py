"""SCIL Training Content Library — Seed data for daily micro-training modules.

Provides a baseline library of training content mapped to the 4 SCIL areas
and their 16 frequencies. Content is structured for AI-personalized delivery.
"""

# Content items: each dict maps to a LearningContent record
# Format: slug, title, description, content_type, area, target_frequency,
#          difficulty, duration_minutes, body (markdown/structure), tags

TRAINING_CONTENT_LIBRARY: list[dict] = [
    # -----------------------------------------------------------------------
    # SENSUS — Beziehung & Emotion
    # -----------------------------------------------------------------------
    {
        "slug": "sensus-empathy-reflection",
        "title": "Empathie im Alltag",
        "description": "Reflektiere deine empathischen Reaktionen in Alltagssituationen und staerke dein Einfuehlungsvermoegen.",
        "content_type": "reflection",
        "area": "sensus",
        "target_frequency": "S01",
        "difficulty": 1,
        "duration_minutes": 10,
        "body": {
            "instruction": "Denke an eine Situation heute, in der jemand eine starke Emotion gezeigt hat. Wie hast du reagiert? Was haettest du anders machen koennen?",
            "prompts": [
                "Welche Emotion hast du bei der anderen Person wahrgenommen?",
                "Wie hast du dich dabei gefuehlt?",
                "Was war deine erste Reaktion?",
                "Wie haettest du mehr Empathie zeigen koennen?",
            ],
        },
        "tags": ["empathie", "beziehung", "reflexion", "einsteiger"],
    },
    {
        "slug": "sensus-active-listening",
        "title": "Aktives Zuhoeren",
        "description": "Uebung zur Verbesserung deiner Zuhoerqualitaet in Gespraechen.",
        "content_type": "exercise",
        "area": "sensus",
        "target_frequency": "S02",
        "difficulty": 2,
        "duration_minutes": 15,
        "body": {
            "instruction": "Fuehre heute ein bewusstes Gespraech, in dem du nur zuhoerst. Keine Ratschlaege, kein Unterbrechen.",
            "steps": [
                "Waehle ein Gespraech (Kolleg:in, Partner:in, Freund:in)",
                "Setze dir das Ziel: 5 Minuten nur zuhoeren",
                "Nutze Blickkontakt und nicke bestaetigend",
                "Fasse am Ende zusammen, was du gehoert hast",
                "Frage: 'Habe ich das richtig verstanden?'",
            ],
            "reflection_prompt": "Wie hat sich das bewusste Zuhoeren angefuehlt? Was hast du bemerkt?",
        },
        "tags": ["zuhoeren", "kommunikation", "beziehung", "uebung"],
    },
    {
        "slug": "sensus-emotional-awareness",
        "title": "Emotionale Selbstwahrnehmung",
        "description": "Lerne deine eigenen Emotionen besser zu erkennen und zu benennen.",
        "content_type": "exercise",
        "area": "sensus",
        "target_frequency": "S03",
        "difficulty": 1,
        "duration_minutes": 10,
        "body": {
            "instruction": "Emotionales Check-in: Nimm dir 5 Minuten Zeit und scanne deinen emotionalen Zustand.",
            "steps": [
                "Schliesse die Augen und atme 3 Mal tief durch",
                "Frage dich: Was fuehle ich gerade?",
                "Benenne die Emotion moeglichst genau (nicht nur 'gut/schlecht')",
                "Wo spuerst du die Emotion im Koerper?",
                "Akzeptiere die Emotion ohne sie zu bewerten",
            ],
            "emotion_wheel": ["Freude", "Traurigkeit", "Wut", "Angst", "Ueberraschung", "Ekel", "Vertrauen", "Neugier"],
        },
        "tags": ["emotionen", "selbstwahrnehmung", "achtsamkeit"],
    },
    {
        "slug": "sensus-trust-building",
        "title": "Vertrauen aufbauen",
        "description": "Strategien zum Aufbau von Vertrauen in beruflichen Beziehungen.",
        "content_type": "article",
        "area": "sensus",
        "target_frequency": "S04",
        "difficulty": 2,
        "duration_minutes": 8,
        "body": {
            "content_markdown": (
                "## Vertrauen aufbauen\n\n"
                "Vertrauen ist die Grundlage jeder erfolgreichen Zusammenarbeit. "
                "Es entsteht durch **Konsistenz**, **Transparenz** und **Verletzlichkeit**.\n\n"
                "### 3 Schritte fuer heute:\n"
                "1. **Halte ein Versprechen** — auch ein kleines\n"
                "2. **Teile eine ehrliche Einschaetzung** — keine Schoenrederei\n"
                "3. **Gib einen Fehler zu** — Verletzlichkeit schafft Naehe\n\n"
                "### Reflexionsfrage:\n"
                "Wem in deinem beruflichen Umfeld vertraust du am meisten? Warum?"
            ),
        },
        "tags": ["vertrauen", "beziehung", "fuehrung"],
    },

    # -----------------------------------------------------------------------
    # CORPUS — Koerpersprache & Praesenz
    # -----------------------------------------------------------------------
    {
        "slug": "corpus-power-posing",
        "title": "Koerpersprache und Praesenz",
        "description": "Uebung zur bewussten Koerpersprache fuer mehr Praesenz und Selbstvertrauen.",
        "content_type": "exercise",
        "area": "corpus",
        "target_frequency": "C01",
        "difficulty": 1,
        "duration_minutes": 10,
        "body": {
            "instruction": "Praesenz-Uebung: Nutze deine Koerpersprache bewusst, um Praesenz zu zeigen.",
            "steps": [
                "Stehe aufrecht, Schultern zurueck, Brust offen",
                "Atme tief in den Bauch (4 Sekunden ein, 4 aus)",
                "Halte diese Haltung fuer 2 Minuten",
                "Beobachte: Wie veraendert sich dein Gefuehl?",
                "Nutze diese Haltung vor dem naechsten Meeting",
            ],
        },
        "tags": ["koerpersprache", "praesenz", "selbstvertrauen"],
    },
    {
        "slug": "corpus-breathing-exercise",
        "title": "Atemtechnik fuer Stresssituationen",
        "description": "Box-Breathing: Eine einfache Atemtechnik fuer sofortige Beruhigung.",
        "content_type": "exercise",
        "area": "corpus",
        "target_frequency": "C02",
        "difficulty": 1,
        "duration_minutes": 5,
        "body": {
            "instruction": "Box-Breathing: 4-4-4-4 Atemtechnik",
            "steps": [
                "Einatmen: 4 Sekunden",
                "Halten: 4 Sekunden",
                "Ausatmen: 4 Sekunden",
                "Halten: 4 Sekunden",
                "Wiederhole 4 Runden",
            ],
            "tip": "Nutze diese Technik vor wichtigen Gespraechen oder bei Stress.",
        },
        "tags": ["atmung", "stress", "entspannung", "koerper"],
    },
    {
        "slug": "corpus-energy-management",
        "title": "Energie-Management",
        "description": "Lerne, deine koerperliche Energie bewusst zu steuern.",
        "content_type": "reflection",
        "area": "corpus",
        "target_frequency": "C03",
        "difficulty": 2,
        "duration_minutes": 10,
        "body": {
            "instruction": "Energie-Tagebuch: Tracke dein Energielevel ueber den Tag.",
            "prompts": [
                "Wann heute hattest du die meiste Energie?",
                "Wann war dein Energietief?",
                "Was hat deine Energie gesteigert?",
                "Was hat sie gesenkt?",
                "Wie koenntest du morgen deine Hochphasen besser nutzen?",
            ],
        },
        "tags": ["energie", "produktivitaet", "koerper"],
    },
    {
        "slug": "corpus-nonverbal-signals",
        "title": "Nonverbale Signale lesen",
        "description": "Schaerfe deine Wahrnehmung fuer die Koerpersprache anderer.",
        "content_type": "exercise",
        "area": "corpus",
        "target_frequency": "C04",
        "difficulty": 3,
        "duration_minutes": 12,
        "body": {
            "instruction": "Beobachtungsuebung: Achte heute in 3 Gespraechen bewusst auf nonverbale Signale.",
            "observation_points": [
                "Koerperhaltung (offen/geschlossen)",
                "Blickkontakt (viel/wenig)",
                "Gestik (lebendig/zurueckhaltend)",
                "Gesichtsausdruck (kongruent zur Aussage?)",
                "Rauemliches Verhalten (Naehe/Distanz)",
            ],
            "reflection_prompt": "Was hast du bemerkt, das dir sonst entgangen waere?",
        },
        "tags": ["koerpersprache", "beobachtung", "nonverbal"],
    },

    # -----------------------------------------------------------------------
    # INTELLEKTUS — Logik & Struktur
    # -----------------------------------------------------------------------
    {
        "slug": "intellektus-decision-framework",
        "title": "Entscheidungs-Framework",
        "description": "Strukturiertes Vorgehen fuer bessere Entscheidungen.",
        "content_type": "exercise",
        "area": "intellektus",
        "target_frequency": "I01",
        "difficulty": 2,
        "duration_minutes": 15,
        "body": {
            "instruction": "Wende das 10-10-10 Framework auf eine anstehende Entscheidung an.",
            "steps": [
                "Waehle eine anstehende Entscheidung",
                "Frage: Wie werde ich in 10 Minuten darueber denken?",
                "Frage: Wie werde ich in 10 Monaten darueber denken?",
                "Frage: Wie werde ich in 10 Jahren darueber denken?",
                "Welche Perspektive gibt den besten Aufschluss?",
            ],
        },
        "tags": ["entscheidung", "logik", "framework", "struktur"],
    },
    {
        "slug": "intellektus-critical-thinking",
        "title": "Kritisches Denken",
        "description": "Uebung zum Hinterfragen von Annahmen und Denkmustern.",
        "content_type": "reflection",
        "area": "intellektus",
        "target_frequency": "I02",
        "difficulty": 3,
        "duration_minutes": 12,
        "body": {
            "instruction": "Annahmen-Check: Hinterfrage eine deiner Ueberzeugungen.",
            "prompts": [
                "Welche Ueberzeugung hast du, die du noch nie hinterfragt hast?",
                "Woher stammt diese Ueberzeugung?",
                "Welche Gegenargumente gibt es?",
                "Was wuerde sich aendern, wenn du falsch laegst?",
                "Wie sicher bist du dir auf einer Skala von 1-10?",
            ],
        },
        "tags": ["kritisches-denken", "reflexion", "annahmen"],
    },
    {
        "slug": "intellektus-problem-solving",
        "title": "Problemloesung mit der 5-Why Methode",
        "description": "Komme der Ursache eines Problems auf den Grund.",
        "content_type": "exercise",
        "area": "intellektus",
        "target_frequency": "I03",
        "difficulty": 2,
        "duration_minutes": 10,
        "body": {
            "instruction": "5-Why Methode: Frage 5 Mal 'Warum?', um die Kernursache zu finden.",
            "steps": [
                "Definiere ein aktuelles Problem",
                "Frage: Warum tritt dieses Problem auf? → Antwort 1",
                "Frage: Warum? (basierend auf Antwort 1) → Antwort 2",
                "Frage: Warum? → Antwort 3",
                "Frage: Warum? → Antwort 4",
                "Frage: Warum? → Antwort 5 (Kernursache)",
            ],
            "tip": "Die echte Ursache liegt selten an der Oberflaeche.",
        },
        "tags": ["problemloesung", "analyse", "methodik"],
    },
    {
        "slug": "intellektus-strategic-thinking",
        "title": "Strategisches Denken",
        "description": "Uebe strategisches Denken anhand realer Szenarien.",
        "content_type": "article",
        "area": "intellektus",
        "target_frequency": "I04",
        "difficulty": 3,
        "duration_minutes": 10,
        "body": {
            "content_markdown": (
                "## Strategisches Denken trainieren\n\n"
                "Strategisches Denken bedeutet, das grosse Ganze zu sehen "
                "und langfristige Konsequenzen zu antizipieren.\n\n"
                "### Uebung: Die Zukunftsrueckschau\n"
                "1. Stelle dir vor: Es ist 1 Jahr von heute\n"
                "2. Dein wichtigstes Ziel ist erreicht\n"
                "3. Schreibe auf: Welche 5 Schritte haben dazu gefuehrt?\n"
                "4. Arbeite rueckwaerts: Was war der erste Schritt?\n\n"
                "### Reflexion:\n"
                "Welchen dieser Schritte kannst du diese Woche beginnen?"
            ),
        },
        "tags": ["strategie", "planung", "langfristig"],
    },

    # -----------------------------------------------------------------------
    # LINGUA — Sprache & Ausdruck
    # -----------------------------------------------------------------------
    {
        "slug": "lingua-clear-communication",
        "title": "Klar kommunizieren",
        "description": "Uebung fuer praeziese und verstaendliche Kommunikation.",
        "content_type": "exercise",
        "area": "lingua",
        "target_frequency": "L01",
        "difficulty": 2,
        "duration_minutes": 10,
        "body": {
            "instruction": "Die 30-Sekunden-Regel: Bringe deine Kernbotschaft in 30 Sekunden auf den Punkt.",
            "steps": [
                "Waehle ein Thema, das du jemandem erklaeren moechtest",
                "Formuliere die Kernbotschaft in einem Satz",
                "Ergaenze maximal 2 Unterstuetzungspunkte",
                "Ueebe laut (Timer: 30 Sekunden)",
                "Kuerze, bis es passt",
            ],
            "tip": "Wenn du es nicht in 30 Sekunden erklaeren kannst, verstehst du es noch nicht gut genug.",
        },
        "tags": ["kommunikation", "klarheit", "praesentation"],
    },
    {
        "slug": "lingua-feedback-giving",
        "title": "Feedback geben mit SBI",
        "description": "Lerne konstruktives Feedback mit dem Situation-Behavior-Impact Modell.",
        "content_type": "exercise",
        "area": "lingua",
        "target_frequency": "L02",
        "difficulty": 2,
        "duration_minutes": 12,
        "body": {
            "instruction": "SBI-Feedback Uebung: Formuliere ein konkretes Feedback.",
            "steps": [
                "Situation: Wann und wo? (z.B. 'Im Meeting gestern...')",
                "Behavior: Was genau wurde gesagt/getan? (ohne Bewertung)",
                "Impact: Welche Wirkung hatte es? (auf dich, das Team, das Ergebnis)",
                "Schreibe dein Feedback auf",
                "Pruefe: Ist es spezifisch, nicht wertend, und hilfreich?",
            ],
        },
        "tags": ["feedback", "kommunikation", "fuehrung"],
    },
    {
        "slug": "lingua-storytelling",
        "title": "Storytelling im Business",
        "description": "Nutze die Kraft von Geschichten fuer wirkungsvolle Kommunikation.",
        "content_type": "article",
        "area": "lingua",
        "target_frequency": "L03",
        "difficulty": 3,
        "duration_minutes": 10,
        "body": {
            "content_markdown": (
                "## Storytelling im Business\n\n"
                "Geschichten bleiben 22x besser im Gedaechtnis als reine Fakten.\n\n"
                "### Die STAR-Struktur:\n"
                "- **S**ituation: Setze die Szene\n"
                "- **T**ask: Was war die Herausforderung?\n"
                "- **A**ction: Was hast du getan?\n"
                "- **R**esult: Was war das Ergebnis?\n\n"
                "### Deine Uebung:\n"
                "Bereite eine Erfolgsgeschichte mit STAR vor, "
                "die du in deinem naechsten Gespraech nutzen kannst."
            ),
        },
        "tags": ["storytelling", "kommunikation", "praesentation"],
    },
    {
        "slug": "lingua-questioning-skills",
        "title": "Die Kunst des Fragens",
        "description": "Bessere Fragen stellen fuer tiefere Gespraeche und Erkenntnisse.",
        "content_type": "exercise",
        "area": "lingua",
        "target_frequency": "L04",
        "difficulty": 2,
        "duration_minutes": 10,
        "body": {
            "instruction": "Fragen-Upgrade: Verwandle geschlossene in offene Fragen.",
            "examples": [
                {"closed": "War das Meeting gut?", "open": "Was war der wertvollste Moment im Meeting?"},
                {"closed": "Bist du zufrieden?", "open": "Was wuerdest du beim naechsten Mal anders machen?"},
                {"closed": "Hast du verstanden?", "open": "Wie wuerdest du das in deinen eigenen Worten erklaeren?"},
            ],
            "challenge": "Stelle heute in 3 Gespraechen mindestens eine offene Frage, die mit 'Was', 'Wie' oder 'Welche' beginnt.",
        },
        "tags": ["fragen", "kommunikation", "coaching"],
    },

    # -----------------------------------------------------------------------
    # GENERAL — Cross-Area Content
    # -----------------------------------------------------------------------
    {
        "slug": "general-weekly-review",
        "title": "Wochen-Reflexion",
        "description": "Reflektiere deine Woche und setze Intentionen fuer die naechste.",
        "content_type": "reflection",
        "area": "general",
        "target_frequency": None,
        "difficulty": 1,
        "duration_minutes": 15,
        "body": {
            "instruction": "Wochen-Reflexion: Schau zurueck und plane voraus.",
            "prompts": [
                "Was war mein groesster Erfolg diese Woche?",
                "Was habe ich ueber mich selbst gelernt?",
                "Welche SCIL-Dimension habe ich am meisten trainiert?",
                "Was moechte ich naechste Woche anders machen?",
                "Welches eine Ziel setze ich mir fuer die kommende Woche?",
            ],
        },
        "tags": ["reflexion", "wochenrueckblick", "planung"],
    },
    {
        "slug": "general-morning-intention",
        "title": "Morgen-Intention",
        "description": "Starte den Tag mit einer bewussten Intention.",
        "content_type": "reflection",
        "area": "general",
        "target_frequency": None,
        "difficulty": 1,
        "duration_minutes": 5,
        "body": {
            "instruction": "Setze eine Intention fuer den heutigen Tag.",
            "prompts": [
                "Welche eine Eigenschaft moechte ich heute staerker zeigen?",
                "In welcher Situation kann ich diese Eigenschaft heute einsetzen?",
                "Was werde ich heute bewusst anders machen als gestern?",
            ],
        },
        "tags": ["morgenroutine", "intention", "achtsamkeit"],
    },
]


async def seed_training_content(db) -> int:
    """Seed the learning content library. Returns count of created items."""
    from sqlalchemy import select
    from bfg_core.models.training import LearningContent, ContentType, ContentArea

    count = 0
    for item in TRAINING_CONTENT_LIBRARY:
        # Check if already exists
        result = await db.execute(
            select(LearningContent).where(LearningContent.slug == item["slug"])
        )
        if result.scalar_one_or_none():
            continue

        content = LearningContent(
            slug=item["slug"],
            title=item["title"],
            description=item["description"],
            content_type=ContentType(item["content_type"]),
            area=ContentArea(item["area"]),
            target_frequency=item.get("target_frequency"),
            difficulty=item.get("difficulty", 2),
            duration_minutes=item.get("duration_minutes", 10),
            body=item.get("body", {}),
            video_url=item.get("video_url"),
            tags=item.get("tags", []),
        )
        db.add(content)
        count += 1

    if count > 0:
        await db.commit()
    return count
