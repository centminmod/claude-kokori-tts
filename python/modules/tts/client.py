"""
TTS client functionality for generating speech from text.

This module provides the core TTS client implementation with voice blending,
caching, and API communication capabilities.
Layer 4 - Business Logic: Depends on Layers 1-3.
"""

import time
import logging
from typing import Optional, List, Tuple, Dict, Any, TYPE_CHECKING

from modules.types.constants import (
    MAX_TEXT_LENGTH, MIN_GENERATED_AUDIO_SIZE, MS_PER_SECOND,
    SUPPORTED_FORMATS, VOICE_BLEND_SEPARATOR, VOICE_WEIGHT_PATTERN,
    OPUS_MIN_TEXT_LENGTH
)
from modules.types.protocols import TTSClientProtocol, ConnectionPoolProtocol, CacheProtocol
from modules.types.api_models import (
    ModelsResponse, PhonemeResponse, VoiceInfo, VoicesListResponse,
    parse_models_response, parse_phoneme_response, parse_error_response,
    parse_voices_list_response
)
from modules.utils.text_processing import validate_text_input, validate_voice_input

if TYPE_CHECKING:
    import requests

logger = logging.getLogger(__name__)


class TTSClient(TTSClientProtocol):
    """TTS client for generating speech from text with caching and voice blending"""
    
    def __init__(
        self,
        connection_pool: ConnectionPoolProtocol,
        cache_manager: CacheProtocol,
        notification_mode: bool = False,
        quiet_mode: bool = False
    ):
        """
        Initialize TTS client.
        
        Args:
            connection_pool: HTTP connection pool for API requests
            cache_manager: Cache manager for audio caching
            notification_mode: Optimize for notifications (shorter timeouts)
            quiet_mode: Suppress non-error output
        """
        self.conn_pool = connection_pool
        self.cache_manager = cache_manager
        self.notification_mode = notification_mode
        self.quiet_mode = quiet_mode
        
        # Voice caching
        self.voice_cache = {}
        self.combined_voices_cache = {}
        self.available_voices = {}
    
    def _print(self, message: str, level: str = "info") -> None:
        """Print message respecting quiet mode"""
        if self.quiet_mode and level != "error":
            return
        print(message)
    
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
        """
        Generate speech from text with comprehensive caching and validation.
        
        Args:
            text: Text to convert to speech
            voice: Voice ID or blend specification
            speed: Speech speed (0.5-2.0)
            response_format: Audio format
            stream: Enable streaming response
            normalize: Apply text normalization
            cache_only: Only generate if not cached (for preloading)
            
        Returns:
            Audio bytes, streaming response, or None if cache_only and not cached
            
        Raises:
            ValueError: If parameters are invalid
        """
        # Input validation
        validate_text_input(text, MAX_TEXT_LENGTH)
        validate_voice_input(voice)
        
        if not isinstance(speed, (int, float)) or not (0.5 <= speed <= 2.0):
            raise ValueError(f"Speed must be between 0.5 and 2.0, got {speed}. Use --speed option to set valid speed.")
        
        if response_format not in SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format '{response_format}'. Supported: {list(SUPPORTED_FORMATS.keys())}. Use --format option to set valid format.")

        # OPUS format fallback for short text (server produces empty audio for short OPUS)
        if response_format == "opus" and len(text) < OPUS_MIN_TEXT_LENGTH:
            response_format = "wav"
            if not self.quiet_mode:
                self._print(f"⚠️ Text too short for OPUS ({len(text)} chars), using WAV instead")

        # Timing for debug mode
        start_time = time.time() if logger.isEnabledFor(logging.DEBUG) else None
        
        # Check cache first
        cached_audio = self.cache_manager.get_audio(text, voice, speed, response_format)
        if cached_audio:
            if start_time:
                elapsed = (time.time() - start_time) * MS_PER_SECOND
                logger.debug(f"⏱️ Cache response time: {elapsed:.1f}ms")
            return cached_audio
        
        if cache_only:
            return None
        
        # Generate new audio
        try:
            if stream:
                return self._generate_speech_streaming(text, voice, speed, response_format, normalize)
            
            # Handle voice blending
            voice_blend = self.parse_voice_blend(voice)
            if len(voice_blend) > 1:
                voice_spec = '+'.join([f"{v}({w})" if w != 1.0 else v for v, w in voice_blend])
                if not self.quiet_mode:
                    self._print(f"🎤 Generating speech with voice blend: {voice_spec}")
            else:
                if not self.quiet_mode:
                    self._print(f"🎤 Generating speech with voice: {voice}")
            
            # Prepare payload
            payload = {
                "model": "kokoro",
                "input": text,
                "voice": voice,
                "speed": speed,
                "response_format": response_format
            }
            
            if not normalize:
                payload["normalization_options"] = {"normalize": False}
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer not-needed"
            }
            
            # Use shorter timeout for notifications
            timeout = 5 if self.notification_mode else 60
            
            response = self.conn_pool.post(
                "/v1/audio/speech",
                json=payload,
                headers=headers,
                timeout=timeout
            )
            
            if response.status_code == 200:
                audio_data = response.content
                
                # Validate audio data
                if len(audio_data) < MIN_GENERATED_AUDIO_SIZE:
                    raise Exception(f"Generated audio too small ({len(audio_data)} bytes)")
                
                # Cache the result
                self.cache_manager.put_audio(text, voice, speed, response_format, audio_data)
                
                if not self.quiet_mode:
                    self._print(f"✅ Generated {len(audio_data)} bytes of audio data")
                
                if start_time:
                    elapsed = (time.time() - start_time) * MS_PER_SECOND
                    logger.debug(f"⏱️ Generated audio response time: {elapsed:.1f}ms")
                
                return audio_data
            else:
                raise Exception(f"API returned status {response.status_code}: {response.text}")
                
        except Exception as e:
            logger.exception("TTS generation failed")
            raise RuntimeError(f"TTS generation failed: {e}") from e
    
    def _generate_speech_streaming(
        self,
        text: str,
        voice: str,
        speed: float,
        response_format: str,
        normalize: bool
    ) -> "requests.Response":
        """Generate streaming speech response"""
        payload = {
            "model": "kokoro",
            "input": text,
            "voice": voice,
            "speed": speed,
            "response_format": response_format
        }
        
        if not normalize:
            payload["normalization_options"] = {"normalize": False}
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer not-needed"
        }
        
        return self.conn_pool.post(
            "/v1/audio/speech",
            json=payload,
            headers=headers,
            stream=True,
            timeout=60
        )
    
    def parse_voice_blend(self, voice: str) -> List[Tuple[str, float]]:
        """
        Parse voice blend specification into voice and weight pairs.
        
        Args:
            voice: Voice blend specification (e.g., "af_bella+af_sky" or "af_bella(2)+af_sky(1)")
            
        Returns:
            List of (voice_id, weight) tuples
        """
        import re
        
        if VOICE_BLEND_SEPARATOR not in voice:
            return [(voice, 1.0)]
        
        voices = []
        total_weight = 0.0
        
        for part in voice.split(VOICE_BLEND_SEPARATOR):
            part = part.strip()
            
            # Check for weight specification
            weight_match = re.match(VOICE_WEIGHT_PATTERN, part)
            if weight_match:
                voice_id = weight_match.group(1)
                weight = float(weight_match.group(2))
            else:
                voice_id = part
                weight = 1.0
            
            voices.append((voice_id, weight))
            total_weight += weight
        
        # Normalize weights
        if total_weight > 0:
            voices = [(voice_id, weight / total_weight) for voice_id, weight in voices]
        
        return voices
    
    def get_voice_phonemes(self, text: str, voice: str = "af_bella") -> PhonemeResponse:
        """
        Get phoneme breakdown for text using specified voice.

        Args:
            text: Text to analyze
            voice: Voice to use for phoneme generation (used to determine language)

        Returns:
            PhonemeResponse containing phoneme information
        """
        try:
            # Extract language code from voice (e.g., 'af_bella' -> 'a' for American English)
            # Voice format is typically: {language_code}{gender}_{name}
            language = voice[0] if voice else "a"

            payload = {
                "text": text,
                "language": language
            }

            headers = {
                "Content-Type": "application/json"
            }

            response = self.conn_pool.post(
                "/dev/phonemize",
                json=payload,
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                return parse_phoneme_response(response.json())
            else:
                error_data = parse_error_response({"error": response.text, "status_code": response.status_code})
                raise Exception(f"Phonemes API returned status {response.status_code}: {error_data.error}")

        except Exception as e:
            logger.exception("Phoneme generation failed")
            raise RuntimeError(f"Phoneme generation failed: {e}") from e
    
    def discover_voices(self) -> Dict[str, VoiceInfo]:
        """
        Discover available voices from the server.

        Uses /v1/audio/voices endpoint which returns a list of voice IDs.

        Returns:
            Dictionary of voice ID to VoiceInfo objects
        """
        try:
            response = self.conn_pool.get("/v1/audio/voices", timeout=10)

            if response.status_code == 200:
                voices_response = parse_voices_list_response(response.json())
                voices = {}

                for voice_id in voices_response.voices:
                    # Create VoiceInfo from voice ID
                    # Voice ID format: {language}{gender}_{name}
                    # e.g., af_bella = American Female Bella
                    voice_info = self._create_voice_info_from_id(voice_id)
                    voices[voice_id] = voice_info

                # Store as dict for backward compatibility with self.available_voices
                self.available_voices = {vid: v.model_dump() for vid, v in voices.items()}
                return voices
            else:
                error_data = parse_error_response({"error": response.text, "status_code": response.status_code})
                raise Exception(f"Voices API returned status {response.status_code}: {error_data.error}")

        except Exception as e:
            logger.exception("Voice discovery failed")
            # Return empty dict on failure, don't raise
            return {}

    def _create_voice_info_from_id(self, voice_id: str) -> VoiceInfo:
        """
        Create VoiceInfo from a voice ID string.

        Voice ID format: {language_prefix}{gender}_{name}
        - af_ = American Female
        - am_ = American Male
        - bf_ = British Female
        - bm_ = British Male
        - ef_ = Spanish Female
        - ff_ = French Female
        - hf_ = Hindi Female
        - if_ = Italian Female
        - jf_ = Japanese Female
        - pf_ = Portuguese Female
        - zf_ = Chinese Female

        Args:
            voice_id: Voice identifier (e.g., 'af_bella')

        Returns:
            VoiceInfo object with parsed metadata
        """
        # Language/gender prefixes
        prefix_map = {
            'af': ('en-US', 'female', 'American'),
            'am': ('en-US', 'male', 'American'),
            'bf': ('en-GB', 'female', 'British'),
            'bm': ('en-GB', 'male', 'British'),
            'ef': ('es', 'female', 'Spanish'),
            'em': ('es', 'male', 'Spanish'),
            'ff': ('fr', 'female', 'French'),
            'fm': ('fr', 'male', 'French'),
            'hf': ('hi', 'female', 'Hindi'),
            'hm': ('hi', 'male', 'Hindi'),
            'if': ('it', 'female', 'Italian'),
            'im': ('it', 'male', 'Italian'),
            'jf': ('ja', 'female', 'Japanese'),
            'jm': ('ja', 'male', 'Japanese'),
            'pf': ('pt', 'female', 'Portuguese'),
            'pm': ('pt', 'male', 'Portuguese'),
            'zf': ('zh', 'female', 'Chinese'),
            'zm': ('zh', 'male', 'Chinese'),
        }

        # Parse voice ID
        prefix = voice_id[:2] if len(voice_id) >= 2 else ''
        name_part = voice_id[3:] if len(voice_id) > 3 and voice_id[2] == '_' else voice_id

        # Get language/gender info
        language, gender, region = prefix_map.get(prefix, ('unknown', 'unknown', 'Unknown'))

        # Create human-readable name
        name = name_part.replace('_', ' ').title()

        return VoiceInfo(
            id=voice_id,
            name=name,
            language=language,
            gender=gender,
            description=f"{region} {gender} voice"
        )
    
    def test_connection(self, timeout: float = 5.0) -> bool:
        """
        Test connection to TTS server.
        
        Args:
            timeout: Connection timeout in seconds
            
        Returns:
            True if connection successful, False otherwise
        """
        try:
            response = self.conn_pool.get("/health", timeout=timeout)
            return response.status_code == 200
        except:
            return False
    
    def create_voice_blend_file(self, voice_blend: str, target_voice: str) -> bool:
        """
        Create a voice blend file on the server.
        
        Args:
            voice_blend: Voice blend specification
            target_voice: Target voice name for the blend
            
        Returns:
            True if blend file created successfully, False otherwise
        """
        try:
            voice_pairs = self.parse_voice_blend(voice_blend)
            
            payload = {
                "voice_name": target_voice,
                "voice_blend": [{"voice": voice, "weight": weight} for voice, weight in voice_pairs]
            }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer not-needed"
            }
            
            response = self.conn_pool.post(
                "/v1/voices/blend",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                if not self.quiet_mode:
                    self._print(f"✅ Voice blend '{target_voice}' created successfully")
                return True
            else:
                if not self.quiet_mode:
                    self._print(f"❌ Failed to create voice blend: {response.text}")
                return False
                
        except Exception as e:
            logger.exception("Voice blend creation failed")
            if not self.quiet_mode:
                self._print(f"❌ Voice blend creation failed: {e}")
            return False