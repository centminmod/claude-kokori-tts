"""
Cache management and coordination for the TTS system.

This module provides a unified interface for managing multiple cache tiers.
Layer 3 - Storage & Processing: Depends on Layers 1-2.
"""

import time
import logging
from typing import Optional, Dict, Any, Set

from modules.types.protocols import AudioCacheProtocol
from modules.cache.lru_cache import LRUCache
from modules.cache.disk_cache import DiskCache
from modules.cache.hot_cache import HotCache

logger = logging.getLogger(__name__)


class CacheManager:
    """Unified cache manager for three-tier caching system"""
    
    def __init__(
        self,
        max_cache_size: int = 100,
        max_cache_memory_mb: int = 100,
        max_disk_cache_gb: float = 1.0,
        hot_cache_keys: Set[str] = None
    ):
        """
        Initialize cache manager with three-tier system.
        
        Args:
            max_cache_size: Maximum items in LRU cache
            max_cache_memory_mb: Maximum LRU cache memory in MB
            max_disk_cache_gb: Maximum disk cache size in GB
            hot_cache_keys: Set of keys for hot cache
        """
        # Three-tier cache system
        self.hot_cache = HotCache(hot_cache_keys or set())  # Tier 1: Hot memory cache
        self.disk_cache = DiskCache(max_size_gb=max_disk_cache_gb)  # Tier 2: Persistent cache
        self.lru_cache = LRUCache(max_cache_size, max_cache_memory_mb)  # Tier 3: LRU cache
        
        # Performance constants
        self.MS_PER_SECOND = 1000
    
    def get_audio(self, text: str, voice: str, speed: float, format: str) -> Optional[bytes]:
        """
        Get audio from cache using tiered approach.
        
        Args:
            text: Text content
            voice: Voice specification  
            speed: Speech speed
            format: Audio format
            
        Returns:
            Audio bytes if found, None otherwise
        """
        start_time = time.time() if logger.isEnabledFor(logging.DEBUG) else None
        
        # Tier 1: Check hot memory cache first (fastest)
        if text.lower() in self.hot_cache.hot_cache_keys:
            hot_key = f"{text.lower()}_{voice}_{speed}_{format}"
            hot_result = self.hot_cache.get(hot_key)
            if hot_result:
                if start_time:
                    elapsed = (time.time() - start_time) * self.MS_PER_SECOND
                    logger.debug(f"⏱️ Hot cache response time: {elapsed:.1f}ms")
                return hot_result
        
        # Tier 2: Check disk cache (fast)
        disk_result = self.disk_cache.get(text, voice, speed, format)
        if disk_result:
            if start_time:
                elapsed = (time.time() - start_time) * self.MS_PER_SECOND
                logger.debug(f"⏱️ Disk cache response time: {elapsed:.1f}ms")
            
            # Promote to hot cache if applicable
            if text.lower() in self.hot_cache.hot_cache_keys:
                hot_key = f"{text.lower()}_{voice}_{speed}_{format}"
                self.hot_cache.put(hot_key, disk_result)
            
            # Also add to LRU cache for faster subsequent access
            cache_key = f"{hash(text)}_{voice}_{speed}_{format}"
            self.lru_cache.put(cache_key, disk_result)
            
            return disk_result
        
        # Tier 3: Check LRU memory cache
        cache_key = f"{hash(text)}_{voice}_{speed}_{format}"
        lru_result = self.lru_cache.get(cache_key)
        if lru_result:
            if start_time:
                elapsed = (time.time() - start_time) * self.MS_PER_SECOND
                logger.debug(f"⏱️ Memory cache response time: {elapsed:.1f}ms")
            return lru_result
        
        return None
    
    def put_audio(self, text: str, voice: str, speed: float, format: str, audio_data: bytes) -> None:
        """
        Store audio in appropriate cache tiers.
        
        Args:
            text: Text content
            voice: Voice specification
            speed: Speech speed
            format: Audio format
            audio_data: Audio data to cache
        """
        # Always save to disk cache for persistence
        self.disk_cache.put(text, voice, speed, format, audio_data)
        
        # Add to LRU memory cache
        cache_key = f"{hash(text)}_{voice}_{speed}_{format}"
        self.lru_cache.put(cache_key, audio_data)
        
        # Add to hot cache if applicable
        if text.lower() in self.hot_cache.hot_cache_keys:
            hot_key = f"{text.lower()}_{voice}_{speed}_{format}"
            self.hot_cache.put(hot_key, audio_data)
    
    def clear_cache(self, tier: Optional[str] = None) -> None:
        """
        Clear cache for specific tier or all tiers.
        
        Args:
            tier: Cache tier to clear ('hot', 'disk', 'memory', or None for all)
        """
        if tier == "hot" or tier is None:
            self.hot_cache.clear()
        
        if tier == "disk" or tier is None:
            self.disk_cache.clear()
        
        if tier == "memory" or tier is None:
            self.lru_cache.clear()
    
    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Get statistics from all cache tiers"""
        hot_stats = self.hot_cache.stats()
        disk_stats = self.disk_cache.stats()
        lru_stats = self.lru_cache.stats()
        
        # Calculate totals
        total_stats = {
            "entries": hot_stats["entries"] + disk_stats["entries"] + lru_stats["size"],
            "memory_mb": hot_stats["memory_mb"] + lru_stats["memory_mb"],
            "disk_mb": disk_stats["size_mb"]
        }
        
        return {
            "hot_cache": hot_stats,
            "disk_cache": disk_stats,
            "memory_cache": lru_stats,
            "total": total_stats
        }
    
    def promote_to_hot_cache(self, text: str, voice: str = "af_bella") -> bool:
        """
        Manually promote a message to hot cache.
        
        Args:
            text: Text to promote
            voice: Voice to try (default voices will be attempted)
            
        Returns:
            True if promoted successfully, False otherwise
        """
        text_lower = text.lower()
        
        # Add to hot cache keys
        self.hot_cache.add_hot_key(text_lower)
        
        # Try to load from disk cache for common voices and formats
        for v in [voice, "af_bella", "af_nicole", "am_adam"]:
            for fmt in ["wav", "mp3"]:
                disk_cached = self.disk_cache.get(text, v, 1.0, fmt)
                if disk_cached:
                    hot_key = f"{text_lower}_{v}_1.0_{fmt}"
                    self.hot_cache.put(hot_key, disk_cached)
                    return True
        
        return False