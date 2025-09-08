from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Create a limiter instance.
# The key_func determines how to identify a client (e.g., by IP address).
limiter = Limiter(key_func=get_remote_address, default_limits=["100 per minute"])

def setup_rate_limiter(app):
    """
    Adds the rate limiter to the FastAPI application instance.
    """
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)