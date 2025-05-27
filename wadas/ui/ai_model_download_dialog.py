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
    QCheckBox,
    QDialog,
    QGroupBox,
    QScrollArea,
    QVBoxLayout, QMessageBox,
)

from wadas.domain.ai_model_downloader import AiModelsDownloader, WADAS_SERVER_URL
from wadas.ui.error_message_dialog import WADASErrorMessage
from wadas.ui.qt.ui_ai_model_download import Ui_AiModelDownloadDialog
from wadas_runtime import WADASModelServer

module_dir_path = os.path.dirname(os.path.abspath(__file__))
AI_DET_MODELS_DIR_PATH = (Path(module_dir_path).parent.parent / "model" / "detection").resolve()
AI_CLASS_MODELS_DIR_PATH = (Path(module_dir_path).parent.parent / "model" / "classification").resolve()
MODEL_REQUEST_CFG = (Path(module_dir_path).parent.parent / "model" / "request").resolve()

class AiModelDownloadDialog(QDialog, Ui_AiModelDownloadDialog):
    """Class to implement AI model download dialog."""

    def __init__(self, node_id: str):
        super().__init__()
        self.ui = Ui_AiModelDownloadDialog()
        self.setWindowTitle("Download AI Models")
        self.setWindowIcon(QIcon((Path(module_dir_path).parent / "img" / "mainwindow_icon.jpg").resolve().as_posix()))

        self.models = []
        self.node_id = node_id
        self.thread = None
        self.downloader = None
        self.stop_flag = False
        self.download_success = False
        self.wadas_model_server = WADASModelServer(WADAS_SERVER_URL)

        self.ui.setupUi(self)
        self.ui.progressBar.setRange(0, 100)
        self.ui.progressBar.setValue(0)
        self.ui.progressBar.setEnabled(False)
        self.ui.groupBox_available_models.setVisible(False)
        self.ui.progressBar.setVisible(False)

        self.classification_models = None
        self.detection_models = None

        # Slots
        self.ui.pushButton_download.clicked.connect(self.download_models)
        self.ui.pushButton_cancel.clicked.connect(self.cancel_download)
        self.ui.checkBox_select_versions.clicked.connect(self.on_select_model_version_checkbox_clicked)

        self.adjustSize()

    def get_available_models(self):
        """Returns the names of available models from a YAML config file downloaded
        from WADAS server."""

        try:
            self.models = self.wadas_model_server.available_models(self.node_id)
        except Exception as e:
            WADASErrorMessage("Error while requesting available models from server", str(e)).exec()

    def initialize_models_list(self):
        """Method to handle AI models list initialization"""

        self.get_available_models()  # This should populate self.models (a list of dicts)

        # Ensure local directories exist
        AI_DET_MODELS_DIR_PATH.mkdir(parents=True, exist_ok=True)
        AI_CLASS_MODELS_DIR_PATH.mkdir(parents=True, exist_ok=True)

        # Get names of locally available models
        local_det_models = [
            d.name.replace("_openvino_model", "") for d in AI_DET_MODELS_DIR_PATH.iterdir() if d.is_dir()
        ]
        local_class_models = [
            d.name.replace("_openvino_model", "") for d in AI_CLASS_MODELS_DIR_PATH.iterdir() if d.is_dir()
        ]

        # Group models by path
        self.detection_models = [m for m in self.models if m["type"] == "detection"]
        self.classification_models = [m for m in self.models if m["type"] == "classification"]

        # Check if available models were successfully loaded
        if not (self.detection_models or self.classification_models):
            WADASErrorMessage(
                "Error while downloading WADAS models",
                "An error occurred while fetching available models list. Please retry."
            ).exec()
            return

        # Ensure the groupBox has a layout; create one if not
        if self.ui.groupBox_available_models.layout() is None:
            layout = QVBoxLayout(self.ui.groupBox_available_models)
            self.ui.groupBox_available_models.setLayout(layout)
        else:
            layout = self.ui.groupBox_available_models.layout()
            # Remove previously added widgets
            for i in reversed(range(layout.count())):
                widget = layout.itemAt(i).widget()
                if widget is not None:
                    widget.setParent(None)

        # Build the detection models group
        if self.detection_models:
            groupBox_detection = QGroupBox("Detection models", self)
            vertical_layout_detection = QVBoxLayout(groupBox_detection)

            for model in self.detection_models:
                model_name = model["name"]
                is_local = model_name in local_det_models
                is_default = model.get("is_default", False)

                checkbox = QCheckBox(model_name, self)

                if is_local:
                    checkbox.setChecked(True)
                    checkbox.setEnabled(False)
                elif is_default:
                    checkbox.setChecked(True)

                if is_default:
                    checkbox.setStyleSheet("font-weight: bold;")
                    checkbox.setText(f"{model_name} (default)")

                vertical_layout_detection.addWidget(checkbox)

            groupBox_detection.setMinimumHeight(150)
            scroll_area_detection = QScrollArea(self)
            scroll_area_detection.setWidgetResizable(True)
            scroll_area_detection.setWidget(groupBox_detection)
            layout.addWidget(scroll_area_detection)

        # Build the classification models group
        if self.classification_models:
            groupBox_classification = QGroupBox("Classification models", self)
            vertical_layout_classification = QVBoxLayout(groupBox_classification)

            for model in self.classification_models:
                model_name = model["name"]
                is_local = model_name in local_class_models
                is_default = model.get("is_default", False)

                checkbox = QCheckBox(model_name, self)

                if is_local:
                    checkbox.setChecked(True)
                    checkbox.setEnabled(False)
                elif is_default:
                    checkbox.setChecked(True)

                if is_default:
                    checkbox.setStyleSheet("font-weight: bold;")
                    checkbox.setText(f"{model_name} (default)")

                vertical_layout_classification.addWidget(checkbox)

            groupBox_classification.setMinimumHeight(150)
            scroll_area_classification = QScrollArea(self)
            scroll_area_classification.setWidgetResizable(True)
            scroll_area_classification.setWidget(groupBox_classification)
            layout.addWidget(scroll_area_classification)

        # Enable and show relevant UI elements
        self.ui.groupBox_available_models.setVisible(True)
        self.ui.progressBar.setVisible(True)
        self.ui.pushButton_download.setEnabled(True)

    def on_select_model_version_checkbox_clicked(self):
        """Method to enable select model button basing on checkbox status"""

        list_models = self.ui.checkBox_select_versions.isChecked()
        self.ui.groupBox_available_models.setVisible(list_models)
        if list_models:
            self.initialize_models_list()
        self.adjustSize()

    def get_default_models(self):
        """Method to get default models for download"""

        default_detection_models = []
        default_classification_models = []

        for model in self.models:
            if model.get("is_default"):
                if model.get("type") == "detection":
                    default_detection_models.append(model)
                elif model.get("type") == "classification":
                    default_classification_models.append(model)

        return default_detection_models, default_classification_models

    def download_models(self):
        """Method to trigger the model download"""

        if not self.ui.checkBox_select_versions.isChecked():
            # Fetch default versions if no custom selection is checked
            self.detection_models, self.classification_models = self.get_default_models()

        self.ui.progressBar.setVisible(True)
        self.ui.progressBar.setEnabled(True)
        self.ui.pushButton_download.setEnabled(False)
        self.ui.pushButton_cancel.setEnabled(True)

        self.thread = QThread()

        # Move downloader to a dedicated thread
        self.downloader = AiModelsDownloader(self.node_id, self.detection_models + self.classification_models)
        self.downloader.moveToThread(self.thread)

        # Connect signals
        self.thread.started.connect(self.downloader.run)
        self.downloader.run_finished.connect(self.on_download_complete)
        self.downloader.run_progress.connect(self.update_progress_bar)
        self.downloader.error_happened.connect(self.handle_error)
        self.downloader.download_success.connect(self.on_download_succeeded)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(self.downloader.deleteLater)

        self.thread.start()

    def update_progress_bar(self, percentage):
        """Update the progress bar safely from any thread."""

        self.ui.progressBar.setValue(percentage)

    def handle_error(self, error_message):
        """Method to handle download errors"""

        WADASErrorMessage("Error", f"An error occurred: {error_message}").exec()
        self.ui.pushButton_download.setEnabled(True)
        self.ui.progressBar.setEnabled(False)

    def on_download_succeeded(self):
        """Handle successful download"""
        QMessageBox.information(self, "Success", "All model files have been successfully downloaded.")

    def on_download_complete(self):
        """Handle end of download"""

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

    def closeEvent(self, event):
        """Handle the dialog close event."""
        if self.thread and self.thread.isRunning():
            self.downloader.stop_flag = True
            self.thread.quit()
            self.thread.wait()