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
# Date: 2024-14-08
# Description: Method containing logic to build a video steam test dialog.

import os

from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QLabel
from PySide6.QtGui import QImage, QPixmap, QIcon
from PySide6.QtCore import Slot

from wadas.domain.motion_detection import MotionDetectionThread

module_dir_path = os.path.dirname(os.path.abspath(__file__))


class MotionDetectionDialog(QDialog):
    """QDialog to preview motion detection video."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Motion Detection Test Dialog")
        self.setWindowIcon(QIcon(os.path.join(module_dir_path, "..", "img", "mainwindow_icon.jpg")))
        self.setGeometry(100, 100, 640, 480)

        # Layout
        self.layout = QVBoxLayout(self)

        # Video display label
        self.video_label = QLabel(self)
        self.video_label.setText("Starting video stream...")
        self.video_label.setStyleSheet("background-color: black;")
        self.video_label.setFixedSize(640, 480)
        self.layout.addWidget(self.video_label)

        # Stop button
        self.stop_button = QPushButton("Stop Motion Detection Test", self)
        self.stop_button.clicked.connect(self.stop_motion_detection)
        self.layout.addWidget(self.stop_button)

        # Motion detection thread
        self.motion_thread = MotionDetectionThread()
        self.motion_thread.frame_ready.connect(self.update_frame)
        self.motion_thread.start()

    @Slot(QImage)
    def update_frame(self, q_image):
        self.video_label.setPixmap(QPixmap.fromImage(q_image))

    def stop_motion_detection(self):
        self.motion_thread.stop()
        self.close()