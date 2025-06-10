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
# Date: 2024-12-23
# Description: Telegram configuration dialog module.

import os
import requests
import keyring

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QGridLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QRadioButton,
    QScrollArea,
    QWidget,
)

from wadas.domain.telegram_recipient import TelegramRecipient
from wadas.domain.notifier import Notifier
from wadas.domain.telegram_notifier import TelegramNotifier
from wadas.ui.qt.ui_configure_telegram import Ui_DialogConfigureTelegram
from wadas.domain.utils import is_valid_uuid4

module_dir_path = os.path.dirname(os.path.abspath(__file__))


class AddReceiverWorker(QThread):
    progress_updated = Signal(int)  # Emits the progress percentage
    recipient_fetched = Signal(TelegramNotifier)  # Emits the fetched TelegramNotifier

    def __init__(self, telegram_notifier):
        super().__init__()
        self.telegram_notifier = telegram_notifier

    def run(self):
        try:
            recipient = self.telegram_notifier.register_new_recipient()
            self.recipient_fetched.emit(recipient)
        except requests.RequestException as e:
            fetched_id = "Error"
            print(f"Error fetching receiver ID: {e}")
            self.recipient_fetched.emit(fetched_id)
        finally:
            self.progress_updated.emit(100)


class DialogConfigureTelegram(QDialog, Ui_DialogConfigureTelegram):
    """Class to insert Telegram configuration data to enable WADAS for Telegram notifications."""

    def __init__(self):
        super(DialogConfigureTelegram, self).__init__()
        self.ui = Ui_DialogConfigureTelegram()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon(os.path.join(module_dir_path, "..", "img", "mainwindow_icon.jpg")))
        self.ui.pushButton_test_message.setEnabled(False)
        self.ui.pushButton_remove_receiver.setEnabled(False)
        self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        self.ui.label_errorMessage.setStyleSheet("color: red")

        self.telegram_notifier = Notifier.notifiers[Notifier.NotifierTypes.TELEGRAM.value]
        self.ui_receiver_idx = 0
        self.removed_cameras = []
        self.removed_rows = set()
        self.worker = None

        # Create scrollable area for receiver list in Receivers tab
        scroll_area = QScrollArea(self.ui.tab_receivers)
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_area.setWidget(scroll_widget)
        cameras_grid_layout = QGridLayout(scroll_widget)
        cameras_grid_layout.setObjectName("gridLayout_receivers")
        self.ui.verticalLayout_receivers.addWidget(scroll_area)

        # Add a progress bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setVisible(False)
        self.ui.verticalLayout_receivers.addWidget(self.progress_bar)

        # Adding first row of receivers form

        # Slots
        self.ui.buttonBox.accepted.connect(self.accept_and_close)
        self.ui.pushButton_test_message.clicked.connect(self.send_telegram_message)
        self.ui.pushButton_add_receiver.clicked.connect(self.add_receiver)
        self.ui.pushButton_remove_receiver.clicked.connect(self.remove_receiver)
        self.ui.lineEdit_org_code.textChanged.connect(self.validate_org_code)
        self.ui.tabWidget.currentChanged.connect(self.check_existing_receivers)

        self.initialize_form()

    def check_existing_receivers(self, index):
        """Method to show the receivers list when the user clicks on the tab 'Receivers'"""
        if self.telegram_notifier:
            if index == 1:
                self.clear_receivers()
                try:
                    self.telegram_notifier.fetch_registered_recipient()
                    for r in self.telegram_notifier.recipients:
                        self.add_recipient_to_gridlayout(r)
                except Exception:
                    self.ui.label_errorMessage.setText("Unable to retrieve existing recipients")

            if index == 0:
                self.ui.plainTextEdit.setPlainText("")
                self.update_receiver_name()

    def initialize_form(self):
        """Method to initialize form with existing Telegram configuration data (if any)."""

        if self.telegram_notifier:
            self.ui.checkBox_enable_telegram_notifications.setChecked(self.telegram_notifier.enabled)
            self.ui.lineEdit_org_code.setText(self.telegram_notifier.org_code)
            self.ui.checkBox_enable_images.setChecked(self.telegram_notifier.allow_images)

        else:
            self.ui.checkBox_enable_telegram_notifications.setChecked(True)

    def add_receiver(self):
        """Method to programmatically add receiver input fields with progress bar update."""
        if self.telegram_notifier:
            self.progress_bar.setValue(0)
            self.progress_bar.setVisible(True)

            self.worker = AddReceiverWorker(self.telegram_notifier)
            self.worker.progress_updated.connect(self.update_progress)
            self.worker.recipient_fetched.connect(self.on_id_fetched)
            self.worker.start()
        else:
            self.ui.label_errorMessage.setText("You cannot add new receivers without an organization code")

    def update_progress(self, value):
        """Update the progress bar value."""
        self.progress_bar.setValue(value)

    def on_id_fetched(self, recipient):
        """Handle the fetched ID and populate the row."""
        self.progress_bar.setVisible(False)  # Hide progress bar after completion

        if not recipient:
            QMessageBox.critical(self, "Error", "Failed to fetch receiver ID.")
            return

        self.add_recipient_to_gridlayout(recipient)

    def add_recipient_to_gridlayout(self, recipient):
        """Method to add a new receiver row to the gridlayout"""
        # Add the receiver row with the fetched ID
        grid_layout_receivers = self.findChild(QGridLayout, "gridLayout_receivers")
        if grid_layout_receivers:
            row = self.ui_receiver_idx
            # Receiver selection check box
            radio_button = QRadioButton()
            radio_button.setObjectName(f"radioButton_receiver_{row}")
            radio_button.setChecked(False)
            radio_button.clicked.connect(self.update_remove_receiver_btn)
            grid_layout_receivers.addWidget(radio_button, row, 0)
            # Receiver id
            label = QLabel("ID:")
            label.setObjectName(f"label_receiverId_{row}")
            grid_layout_receivers.addWidget(label, row, 1)
            id_line_edit = QLineEdit()
            id_line_edit.setObjectName(f"lineEdit_receiver_id_{row}")
            id_line_edit.setText(recipient.recipient_id)
            id_line_edit.setReadOnly(True)
            grid_layout_receivers.addWidget(id_line_edit, row, 2)
            # Receiver name
            label = QLabel("Name:")
            label.setObjectName(f"label_Receiver_name_{row}")
            label.setToolTip("Receiver name")
            grid_layout_receivers.addWidget(label, row, 3)
            user_line_edit = QLineEdit()
            user_line_edit.setObjectName(f"lineEdit_name_{row}")
            if recipient.name:
                user_line_edit.setText(recipient.name)
            grid_layout_receivers.addWidget(user_line_edit, row, 4)
            grid_layout_receivers.setAlignment(Qt.AlignmentFlag.AlignTop)
            self.ui_receiver_idx += 1

    def update_remove_receiver_btn(self):
        """Method to update remove receiver button enablement logic."""

        self.ui.pushButton_remove_receiver.setEnabled(True)

    def clear_receivers(self):
        """Method to clear the list of the receivers."""
        grid_layout_receivers = self.findChild(QGridLayout, "gridLayout_receivers")
        for i in range(0, self.ui_receiver_idx):
            for j in range(0, 5):
                if item := grid_layout_receivers.itemAtPosition(i, j):
                    item.widget().deleteLater()
        self.update()

    def remove_receiver(self):
        """Method to programmatically remove receiver input fields."""
        for i in range(0, self.ui_receiver_idx):
            radiobtn = self.findChild(QRadioButton, f"radioButton_receiver_{i}")
            receiver_id_ln = self.findChild(QLineEdit, f"lineEdit_receiver_id_{i}")
            if radiobtn and radiobtn.isChecked() and receiver_id_ln:
                recipient = self.telegram_notifier.get_recipient_by_id(receiver_id_ln.text())
                self.telegram_notifier.remove_registered_recipient(recipient)
                break

        self.check_existing_receivers(1)

    def validate_org_code(self):
        """Method to validate form data."""

        # if org_code is not changed
        if self.telegram_notifier and self.telegram_notifier.org_code == self.ui.lineEdit_org_code.text():
            self.ui.label_errorMessage.setText("")
            self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
            self.ui.pushButton_test_message.setEnabled(True)
            return

        if self.ui.lineEdit_org_code.text():
            if is_valid_uuid4(self.ui.lineEdit_org_code.text()):
                self.ui.label_errorMessage.setText("")
                self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
                self.ui.pushButton_test_message.setEnabled(True)

                # if the org_code is valid, TelegramNotifier is instantiated
                self.telegram_notifier = TelegramNotifier(self.ui.lineEdit_org_code.text())
            else:
                self.ui.label_errorMessage.setText("Insert a valid organization code")
        else:
            if not self.ui.lineEdit_org_code.text():
                self.ui.label_errorMessage.setText("Organization code cannot be empty.")

            self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
            self.ui.pushButton_test_message.setEnabled(False)

    def update_receiver_name(self):
        """Method to keep tracks of the names chosen for the recipients."""
        for i in range(0, self.ui_receiver_idx):
            receiver_id_ln = self.findChild(QLineEdit, f"lineEdit_receiver_id_{i}")
            receiver_name_ln = self.findChild(QLineEdit, f"lineEdit_name_{i}")

            if receiver_id_ln:

                t: TelegramRecipient = self.telegram_notifier.get_recipient_by_id(receiver_id_ln.text())
                t.name = receiver_name_ln.text() if receiver_name_ln.text() else None

    def accept_and_close(self):
        """When Ok is clicked, save email config info before closing."""

        if self.telegram_notifier:
            self.update_receiver_name()
            self.telegram_notifier.enabled = self.ui.checkBox_enable_telegram_notifications.isChecked()
            self.telegram_notifier.allow_images = self.ui.checkBox_enable_images.isChecked()
            Notifier.notifiers[Notifier.NotifierTypes.TELEGRAM.value] = self.telegram_notifier

        self.accept()

    def send_telegram_message(self):
        """Method to send WhatsApp message notification."""
        self.ui.label_errorMessage.setText("")
        if self.telegram_notifier.recipients:
            message = "WADAS Test Message!"
            try:
                status, data = self.telegram_notifier.send_telegram_message(message)
                if status == 200:
                    if data["status"] == "ok":
                        self.ui.plainTextEdit.setPlainText("Telegram notification sent!")
                    else:
                        self.ui.plainTextEdit.setPlainText("\n".join(data["error_msgs"]))
                else:
                    self.ui.plainTextEdit.setPlainText(f"Error sending Test Message: {str(status)} - {data}")
            except Exception:
                self.ui.plainTextEdit.setPlainText(f"Error sending Test Message!")
        else:
            self.ui.label_errorMessage.setText("No recipient configured")
