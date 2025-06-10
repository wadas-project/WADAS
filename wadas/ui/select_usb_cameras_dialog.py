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
# Date: 2024-09-12
# Description: Local cameras configuration module.


import functools
import os

import cv2
from cv2_enumerate_cameras import enumerate_cameras
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QLineEdit,
    QPushButton,
)

from wadas.domain.camera import Camera, cameras
from wadas.domain.database import DataBase
from wadas.domain.usb_camera import USBCamera
from wadas.ui.qt.ui_select_usb_cameras import Ui_DialogSelectUSBCameras
from wadas.ui.motion_detection_dialog import MotionDetectionDialog

module_dir_path = os.path.dirname(os.path.abspath(__file__))


class DialogSelectLocalCameras(QDialog, Ui_DialogSelectUSBCameras):
    """Class to select and configure local cameras (i.e., directly plugged to the WADAS node)."""

    def __init__(self):
        super(DialogSelectLocalCameras, self).__init__()
        self.ui = Ui_DialogSelectUSBCameras()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon(os.path.join(module_dir_path, "..", "img", "mainwindow_icon.jpg")))
        self.enumerated_usb_cameras = enumerate_cameras(cv2.CAP_V4L2)
        # TODO: check API preference for linux and implement it OS independent.

        self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        self.ui.label_errorMessage.setStyleSheet("color: red")

        self.list_usb_cameras()
        self.initialize_usb_cameras()
        self.initialize_detection_params()

        # Slots
        self.ui.buttonBox.accepted.connect(self.accept_and_close)

        # db enablement status
        self.db_enabled = bool(DataBase.get_enabled_db())

    def list_usb_cameras(self):
        """Method to initialize cameras list."""

        # Setting titles to columns
        table_titles = ["Enabled", "Index", "Name", "PID", "VID", "WADAS ID", "Test"]
        bold_font = QFont()
        bold_font.setBold(True)
        row = col = 0
        for title in table_titles:
            label = QLabel(title)
            label.setFont(bold_font)
            self.ui.gridLayout_localCameras.addWidget(label, row, col)
            col += 1

        row = 1
        for camera_info in self.enumerated_usb_cameras:
            camera_index = str(camera_info.index)

            # Camera selection check box
            check_box = QCheckBox()
            check_box.setObjectName(f"checkBox_camera_{camera_index}")
            check_box.setChecked(False)
            check_box.checkStateChanged.connect(self.validate_cameras_selection)
            self.ui.gridLayout_localCameras.addWidget(check_box, row, 0)
            # Camera index
            label = QLabel(f"{camera_info.index}")
            label.setObjectName(f"label_cameraIdx_{camera_index}")
            self.ui.gridLayout_localCameras.addWidget(label, row, 1)
            # Camera name
            label = QLabel(f"{camera_info.name}")
            label.setObjectName(f"label_cameraName_{camera_index}")
            label.setToolTip(f"Path: {camera_info.path}")
            self.ui.gridLayout_localCameras.addWidget(label, row, 2)
            # Camera PID
            label = QLabel(f"{camera_info.pid}")
            label.setObjectName(f"label_cameraPid_{camera_index}")
            self.ui.gridLayout_localCameras.addWidget(label, row, 3)
            # Camera VID
            label = QLabel(f"{camera_info.vid}")
            label.setObjectName(f"label_cameraVid_{camera_index}")
            self.ui.gridLayout_localCameras.addWidget(label, row, 4)
            # Camera ID
            id_line_edit = QLineEdit()
            id_line_edit.setObjectName(f"lineEdit_cameraID_{camera_index}")
            id_line_edit.textChanged.connect(self.validate_cameras_selection)
            self.ui.gridLayout_localCameras.addWidget(id_line_edit, row, 5)
            # Test button to preview video (and detection if enabled)
            test_button = QPushButton("Test video")
            test_button.setObjectName(f"button_camera_{camera_index}")
            self.ui.gridLayout_localCameras.addWidget(test_button, row, 6)
            test_button.clicked.connect(
                functools.partial(self.test_camera_stream, camera_info.index)
            )
            self.ui.tab_camerasList.setTabOrder(check_box, id_line_edit)

            row += 1
        self.ui.gridLayout_localCameras.setAlignment(Qt.AlignmentFlag.AlignTop)

    def initialize_usb_cameras(self):
        """Method to initialize attributes from existing camera configuration (if any)."""
        if not cameras:
            return

        # Initialize camera checkboxes (if any was selected before) and IDs
        camera_number = len(self.enumerated_usb_cameras)
        for i in range(camera_number):
            checkbox = self.findChild(QCheckBox, f"checkBox_camera_{i}")
            line_edit = self.findChild(QLineEdit, f"lineEdit_cameraID_{i}")
            if not checkbox or not line_edit:
                continue

            cur_enum_cam = self.enumerated_usb_cameras[i]
            camera: USBCamera
            for camera in cameras:
                if camera.type == Camera.CameraTypes.USB_CAMERA:
                    # Iterate only USB Camera type
                    if (
                        camera.path == cur_enum_cam.path
                        and camera.name == cur_enum_cam.name
                        and camera.pid == cur_enum_cam.pid
                        and camera.vid == cur_enum_cam.vid
                    ):
                        checkbox.setChecked(camera.enabled)
                        line_edit.setText(camera.id)

    def initialize_detection_params(self):
        """Method to initialize detection parameters in UI."""

        self.ui.lineEdit_threshold.setText(f"{Camera.detection_params['threshold']}")
        self.ui.lineEdit_minContourArea.setText(f"{Camera.detection_params['min_contour_area']}")
        self.ui.lineEdit_detectionThreshold.setText(
            f"{Camera.detection_params['detection_per_second']}"
        )

    def validate_cameras_selection(self):
        """This method validated the selected cameras."""

        valid = True
        for camera_info in self.enumerated_usb_cameras:
            camera_index = str(camera_info.index)
            checkbox = self.findChild(QCheckBox, f"checkBox_camera_{camera_index}")
            line_edit = self.findChild(QLineEdit, f"lineEdit_cameraID_{camera_index}")
            if checkbox and checkbox.isChecked() and not line_edit.text():
                self.ui.label_errorMessage.setText(f"Please add ID for Camera {camera_index}")
                valid = False
            elif self.is_duplicated_id(camera_index):
                self.ui.label_errorMessage.setText(f"Duplicated Camera ID {line_edit.text()}")
                valid = False
            else:
                self.ui.label_errorMessage.setText("")

        self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(valid)

    def is_duplicated_id(self, idx):
        """Method that checks for duplicated camera ids."""

        camera_ids = []
        for camera_info in self.enumerated_usb_cameras:
            camera_index = str(camera_info.index)
            checkbox = self.findChild(QCheckBox, f"checkBox_camera_{camera_index}")
            camera_id = self.findChild(QLineEdit, f"lineEdit_cameraID_{camera_index}").text()
            if checkbox and checkbox.isChecked() and camera_id:
                if camera_id not in camera_ids:
                    camera_ids.append(camera_id)
                elif idx == str(camera_info.index):
                    return True
        return False

    def accept_and_close(self):
        """When Ok is clicked, save camera config info before closing."""

        # USB Cameras
        camera_number = len(self.enumerated_usb_cameras)
        if cameras:
            # We need to update values of existing enabled cameras.
            # The rest we will ignore unless they have an ID assigned.
            for idx in range(camera_number):
                checkbox = self.findChild(QCheckBox, f"checkBox_camera_{idx}")
                line_edit = self.findChild(QLineEdit, f"lineEdit_cameraID_{idx}")
                if checkbox and line_edit:
                    saved = False
                    for camera in cameras:
                        if camera.type == Camera.CameraTypes.USB_CAMERA:
                            if (
                                self.enumerated_usb_cameras[idx].index == camera.index
                                and self.enumerated_usb_cameras[idx].name == camera.name
                                and self.enumerated_usb_cameras[idx].pid == camera.pid
                                and self.enumerated_usb_cameras[idx].vid == camera.vid
                                and self.enumerated_usb_cameras[idx].path == camera.path
                            ):

                                # Camera index has not changed,
                                # let's save ID and enablement status if changed.
                                camera.enabled = checkbox.isChecked()
                                camera.id = line_edit.text()
                                saved = True
                                if self.db_enabled:
                                    DataBase.update_camera(camera)
                                break
                            elif (
                                self.enumerated_usb_cameras[idx].name == camera.name
                                and self.enumerated_usb_cameras[idx].pid == camera.pid
                                and self.enumerated_usb_cameras[idx].vid == camera.vid
                                and self.enumerated_usb_cameras[idx].path == camera.path
                            ):
                                # Camera index has changed
                                camera.idx = idx
                                camera.name = self.enumerated_usb_cameras[idx].name
                                camera.pid = self.enumerated_usb_cameras[idx].pid
                                camera.vid = self.enumerated_usb_cameras[idx].vid
                                camera.path = self.enumerated_usb_cameras[idx].path
                                camera.enabled = checkbox.isChecked()
                                camera.id = line_edit.text()
                                saved = True
                                break
                    if not saved:
                        # New camera
                        camera = USBCamera(
                            line_edit.text(),
                            self.enumerated_usb_cameras[idx].name,
                            checkbox.isChecked(),
                            idx,
                            self.enumerated_usb_cameras[idx].backend,
                            True,
                            self.enumerated_usb_cameras[idx].pid,
                            self.enumerated_usb_cameras[idx].vid,
                            self.enumerated_usb_cameras[idx].path,
                        )
                        cameras.append(camera)

                        # If db is enabled, insert camera into db.
                        if self.db_enabled:
                            DataBase.insert_into_db(camera)
        else:
            # Save cameras
            for idx in range(camera_number):
                checkbox = self.findChild(QCheckBox, f"checkBox_camera_{idx}")
                line_edit = self.findChild(QLineEdit, f"lineEdit_cameraID_{idx}")
                if checkbox and line_edit:
                    camera = USBCamera(
                        line_edit.text(),
                        self.enumerated_usb_cameras[idx].name,
                        checkbox.isChecked(),
                        idx,
                        self.enumerated_usb_cameras[idx].backend,
                        True,
                        self.enumerated_usb_cameras[idx].pid,
                        self.enumerated_usb_cameras[idx].vid,
                        self.enumerated_usb_cameras[idx].path,
                    )
                    cameras.append(camera)

                    # If db is enabled, insert camera into db.
                    if self.db_enabled:
                        DataBase.insert_into_db(camera)
        self.accept()

    def test_camera_stream(self, camera_idx):
        """Method to test camera video stream and motion detection"""

        camera = USBCamera(
            f"Test md for {self.enumerated_usb_cameras[camera_idx].name}",
            self.enumerated_usb_cameras[camera_idx].name,
            True,
            self.enumerated_usb_cameras[camera_idx].index,
            self.enumerated_usb_cameras[camera_idx].backend,
            True,
            self.enumerated_usb_cameras[camera_idx].pid,
            self.enumerated_usb_cameras[camera_idx].vid,
            self.enumerated_usb_cameras[camera_idx].path,
        )

        # Open Motion Detection Test Dialog
        dialog = MotionDetectionDialog()
        dialog.exec_()

