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

import keyring
import validators
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QMessageBox

from wadas.domain.ai_model_downloader import WADAS_SERVER_URL
from wadas.ui.access_request_dialog import AccessRequestDialog
from wadas.ui.ai_model_download_dialog import AiModelDownloadDialog
from wadas.ui.error_message_dialog import WADASErrorMessage
from wadas.ui.qt.ui_model_request_login import Ui_DialogModelRequestLogin
from wadas_runtime import WADASModelServer

module_dir_path = os.path.dirname(os.path.abspath(__file__))
MODELS_FOLDER = Path(module_dir_path).parent.parent / "model"
MODEL_REQUEST_CFG = MODELS_FOLDER / "request"


class DialogModelRequestLogin(QDialog, Ui_DialogModelRequestLogin):
    """Class to instantiate UI dialog to configure Ai model parameters."""

    def __init__(self, models_found=True):
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
        self.ui.label_no_models.setVisible(not models_found)
        self.update_credentials()
        self.update_request_fields()
        self.adjustSize()

    def update_request_fields(self):
        """Method to update access request UI related widgets"""
        if os.path.isfile(MODEL_REQUEST_CFG):
            self.ui.label_request_title.setText("Check submitted request:")
            self.ui.pushButton_request.setText("Check request")

    def update_credentials(self):
        """Method to populate credentials fields."""

        credentials= keyring.get_credential(f"WADAS_Ai_model_request", "")
        if credentials:
            self.ui.lineEdit_email.setText(credentials.username)
            self.ui.lineEdit_token.setText(credentials.password)

    def handle_request(self):
        """Method to handle new or submitted request"""

        if AccessRequestDialog().exec():
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
        if not validators.email(self.ui.lineEdit_email.text()):
            valid = False
            message = "Provided email is not a valid email format!"
        self.ui.label_error.setText(message)
        self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(valid)

    def show_confirmation_dialog(self):
        """Method to show confirmation dialog to user"""

        msg_box = QMessageBox()
        msg_box.setWindowTitle("Overwrite current settings?")
        msg_box.setText("By proceeding with modification credentials will be overwritten.\n"
                        "Are you sure you want to continue?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)

        return msg_box.exec()

    def accept_and_close(self):
        """Method to trigger login phase and move to models selection"""
        credentials = keyring.get_credential(f"WADAS_Ai_model_request", "")
        new_credential = credentials.username != self.ui.lineEdit_email.text()

        # Ask user if is ok to proceed as old credentials, node and organization id will be overwritten
        if new_credential and self.show_confirmation_dialog() == QMessageBox.No:
            return

        # Save credentials
        if not credentials or new_credential:
            keyring.set_password(
                f"WADAS_Ai_model_request",
                self.ui.lineEdit_email.text(),
                self.ui.lineEdit_token.text(),
            )

        org_code_key = keyring.get_credential("WADAS_org_code", "")
        if not org_code_key or not org_code_key.password or new_credential:
            try:
                org_code = self.wadas_model_server.login(username=self.ui.lineEdit_email.text().strip(),
                                                         password=self.ui.lineEdit_token.text())
            except Exception as e:
                WADASErrorMessage("User login error", str(e)).exec()
                return

            keyring.set_password(
                f"WADAS_org_code",
                self.ui.lineEdit_email.text().strip(),
                org_code,
            )
        else:
            org_code = org_code_key.password

        # Get node ID
        try:
            node_id  = str(self.wadas_model_server.register_node(org_code=org_code))
        except Exception as e:
            WADASErrorMessage("User registration error", str(e)).exec()
            return

        self.accept()
        download_dialog = AiModelDownloadDialog(node_id)
        download_dialog.exec()