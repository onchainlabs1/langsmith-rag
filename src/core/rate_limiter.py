"""Rate limiting middleware for EU AI Act Compliance RAG System."""

import time
from typing import Dict, Optional
from collections import defaultdict, deque
from datetime import datetime, timedelta

from fastapi import HTTPException, status, Request
from fastapi.responses import Response

from src.core.auth import get_current_user, User


class TokenBucket:
    """Token bucket rate limiter implementation."""
    
    def __init__(self, capacity: int, refill_rate: float):
        """Initialize token bucket.
        
        Args:
            capacity: Maximum number of tokens
            refill_rate: Tokens added per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()
    
    def consume(self, tokens: int = 1) -> bool:
        """Try to consume tokens from bucket.
        
        Args:
            tokens: Number of tokens to consume
            
        Returns:
            True if tokens were consumed, False otherwise
        """
        now = time.time()
        time_passed = now - self.last_refill
        
        # Refill tokens based on time passed
        self.tokens = min(self.capacity, self.tokens + time_passed * self.refill_rate)
        self.last_refill = now
        
        # Check if we have enough tokens
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False


class FixedWindowLimiter:
    """Fixed window rate limiter implementation."""
    
    def __init__(self, window_size: int, max_requests: int):
        """Initialize fixed window limiter.
        
        Args:
            window_size: Window size in seconds
            max_requests: Maximum requests per window
        """
        self.window_size = window_size
        self.max_requests = max_requests
        self.windows: Dict[str, deque] = defaultdict(deque)
    
    def is_allowed(self, key: str) -> bool:
        """Check if request is allowed.
        
        Args:
            key: Unique identifier for rate limiting
            
        Returns:
            True if request is allowed, False otherwise
        """
        now = time.time()
        window_start = now - self.window_size
        
        # Clean old requests
        user_requests = self.windows[key]
        while user_requests and user_requests[0] < window_start:
            user_requests.popleft()
        
        # Check if under limit
        if len(user_requests) < self.max_requests:
            user_requests.append(now)
            return True
        return False


class RateLimiter:
    """Rate limiter service."""
    
    def __init__(self) -> None:
        """Initialize rate limiter."""
        # Rate limits per user role
        self.limits = {
            "admin": {"requests_per_minute": 300, "burst": 50},
            "analyst": {"requests_per_minute": 120, "burst": 20},
            "viewer": {"requests_per_minute": 60, "burst": 10}
        }
        
        # User-specific rate limiters
        self.user_limiters: Dict[str, TokenBucket] = {}
        
    def get_user_limiter(self, user_id: str, role: str) -> TokenBucket:
        """Get or create rate limiter for user."""
        if user_id not in self.user_limiters:
            limits = self.limits.get(role, self.limits["viewer"])
            # Convert to tokens per second
            refill_rate = limits["requests_per_minute"] / 60.0
            capacity = limits["burst"]
            
            self.user_limiters[user_id] = TokenBucket(capacity, refill_rate)
        
        return self.user_limiters[user_id]
    
    def is_allowed(self, user_id: str, role: str) -> bool:
        """Check if request is allowed for user."""
        limiter = self.get_user_limiter(user_id, role)
        return limiter.consume()
    
    def get_remaining_tokens(self, user_id: str, role: str) -> int:
        """Get remaining tokens for user."""
        limiter = self.get_user_limiter(user_id, role)
        return int(limiter.tokens)
    
    def get_reset_time(self, user_id: str, role: str) -> float:
        """Get time until tokens reset."""
        limiter = self.get_user_limiter(user_id, role)
        limits = self.limits.get(role, self.limits["viewer"])
        refill_rate = limits["requests_per_minute"] / 60.0
        
        if limiter.tokens >= limiter.capacity:
            return 0
        
        tokens_needed = limiter.capacity - limiter.tokens
        return tokens_needed / refill_rate


# Global rate limiter instance
rate_limiter = RateLimiter()


async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware."""
    # Skip rate limiting for health checks and metrics
    if request.url.path in ["/health", "/metrics", "/docs", "/openapi.json"]:
        return await call_next(request)
    
    # Get user from JWT token
    try:
        from src.core.auth import get_current_user
        user = get_current_user()
        
        # Check rate limit
        if not rate_limiter.is_allowed(user.user_id, user.role.value):
            # Calculate rate limit headers
            remaining = rate_limiter.get_remaining_tokens(user.user_id, user.role.value)
            reset_time = rate_limiter.get_reset_time(user.user_id, user.role.value)
            
            response = Response(
                content='{"detail": "Rate limit exceeded"}',
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                media_type="application/json"
            )
            
            # Add rate limit headers
            response.headers["X-RateLimit-Limit"] = str(rate_limiter.limits[user.role.value]["requests_per_minute"])
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            response.headers["X-RateLimit-Reset"] = str(int(time.time() + reset_time))
            response.headers["Retry-After"] = str(int(reset_time))
            
            return response
        
        # Add rate limit headers to successful response
        response = await call_next(request)
        
        remaining = rate_limiter.get_remaining_tokens(user.user_id, user.role.value)
        reset_time = rate_limiter.get_reset_time(user.user_id, user.role.value)
        
        response.headers["X-RateLimit-Limit"] = str(rate_limiter.limits[user.role.value]["requests_per_minute"])
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time() + reset_time))
        
        return response
        
    except HTTPException as e:
        # If authentication fails, let it pass through
        if e.status_code == status.HTTP_401_UNAUTHORIZED:
            return await call_next(request)
        raise
    except Exception:
        # If rate limiting fails, allow request to proceed
        return await call_next(request)
