"""Unified ChatState model (consolidated).

This replaces earlier duplicate definitions (dataclass + Pydantic). For the
basic chat flow we only leverage a subset of fields; the remaining attributes
anticipate later graph orchestration work (intent classification, parameter
collection, tool execution, etc.).
"""
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class ChatState(BaseModel):  # Future: may become a typed state machine model
    user_id: Optional[int] = None
    enterprise_id: Optional[int] = None
    user_message: Optional[str] = None
    intent: Optional[str] = None
    missing_params: Dict[str, Any] = Field(default_factory=dict)
    collected_params: Dict[str, Any] = Field(default_factory=dict)
    proposed_action: Optional[Dict[str, Any]] = None
    confirmation_status: Optional[str] = None
    tool_result: Optional[Dict[str, Any]] = None
    response_draft: Optional[str] = None
    final_response: Optional[str] = None

__all__ = ["ChatState"]
