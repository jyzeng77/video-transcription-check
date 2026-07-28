#!/usr/bin/env bash
set -euo pipefail

RED="\033[91m"
GREEN="\033[92m"
YELLOW="\033[93m"
RESET="\033[0m"

ok() {
    printf "${GREEN}✓${RESET} %s\n" "$1"
}

warn() {
    printf "${YELLOW}!${RESET} %s\n" "$1"
}

fail() {
    printf "${RED}✗${RESET} %s\n" "$1"
}

VENV_DIR="venv"

echo "Video Transcription And Comparison Tool - Setup"
echo "================================================"
echo

# Step 1: Check Python
echo "Step 1: Check Python."
if command -v python3 &>/dev/null; then
    PY="$(command -v python3)"
    VERSION="$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
    MAJOR="$(echo "$VERSION" | cut -d. -f1)"
    MINOR="$(echo "$VERSION" | cut -d. -f2)"
    if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 8 ]; then
        ok "Python $VERSION found at $PY"
    else
        fail "Python 3.8 or later is required. Found: Python $VERSION"
        exit 1
    fi
else
    fail "Python 3 is not installed."
    echo "  Install it from https://www.python.org/downloads/"
    exit 1
fi

# Step 2: Create virtual environment
echo
echo "Step 2: Create virtual environment."
if [ -d "$VENV_DIR" ]; then
    ok "Virtual environment already exists at $VENV_DIR."
else
    if python3 -m venv "$VENV_DIR"; then
        ok "Virtual environment created at $VENV_DIR."
    else
        fail "Failed to create virtual environment."
        exit 1
    fi
fi

# Step 3: Install packages in the virtual environment
echo
echo "Step 3: Install Python packages."
if "$VENV_DIR/bin/pip" install -r requirements.txt --quiet; then
    ok "Packages installed."
else
    fail "Failed to install Python packages."
    exit 1
fi

#
# Step 4: Check FFmpeg
echo
echo "Step 4: Check FFmpeg."
if command -v ffmpeg &>/dev/null; then
    ok "FFmpeg found at $(command -v ffmpeg)"
else
    warn "FFmpeg is not installed."
    echo "  Install it with:"
    echo "    macOS:   brew install ffmpeg"
    echo "    Linux:   sudo apt update && sudo apt install ffmpeg"
    echo "    Windows: https://ffmpeg.org/download.html"
    echo
    echo "  FFmpeg is required for video transcription."
fi

# Done
echo
echo "Setup complete."
echo
echo "To activate the virtual environment, run:"
echo "  source $VENV_DIR/bin/activate"
echo
echo "Then run the tool with:"
echo "  python3 main.py"