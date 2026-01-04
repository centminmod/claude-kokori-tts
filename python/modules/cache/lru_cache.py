"""
LRU Cache implementation for the TTS system.

This module provides a thread-safe LRU cache with size and memory limits.
Layer 3 - Storage & Processing: Depends on Layers 1-2.
"""

import threading
from collections import OrderedDict
from typing import Optional, Dict, Any, Tuple

from modules.types.protocols import CacheProtocol


class LRUCache(CacheProtocol):
    """Thread-safe LRU cache with size limits"""
    
    def __init__(self, max_size: int = 100, max_memory_mb: int = 100):
        """
        Initialize LRU cache.
        
        Args:
            max_size: Maximum number of items in cache
            max_memory_mb: Maximum memory usage in MB
        """
        self.max_size = max_size
        self.max_memory = max_memory_mb * 1024 * 1024  # Convert to bytes
        self.cache: OrderedDict[str, Tuple[bytes, int]] = OrderedDict()
        self.current_memory = 0
        self.lock = threading.Lock()
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[bytes]:
        """Get item from cache"""
        with self.lock:
            if key in self.cache:
                # Move to end (most recent)
                self.cache.move_to_end(key)
                self.hits += 1
                return self.cache[key][0]
            self.misses += 1
            return None
    
    def put(self, key: str, value: bytes) -> None:
        """Put item in cache with size management"""
        size = len(value)
        
        with self.lock:
            # Remove old entry if exists
            if key in self.cache:
                old_size = self.cache[key][1]
                self.current_memory -= old_size
                del self.cache[key]
            
            # Evict items if necessary
            while (len(self.cache) >= self.max_size or 
                   self.current_memory + size > self.max_memory) and self.cache:
                oldest_key, (_, old_size) = self.cache.popitem(last=False)
                self.current_memory -= old_size
            
            # Add new item
            self.cache[key] = (value, size)
            self.current_memory += size
    
    def clear(self) -> None:
        """Clear all cache entries"""
        with self.lock:
            self.cache.clear()
            self.current_memory = 0
            self.hits = 0
            self.misses = 0
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            total_requests = self.hits + self.misses
            hit_rate = self.hits / total_requests if total_requests > 0 else 0
            return {
                "size": len(self.cache),
                "memory_mb": self.current_memory / (1024 * 1024),
                "hits": self.hits,
                "misses": self.misses,
                "hit_rate": hit_rate
            }