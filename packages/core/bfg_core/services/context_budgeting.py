"""Context Budgeting — Token-aware context management for LLM calls.

Provides helpers for:
1. Estimating token cost of text (heuristic, no dependencies)
2. Resolving context limits per provider/model
3. Smart truncation of assessment context
4. Token-aware conversation windowing
5. Building final LLM payloads within budget

Ported from cNode context_budgeting.py, adapted for BFG Platform.
Zero external dependencies — pure Python only.
"""

import logging
import math
import os
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


# ============================================================================
# Part 1: Token Estimation (heuristic, no deps)
# ============================================================================

# Rough character-to-token ratio.
# English text: ~4 chars/token; code/symbols: ~3.5 chars/token
_CHARS_PER_TOKEN_DEFAULT = 4.0
_CHARS_PER_TOKEN_CODE = 3.5

# Threshold: if >15% of chars are non-alphanumeric, treat as code-heavy
_CODE_SYMBOL_RATIO_THRESHOLD = 0.15


def estimate_tokens(text: str) -> int:
    """Estimate the number of tokens in a text string.

    Uses a fast heuristic: ~4 chars per token for prose,
    ~3.5 chars per token for code-heavy text (many symbols/newlines).

    No external tokenizer libraries required.
    """
    if not text:
        return 0

    length = len(text)

    # Count non-alphanumeric, non-space characters (symbols, brackets, etc.)
    symbol_count = sum(1 for c in text if not c.isalnum() and not c.isspace())
    symbol_ratio = symbol_count / max(length, 1)

    if symbol_ratio > _CODE_SYMBOL_RATIO_THRESHOLD:
        return math.ceil(length / _CHARS_PER_TOKEN_CODE)
    return math.ceil(length / _CHARS_PER_TOKEN_DEFAULT)


# ============================================================================
# Part 2: Context Limit Resolution
# ============================================================================

# Known context limits by provider + model prefix (conservative estimates).
# These are input token limits; output tokens are reserved separately.
_KNOWN_CONTEXT_LIMITS: Dict[str, int] = {
    # Anthropic
    "claude-sonnet-4": 200_000,
    "claude-opus-4": 200_000,
    "claude-4": 200_000,
    "claude-3-7-sonnet": 200_000,
    "claude-3-5-sonnet": 200_000,
    "claude-3-5-haiku": 200_000,
    "claude-3-opus": 200_000,
    "claude-3-sonnet": 200_000,
    "claude-3-haiku": 200_000,

    # OpenAI
    "gpt-4o": 128_000,
    "gpt-4o-mini": 128_000,
    "gpt-4-turbo": 128_000,
    "gpt-4.1": 128_000,
    "gpt-4.1-mini": 128_000,
    "gpt-4.1-nano": 128_000,
    "gpt-4": 8_192,
    "gpt-3.5-turbo": 16_385,
    "o1": 200_000,
    "o1-mini": 128_000,
    "o3": 200_000,
    "o3-mini": 128_000,
    "o4-mini": 200_000,

    # Ollama / local models
    "llama3": 8_192,
    "llama3.1": 128_000,
    "llama3.2": 128_000,
    "mistral": 32_768,
    "mixtral": 32_768,
    "phi-3": 128_000,
    "gemma2": 8_192,
    "qwen2.5": 32_768,
}

# Provider-level defaults when model is not in the known table
_PROVIDER_DEFAULTS: Dict[str, int] = {
    "anthropic": 200_000,
    "openai": 128_000,
    "ollama": 16_000,
}

# Absolute fallback
_DEFAULT_CONTEXT_LIMIT = 32_000

# Safety margin: use only this fraction of the limit (keeps headroom)
_SAFETY_MARGIN = 0.85

# Output reserves by task type (tokens reserved for model response)
OUTPUT_RESERVES: Dict[str, int] = {
    "chat": 800,
    "scoring": 1_500,
    "coaching": 1_200,
    "classification": 400,
}

OUTPUT_RESERVE_DEFAULT = 800


def resolve_context_limit(
    provider: Optional[str] = None,
    model: Optional[str] = None,
) -> int:
    """Resolve the effective input token limit for a provider/model pair.

    Resolution order:
    1. Environment variable CONTEXT_LIMIT_OVERRIDE
    2. Known model table — prefix match
    3. Provider default
    4. Absolute fallback (32,000)

    Returns the usable limit after applying the 85% safety margin.
    """
    # 1. Environment override
    env_limit = os.environ.get("CONTEXT_LIMIT_OVERRIDE")
    if env_limit:
        try:
            raw = int(env_limit)
            return int(raw * _SAFETY_MARGIN)
        except (ValueError, TypeError):
            pass

    # 2. Model-specific lookup (prefix match)
    raw_limit = None
    if model:
        model_lower = model.lower()
        for key, limit in _KNOWN_CONTEXT_LIMITS.items():
            if model_lower.startswith(key):
                raw_limit = limit
                break

    # 3. Provider default
    if raw_limit is None and provider:
        raw_limit = _PROVIDER_DEFAULTS.get(provider.lower())

    # 4. Absolute fallback
    if raw_limit is None:
        raw_limit = _DEFAULT_CONTEXT_LIMIT

    return int(raw_limit * _SAFETY_MARGIN)


# ============================================================================
# Part 3: Smart Context Truncation
# ============================================================================

_TRUNCATION_MARKER = "\n\n[… context truncated to fit model limits …]\n"


def build_context_bundle(
    context_text: Optional[str],
    budget_tokens: int,
) -> Dict[str, Any]:
    """Truncate assessment context to fit within a token budget.

    Strategy:
    - If the context fits within budget, return it unchanged.
    - If it exceeds budget, keep:
      - First 1,000 chars (head snippet — usually the core context)
      - Most recent content (recency bias) up to remaining budget
      - Truncation marker in the middle

    Returns:
        {
            "context_text": str,
            "used_tokens": int,
            "original_tokens": int,
            "truncated": bool,
            "omitted_chars": int,
        }
    """
    if not context_text:
        fallback = "No additional context provided."
        return {
            "context_text": fallback,
            "used_tokens": estimate_tokens(fallback),
            "original_tokens": 0,
            "truncated": False,
            "omitted_chars": 0,
        }

    original_tokens = estimate_tokens(context_text)

    if original_tokens <= budget_tokens:
        return {
            "context_text": context_text,
            "used_tokens": original_tokens,
            "original_tokens": original_tokens,
            "truncated": False,
            "omitted_chars": 0,
        }

    # Need to truncate. Convert token budget to approximate char budget.
    char_budget = int(budget_tokens * _CHARS_PER_TOKEN_DEFAULT)
    marker_len = len(_TRUNCATION_MARKER)

    # Reserve space for head snippet + marker
    head_size = min(1_000, char_budget // 4)
    tail_budget = char_budget - head_size - marker_len

    if tail_budget <= 0:
        # Extreme budget — just take first N chars
        truncated_text = context_text[:char_budget]
        return {
            "context_text": truncated_text,
            "used_tokens": estimate_tokens(truncated_text),
            "original_tokens": original_tokens,
            "truncated": True,
            "omitted_chars": len(context_text) - char_budget,
        }

    head = context_text[:head_size]
    tail = context_text[-tail_budget:]

    truncated_text = head + _TRUNCATION_MARKER + tail
    omitted = len(context_text) - head_size - tail_budget

    return {
        "context_text": truncated_text,
        "used_tokens": estimate_tokens(truncated_text),
        "original_tokens": original_tokens,
        "truncated": True,
        "omitted_chars": max(0, omitted),
    }


# ============================================================================
# Part 4: Token-aware Conversation Windowing
# ============================================================================

_MIN_MESSAGES = 4  # Always try to include at least the last 4 messages
_SUMMARY_MAX_TOKENS = 300  # Budget for older-messages summary


def build_conversation_window(
    messages: List[Dict[str, str]],
    budget_tokens: int,
) -> Dict[str, Any]:
    """Select the maximum recent conversation history within a token budget.

    Strategy:
    - Start from the most recent message, add backwards.
    - Always include at least the last 4 messages (unless they alone exceed budget).
    - If older messages are omitted, include a short summary block.

    Args:
        messages: List of {"role": "user"|"assistant", "content": "..."} dicts
        budget_tokens: Available token budget for conversation history

    Returns:
        {
            "selected": list,
            "omitted_count": int,
            "summary_text": str,
            "used_tokens": int,
        }
    """
    if not messages:
        return {
            "selected": [],
            "omitted_count": 0,
            "summary_text": "",
            "used_tokens": 0,
        }

    if budget_tokens <= 0:
        return {
            "selected": [],
            "omitted_count": len(messages),
            "summary_text": "",
            "used_tokens": 0,
        }

    # Calculate token cost per message
    msg_costs = []
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        formatted = f"[{role}]: {content}"
        tokens = estimate_tokens(formatted)
        msg_costs.append(tokens)

    # Build window from most recent backwards
    total = len(messages)
    included_tokens = 0
    included_count = 0

    # Phase 1: Always include last _MIN_MESSAGES (up to budget)
    for i in range(total - 1, max(total - _MIN_MESSAGES - 1, -1), -1):
        cost = msg_costs[i]
        if included_tokens + cost > budget_tokens and included_count >= 2:
            break
        included_tokens += cost
        included_count += 1

    # Phase 2: Keep adding older messages while budget allows
    remaining_budget = budget_tokens - included_tokens - _SUMMARY_MAX_TOKENS
    scan_idx = total - included_count - 1

    while scan_idx >= 0 and remaining_budget > 0:
        cost = msg_costs[scan_idx]
        if cost > remaining_budget:
            break
        included_tokens += cost
        included_count += 1
        remaining_budget -= cost
        scan_idx -= 1

    # Select messages (most recent N)
    start_idx = total - included_count
    selected = messages[start_idx:]
    omitted_count = start_idx

    # Build summary of omitted messages
    summary_text = ""
    if omitted_count > 0:
        summary_text = _build_omission_summary(messages[:start_idx])
        included_tokens += estimate_tokens(summary_text)

    return {
        "selected": selected,
        "omitted_count": omitted_count,
        "summary_text": summary_text,
        "used_tokens": included_tokens,
    }


def _build_omission_summary(omitted_messages: List[Dict[str, str]]) -> str:
    """Build a deterministic summary of omitted conversation messages.

    No LLM summarization — just a brief rule-based note.
    """
    if not omitted_messages:
        return ""

    count = len(omitted_messages)
    user_count = sum(1 for m in omitted_messages if m.get("role") == "user")

    # Extract key topics from last few omitted messages
    topic_snippets = []
    for msg in omitted_messages[-3:]:
        content = msg.get("content", "")
        snippet = content[:80].replace("\n", " ").strip()
        if snippet:
            topic_snippets.append(snippet)

    summary_parts = [
        f"[{count} earlier messages omitted ({user_count} from user)]"
    ]
    if topic_snippets:
        summary_parts.append("Recent topics: " + " | ".join(topic_snippets))

    return "\n".join(summary_parts)


# ============================================================================
# Part 5: Unified LLM Payload Builder
# ============================================================================

def build_budgeted_prompt(
    system_prompt: str,
    context_text: str,
    conversation_messages: Optional[List[Dict[str, str]]] = None,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    output_reserve: int = OUTPUT_RESERVE_DEFAULT,
) -> Dict[str, Any]:
    """Build a complete LLM prompt payload within context budget.

    Allocates the token budget across:
    1. System prompt (fixed — never truncated)
    2. Context text (assessment context — truncated if needed)
    3. Conversation history (windowed by token budget)
    4. Output reserve (reserved for the model's response)

    Returns:
        {
            "context_bundle": {...},
            "conversation_window": {...},
            "metrics": {
                "limit": int,
                "reserved_output": int,
                "used_est_tokens": int,
                "system_est_tokens": int,
                "context_est_tokens": int,
                "context_original_tokens": int,
                "history_est_tokens": int,
                "history_omitted_count": int,
                "truncated": bool,
            }
        }
    """
    total_limit = resolve_context_limit(provider, model)
    input_budget = total_limit - output_reserve

    # 1. System prompt (fixed cost)
    system_tokens = estimate_tokens(system_prompt)
    remaining = input_budget - system_tokens

    if remaining <= 0:
        logger.warning(
            "System prompt (%d est tokens) exceeds input budget (%d). Proceeding anyway.",
            system_tokens,
            input_budget,
        )
        remaining = max(500, input_budget // 2)  # Emergency floor

    # 2. Allocate budget: 60% context, 40% history (when both present)
    has_conversation = bool(conversation_messages)
    if has_conversation:
        context_budget = int(remaining * 0.6)
        history_budget = remaining - context_budget
    else:
        context_budget = remaining
        history_budget = 0

    # 3. Truncate context
    context_bundle = build_context_bundle(context_text, context_budget)

    # 4. If context used less than allocated, give surplus to history
    context_surplus = context_budget - context_bundle["used_tokens"]
    if context_surplus > 0 and has_conversation:
        history_budget += context_surplus

    # 5. Window conversation history
    if has_conversation and conversation_messages:
        window = build_conversation_window(conversation_messages, history_budget)
    else:
        window = {
            "selected": [],
            "omitted_count": 0,
            "summary_text": "",
            "used_tokens": 0,
        }

    # 6. Compute metrics
    total_used = system_tokens + context_bundle["used_tokens"] + window["used_tokens"]
    truncated = context_bundle["truncated"] or window["omitted_count"] > 0

    return {
        "context_bundle": context_bundle,
        "conversation_window": window,
        "metrics": {
            "limit": total_limit,
            "reserved_output": output_reserve,
            "used_est_tokens": total_used,
            "system_est_tokens": system_tokens,
            "context_est_tokens": context_bundle["used_tokens"],
            "context_original_tokens": context_bundle["original_tokens"],
            "history_est_tokens": window["used_tokens"],
            "history_omitted_count": window["omitted_count"],
            "truncated": truncated,
        },
    }


def budget_for_prompt(
    system_prompt: str,
    user_message: str,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    output_reserve: int = OUTPUT_RESERVE_DEFAULT,
) -> Dict[str, Any]:
    """Simple budget check for non-chat prompts (scoring, classification).

    For prompts that have no conversation history — just system + user message.
    Truncates the user message if it exceeds the budget.

    Returns:
        {
            "system_prompt": str,
            "user_message": str,
            "metrics": {
                "limit": int,
                "reserved_output": int,
                "used_est_tokens": int,
                "system_est_tokens": int,
                "user_est_tokens": int,
                "truncated": bool,
            }
        }
    """
    total_limit = resolve_context_limit(provider, model)
    input_budget = total_limit - output_reserve

    system_tokens = estimate_tokens(system_prompt)
    user_budget = input_budget - system_tokens

    if user_budget <= 0:
        logger.warning("System prompt exceeds budget; cannot truncate further.")
        return {
            "system_prompt": system_prompt,
            "user_message": user_message,
            "metrics": {
                "limit": total_limit,
                "reserved_output": output_reserve,
                "used_est_tokens": system_tokens + estimate_tokens(user_message),
                "system_est_tokens": system_tokens,
                "user_est_tokens": estimate_tokens(user_message),
                "truncated": False,
            },
        }

    user_tokens = estimate_tokens(user_message)
    truncated = False

    if user_tokens > user_budget:
        # Truncate user message to fit
        char_budget = int(user_budget * _CHARS_PER_TOKEN_DEFAULT)
        head_size = min(2_000, char_budget // 3)
        tail_size = char_budget - head_size - len(_TRUNCATION_MARKER)
        if tail_size > 0:
            user_message = (
                user_message[:head_size]
                + _TRUNCATION_MARKER
                + user_message[-tail_size:]
            )
        else:
            user_message = user_message[:char_budget]
        user_tokens = estimate_tokens(user_message)
        truncated = True

    return {
        "system_prompt": system_prompt,
        "user_message": user_message,
        "metrics": {
            "limit": total_limit,
            "reserved_output": output_reserve,
            "used_est_tokens": system_tokens + user_tokens,
            "system_est_tokens": system_tokens,
            "user_est_tokens": user_tokens,
            "truncated": truncated,
        },
    }
