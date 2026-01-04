---
description: Start interactive TTS mode for conversational use
allowed-tools:
  - Bash
---

# Interactive Mode

Start an interactive TTS session with real-time commands.

```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/tts-wrapper.sh" interactive
```

## Interactive Commands

Once in interactive mode, you can use these commands:

- `voice <name>` - Set voice (e.g., `voice af_bella+af_sky`)
- `format <fmt>` - Change output format (wav, mp3, etc.)
- `speed <n>` - Set speech speed
- `export on/off` - Toggle export mode
- `export-dir <path>` - Set export directory
- `stats` - Show cache statistics
- `health` - Check server health
- `voices` - List available voices
- `help` - Show command help
- `quit` or `exit` - Exit interactive mode

Type any other text to speak it immediately.

## Note

Interactive mode requires terminal stdin access and may not work in all contexts.
