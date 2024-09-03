from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from slowapi import _rate_limit_exceeded_handler

# Initialize the Limiter with a global rate limit (e.g., 5 requests per minute)
default_limits=["10/minute", "500/hour"]
limiter = Limiter(key_func=get_remote_address, default_limits=default_limits)

