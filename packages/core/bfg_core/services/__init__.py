"""BFG Core — Services: AI, Tokens, Email, Consent, Intent Routing, Context Budgeting."""

from bfg_core.services.ai_service import AIService
from bfg_core.services.token_service import TokenService
from bfg_core.services.email_service import EmailService
from bfg_core.services.consent_service import ConsentService
from bfg_core.services.intent_router import IntentRouter, BaseIntent, IntentResult
from bfg_core.services.context_budgeting import (
    estimate_tokens,
    resolve_context_limit,
    build_context_bundle,
    build_conversation_window,
    build_budgeted_prompt,
    budget_for_prompt,
    OUTPUT_RESERVES,
)

__all__ = [
    "AIService",
    "TokenService",
    "EmailService",
    "ConsentService",
    "IntentRouter",
    "BaseIntent",
    "IntentResult",
    "estimate_tokens",
    "resolve_context_limit",
    "build_context_bundle",
    "build_conversation_window",
    "build_budgeted_prompt",
    "budget_for_prompt",
    "OUTPUT_RESERVES",
]
