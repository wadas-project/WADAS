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
# Description: QTextEdit module.

import logging

from PySide6 import QtGui
from PySide6.QtCore import QObject, Signal


class QTextEditLogger(logging.Handler):
    """Class to enable logging in QTextEdit widget within mainwindow"""

    class Emitter(QObject):
        log = Signal(str)

    def __init__(self, parent):
        super().__init__()
        self.widget = parent
        self.widget.setReadOnly(True)
        self.widget.ensureCursorVisible()
        self.widget.moveCursor(QtGui.QTextCursor.End)

        self.emitter = QTextEditLogger.Emitter()
        self.emitter.log.connect(self.widget.appendPlainText)

    def emit(self, record):
        msg = self.format(record)
        self.emitter.log.emit(msg)
