---
description: List all available TTS voices including blending examples
allowed-tools:
  - Bash
---

# List Voices

Show all available voices from the Kokoro TTS server.

```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/tts-wrapper.sh" voices
```

## Voice Naming Convention

- `af_*` - American Female voices
- `am_*` - American Male voices
- `bf_*` - British Female voices
- `bm_*` - British Male voices

## Voice Blending

Combine voices with the `+` syntax:
- `af_bella+af_sky` - Equal mix of two voices
- `af_bella(2)+af_sky(1)` - 2:1 weighted blend
