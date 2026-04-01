"""
360° Feedback Agent — Conversational Multi-Rater Assessment

Leads raters through a natural conversation to collect structured and
qualitative feedback, maps responses to SCIL frequencies, aggregates
multi-rater data, and computes Johari Window quadrants.

Architecture:
  1. Conversational Layer — STAR-method guided dialogue
  2. Adaptive Questioning Engine — dynamic follow-ups, SCIL mapping
  3. Analysis & Aggregation Layer — multi-rater scoring, NLP synthesis
  4. Output & Visualization Layer — Johari, polygon overlay, heatmap
"""

import os
import json
import uuid
from typing import Any
from datetime import datetime

import anthropic


# ── SCIL frequency ↔ 360° competency mapping ──
COMPETENCY_SCIL_MAP: dict[str, list[tuple[str, str, float]]] = {
    "persuasion": [
        ("sensus", "conviction", 0.40),
        ("lingua", "eloquence", 0.30),
        ("corpus", "gesture", 0.30),
    ],
    "analytical_thinking": [
        ("intellektus", "analytics", 0.50),
        ("intellektus", "structure", 0.30),
        ("intellektus", "objectivity", 0.20),
    ],
    "empathy": [
        ("sensus", "emotionality", 0.40),
        ("sensus", "inner_presence", 0.35),
        ("corpus", "facial_expression", 0.25),
    ],
    "presence": [
        ("corpus", "spatial_presence", 0.40),
        ("corpus", "appearance", 0.30),
        ("lingua", "voice", 0.30),
    ],
    "strategic_thinking": [
        ("intellektus", "goal_orientation", 0.40),
        ("intellektus", "analytics", 0.30),
        ("intellektus", "structure", 0.30),
    ],
    "storytelling": [
        ("lingua", "imagery", 0.40),
        ("lingua", "eloquence", 0.30),
        ("sensus", "emotionality", 0.30),
    ],
    "team_leadership": [
        ("sensus", "moment_focus", 0.35),
        ("corpus", "spatial_presence", 0.35),
        ("intellektus", "goal_orientation", 0.30),
    ],
    "clarity": [
        ("lingua", "articulation", 0.35),
        ("intellektus", "structure", 0.35),
        ("intellektus", "objectivity", 0.30),
    ],
}

COMPETENCY_LABELS_DE: dict[str, str] = {
    "persuasion": "Überzeugungskraft",
    "analytical_thinking": "Analytisches Denken",
    "empathy": "Empathie",
    "presence": "Präsenz & Auftreten",
    "strategic_thinking": "Strategisches Denken",
    "storytelling": "Storytelling",
    "team_leadership": "Teamführung",
    "clarity": "Klarheit in der Kommunikation",
}

RATER_SYSTEM_PROMPT = """Du bist der 360°-Feedback-Agent — ein empathischer, professioneller KI-Moderator,
der Feedback-Geber durch einen strukturierten Feedback-Prozess führt.

## Deine Rolle
Du führst ein natürliches Gespräch mit einem Feedback-Geber (Rater) über eine Zielperson.
Das Feedback wird auf 8 Kernkompetenzen abgebildet, die den 16 SCIL-Frequenzen zugeordnet sind.

## Kompetenzen, die du erfasst:
1. Überzeugungskraft — Wie gut kann die Person andere überzeugen?
2. Analytisches Denken — Wie strukturiert und logisch denkt die Person?
3. Empathie — Wie gut nimmt die Person Emotionen anderer wahr?
4. Präsenz & Auftreten — Wie souverän tritt die Person auf?
5. Strategisches Denken — Wie gut plant und priorisiert die Person?
6. Storytelling — Wie packend erzählt und präsentiert die Person?
7. Teamführung — Wie gut führt die Person Teams?
8. Klarheit — Wie verständlich kommuniziert die Person?

## Gesprächsführung (4 Phasen):

### Phase 1: KONTEXTUALISIERUNG (1-2 Fragen)
- Begrüße den Rater und erkläre kurz den Ablauf
- Frage nach dem Beziehungskontext: "In welcher Rolle arbeiten Sie mit [Person] zusammen?"
- Bestätige die Anonymität: "Ihre Antworten werden vollständig anonymisiert."

### Phase 2: ADAPTIVE GESPRÄCHSFÜHRUNG (8-12 Fragen)
- Nutze die STAR-Methode: "Beschreiben Sie eine Situation, in der [Person]..."
- Passe deine Fragen an die bisherigen Antworten an
- Vertiefe bei relevanten Themen
- Frage sowohl nach Stärken als auch nach Entwicklungsfeldern
- Decke alle 8 Kompetenzen ab

### Phase 3: EINGEBETTETE BEWERTUNG (1-2 Fragen)
- Frage: "Wenn Sie eine besondere Stärke von [Person] nennen müssten?"
- Frage: "Und ein Bereich, in dem [Person] noch wachsen könnte?"

### Phase 4: ZUSAMMENFASSUNG (1 Frage)
- Fasse zusammen, was du gehört hast
- Frage: "Habe ich das richtig zusammengefasst?"

## Scoring
Bewerte jede Kompetenz intern auf einer Skala von 1-10.
Extrahiere qualitative Kernaussagen für jede Kompetenz.

## Wichtig
- Bleibe stets professionell und wertschätzend
- Ermutige den Rater zu konkreten Beispielen
- Akzeptiere "kann ich nicht beurteilen" bei fehlender Erfahrung
- Frage NIEMALS nach vertraulichen oder persönlichen Daten des Raters
- Sprich Deutsch, außer der Rater wechselt die Sprache
- Nenne die Zielperson immer beim Vornamen (wird dir mitgeteilt)
"""


class Feedback360Agent:
    """Conversational 360° feedback agent with SCIL mapping."""

    def __init__(self):
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        self.client = anthropic.AsyncAnthropic(api_key=api_key) if api_key else None
        self.sessions: dict[str, dict[str, Any]] = {}

    # ── Session lifecycle ──────────────────────────────────────

    async def start_rater_session(
        self,
        round_id: str,
        rater_id: str,
        target_name: str,
        rater_perspective: str,  # "self", "supervisor", "peer", "report", "external"
    ) -> str:
        session_key = f"{round_id}:{rater_id}"
        self.sessions[session_key] = {
            "round_id": round_id,
            "rater_id": rater_id,
            "target_name": target_name,
            "perspective": rater_perspective,
            "messages": [],
            "scores": {},
            "qualitative": {},
            "phase": "context",
            "question_count": 0,
            "competencies_covered": set(),
        }

        if rater_perspective == "self":
            greeting = (
                f"Willkommen zu deiner Selbsteinschätzung! 🎯\n\n"
                f"Ich werde dir einige Fragen zu deiner eigenen Wirkung und Kommunikation stellen. "
                f"Sei dabei so ehrlich wie möglich — es gibt keine richtigen oder falschen Antworten.\n\n"
                f"**Lass uns starten: In welcher beruflichen Rolle bist du gerade unterwegs?**"
            )
        else:
            perspective_label = {
                "supervisor": "als Vorgesetzte/r",
                "peer": "als Kolleg/in",
                "report": "als Teammitglied",
                "external": "als externe/r Partner/in",
            }.get(rater_perspective, "")

            greeting = (
                f"Willkommen zum 360°-Feedback für **{target_name}**! 🎯\n\n"
                f"Ich führe Sie durch ein kurzes Gespräch (ca. 10-15 Minuten), "
                f"um Ihr Feedback zu erfassen. Ihre Antworten werden **vollständig anonymisiert** — "
                f"{target_name} wird nur aggregierte Ergebnisse sehen, nie einzelne Rater.\n\n"
                f"**Zunächst: Wie oft arbeiten Sie {perspective_label} mit {target_name} zusammen?**"
            )

        self.sessions[session_key]["messages"].append(
            {"role": "assistant", "content": greeting}
        )
        return greeting

    async def process_rater_message(
        self, round_id: str, rater_id: str, message: str
    ) -> dict[str, Any]:
        session_key = f"{round_id}:{rater_id}"
        session = self.sessions.get(session_key)
        if not session:
            return {"message": "Session nicht gefunden.", "is_complete": False}

        session["messages"].append({"role": "user", "content": message})
        session["question_count"] += 1

        progress = min(session["question_count"] / 14, 0.95)

        if not self.client:
            return self._demo_rater_response(session)

        # Determine which competencies still need coverage
        uncovered = set(COMPETENCY_SCIL_MAP.keys()) - session["competencies_covered"]
        coverage_hint = ""
        if uncovered and session["question_count"] > 3:
            labels = [COMPETENCY_LABELS_DE.get(c, c) for c in list(uncovered)[:3]]
            coverage_hint = (
                f"\n\n[INTERN: Noch nicht abgedeckte Kompetenzen: {', '.join(labels)}. "
                f"Versuche, in den nächsten Fragen diese Bereiche zu adressieren.]"
            )

        is_ending = session["question_count"] >= 12
        ending_hint = ""
        if is_ending:
            ending_hint = "\n\n[INTERN: Nähert sich dem Ende. Gehe zur Zusammenfassungs-Phase über.]"

        system = RATER_SYSTEM_PROMPT.replace(
            "[Person]", session["target_name"]
        ) + coverage_hint + ending_hint

        response = await self.client.messages.create(
            model="claude-sonnet-4-5-20250514",
            max_tokens=600,
            system=system,
            messages=session["messages"],
        )

        agent_message = response.content[0].text
        session["messages"].append({"role": "assistant", "content": agent_message})

        # Try to extract competency scores if agent included them
        scores_update = self._extract_scores(agent_message)
        if scores_update:
            session["scores"].update(scores_update)
            session["competencies_covered"].update(scores_update.keys())

        is_complete = session["question_count"] >= 14

        result: dict[str, Any] = {
            "message": agent_message,
            "progress": progress,
            "is_complete": is_complete,
        }

        if is_complete:
            result["scores"] = session["scores"]
            result["scil_scores"] = self.map_competencies_to_scil(session["scores"])
            result["qualitative"] = session.get("qualitative", {})

        return result

    # ── SCIL mapping ───────────────────────────────────────────

    @staticmethod
    def map_competencies_to_scil(
        competency_scores: dict[str, float],
    ) -> dict[str, dict[str, float]]:
        """Map 360° competency scores to SCIL 16-frequency scores."""
        scil_scores: dict[str, dict[str, float]] = {
            "sensus": {},
            "corpus": {},
            "intellektus": {},
            "lingua": {},
        }
        scil_weights: dict[str, dict[str, float]] = {
            "sensus": {},
            "corpus": {},
            "intellektus": {},
            "lingua": {},
        }

        for comp, score in competency_scores.items():
            mapping = COMPETENCY_SCIL_MAP.get(comp, [])
            for area, freq, weight in mapping:
                if freq not in scil_scores[area]:
                    scil_scores[area][freq] = 0.0
                    scil_weights[area][freq] = 0.0
                scil_scores[area][freq] += score * weight
                scil_weights[area][freq] += weight

        # Normalize by total weight
        for area in scil_scores:
            for freq in scil_scores[area]:
                w = scil_weights[area].get(freq, 1.0)
                if w > 0:
                    scil_scores[area][freq] = round(scil_scores[area][freq] / w, 1)

        return scil_scores

    # ── Johari Window ──────────────────────────────────────────

    @staticmethod
    def compute_johari_window(
        self_scores: dict[str, float],
        aggregated_other_scores: dict[str, float],
        threshold: float = 1.5,
    ) -> dict[str, list[str]]:
        """
        Compute Johari Window quadrants from self vs. aggregated other scores.

        threshold: Score difference required to classify as discrepant.
        Returns dict with quadrant → list of competency keys.
        """
        johari: dict[str, list[str]] = {
            "public": [],        # Both see it — self ≈ others
            "blind_spot": [],    # Others see, self doesn't — self < others
            "hidden": [],        # Self sees, others don't — self > others
            "unknown": [],       # Neither sees — both low
        }

        all_competencies = set(self_scores.keys()) | set(aggregated_other_scores.keys())

        for comp in all_competencies:
            s = self_scores.get(comp, 5.0)
            o = aggregated_other_scores.get(comp, 5.0)
            diff = s - o

            if abs(diff) <= threshold:
                # Agreement
                if (s + o) / 2 >= 6.0:
                    johari["public"].append(comp)
                else:
                    johari["unknown"].append(comp)
            elif diff > threshold:
                johari["hidden"].append(comp)
            else:
                johari["blind_spot"].append(comp)

        return johari

    # ── Multi-rater aggregation ────────────────────────────────

    @staticmethod
    def aggregate_rater_scores(
        rater_scores: list[dict[str, float]],
    ) -> dict[str, float]:
        """Aggregate scores from multiple raters (mean, with outlier detection)."""
        if not rater_scores:
            return {}

        all_comps = set()
        for rs in rater_scores:
            all_comps.update(rs.keys())

        aggregated: dict[str, float] = {}
        for comp in all_comps:
            values = [rs[comp] for rs in rater_scores if comp in rs]
            if not values:
                continue
            # Simple mean (could add IQR outlier removal for large groups)
            aggregated[comp] = round(sum(values) / len(values), 1)

        return aggregated

    # ── Helpers ────────────────────────────────────────────────

    def _extract_scores(self, text: str) -> dict[str, float]:
        """Try to extract JSON scores from agent message."""
        if "```json" not in text:
            return {}
        try:
            start = text.index("```json") + 7
            end = text.index("```", start)
            data = json.loads(text[start:end])
            return data.get("scores", {})
        except (ValueError, json.JSONDecodeError):
            return {}

    def _demo_rater_response(self, session: dict) -> dict[str, Any]:
        """Demo responses when no API key is set."""
        q = session["question_count"]
        target = session["target_name"]

        demo_qs = [
            f"Danke! Und in welchen Situationen erleben Sie {target} am häufigsten? "
            f"**Eher in Meetings, Präsentationen, oder im Tagesgeschäft?**",

            f"Verstehe. **Wenn Sie an {target}s Fähigkeit denken, andere zu überzeugen — "
            f"beschreiben Sie eine konkrete Situation, die Ihnen in Erinnerung geblieben ist.**",

            f"Spannend! Und wie würden Sie {target}s **analytische Fähigkeiten** einschätzen? "
            f"Fällt Ihnen ein Beispiel ein, wo die Struktur und Klarheit besonders aufgefallen ist?",

            f"Gut zu wissen. **Wie empathisch erleben Sie {target}?** "
            f"Nimmt {target} wahr, wenn im Team etwas nicht stimmt?",

            f"**Wie würden Sie {target}s Auftreten und Präsenz beschreiben?** "
            f"Nimmt {target} den Raum ein, wenn er/sie spricht?",

            f"Letzte Frage: **Wenn Sie EINE besondere Stärke von {target} nennen müssten — welche wäre das? "
            f"Und ein Bereich, in dem {target} noch wachsen könnte?**",
        ]

        is_complete = q >= len(demo_qs)

        if q <= len(demo_qs):
            message = demo_qs[q - 1]
        else:
            message = (
                f"Vielen Dank für Ihr wertvolles Feedback zu {target}! "
                f"Ihre Einschätzungen werden anonymisiert in die Gesamtauswertung einfließen."
            )
            is_complete = True

        demo_scores = {
            "persuasion": 7.5,
            "analytical_thinking": 8.2,
            "empathy": 6.8,
            "presence": 7.0,
            "strategic_thinking": 7.8,
            "storytelling": 6.5,
            "team_leadership": 7.3,
            "clarity": 8.0,
        }

        result: dict[str, Any] = {
            "message": message,
            "progress": min(q / 6, 1.0),
            "is_complete": is_complete,
        }

        if is_complete:
            result["scores"] = demo_scores
            result["scil_scores"] = self.map_competencies_to_scil(demo_scores)

        return result

    async def save_session(self, round_id: str, rater_id: str):
        """Persist session state."""
        pass  # In production: POST to backend
