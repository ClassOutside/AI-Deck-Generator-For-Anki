import shutil
from pathlib import Path
from settings import TMP_MP3_DIR

class CleanupService:
    def __init__(self, base_dir: Path):
        self.BASE_DIR = base_dir

    def cleanup_tmp_mp3(self):
        tmp_dir = self.BASE_DIR / TMP_MP3_DIR
        if tmp_dir.exists() and tmp_dir.is_dir():
            shutil.rmtree(tmp_dir)
            print(f"[cleanup_tmp_mp3] Deleted {tmp_dir.resolve()}")

    def full_cleanup(self):
        """Call both cleanups."""
        self.cleanup_tmp_mp3()

    def perform_cleanup(self, voicevox_proc, voicevox_service):
        """Cleans up temporary files and terminates the VoiceVox process if running."""
        if voicevox_proc:
            self.full_cleanup()
            voicevox_service.stop_voicevox_process()
            print("[perform_cleanup] VoiceVox stopped and files cleaned up.")
