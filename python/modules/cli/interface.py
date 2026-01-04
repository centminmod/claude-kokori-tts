"""
Command-line interface for the TTS system.

This module provides the CLI interface and interactive mode functionality.
Layer 5 - Orchestration: Depends on Layers 1-4.
"""

import sys
import time
import logging
from typing import Optional, Dict, Any

from modules.core.service import EnhancedKokoroFastAPIIntegration
from modules.types.constants import SUPPORTED_FORMATS

logger = logging.getLogger(__name__)


class TTSCLIInterface:
    """Command-line interface for the TTS system"""
    
    def __init__(self, tts_service: EnhancedKokoroFastAPIIntegration):
        """
        Initialize CLI interface.
        
        Args:
            tts_service: The main TTS service instance
        """
        self.tts_service = tts_service
        self.interactive_settings = {
            'voice': 'af_bella',
            'speed': 1.0,
            'format': 'wav',
            'stream': False,
            'export': False,
            'export_dir': './exports'
        }
    
    def interactive_mode(self) -> None:
        """Run interactive TTS mode with enhanced commands"""
        print("🎤 Enhanced Claude Code + Kokoro TTS Interactive Mode")
        print("Type 'help' for commands, 'quit' to exit")
        print("=" * 60)
        
        # Show current settings
        self._show_settings()
        
        while True:
            try:
                user_input = input("\n💬 > ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                # Handle commands
                if user_input.startswith('/') or ' ' not in user_input:
                    if not self._handle_command(user_input):
                        continue
                else:
                    # Treat as text to speak
                    self._speak_interactive_text(user_input)
                    
            except KeyboardInterrupt:
                print("\\n👋 Goodbye!")
                break
            except EOFError:
                print("\\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                logger.exception("Interactive mode error")
    
    def _handle_command(self, command: str) -> bool:
        """
        Handle interactive commands.
        
        Args:
            command: Command string
            
        Returns:
            True if command was handled, False to skip speaking
        """
        cmd = command.lower().strip('/')
        parts = cmd.split()
        
        if not parts:
            return False
        
        cmd_name = parts[0]
        cmd_args = parts[1:] if len(parts) > 1 else []
        
        # Help command
        if cmd_name in ['help', 'h']:
            self._show_help()
            return False
        
        # Settings commands
        elif cmd_name == 'settings':
            self._show_settings()
            return False
        
        elif cmd_name == 'voice':
            if cmd_args:
                self.interactive_settings['voice'] = ' '.join(cmd_args)
                print(f"🎵 Voice set to: {self.interactive_settings['voice']}")
            else:
                print(f"Current voice: {self.interactive_settings['voice']}")
            return False
        
        elif cmd_name == 'speed':
            if cmd_args:
                try:
                    speed = float(cmd_args[0])
                    if 0.5 <= speed <= 2.0:
                        self.interactive_settings['speed'] = speed
                        print(f"⚡ Speed set to: {speed}")
                    else:
                        print("❌ Speed must be between 0.5 and 2.0")
                except ValueError:
                    print("❌ Invalid speed value")
            else:
                print(f"Current speed: {self.interactive_settings['speed']}")
            return False
        
        elif cmd_name == 'format':
            if cmd_args:
                fmt = cmd_args[0].lower()
                if fmt in SUPPORTED_FORMATS:
                    self.interactive_settings['format'] = fmt
                    print(f"🎵 Format set to: {fmt}")
                else:
                    print(f"❌ Unsupported format. Available: {list(SUPPORTED_FORMATS.keys())}")
            else:
                print(f"Current format: {self.interactive_settings['format']}")
            return False
        
        elif cmd_name == 'stream':
            if cmd_args:
                if cmd_args[0].lower() in ['on', 'true', '1']:
                    self.interactive_settings['stream'] = True
                    print("🌊 Streaming enabled")
                elif cmd_args[0].lower() in ['off', 'false', '0']:
                    self.interactive_settings['stream'] = False
                    print("🌊 Streaming disabled")
            else:
                status = "enabled" if self.interactive_settings['stream'] else "disabled"
                print(f"Streaming: {status}")
            return False
        
        elif cmd_name == 'export':
            if cmd_args:
                if cmd_args[0].lower() in ['on', 'true', '1']:
                    self.interactive_settings['export'] = True
                    print("💾 Export enabled")
                elif cmd_args[0].lower() in ['off', 'false', '0']:
                    self.interactive_settings['export'] = False
                    print("💾 Export disabled")
            else:
                status = "enabled" if self.interactive_settings['export'] else "disabled"
                print(f"Export: {status}")
            return False
        
        elif cmd_name == 'export-dir':
            if cmd_args:
                export_dir = ' '.join(cmd_args)
                if self.tts_service.export_manager.set_export_directory(export_dir):
                    self.interactive_settings['export_dir'] = export_dir
                    print(f"📁 Export directory set to: {export_dir}")
                else:
                    print("❌ Failed to set export directory")
            else:
                print(f"Current export directory: {self.interactive_settings['export_dir']}")
            return False
        
        # Voice management
        elif cmd_name == 'voices':
            self._list_voices()
            return False
        
        elif cmd_name == 'blend':
            if cmd_args:
                voice_blend = ' '.join(cmd_args)
                target_voice = f"blend_{int(time.time())}"
                if self.tts_service.tts_client.create_voice_blend_file(voice_blend, target_voice):
                    print(f"✅ Created voice blend: {target_voice}")
                else:
                    print("❌ Failed to create voice blend")
            else:
                print("Usage: /blend af_bella(2)+af_sky(1)")
            return False
        
        # Content analysis
        elif cmd_name == 'phonemes':
            if cmd_args:
                text = ' '.join(cmd_args)
                try:
                    phoneme_response = self.tts_service.tts_client.get_voice_phonemes(
                        text, self.interactive_settings['voice']
                    )
                    print(f"🔤 Phonemes for '{text}': {phoneme_response.phonemes}")
                    if phoneme_response.tokens:
                        print(f"   Tokens: {phoneme_response.tokens}")
                    if phoneme_response.word_timestamps:
                        print(f"   Word timestamps available: {len(phoneme_response.word_timestamps)} words")
                except Exception as e:
                    print(f"❌ Phoneme analysis failed: {e}")
            else:
                print("Usage: /phonemes <text>")
            return False
        
        # Cache management
        elif cmd_name == 'stats':
            self._show_cache_stats()
            return False
        
        elif cmd_name == 'cache':
            if cmd_args:
                if cmd_args[0] == 'stats':
                    self._show_detailed_cache_stats()
                elif cmd_args[0] == 'clear':
                    tier = cmd_args[1] if len(cmd_args) > 1 else None
                    self.tts_service.clear_cache(tier)
                else:
                    print("Usage: /cache [stats|clear [hot|disk|memory|all]]")
            else:
                print("Usage: /cache [stats|clear]")
            return False
        
        elif cmd_name == 'promote':
            if cmd_args:
                text = ' '.join(cmd_args)
                self.tts_service.promote_to_hot_cache(text, self.interactive_settings['voice'])
            else:
                print("Usage: /promote <text>")
            return False
        
        # Server monitoring
        elif cmd_name == 'server':
            debug_info = self.tts_service.get_server_debug_info()
            print(self.tts_service.format_server_stats(debug_info))
            return False
        
        elif cmd_name == 'health':
            is_healthy, summary = self.tts_service.get_server_health()
            print(f"Server Health: {summary}")
            return False
        
        elif cmd_name == 'monitor':
            duration = int(cmd_args[0]) if cmd_args else 30
            print(f"🔍 Monitoring server for {duration} seconds...")
            self.tts_service.monitor_server_continuous(duration=duration)
            return False
        
        # Debug commands
        elif cmd_name == 'debug':
            self._show_debug_info()
            return False
        
        else:
            print(f"❌ Unknown command: {cmd_name}")
            print("Type 'help' for available commands")
            return False
    
    def _speak_interactive_text(self, text: str) -> None:
        """Speak text using current interactive settings"""
        try:
            # Export if enabled
            if self.interactive_settings['export']:
                self.tts_service.export_manager.export_audio(
                    text=text,
                    voice=self.interactive_settings['voice'],
                    speed=self.interactive_settings['speed'],
                    format_type=self.interactive_settings['format'],
                    export_dir=self.interactive_settings['export_dir'],
                    play_audio=False  # We'll play separately
                )
            
            # Speak the text
            self.tts_service.speak_text(
                text=text,
                voice=self.interactive_settings['voice'],
                speed=self.interactive_settings['speed'],
                format_type=self.interactive_settings['format'],
                stream=self.interactive_settings['stream']
            )
            
        except Exception as e:
            print(f"❌ Failed to speak text: {e}")
            logger.exception("Interactive speech failed")
    
    def _show_help(self) -> None:
        """Show help information"""
        print("\\n📖 Available Commands:")
        print("=" * 50)
        print("🎵 Voice & Audio:")
        print("  /voice <voice_id>     - Set voice (e.g., af_bella)")
        print("  /speed <0.5-2.0>      - Set speech speed")
        print("  /format <format>      - Set audio format (wav, mp3, etc)")
        print("  /stream on/off        - Toggle streaming mode")
        print("  /voices               - List available voices")
        print("  /blend <specification> - Create voice blend")
        print("  /phonemes <text>      - Show phoneme breakdown")
        print()
        print("💾 Export:")
        print("  /export on/off        - Toggle auto-export")
        print("  /export-dir <path>    - Set export directory")
        print()
        print("📊 Cache & Stats:")
        print("  /stats                - Show cache statistics")
        print("  /cache stats          - Detailed cache statistics")
        print("  /cache clear [tier]   - Clear cache (hot/disk/memory/all)")
        print("  /promote <text>       - Promote text to hot cache")
        print()
        print("🖥️ Server:")
        print("  /server               - Show server debug information")
        print("  /health               - Check server health")
        print("  /monitor [duration]   - Monitor server continuously")
        print()
        print("🔧 Other:")
        print("  /settings             - Show current settings")
        print("  /debug                - Show debug information")
        print("  /help                 - Show this help")
        print("  /quit                 - Exit interactive mode")
        print()
        print("💬 To speak text, just type it without a command prefix")
    
    def _show_settings(self) -> None:
        """Show current interactive settings"""
        print("\\n⚙️ Current Settings:")
        print("=" * 30)
        for key, value in self.interactive_settings.items():
            print(f"  {key}: {value}")
    
    def _list_voices(self) -> None:
        """List available voices"""
        voices = self.tts_service.tts_client.available_voices
        if voices:
            print(f"\\n🎵 Available Voices ({len(voices)}):")
            print("=" * 40)
            for voice_id, voice_info in sorted(voices.items()):
                name = voice_info.get('name', voice_id)
                description = voice_info.get('description', 'No description')
                print(f"  {voice_id}: {name} - {description}")
        else:
            print("❌ No voices discovered. Check server connection.")
    
    def _show_cache_stats(self) -> None:
        """Show cache statistics"""
        stats = self.tts_service.get_cache_statistics()
        print(f"\\n📊 Cache Statistics:")
        print("=" * 30)
        print(f"  Total entries: {stats['total']['entries']}")
        print(f"  Memory usage: {stats['total']['memory_mb']:.1f}MB")
        print(f"  Disk usage: {stats['total']['disk_mb']:.1f}MB")
    
    def _show_detailed_cache_stats(self) -> None:
        """Show detailed cache statistics"""
        stats = self.tts_service.get_cache_statistics()
        print(f"\\n📊 Detailed Cache Statistics:")
        print("=" * 40)
        
        print("🔥 Hot Cache:")
        hot = stats['hot_cache']
        print(f"  Entries: {hot['entries']}")
        print(f"  Memory: {hot['memory_mb']:.1f}MB")
        
        print("\\n💾 Disk Cache:")
        disk = stats['disk_cache']
        print(f"  Entries: {disk['entries']}")
        print(f"  Size: {disk['size_mb']:.1f}MB")
        
        print("\\n🔄 LRU Cache:")
        lru = stats['memory_cache']
        print(f"  Entries: {lru['size']}")
        print(f"  Memory: {lru['memory_mb']:.1f}MB")
        print(f"  Hit rate: {lru.get('hit_rate', 0):.1f}%")
    
    def _show_debug_info(self) -> None:
        """Show debug information"""
        print("\\n🔧 Debug Information:")
        print("=" * 30)
        print(f"  Base URL: {self.tts_service.base_url}")
        print(f"  Notification mode: {self.tts_service.notification_mode}")
        print(f"  Quiet mode: {self.tts_service.quiet_mode}")
        print(f"  Preload enabled: {self.tts_service.preload_enabled}")
        print(f"  Background worker: {self.tts_service.background_executor.is_alive() if self.tts_service.background_executor else 'Not started'}")
        print(f"  Temp files: {len(self.tts_service.temp_files)}")
    
    def run_single_command(
        self,
        text: str,
        voice: str = "af_bella",
        speed: float = 1.0,
        format_type: str = "wav",
        export: bool = False,
        export_filename: Optional[str] = None,
        export_dir: Optional[str] = None,
        background: bool = False,
        stream: bool = False,
        quiet: bool = False
    ) -> bool:
        """
        Run a single TTS command (non-interactive).
        
        Args:
            text: Text to speak
            voice: Voice to use
            speed: Speech speed
            format_type: Audio format
            export: Export to file
            export_filename: Custom export filename
            export_dir: Export directory
            background: Play in background
            stream: Use streaming
            quiet: Suppress output
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Export if requested
            if export:
                exported_file = self.tts_service.export_manager.export_audio(
                    text=text,
                    filename=export_filename,
                    voice=voice,
                    speed=speed,
                    format_type=format_type,
                    export_dir=export_dir,
                    play_audio=not quiet  # Don't play if quiet
                )
                
                if not exported_file:
                    return False
            else:
                # Just speak the text
                if not quiet:
                    self.tts_service.speak_text(
                        text=text,
                        voice=voice,
                        speed=speed,
                        format_type=format_type,
                        background=background,
                        stream=stream
                    )
            
            return True
            
        except Exception as e:
            if not quiet:
                print(f"❌ Command failed: {e}")
            logger.exception("Single command failed")
            return False