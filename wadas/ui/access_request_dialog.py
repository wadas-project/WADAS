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
import json

import keyring
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QDialogButtonBox

from wadas.ui.qt.ui_access_request import Ui_DialogModelAccessRequest

module_dir_path = os.path.dirname(os.path.abspath(__file__))
model_request_id_path = Path(module_dir_path).parent.parent / "model" / "request"
#{
#  "name": "Mario Rossi",
#  "email": "mario.rossi@example.com",
#  "num_of_nodes": 3,
#  "rationale": "some rationale",
#  "request_id": 101
#}

class Request():
    """Class to model Ai model access request."""
    def __init__(self, id, name, organization, email, nodes_num, rationale):
        self.id = id
        self.name = name
        self.organization = organization
        self.email = email
        self.nodes_num = nodes_num
        self.rationale = rationale

    def to_json(self):
        data = {
            "name": self.name,
            "email": self.email,
            "num_of_nodes": self.nodes_num,
            "rationale": self.rationale,
            "request_id": self.id
        }
        with open(model_request_id_path, 'w') as f:
            json.dump(data, f, indent=4)

class AccessRequestDialog(QDialog, Ui_DialogModelAccessRequest):
    """Class to instantiate UI dialog to configure Ai model parameters."""

    def __init__(self):
        super(AccessRequestDialog, self).__init__()
        self.ui = Ui_DialogModelAccessRequest()

        # UI
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon((Path(module_dir_path).parent / "img" / "mainwindow_icon.jpg").resolve().as_posix()))
        self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        self.ui.label_error.setStyleSheet("color: red")
        self.ui.groupBox_new_request.setVisible(False)

        # Slots
        self.ui.buttonBox.accepted.connect(self.accept_and_close)
        self.ui.checkBox_new_request.clicked.connect(self.on_new_request_toggled)
        self.ui.lineEdit_email.textChanged.connect(self.validate)
        self.ui.lineEdit_token.textChanged.connect(self.validate)
        self.ui.lineEdit_name_surname.textChanged.connect(self.validate)
        self.ui.pushButton_check_request.clicked.connect(self.get_request_status)

        self.request = None
        self.initialize_dialog()

    def get_request(self):
        """Method to retrieve the request id from file, if any"""

        try:
            with open(model_request_id_path, 'r') as file:
                data = json.load(file)
                self.request = Request(
                    data.get('request_id'),
                    data.get('name'),
                    data.get('email'),
                    data.get('num_of_nodes'),
                    data.get('rationale'),
                    data.get('organization')
                )
        except (FileNotFoundError, json.JSONDecodeError, TypeError):
            self.request = None

    def get_credentials(self):
        """Method to retrieve credentials from keyring, if any"""
        return keyring.get_credential(f"WADAS_Ai_model_request", "")

    def get_request_status(self):
        """Get request status from server"""
        # TODO: query server for request status
        self.ui.label_request_status.setText("Pending")

    def initialize_dialog(self):
        """Method to initialize dialog"""

        # Credentials
        if credentials:= self.get_credentials():
            self.ui.lineEdit_email.setText(credentials.username)
            self.ui.lineEdit_token.setText(credentials.password)
        self.get_request()
        if self.request:
            self.ui.checkBox_new_request.setChecked(True)
        self.on_new_request_toggled()

    def on_new_request_toggled(self):
        """Method to show new request input fields in dialog"""

        # Request
        new_request = True if self.request else False

        self.ui.label_request_status.setVisible(new_request)
        self.ui.label_status_title.setVisible(new_request)
        self.ui.pushButton_check_request.setVisible(new_request)
        if new_request:
            self.get_request_status()

            self.ui.lineEdit_organization.setText(self.request.organization)
            self.ui.lineEdit_node_num.setText(self.request.nodes_num)
            self.ui.lineEdit_name_surname.setText(self.request.name)
            self.ui.plainTextEdit_rationale.setPlainText(self.request.rationale)
        else:
            self.ui.label_request_status.setText("")
            self.ui.lineEdit_node_num.setText("1")

        self.ui.groupBox_new_request.setVisible(self.ui.checkBox_new_request.isChecked())
        self.adjustSize()

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
        if self.ui.checkBox_new_request.isChecked() and not self.ui.lineEdit_name_surname.text():
            valid = False
            message = "Name and Surname field cannot be empty!"
        if self.ui.checkBox_new_request.isChecked() and not self.ui.plainTextEdit_rationale.toPlainText():
            valid = False
            message = "Rationale field cannot be empty!"

        self.ui.label_error.setText(message)
        self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(valid)

    def accept_and_close(self):
        """When Ok is clicked, perform changes"""

        #TODO: send data to server and obtain request id

        # Store credentials in keyring
        keyring.set_password(
            f"WADAS_Ai_model_request",
            self.ui.lineEdit_email.text(),
            self.ui.lineEdit_token.text(),
        )

        self.request = Request("1", #TODO: replace with server provided id
                               self.ui.lineEdit_name_surname.text(),
                               self.ui.lineEdit_organization.text(),
                               self.ui.lineEdit_email.text(),
                               self.ui.lineEdit_node_num.text(),
                               self.ui.plainTextEdit_rationale.toPlainText())
        self.request.to_json()
        self.accept()