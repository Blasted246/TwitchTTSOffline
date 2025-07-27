import asyncio
import logging
import subprocess
import requests
import webbrowser
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from twitchio.ext import commands
import edge_tts

# === CONFIG ===
CLIENT_ID = "ADD YOUR CLIENT ID HERE" # This is like, not that secret but still, don't show anybody
CLIENT_SECRET = "ADD YOUR CLIENT SECRET HERE PLEASE" # It's in the name, it's a secret, no peeking :/
REDIRECT_URI = "http://localhost:8080"
SCOPES = "chat:read chat:edit"
USERNAME_TO_IGNORE = "CHANNEL NAME"
USE_EDGE_TTS = True  # False = use espeak-ng

# === LOGGING ===
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s') # I want to know if the messages are going through, okay?

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
            self.wfile.write(b"<html><body><h1>All done! You may close this window now, check your terminal!</h1></body></html>")
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

# === TTS HANDLING ===
async def play_audio(file):
    logging.info(f"Playing audio file: {file}")
    process = await asyncio.create_subprocess_exec(
        "ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", file
    )
    await process.communicate()

async def speak_message(text):
    logging.info(f"TTS: {text}")
    if USE_EDGE_TTS:
        try:
            communicate = edge_tts.Communicate(text, voice="en-GB-RyanNeural") # The one I like personally
            await communicate.save("tts.mp3")
            await play_audio("tts.mp3")
        except Exception as e:
            logging.error(f"Edge-TTS Error: {e}")
    else:
        try:
            subprocess.run(["espeak-ng", text])
        except Exception as e:
            logging.error(f"espeak-ng Error: {e}")

# === MAIN BOT ===
def start_bot(access_token, username):
    class Bot(commands.Bot):
        def __init__(self):
            super().__init__(
                token=access_token,
                prefix="",  # Add your prefix here if you want to have one I guess
                initial_channels=[username]
            )

        async def event_ready(self):
            logging.info(f"Connected as {self.nick}")

        async def event_message(self, message):
            if message.echo or message.author.name.lower() == USERNAME_TO_IGNORE.lower():
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
    # Last little thing, if you are looking at this and really know what you are doing, please for the love of your mother fork this and FIX THIS PLEASE!

    print("Starting bot...")
    asyncio.run(start_bot(access_token, USERNAME_TO_IGNORE))

if __name__ == "__main__":
    main()
