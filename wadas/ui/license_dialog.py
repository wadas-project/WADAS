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
# Date: 2024-11-28
# Description: Module containing logic to draw license dialog.

import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QPushButton, QTextEdit, QVBoxLayout

module_dir_path = os.path.dirname(os.path.abspath(__file__))


class LicenseDialog(QDialog):
    """Class to represent LICENSE file in a QDialog"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("License")
        self.setGeometry(150, 150, 450, 400)
        self.setWindowIcon(QIcon(os.path.join(module_dir_path, "..", "img", "mainwindow_icon.jpg")))

        layout = QVBoxLayout()

        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)
        self.text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        layout.addWidget(self.text_edit)

        # Load license file
        license_dir = os.path.abspath(os.path.join(module_dir_path, "..", ".."))
        license_path = os.path.join(license_dir, "LICENSE")
        with open(license_path) as license_file:
            license_text = license_file.read()
            self.text_edit.setPlainText(license_text)

        close_button = QPushButton("Close", self)
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)

        self.setLayout(layout)