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
# Description: Module containing MainWindow class and methods.


import datetime
import logging
import os
import sys
from datetime import timedelta
from logging.handlers import RotatingFileHandler
from packaging.version import Version
from pathlib import Path
import uuid

import keyring
from PySide6 import QtCore, QtGui
from PySide6.QtCore import QSettings, QThread
from PySide6.QtGui import QBrush
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
)

from wadas.domain.database import DataBase
from wadas._version import __version__
from wadas.domain.actuator import Actuator
from wadas.domain.ai_model import AiModel
from wadas.domain.animal_detection_mode import AnimalDetectionAndClassificationMode
from wadas.domain.bear_detection_mode import BearDetectionMode
from wadas.domain.custom_classification_mode import CustomClassificationMode
from wadas.domain.camera import cameras, Camera
from wadas.domain.configuration import load_configuration_from_file, save_configuration_to_file
from wadas.domain.fastapi_actuator_server import FastAPIActuatorServer
from wadas.domain.ftps_server import initialize_fpts_logger
from wadas.domain.notifier import Notifier
from wadas.domain.operation_mode import OperationMode
from wadas.domain.test_model_mode import TestModelMode
from wadas.domain.utils import initialize_asyncio_logger
from wadas.ui.about_dialog import AboutDialog
from wadas.ui.ai_model_download_dialog import AiModelDownloadDialog
from wadas.ui.configure_actuators_dialog import DialogConfigureActuators
from wadas.ui.configure_ai_model_dialog import ConfigureAiModel
from wadas.ui.configure_camera_actuator_associations_dialog import (
    DialogConfigureCameraToActuatorAssociations,
)
from wadas.ui.configure_db_dialog import ConfigureDBDialog
from wadas.ui.configure_email_dialog import DialogInsertEmail
from wadas.ui.configure_ftp_cameras_dialog import DialogFTPCameras
from wadas.ui.configure_telegram_dialog import DialogConfigureTelegram
from wadas.ui.configure_whatsapp_dialog import DialogConfigureWhatsApp
from wadas.ui.configure_web_interface import DialogConfigureWebInterface
from wadas.ui.error_message_dialog import WADASErrorMessage
from wadas.ui.license_dialog import LicenseDialog
from wadas.ui.select_animal_species import DialogSelectAnimalSpecies
from wadas.ui.select_mode_dialog import DialogSelectMode
from wadas.ui.select_test_mode_input import DialogSelectTestModeInput
from wadas.ui.select_usb_cameras_dialog import DialogSelectLocalCameras
from wadas.ui.terms_n_conditions_dialog import TermsAndConditionsDialog
from wadas.ui.qt.ui_mainwindow import Ui_MainWindow
from wadas.ui.qtextedit_logger import QTextEditLogger

logger = logging.getLogger()

level_mapping = {
    0: logging.DEBUG,
    1: logging.INFO,
    2: logging.WARNING,
    3: logging.ERROR,
    4: logging.CRITICAL,
}

module_dir_path = os.path.dirname(os.path.abspath(__file__))


class MainWindow(QMainWindow):
    """Main Window class listing code customization. All code to manipulate
    the mainwindow class shall be defined here.
    ui/mainwindow.py represents auto generated code from Qt Creator, it is
    overwritten every time a new modification is done on Qt Creator side."""

    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.configuration_file_name = None
        self.key_ring = None
        self.ftp_server = None
        self.load_status = dict.fromkeys(
            ["errors_on_load",
            "errors_log",
            "config_version",
            "compatible_config",
            "valid_ftp_keyring",
            "valid_email_keyring",
            "valid_whatsapp_keyring"
             ]
        )
        self.uuid = uuid.uuid4()
        self.settings = QSettings("UI_settings.ini", QSettings.IniFormat)
        self.default_window_title = f"{self.windowTitle()}  {__version__}"
        self.set_mainwindow_title()

        # Connect Actions
        self._connect_actions()

        # Create required folders
        os.makedirs("log", exist_ok=True)

        # Setup UI logger
        self._setup_logger()

        # Initialize startup image
        self.set_image(os.path.join(module_dir_path, "..", "img", "WADAS_logo_big.jpg"))
        # Set mainwindow icon
        self.setWindowIcon(
            QtGui.QIcon(os.path.join(module_dir_path, "..", "img", "mainwindow_icon.jpg"))
        )

        # Last saved config
        if (path := self.settings.value("last_saved_config_path", None, str)) and os.path.exists(path):
            self.set_recent_configuration(path)
        else:
            self.ui.actionRecent_configuration.setEnabled(False)

        # Update mainwindow UI methods
        self._init_logging_dropdown()
        self.update_toolbar_status()
        self.update_info_widget()
        logger.info("Welcome to WADAS!")

        self.show_terms_n_conditions()

    def _connect_actions(self):
        """List all actions to connect to MainWindow"""
        self.ui.actionSelect_Mode.triggered.connect(self.select_mode)
        self.ui.actionRun.triggered.connect(self.run)
        self.ui.actionStop.triggered.connect(self.interrupt_thread)
        self.ui.actionActionConfigureEmail.triggered.connect(self.configure_email)
        self.ui.actionSelectLocalCameras.triggered.connect(self.select_local_cameras)
        self.ui.actionConfigure_Ai_model.triggered.connect(self.configure_ai_model)
        self.ui.actionSave_configuration_as.triggered.connect(self.save_as_to_config_file)
        self.ui.actionSave_configuration_as_menu.triggered.connect(self.save_as_to_config_file)
        self.ui.actionOpen_configuration_file.triggered.connect(self.load_config_from_file)
        self.ui.actionOpen_configuration_file_menu.triggered.connect(self.load_config_from_file)
        self.ui.actionSave_configuration.triggered.connect(self.save_config_to_file)
        self.ui.actionSave_configuration_menu.triggered.connect(self.save_config_to_file)
        self.ui.actionConfigure_FTP_Cameras.triggered.connect(self.configure_ftp_cameras)
        self.ui.actionConfigure_actuators.triggered.connect(self.configure_actuators)
        self.ui.actionConfigure_camera_to_actuator_associations.triggered.connect(
            self.configure_camera_to_actuators_associations
        )
        self.ui.actionLicense.triggered.connect(self.show_license)
        self.ui.actionAbout.triggered.connect(self.show_about)
        self.ui.actionConfigure_WA.triggered.connect(self.configure_whatsapp)
        self.ui.actionConfigure_Telegram.triggered.connect(self.configure_telegram)
        self.ui.actionRecent_configuration.triggered.connect(self.open_last_saved_file)
        self.ui.actionConfigure_database.triggered.connect(self.configure_database)
        self.ui.actionConfigure_web_interface.triggered.connect(self.configure_web_interface)
        self.ui.actionExit.triggered.connect(self.close)

    def _connect_mode_ui_slots(self):
        """Function to connect UI slot with operation_mode signals."""

        # Connect Signal to update image in widget.
        OperationMode.cur_operation_mode.update_image.connect(self.set_image)
        OperationMode.cur_operation_mode.update_image.connect(self.update_info_widget)
        OperationMode.cur_operation_mode.run_finished.connect(self.on_run_completion)

        # Connect Signal to update actuator list in widget.
        OperationMode.cur_operation_mode.update_actuator_status.connect(self.update_en_actuator_list)

    def _setup_logger(self):
        """Initialize MainWindow logger for UI logging."""

        # fix: one of our import libraries is setting a root logger with a handler
        # we need to remove it to avoid duplicate logs
        for handler in logging.root.handlers[1:]:
            logging.root.removeHandler(handler)

        formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s", "%Y-%m-%d %H:%M:%S")
        logging_level = logging.DEBUG
        # Line edit logging in mainwindow
        self.log_txtedt_handler = QTextEditLogger(self.ui.plainTextEdit_log)
        self.log_txtedt_handler.setFormatter(formatter)
        logger.setLevel(logging.INFO)
        logger.addHandler(self.log_txtedt_handler)

        # WADAS log file
        file_handler = RotatingFileHandler(
            os.path.join(os.getcwd(), "log", "WADAS.log"),
            maxBytes=10 * 1024 * 1024,
            backupCount=3,
        )
        file_handler.setLevel(logging_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        initialize_fpts_logger()
        initialize_asyncio_logger()

    def set_mainwindow_title(self, projectname="Untitled"):
        """Method to set MainWindow title showing version and projectname"""

        window_title = f"{self.default_window_title} - {projectname}[*]"
        self.setWindowTitle(window_title)

    def set_image(self, img):
        """Set image to show in WADAS. This is used for startup, detected and
        classified images."""
        if os.path.isfile(img):
            image_widget = self.ui.label_image
            image_widget.setPixmap(QtGui.QPixmap(img))
            image_widget.setMinimumSize(1, 1)
            image_widget.setScaledContents(True)
            image_widget.show()
        else:
            logger.error("Provided image path is not valid. %s", img)

    def select_mode(self):
        """Slot for mode selection (toolbar button)"""

        dialog = DialogSelectMode()
        if dialog.exec():
            if OperationMode.cur_operation_mode_type:
                logger.info("Selected operation mode: %s", OperationMode.cur_operation_mode_type.value)
                if (OperationMode.cur_operation_mode_type ==
                        OperationMode.OperationModeTypes.CustomSpeciesClassificationMode):
                    logger.info("Selected custom species to classify: %s",
                                OperationMode.cur_custom_classification_species)
                self.setWindowModified(True)
                self.update_toolbar_status()
                self.update_info_widget()
            else:
                logger.debug("No operation mode selected.")

    def run(self):
        """Slot to run selected mode once run button is clicked.
        Since image processing is heavy task, new thread is created."""

        self.instantiate_selected_model()
        # Satisfy preconditions independently of selected operation mode
        if not self.check_models():
            logger.error("Cannot run operation mode without AI models. Aborting.")
            return
        if OperationMode.cur_operation_mode.type != OperationMode.OperationModeTypes.TestModelMode:
            if not cameras:
                logger.error("No camera configured. Please configure input cameras and run again.")
                return
            elif not self.camera_enabled():
                logger.error("No camera enabled. Please enable at least one camera and run again.")
                return
        else:
            # Passing cameras list to the selected operation mode
            OperationMode.cur_operation_mode.cameras = cameras

        # Check if notifications have been configured, if not warn the user
        if not self.check_notification_enablement():
            return

        # Satisfy preconditions and required inputs for the selected operation mode
        if OperationMode.cur_operation_mode:
            match OperationMode.cur_operation_mode.type:
                case OperationMode.OperationModeTypes.TestModelMode:
                    url, file_path = self.test_model_mode_input_dialog()
                    OperationMode.cur_operation_mode.url = url
                    OperationMode.cur_operation_mode.file_path = file_path
                    if not OperationMode.cur_operation_mode.url and not OperationMode.cur_operation_mode.file_path:
                        logger.error("Cannot proceed without a valid input. Please run again.")
                        return
                case OperationMode.OperationModeTypes.CustomSpeciesClassificationMode:
                    if not OperationMode.cur_custom_classification_species:
                        return
                    else:
                        OperationMode.cur_operation_mode.custom_target_species = (
                            OperationMode.cur_custom_classification_species)

            db_status_log = "Database not configured."
            if (db := DataBase.get_instance()):
                db_status_log = "Database enabled!" if db.enabled else "Database configured but not enabled."
            logger.info(db_status_log)

            # Connect slots to update UI from operation mode
            self._connect_mode_ui_slots()

            # Initialize thread where to run the inference
            self.thread = QThread()

            # Move operation mode in dedicated thread
            OperationMode.cur_operation_mode.moveToThread(self.thread)

            # Connect thread related signals and slots
            self.thread.started.connect(OperationMode.cur_operation_mode.run)
            OperationMode.cur_operation_mode.run_finished.connect(self.thread.quit)
            OperationMode.cur_operation_mode.run_finished.connect(OperationMode.cur_operation_mode.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)

            # Start the thread
            self.thread.start()

            # Enable Stop button in toolbar
            self.update_toolbar_status_on_run(True)
        else:
            logger.error("Unable to run the selected model.")

    def camera_enabled(self):
        """Method to check whether at least a camera is enabled."""

        return any(camera.enabled for camera in cameras)

    def instantiate_selected_model(self):
        """Given the selected model from dedicated UI Dialog, instantiate the corresponding object."""

        if not OperationMode.cur_operation_mode_type:
            logger.error("No operation mode selected.")
            return
        else:
            match OperationMode.cur_operation_mode_type:
                case OperationMode.OperationModeTypes.TestModelMode:
                    OperationMode.cur_operation_mode = TestModelMode()
                case OperationMode.OperationModeTypes.AnimalDetectionMode:
                    OperationMode.cur_operation_mode = AnimalDetectionAndClassificationMode(classification=False)
                case OperationMode.OperationModeTypes.AnimalDetectionAndClassificationMode:
                    OperationMode.cur_operation_mode = AnimalDetectionAndClassificationMode()
                case OperationMode.OperationModeTypes.BearDetectionMode:
                    OperationMode.cur_operation_mode = BearDetectionMode()
                case OperationMode.OperationModeTypes.CustomSpeciesClassificationMode:
                    OperationMode.cur_operation_mode = CustomClassificationMode()
                # add case for new operation modes

    def on_run_completion(self):
        """Actions performed after a run is completed."""

        self.update_toolbar_status_on_run(False)
        self.update_info_widget()
        self.update_en_actuator_list()

    def interrupt_thread(self):
        """Method to interrupt a running thread."""

        if self.thread:
            self.thread.requestInterruption()

    def update_toolbar_status(self):
        """Update status of toolbar and related buttons (actions)."""

        if not OperationMode.cur_operation_mode_type:
            self.ui.actionRun.setEnabled(False)
        elif OperationMode.cur_operation_mode_type == OperationMode.OperationModeTypes.TestModelMode:
            self.ui.actionRun.setEnabled(True)
        elif (
            OperationMode.cur_operation_mode_type != OperationMode.OperationModeTypes.TestModelMode
            and not cameras
        ):
            self.ui.actionRun.setEnabled(False)
            logger.warning("No camera configured. Please configure camera(s) to run the selected operation mode.")
        elif (
            OperationMode.cur_operation_mode_type != OperationMode.OperationModeTypes.TestModelMode
            and not self.camera_enabled()
        ):
            self.ui.actionRun.setEnabled(False)
            logger.warning("No camera enabled. Please enable at least a camera to run the selected operation mode.")
        else:
            valid_configuration = True
            if self.enabled_email_notifier_exists() and not self.load_status["valid_email_keyring"]:
                valid_configuration = False
                logger.info("Enabled email notifier exists but not valid credentials in keyring are stored. "
                            "Please edit email configuration to fix the issue and to be able to run.")
            if self.ftp_camera_exists() and not self.load_status["valid_ftp_keyring"]:
                valid_configuration = False
                logger.info("FTP camera(s) configured but not valid credentials in keyring are stored."
                            "Please edit FTP Camera(s) configuration to fix the issue and to be able to run.")
            if self.enabled_whatsapp_notifier_exists() and not self.load_status["valid_whatsapp_keyring"]:
                valid_configuration = False
                logger.info("WhatsApp notifications configured but not valid token in keyring is stored."
                            "Please edit WhatsApp configuration to fix the issue and to be able to run.")

            self.ui.actionRun.setEnabled(valid_configuration)
        self.ui.actionStop.setEnabled(False)
        self.ui.actionSave_configuration_as.setEnabled(self.isWindowModified())
        self.ui.actionSave_configuration_as_menu.setEnabled(self.isWindowModified())
        self.ui.actionSave_configuration.setEnabled(
            self.isWindowModified() and bool(self.configuration_file_name)
        )
        self.ui.actionSave_configuration_menu.setEnabled(
            self.isWindowModified() and bool(self.configuration_file_name)
        )
        self.ui.actionConfigure_web_interface.setEnabled(bool(DataBase.get_enabled_db()))

    def ftp_camera_exists(self):
        """Method that checks if at least one FTP camera exists in camera list."""

        return any(camera.type == Camera.CameraTypes.FTP_CAMERA for camera in cameras)

    def enabled_email_notifier_exists(self):
        """Method that checks if email notifier is configured."""

        return any(((Notifier.notifiers[notifier] and Notifier.notifiers[notifier].type == Notifier.NotifierTypes.EMAIL
                  and Notifier.notifiers[notifier].enabled) for notifier in Notifier.notifiers))

    def enabled_whatsapp_notifier_exists(self):
        """Method that checks if whatsapp notifier is configured"""

        return any(((Notifier.notifiers[notifier] and
                     Notifier.notifiers[notifier].type == Notifier.NotifierTypes.WHATSAPP and
                     Notifier.notifiers[notifier].enabled) for notifier in Notifier.notifiers))

    def update_toolbar_status_on_run(self, running):
        """Update toolbar status while running model."""

        self.ui.actionStop.setEnabled(running)
        self.ui.actionRun.setEnabled(not running)
        self.ui.actionActionConfigureEmail.setEnabled(not running)
        self.ui.actionSelect_Mode.setEnabled(not running)
        self.ui.actionConfigure_Ai_model.setEnabled(not running)
        self.ui.actionSelectLocalCameras.setEnabled(not running)
        self.ui.actionConfigure_FTP_Cameras.setEnabled(not running)
        self.ui.actionOpen_configuration_file.setEnabled(not running)
        self.ui.actionOpen_configuration_file_menu.setEnabled(not running)
        self.ui.actionSave_configuration_as_menu.setEnabled(not running)
        self.ui.actionSave_configuration_as.setEnabled(not running)
        self.ui.actionSave_configuration.setEnabled(not running)
        self.ui.actionRecent_configuration.setEnabled(not running)
        self.ui.actionConfigure_actuators.setEnabled(not running)
        self.ui.actionConfigure_camera_to_actuator_associations.setEnabled(not running)
        self.ui.actionConfigure_WA.setEnabled(not running)
        self.ui.actionConfigure_Telegram.setEnabled(not running)
        self.ui.actionConfigure_database.setEnabled(not running)

    def update_info_widget(self):
        """Update information widget."""

        if OperationMode.cur_operation_mode_type:
            self.ui.label_op_mode.setText(OperationMode.cur_operation_mode_type.value)
            match OperationMode.cur_operation_mode_type:
                case OperationMode.OperationModeTypes.TunnelMode:
                    classification_en_txt = "No"
                case OperationMode.OperationModeTypes.AnimalDetectionMode:
                    classification_en_txt = "No"
                case OperationMode.OperationModeTypes.CustomSpeciesClassificationMode:
                    classification_en_txt = "Yes (custom)"
                case _:
                    classification_en_txt = "Yes"
            self.ui.label_classification_enablement.setText(classification_en_txt)
        else:
            self.ui.label_op_mode.setText("None")
            self.ui.label_classification_enablement.setText("")

        if OperationMode.cur_operation_mode:
            path = Path(OperationMode.cur_operation_mode.last_detection)
            self.ui.label_last_detection.setText(os.path.join(path.parent.name, path.name))
            self.ui.label_classified_animal.setText(
                str(OperationMode.cur_operation_mode.last_classified_animals_str)
            )

        if db := DataBase.get_enabled_db():
            self.ui.label_database.setText(db.type.value)
        else:
            self.ui.label_database.setText("None")

        notifier_lable_text = ", ".join(
            cur_notifier.type.value for notifier, cur_notifier in Notifier.notifiers.items()
            if cur_notifier and cur_notifier.enabled) or "None"
        self.ui.label_notification_method.setText(notifier_lable_text)

    def test_model_mode_input_dialog(self):
        """Method to run dialog for insertion of a URL to fetch image from."""

        if (select_test_mode_input_dlg := DialogSelectTestModeInput()).exec():
            if select_test_mode_input_dlg.url:
                logger.debug("Provided URL from dialog: %s", select_test_mode_input_dlg.url)
            elif select_test_mode_input_dlg.file_path:
                logger.debug("Provided file path from dialog: %s", select_test_mode_input_dlg.url)
            else:
                logger.error("Invalid input provided. Aborting Test Model Mode...")

            return select_test_mode_input_dlg.url, select_test_mode_input_dlg.file_path
        else:
            logger.info("Test model mode input selection aborted.")
            return "", ""

    def custom_species_dialog(self):
        """Method to run a dialog to return selected custom species to classify."""

        species_dialog = DialogSelectAnimalSpecies()
        if species_dialog.exec_():
            logger.info("Selected custom species to classify: %s", species_dialog.selected_species)
            return species_dialog.selected_species
        else:
            logger.warning("Custom species selection aborted.")
            return ""

    def configure_email(self):
        """Method to run dialog for insertion of email parameters to enable notifications."""

        insert_email_dialog = DialogInsertEmail()
        if insert_email_dialog.exec_():
            logger.info("Email configuration added.")

            credentials = keyring.get_credential("WADAS_email", "")
            logger.info("Saved credentials for %s", credentials.username)
            self.load_status["valid_email_keyring"] = True
            self.setWindowModified(True)
            self.update_toolbar_status()
            self.update_info_widget()
        else:
            logger.debug("Email configuration aborted.")

    def check_notification_enablement(self):
        """Method to check whether a notification protocol has been set in WADAS.
        If not, ask the user whether to proceed without."""

        notification_cfg = False
        notification_enabled = False
        for notifier in Notifier.notifiers:
            if Notifier.notifiers[notifier]:
                if Notifier.notifiers[notifier].is_configured():
                    notification_cfg = True
                if Notifier.notifiers[notifier].enabled:
                    notification_enabled = True
        message = ""
        if not notification_cfg:
            logger.warning("No notification protocol set.")
            message = "No notification protocol properly set. Do you wish to continue anyway?"
        elif not notification_enabled:
            logger.warning("No notification protocol enabled.")
            message = "No enabled notification protocol. Do you wish to continue anyway?"

        if message:
            message_box = QMessageBox(self)
            message_box.setWindowTitle("No enabled notification protocol")
            message_box.setText(message)
            message_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            answer = message_box.exec()

            return answer == QMessageBox.Yes
        else:
            return True

    def save_config_if_db_exists(self):
        """Method that performs autosave of the configuration to file if database exists"""

        if DataBase.get_enabled_db():
            if self.configuration_file_name:
                # Force project save to guarantee consistency
                logger.info("Autosave enabled! note: DB will enforce autosave when modifying cameras and actuators.")
                self.save_config_to_file()
            else:
                logger.warning("Current configuration has not been saved yet! "
                               "Please save it as soon as possible to avoid db misalignment.")

    def select_local_cameras(self):
        """Method to trigger UI dialog for local camera(s) configuration."""

        select_local_cameras = DialogSelectLocalCameras()
        if select_local_cameras.exec_():
            logger.info("Camera(s) configured.")
            self.setWindowModified(True)
            self.update_toolbar_status()
            self.update_en_camera_list()
            self.save_config_if_db_exists()

    def configure_actuators(self):
        """Method to trigger UI dialog for actuator(s) configuration."""

        configure_actuators_dlg = DialogConfigureActuators()
        if configure_actuators_dlg.exec_():
            logger.info("Actuator(s) configured.")
            self.setWindowModified(True)
            self.update_toolbar_status()
            self.update_en_actuator_list()
            self.save_config_if_db_exists()

    def configure_camera_to_actuators_associations(self):
        """Method to trigger UI dialog for actuator(s) configuration."""

        configure_camera2actuators_dlg = DialogConfigureCameraToActuatorAssociations()
        if configure_camera2actuators_dlg.exec_():
            logger.info("Camera(s) to Actuator(s) association(s) configured.")
            self.setWindowModified(True)
            self.update_toolbar_status()
            self.save_config_if_db_exists()

    def configure_ai_model(self):
        """Method to trigger UI dialog to configure Ai model."""

        configure_ai_model = ConfigureAiModel()
        if configure_ai_model.exec():
            logger.info("Ai model configured.")
            logger.debug(
                "Detection threshold: %s. Classification threshold: %s",
                AiModel.detection_threshold,
                AiModel.classification_threshold,
            )
            self.setWindowModified(True)
            self.update_toolbar_status()

    def check_models(self):
        """Method to initialize classification model."""
        if not AiModel.check_model(AiModel.detection_model_version, AiModel.classification_model_version):
            logger.warning("AI module not found. Downloading...")
            ai_download_dialog = AiModelDownloadDialog(True)
            if ai_download_dialog.exec():
                return (ai_download_dialog.download_success and
                        AiModel.check_model(AiModel.detection_model_version, AiModel.classification_model_version))
            else:
                logger.error("Ai models files download cancelled by user. Aborting.")
                return False
        else:
            logger.info("AI module found!")
            return True

    def set_recent_configuration(self, cfg_file_path):
        """Method to set recent configuration file used references"""

        self.ui.actionRecent_configuration.setText(cfg_file_path)
        self.ui.actionRecent_configuration.setEnabled(True)
        self.settings.setValue("last_saved_config_path", cfg_file_path)

    def save_config_to_file(self):
        """Method to save configuration to file."""

        if not self.configuration_file_name:
            error_dialog = WADASErrorMessage("No configuration file provided",
            "No configuration file provided. Please specify file name and path.")
            error_dialog.exec()
            logger.error("No configuration file provided. Aborting save.")
            return
        else:
            save_configuration_to_file(self.configuration_file_name, self.uuid)
            self.set_mainwindow_title(os.path.basename(self.configuration_file_name))
            self.setWindowModified(False)
            self.update_toolbar_status()
            self.set_recent_configuration(self.configuration_file_name)

    def save_as_to_config_file(self):
        """Method to save configuration file as"""

        file_name = QFileDialog.getSaveFileName(
            self,
            "Select WADAS configuration file to save",
            os.getcwd(),
            "YAML File (*.yaml)",
        )
        if file_name[0]:
            self.configuration_file_name = str(file_name[0])
        else:
            # Empty file name (or dialog Cancel button)
            return

        self.save_config_to_file()

    def load_config_from_file(self):
        """Method to load config from file."""

        file_name = QFileDialog.getOpenFileName(
            self, "Open WADAS configuration file", os.getcwd(), "YAML File (*.yaml)"
        )

        if file_name[0]:
            self.load_status = load_configuration_from_file(file_name[0])
            if not self.compatible_version() or self.errors_on_load():
                return

            self.configuration_file_name = file_name[0]
            self.uuid = uuid.UUID(self.load_status["uuid"])
            self.set_mainwindow_title(os.path.basename(file_name[0]))
            self.setWindowModified(False)
            self.update_toolbar_status()
            self.update_info_widget()
            self.update_en_camera_list()
            self.update_en_actuator_list()
            self.set_recent_configuration(self.configuration_file_name)

            self.check_keyrings_status()

    def compatible_version(self):
        """Method to check if version of loaded config is compatible with WADAS one"""

        if self.load_status["compatible_config"]:
            if self.load_status["config_version"] < Version(__version__.lstrip("v")):
                logger.debug("Older WADAS version configuration loaded.")
            return True
        else:
            error_dialog = WADASErrorMessage("Incompatible configuration file provided",
                "Provided WADAS configuration version is not compatible with current version of "
                "WADAS therefore cannot be loaded."
            )
            error_dialog.exec()
            return False

    def errors_on_load(self):
        """Method to check if error(s) occurred while loading the config file."""

        if self.load_status["errors_on_load"]:
            if self.load_status["errors_on_load"]:
                error_dlg = WADASErrorMessage("Error occurred while loading configuration file",
                                              repr(self.load_status["errors_log"]))
            else:
                error_dlg = WADASErrorMessage("Error occurred while loading configuration file",
                                              "Please check logs for error detail.")
            error_dlg.exec()
            return True
        else:
            return False

    def check_keyrings_status(self):
        """Method to check keyring status returned after load from config"""

        if not self.load_status["valid_email_keyring"]:
            reply = QMessageBox.question(
                self,
                "Invalid email credentials. ",
                "Would you like to edit email configuration to fix credentials issue?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.configure_email()

        if not self.load_status["valid_ftp_keyring"]:
            reply = QMessageBox.question(
                self,
                "Invalid FTP camera credentials. ",
                "Would you like to edit FTP camera configuration to fix credentials issue?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.configure_ftp_cameras()

        if not self.load_status["valid_whatsapp_keyring"]:
            reply = QMessageBox.question(
                self,
                "Invalid WhatsApp token. ",
                "Would you like to edit WhatsApp configuration to fix token issue?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.configure_whatsapp()

    def configure_ftp_cameras(self):
        """Method to trigger ftp cameras configuration dialog"""

        configure_ftp_cameras_dlg = DialogFTPCameras()
        if configure_ftp_cameras_dlg.exec():
            logger.info("FTP Server and Cameras configured.")
            self.load_status["valid_ftp_keyring"] = True
            self.setWindowModified(True)
            self.update_toolbar_status()
            self.update_en_camera_list()
            self.save_config_if_db_exists()

    def configure_whatsapp(self):
        """Method to trigger WhatsApp configuration dialog"""

        configure_whatsapp_dlg = DialogConfigureWhatsApp()
        if configure_whatsapp_dlg.exec():
            logger.info("WhatsApp notification configured.")
            self.setWindowModified(True)
            self.update_toolbar_status()
            self.update_info_widget()

    def configure_telegram(self):
        """Method to trigger Telegram configuration dialog"""

        configure_telegram_dlg = DialogConfigureTelegram()
        if configure_telegram_dlg.exec():
            logger.info("Telegram notification configured.")
            self.setWindowModified(True)
            self.update_toolbar_status()
            self.update_info_widget()

    def configure_database(self):
        """Method to trigger DB configuration dialog"""

        if (configure_db_dialog := ConfigureDBDialog(self.uuid)).exec():
            logger.info("Database configured.")
            if configure_db_dialog.db_created and DataBase.get_enabled_db() and self.configuration_file_name:
                # Force project save to guarantee consistency
                logger.info(
                    "Autosave enabled! note: DB will enforce autosave when creating new db.")
                self.save_config_to_file()
            self.setWindowModified(True)
            self.update_toolbar_status()
            self.update_info_widget()

    def configure_web_interface(self):
        """Method to trigger web interface configuration dialog"""

        if DialogConfigureWebInterface(self.uuid).exec():
            logger.info("Web interface configured.")

    def update_en_camera_list(self):
        """Method to list enabled camera(s) in UI"""

        self.ui.listWidget_en_cameras.clear()
        for camera in cameras:
            if camera.enabled:
                text = f"({camera.type.value}) {camera.id}"
                self.ui.listWidget_en_cameras.addItem(text)

    def update_en_actuator_list(self):
        """Method to list enabled actuator(s) in UI"""
        threshold_time = FastAPIActuatorServer.actuator_server.actuator_timeout_threshold if FastAPIActuatorServer.actuator_server else 30
        self.ui.listWidget_en_actuators.clear()
        for actuator in Actuator.actuators.values():
            if actuator.enabled:
                if FastAPIActuatorServer.actuator_server.startup_time:
                    # inactive actuator: connected at least once but unseen for {threshold_time} seconds
                    # or never connected within the first {threshold_time} seconds since server startup.
                    if (actuator.last_update is not None and (
                            datetime.datetime.now() - actuator.last_update > timedelta(seconds=threshold_time)) or
                            actuator.last_update is None and (
                                    datetime.datetime.now() - FastAPIActuatorServer.actuator_server.startup_time > timedelta(
                                seconds=threshold_time))):

                        text = f"({actuator.type.value}) {actuator.id} - inactive"
                        color = QtCore.Qt.GlobalColor.red
                        tooltip_text = f"Last Activity: {actuator.last_update.strftime('%d %b %Y, %H:%M:%S')}" \
                            if actuator.last_update else "Last Activity: never"

                    # active actuator: connected in the last {threshold_time} seconds
                    elif actuator.last_update is not None and (
                            datetime.datetime.now() - actuator.last_update <= timedelta(seconds=threshold_time)):
                        text = f"({actuator.type.value}) {actuator.id}"
                        color = QtCore.Qt.GlobalColor.darkGreen
                        tooltip_text = f"Last Activity: {actuator.last_update.strftime('%d %b %Y, %H:%M:%S')}"

                    # waiting for actuator first connection
                    else:
                        text = f"({actuator.type.value}) {actuator.id}"
                        color = QtCore.Qt.GlobalColor.black
                        tooltip_text = ""

                # server not started
                else:
                    text = f"({actuator.type.value}) {actuator.id}"
                    color = QtCore.Qt.GlobalColor.black
                    tooltip_text = ""

                self.ui.listWidget_en_actuators.addItem(text)
                item = self.ui.listWidget_en_actuators.item(
                    self.ui.listWidget_en_actuators.count() - 1
                )
                item.setForeground(QBrush(color))
                item.setToolTip(tooltip_text)

    def _init_logging_dropdown(self):
        """Method to initialize logging levels in tooldbar dropdown"""

        label = QLabel("Log level: ")
        self.ui.toolBar.addWidget(label)

        combo_box = QComboBox(self)
        combo_box.setObjectName("logLevelComboBox")
        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        combo_box.addItems(levels)
        combo_box.setToolTip("Select logging level")
        combo_box.setCurrentText("INFO")
        combo_box.currentIndexChanged.connect(self.change_logging_level)
        self.ui.toolBar.addWidget(combo_box)

    def change_logging_level(self, index):
        """Method to modify UI logging level"""

        new_level = level_mapping.get(index, logging.DEBUG)
        logger.setLevel(logging.DEBUG)
        self.log_txtedt_handler.setLevel(logging.DEBUG)
        logger.log(new_level, "Logging level changed to %s:", logging.getLevelName(new_level))
        self.log_txtedt_handler.setLevel(new_level)

    def closeEvent(self, event):
        """Method to handle proper thread closure when close window action is triggered"""

        if not self.ui.actionRun.isEnabled() and self.ui.actionStop.isEnabled():
            reply = QMessageBox.question(
                self,
                "Confirm Exit",
                "Are you sure you want to exit?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                # Terminate running mode for safe shutdown
                self.interrupt_thread()
                # Terminate DB object, engine and active session(s)
                DataBase.destroy_instance()
                event.accept()
            else:
                event.ignore()
        elif self.ui.actionSave_configuration_as.isEnabled():
            reply = QMessageBox.question(
                self,
                "Confirm Exit",
                """There are unsaved settings, if you proceed now all changes will be lost.
Are you sure you want to exit?""",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    def show_license(self):
        """Method to show WADAS license in UI dialog."""

        license_dialog = LicenseDialog()
        license_dialog.exec()

    def show_about(self):
        """Method to show about WADAS UI dialog."""

        about_dialog = AboutDialog()
        about_dialog.exec_()

    def show_terms_n_conditions(self):
        """Method to show terms and conditions of use for WADAS."""

        # Check if the welcome message should be shown
        if not self.settings.value("show_terms_n_conditions", True, type=bool):
            return

        terms_n_conditions_dlg = TermsAndConditionsDialog(self.settings.value("terms_n_conditions", False, type=bool))
        terms_n_conditions_dlg.exec()

        # Save the preference if the user checks "Don't show again"
        if terms_n_conditions_dlg.terms_accepted:
            self.settings.setValue("terms_n_conditions", True)
            if terms_n_conditions_dlg.dont_show:
                self.settings.setValue("show_terms_n_conditions", False)
        else:
            # Force closure if terms and conditions are not accepted
            self.close()
            sys.exit()

    def open_last_saved_file(self):
        """Method to enable opening of last saved configuration file"""

        if (path:=self.settings.value("last_saved_config_path", None, str)) and os.path.exists(path):
            self.load_status = load_configuration_from_file(path)
            if not self.compatible_version() or self.errors_on_load():
                return

            self.configuration_file_name = path
            self.uuid = uuid.UUID(self.load_status["uuid"])
            self.set_mainwindow_title(os.path.basename(path))
            self.setWindowModified(False)
            self.update_toolbar_status()
            self.update_info_widget()
            self.update_en_camera_list()
            self.update_en_actuator_list()
            self.set_recent_configuration(self.configuration_file_name)

            self.check_keyrings_status()
        else:
            logger.warning("No last saved file found or file no longer exists.")
            self.ui.actionRecent_configuration.setEnabled(False)  # Disable if file does not exist
            self.settings.remove("last_saved_config_path")
