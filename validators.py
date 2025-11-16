"""
Validation utilities for API requests
"""
from fastapi import HTTPException, status
from typing import Optional
import requests
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)


class ImageValidator:
    """Validate image URLs and properties"""
    
    def __init__(self, max_size_mb: int = 10, allowed_formats: list = None):
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.allowed_formats = allowed_formats or ["jpg", "jpeg", "png", "webp", "gif"]
    
    def validate_url(self, url: str) -> bool:
        """Validate URL format"""
        try:
            result = urlparse(str(url))
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def validate_image_url(self, url: str, check_size: bool = True) -> dict:
        """
        Validate image URL and optionally check file size
        Returns dict with validation results
        """
        # Check URL format
        if not self.validate_url(url):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid URL format"
            )
        
        # Check if URL is accessible
        if check_size:
            try:
                # HEAD request to check size without downloading
                response = requests.head(str(url), timeout=10, allow_redirects=True)
                
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Image URL not accessible (status: {response.status_code})"
                    )
                
                # Check content type
                content_type = response.headers.get("Content-Type", "").lower()
                if not content_type.startswith("image/"):
                    logger.warning(f"Non-image content type: {content_type}")
                    # Don't fail, as some servers don't set correct content-type
                
                # Check file size
                content_length = response.headers.get("Content-Length")
                if content_length:
                    size_bytes = int(content_length)
                    size_mb = size_bytes / (1024 * 1024)
                    
                    if size_bytes > self.max_size_bytes:
                        raise HTTPException(
                            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            detail=f"Image too large ({size_mb:.2f}MB). Maximum allowed: {self.max_size_bytes / (1024 * 1024)}MB"
                        )
                    
                    logger.info(f"Image size validated: {size_mb:.2f}MB")
                    
                    return {
                        "valid": True,
                        "size_bytes": size_bytes,
                        "size_mb": size_mb,
                        "content_type": content_type
                    }
                else:
                    logger.warning("Content-Length header not present, skipping size check")
                    return {
                        "valid": True,
                        "size_bytes": None,
                        "size_mb": None,
                        "content_type": content_type
                    }
                    
            except requests.exceptions.Timeout:
                raise HTTPException(
                    status_code=status.HTTP_408_REQUEST_TIMEOUT,
                    detail="Image URL request timed out"
                )
            except requests.exceptions.RequestException as e:
                logger.error(f"Error validating image URL: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Could not validate image URL: {str(e)}"
                )
        
        return {"valid": True}
    
    def validate_format(self, format_str: str) -> str:
        """Validate output format"""
        format_lower = format_str.lower()
        
        if format_lower not in self.allowed_formats:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid format '{format_str}'. Allowed: {', '.join(self.allowed_formats)}"
            )
        
        return format_lower

