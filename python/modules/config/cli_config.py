"""
CLI configuration objects for the TTS system.

This module provides configuration dataclasses for organizing CLI parameters.
Layer 2 - Core Services: Depends on Layer 1.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AudioConfig:
    """Configuration for audio-related settings"""
    voice: str = 'af_bella'
    speed: float = 1.0
    format: str = 'wav'
    stream: bool = False
    background: bool = False
    no_normalize: bool = False
    phonemes: bool = False


@dataclass
class OutputConfig:
    """Configuration for output-related settings"""
    quiet: bool = False
    json_output: bool = False
    export: Optional[str] = None
    export_dir: str = '.'


@dataclass
class ServerConfig:
    """Configuration for server-related settings"""
    server_url: str = 'http://localhost:8880'
    notification_mode: bool = False
    debug: bool = False
    no_preload: bool = False
    skip_voice_check: bool = False


@dataclass
class OperationConfig:
    """Configuration for operation flags"""
    # Main operation
    text: Optional[str] = None
    file: Optional[str] = None
    interactive: bool = False
    
    # Test operations
    test: bool = False
    test_all: bool = False
    test_quick: bool = False
    
    # Utility operations
    list_voices: bool = False
    cache_stats: bool = False
    clear_cache: Optional[str] = None
    server_stats: bool = False
    health_check: bool = False
    monitor_server: Optional[int] = None
    
    # Meta operations
    version: bool = False


@dataclass
class CLIConfig:
    """Main configuration object containing all CLI settings"""
    audio: AudioConfig = field(default_factory=AudioConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    server: ServerConfig = field(default_factory=ServerConfig)
    operation: OperationConfig = field(default_factory=OperationConfig)
    
    @classmethod
    def from_click_params(cls, **kwargs) -> 'CLIConfig':
        """
        Create CLIConfig from Click parameters.
        
        Args:
            **kwargs: All Click parameters
            
        Returns:
            CLIConfig instance
        """
        # Create sub-configs
        audio = AudioConfig(
            voice=kwargs.get('voice', 'af_bella'),
            speed=kwargs.get('speed', 1.0),
            format=kwargs.get('format', 'wav'),
            stream=kwargs.get('stream', False),
            background=kwargs.get('background', False),
            no_normalize=kwargs.get('no_normalize', False),
            phonemes=kwargs.get('phonemes', False)
        )
        
        output = OutputConfig(
            quiet=kwargs.get('quiet', False),
            json_output=kwargs.get('json_output', False),
            export=kwargs.get('export'),
            export_dir=kwargs.get('export_dir', '.')
        )
        
        server = ServerConfig(
            server_url=kwargs.get('server', 'http://localhost:8880'),
            notification_mode=kwargs.get('notification', False),
            debug=kwargs.get('debug', False),
            no_preload=kwargs.get('no_preload', False),
            skip_voice_check=kwargs.get('skip_voice_check', False)
        )
        
        operation = OperationConfig(
            text=kwargs.get('text'),
            file=kwargs.get('file'),
            interactive=kwargs.get('interactive', False),
            test=kwargs.get('test', False),
            test_all=kwargs.get('test_all', False),
            test_quick=kwargs.get('test_quick', False),
            list_voices=kwargs.get('list_voices', False),
            cache_stats=kwargs.get('cache_stats', False),
            clear_cache=kwargs.get('clear_cache'),
            server_stats=kwargs.get('server_stats', False),
            health_check=kwargs.get('health_check', False),
            monitor_server=kwargs.get('monitor_server'),
            version=kwargs.get('version', False)
        )
        
        return cls(
            audio=audio,
            output=output,
            server=server,
            operation=operation
        )