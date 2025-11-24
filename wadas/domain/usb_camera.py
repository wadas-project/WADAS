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
# Description: USB Camera module


import logging
import os
import threading
import time

import cv2

from wadas.domain.actuator import Actuator
from wadas.domain.camera import Camera, media_queue
from wadas.domain.utils import get_timestamp

logger = logging.getLogger(__name__)


class USBCamera(Camera):
    """USB Camera class, specialization of Camera class."""

    def __init__(
        self,
        id,
        name="",
        enabled=False,
        index=None,
        backend=None,
        en_mot_det=False,
        pid="",
        vid="",
        path="",
        actuators=None,
    ):
        if actuators is None:
            actuators = []
        super().__init__(id)
        self.type = Camera.CameraTypes.USB_CAMERA
        self.name = name
        self.enabled = enabled
        self.index = int(index)
        self.backend = int(backend)
        self.en_wadas_motion_detection = en_mot_det
        self.pid = pid
        self.vid = vid
        self.path = path
        self.actuators = actuators

    def detect_motion_from_video(self):
        """Method to run motion detection on camera video stream.
        Only for cameras that are note povided with commercial motion detection feature."""

        logger.info("Starting motion detection for camera %s.", self.id)

        if self.index is None or self.backend is None:
            logger.error("Missing required camera info.")
            return

        # Following motion detection is a simple one aiming to enable functionalities in WADAS.
        # TODO: leverage University support to improve motion detection efficiency.

        cap = cv2.VideoCapture(self.index, self.backend)

        # Check if camera opened successfully
        if not cap.isOpened():
            logger.error("Error opening video stream.")
            return

        # Create Background Subtractor MOG2 object
        background_sub = cv2.createBackgroundSubtractorMOG2()

        # Camera info for debug mode
        length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        logger.debug(
            "Length: %.2f | Width: %.2f | Height: %.2f | Fps: %.2f",
            length,
            width,
            height,
            fps,
        )

        last_detection_time = 0
        ms_sample_rate = Camera.detection_params["ms_sample_rate"]
        threshold = Camera.detection_params["threshold"]
        min_contour_area = Camera.detection_params["min_contour_area"]
        detection_per_second = Camera.detection_params["detection_per_second"]

        # Read until video is completed
        while cap.isOpened() and not self.stop_thread:
            # Capture frame-by-frame
            ret, frame = cap.read()
            cap.set(cv2.CAP_PROP_POS_MSEC, ms_sample_rate)

            if ret:
                # Apply background subtraction
                foreground_mask = background_sub.apply(frame)

                # apply global threshold to remove shadows
                retval, mask_thresh = cv2.threshold(
                    foreground_mask,
                    threshold,
                    255,
                    cv2.THRESH_BINARY,
                )

                """TODO: check if following interpolation helps refine the motion detection
                # set the kernal
                kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
                # Apply erosion
                # mask_eroded = cv2.morphologyEx(mask_thresh, cv2.MORPH_OPEN, kernel)"""

                # Find contours
                contours, hierarchy = cv2.findContours(
                    mask_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
                )

                # filtering contours using list comprehension
                approved_contours = [
                    cnt for cnt in contours if cv2.contourArea(cnt) > min_contour_area
                ]
                frame_out = frame.copy()
                if len(approved_contours) > 0:
                    # Limit the amount of frame processed per second
                    current_detection_time = time.time()
                    if (current_detection_time - last_detection_time) < detection_per_second:
                        continue

                    logger.debug("Motion detected from camera %s!", self.id)
                    last_detection_time = current_detection_time

                    # Adding detected image into the AI queue for animal detection
                    img_path = os.path.join(
                        "wadas_motion_detection",
                        f"camera_{self.id}_{get_timestamp()}.jpg",
                    )
                    cv2.imwrite(img_path, frame_out)
                    media_queue.put(
                        {
                            "media_path": img_path,
                            "media_id": f"camera_{self.id}_{get_timestamp()}.jpg",
                            "camera_id": self.id,
                        }
                    )
            else:
                break

        # When everything done, release the video capture and writer object
        cap.release()

    def run(self):
        """Method to create new thread for Camera class."""

        thread = None
        if self.en_wadas_motion_detection:
            logger.debug("Instantiating motion detection thread for camera %s", self.id)
            thread = threading.Thread(target=self.detect_motion_from_video)
        else:
            logger.error("Misconfigured Camera!")
            return

        if thread:
            thread.start()
            logger.info("Starting thread for camera %s", self.id)
        else:
            logger.error("Unable to create new thread for camera %s", self.id)

        return thread

    def serialize(self):
        """Method to serialize USB Camera object into file."""
        actuators = [actuator.id for actuator in self.actuators]
        return {
            "type": self.type.value,
            "id": self.id,
            "name": self.name,
            "enabled": self.enabled,
            "index": self.index,
            "backend": self.backend,
            "enable_mot_det": self.en_wadas_motion_detection,
            "pid": self.pid,
            "vid": self.vid,
            "path": self.path,
            "actuators": actuators,
        }

    @staticmethod
    def deserialize(data):
        """Method to deserialize USB Camera object from file."""
        actuators = (
            [Actuator.actuators[key] for key in data["actuators"]] if "actuators" in data else []
        )
        return USBCamera(
            data["id"],
            data["name"],
            data["enabled"],
            data["index"],
            data["backend"],
            data["enable_mot_det"],
            data["pid"],
            data["vid"],
            data["path"],
            actuators,
        )
