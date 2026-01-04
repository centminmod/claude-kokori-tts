"""
Configuration module for the TTS system.

This module provides configuration loading and CLI configuration objects.
Layer 2 - Core Services: Depends on Layer 1.
"""

from .loader import ConfigurationLoader
from .cli_config import (
    CLIConfig,
    AudioConfig,
    OutputConfig,
    ServerConfig,
    OperationConfig
)

__all__ = [
    'ConfigurationLoader',
    'CLIConfig',
    'AudioConfig',
    'OutputConfig',
    'ServerConfig',
    'OperationConfig'
]