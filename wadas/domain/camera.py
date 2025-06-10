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
# Description: Camera base class module

import logging
from abc import abstractmethod
from enum import Enum
from queue import Queue

logger = logging.getLogger(__name__)
# Queue containing all the images received by Cameras to be processed by AiModel
img_queue = Queue()
# List of Cameras selected by user for image processing
cameras = []


class Camera:
    """Base class of a camera."""

    detection_params = {
        "threshold": 180,
        "min_contour_area": 300,
        "detection_per_second": 1,
        "ms_sample_rate": 1000,
    }

    class CameraTypes(Enum):
        USB_CAMERA = "USB Camera"
        FTP_CAMERA = "FTP Camera"

    def __init__(self, id, enabled=False):
        self.type = None
        self.id = id
        self.enabled = enabled
        self.stop_thread = False
        self.actuators = []

    @abstractmethod
    def serialize(self):
        """Method to serialize Camera object into file."""

    @staticmethod
    def deserialize(data):
        """Method to deserialize Camera object from file."""
