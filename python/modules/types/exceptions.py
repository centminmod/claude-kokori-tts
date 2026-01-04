"""
Custom exceptions for the TTS system.

This module defines specific exception types for better error handling and reporting.
Layer 1 - Foundation: No dependencies on other layers.
"""


class TTSError(Exception):
    """Base exception class for all TTS-related errors."""
    pass


class PathTraversalError(TTSError):
    """Raised when a path traversal attempt is detected."""
    pass


class InvalidPathError(TTSError):
    """Raised when a path is invalid or contains forbidden characters."""
    pass


class TTSConnectionError(TTSError):
    """Raised when connection to the TTS server fails."""
    pass


class InvalidVoiceError(TTSError):
    """Raised when an invalid voice is specified."""
    pass


class AudioGenerationError(TTSError):
    """Raised when audio generation fails."""
    pass


class CacheError(TTSError):
    """Raised when cache operations fail."""
    pass


class ExportError(TTSError):
    """Raised when audio export operations fail."""
    pass


class ConfigurationError(TTSError):
    """Raised when there are configuration-related issues."""
    pass