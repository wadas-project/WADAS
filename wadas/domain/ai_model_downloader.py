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
import shutil
from pathlib import Path

import yaml
from huggingface_hub import hf_hub_download, list_repo_files
from PySide6.QtCore import QObject, Signal

logger = logging.getLogger(__name__)
module_dir_path = os.path.dirname(os.path.abspath(__file__))

MODEL_FILES = [
    "detection_model.xml",
    "detection_model.bin",
    "classification_model.xml",
    "classification_model.bin",
]
REPO_ID = "wadas-it/wadas"
SAVE_DIRECTORY = (Path(module_dir_path).parent.parent / "model").resolve()
CONFIG_FILE = "wadas_models.yaml"


class AiModelsDownloader(QObject):
    """Class implementing Ai Model download logic."""

    run_finished = Signal()
    run_progress = Signal(int)
    error_happened = Signal(str)

    def __init__(self, token, det_model_files, class_model_files):
        super(AiModelsDownloader, self).__init__()
        self.token = token
        self.stop_flag = False
        self.det_model_directories = det_model_files
        self.class_model_directories = class_model_files

    def run(self):
        """AI Model Download running in a dedicated thread"""
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
            remote_files = []
            # Get list of all files in the repository
            try:
                all_files = list_repo_files(repo_id=REPO_ID, use_auth_token=self.token)
            except Exception as e:
                self.error_happened.emit(f"Error listing files: {str(e)}")
                return

            for folder in models_folders:
                if self.stop_flag:
                    break

                # Filter only files that belongs to current folder
                cur_dir_remote_files = [f for f in all_files if f.startswith(str(folder))]
                # Add cur dir files to total list files
                remote_files.extend(cur_dir_remote_files)

            for i, remote_file_path in enumerate(remote_files):
                if self.stop_flag:
                    break

                local_file_path = Path(SAVE_DIRECTORY, remote_file_path)

                # Download the file
                try:
                    cached_file_path = hf_hub_download(
                        repo_id=REPO_ID, filename=remote_file_path, use_auth_token=self.token
                    )
                    # Make sure destination dir exists
                    os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
                    shutil.move(cached_file_path, local_file_path)

                    if remote_files:
                        self.run_progress.emit((i + 1) * 100 // len(remote_files))
                except Exception as e:
                    self.error_happened.emit(f"Error downloading {remote_file_path}: {e}")
                    continue

            self.run_finished.emit()

        except Exception as e:
            self.error_happened.emit(str(e))

    def check_for_termination_requests(self):
        """Terminate current thread if interrupt request comes from Dialog."""

        if self.thread().isInterruptionRequested():
            self.stop_flag = True
            logger.error("Ai Models download cancelled by user.")

    @classmethod
    def get_available_models(self, token):
        """Returns the names of available models from a YAML config file downloaded
        from Hugging Face."""
        try:
            # Download configuration file from Hugging Face
            config_file_path = hf_hub_download(
                repo_id=REPO_ID, filename=CONFIG_FILE, use_auth_token=token
            )

            with open(config_file_path, "r") as file_:
                config = yaml.safe_load(file_)
                detection_models = config.get("detection_models", ())
                classification_models = config.get("classification_models", ())
                return detection_models, classification_models
        except Exception:
            return (), ()

    @classmethod
    def get_default_models(self, token):
        """Returns the default detection and classification models from the YAML config file."""
        try:
            # Download configuration file from Hugging Face
            config_file_path = hf_hub_download(
                repo_id=REPO_ID, filename=CONFIG_FILE, use_auth_token=token
            )

            with open(config_file_path, "r") as file:
                config = yaml.safe_load(file)
                default_detection_model = config.get("default_detection_model", None)
                default_classification_model = config.get("default_classification_model", None)
                return (
                    [default_detection_model] if default_detection_model else [],
                    [default_classification_model] if default_classification_model else [],
                )
        except Exception:
            return (), ()
