import os
from typing import Any

import anthropic
import httpx


COACHING_SYSTEM_PROMPT = """Du bist der SCIL Personal Development Coach — ein empathischer, evidenzbasierter KI-Coach für persönliche Entwicklung.

## Deine Rolle
Du hilfst Nutzern, ihre diagnostischen Ergebnisse zu verstehen und in konkrete Entwicklungsschritte umzusetzen.
Du kennst dich aus mit:
- SCIL-Wirkungskompetenz (16 Frequenzen)
- Big Five Persönlichkeitsmodell
- Emotionale Intelligenz
- Wertediagnostik (Schwartz)
- Resilienz-Forschung
- Evidenzbasierte Coaching-Methoden

## Coaching-Prinzipien
1. **Stärkenbasiert**: Beginne immer mit dem, was schon gut funktioniert
2. **Lösungsorientiert**: Fokus auf "Was willst du erreichen?" statt "Was ist das Problem?"
3. **Konkret**: Gib immer umsetzbare Tipps und Übungen
4. **Empathisch**: Höre aktiv zu, validiere Gefühle
5. **Evidenzbasiert**: Verweise auf wissenschaftliche Erkenntnisse wo passend
6. **Empowerment**: Der Nutzer ist der Experte für sein Leben

## Gesprächsformate
- **Check-in**: Kurzer täglicher Impuls (2-3 Min)
- **Situatives Coaching**: Nutzer kommt mit einer konkreten Situation
- **Entwicklungsplanung**: Langfristige Ziele und Meilensteine setzen
- **Vorbereitung**: z.B. auf eine Präsentation, ein Meeting, ein Gespräch

## Grenzen
- Bei psychischen Krisen → Verweis an professionelle Hilfe
- Bei komplexen Themen → Vermittlung an menschliche Coaches aus dem Netzwerk
- Du stellst keine Diagnosen im klinischen Sinne

Sprich Deutsch, außer der Nutzer wechselt die Sprache.
"""


class CoachingAgent:
    def __init__(self):
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        self.client = anthropic.AsyncAnthropic(api_key=api_key) if api_key else None
        self.sessions: dict[str, dict[str, Any]] = {}
        self.backend_url = os.environ.get("BACKEND_URL", "http://backend:8000")

    async def start_session(self, user_id: str) -> str:
        self.sessions[user_id] = {
            "messages": [],
            "user_profile": None,
        }

        greeting = (
            "Hallo! Ich bin dein persönlicher Entwicklungs-Coach. "
            "Ich kenne deine Diagnostik-Ergebnisse und bin hier, um dich bei deiner Weiterentwicklung zu unterstützen.\n\n"
            "**Was kann ich für dich tun?**\n"
            "- Ergebnisse besprechen und verstehen\n"
            "- Situatives Coaching (z.B. Vorbereitung auf ein Meeting)\n"
            "- Entwicklungsplan erstellen\n"
            "- Täglicher Check-in und Impulse\n\n"
            "Was beschäftigt dich gerade?"
        )

        if self.client:
            response = await self.client.messages.create(
                model="claude-sonnet-4-5-20250514",
                max_tokens=400,
                system=COACHING_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": "Bitte begrüße mich als meinen Coaching-Agenten."}],
            )
            greeting = response.content[0].text

        self.sessions[user_id]["messages"].append({"role": "assistant", "content": greeting})
        return greeting

    async def process_message(self, user_id: str, user_message: str) -> dict[str, Any]:
        session = self.sessions.get(user_id)
        if not session:
            return {"message": "Session nicht gefunden.", "suggestions": []}

        session["messages"].append({"role": "user", "content": user_message})

        if not self.client:
            return {
                "message": (
                    "Das ist eine tolle Frage! Basierend auf deinem Profil würde ich vorschlagen, "
                    "dass wir uns zunächst auf deine Stärken im Bereich Intellektus konzentrieren "
                    "und dann schauen, wie wir dein Corpus-Repertoire erweitern können.\n\n"
                    "**Konkrete Übung für diese Woche:**\n"
                    "Achte in deinem nächsten Meeting bewusst auf deine Gestik. "
                    "Nutze offene Handgesten, wenn du sprichst, und nimm bewusst Raum ein.\n\n"
                    "*Hinweis: Für eine vollständige Coaching-Erfahrung hinterlege bitte deinen ANTHROPIC_API_KEY.*"
                ),
                "suggestions": [
                    "Mein SCIL-Profil besprechen",
                    "Vorbereitung auf eine Präsentation",
                    "Entwicklungsplan erstellen",
                ],
            }

        response = await self.client.messages.create(
            model="claude-sonnet-4-5-20250514",
            max_tokens=600,
            system=COACHING_SYSTEM_PROMPT,
            messages=session["messages"],
        )

        agent_message = response.content[0].text
        session["messages"].append({"role": "assistant", "content": agent_message})

        return {
            "message": agent_message,
            "suggestions": [],
        }

    async def save_session(self, user_id: str):
        """Save session state."""
        pass
