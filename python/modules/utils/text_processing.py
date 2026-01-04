"""
Text processing utilities for the TTS system.

This module contains utility functions for text validation, processing, and chunking.
Layer 1 - Foundation: No dependencies on other modules.
"""

import re
from typing import List, Set


def validate_text_input(text: str, max_length: int = 10000) -> None:
    """
    Validate text input for TTS processing.
    
    Args:
        text: Text to validate
        max_length: Maximum allowed text length
        
    Raises:
        ValueError: If text is invalid
    """
    if not isinstance(text, str):
        raise ValueError(f"Text must be a string, got {type(text).__name__}")
    
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")
    
    if len(text) > max_length:
        raise ValueError(
            f"Text too long: {len(text)} characters (max {max_length}). "
            "Consider using chunking for long text."
        )


def validate_voice_input(voice: str) -> None:
    """
    Validate voice input.
    
    Args:
        voice: Voice specification to validate
        
    Raises:
        ValueError: If voice is invalid
    """
    if not isinstance(voice, str) or not voice.strip():
        raise ValueError(
            "Voice must be a non-empty string. Use --list-voices to see available options."
        )


def validate_speed_input(speed: float) -> None:
    """
    Validate speed input.
    
    Args:
        speed: Speech speed to validate
        
    Raises:
        ValueError: If speed is invalid
    """
    if not isinstance(speed, (int, float)) or not (0.5 <= speed <= 2.0):
        raise ValueError(
            f"Speed must be between 0.5 and 2.0, got {speed}. "
            "Use --speed option to set valid speed."
        )


def validate_format_input(response_format: str, supported_formats: Set[str] = None) -> None:
    """
    Validate audio format input.
    
    Args:
        response_format: Audio format to validate
        supported_formats: Set of supported formats (default: wav, mp3, pcm, opus, flac)
        
    Raises:
        ValueError: If format is invalid
    """
    if supported_formats is None:
        supported_formats = {"wav", "mp3", "pcm", "opus", "flac"}
    
    if response_format not in supported_formats:
        raise ValueError(
            f"Unsupported format '{response_format}'. "
            f"Supported: {list(supported_formats)}. "
            "Use --format option to set valid format."
        )


def validate_export_inputs(export_file: str = None, export_dir: str = None) -> None:
    """
    Validate export-related inputs.
    
    Args:
        export_file: Export filename to validate
        export_dir: Export directory to validate
        
    Raises:
        ValueError: If inputs are invalid
    """
    if export_dir and not isinstance(export_dir, str):
        raise ValueError("Export directory must be a string")
    
    if export_file is not None and not isinstance(export_file, str):
        raise ValueError("Export filename must be a string or None")


def split_text_for_tts(text: str, max_length: int = 300) -> List[str]:
    """
    Split text into optimal chunks for TTS processing.
    
    Args:
        text: Text to split
        max_length: Maximum length per chunk (default: 300)
        
    Returns:
        List of text chunks
    """
        
    if len(text) <= max_length:
        return [text]
    
    # Smart sentence splitting
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= max_length:
            current_chunk += " " + sentence if current_chunk else sentence
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = sentence
    
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks


def clean_filename_text(text: str, max_length: int = 30) -> str:
    """
    Clean text for use in filenames.
    
    Args:
        text: Text to clean
        max_length: Maximum length of cleaned text
        
    Returns:
        Cleaned text suitable for filenames
    """
    # Remove non-alphanumeric characters except spaces and hyphens
    safe_text = re.sub(r'[^\w\s-]', '', text)[:max_length].strip()
    # Replace spaces and multiple hyphens with single underscores
    safe_text = re.sub(r'[-\s]+', '_', safe_text)
    return safe_text


def clean_voice_for_filename(voice: str) -> str:
    """
    Clean voice specification for use in filenames.
    
    Args:
        voice: Voice specification to clean
        
    Returns:
        Cleaned voice name suitable for filenames
    """
    return voice.replace('+', '_').replace('(', '').replace(')', '').replace(':', '_')