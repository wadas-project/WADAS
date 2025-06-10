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
# Date: 2024-08-16
# Description: Insert URL module

import os
import re

import validators
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QFileDialog

from wadas.ui.qt.ui_select_test_mode_input import Ui_DialogSelectTestModeInput

module_dir_path = os.path.dirname(os.path.abspath(__file__))


class DialogSelectTestModeInput(QDialog, Ui_DialogSelectTestModeInput):
    """Class to allow URL insertion from dialog."""

    def __init__(self):
        super(DialogSelectTestModeInput, self).__init__()
        self.ui = Ui_DialogSelectTestModeInput()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon(os.path.join(module_dir_path, "..", "img", "mainwindow_icon.jpg")))
        self.ui.label_error.setStyleSheet("color: red")
        self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        self.ui.lineEdit_url.setText("https://www.parks.it/tmpFoto/30079_4_PNALM.jpeg") #TODO: remove for 1.0 release
        self.url = ""
        self.file_path = ""

        # Slots
        self.ui.radioButton_image.clicked.connect(self.validate)
        self.ui.radioButton_video.clicked.connect(self.validate)
        self.ui.radioButton_url.clicked.connect(self.validate)
        self.ui.radioButton_file.clicked.connect(self.validate)
        self.ui.radioButton_url.clicked.connect(self.on_input_radio_button_clicked)
        self.ui.radioButton_file.clicked.connect(self.on_input_radio_button_clicked)
        self.ui.lineEdit_url.textChanged.connect(self.validate)
        self.ui.lineEdit_file.textChanged.connect(self.validate)
        self.ui.pushButton_select_file.clicked.connect(self.on_select_file_button_clicked)
        self.ui.buttonBox.accepted.connect(self.accept_and_close)

        self.on_input_radio_button_clicked()
        self.validate() #TODO: remove for 1.0 release

    def on_input_radio_button_clicked(self):
        """Method to handle input method selection via radio buttons"""

        url_checked = self.ui.radioButton_url.isChecked()
        if url_checked:
            self.ui.lineEdit_file.setText("")
        else:
            self.ui.lineEdit_url.setText("")
        self.ui.lineEdit_url.setEnabled(url_checked)
        self.ui.lineEdit_file.setEnabled(not url_checked)
        self.ui.pushButton_select_file.setEnabled(not url_checked)

    def on_select_file_button_clicked(self):
        """Method to select input from file"""

        input_file_type = "image" if self.ui.radioButton_image.isChecked() else "video"
        input_file_extensions = "JPEG (*.jpg *.jpeg);;PNG (*.png);;BMP (*.bmp);;TIFF (*.tiff *.tif)" \
            if self.ui.radioButton_image.isChecked() else\
            "mp4 (*.mp4);;AVI (*.AVI);;MOV (*.mov);;MKV (*.mkv);;WMV (*.wmv)"

        file_name = QFileDialog.getOpenFileName(
            self, f"Open {input_file_type} file", os.getcwd(), input_file_extensions
        )
        self.ui.lineEdit_file.setText(str(file_name[0]))
        self.validate()

    def accept_and_close(self):
        """When Ok is clicked, save url before closing."""
        self.url = self.ui.lineEdit_url.text()
        self.file_path = self.ui.lineEdit_file.text()
        self.accept()

    def is_supported_media(self, url, is_image):
        """Method to validate if given URL embeds correct file format"""

        image_formats = (r'\.(jpg|jpeg|png|bmp|tiff|tif)$')
        video_formats = (r'\.(mp4|avi|mov|mkv|wmv)$')

        if is_image and re.search(image_formats, url, re.IGNORECASE):
            return True
        elif not is_image and re.search(video_formats, url, re.IGNORECASE):
            return True
        else:
            return False

    def validate(self):
        """Method to validate provided input values"""

        is_image = self.ui.radioButton_image.isChecked()
        media_type_str = "image" if is_image else "video"
        if self.ui.radioButton_file.isChecked():
            url = self.ui.lineEdit_file.text()
            is_valid = os.path.isfile(url)
            error_message = "" if is_valid else "Invalid file path provided"
        else:
            # Validate URL
            url = self.ui.lineEdit_url.text()
            is_valid = bool(validators.url(url))
            error_message = "" if is_valid else "Invalid URL provided"
            if is_valid:
                is_supported_format = self.is_supported_media(url, is_image)
                error_message = "" if is_supported_format else f"Invalid {media_type_str} format at provided URL"
                is_valid = is_supported_format

        self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(is_valid)
        self.ui.label_error.setText(error_message)

