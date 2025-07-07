# services/popup_service.py

from PySide6.QtWidgets import QMessageBox, QWidget

class PopupService:
    @staticmethod
    def show_error_popup(parent: QWidget, title: str = "Error", message: str = None):
        if message is None:
            message = (
                "An unexpected error occurred."
            )
        QMessageBox.information(
            parent,
            title,
            message,
            QMessageBox.Ok
        )
