"""Lightweight test/diagnostic to verify AI Chat tables exist.

Not a formal pytest (can be adapted later). Provides an async `main` callable
so it can be executed manually if desired.
"""
import asyncio
from sqlalchemy import inspect
from app.gateway.database import engine
from app.microservices.AI_chat.ai_chat.persistence.migrate import ensure_ai_chat_tables


EXPECTED_TABLES = {
    "ai_chat_conversations",
    "ai_chat_messages",
    "ai_chat_summaries",
    "ai_chat_audits",
    "ai_chat_rate_limits",
}


async def check_tables():
    await ensure_ai_chat_tables()
    async with engine.begin() as conn:
        insp = await conn.run_sync(inspect)
        existing = set(insp.get_table_names())
        missing = EXPECTED_TABLES - existing
        return existing, missing


async def main():  # pragma: no cover - manual diagnostic
    existing, missing = await check_tables()
    if missing:
        print(f"❌ Missing tables: {missing}")
    else:
        print("✅ All AI Chat tables present.")


if __name__ == "__main__":  # pragma: no cover
    asyncio.run(main())
