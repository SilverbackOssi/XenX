"""Service layer composing persistence + model provider for simple chat flow.

This is a minimal synchronous request/response interaction used before
LangGraph orchestration is implemented. It will likely be refactored into
node-based execution later.
"""
from __future__ import annotations

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from ..services.model_provider import get_model_provider, ModelMessage
from ..persistence import repository


async def process_message(
    db: AsyncSession,
    user_id: Optional[int],
    enterprise_id: Optional[int],
    conversation_id: Optional[int],
    message: str,
) -> dict:
    """Handle a single user message and return assistant reply payload.

    Steps:
        1. Create conversation if needed.
        2. Persist user message.
        3. Collect recent messages (for minimal context) and call model provider.
        4. Persist assistant message.
        5. Return structured response.
    """
    # 1. Conversation ensure
    if conversation_id is None:
        conv = await repository.create_conversation(db, user_id=user_id, enterprise_id=enterprise_id)
        conversation_id = conv.id
    # 2. Persist user message
    user_msg = await repository.append_message(
        db,
        conversation_id=conversation_id,
        role="user",
        content_text=message,
    )
    # 3. Collect recent messages (simple mapping to provider format)
    recent: List = await repository.list_recent_messages(db, conversation_id, limit=12)
    provider_messages = [ModelMessage(role=m.role, content=m.content_text or "") for m in recent]
    provider = get_model_provider()
    gen = await provider.generate(provider_messages)
    # 4. Persist assistant message
    assistant_msg = await repository.append_message(
        db,
        conversation_id=conversation_id,
        role="assistant",
        content_text=gen.text,
    )
    # 5. Return response
    return {
        "conversation_id": conversation_id,
        "user_message": user_msg.content_text,
        "assistant_message": assistant_msg.content_text,
        "trace_id": gen.trace_id,
        "model_name": gen.model_name,
    }

__all__ = ["process_message"]
