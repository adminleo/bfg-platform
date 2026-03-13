"""SCIL Coaching Agent — evidence-based personal development coaching.

Ported from gr8hub agent-service, scoped to SCIL context.
"""

import os
from typing import Any

import anthropic


COACHING_SYSTEM_PROMPT = """Du bist der SCIL Personal Development Coach — ein empathischer, evidenzbasierter KI-Coach fuer persoenliche Entwicklung.

## Deine Rolle
Du hilfst Nutzern, ihre SCIL-Wirkungsprofile zu verstehen und in konkrete Entwicklungsschritte umzusetzen.
SCIL misst Wirkungskompetenz (Aussenwirkung), nicht Persoenlichkeit — alles ist trainierbar!

## SCIL-Framework
4 Frequenzbereiche mit je 4 Frequenzen (16 total):
- Sensus: Innere Praesenz, Innere Ueberzeugung, Prozessfokussierung, Emotionalitaet
- Corpus: Erscheinungsbild, Mimik, Gestik, Raeumliche Praesenz
- Intellektus: Sachlichkeit, Analytik, Struktur, Zielorientierung
- Lingua: Stimme, Artikulation, Beredsamkeit, Bildhaftigkeit

Charisma-Hypothese: Maximale Balance aller 16 Frequenzen auf hohem Niveau = hoechste Interaktionskompetenz.

## Coaching-Prinzipien
1. Staerkenbasiert: Beginne immer mit dem, was schon gut funktioniert
2. Loesungsorientiert: Fokus auf "Was willst du erreichen?"
3. Konkret: Gib immer umsetzbare Tipps und Uebungen
4. Empathisch: Hoere aktiv zu, validiere Gefuehle
5. Evidenzbasiert: Verweise auf wissenschaftliche Erkenntnisse wo passend
6. Empowerment: Der Nutzer ist der Experte fuer sein Leben

## Grenzen
- Bei psychischen Krisen -> Verweis an professionelle Hilfe
- Bei komplexen Themen -> Vermittlung an SCIL-Experten aus dem Partner-Netzwerk
- Du stellst keine Diagnosen im klinischen Sinne

Sprich Deutsch, ausser der Nutzer wechselt die Sprache.
"""


class CoachingAgent:
    def __init__(self):
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        self.client = anthropic.AsyncAnthropic(api_key=api_key) if api_key else None
        self.sessions: dict[str, dict[str, Any]] = {}

    async def start_session(self, user_id: str) -> str:
        self.sessions[user_id] = {
            "messages": [],
            "user_profile": None,
        }

        greeting = (
            "Hallo! Ich bin dein persoenlicher SCIL-Coach. "
            "Ich kenne dein Wirkungsprofil und bin hier, um dich bei deiner Weiterentwicklung zu unterstuetzen.\n\n"
            "**Was kann ich fuer dich tun?**\n"
            "- Ergebnisse besprechen und verstehen\n"
            "- Situatives Coaching (z.B. Vorbereitung auf ein Meeting)\n"
            "- Entwicklungsplan erstellen\n"
            "- Taeglicher Check-in und Impulse\n\n"
            "Was beschaeftigt dich gerade?"
        )

        if self.client:
            response = await self.client.messages.create(
                model="claude-sonnet-4-5-20250514",
                max_tokens=400,
                system=COACHING_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": "Bitte begruesse mich als meinen SCIL-Coaching-Agenten."}],
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
                    "Das ist eine tolle Frage! Basierend auf deinem Wirkungsprofil wuerde ich vorschlagen, "
                    "dass wir uns zunaechst auf deine Staerken im Bereich Intellektus konzentrieren "
                    "und dann schauen, wie wir dein Corpus-Repertoire erweitern koennen.\n\n"
                    "**Konkrete Uebung fuer diese Woche:**\n"
                    "Achte in deinem naechsten Meeting bewusst auf deine Gestik. "
                    "Nutze offene Handgesten, wenn du sprichst, und nimm bewusst Raum ein.\n\n"
                    "*Hinweis: Fuer eine vollstaendige Coaching-Erfahrung hinterlege bitte deinen ANTHROPIC_API_KEY.*"
                ),
                "suggestions": [
                    "Mein SCIL-Profil besprechen",
                    "Vorbereitung auf eine Praesentation",
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

        return {"message": agent_message, "suggestions": []}
