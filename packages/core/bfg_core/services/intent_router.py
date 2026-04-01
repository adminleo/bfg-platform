"""Extensible Intent Router — LLM-first classification with keyword fallback.

Base router provides core intents (GENERAL, HELP, EXPLAIN, COMPARE).
Products extend by registering their own intents + keywords at startup.

Usage:
    from bfg_core.services.intent_router import IntentRouter, BaseIntent, IntentResult

    router = IntentRouter(ai_service=ai_svc)

    # Register SCIL-specific intents
    router.register_intents({
        "scil_start": ["diagnostik starten", "profil erstellen", "scil starten"],
        "scil_explain": ["frequenz erklaeren", "was bedeutet sensus"],
        "scil_coaching": ["coaching", "entwicklung", "training"],
    })

    result = await router.classify("Ich moechte mein SCIL-Profil erstellen")
    # IntentResult(intent="scil_start", confidence=0.95, method="llm")
"""

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class BaseIntent(str, Enum):
    """Core intents shared across all BFG products."""
    GENERAL = "general"
    HELP = "help"
    EXPLAIN = "explain"
    COMPARE = "compare"
    UNKNOWN = "unknown"


@dataclass
class IntentResult:
    """Result of intent classification."""
    intent: str
    confidence: float  # 0.0 to 1.0
    method: str  # "llm" or "keyword"
    raw_response: str | None = None  # LLM raw response for debugging


# Default keyword map for base intents (DE + EN)
_DEFAULT_KEYWORDS: dict[str, list[str]] = {
    "help": [
        "hilfe", "help", "was kannst du", "what can you",
        "funktionen", "features", "anleitung", "guide",
    ],
    "explain": [
        "erklaer", "explain", "warum", "why", "bedeutet",
        "was ist", "what is", "definition", "beschreib",
    ],
    "compare": [
        "vergleich", "compare", "unterschied", "difference",
        "gegenueber", "versus", "vs",
    ],
}

# Classification system prompt
_CLASSIFICATION_PROMPT = """Du bist ein Intent-Klassifikator. Ordne die Benutzernachricht einem der folgenden Intents zu.

Verfuegbare Intents:
{intent_list}

Antworte NUR mit dem Intent-Namen (Kleinbuchstaben, ein Wort). Keine Erklaerung.

Wenn die Nachricht zu keinem Intent passt, antworte mit "unknown".
"""


class IntentRouter:
    """Extensible intent classification with LLM-first approach and keyword fallback.

    Args:
        ai_service: Optional AIService instance for LLM classification.
                    If None, only keyword matching is used.
        keyword_map: Additional keyword map to merge with defaults.
                     Dict of intent_name -> list of keywords/phrases.
        classification_prompt: Override the default classification prompt.
    """

    def __init__(
        self,
        ai_service: Any | None = None,
        keyword_map: dict[str, list[str]] | None = None,
        classification_prompt: str | None = None,
    ):
        self._ai_service = ai_service
        self._classification_prompt = classification_prompt or _CLASSIFICATION_PROMPT

        # Build keyword map: defaults + any provided overrides
        self._keyword_map: dict[str, list[str]] = dict(_DEFAULT_KEYWORDS)
        if keyword_map:
            self._keyword_map.update(keyword_map)

        # All known intent names (for LLM prompt and validation)
        self._known_intents: set[str] = set()
        for intent in BaseIntent:
            self._known_intents.add(intent.value)
        if keyword_map:
            self._known_intents.update(keyword_map.keys())

    def register_intents(self, intents: dict[str, list[str]]) -> None:
        """Register additional intents with their keywords.

        Called by product apps at startup to extend the router.

        Args:
            intents: Dict of intent_name -> list of keywords/phrases.
                     Example: {"scil_start": ["diagnostik starten", "profil erstellen"]}
        """
        for intent_name, keywords in intents.items():
            self._known_intents.add(intent_name)
            if intent_name in self._keyword_map:
                self._keyword_map[intent_name].extend(keywords)
            else:
                self._keyword_map[intent_name] = list(keywords)

        logger.info(
            "Registered %d intent(s): %s",
            len(intents), ", ".join(intents.keys()),
        )

    async def classify(
        self,
        message: str,
        *,
        context: dict | None = None,
        language: str = "de",
    ) -> IntentResult:
        """Classify a user message into an intent.

        Strategy:
        1. If AIService is configured: try LLM classification first
        2. Fallback to keyword matching
        3. Default to UNKNOWN

        Args:
            message: The user's message text.
            context: Optional context dict (e.g., current_page, session_state).
            language: Language code ("de" or "en").

        Returns:
            IntentResult with intent, confidence, and method.
        """
        # Try LLM classification first
        if self._ai_service and self._ai_service.is_configured():
            try:
                result = await self._llm_classify(message, context, language)
                if result.confidence >= 0.5:
                    return result
                # Low confidence from LLM — try keyword as tiebreaker
                keyword_result = self._keyword_classify(message)
                if keyword_result.confidence > result.confidence:
                    return keyword_result
                return result
            except Exception as e:
                logger.warning("LLM classification failed, using keyword fallback: %s", e)

        # Keyword fallback
        return self._keyword_classify(message)

    def _keyword_classify(self, message: str) -> IntentResult:
        """Classify using keyword matching.

        Scores each intent by counting keyword matches in the message.
        Returns the intent with the highest score (or UNKNOWN if no matches).
        """
        message_lower = message.lower().strip()
        scores: dict[str, int] = {}

        for intent_name, keywords in self._keyword_map.items():
            score = 0
            for keyword in keywords:
                keyword_lower = keyword.lower()
                # Check for substring match
                if keyword_lower in message_lower:
                    # Longer keywords get more weight
                    score += len(keyword_lower.split())
            if score > 0:
                scores[intent_name] = score

        if not scores:
            return IntentResult(
                intent=BaseIntent.GENERAL.value,
                confidence=0.1,
                method="keyword",
            )

        # Pick highest-scoring intent
        best_intent = max(scores, key=scores.get)  # type: ignore
        max_score = scores[best_intent]

        # Normalize confidence: 1 keyword match = 0.5, 2 = 0.7, 3+ = 0.85
        if max_score >= 3:
            confidence = 0.85
        elif max_score >= 2:
            confidence = 0.7
        else:
            confidence = 0.5

        return IntentResult(
            intent=best_intent,
            confidence=confidence,
            method="keyword",
        )

    async def _llm_classify(
        self,
        message: str,
        context: dict | None,
        language: str,
    ) -> IntentResult:
        """Classify using LLM — small, fast model call."""
        intent_list = "\n".join(f"- {name}" for name in sorted(self._known_intents))
        system_prompt = self._classification_prompt.format(intent_list=intent_list)

        # Use a fast/cheap model for classification
        response = await self._ai_service.generate(
            message,
            system=system_prompt,
            model="claude-3-5-haiku-20241022",  # Fast + cheap
            max_tokens=50,
            temperature=0.0,
            intent="classification",
        )

        if not response:
            return IntentResult(
                intent=BaseIntent.UNKNOWN.value,
                confidence=0.0,
                method="llm",
                raw_response="",
            )

        # Parse response — expect a single intent name
        parsed = response.strip().lower().replace('"', "").replace("'", "")
        # Remove any explanation after the intent name
        parsed = re.split(r"[\s\n.,;:]", parsed)[0]

        if parsed in self._known_intents:
            return IntentResult(
                intent=parsed,
                confidence=0.9,
                method="llm",
                raw_response=response,
            )

        # Fuzzy match: check if the response contains any known intent
        for intent_name in self._known_intents:
            if intent_name in parsed or parsed in intent_name:
                return IntentResult(
                    intent=intent_name,
                    confidence=0.7,
                    method="llm",
                    raw_response=response,
                )

        return IntentResult(
            intent=BaseIntent.UNKNOWN.value,
            confidence=0.3,
            method="llm",
            raw_response=response,
        )
