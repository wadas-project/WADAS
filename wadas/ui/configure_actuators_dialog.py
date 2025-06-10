"""Configure actuators module"""

import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QGridLayout,
    QLabel,
    QLineEdit,
    QRadioButton,
    QScrollArea,
    QWidget,
)
from validators import ipv4

from wadas.domain.actuator import Actuator
from wadas.domain.camera import cameras
from wadas.domain.database import DataBase
from wadas.domain.fastapi_actuator_server import FastAPIActuatorServer, initialize_fastapi_logger
from wadas.domain.feeder_actuator import FeederActuator
from wadas.domain.roadsign_actuator import RoadSignActuator
from wadas.ui.qt.ui_configure_actuators import Ui_DialogConfigureActuators
from wadas.ui.qtextedit_logger import QTextEditLogger

module_dir_path = os.path.dirname(os.path.abspath(__file__))


class DialogConfigureActuators(QDialog, Ui_DialogConfigureActuators):
    """Class to instantiate UI dialog to configure actuator server and client(s) parameters."""

    def __init__(self):
        super(DialogConfigureActuators, self).__init__()
        self.ui = Ui_DialogConfigureActuators()
        self.ui_actuator_idx = 0
        self.removed_actuators = []
        self.actuator_server = None
        self.actuator_server_thread = None
        self.removed_rows = set()

        # UI
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon(os.path.join(module_dir_path, "..", "img", "mainwindow_icon.jpg")))
        self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        self.ui.pushButton_stop_server.setEnabled(False)
        self.ui.pushButton_remove_actuator.setEnabled(False)
        self.ui.label_status.setStyleSheet("color: red")

        # Create scrollable area for Actuator list in Actuators tab
        scroll_area = QScrollArea(self.ui.tab_actuator_list)
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_area.setWidget(scroll_widget)
        actuators_grid_layout = QGridLayout(scroll_widget)
        actuators_grid_layout.setObjectName("gridLayout_actuators")
        self.ui.verticalLayout_actuators.addWidget(scroll_area)

        # Adding first row of actuators form
        self.add_actuator() if not Actuator.actuators else self.add_actuator(False)

        # Slots
        self.ui.buttonBox.accepted.connect(self.accept_and_close)
        self.ui.buttonBox.rejected.connect(self.reject_and_close)
        self.ui.pushButton_add_actuator.clicked.connect(self.on_add_actuator_clicked)
        self.ui.pushButton_remove_actuator.clicked.connect(self.remove_actuator)
        self.ui.pushButton_key_file.clicked.connect(self.select_key_file)
        self.ui.pushButton_cert_file.clicked.connect(self.select_certificate_file)
        self.ui.lineEdit_actuator_timeout.textChanged.connect(self.validate)
        self.ui.lineEdit_server_ip.textChanged.connect(self.validate)
        self.ui.lineEdit_server_port.textChanged.connect(self.validate)
        self.ui.pushButton_start_server.clicked.connect(self.start_actuator_server)
        self.ui.pushButton_stop_server.clicked.connect(self.stop_actuator_server)

        # Init dialog
        self.initialize_dialog()

        # DB enablement status
        self.db_enabled = bool(DataBase.get_enabled_db())

    def initialize_dialog(self):
        """Method to initialize dialog with existing values (if any)."""

        if FastAPIActuatorServer.actuator_server:
            self.ui.lineEdit_actuator_timeout.setText(str(
                FastAPIActuatorServer.actuator_server.actuator_timeout_threshold))
            self.ui.lineEdit_server_ip.setText(str(FastAPIActuatorServer.actuator_server.ip))
            self.ui.lineEdit_server_port.setText(str(FastAPIActuatorServer.actuator_server.port))
            self.ui.label_key_file.setText(FastAPIActuatorServer.actuator_server.ssl_key)
            self.ui.label_cert_file.setText(FastAPIActuatorServer.actuator_server.ssl_certificate)
        else:
            self.ui.lineEdit_actuator_timeout.setText("30")
            self.ui.lineEdit_server_ip.setText("0.0.0.0")
            self.ui.lineEdit_server_port.setText("8443")

        self.list_actuators_in_tab()

    def list_actuators_in_tab(self):
        """Method to list actuators in actuators tab."""

        i = 0
        for key in Actuator.actuators:
            if i > 0:
                self.add_actuator(type_select_enabled=False)
            actuator_id_ln = self.findChild(QLineEdit, f"lineEdit_actuator_id_{i}")
            actuator_id_ln.setText(Actuator.actuators[key].id)
            actuator_type_cb: QComboBox
            actuator_type_cb = self.findChild(QComboBox, f"comboBox_actuator_type_{i}")
            if Actuator.actuators[key].type == Actuator.ActuatorTypes.ROADSIGN:
                actuator_type_cb.setCurrentText(Actuator.ActuatorTypes.ROADSIGN.value)
            elif Actuator.actuators[key].type == Actuator.ActuatorTypes.FEEDER:
                actuator_type_cb.setCurrentText(Actuator.ActuatorTypes.FEEDER.value)
            actuator_enablement: QCheckBox
            actuator_enablement = self.findChild(QCheckBox, f"checkBox_actuator_enablement_{i}")
            actuator_enablement.setChecked(Actuator.actuators[key].enabled)
            i += 1

    def validate(self):
        """Method to validate dialog input fields"""

        valid = True
        # Actuator timeout
        actuator_timeout = self.ui.lineEdit_actuator_timeout.text()
        if not actuator_timeout:
            self.ui.label_status.setText("No actuator timeout provided!")
            valid = False
        else:
            try:
                int_actuator_timeout = int(self.ui.lineEdit_actuator_timeout.text())
                if int_actuator_timeout < 0:
                    self.ui.label_status.setText(
                        "Invalid actuator timeout provided! It shall be a positive integer value.")
                    valid = False
            except ValueError:
                self.ui.label_status.setText("Invalid actuator timeout provided! It shall be an integer value.")
                valid = False
        # IP
        if not ipv4(self.ui.lineEdit_server_ip.text()):
            self.ui.label_status.setText("Invalid server IP address provided!")
            valid = False
        # Port
        if port := self.ui.lineEdit_server_port.text():
            if int(port) < 1 or int(port) > 65535:
                self.ui.label_status.setText("Invalid server port provided!")
                valid = False
        else:
            self.ui.label_status.setText("No server port provided!")
            valid = False
        # SSL key file
        if not os.path.isfile(self.ui.label_key_file.text()):
            self.ui.label_status.setText("Invalid SSL key file provided!")
            valid = False
        # SSL Certificate file
        if not os.path.isfile(self.ui.label_cert_file.text()):
            self.ui.label_status.setText("Invalid SSL certificate file provided!")
            valid = False
        # Actuator ID
        for i in range(0, self.ui_actuator_idx):
            if i in self.removed_rows:
                continue

            if not self.get_actuator_id(i):
                self.ui.label_status.setText("Missing Actuator ID!")
                valid = False
            elif self.is_duplicated_id(i):
                self.ui.label_status.setText(f"Duplicated Actuator ID {self.get_actuator_id(i)}!")
                valid = False

        if valid:
            self.ui.label_status.setText("")
        self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(valid)
        self.ui.pushButton_start_server.setEnabled(valid)

    def add_actuator(self, type_select_enabled=True):
        """Method to add new actuator line edits."""

        grid_layout_actuators = self.findChild(QGridLayout, "gridLayout_actuators")
        if grid_layout_actuators:
            row = self.ui_actuator_idx
            # Actuator selection check box
            radio_button = QRadioButton()
            radio_button.setObjectName(f"radioButton_actuator_{row}")
            radio_button.setChecked(False)
            radio_button.clicked.connect(self.update_remove_actuator_btn)
            grid_layout_actuators.addWidget(radio_button, row, 0)
            # Actuator id
            label = QLabel("ID:")
            label.setObjectName(f"label_actuator_id_{row}")
            grid_layout_actuators.addWidget(label, row, 1)
            id_line_edit = QLineEdit()
            id_line_edit.setObjectName(f"lineEdit_actuator_id_{row}")
            id_line_edit.textChanged.connect(self.validate)
            grid_layout_actuators.addWidget(id_line_edit, row, 2)
            # Actuator type
            label = QLabel("Type:")
            label.setObjectName(f"label_actuator_type_{row}")
            grid_layout_actuators.addWidget(label, row, 3)
            combo_box = QComboBox(self)
            combo_box.setObjectName(f"comboBox_actuator_type_{row}")
            types = [type.value for type in Actuator.ActuatorTypes]
            combo_box.addItems(types)
            combo_box.currentIndexChanged.connect(self.validate)
            combo_box.setToolTip("Select actuator type")
            combo_box.setEnabled(type_select_enabled) # If Actuator object exists type cannot be changed
            grid_layout_actuators.addWidget(combo_box, row, 4)
            # Actuator Enablement
            label = QLabel("Enable:")
            label.setObjectName(f"label_actuator_enable_{row}")
            grid_layout_actuators.addWidget(label, row, 5)
            check_box = QCheckBox()
            check_box.setObjectName(f"checkBox_actuator_enablement_{row}")
            check_box.setChecked(False)
            check_box.checkStateChanged.connect(self.validate)
            grid_layout_actuators.addWidget(check_box, row, 6)
            grid_layout_actuators.setAlignment(Qt.AlignmentFlag.AlignTop)
            self.ui_actuator_idx += 1

            self.validate()

    def remove_actuator(self):
        """Method to remove Actuator from list."""

        for i in range(0, self.ui_actuator_idx):
            radiobtn = self.findChild(QRadioButton, f"radioButton_actuator_{i}")
            if radiobtn:
                actuator_id_ln = self.findChild(QLineEdit, f"lineEdit_actuator_id_{i}")
                if radiobtn.isChecked() and actuator_id_ln:
                    self.removed_actuators.append(actuator_id_ln.text())
                    # QGridLayout does not remove the row, only widgets so we store deleted rows
                    self.removed_rows.add(i)
                    gridLayout_actuators = self.findChild(QGridLayout, "gridLayout_actuators")
                    if gridLayout_actuators:
                        for j in range(0, 7):
                            gridLayout_actuators.itemAtPosition(i, j).widget().setParent(None)
        self.ui.pushButton_remove_actuator.setEnabled(False)
        self.validate()

    def update_remove_actuator_btn(self):
        """Method to remove actuator from the list"""

        self.ui.pushButton_remove_actuator.setEnabled(True)

    def select_key_file(self):
        """Method to select SSL key file"""

        file_name = QFileDialog.getOpenFileName(
            self, "Open SSL key file", os.getcwd(), "Pem File (*.pem)"
        )
        self.ui.label_key_file.setText(str(file_name[0]))
        self.validate()

    def select_certificate_file(self):
        """Method to select SSL certificate file"""

        file_name = QFileDialog.getOpenFileName(
            self, "Open SSL certificate file", os.getcwd(), "Pem File (*.pem)"
        )
        self.ui.label_cert_file.setText(str(file_name[0]))
        self.validate()

    def get_actuator_id(self, row):
        """Method to get actuator id text from UI programmatically by row number"""
        actuator_id_ln: QLineEdit
        actuator_id_ln = self.findChild(QLineEdit, f"lineEdit_actuator_id_{row}")
        return actuator_id_ln.text() if actuator_id_ln else None

    def get_actuator_type(self, row):
        """Method to get actuator type from UI programmatically by row number"""
        actuator_type: QComboBox
        actuator_type = self.findChild(QComboBox, f"comboBox_actuator_type_{row}")
        return actuator_type.currentText()

    def get_actuator_enablement(self, row):
        """Method to get actuator enablement from UI programmatically by row number"""
        actuator_enablement: QCheckBox
        actuator_enablement = self.findChild(QCheckBox, f"checkBox_actuator_enablement_{row}")
        return actuator_enablement.isChecked()

    def is_duplicated_id(self, idx):
        """Method to check whether actuators have unique id."""

        actuators_id = set()
        for i in range(0, self.ui_actuator_idx):
            cur_id = self.get_actuator_id(i)
            if cur_id not in actuators_id:
                actuators_id.add(cur_id)
            elif i == idx:
                return True
        return False

    def on_add_actuator_clicked(self):
        self.add_actuator(type_select_enabled=True)

    def accept_and_close(self):
        """When Ok is clicked, save Ai model config info before closing."""

        if FastAPIActuatorServer.actuator_server:
            FastAPIActuatorServer.actuator_server.actuator_timeout_threshold = int(
                self.ui.lineEdit_actuator_timeout.text())
            FastAPIActuatorServer.actuator_server.ip = self.ui.lineEdit_server_ip.text()
            FastAPIActuatorServer.actuator_server.port = int(self.ui.lineEdit_server_port.text())
            FastAPIActuatorServer.actuator_server.ssl_certificate = self.ui.label_cert_file.text()
            FastAPIActuatorServer.actuator_server.ssl_key = self.ui.label_key_file.text()
        else:
            FastAPIActuatorServer.actuator_server = FastAPIActuatorServer(
                self.ui.lineEdit_server_ip.text(),
                int(self.ui.lineEdit_server_port.text()),
                self.ui.label_cert_file.text(),
                self.ui.label_key_file.text(),
                int(self.ui.lineEdit_actuator_timeout.text())
            )
        if Actuator.actuators:
            actuators_id = set()
            for i in range(0, self.ui_actuator_idx):
                if i in self.removed_rows:
                    continue

                cur_actuator_id = self.get_actuator_id(i)
                cur_actuator_type = self.get_actuator_type(i)
                cur_actuator_enablement = self.get_actuator_enablement(i)
                if cur_actuator_id and cur_actuator_type:
                    actuators_id.add(cur_actuator_id)
                    if cur_actuator_id in Actuator.actuators:
                        # Actuator exists and we update its enablement status
                        Actuator.actuators[cur_actuator_id].enabled = cur_actuator_enablement
                        # Update actuator in db if enabled
                        if self.db_enabled:
                            DataBase.update_actuator(Actuator.actuators[cur_actuator_id])
                    else:
                        # Actuator does not exist, therefore we add it to the dictionary
                        if cur_actuator_type == Actuator.ActuatorTypes.ROADSIGN.value:
                            actuator = RoadSignActuator(cur_actuator_id, cur_actuator_enablement)
                            Actuator.actuators[actuator.id] = actuator
                            # If db is enabled,add actuator into db
                            if self.db_enabled:
                                DataBase.insert_into_db(actuator)
                        elif cur_actuator_type == Actuator.ActuatorTypes.FEEDER.value:
                            actuator = FeederActuator(cur_actuator_id, cur_actuator_enablement)
                            Actuator.actuators[actuator.id] = actuator
                            # If db is enabled,add actuator into db
                            if self.db_enabled:
                                DataBase.insert_into_db(actuator)
            # If an actuator changes the id we have to remove previous orphaned ids from dictionary
            for key in list(Actuator.actuators):
                if key not in actuators_id:
                    # Remove actuator from db
                    if self.db_enabled:
                        DataBase.update_actuator(Actuator.actuators[key], delete_actuator=True)
                    del Actuator.actuators[key]
                    # Remove orphan actuators from Camera association (if any)
                    for camera in cameras:
                        for actuator in tuple(camera.actuators):
                            if actuator.id == key:
                                camera.actuators.remove(actuator)
        else:
            for i in range(0, self.ui_actuator_idx):
                cur_actuator_id = self.get_actuator_id(i)
                cur_actuator_type = self.get_actuator_type(i)
                cur_actuator_enablement = self.get_actuator_enablement(i)
                if cur_actuator_id and cur_actuator_type:
                    if cur_actuator_type == Actuator.ActuatorTypes.ROADSIGN.value:
                        actuator = RoadSignActuator(cur_actuator_id, cur_actuator_enablement)
                        Actuator.actuators[actuator.id] = actuator
                        # If db is enabled,add actuator into db
                        if self.db_enabled:
                            DataBase.insert_into_db(actuator)
                    elif cur_actuator_type == Actuator.ActuatorTypes.FEEDER.value:
                        actuator = FeederActuator(cur_actuator_id, cur_actuator_enablement)
                        Actuator.actuators[actuator.id] = actuator
                        # If db is enabled,add actuator into db
                        if self.db_enabled:
                            DataBase.insert_into_db(actuator)
        self.accept()

    def reject_and_close(self):
        self._stop_actuator_server()

    def start_actuator_server(self):
        """Method to start the Actuator server."""

        if not self.actuator_server:
            self.actuator_server = FastAPIActuatorServer(
                self.ui.lineEdit_server_ip.text(),
                int(self.ui.lineEdit_server_port.text()),
                self.ui.label_cert_file.text(),
                self.ui.label_key_file.text(),
            )
        self._setup_logger()
        self.ui.pushButton_stop_server.setEnabled(True)
        self.ui.pushButton_start_server.setEnabled(False)
        self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        # Start the thread
        self.actuator_server_thread = self.actuator_server.run()

    def _stop_actuator_server(self):
        """Method to stop the Actuator server"""
        if self.actuator_server and self.actuator_server_thread:
            self.actuator_server.stop()
            self.actuator_server_thread.join()

    def stop_actuator_server(self):
        """Method to stop the Actuator server and to show the appropriate buttons on the UI"""
        self._stop_actuator_server()
        self.ui.pushButton_stop_server.setEnabled(False)
        self.ui.pushButton_start_server.setEnabled(True)
        self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)

    def _setup_logger(self):
        """Initialize fastapi logger for UI logging."""
        log_textbox = QTextEditLogger(self.ui.plainTextEdit_test_server_log)
        initialize_fastapi_logger(handler=log_textbox)

    def closeEvent(self, event):
        self._stop_actuator_server()