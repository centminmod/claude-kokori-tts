"""
Disk-based audio cache implementation for the TTS system.

This module provides persistent audio caching with metadata management.
Layer 3 - Storage & Processing: Depends on Layers 1-2.
"""

import json
import time
import threading
import hashlib
import logging
from pathlib import Path
from typing import Optional, Dict, Any

from modules.types.protocols import AudioCacheProtocol
from modules.types.constants import TEXT_PREVIEW_LENGTH
from modules.filesystem.file_utils import get_cache_directory, ensure_directory_exists
from modules.utils.text_processing import clean_filename_text, clean_voice_for_filename

logger = logging.getLogger(__name__)


class DiskCache(AudioCacheProtocol):
    """Disk-based audio cache for persistent storage"""
    
    def __init__(self, cache_dir: Optional[Path] = None, max_size_gb: float = 1.0):
        """
        Initialize disk cache
        
        Args:
            cache_dir: Directory for cache storage (default: ~/.claude_tts/cache/audio)
            max_size_gb: Maximum cache size in GB
        """
        self.cache_dir = cache_dir or get_cache_directory()
        ensure_directory_exists(self.cache_dir)
        self.metadata_file = self.cache_dir.parent / "metadata.json"
        self.max_size = max_size_gb * 1024 * 1024 * 1024  # Convert to bytes
        self.metadata: Dict[str, Dict[str, Any]] = self._load_metadata()
        self.lock = threading.Lock()
    
    def _get_cache_key(self, text: str, voice: str, speed: float, format: str) -> str:
        """Generate unique cache key"""
        content = f"{text}:{voice}:{speed}:{format}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str, voice: str, text_preview: str, format: str) -> Path:
        """Generate cache file path"""
        # Clean text preview for filename
        safe_text = clean_filename_text(text_preview, 30)
        voice_clean = clean_voice_for_filename(voice)
        filename = f"{voice_clean}_{cache_key[:8]}_{safe_text}.{format}"
        return self.cache_dir / filename
    
    def _load_metadata(self) -> Dict[str, Dict[str, Any]]:
        """Load cache metadata"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except (IOError, OSError, json.JSONDecodeError) as e:
                logger.exception("Failed to load cache metadata")
            except Exception as e:
                logger.exception("Unexpected error loading cache metadata")
        return {}
    
    def _save_metadata(self) -> None:
        """Save cache metadata"""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
        except (IOError, OSError) as e:
            logger.exception("Failed to save cache metadata")
        except Exception as e:
            logger.exception("Unexpected error saving cache metadata")
    
    def get(self, text: str, voice: str, speed: float, format: str) -> Optional[bytes]:
        """Get audio from disk cache"""
        cache_key = self._get_cache_key(text, voice, speed, format)
        
        with self.lock:
            if cache_key in self.metadata:
                file_path = Path(self.metadata[cache_key]['path'])
                if file_path.exists():
                    try:
                        # Update access time
                        self.metadata[cache_key]['last_access'] = time.time()
                        self.metadata[cache_key]['access_count'] += 1
                        self._save_metadata()
                        
                        # Read audio data
                        with open(file_path, 'rb') as f:
                            return f.read()
                    except (IOError, OSError) as e:
                        logger.exception(f"Failed to read cache file {file_path}")
                    except Exception as e:
                        logger.exception(f"Unexpected error reading cache file {file_path}")
                else:
                    # Clean up orphaned metadata
                    del self.metadata[cache_key]
                    self._save_metadata()
        
        return None
    
    def put(self, text: str, voice: str, speed: float, format: str, audio_data: bytes) -> bool:
        """Store audio in disk cache"""
        cache_key = self._get_cache_key(text, voice, speed, format)
        file_path = self._get_cache_path(cache_key, voice, text, format)
        
        with self.lock:
            try:
                # Check if cleanup needed
                self._cleanup_if_needed(len(audio_data))
                
                # Write audio file
                with open(file_path, 'wb') as f:
                    f.write(audio_data)
                
                # Update metadata
                self.metadata[cache_key] = {
                    'path': str(file_path),
                    'size': len(audio_data),
                    'created': time.time(),
                    'last_access': time.time(),
                    'access_count': 1,
                    'text': text[:TEXT_PREVIEW_LENGTH],  # Store preview
                    'voice': voice,
                    'format': format
                }
                self._save_metadata()
                return True
                
            except (IOError, OSError) as e:
                logger.exception(f"Failed to write cache file {file_path}")
                return False
            except Exception as e:
                logger.exception(f"Unexpected error writing cache file {file_path}")
                return False
    
    def _cleanup_if_needed(self, new_size: int) -> None:
        """Clean up old cache entries if needed"""
        total_size = sum(entry['size'] for entry in self.metadata.values())
        
        if total_size + new_size > self.max_size:
            # Sort by last access time (LRU)
            sorted_entries = sorted(
                self.metadata.items(),
                key=lambda x: x[1]['last_access']
            )
            
            # Remove oldest entries until we have space
            while sorted_entries and total_size + new_size > self.max_size:
                cache_key, entry = sorted_entries.pop(0)
                file_path = Path(entry['path'])
                
                try:
                    if file_path.exists():
                        file_path.unlink()
                    total_size -= entry['size']
                    del self.metadata[cache_key]
                except Exception as e:
                    logger.error(f"Failed to delete cache file {file_path}: {e}")
    
    def clear(self) -> None:
        """Clear entire disk cache"""
        with self.lock:
            for entry in self.metadata.values():
                file_path = Path(entry['path'])
                try:
                    if file_path.exists():
                        file_path.unlink()
                except Exception as e:
                    logger.error(f"Failed to delete cache file {file_path}: {e}")
            
            self.metadata.clear()
            self._save_metadata()
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            total_size = sum(entry['size'] for entry in self.metadata.values())
            return {
                'entries': len(self.metadata),
                'size_mb': total_size / (1024 * 1024),
                'max_size_gb': self.max_size / (1024 * 1024 * 1024),
                'usage_percent': (total_size / self.max_size) * 100 if self.max_size > 0 else 0
            }