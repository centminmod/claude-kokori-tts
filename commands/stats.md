---
description: Show server health and cache statistics
argument-hint: "[--json]"
allowed-tools:
  - Bash
---

# Server & Cache Stats

Show comprehensive server and cache statistics.

```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/tts-wrapper.sh" stats $ARGUMENTS
```

## What's Shown

- Server health status
- Available voices count
- Cache tier statistics (hot, disk, memory)
- Memory usage
- Response times

## Options

- `--json` - Output in JSON format for automation
