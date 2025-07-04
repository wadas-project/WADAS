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

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QTextEdit

from wadas.domain.ai_model_downloader import WADAS_SERVER_URL
from wadas.ui.error_message_dialog import WADASErrorMessage
from wadas.ui.qt.ui_access_request import Ui_DialogModelAccessRequest

module_dir_path = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = Path(module_dir_path).parent.parent / "model"
MODEL_REQUEST_CFG = MODELS_DIR / "request"
# Example of MODEL_REQUEST_CFG format:
#{
#  "name": "Mario Rossi",
#  "email": "mario.rossi@example.com",
#  "num_of_nodes": 3,
#  "rationale": "some rationale",
#  "request_id": 101
#}
TERMS_URL = f"{WADAS_SERVER_URL}api/v1/terms/download"
TERMS_PATH = MODELS_DIR / "TERMS_AND_CONDITIONS"

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
        with open(MODEL_REQUEST_CFG, 'w') as f:
            json.dump(data, f, indent=4)

class TermsAndConditionsDialog(QDialog):
    """Class to represent TERMS_AND_CONDITIONS_OF_USE file in a QDialog"""
    def __init__(self, terms_accepted=False):
        super().__init__()
        # Acceptance status
        self.terms_accepted = terms_accepted
        # Don't show again Terms and Conditions (if accepted)
        self.dont_show = False

        # UI
        self.setWindowTitle("WADAS Terms and Conditions of use")
        self.setGeometry(150, 150, 500, 400)
        self.setWindowIcon(QIcon(os.path.join(module_dir_path, "..", "img", "mainwindow_icon.jpg")))

        layout = QVBoxLayout()

        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)
        self.text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        layout.addWidget(self.text_edit)

        # Load Terms and Conditions file
        with open(TERMS_PATH, encoding="utf-8") as terms_n_conditions_file:
            license_text = terms_n_conditions_file.read()
            self.text_edit.setPlainText(license_text)

        self.setLayout(layout)

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

        # Slots
        self.ui.buttonBox.accepted.connect(self.accept_and_close)
        self.ui.lineEdit_email.textChanged.connect(self.validate)
        self.ui.lineEdit_name_surname.textChanged.connect(self.validate)
        self.ui.plainTextEdit_rationale.textChanged.connect(self.validate)
        self.ui.pushButton_check_request.clicked.connect(self.get_request_status)
        self.ui.pushButton_clear_request.clicked.connect(self.on_clear_request_triggered)
        self.ui.pushButton_terms_of_use.clicked.connect(self.show_terms_of_use)
        self.ui.checkBox_gdpr.clicked.connect(self.validate)
        self.ui.checkBox_terms_of_use.clicked.connect(self.validate)

        self.request = None
        self.initialize_dialog()

    def get_request_from_local(self):
        """Method to retrieve the request id from file, if any"""

        try:
            with open(MODEL_REQUEST_CFG, 'r') as json_file:
                data = json.load(json_file)
                self.request = Request(
                    data.get('name'),
                    data.get('organization'),
                    data.get('email'),
                    data.get('num_of_nodes'),
                    data.get('rationale'),
                    data.get('request_id')
                )
        except (FileNotFoundError, json.JSONDecodeError, TypeError):
            self.request = None

    def get_request_status(self):
        """Get request status from server"""

        status_url = f'{WADAS_SERVER_URL}api/v1/access_requests/{self.request.id}/status'

        # Common headers
        headers = {
            'Content-Type': 'application/json'
        }

        try:
            status_response = requests.get(status_url, headers=headers, timeout=10)
            status_response.raise_for_status()
            status = status_response.json().get('status')

            self.ui.label_request_status.setText(status)

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

        self.get_request_from_local()
        if self.request:
            self.ui.checkBox_terms_of_use.setChecked(True)
            self.ui.checkBox_gdpr.setChecked(True)
            self.enable_editing(False)
        else:
            self.ui.pushButton_clear_request.setVisible(False)

        self.update_request_fields()

    def enable_editing(self, editing):
        """Method to prevent modification from dialog when request is approved"""

        self.ui.lineEdit_email.setEnabled(editing)
        self.ui.lineEdit_node_num.setEnabled(editing)
        self.ui.lineEdit_name_surname.setEnabled(editing)
        self.ui.plainTextEdit_rationale.setEnabled(editing)
        self.ui.lineEdit_organization.setEnabled(editing)
        self.ui.checkBox_terms_of_use.setEnabled(editing)
        self.ui.checkBox_gdpr.setEnabled(editing)

    def update_request_fields(self):
        """Method to show new request input fields in dialog"""

        # Request
        submitted_request = True if self.request else False

        self.ui.label_request_status.setVisible(submitted_request)
        self.ui.label_status_title.setVisible(submitted_request)
        self.ui.pushButton_check_request.setVisible(submitted_request)
        if submitted_request:
            self.get_request_status()

            self.ui.lineEdit_email.setText(self.request.email)
            self.ui.lineEdit_organization.setText(self.request.organization)
            self.ui.lineEdit_node_num.setText(str(self.request.nodes_num))
            self.ui.lineEdit_name_surname.setText(self.request.name)
            self.ui.plainTextEdit_rationale.setPlainText(self.request.rationale)
        else:
            self.ui.label_request_status.setText("")
            self.ui.lineEdit_node_num.setText("1")

    def on_clear_request_triggered(self):
        """Method to clear local history of previously submitted model request"""

        if os.path.isfile(MODEL_REQUEST_CFG):
            os.remove(MODEL_REQUEST_CFG)

            # Clear dialog input fields
            self.ui.lineEdit_email.setText("")
            self.ui.lineEdit_node_num.setText("1")
            self.ui.lineEdit_organization.setText("")
            self.ui.lineEdit_name_surname.setText("")
            self.ui.plainTextEdit_rationale.setPlainText("")
            self.ui.label_request_status.setText("")
            self.ui.label_request_status.setVisible(False)
            self.ui.label_status_title.setVisible(False)
            self.ui.pushButton_check_request.setVisible(False)
            self.enable_editing(True)

    def validate(self):
        """Method to validate input fields"""

        valid = True
        message = ""

        if not self.ui.lineEdit_email.text():
            valid = False
            message = "Email field cannot be empty!"
        if not self.ui.lineEdit_name_surname.text():
            valid = False
            message = "Name and Surname field cannot be empty!"
        if not self.ui.plainTextEdit_rationale.toPlainText().strip():
            valid = False
            message = "Rationale field cannot be empty!"
        if not self.ui.checkBox_terms_of_use.isChecked():
            valid = False
            message = "You must accept WADAS Ai models Terms of Use!"
        if not self.ui.checkBox_gdpr.isChecked():
            valid = False
            message = "You must check privacy disclaimer!"

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
            submit_response = requests.post(submit_url, json=payload, headers=headers, timeout=10)
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

    def show_terms_of_use(self):
        """Method to show WADAS Ai models terms of use"""

        try:
            response = requests.get(TERMS_URL, stream=True, timeout=10)

            if response.status_code == 200:
                with open(TERMS_PATH, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            elif response.status_code == 401:
                WADASErrorMessage("Error while downloading terms and conditions",
                                  "Unauthorized access (401).").exec()
            else:
                WADASErrorMessage("Download error", f"Code: {response.status_code}").exec()
        except requests.exceptions.RequestException as e:
            WADASErrorMessage("Error while downloading terms and conditions", str(e)).exec()
            return

        TermsAndConditionsDialog().exec()

    def accept_and_close(self):
        """When Ok is clicked, perform changes"""

        if not self.request:
            self.request = Request(
                                   self.ui.lineEdit_name_surname.text(),
                                   self.ui.lineEdit_organization.text(),
                                   self.ui.lineEdit_email.text(),
                                   self.ui.lineEdit_node_num.text(),
                                   self.ui.plainTextEdit_rationale.toPlainText()
            )
            self.request.id = self.issue_new_request_to_server()

            if self.request.id != 0:
                self.request.to_json()
                self.accept()
            else:
                WADASErrorMessage("Unable to complete the request",
                                  f"Invalid request id returned from the server.").exec()
        else:
            self.accept()