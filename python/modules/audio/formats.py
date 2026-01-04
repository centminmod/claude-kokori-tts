"""
Audio format handling and validation for the TTS system.

This module provides audio format utilities and validation.
Layer 3 - Storage & Processing: Depends on Layers 1-2.
"""

from typing import Dict

from modules.types.constants import SUPPORTED_FORMATS


def get_supported_formats() -> Dict[str, str]:
    """
    Get dictionary of supported audio formats.
    
    Returns:
        Dictionary mapping format names to MIME types
    """
    return SUPPORTED_FORMATS.copy()


def is_format_supported(format_name: str) -> bool:
    """
    Check if an audio format is supported.
    
    Args:
        format_name: Format name to check
        
    Returns:
        True if format is supported, False otherwise
    """
    return format_name.lower() in SUPPORTED_FORMATS


def get_format_mime_type(format_name: str) -> str:
    """
    Get MIME type for an audio format.
    
    Args:
        format_name: Format name
        
    Returns:
        MIME type string, or 'audio/wav' as fallback
    """
    return SUPPORTED_FORMATS.get(format_name.lower(), "audio/wav")


def validate_audio_data(audio_data: bytes, min_size: int = 100) -> bool:
    """
    Validate audio data meets minimum requirements.
    
    Args:
        audio_data: Audio data to validate
        min_size: Minimum required size in bytes
        
    Returns:
        True if audio data is valid, False otherwise
    """
    if not audio_data:
        return False
    
    if len(audio_data) < min_size:
        return False
    
    return True


def detect_wav_header(audio_data: bytes) -> bool:
    """
    Detect if audio data has a WAV header.
    
    Args:
        audio_data: Audio data to check
        
    Returns:
        True if WAV header detected, False otherwise
    """
    if len(audio_data) < 4:
        return False
    
    return audio_data[:4] == b'RIFF'


def concatenate_wav_audio(audio_chunks: list[bytes]) -> bytes:
    """
    Concatenate multiple WAV audio chunks.
    
    For WAV files, we keep the first header and append just the audio data
    from subsequent chunks.
    
    Args:
        audio_chunks: List of WAV audio data chunks
        
    Returns:
        Concatenated audio data
    """
    if not audio_chunks:
        return b''
    
    if len(audio_chunks) == 1:
        return audio_chunks[0]
    
    # Start with first chunk (includes header)
    combined_audio = audio_chunks[0]
    
    # Append audio data from subsequent chunks (skip headers)
    for audio_chunk in audio_chunks[1:]:
        if detect_wav_header(audio_chunk) and len(audio_chunk) > 44:
            # Skip standard WAV header (44 bytes)
            combined_audio += audio_chunk[44:]
        else:
            # If no RIFF header found, append entire chunk (safer fallback)
            combined_audio += audio_chunk
    
    return combined_audio


def get_file_extension(format_name: str) -> str:
    """
    Get file extension for an audio format.
    
    Args:
        format_name: Format name
        
    Returns:
        File extension with dot (e.g., '.wav')
    """
    # Map format names to extensions
    extensions = {
        'wav': '.wav',
        'mp3': '.mp3',
        'pcm': '.pcm',
        'opus': '.opus',
        'flac': '.flac'
    }
    
    return extensions.get(format_name.lower(), '.wav')