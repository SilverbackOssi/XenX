"""AI Chat configuration wrapper.

This module adapts the central application settings (see `app.config`) into a
lightweight config object specific to the AI chat feature. Avoids re-loading
environment variables or creating conflicting sources of truth.
"""
from pydantic import BaseModel
from app.config import get_settings


class AIChatConfig(BaseModel):
    enable_ai_chat: bool
    simulation_mode: bool
    model_provider: str
    model_name: str
    max_tokens_model: int
    rate_limit_requests_per_window: int
    rate_limit_window_seconds: int
    rate_limit_actions_per_hour: int
    action_proposals_per_hour: int
    summary_trigger_turns: int
    summary_keep_recent_turns: int
    invite_reinvite_interval_seconds: int
    log_level: str


def load_ai_chat_config() -> AIChatConfig:
    s = get_settings()
    return AIChatConfig(
        enable_ai_chat=s.ENABLE_AI_CHAT,
        simulation_mode=s.SIMULATION_MODE,
        model_provider=s.MODEL_PROVIDER,
        model_name=s.MODEL_NAME,
        max_tokens_model=s.MAX_TOKENS_MODEL,
        rate_limit_requests_per_window=s.RATE_LIMIT_REQUESTS_PER_WINDOW,
        rate_limit_window_seconds=s.RATE_LIMIT_WINDOW_SECONDS,
        rate_limit_actions_per_hour=s.RATE_LIMIT_ACTIONS_PER_HOUR,
        action_proposals_per_hour=s.ACTION_PROPOSALS_PER_HOUR,
        summary_trigger_turns=s.SUMMARY_TRIGGER_TURNS,
        summary_keep_recent_turns=s.SUMMARY_KEEP_RECENT_TURNS,
        invite_reinvite_interval_seconds=s.INVITE_REINVITE_INTERVAL_SECONDS,
        log_level=s.LOG_LEVEL,
    )


CONFIG = load_ai_chat_config()

__all__ = ["AIChatConfig", "load_ai_chat_config", "CONFIG"]
