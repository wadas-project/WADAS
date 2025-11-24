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
# Description: Tunnel base class module

import logging

from wadas.ai.object_counter import TrackingRegion

logger = logging.getLogger(__name__)


class Tunnel:
    """Class to represent tunnels object."""

    # List of Tunnel objects
    tunnels = []

    def __init__(
        self,
        id,
        camera_entrance_1,
        camera_entrance_2,
        entrance_1_direction=TrackingRegion.DOWN,
        entrance_2_direction=TrackingRegion.DOWN,
        enabled=True,
    ):
        self.id = id
        self.camera_entrance_1 = camera_entrance_1
        self.entrance_1_direction = entrance_1_direction
        self.camera_entrance_2 = camera_entrance_2
        self.entrance_2_direction = entrance_2_direction
        self.enabled = enabled
        self.counter = 0

    @classmethod
    def tunnel_exists(cls, tunnel):
        """Method to check whether a tunnel is already in the list"""

        return any(cur_tunnel.id == tunnel.id for cur_tunnel in cls.tunnels)

    def serialize(self):
        """Method to serialize Tunnel object into file."""

        return {
            "id": self.id,
            "camera_entrance_1": self.camera_entrance_1,
            "camera_entrance_2": self.camera_entrance_2,
            "entrance_1_direction": self.entrance_1_direction.value,
            "entrance_2_direction": self.entrance_2_direction.value,
            "enabled": self.enabled,
        }

    @staticmethod
    def deserialize(data):
        """Method to deserialize Tunnel object from file."""

        return Tunnel(
            data["id"],
            data["camera_entrance_1"],
            data["camera_entrance_2"],
            TrackingRegion.get_tracking_region(data["entrance_1_direction"]),
            TrackingRegion.get_tracking_region(data["entrance_2_direction"]),
            data["enabled"],
        )
