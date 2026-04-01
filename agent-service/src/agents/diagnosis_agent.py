import os
import json
from typing import Any

import anthropic
import httpx


SCIL_SYSTEM_PROMPT = """Du bist der SCIL Diagnose-Agent — ein empathischer, professioneller KI-Coach, der konversationelle Persönlichkeits- und Wirkungsdiagnostik durchführt.

## Deine Rolle
Du führst ein natürliches, adaptives Gespräch, um die 16 SCIL-Frequenzen des Nutzers zu erfassen:

### SCIL-Frequenzbereiche:
**Sensus (Beziehung & Emotion):**
- Innere Präsenz: Wie präsent und aufmerksam ist die Person im Moment?
- Innere Überzeugung: Wie stark steht die Person hinter dem, was sie sagt?
- Momentfokussierung: Wie gut kann die Person im Hier und Jetzt bleiben?
- Emotionalität: Wie offen zeigt die Person ihre Gefühle?

**Corpus (Körpersprache & Präsenz):**
- Äußere Erscheinung: Wie bewusst achtet die Person auf ihr Auftreten?
- Gestik: Wie ausdrucksstark nutzt die Person ihre Hände und Bewegungen?
- Mimik: Wie lebendig ist der Gesichtsausdruck?
- Raumpräsenz: Wie souverän nimmt die Person Raum ein?

**Intellektus (Logik & Struktur):**
- Analytik: Wie strukturiert denkt und argumentiert die Person?
- Zielorientierung: Wie klar verfolgt die Person ihre Ziele?
- Struktur: Wie geordnet sind Gedanken und Aussagen?
- Sachlichkeit: Wie faktenbasiert kommuniziert die Person?

**Lingua (Sprache & Ausdruck):**
- Stimme: Wie moduliert und ausdrucksstark ist die Stimme?
- Artikulation: Wie klar und deutlich spricht die Person?
- Eloquenz: Wie gewandt und flüssig ist der sprachliche Ausdruck?
- Bildhaftigkeit: Wie stark nutzt die Person Metaphern und bildhafte Sprache?

## Gesprächsführung
1. Beginne mit einer warmen Begrüßung und erkläre kurz den Ablauf
2. Stelle Fragen, die natürlich wirken — keine Fragebögen-Atmosphäre
3. Nutze Szenarien und Situationsbeschreibungen: "Stell dir vor, du stehst vor 50 Leuten..."
4. Passe deine Fragen an die bisherigen Antworten an
5. Sprich maximal 2-3 Frequenzen pro Frage an
6. Gib zwischendurch wertschätzendes Feedback
7. Nach ca. 15-20 Fragen solltest du ein gutes Bild haben

## Scoring
Bewerte jede Frequenz intern auf einer Skala von 1-10 basierend auf den Antworten.
Tracke deinen Fortschritt und informiere den Nutzer.

## Wichtig
- Sei empathisch und wertschätzend — niemals wertend
- Es gibt keine "schlechten" Ergebnisse, nur Entwicklungsfelder
- Betone: Wirkungskompetenz ist trainierbar
- Sprich Deutsch, außer der Nutzer wechselt die Sprache
"""


class DiagnosisAgent:
    def __init__(self):
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        self.client = anthropic.AsyncAnthropic(api_key=api_key) if api_key else None
        self.sessions: dict[str, dict[str, Any]] = {}
        self.backend_url = os.environ.get("BACKEND_URL", "http://backend:8000")

    async def start_session(self, run_id: str) -> str:
        self.sessions[run_id] = {
            "messages": [],
            "scores": {},
            "progress": 0.0,
            "question_count": 0,
        }

        if not self.client:
            return (
                "Willkommen bei deiner SCIL-Diagnostik! 🎯\n\n"
                "Ich bin dein KI-Coach und werde in den nächsten 15-20 Minuten ein Gespräch mit dir führen, "
                "um dein persönliches Wirkungsprofil zu erstellen.\n\n"
                "Es gibt dabei keine richtigen oder falschen Antworten — es geht darum, wie du kommunizierst "
                "und auf andere wirkst. Und das Beste: Alles, was wir hier herausfinden, ist trainierbar!\n\n"
                "Lass uns starten: **Erzähl mir kurz, in welchem beruflichen Kontext du gerade unterwegs bist "
                "und was dich hierher geführt hat.**"
            )

        response = await self.client.messages.create(
            model="claude-sonnet-4-5-20250514",
            max_tokens=500,
            system=SCIL_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": "Bitte starte die Diagnostik-Session mit einer Begrüßung."}],
        )
        greeting = response.content[0].text
        self.sessions[run_id]["messages"].append({"role": "assistant", "content": greeting})
        return greeting

    async def process_message(self, run_id: str, user_message: str) -> dict[str, Any]:
        session = self.sessions.get(run_id)
        if not session:
            return {"message": "Session nicht gefunden. Bitte starte eine neue Diagnostik.", "is_complete": False}

        session["messages"].append({"role": "user", "content": user_message})
        session["question_count"] += 1

        # Calculate progress (roughly 20 exchanges for full assessment)
        progress = min(session["question_count"] / 20, 0.95)
        session["progress"] = progress

        if not self.client:
            # Demo mode without API key
            return self._demo_response(session)

        # Build messages for Claude
        messages = session["messages"].copy()

        # Add scoring instruction as we progress
        scoring_instruction = ""
        if session["question_count"] > 5:
            scoring_instruction = (
                "\n\n[INTERN: Aktualisiere deine Einschätzung der 16 Frequenzen basierend auf dem bisherigen Gespräch. "
                "Gib am Ende deiner Antwort ein JSON-Block mit deinen aktuellen Scores an, Format: "
                '{"scores": {"sensus": {"inner_presence": X, ...}, ...}, "progress": Y}. '
                "Dieses JSON wird dem Nutzer NICHT gezeigt.]"
            )

        if session["question_count"] >= 18:
            scoring_instruction += "\n\n[INTERN: Du nähert dich dem Ende der Diagnostik. Bereite einen Abschluss vor.]"

        response = await self.client.messages.create(
            model="claude-sonnet-4-5-20250514",
            max_tokens=800,
            system=SCIL_SYSTEM_PROMPT + scoring_instruction,
            messages=messages,
        )

        agent_message = response.content[0].text
        session["messages"].append({"role": "assistant", "content": agent_message})

        # Extract scores if present
        polygon_update = None
        is_complete = session["question_count"] >= 20

        if "```json" in agent_message:
            try:
                json_start = agent_message.index("```json") + 7
                json_end = agent_message.index("```", json_start)
                scores_data = json.loads(agent_message[json_start:json_end])
                session["scores"] = scores_data.get("scores", session["scores"])
                polygon_update = session["scores"]
                agent_message = agent_message[:agent_message.index("```json")].strip()
            except (ValueError, json.JSONDecodeError):
                pass

        result = {
            "message": agent_message,
            "progress": progress,
            "polygon_update": polygon_update,
            "is_complete": is_complete,
        }

        if is_complete:
            result["scores"] = session["scores"]
            result["polygon_data"] = self._compute_polygon(session["scores"])
            result["summary"] = await self._generate_summary(session)

        return result

    def _demo_response(self, session: dict) -> dict[str, Any]:
        """Fallback demo responses when no API key is configured."""
        q = session["question_count"]
        demo_questions = [
            "Danke für den Kontext! Jetzt mal eine Situation: **Stell dir vor, du betrittst einen Raum mit 20 Personen, die du nicht kennst. Was ist dein erster Impuls — gehst du direkt auf jemanden zu, beobachtest du erst, oder suchst du einen vertrauten Anker?**",
            "Interessant! Und wie würdest du dein Auftreten in dieser Situation beschreiben? **Wenn du dir selbst bei einem Vortrag zuschauen könntest — was würde dir auffallen? Nutzt du viel Gestik? Wie laut und moduliert sprichst du?**",
            "Gut zu wissen! Jetzt zum Thema Struktur: **Wenn du eine neue Idee präsentierst, startest du eher mit dem großen Bild und einer emotionalen Geschichte, oder mit Fakten, Daten und einer klaren Gliederung?**",
            "Spannend! **Was passiert, wenn in einem Meeting eine emotional aufgeladene Situation entsteht — ein Konflikt, Frustration, Unsicherheit? Wie reagierst du?**",
            "Letzte Frage: **Wenn du eine Person beschreiben müsstest, die du als besonders charismatisch empfindest — was macht diese Person aus? Und in welchem dieser Aspekte siehst du dich selbst?**",
        ]

        is_complete = q >= 5  # Demo: complete after 5 questions

        if q <= len(demo_questions):
            message = demo_questions[q - 1]
        else:
            message = "Vielen Dank! Ich habe jetzt ein gutes Bild. Lass mich dein SCIL-Profil berechnen..."
            is_complete = True

        demo_scores = {
            "sensus": {"inner_presence": 7.2, "conviction": 6.8, "moment_focus": 7.5, "emotionality": 5.9},
            "corpus": {"appearance": 6.5, "gesture": 5.8, "facial_expression": 7.1, "spatial_presence": 6.3},
            "intellektus": {"analytics": 8.1, "goal_orientation": 7.8, "structure": 8.4, "objectivity": 7.6},
            "lingua": {"voice": 6.9, "articulation": 7.3, "eloquence": 7.0, "imagery": 6.2},
        }

        result = {
            "message": message,
            "progress": min(q / 5, 1.0),
            "polygon_update": demo_scores if q >= 3 else None,
            "is_complete": is_complete,
        }

        if is_complete:
            result["scores"] = demo_scores
            result["polygon_data"] = self._compute_polygon(demo_scores)
            result["summary"] = (
                "## Dein SCIL-Profil\n\n"
                "Dein Profil zeigt eine starke Ausprägung im Bereich **Intellektus** — du denkst "
                "strukturiert, argumentierst analytisch und verfolgst klare Ziele. Dein **Sensus**-Bereich "
                "ist ebenfalls gut ausgeprägt, besonders in Momentfokussierung und innerer Präsenz.\n\n"
                "**Entwicklungsfelder:**\n"
                "- **Corpus**: Gestik und Raumpräsenz könnten gezielt ausgebaut werden\n"
                "- **Lingua**: Bildhaftigkeit und Stimm-Modulation bieten Potenzial\n\n"
                "Die gute Nachricht: All das ist trainierbar!"
            )

        return result

    def _compute_polygon(self, scores: dict) -> dict:
        """Compute polygon visualization data from scores."""
        if not scores:
            return {}

        polygon = {}
        for area, freqs in scores.items():
            if isinstance(freqs, dict):
                polygon[area] = {
                    "frequencies": freqs,
                    "average": sum(freqs.values()) / len(freqs) if freqs else 0,
                }

        # Calculate overall balance
        averages = [v["average"] for v in polygon.values() if "average" in v]
        if averages:
            mean = sum(averages) / len(averages)
            variance = sum((a - mean) ** 2 for a in averages) / len(averages)
            balance = max(0, 10 - variance * 2)  # Lower variance = higher balance
            polygon["overall_balance"] = round(balance, 1)

        return polygon

    async def _generate_summary(self, session: dict) -> str:
        """Generate a natural language summary of the results."""
        if not self.client:
            return session.get("scores", {}).get("summary", "Zusammenfassung wird erstellt...")

        scores_str = json.dumps(session.get("scores", {}), indent=2)
        response = await self.client.messages.create(
            model="claude-sonnet-4-5-20250514",
            max_tokens=800,
            system="Du bist ein SCIL-Experte. Erstelle eine wertschätzende, ermutigende Zusammenfassung des SCIL-Profils.",
            messages=[{
                "role": "user",
                "content": f"Erstelle eine Zusammenfassung dieses SCIL-Profils:\n{scores_str}\n\nBetone Stärken und zeige Entwicklungsfelder als Chancen auf. Formatiere als Markdown.",
            }],
        )
        return response.content[0].text

    async def save_session(self, run_id: str):
        """Save session state to backend."""
        session = self.sessions.get(run_id)
        if not session:
            return
        # In production: POST to backend API to persist
        # async with httpx.AsyncClient() as client:
        #     await client.post(f"{self.backend_url}/api/v1/diagnostics/runs/{run_id}/save", json=session)
