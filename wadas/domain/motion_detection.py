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
# Description: Module containing logic to instantiate a Motion Detection thread to
# process video stream integrated with Qt UI.


import time

import cv2
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage

from wadas.domain.camera import Camera


class MotionDetectionThread(QThread):
    """Motion Detection QThread to integrate cv video stream into Qt Dialog"""

    frame_ready = Signal(QImage)

    def __init__(self, camera_index=0, parent=None):
        super().__init__(parent)
        self.running = False
        self.camera_index = camera_index

    def run(self):
        self.running = True
        cap = cv2.VideoCapture(self.camera_index)

        if not cap.isOpened():
            print("Error: Unable to open camera.")
            return

        background_sub = cv2.createBackgroundSubtractorMOG2()
        min_contour_area = Camera.detection_params["min_contour_area"]
        while self.running:
            ret, frame = cap.read()
            if not ret:
                break

            # Apply background subtraction
            foreground_mask = background_sub.apply(frame)
            contours, _ = cv2.findContours(
                foreground_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            for cnt in contours:
                if cv2.contourArea(cnt) > min_contour_area:
                    x, y, w, h = cv2.boundingRect(cnt)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

            # Convert frame to QImage
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, channel = frame_rgb.shape
            bytes_per_line = 3 * width
            q_image = QImage(frame_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)

            self.frame_ready.emit(q_image)

            time.sleep(0.03)  # Simulate ~30 FPS

        cap.release()

    def stop(self):
        self.running = False
        self.wait()
