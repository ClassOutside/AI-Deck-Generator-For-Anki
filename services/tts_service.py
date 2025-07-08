import sys
from pathlib import Path
import subprocess
import requests

from settings import (
    VOICEVOX_PATH, API_URL, API_PORT,
    AUDIO_QUERY_ENDPOINT, AUDIO_SYNTHESIS_ENDPOINT,
    TMP_MP3_DIR, VOICEVOX_SPEAKER, TRANSLATION_TYPE_KEYS
)

class TextToSpeechService:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.tmp_dir = self.base_dir / TMP_MP3_DIR
        self.tmp_dir.mkdir(parents=True, exist_ok=True)
        self.proc = None

    def start_voicevox_process(self):
        """
        Launch the VOICEVOX engine helper and return the Popen handle.
        If the executable does not exist or is invalid, print an error and return None.
        """
        exe_path = Path(VOICEVOX_PATH)

        if not exe_path.exists() or exe_path.is_dir():
            print(f"[start_voicevox_process] ERROR: VOICEVOX executable not found at: {exe_path}")
            return None

        if exe_path.stat().st_size == 0:
            print(f"[start_voicevox_process] ERROR: VOICEVOX executable is empty at: {exe_path}")
            return None

        try:
            args = [
                str(exe_path),
                "--host", API_URL,
                "--port", str(API_PORT),
            ]
            self.proc = subprocess.Popen(
                args,
                stdout=None,
                stderr=None,
                shell=False,
            )
            print(f"[start_voicevox_process] VOICEVOX started: {exe_path}")
            return self.proc
        except Exception as e:
            print(f"[start_voicevox_process] ERROR: Failed to start VOICEVOX: {e}")
            return None


    def stop_voicevox_process(self):
        """
        Terminate the VoiceVox process if running.
        """
        if self.proc:
            self.proc.terminate()
            self.proc.wait()
            self.proc = None

    def generate_mp3s(self, data: dict):
        """
        Generate mp3s using VOICEVOX service based on the given data.
        """
        print(f"[generate_mp3s] Generating mp3s in: {self.tmp_dir.resolve()}")
        for key in TRANSLATION_TYPE_KEYS:
            if data and key in data and isinstance(data[key], list):
                for item in data[key]:
                    if not item:
                        continue
                    
                    idx = item[0] if len(item) > 0 else None
                    # Determine input text for TTS
                    if key == 'L':
                        text = item[1] if len(item) > 1 else None
                    else:  # 'W' or 'K'
                        text = item[3] if len(item) > 3 else None

                    if not text:
                        continue

                    print(f"[generate_mp3s] Synthesizing ({key}): {text}")
                    try:
                        # 1. Audio query
                        query_url = f"http://{API_URL.rstrip('/')}:{API_PORT}{AUDIO_QUERY_ENDPOINT}"

                        query_resp = requests.post(
                            query_url,
                            params={"text": text, "speaker": VOICEVOX_SPEAKER},
                        )
                        query_resp.raise_for_status()
                        audio_query = query_resp.json()

                        # 2. Synthesis
                        synth_url = f"http://{API_URL.rstrip('/')}:{API_PORT}{AUDIO_SYNTHESIS_ENDPOINT}"
                        synth_resp = requests.post(
                            synth_url,
                            params={"speaker": VOICEVOX_SPEAKER},
                            json=audio_query,
                        )
                        synth_resp.raise_for_status()
                        mp3_path = self.tmp_dir / f"{idx}.mp3"
                        with open(mp3_path, "wb") as f:
                            f.write(synth_resp.content)
                        print(f"[generate_mp3s] MP3 saved: {mp3_path.resolve()}")
                    except Exception as e:
                        print(f"[generate_mp3s] Voicevox synthesis failed for line {idx} ({key}): {e}")
