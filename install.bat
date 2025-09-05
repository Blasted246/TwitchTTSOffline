@echo off
REM Install script for Twitch Chat TTS Bot (Edge-TTS)

where python >nul 2>nul || (
  echo Python is not installed. Please install Python 3.8+ and rerun this script.
  pause
  exit /b 1
)

where pip >nul 2>nul || (
  echo pip is not installed. Please install pip and rerun this script.
  pause
  exit /b 1
)

echo Installing Python dependencies...
pip install -r requirements.txt || (
  echo Failed to install Python dependencies.
  pause
  exit /b 1
)

echo Checking for FFmpeg...
where ffplay >nul 2>nul || (
  echo FFmpeg (ffplay) not found in PATH.
  echo Please download FFmpeg from https://ffmpeg.org/download.html and add ffmpeg\bin to your PATH.
  pause
  exit /b 1
)

echo.
echo Installation complete!
echo 1. Edit config.txt with your Twitch channel and settings.
echo 2. Run the bot with: python Twitch_TTS.py
echo    or double-click Startup.bat
pause