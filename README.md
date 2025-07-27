
# Twitch Chat TTS Bot (Offline / Edge-TTS)

Have a local TTS service read your Twitch Chat for you!  
Reads all chat messages except your own and speaks them aloud using **Edge-TTS** (modern neural voices) or **espeak-ng** (retro, robot-like vibes).  
You can toggle between these two by setting the flag `USE_EDGE_TTS = True` in the script.

---

## Manual Prerequisites

This project relies on Python 3.8+ and either:

- **Edge-TTS** (uses Microsoft Edge neural voices, requires `edge-tts` Python package and `ffmpeg` for audio playback), or  
- **espeak-ng** (classic, lightweight, robotic TTS engine available locally on most platforms).
- Go to [Twitch Token Generator](https://twitchtokengenerator.com/) to get your client secret and client ID.
---

### Installing Python

Make sure Python 3.8 or newer is installed on your system:  
- [Download Python](https://www.python.org/downloads/)  
- Verify installation with:

```bash
python --version
````

---

### Installing Edge-TTS

```bash
pip install twitchio edge-tts
```

* **REQUIRED:** Install FFMPEG to play audio output

  * Download from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
  * Follow platform-specific installation instructions to add `ffmpeg` to your system PATH.

---

### Installing espeak-ng

* **Windows:**

  * Download installer from [https://github.com/espeak-ng/espeak-ng/releases](https://github.com/espeak-ng/espeak-ng/releases) (look for `.exe` installer)
  * Install and add to PATH if needed.

* **Linux (Debian/Ubuntu):**

```bash
sudo apt-get update
sudo apt-get install espeak-ng
```

* **macOS (using Homebrew):**

```bash
brew install espeak-ng
```

* To verify installation:

```bash
espeak-ng --version
```

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

4. The bot will join your specified channel and read aloud all chat messages except your own.

---

## Configuration

* `USE_EDGE_TTS`: Set to `True` to use Edge-TTS (modern neural voices). Set to `False` to use espeak-ng (retro, robotic voices).
* `CHANNEL`: Set this to your Twitch channel name.

---

## Notes

* Ensure that `ffmpeg` is installed and accessible in your system's PATH if using Edge-TTS.
* If using espeak-ng, you can adjust the voice and language settings by modifying the `espeak-ng` command options in the script.
* This bot uses the Twitch IRC chat interface to read messages. Ensure your Twitch account has the necessary permissions to read chat messages.

---

## License

This project is licensed under the MIT License:

```
Copyright 2025 - DatLazyCoder

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
```
