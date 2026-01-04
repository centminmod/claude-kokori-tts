---
description: Export speech to audio file (WAV, MP3, FLAC, OPUS)
argument-hint: "[filename] <text> [--voice <voice>] [--quiet]"
allowed-tools:
  - Bash
---

# Export Audio

Export speech to an audio file.

```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/tts-wrapper.sh" export $ARGUMENTS
```

## Examples

- `/claude-kokoro-tts:export "Hello world"` - Auto-generate filename
- `/claude-kokoro-tts:export speech.mp3 "Hello world"` - Custom filename
- `/claude-kokoro-tts:export --voice af_bella+af_sky "Blended voice"` - Export voice blend
- `/claude-kokoro-tts:export --quiet "Hello world"` - Export without playback

## Supported Formats

- WAV (default, best compatibility)
- MP3 (compressed)
- FLAC (lossless compression)
- OPUS (high compression)

Format is auto-detected from filename extension, or use `--format`.
