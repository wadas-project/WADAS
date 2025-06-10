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
# Date: 2024-10-20
# Description: Actuator module

import datetime
import logging
from abc import abstractmethod
from enum import Enum
from queue import Empty, Queue

from wadas.domain.actuation_event import ActuationEvent

logger = logging.getLogger(__name__)


class Actuator:
    """Base class of an actuator."""

    actuators = {}

    class ActuatorTypes(Enum):
        ROADSIGN = "Road Sign"
        FEEDER = "Feeder"

    def __init__(self, actuator_id, enabled=False):
        self.cmd_queue = Queue()
        self.id = actuator_id
        self.last_update = None
        self.enabled = enabled
        self.stop_thread = False
        self.type = None

    def send_command(self, cmd: Enum):
        """Method to insert a command into the actuator queue"""

        self.cmd_queue.put(cmd.value)

    def get_command(self):
        """Method to get the last command of the queue"""
        self.last_update = datetime.datetime.now()
        try:
            return self.cmd_queue.get(block=False)
        except Empty:
            return None  # if there are no commands, return None

    @abstractmethod
    def actuate(self, actuation_event: ActuationEvent):
        """Method to trigger the actuator sending the appropriate command"""
        pass

    @abstractmethod
    def serialize(self):
        """Method to serialize Actuator object into file."""
        pass

    @staticmethod
    def deserialize(data):
        """Method to deserialize Actuator object from file."""
        pass
