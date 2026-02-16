"""
Rate limiting middleware for FastAPI.
"""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from config import config


def get_client_ip(request: Request) -> str:
    """
    Get client IP address from request.
    
    Args:
        request: FastAPI request
        
    Returns:
        str: Client IP address
    """
    # Check for forwarded IP first (for proxy/load balancer scenarios)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    
    # Fallback to direct connection IP
    return get_remote_address(request)


# Initialize rate limiter
limiter = Limiter(
    key_func=get_client_ip,
    default_limits=[f"{config.RATE_LIMIT_PER_MINUTE}/minute"]
)
