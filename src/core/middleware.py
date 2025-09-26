"""Security middleware for FastAPI."""

import time
import logging
from typing import Callable
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from src.core.security import security_headers, rate_limiter, input_validator

logger = logging.getLogger(__name__)


class SecurityMiddleware:
    """Security middleware for request/response processing."""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope: dict, receive: Callable, send: Callable):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        
        # Security checks
        try:
            # Check for blocked IPs
            client_ip = request.client.host
            if rate_limiter.is_ip_blocked(client_ip):
                response = JSONResponse(
                    status_code=403,
                    content={"detail": "Access denied"}
                )
                await response(scope, receive, send)
                return
            
            # Process request
            response = await self.app(scope, receive, send)
            
            # Add security headers
            if hasattr(response, 'headers'):
                for header, value in security_headers.get_security_headers().items():
                    response.headers[header] = value
            
            return response
            
        except Exception as e:
            logger.error(f"Security middleware error: {str(e)}")
            response = JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"}
            )
            await response(scope, receive, send)


class RequestLoggingMiddleware:
    """Middleware for secure request logging."""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope: dict, receive: Callable, send: Callable):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        start_time = time.time()
        
        # Log request (sanitized)
        client_ip = request.client.host
        user_agent = request.headers.get("user-agent", "unknown")
        
        logger.info(
            "Request received",
            extra={
                "method": request.method,
                "url": str(request.url),
                "client_ip": client_ip,
                "user_agent": input_validator.sanitize_for_logging(user_agent),
                "timestamp": start_time
            }
        )
        
        # Process request
        response = await self.app(scope, receive, send)
        
        # Log response
        duration = time.time() - start_time
        logger.info(
            "Request completed",
            extra={
                "method": request.method,
                "url": str(request.url),
                "client_ip": client_ip,
                "duration": duration,
                "status_code": getattr(response, 'status_code', 200)
            }
        )
        
        return response


class CORSMiddleware:
    """Secure CORS middleware."""
    
    def __init__(self, app, allowed_origins: list = None):
        self.app = app
        self.allowed_origins = allowed_origins or ["http://localhost:3000", "http://localhost:8501"]
    
    async def __call__(self, scope: dict, receive: Callable, send: Callable):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        origin = request.headers.get("origin")
        
        # Check origin
        if origin and origin not in self.allowed_origins:
            response = JSONResponse(
                status_code=403,
                content={"detail": "Origin not allowed"}
            )
            await response(scope, receive, send)
            return
        
        # Process request
        response = await self.app(scope, receive, send)
        
        # Add CORS headers
        if hasattr(response, 'headers'):
            if origin in self.allowed_origins:
                response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            response.headers["Access-Control-Max-Age"] = "86400"
        
        return response
