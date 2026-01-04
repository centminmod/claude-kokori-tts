"""
Testing module for TTS system functionality tests.

This module provides comprehensive testing capabilities for the TTS system.
Layer 5 - Orchestration: Depends on all other layers.
"""

from .test_operations import run_tests

__all__ = ['run_tests']