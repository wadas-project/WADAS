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
# Description: DB UI configuration module.

import os

import keyring
import validators
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QMessageBox, QStatusBar, QProgressBar

from wadas.domain.database import DataBase
from wadas.ui.error_message_dialog import WADASErrorMessage
from wadas.ui.qt.ui_configure_db_dialog import Ui_ConfigureDBDialog
from wadas.domain.utils import is_valid_database_name
from wadas._version import __dbversion__

module_dir_path = os.path.dirname(os.path.abspath(__file__))


class SanitizeWorker(QThread):
    finished = Signal()  # Signal emitted when the task is done

    def run(self):
        DataBase.sanitize_db()
        self.finished.emit()

class ConfigureDBDialog(QDialog, Ui_ConfigureDBDialog):
    """Class to insert DB configuration to enable WADAS for database persistency."""

    def __init__(self, project_uuid):
        super(ConfigureDBDialog, self).__init__()
        self.ui = Ui_ConfigureDBDialog()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon(os.path.join(module_dir_path, "..", "img", "mainwindow_icon.jpg")))
        self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        self.ui.label_error.setStyleSheet("color: red")
        self.ui.pushButton_test_db.setEnabled(False)

        # Slots
        self.ui.buttonBox.accepted.connect(self.accept_and_close)
        self.ui.pushButton_test_db.clicked.connect(self.test_db)
        self.ui.radioButton_MySQL.clicked.connect(self.on_radioButton_checked)
        self.ui.radioButton_SQLite.clicked.connect(self.on_radioButton_checked)
        self.ui.radioButton_MariaDB.clicked.connect(self.on_radioButton_checked)
        self.ui.lineEdit_db_host.textChanged.connect(self.validate)
        self.ui.lineEdit_db_port.textChanged.connect(self.validate)
        self.ui.lineEdit_db_username.textChanged.connect(self.validate)
        self.ui.lineEdit_db_password.textChanged.connect(self.validate)
        self.ui.lineEdit_db_name.textChanged.connect(self.validate)
        self.ui.buttonBox.button(QDialogButtonBox.Cancel).clicked.connect(self.on_cancel_clicked)
        self.ui.checkBox_enable_db.clicked.connect(self.on_enable_state_changed)

        self.init_dialog()
        self.uuid = project_uuid
        self.db_created = False
        self.initial_wadas_db = DataBase.get_instance()
        self.ui.plainTextEdit_db_test.setPlainText("Test out your DB before accepting changes!")

        # Indefinite progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate range
        self.progress_bar.setVisible(False)  # Initially hidden
        self.ui.gridLayout_mysql.addWidget(self.progress_bar)

    def init_dialog(self):
        """Method to initialize dialog with saved configuration data"""

        if not (wadas_db := DataBase.get_instance()):
            self.ui.checkBox_enable_db.setChecked(True)
            self.ui.radioButton_SQLite.setChecked(True)
            self.ui.label_db_version.setText(__dbversion__)
            self.ui.checkBox_new_db.setChecked(True)
        else:
            self.ui.checkBox_enable_db.setChecked(wadas_db.enabled)
            self.ui.lineEdit_db_host.setText(wadas_db.host)
            self.ui.label_db_version.setText(wadas_db.version)
            if wadas_db.type:
                match wadas_db.type:
                    case DataBase.DBTypes.MYSQL:
                        self.ui.radioButton_MySQL.setChecked(True)
                        pwd = keyring.get_password("WADAS_DB_MySQL", wadas_db.username)
                        self.ui.lineEdit_db_port.setText(str(wadas_db.port))
                        self.ui.lineEdit_db_username.setText(wadas_db.username)
                        self.ui.lineEdit_db_password.setText(pwd)
                        self.ui.lineEdit_db_name.setText(wadas_db.database_name)
                    case DataBase.DBTypes.MARIADB:
                        self.ui.radioButton_MariaDB.setChecked(True)
                        pwd = keyring.get_password("WADAS_DB_MariaDB", wadas_db.username)
                        self.ui.lineEdit_db_port.setText(str(wadas_db.port))
                        self.ui.lineEdit_db_username.setText(wadas_db.username)
                        self.ui.lineEdit_db_password.setText(pwd)
                        self.ui.lineEdit_db_name.setText(wadas_db.database_name)
                    case DataBase.DBTypes.SQLITE:
                        self.ui.radioButton_SQLite.setChecked(True)
                    case _:
                        unrecognized_db_type_dlg = WADASErrorMessage("Unrecognized DB type",
                                                                     "Database type is not recognized or supported.")
                        unrecognized_db_type_dlg.exec()
            else:
                unrecognized_db_type_dlg = WADASErrorMessage("No DB type",
                                                             "Database type is not configured.")
                unrecognized_db_type_dlg.exec()
        self.on_radioButton_checked(True)

    def on_radioButton_checked(self, init_dialog=False):
        """Method to update dialog fields depending on DB selection"""

        auth_db_selected = self.ui.radioButton_MySQL.isChecked() or self.ui.radioButton_MariaDB.isChecked()
        self.ui.lineEdit_db_port.setEnabled(auth_db_selected)
        self.ui.lineEdit_db_username.setEnabled(auth_db_selected)
        self.ui.lineEdit_db_password.setEnabled(auth_db_selected)
        self.ui.lineEdit_db_name.setEnabled(auth_db_selected)
        if auth_db_selected:
            self.ui.label_host.setText("Host name:")
            if not self.ui.lineEdit_db_name.text():
                self.ui.lineEdit_db_name.setPlaceholderText("wadas")
            if not self.ui.lineEdit_db_host.text():
                self.ui.lineEdit_db_host.setPlaceholderText("127.0.0.1")
        elif self.ui.radioButton_SQLite.isChecked():
            self.ui.label_host.setText("File name:")
            self.ui.lineEdit_db_name.setPlaceholderText("")
            if not self.ui.lineEdit_db_host.text():
                self.ui.lineEdit_db_host.setPlaceholderText("wadas_db.sqlite")
        self.validate()

    def _update_common_params(self, wadas_db):
        """Method to update params common to MySQL and SQLite db types"""

        wadas_db.host = self.ui.lineEdit_db_host.text()
        wadas_db.enabled = self.ui.checkBox_enable_db.isChecked()

    def _update_mysql_params(self, wadas_db):
        """Method to update params specific to MySQL or MariaDB db type"""

        self._update_common_params(wadas_db)
        wadas_db.port = int(self.ui.lineEdit_db_port.text())
        wadas_db.username = self.ui.lineEdit_db_username.text()
        wadas_db.database_name = self.ui.lineEdit_db_name.text()

    def accept_and_close(self):
        """When Ok is clicked, save db config info before closing."""

        wadas_db = DataBase.get_instance()
        if self.ui.radioButton_SQLite.isChecked():
            if not wadas_db:
                self.new_sqlite_db()
            elif wadas_db.type != DataBase.DBTypes.SQLITE:
                if self.ask_db_type_change():
                    DataBase.destroy_instance()
                    self.new_sqlite_db()
            else:
                self._update_common_params(wadas_db)
        elif self.ui.radioButton_MySQL.isChecked():
            if not wadas_db:
                self.new_mysql_db()
            elif wadas_db.type != DataBase.DBTypes.MYSQL:
                if self.ask_db_type_change():
                    DataBase.destroy_instance()
                    self.new_mysql_db()
            else:
                self._update_mysql_params(wadas_db)
        elif self.ui.radioButton_MariaDB.isChecked():
            if not wadas_db:
                self.new_mariadb_db()
            elif wadas_db.type != DataBase.DBTypes.MARIADB:
                if self.ask_db_type_change():
                    DataBase.destroy_instance()
                    self.new_mariadb_db()
            else:
                self._update_mysql_params(wadas_db)

        if create_db:= self.ui.checkBox_new_db.isChecked():
            self.create_db()

        if create_db and not self.db_created:
            return
        self.accept()

    def ask_db_type_change(self):
        reply = QMessageBox.question(
            self,
            "Confirm Replace Database",
            "Changing the database type will replace the existing database. Do you want to continue?",
            QMessageBox.Yes | QMessageBox.No
        )
        return reply != QMessageBox.No

    def new_mysql_db(self):
        """Method to create and initialize a new MySQL DB with dialog input fields"""

        DataBase.initialize(
            DataBase.DBTypes.MYSQL,
            self.ui.lineEdit_db_host.text(),
            int(self.ui.lineEdit_db_port.text()),
            self.ui.lineEdit_db_username.text(),
            self.ui.lineEdit_db_name.text(),
            self.ui.checkBox_enable_db.isChecked(),
            self.ui.label_db_version.text()
        )
        keyring.set_password(
            "WADAS_DB_MySQL",
            self.ui.lineEdit_db_username.text(),
            self.ui.lineEdit_db_password.text(),
        )

    def new_sqlite_db(self):
        """Method to create and initialize a new SQLite DB with dialog input fields"""

        DataBase.initialize(
            DataBase.DBTypes.SQLITE,
            self.ui.lineEdit_db_host.text(),
            None,
            "",
            "",
            self.ui.checkBox_enable_db.isChecked(),
            self.ui.label_db_version.text()
        )

    def new_mariadb_db(self):
        """Method to create and initialize a new MariaDB with dialog input fields"""

        DataBase.initialize(
            DataBase.DBTypes.MARIADB,
            self.ui.lineEdit_db_host.text(),
            int(self.ui.lineEdit_db_port.text()),
            self.ui.lineEdit_db_username.text(),
            self.ui.lineEdit_db_name.text(),
            self.ui.checkBox_enable_db.isChecked(),
            self.ui.label_db_version.text()
        )
        keyring.set_password(
            "WADAS_DB_MariaDB",
            self.ui.lineEdit_db_username.text(),
            self.ui.lineEdit_db_password.text(),
        )

    def init_db_from_dialog_params(self, log_info=True):
        """Method to initialize database object from dialog input fields"""

        db_type = None
        if self.ui.radioButton_SQLite.isChecked():
            db_type = DataBase.DBTypes.SQLITE
        elif self.ui.radioButton_MySQL.isChecked():
            db_type = DataBase.DBTypes.MYSQL
        elif self.ui.radioButton_MariaDB.isChecked():
            db_type = DataBase.DBTypes.MARIADB

        port_str = self.ui.lineEdit_db_port.text()
        DataBase.initialize(
            db_type,
            self.ui.lineEdit_db_host.text(),
            int(port_str) if port_str.isdigit() else 0,
            self.ui.lineEdit_db_username.text(),
            self.ui.lineEdit_db_name.text(),
            self.ui.checkBox_enable_db.isChecked(),
            self.ui.label_db_version.text(),
            log=log_info
        )

    def create_db(self):
        """Method to trigger new db creation"""

        if self.initial_wadas_db:
            if self.initial_wadas_db.host != self.ui.lineEdit_db_host.text():
                DataBase.destroy_instance()
            elif (not self.ui.radioButton_SQLite.isChecked() and
                        self.ui.lineEdit_db_name.text() != self.initial_wadas_db.database_name):
                    DataBase.destroy_instance()
            else:
                db_uuid = DataBase.get_db_uuid()
                db_version = DataBase.get_db_version()
                if db_uuid and db_version:
                    message = "Database already existing!" if self.db_created else \
                        "Cannot create the db as it already exists! Please delete it or rename it before proceed."
                    self.show_status_dialog("Database creation status", message, False)
                    return

        if db := DataBase.get_instance():
            # Populate DB with existing cameras and actuators
            if db.create_database():
                DataBase.populate_db(self.uuid)
                self.db_created = True
        message = "Database successfully created!" if self.db_created else "Failed to create the db!"
        self.show_status_dialog("Database creation status", message, self.db_created)
        self.validate()

    def show_status_dialog(self, title, message, success: bool):
        """Method to show message with db creation status"""

        icon = QMessageBox.Information if success else QMessageBox.Critical
        msg_box = QMessageBox()
        msg_box.setWindowTitle(title)
        msg_box.setWindowIcon(QIcon(os.path.join(module_dir_path, "..", "img", "mainwindow_icon.jpg")))
        msg_box.setText(message)
        msg_box.setIcon(icon)
        msg_box.setStandardButtons(QMessageBox.Ok)

        msg_box.exec()

    def validate_port(self, port):
        """Validate port method"""

        try:
            port_to_int = int(port)
        except  ValueError:
            self.ui.label_error.setText("Invalid port type. Shall be an integer value!")
            return False

        if port_to_int < 1 or port_to_int > 65535:
            self.ui.label_error.setText("Invalid port provided!")
            return False
        else:
            return True

    def validate(self):
        """Method to validate db parameters"""

        valid = True
        host = self.ui.lineEdit_db_host.text()
        is_sqlite_selected = self.ui.radioButton_SQLite.isChecked()

        if not is_sqlite_selected and not is_valid_database_name(self.ui.lineEdit_db_name.text()):
            valid = False
            self.ui.label_error.setText("No valid database name!")

        if not host:
            host_field_text = "file name" if is_sqlite_selected else "host name"
            self.ui.label_error.setText(f"Database {host_field_text} field cannot be empty.")
            valid = False

        if self.ui.radioButton_MySQL.isChecked() or self.ui.radioButton_MariaDB.isChecked():
            if not self.ui.lineEdit_db_password.text():
                self.ui.label_error.setText("Database password field cannot be empty.")
                valid = False
            if not self.ui.lineEdit_db_username.text():
                self.ui.label_error.setText("Database username field cannot be empty.")
                valid = False
            if port := self.ui.lineEdit_db_port.text():
                if not self.validate_port(port):
                    valid = False
            else:
                self.ui.label_error.setText("No server port provided!")
                valid = False
            if (host and (
                    not validators.domain(host)
                    and not validators.ipv4(host)
                    and not validators.ipv6(host)
                    )
            ):
                self.ui.label_error.setText("No valid hostname or IP address provided!")
                valid = False
        elif is_sqlite_selected:
            if (host and (
                    validators.ipv4(host) or
                    validators.ipv6(host))):
                self.ui.label_error.setText("No valid sqlite db file name provided!")
                valid = False

        if valid:
            self.ui.label_error.setText("")
            self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
            enable_test = valid if not self.ui.checkBox_new_db.isChecked() else (valid and self.db_created)

            self.ui.pushButton_test_db.setEnabled(enable_test)
        else:
            self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

    def test_db(self):
        """Method to test db connection"""

        self.ui.plainTextEdit_db_test.setPlainText("")
        # Make sure we're testing latest input data and not instantiated db values
        DataBase.destroy_instance()
        self.init_db_from_dialog_params(log_info=False)

        db_uuid = DataBase.get_db_uuid()
        db_version = DataBase.get_db_version()

        if db_uuid and db_version:
            text = (f"DB version: {db_version},\n"
                    f"Associated project uuid: {db_uuid}.\n"
                    f"Connection test succeeded!")
        elif not db_uuid:
            text = ("DB associated uuid not found!\n"
                    "Connection test failed!")
        elif not db_version:
            text = ("DB version not found!\n"
                    "Connection test failed!")
        else:
            text = "Connection test failed!"
        self.ui.plainTextEdit_db_test.setPlainText(text)

        if db_uuid and str(self.uuid) != db_uuid:
            self.show_status_dialog("Project UUID mismatch in database",
                                    "Project UUID is different than the one stored in DB!\n"
                                    f"Project UUID:{self.uuid}\n"
                                    "Use of this database is highly discouraged as it might cause errors and crashes.\n"
                                    "Please make sure to select the correct one.",
                                    False)
            self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

    def on_cancel_clicked(self):
        """Method to cancel and exit the dialog"""

        # DB instance is saved only when OK button is pressed.
        if self.initial_wadas_db:
            DataBase.destroy_instance()
            # Pristine previous db config, if any
            port, username, database_name = (None, None, None) if (
                self.initial_wadas_db.type == DataBase.DBTypes.SQLITE) else (
                self.initial_wadas_db.port, self.initial_wadas_db.username, self.initial_wadas_db.database_name)
            DataBase.initialize(
                self.initial_wadas_db.type,
                self.initial_wadas_db.host,
                port,
                username,
                database_name,
                self.initial_wadas_db.enabled,
                self.initial_wadas_db.version,
                False
            )

    def on_enable_state_changed(self):
        """Method to sanitize db if existing db is re-enabled."""

        if self.ui.checkBox_enable_db.isChecked():
            if self.initial_wadas_db and not self.initial_wadas_db.enabled and not self.db_created:
                reply = QMessageBox.question(
                    self,
                    "Confirm database synchronization",
                    "Re-Enabling the db will cause the synchronization of WADAS data into db.\n"
                    "This operation cannot be reverted or interrupted. Are you sure you want to continue?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    self.start_sanitization()
                    self.show_status_dialog("Database synchronization status",
                                            "Database synchronization complete!",
                                            True)
                else:
                    self.ui.checkBox_enable_db.setChecked(False)

    def start_sanitization(self):
        """Method that starts the sanitization process in a separate thread."""

        self.progress_bar.setVisible(True)
        self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        self.ui.buttonBox.button(QDialogButtonBox.Cancel).setEnabled(False)
        self.ui.label_error.setText("Synchronizing database...")

        # Create and start the worker thread
        self.worker = SanitizeWorker()
        self.worker.finished.connect(self.on_sanitization_complete)
        self.worker.start()

    def on_sanitization_complete(self):
        """Method to complete the sanitization process."""

        self.progress_bar.setVisible(False)
        self.ui.label_error.setText("")
        self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
        self.ui.buttonBox.button(QDialogButtonBox.Cancel).setEnabled(True)