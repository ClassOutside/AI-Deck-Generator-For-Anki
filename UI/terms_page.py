from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QSizePolicy, QTextEdit
)


class TermsPage(QWidget):
    def __init__(self, base_dir: Path, settings, on_accept_callback):
        super().__init__()

        self.BASE_DIR = base_dir
        self.settings = settings
        self.on_accept_callback = on_accept_callback

        font = QFont()
        font.setPointSize(self.settings.FONT_SIZE)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(*self.settings.MARGINS)
        main_layout.setSpacing(self.settings.SPACING)

        # === Icon at top center ===
        icon_label = QLabel()
        icon_path = self.BASE_DIR / self.settings.ICON_FILE
        pixmap = QPixmap(str(icon_path))
        icon_label.setPixmap(
            pixmap.scaled(self.settings.ICON_SIZE, self.settings.ICON_SIZE,
                          Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )
        icon_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(icon_label)

        # === Terms prompt label ===
        terms_label = QLabel(
            "Please read and accept the terms and conditions to continue."
        )
        terms_label.setFont(font)
        terms_label.setWordWrap(True)
        terms_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(terms_label)

        # === Scrollable, non-editable terms text ===
        terms_text = QTextEdit()
        terms_text.setFont(font)
        terms_text.setReadOnly(True)
        terms_path = self.BASE_DIR / 'TERMS_AND_CONDITIONS.txt'
        try:
            with open(terms_path, 'r', encoding='utf-8') as f:
                terms_content = f.read()
        except FileNotFoundError:
            terms_content = "Terms and conditions file not found."
        except Exception as e:
            terms_content = f"Error loading terms: {e}"

        terms_text.setPlainText(terms_content)
        terms_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_layout.addWidget(terms_text)

        # === Accept Button ===
        accept_btn = QPushButton("Accept")
        accept_btn.setFont(font)
        accept_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        accept_btn.setFixedHeight(40)
        accept_btn.clicked.connect(self.accept_terms)
        main_layout.addWidget(accept_btn)

        main_layout.addStretch(1)

        self.setLayout(main_layout)

    def accept_terms(self):
        self.on_accept_callback()
