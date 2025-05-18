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

import os
from pathlib import Path
import requests

import keyring
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QDialogButtonBox

from wadas.ui.access_request_dialog import AccessRequestDialog
from wadas.ui.ai_model_download_dialog import AiModelDownloadDialog
from wadas.ui.error_message_dialog import WADASErrorMessage
from wadas.ui.qt.ui_model_request_login import Ui_DialogModelRequestLogin

module_dir_path = os.path.dirname(os.path.abspath(__file__))
model_request_id_path = Path(module_dir_path).parent.parent / "model" / "request"
WADAS_SERVER_URL = "https://localhost:8443/"

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

        self.initialize_dialog()


    def update_request_fields(self):
        """Method to update access request UI related widgets"""
        if os.path.isfile(model_request_id_path):
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

        if not (keyring.get_credential(f"WADAS_Ai_model_request", "")):
            keyring.set_password(
                f"WADAS_Ai_model_request",
                self.ui.lineEdit_email.text(),
                self.ui.lineEdit_token.text(),
            )

        url = f"{WADAS_SERVER_URL}api/v1/organizations_login"
        payload = {
            "username": self.ui.lineEdit_email.text().strip(),
            "password": self.ui.lineEdit_token.text()
        }

        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 401:
                WADASErrorMessage("Login failed", "Invalid credentials!").exec()
                return
            else:
                response.raise_for_status()

                # Parsing JSON response
                response_data = response.json()
                org_code = response_data.get("org_code")

                if org_code:
                    with open("org_code", "w", encoding="utf-8") as f:
                        f.write(org_code)
                else:
                    WADASErrorMessage("Error in receiving organization code.",
                                      "Organization code not found in server response.").exec()
                    return

        except requests.exceptions.HTTPError as http_err:
            WADASErrorMessage("HTTP error occurred", str(http_err))
        except requests.exceptions.RequestException as req_err:
            WADASErrorMessage("Request error occurred", str(req_err))
        except ValueError as json_err:
            WADASErrorMessage("Failed to parse JSON", str(json_err))
        except Exception as e:
            WADASErrorMessage("Unexpected error", str(e))

        self.accept()
        download_dialog = AiModelDownloadDialog()
        download_dialog.exec()