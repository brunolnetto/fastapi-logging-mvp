from slowapi import Limiter
from slowapi.util import get_remote_address

from backend.app.config import settings

# Initialize the Limiter with a global rate limit (e.g., 5 requests per minute)
limiter = Limiter(
    key_func=get_remote_address, default_limits=settings.DEFAULT_RATE_LIMITS
)
