---
description: Test TTS system connectivity and functionality
argument-hint: "[--test-quick | --test-all]"
allowed-tools:
  - Bash
---

# Test TTS System

Run system tests to verify Kokoro server connectivity and TTS functionality.

```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/tts-wrapper.sh" test $ARGUMENTS
```

## Test Modes

- `/claude-kokoro-tts:test` - Basic connectivity test
- `/claude-kokoro-tts:test --test-quick` - Quick 4-test suite
- `/claude-kokoro-tts:test --test-all` - Comprehensive 10-test suite

## What's Tested

- Server health endpoint
- Voice discovery
- Audio generation
- Cache functionality
- Voice blending (in comprehensive mode)
