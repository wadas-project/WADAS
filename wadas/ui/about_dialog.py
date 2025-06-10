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
# Description: Module containing logic to show About WADAS info in dedicated dialog.

import os

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QPushButton, QTextBrowser, QVBoxLayout

from wadas._version import __version__

module_dir_path = os.path.dirname(os.path.abspath(__file__))


class AboutDialog(QDialog):
    """Class to show About WADAS info in dedicated dialog."""
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("About WADAS")
        self.setGeometry(150, 150, 500, 300)
        self.setWindowIcon(QIcon(os.path.join(module_dir_path, "..", "img", "mainwindow_icon.jpg")))

        layout = QVBoxLayout()

        about_text = QTextBrowser(self)
        about_text.setReadOnly(True)
        about_text.setText(
            f"""<h2>Wild Animal Detection and Alert System</h2>
            <p>Wild Animal Detection and Alert System (WADAS) is a project for
            AI-based detection and classification wildlife, capable of producing
            notification and actuate remote devices to prevent fatal accidents involving
            wild animals or act as prevention measure to improve animal-to-humans
            coexistence.</p>
            <p>WADAS goal is to protect wildlife. Any misuse causing harm or even death
            of animals is discouraged and forbidden.</p>
            <p>Version: {__version__}</p>
            <p>Developed by: Stefano Dell'Osa,
             Alessandro Palla,
             Antonio Farina,
             Cesare Di Mauro.</p>
            <p>For more information, visit our <a href='https://github.com/stefanodellosa-personal/WADAS'>GitHub</a>.</p>
            """
        )
        about_text.setOpenExternalLinks(True)  # Allow opening links in a browser
        layout.addWidget(about_text)

        close_button = QPushButton("Close", self)
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

        self.setLayout(layout)
