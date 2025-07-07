import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication, QStackedWidget
from PySide6.QtGui import QIcon
from services.settings_service import SettingsService
from UI import generator, settings_page, terms_page  # Removed pin_page
from services.cleanup_service import CleanupService
from services.tts_service import TextToSpeechService

BASE_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))

class MainWindow(QStackedWidget):
    def __init__(self):
        super().__init__()

        # Initialize SettingsService
        self.settings_service = SettingsService(BASE_DIR)
        self.voicevox_service = TextToSpeechService(BASE_DIR)
        self.settings_data = self.settings_service.load_settings()

        self.setWindowTitle(self.settings_data.WINDOW_TITLE)
        icon_path = BASE_DIR / self.settings_data.ICON_FILE
        self.setWindowIcon(QIcon(str(icon_path)))

        # Initialize Generator page WITHOUT starting Voicevox here
        self.generator_page = generator.GeneratorPage(
            base_dir=BASE_DIR,
            settings=self.settings_data,
            open_settings_callback=self.show_settings,
            get_output_folder_callback=self.settings_service.get_output_folder
        )

        self.settings_page = settings_page.SettingsPage(
            base_dir=BASE_DIR,
            settings=self.settings_data,
            settings_service=self.settings_service,
            back_to_generator_callback=self.show_generator
        )

        self.terms_page = terms_page.TermsPage(
            base_dir=BASE_DIR,
            settings=self.settings_data,
            on_accept_callback=self.terms_accepted
        )

        self.addWidget(self.terms_page)
        self.addWidget(self.generator_page)
        self.addWidget(self.settings_page)

        # Decide initial screen
        if not self.settings_service.is_terms_accepted():
            self.setCurrentWidget(self.terms_page)
        else:
            self.setCurrentWidget(self.generator_page)

        self.cleanup_service = CleanupService(BASE_DIR)

        # VoiceVox service and process references from generator page
        self.voicevox_service = self.generator_page.voicevox_service
        self.voicevox_proc = self.voicevox_service.start_voicevox_process()

    def show_settings(self):
        self.settings_page.set_folder_path(self.settings_service.get_output_folder())
        self.settings_page.set_voicevox_path(self.settings_service.get_voicevox_path())
        self.setCurrentWidget(self.settings_page)

    def show_generator(self):
        self.settings_service.set_output_folder(self.settings_page.get_folder_path())
        self.settings_service.set_voicevox_path(self.settings_page.get_voicevox_path())
        self.setCurrentWidget(self.generator_page)

    def terms_accepted(self):
        self.settings_service.set_terms_accepted()
        self.setCurrentWidget(self.generator_page)

    def cleanup(self):
        self.cleanup_service.perform_cleanup(self.voicevox_proc, self.voicevox_service)



if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.resize(window.settings_data.WINDOW_LENGTH, window.settings_data.WINDOW_WIDTH)
    window.show()

    # Connect app exit to cleanup
    app.aboutToQuit.connect(window.cleanup)

    sys.exit(app.exec())
