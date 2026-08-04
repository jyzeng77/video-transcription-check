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

# Step 5: Install llama.cpp (for the optional local LLM consolidation)
echo
echo "Step 5: Install llama.cpp."
LLAMA_SERVER_BIN="$(command -v llama-server || true)"
if [ -n "$LLAMA_SERVER_BIN" ]; then
    ok "llama-server found at $LLAMA_SERVER_BIN"
elif [ -x "./bin/llama-server" ]; then
    ok "llama-server found at $(pwd)/bin/llama-server"
else
    case "$(uname -s)" in
        Darwin)
            if command -v brew &>/dev/null; then
                if brew install llama.cpp --quiet; then
                    ok "llama.cpp installed via Homebrew."
                else
                    fail "Failed to install llama.cpp."
                    exit 1
                fi
            else
                fail "Homebrew is required to install llama.cpp on macOS."
                echo "  Install it from https://brew.sh"
                exit 1
            fi
            ;;
        Linux)
            echo "  Downloading llama.cpp binaries..."
            LLAMA_TAG="$(curl -s https://api.github.com/repos/ggml-org/llama.cpp/releases/latest | grep '"tag_name"' | head -1 | cut -d'"' -f4)"
            if [ -z "$LLAMA_TAG" ]; then
                fail "Could not determine the latest llama.cpp release."
                exit 1
            fi
            mkdir -p bin
            if curl -sL -o /tmp/llama-bin.zip "https://github.com/ggml-org/llama.cpp/releases/download/${LLAMA_TAG}/llama-${LLAMA_TAG}-bin-ubuntu-x64.zip" \
                && unzip -oq /tmp/llama-bin.zip -d bin; then
                ok "llama.cpp binaries installed into ./bin (release ${LLAMA_TAG})."
            else
                fail "Failed to download llama.cpp binaries."
                exit 1
            fi
            ;;
        MINGW*|MSYS*|CYGWIN*)
            echo "  Downloading llama.cpp binaries..."
            LLAMA_TAG="$(curl -s https://api.github.com/repos/ggml-org/llama.cpp/releases/latest | grep '"tag_name"' | head -1 | cut -d'"' -f4)"
            if [ -z "$LLAMA_TAG" ]; then
                fail "Could not determine the latest llama.cpp release."
                exit 1
            fi
            mkdir -p bin
            if curl -sL -o /tmp/llama-bin.zip "https://github.com/ggml-org/llama.cpp/releases/download/${LLAMA_TAG}/llama-${LLAMA_TAG}-bin-win-cpu-x64.zip" \
                && unzip -oq /tmp/llama-bin.zip -d bin; then
                ok "llama.cpp binaries installed into ./bin (release ${LLAMA_TAG})."
            else
                fail "Failed to download llama.cpp binaries."
                exit 1
            fi
            ;;
        *)
            fail "Unsupported operating system for llama.cpp."
            exit 1
            ;;
    esac
fi

# Step 6: Download the local LLM model (for consolidation)
echo
echo "Step 6: Download the local LLM model."
MODEL_DIR="models"
MODEL_NAME="qwen2.5-1.5b-instruct-q4_k_m.gguf"
MODEL_URL="https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/${MODEL_NAME}"
if [ -f "${MODEL_DIR}/${MODEL_NAME}" ]; then
    ok "Model already present at ${MODEL_DIR}/${MODEL_NAME}."
else
    echo "  Downloading ~1 GB model (only needed once, then cached locally)..."
    mkdir -p "$MODEL_DIR"
    if curl -sL -o "${MODEL_DIR}/${MODEL_NAME}" "$MODEL_URL"; then
        ok "Model downloaded to ${MODEL_DIR}/${MODEL_NAME}."
    else
        rm -f "${MODEL_DIR}/${MODEL_NAME}"
        fail "Failed to download the model."
        echo "  Check your internet connection and try again."
        exit 1
    fi
fi

# Done
echo
echo "Setup complete."
echo
echo "Run the tool with:"
echo "  python3 main.py"