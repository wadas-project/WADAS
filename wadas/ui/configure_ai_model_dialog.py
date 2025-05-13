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
# Date: 2024-08-14
# Description: Configure Ai model module.


import os
from pathlib import Path

import openvino as ov
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QDialogButtonBox

from wadas.ai.models import txt_animalclasses
from wadas.domain.ai_model import AiModel

#from wadas.ui.ai_model_download_dialog import AiModelDownloadDialog
from wadas.ui.access_request_dialog import AccessRequestDialog
from wadas.ui.qt.ui_configure_ai_model import Ui_DialogConfigureAi

module_dir_path = os.path.dirname(os.path.abspath(__file__))
det_models_dir_path = (Path(module_dir_path).parent.parent / "model" / "detection").resolve()
class_models_dir_path = (Path(module_dir_path).parent.parent / "model" / "classification").resolve()


class ConfigureAiModel(QDialog, Ui_DialogConfigureAi):
    """Class to instantiate UI dialog to configure Ai model parameters."""

    def __init__(self):
        super(ConfigureAiModel, self).__init__()
        self.ui = Ui_DialogConfigureAi()

        # UI
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon((Path(module_dir_path).parent / "img" / "mainwindow_icon.jpg").resolve().as_posix()))
        self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        self.ui.label_errorMEssage.setStyleSheet("color: red")
        self.ui.lineEdit_classificationThreshold.setText(str(AiModel.classification_threshold))
        self.ui.lineEdit_detectionThreshold.setText(str(AiModel.detection_threshold))
        self.ui.lineEdit_video_fps.setText(str(AiModel.video_fps))
        self.populate_language_dropdown()
        self.available_ai_devices = ov.Core().get_available_devices()
        self.available_ai_devices.append("auto")
        self.populate_ai_models_version_dropdown()
        self.populate_ai_devices_dropdowns()

        # Slots
        self.ui.buttonBox.accepted.connect(self.accept_and_close)
        self.ui.lineEdit_classificationThreshold.textChanged.connect(self.validate_data)
        self.ui.lineEdit_detectionThreshold.textChanged.connect(self.validate_data)
        self.ui.lineEdit_video_fps.textChanged.connect(self.validate_data)
        self.ui.pushButton_download_models.clicked.connect(self.on_download_models_clicked)

        self.validate_data()


    def populate_language_dropdown(self):
        """Populate the dropdown with the list of available actuators."""
        self.ui.comboBox_class_lang.clear()
        for language in txt_animalclasses:
            self.ui.comboBox_class_lang.addItem(language)
        if AiModel.language in txt_animalclasses:
            self.ui.comboBox_class_lang.setCurrentText(AiModel.language)

    def populate_ai_devices_dropdowns(self):
        """Method to populate Ai devices list dropdowns."""

        self.ui.comboBox_detection_dev.clear()
        self.ui.comboBox_class_dev.clear()

        for device in self.available_ai_devices:
            self.ui.comboBox_detection_dev.addItem(device)
            self.ui.comboBox_class_dev.addItem(device)
        if AiModel.detection_device in self.available_ai_devices:
            self.ui.comboBox_detection_dev.setCurrentText(AiModel.detection_device)
        else:
            self.ui.comboBox_detection_dev.setCurrentText("auto")
        if AiModel.classification_device in self.available_ai_devices:
            self.ui.comboBox_class_dev.setCurrentText(AiModel.classification_device)
        else:
            self.ui.comboBox_detection_dev.setCurrentText("auto")

    def populate_ai_models_version_dropdown(self):
        """Method to populate Ai models versions dropdowns"""

        self.ui.comboBox_detection_model_version.clear()
        self.ui.comboBox_classification_model_version.clear()

        if (det_models_dir := Path(det_models_dir_path)).is_dir():
            det_models_directories = (d for d in det_models_dir.iterdir() if d.is_dir())
            for directory in det_models_directories:
                bin_files = [f for f in directory.iterdir() if f.suffix == ".bin"]
                if bin_files:
                    model_version = bin_files[0].stem  # Remove .bin extension
                    self.ui.comboBox_detection_model_version.addItem(model_version)
        self.ui.comboBox_detection_model_version.setCurrentText(AiModel.detection_model_version)

        if (class_models_dir := Path(class_models_dir_path)).is_dir():
            class_models_directories = (d for d in class_models_dir.iterdir() if d.is_dir())
            for directory in class_models_directories:
                bin_files = [f for f in directory.iterdir() if f.suffix == ".bin"]
                if bin_files:
                    model_version = bin_files[0].stem  # Remove .bin extension
                    self.ui.comboBox_classification_model_version.addItem(model_version)
        self.ui.comboBox_classification_model_version.setCurrentText(AiModel.classification_model_version)

    def on_download_models_clicked(self):
        """Method to trigger the download of Ai Models"""

        ai_model_download_dlg = AccessRequestDialog()
        if ai_model_download_dlg.exec():
            self.populate_ai_models_version_dropdown()

    def validate_data(self):
        """Method to validate input values."""

        valid = True
        error_message = ""
        if not self.ui.lineEdit_classificationThreshold.text():
            error_message = "No classification threshold provided. Please insert a value between 0 and 1."
            valid = False
        elif (
            cthreshold := float(self.ui.lineEdit_classificationThreshold.text())
        ) > 1 or cthreshold < 0:
            error_message = "Invalid classification threshold. Please insert a value between 0 and 1."
            valid = False

        if not self.ui.lineEdit_detectionThreshold.text():
            error_message = "No detection threshold provided. Please insert a value between 0 and 1."
            valid = False
        elif (dthreshold := float(self.ui.lineEdit_detectionThreshold.text())) > 1 or dthreshold < 0:
            error_message = "Invalid detection threshold. Please insert a value between 0 and 1."
            valid = False

        if not self.ui.lineEdit_video_fps.text():
            error_message = "No video down sampling value provided. Please insert a value > 0."
            valid = False
        elif int(self.ui.lineEdit_video_fps.text()) <= 0:
            error_message = "Invalid video down sampling value. Please insert a value > 0."
            valid = False

        self.ui.label_errorMEssage.setText(error_message)
        self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(valid)

    def accept_and_close(self):
        """When Ok is clicked, save Ai model config info before closing."""

        AiModel.classification_threshold = float(self.ui.lineEdit_classificationThreshold.text())
        AiModel.detection_threshold = float(self.ui.lineEdit_detectionThreshold.text())
        AiModel.language = self.ui.comboBox_class_lang.currentText()
        AiModel.detection_device = self.ui.comboBox_detection_dev.currentText()
        AiModel.classification_device = self.ui.comboBox_class_dev.currentText()
        AiModel.video_fps = int(self.ui.lineEdit_video_fps.text())
        AiModel.detection_model_version = self.ui.comboBox_detection_model_version.currentText()
        AiModel.classification_model_version = self.ui.comboBox_classification_model_version.currentText()
        self.accept()
