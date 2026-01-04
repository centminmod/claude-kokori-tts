#!/bin/bash
# Verify uv is installed and provide installation instructions

if command -v uv &> /dev/null; then
    UV_VERSION=$(uv --version 2>/dev/null | head -1)
    echo "✓ uv found: $UV_VERSION"
    exit 0
else
    echo "✗ uv is not installed"
    echo ""
    echo "Install uv using one of these methods:"
    echo ""
    echo "macOS/Linux:"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo ""
    echo "macOS (Homebrew):"
    echo "  brew install uv"
    echo ""
    echo "Windows:"
    echo "  powershell -c \"irm https://astral.sh/uv/install.ps1 | iex\""
    echo ""
    echo "After installation, restart your terminal."
    exit 1
fi
