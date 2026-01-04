"""
Audio playback functionality for the TTS system.

This module handles audio playback using pygame with proper temp file management.
Layer 4 - Business Logic: Depends on Layers 1-3.
"""

import os
import time
import threading
import logging
from typing import Set, Optional, TYPE_CHECKING

from modules.types.protocols import AudioPlayerProtocol
from modules.types.constants import MIN_AUDIO_SIZE, SUPPORTED_FORMATS, STREAM_CHUNK_SIZE
from modules.filesystem.file_utils import create_temp_audio_file

if TYPE_CHECKING:
    import requests
    import pygame

# Optional imports with fallbacks
try:
    import pygame
    HAS_PYGAME = True
except ImportError:
    HAS_PYGAME = False

try:
    import pyaudio
    HAS_PYAUDIO = True
except ImportError:
    HAS_PYAUDIO = False

logger = logging.getLogger(__name__)


class AudioPlayer(AudioPlayerProtocol):
    """Audio player using pygame with temp file management"""
    
    def __init__(
        self,
        notification_mode: bool = False,
        quiet_mode: bool = False,
        temp_files: Optional[Set[str]] = None
    ):
        """
        Initialize audio player.
        
        Args:
            notification_mode: Optimize for notifications (non-blocking)
            quiet_mode: Suppress non-error output
            temp_files: Set to track temporary files for cleanup
        """
        self.notification_mode = notification_mode
        self.quiet_mode = quiet_mode
        self.temp_files = temp_files or set()
        self.temp_files_lock = threading.Lock()
        
        # Initialize pygame if available
        self.pygame_ready = False
        if HAS_PYGAME:
            self._init_pygame()
        
        # Initialize PyAudio if available
        self.pyaudio_instance = None
        if HAS_PYAUDIO:
            self._init_pyaudio()
    
    def _init_pygame(self) -> None:
        """Initialize pygame mixer"""
        try:
            buffer_size = 512 if self.notification_mode else 1024
            pygame.mixer.pre_init(
                frequency=24000,
                size=-16,
                channels=1,
                buffer=buffer_size
            )
            pygame.mixer.init()
            self.pygame_ready = True
            
            if not self.quiet_mode:
                self._print("✅ Pygame audio system initialized")
        except Exception as e:
            logger.exception("Pygame audio initialization failed")
            try:
                pygame.mixer.init()  # Fallback initialization
                self.pygame_ready = True
            except:
                self.pygame_ready = False
    
    def _init_pyaudio(self) -> None:
        """Initialize PyAudio for streaming"""
        try:
            self.pyaudio_instance = pyaudio.PyAudio()
            if not self.quiet_mode:
                self._print("✅ PyAudio streaming support enabled")
        except Exception as e:
            logger.warning(f"PyAudio initialization failed: {e}")
            self.pyaudio_instance = None
    
    def _print(self, message: str, level: str = "info") -> None:
        """Print message respecting quiet mode"""
        if self.quiet_mode and level != "error":
            return
        print(message)
    
    def _cleanup_temp_file(self, temp_path: str) -> None:
        """Clean up a specific temporary file"""
        try:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                logger.debug(f"Cleaned up temp file: {temp_path}")
            
            # Remove from tracking
            with self.temp_files_lock:
                self.temp_files.discard(temp_path)
                
        except (OSError, IOError) as e:
            logger.debug(f"Failed to cleanup temp file {temp_path}: {e}")
        except Exception as e:
            logger.warning(f"Unexpected error during temp file cleanup: {e}")
    
    def play_audio(self, audio_bytes: bytes, format_type: str = "wav") -> None:
        """Play audio with format detection and optimizations"""
        if not self.pygame_ready:
            logger.error("Pygame not available for audio playback")
            return
        
        try:
            if not self.quiet_mode:
                self._print(f"🔊 Playing {format_type.upper()} audio...")
            
            # Validate audio data
            if not audio_bytes or len(audio_bytes) < MIN_AUDIO_SIZE:
                raise ValueError(f"Audio data too small: {len(audio_bytes) if audio_bytes else 0} bytes")
            
            # Create temporary file
            file_ext = format_type if format_type in SUPPORTED_FORMATS else "wav"
            temp_path = create_temp_audio_file(audio_bytes, file_ext)
            
            # Track temp file for cleanup
            with self.temp_files_lock:
                self.temp_files.add(temp_path)
            
            # Load audio file
            try:
                pygame.mixer.music.load(temp_path)
            except pygame.error as e:
                # ModPlug_Load errors are harmless - pygame tries multiple decoders
                # Only log at debug level to avoid confusing users
                logger.debug(f"Pygame format fallback (harmless): {e}")
                # Clean up temp file immediately on error
                self._cleanup_temp_file(temp_path)
                return
            
            # Play audio
            pygame.mixer.music.play()

            # Wait for playback to complete
            while pygame.mixer.music.get_busy():
                pygame.time.wait(50)

            if not self.quiet_mode:
                self._print("✅ Audio playback complete!")

            # Clean up temp file after playback completes
            self._cleanup_temp_file(temp_path)
                    
        except pygame.error as e:
            logger.exception("Pygame audio playback failed")
            if not self.quiet_mode and not self.notification_mode:
                self._print(f"❌ Audio playback failed: {str(e)}", level="error")
        except Exception as e:
            logger.exception("Unexpected error during audio playback")
            if not self.quiet_mode and not self.notification_mode:
                self._print(f"❌ Audio playback failed: {str(e)}", level="error")
    
    def play_streaming_audio(self, response: "requests.Response") -> None:
        """Play streaming audio using PyAudio if available"""
        if not self.pyaudio_instance:
            # Fallback to buffered playback
            audio_data = b""
            for chunk in response.iter_content(chunk_size=STREAM_CHUNK_SIZE):
                if chunk:
                    audio_data += chunk
            self.play_audio(audio_data, "pcm")
            return
        
        try:
            if not self.quiet_mode:
                self._print("🔊 Streaming audio playback...")
            
            stream = self.pyaudio_instance.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=24000,
                output=True
            )
            
            try:
                for chunk in response.iter_content(chunk_size=STREAM_CHUNK_SIZE):
                    if chunk:
                        stream.write(chunk)
                
                if not self.quiet_mode:
                    self._print("✅ Streaming playback complete!")
            finally:
                stream.stop_stream()
                stream.close()
                
        except (ImportError, AttributeError) as e:
            logger.warning(f"PyAudio streaming not available: {e}")
            # Fallback to buffered playback
            self._fallback_buffered_playback(response)
        except Exception as e:
            logger.exception("Streaming playback failed")
            # Fallback to buffered playback
            self._fallback_buffered_playback(response)
    
    def _fallback_buffered_playback(self, response: "requests.Response") -> None:
        """Fallback to buffered playback when streaming fails"""
        audio_data = b""
        for chunk in response.iter_content(chunk_size=STREAM_CHUNK_SIZE):
            if chunk:
                audio_data += chunk
        self.play_audio(audio_data, "pcm")
    
    def cleanup(self) -> None:
        """Cleanup resources on shutdown"""
        # Cleanup PyAudio
        if self.pyaudio_instance:
            try:
                self.pyaudio_instance.terminate()
            except Exception as e:
                logger.debug(f"Error terminating PyAudio: {e}")
        
        # Cleanup pygame
        if self.pygame_ready:
            try:
                pygame.mixer.quit()
            except Exception as e:
                logger.debug(f"Error quitting pygame mixer: {e}")
        
        # Cleanup tracked temp files
        with self.temp_files_lock:
            temp_files_copy = self.temp_files.copy()
            for temp_file in temp_files_copy:
                try:
                    if os.path.exists(temp_file):
                        os.unlink(temp_file)
                except (OSError, IOError):
                    pass  # Ignore errors during cleanup
                except Exception:
                    pass  # Ignore unexpected errors
            
            self.temp_files.clear()