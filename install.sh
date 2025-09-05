#!/bin/bash
# Install script for Twitch Chat TTS Bot (Edge-TTS)
set -e

echo "=== Twitch TTS Bot Installation ==="
echo

# Check Python version
if ! command -v python3 >/dev/null 2>&1; then
  echo "❌ Python 3 is not installed. Please install Python 3.8+ and rerun this script."
  exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "✅ Found Python $PYTHON_VERSION"

if ! command -v pip3 >/dev/null 2>&1; then
  echo "❌ pip3 is not installed. Please install pip and rerun this script."
  exit 1
fi

echo "✅ Found pip3"
echo

echo "📦 Installing Python dependencies..."
echo "Installing core dependencies (edge-tts, unidecode)..."
pip3 install edge-tts unidecode

echo "Installing optional dependencies..."
echo "  - pykakasi (Japanese text support) - this may take a while..."
pip3 install pykakasi || echo "⚠️  Warning: Failed to install pykakasi (Japanese support will be disabled)"

# Platform-specific optional dependencies
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
  echo "  - pycaw (Windows audio control)..."
  pip3 install pycaw || echo "⚠️  Warning: Failed to install pycaw (audio ducking will be disabled)"
else
  echo "  - Skipping pycaw (Windows-only dependency)"
fi

echo

echo "🎵 Checking for FFmpeg..."
if ! command -v ffplay >/dev/null 2>&1; then
  echo "❌ FFmpeg (ffplay) not found in PATH."
  echo "Please install FFmpeg:"
  echo "  - macOS: brew install ffmpeg"
  echo "  - Ubuntu/Debian: sudo apt install ffmpeg"
  echo "  - Or download from: https://ffmpeg.org/download.html"
  echo "After installation, make sure ffplay is in your PATH."
  exit 1
fi

echo "✅ Found FFmpeg"
echo

echo "🎉 Installation complete!"
echo
echo "Next steps:"
echo "1. Edit config.txt with your Twitch channel and settings"
echo "2. Run the bot with: python3 Twitch_TTS.py"
echo
echo "Platform: $(uname -s)"
echo "Optional features available:"
if pip3 show pykakasi >/dev/null 2>&1; then
  echo "✅ Japanese text romanization (pykakasi)"
else
  echo "❌ Japanese text romanization (install pykakasi for this feature)"
fi

# Platform-specific audio ducking info
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
  if pip3 show pycaw >/dev/null 2>&1; then
    echo "✅ Windows audio ducking (pycaw)"
  else
    echo "❌ Audio ducking (requires pycaw)"
  fi
else
  echo "ℹ️  Audio ducking: Not available on this platform (Windows only)"
  echo "    TTS will still work perfectly! Audio ducking automatically lowers"
  echo "    other app volumes while TTS is speaking (Windows feature only)."
fi

echo
echo "🔊 Audio output: The bot uses ffplay for TTS playback"
echo "   You can control TTS volume with the TTS_VOLUME setting in config.txt"
