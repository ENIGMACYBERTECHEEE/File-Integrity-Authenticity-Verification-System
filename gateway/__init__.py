"""
Import fix for slowapi module.
"""
from slowapi.errors import RateLimitExceeded

def _rate_limit_exceeded_handler(request, exc):
    """Handle rate limit exceeded exception."""
    from fastapi.responses import JSONResponse
    from fastapi import status
    
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"detail": "Rate limit exceeded. Please try again later."}
    )
