"""Chat state placeholder model."""
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

class ChatState(BaseModel):
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
