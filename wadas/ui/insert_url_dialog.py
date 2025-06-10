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

import validators
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QDialogButtonBox

from wadas.ui.qt.ui_insert_url import Ui_InsertUrlDialog

module_dir_path = os.path.dirname(os.path.abspath(__file__))


class InsertUrlDialog(QDialog, Ui_InsertUrlDialog):
    """Class to allow URL insertion from dialog."""

    def __init__(self):
        super(InsertUrlDialog, self).__init__()
        self.ui = Ui_InsertUrlDialog()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon(os.path.join(module_dir_path, "..", "img", "mainwindow_icon.jpg")))
        self.url = ""
        self.ui.buttonBox.accepted.connect(self.accept_and_close)
        self.ui.lineEdit_url.textChanged.connect(self.validate_url)
        # TODO: uncomment line below if no URL is provided by default
        # self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

    def accept_and_close(self):
        """When Ok is clicked, save url before closing."""
        self.url = self.ui.lineEdit_url.text()
        self.accept()

    def validate_url(self):
        """Check if inserted URL is valid."""

        url = self.ui.lineEdit_url.text()
        is_validated = bool(validators.url(url))
        self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(is_validated)
