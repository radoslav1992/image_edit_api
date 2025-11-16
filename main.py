"""
Background Removal API - Production Ready for RapidAPI
Version: 1.0.0
"""
from fastapi import FastAPI, HTTPException, status, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List
import replicate
import logging
from datetime import datetime
import httpx
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Import custom modules
from config import settings
from middleware import RequestLoggingMiddleware, APIKeyValidationMiddleware
from cache import cache
from validators import ImageValidator

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Professional AI-powered background removal API. Perfect for e-commerce, marketing, and creative applications.",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    terms_of_service="/terms",
    contact={
        "name": "API Support",
        "email": "support@backgroundremoval.api",
    },
    license_info={
        "name": "Commercial License",
        "url": "/terms",
    },
)

# Add rate limit handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
if settings.log_requests:
    app.add_middleware(RequestLoggingMiddleware)

# Parse allowed API keys
allowed_keys = []
if settings.allowed_api_keys:
    allowed_keys = [key.strip() for key in settings.allowed_api_keys.split(",")]

app.add_middleware(APIKeyValidationMiddleware, allowed_keys=allowed_keys)

# Initialize validator
image_validator = ImageValidator(
    max_size_mb=settings.max_image_size_mb,
    allowed_formats=settings.allowed_image_formats
)

# Validate API token on startup
if not settings.replicate_api_token:
    logger.error("REPLICATE_API_TOKEN not found in environment variables")
    raise ValueError("REPLICATE_API_TOKEN must be set in .env file")


# ==================== Models ====================

class BackgroundRemovalRequest(BaseModel):
    """Request model for background removal"""
    image_url: HttpUrl = Field(
        ..., 
        description="URL of the image to process",
        examples=["https://example.com/image.jpg"]
    )
    format: Optional[str] = Field(
        default="png",
        description="Output format: png or jpg",
        examples=["png"]
    )
    reverse: Optional[bool] = Field(
        default=False,
        description="Remove the foreground instead of the background",
        examples=[False]
    )
    threshold: Optional[float] = Field(
        default=0,
        ge=0,
        le=1,
        description="Threshold for background removal (0-1)",
        examples=[0]
    )
    background_type: Optional[str] = Field(
        default="rgba",
        description="Background type: rgba, white, black, or custom color",
        examples=["rgba"]
    )
    webhook_url: Optional[HttpUrl] = Field(
        None,
        description="Optional webhook URL to receive results asynchronously"
    )


class BackgroundRemovalResponse(BaseModel):
    """Response model for background removal"""
    success: bool = Field(..., description="Whether the operation was successful")
    output_url: Optional[str] = Field(None, description="URL of the processed image")
    message: Optional[str] = Field(None, description="Success or error message")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")
    cached: Optional[bool] = Field(None, description="Whether result was from cache")
    request_id: Optional[str] = Field(None, description="Unique request identifier")


class WebhookPayload(BaseModel):
    """Webhook payload model"""
    request_id: str
    success: bool
    output_url: Optional[str] = None
    error: Optional[str] = None
    timestamp: str
    processing_time: float


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    uptime: str
    cache_stats: dict
    api_configured: bool


class UsageStats(BaseModel):
    """Usage statistics"""
    total_requests: int
    cache_hits: int
    cache_misses: int
    cache_hit_rate: str


# ==================== Helper Functions ====================

async def send_webhook(webhook_url: str, payload: WebhookPayload):
    """Send webhook notification"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                str(webhook_url),
                json=payload.dict(),
                timeout=settings.webhook_timeout
            )
            if response.status_code == 200:
                logger.info(f"Webhook sent successfully to {webhook_url}")
            else:
                logger.warning(f"Webhook failed with status {response.status_code}")
    except Exception as e:
        logger.error(f"Error sending webhook: {str(e)}")


def generate_cache_key(request: BackgroundRemovalRequest) -> str:
    """Generate cache key from request parameters"""
    import hashlib
    import json
    
    cache_data = {
        "image_url": str(request.image_url),
        "format": request.format,
        "reverse": request.reverse,
        "threshold": request.threshold,
        "background_type": request.background_type
    }
    
    key_string = json.dumps(cache_data, sort_keys=True)
    return hashlib.md5(key_string.encode()).hexdigest()


# ==================== Endpoints ====================

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - API information"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "online",
        "documentation": "/docs",
        "api_prefix": settings.api_prefix,
        "endpoints": {
            "health": "/health",
            "remove_background": f"{settings.api_prefix}/remove-background",
            "batch_processing": f"{settings.api_prefix}/remove-background/batch",
            "cache_stats": "/cache/stats",
            "terms": "/terms",
            "privacy": "/privacy"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint with system statistics"""
    import time
    
    # Calculate uptime (simplified - in production use actual start time)
    uptime_seconds = int(time.time() % 86400)
    hours = uptime_seconds // 3600
    minutes = (uptime_seconds % 3600) // 60
    
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        uptime=f"{hours}h {minutes}m",
        cache_stats=cache.stats(),
        api_configured=bool(settings.replicate_api_token)
    )


@app.get("/cache/stats", tags=["Admin"])
async def get_cache_stats():
    """Get cache statistics"""
    return {
        "cache": cache.stats(),
        "enabled": settings.cache_enabled
    }


@app.delete("/cache", tags=["Admin"])
async def clear_cache():
    """Clear the cache (admin endpoint)"""
    cache.clear()
    return {"message": "Cache cleared successfully"}


@app.post(
    f"{settings.api_prefix}/remove-background",
    response_model=BackgroundRemovalResponse,
    tags=["Background Removal"],
    summary="Remove background from image",
    description="Remove background from an image using AI. Supports caching and webhooks."
)
@limiter.limit(settings.rate_limit_default)
async def remove_background(
    request_data: BackgroundRemovalRequest,
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Remove background from an image using AI.
    
    Features:
    - AI-powered background removal
    - Response caching for improved performance
    - Webhook support for async notifications
    - Rate limiting to prevent abuse
    - Input validation and error handling
    
    Parameters:
    - **image_url**: URL of the image to process (required)
    - **format**: Output format - png or jpg (default: png)
    - **reverse**: Remove foreground instead of background (default: false)
    - **threshold**: Threshold for background removal 0-1 (default: 0)
    - **background_type**: Background type - rgba, white, black, or custom (default: rgba)
    - **webhook_url**: Optional webhook URL for async notification
    """
    import time
    start_time = time.time()
    
    # Get request ID from middleware
    request_id = getattr(request.state, "request_id", "unknown")
    
    try:
        # Validate image URL (if enabled)
        if settings.validate_image_urls:
            logger.info(f"Validating image: {request_data.image_url}")
            image_validator.validate_image_url(str(request_data.image_url))
        else:
            logger.debug(f"Skipping URL validation for: {request_data.image_url}")
        
        # Validate format
        output_format = image_validator.validate_format(request_data.format)
        
        # Check cache
        cached_result = None
        cache_key = None
        
        if settings.cache_enabled:
            cache_key = generate_cache_key(request_data)
            cached_result = cache.get(cache_key)
            
            if cached_result:
                logger.info(f"Cache hit for request {request_id}")
                processing_time = time.time() - start_time
                
                return BackgroundRemovalResponse(
                    success=True,
                    output_url=cached_result,
                    message="Background removed successfully (cached)",
                    processing_time=processing_time,
                    cached=True,
                    request_id=request_id
                )
        
        # Process image
        logger.info(f"Processing image with Replicate: {request_data.image_url}")
        
        output = replicate.run(
            settings.replicate_model,
            input={
                "image": str(request_data.image_url),
                "format": output_format,
                "reverse": request_data.reverse,
                "threshold": request_data.threshold,
                "background_type": request_data.background_type
            }
        )
        
        # Get output URL
        output_url = output.url() if hasattr(output, 'url') else str(output)
        
        processing_time = time.time() - start_time
        logger.info(f"Successfully processed image in {processing_time:.2f}s. Output: {output_url}")
        
        # Cache result
        if settings.cache_enabled and cache_key:
            cache.set(cache_key, output_url, ttl=settings.cache_ttl)
        
        # Send webhook if provided
        if request_data.webhook_url and settings.webhook_enabled:
            webhook_payload = WebhookPayload(
                request_id=request_id,
                success=True,
                output_url=output_url,
                timestamp=datetime.utcnow().isoformat(),
                processing_time=processing_time
            )
            background_tasks.add_task(send_webhook, request_data.webhook_url, webhook_payload)
        
        return BackgroundRemovalResponse(
            success=True,
            output_url=output_url,
            message="Background removed successfully",
            processing_time=processing_time,
            cached=False,
            request_id=request_id
        )
        
    except HTTPException:
        raise
    except replicate.exceptions.ReplicateError as e:
        logger.error(f"Replicate API error: {str(e)}")
        
        # Send error webhook if provided
        if request_data.webhook_url and settings.webhook_enabled:
            webhook_payload = WebhookPayload(
                request_id=request_id,
                success=False,
                error=str(e),
                timestamp=datetime.utcnow().isoformat(),
                processing_time=time.time() - start_time
            )
            background_tasks.add_task(send_webhook, request_data.webhook_url, webhook_payload)
        
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Background removal service error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        
        # Send error webhook if provided
        if request_data.webhook_url and settings.webhook_enabled:
            webhook_payload = WebhookPayload(
                request_id=request_id,
                success=False,
                error=str(e),
                timestamp=datetime.utcnow().isoformat(),
                processing_time=time.time() - start_time
            )
            background_tasks.add_task(send_webhook, request_data.webhook_url, webhook_payload)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@app.post(
    f"{settings.api_prefix}/remove-background/batch",
    tags=["Background Removal"],
    summary="Batch process multiple images",
    description="Process multiple images for background removal"
)
@limiter.limit("10/minute")
async def remove_background_batch(
    image_urls: List[HttpUrl],
    request: Request,
    format: str = "png",
    background_type: str = "rgba"
):
    """
    Batch process multiple images for background removal.
    
    Rate limited to 10 requests per minute.
    
    Parameters:
    - **image_urls**: List of image URLs to process (max 10)
    - **format**: Output format for all images (default: png)
    - **background_type**: Background type for all images (default: rgba)
    """
    import time
    
    # Limit batch size
    if len(image_urls) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 10 images per batch request"
        )
    
    results = []
    start_time = time.time()
    
    for image_url in image_urls:
        try:
            # Check cache first
            cache_key = None
            cached_result = None
            
            if settings.cache_enabled:
                import hashlib
                import json
                cache_data = {
                    "image_url": str(image_url),
                    "format": format,
                    "background_type": background_type
                }
                cache_key = hashlib.md5(json.dumps(cache_data, sort_keys=True).encode()).hexdigest()
                cached_result = cache.get(cache_key)
            
            if cached_result:
                results.append({
                    "input_url": str(image_url),
                    "success": True,
                    "output_url": cached_result,
                    "cached": True
                })
                continue
            
            # Process image
            output = replicate.run(
                settings.replicate_model,
                input={
                    "image": str(image_url),
                    "format": format,
                    "reverse": False,
                    "threshold": 0,
                    "background_type": background_type
                }
            )
            
            output_url = output.url() if hasattr(output, 'url') else str(output)
            
            # Cache result
            if settings.cache_enabled and cache_key:
                cache.set(cache_key, output_url)
            
            results.append({
                "input_url": str(image_url),
                "success": True,
                "output_url": output_url,
                "cached": False
            })
            
        except Exception as e:
            results.append({
                "input_url": str(image_url),
                "success": False,
                "error": str(e)
            })
    
    processing_time = time.time() - start_time
    
    return {
        "total": len(image_urls),
        "successful": sum(1 for r in results if r["success"]),
        "failed": sum(1 for r in results if not r["success"]),
        "processing_time": processing_time,
        "results": results
    }


@app.get("/terms", tags=["Legal"])
async def terms_of_service():
    """Terms of Service"""
    return {
        "title": "Terms of Service",
        "effective_date": "2024-01-01",
        "terms": {
            "1. Acceptance of Terms": "By accessing and using this API, you accept and agree to be bound by the terms and provision of this agreement.",
            "2. Use License": "Permission is granted to use this API for commercial and personal purposes subject to the restrictions in these terms.",
            "3. Restrictions": {
                "a": "You may not use the API in any way that could damage, disable, or impair the service",
                "b": "You may not attempt to gain unauthorized access to the API or its related systems",
                "c": "You may not use the API to process illegal content or content you don't have rights to",
                "d": "You must comply with all rate limits and usage quotas"
            },
            "4. API Key and Security": "You are responsible for maintaining the confidentiality of your API key and for all activities that occur under your key.",
            "5. Data Privacy": "We process images temporarily and do not store your images or results permanently. See Privacy Policy for details.",
            "6. Service Availability": "We strive for 99.9% uptime but do not guarantee uninterrupted service. Scheduled maintenance will be announced.",
            "7. Payment and Billing": "Subscription fees are billed according to your chosen plan. Overages may apply for usage exceeding plan limits.",
            "8. Refund Policy": "Refunds are provided on a case-by-case basis for service outages exceeding our SLA.",
            "9. Termination": "We reserve the right to terminate or suspend access to our API immediately, without prior notice, for conduct that violates these Terms.",
            "10. Limitation of Liability": "The API is provided 'as is' without warranties. We are not liable for any indirect, incidental, or consequential damages.",
            "11. Changes to Terms": "We reserve the right to modify these terms at any time. Continued use of the API constitutes acceptance of changes.",
            "12. Governing Law": "These terms are governed by applicable international laws.",
            "13. Contact": "For questions about these Terms, contact us at support@backgroundremoval.api"
        }
    }


@app.get("/privacy", tags=["Legal"])
async def privacy_policy():
    """Privacy Policy"""
    return {
        "title": "Privacy Policy",
        "effective_date": "2024-01-01",
        "policy": {
            "1. Information We Collect": {
                "API Usage Data": "We collect API request logs, response times, error rates, and usage statistics",
                "Image URLs": "We temporarily process image URLs provided in API requests",
                "Authentication Data": "API keys, subscription tiers, and user identifiers from RapidAPI"
            },
            "2. How We Use Information": {
                "Service Delivery": "To process your background removal requests",
                "Performance Monitoring": "To monitor API performance and reliability",
                "Analytics": "To understand usage patterns and improve our service",
                "Billing": "To track usage for billing purposes"
            },
            "3. Data Storage and Retention": {
                "Image Processing": "Images are processed in real-time and not stored permanently",
                "Cache": "Results may be cached temporarily (up to 1 hour) for performance",
                "Logs": "Request logs are retained for 30 days for debugging and analytics",
                "No Content Storage": "We do not permanently store your images or processed results"
            },
            "4. Data Sharing": {
                "Third-Party Services": "We use Replicate.com for AI processing. Images are sent to their service. See their privacy policy at replicate.com/privacy",
                "No Sale of Data": "We do not sell your personal information or usage data",
                "Legal Requirements": "We may disclose data if required by law or to protect our rights"
            },
            "5. Security": {
                "Encryption": "All API communications use HTTPS/TLS encryption",
                "API Keys": "API keys are hashed and stored securely",
                "Access Control": "Access to systems is restricted to authorized personnel"
            },
            "6. Your Rights": {
                "Access": "You can request information about data we hold about you",
                "Deletion": "You can request deletion of your account and associated data",
                "Opt-Out": "You can stop using the service at any time"
            },
            "7. Cookies and Tracking": "We do not use cookies. API usage is tracked via request headers only.",
            "8. Children's Privacy": "Our service is not intended for users under 18 years of age.",
            "9. International Data Transfers": "Your data may be processed in various regions where our infrastructure operates.",
            "10. Changes to Privacy Policy": "We will notify users of material changes to this policy.",
            "11. Contact": "For privacy concerns, contact us at privacy@backgroundremoval.api"
        }
    }


@app.get("/pricing", tags=["Information"])
async def pricing_info():
    """Pricing information and plan details"""
    return {
        "title": "API Pricing Plans",
        "currency": "USD",
        "plans": [
            {
                "name": "Free",
                "price": 0,
                "billing": "monthly",
                "features": {
                    "requests_per_month": 50,
                    "rate_limit": "50 per day",
                    "max_image_size": "5MB",
                    "formats": ["png", "jpg"],
                    "cache": True,
                    "webhooks": False,
                    "batch_processing": False,
                    "support": "Community"
                }
            },
            {
                "name": "Basic",
                "price": 9.99,
                "billing": "monthly",
                "features": {
                    "requests_per_month": 1000,
                    "rate_limit": "1000 per day",
                    "max_image_size": "10MB",
                    "formats": ["png", "jpg", "webp"],
                    "cache": True,
                    "webhooks": True,
                    "batch_processing": True,
                    "support": "Email"
                },
                "savings": "90% vs pay-as-you-go"
            },
            {
                "name": "Pro",
                "price": 49.99,
                "billing": "monthly",
                "features": {
                    "requests_per_month": 10000,
                    "rate_limit": "10000 per day",
                    "max_image_size": "20MB",
                    "formats": ["png", "jpg", "webp", "gif"],
                    "cache": True,
                    "webhooks": True,
                    "batch_processing": True,
                    "support": "Priority Email"
                },
                "savings": "95% vs pay-as-you-go",
                "popular": True
            },
            {
                "name": "Enterprise",
                "price": 199.99,
                "billing": "monthly",
                "features": {
                    "requests_per_month": "Unlimited",
                    "rate_limit": "Custom",
                    "max_image_size": "50MB",
                    "formats": ["All supported formats"],
                    "cache": True,
                    "webhooks": True,
                    "batch_processing": True,
                    "support": "24/7 Phone & Email",
                    "sla": "99.9% uptime guarantee",
                    "dedicated_support": True,
                    "custom_features": True
                }
            }
        ],
        "pay_as_you_go": {
            "price_per_request": 0.02,
            "description": "No monthly commitment, pay only for what you use"
        },
        "notes": [
            "All plans include HTTPS encryption and secure processing",
            "Overage charges: $0.01 per additional request",
            "Educational discounts available upon request",
            "Enterprise plans can be customized to your needs",
            "30-day money-back guarantee on all paid plans"
        ],
        "contact": "For custom enterprise plans, contact sales@backgroundremoval.api"
    }


@app.get("/sla", tags=["Information"])
async def service_level_agreement():
    """Service Level Agreement details"""
    return {
        "title": "Service Level Agreement (SLA)",
        "version": "1.0",
        "effective_date": "2024-01-01",
        "sla": {
            "uptime_guarantee": {
                "free_tier": "Best effort (no guarantee)",
                "basic_tier": "99.0% monthly uptime",
                "pro_tier": "99.5% monthly uptime",
                "enterprise_tier": "99.9% monthly uptime"
            },
            "response_time": {
                "p50": "< 2 seconds",
                "p95": "< 5 seconds",
                "p99": "< 10 seconds",
                "note": "Response times exclude AI processing time which varies by image size"
            },
            "support_response_time": {
                "free": "Best effort via community forums",
                "basic": "48 hours via email",
                "pro": "24 hours via email",
                "enterprise": "4 hours via phone/email, 24/7 availability"
            },
            "maintenance_windows": {
                "scheduled": "Announced 48 hours in advance",
                "frequency": "Monthly, typically on weekends",
                "duration": "Maximum 2 hours",
                "emergency": "May occur without notice for critical issues"
            },
            "data_retention": {
                "request_logs": "30 days",
                "cached_results": "1 hour",
                "images": "Not stored (processed in real-time only)"
            },
            "service_credits": {
                "99.9%_to_99.0%": "10% monthly fee credit",
                "99.0%_to_95.0%": "25% monthly fee credit",
                "below_95.0%": "50% monthly fee credit"
            },
            "exclusions": {
                "1": "Downtime caused by third-party services (Replicate.com)",
                "2": "Issues caused by customer's network or systems",
                "3": "Scheduled maintenance windows",
                "4": "Force majeure events",
                "5": "Customer's violation of Terms of Service"
            },
            "monitoring": {
                "status_page": "status.backgroundremoval.api",
                "real_time_monitoring": "24/7 automated monitoring",
                "incident_notification": "Email alerts for Pro and Enterprise tiers"
            },
            "claiming_credits": {
                "process": "Submit ticket within 30 days of incident",
                "review_time": "5 business days",
                "application": "Credits applied to next billing cycle"
            }
        }
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unexpected errors"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "An unexpected error occurred",
            "detail": str(exc) if settings.log_level == "DEBUG" else "Internal server error",
            "request_id": getattr(request.state, "request_id", "unknown")
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower()
    )
