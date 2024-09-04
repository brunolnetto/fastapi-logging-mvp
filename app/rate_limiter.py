from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from slowapi import _rate_limit_exceeded_handler

from app.config import settings

# Initialize the Limiter with a global rate limit (e.g., 5 requests per minute)
limiter = Limiter(key_func=get_remote_address, default_limits=settings.DEFAULT_RATE_LIMITS)

