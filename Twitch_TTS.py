import os
import sys
import time
import random
import asyncio
import logging
import atexit
import edge_tts
from unidecode import unidecode
try:
    import pykakasi
    HAS_PYKAKASI = True
except Exception:
    HAS_PYKAKASI = False
try:
    from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
    HAS_PYCAW = True
except Exception:
    HAS_PYCAW = False

# === CONFIG FROM FILE ===
def read_config(path="config.txt"):
    config = {}
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file '{path}' not found.")
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"): continue
            if "=" in line:
                k, v = line.split("=", 1)
                config[k.strip()] = v.strip()
    return config

_cfg = read_config()
CHANNEL_NAME = _cfg.get("CHANNEL_NAME", "your_channel_here")
CHANNEL_NAME_LOWER = CHANNEL_NAME.lower()
TTS_VOICE = (_cfg.get("TTS_VOICE", "en-GB-RyanNeural") or "en-GB-RyanNeural").strip()

try:
    TTS_VOLUME = float(_cfg.get("TTS_VOLUME", "1.0"))
    TTS_VOLUME = max(0.0, min(1.0, TTS_VOLUME))
except ValueError:
    TTS_VOLUME = 1.0
    logging.warning("Invalid TTS_VOLUME in config, using default: 1.0")

try:
    TTS_ATTENUATION = float(_cfg.get("TTS_ATTENUATION", "0.5"))
    TTS_ATTENUATION = max(0.0, min(1.0, TTS_ATTENUATION))
except ValueError:
    TTS_ATTENUATION = 0.5
    logging.warning("Invalid TTS_ATTENUATION in config, using default: 0.5")
def _parse_exclude_processes(val: str):
    if not val:
        return set()
    parts = [p.strip().lower() for p in val.split(',') if p.strip()]
    norm = set()
    for p in parts:
        if sys.platform.startswith('win') and not p.endswith('.exe'):
            p = p + '.exe'
        norm.add(p)
    return norm

_EXCLUDE_FROM_CONFIG = _parse_exclude_processes(_cfg.get("ATTENUATION_EXCLUDE_PROCESSES", ""))

def _parse_user_list(val: str):
    if not val:
        return set()
    return {p.strip().lower() for p in val.split(',') if p.strip()}

IGNORE_USERS = _parse_user_list(_cfg.get("IGNORE_USERS", ""))

try:
    ATTENUATION_DELAY_MS = int(_cfg.get("ATTENUATION_DELAY_MS", "100"))
    if ATTENUATION_DELAY_MS < 0:
        ATTENUATION_DELAY_MS = 0
except ValueError:
    ATTENUATION_DELAY_MS = 100

try:
    NAME_REPEAT_COOLDOWN = float(_cfg.get("NAME_REPEAT_COOLDOWN", "15"))
    if NAME_REPEAT_COOLDOWN < 0:
        NAME_REPEAT_COOLDOWN = 0
except ValueError:
    NAME_REPEAT_COOLDOWN = 15
    logging.warning("Invalid NAME_REPEAT_COOLDOWN in config, using default: 15")

# === LOGGING ===
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')

# === ATTENUATION SAVING ===
_ACTIVE_ATTENUATION = {}
FADE_MS = 100

# === ROMANIZATION ===
def _contains_japanese(text: str) -> bool:
    for ch in text:
        o = ord(ch)
        if 0x3040 <= o <= 0x309F:  # Hiragana
            return True
        if 0x30A0 <= o <= 0x30FF:  # Katakana
            return True
        if 0x31F0 <= o <= 0x31FF:  # Katakana Phonetic Extensions
            return True
        if 0xFF66 <= o <= 0xFF9D:  # Halfwidth Katakana
            return True
    return False

def _contains_han(text: str) -> bool:
    for ch in text:
        o = ord(ch)
        if 0x4E00 <= o <= 0x9FFF:
            return True
    return False

def _ja_to_romaji(text: str) -> str:
    if not HAS_PYKAKASI:
        return unidecode(text)
    try:
        kks = pykakasi.kakasi()
        result = kks.convert(text)
        romaji = " ".join(seg.get("hepburn") or "" for seg in result)
        return " ".join(romaji.split()) or text
    except Exception:
        return unidecode(text)

def _romanize_text(text: str) -> str:
    if _contains_japanese(text) or _contains_han(text):
        return _ja_to_romaji(text)
    return unidecode(text)

def _restore_other_app_volumes(original: dict):
    if not (HAS_PYCAW and sys.platform.startswith("win")):
        return
    try:
        sessions = AudioUtilities.GetAllSessions()
        by_pid = {s.Process.pid: s for s in sessions if s.Process}
        for pid, vol in original.items():
            try:
                s = by_pid.get(pid)
                if not s:
                    continue
                volume = s._ctl.QueryInterface(ISimpleAudioVolume)
                volume.SetMasterVolume(float(vol), None)
            except Exception:
                continue
    except Exception:
        pass
async def _ramp_duck_other_app_volumes(factor: float, exclude_pids=None, exclude_names=None, duration_ms: int = FADE_MS):
    if not (HAS_PYCAW and sys.platform.startswith("win")):
        return {}
    if exclude_pids is None:
        exclude_pids = set()
    if exclude_names is None:
        exclude_names = set()
    exclude_names_lower = {n.lower() for n in exclude_names}
    sessions_info = []
    original = {}
    try:
        for session in AudioUtilities.GetAllSessions():
            try:
                process = session.Process
                if not process:
                    continue
                name = (process.name() or "").lower()
                if process.pid in exclude_pids:
                    continue
                if name in exclude_names_lower:
                    continue
                vol = session._ctl.QueryInterface(ISimpleAudioVolume)
                prev = float(vol.GetMasterVolume())
                target = max(0.0, min(1.0, prev * float(factor)))
                original[process.pid] = prev
                sessions_info.append((process.pid, vol, prev, target))
            except Exception:
                continue
    except Exception:
        pass
    global _ACTIVE_ATTENUATION
    _ACTIVE_ATTENUATION = original.copy()
    steps = max(1, int(duration_ms // 10))
    for i in range(1, steps + 1):
        t = i / steps
        for pid, vol, prev, target in sessions_info:
            try:
                val = prev + (target - prev) * t
                vol.SetMasterVolume(float(val), None)
            except Exception:
                continue
        await asyncio.sleep(duration_ms / steps / 1000.0)
    for pid, vol, prev, target in sessions_info:
        try:
            vol.SetMasterVolume(float(target), None)
        except Exception:
            continue
    return original

async def _ramp_restore_app_volumes(original: dict, duration_ms: int = FADE_MS):
    if not (HAS_PYCAW and sys.platform.startswith("win")):
        return
    info = []
    try:
        sessions = AudioUtilities.GetAllSessions()
        by_pid = {s.Process.pid: s for s in sessions if s.Process}
        for pid, orig in original.items():
            try:
                s = by_pid.get(pid)
                if not s:
                    continue
                vol = s._ctl.QueryInterface(ISimpleAudioVolume)
                current = float(vol.GetMasterVolume())
                info.append((pid, vol, current, float(orig)))
            except Exception:
                continue
    except Exception:
        info = []
    steps = max(1, int(duration_ms // 10))
    for i in range(1, steps + 1):
        t = i / steps
        for pid, vol, current, orig in info:
            try:
                val = current + (orig - current) * t
                vol.SetMasterVolume(float(val), None)
            except Exception:
                continue
        await asyncio.sleep(duration_ms / steps / 1000.0)
    for pid, vol, current, orig in info:
        try:
            vol.SetMasterVolume(float(orig), None)
        except Exception:
            continue
    global _ACTIVE_ATTENUATION
    _ACTIVE_ATTENUATION = {}


# === TTS PIPELINE ===
# Two-stage pipeline: text -> audio file path -> playback
tts_text_queue = asyncio.Queue()
tts_audio_queue = asyncio.Queue()

async def generate_tts_file(text: str) -> str:
    if not text or not text.strip():
        raise ValueError("Empty text")
    romanized = _romanize_text(text)
    communicate = edge_tts.Communicate(romanized, voice=TTS_VOICE)
    # Unique file per item so we can pipeline generation/playback
    temp_path = os.path.join(os.getcwd(), f"tts_{int(time.time()*1000)}_{random.randint(1000,9999)}.mp3")
    await communicate.save(temp_path)
    if not os.path.exists(temp_path) or os.path.getsize(temp_path) == 0:
        raise Exception("Failed to create audio file")
    return temp_path

last_sender = None
last_time = 0

async def tts_gen_worker():
    global last_sender, last_time
    while True:
        tts_item = await tts_text_queue.get()
        if isinstance(tts_item, tuple) and len(tts_item) == 2:
            display_name, message_text = tts_item
        else:
            display_name, message_text = None, tts_item
        now = time.time()
        if display_name is not None:
            if last_sender == display_name and (now - last_time) < NAME_REPEAT_COOLDOWN:
                tts_text = message_text
            else:
                tts_text = f"{display_name} says {message_text}"
                last_sender = display_name
                last_time = now
        else:
            tts_text = message_text
        try:
            path = await generate_tts_file(str(tts_text))
            await tts_audio_queue.put(path)
        except Exception as e:
            logging.error(f"TTS worker error: {e}")
        tts_text_queue.task_done()

async def tts_playback_worker():
    grace_sec = max(0.0, float(ATTENUATION_DELAY_MS) / 1000.0)
    while True:
        # Block for first item of the burst
        path = await tts_audio_queue.get()
        original_volumes = {}
        try:
            # Duck once for the entire burst
            original_volumes = await _ramp_duck_other_app_volumes(
                factor=TTS_ATTENUATION,
                exclude_pids={os.getpid()},
                exclude_names={"ffplay.exe"} | _EXCLUDE_FROM_CONFIG,
                duration_ms=ATTENUATION_DELAY_MS
            )

            while True:
                # Play current file
                volume = min(100, max(0, int(float(TTS_VOLUME) * 100)))
                try:
                    process = await asyncio.create_subprocess_exec(
                        "ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet",
                        "-volume", str(volume), path,
                        stdin=asyncio.subprocess.DEVNULL,
                        stdout=asyncio.subprocess.DEVNULL,
                        stderr=asyncio.subprocess.DEVNULL,
                    )
                    await process.communicate()
                except FileNotFoundError:
                    logging.error("ffplay not found. Please install ffmpeg")
                except Exception as e:
                    logging.error(f"TTS playback error: {e}")
                finally:
                    # Cleanup file
                    try:
                        os.remove(path)
                    except Exception:
                        pass
                    tts_audio_queue.task_done()

                # Try to chain next file without restoring
                try:
                    # Prefer immediate next if already queued
                    path = tts_audio_queue.get_nowait()
                    continue
                except asyncio.QueueEmpty:
                    pass

                # Optionally wait a short grace for next file to arrive
                got_next = False
                if grace_sec > 0:
                    try:
                        path = await asyncio.wait_for(tts_audio_queue.get(), timeout=grace_sec)
                        got_next = True
                    except asyncio.TimeoutError:
                        got_next = False
                if not got_next:
                    break  # end of burst
            # Restore once after the burst finishes
        finally:
            try:
                if original_volumes:
                    await _ramp_restore_app_volumes(original_volumes or {}, duration_ms=ATTENUATION_DELAY_MS)
            except Exception:
                pass


# === MAIN TTS ===
def start_bot(channel):
    async def runner():
        gen_task = asyncio.create_task(tts_gen_worker())
        play_task = asyncio.create_subprocess_exec  # placeholder to keep type hints happy
        play_task = asyncio.create_task(tts_playback_worker())
        try:
            while True:
                try:
                    await anonymous_irc_reader(channel)
                    logging.warning("Disconnected from IRC. Reconnecting in 5 seconds...")
                except Exception as e:
                    logging.error(f"IRC loop error: {e}")
                await asyncio.sleep(5)
        finally:
            gen_task.cancel()
            play_task.cancel()
            try:
                await gen_task
            except asyncio.CancelledError:
                pass
            try:
                await play_task
            except asyncio.CancelledError:
                pass
    asyncio.run(runner())


async def anonymous_irc_reader(channel: str):
    server = "irc.chat.twitch.tv"
    port = 6667
    nick = f"justinfan{random.randint(10000,99999)}"
    logging.info(f"Connected to #{channel}")

    reader, writer = await asyncio.open_connection(server, port)

    def send(line: str):
        logging.debug(f">>> {line.strip()}")
        writer.write((line + "\r\n").encode())

    send("CAP REQ :twitch.tv/tags twitch.tv/commands twitch.tv/membership")
    send(f"NICK {nick}")
    send(f"JOIN #{channel}")

    try:
        while not reader.at_eof():
            raw = await reader.readline()
            if not raw:
                break
            line = raw.decode(errors="ignore").strip()
            logging.debug(f"<<< {line}")

            if line.startswith("PING"):
                send(line.replace("PING", "PONG"))
                continue

            if "PRIVMSG" in line:
                try:
                    tags_part = None
                    rest = line
                    if line.startswith("@"):
                        tags_part, rest = line.split(" ", 1)
                    parts = rest.split(" :", 1)
                    prefix_and_cmd = parts[0]
                    message_text = parts[1] if len(parts) > 1 else ""

                    prefix = prefix_and_cmd.split(" ")[0]
                    if prefix.startswith(":"):
                        sender = prefix[1:].split("!")[0]
                    else:
                        sender = "unknown"

                    display_name = sender
                    if tags_part:
                        tags = {}
                        for kv in tags_part[1:].split(";"):
                            if "=" in kv:
                                k, v = kv.split("=", 1)
                                tags[k] = v
                        display_name = tags.get("display-name", sender)

                    # Skip our own messages
                    if sender.lower() == CHANNEL_NAME_LOWER:
                        continue
                    # Skip users from ignore list (sender or display name)
                    if sender.lower() in IGNORE_USERS or display_name.lower() in IGNORE_USERS:
                        continue
                    if message_text.strip().startswith("!"):
                        continue

                    logging.info(f"Received: {display_name} says {message_text}")
                    await tts_text_queue.put((display_name, message_text))
                except Exception as e:
                    logging.error(f"Error parsing line: {e} -- {line}")
    except Exception as e:
        logging.error(f"Anonymous IRC reader error: {e}")
    finally:
        try:
            writer.close()
            await writer.wait_closed()
        except Exception:
            pass


# === REAL MAIN ===

def main():
    if CHANNEL_NAME == "your_channel_here" or not CHANNEL_NAME:
        print("Please set CHANNEL_NAME in config.txt before running. Exiting.")
        return
    logging.info(f"Starting in anonymous mode. Reading chat from channel: {CHANNEL_NAME}")
    try:
        start_bot(CHANNEL_NAME)
    except KeyboardInterrupt:
        logging.info("Interrupted. Exiting...")
    finally:
        try:
            if _ACTIVE_ATTENUATION:
                logging.info("Restoring volumes on shutdown...")
                _restore_other_app_volumes(_ACTIVE_ATTENUATION)
        except Exception as e:
            logging.debug(f"Shutdown restore failed: {e}")


if __name__ == "__main__":
    def _emergency_restore_on_exit():
        try:
            if _ACTIVE_ATTENUATION:
                logging.info("Emergency restore on exit...")
                _restore_other_app_volumes(_ACTIVE_ATTENUATION)
        except Exception as e:
            logging.debug(f"Atexit restore failed: {e}")

    atexit.register(_emergency_restore_on_exit)
    main()
