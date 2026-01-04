# Changelog

All notable changes to the Claude Kokoro TTS Plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2026-01-04

### Added

- **Configuration file support** for overriding script defaults
  - YAML config files: project root `.claude_tts.yml` or user home `~/.claude_tts/config.yml`
  - Precedence: CLI args > project config > user config > hardcoded defaults
  - Configurable: server URL, default voice/format/speed, mode flags (notification, quiet, debug, stream, background, preload)
  - Well-documented config file with commented option descriptions

### Technical

- Based on claude_tts.py v0.1.14
- New `load_cli_defaults()` method in ConfigurationLoader
- Click's `default_map` context setting for seamless config integration

## [1.1.1] - 2026-01-04

### Fixed

- **Critical**: Corrected hooks.json format to match official Claude Code specification
  - Events with matchers (PreToolUse, PostToolUse, PermissionRequest) now use `matcher` field
  - All events now use proper nested `hooks` array structure
  - Consolidated Write/Edit matchers using regex pattern `Write|Edit`

## [1.1.0] - 2026-01-04

### Added

- **Automatic TTS notifications** on Claude Code events
  - SessionStart, UserPromptSubmit, Notification
  - PreToolUse and PostToolUse for Bash, Write, Edit
  - SubagentStop, Stop, SessionEnd
  - PreCompact, PermissionRequest
- Desktop notifications via terminal-notifier (macOS, optional)
- New `unified_notifier.py` script for hook event handling

### Changed

- Updated hooks.json with 14 hook events (was only SessionStart check)
- Improved README with Automatic Notifications section
- Scripts directory now contains 4 files (added unified_notifier.py)

### Technical

- TTS script path now resolved dynamically relative to plugin root
- Desktop notifications fail silently if terminal-notifier not installed
- All hook timeouts set to 15 seconds for TTS completion

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
