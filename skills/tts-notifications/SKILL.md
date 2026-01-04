---
name: tts-notifications
description: Use TTS to speak notifications, alerts, and important messages to the user. Invoke when the user requests audio feedback, task completion announcements, or error notifications that should be spoken aloud.
allowed-tools:
  - Bash
---

# TTS Notifications Skill

This skill enables Claude to speak text aloud using the Kokoro TTS system.

## When to Use

Invoke this skill when:
- User explicitly asks for audio/spoken output
- Task completion notifications would benefit from being spoken
- Error announcements that should grab user attention
- User has indicated preference for audio feedback
- Accessibility needs require spoken feedback

## How to Use

Execute the TTS wrapper script to speak a message:

```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/tts-wrapper.sh" speak "Your message here"
```

## Quick Notification Mode

For non-blocking notifications:

```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/tts-wrapper.sh" speak -n -b -q "Quick notification"
```

Options:
- `-n, --notification` - Optimized for quick notifications (reduced timeout)
- `-b, --background` - Play in background without blocking
- `-q, --quiet` - Suppress text output

## Voice Selection

Use a specific voice or blend:

```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/tts-wrapper.sh" speak --voice af_bella "Message"
"${CLAUDE_PLUGIN_ROOT}/scripts/tts-wrapper.sh" speak --voice "af_bella+af_sky" "Blended"
```

## Common Preloaded Messages

These messages are preloaded for instant playback:
- "Build completed successfully"
- "Build failed"
- "Error: Command failed"
- "Tests passed"
- "Tests failed"
- "Task completed"
- "Processing"
- "Warning"

## Example Scenarios

### Task Completion
```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/tts-wrapper.sh" speak -n -b "Task completed successfully"
```

### Error Alert
```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/tts-wrapper.sh" speak "Error: Build failed with 3 errors"
```

### Progress Update
```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/tts-wrapper.sh" speak -n -q "Processing step 2 of 5"
```

## Requirements

- Kokoro TTS server must be running on localhost:8880
- `uv` must be installed for Python dependency management
