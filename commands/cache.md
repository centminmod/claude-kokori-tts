---
description: Manage TTS cache (stats, clear)
argument-hint: "stats | clear [hot|disk|memory|all]"
allowed-tools:
  - Bash
---

# Cache Management

Manage the TTS cache system.

```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/tts-wrapper.sh" cache $ARGUMENTS
```

## Commands

- `/claude-kokoro-tts:cache stats` - Show cache statistics
- `/claude-kokoro-tts:cache clear hot` - Clear hot (memory) cache
- `/claude-kokoro-tts:cache clear disk` - Clear disk cache
- `/claude-kokoro-tts:cache clear memory` - Clear LRU memory cache
- `/claude-kokoro-tts:cache clear all` - Clear all cache tiers

## Cache Tiers

1. **Hot Cache** - Critical messages in memory (<10ms access)
2. **Disk Cache** - Persistent storage at `~/.claude_tts/cache/` (~50ms access)
3. **Memory Cache** - LRU cache for recent messages (~50ms access)

## Note

Clearing the disk cache removes all cached audio files. They will be regenerated on next use.
