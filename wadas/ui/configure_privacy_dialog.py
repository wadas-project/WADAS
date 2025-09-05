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
# Date: 2025-09-01
# Description: FTP server and cameras UI Module

import os

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog

from wadas.domain.operation_mode import OperationMode
from wadas.ui.qt.ui_configure_privacy import Ui_DialogConfigurePrivacy


module_dir_path = os.path.dirname(os.path.abspath(__file__))


class DialogConfigurePrivacy(QDialog, Ui_DialogConfigurePrivacy):
    """Class to configure privacy aspects from dedicated dialog"""
    def __init__(self):
        super(DialogConfigurePrivacy, self).__init__()
        self.ui = Ui_DialogConfigurePrivacy()

        # UI
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon(os.path.join(module_dir_path, "..", "img", "mainwindow_icon.jpg")))

        # Slots
        self.ui.buttonBox.accepted.connect(self.accept_and_close)

        self.initialize_dialog()

    def initialize_dialog(self):
        """Method to initialize dialog with existing values (if any)."""

        self.ui.checkBox_remove_original_image.setChecked(OperationMode.enforce_privacy_remove_original_img)
        self.ui.checkBox_remove_detection_image.setChecked(OperationMode.enforce_privacy_remove_detection_img)
        self.ui.checkBox_remove_classification_image.setChecked(OperationMode.enforce_privacy_remove_classification_img)

    def accept_and_close(self):
        """When Ok is clicked, save FTP config info before closing."""

        OperationMode.enforce_privacy_remove_original_img = self.ui.checkBox_remove_original_image.isChecked()
        OperationMode.enforce_privacy_remove_detection_img = self.ui.checkBox_remove_detection_image.isChecked()
        OperationMode.enforce_privacy_remove_classification_img = self.ui.checkBox_remove_classification_image.isChecked()
        self.accept()