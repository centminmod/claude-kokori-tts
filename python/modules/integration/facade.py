"""
Integration facade that provides the main entry point for the modular TTS system.

This module serves as the main entry point that replaces the original monolithic
implementation with the new modular architecture.
Layer 5 - Orchestration: Depends on Layers 1-4.
"""

import logging
from typing import Optional, List, Dict, Any

from modules.core.service import EnhancedKokoroFastAPIIntegration
from modules.cli.interface import TTSCLIInterface
from modules.types.constants import DEFAULT_PRELOAD_MESSAGES
from typing import Tuple

logger = logging.getLogger(__name__)


class ModularTTSFacade:
    """
    Main facade for the modular TTS system.
    
    This class provides the same interface as the original EnhancedKokoroFastAPIIntegration
    but uses the new modular architecture underneath.
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:8880",
        notification_mode: bool = False,
        quiet_mode: bool = False,
        preload: bool = True,
        max_cache_size: int = 100,
        max_cache_memory_mb: int = 100,
        max_disk_cache_gb: float = 1.0,
        hot_cache_messages: List[str] = None,
        skip_voice_check: bool = False
    ):
        """
        Initialize the modular TTS facade.

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
        # Initialize the core service
        self.service = EnhancedKokoroFastAPIIntegration(
            base_url=base_url,
            max_cache_size=max_cache_size,
            max_cache_memory_mb=max_cache_memory_mb,
            max_disk_cache_gb=max_disk_cache_gb,
            notification_mode=notification_mode,
            quiet_mode=quiet_mode,
            preload=preload,
            hot_cache_messages=hot_cache_messages or DEFAULT_PRELOAD_MESSAGES,
            skip_voice_check=skip_voice_check
        )
        
        # Initialize CLI interface
        self.cli = TTSCLIInterface(self.service)
        
        # Expose commonly used attributes for backward compatibility
        self.base_url = self.service.base_url
        self.notification_mode = self.service.notification_mode
        self.quiet_mode = self.service.quiet_mode
        self.preload_enabled = self.service.preload_enabled
    
    @property
    def available_voices(self) -> Dict[str, str]:
        """Expose available voices as property for CLI compatibility"""
        return self.service.tts_client.available_voices
    
    # Core TTS functionality
    def speak_text(
        self,
        text: str,
        voice: str = "af_bella",
        speed: float = 1.0,
        response_format: str = "wav",
        stream: bool = False,
        normalize: bool = True,
        background: bool = False,
        export_file: Optional[str] = None,
        export_dir: str = "."
    ) -> bool:
        """Convert text to speech and play audio (with CLI compatibility)"""
        try:
            # Handle export if requested
            if export_file is not None:
                # Use empty string as filename for auto-generation
                export_filename = export_file if export_file else None
                result = self.export_audio(
                    text=text,
                    filename=export_filename,
                    voice=voice,
                    speed=speed,
                    format_type=response_format,
                    export_dir=export_dir,
                    play_audio=not background
                )
                return result is not None
            else:
                # Just play the audio
                self.service.speak_text(
                    text=text,
                    voice=voice,
                    speed=speed,
                    format_type=response_format,
                    background=background,
                    stream=stream
                )
                return True
        except Exception as e:
            logger.exception("speak_text failed")
            return False
    
    def generate_speech(
        self,
        text: str,
        voice: str = "af_bella",
        speed: float = 1.0,
        response_format: str = "wav",
        stream: bool = False,
        normalize: bool = True,
        cache_only: bool = False
    ) -> Optional[bytes]:
        """Generate speech from text"""
        return self.service.tts_client.generate_speech(
            text, voice, speed, response_format, stream, normalize, cache_only
        )
    
    # Interactive mode
    def interactive_mode(self, voice: str = "af_bella", response_format: str = "wav") -> None:
        """Run interactive TTS mode with voice and format settings"""
        # Update interactive settings before starting
        self.cli.interactive_settings['voice'] = voice
        self.cli.interactive_settings['format'] = response_format
        return self.cli.interactive_mode()
    
    # Export functionality
    def export_audio(
        self,
        text: str,
        filename: Optional[str] = None,
        voice: str = "af_bella",
        speed: float = 1.0,
        format_type: str = "wav",
        export_dir: Optional[str] = None,
        play_audio: bool = True
    ) -> Optional[str]:
        """Export audio to file"""
        return self.service.export_manager.export_audio(
            text, filename, voice, speed, format_type, export_dir, play_audio
        )
    
    def generate_export_filename(
        self,
        text: str,
        voice: str,
        format_type: str,
        max_text_length: int = 50
    ) -> str:
        """Generate a filename for audio export"""
        return self.service.export_manager.generate_export_filename(
            text, voice, format_type, max_text_length
        )
    
    # Voice management
    def get_available_voices(self) -> Dict[str, Dict[str, Any]]:
        """Get available voices"""
        return self.service.tts_client.available_voices
    
    def discover_voices(self) -> Dict[str, Dict[str, Any]]:
        """Discover available voices from server"""
        voices = self.service.tts_client.discover_voices()
        # Convert VoiceInfo objects to dicts for backward compatibility
        return {vid: voice.model_dump() for vid, voice in voices.items()}
    
    def parse_voice_blend(self, voice: str):
        """Parse voice blend specification"""
        return self.service.tts_client.parse_voice_blend(voice)
    
    def create_voice_blend_file(self, voice_blend: str, target_voice: str) -> bool:
        """Create a voice blend file"""
        return self.service.tts_client.create_voice_blend_file(voice_blend, target_voice)
    
    def get_voice_phonemes(self, text: str, voice: str = "af_bella") -> Dict[str, Any]:
        """Get phoneme breakdown for text"""
        phoneme_response = self.service.tts_client.get_voice_phonemes(text, voice)
        # Convert PhonemeResponse to dict for backward compatibility
        return phoneme_response.model_dump()
    
    def get_phonemes(self, text: str, language: str = "a") -> Tuple[str, List[int]]:
        """Convert text to phonemes and tokens (CLI compatibility)"""
        # Use get_voice_phonemes with default voice and extract the needed data
        phoneme_response = self.service.tts_client.get_voice_phonemes(text, "af_bella")
        return phoneme_response.phonemes, phoneme_response.tokens
    
    # Server monitoring
    def get_server_debug_info(self):
        """Get comprehensive server debug information"""
        return self.service.get_server_debug_info()
    
    def get_server_health(self):
        """Get server health status"""
        return self.service.get_server_health()
    
    def format_server_stats(self, debug_info=None) -> str:
        """Format server debug information for display"""
        return self.service.format_server_stats(debug_info)
    
    def monitor_server_continuous(self, interval: int = 5, duration: int = 60) -> None:
        """Monitor server continuously"""
        return self.service.monitor_server_continuous(interval, duration)
    
    def test_connection_with_retry(self, max_retries: int = 3, timeout: float = 5.0) -> bool:
        """Test connection with retry logic"""
        return self.service.test_connection_with_retry(max_retries, timeout)
    
    # Cache management
    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        return self.service.get_cache_statistics()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Alias for get_cache_statistics() for CLI backward compatibility"""
        return self.get_cache_statistics()
    
    def clear_cache(self, tier: Optional[str] = None) -> None:
        """Clear cache for specific tier or all tiers"""
        return self.service.clear_cache(tier)
    
    def promote_to_hot_cache(self, text: str, voice: str = "af_bella") -> bool:
        """Promote a message to hot cache"""
        return self.service.promote_to_hot_cache(text, voice)
    
    # Compatibility methods for legacy code
    def _print(self, message: str, level: str = "info") -> None:
        """Print message respecting quiet mode"""
        return self.service._print(message, level)
    
    def play_audio(self, audio_bytes: bytes, format_type: str = "wav") -> None:
        """Play audio directly (for test mode)"""
        return self.service.audio_player.play_audio(audio_bytes, format_type)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics (alias for compatibility)"""
        cache_stats = self.get_cache_statistics()
        return {
            "cache": cache_stats.get("memory_cache", {})
        }
    
    # CLI command execution
    def run_single_command(
        self,
        text: str,
        voice: str = "af_bella",
        speed: float = 1.0,
        format_type: str = "wav",
        export: bool = False,
        export_filename: Optional[str] = None,
        export_dir: Optional[str] = None,
        background: bool = False,
        stream: bool = False,
        quiet: bool = False
    ) -> bool:
        """Run a single TTS command (non-interactive)"""
        return self.cli.run_single_command(
            text, voice, speed, format_type, export, export_filename,
            export_dir, background, stream, quiet
        )
    
    # Testing and diagnostic methods
    def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run comprehensive system tests"""
        results = {}
        
        try:
            # Test connection
            results['connection'] = self.test_connection_with_retry(max_retries=1, timeout=3)
            
            # Test voice discovery
            voices = self.discover_voices()
            results['voice_discovery'] = len(voices) > 0
            results['voice_count'] = len(voices)
            
            # Test basic TTS
            try:
                audio = self.generate_speech("Test", cache_only=True)
                results['basic_tts'] = audio is not None
            except:
                results['basic_tts'] = False
            
            # Test cache
            cache_stats = self.get_cache_statistics()
            results['cache_system'] = cache_stats is not None
            
            # Test server health
            is_healthy, health_summary = self.get_server_health()
            results['server_health'] = is_healthy
            results['health_summary'] = health_summary
            
        except Exception as e:
            results['error'] = str(e)
            logger.exception("Comprehensive test failed")
        
        return results
    
    def run_quick_tests(self) -> Dict[str, Any]:
        """Run quick system tests"""
        results = {}
        
        try:
            # Quick connection test
            results['connection'] = self.test_connection_with_retry(max_retries=1, timeout=1)
            
            # Quick voice check
            voices = self.get_available_voices()
            results['voices_available'] = len(voices) > 0
            
            # Quick cache check
            cache_stats = self.get_cache_statistics()
            results['cache_working'] = cache_stats is not None
            
            # Overall status
            results['system_ready'] = all([
                results['connection'],
                results['voices_available'],
                results['cache_working']
            ])
            
        except Exception as e:
            results['error'] = str(e)
            results['system_ready'] = False
        
        return results