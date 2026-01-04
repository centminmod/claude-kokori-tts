"""
Hot cache implementation for the TTS system.

This module provides an in-memory cache for frequently accessed messages.
Layer 3 - Storage & Processing: Depends on Layers 1-2.
"""

import threading
from typing import Dict, Set

from modules.types.protocols import CacheProtocol


class HotCache(CacheProtocol):
    """In-memory hot cache for frequently accessed messages"""
    
    def __init__(self, hot_cache_keys: Set[str] = None):
        """
        Initialize hot cache.
        
        Args:
            hot_cache_keys: Set of keys that should be kept in hot cache
        """
        self.cache: Dict[str, bytes] = {}
        self.hot_cache_keys = hot_cache_keys or set()
        self.lock = threading.Lock()
    
    def get(self, key: str) -> bytes:
        """Get item from hot cache"""
        with self.lock:
            return self.cache.get(key)
    
    def put(self, key: str, value: bytes) -> None:
        """Put item in hot cache (only if it's a hot cache key)"""
        if key.lower() in self.hot_cache_keys:
            with self.lock:
                self.cache[key] = value
    
    def clear(self) -> None:
        """Clear all hot cache entries"""
        with self.lock:
            self.cache.clear()
    
    def stats(self) -> Dict[str, any]:
        """Get hot cache statistics"""
        with self.lock:
            return {
                "entries": len(self.cache),
                "messages": list(self.hot_cache_keys),
                "memory_mb": sum(len(data) for data in self.cache.values()) / (1024 * 1024)
            }
    
    def add_hot_key(self, key: str) -> None:
        """Add a key to the hot cache keys set"""
        with self.lock:
            self.hot_cache_keys.add(key.lower())
    
    def remove_hot_key(self, key: str) -> None:
        """Remove a key from the hot cache keys set"""
        with self.lock:
            self.hot_cache_keys.discard(key.lower())
            # Also remove from cache if present
            if key in self.cache:
                del self.cache[key]
    
    def is_hot_key(self, key: str) -> bool:
        """Check if a key is marked as hot"""
        return key.lower() in self.hot_cache_keys