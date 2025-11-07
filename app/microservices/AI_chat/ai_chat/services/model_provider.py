"""Model provider abstraction layer for AI Chat (Section 3.1–3.4).

This module defines a narrow interface the rest of the chat system relies on
for Large Language Model (LLM) style generations. The intent is to:

1. Decouple orchestration / graph logic from any specific provider SDK.
2. Provide a trivially swappable shim for local development (no network calls).
3. Centralize trace ID generation + latency measurement.
4. Prepare for future structured / JSON tool planning generations.

Entities:
        * :class:`ModelMessage` – Lightweight representation of a chat turn.
        * :class:`GenerationResult` – Normalized output contract for all providers.
        * :class:`ModelProvider` – Protocol (interface) every provider must satisfy.
        * :class:`GeminiFreeStub` – Development stub mimicking a Gemini provider.
        * :class:`FallbackEchoProvider` – Safety net provider used when config
            indicates an unknown provider string.
        * :func:`get_model_provider` – Factory returning a provider instance based
            on runtime configuration (``CONFIG.model_provider``).

Design Notes:
        * Asynchronous API: anticipates real HTTP calls + streaming in the future.
        * ``json_schema`` parameter: reserved for structured output requests.
            The stub simply acknowledges keys; a real implementation would supply
            a constrained generation / tool spec prompt.
        * Trace IDs: Generated *inside* the provider boundary to ensure every
            upstream call (including retries) has a unique identifier while still
            allowing propagation into auditing & metrics.

Example:
        >>> provider = get_model_provider()
        >>> result = await provider.generate([ModelMessage(role="user", content="Hello")])
        >>> result.text  # doctest: +ELLIPSIS
        'Stub(default) response to: Hello'

Future Enhancements (not implemented here):
        * Streaming token callback interface.
        * Retry / backoff wrappers with provider error classification.
        * Token usage accounting (prompt vs completion) on real providers.
        * JSON schema enforcement / validation retries.
"""
from __future__ import annotations

from typing import Protocol, List, Optional, Dict, Any, TypedDict, Union
from enum import Enum
from dataclasses import dataclass
import uuid
import time

from ..config import CONFIG


class MessageRole(str, Enum):
    """Canonical roles for messages in a conversation."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"

    @classmethod
    def coerce(cls, value: Union[str, MessageRole]) -> MessageRole:
        if isinstance(value, cls):
            return value
        try:
            return cls(value.lower())
        except Exception as e:
            raise ValueError(f"Invalid role '{value}'. Allowed: {[r.value for r in cls]}") from e


@dataclass
class ModelMessage:
    """Single chat message passed to the model provider.
    A minimal, provider-agnostic representation of a conversation turn.

    Attributes:
        role: Canonical role label (see :class:`MessageRole`).
        content: Raw textual content associated with the role.
    """

    role: MessageRole
    content: str

    def __post_init__(self):
        self.role = MessageRole.coerce(self.role)

class RawGenerationMeta(TypedDict, total=False):
    """Provider-specific diagnostic / introspection payload.

    Standard optional keys (conventions, not guarantees):
        echoed: Last user message echoed (stub only)
        mode: Semantic generation mode label
        schema: Whether json_schema hint was supplied
        count: Number of messages considered (fallback provider)
        provider: Provider name (redundant convenience)
    """

    echoed: str
    mode: str
    schema: bool
    count: int
    provider: str

@dataclass
class GenerationResult:
    """Unified response object returned by any :class:`ModelProvider`.

    Attributes:
        text: Primary textual model output (may embed structured JSON upstream).
        trace_id: Unique identifier for this generation – propagate to logs & audits.
        model_name: Name / label of the underlying provider implementation.
        latency_ms: Milliseconds elapsed for the *provider* call (excludes
            orchestration overhead outside this module).
        raw: Lightly structured provider-specific diagnostic metadata (debug / introspection use only).
        chunks: Optional list of incremental pieces (future streaming support); ``text`` should equal ``\"\".join(chunks)`` when populated.
    """

    trace_id: str
    model_name: str
    latency_ms: int
    text: str
    raw: RawGenerationMeta
    chunks: Optional[List[str]] = None  # For future streaming support, only populated in streaming mode


class ModelProvider(Protocol):
    """Protocol describing required provider behavior.

    Implementations MUST:
        * Expose a ``name`` attribute identifying the backend.
        * Implement ``generate`` as an async function.
        * Return a fully-populated :class:`GenerationResult` (never ``None``).

    Parameters (generate):
        messages: Ordered list of conversation turns (latest last).
        mode: Optional semantic hint (e.g. ``"planning"``, ``"summarize"``).
        json_schema: If supplied, provider should attempt to steer output
            towards a JSON object matching this schema (best-effort in stubs).

    Returns:
        GenerationResult: Normalized provider output.
    """

    name: str
    capabilities: Dict[str, Any]

    async def generate(
        self,
        messages: List[ModelMessage],
        mode: str = "default",
        json_schema: Optional[Dict[str, Any]] = None,
    ) -> GenerationResult:  # pragma: no cover - interface specification
        ...

def compute_latency_ms(start: float) -> int:
    """Return elapsed milliseconds given a start time."""
    return int((time.time() - start) * 1000)

class GeminiFreeStub:
    """Stub adapter simulating a Gemini provider.

    Behavior:
        * Echoes the last user message with a stub prefix and optional schema key list.
        * Generates a trace ID and simple latency metric.
        * Supplies a minimal ``raw`` diagnostic dict.

    This implementation **never** makes network calls – suitable for offline
    development and unit testing.
    """

    name = "gemini_stub"
    capabilities: Dict[str, Any] = {
        "streaming": False,
        "structured_json": "best_effort",
    }

    async def generate(
        self,
        messages: List[ModelMessage],
        mode: str = "default",
        json_schema: Optional[Dict[str, Any]] = None,
    ) -> GenerationResult:
        """Produce a deterministic stub response.

        Args:
            messages: Conversation messages (latest last).
            mode: Optional semantic mode label.
            json_schema: Optional JSON schema; only its property keys are echoed.

        Returns:
            GenerationResult: Stubbed generation payload.
        """
        start = time.time()
        user_msgs = [m for m in messages if m.role is MessageRole.USER]
        last_user = user_msgs[-1].content if user_msgs else "(no user input)"
        base_output = f"Stub({mode}) response to: {last_user[:200]}"
        if json_schema:
            base_output += " | schema_stub: {keys}".format(keys=list(json_schema.get("properties", {}).keys()))
        trace_id = str(uuid.uuid4())
        latency_ms = compute_latency_ms(start)
        return GenerationResult(
            text=base_output,
            trace_id=trace_id,
            model_name=self.name,
            latency_ms=latency_ms,
            raw={"echoed": last_user, "mode": mode, "schema": bool(json_schema), "provider": self.name},
        )


class FallbackEchoProvider:
    """Provider used when configuration selects an unknown backend.

    Produces a compact echo of the last few turns for visibility.
    """

    name = "echo_fallback"
    capabilities: Dict[str, Any] = {
        "streaming": False,
        "structured_json": "unsupported",
    }

    async def generate(
        self,
        messages: List[ModelMessage],
        mode: str = "default",
        json_schema: Optional[Dict[str, Any]] = None,
    ) -> GenerationResult:
        """Echo last conversation window content.

        The ``json_schema`` parameter is ignored intentionally (fallback behavior).
        """
        start = time.time()
        combined = " | ".join(f"{m.role}: {m.content[:80]}" for m in messages[-4:])
        trace_id = str(uuid.uuid4())
        latency_ms = compute_latency_ms(start)
        return GenerationResult(
            text=f"Fallback({mode}) => {combined}",
            trace_id=trace_id,
            model_name=self.name,
            latency_ms=latency_ms,
            raw={"count": len(messages), "mode": mode, "schema": False, "provider": self.name},
        )

_CACHED_PROVIDER: Optional[ModelProvider] = None
_CACHED_PROVIDER_KEY: Optional[str] = None

def get_model_provider() -> ModelProvider:
    """Return a (memoized) provider instance based on configuration.

    Re-instantiates only if the configured provider string changes.
    """
    global _CACHED_PROVIDER, _CACHED_PROVIDER_KEY
    key = CONFIG.model_provider.lower()
    if _CACHED_PROVIDER and _CACHED_PROVIDER_KEY == key:
        return _CACHED_PROVIDER
    if key.startswith("gemini"):
        _CACHED_PROVIDER = GeminiFreeStub()
    else:
        _CACHED_PROVIDER = FallbackEchoProvider()
    _CACHED_PROVIDER_KEY = key
    return _CACHED_PROVIDER

def provider_capabilities(provider: Optional[ModelProvider] = None) -> Dict[str, Any]:
    """Return capability flags for a provider (streaming, structured JSON, etc.)."""
    if provider is None:
        provider = get_model_provider()
    return getattr(provider, "capabilities", {"streaming": False})


__all__ = [
    "MessageRole",
    "ModelMessage",
    "RawGenerationMeta",
    "GenerationResult",
    "ModelProvider",
    "GeminiFreeStub",
    "FallbackEchoProvider",
    "get_model_provider",
    "provider_capabilities",
    "compute_latency_ms",
]
