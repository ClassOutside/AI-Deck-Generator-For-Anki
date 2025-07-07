import sys
from pathlib import Path
import importlib.util
import openai
from settings import DEBUG_API, AI_MODEL, MAX_TOKENS, TEMPERATURE, PROMPT_FILE, DEBUG_RESPONSE_FILE
from services.encryption_service import EncryptionService

class TranslationService:
    def __init__(self, base_dir: Path):
        self.BASE_DIR = base_dir
        self.encryption_service = EncryptionService()
        # load keys module from base_dir/keys.py
        spec = importlib.util.spec_from_file_location(
            "local_keys",                       # arbitrary module name
            str(self.BASE_DIR / "keys.py")      # path to the keys file
        )
        local_keys = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(local_keys)
        # stash the values on self for later
        self._encrypted_api_key = local_keys.ENCRYPTED_API_KEY
        self._salt              = local_keys.SALT
        self._iv                = local_keys.IV

    def request_translation_api(self, lines: list[str], pin: str, prompt_path: str = PROMPT_FILE) -> str:
        if DEBUG_API:
            return self.request_translation_api_debug(lines, response_path=self.BASE_DIR / DEBUG_RESPONSE_FILE)

        if not pin:
            raise ValueError("PIN must be provided to decrypt the API key.")

        # decrypt from the locally loaded keys.py
        api_key = self.encryption_service.decrypt(
            pin,
            self._encrypted_api_key,
            self._salt,
            self._iv,
        )
        if not api_key:
            raise ValueError("Invalid PIN or failed to decrypt API key.")

        openai.api_key = api_key

        prompt_file = self.BASE_DIR / prompt_path
        with open(prompt_file, encoding="utf-8") as f:
            prompt = f.read().strip()

        joined_lines = "\n".join(lines)
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user",   "content": joined_lines}
        ]

        try:
            response = openai.chat.completions.create(
                model=AI_MODEL,
                messages=messages,
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE,
            )
            content = response.choices[0].message.content.strip()
            print(content)
            return content
        except Exception as e:
            print(f"OpenAI API error: {e}")
            raise RuntimeError("Failed to connect to OpenAI service.") from e

    def request_translation_api_debug(self, lines: list[str], response_path: Path) -> str:
        try:
            path = Path(response_path)
            if not path.is_absolute():
                path = self.BASE_DIR / path
            with open(path, encoding="utf-8") as f:
                return f.read().strip()
        except Exception as e:
            print(f"Error reading response file: {e}")
            return ""
