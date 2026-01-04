#!/bin/bash
# Main wrapper script for TTS Python tool
# This script routes commands to the appropriate claude_tts.py flags

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_ROOT="$(dirname "$SCRIPT_DIR")"
PYTHON_DIR="$PLUGIN_ROOT/python"

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Error: 'uv' is not installed. TTS plugin requires uv for dependency management."
    echo ""
    echo "Install uv:"
    echo "  macOS/Linux: curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "  macOS (Homebrew): brew install uv"
    echo ""
    echo "After installation, restart your terminal."
    exit 1
fi

# Check if Kokoro server is running
check_server() {
    if ! curl -s --connect-timeout 2 http://localhost:8880/health > /dev/null 2>&1; then
        echo "Error: Kokoro TTS server is not running on port 8880."
        echo ""
        echo "Start the server with:"
        echo "  docker run -d --name kokoro -p 8880:8880 ghcr.io/remsky/kokoro-fastapi-cpu:latest"
        echo ""
        echo "Or if container exists:"
        echo "  docker start kokoro"
        exit 2
    fi
}

# Parse command
COMMAND="${1:-}"
shift 2>/dev/null || true

case "$COMMAND" in
    speak)
        check_server
        cd "$PYTHON_DIR" && uv run claude_tts.py "$@"
        ;;
    voices)
        check_server
        cd "$PYTHON_DIR" && uv run claude_tts.py --list-voices "$@"
        ;;
    test)
        check_server
        cd "$PYTHON_DIR" && uv run claude_tts.py --test "$@"
        ;;
    test-quick)
        check_server
        cd "$PYTHON_DIR" && uv run claude_tts.py --test-quick "$@"
        ;;
    test-all)
        check_server
        cd "$PYTHON_DIR" && uv run claude_tts.py --test-all "$@"
        ;;
    export)
        check_server
        cd "$PYTHON_DIR" && uv run claude_tts.py --export "$@"
        ;;
    interactive)
        check_server
        cd "$PYTHON_DIR" && uv run claude_tts.py --interactive "$@"
        ;;
    phonemes)
        check_server
        cd "$PYTHON_DIR" && uv run claude_tts.py --phonemes "$@"
        ;;
    stats)
        check_server
        cd "$PYTHON_DIR" && uv run claude_tts.py --server-stats "$@"
        ;;
    health)
        check_server
        cd "$PYTHON_DIR" && uv run claude_tts.py --health-check "$@"
        ;;
    cache)
        CACHE_CMD="${1:-stats}"
        shift 2>/dev/null || true
        case "$CACHE_CMD" in
            stats)
                cd "$PYTHON_DIR" && uv run claude_tts.py --cache-stats "$@"
                ;;
            clear)
                TIER="${1:-all}"
                cd "$PYTHON_DIR" && uv run claude_tts.py --clear-cache "$TIER"
                ;;
            *)
                echo "Unknown cache command: $CACHE_CMD"
                echo "Usage: cache stats | cache clear [hot|disk|memory|all]"
                exit 1
                ;;
        esac
        ;;
    help)
        echo "Claude Kokoro TTS Plugin - Command Reference"
        echo ""
        echo "Commands:"
        echo "  speak <text>       - Speak text (default)"
        echo "  voices             - List available voices"
        echo "  test               - Basic connectivity test"
        echo "  test-quick         - Quick 4-test suite"
        echo "  test-all           - Comprehensive 10-test suite"
        echo "  export <text>      - Export audio to file"
        echo "  interactive        - Start interactive mode"
        echo "  phonemes <text>    - Show phoneme breakdown"
        echo "  stats              - Show server statistics"
        echo "  health             - Quick health check"
        echo "  cache stats        - Show cache statistics"
        echo "  cache clear [tier] - Clear cache (hot|disk|memory|all)"
        echo "  help               - Show this help"
        echo ""
        echo "Options (for speak/export):"
        echo "  --voice <voice>    - Use specific voice (e.g., af_bella)"
        echo "  --voice <blend>    - Voice blend (e.g., af_bella+af_sky)"
        echo "  --format <fmt>     - Output format (wav|mp3|flac|opus)"
        echo "  --speed <n>        - Speech speed multiplier"
        echo "  -n, --notification - Quick notification mode"
        echo "  -b, --background   - Play in background"
        echo "  -q, --quiet        - Suppress text output"
        ;;
    "")
        echo "Usage: tts-wrapper.sh <command> [options]"
        echo "Run 'tts-wrapper.sh help' for command list"
        exit 1
        ;;
    *)
        # If no recognized command, treat as text to speak
        check_server
        cd "$PYTHON_DIR" && uv run claude_tts.py "$COMMAND" "$@"
        ;;
esac
