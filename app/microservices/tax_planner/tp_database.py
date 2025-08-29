from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.TAX_PLANNER_DATABASE_URL,
    echo=settings.DATABASE_ECHO
)
AsyncSessionLocal = async_sessionmaker(
    engine, expire_on_commit=False
)
TPBase = declarative_base()

async def init_tp_db():
    async with engine.begin() as conn:
        await conn.run_sync(TPBase.metadata.drop_all)
        await conn.run_sync(TPBase.metadata.create_all)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except:
            await session.rollback()
            raise
        finally:
            await session.close()

