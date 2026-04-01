"""Multi-provider AI service with audit logging.

Provides a unified async interface to AI providers:
- Anthropic (Claude) — primary
- OpenAI (GPT) — fallback
- Ollama — local development

Every call is logged to AIAuditLog for compliance and cost tracking.

Ported from cNode ai_service.py (715 lines), converted to fully async,
simplified to env-based config (no DB provider configs).

Usage:
    from bfg_core.services.ai_service import AIService
    from bfg_core.config import CoreSettings

    settings = CoreSettings()
    ai = AIService(settings, session_factory)

    text = await ai.generate("Erklaere SCIL.", system="Du bist ein SCIL-Experte.")
"""

import logging
import time
from typing import Any, AsyncGenerator
from uuid import UUID

import httpx
from sqlalchemy.ext.asyncio import async_sessionmaker

from bfg_core.config import CoreSettings
from bfg_core.models.audit import AIAuditLog

logger = logging.getLogger(__name__)

# Default models per provider
_DEFAULT_MODELS = {
    "anthropic": "claude-sonnet-4-20250514",
    "openai": "gpt-4o",
    "ollama": "llama3.2",
}

# Rough cost per 1M tokens (USD) — for audit logging, not billing
_COST_TABLE: dict[str, tuple[float, float]] = {
    # (input_cost_per_1M, output_cost_per_1M)
    "claude-sonnet-4": (3.0, 15.0),
    "claude-3-5-sonnet": (3.0, 15.0),
    "claude-3-5-haiku": (0.80, 4.0),
    "claude-3-haiku": (0.25, 1.25),
    "gpt-4o": (2.50, 10.0),
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-4-turbo": (10.0, 30.0),
    "gpt-4.1": (2.0, 8.0),
    "gpt-4.1-mini": (0.40, 1.60),
    "gpt-4.1-nano": (0.10, 0.40),
    "o3-mini": (1.10, 4.40),
}


def _estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Estimate USD cost for a call. Returns 0.0 for unknown/local models."""
    model_lower = model.lower()
    for prefix, (in_cost, out_cost) in _COST_TABLE.items():
        if model_lower.startswith(prefix):
            return (input_tokens * in_cost + output_tokens * out_cost) / 1_000_000
    return 0.0


def _resolve_provider(model: str | None, llm_mode: str) -> tuple[str, str]:
    """Resolve provider name and model name from a model string or llm_mode."""
    if model:
        model_lower = model.lower()
        if model_lower.startswith("claude"):
            return "anthropic", model
        elif model_lower.startswith(("gpt-", "o1", "o3", "o4")):
            return "openai", model
        else:
            return "ollama", model

    mode = llm_mode.lower()
    if mode == "ollama":
        return "ollama", _DEFAULT_MODELS["ollama"]
    else:
        return "anthropic", _DEFAULT_MODELS["anthropic"]


class AIService:
    """Multi-provider async AI service with audit logging.

    Constructor takes settings and a session factory (for audit log persistence).
    User ID is passed per-call, not bound at construction time.
    """

    def __init__(
        self,
        settings: CoreSettings,
        session_factory: async_sessionmaker,
    ):
        self._settings = settings
        self._session_factory = session_factory
        self._anthropic_client = None
        self._openai_client = None
        self.last_token_usage: dict[str, Any] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def generate(
        self,
        prompt: str,
        *,
        system: str = "",
        model: str | None = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        user_id: UUID | None = None,
        intent: str | None = None,
        session_id: str | None = None,
    ) -> str:
        """Generate a text response using the configured AI provider.

        LLM_MODE controls routing:
        - cloud:  Use configured cloud provider (Anthropic or OpenAI)
        - ollama: Use local Ollama instance only
        - hybrid: Try cloud first, fallback to Ollama on failure

        Returns empty string if no AI is configured or all providers fail.
        """
        llm_mode = self._settings.llm_mode.lower()
        provider, model_name = _resolve_provider(model, llm_mode)

        if llm_mode == "ollama":
            return await self._call_ollama(
                prompt, system, model_name, max_tokens, temperature,
                user_id, intent, session_id,
            )

        try:
            if provider == "anthropic":
                return await self._call_anthropic(
                    prompt, system, model_name, max_tokens, temperature,
                    user_id, intent, session_id,
                )
            elif provider == "openai":
                return await self._call_openai(
                    prompt, system, model_name, max_tokens, temperature,
                    user_id, intent, session_id,
                )
            else:
                return await self._call_ollama(
                    prompt, system, model_name, max_tokens, temperature,
                    user_id, intent, session_id,
                )
        except Exception as e:
            if llm_mode == "hybrid":
                logger.warning(
                    "Cloud provider %s failed, falling back to Ollama: %s",
                    provider, e,
                )
                return await self._call_ollama(
                    prompt, system, _DEFAULT_MODELS["ollama"], max_tokens,
                    temperature, user_id, intent, session_id,
                )
            logger.error("AI generation failed for %s: %s", provider, e, exc_info=True)
            return ""

    async def generate_with_tools(
        self,
        prompt: str,
        tools: list[dict],
        *,
        system: str = "",
        model: str | None = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        user_id: UUID | None = None,
        intent: str | None = None,
        session_id: str | None = None,
    ) -> dict[str, Any]:
        """Generate a response with tool/function calling support.

        Args:
            tools: Tool definitions in Anthropic format:
                   [{"name": str, "description": str, "input_schema": dict}]

        Returns:
            {"content": str, "tool_calls": [{"name": str, "input": dict, "id": str}]}
        """
        provider, model_name = _resolve_provider(model, self._settings.llm_mode)
        start_time = time.time()

        try:
            if provider == "anthropic":
                client = self._get_anthropic()
                response = await client.messages.create(
                    model=model_name,
                    max_tokens=max_tokens,
                    system=system,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    tools=tools,
                )

                content = ""
                tool_calls = []
                for block in response.content:
                    if block.type == "text":
                        content += block.text
                    elif block.type == "tool_use":
                        tool_calls.append({
                            "name": block.name,
                            "input": block.input,
                            "id": block.id,
                        })

                latency_ms = int((time.time() - start_time) * 1000)
                in_tok = response.usage.input_tokens
                out_tok = response.usage.output_tokens

                self.last_token_usage = {
                    "input_tokens": in_tok,
                    "output_tokens": out_tok,
                    "total_tokens": in_tok + out_tok,
                    "provider": "anthropic",
                    "model": model_name,
                }

                await self._log_call(
                    provider="anthropic", model=model_name,
                    input_tokens=in_tok, output_tokens=out_tok,
                    latency_ms=latency_ms,
                    cost_usd=_estimate_cost(model_name, in_tok, out_tok),
                    status="success", error_message=None,
                    user_id=user_id, intent=intent, session_id=session_id,
                )

                return {"content": content, "tool_calls": tool_calls}

            elif provider == "openai":
                client = self._get_openai()
                openai_tools = [
                    {
                        "type": "function",
                        "function": {
                            "name": t["name"],
                            "description": t.get("description", ""),
                            "parameters": t.get("input_schema", {}),
                        },
                    }
                    for t in tools
                ]

                response = await client.chat.completions.create(
                    model=model_name,
                    max_tokens=max_tokens,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=temperature,
                    tools=openai_tools,
                )

                choice = response.choices[0]
                content = choice.message.content or ""
                tool_calls = []
                if choice.message.tool_calls:
                    import json as _json
                    for tc in choice.message.tool_calls:
                        tool_calls.append({
                            "name": tc.function.name,
                            "input": _json.loads(tc.function.arguments),
                            "id": tc.id,
                        })

                latency_ms = int((time.time() - start_time) * 1000)
                in_tok = response.usage.prompt_tokens
                out_tok = response.usage.completion_tokens

                self.last_token_usage = {
                    "input_tokens": in_tok,
                    "output_tokens": out_tok,
                    "total_tokens": in_tok + out_tok,
                    "provider": "openai",
                    "model": model_name,
                }

                await self._log_call(
                    provider="openai", model=model_name,
                    input_tokens=in_tok, output_tokens=out_tok,
                    latency_ms=latency_ms,
                    cost_usd=_estimate_cost(model_name, in_tok, out_tok),
                    status="success", error_message=None,
                    user_id=user_id, intent=intent, session_id=session_id,
                )

                return {"content": content, "tool_calls": tool_calls}

            else:
                result = await self.generate(prompt, system=system, model=model, user_id=user_id)
                return {"content": result, "tool_calls": []}

        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            await self._log_call(
                provider=provider, model=model_name,
                input_tokens=0, output_tokens=0,
                latency_ms=latency_ms, cost_usd=0.0,
                status="error", error_message=str(e),
                user_id=user_id, intent=intent, session_id=session_id,
            )
            logger.error("Tool-use generation failed: %s", e, exc_info=True)
            return {"content": "", "tool_calls": []}

    async def generate_stream(
        self,
        prompt: str,
        *,
        system: str = "",
        model: str | None = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        user_id: UUID | None = None,
        intent: str | None = None,
        session_id: str | None = None,
    ) -> AsyncGenerator[str, None]:
        """Stream a response, yielding text chunks as they arrive."""
        provider, model_name = _resolve_provider(model, self._settings.llm_mode)
        start_time = time.time()

        try:
            if provider == "anthropic":
                async for chunk in self._stream_anthropic(
                    prompt, system, model_name, max_tokens, temperature,
                    user_id, intent, session_id, start_time,
                ):
                    yield chunk
            elif provider == "openai":
                async for chunk in self._stream_openai(
                    prompt, system, model_name, max_tokens, temperature,
                    user_id, intent, session_id, start_time,
                ):
                    yield chunk
            else:
                async for chunk in self._stream_ollama(
                    prompt, system, model_name, max_tokens, temperature,
                    user_id, intent, session_id, start_time,
                ):
                    yield chunk

        except Exception as e:
            logger.error("Streaming failed for %s, falling back: %s", provider, e)
            result = await self.generate(
                prompt, system=system, model=model, user_id=user_id, intent=intent,
            )
            if result:
                yield result

    def is_configured(self, provider: str | None = None) -> bool:
        """Check if AI is configured (API key present) for a specific or any provider."""
        if provider == "anthropic":
            return bool(self._settings.anthropic_api_key)
        if provider == "openai":
            return bool(self._settings.openai_api_key)
        if provider == "ollama":
            return True

        llm_mode = self._settings.llm_mode.lower()
        if llm_mode in ("ollama", "hybrid"):
            return True
        return bool(self._settings.anthropic_api_key) or bool(self._settings.openai_api_key)

    async def get_status(self) -> dict[str, Any]:
        """Get detailed status about AI configuration."""
        providers = []
        if self._settings.anthropic_api_key:
            providers.append({"provider": "anthropic", "model": _DEFAULT_MODELS["anthropic"], "configured": True})
        if self._settings.openai_api_key:
            providers.append({"provider": "openai", "model": _DEFAULT_MODELS["openai"], "configured": True})
        providers.append({
            "provider": "ollama", "model": _DEFAULT_MODELS["ollama"],
            "configured": True, "base_url": self._settings.ollama_base_url,
        })

        return {"configured": self.is_configured(), "llm_mode": self._settings.llm_mode, "providers": providers}

    # ------------------------------------------------------------------
    # Provider Clients (lazy init)
    # ------------------------------------------------------------------

    def _get_anthropic(self):
        if self._anthropic_client is None:
            from anthropic import AsyncAnthropic
            self._anthropic_client = AsyncAnthropic(api_key=self._settings.anthropic_api_key)
        return self._anthropic_client

    def _get_openai(self):
        if self._openai_client is None:
            from openai import AsyncOpenAI
            self._openai_client = AsyncOpenAI(api_key=self._settings.openai_api_key)
        return self._openai_client

    # ------------------------------------------------------------------
    # Provider Implementations
    # ------------------------------------------------------------------

    async def _call_anthropic(
        self, prompt: str, system: str, model: str, max_tokens: int,
        temperature: float, user_id: UUID | None, intent: str | None,
        session_id: str | None,
    ) -> str:
        client = self._get_anthropic()
        start_time = time.time()

        response = await client.messages.create(
            model=model, max_tokens=max_tokens, system=system,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
        )

        text = response.content[0].text if response.content else ""
        latency_ms = int((time.time() - start_time) * 1000)
        in_tok = response.usage.input_tokens
        out_tok = response.usage.output_tokens

        self.last_token_usage = {
            "input_tokens": in_tok, "output_tokens": out_tok,
            "total_tokens": in_tok + out_tok, "provider": "anthropic", "model": model,
        }

        await self._log_call(
            provider="anthropic", model=model, input_tokens=in_tok, output_tokens=out_tok,
            latency_ms=latency_ms, cost_usd=_estimate_cost(model, in_tok, out_tok),
            status="success", error_message=None,
            user_id=user_id, intent=intent, session_id=session_id,
        )
        return text

    async def _call_openai(
        self, prompt: str, system: str, model: str, max_tokens: int,
        temperature: float, user_id: UUID | None, intent: str | None,
        session_id: str | None,
    ) -> str:
        client = self._get_openai()
        start_time = time.time()

        response = await client.chat.completions.create(
            model=model, max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
        )

        text = response.choices[0].message.content or ""
        latency_ms = int((time.time() - start_time) * 1000)
        in_tok = response.usage.prompt_tokens
        out_tok = response.usage.completion_tokens

        self.last_token_usage = {
            "input_tokens": in_tok, "output_tokens": out_tok,
            "total_tokens": in_tok + out_tok, "provider": "openai", "model": model,
        }

        await self._log_call(
            provider="openai", model=model, input_tokens=in_tok, output_tokens=out_tok,
            latency_ms=latency_ms, cost_usd=_estimate_cost(model, in_tok, out_tok),
            status="success", error_message=None,
            user_id=user_id, intent=intent, session_id=session_id,
        )
        return text

    async def _call_ollama(
        self, prompt: str, system: str, model: str, max_tokens: int,
        temperature: float, user_id: UUID | None, intent: str | None,
        session_id: str | None,
    ) -> str:
        url = f"{self._settings.ollama_base_url}/api/chat"
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "stream": False,
            "options": {"num_predict": max_tokens, "temperature": temperature},
        }

        start_time = time.time()
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
                data = resp.json()

            text = data.get("message", {}).get("content", "")
            latency_ms = int((time.time() - start_time) * 1000)
            in_tok = data.get("prompt_eval_count", 0)
            out_tok = data.get("eval_count", 0)

            self.last_token_usage = {
                "input_tokens": in_tok, "output_tokens": out_tok,
                "total_tokens": in_tok + out_tok, "provider": "ollama", "model": model,
            }

            await self._log_call(
                provider="ollama", model=f"ollama/{model}",
                input_tokens=in_tok, output_tokens=out_tok,
                latency_ms=latency_ms, cost_usd=0.0,
                status="success", error_message=None,
                user_id=user_id, intent=intent, session_id=session_id,
            )
            return text

        except httpx.ConnectError:
            logger.error("Cannot connect to Ollama at %s. Is Ollama running?", self._settings.ollama_base_url)
            return ""
        except Exception as e:
            logger.error("Ollama generation failed: %s", e, exc_info=True)
            return ""

    # ------------------------------------------------------------------
    # Streaming Implementations
    # ------------------------------------------------------------------

    async def _stream_anthropic(
        self, prompt: str, system: str, model: str, max_tokens: int,
        temperature: float, user_id: UUID | None, intent: str | None,
        session_id: str | None, start_time: float,
    ) -> AsyncGenerator[str, None]:
        client = self._get_anthropic()
        full_response = ""
        input_tokens = output_tokens = 0

        async with client.messages.stream(
            model=model, max_tokens=max_tokens, system=system,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
        ) as stream:
            async for text in stream.text_stream:
                full_response += text
                yield text
            final_msg = await stream.get_final_message()
            if final_msg and final_msg.usage:
                input_tokens = final_msg.usage.input_tokens
                output_tokens = final_msg.usage.output_tokens

        latency_ms = int((time.time() - start_time) * 1000)
        self.last_token_usage = {
            "input_tokens": input_tokens, "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens, "provider": "anthropic", "model": model,
        }
        await self._log_call(
            provider="anthropic", model=model, input_tokens=input_tokens, output_tokens=output_tokens,
            latency_ms=latency_ms, cost_usd=_estimate_cost(model, input_tokens, output_tokens),
            status="success", error_message=None,
            user_id=user_id, intent=intent, session_id=session_id,
        )

    async def _stream_openai(
        self, prompt: str, system: str, model: str, max_tokens: int,
        temperature: float, user_id: UUID | None, intent: str | None,
        session_id: str | None, start_time: float,
    ) -> AsyncGenerator[str, None]:
        client = self._get_openai()
        full_response = ""
        input_tokens = output_tokens = 0

        stream = await client.chat.completions.create(
            model=model, max_tokens=max_tokens,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": prompt}],
            temperature=temperature, stream=True,
            stream_options={"include_usage": True},
        )

        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                text = chunk.choices[0].delta.content
                full_response += text
                yield text
            if hasattr(chunk, "usage") and chunk.usage:
                input_tokens = chunk.usage.prompt_tokens
                output_tokens = chunk.usage.completion_tokens

        latency_ms = int((time.time() - start_time) * 1000)
        self.last_token_usage = {
            "input_tokens": input_tokens, "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens, "provider": "openai", "model": model,
        }
        await self._log_call(
            provider="openai", model=model, input_tokens=input_tokens, output_tokens=output_tokens,
            latency_ms=latency_ms, cost_usd=_estimate_cost(model, input_tokens, output_tokens),
            status="success", error_message=None,
            user_id=user_id, intent=intent, session_id=session_id,
        )

    async def _stream_ollama(
        self, prompt: str, system: str, model: str, max_tokens: int,
        temperature: float, user_id: UUID | None, intent: str | None,
        session_id: str | None, start_time: float,
    ) -> AsyncGenerator[str, None]:
        import json
        url = f"{self._settings.ollama_base_url}/api/chat"
        payload = {
            "model": model,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}],
            "stream": True,
            "options": {"num_predict": max_tokens, "temperature": temperature},
        }

        input_tokens = output_tokens = 0
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream("POST", url, json=payload) as resp:
                    resp.raise_for_status()
                    async for line in resp.aiter_lines():
                        if not line.strip():
                            continue
                        data = json.loads(line)
                        if data.get("done"):
                            input_tokens = data.get("prompt_eval_count", 0)
                            output_tokens = data.get("eval_count", 0)
                            break
                        content = data.get("message", {}).get("content", "")
                        if content:
                            yield content

            latency_ms = int((time.time() - start_time) * 1000)
            self.last_token_usage = {
                "input_tokens": input_tokens, "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens, "provider": "ollama", "model": model,
            }
            await self._log_call(
                provider="ollama", model=f"ollama/{model}",
                input_tokens=input_tokens, output_tokens=output_tokens,
                latency_ms=latency_ms, cost_usd=0.0,
                status="success", error_message=None,
                user_id=user_id, intent=intent, session_id=session_id,
            )
        except Exception as e:
            logger.error("Ollama streaming failed: %s", e, exc_info=True)

    # ------------------------------------------------------------------
    # Audit Logging
    # ------------------------------------------------------------------

    async def _log_call(
        self, *, provider: str, model: str, input_tokens: int, output_tokens: int,
        latency_ms: int, cost_usd: float, status: str, error_message: str | None,
        user_id: UUID | None, intent: str | None, session_id: str | None,
    ) -> None:
        """Create AIAuditLog record in its own session (separate transaction)."""
        try:
            async with self._session_factory() as session:
                audit = AIAuditLog(
                    user_id=user_id, session_id=session_id,
                    provider=provider, model=model, endpoint="messages",
                    intent=intent, input_tokens=input_tokens, output_tokens=output_tokens,
                    latency_ms=latency_ms, cost_usd=cost_usd,
                    status=status, error_message=error_message,
                )
                session.add(audit)
                await session.commit()
        except Exception as e:
            logger.error("Failed to create AI audit log: %s", e, exc_info=True)
