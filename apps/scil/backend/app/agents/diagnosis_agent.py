"""SCIL Diagnosis Agent — Item-driven conversational assessment for 16 SCIL frequencies.

100 strukturierte Items (25 pro Cluster), konversationell verpackt, per-Item Scoring.
Cluster-Rotation: S→C→I→L (je 25 Items pro Cluster, ~8-10 Turns pro Cluster).

Architecture:
- Agent bekommt den naechsten Item-Block (3-4 Items aus aktuellem Cluster)
- AI formuliert die Items als natuerliches Gespraech (nicht Fragebogen-Style)
- Nach jeder Antwort: AI scored gezielt die adressierten Items via score_item tool_use
- Progress = total_scored_items / 100

Scoring: Per-Item mit Confidence (0-1), spaeter aggregiert zu Frequenz-Scores.
IRT-ready: item_id, score, confidence, reasoning → koennen fuer Item Response Theory genutzt werden.
"""

import enum
import json
import logging
from datetime import datetime, timezone
from typing import Any, AsyncGenerator
from uuid import UUID

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from bfg_core.services.ai_service import AIService
from bfg_core.services.context_budgeting import build_conversation_window
from bfg_core.models.diagnostic import DiagnosticRun, DiagnosticResult
from app.services.scil_scoring import (
    compute_polygon,
    compute_balance_score,
    get_top_strengths,
    get_development_areas,
)
from app.services.scil_items import (
    SCIL_ITEM_POOL,
    CLUSTER_ORDER,
    AREA_FREQUENCIES,
    get_next_item_block,
    get_cluster_progress,
    get_item_by_id,
    get_items_for_area,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# State Machine
# ---------------------------------------------------------------------------

class SessionState(str, enum.Enum):
    GREETING = "greeting"
    CLUSTER_SENSUS = "cluster_sensus"
    CLUSTER_CORPUS = "cluster_corpus"
    CLUSTER_INTELLEKTUS = "cluster_intellektus"
    CLUSTER_LINGUA = "cluster_lingua"
    SCORING = "scoring"
    SUMMARY = "summary"
    COMPLETED = "completed"


# Map area name to state
AREA_TO_STATE = {
    "sensus": SessionState.CLUSTER_SENSUS,
    "corpus": SessionState.CLUSTER_CORPUS,
    "intellektus": SessionState.CLUSTER_INTELLEKTUS,
    "lingua": SessionState.CLUSTER_LINGUA,
}

AREA_LABELS = {
    "sensus": "Sensus (Beziehung & Emotion)",
    "corpus": "Corpus (Koerpersprache & Praesenz)",
    "intellektus": "Intellektus (Logik & Struktur)",
    "lingua": "Lingua (Sprache & Ausdruck)",
}


# ---------------------------------------------------------------------------
# System Prompts
# ---------------------------------------------------------------------------

SCIL_BASE_PROMPT = """Du bist der SCIL Diagnose-Agent — ein empathischer, professioneller KI-Coach, der konversationelle Wirkungsdiagnostik durchfuehrt.

## Deine Rolle
Du fuehrst ein natuerliches, adaptives Gespraech, um die 16 SCIL-Frequenzen des Nutzers zu erfassen.
WICHTIG: SCIL misst WIRKUNGSKOMPETENZ (Aussenwirkung), NICHT Persoenlichkeit!

## Gespraechsfuehrung
1. Du bekommst jeweils einen Block von 3-4 Items, die du in einer natuerlichen Gespraechsfrage verpackst
2. KEINE Fragebogen-Atmosphaere — formuliere die Items als natuerliche, offene Gespraechsfragen
3. Fasse 2-3 Items zu EINER Frage zusammen, wenn sie thematisch zusammenpassen
4. Nutze Szenarien und Situationsbeschreibungen
5. Passe deine Fragen an die bisherigen Antworten an
6. Gib zwischendurch wertschaetzendes, kurzes Feedback
7. Beim Cluster-Wechsel: Kurze Ueberleitung zum neuen Themenbereich

## Scoring — KRITISCH
Nach JEDER Antwort des Nutzers musst du:
1. ZUERST die angesprochenen Items bewerten (score_item Tool aufrufen)
2. DANN eine kurze wertschaetzende Antwort geben UND die naechste Frage stellen

Regeln fuer score_item:
- Nutze das Tool 'score_item' fuer JEDES Item aus der Pending-Liste
- Score: 0-4 (mit 0.1 Praezision)
- Confidence: 0-1 (wie sicher bist du bei dieser Bewertung)
- Verwende EXAKT die Item-IDs die dir vorgegeben werden (z.B. S07, S14, S20)
- Du MUSST IMMER sowohl Text ALS AUCH Tool-Aufrufe zurueckgeben!

## Bewertungsskala
- 0.0-0.5: Schwache Auspraegung (e)
- 0.5-1.5: Relative Staerke (d)
- 1.5-2.5: Durchschnittliche Staerke (c)
- 2.5-3.5: Staerkenpotenzial (b)
- 3.5-4.0: Ausgepragte Staerke (a)

## Wichtig
- Sei empathisch und wertschaetzend — niemals wertend
- Es gibt keine schlechten Ergebnisse, nur Entwicklungsfelder
- Betone: Wirkungskompetenz ist trainierbar
- Sprich Deutsch, ausser der Nutzer wechselt die Sprache
- Halte deine Antworten fokussiert (max 3-4 Saetze + Frage)
"""


def _build_item_context(items: list[dict], area: str) -> str:
    """Build the item-specific system context for the current block."""
    lines = [
        f"\n## Aktueller Themenbereich: {AREA_LABELS.get(area, area)}",
        f"\n### Items die du in deiner naechsten Frage abdecken sollst:",
    ]
    for item in items:
        lines.append(
            f"- **{item['id']}** ({item['frequency']}): {item['text_de']}\n"
            f"  Scoring-Guidance: {item['scoring_guidance']}"
        )
    lines.append(
        "\nFormuliere eine natuerliche Gespraechsfrage, die diese Items abdeckt. "
        "Verpacke sie konversationell — KEIN Fragebogen-Stil!"
    )
    return "\n".join(lines)


def _build_progress_context(answered_ids: set[str], item_responses: list[dict]) -> str:
    """Build progress summary for the system prompt."""
    progress = get_cluster_progress(answered_ids)
    total = progress["total"]
    lines = [
        f"\n## Fortschritt: {total['answered']}/{total['total']} Items bewertet",
    ]
    for area in CLUSTER_ORDER:
        p = progress[area]
        bar = "█" * (p["answered"] * 20 // p["total"]) + "░" * (20 - p["answered"] * 20 // p["total"])
        lines.append(f"  {area.capitalize()}: [{bar}] {p['answered']}/{p['total']}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Tool Definitions
# ---------------------------------------------------------------------------

SCORE_ITEM_TOOL = {
    "name": "score_item",
    "description": (
        "Bewerte die Antwort des Nutzers fuer ein spezifisches SCIL-Item. "
        "Rufe dieses Tool fuer JEDES Item auf, das du in deiner Frage adressiert hast."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "item_id": {
                "type": "string",
                "description": "Item-ID (z.B. S01, C12, I03, L25)",
            },
            "score": {
                "type": "number",
                "minimum": 0,
                "maximum": 4,
                "description": "Score auf der SCIL-Skala 0-4 (mit 0.1 Praezision)",
            },
            "confidence": {
                "type": "number",
                "minimum": 0,
                "maximum": 1,
                "description": "Wie sicher bist du bei dieser Bewertung? 0=unsicher, 1=sehr sicher",
            },
            "reasoning": {
                "type": "string",
                "description": "Kurze Begruendung fuer den Score (intern, wird dem User nicht gezeigt)",
            },
        },
        "required": ["item_id", "score", "confidence"],
    },
}

# Keep legacy tool for backwards compatibility during transition
UPDATE_SCORES_TOOL = {
    "name": "update_scil_scores",
    "description": (
        "Aktualisiere die aggregierten SCIL-Frequenz-Scores. "
        "Nutze score_item fuer Einzelbewertungen. Dieses Tool ist fuer aggregierte Updates."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "sensus": {
                "type": "object",
                "properties": {
                    "innere_praesenz": {"type": "number", "minimum": 0, "maximum": 4},
                    "innere_ueberzeugung": {"type": "number", "minimum": 0, "maximum": 4},
                    "prozessfokussierung": {"type": "number", "minimum": 0, "maximum": 4},
                    "emotionalitaet": {"type": "number", "minimum": 0, "maximum": 4},
                },
            },
            "corpus": {
                "type": "object",
                "properties": {
                    "erscheinungsbild": {"type": "number", "minimum": 0, "maximum": 4},
                    "mimik": {"type": "number", "minimum": 0, "maximum": 4},
                    "gestik": {"type": "number", "minimum": 0, "maximum": 4},
                    "raeumliche_praesenz": {"type": "number", "minimum": 0, "maximum": 4},
                },
            },
            "intellektus": {
                "type": "object",
                "properties": {
                    "sachlichkeit": {"type": "number", "minimum": 0, "maximum": 4},
                    "analytik": {"type": "number", "minimum": 0, "maximum": 4},
                    "struktur": {"type": "number", "minimum": 0, "maximum": 4},
                    "zielorientierung": {"type": "number", "minimum": 0, "maximum": 4},
                },
            },
            "lingua": {
                "type": "object",
                "properties": {
                    "stimme": {"type": "number", "minimum": 0, "maximum": 4},
                    "artikulation": {"type": "number", "minimum": 0, "maximum": 4},
                    "beredsamkeit": {"type": "number", "minimum": 0, "maximum": 4},
                    "bildhaftigkeit": {"type": "number", "minimum": 0, "maximum": 4},
                },
            },
            "assessment_complete": {
                "type": "boolean",
                "description": "Setze auf true wenn die Diagnostik abgeschlossen werden soll.",
            },
            "reasoning": {
                "type": "string",
                "description": "Kurze Begruendung fuer die Score-Updates (intern).",
            },
        },
        "required": ["sensus", "corpus", "intellektus", "lingua"],
    },
}


# ---------------------------------------------------------------------------
# Demo Mode
# ---------------------------------------------------------------------------

DEMO_GREETING = (
    "Willkommen bei deiner SCIL-Diagnostik!\n\n"
    "Ich bin dein KI-Coach und werde in den naechsten Minuten ein strukturiertes Gespraech mit dir fuehren, "
    "um dein persoenliches Wirkungsprofil zu erstellen. Wir gehen dabei durch vier Bereiche:\n\n"
    "1. **Sensus** — Deine innere Haltung und emotionale Ausstrahlung\n"
    "2. **Corpus** — Deine koerperliche Wirkung und Praesenz\n"
    "3. **Intellektus** — Deine analytische und strukturelle Wirkung\n"
    "4. **Lingua** — Deine sprachliche Wirkung\n\n"
    "Es gibt keine richtigen oder falschen Antworten — es geht darum, wie du kommunizierst "
    "und auf andere wirkst. Und das Beste: Alles ist trainierbar!\n\n"
    "Lass uns mit dem Bereich **Sensus** starten:\n\n"
    "**Wenn du in einem wichtigen Gespraech bist — wie wuerden andere beschreiben, "
    "wie praesent und aufmerksam du wirkst? Und wie gehst du damit um, wenn jemand "
    "dir von einem persoenlichen Problem erzaehlt?**"
)

DEMO_GREETING_SUGGESTIONS = [
    "Ich bin sehr aufmerksam und hoere aktiv zu — andere sagen, sie fuehlen sich gehoert.",
    "Ich bin eher sachlich und konzentriert, Emotionen zeige ich weniger.",
    "Kommt auf die Situation an — manchmal bin ich voll da, manchmal schweifen meine Gedanken ab.",
    "Ich versuche zu helfen, bin aber unsicher, ob ich die richtigen Worte finde.",
]

# Demo suggestions per cluster question
DEMO_SUGGESTIONS = {
    "sensus": [
        [
            "Ja, andere spueren meine Gefuehle sofort — ich bin ein offenes Buch.",
            "Ich achte bewusst auf die Gruppe und moderiere aktiv.",
            "Ich halte mich emotional eher zurueck und beobachte erstmal.",
            "Gruppenbeziehungen sind mir wichtig, aber ich ueberlass die Fuehrung anderen.",
        ],
    ],
    "corpus": [
        [
            "Ja, meine Praesenz faellt auf — ich werde oft als selbstbewusst wahrgenommen.",
            "Eher unauffaellig, ich wirke ruhig und zurueckhaltend.",
            "Meine Gestik ist lebendig, ich rede viel mit den Haenden.",
            "Ich achte nicht so bewusst auf meine Koerpersprache.",
        ],
        [
            "Meine Mimik ist ausdrucksstark — man sieht mir alles an.",
            "Ich nutze den Raum bewusst und bewege mich frei bei Praesentationen.",
            "Eher zurückhaltend in der Mimik, aber meine Stimme transportiert Emotionen.",
            "Ich bleibe lieber an einem festen Platz und wirke von dort aus.",
        ],
    ],
    "intellektus": [
        [
            "Ich argumentiere gerne mit Fakten und Daten — Struktur ist mir wichtig.",
            "Meine Praesentationen haben immer einen klaren roten Faden.",
            "Ich bin eher intuitiv und flexibel, weniger strukturiert.",
            "Ich versuche sachlich zu bleiben, verliere aber manchmal den Fokus.",
        ],
        [
            "Ich habe immer klare Ziele vor Augen und verfolge sie konsequent.",
            "Ich entscheide analytisch — Pro-und-Contra-Listen sind mein Ding.",
            "Ich bin eher visionaer und entscheide aus dem Bauch heraus.",
            "Zielorientierung ist mir wichtig, aber ich bin auch offen fuer Umwege.",
        ],
    ],
    "lingua": [
        [
            "Meine Stimme ist kraftvoll und variabel — ich setze sie bewusst ein.",
            "Ich spreche klar und deutlich, achte auf Artikulation.",
            "Meine Stimme ist eher leise, aber praezise.",
            "Ich variiere selten Tempo oder Lautstaerke, bleibe eher gleichmaessig.",
        ],
        [
            "Ich liebe Metaphern und bildhafte Sprache — damit kann ich begeistern.",
            "Andere folgen meiner Rhetorik gut, ich strukturiere meine Argumente klar.",
            "Ich bin eher sachlich und verwende weniger Sprachbilder.",
            "Manchmal faellt es mir schwer, komplexe Themen einfach zu erklaeren.",
        ],
    ],
}

SUGGESTIONS_SYSTEM_PROMPT = """Generiere exakt 4 kurze Antwortvorschlaege (je max 15 Woerter) fuer die gegebene SCIL-Diagnostik-Frage.

Regeln:
- Die 4 Optionen muessen verschiedene AUSPRAEGUNGSGRADE abdecken (stark/mittel/schwach/differenziert)
- Formuliere in der Ich-Form, natuerlich und authentisch
- KEINE Fragebogen-Sprache — klingt wie eine echte Person
- Jede Option sollte genuegend Info liefern, damit der Agent die Items scoren kann
- Kurz und praegnant — max 15 Woerter pro Option
- Deutsch

Antworte NUR mit einem JSON-Array von genau 4 Strings, NICHTS anderes:
["Option 1", "Option 2", "Option 3", "Option 4"]"""

DEMO_SCORES = {
    "sensus": {"innere_praesenz": 3.2, "innere_ueberzeugung": 2.8, "prozessfokussierung": 3.0, "emotionalitaet": 2.4},
    "corpus": {"erscheinungsbild": 2.6, "mimik": 2.8, "gestik": 2.3, "raeumliche_praesenz": 2.5},
    "intellektus": {"sachlichkeit": 3.1, "analytik": 3.4, "struktur": 3.2, "zielorientierung": 3.0},
    "lingua": {"stimme": 2.8, "artikulation": 2.9, "beredsamkeit": 2.7, "bildhaftigkeit": 2.5},
}

DEMO_SUMMARY = (
    "## Dein SCIL-Wirkungsprofil\n\n"
    "Dein Profil zeigt eine starke Auspraegung im Bereich **Intellektus** — du denkst "
    "strukturiert, argumentierst analytisch und verfolgst klare Ziele.\n\n"
    "**Staerken:**\n"
    "- **Analytik** (3.4) — Ausgepraegtes analytisches Denken\n"
    "- **Innere Praesenz** (3.2) — Hohe Aufmerksamkeit und Praesenz\n"
    "- **Struktur** (3.2) — Klare Gedankenordnung\n\n"
    "**Entwicklungsfelder:**\n"
    "- **Gestik** (2.3) — Mehr Ausdruck durch Koerpersprache moeglich\n"
    "- **Emotionalitaet** (2.4) — Offeneres Zeigen von Gefuehlen\n"
    "- **Bildhaftigkeit** (2.5) — Staerkerer Einsatz von Metaphern\n\n"
    "**Balance-Score: 3.2/4.0** — Gute Ausgewogenheit ueber alle Bereiche.\n\n"
    "Die gute Nachricht: Wirkungskompetenz ist trainierbar!"
)

# Demo questions for each cluster
DEMO_CLUSTER_QUESTIONS = {
    "sensus": [
        "Spannend! Danke fuer den Einblick. Jetzt noch eine Frage zum Bereich Sensus: **Wie reagieren "
        "andere auf deine emotionale Ausstrahlung? Spueren Menschen in deiner Naehe deine Gefuehle? "
        "Und wie gehst du mit Gruppenprozessen um — achtest du bewusst auf die Beziehungsebene?**",
    ],
    "corpus": [
        "Sehr gut! Lass uns zum Bereich **Corpus** uebergehen — also deine koerperliche Wirkung.\n\n"
        "**Wenn du einen Raum betrittst — faellt deine Anwesenheit auf? Wie beschreiben andere "
        "deinen ersten Eindruck und deine Gestik, wenn du sprichst?**",
        "Danke! Noch eine Frage dazu: **Wie lebendig ist deine Mimik? Koennen andere deine Reaktionen "
        "gut an deinem Gesicht ablesen? Und wie bewusst nutzt du den Raum bei Praesentationen?**",
    ],
    "intellektus": [
        "Super, weiter zum Bereich **Intellektus** — deine analytische Wirkung.\n\n"
        "**Wie erleben andere deine Faehigkeit, sachlich und faktenbasiert zu argumentieren? "
        "Wie strukturiert sind deine Praesentationen?**",
        "Und noch: **Wie beschreiben andere deine Zielorientierung — wissen sie, was dir am wichtigsten ist? "
        "Bist du eher analytisch oder intuitiv in Entscheidungen?**",
    ],
    "lingua": [
        "Letzter Bereich: **Lingua** — deine sprachliche Wirkung.\n\n"
        "**Wie beschreiben andere deine Stimme? Variierst du bewusst Lautstaerke, Tempo und Betonung? "
        "Und wie klar und deutlich sprichst du?**",
        "Noch eine Frage: **Wie gut kannst du durch Sprachbilder und Metaphern abstrakte Konzepte "
        "greifbar machen? Koennen andere deiner Rhetorik gut folgen?**",
    ],
}


# ---------------------------------------------------------------------------
# Agent Class
# ---------------------------------------------------------------------------

class DiagnosisAgent:
    """SCIL diagnosis agent with item-driven assessment and per-item scoring."""

    def __init__(
        self,
        ai_service: AIService,
        session_factory: async_sessionmaker,
    ):
        self.ai_service = ai_service
        self.session_factory = session_factory

    # ------------------------------------------------------------------
    # Public: Start Session
    # ------------------------------------------------------------------

    async def start_session(self, run: DiagnosticRun) -> AsyncGenerator[dict, None]:
        """Start a new diagnostic session with greeting. Yields SSE events."""
        async with self.session_factory() as db:
            run_db = await db.get(DiagnosticRun, run.id)
            if not run_db:
                yield {"type": "agent_text", "content": "Session nicht gefunden.", "done": True}
                return

            run_db.status = "in_progress"
            run_db.conversation = []
            run_db.item_responses = []

            if not self.ai_service.is_configured():
                # Demo mode
                run_db.conversation = [{"role": "assistant", "content": DEMO_GREETING}]
                answers = dict(run_db.answers or {})
                answers["_suggestions"] = DEMO_GREETING_SUGGESTIONS
                run_db.answers = answers
                await db.commit()
                yield {"type": "agent_text", "content": DEMO_GREETING, "done": True}
                yield {"type": "suggestions", "suggestions": DEMO_GREETING_SUGGESTIONS}
                return

            # Build initial system prompt with first item block
            first_items = get_next_item_block(set(), current_area="sensus", block_size=3)
            item_context = _build_item_context(first_items, "sensus")

            system = SCIL_BASE_PROMPT + item_context + (
                "\n\n[INTERN: Begruessung + erste Frage. Erklaere kurz den Ablauf "
                "(4 Bereiche, ca. 25 Minuten) und stelle dann gleich die erste Frage "
                "basierend auf den Items oben.]"
            )

            full_text = ""
            async for chunk in self.ai_service.generate_stream(
                prompt="Bitte starte die Diagnostik-Session mit einer warmen Begruessung und der ersten Frage.",
                system=system,
                model="claude-sonnet-4-20250514",
                max_tokens=600,
                user_id=run_db.user_id,
                intent="scil_greeting",
                session_id=str(run_db.id),
            ):
                full_text += chunk
                yield {"type": "agent_text", "content": chunk, "done": False}

            yield {"type": "agent_text", "content": "", "done": True}

            # Generate suggestions for the greeting question
            suggestions = await self._generate_suggestions(full_text, first_items, run_db)
            if suggestions:
                yield {"type": "suggestions", "suggestions": suggestions}

            # Store which items were presented (for scoring context)
            run_db.conversation = [
                {"role": "assistant", "content": full_text},
            ]
            # Store pending items in answers metadata
            answers = dict(run_db.answers or {})
            answers["_pending_items"] = [item["id"] for item in first_items]
            answers["_current_area"] = "sensus"
            if suggestions:
                answers["_suggestions"] = suggestions
            run_db.answers = answers
            await db.commit()

    # ------------------------------------------------------------------
    # Public: Process Message
    # ------------------------------------------------------------------

    async def process_message(
        self,
        run_id: UUID,
        user_message: str,
    ) -> AsyncGenerator[dict, None]:
        """Process user message with item-driven scoring. Yields SSE events."""
        async with self.session_factory() as db:
            run = await db.get(DiagnosticRun, run_id)
            if not run:
                yield {
                    "type": "agent_text",
                    "content": "Session nicht gefunden. Bitte starte eine neue Diagnostik.",
                    "done": True,
                }
                return

            # Add user message to conversation
            conversation = list(run.conversation or [])
            conversation.append({"role": "user", "content": user_message})
            item_responses = list(run.item_responses or [])
            answers = dict(run.answers or {})

            # Get answered item IDs
            answered_ids = {r["item_id"] for r in item_responses}
            pending_items = answers.get("_pending_items", [])
            current_area = answers.get("_current_area", "sensus")

            # Calculate progress
            total_scored = len(answered_ids)
            progress = min(total_scored / 100, 0.99)

            if not self.ai_service.is_configured():
                # Demo mode
                async for event in self._demo_response(db, run, conversation, item_responses, answered_ids):
                    yield event
                return

            # Build messages with context budgeting
            messages = self._build_messages(conversation)

            # Determine next items to present (after scoring current ones)
            next_items = get_next_item_block(answered_ids, current_area=current_area, block_size=3)

            # Determine the next area if current cluster is nearly done
            cluster_prog = get_cluster_progress(answered_ids)
            area_prog = cluster_prog.get(current_area, {})
            area_remaining = area_prog.get("total", 25) - area_prog.get("answered", 0)

            # Check if we're transitioning to a new cluster
            next_area = current_area
            if area_remaining <= 0 and next_items:
                next_area = next_items[0]["area"]

            # Build system prompt with item context
            system = SCIL_BASE_PROMPT

            # Add progress context
            system += _build_progress_context(answered_ids, item_responses)

            # Add scoring instructions for pending items — VERY explicit
            if pending_items:
                pending_details = []
                for pid in pending_items:
                    pitem = get_item_by_id(pid)
                    if pitem:
                        pending_details.append(
                            f"  - {pid} ({pitem['frequency']}): {pitem['scoring_guidance'][:120]}"
                        )
                pending_str = "\n".join(pending_details)
                system += (
                    f"\n\n## WICHTIG — JETZT BEWERTEN!\n"
                    f"Der Nutzer hat gerade auf deine vorherige Frage geantwortet.\n"
                    f"Du MUSST jetzt folgende Items bewerten (rufe score_item fuer JEDES auf):\n"
                    f"{pending_str}\n\n"
                    f"Verwende EXAKT diese Item-IDs: {', '.join(pending_items)}\n"
                    f"Zusaetzlich: Gib eine kurze wertschaetzende Antwort und stelle die naechste Frage.\n"
                    f"WICHTIG: Du MUSST sowohl Text ALS AUCH score_item Tool-Aufrufe zurueckgeben!"
                )

            # Add next items context
            if next_items:
                system += _build_item_context(next_items, next_area)

                # Cluster transition hint
                if next_area != current_area:
                    system += (
                        f"\n\n[INTERN: Du wechselst jetzt vom Bereich {AREA_LABELS.get(current_area, current_area)} "
                        f"zum Bereich {AREA_LABELS.get(next_area, next_area)}. "
                        f"Mache eine kurze, natuerliche Ueberleitung.]"
                    )

            # Check if assessment should complete
            should_complete = total_scored >= 96  # Allow 96+ with high confidence
            is_nearly_done = total_scored >= 90

            if should_complete and not next_items:
                system += (
                    "\n\n[INTERN: Alle Items sind bewertet! Bereite einen wertschaetzenden "
                    "Abschluss vor und fasse kurz zusammen, was du beobachtet hast.]"
                )
            elif is_nearly_done:
                system += (
                    f"\n\n[INTERN: Du bist fast fertig ({total_scored}/100 Items). "
                    "Noch ein paar letzte Fragen, dann kannst du abschliessen.]"
                )

            # Generate response with tool_use
            tools = [SCORE_ITEM_TOOL, UPDATE_SCORES_TOOL]

            result = await self.ai_service.generate_with_tools(
                prompt=self._format_conversation(messages),
                tools=tools,
                system=system,
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                temperature=0.7,
                user_id=run.user_id,
                intent="scil_assessment",
                session_id=str(run_id),
            )

            agent_text = result.get("content", "")
            tool_calls = result.get("tool_calls", [])

            # Process tool calls
            turn_number = sum(1 for m in conversation if m["role"] == "user")
            new_scored_ids: set[str] = set()
            scored_summary_parts: list[str] = []

            for tc in tool_calls:
                if tc["name"] == "score_item":
                    item_id = tc["input"].get("item_id", "")
                    score = tc["input"].get("score", 0)
                    confidence = tc["input"].get("confidence", 0.5)
                    reasoning = tc["input"].get("reasoning", "")

                    # Validate item exists
                    item = get_item_by_id(item_id)
                    if item:
                        clamped_score = round(min(4.0, max(0.0, float(score))), 1)
                        # Add to item_responses
                        item_responses.append({
                            "item_id": item_id,
                            "score": clamped_score,
                            "confidence": round(min(1.0, max(0.0, float(confidence))), 2),
                            "reasoning": reasoning,
                            "scored_at": datetime.now(timezone.utc).isoformat(),
                            "turn_number": turn_number,
                            "area": item["area"],
                            "frequency": item["frequency"],
                        })
                        new_scored_ids.add(item_id)
                        scored_summary_parts.append(f"{item_id}={clamped_score}")
                        logger.info(f"Scored item {item_id}: {clamped_score} (confidence: {confidence})")
                    else:
                        logger.warning(f"Unknown item ID from AI: {item_id}")

                elif tc["name"] == "update_scil_scores":
                    # Legacy aggregate scoring — extract and merge
                    scores = self._extract_scores(tc["input"])
                    # Merge into answers (but item_responses is the source of truth)
                    for area_key, freq_scores in scores.items():
                        if area_key not in answers or not isinstance(answers.get(area_key), dict):
                            answers[area_key] = {}
                        answers[area_key].update(freq_scores)

            # Update answered_ids with new scores
            answered_ids = {r["item_id"] for r in item_responses}
            total_scored = len(answered_ids)
            progress = min(total_scored / 100, 0.99)

            # Aggregate item scores to frequency scores
            aggregated = self._aggregate_item_scores(item_responses)
            for area_key, freq_scores in aggregated.items():
                if area_key.startswith("_"):
                    continue
                if area_key not in answers or not isinstance(answers.get(area_key), dict):
                    answers[area_key] = {}
                answers[area_key].update(freq_scores)

            # Emit scores update
            if new_scored_ids or aggregated:
                polygon = compute_polygon(aggregated if aggregated else answers)
                cluster_progress = get_cluster_progress(answered_ids)
                yield {
                    "type": "scores_update",
                    "scores": aggregated if aggregated else answers,
                    "progress": progress,
                    "polygon": polygon,
                }
                # Emit cluster progress
                yield {
                    "type": "cluster_progress",
                    "cluster": {
                        area: cluster_progress[area]
                        for area in CLUSTER_ORDER
                    },
                    "total_scored": total_scored,
                    "total_required": 100,
                }

            # If AI returned tools but no text, do a follow-up call for the conversational response
            if not agent_text.strip() and (new_scored_ids or next_items):
                # Re-compute next items after scoring
                updated_answered = {r["item_id"] for r in item_responses}
                follow_up_items = get_next_item_block(updated_answered, current_area=next_area, block_size=3)
                follow_up_area = follow_up_items[0]["area"] if follow_up_items else next_area

                follow_up_prompt = (
                    f"Du hast gerade Items bewertet: {', '.join(scored_summary_parts)}.\n"
                    f"Gib jetzt eine kurze, wertschaetzende Antwort auf die Aussage des Nutzers "
                    f"und stelle die naechste Gespraechsfrage."
                )
                if follow_up_items:
                    follow_up_prompt += _build_item_context(follow_up_items, follow_up_area)
                    # Update next items for the pending list
                    next_items = follow_up_items
                    next_area = follow_up_area

                full_text = ""
                async for chunk in self.ai_service.generate_stream(
                    prompt=self._format_conversation(messages) + f"\n\nAgent (Kontext): [Scores vergeben: {', '.join(scored_summary_parts)}]\n\n{follow_up_prompt}",
                    system=SCIL_BASE_PROMPT + _build_progress_context(updated_answered, item_responses),
                    model="claude-sonnet-4-20250514",
                    max_tokens=400,
                    user_id=run.user_id,
                    intent="scil_followup",
                    session_id=str(run_id),
                ):
                    full_text += chunk
                    yield {"type": "agent_text", "content": chunk, "done": False}

                yield {"type": "agent_text", "content": "", "done": True}
                agent_text = full_text

            elif agent_text:
                yield {"type": "agent_text", "content": agent_text, "done": True}

            # Generate answer suggestions for the next question (if not completing)
            should_complete = total_scored >= 96 and not next_items
            current_suggestions = []
            if not should_complete and agent_text.strip() and next_items:
                current_suggestions = await self._generate_suggestions(agent_text, next_items, run)
                if current_suggestions:
                    yield {"type": "suggestions", "suggestions": current_suggestions}

            # Update state
            conversation.append({"role": "assistant", "content": agent_text})
            run.conversation = conversation
            run.item_responses = item_responses
            run.progress = progress

            # Update pending items for next turn
            if next_items:
                answers["_pending_items"] = [item["id"] for item in next_items]
                answers["_current_area"] = next_area
            else:
                answers["_pending_items"] = []

            # Persist suggestions for session reload
            if current_suggestions:
                answers["_suggestions"] = current_suggestions
            else:
                answers.pop("_suggestions", None)

            run.answers = answers

            # Handle completion
            all_done = total_scored >= 96 and not next_items
            force_complete = total_scored >= 100

            if all_done or force_complete:
                run.status = "scoring"
                await db.commit()
                yield {"type": "status", "status": "scoring"}

                # Finalize
                result_obj = await self._finalize(db, run)
                run.status = "completed"
                await db.commit()

                yield {"type": "complete", "result_id": str(result_obj.id)}
            else:
                await db.commit()

    # ------------------------------------------------------------------
    # Demo Mode
    # ------------------------------------------------------------------

    async def _demo_response(
        self,
        db: AsyncSession,
        run: DiagnosticRun,
        conversation: list[dict],
        item_responses: list[dict],
        answered_ids: set[str],
    ) -> AsyncGenerator[dict, None]:
        """Generate demo responses without AI — simulates cluster progression."""
        user_count = sum(1 for m in conversation if m["role"] == "user")
        answers = dict(run.answers or {})
        current_area = answers.get("_current_area", "sensus")

        # Determine demo progress and message
        # Demo has ~7 turns total: 2 sensus, 2 corpus, 2 intellektus, 1 lingua + summary
        demo_sequence = []
        for area in CLUSTER_ORDER:
            questions = DEMO_CLUSTER_QUESTIONS.get(area, [])
            for q in questions:
                demo_sequence.append({"area": area, "text": q})

        current_idx = user_count - 1  # 0-indexed (first user message = idx 0)
        is_complete = current_idx >= len(demo_sequence)

        if is_complete:
            message = (
                "Vielen Dank fuer deine offenen Antworten! Ich habe jetzt ein umfassendes Bild "
                "deiner Wirkungskompetenz. Lass mich dein SCIL-Profil berechnen..."
            )
        else:
            entry = demo_sequence[min(current_idx, len(demo_sequence) - 1)]
            message = entry["text"]
            current_area = entry["area"]

        # Simulate item scoring for demo
        # Score ~14 items per turn to reach ~100 in 7 turns
        demo_items_per_turn = 14
        simulated_scored = min(user_count * demo_items_per_turn, 100)
        progress = min(simulated_scored / 100, 1.0)

        # Yield text
        yield {"type": "agent_text", "content": message, "done": True}

        # Yield suggestions for next question (unless completing)
        if not is_complete:
            demo_area_suggestions = DEMO_SUGGESTIONS.get(current_area, [])
            # Pick the right suggestion set based on turn within area
            area_turn_idx = sum(
                1 for seq_entry in demo_sequence[:current_idx]
                if seq_entry["area"] == current_area
            )
            if area_turn_idx < len(demo_area_suggestions):
                yield {"type": "suggestions", "suggestions": demo_area_suggestions[area_turn_idx]}
            elif demo_area_suggestions:
                yield {"type": "suggestions", "suggestions": demo_area_suggestions[-1]}

        # Yield scores after turn 2
        if user_count >= 2:
            polygon = compute_polygon(DEMO_SCORES)
            yield {
                "type": "scores_update",
                "scores": DEMO_SCORES,
                "progress": progress,
                "polygon": polygon,
            }
            yield {
                "type": "cluster_progress",
                "cluster": {
                    "sensus": {"answered": min(simulated_scored, 25), "total": 25},
                    "corpus": {"answered": min(max(simulated_scored - 25, 0), 25), "total": 25},
                    "intellektus": {"answered": min(max(simulated_scored - 50, 0), 25), "total": 25},
                    "lingua": {"answered": min(max(simulated_scored - 75, 0), 25), "total": 25},
                },
                "total_scored": simulated_scored,
                "total_required": 100,
            }

        # Update state
        conversation.append({"role": "assistant", "content": message})
        run.conversation = conversation
        run.progress = progress
        answers["_current_area"] = current_area
        run.answers = {**answers, **DEMO_SCORES} if user_count >= 2 else answers

        if is_complete:
            run.status = "scoring"
            await db.commit()
            yield {"type": "status", "status": "scoring"}

            result_obj = await self._finalize_demo(db, run)
            run.status = "completed"
            await db.commit()
            yield {"type": "complete", "result_id": str(result_obj.id)}
        else:
            await db.commit()

    # ------------------------------------------------------------------
    # Finalization
    # ------------------------------------------------------------------

    async def _finalize(self, db: AsyncSession, run: DiagnosticRun) -> DiagnosticResult:
        """Finalize: aggregate item scores, compute polygon, generate summary."""
        item_responses = run.item_responses or []

        # Aggregate item-level scores to frequency scores
        scores = self._aggregate_item_scores(item_responses)
        if not scores:
            # Fallback to answers dict
            scores = {k: v for k, v in (run.answers or {}).items() if not k.startswith("_")}

        polygon = compute_polygon(scores)
        strengths = get_top_strengths(scores, n=3)
        dev_areas = get_development_areas(scores, n=3)

        # Generate AI summary
        strengths_str = ", ".join(f"{s.label} ({s.score})" for s in strengths)
        dev_str = ", ".join(f"{d.label} ({d.score})" for d in dev_areas)
        total_items = len(item_responses)
        balance = compute_balance_score(scores)

        summary = await self.ai_service.generate(
            prompt=(
                f"Erstelle eine wertschaetzende Zusammenfassung dieses SCIL-Wirkungsprofils:\n\n"
                f"Scores: {json.dumps(scores, indent=2)}\n\n"
                f"Top-Staerken: {strengths_str}\n"
                f"Entwicklungsfelder: {dev_str}\n"
                f"Balance-Score: {balance}\n"
                f"Bewertete Items: {total_items}/100\n\n"
                "Betone Staerken, zeige Entwicklungsfelder als Chancen. "
                "Erklaere kurz, was der Balance-Score bedeutet. Formatiere als Markdown."
            ),
            system=(
                "Du bist ein SCIL-Experte. SCIL misst Wirkungskompetenz (Aussenwirkung), "
                "nicht Persoenlichkeit. Erstelle eine professionelle, wertschaetzende Zusammenfassung. "
                "Max 300 Woerter."
            ),
            model="claude-sonnet-4-20250514",
            max_tokens=800,
            user_id=run.user_id,
            intent="scil_summary",
            session_id=str(run.id),
        )

        recommendations = [
            {
                "area": d.area,
                "frequency": d.key,
                "label": d.label,
                "current_score": d.score,
                "level": d.level,
            }
            for d in dev_areas
        ]

        result = DiagnosticResult(
            run_id=run.id,
            user_id=run.user_id,
            scores=scores,
            summary=summary or "Zusammenfassung wird erstellt...",
            recommendations=recommendations,
            polygon_data=polygon,
        )
        db.add(result)
        run.completed_at = datetime.now(timezone.utc)

        # Update answers with final aggregated scores
        answers = dict(run.answers or {})
        for area_key, freq_scores in scores.items():
            if not area_key.startswith("_"):
                answers[area_key] = freq_scores
        run.answers = answers

        await db.flush()
        return result

    async def _finalize_demo(self, db: AsyncSession, run: DiagnosticRun) -> DiagnosticResult:
        """Finalize demo assessment with pre-built summary."""
        scores = DEMO_SCORES
        polygon = compute_polygon(scores)

        dev_areas = get_development_areas(scores, n=3)
        recommendations = [
            {"area": d.area, "frequency": d.key, "label": d.label, "current_score": d.score, "level": d.level}
            for d in dev_areas
        ]

        result = DiagnosticResult(
            run_id=run.id,
            user_id=run.user_id,
            scores=scores,
            summary=DEMO_SUMMARY,
            recommendations=recommendations,
            polygon_data=polygon,
        )
        db.add(result)
        run.answers = {**dict(run.answers or {}), **scores}
        run.completed_at = datetime.now(timezone.utc)
        await db.flush()
        return result

    # ------------------------------------------------------------------
    # Suggestions
    # ------------------------------------------------------------------

    async def _generate_suggestions(
        self,
        agent_question: str,
        next_items: list[dict],
        run: DiagnosticRun,
    ) -> list[str]:
        """Generate 4 answer suggestions for the current agent question.

        Uses a lightweight AI call to produce 4 short answer options covering
        different strength levels (strong/medium/weak/nuanced).
        """
        if not agent_question.strip():
            return []

        # Build context about items being assessed
        item_hints = ""
        if next_items:
            hints = []
            for item in next_items[:3]:
                hints.append(f"- {item['id']} ({item['frequency']}): {item['scoring_guidance'][:80]}")
            item_hints = "\nItems die bewertet werden:\n" + "\n".join(hints)

        prompt = (
            f"Frage des Agents:\n\"{agent_question[-500:]}\"\n"
            f"{item_hints}\n\n"
            f"Generiere 4 Antwortvorschlaege als JSON-Array."
        )

        try:
            raw = await self.ai_service.generate(
                prompt=prompt,
                system=SUGGESTIONS_SYSTEM_PROMPT,
                model="claude-sonnet-4-20250514",
                max_tokens=250,
                temperature=0.8,
                user_id=run.user_id,
                intent="scil_suggestions",
                session_id=str(run.id),
            )

            # Parse JSON array from response
            raw = raw.strip()
            # Handle case where model wraps in markdown code block
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0].strip()

            suggestions = json.loads(raw)
            if isinstance(suggestions, list) and len(suggestions) >= 4:
                return [str(s).strip() for s in suggestions[:4]]
            elif isinstance(suggestions, list) and len(suggestions) > 0:
                return [str(s).strip() for s in suggestions[:4]]
        except Exception as e:
            logger.warning(f"Failed to generate suggestions: {e}")

        return []

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _build_messages(self, conversation: list[dict]) -> list[dict]:
        """Build messages list with context budgeting for long conversations."""
        if len(conversation) <= 14:
            return conversation

        budget = 8000  # Increased for 100-item sessions
        result = build_conversation_window(conversation, budget)
        selected = result.get("selected", conversation[-8:])

        summary = result.get("summary_text", "")
        if summary and selected:
            selected = [{"role": "assistant", "content": f"[Kontext bisheriger Gespraechsverlauf: {summary}]"}] + selected

        return selected

    def _format_conversation(self, messages: list[dict]) -> str:
        """Format conversation for generate/generate_with_tools."""
        parts = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "user":
                parts.append(f"User: {content}")
            elif role == "assistant":
                parts.append(f"Agent: {content}")
        return "\n\n".join(parts)

    def _extract_scores(self, tool_input: dict) -> dict:
        """Extract and validate SCIL scores from legacy update_scil_scores tool."""
        scores: dict[str, dict[str, float]] = {}
        for area in ("sensus", "corpus", "intellektus", "lingua"):
            area_data = tool_input.get(area, {})
            scores[area] = {}
            for key, value in area_data.items():
                if isinstance(value, (int, float)):
                    scores[area][key] = round(min(4.0, max(0.0, float(value))), 1)
        return scores

    def _aggregate_item_scores(self, item_responses: list[dict]) -> dict:
        """Aggregate per-item scores to frequency-level scores (confidence-weighted mean).

        Returns dict in the same format as the legacy scores:
        {
            "sensus": {"innere_praesenz": 3.2, ...},
            "corpus": {...},
            ...
        }
        """
        if not item_responses:
            return {}

        # Group by frequency
        freq_scores: dict[str, list[tuple[float, float]]] = {}  # freq -> [(score, confidence)]
        for resp in item_responses:
            freq = resp.get("frequency", "")
            score = resp.get("score", 0)
            confidence = resp.get("confidence", 0.5)
            if freq:
                if freq not in freq_scores:
                    freq_scores[freq] = []
                freq_scores[freq].append((float(score), float(confidence)))

        # Compute confidence-weighted mean per frequency
        aggregated: dict[str, dict[str, float]] = {}
        for area, frequencies in AREA_FREQUENCIES.items():
            aggregated[area] = {}
            for freq in frequencies:
                if freq in freq_scores:
                    scores_and_conf = freq_scores[freq]
                    total_weight = sum(c for _, c in scores_and_conf)
                    if total_weight > 0:
                        weighted_sum = sum(s * c for s, c in scores_and_conf)
                        aggregated[area][freq] = round(weighted_sum / total_weight, 1)
                    else:
                        # Simple average if all confidence is 0
                        avg = sum(s for s, _ in scores_and_conf) / len(scores_and_conf)
                        aggregated[area][freq] = round(avg, 1)

        return aggregated
