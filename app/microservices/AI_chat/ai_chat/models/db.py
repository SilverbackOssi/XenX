"""SQLAlchemy models for AI Chat persistence.

These models are isolated from core user/enterprise tables but reference user_id
and enterprise_id (integers) for linkage. Foreign key constraints are omitted
initially to reduce coupling; can be added later if desired.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, Index
from app.gateway.database import Base


class AIChatConversation(Base):
    __tablename__ = "ai_chat_conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=True)
    enterprise_id = Column(Integer, index=True, nullable=True)
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_ai_chat_conv_user_active", "user_id", "active"),
    )


class AIChatMessage(Base):
    __tablename__ = "ai_chat_messages"

    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, index=True, nullable=False)
    turn_index = Column(Integer, nullable=False)
    role = Column(String(16), nullable=False)  # user|assistant|system|tool
    content_text = Column(Text, nullable=True)
    action_json = Column(JSON, nullable=True)
    confirmation_status = Column(String(16), nullable=True)  # none|pending|confirmed|rejected
    safety_flags = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_ai_chat_msgs_conv_turn", "conversation_id", "turn_index"),
    )


class AIChatSummary(Base):
    __tablename__ = "ai_chat_summaries"

    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, index=True, nullable=False)
    up_to_turn = Column(Integer, nullable=False)
    summary_text = Column(Text, nullable=False)
    compression_ratio = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class AIChatAudit(Base):
    __tablename__ = "ai_chat_audits"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    user_id = Column(Integer, index=True, nullable=True)
    enterprise_id = Column(Integer, index=True, nullable=True)
    action_name = Column(String(64), index=True, nullable=False)
    input_sanitized_json = Column(JSON, nullable=True)
    result_status = Column(String(24), nullable=False)  # success|denied|error|aborted
    latency_ms = Column(Integer, nullable=True)
    trace_id = Column(String(64), index=True, nullable=True)
    confirmation_token = Column(String(64), nullable=True)
    permission_snapshot = Column(JSON, nullable=True)


class AIChatRateLimit(Base):
    __tablename__ = "ai_chat_rate_limits"

    id = Column(Integer, primary_key=True)
    ip_hash = Column(String(128), index=True, nullable=False)
    window_start = Column(DateTime, default=datetime.utcnow, nullable=False)
    request_count = Column(Integer, default=0, nullable=False)
    action_count = Column(Integer, default=0, nullable=False)

    __table_args__ = (
        Index("ix_ai_chat_rate_ip_window", "ip_hash", "window_start"),
    )


__all__ = [
    "AIChatConversation",
    "AIChatMessage",
    "AIChatSummary",
    "AIChatAudit",
    "AIChatRateLimit",
]
