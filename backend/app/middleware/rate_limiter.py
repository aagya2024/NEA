"""
Rate Limiter
=============
Simple in-memory rate limiter for protecting expensive endpoints (e.g., chatbot).

NOTE: This uses in-memory storage and resets on server restart.
For production with multiple workers, use Redis-based rate limiting.
"""

import time
from collections import defaultdict
from fastapi import HTTPException, status, Request, Depends


class RateLimiter:
    """
    Token bucket rate limiter.
    
    Args:
        max_requests: Maximum requests allowed in the time window
        window_seconds: Time window in seconds
    """
    
    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: dict[str, list[float]] = defaultdict(list)
    
    def _cleanup(self, key: str):
        """Remove expired timestamps."""
        now = time.time()
        self._requests[key] = [
            ts for ts in self._requests[key]
            if now - ts < self.window_seconds
        ]
    
    def check(self, key: str) -> bool:
        """Check if a request is allowed."""
        self._cleanup(key)
        if len(self._requests[key]) >= self.max_requests:
            return False
        self._requests[key].append(time.time())
        return True


# Pre-configured limiter instances
chat_limiter = RateLimiter(max_requests=20, window_seconds=60)


def rate_limit_chat(request: Request):
    """
    FastAPI dependency that enforces rate limiting on chat endpoints.
    
    Uses client IP as the rate limit key.
    """
    client_ip = request.client.host if request.client else "unknown"
    
    if not chat_limiter.check(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please wait before sending another message.",
        )
