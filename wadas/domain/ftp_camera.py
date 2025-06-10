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
# Date: 2024-10-01
# Description: FTP Camera module

import logging

from wadas.domain.actuator import Actuator
from wadas.domain.camera import Camera

logger = logging.getLogger(__name__)


class FTPCamera(Camera):
    """FTP Camera class, specialization of Camera class."""

    def __init__(self, id, ftp_folder, enabled=True, actuators=None):
        if actuators is None:
            actuators = []
        super().__init__(id, enabled)
        # NOTE: Camera ID is also FTP user
        self.type = Camera.CameraTypes.FTP_CAMERA
        self.ftp_folder = ftp_folder
        self.actuators = actuators

    def serialize(self):
        """Method to serialize FTP Camera object into file."""
        actuators = [actuator.id for actuator in self.actuators]
        return {
            "type": self.type.value,
            "id": self.id,
            "ftp_folder": self.ftp_folder,
            "enabled": self.enabled,
            "actuators": actuators,
        }

    @staticmethod
    def deserialize(data):
        """Method to deserialize FTP Camera object from file."""

        actuators = (
            [Actuator.actuators[key] for key in data["actuators"]] if "actuators" in data else []
        )
        return FTPCamera(data["id"], data["ftp_folder"], data["enabled"], actuators)
