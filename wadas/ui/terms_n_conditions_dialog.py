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
# Date: 2024-12-27
# Description: Module containing logic to draw the Terms and Conditions dialog.

import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QCheckBox, QDialog, QPushButton, QTextEdit, QVBoxLayout

module_dir_path = os.path.dirname(os.path.abspath(__file__))


class TermsAndConditionsDialog(QDialog):
    """Class to represent TERMS_AND_CONDITIONS_OF_USE file in a QDialog"""
    def __init__(self, terms_accepted=False):
        super().__init__()
        # Acceptance status
        self.terms_accepted = terms_accepted
        # Don't show again Terms and Conditions (if accepted)
        self.dont_show = False

        # UI
        self.setWindowTitle("WADAS Terms and Conditions of use")
        self.setGeometry(150, 150, 500, 400)
        self.setWindowIcon(QIcon(os.path.join(module_dir_path, "..", "img", "mainwindow_icon.jpg")))

        layout = QVBoxLayout()

        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)
        self.text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        layout.addWidget(self.text_edit)

        # Load Terms and Conditions file
        terms_n_conditions_file = os.path.abspath(os.path.join(module_dir_path, "..", ".."))
        terms_n_conditions_file = os.path.join(terms_n_conditions_file, "TERMS_AND_CONDITIONS_OF_USE")
        with open(terms_n_conditions_file) as terms_n_conditions_file:
            license_text = terms_n_conditions_file.read()
            self.text_edit.setPlainText(license_text)

        # Checkbox for "Agree Terms and Conditions"
        self.agree_checkbox = QCheckBox("I have read, understood and accepted Terms and Conditions of Use.")
        self.agree_checkbox.setChecked(self.terms_accepted)
        self.agree_checkbox.clicked.connect(self.on_agree_checkbox_changed)
        layout.addWidget(self.agree_checkbox)

        # Checkbox for "Don't show this again"
        self.dont_show_checkbox = QCheckBox("Don't show this again")
        self.dont_show_checkbox.setEnabled(False)  # Disabled by default as this depend on acceptance
        layout.addWidget(self.dont_show_checkbox)

        close_button = QPushButton("Close", self)
        close_button.clicked.connect(self.on_close)
        layout.addWidget(close_button)

        self.setLayout(layout)
        self.on_agree_checkbox_changed()

    def on_agree_checkbox_changed(self):
        """Method to enable don't show again checkbox"""

        self.dont_show_checkbox.setEnabled(self.agree_checkbox.isChecked())

    def on_close(self):
        """Method to save Terms and Conditions agreement selection."""

        if self.agree_checkbox.isChecked():
            self.terms_accepted = True
            if self.dont_show_checkbox.isChecked():
                self.dont_show = True
        self.accept()