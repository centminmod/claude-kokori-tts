"""
Protocol definitions and interfaces for the TTS system.

This module defines abstract interfaces that higher layers can implement,
preventing circular dependencies by establishing contracts in the foundation layer.
Layer 1 - Foundation: No dependencies on other modules.
"""

from typing import Protocol, Optional, Dict, Any, List, Tuple, Union, TYPE_CHECKING

if TYPE_CHECKING:
    import requests


class CacheProtocol(Protocol):
    """Protocol for cache implementations"""
    
    def get(self, key: str) -> Optional[bytes]:
        """Get item from cache by key"""
        ...
    
    def put(self, key: str, value: bytes) -> None:
        """Put item in cache with key"""
        ...
    
    def clear(self) -> None:
        """Clear all cache entries"""
        ...
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        ...


class AudioCacheProtocol(Protocol):
    """Protocol for audio-specific cache implementations"""
    
    def get(self, text: str, voice: str, speed: float, format: str) -> Optional[bytes]:
        """Get audio from cache with audio-specific parameters"""
        ...
    
    def put(self, text: str, voice: str, speed: float, format: str, audio_data: bytes) -> bool:
        """Store audio in cache with audio-specific parameters"""
        ...
    
    def clear(self) -> None:
        """Clear entire cache"""
        ...
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        ...


class AudioPlayerProtocol(Protocol):
    """Protocol for audio playback implementations"""
    
    def play_audio(self, audio_bytes: bytes, format_type: str = "wav") -> None:
        """Play audio from bytes"""
        ...
    
    def play_streaming_audio(self, response: "requests.Response") -> None:
        """Play streaming audio from HTTP response"""
        ...


class TTSClientProtocol(Protocol):
    """Protocol for TTS client implementations"""
    
    def generate_speech(
        self,
        text: str,
        voice: str = "af_bella",
        speed: float = 1.0,
        response_format: str = "wav",
        stream: bool = False,
        normalize: bool = True
    ) -> Union[bytes, "requests.Response", None]:
        """Generate speech from text"""
        ...
    
    def get_phonemes(self, text: str, language: str = "a") -> Tuple[str, List[int]]:
        """Convert text to phonemes and tokens"""
        ...


class ConnectionPoolProtocol(Protocol):
    """Protocol for HTTP connection pool implementations"""
    
    def get(self, endpoint: str, **kwargs) -> "requests.Response":
        """GET request with connection pooling"""
        ...
    
    def post(self, endpoint: str, **kwargs) -> "requests.Response":
        """POST request with connection pooling"""
        ...
    
    def close(self) -> None:
        """Close all connections"""
        ...


class ConfigurationProtocol(Protocol):
    """Protocol for configuration loading implementations"""
    
    def load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load configuration from file or environment"""
        ...
    
    def get_preload_messages(self) -> List[Any]:
        """Get preload messages configuration"""
        ...


class VoiceManagerProtocol(Protocol):
    """Protocol for voice management implementations"""
    
    def get_available_voices(self) -> Dict[str, str]:
        """Get available voices from server or fallback"""
        ...
    
    def parse_voice_blend(self, voice_spec: str) -> List[Tuple[str, float]]:
        """Parse voice blending specification"""
        ...
    
    def validate_voice(self, voice: str) -> bool:
        """Validate if voice specification is valid"""
        ...


class ExportManagerProtocol(Protocol):
    """Protocol for audio export implementations"""
    
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
        ...
    
    def generate_export_filename(
        self,
        text: str,
        voice: str,
        format_type: str,
        max_text_length: int = 50
    ) -> str:
        """Generate a filename for audio export"""
        ...


class ExportProtocol(Protocol):
    """Protocol for audio export implementations"""
    
    def export_audio(
        self,
        audio_data: bytes,
        text: str,
        voice: str,
        format: str,
        custom_filename: Optional[str] = None,
        export_dir: str = "."
    ) -> str:
        """Export audio data to file"""
        ...
    
    def generate_export_filename(
        self,
        text: str,
        voice: str,
        format: str,
        custom_filename: Optional[str] = None,
        export_dir: str = "."
    ) -> str:
        """Generate filename for exported audio"""
        ...


class ServerMonitorProtocol(Protocol):
    """Protocol for server monitoring implementations"""
    
    def get_server_health(self) -> Tuple[bool, str]:
        """Get server health status"""
        ...
    
    def get_server_debug_info(self) -> Any:
        """Get comprehensive server debug information"""
        ...
    
    def format_server_stats(self, debug_info: Any) -> str:
        """Format server debug information for display"""
        ...


class TextProcessorProtocol(Protocol):
    """Protocol for text processing implementations"""
    
    def split_text_for_tts(self, text: str, max_length: int) -> List[str]:
        """Split text into optimal chunks for TTS"""
        ...
    
    def validate_text(self, text: str) -> bool:
        """Validate text for TTS processing"""
        ...
    
    def normalize_text(self, text: str) -> str:
        """Normalize text for TTS processing"""
        ...