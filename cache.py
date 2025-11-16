"""
Simple caching mechanism for API responses
"""
from typing import Optional, Any
import hashlib
import json
import time
from collections import OrderedDict
import logging

logger = logging.getLogger(__name__)


class SimpleCache:
    """
    Simple in-memory cache with TTL support.
    In production, use Redis or Memcached for distributed caching.
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.cache = OrderedDict()
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.hits = 0
        self.misses = 0
    
    def _generate_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key not in self.cache:
            self.misses += 1
            logger.debug(f"Cache miss: {key}")
            return None
        
        value, expiry = self.cache[key]
        
        # Check if expired
        if time.time() > expiry:
            del self.cache[key]
            self.misses += 1
            logger.debug(f"Cache expired: {key}")
            return None
        
        # Move to end (most recently used)
        self.cache.move_to_end(key)
        self.hits += 1
        logger.debug(f"Cache hit: {key}")
        return value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache"""
        # Enforce max size
        if len(self.cache) >= self.max_size:
            # Remove oldest item
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
            logger.debug(f"Cache full, removed oldest: {oldest_key}")
        
        expiry = time.time() + (ttl or self.default_ttl)
        self.cache[key] = (value, expiry)
        logger.debug(f"Cache set: {key}, TTL: {ttl or self.default_ttl}s")
    
    def delete(self, key: str):
        """Delete value from cache"""
        if key in self.cache:
            del self.cache[key]
            logger.debug(f"Cache deleted: {key}")
    
    def clear(self):
        """Clear all cache"""
        self.cache.clear()
        logger.info("Cache cleared")
    
    def stats(self) -> dict:
        """Get cache statistics"""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": f"{hit_rate:.2f}%",
            "total_requests": total_requests
        }


# Global cache instance
cache = SimpleCache(max_size=1000, default_ttl=3600)

