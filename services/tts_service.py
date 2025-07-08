import importlib.util
import subprocess
import requests
from pathlib import Path
import os
import wave
import lameenc
from services.popup_service import PopupService

class TextToSpeechService:
    def __init__(self, base_dir: Path, parent=None):
        self.base_dir = base_dir
        self.tmp_dir = self.base_dir / "tmp_mp3"  # keep same tmp_dir name
        self.tmp_dir.mkdir(parents=True, exist_ok=True)
        self.proc = None
        self.parent = parent  # QWidget for popup parent
        self.settings = self._load_settings()

    def _load_settings(self):
        """
        Dynamically load settings.py as a module.
        """
        settings_path = self.base_dir / "settings.py"
        spec = importlib.util.spec_from_file_location("settings", str(settings_path))
        settings = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(settings)
        return settings

    def start_voicevox_process(self):
        """
        Launch the VOICEVOX engine helper and return the Popen handle.
        Suppresses console window on Windows.
        """
        exe_path = Path(self.settings.VOICEVOX_PATH)

        if not exe_path.exists() or exe_path.is_dir() or exe_path.stat().st_size == 0:
            print(f"[start_voicevox_process] ERROR: Invalid VOICEVOX executable at: {exe_path}")
            if self.settings.TERMS_AGREEMENT_AGREED_TO:
                PopupService.show_error_popup(
                    parent=self.parent,
                    title="Voicevox Error",
                    message="Voicevox failed to start.\nPlease check the executable path in settings.py."
                )
            return None

        try:
            args = [
                str(exe_path),
                "--host", self.settings.API_URL,
                "--port", str(self.settings.API_PORT),
            ]

            # Add flag to hide console window on Windows
            startup_flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0

            self.proc = subprocess.Popen(
                args,
                stdout=None,
                stderr=None,
                shell=False,
                creationflags=startup_flags
            )
            print(f"[start_voicevox_process] VOICEVOX started: {exe_path}")
            return self.proc
        except Exception as e:
            print(f"[start_voicevox_process] ERROR: Failed to start VOICEVOX: {e}")
            if self.settings.TERMS_AGREEMENT_AGREED_TO:
                PopupService.show_error_popup(
                    parent=self.parent,
                    title="Voicevox Error",
                    message="Voicevox failed to start.\nPlease check the executable path in settings.py."
                )
            return None

    def stop_voicevox_process(self):
        if self.proc:
            self.proc.terminate()
            self.proc.wait()
            self.proc = None

    def generate_wavs(self, data: dict):
        """
        Generate WAV files using VOICEVOX service based on the given data.
        """
        settings = self.settings
        print(f"[generate_wavs] Generating WAVs in: {self.tmp_dir.resolve()}")

        for key in settings.TRANSLATION_TYPE_KEYS:
            if data and key in data and isinstance(data[key], list):
                for item in data[key]:
                    if not item:
                        continue

                    idx = item[0] if len(item) > 0 else None
                    text = item[1] if key == 'L' and len(item) > 1 else (
                        item[3] if len(item) > 3 else None
                    )
                    if not text:
                        continue

                    print(f"[generate_wavs] Synthesizing ({key}): {text}")
                    try:
                        query_url = f"http://{settings.API_URL.rstrip('/')}:{settings.API_PORT}{settings.AUDIO_QUERY_ENDPOINT}"
                        query_resp = requests.post(
                            query_url,
                            params={"text": text, "speaker": settings.VOICEVOX_SPEAKER},
                        )
                        query_resp.raise_for_status()
                        audio_query = query_resp.json()

                        synth_url = f"http://{settings.API_URL.rstrip('/')}:{settings.API_PORT}{settings.AUDIO_SYNTHESIS_ENDPOINT}"
                        synth_resp = requests.post(
                            synth_url,
                            params={"speaker": settings.VOICEVOX_SPEAKER},
                            json=audio_query,
                        )
                        synth_resp.raise_for_status()

                        wav_path = self.tmp_dir / f"{idx}.wav"
                        with open(wav_path, "wb") as f:
                            f.write(synth_resp.content)
                        print(f"[generate_wavs] WAV saved: {wav_path.resolve()}")

                    except Exception as e:
                        print(f"[generate_wavs] Voicevox synthesis failed for line {idx} ({key}): {e}")

    def convert_to_mp3(self):
        """
        Convert all .wav files in tmp_dir to .mp3 using lameenc. Reads WAV header to preserve sample rate and channels.
        """
        print(f"[convert_to_mp3] Converting WAVs to MP3 in: {self.tmp_dir.resolve()}")

        for wav_file in self.tmp_dir.glob("*.wav"):
            mp3_file = wav_file.with_suffix('.mp3')
            try:
                print(f"[convert_to_mp3] Processing {wav_file.name}")
                with wave.open(str(wav_file), 'rb') as wf:
                    sample_rate = wf.getframerate()
                    channels = wf.getnchannels()
                    pcm_data = wf.readframes(wf.getnframes())

                # Initialize encoder per file to match WAV properties
                encoder = lameenc.Encoder()
                encoder.set_bit_rate(
                    getattr(self.settings, 'MP3_BITRATE', 128)
                )
                encoder.set_in_sample_rate(sample_rate)
                encoder.set_channels(channels)
                encoder.set_quality(
                    getattr(self.settings, 'MP3_QUALITY', 2)
                )

                mp3_data = encoder.encode(pcm_data)
                mp3_data += encoder.flush()

                with open(mp3_file, 'wb') as f:
                    f.write(mp3_data)
                print(f"[convert_to_mp3] MP3 created: {mp3_file.resolve()}")
            except Exception as e:
                print(f"[convert_to_mp3] ERROR encoding {wav_file.name}: {e}")

    def generate_mp3s(self, data: dict):
        """
        Orchestrates the creation of WAVs followed by MP3 conversion.
        """
        print(f"[generate_mp3s] Starting full generation pipeline in: {self.tmp_dir.resolve()}")
        self.generate_wavs(data)
        self.convert_to_mp3()
