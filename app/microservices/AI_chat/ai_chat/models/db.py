"""SQLAlchemy models for AI Chat persistence.

These models are isolated from core user/enterprise tables but reference user_id
and enterprise_id (integers) for linkage. Foreign key constraints are omitted
initially to reduce coupling; can be added later if desired.
"""
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    Text,
    JSON,
    Index,
    UniqueConstraint,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from app.gateway.database import Base


class AIChatConversation(Base):
    """Top-level conversation thread for the AI chat system.

    A conversation groups an ordered sequence of messages (turns) between the
    user and assistant. It may optionally be linked to a user or enterprise
    but deliberately omits FK constraints to those external modules to avoid
    tight coupling. Deleting a conversation cascades to its messages and
    summaries.
    """

    __tablename__ = "ai_chat_conversations"

    id = Column(Integer, primary_key=True, index=True, comment="Primary key")
    user_id = Column(Integer, index=True, nullable=True, comment="Optional user identifier (no FK – external module)")
    enterprise_id = Column(Integer, index=True, nullable=True, comment="Optional enterprise identifier (no FK – external module)")
    active = Column(Boolean, default=True, nullable=False, comment="Soft flag indicating whether conversation is active/visible")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, comment="Creation timestamp (UTC)")
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Last update timestamp (UTC)",
    )

    # Relationships
    messages = relationship(
        "AIChatMessage",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="AIChatMessage.turn_index",
        passive_deletes=True,
    )
    summaries = relationship(
        "AIChatSummary",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="AIChatSummary.up_to_turn",
        passive_deletes=True,
    )

    __table_args__ = (
        Index("ix_ai_chat_conv_user_active", "user_id", "active"),
        {"comment": "AI chat conversation threads"},
    )


class AIChatMessage(Base):
    """Individual message (turn) within a conversation.

    Holds either natural language content or a structured tool/action payload.
    Turn order is maintained by incrementing `turn_index` per conversation.
    """

    __tablename__ = "ai_chat_messages"

    id = Column(Integer, primary_key=True, comment="Primary key")
    conversation_id = Column(
        Integer,
        ForeignKey("ai_chat_conversations.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="Parent conversation (FK, cascade delete)",
    )
    turn_index = Column(Integer, nullable=False, comment="0-based sequential turn number in conversation")
    role = Column(String(16), nullable=False, comment="Message role: user|assistant|system|tool")
    content_text = Column(Text, nullable=True, comment="Plain text content (if applicable)")
    action_json = Column(JSON, nullable=True, comment="Structured tool/action invocation payload")
    confirmation_status = Column(
        String(16),
        nullable=True,
        comment="Workflow confirmation state: none|pending|confirmed|rejected",
    )
    safety_flags = Column(JSON, nullable=True, comment="Optional moderation/safety annotations")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="Creation timestamp (UTC)")

    # Relationships
    conversation = relationship("AIChatConversation", back_populates="messages")

    __table_args__ = (
        Index("ix_ai_chat_msgs_conv_turn", "conversation_id", "turn_index"),
        {"comment": "Messages (turns) for AI chat conversations"},
    )


class AIChatSummary(Base):
    """Rolling / hierarchical summaries of conversation state.

    Used to compress earlier turns for context window management. Multiple
    summaries can exist at different `up_to_turn` checkpoints.
    """

    __tablename__ = "ai_chat_summaries"

    id = Column(Integer, primary_key=True, comment="Primary key")
    conversation_id = Column(
        Integer,
        ForeignKey("ai_chat_conversations.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="Parent conversation (FK, cascade delete)",
    )
    up_to_turn = Column(Integer, nullable=False, comment="Inclusive highest turn index covered by this summary")
    summary_text = Column(Text, nullable=False, comment="Compressed representation of conversation so far")
    compression_ratio = Column(
        Integer,
        nullable=True,
        comment="Approximate (original_tokens / summary_tokens * 100) integer percentage",
    )
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, comment="Creation timestamp (UTC)")

    # Relationships
    conversation = relationship("AIChatConversation", back_populates="summaries")

    __table_args__ = (
        UniqueConstraint("conversation_id", "up_to_turn", name="uq_summary_conv_turn"),
        {"comment": "Rolling summaries of conversation state"},
    )


class AIChatAudit(Base):
    """Audit log for security / compliance events in AI chat operations."""

    __tablename__ = "ai_chat_audits"

    id = Column(Integer, primary_key=True, comment="Primary key")
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, comment="Event timestamp (UTC)")
    user_id = Column(Integer, index=True, nullable=True, comment="Optional user id (no FK – external module)")
    enterprise_id = Column(Integer, index=True, nullable=True, comment="Optional enterprise id (no FK – external module)")
    action_name = Column(String(64), index=True, nullable=False, comment="Action identifier / verb")
    input_sanitized_json = Column(JSON, nullable=True, comment="Redacted/filtered input payload for audit")
    result_status = Column(
        String(24),
        nullable=False,
        comment="Outcome: success|denied|error|aborted",
    )
    latency_ms = Column(Integer, nullable=True, comment="Measured latency in milliseconds")
    trace_id = Column(String(64), index=True, nullable=True, comment="Optional trace/span identifier for correlation")
    confirmation_token = Column(String(64), nullable=True, comment="Token tying audit to a user confirmation flow")
    permission_snapshot = Column(JSON, nullable=True, comment="Serialized permissions state at time of action")


class AIChatRateLimit(Base):
    """Sliding window counters for basic rate limiting by client fingerprint."""

    __tablename__ = "ai_chat_rate_limits"

    id = Column(Integer, primary_key=True, comment="Primary key")
    ip_hash = Column(String(128), index=True, nullable=False, comment="Hashed client IP / fingerprint")
    window_start = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, comment="Window start timestamp (UTC)")
    request_count = Column(Integer, default=0, nullable=False, comment="Number of chat requests in window")
    action_count = Column(Integer, default=0, nullable=False, comment="Number of tool/action executions in window")

    __table_args__ = (
        Index("ix_ai_chat_rate_ip_window", "ip_hash", "window_start"),
        {"comment": "Rate limit tracking for AI chat usage"},
    )


__all__ = [
    "AIChatConversation",
    "AIChatMessage",
    "AIChatSummary",
    "AIChatAudit",
    "AIChatRateLimit",
]
