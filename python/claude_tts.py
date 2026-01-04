#!/usr/bin/env python3
"""
Claude Code + Kokoro-FastAPI TTS Integration (Enhanced)
Advanced TTS with voice blending, streaming, and Claude Code hook support

Version: 0.1.15

Prerequisites:
    1. Run Kokoro-FastAPI server: docker run -p 8880:8880 ghcr.io/remsky/kokoro-fastapi-cpu:latest
    2. Ensure Docker Desktop has VirtioFS enabled and sufficient resources

Features:
    - Notification mode optimized for Claude Code hooks
    - Preload system for instant playback of common messages
    - Voice blending and streaming support
    - Multiple output formats (WAV, MP3, PCM, OPUS, FLAC)
    - Audio export with smart filename generation
    - Server monitoring and health checking via debug endpoints
    - Real-time server resource monitoring and alerting
    - Comprehensive error handling and reliability
    - Type annotations and IDE support
"""

# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "requests>=2.31.0",
#     "pygame>=2.5.0",
#     "click>=8.1.0",
#     "python-dotenv>=1.0.0",
#     "pyaudio>=0.2.11",
#     "pyyaml>=6.0",
#     "urllib3>=2.0.0",
#     "pydantic>=2.0.0",
# ]
# ///

import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import sys
import json
import time
import logging
from typing import Optional

import click
from dotenv import load_dotenv

# Version constant
__version__ = "0.1.15"

# Configure environment and logging
load_dotenv()
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Suppress urllib3 warnings
urllib3_logger = logging.getLogger('urllib3.connectionpool')
urllib3_logger.setLevel(logging.ERROR)

# Import dataclasses for CLI JSON serialization
from modules.types.data_models import ServerDebugInfo, StorageInfo

# Import custom exceptions for better error handling
from modules.types.exceptions import (
    TTSError,
    TTSConnectionError,
    InvalidVoiceError,
    AudioGenerationError,
    CacheError,
    ExportError,
    ConfigurationError,
    PathTraversalError,
    InvalidPathError
)

# Import the modular facade that replaces the monolithic class
from modules.integration.facade import ModularTTSFacade

# Import test operations
from modules.testing import run_tests

# Import CLI configuration
from modules.config import CLIConfig

# Alias for 100% backward compatibility
EnhancedKokoroFastAPIIntegration = ModularTTSFacade



def handle_tts_operation_errors(func, *args, quiet: bool = False, **kwargs):
    """
    Handle common TTS operation errors in a unified way.
    
    Args:
        func: The function to execute
        *args: Positional arguments for the function
        quiet: Whether to suppress output
        **kwargs: Keyword arguments for the function
        
    Returns:
        Dictionary with success, message, and error fields
    """
    try:
        result = func(*args, **kwargs)
        # Handle functions that return success boolean
        if isinstance(result, bool):
            return {
                "success": result,
                "message": "Operation successful" if result else "Operation failed",
                "error": None
            }
        # Handle functions that return tuple (e.g., get_phonemes)
        elif isinstance(result, tuple):
            return {
                "success": True,
                "data": result,
                "message": "Operation successful",
                "error": None
            }
        else:
            return {
                "success": True,
                "message": "Operation successful",
                "error": None
            }
    except FileNotFoundError as e:
        if not quiet:
            print(f"❌ File not found: {e}")
        return {"success": False, "error": str(e), "message": "File not found"}
    except PermissionError as e:
        if not quiet:
            print(f"❌ Permission denied: {e}")
        return {"success": False, "error": str(e), "message": "Permission denied"}
    except UnicodeDecodeError as e:
        if not quiet:
            print(f"❌ Unable to read file (encoding error): {e}")
        return {"success": False, "error": str(e), "message": "File encoding error"}
    except InvalidVoiceError as e:
        if not quiet:
            print(f"❌ Invalid voice: {e}")
        return {"success": False, "error": str(e), "message": "Invalid voice specified"}
    except (PathTraversalError, InvalidPathError) as e:
        if not quiet:
            print(f"❌ Security error: {e}")
        return {"success": False, "error": str(e), "message": "Invalid export path"}
    except ExportError as e:
        if not quiet:
            print(f"❌ Export failed: {e}")
        return {"success": False, "error": str(e), "message": "Export failed"}
    except AudioGenerationError as e:
        if not quiet:
            print(f"❌ Audio generation failed: {e}")
        return {"success": False, "error": str(e), "message": "Audio generation failed"}
    except (ConnectionError, TTSConnectionError) as e:
        if not quiet:
            print(f"❌ Connection error: {e}")
        return {"success": False, "error": str(e), "message": "Server connection lost"}
    except ValueError as e:
        if not quiet:
            print(f"❌ Invalid input: {e}")
        return {"success": False, "error": str(e), "message": "Invalid input"}
    except TTSError as e:
        if not quiet:
            print(f"❌ TTS error: {e}")
        return {"success": False, "error": str(e), "message": "TTS error"}
    except Exception as e:
        if not quiet:
            print(f"❌ Unexpected error: {e}")
        return {"success": False, "error": str(e), "message": "Unexpected error"}


def handle_utility_operations(
    tts: ModularTTSFacade,
    cache_stats: bool,
    clear_cache: Optional[str],
    server_stats: bool,
    health_check: bool,
    monitor_server: Optional[int],
    json_output: bool,
    quiet: bool
) -> Optional[int]:
    """
    Handle utility operations like cache management and server monitoring.
    
    Args:
        tts: TTS instance
        cache_stats: Show cache statistics
        clear_cache: Clear cache tier
        server_stats: Show server stats
        health_check: Check server health
        monitor_server: Monitor server for N seconds
        json_output: Output in JSON format
        quiet: Quiet mode
        
    Returns:
        0 for success, 1 for error, None if no operation was handled
    """
    if cache_stats:
        stats = tts.get_cache_stats()
        print("📊 Cache Statistics:")
        print(f"   Hot Cache: {len(stats['hot_cache']['messages'])} messages, {stats['hot_cache']['memory_mb']:.1f}MB")
        print(f"   Disk Cache: {stats['disk_cache']['entries']} entries, {stats['disk_cache']['size_mb']:.1f}MB")
        print(f"   Memory Cache: {stats['memory_cache']['size']} items, {stats['memory_cache']['memory_mb']:.1f}MB, {stats['memory_cache']['hit_rate']:.1%} hit rate")
        print(f"   Total: {stats['total']['entries']} entries, {stats['total']['memory_mb']:.1f}MB memory, {stats['total']['disk_mb']:.1f}MB disk")
        return 0
    
    if clear_cache:
        tier = clear_cache.lower()
        if tier not in ['hot', 'disk', 'memory', 'all']:
            print("❌ Invalid cache tier. Use: hot, disk, memory, or all")
            return 1
        
        tts.clear_cache(tier if tier != 'all' else None)
        print(f"✅ Cleared {tier} cache{'s' if tier == 'all' else ''}")
        return 0
    
    if server_stats:
        debug_info = tts.get_server_debug_info()
        if json_output:
            result = {"success": True, "server_stats": {
                "health": debug_info.get_health_summary(),
                "healthy": debug_info.is_healthy(),
                "threads": debug_info.threads,
                "system": debug_info.system,
                "storage": [vars(s) for s in debug_info.storage] if debug_info.storage else None,
                "errors": debug_info.errors,
                "timestamp": debug_info.timestamp
            }}
            print(json.dumps(result, indent=2))
        else:
            print(tts.format_server_stats(debug_info))
        return 0
    
    if health_check:
        is_healthy, health_summary = tts.get_server_health()
        if json_output:
            result = {"success": True, "healthy": is_healthy, "status": health_summary}
            print(json.dumps(result))
        else:
            print(f"🏥 Server Health: {health_summary}")
        return 0
    
    if monitor_server:
        if monitor_server <= 0:
            print("❌ Monitor duration must be positive")
            return 1
        try:
            tts.monitor_server_continuous(interval=5, duration=monitor_server)
        except KeyboardInterrupt:
            if not quiet:
                print("\n🛑 Monitoring stopped by user")
        return 0
    
    return None


def get_context_settings() -> dict:
    """
    Get Click context settings with config-based defaults.

    Loads configuration from:
    1. Project root .claude_tts.yml (highest priority)
    2. User home ~/.claude_tts/config.yml (lower priority)

    CLI arguments always override config file values.

    Returns:
        Dictionary with 'default_map' for Click context settings
    """
    try:
        from modules.config.loader import ConfigurationLoader
        config_loader = ConfigurationLoader()
        default_map = config_loader.load_cli_defaults()
        if default_map:
            return {'default_map': default_map}
    except Exception as e:
        # Silently fall back to hardcoded defaults if config loading fails
        logger.debug(f"Config file loading failed, using defaults: {e}")
    return {}


@click.command(context_settings=get_context_settings())
@click.argument('text', required=False)
@click.option('--voice', '-v', default='af_bella', help='Voice to use (supports blending: af_bella+af_sky)')
@click.option('--speed', '-s', default=1.0, type=float, help='Speech speed (0.5-2.0)')
@click.option('--format', '-f', default='wav', type=click.Choice(['wav', 'mp3', 'pcm', 'opus', 'flac']), help='Audio format')
@click.option('--interactive', '-i', is_flag=True, help='Interactive mode')
@click.option('--stream', is_flag=True, help='Enable streaming playback')
@click.option('--file', type=click.Path(exists=True), help='Read text from file')
@click.option('--export', type=str, default=None, help='Export audio to file (filename, or empty string for auto-generation)')
@click.option('--export-dir', type=click.Path(), default='.', help='Directory for exported files (default: current directory)')
@click.option('--list-voices', is_flag=True, help='List available voices')
@click.option('--test', is_flag=True, help='Test system setup')
@click.option('--test-all', is_flag=True, help='Run comprehensive functionality tests')
@click.option('--test-quick', is_flag=True, help='Run quick functionality tests')
@click.option('--phonemes', is_flag=True, help='Show phonemes for input text')
@click.option('--no-normalize', is_flag=True, help='Disable text normalization')
@click.option('--server', default='http://localhost:8880', help='Kokoro-FastAPI server URL')
@click.option('--notification', '-n', is_flag=True, help='Notification mode (optimized for Claude Code hooks)')
@click.option('--quiet', '-q', is_flag=True, help='Quiet mode (suppress non-error output)')
@click.option('--background', '-b', is_flag=True, help='Play audio in background')
@click.option('--json', 'json_output', is_flag=True, help='Output JSON response')
@click.option('--no-preload', is_flag=True, help='Disable message preloading')
@click.option('--debug', is_flag=True, help='Enable debug logging')
@click.option('--version', is_flag=True, help='Show version information')
@click.option('--cache-stats', is_flag=True, help='Show cache statistics')
@click.option('--clear-cache', type=str, help='Clear cache (hot/disk/memory/all)')
@click.option('--server-stats', is_flag=True, help='Show server debug statistics')
@click.option('--health-check', is_flag=True, help='Check server health status')
@click.option('--monitor-server', type=int, help='Monitor server continuously for N seconds')
@click.option('--skip-voice-check', is_flag=True, help='Skip voice discovery for faster startup (use with known voices)')
def main(text: Optional[str], voice: str, speed: float, format: str, interactive: bool,
         stream: bool, file: Optional[str], export: Optional[str], export_dir: str, list_voices: bool, test: bool, test_all: bool,
         test_quick: bool, phonemes: bool, no_normalize: bool, server: str, notification: bool,
         quiet: bool, background: bool, json_output: bool, no_preload: bool,
         debug: bool, version: bool, cache_stats: bool, clear_cache: Optional[str],
         server_stats: bool, health_check: bool, monitor_server: Optional[int],
         skip_voice_check: bool):
    """Enhanced Claude Code + Kokoro-FastAPI TTS
    
    Setup:
        1. Ensure Docker Desktop is running
        2. Run: docker run -p 8880:8880 ghcr.io/remsky/kokoro-fastapi-cpu:latest
        3. Use this enhanced script!
    
    Examples:
        # Basic usage
        uv run claude_tts.py "Hello world!"
        
        # Notification mode for hooks
        uv run claude_tts.py --notification "Build completed"
        
        # Voice blending
        uv run claude_tts.py --voice "af_bella+af_sky" "Blended voice"
        
        # Background playback
        uv run claude_tts.py --background --quiet "Processing..."
        
        # Server monitoring
        uv run claude_tts.py --server-stats
        uv run claude_tts.py --health-check
        uv run claude_tts.py --monitor-server 30
        
        # Interactive mode with server monitoring
        uv run claude_tts.py --interactive --stream
    """
    
    # Create configuration object from all parameters
    config = CLIConfig.from_click_params(
        text=text, voice=voice, speed=speed, format=format, interactive=interactive,
        stream=stream, file=file, export=export, export_dir=export_dir,
        list_voices=list_voices, test=test, test_all=test_all, test_quick=test_quick,
        phonemes=phonemes, no_normalize=no_normalize, server=server,
        notification=notification, quiet=quiet, background=background,
        json_output=json_output, no_preload=no_preload, debug=debug,
        version=version, cache_stats=cache_stats, clear_cache=clear_cache,
        server_stats=server_stats, health_check=health_check, monitor_server=monitor_server,
        skip_voice_check=skip_voice_check
    )
    
    # Handle version flag
    if config.operation.version:
        print(f"Enhanced Claude Code + Kokoro TTS Integration v{__version__}")
        return
    
    # Configure logging
    if config.server.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # JSON output structure
    result = {
        "success": False,
        "message": "",
        "error": None
    }
    
    # Initialize TTS instance once
    try:
        tts = EnhancedKokoroFastAPIIntegration(
            base_url=config.server.server_url,
            notification_mode=config.server.notification_mode,
            quiet_mode=config.output.quiet or config.output.json_output,
            preload=not config.server.no_preload,
            skip_voice_check=config.server.skip_voice_check
        )
    except (ConnectionError, TTSConnectionError) as e:
        result["error"] = str(e)
        result["message"] = "Failed to connect to TTS server"
        if config.output.json_output:
            print(json.dumps(result))
        else:
            print(f"❌ Server connection failed: {str(e)}")
        sys.exit(2)  # Exit code 2 for server unavailable
    except ConfigurationError as e:
        result["error"] = str(e)
        result["message"] = "Configuration error"
        if config.output.json_output:
            print(json.dumps(result))
        else:
            print(f"❌ Configuration error: {str(e)}")
        sys.exit(1)
    except TTSError as e:
        result["error"] = str(e)
        result["message"] = "TTS system error"
        if config.output.json_output:
            print(json.dumps(result))
        else:
            print(f"❌ TTS error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        result["error"] = str(e)
        result["message"] = "Unexpected initialization error"
        if config.output.json_output:
            print(json.dumps(result))
        else:
            print(f"❌ Unexpected error: {str(e)}")
        sys.exit(1)
    
    # Handle utility operations (cache, server monitoring, etc)
    if config.operation.cache_stats or config.operation.clear_cache or config.operation.server_stats or config.operation.health_check or config.operation.monitor_server:
        try:
            exit_code = handle_utility_operations(
                tts, config.operation.cache_stats, config.operation.clear_cache, config.operation.server_stats,
                config.operation.health_check, config.operation.monitor_server, config.output.json_output, config.output.quiet
            )
            if exit_code is not None:
                sys.exit(exit_code)
        except (ConnectionError, TTSConnectionError) as e:
            if config.output.json_output:
                print(json.dumps({"success": False, "error": str(e)}))
            else:
                print(f"❌ Server connection failed: {e}")
            sys.exit(2)
        except CacheError as e:
            if config.output.json_output:
                print(json.dumps({"success": False, "error": str(e)}))
            else:
                print(f"❌ Cache operation failed: {e}")
            sys.exit(1)
        except ValueError as e:
            if config.output.json_output:
                print(json.dumps({"success": False, "error": str(e)}))
            else:
                print(f"❌ Invalid input: {e}")
            sys.exit(1)
        except TTSError as e:
            if config.output.json_output:
                print(json.dumps({"success": False, "error": str(e)}))
            else:
                print(f"❌ TTS error: {e}")
            sys.exit(1)
        except Exception as e:
            if config.output.json_output:
                print(json.dumps({"success": False, "error": str(e)}))
            else:
                print(f"❌ Unexpected error: {e}")
            sys.exit(1)
    
    # Handle test operations
    if config.operation.test or config.operation.test_all or config.operation.test_quick:
        test_type = 'basic' if config.operation.test else 'all' if config.operation.test_all else 'quick'
        exit_code = run_tests(
            tts, test_type, config.audio.voice, config.audio.format, config.server.server_url, config.output.quiet, config.output.json_output
        )
        if exit_code is not None:
            sys.exit(exit_code)
    
    if config.operation.list_voices:
        if config.output.json_output:
            result["success"] = True
            result["voices"] = tts.available_voices
            print(json.dumps(result))
        else:
            print("\n🎤 Available voices:")
            for voice_id, description in tts.available_voices.items():
                print(f"  {voice_id}: {description}")
            print("\n🎨 Voice blending examples:")
            print("  af_bella+af_sky (equal mix)")
            print("  af_bella(2)+af_sky(1) (2:1 ratio)")
        sys.exit(0)
    
    if config.operation.interactive:
        tts.interactive_mode(config.audio.voice, config.audio.format)
    elif config.operation.file:
        def read_and_speak_file():
            with open(config.operation.file, 'r', encoding='utf-8') as f:
                file_text = f.read().strip()
            if not file_text:
                if not config.output.quiet:
                    print("❌ File is empty")
                return {"success": False, "message": "File is empty", "error": None}
            
            success = tts.speak_text(
                file_text, config.audio.voice, config.audio.speed, config.audio.format,
                config.audio.stream, not config.audio.no_normalize, config.audio.background,
                config.output.export, config.output.export_dir
            )
            return {
                "success": success,
                "message": "File processed successfully" if success else "Processing failed",
                "error": None
            }
        
        operation_result = handle_tts_operation_errors(
            read_and_speak_file,
            quiet=config.output.quiet
        )
        result.update(operation_result)
    elif config.operation.text:
        if config.audio.phonemes:
            def get_phonemes_operation():
                phonemes_result, tokens = tts.get_phonemes(config.operation.text)
                if not config.output.quiet:
                    print(f"✅ Phonemes: {phonemes_result}")
                    print(f"✅ Tokens: {tokens}")
                return phonemes_result, tokens
            
            operation_result = handle_tts_operation_errors(
                get_phonemes_operation,
                quiet=config.output.quiet
            )
            if operation_result["success"] and "data" in operation_result:
                phonemes_result, tokens = operation_result["data"]
                result["success"] = True
                result["phonemes"] = phonemes_result
                result["tokens"] = tokens
                result["message"] = "Phoneme generation successful"
            else:
                result.update(operation_result)
                # Override generic message with phoneme-specific message for certain errors
                if operation_result.get("message") == "TTS error":
                    result["message"] = "Phoneme generation failed"
        else:
            def speak_text_operation():
                return tts.speak_text(
                    config.operation.text, config.audio.voice, config.audio.speed, config.audio.format,
                    config.audio.stream, not config.audio.no_normalize, config.audio.background,
                    config.output.export, config.output.export_dir
                )
            
            operation_result = handle_tts_operation_errors(
                speak_text_operation,
                quiet=config.output.quiet
            )
            result.update(operation_result)
            if operation_result["success"]:
                result["message"] = "Text spoken successfully"
            elif operation_result["message"] == "Operation failed":
                result["message"] = "Speech failed"
    else:
        result["message"] = "No input provided"
        if not config.output.quiet:
            print("❌ Please provide text, use --file, --interactive, --list-voices, or --test")
    
    if config.output.json_output:
        print(json.dumps(result))
    
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()

