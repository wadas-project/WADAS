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
from requests.exceptions import RequestException, ConnectionError, Timeout, HTTPError
import json

import keyring
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QDialogButtonBox

from wadas.ui.error_message_dialog import WADASErrorMessage
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
WADAS_SERVER_URL = "https://localhost:8443/"

class Request():
    """Class to model Ai model access request."""
    def __init__(self, name, organization, email, nodes_num, rationale, id=0):
        self.name = name
        self.organization = organization
        self.email = email
        self.nodes_num = nodes_num
        self.rationale = rationale
        self.id = id

    def to_json(self):
        data = {
            "name": self.name,
            "email": self.email,
            "num_of_nodes": self.nodes_num,
            "organization": self.organization,
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
        self.ui.plainTextEdit_rationale.textChanged.connect(self.validate)
        self.ui.pushButton_check_request.clicked.connect(self.get_request_status)
        self.ui.pushButton_clear_request.clicked.connect(self.on_clear_request_triggered)

        self.request = None
        self.initialize_dialog()

    def get_request_from_local(self):
        """Method to retrieve the request id from file, if any"""

        try:
            with open(model_request_id_path, 'r') as json_file:
                data = json.load(json_file)
                self.request = Request(
                    data.get('name'),
                    data.get('email'),
                    data.get('num_of_nodes'),
                    data.get('rationale'),
                    data.get('organization'),
                    data.get('request_id')
                )
        except (FileNotFoundError, json.JSONDecodeError, TypeError):
            self.request = None

    def get_credentials(self):
        """Method to retrieve credentials from keyring, if any"""
        return keyring.get_credential(f"WADAS_Ai_model_request", "")

    def get_request_status(self):
        """Get request status from server"""

        status_url = f'{WADAS_SERVER_URL}api/v1/access_requests/{self.request.id}/status'

        # Common headers
        headers = {
            'Content-Type': 'application/json'
        }

        try:
            status_response = requests.get(status_url, headers=headers, timeout=10, verify=False)
            status_response.raise_for_status()
            status = status_response.json().get('status')

            self.ui.label_request_status.setText(status)

            if status != "pending":
                self.on_processed_request()
        except (ConnectionError, Timeout) as conn_err:
            WADASErrorMessage("Network error",
                              f"Network error while checking request status: {conn_err}").exec()
        except HTTPError as http_err:
            WADASErrorMessage("Network error",
                              f"HTTP error while checking request status: {http_err}").exec()
        except RequestException as req_err:
            WADASErrorMessage("Network error",
                              f"Unexpected error while checking request status: {req_err}").exec()

    def initialize_dialog(self):
        """Method to initialize dialog"""

        # Credentials
        if credentials:= self.get_credentials():
            self.ui.lineEdit_email.setText(credentials.username)
            self.ui.lineEdit_token.setText(credentials.password)
        self.get_request_from_local()
        if self.request:
            self.ui.checkBox_new_request.setChecked(True)
            self.ui.pushButton_clear_request.setVisible(True)
            self.ui.pushButton_clear_request.setEnabled(True)
        else:
            self.ui.pushButton_clear_request.setVisible(False)

        self.on_new_request_toggled()

    def on_processed_request(self):
        """Method to prevent modification from dialog when request is approved"""

        self.ui.lineEdit_node_num.setEnabled(False)
        self.ui.lineEdit_name_surname.setEnabled(False)
        self.ui.plainTextEdit_rationale.setEnabled(False)
        self.ui.lineEdit_organization.setEnabled(False)

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
            self.ui.lineEdit_node_num.setText(str(self.request.nodes_num))
            self.ui.lineEdit_name_surname.setText(self.request.name)
            self.ui.plainTextEdit_rationale.setPlainText(self.request.rationale)
        else:
            self.ui.label_request_status.setText("")
            self.ui.lineEdit_node_num.setText("1")

        self.ui.groupBox_new_request.setVisible(self.ui.checkBox_new_request.isChecked())
        self.adjustSize()

    def on_clear_request_triggered(self):
        """Method to clear local history of previously submitted model request"""

        if os.path.isfile(model_request_id_path):
            os.remove(model_request_id_path)
            self.ui.pushButton_clear_request.setVisible(False)
            # Clear dialog input fields
            self.ui.lineEdit_token.setText("")
            self.ui.lineEdit_email.setText("")
            self.ui.lineEdit_node_num.setText("1")
            self.ui.lineEdit_organization.setText("")
            self.ui.lineEdit_name_surname.setText("")
            self.ui.plainTextEdit_rationale.setPlainText("")
            self.ui.label_request_status.setText("")
            self.ui.label_request_status.setVisible(False)
            self.ui.label_status_title.setVisible(False)
            self.ui.pushButton_check_request.setVisible(False)

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
        if self.ui.checkBox_new_request.isChecked() and not self.ui.plainTextEdit_rationale.toPlainText().strip():
            valid = False
            message = "Rationale field cannot be empty!"

        self.ui.label_error.setText(message)
        self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(valid)

    def issue_new_request_to_server(self):
        """Method to submit a new request to WADAS server via https"""

        headers = {
            'Content-Type': 'application/json'
        }

        submit_url = f'{WADAS_SERVER_URL}api/v1/access_requests'
        payload = {
            "name": self.request.name,
            "email": self.request.email,
            "org_name": self.request.organization,
            "text": self.request.rationale
        }

        try:
            submit_response = requests.post(submit_url, json=payload, headers=headers, timeout=10, verify=False)
            submit_response.raise_for_status()  # Raises HTTPError for bad responses

            response_data = submit_response.json()

            if not isinstance(response_data, dict) or "request_id" not in response_data:
                raise ValueError("Invalid response format: 'request_id' not found.")

            request_id = response_data["request_id"]

            if not isinstance(request_id, int):
                raise ValueError(f"Invalid 'request_id' type: expected int, got {type(request_id).__name__}")

            return request_id

        except (ConnectionError, Timeout) as conn_err:
            WADASErrorMessage("Network error",
                              f"Network error while submitting the request: {conn_err}").exec()
        except HTTPError as http_err:
            WADASErrorMessage("Network error",
                              f"HTTP error while submitting the request: {http_err}").exec()
        except ValueError as val_err:
            WADASErrorMessage("Response error",
                              f"Invalid server response: {val_err}").exec()
        except RequestException as req_err:
            WADASErrorMessage("Network error",
                              f"Unexpected error while submitting the request: {req_err}").exec()

    def accept_and_close(self):
        """When Ok is clicked, perform changes"""

        self.request = Request(
                               self.ui.lineEdit_name_surname.text(),
                               self.ui.lineEdit_organization.text(),
                               self.ui.lineEdit_email.text(),
                               self.ui.lineEdit_node_num.text(),
                               self.ui.plainTextEdit_rationale.toPlainText()
        )
        self.request.id = self.issue_new_request_to_server()

        if self.request.id != 0:
            # Store credentials in keyring
            keyring.set_password(
                f"WADAS_Ai_model_request",
                self.ui.lineEdit_email.text(),
                self.ui.lineEdit_token.text(),
            )

            self.request.to_json()
            self.accept()
        else:
            WADASErrorMessage("Unable to complete the request",
                              f"Invalid request id returned from the server.").exec()