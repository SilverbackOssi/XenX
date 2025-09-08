import redis.asyncio as redis
from app.config import get_settings
from datetime import timedelta

settings = get_settings()

# Create a reusable Redis connection pool
redis_pool = redis.ConnectionPool.from_url(
    settings.REDIS_URL, 
    decode_responses=True # Decode responses to strings
)

def get_redis_client() -> redis.Redis:
    """
    Dependency to get a Redis client from the connection pool.
    """
    return redis.Redis(connection_pool=redis_pool)


class BlacklistService:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    async def add_to_blacklist(self, jti: str, expires_in: timedelta):
        """
        Adds a token's JTI (JWT ID) to the blacklist with an expiry.
        The expiry prevents the blacklist from growing indefinitely.
        """
        await self.redis.set(f"jti:{jti}", "blacklisted", ex=expires_in)

    async def is_blacklisted(self, jti: str) -> bool:
        """
        Checks if a token's JTI is in the blacklist.
        """
        return await self.redis.get(f"jti:{jti}") is not None