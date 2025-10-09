"""Rate limiting and security middleware."""

import time
from collections import defaultdict
from typing import Callable

from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

from ..config import get_settings

settings = get_settings()


class RateLimiter:
    """In-memory rate limiter (use Redis for production)."""

    def __init__(self):
        self.requests = defaultdict(list)
        self.blocked = set()

    def is_rate_limited(
        self,
        identifier: str,
        max_requests: int = 100,
        window_seconds: int = 60,
    ) -> bool:
        """Check if identifier is rate limited.

        Args:
            identifier: IP address or user ID
            max_requests: Maximum requests per window
            window_seconds: Time window in seconds

        Returns:
            True if rate limited, False otherwise
        """
        if identifier in self.blocked:
            return True

        now = time.time()
        window_start = now - window_seconds

        # Clean old requests
        self.requests[identifier] = [
            req_time
            for req_time in self.requests[identifier]
            if req_time > window_start
        ]

        # Check limit
        if len(self.requests[identifier]) >= max_requests:
            self.blocked.add(identifier)
            return True

        # Add current request
        self.requests[identifier].append(now)
        return False

    def reset_identifier(self, identifier: str):
        """Reset rate limit for identifier.

        Args:
            identifier: IP address or user ID
        """
        if identifier in self.requests:
            del self.requests[identifier]
        if identifier in self.blocked:
            self.blocked.remove(identifier)


# Global rate limiter instance
rate_limiter = RateLimiter()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware."""

    async def dispatch(self, request: Request, call_next: Callable):
        """Process request with rate limiting.

        Args:
            request: HTTP request
            call_next: Next middleware/handler

        Returns:
            HTTP response

        Raises:
            HTTPException: If rate limited
        """
        # Skip rate limiting for health checks
        if request.url.path in ["/health/ready", "/health/live"]:
            return await call_next(request)

        # Get identifier (IP or user)
        identifier = request.client.host

        # Check rate limit
        if rate_limiter.is_rate_limited(
            identifier,
            max_requests=settings.auth.rate_limit_requests,
            window_seconds=settings.auth.rate_limit_window,
        ):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later.",
                headers={"Retry-After": str(settings.auth.rate_limit_window)},
            )

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        remaining = settings.auth.rate_limit_requests - len(
            rate_limiter.requests[identifier]
        )
        response.headers["X-RateLimit-Limit"] = str(settings.auth.rate_limit_requests)
        response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))
        response.headers["X-RateLimit-Reset"] = str(
            int(time.time()) + settings.auth.rate_limit_window
        )

        return response


rate_limit_middleware = RateLimitMiddleware





