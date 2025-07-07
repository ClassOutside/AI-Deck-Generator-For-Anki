from pathlib import Path
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QIcon, QFont
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QFileDialog, QFrame
)
from services.encryption_service import EncryptionService
from services.popup_service import PopupService

class SettingsPage(QWidget):
    def __init__(
        self,
        base_dir: Path,
        settings,
        settings_service,
        back_to_generator_callback
    ):
        super().__init__()
        self.BASE_DIR = base_dir
        self.settings = settings
        self.settings_service = settings_service
        self.back_to_generator_callback = back_to_generator_callback

        self.encryption_service = EncryptionService()

        font = QFont()
        font.setPointSize(self.settings.FONT_SIZE)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(*self.settings.MARGINS)
        main_layout.setSpacing(self.settings.SPACING)

        # Top Bar
        top_bar = QGridLayout()
        back_button = QPushButton()
        back_button.setIcon(QIcon(str(self.BASE_DIR / "icons/chevron-left.svg")))
        back_button.setIconSize(QSize(20, 20))
        back_button.setFixedSize(30, 30)
        back_button.setFlat(True)
        back_button.setToolTip("Back")
        back_button.clicked.connect(self.back_to_generator_callback)
        top_bar.addWidget(back_button, 0, 0, alignment=Qt.AlignTop | Qt.AlignLeft)

        icon_label = QLabel()
        pixmap = QPixmap(str(self.BASE_DIR / self.settings.ICON_FILE))
        icon_label.setPixmap(pixmap.scaled(
            self.settings.ICON_SIZE, self.settings.ICON_SIZE,
            Qt.KeepAspectRatio, Qt.SmoothTransformation
        ))
        icon_label.setAlignment(Qt.AlignCenter)
        top_bar.addWidget(icon_label, 0, 1, alignment=Qt.AlignTop | Qt.AlignHCenter)
        top_bar.addWidget(QWidget(), 0, 2)
        main_layout.addLayout(top_bar)

        # Output Folder
        folder_layout = QGridLayout()
        folder_layout.addWidget(self._label("Output Folder", font), 0, 0)
        self.folder_path = QLineEdit()
        self.folder_path.setFont(font)
        self.folder_path.setReadOnly(True)
        folder_layout.addWidget(self.folder_path, 0, 1)

        browse_btn = QPushButton("Browse…")
        browse_btn.setFont(font)
        browse_btn.clicked.connect(self.browse_folder)
        folder_layout.addWidget(browse_btn, 0, 2)
        folder_layout.setColumnStretch(1, 1)
        main_layout.addLayout(folder_layout)

        # VOICEVOX Path
        voicevox_layout = QGridLayout()
        voicevox_layout.addWidget(self._label("VOICEVOX Path", font), 0, 0)
        self.voicevox_path = QLineEdit()
        self.voicevox_path.setFont(font)
        self.voicevox_path.setReadOnly(True)
        voicevox_layout.addWidget(self.voicevox_path, 0, 1)

        browse_voicevox_btn = QPushButton("Browse…")
        browse_voicevox_btn.setFont(font)
        browse_voicevox_btn.clicked.connect(self.browse_voicevox_path)
        voicevox_layout.addWidget(browse_voicevox_btn, 0, 2)
        voicevox_layout.setColumnStretch(1, 1)
        main_layout.addLayout(voicevox_layout)

        # API Key
        api_key_layout = QGridLayout()
        api_key_layout.addWidget(self._label("Update API Key", font), 0, 0)
        self.api_key_field = QLineEdit()
        self.api_key_field.setFont(font)
        api_key_layout.addWidget(self.api_key_field, 0, 1)
        api_key_layout.setColumnStretch(1, 1)
        main_layout.addLayout(api_key_layout)

        # PIN Field
        pin_layout = QGridLayout()
        pin_layout.addWidget(self._label("PIN", font), 0, 0)
        self.pin_field = QLineEdit()
        self.pin_field.setFont(font)
        self.pin_field.setEchoMode(QLineEdit.Password)
        pin_layout.addWidget(self.pin_field, 0, 1)
        pin_layout.setColumnStretch(1, 1)
        main_layout.addLayout(pin_layout)

        # Line separator
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)

        # Save Button
        self.save_btn = QPushButton("Save Settings")
        self.save_btn.setFont(font)
        self.save_btn.setFixedHeight(40)
        self.save_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self.on_save_clicked)
        main_layout.addWidget(self.save_btn)

        main_layout.addStretch(1)
        self.setLayout(main_layout)

        # Initialize values from settings service
        self.folder_path.setText(self.settings_service.get_output_folder())
        self.voicevox_path.setText(self.settings_service.get_voicevox_path())

        # Connect signals for validation
        self.api_key_field.textChanged.connect(self.update_save_button_state)
        self.pin_field.textChanged.connect(self.update_save_button_state)
        self.folder_path.textChanged.connect(self.update_save_button_state)
        self.voicevox_path.textChanged.connect(self.update_save_button_state)
        self.update_save_button_state()

    def _label(self, text, font):
        lbl = QLabel(text)
        lbl.setFont(font)
        lbl.setFixedWidth(160)
        return lbl

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder", str(Path.cwd()))
        if folder:
            self.folder_path.setText(folder)

    def browse_voicevox_path(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select VOICEVOX Executable", str(Path.cwd()))
        if path:
            self.voicevox_path.setText(path)

    def on_save_clicked(self):
        folder_text = self.folder_path.text().strip()
        voicevox_text = self.voicevox_path.text().strip()
        api_key_text = self.api_key_field.text().strip()
        pin_text = self.pin_field.text().strip()

        self.settings_service.set_output_folder(folder_text)
        self.settings_service.set_voicevox_path(voicevox_text)
        self.settings_service.save_settings()

        if api_key_text and pin_text:
            self.settings_service.encrypt_and_store_api_key(api_key_text, pin_text)

        # Always show restart required popup
        PopupService.show_error_popup(
            self, "Restart Required",
            "Please restart the application for the changes to take effect."
        )

        self.back_to_generator_callback()

    def update_save_button_state(self):
        api_key = self.api_key_field.text().strip()
        pin = self.pin_field.text().strip()
        # Validate API key and PIN logic - both empty or both present
        api_key_and_pin_valid = ((not api_key and not pin) or (bool(api_key) and bool(pin)))
        self.save_btn.setEnabled(api_key_and_pin_valid)

    # Additional helper getters/setters if needed
    def get_folder_path(self):
        return self.folder_path.text()

    def set_folder_path(self, path):
        self.folder_path.setText(path)

    def get_voicevox_path(self):
        return self.voicevox_path.text()

    def set_voicevox_path(self, path):
        self.voicevox_path.setText(path)
