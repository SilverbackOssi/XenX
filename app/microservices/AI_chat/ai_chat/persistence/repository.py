"""Repository functions for AI Chat persistence.

Simple abstractions over CRUD operations to keep graph/tool code clean.
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from ..models.db import (
    AIChatConversation,
    AIChatMessage,
    AIChatSummary,
    AIChatAudit,
)


async def create_conversation(db: AsyncSession, user_id: Optional[int], enterprise_id: Optional[int]) -> AIChatConversation:
    conv = AIChatConversation(user_id=user_id, enterprise_id=enterprise_id)
    db.add(conv)
    await db.flush()
    return conv


async def append_message(
    db: AsyncSession,
    conversation_id: int,
    role: str,
    content_text: Optional[str],
    action_json: Optional[dict] = None,
    confirmation_status: Optional[str] = None,
    safety_flags: Optional[List[str]] = None,
) -> AIChatMessage:
    # Determine next turn index
    q = select(func.max(AIChatMessage.turn_index)).where(AIChatMessage.conversation_id == conversation_id)
    res = await db.execute(q)
    current_max = res.scalar() or 0
    msg = AIChatMessage(
        conversation_id=conversation_id,
        turn_index=current_max + 1,
        role=role,
        content_text=content_text,
        action_json=action_json,
        confirmation_status=confirmation_status,
        safety_flags=safety_flags or [],
    )
    db.add(msg)
    await db.flush()
    return msg


async def list_recent_messages(db: AsyncSession, conversation_id: int, limit: int = 50) -> List[AIChatMessage]:
    q = (
        select(AIChatMessage)
        .where(AIChatMessage.conversation_id == conversation_id)
        .order_by(AIChatMessage.turn_index.desc())
        .limit(limit)
    )
    res = await db.execute(q)
    rows = res.scalars().all()
    return list(reversed(rows))


async def store_summary(
    db: AsyncSession,
    conversation_id: int,
    up_to_turn: int,
    summary_text: str,
    compression_ratio: Optional[float] = None,
) -> AIChatSummary:
    summary = AIChatSummary(
        conversation_id=conversation_id,
        up_to_turn=up_to_turn,
        summary_text=summary_text,
        compression_ratio=compression_ratio,
    )
    db.add(summary)
    await db.flush()
    return summary


async def write_audit(
    db: AsyncSession,
    user_id: Optional[int],
    enterprise_id: Optional[int],
    action_name: str,
    input_sanitized_json: Optional[dict],
    result_status: str,
    latency_ms: Optional[int],
    trace_id: Optional[str],
    confirmation_token: Optional[str],
    permission_snapshot: Optional[dict],
) -> AIChatAudit:
    record = AIChatAudit(
        user_id=user_id,
        enterprise_id=enterprise_id,
        action_name=action_name,
        input_sanitized_json=input_sanitized_json,
        result_status=result_status,
        latency_ms=latency_ms,
        trace_id=trace_id,
        confirmation_token=confirmation_token,
        permission_snapshot=permission_snapshot,
    )
    db.add(record)
    await db.flush()
    return record


__all__ = [
    "create_conversation",
    "append_message",
    "list_recent_messages",
    "store_summary",
    "write_audit",
]
