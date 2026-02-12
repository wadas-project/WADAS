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
# Description: Email UI configuration module.


import os
import smtplib
import ssl
from email.mime.text import MIMEText

import keyring
import validators
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QDialogButtonBox

from wadas.domain.email_notifier import EmailNotifier
from wadas.domain.notifier import Notifier
from wadas.ui.qt.ui_configure_email import Ui_DialogConfigureEmail

module_dir_path = os.path.dirname(os.path.abspath(__file__))


class DialogInsertEmail(QDialog, Ui_DialogConfigureEmail):
    """Class to insert email configuration to enable WADAS for email notifications."""

    def __init__(self):
        super(DialogInsertEmail, self).__init__()
        self.ui = Ui_DialogConfigureEmail()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon(os.path.join(module_dir_path, "..", "img", "mainwindow_icon.jpg")))

        self.email_notifier = Notifier.notifiers[Notifier.NotifierTypes.EMAIL.value]
        self.valid_sender_email = False
        self.valid_smtp = False
        self.valid_port = False
        self.valid_password = False
        self.valid_receiver_emails = False
        self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        self.ui.pushButton_testEmail.setEnabled(False)
        self.ui.label_status.setStyleSheet("color: red")

        # Slots
        self.ui.buttonBox.accepted.connect(self.accept_and_close)
        self.ui.lineEdit_senderEmail.textChanged.connect(self.validate_email_configuration)
        self.ui.lineEdit_smtpServer.textChanged.connect(self.validate_email_configuration)
        self.ui.lineEdit_port.textChanged.connect(self.validate_email_configuration)
        self.ui.lineEdit_password.textChanged.connect(self.validate_email_configuration)
        self.ui.textEdit_recipient_email.textChanged.connect(self.validate_email_configuration)
        self.ui.pushButton_testEmail.clicked.connect(self.validate_email_configuration)
        self.ui.lineEdit_username.textChanged.connect(self.validate_email_configuration)
        self.ui.checkBox_username.clicked.connect(self.on_checBox_username_status_changed)

        self.initialize_form()

    def initialize_form(self):
        """Method to initialize form with existing email configuration data (if any)."""

        if Notifier.notifiers[Notifier.NotifierTypes.EMAIL.value]:
            self.ui.checkBox_email_en.setChecked(self.email_notifier.enabled)
            self.ui.lineEdit_senderEmail.setText(self.email_notifier.sender_email)
            self.ui.lineEdit_smtpServer.setText(self.email_notifier.smtp_hostname)
            self.ui.lineEdit_port.setText(self.email_notifier.smtp_port)
            custom_username = bool(self.email_notifier.sender_email != self.email_notifier.username)
            self.ui.checkBox_username.setChecked(custom_username)
            if custom_username:
                self.ui.lineEdit_username.setText(self.email_notifier.username)
            credentials = keyring.get_credential("WADAS_email", self.email_notifier.sender_email)
            if credentials and credentials.username == self.email_notifier.sender_email:
                self.ui.lineEdit_senderEmail.setText(credentials.username)
                self.ui.lineEdit_password.setText(credentials.password)
            if recipients_email := self.email_notifier.recipients_email:
                recipients = ", ".join(recipients_email)
                self.ui.textEdit_recipient_email.setText(recipients)
            self.validate_password()
            self.validate_email_configuration()
        else:
            self.ui.checkBox_email_en.setChecked(True)
            self.ui.checkBox_username.setChecked(False)
            self.ui.lineEdit_username.setEnabled(False)

    def on_checBox_username_status_changed(self):
        """Method to handle username line edit enablement basing on checkbox status"""

        self.ui.lineEdit_username.setEnabled(self.ui.checkBox_username.isChecked())
        self.ui.lineEdit_username.setText("")
        self.validate_email_configuration()

    def accept_and_close(self):
        """When Ok is clicked, save email config info before closing."""
        recipients = []
        for recipient in self.ui.textEdit_recipient_email.toPlainText().strip().split(", "):
            recipients.append(recipient)

        if not Notifier.notifiers[Notifier.NotifierTypes.EMAIL.value]:
            Notifier.notifiers[Notifier.NotifierTypes.EMAIL.value] = EmailNotifier(
                self.ui.lineEdit_senderEmail.text(),
                self.ui.lineEdit_smtpServer.text(),
                self.ui.lineEdit_port.text(),
                recipients,
                self.ui.checkBox_email_en.isChecked(),
            )
            self.add_email_credentials(self.ui.lineEdit_senderEmail.text(), self.ui.lineEdit_password.text())
        else:
            self.email_notifier.enabled = self.ui.checkBox_email_en.isChecked()
            self.email_notifier.sender_email = self.ui.lineEdit_senderEmail.text()
            self.email_notifier.smtp_hostname = self.ui.lineEdit_smtpServer.text()
            self.email_notifier.smtp_port = self.ui.lineEdit_port.text()
            self.email_notifier.recipients_email = []
            self.email_notifier.recipients_email = recipients
            self.add_email_credentials(self.ui.lineEdit_senderEmail.text(), self.ui.lineEdit_password.text())

            Notifier.notifiers[Notifier.NotifierTypes.EMAIL.value] = self.email_notifier
        self.accept()

    def add_email_credentials(self, username, password):
        """Method to add email credentials to system keyring."""

        # If credentials exist remove them (workaround keyring bug)
        credentials = keyring.get_credential(
            f"WADAS_email", ""
        )
        if credentials:
            try:
                keyring.delete_password(f"WADAS_email", credentials.username)
            except keyring.errors.PasswordDeleteError:
                # Credentials not in the system
                pass

        # Set new/modified credentials for camera
        keyring.set_password(
            "WADAS_email",
            username,
            password,
        )

    def validate_email_configuration(self):
        """Check if inserted email config is valid."""

        valid = True
        if not self.validate_recipients_email():
            self.ui.label_status.setText("Invalid recipients email(s) provided!")
            valid = False
        if not self.validate_smtp_port():
            self.ui.label_status.setText("Invalid smtp port provided!")
            valid = False
        if not self.validate_smtp_server():
            self.ui.label_status.setText("Invalid smtp server provided!")
            valid = False
        if not self.validate_username():
            self.ui.label_status.setText("Invalid username provided!")
            valid = False
        if not self.validate_sender_email():
            self.ui.label_status.setText("Invalid sender email provided!")
            valid = False
        if not self.validate_password():
            self.ui.label_status.setText("Invalid password provided!")
            valid = False

        if valid:
            self.ui.label_status.setText("")
            self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
            self.ui.pushButton_testEmail.setEnabled(True)
        else:
            self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
            self.ui.pushButton_testEmail.setEnabled(False)

    def validate_smtp_port(self):
        """Method to validate smtp port."""

        if (text := self.ui.lineEdit_port.text()).isdigit() and 1 <= int(text) <= 65535:
            return True
        else:
            return False

    def validate_sender_email(self):
        """Method to validate email format."""

        if validators.email(self.ui.lineEdit_senderEmail.text()):
            return True
        else:
            return False

    def validate_smtp_server(self):
        """Method to validate smtp hostname."""

        return bool(self.ui.lineEdit_smtpServer.text())

    def validate_password(self):
        """Method to validate password."""

        return bool(self.ui.lineEdit_password.text())

    def validate_recipients_email(self):
        """Method to validate receiver email(s)."""

        recipients_email = self.ui.textEdit_recipient_email.toPlainText().strip()
        if recipients_email:
            emails = recipients_email.split(", ")
            for email in emails:
                if not validators.email(email):
                    return False
                else:
                    return True

    def validate_username(self):
        """Method to validate username"""

        if self.ui.checkBox_username.isChecked():
            return bool(self.ui.lineEdit_username.text())
        else:
            return True

    def send_email(self):
        """Method to test email."""

        credentials = keyring.get_credential("WADAS_email", self.ui.lineEdit_senderEmail.text())
        sender = credentials.username
        recipients = self.ui.textEdit_recipient_email.toPlainText().strip().split(", ")

        text = "WADAS test email."
        message = MIMEText(text, "plain")

        message["Subject"] = "WADAS test email"
        message["From"] = sender
        message["To"] = self.ui.textEdit_recipient_email.toPlainText().strip()

        # Connect to Gmail's SMTP server using SSL.
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(
            self.ui.lineEdit_smtpServer.text(),
            self.ui.lineEdit_port.text(),
            context=context,
        ) as smtp_server:
            try:
                username =  self.ui.lineEdit_username if self.ui.checkBox_username.isChecked() else sender
                smtp_server.login(username, credentials.password)

                for recipient in recipients:
                    smtp_server.sendmail(sender, recipient, message.as_string())
                self.ui.plainTextEdit_test_log.setPlainText("Test email(s) sent!")
            except smtplib.SMTPResponseException as e:
                self.ui.label_status.setText(f"Test email(s) Failed!")
                self.ui.plainTextEdit_test_log.setPlainText(f"{e.smtp_code}: {e.smtp_error}")