"""
Audio export functionality for the TTS system.

This module handles exporting audio to files with auto-naming and format handling.
Layer 4 - Business Logic: Depends on Layers 1-3.
"""

import os
import time
import logging
from typing import Optional, List
from pathlib import Path

from modules.types.protocols import ExportManagerProtocol, TTSClientProtocol
from modules.types.constants import SUPPORTED_FORMATS, MAX_TEXT_LENGTH
from modules.types.exceptions import ExportError, PathTraversalError, InvalidPathError
from modules.filesystem.file_utils import ensure_directory_exists, get_safe_filename, validate_safe_path
from modules.audio.formats import get_file_extension, concatenate_wav_audio
from modules.utils.text_processing import clean_filename_text, split_text_for_tts

logger = logging.getLogger(__name__)


class ExportManager(ExportManagerProtocol):
    """Manager for exporting audio to files"""
    
    def __init__(
        self,
        tts_client: TTSClientProtocol,
        default_export_dir: str = "./exports",
        quiet_mode: bool = False
    ):
        """
        Initialize export manager.
        
        Args:
            tts_client: TTS client for generating audio
            default_export_dir: Default directory for exports
            quiet_mode: Suppress non-error output
        """
        self.tts_client = tts_client
        self.default_export_dir = Path(default_export_dir)
        self.quiet_mode = quiet_mode
        
        # Ensure default export directory exists
        ensure_directory_exists(self.default_export_dir)
    
    def _print(self, message: str, level: str = "info") -> None:
        """Print message respecting quiet mode"""
        if self.quiet_mode and level != "error":
            return
        print(message)
    
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
        """
        Export audio to file with optional playback.

        Args:
            text: Text to convert to speech
            filename: Custom filename or absolute path (auto-generated if None)
            voice: Voice to use
            speed: Speech speed
            format_type: Audio format
            export_dir: Export directory (uses default if None)
            play_audio: Also play the audio after export

        Returns:
            Path to exported file if successful, None otherwise
        """
        try:
            # Handle absolute paths in filename
            if filename and os.path.isabs(filename):
                # User provided absolute path - extract directory and filename
                target_dir = Path(os.path.dirname(filename))
                filename = os.path.basename(filename)
            else:
                # Determine export directory from parameter or default
                target_dir = Path(export_dir) if export_dir else self.default_export_dir

            ensure_directory_exists(target_dir)

            # Generate filename if not provided
            if filename is None:
                filename = self.generate_export_filename(text, voice, format_type)

            # Check if filename already has a supported audio extension
            file_ext = os.path.splitext(filename)[1].lower().lstrip('.')
            if file_ext in SUPPORTED_FORMATS:
                # User specified a supported format in filename - use it
                format_type = file_ext
            elif not filename.endswith(get_file_extension(format_type)):
                # Add extension if missing
                filename += get_file_extension(format_type)
            
            # Validate and create safe path
            try:
                safe_path = validate_safe_path(target_dir, filename)
                export_path = str(safe_path)
            except (PathTraversalError, InvalidPathError) as e:
                raise ExportError(f"Invalid export path: {e}")
            
            # Handle collision avoidance
            export_path = self._avoid_filename_collision(export_path)
            
            # Generate or retrieve audio
            if len(text) > MAX_TEXT_LENGTH:
                # Handle long text with chunking
                audio_data = self._export_chunked_text(text, voice, speed, format_type)
            else:
                audio_data = self.tts_client.generate_speech(
                    text=text,
                    voice=voice,
                    speed=speed,
                    response_format=format_type
                )
            
            if not audio_data:
                raise ValueError("Failed to generate audio data")
            
            # Write to file
            with open(export_path, 'wb') as f:
                f.write(audio_data)
            
            file_size_mb = len(audio_data) / (1024 * 1024)
            
            if not self.quiet_mode:
                self._print(f"💾 Exported {file_size_mb:.2f}MB to: {export_path}")
            
            return export_path
            
        except Exception as e:
            logger.exception("Audio export failed")
            if not self.quiet_mode:
                self._print(f"❌ Export failed: {e}", level="error")
            return None
    
    def _export_chunked_text(
        self,
        text: str,
        voice: str,
        speed: float,
        format_type: str
    ) -> bytes:
        """
        Export long text by chunking and concatenating audio.
        
        Args:
            text: Long text to export
            voice: Voice to use
            speed: Speech speed
            format_type: Audio format
            
        Returns:
            Concatenated audio data
        """
        chunks = split_text_for_tts(text, MAX_TEXT_LENGTH)
        audio_chunks = []
        
        if not self.quiet_mode:
            self._print(f"📝 Processing {len(chunks)} text chunks for export...")
        
        for i, chunk in enumerate(chunks, 1):
            if not self.quiet_mode:
                self._print(f"🔄 Processing chunk {i}/{len(chunks)}...")
            
            chunk_audio = self.tts_client.generate_speech(
                text=chunk,
                voice=voice,
                speed=speed,
                response_format=format_type
            )
            
            if chunk_audio:
                audio_chunks.append(chunk_audio)
            else:
                logger.warning(f"Failed to generate audio for chunk {i}")
        
        if not audio_chunks:
            raise ValueError("No audio chunks generated")
        
        # Concatenate audio chunks
        if format_type.lower() == "wav":
            combined_audio = concatenate_wav_audio(audio_chunks)
        else:
            # For non-WAV formats, simple concatenation
            combined_audio = b''.join(audio_chunks)
        
        return combined_audio
    
    def generate_export_filename(
        self,
        text: str,
        voice: str,
        format_type: str,
        max_text_length: int = 50
    ) -> str:
        """
        Generate a filename for audio export.
        
        Args:
            text: Text content
            voice: Voice used
            format_type: Audio format
            max_text_length: Maximum length of text in filename
            
        Returns:
            Generated filename
        """
        # Clean and truncate text for filename
        clean_text = clean_filename_text(text, max_text_length)
        
        # Create timestamp
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        
        # Extract voice name (handle blends)
        voice_part = voice.split('+')[0] if '+' in voice else voice
        voice_name = voice_part.replace('_', '-')
        
        # Combine parts
        filename = f"{timestamp}_{voice_name}_{clean_text}"
        
        # Add extension
        filename += get_file_extension(format_type)
        
        return filename
    
    def _avoid_filename_collision(self, filepath: str) -> str:
        """
        Avoid filename collisions by adding counter.
        
        Args:
            filepath: Original file path
            
        Returns:
            Non-colliding file path
        """
        if not os.path.exists(filepath):
            return filepath
        
        # Split path and extension
        base_path, ext = os.path.splitext(filepath)
        counter = 1
        
        # Try numbered variants
        while os.path.exists(f"{base_path}_{counter}{ext}"):
            counter += 1
        
        return f"{base_path}_{counter}{ext}"
    
    def export_batch(
        self,
        texts: List[str],
        voice: str = "af_bella",
        speed: float = 1.0,
        format_type: str = "wav",
        export_dir: Optional[str] = None
    ) -> List[str]:
        """
        Export multiple texts to audio files.
        
        Args:
            texts: List of texts to export
            voice: Voice to use
            speed: Speech speed
            format_type: Audio format
            export_dir: Export directory
            
        Returns:
            List of exported file paths
        """
        exported_files = []
        
        if not self.quiet_mode:
            self._print(f"📁 Batch exporting {len(texts)} texts...")
        
        for i, text in enumerate(texts, 1):
            if not self.quiet_mode:
                self._print(f"🔄 Exporting {i}/{len(texts)}...")
            
            exported_file = self.export_audio(
                text=text,
                voice=voice,
                speed=speed,
                format_type=format_type,
                export_dir=export_dir,
                play_audio=False  # Don't play during batch export
            )
            
            if exported_file:
                exported_files.append(exported_file)
        
        if not self.quiet_mode:
            self._print(f"✅ Batch export complete: {len(exported_files)} files exported")
        
        return exported_files
    
    def set_export_directory(self, export_dir: str) -> bool:
        """
        Set the default export directory.
        
        Args:
            export_dir: New export directory path
            
        Returns:
            True if directory set successfully, False otherwise
        """
        try:
            export_dir = Path(export_dir)
            ensure_directory_exists(export_dir)
            self.default_export_dir = export_dir
            
            if not self.quiet_mode:
                self._print(f"📁 Export directory set to: {export_dir}")
            
            return True
        except Exception as e:
            logger.exception("Failed to set export directory")
            if not self.quiet_mode:
                self._print(f"❌ Failed to set export directory: {e}", level="error")
            return False
    
    def get_export_info(self, filepath: str) -> dict:
        """
        Get information about an exported file.
        
        Args:
            filepath: Path to exported file
            
        Returns:
            Dictionary with file information
        """
        try:
            if not os.path.exists(filepath):
                return {"error": "File not found"}
            
            stat = os.stat(filepath)
            
            return {
                "path": filepath,
                "size_bytes": stat.st_size,
                "size_mb": stat.st_size / (1024 * 1024),
                "created": time.ctime(stat.st_ctime),
                "modified": time.ctime(stat.st_mtime),
                "format": os.path.splitext(filepath)[1][1:].lower()
            }
        except Exception as e:
            return {"error": str(e)}