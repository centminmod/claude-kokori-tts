#!/bin/bash
# SessionStart hook: Check if Kokoro server and uv are available
# This script warns but does not block session startup

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "⚠️  TTS Plugin: 'uv' is not installed"
    echo "   Install: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 0  # Don't block session, just warn
fi

# Check if Kokoro server is running
if curl -s --connect-timeout 2 http://localhost:8880/health > /dev/null 2>&1; then
    echo "✓ TTS Plugin: Kokoro server ready on port 8880"
else
    echo "⚠️  TTS Plugin: Kokoro server not running on port 8880"
    echo "   Start: docker run -d --name kokoro -p 8880:8880 ghcr.io/remsky/kokoro-fastapi-cpu:latest"
fi

exit 0  # Always exit 0 to not block session
