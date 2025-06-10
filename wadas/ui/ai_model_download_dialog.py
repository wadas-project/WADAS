# This file is part of WADAS project.
#
# WADAS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# WADAS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with WADAS. If not, see <https://www.gnu.org/licenses/>.
#
# Author(s): Stefano Dell'Osa, Alessandro Palla, Cesare Di Mauro, Antonio Farina
# Date: 2025-01-01
# Description: Module containing Ai Model Downloader Dialog class and methods.

import os
from pathlib import Path

from PySide6.QtCore import QThread
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QDialog,
    QMessageBox
)

from wadas.domain.ai_model_downloader import AiModelsDownloader
from wadas.ui.ai_model_downloader_selector_dialog import Dialog_AiModelDownloaderSelector
from wadas.ui.qt.ui_ai_model_download import Ui_AiModelDownloadDialog

module_dir_path = os.path.dirname(os.path.abspath(__file__))

class AiModelDownloadDialog(QDialog, Ui_AiModelDownloadDialog):
    """Class to implement AI model download dialog."""

    def __init__(self, no_model=False):
        super().__init__()
        self.ui = Ui_AiModelDownloadDialog()
        self.setWindowTitle("Download AI Models")
        self.setWindowIcon(QIcon((Path(module_dir_path).parent / "img" / "mainwindow_icon.jpg").resolve().as_posix()))

        self.det_models = []
        self.class_models = []
        self.thread = None
        self.downloader = None
        self.stop_flag = False
        self.download_success = False

        self.ui.setupUi(self)
        self.ui.progressBar.setRange(0, 100)
        self.ui.progressBar.setValue(0)
        self.ui.progressBar.setEnabled(False)
        self.ui.pushButton_download.setEnabled(False)
        self.ui.pushButton_select_model_version.setVisible(False)
        self.ui.pushButton_select_model_version.setEnabled(False)
        self.ui.progressBar.setVisible(False)
        self.ui.lineEdit_token.textChanged.connect(self.validate)
        self.ui.pushButton_download.clicked.connect(self.download_models)
        self.ui.pushButton_cancel.clicked.connect(self.cancel_download)
        self.ui.pushButton_select_model_version.clicked.connect(self.on_select_model_version_button_clicked)
        self.ui.checkBox_select_versions.clicked.connect(self.on_select_model_version_checkbox_clicked)

        welcome_message = "Download WADAS models from Huggingface.co/wadas-it/wadas" if not no_model else\
            "Ai Model files not found. Download them from Huggingface.co/wadas-it/wadas."
        self.ui.label_welcome_message.setText(welcome_message)

    def on_select_model_version_checkbox_clicked(self):
        """Method to enable select model button basing on checkbox status"""

        self.ui.pushButton_select_model_version.setVisible(self.ui.checkBox_select_versions.isChecked())
        self.update_select_model_button_enablement()

    def on_select_model_version_button_clicked(self):
        """Method to select Ai model versions to download"""

        dialog = Dialog_AiModelDownloaderSelector(self.ui.lineEdit_token.text())
        if not dialog.exec():
            self.ui.checkBox_select_versions.setChecked(False)
            self.ui.pushButton_select_model_version.setVisible(False)
        else:
            self.det_models = dialog.selected_detection_models
            self.class_models = dialog.selected_classification_models

    def update_select_model_button_enablement(self):
        """Method to enable/disable select model versions button"""

        self.ui.pushButton_select_model_version.setEnabled(bool(self.ui.lineEdit_token.text()))

    def download_models(self):
        """Method to trigger the model download"""

        token = self.ui.lineEdit_token.text().strip()
        if not token:
            QMessageBox.critical(self, "Error", "Token field cannot be empty.")
            return

        if not self.ui.checkBox_select_versions.isChecked():
            # Fetch default versions if no custom selection is checked
            self.det_models, self.class_models = AiModelsDownloader.get_default_models(self.ui.lineEdit_token.text())

        self.ui.progressBar.setVisible(True)
        self.ui.progressBar.setEnabled(True)
        self.ui.pushButton_download.setEnabled(False)
        self.ui.pushButton_cancel.setEnabled(True)
        self.ui.lineEdit_token.setEnabled(False)

        self.thread = QThread()

        # Move downloader to a dedicated thread
        self.downloader = AiModelsDownloader(token, self.det_models, self.class_models)
        self.downloader.moveToThread(self.thread)

        # Connect signals
        self.thread.started.connect(self.downloader.run)
        self.downloader.run_finished.connect(self.on_download_complete)
        self.downloader.run_progress.connect(self.update_progress_bar)
        self.downloader.error_happened.connect(self.handle_error)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(self.downloader.deleteLater)

        self.thread.start()

    def update_progress_bar(self, percentage):
        """Update the progress bar safely from any thread."""

        self.ui.progressBar.setValue(percentage)

    def handle_error(self, error_message):
        """Method to handle download errors"""

        QMessageBox.critical(self, "Error", f"An error occurred: {error_message}")
        self.ui.pushButton_download.setEnabled(True)
        self.ui.progressBar.setEnabled(False)
        self.ui.lineEdit_token.setEnabled(True)

    def on_download_complete(self):
        """Handle successful download"""

        QMessageBox.information(self, "Success", "All model files have been successfully downloaded.")
        if self.thread:
            self.thread.quit()
            self.thread.wait()
        self.download_success = True
        self.accept()

    def cancel_download(self):
        """Method to cancel AI Model download"""
        if self.downloader:
            self.downloader.stop_flag = True
        if self.thread and self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()

        self.reject()

    def validate(self):
        """Method to validate the dialog input fields"""

        self.update_select_model_button_enablement()
        self.ui.pushButton_download.setEnabled(bool(self.ui.lineEdit_token.text()))

    def closeEvent(self, event):
        """Handle the dialog close event."""
        if self.thread and self.thread.isRunning():
            self.downloader.stop_flag = True
            self.thread.quit()
            self.thread.wait()