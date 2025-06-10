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
# Description: Module containing Ai Model downloader selector class and methods.

import os
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QGroupBox,
    QScrollArea,
    QVBoxLayout,
)

from wadas.domain.ai_model_downloader import AiModelsDownloader
from wadas.ui.error_message_dialog import WADASErrorMessage

module_dir_path = Path(__file__).resolve().parent
ai_det_models_dir_path = (Path(module_dir_path).parent.parent / "model" / "detection").resolve()
ai_class_models_dir_path = (Path(module_dir_path).parent.parent / "model" / "classification").resolve()

class Dialog_AiModelDownloaderSelector(QDialog):
    """Class to implement AI model downloader selector dialog."""

    def __init__(self, hf_token):
        super().__init__()

        self.selected_detection_models = []
        self.selected_classification_models = []
        self.setWindowTitle("Select AI Models to download")
        self.setWindowIcon(QIcon((Path(module_dir_path).parent / "img" / "mainwindow_icon.jpg").resolve().as_posix()))

        main_layout = QVBoxLayout(self)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        groupBox_detection = QGroupBox("Detection models", self)
        vertical_layout_detection = QVBoxLayout(groupBox_detection)

        detection_models, classification_models = AiModelsDownloader.get_available_models(hf_token)
        # Make sure local directories exists prior to download
        ai_det_models_dir_path.mkdir(parents=True, exist_ok=True)
        ai_class_models_dir_path.mkdir(parents=True, exist_ok=True)
        local_det_models = [d.name.replace("_openvino_model", "") for d in ai_det_models_dir_path.iterdir() if d.is_dir()]
        local_class_models = [d.name.replace("_openvino_model", "") for d in ai_class_models_dir_path.iterdir() if d.is_dir()]
        if detection_models and classification_models:
            for model in detection_models:
                checkbox = QCheckBox(model, self)
                if local_det_models and model in local_det_models:
                    checkbox.setChecked(True)
                    checkbox.setEnabled(False)
                vertical_layout_detection.addWidget(checkbox)

            scroll_area_detection = QScrollArea(self)
            scroll_area_detection.setWidgetResizable(True)
            scroll_area_detection.setWidget(groupBox_detection)


            groupBox_classification = QGroupBox("Classification models", self)
            vertical_layout_classification = QVBoxLayout(groupBox_classification)

            for model in classification_models:
                checkbox = QCheckBox(model, self)
                if local_class_models and model in local_class_models:
                    checkbox.setChecked(True)
                    checkbox.setEnabled(False)
                vertical_layout_classification.addWidget(checkbox)

            scroll_area_classification = QScrollArea(self)
            scroll_area_classification.setWidgetResizable(True)
            scroll_area_classification.setWidget(groupBox_classification)

            main_layout.addWidget(scroll_area_detection)
            main_layout.addWidget(scroll_area_classification)

            main_layout.addWidget(self.buttonBox)
        else:
            WADASErrorMessage("Error while downloading WADAS models",
                              "An error occurred while fetching available models list."
                              " Please retry.").exec()

    def accept(self):
        """Method to accept and close dialog"""

        for checkbox in self.findChildren(QCheckBox):
            if checkbox.isEnabled():
                if "Detection" in checkbox.parent().title() and checkbox.isChecked():
                    self.selected_detection_models.append(checkbox.text())

                if "Classification" in checkbox.parent().title() and checkbox.isChecked():
                    self.selected_classification_models.append(checkbox.text())

        super().accept()
