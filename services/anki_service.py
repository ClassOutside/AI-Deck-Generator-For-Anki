import openai
from pathlib import Path
from settings import TMP_MP3_DIR, SUBDECK_NAMES, TRANSLATION_TYPE_KEYS, CSS_FILE, OUTPUT_DIR, CARD_MODEL
import genanki
from datetime import datetime

class AnkiService:
    def __init__(self, base_dir: Path):
        self.BASE_DIR = base_dir

    def create_subdeck(self, data, song_name, subdeck_type, model):
        subdeck_names = SUBDECK_NAMES
        subdeck_title = f"{song_name}::{subdeck_names.get(subdeck_type, subdeck_type)}"
        subdeck_id = abs(hash(subdeck_title)) % (10 ** 10)
        subdeck = genanki.Deck(subdeck_id, subdeck_title)

        if data and subdeck_type in data and isinstance(data[subdeck_type], list):
            idx = 1
            for item in data[subdeck_type]:
                if item and len(item) >= 3:
                    japanese = str(item[0]) if item[0] else ""
                    translate = str(item[1]) if item[1] else ""
                    romaji = str(item[2]) if item[2] else ""
                    if japanese and (romaji or translate):
                        mp3_filename = f"{idx}.mp3"
                        note = genanki.Note(
                            model=model,
                            fields=[
                                f"{japanese}<br>[sound:{mp3_filename}]",
                                translate,
                                romaji
                            ]
                        )
                        subdeck.add_note(note)
                        print(f"[create_subdeck] Added to {subdeck_title}: {japanese} -> {romaji}, {translate}, mp3: {mp3_filename}")
                    else:
                        print(f"[create_subdeck] Skipped line {idx}: missing fields")
                    idx += 1
                else:
                    print(f"[create_subdeck] Skipped line {idx}: not enough elements")
        return subdeck

    def create_direction_deck(self, data, song_name, direction, model):
        dir_names = {
            "ja_en": "Japanese to English",
            "en_ja": "English to Japanese"
        }
        deck_title = f"{song_name}::{dir_names[direction]}"
        deck_id = abs(hash(deck_title)) % (10 ** 10)
        direction_deck = genanki.Deck(deck_id, deck_title)

        subdecks = []
        for subdeck_type in TRANSLATION_TYPE_KEYS:
            subdeck_names = SUBDECK_NAMES
            subdeck_title = f"{deck_title}::{subdeck_names[subdeck_type]}"
            subdeck_id = abs(hash(subdeck_title)) % (10 ** 10)
            subdeck = genanki.Deck(subdeck_id, subdeck_title)

            if data and subdeck_type in data and isinstance(data[subdeck_type], list):
                for item in data[subdeck_type]:
                    if item and len(item) >= 4:
                        idx = item[0]
                        japanese = str(item[1]) if item[1] else ""
                        english = str(item[2]) if item[2] else ""
                        romaji = str(item[3]) if item[3] else ""
                        mp3_filename = f"{idx}.mp3"
                        if direction == "ja_en":
                            note = genanki.Note(
                                model=model,
                                fields=[
                                    f"{japanese}<br>[sound:{mp3_filename}]",
                                    english,
                                    romaji
                                ]
                            )
                        else:
                            note = genanki.Note(
                                model=model,
                                fields=[
                                    english,
                                    japanese,
                                    f"{romaji}<br>[sound:{mp3_filename}]"
                                ]
                            )
                        subdeck.add_note(note)
                    else:
                        print(f"[create_direction_deck] Skipped line: not enough elements")
            subdecks.append(subdeck)
        return [direction_deck] + subdecks

    def load_anki_css(self, css_path=CSS_FILE):
        try:
            css_file = self.BASE_DIR / css_path
            with open(css_file, encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"Could not load CSS: {e}")
            return ""

    def generate_anki_deck(self, data: dict, deck_title: str, output_dir: str = None):
        """
        Generate an Anki .apkg file with a timestamped filename.

        If output_dir is provided, use that folder;
        otherwise fall back to OUTPUT_DIR under BASE_DIR.
        """
        tmp_anki_dir = Path(output_dir) if output_dir else self.BASE_DIR / OUTPUT_DIR
        tmp_anki_dir.mkdir(parents=True, exist_ok=True)

        print(f"[generate_anki_deck] Using output folder: {tmp_anki_dir.resolve()}")

        deck_id = abs(hash(deck_title)) % (10 ** 10)
        main_deck = genanki.Deck(deck_id, deck_title)
        css = self.load_anki_css()
        model = genanki.Model(
            CARD_MODEL,
            'Simple Model',
            fields=[
                {'name': 'Front'},
                {'name': 'Translation'},
                {'name': 'Romaji'},
            ],
            templates=[
                {
                    'name': 'Card 1',
                    'qfmt': '{{Front}}',
                    'afmt': '{{Translation}}<br><div class="romaji">{{Romaji}}</div>',
                },
            ],
            css=css,
        )

        all_decks = [main_deck]
        all_decks += self.create_direction_deck(data, deck_title, "ja_en", model)
        all_decks += self.create_direction_deck(data, deck_title, "en_ja", model)

        timestamp = datetime.now().strftime("%m-%d-%Y_%I-%M-%p")
        safe_title = deck_title.replace(' ', '_')
        filename = f"{safe_title}_{timestamp}.apkg"
        apkg_path = tmp_anki_dir / filename

        media_files = []
        tmp_mp3_dir = self.BASE_DIR / TMP_MP3_DIR
        if tmp_mp3_dir.exists() and tmp_mp3_dir.is_dir():
            for mp3_file in tmp_mp3_dir.glob("*.mp3"):
                media_files.append(str(mp3_file.resolve()))

        genanki.Package(all_decks, media_files=media_files).write_to_file(str(apkg_path))
        print(f"[generate_anki_deck] Deck saved to: {apkg_path.resolve()}")

