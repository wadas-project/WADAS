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
# Date: 2024-10-01
# Description: Web interface users UI Module
import base64
import logging
import subprocess
import sys
import time
from enum import Enum
from pathlib import Path

import bcrypt
from PySide6.QtCore import Qt, QThread
from PySide6.QtCore import Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QGridLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QRadioButton,
    QScrollArea,
    QWidget,
)
from validators import email as valid_email

from wadas.domain.database import DataBase, DBUser
from wadas.domain.utils import send_data_on_local_socket
from wadas.ui.error_message_dialog import WADASErrorMessage
from wadas.ui.qt.ui_configure_web_interface import Ui_DialogConfigureWebInterface

logger = logging.getLogger(__name__)

module_dir_path = Path(__file__).parent
webserver_dir = Path(module_dir_path).parent.parent / "wadas_webserver"

WEBSERVER_SOCKET_PORT = 65000


class WebserverCommands(Enum):
    KILL = "kill"
    STATUS = "status"


class WebInterfaceStatus(Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    CHECKING = "Checking"
    STARTING = "Starting"
    STOPPING = "Stopping"


class WebserverMonitorThread(QThread):
    status_signal = Signal(WebInterfaceStatus)

    def run(self):
        time.sleep(0.2)
        try:
            received = send_data_on_local_socket(WEBSERVER_SOCKET_PORT, WebserverCommands.STATUS)
            self.status_signal.emit(WebInterfaceStatus.ACTIVE if received is not None else WebInterfaceStatus.INACTIVE)
        except ConnectionRefusedError:
            self.status_signal.emit(WebInterfaceStatus.INACTIVE)


class DialogConfigureWebInterface(QDialog, Ui_DialogConfigureWebInterface):
    """Class to configure FTP server and cameras"""
    WEB_INTERFACE_MAIN_FILE = "wadas_webserver_main.py"

    def __init__(self, project_uuid):
        super(DialogConfigureWebInterface, self).__init__()
        self.ui = Ui_DialogConfigureWebInterface()
        self.ui_user_idx = 0
        self.removed_users = []
        self.removed_rows = set()
        self.roles = ["Admin", "Viewer"]
        self.web_interface_status = WebInterfaceStatus.CHECKING
        self.web_interface_expected_status = None
        self.project_uuid = project_uuid

        self.webserver_monitor = WebserverMonitorThread()
        self.webserver_monitor.start()

        # DB enablement status
        self.db_enabled = bool(DataBase.get_enabled_db())

        # UI
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon(str(module_dir_path.parent / "img" / "mainwindow_icon.jpg")))
        self.ui.pushButton_remove_user.setEnabled(False)
        self.ui.pushButton_reset_password.setEnabled(False)
        self.ui.label_errorMessage.setStyleSheet("color: red")

        # Create scrollable area for users
        scroll_area = QScrollArea(self.ui.verticalLayoutWidget)
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_area.setWidget(scroll_widget)
        users_grid_layout = QGridLayout(scroll_widget)
        users_grid_layout.setObjectName("gridLayout_users")
        self.ui.verticalLayout_users.addWidget(scroll_area)

        self.add_user()

        # Slots
        self.ui.buttonBox.accepted.connect(self.accept_and_close)
        self.ui.pushButton_add_user.clicked.connect(self.add_user)
        self.ui.pushButton_remove_user.clicked.connect(self.remove_user)
        self.ui.pushButton_reset_password.clicked.connect(self.reset_user_password)
        self.ui.pushButton_stop_web_interface.clicked.connect(self.on_web_interface_stop_clicked)
        self.ui.pushButton_start_web_interface.clicked.connect(self.on_web_interface_start_clicked)
        self.webserver_monitor.status_signal.connect(self.catch_web_interface_status)

        # Init dialog
        self.initialize_dialog()

    def initialize_dialog(self):
        """Method to initialize dialog with existing values (if any)."""

        self.update_web_interface_status()
        if self.db_enabled:
            for i, (username, email, role) in enumerate(DataBase.get_users()):
                if i:
                    self.add_user()

                user_ln = self.findChild(QLineEdit, f"lineEdit_user_{i}")
                user_ln.setText(username)
                user_ln.setEnabled(False)

                password_ln = self.findChild(QLineEdit, f"lineEdit_password_{i}")
                password_ln.setText("xxxxxxx")
                password_ln.setEnabled(False)

                email_ln = self.findChild(QLineEdit, f"lineEdit_email_{i}")
                email_ln.setText(email)

                role_cb = self.findChild(QComboBox, f"comboBox_role_{i}")
                role_txt = role if role in self.roles else "Viewer"
                role_cb.setCurrentText(role_txt)

                self.validate()
        else:
            self.findChild(QLineEdit, "lineEdit_user_0").setEnabled(False)
            self.findChild(QLineEdit, "lineEdit_password_0").setEnabled(False)
            self.findChild(QLineEdit, "lineEdit_email_0").setEnabled(False)
            self.findChild(QComboBox, "comboBox_role_0").setEnabled(False)
            self.findChild(QRadioButton, "radioButton_user_0").setEnabled(False)
            self.ui.pushButton_add_user.setEnabled(False)
            self.ui.pushButton_start_web_interface.setEnabled(False)
            self.ui.label_errorMessage.setText("Database not configured or enabled!")

    def catch_web_interface_status(self, status):
        self.web_interface_status = status
        if self.web_interface_expected_status and self.web_interface_status != self.web_interface_expected_status:
            QMessageBox.warning(
                self,
                "Error",
                "Unable to communicate with WADAS Web Interface.\nSee WADAS_webserver.log for further details."
            )
        self.update_web_interface_status()

    def update_web_interface_status(self):
        """Method to reflect up-to-date web interface status."""

        status = self.web_interface_status
        status_txt = status.value
        status_color = "color: green" if status == WebInterfaceStatus.ACTIVE else "color: red" \
            if status == WebInterfaceStatus.INACTIVE else "color:black"
        self.ui.label_web_interface_status.setText(status_txt)
        self.ui.label_web_interface_status.setStyleSheet(status_color)
        self.ui.pushButton_start_web_interface.setEnabled(status == WebInterfaceStatus.INACTIVE)
        self.ui.pushButton_stop_web_interface.setEnabled(status == WebInterfaceStatus.ACTIVE)
        self.web_interface_expected_status = None

    def on_web_interface_start_clicked(self):
        """Method to trigger start of web interface"""

        script_path = webserver_dir / self.WEB_INTERFACE_MAIN_FILE

        enc_conn_str = base64.b64encode(DataBase.get_instance().get_connection_string().encode("utf-8")).decode("utf-8")

        if script_path.exists():
            try:
                subprocess.Popen(
                    [sys.executable, script_path, f"--enc_conn_str={enc_conn_str}",
                     f"--project_uuid={self.project_uuid}"],

                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    close_fds=True
                )
                self.web_interface_status = WebInterfaceStatus.STARTING
                self.update_web_interface_status()

                # check actual status
                self.web_interface_expected_status = WebInterfaceStatus.ACTIVE
                self.webserver_monitor.start()
            except Exception:
                logger.exception("Unable to start WADAS Web Interface process")
                QMessageBox.warning(
                    self,
                    "Error",
                    "Unable to start WADAS Web Interface process"
                )
        else:
            logger.error("Web Interface file not found")
            QMessageBox.warning(
                self,
                "Error",
                "Web Interface file not found"
            )

    def on_web_interface_stop_clicked(self):
        """Method to trigger stop of web interface"""
        try:
            received = send_data_on_local_socket(WEBSERVER_SOCKET_PORT, WebserverCommands.KILL)
        except Exception:
            logger.error("Unable to communicate with Web Interface")

        self.web_interface_status = WebInterfaceStatus.STOPPING
        self.update_web_interface_status()

        # check actual status
        self.web_interface_expected_status = WebInterfaceStatus.INACTIVE
        self.webserver_monitor.start()

    def add_user(self):
        """Method to add a user into the dialog"""

        if grid_layout_users := self.findChild(QGridLayout, "gridLayout_users"):
            row = self.ui_user_idx
            # User selection check box
            radio_button = QRadioButton()
            radio_button.setObjectName(f"radioButton_user_{row}")
            radio_button.setChecked(False)
            radio_button.clicked.connect(self.on_radio_button_clicked)
            grid_layout_users.addWidget(radio_button, row, 0)
            # User
            label = QLabel("User:")
            label.setObjectName(f"label_user_{row}")
            grid_layout_users.addWidget(label, row, 1)
            user_line_edit = QLineEdit()
            user_line_edit.setObjectName(f"lineEdit_user_{row}")
            user_line_edit.textChanged.connect(self.validate)
            grid_layout_users.addWidget(user_line_edit, row, 2)
            # Password
            label = QLabel("Password:")
            label.setObjectName(f"label_password_{row}")
            grid_layout_users.addWidget(label, row, 3)
            pass_line_edit = QLineEdit()
            pass_line_edit.setObjectName(f"lineEdit_password_{row}")
            pass_line_edit.setEchoMode(QLineEdit.EchoMode.Password)
            pass_line_edit.textChanged.connect(self.validate)
            grid_layout_users.addWidget(pass_line_edit, row, 4)
            # Email
            label = QLabel("Email:")
            label.setObjectName(f"label_email_{row}")
            grid_layout_users.addWidget(label, row, 5)
            email_line_edit = QLineEdit()
            email_line_edit.setObjectName(f"lineEdit_email_{row}")
            email_line_edit.textChanged.connect(self.validate)
            grid_layout_users.addWidget(email_line_edit, row, 6)
            # Role
            label = QLabel("Role:")
            label.setObjectName(f"label_role_{row}")
            grid_layout_users.addWidget(label, row, 7)
            combo_box = QComboBox(self)
            combo_box.setObjectName(f"comboBox_role_{row}")
            combo_box.addItems(self.roles)
            combo_box.currentIndexChanged.connect(self.validate)
            combo_box.setToolTip("Select user role")
            grid_layout_users.addWidget(combo_box, row, 8)

            grid_layout_users.setAlignment(Qt.AlignmentFlag.AlignTop)
            self.ui_user_idx += 1

            self.validate()

    def remove_user(self):
        """Method to remove user from list."""

        for i in range(0, self.ui_user_idx):
            if radiobtn := self.findChild(QRadioButton, f"radioButton_user_{i}"):
                if radiobtn.isChecked() and (user_ln := self.findChild(QLineEdit, f"lineEdit_user_{i}")):
                    self.removed_users.append(user_ln.text())
                    self.removed_rows.add(i)
                    grid_layout_users = self.findChild(QGridLayout, "gridLayout_users")
                    if grid_layout_users:
                        for j in range(0, 9):
                            grid_layout_users.itemAtPosition(i, j).widget().setParent(None)
        self.ui.pushButton_remove_user.setEnabled(False)
        self.ui.pushButton_reset_password.setEnabled(False)

    def on_radio_button_clicked(self):
        """Method to update remove user button enablement logic."""

        self.ui.pushButton_remove_user.setEnabled(True)
        self.ui.pushButton_reset_password.setEnabled(True)

    def get_line_edit_txt_by_objectname(self, object_name):
        """Method to get text from UI line edit programmatically by objectname"""

        ln_object = self.findChild(QLineEdit, object_name)
        return ln_object.text() if ln_object else None

    def validate(self):
        """Method to validate dialog input fields"""

        for i in range(0, self.ui_user_idx):
            if i in self.removed_rows:
                continue
            if not self.get_line_edit_txt_by_objectname(f"lineEdit_user_{i}"):
                self.ui.label_errorMessage.setText("user name cannot be empty!")
                return False
            if not self.get_line_edit_txt_by_objectname(f"lineEdit_password_{i}"):
                self.ui.label_errorMessage.setText("password cannot be empty!")
                return False
            email = self.get_line_edit_txt_by_objectname(f"lineEdit_email_{i}")
            if not email:
                self.ui.label_errorMessage.setText("email cannot be empty!")
                return False
            elif not valid_email(email):
                self.ui.label_errorMessage.setText("Invalid email provided!")
                return False

        self.ui.label_errorMessage.setText("")
        return True

    def reset_user_password(self):
        """Method to reset user password in db."""

        for i in range(0, self.ui_user_idx):
            if radiobtn := self.findChild(QRadioButton, f"radioButton_user_{i}"):
                if radiobtn.isChecked() and (password_ln := self.findChild(QLineEdit, f"lineEdit_password_{i}")):
                    password_ln.setText("")
                    password_ln.setEnabled(True)

    def hash_password(self, password):
        """Method to generate a salt and create hash of a password"""

        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt)

    def accept_and_close(self):
        """Method to apply changes to db"""

        for i in range(0, self.ui_user_idx):
            if i in self.removed_rows:
                continue

            new_user = bool(self.findChild(QLineEdit, f"lineEdit_user_{i}").isEnabled())
            new_password = bool(self.findChild(QLineEdit, f"lineEdit_password_{i}").isEnabled())

            username = self.get_line_edit_txt_by_objectname(f"lineEdit_user_{i}")
            password = self.get_line_edit_txt_by_objectname(f"lineEdit_password_{i}")
            email = self.get_line_edit_txt_by_objectname(f"lineEdit_email_{i}")
            role = self.findChild(QComboBox, f"comboBox_role_{i}").currentText()
            hashed_password = self.hash_password(password)

            if new_user:
                db_user = DBUser(username, hashed_password, email, role)
                DataBase.insert_into_db(db_user)
            else:
                db_email, db_role = DataBase.get_user_email_and_role(username)
                if db_email != email:
                    if not DataBase.update_user_email(username, email):
                        WADASErrorMessage("Unable to update user email",
                                          f"Unable to update {username} email in db!").exec()
                if db_role != role:
                    if not DataBase.update_user_role(username, role):
                        WADASErrorMessage("Unable to update user role",
                                          f"Unable to update {username} role in db!").exec()
                if new_password:
                    if not DataBase.update_user_password(username, hashed_password):
                        WADASErrorMessage("Unable to update user password",
                                          f"Unable to update {username} password in db!").exec()

        for user in self.removed_users:
            if not DataBase.delete_user(user):
                WADASErrorMessage("Unable to remove user from db",
                                  f"Unable to remove {user} from db!").exec()
        self.close()
