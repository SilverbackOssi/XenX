"""Configuration for AI Chat module (placeholder)."""
from pydantic import BaseModel
import os

class AIChatConfig(BaseModel):
    enable_ai_chat: bool = False
    model_provider: str = "gemini"
    model_name: str = "gemini-free"
    rate_limit_requests_per_window: int = 60
    rate_limit_window_seconds: int = 300
    rate_limit_actions_per_hour: int = 10
    action_proposals_per_hour: int = 20
    summary_trigger_turns: int = 15
    summary_keep_recent_turns: int = 12


def load_ai_chat_config() -> AIChatConfig:
    return AIChatConfig(
        enable_ai_chat=os.getenv("ENABLE_AI_CHAT", "false").lower() == "true",
        model_provider=os.getenv("MODEL_PROVIDER", "gemini"),
        model_name=os.getenv("MODEL_NAME", "gemini-free"),
        rate_limit_requests_per_window=int(os.getenv("RATE_LIMIT_REQUESTS_PER_WINDOW", 60)),
        rate_limit_window_seconds=int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", 300)),
        rate_limit_actions_per_hour=int(os.getenv("RATE_LIMIT_ACTIONS_PER_HOUR", 10)),
        action_proposals_per_hour=int(os.getenv("ACTION_PROPOSALS_PER_HOUR", 20)),
        summary_trigger_turns=int(os.getenv("SUMMARY_TRIGGER_TURNS", 15)),
        summary_keep_recent_turns=int(os.getenv("SUMMARY_KEEP_RECENT_TURNS", 12)),
    )
