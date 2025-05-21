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
# Description: Ai models access request module.
import json
import os
from pathlib import Path
import requests

import keyring
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QDialogButtonBox

from wadas.domain.ai_model_downloader import WADAS_SERVER_URL
from wadas.ui.access_request_dialog import AccessRequestDialog
from wadas.ui.ai_model_download_dialog import AiModelDownloadDialog
from wadas.ui.error_message_dialog import WADASErrorMessage
from wadas.ui.qt.ui_model_request_login import Ui_DialogModelRequestLogin
from wadas_runtime import WADASModelServer

module_dir_path = os.path.dirname(os.path.abspath(__file__))
MODELS_FOLDER = Path(module_dir_path).parent.parent / "model"
MODEL_REQUEST_CFG = MODELS_FOLDER / "request"
MODEL_NODE_CFG = MODELS_FOLDER / "user"


class DialogModelRequestLogin(QDialog, Ui_DialogModelRequestLogin):
    """Class to instantiate UI dialog to configure Ai model parameters."""

    def __init__(self):
        super(DialogModelRequestLogin, self).__init__()
        self.ui = Ui_DialogModelRequestLogin()

        # UI
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon((Path(module_dir_path).parent / "img" / "mainwindow_icon.jpg").resolve().as_posix()))
        self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        self.ui.label_error.setStyleSheet("color: red")

        # Slots
        self.ui.buttonBox.accepted.connect(self.accept_and_close)
        self.ui.pushButton_request.clicked.connect(self.handle_request)
        self.ui.lineEdit_email.textChanged.connect(self.validate)
        self.ui.lineEdit_token.textChanged.connect(self.validate)

        self.wadas_model_server = WADASModelServer(WADAS_SERVER_URL)
        self.initialize_dialog()


    def update_request_fields(self):
        """Method to update access request UI related widgets"""
        if os.path.isfile(MODEL_REQUEST_CFG):
            self.ui.label_request_title.setText("Check submitted request:")
            self.ui.pushButton_request.setText("Check request")

    def initialize_dialog(self):
        """Method to initialize dialog"""

        credentials= keyring.get_credential(f"WADAS_Ai_model_request", "")

        if credentials:
            self.ui.lineEdit_email.setText(credentials.username)
            self.ui.lineEdit_token.setText(credentials.password)
        self.update_request_fields()

    def handle_request(self):
        """Method to handle new or submitted request"""

        if (access_request_dialog := AccessRequestDialog()).exec():
            self.update_request_fields()

    def validate(self):
        """Method to validate input fields"""

        valid = True
        message = ""

        if not self.ui.lineEdit_token.text():
            valid = False
            message = "Token field cannot be empty!"
        if not self.ui.lineEdit_email.text():
            valid = False
            message = "Email field cannot be empty!"

        self.ui.label_error.setText(message)
        self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(valid)

    def accept_and_close(self):
        """Method to trigger login phase and move to models selection"""

        if not (credentials := keyring.get_credential(f"WADAS_Ai_model_request", "")) or (
                new_credential := (credentials.username != self.ui.lineEdit_email.text())):
            keyring.set_password(
                f"WADAS_Ai_model_request",
                self.ui.lineEdit_email.text(),
                self.ui.lineEdit_token.text(),
            )

        if not os.path.isfile(MODEL_NODE_CFG) or new_credential:
            try:
                node_id, org_id = self.wadas_model_server.register_node(username=self.ui.lineEdit_email.text().strip(),
                                                                        password=self.ui.lineEdit_token.text())
                # Store user id locally
                data = {
                    "node_id": node_id,
                    "org_id": org_id
                }
                with open(MODEL_NODE_CFG, "w") as json_file:
                    json.dump(data, json_file, indent=4)
            except Exception as e:
                WADASErrorMessage("User registration error", str(e)).exec()
                return
        else:
            with open(MODEL_NODE_CFG) as json_file:
                data = json.load(json_file)
            node_id = data.get("node_id")
        self.accept()
        download_dialog = AiModelDownloadDialog(node_id)
        download_dialog.exec()