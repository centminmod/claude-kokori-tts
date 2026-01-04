"""
Core TTS service that orchestrates all components.

This module provides the main TTS service that coordinates all other modules.
Layer 5 - Orchestration: Depends on Layers 1-4.
"""

import atexit
import threading
import time
import logging
from typing import Dict, List, Tuple, Set, Optional, Any
from pathlib import Path

from modules.types.data_models import PreloadMessage, ServerDebugInfo
from modules.types.constants import DEFAULT_PRELOAD_MESSAGES
from modules.config.loader import ConfigurationLoader
from modules.http.connection_pool import ConnectionPool
from modules.cache.manager import CacheManager
from modules.audio.player import AudioPlayer
from modules.tts.client import TTSClient
from modules.export.manager import ExportManager
from modules.monitoring.health import ServerHealthMonitor
from modules.utils.text_processing import split_text_for_tts, validate_text_input

logger = logging.getLogger(__name__)


class EnhancedKokoroFastAPIIntegration:
    """Main TTS service that orchestrates all components"""
    
    def __init__(
        self,
        base_url: str = "http://localhost:8880",
        max_cache_size: int = 100,
        max_cache_memory_mb: int = 100,
        max_disk_cache_gb: float = 1.0,
        notification_mode: bool = False,
        quiet_mode: bool = False,
        preload: bool = True,
        hot_cache_messages: List[str] = None,
        skip_voice_check: bool = False
    ):
        """
        Initialize the enhanced TTS integration service.

        Args:
            base_url: Base URL for Kokoro-FastAPI server
            max_cache_size: Maximum items in LRU cache
            max_cache_memory_mb: Maximum LRU cache memory in MB
            max_disk_cache_gb: Maximum disk cache size in GB
            notification_mode: Optimize for notifications (shorter timeouts)
            quiet_mode: Suppress non-error output
            preload: Enable message preloading
            hot_cache_messages: Messages to keep in hot memory cache
            skip_voice_check: Skip voice discovery for faster startup (use with known voices)
        """
        self.base_url = base_url.rstrip('/')
        self.notification_mode = notification_mode
        self.quiet_mode = quiet_mode
        self.preload_enabled = preload
        self.skip_voice_check = skip_voice_check
        
        # Thread safety
        self._state_lock = threading.Lock()
        
        # Initialize configuration loader
        self.config_loader = ConfigurationLoader()
        
        # Load hot cache messages
        if hot_cache_messages is None:
            hot_cache_messages = DEFAULT_PRELOAD_MESSAGES
        
        hot_cache_keys = set(msg.lower() for msg in hot_cache_messages)
        
        # Initialize connection pool
        self.conn_pool = ConnectionPool(base_url)
        
        # Initialize cache manager
        self.cache_manager = CacheManager(
            max_cache_size=max_cache_size,
            max_cache_memory_mb=max_cache_memory_mb,
            max_disk_cache_gb=max_disk_cache_gb,
            hot_cache_keys=hot_cache_keys
        )
        
        # Initialize TTS client
        self.tts_client = TTSClient(
            connection_pool=self.conn_pool,
            cache_manager=self.cache_manager,
            notification_mode=notification_mode,
            quiet_mode=quiet_mode
        )
        
        # Temp file tracking for cleanup
        self.temp_files: Set[str] = set()
        
        # Initialize audio player
        self.audio_player = AudioPlayer(
            notification_mode=notification_mode,
            quiet_mode=quiet_mode,
            temp_files=self.temp_files
        )
        
        # Initialize export manager
        self.export_manager = ExportManager(
            tts_client=self.tts_client,
            quiet_mode=quiet_mode
        )
        
        # Initialize server health monitor
        self.health_monitor = ServerHealthMonitor(self.conn_pool)
        
        # Preloaded messages
        self.preloaded_messages: Dict[str, PreloadMessage] = {}
        
        # Background worker
        self.background_executor = None
        self.task_queue: List[Tuple[str, Dict[str, Any]]] = []
        self.queue_lock = threading.Lock()
        self.shutdown = False
        
        # Register cleanup
        atexit.register(self._cleanup)
        
        # Initialize and test connection
        self._initialize_service()
    
    def _print(self, message: str, level: str = "info") -> None:
        """Print message respecting quiet mode"""
        if self.quiet_mode and level != "error":
            return
        print(message)
    
    def _initialize_service(self) -> None:
        """Initialize the service and test connections"""
        # Test connection with appropriate timeout
        timeout = 1 if self.notification_mode else 3
        max_retries = 2 if self.notification_mode else 3
        
        if not self.test_connection_with_retry(max_retries=max_retries, timeout=timeout):
            if not self.notification_mode:
                self._print("❌ Failed to connect to Kokoro-FastAPI server")
                self._print("💡 Troubleshooting:")
                self._print("   1. Ensure Docker Desktop is running")
                self._print("   2. Check VirtioFS is enabled in Docker settings")
                self._print("   3. Verify sufficient resources (4GB RAM, 2 CPU cores)")
                self._print("   4. Run: docker run -p 8880:8880 ghcr.io/remsky/kokoro-fastapi-cpu:latest")
                raise ConnectionError("Kokoro-FastAPI server not available")
            else:
                logger.warning("Kokoro-FastAPI server not available")
                return
        
        # Discover voices if not skipped (skip for faster hook performance)
        if not self.skip_voice_check:
            self.tts_client.discover_voices()

        if self.preload_enabled:
            self._load_preload_messages()
            self._pregenerate_messages()
        
        # Start background worker
        self.background_executor = threading.Thread(target=self._background_worker, daemon=True)
        self.background_executor.start()
    
    def test_connection_with_retry(self, max_retries: int = 3, timeout: float = 5.0) -> bool:
        """Test connection with retry logic"""
        for attempt in range(max_retries):
            if self.tts_client.test_connection(timeout=timeout):
                return True
            
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                if not self.quiet_mode:
                    self._print(f"⏳ Connection attempt {attempt + 1} failed, retrying in {wait_time}s...")
                time.sleep(wait_time)
        
        return False
    
    def _load_preload_messages(self) -> None:
        """Load preload messages from configuration"""
        try:
            messages = self.config_loader.load_preload_messages()
            
            with self._state_lock:
                for msg_text in messages:
                    self.preloaded_messages[msg_text.lower()] = PreloadMessage(
                        text=msg_text,
                        voice="af_bella",
                        speed=1.0,
                        format_type="wav",
                        generated_at=None,
                        audio_data=None
                    )
            
            if not self.quiet_mode:
                self._print(f"📋 Loaded {len(messages)} preload messages")
                
        except Exception as e:
            logger.warning(f"Failed to load preload messages: {e}")
    
    def _pregenerate_messages(self) -> None:
        """Pre-generate audio for common messages"""
        if not self.preloaded_messages:
            return
        
        if not self.quiet_mode:
            self._print("🔥 Pre-generating hot cache messages...")
        
        for message in self.preloaded_messages.values():
            try:
                # Check if already in disk cache
                cached_audio = self.cache_manager.get_audio(
                    message.text, message.voice, message.speed, message.format_type
                )
                
                if cached_audio:
                    if not self.quiet_mode:
                        self._print(f"🔥 Hot cached: {message.text}")
                    # Promote to hot cache
                    self.cache_manager.promote_to_hot_cache(message.text, message.voice)
                else:
                    if not self.quiet_mode:
                        self._print(f"✅ Pre-generated: {message.text}")
                    # Generate and cache
                    self.tts_client.generate_speech(
                        text=message.text,
                        voice=message.voice,
                        speed=message.speed,
                        response_format=message.format_type
                    )
                    
            except Exception as e:
                logger.warning(f"Failed to pregenerate '{message.text}': {e}")
    
    def speak_text(
        self,
        text: str,
        voice: str = "af_bella",
        speed: float = 1.0,
        format_type: str = "wav",
        background: bool = False,
        stream: bool = False
    ) -> None:
        """
        Convert text to speech and play audio.
        
        Args:
            text: Text to speak
            voice: Voice to use
            speed: Speech speed
            format_type: Audio format
            background: Play in background (non-blocking)
            stream: Use streaming playback
        """
        start_time = time.time() if logger.isEnabledFor(logging.DEBUG) else None
        
        try:
            # Validate input
            validate_text_input(text)
            
            # Handle long text with chunking
            if len(text) > 500:  # Chunk threshold
                self._speak_chunked_text(text, voice, speed, format_type, background, stream)
                return
            
            # Generate or get cached audio
            if stream:
                response = self.tts_client.generate_speech(
                    text=text,
                    voice=voice,
                    speed=speed,
                    response_format=format_type,
                    stream=True
                )
                self.audio_player.play_streaming_audio(response)
            else:
                audio_data = self.tts_client.generate_speech(
                    text=text,
                    voice=voice,
                    speed=speed,
                    response_format=format_type
                )
                
                if audio_data:
                    if background:
                        # Play in background thread
                        threading.Thread(
                            target=self.audio_player.play_audio,
                            args=(audio_data, format_type),
                            daemon=True
                        ).start()
                    else:
                        self.audio_player.play_audio(audio_data, format_type)
            
            # Log timing
            if start_time:
                elapsed = (time.time() - start_time) * 1000
                logger.debug(f"⏱️ Total speak_text execution time: {elapsed:.1f}ms")
                
        except Exception as e:
            logger.exception("Text-to-speech failed")
            if not self.quiet_mode:
                self._print(f"❌ Text-to-speech failed: {e}", level="error")
    
    def _speak_chunked_text(
        self,
        text: str,
        voice: str,
        speed: float,
        format_type: str,
        background: bool,
        stream: bool
    ) -> None:
        """Handle speaking of long text by chunking"""
        chunks = split_text_for_tts(text, 300)  # 300 char chunks
        
        if not self.quiet_mode:
            self._print(f"📝 Speaking {len(chunks)} text chunks...")
        
        for i, chunk in enumerate(chunks, 1):
            if not self.quiet_mode:
                self._print(f"🔊 Speaking chunk {i}/{len(chunks)}...")
            
            self.speak_text(
                text=chunk,
                voice=voice,
                speed=speed,
                format_type=format_type,
                background=background and (i == len(chunks)),  # Only last chunk in background
                stream=stream
            )
    
    def get_server_debug_info(self) -> ServerDebugInfo:
        """Get comprehensive server debug information"""
        return self.health_monitor.get_server_debug_info()
    
    def get_server_health(self) -> Tuple[bool, str]:
        """Get server health status"""
        return self.health_monitor.get_server_health()
    
    def format_server_stats(self, debug_info: ServerDebugInfo = None) -> str:
        """Format server debug information for display"""
        if debug_info is None:
            debug_info = self.get_server_debug_info()
        return self.health_monitor.format_server_stats(debug_info)
    
    def monitor_server_continuous(self, interval: int = 5, duration: int = 60) -> None:
        """Monitor server continuously"""
        self.health_monitor.monitor_server_continuous(interval, duration, self.quiet_mode)
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        return self.cache_manager.get_comprehensive_stats()
    
    def clear_cache(self, tier: Optional[str] = None) -> None:
        """Clear cache for specific tier or all tiers"""
        self.cache_manager.clear_cache(tier)
        if not self.quiet_mode:
            tier_msg = f" {tier}" if tier else ""
            self._print(f"🗑️ Cleared{tier_msg} cache")
    
    def promote_to_hot_cache(self, text: str, voice: str = "af_bella") -> bool:
        """Promote a message to hot cache"""
        result = self.cache_manager.promote_to_hot_cache(text, voice)
        if result and not self.quiet_mode:
            self._print(f"⬆️ Promoted to hot cache: {text}")
        return result
    
    def _background_worker(self) -> None:
        """Background worker for async tasks"""
        while not self.shutdown:
            try:
                with self.queue_lock:
                    if self.task_queue:
                        task_type, task_data = self.task_queue.pop(0)
                    else:
                        task_type = task_data = None
                
                if task_type == "preload":
                    # Handle preload tasks
                    text = task_data.get("text")
                    voice = task_data.get("voice", "af_bella")
                    self.tts_client.generate_speech(text=text, voice=voice, cache_only=True)
                
                time.sleep(0.1)  # Prevent busy waiting
                
            except Exception as e:
                logger.exception("Background worker error")
    
    def _cleanup(self) -> None:
        """Cleanup resources on shutdown"""
        self.shutdown = True
        
        # Cleanup audio player
        if hasattr(self, 'audio_player'):
            self.audio_player.cleanup()
        
        # Wait for background worker to finish
        if self.background_executor and self.background_executor.is_alive():
            self.background_executor.join(timeout=1.0)
        
        logger.info("TTS service cleanup completed")