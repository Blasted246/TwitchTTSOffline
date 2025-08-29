
# Twitch Chat TTS Bot (Offline / Edge-TTS)

Have a local TTS service read your Twitch Chat for you!  
Reads all chat messages except your own and speaks them aloud using **Edge-TTS** (modern neural voices).

---

## Manual Prerequisites

This project relies on Python 3.8+ and the following things:

- **Edge-TTS** (uses Microsoft Edge neural voices, requires `edge-tts` Python package and `ffmpeg` for audio playback).
- (Windows) Per‑app volume ducking uses `pycaw`; on non‑Windows, TTS still works but ducking is disabled.
---

### Installing Python

Make sure Python 3.8 or newer is installed on your system:  
- [Download Python](https://www.python.org/downloads/)  
- Verify installation with:

```bash
python --version
```

---

### Installing dependencies

```bash
pip install -r requirements.txt
```

* **REQUIRED:** Install FFmpeg to play audio output

  * Download from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
  * Follow platform-specific installation instructions to add `ffmpeg` to your system PATH.

---

## Usage with requirements.txt

1. Clone this repository or download the script.
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Run the bot:

```bash
python Twitch_TTS.py
```

On Windows, you can also double‑click `Startup.bat` after editing `config.txt`.

4. The bot will join your specified channel and read aloud all chat messages except your own.

---

## Configuration

Edit `config.txt`:

- `CHANNEL_NAME`: Your Twitch channel (without the `#`).
- `NAME_REPEAT_COOLDOWN`: Seconds before repeating the username in TTS (default `15`).
- `TTS_VOLUME`: TTS loudness 0.0–1.0 (default `1.0`).
- `TTS_ATTENUATION`: Relative multiplier to duck other apps during TTS (default `0.5`).
- `TTS_VOICE`: Edge-TTS neural voice name (default `en-GB-RyanNeural`). Examples: `en-US-GuyNeural`, `en-GB-SoniaNeural`, `ja-JP-NanamiNeural`.
- `ATTENUATION_EXCLUDE_PROCESSES`: Comma-separated process names to exclude from ducking (optional).
- `ATTENUATION_DELAY_MS`: Fade duration and pre-duck delay in ms (default `100`).
- `IGNORE_USERS`: Comma-separated usernames to ignore (case-insensitive).

Notes:
- `ffplay.exe` is excluded from ducking automatically so TTS playback is unaffected.
- Ducking is applied once per burst of messages and restored after a brief grace (uses `ATTENUATION_DELAY_MS`).

### Choosing a voice
- Official voice list (names to use in `TTS_VOICE`):
  - https://learn.microsoft.com/azure/ai-services/speech-service/language-support?tabs=tts
- Voice gallery with audio samples:
  - https://speech.microsoft.com/portal/voicegallery

---

## Notes

* Ensure that `ffmpeg` is installed and accessible in your system's PATH.
* The bot skips your own messages and commands starting with `!`.

### Troubleshooting
- Error: "ffplay not found" → Install FFmpeg and ensure `ffmpeg\bin` is on PATH, or provide full path to `ffplay`.
- No ducking on macOS/Linux → Expected; per‑app ducking requires Windows + `pycaw`.

---

<small>MIT License — see the [license](LICENSE) file for details.</small>
