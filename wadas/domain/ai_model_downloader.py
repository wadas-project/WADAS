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
import zipfile
from pathlib import Path

from PySide6.QtCore import QObject, Signal
from wadas_runtime import WADASModelServer

logger = logging.getLogger(__name__)
MODULE_DIR_PATH = os.path.dirname(os.path.abspath(__file__))
MODEL_DIRECTORY = (Path(MODULE_DIR_PATH).parent.parent / "model").resolve()
MODEL_REQUEST_CFG = (MODEL_DIRECTORY / "request").resolve()
REPO_ID = "wadas-it/wadas"
WADAS_SERVER_URL = "https://api-dev.wadas.it:8443/"


class AiModelsDownloader(QObject):
    """Class implementing Ai Model download logic."""

    run_finished = Signal()
    run_progress = Signal(int)
    error_happened = Signal(str)
    download_success = Signal()
    update_status = Signal(str)

    def __init__(self, node_id: str, models):
        super(AiModelsDownloader, self).__init__()
        self.node_id = node_id
        self.stop_flag = False
        self.models = models
        self.success = True
        self.wadas_model_server = WADASModelServer(WADAS_SERVER_URL)

    def run(self):
        """AI Model(s) Download running in a dedicated thread"""

        total_phases = len(self.models) * 2
        try:
            os.makedirs(MODEL_DIRECTORY, exist_ok=True)
            self.update_status.emit("Initiating models download...")
            for i, model in enumerate(self.models):
                if self.stop_flag:
                    break

                model_path = model["path"].lstrip("/")
                local_model_dir = MODEL_DIRECTORY / model_path
                local_zipfile_path = f"{local_model_dir}.zip"
                # Make sure destination dir exists
                os.makedirs(os.path.dirname(local_model_dir), exist_ok=True)
                self.update_status.emit(f"Packaging and downloading {model['name']} model...")
                # Download the model zip file
                try:
                    download_status = self.wadas_model_server.download_model(
                        user_id=self.node_id,
                        model_name=model["name"],
                        model_path=str(local_zipfile_path),
                    )

                    if not download_status:
                        self.error_happened.emit(
                            f"Error downloading {model['name']}: Bad download status returned."
                        )
                        self.success = False
                        continue
                    self.run_progress.emit((i + 1) * 100 // total_phases)

                    # Unzip model files
                    self.update_status.emit(f"Unpackaging model {model['name']} ...")
                    with zipfile.ZipFile(local_zipfile_path, "r") as zip_ref:
                        zip_ref.extractall(local_model_dir)
                    if os.path.isfile(local_zipfile_path):
                        self.update_status.emit(f"Removing archive for {model['name']} model...")
                        os.remove(local_zipfile_path)
                    self.run_progress.emit((i + 2) * 100 // total_phases)
                except Exception as e:
                    self.error_happened.emit(f"Error downloading {model['name']}: {e}")
                    self.success = False
                    if os.path.isdir(local_model_dir):
                        os.remove(local_model_dir)
                    continue

            if self.success:
                self.download_success.emit()
            self.run_finished.emit()

        except Exception as e:
            self.error_happened.emit(str(e))

    def check_for_termination_requests(self):
        """Terminate current thread if interrupt request comes from Dialog."""

        if self.thread().isInterruptionRequested():
            self.stop_flag = True
            logger.error("Ai Models download cancelled by user.")
