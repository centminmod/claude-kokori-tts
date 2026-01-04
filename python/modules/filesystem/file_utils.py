"""
File system utilities for the TTS system.

This module provides file system operations and utilities.
Layer 2 - Core Services: Depends only on Layer 1 (Foundation) and external libraries.
"""

import os
import time
import tempfile
from pathlib import Path
from typing import Set, Optional

from modules.types.exceptions import PathTraversalError, InvalidPathError


def ensure_directory_exists(directory: Path) -> None:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory: Path to directory
    """
    directory.mkdir(parents=True, exist_ok=True)


def get_config_directory() -> Path:
    """
    Get the configuration directory for the TTS system.
    
    Returns:
        Path to configuration directory
    """
    config_dir = Path.home() / '.claude_tts'
    ensure_directory_exists(config_dir)
    return config_dir


def get_cache_directory() -> Path:
    """
    Get the cache directory for the TTS system.
    
    Returns:
        Path to cache directory
    """
    cache_dir = get_config_directory() / 'cache' / 'audio'
    ensure_directory_exists(cache_dir)
    return cache_dir


def get_temp_directory() -> Path:
    """
    Get temporary directory for TTS files.
    
    Returns:
        Path to temporary directory
    """
    temp_dir = Path.home() / "tmp"
    ensure_directory_exists(temp_dir)
    return temp_dir


def cleanup_temp_files(temp_files: Set[str], cleanup_age: int = 3600) -> None:
    """
    Clean up temporary files.
    
    Args:
        temp_files: Set of temporary file paths to clean
        cleanup_age: Age threshold in seconds for cleanup
    """
    # Clean up tracked temp files
    temp_files_copy = temp_files.copy()  # Avoid modification during iteration
    for temp_file in temp_files_copy:
        try:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
        except (OSError, IOError):
            pass  # Ignore errors during cleanup
        except Exception:
            pass  # Ignore unexpected errors
    
    # Clear the tracking set
    temp_files.clear()


def cleanup_orphaned_temp_files(cleanup_age: int = 3600) -> None:
    """
    Clean up orphaned temporary files.
    
    Args:
        cleanup_age: Age threshold in seconds (default: 1 hour)
    """
    try:
        temp_dir = get_temp_directory()
        if temp_dir.exists():
            current_time = time.time()
            for temp_file in temp_dir.glob("tmp*"):
                try:
                    # Only clean up files that are likely from this app and are old
                    if (temp_file.is_file() and 
                        current_time - temp_file.stat().st_mtime > cleanup_age):
                        temp_file.unlink()
                except (OSError, IOError):
                    pass  # Ignore errors during cleanup
                except Exception:
                    pass  # Ignore unexpected errors
    except Exception:
        pass  # Ignore errors during orphaned file cleanup


def create_temp_audio_file(audio_bytes: bytes, format_type: str = "wav") -> str:
    """
    Create a temporary file for audio data.
    
    Args:
        audio_bytes: Audio data to write
        format_type: Audio format extension
        
    Returns:
        Path to created temporary file
    """
    temp_dir = get_temp_directory()
    file_ext = f".{format_type}" if format_type else ".wav"
    
    with tempfile.NamedTemporaryFile(
        suffix=file_ext,
        delete=False,
        dir=temp_dir
    ) as temp_file:
        temp_file.write(audio_bytes)
        return temp_file.name


def safe_file_read(file_path: Path, encoding: str = 'utf-8') -> Optional[str]:
    """
    Safely read a file with error handling.
    
    Args:
        file_path: Path to file to read
        encoding: File encoding
        
    Returns:
        File contents or None if error
    """
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    except (IOError, OSError, UnicodeDecodeError):
        return None
    except Exception:
        return None


def safe_file_write(file_path: Path, content: str, encoding: str = 'utf-8') -> bool:
    """
    Safely write to a file with error handling.
    
    Args:
        file_path: Path to file to write
        content: Content to write
        encoding: File encoding
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure parent directory exists
        ensure_directory_exists(file_path.parent)
        
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
        return True
    except (IOError, OSError, UnicodeEncodeError):
        return False
    except Exception:
        return False


def get_safe_filename(filename: str, max_length: int = 255) -> str:
    """
    Get a safe filename by removing/replacing invalid characters.
    
    Args:
        filename: Original filename
        max_length: Maximum filename length
        
    Returns:
        Safe filename
    """
    import re
    
    # Remove or replace invalid characters
    safe_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Replace multiple underscores with single
    safe_name = re.sub(r'_+', '_', safe_name)
    
    # Strip leading/trailing whitespace and dots
    safe_name = safe_name.strip(' .')
    
    # Truncate if too long
    if len(safe_name) > max_length:
        name_part, ext_part = os.path.splitext(safe_name)
        safe_name = name_part[:max_length - len(ext_part)] + ext_part
    
    # Ensure not empty
    if not safe_name:
        safe_name = "unnamed_file"
    
    return safe_name


def validate_safe_path(base_dir: Path, user_path: str) -> Path:
    """
    Validate that a user-provided path stays within the base directory.
    
    This prevents path traversal attacks by ensuring the resolved path
    is within the intended base directory.
    
    Args:
        base_dir: Base directory that paths must stay within
        user_path: User-provided path (filename or relative path)
        
    Returns:
        Resolved safe path within base_dir
        
    Raises:
        PathTraversalError: If path traversal is detected
        InvalidPathError: If path contains invalid characters
    """
    # Convert to Path objects and resolve to absolute paths
    base = base_dir.resolve()
    
    # Remove any leading path separators to prevent absolute path injection
    clean_user_path = user_path.lstrip(os.sep).lstrip('/')
    
    # Check for null bytes which can cause security issues
    if '\0' in clean_user_path:
        raise InvalidPathError(f"Invalid path: contains null bytes")
    
    # Construct the target path
    target = (base / clean_user_path).resolve()
    
    # Ensure the target path is within the base directory
    try:
        target.relative_to(base)
    except ValueError:
        # Path is outside base directory
        raise PathTraversalError(f"Path traversal detected: {user_path}")
    
    return target