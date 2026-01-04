---
description: Show phoneme breakdown for text
argument-hint: "<text>"
allowed-tools:
  - Bash
---

# Phoneme Analysis

Convert text to phonemes and show the breakdown. Useful for understanding how text will be pronounced.

```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/tts-wrapper.sh" phonemes $ARGUMENTS
```

## Example

`/claude-kokoro-tts:phonemes "Hello world"`

This shows how the TTS engine will interpret and pronounce the text using IPA-like phoneme notation.
