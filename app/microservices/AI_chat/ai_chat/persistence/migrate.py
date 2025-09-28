"""Lightweight migration / table creation for AI Chat models.

This module intentionally avoids a full Alembic dependency for early phases.
It can be invoked at application startup to ensure the AI Chat tables exist.

Usage (async):
    from .migrate import ensure_ai_chat_tables
    await ensure_ai_chat_tables()

Idempotent: SQLAlchemy's `create_all` is safe if tables already exist.
"""
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from app.gateway.database import engine, Base
from ..models import db as models  # noqa: F401  (import registers models with Base)


async def ensure_ai_chat_tables() -> None:
    """Create AI Chat related tables if they do not exist.

    Wrapped in a single connection. Errors are logged then re-raised so that
    startup can decide whether to continue or abort.
    """
    async with engine.begin() as conn:
        try:
            await conn.run_sync(Base.metadata.create_all)
        except SQLAlchemyError as exc:  # pragma: no cover - defensive
            # Simple stderr logging (replace with structured logger later)
            print(f"[AI_CHAT][MIGRATION][ERROR] {exc}")
            raise
        else:  # pragma: no cover - trivial branch
            # Optional: record a marker (could be removed later)
            try:
                await conn.execute(text("SELECT 1"))
            except Exception:  # noqa: BLE001
                pass

__all__ = ["ensure_ai_chat_tables"]
