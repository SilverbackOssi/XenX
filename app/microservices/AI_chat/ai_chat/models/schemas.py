"""Pydantic schemas for basic chat flow.

These are intentionally minimal for the first interactive endpoint. They
will evolve as orchestration complexity grows (action proposals, etc.).
"""
from __future__ import annotations
from ..services.model_provider import MessageRole
from pydantic import BaseModel, Field, validator
from typing import Optional, List

from app.microservices.AI_chat.ai_chat.services.model_provider import ModelMessage


class ChatMessageIn(BaseModel):
    conversation_id: Optional[int] = Field(None, description="Existing conversation id (omit to start new)")
    message: str = Field(..., min_length=1, description="User message text")
    enterprise_id: Optional[int] = Field(None, description="Optional enterprise context id")

    @validator("message")
    def not_blank(cls, v: str) -> str:  # noqa: D401
        v2 = v.strip()
        if not v2:
            raise ValueError("message cannot be blank")
        return v2


class ChatMessageOut(BaseModel):
    conversation_id: int
    user_message: str
    assistant_message: str
    trace_id: str
    model_name: str


class ConversationHistoryItem(BaseModel):
    """Represents a single message turn in a conversation history.
    This is the Pydantic schema representation of a ModelMessage.
    """
    role: MessageRole
    content: str


class ConversationHistoryOut(BaseModel):
    conversation_id: int
    messages: List[ConversationHistoryItem]

__all__ = [
    "ChatMessageIn",
    "ChatMessageOut",
    "ConversationHistoryOut",
    "ConversationHistoryItem",
]
