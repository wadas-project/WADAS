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
# Description: """Main of WADAS application.

import platform
import sys

from PySide6.QtWidgets import QApplication

from wadas.ui.mainwindow import MainWindow


def main():
    """Main function to lunch mainwindow."""

    app = QApplication(sys.argv)
    system = platform.system()
    if system == "Windows":
        # Force style to avoid Win 11 issue with disabled icons not grayed out.
        app.setStyle("fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
