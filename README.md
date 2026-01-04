# Claude Kokoro TTS Plugin

Text-to-speech integration for Claude Code using Kokoro-FastAPI with voice blending, streaming, and comprehensive format support.

## What This Plugin Installs

### Plugin Files (in Claude Code's plugin cache)

| Directory | Contents | Purpose |
|-----------|----------|---------|
| `.claude-plugin/` | `plugin.json` | Plugin manifest |
| `commands/` | 8 markdown files | Slash command definitions |
| `hooks/` | `hooks.json` | Automatic TTS notifications on events |
| `scripts/` | 4 scripts | Python wrapper + notification scripts |
| `python/` | `claude_tts.py` + `modules/` | TTS Python code (~7,500 lines) |
| `skills/` | `SKILL.md` | TTS notification skill |

**Note**: Plugin files are copied to Claude Code's plugin cache directory when installed. The original plugin directory is not modified.

### Files Created on Your System

| Location | Purpose | Size |
|----------|---------|------|
| `~/.claude_tts/cache/` | Audio cache (speeds up repeated phrases) | Up to 1GB |
| `~/.claude_tts/config.yml` | User configuration file (optional) | <1KB |
| `~/.claude_tts/preload.json` | Custom preload messages (optional) | <1KB |

These directories are created automatically on first use and persist across plugin updates.

### Configuration File (NEW in v1.2.0)

Create a `.claude_tts.yml` file in your project root or `~/.claude_tts/config.yml` to customize defaults:

```yaml
# Server configuration
server:
  url: http://localhost:8880

# Audio settings
audio:
  voice: af_bella      # af_bella, af_sky, am_adam, bf_emma, etc.
  format: wav          # wav, mp3, pcm, opus, flac
  speed: 1.0           # 0.5 to 2.0

# Mode flags
notification: false    # Optimized for Claude Code hooks
quiet: false           # Suppress output
preload: true          # Preload messages at startup
```

**Precedence:** CLI args > project `.claude_tts.yml` > user `~/.claude_tts/config.yml` > hardcoded defaults

### Network Connections

| Destination | Purpose | When |
|-------------|---------|------|
| `localhost:8880` | Kokoro-FastAPI server | Every TTS request |

**No external network calls** - all TTS processing happens locally via your Docker container.

### System Dependencies (User Must Install)

| Dependency | Install Command | Purpose |
|------------|-----------------|---------|
| **uv** | `curl -LsSf https://astral.sh/uv/install.sh \| sh` | Python package manager |
| **Docker** | [docker.com](https://docker.com) | Runs Kokoro server |
| **portaudio** (optional) | `brew install portaudio` | Streaming audio |

### Python Packages (Auto-Installed by uv)

These are installed automatically to an isolated environment when you first run a command:

- `requests>=2.31.0` - HTTP client for API calls
- `pygame>=2.5.0` - Audio playback
- `click>=8.1.0` - CLI framework
- `python-dotenv>=1.0.0` - Environment config
- `pydantic>=2.0.0` - Data validation
- `pyaudio>=0.2.11` - Streaming audio (optional)
- `pyyaml>=6.0` - YAML config (optional)

## Prerequisites

### 1. Install uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# macOS (Homebrew)
brew install uv
```

### 2. Start Kokoro Server

```bash
docker run -d --restart unless-stopped --name kokoro -p 8880:8880 \
  ghcr.io/remsky/kokoro-fastapi-cpu:latest
```

Verify it's running:
```bash
curl http://localhost:8880/health
```

## Installation

### Method 1: Development/Testing (Temporary)

Load the plugin directly for the current session:

```bash
claude --plugin-dir /path/to/claude-kokoro-tts
```

This loads the plugin without installation - useful for testing.

### Method 2: Interactive Installation (Recommended)

Use the `/plugin` command within Claude Code:

```text
/plugin
```

Then browse, install, and enable the plugin interactively.

### Method 3: Manual Settings (Advanced)

Add to your `.claude/settings.json`:

```json
{
  "enabledPlugins": {
    "claude-kokoro-tts": true
  }
}
```

**Note**: The `enabledPlugins` setting is always manual - it is not automatically set during installation. This method requires the plugin files to already be in Claude Code's plugin cache.

## Usage

### Slash Commands

| Command | Example |
|---------|---------|
| Speak text | `/claude-kokoro-tts:speak Hello world!` |
| Voice blend | `/claude-kokoro-tts:speak --voice af_bella+af_sky "Blended"` |
| List voices | `/claude-kokoro-tts:voices` |
| Test setup | `/claude-kokoro-tts:test` |
| Export audio | `/claude-kokoro-tts:export speech.mp3 "Save this"` |
| Interactive mode | `/claude-kokoro-tts:interactive` |
| Phoneme analysis | `/claude-kokoro-tts:phonemes "Hello"` |
| Server stats | `/claude-kokoro-tts:stats` |
| Cache stats | `/claude-kokoro-tts:cache stats` |
| Clear cache | `/claude-kokoro-tts:cache clear all` |

### Voice Blending

Combine voices with `+` syntax:
- `af_bella+af_sky` - Equal mix
- `af_bella(2)+af_sky(1)` - 2:1 weighted ratio

### Quick Notifications

For fast, non-blocking speech:
```
/claude-kokoro-tts:speak -n -b -q "Build complete"
```

Options:
- `-n` - Notification mode (fast)
- `-b` - Background playback (non-blocking)
- `-q` - Quiet (suppress text output)

## Session Startup

On each Claude Code session start, the plugin:
1. Checks if `uv` is installed
2. Checks if Kokoro server is responding on port 8880
3. Prints a warning if either is missing (does not block session)
4. Announces "Session Started" via TTS

## Automatic Notifications

The plugin automatically announces Claude Code events via TTS:

| Event | What's Announced |
|-------|------------------|
| SessionStart | "Session Started" |
| UserPromptSubmit | "Processing: {prompt preview}" |
| Notification | "Input Required: {message}" |
| PreToolUse:Bash | "Wants to run a {command} command" |
| PreToolUse:Write/Edit | "Wants to modify: {file}" |
| PostToolUse:Bash | "Command succeeded" or "Command failed" |
| PostToolUse:Write/Edit | "File saved" |
| SubagentStop | "A subagent task has finished" |
| Stop | "Finished working in {directory}" |
| SessionEnd | "Session ended after {N} turns" |
| PreCompact | "Compacting memory" |
| PermissionRequest | "Permission needed for {tool}" |

### Desktop Notifications (macOS)

If `terminal-notifier` is installed, you also get desktop notifications:

```bash
brew install terminal-notifier
```

Desktop notifications are optional - TTS works without them.

### Disable Automatic Notifications

To use only manual slash commands without automatic TTS:
1. Edit the plugin's `hooks/hooks.json`
2. Remove the events you don't want

## Troubleshooting

### "uv not found"

Install uv:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### "Kokoro server not running"

Start the container:
```bash
docker start kokoro
```

Or run a new container:
```bash
docker run -d --name kokoro -p 8880:8880 ghcr.io/remsky/kokoro-fastapi-cpu:latest
```

### Audio playback issues

Install portaudio (macOS):
```bash
brew install portaudio
```

### First run is slow

The first run downloads Python packages to an isolated environment. Subsequent runs are fast.

## Privacy & Security

- **No telemetry**: Plugin does not send data anywhere
- **Local only**: All TTS processing happens on your machine via Docker
- **Cache location**: `~/.claude_tts/cache/` (you control it)
- **Open source**: Full source code visible in `python/` directory

## Uninstallation

1. Disable plugin:
   ```
   /plugin disable claude-kokoro-tts
   ```

2. Optionally remove cache:
   ```bash
   rm -rf ~/.claude_tts/
   ```

3. Optionally stop Kokoro:
   ```bash
   docker stop kokoro && docker rm kokoro
   ```

## Technical Details

### Architecture

The plugin wraps a Python TTS integration (~7,500 lines) with:
- **5-layer modular architecture** preventing circular dependencies
- **3-tier caching system** (hot memory, disk, LRU)
- **Voice blending** with weighted mixing
- **Multiple audio formats** (WAV, MP3, FLAC, OPUS)

### Cache Tiers

| Tier | Location | Access Time | Capacity |
|------|----------|-------------|----------|
| Hot | Memory | <10ms | ~10MB |
| Disk | `~/.claude_tts/cache/` | ~50ms | 1GB |
| LRU | Memory | ~50ms | 100 items |

### Preloaded Messages

Common messages are preloaded for instant playback:
- "Build completed successfully"
- "Build failed"
- "Tests passed" / "Tests failed"
- "Task completed"
- "Error: Command failed"

## License

MIT

## Contributing

Issues and pull requests welcome at the project repository.
