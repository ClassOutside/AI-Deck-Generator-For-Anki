from pathlib import Path
import importlib.util
import os
import base64

from services.encryption_service import EncryptionService


class SettingsService:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.encryption_service = EncryptionService()
        self._settings_cache = {
            "OUTPUT_DIR": None,
            "VOICEVOX_PATH": None,
        }
        self.settings = None

    def load_settings(self):
        settings_path = self.base_dir / "settings.py"
        spec = importlib.util.spec_from_file_location("settings", str(settings_path))
        settings = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(settings)
        self.settings = settings

        self._settings_cache["OUTPUT_DIR"] = settings.OUTPUT_DIR
        self._settings_cache["VOICEVOX_PATH"] = settings.VOICEVOX_PATH

        return settings

    def save_settings(self):
        settings_path = self.base_dir / "settings.py"

        with open(settings_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        replacements = {
            "OUTPUT_DIR": f'r"{self._settings_cache["OUTPUT_DIR"]}"',
            "VOICEVOX_PATH": f'r"{self._settings_cache["VOICEVOX_PATH"]}"',
            "TERMS_AGREEMENT_AGREED_TO": str(getattr(self.settings, "TERMS_AGREEMENT_AGREED_TO", False)),
        }

        updated_lines = []
        for line in lines:
            updated = False
            for key, val in replacements.items():
                if line.strip().startswith(f"{key}"):
                    updated_lines.append(f'{key} = {val}\n')
                    updated = True
                    break
            if not updated:
                updated_lines.append(line)

        with open(settings_path, "w", encoding="utf-8") as f:
            f.writelines(updated_lines)

    # Output Folder
    def get_output_folder(self) -> str:
        return self._settings_cache["OUTPUT_DIR"]

    def set_output_folder(self, folder_path: str):
        self._settings_cache["OUTPUT_DIR"] = folder_path
        self.settings.OUTPUT_DIR = folder_path

    # VOICEVOX Path
    def get_voicevox_path(self) -> str:
        return self._settings_cache["VOICEVOX_PATH"]

    def set_voicevox_path(self, path: str) -> bool:
        previous = self._settings_cache["VOICEVOX_PATH"]
        self._settings_cache["VOICEVOX_PATH"] = path
        self.settings.VOICEVOX_PATH = path
        return previous != path  # True if changed

    # Terms Agreement
    def set_terms_accepted(self):
        if self.settings is None:
            raise RuntimeError("Settings not loaded.")
        self.settings.TERMS_AGREEMENT_AGREED_TO = True
        self.save_settings()

    def is_terms_accepted(self) -> bool:
        if self.settings is None:
            raise RuntimeError("Settings not loaded.")
        return getattr(self.settings, "TERMS_AGREEMENT_AGREED_TO", False)

    # API Key Management
    def encrypt_and_store_api_key(self, api_key: str, pin: str):
        """
        Encrypts and saves the API key with provided PIN,
        writes base64 encoded data, salt, and iv into keys.py
        """
        salt = os.urandom(16)
        key = self.encryption_service.derive_key(pin, salt)
        iv, encrypted = self.encryption_service.encrypt(api_key, key)

        encoded_salt = base64.b64encode(salt).decode()
        encoded_iv = base64.b64encode(iv).decode()
        encoded_data = base64.b64encode(encrypted).decode()

        key_file = self.base_dir / "keys.py"
        with open(key_file, "w", encoding="utf-8") as f:
            f.write(f'ENCRYPTED_API_KEY = "{encoded_data}"\n')
            f.write(f'SALT = "{encoded_salt}"\n')
            f.write(f'IV = "{encoded_iv}"\n')

    # Optional utility if needed externally
    def save_all(self, api_key: str = None, pin: str = None) -> bool:
        """
        Saves all settings including optional encrypted API key.
        Returns True if VOICEVOX path was changed (requires restart).
        """
        voicevox_changed = self.set_voicevox_path(self.get_voicevox_path())
        self.save_settings()

        if api_key and pin:
            self.encrypt_and_store_api_key(api_key, pin)

        return voicevox_changed
