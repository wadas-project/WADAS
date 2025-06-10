import os

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMessageBox

module_dir_path = os.path.dirname(os.path.abspath(__file__))


class WADASErrorMessage(QMessageBox):
    """Class to show error messages with WADAS logo and config as default."""

    def __init__(self, title, message):
        super(WADASErrorMessage, self).__init__()
        self.setWindowTitle(title)
        self.setText(message)
        self.setIcon(QMessageBox.Critical)  # Imposta l'icona come errore critico
        self.setWindowIcon(QIcon(os.path.join(module_dir_path, "..", "img", "mainwindow_icon.jpg")))