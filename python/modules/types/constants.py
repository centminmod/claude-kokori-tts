"""
Constants and configuration values for the TTS system.

This module contains all constant definitions used throughout the TTS system.
Layer 1 - Foundation: No dependencies on other modules.
"""

# Version constant
__version__ = "0.0.8"

# Supported audio formats
SUPPORTED_FORMATS = {
    "wav": "audio/wav",
    "mp3": "audio/mpeg",
    "pcm": "audio/pcm",
    "opus": "audio/opus",
    "flac": "audio/flac"
}

# Text processing constants
MAX_TEXT_LENGTH = 10000  # Maximum text length for TTS
DEFAULT_CHUNK_SIZE = 300  # Default chunk size for long text
NOTIFICATION_TEXT_LIMIT = 100  # Max text length for notification mode
TEXT_PREVIEW_LENGTH = 100  # Length of text preview in cache metadata

# Audio settings constants
AUDIO_FREQUENCY = 24000  # Audio frequency (Hz)
AUDIO_SAMPLE_SIZE = -16  # Audio sample size (bits)
AUDIO_CHANNELS = 1  # Mono audio
NOTIFICATION_BUFFER_SIZE = 512  # Buffer size for notification mode
DEFAULT_BUFFER_SIZE = 1024  # Default buffer size
STREAM_CHUNK_SIZE = 1024  # Chunk size for streaming

# Cache constants
DEFAULT_CACHE_SIZE = 100  # Default cache size (items)
DEFAULT_CACHE_MEMORY_MB = 100  # Default cache memory limit (MB)
DEFAULT_DISK_CACHE_GB = 1.0  # Default disk cache size (GB)
BYTES_PER_MB = 1024 * 1024  # Bytes per megabyte
BYTES_PER_GB = 1024 * 1024 * 1024  # Bytes per gigabyte

# Validation constants
MIN_AUDIO_SIZE = 100  # Minimum audio size (bytes) for validation
MIN_GENERATED_AUDIO_SIZE = 1000  # Minimum generated audio size (bytes)
TEMP_FILE_CLEANUP_AGE = 3600  # Age threshold for temp file cleanup (1 hour)

# Performance constants
MS_PER_SECOND = 1000  # Milliseconds per second
CACHE_PERFORMANCE_THRESHOLD = 0.1  # Threshold for cache performance (100ms)

# Hot cache constants
HOT_CACHE_MEMORY_MB = 10  # Maximum memory for hot cache
HOT_CACHE_MESSAGE_LIMIT = 50  # Maximum messages in hot cache

# Connection constants
CONNECTION_TIMEOUT_NOTIFICATION = 1  # Timeout for notification mode (seconds)
CONNECTION_TIMEOUT_DEFAULT = 30  # Default connection timeout (seconds)
CONNECTION_RETRY_COUNT = 3  # Number of connection retries
CONNECTION_RETRY_DELAY = 0.5  # Delay between retries (seconds)

# Default server URL
DEFAULT_SERVER_URL = "http://localhost:8880"

# Default voices fallback list
FALLBACK_VOICES = {
    "af_bella": "American Female - Bella (Grade A-) ⭐ Recommended",
    "af_nicole": "American Female - Nicole (Grade B-)",
    "af_sarah": "American Female - Sarah (Grade C+)",
    "am_michael": "American Male - Michael (Grade C+)",
    "am_adam": "American Male - Adam (Grade B-)",
    "bf_emma": "British Female - Emma (Grade B-)",
    "bm_george": "British Male - George (Grade C)",
}

# Voice blending constants
VOICE_BLEND_SEPARATOR = "+"
VOICE_WEIGHT_PATTERN = r"^([^()]+)\(([0-9.]+)\)$"

# Default preload messages (common TTS messages)
DEFAULT_PRELOAD_MESSAGES = [
    "Build completed successfully",
    "Build failed",
    "Error: Command failed",
    "Running tests",
    "Tests passed",
    "Tests failed",
    "Processing",
    "Task completed",
    "Warning",
    "Claude Code session complete"
]

# Hook-specific preload messages (for Claude Code hooks)
HOOK_PRELOAD_MESSAGES = [
    "Session Started",
    "Prompt Submitted",
    "Input Required",
    "Command Execution",
    "File Operation",
    "Subagent Complete",
    "Session Complete"
]