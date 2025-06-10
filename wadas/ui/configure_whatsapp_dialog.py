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
# Date: 2024-12-16
# Description: Whatsapp configuration dialog module.


import os
import requests

import keyring
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QDialogButtonBox

from wadas.domain.notifier import Notifier
from wadas.domain.whatsapp_notifier import WhatsAppNotifier
from wadas.ui.qt.ui_configure_whatsapp import Ui_DialogConfigureWhatsApp

module_dir_path = os.path.dirname(os.path.abspath(__file__))


class DialogConfigureWhatsApp(QDialog, Ui_DialogConfigureWhatsApp):
    """Class to insert WhatsApp configuration data to enable WADAS for WhatsApp notifications."""

    def __init__(self):
        super(DialogConfigureWhatsApp, self).__init__()
        self.ui = Ui_DialogConfigureWhatsApp()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon(os.path.join(module_dir_path, "..", "img", "mainwindow_icon.jpg")))
        self.ui.pushButton_testMessage.setEnabled(False)
        self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        self.ui.label_errorMessage.setStyleSheet("color: red")

        self.whatsapp_notifier = Notifier.notifiers[Notifier.NotifierTypes.WHATSAPP.value]

        # Slots
        self.ui.buttonBox.accepted.connect(self.accept_and_close)
        self.ui.lineEdit_phoneID.textChanged.connect(self.validate)
        self.ui.lineEdit_accessToken.textChanged.connect(self.validate)
        self.ui.textEdit_recipientsNumbers.textChanged.connect(self.validate)
        self.ui.pushButton_testMessage.clicked.connect(self.send_whatsapp_message)

        self.initialize_form()

    def initialize_form(self):
        """Method to initialize form with existing WhatsApp configuration data (if any)."""

        if Notifier.notifiers[Notifier.NotifierTypes.WHATSAPP.value]:
            self.ui.checkBox_enableWhatsAppNotifications.setChecked(self.whatsapp_notifier.enabled)
            self.ui.lineEdit_phoneID.setText(self.whatsapp_notifier.sender_id)
            credentials = keyring.get_credential("WADAS_WhatsApp", self.whatsapp_notifier.sender_id)
            if credentials and credentials.username == self.whatsapp_notifier.sender_id:
                self.ui.lineEdit_accessToken.setText(credentials.password)
            if recipients_numbers := self.whatsapp_notifier.recipient_numbers:
                recipients = ", ".join(recipients_numbers)
                self.ui.textEdit_recipientsNumbers.setText(recipients)
            self.ui.checkBox_allowImg.setChecked(self.whatsapp_notifier.allow_images)
        else:
            self.ui.checkBox_enableWhatsAppNotifications.setEnabled(True)

    def validate(self):
        """Method to validate form data."""

        if (self.ui.lineEdit_accessToken.text() and self.ui.lineEdit_phoneID.text().isdigit() and
                self.ui.textEdit_recipientsNumbers.toPlainText().strip()):
            self.ui.label_errorMessage.setText("")
            self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
            self.ui.pushButton_testMessage.setEnabled(True)
        else:
            if not self.ui.lineEdit_phoneID.text():
                self.ui.label_errorMessage.setText("Phone ID cannot be empty.")
            elif not self.ui.lineEdit_phoneID.text().isdigit():
                self.ui.label_errorMessage.setText("Phone ID must contain digits only.")
            elif not self.ui.lineEdit_accessToken.text():
                self.ui.label_errorMessage.setText("Access token cannot be empty.")
            elif not self.ui.textEdit_recipientsNumbers.toPlainText():
                self.ui.label_errorMessage.setText("Recipients number list cannot be empty.")
            self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
            self.ui.pushButton_testMessage.setEnabled(False)

    def add_whatsapp_credentials(self, username, token):
        """Method to add WhatsApp credentials to system keyring."""

        # If credentials exist remove them (workaround keyring bug)
        credentials = keyring.get_credential(
            "WADAS_WhatsApp", ""
        )
        if credentials:
            try:
                keyring.delete_password("WADAS_WhatsApp", credentials.username)
            except keyring.errors.PasswordDeleteError:
                # Credentials not in the system
                pass

        # Set new/modified credentials for camera
        keyring.set_password(
            "WADAS_WhatsApp",
            username,
            token,
        )

    def accept_and_close(self):
        """When Ok is clicked, save email config info before closing."""

        recipients = self.ui.textEdit_recipientsNumbers.toPlainText().strip().split(", ")

        if not Notifier.notifiers[Notifier.NotifierTypes.WHATSAPP.value]:
            Notifier.notifiers[Notifier.NotifierTypes.WHATSAPP.value] = WhatsAppNotifier(
                self.ui.lineEdit_phoneID.text(),
                recipients,
                self.ui.checkBox_enableWhatsAppNotifications.isChecked(),
                self.ui.checkBox_allowImg.isChecked()
            )
            self.add_whatsapp_credentials(self.ui.lineEdit_phoneID.text(), self.ui.lineEdit_accessToken.text())
        else:
            self.whatsapp_notifier.enabled = self.ui.checkBox_enableWhatsAppNotifications.isChecked()
            self.whatsapp_notifier.sender_id = self.ui.lineEdit_phoneID.text()
            self.whatsapp_notifier.recipient_numbers = []
            self.whatsapp_notifier.recipient_numbers = recipients
            self.add_whatsapp_credentials(self.ui.lineEdit_phoneID.text(), self.ui.lineEdit_accessToken.text())
            self.whatsapp_notifier.allow_images = self.ui.checkBox_allowImg.isChecked()

            Notifier.notifiers[Notifier.NotifierTypes.WHATSAPP.value] = self.whatsapp_notifier
        self.accept()

    def send_whatsapp_message(self):
        """Method to send WhatsApp message notification."""

        message = "WADAS Test Message!"
        url = f"https://graph.facebook.com/v17.0/{self.ui.lineEdit_phoneID.text()}/messages"
        access_token = self.ui.lineEdit_accessToken.text()
        recipients = self.ui.textEdit_recipientsNumbers.toPlainText().strip().split(", ")

        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

        for recipient_phone_number in recipients:
            data = {
                "messaging_product": "whatsapp",
                "to": recipient_phone_number,
                "type": "text",
                "text": {"body": message},
            }

            response = requests.post(url, headers=headers, json=data)

            if response.status_code == 200:
                self.ui.plainTextEdit_testMessageLog.setPlainText("WhatsApp notification sent!")
            else:
                self.ui.plainTextEdit_testMessageLog.setPlainText(f"Error: {response.status_code}, {response.text}")