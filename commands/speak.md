---
description: Speak text using TTS with optional voice and format settings
argument-hint: "<text> [--voice <voice>] [--format <fmt>]"
allowed-tools:
  - Bash
---

# Speak Text

Convert text to speech and play audio using Kokoro-FastAPI.

## Usage

```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/tts-wrapper.sh" speak $ARGUMENTS
```

## Examples

- `/claude-kokoro-tts:speak Hello world!`
- `/claude-kokoro-tts:speak --voice af_bella "Custom voice"`
- `/claude-kokoro-tts:speak --voice "af_bella+af_sky" "Voice blend"`
- `/claude-kokoro-tts:speak --voice "af_bella(2)+af_sky(1)" "Weighted blend"`
- `/claude-kokoro-tts:speak -n -b -q "Quick notification"` (notification mode, background, quiet)

## Options

- `--voice <voice>` - Use specific voice (e.g., af_bella, bf_emma)
- `--format <fmt>` - Output format (wav, mp3, flac, opus)
- `--speed <n>` - Speech speed multiplier
- `-n, --notification` - Quick notification mode (fast)
- `-b, --background` - Play in background (non-blocking)
- `-q, --quiet` - Suppress text output
