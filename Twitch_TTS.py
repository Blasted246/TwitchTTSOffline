import asyncio
import logging
import subprocess
import requests
import webbrowser
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from twitchio.ext import commands
import edge_tts
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
import comtypes

print("Please make sure you fill out the variables before starting the script, remove line 13 once done.")
# === CONFIG ===
CLIENT_ID = "Use your own man" # Get this from like wherever
CLIENT_SECRET = "WOAH THIS IS SECRET, USE YOUR OWN!!!" # This is harder to get so do some research, I got mine from twitchio
REDIRECT_URI = "http://localhost:8080"
SCOPES = "chat:read chat:edit"
USERNAME_TO_IGNORE = "Put your username here, this var also convinently ignores your username in TTS as well for those BS players out there"
USE_EDGE_TTS = True  # False = use espeak-ng
IGNORED_COMMANDS = ("!bsr", "!bsprofile", "!queue", "!drinkwater") # Put stuff here ig like these are mine

# === LOGGING ===
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')

# === AUTH FLOW ===
class OAuthHandler(BaseHTTPRequestHandler):
    server_version = "OAuthHandler/1.0"
    def do_GET(self):
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        if "code" in params:
            self.server.auth_code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"<html><body><h1>You can close this window now.</h1></body></html>")
        else:
            self.send_response(400)
            self.end_headers()

def run_server():
    server = HTTPServer(("localhost", 8080), OAuthHandler)
    server.auth_code = None
    while server.auth_code is None:
        server.handle_request()
    return server.auth_code

def exchange_code_for_token(client_id, client_secret, code, redirect_uri):
    url = "https://id.twitch.tv/oauth2/token"
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri,
    }
    response = requests.post(url, data=data)
    response.raise_for_status()
    return response.json()

# === AUDIO CONTROL ===
def lower_volumes():
    sessions = AudioUtilities.GetAllSessions()
    original_volumes = {}
    for session in sessions:
        volume = session._ctl.QueryInterface(ISimpleAudioVolume)
        process = session.Process
        if process and "obs64.exe" not in process.name().lower():
            try:
                original_volumes[process.pid] = volume.GetMasterVolume()
                volume.SetMasterVolume(0.2, None)
            except Exception:
                pass
    return original_volumes

def restore_volumes(original_volumes):
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        volume = session._ctl.QueryInterface(ISimpleAudioVolume)
        process = session.Process
        if process and process.pid in original_volumes:
            try:
                volume.SetMasterVolume(original_volumes[process.pid], None)
            except Exception:
                pass

# === TTS HANDLING ===
async def play_audio(file):
    logging.info(f"Playing audio file: {file}")
    original_volumes = lower_volumes()
    process = await asyncio.create_subprocess_exec(
        "ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", file
    )
    await process.communicate()
    restore_volumes(original_volumes)

async def speak_message(text):
    logging.info(f"TTS: {text}")
    if USE_EDGE_TTS:
        try:
            communicate = edge_tts.Communicate(text, voice="en-GB-RyanNeural")
            await communicate.save("tts.mp3")
            await play_audio("tts.mp3")
        except Exception as e:
            logging.error(f"Edge-TTS Error: {e}")
    else:
        try:
            original_volumes = lower_volumes()
            subprocess.run(["espeak-ng", text])
            restore_volumes(original_volumes)
        except Exception as e:
            logging.error(f"espeak-ng Error: {e}")

# === MAIN BOT ===
def start_bot(access_token, username):
    class Bot(commands.Bot):
        def __init__(self):
            super().__init__(
                token=access_token,
                prefix="",  # No prefix; listen to all messages
                initial_channels=[username]
            )

        async def event_ready(self):
            logging.info(f"Connected as {self.nick}")

        async def event_message(self, message):
            if message.echo or message.author.name.lower() == USERNAME_TO_IGNORE.lower():
                return
            if any(message.content.lower().startswith(cmd) for cmd in IGNORED_COMMANDS):
                return

            text = f"{message.author.name} says {message.content}"
            logging.info(f"Received: {text}")
            await speak_message(text)

    bot = Bot()
    bot.run()

# === ENTRY POINT ===
def main():
    print("Opening Twitch auth URL...")
    auth_url = (
        f"https://id.twitch.tv/oauth2/authorize"
        f"?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
        f"&scope={urllib.parse.quote(SCOPES)}"
    )
    webbrowser.open(auth_url)

    print("Waiting for Twitch authorization...")
    code = run_server()

    print("Exchanging auth code for token...")
    token_response = exchange_code_for_token(CLIENT_ID, CLIENT_SECRET, code, REDIRECT_URI)
    access_token = token_response.get("access_token")

    print("Starting bot...")
    asyncio.run(start_bot(access_token, USERNAME_TO_IGNORE))

if __name__ == "__main__":
    main()
