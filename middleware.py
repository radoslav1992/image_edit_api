"""
Custom middleware for logging, tracking, and authentication
"""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import time
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all requests and track usage"""
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Generate request ID
        request_id = f"{int(time.time() * 1000)}"
        
        # Start timer
        start_time = time.time()
        
        # Get user info from headers (RapidAPI forwards user info)
        user_id = request.headers.get("X-RapidAPI-User", "anonymous")
        subscription = request.headers.get("X-RapidAPI-Subscription", "free")
        
        # Log request
        logger.info(
            f"Request started | ID: {request_id} | "
            f"Method: {request.method} | Path: {request.url.path} | "
            f"User: {user_id} | Subscription: {subscription}"
        )
        
        # Add custom headers to request state
        request.state.request_id = request_id
        request.state.user_id = user_id
        request.state.subscription = subscription
        request.state.start_time = start_time
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log response
            logger.info(
                f"Request completed | ID: {request_id} | "
                f"Status: {response.status_code} | "
                f"Duration: {duration:.2f}s"
            )
            
            # Add custom headers to response
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{duration:.2f}s"
            
            # Track usage (in production, save to database)
            self._track_usage(
                request_id=request_id,
                user_id=user_id,
                subscription=subscription,
                endpoint=request.url.path,
                method=request.method,
                status_code=response.status_code,
                duration=duration
            )
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"Request failed | ID: {request_id} | "
                f"Error: {str(e)} | Duration: {duration:.2f}s"
            )
            raise
    
    def _track_usage(self, **kwargs):
        """Track API usage (implement database logging in production)"""
        usage_data = {
            "timestamp": datetime.utcnow().isoformat(),
            **kwargs
        }
        
        # In production, save to database or analytics service
        logger.debug(f"Usage tracked: {json.dumps(usage_data)}")


class APIKeyValidationMiddleware(BaseHTTPMiddleware):
    """Middleware to validate API keys"""
    
    def __init__(self, app, allowed_keys: list = None):
        super().__init__(app)
        self.allowed_keys = allowed_keys or []
        # Public endpoints that don't require API key
        self.public_paths = ["/", "/health", "/docs", "/redoc", "/openapi.json", "/terms", "/privacy"]
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Skip validation for public endpoints
        if any(request.url.path.startswith(path) for path in self.public_paths):
            return await call_next(request)
        
        # Check for RapidAPI headers (RapidAPI adds these automatically)
        rapidapi_key = request.headers.get("X-RapidAPI-Key")
        rapidapi_secret = request.headers.get("X-RapidAPI-Proxy-Secret")
        
        # If RapidAPI headers present, allow (RapidAPI handles auth)
        if rapidapi_key or rapidapi_secret:
            logger.debug("Request authenticated via RapidAPI")
            return await call_next(request)
        
        # Check for custom API key (for direct access)
        api_key = request.headers.get("X-API-Key")
        
        if not api_key:
            # In development mode, allow requests without API key
            # In production, you should enforce this
            if len(self.allowed_keys) > 0:
                logger.warning("Request without API key")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="API key required. Provide X-API-Key header or use RapidAPI."
                )
            else:
                logger.debug("API key validation disabled (development mode)")
                return await call_next(request)
        
        # Validate API key
        if self.allowed_keys and api_key not in self.allowed_keys:
            logger.warning(f"Invalid API key attempted: {api_key[:8]}...")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid API key"
            )
        
        logger.debug("Request authenticated via API key")
        return await call_next(request)

