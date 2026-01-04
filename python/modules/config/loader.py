"""
Configuration loading and management for the TTS system.

This module handles loading configuration from various sources including YAML, JSON, and text files.
Layer 2 - Core Services: Depends only on Layer 1 (Foundation) and external libraries.
"""

import json
import logging
from typing import List, Dict, Any, Set, Optional
from pathlib import Path

from modules.types.data_models import PreloadMessage
from modules.types.protocols import ConfigurationProtocol
from modules.filesystem.file_utils import get_config_directory, safe_file_read

# Optional YAML support
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

logger = logging.getLogger(__name__)


# Import DEFAULT_PRELOAD_MESSAGES from constants to avoid duplication
from modules.types.constants import DEFAULT_PRELOAD_MESSAGES


class ConfigurationLoader(ConfigurationProtocol):
    """Configuration loader for TTS system"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize configuration loader.
        
        Args:
            config_dir: Configuration directory (default: ~/.claude_tts)
        """
        self.config_dir = config_dir or get_config_directory()
    
    def load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Load configuration from file or environment.
        
        Args:
            config_path: Optional path to config file
            
        Returns:
            Configuration dictionary
        """
        if config_path:
            return self._load_config_file(Path(config_path))
        
        # Try default locations
        yaml_path = self.config_dir / 'config.yml'
        json_path = self.config_dir / 'config.json'
        
        if HAS_YAML and yaml_path.exists():
            return self._load_yaml_config(yaml_path)
        elif json_path.exists():
            return self._load_json_config(json_path)
        
        return {}
    
    def get_preload_messages(self) -> List[PreloadMessage]:
        """
        Load preload messages from configuration files.
        
        Returns:
            List of preload messages
        """
        messages = []
        
        # Try YAML configuration first (if available)
        yaml_path = self.config_dir / 'preload.yml'
        if HAS_YAML and yaml_path.exists():
            try:
                content = safe_file_read(yaml_path)
                if content:
                    config = yaml.safe_load(content)
                    if config:
                        # Load preload messages
                        for msg_data in config.get('messages', []):
                            if isinstance(msg_data, dict):
                                messages.append(PreloadMessage(**msg_data))
            except Exception as e:
                logger.error(f"Failed to load YAML preload config: {e}")
        
        # Try JSON configuration (fallback or alternative)
        json_path = self.config_dir / 'preload.json'
        if json_path.exists() and not messages:  # Only if YAML didn't load messages
            try:
                content = safe_file_read(json_path)
                if content:
                    config = json.loads(content)
                    
                    # Load preload messages
                    for msg_data in config.get('messages', []):
                        if isinstance(msg_data, dict):
                            messages.append(PreloadMessage(**msg_data))
            except Exception as e:
                logger.error(f"Failed to load JSON preload config: {e}")
        
        # Always check text file (merge with JSON/YAML)
        txt_path = self.config_dir / 'preload.txt'
        if txt_path.exists():
            try:
                content = safe_file_read(txt_path)
                if content:
                    for line in content.splitlines():
                        line = line.strip()
                        if line and not line.startswith('#'):
                            # Check if already exists
                            if not any(msg.text == line for msg in messages):
                                messages.append(PreloadMessage(text=line))
            except Exception as e:
                logger.error(f"Failed to load text preload config: {e}")
        
        # Use defaults if no config
        if not messages:
            messages = [PreloadMessage(text=msg) for msg in DEFAULT_PRELOAD_MESSAGES]
        
        return messages
    
    def load_preload_messages(self) -> List[str]:
        """
        Load preload messages as simple strings.
        
        Returns:
            List of preload message strings
        """
        preload_msgs = self.get_preload_messages()
        return [msg.text for msg in preload_msgs]
    
    def get_hot_cache_messages(self) -> Set[str]:
        """
        Get hot cache messages from configuration.
        
        Returns:
            Set of messages that should be kept in hot cache
        """
        hot_cache_keys = set()
        
        # Try YAML configuration first
        yaml_path = self.config_dir / 'preload.yml'
        if HAS_YAML and yaml_path.exists():
            try:
                content = safe_file_read(yaml_path)
                if content:
                    config = yaml.safe_load(content)
                    if config:
                        hot_cache_list = config.get('hot_cache', [])
                        for msg in hot_cache_list:
                            if isinstance(msg, str):
                                hot_cache_keys.add(msg.lower())
            except Exception as e:
                logger.error(f"Failed to load YAML hot cache config: {e}")
        
        # Try JSON configuration
        json_path = self.config_dir / 'preload.json'
        if json_path.exists() and not hot_cache_keys:
            try:
                content = safe_file_read(json_path)
                if content:
                    config = json.loads(content)
                    hot_cache_list = config.get('hot_cache', [])
                    for msg in hot_cache_list:
                        if isinstance(msg, str):
                            hot_cache_keys.add(msg.lower())
            except Exception as e:
                logger.error(f"Failed to load JSON hot cache config: {e}")
        
        # Default hot cache messages if none configured
        if not hot_cache_keys:
            hot_cache_keys = {
                "claude code session complete",
                "build completed successfully", 
                "tests passed"
            }
        
        return hot_cache_keys
    
    def _load_config_file(self, config_path: Path) -> Dict[str, Any]:
        """Load configuration from specific file"""
        if config_path.suffix.lower() in ['.yml', '.yaml']:
            return self._load_yaml_config(config_path)
        elif config_path.suffix.lower() == '.json':
            return self._load_json_config(config_path)
        else:
            logger.warning(f"Unsupported config file format: {config_path}")
            return {}
    
    def _load_yaml_config(self, yaml_path: Path) -> Dict[str, Any]:
        """Load YAML configuration"""
        if not HAS_YAML:
            logger.warning("YAML support not available")
            return {}
        
        try:
            content = safe_file_read(yaml_path)
            if content:
                return yaml.safe_load(content) or {}
        except Exception as e:
            logger.error(f"Failed to load YAML config from {yaml_path}: {e}")
        
        return {}
    
    def _load_json_config(self, json_path: Path) -> Dict[str, Any]:
        """Load JSON configuration"""
        try:
            content = safe_file_read(json_path)
            if content:
                return json.loads(content)
        except Exception as e:
            logger.error(f"Failed to load JSON config from {json_path}: {e}")
        
        return {}