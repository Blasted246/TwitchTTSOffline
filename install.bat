@echo off
REM Install script for Twitch Chat TTS Bot (Edge-TTS)

echo === Twitch TTS Bot Installation ===
echo.

REM Check Python
where python >nul 2>nul || (
  echo ❌ Python is not installed. Please install Python 3.8+ and rerun this script.
  pause
  exit /b 1
)

for /f "tokens=*" %%i in ('python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"') do set PYTHON_VERSION=%%i
echo ✅ Found Python %PYTHON_VERSION%

where pip >nul 2>nul || (
  echo ❌ pip is not installed. Please install pip and rerun this script.
  pause
  exit /b 1
)

echo ✅ Found pip
echo.

echo 📦 Installing Python dependencies...
echo Installing core dependencies (edge-tts, unidecode)...
pip install edge-tts unidecode || (
  echo ❌ Failed to install core dependencies.
  pause
  exit /b 1
)

echo Installing optional dependencies...
echo   - pykakasi (Japanese text support) - this may take a while...
pip install pykakasi || echo ⚠️  Warning: Failed to install pykakasi (Japanese support will be disabled)

echo   - pycaw (Windows audio control)...
pip install pycaw || echo ⚠️  Warning: Failed to install pycaw (audio ducking will be disabled)

echo.

echo 🎵 Checking for FFmpeg...
where ffplay >nul 2>nul || (
  echo ❌ FFmpeg (ffplay) not found in PATH.
  echo Please install FFmpeg:
  echo   - Download from: https://ffmpeg.org/download.html
  echo   - Extract and add ffmpeg\bin to your PATH
  echo   - Or use package manager like Chocolatey: choco install ffmpeg
  pause
  exit /b 1
)

echo ✅ Found FFmpeg
echo.

echo 🎉 Installation complete!
echo.
echo Next steps:
echo 1. Edit config.txt with your Twitch channel and settings
echo 2. Run the bot with: python Twitch_TTS.py
echo    or double-click Startup.bat
echo.
echo Platform: Windows
echo Optional features available:
pip show pykakasi >nul 2>nul && (
  echo ✅ Japanese text romanization (pykakasi)
) || (
  echo ❌ Japanese text romanization (install pykakasi for this feature)
)

pip show pycaw >nul 2>nul && (
  echo ✅ Windows audio ducking (pycaw)
  echo    - Automatically lowers other app volumes during TTS
) || (
  echo ❌ Audio ducking (requires pycaw)
  echo    - Install with: pip install pycaw
)

echo.
echo 🔊 Audio output: The bot uses ffplay for TTS playback
echo    You can control TTS volume with the TTS_VOLUME setting in config.txt
echo    Audio ducking will automatically lower other apps during TTS (Windows exclusive)

pause