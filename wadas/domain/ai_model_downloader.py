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
# Description: Module containing Ai Model downloader class and methods.

import logging
import os
from pathlib import Path

import requests
from PySide6.QtCore import QObject, Signal

from wadas.ui.error_message_dialog import WADASErrorMessage

logger = logging.getLogger(__name__)
module_dir_path = os.path.dirname(os.path.abspath(__file__))

AVAILABLE_MODELS_CFG_LOCAL = (
    Path(module_dir_path).parent.parent / "model" / "wadas_models.yaml"
).resolve()
MODEL_REQUEST_CFG = (Path(module_dir_path).parent.parent / "model" / "request").resolve()
MODEL_FILES = [
    "detection_model.xml",
    "detection_model.bin",
    "classification_model.xml",
    "classification_model.bin",
]
REPO_ID = "wadas-it/wadas"
SAVE_DIRECTORY = (Path(module_dir_path).parent.parent / "model").resolve()
WADAS_SERVER_URL = "https://localhost:8443/"


class AiModelsDownloader(QObject):
    """Class implementing Ai Model download logic."""

    run_finished = Signal()
    run_progress = Signal(int)
    error_happened = Signal(str)

    def __init__(self, node_id, det_model_files, class_model_files):
        super(AiModelsDownloader, self).__init__()
        self.node_id = node_id
        self.stop_flag = False
        self.det_model_directories = det_model_files
        self.class_model_directories = class_model_files

    def run(self):
        """AI Model(s) Download running in a dedicated thread"""
        try:
            os.makedirs(SAVE_DIRECTORY, exist_ok=True)

            # convert path to string
            absolute_det_dir_path = [
                Path("detection", item).as_posix() for item in self.det_model_directories
            ]
            absolute_class_dir_path = [
                Path("classification", item).as_posix() for item in self.class_model_directories
            ]
            models_folders = absolute_det_dir_path + absolute_class_dir_path

            for _folder in models_folders:
                if self.stop_flag:
                    break

            # TODO: update iteration logic
            for file_path in enumerate(self.det_model_directories + self.class_model_directories):
                if self.stop_flag:
                    break

                local_file_path = Path(SAVE_DIRECTORY, file_path)
                model_name = "DFv1.2"
                model_file_extension = "bin"

                # Download the file
                try:
                    DOWNLOAD_URL = (
                        f"{WADAS_SERVER_URL}api/v1/nodes/{self.node_id}/models/download?model_name="
                        f"{model_name}"
                        f"&type_ext={model_file_extension}"
                    )
                    # Make sure destination dir exists
                    os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

                    destination_file = Path(f"{model_name}.{model_file_extension}")
                    try:
                        response = requests.get(DOWNLOAD_URL, stream=True, timeout=30)

                        if response.status_code == 200:
                            with open(destination_file, "wb") as f:
                                for chunk in response.iter_content(chunk_size=8192):
                                    if chunk:
                                        f.write(chunk)
                            print(f"Modello scaricato correttamente: {destination_file}")
                        elif response.status_code == 401:
                            WADASErrorMessage(
                                "Authentication failed!", "(401): unauthorized access."
                            ).exec()
                        else:
                            WADASErrorMessage(
                                "Download error", f"Error code: {response.status_code}"
                            ).exec()

                    except requests.exceptions.RequestException as e:
                        WADASErrorMessage("Error while downloading model file", str(e)).exec()

                    # if remote_files:
                    # self.run_progress.emit((i + 1) * 100 // len(remote_files))
                except Exception as e:
                    self.error_happened.emit(f"Error downloading {file_path}: {e}")
                    continue

            self.run_finished.emit()

        except Exception as e:
            self.error_happened.emit(str(e))

    def check_for_termination_requests(self):
        """Terminate current thread if interrupt request comes from Dialog."""

        if self.thread().isInterruptionRequested():
            self.stop_flag = True
            logger.error("Ai Models download cancelled by user.")
