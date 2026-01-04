# Changelog

All notable changes to the Claude Kokoro TTS Plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-04

### Added

- Initial release as Claude Code plugin
- 8 slash commands: speak, voices, test, export, interactive, phonemes, stats, cache
- SessionStart hook for automatic server verification
- TTS notifications skill for Claude to invoke automatically
- Voice blending with weighted mixing (e.g., `af_bella(2)+af_sky(1)`)
- 3-tier caching system (hot, disk, LRU)
- Multiple audio format support (WAV, MP3, FLAC, OPUS)
- Notification mode for quick, non-blocking speech
- Comprehensive README with transparency documentation

### Technical

- Based on claude_tts.py v0.1.13
- ~7,500 lines of Python code across 38 modules
- 5-layer modular architecture
- PEP 723 inline dependencies for uv compatibility
