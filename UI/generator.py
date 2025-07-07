from pathlib import Path
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QIcon, QFont
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QLabel,
    QLineEdit, QTextEdit, QPushButton, QFrame,
    QSizePolicy
)
from services.text_manipulation_service import TextManipulationService
from services.translation_service import TranslationService
from services.tts_service import TextToSpeechService
from services.anki_service import AnkiService
from services.cleanup_service import CleanupService
import json
from services.popup_service import PopupService


class GeneratorPage(QWidget):
    def __init__(self, base_dir: Path, settings, open_settings_callback, get_output_folder_callback):
        super().__init__()
        self.BASE_DIR = base_dir
        self.settings = settings
        self.open_settings_callback = open_settings_callback
        self.get_output_folder_callback = get_output_folder_callback

        # Initialize services
        self.anki_generator = AnkiService(self.BASE_DIR)
        self.cleanup_service = CleanupService(self.BASE_DIR)
        self.text_processor = TextManipulationService(base_dir=self.BASE_DIR)
        self.translation_service = TranslationService(base_dir=self.BASE_DIR)

        # Initialize TextToSpeechService instance
        self.voicevox_service = TextToSpeechService(base_dir=self.BASE_DIR)

        font = QFont()
        font.setPointSize(self.settings.FONT_SIZE)

        default_input = self.text_processor.get_default_input()

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(*self.settings.MARGINS)
        main_layout.setSpacing(self.settings.SPACING)

        # === Top Bar ===
        top_bar = QGridLayout()
        top_bar.setContentsMargins(0, 0, 0, 0)
        top_bar.setColumnStretch(0, 1)
        top_bar.setColumnStretch(1, 0)
        top_bar.setColumnStretch(2, 1)

        # Center icon
        icon_label = QLabel()
        icon_path = self.BASE_DIR / self.settings.ICON_FILE
        pixmap = QPixmap(str(icon_path))
        icon_label.setPixmap(
            pixmap.scaled(self.settings.ICON_SIZE, self.settings.ICON_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )
        icon_label.setAlignment(Qt.AlignCenter)
        top_bar.addWidget(icon_label, 0, 1, alignment=Qt.AlignTop | Qt.AlignHCenter)

        # Settings button
        settings_button = QPushButton()
        settings_icon_path = self.BASE_DIR / "icons/settings.svg"
        settings_button.setIcon(QIcon(str(settings_icon_path)))
        settings_button.setIconSize(QSize(20, 20))
        settings_button.setFixedSize(30, 30)
        settings_button.setFlat(True)
        settings_button.setToolTip("Settings")
        settings_button.clicked.connect(self.open_settings_callback)
        top_bar.addWidget(settings_button, 0, 2, alignment=Qt.AlignTop | Qt.AlignRight)

        main_layout.addLayout(top_bar)

        # === PIN Field ===
        pin_layout = QGridLayout()
        pin_layout.setHorizontalSpacing(self.settings.SPACING)
        pin_layout.setVerticalSpacing(self.settings.SPACING)

        pin_label = QLabel("Enter PIN")
        pin_label.setFont(font)

        self.pin_input = QLineEdit()
        self.pin_input.setFont(font)
        self.pin_input.setEchoMode(QLineEdit.Password)  # ← Hide text input

        pin_layout.addWidget(pin_label, 0, 0)
        pin_layout.addWidget(self.pin_input, 0, 1, 1, 2)
        pin_layout.setColumnStretch(1, 1)

        main_layout.addLayout(pin_layout)

        # Divider between PIN and deck title
        pin_divider = QFrame()
        pin_divider.setFrameShape(QFrame.HLine)
        pin_divider.setFrameShadow(QFrame.Sunken)
        pin_divider.setStyleSheet("margin-top: 4px; margin-bottom: 4px;")
        main_layout.addWidget(pin_divider)

        # === Deck Title ===
        title_layout = QGridLayout()
        title_layout.setHorizontalSpacing(self.settings.SPACING)
        title_layout.setVerticalSpacing(self.settings.SPACING)

        title_label = QLabel("Deck Title")
        title_label.setFont(font)
        self.deck_title = QLineEdit(self.settings.DEFAULT_TITLE)
        self.deck_title.setFont(font)

        title_layout.addWidget(title_label, 0, 0)
        title_layout.addWidget(self.deck_title, 0, 1, 1, 2)
        title_layout.setColumnStretch(1, 1)

        main_layout.addLayout(title_layout)

        # === Divider ===
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)

        # === Text Input ===
        input_label = QLabel("Paste Text to Translate")
        input_label.setFont(font)
        input_label.setAlignment(Qt.AlignLeft)
        main_layout.addWidget(input_label)

        self.input = QTextEdit()
        self.input.setFont(font)
        self.input.setPlainText(default_input)
        self.input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_layout.addWidget(self.input, 1)

        # === Generate Button ===
        self.process_btn = QPushButton("Generate Deck")
        self.process_btn.setFont(font)
        self.process_btn.setFixedHeight(40)
        self.process_btn.setEnabled(True)
        self.process_btn.clicked.connect(self.process_input)
        main_layout.addWidget(self.process_btn)

        self.setLayout(main_layout)

    def process_input(self):
        raw_text = self.input.toPlainText()
        preprocessed = self.text_processor.split_lines(raw_text)
        lines = self.text_processor.extract_unique_lines(preprocessed)

        pin = self.pin_input.text().strip()

        try:
            api_output = self.translation_service.request_translation_api(lines, pin=pin)
            data = json.loads(api_output)
            data = self.text_processor.add_indices_to_data(data)
        except Exception as e:
            print(f"Failed to parse translation API output: {e}")
            PopupService.show_error_popup(
                self,
                title="Translation Failed",
                message="Translation failed.\nPlease check your API key or network connection."
            )
            return

        output_dir = self.get_output_folder_callback()

        # Generate MP3 files
        self.voicevox_service.generate_mp3s(data)

        # Generate Anki deck
        self.anki_generator.generate_anki_deck(data, self.deck_title.text(), output_dir=output_dir)
