#!/bin/bash
# Install script for Twitch Chat TTS Bot (Edge-TTS)
set -e

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 is not installed. Please install Python 3.8+ and rerun this script."
  exit 1
fi

if ! command -v pip3 >/dev/null 2>&1; then
  echo "pip3 is not installed. Please install pip and rerun this script."
  exit 1
fi

echo "Installing Python dependencies..."
pip3 install -r requirements.txt

echo "Checking for FFmpeg..."
if ! command -v ffplay >/dev/null 2>&1; then
  echo "FFmpeg (ffplay) not found in PATH."
  echo "Please download FFmpeg from https://ffmpeg.org/download.html and add ffmpeg/bin to your PATH."
  exit 1
fi

echo
echo "Installation complete!"
echo "1. Edit config.txt with your Twitch channel and settings."
echo "2. Run the bot with: python3 Twitch_TTS.py"
