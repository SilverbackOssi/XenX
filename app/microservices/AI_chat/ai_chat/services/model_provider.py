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

from typing import Protocol, List, Optional, Dict, Any, Union
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


@dataclass
class GenerationResult:
    """Unified response object returned by any :class:`ModelProvider`.

    Attributes:
        text: Primary textual model output (may embed structured JSON upstream).
        trace_id: Unique identifier for this generation – propagate to logs & audits.
        model_name: Name / label of the underlying provider implementation.
        latency_ms: Milliseconds elapsed for the *provider* call (excludes
            orchestration overhead outside this module).
        raw: Provider-specific diagnostic payload (debug / introspection use only).
    """

    trace_id: str
    model_name: str
    latency_ms: int
    text: str
    raw: Dict[str, Any]
    chunks: Optional[List[str]] = None  # For future streaming support, only populated in streaming mode


class ModelProvider(Protocol):  # Section 3.1
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

    async def generate(
        self,
        messages: List[ModelMessage],
        mode: str = "default",
        json_schema: Optional[Dict[str, Any]] = None,
    ) -> GenerationResult:  # pragma: no cover - interface specification
        ...


class GeminiFreeStub:
    """Stub adapter simulating a Gemini provider (Section 3.2).

    Behavior:
        * Echoes the last user message with a stub prefix and optional schema key list.
        * Generates a trace ID and simple latency metric.
        * Supplies a minimal ``raw`` diagnostic dict.

    This implementation **never** makes network calls – suitable for offline
    development and unit testing.
    """

    name = "gemini_stub"

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
        trace_id = str(uuid.uuid4())  # Section 3.4
        latency_ms = int((time.time() - start) * 1000)
        return GenerationResult(
            text=base_output,
            trace_id=trace_id,
            model_name=self.name,
            latency_ms=latency_ms,
            raw={"echoed": last_user, "mode": mode, "schema": bool(json_schema)},
        )


class FallbackEchoProvider:
    """Provider used when configuration selects an unknown backend.

    Produces a compact echo of the last few turns for visibility.
    """

    name = "echo_fallback"

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
        latency_ms = int((time.time() - start) * 1000)
        return GenerationResult(
            text=f"Fallback({mode}) => {combined}",
            trace_id=trace_id,
            model_name=self.name,
            latency_ms=latency_ms,
            raw={"count": len(messages)},
        )


def get_model_provider() -> ModelProvider:  # Section 3.3
    """Return a concrete provider instance based on configuration.

    Resolution Logic:
        * If ``CONFIG.model_provider`` starts with ``"gemini"`` → :class:`GeminiFreeStub`.
        * Otherwise → :class:`FallbackEchoProvider`.

    Returns:
        ModelProvider: Instantiated provider (stateless objects – lightweight to create).
    """
    provider = CONFIG.model_provider.lower()
    if provider.startswith("gemini"):
        return GeminiFreeStub()
    return FallbackEchoProvider()


__all__ = [
    "MessageRole",
    "ModelMessage",
    "GenerationResult",
    "ModelProvider",
    "GeminiFreeStub",
    "FallbackEchoProvider",
    "get_model_provider",
]
