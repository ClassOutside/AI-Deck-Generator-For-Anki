import sys
from pathlib import Path
import re
from settings import DEBUG_INPUT, DEBUG_INPUT_FILE, TRANSLATION_TYPE_KEYS

class TextManipulationService:
    def __init__(self, base_dir: Path):
        # Resolve BASE_DIR for both dev and PyInstaller contexts if not provided
        self.base_dir = base_dir

    def split_lines(self, text: str) -> str:
        """
        Split text into lines at line-ending punctuation (., 。, !, ！, ?, ？),
        removing that punctuation and any following spaces.
        """
        intermediate = re.sub(r'[\.。！？\!?]\s*', '\n', text)
        lines = [line.strip() for line in intermediate.split('\n') if line.strip()]
        return '\n'.join(lines)

    def extract_unique_lines(self, raw_text: str) -> list[str]:
        """Process raw lines into unique lines (deduplicated, non-empty)."""
        lines = set(filter(None, raw_text.splitlines()))
        return sorted(lines)

    def add_indices_to_data(self, data: dict) -> dict:
        """
        Adds a unique string index as the first element of each array in L, W, K.
        Modifies data in-place and returns it.
        """
        idx = 1
        for key in TRANSLATION_TYPE_KEYS:
            if key in data and isinstance(data[key], list):
                for item in data[key]:
                    if isinstance(item, list):
                        item.insert(0, str(idx))
                        idx += 1
        return data

    def get_default_input(self) -> str:
        """
        Returns the contents of input.txt if DEBUG_INPUT is True and the file exists,
        else returns an empty string.
        """
        default_input_path = self.base_dir / DEBUG_INPUT_FILE
        if DEBUG_INPUT and default_input_path.exists():
            with open(default_input_path, encoding="utf-8") as f:
                return f.read()
        return ""
    
    def remove_non_source_language(self, text: str) -> str:
        """
        Strip out any non-Japanese characters, leaving only:
         - Hiragana     (U+3040–U+309F)
         - Katakana     (U+30A0–U+30FF)
         - Kanji         (U+4E00–U+9FFF)
         - Common Japanese punctuation and spaces
           (U+3000–U+303F)
        Everything else (ASCII letters, numbers, Latin punctuation, etc.)
        is removed.
        """
        # This regex matches any character NOT in the Japanese blocks;
        # we replace those with empty string.
        return re.sub(
            r"[^\u3000-\u303F\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]+",
            "",
            text
        )
