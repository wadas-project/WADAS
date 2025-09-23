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
import json
import logging
from abc import abstractmethod
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from queue import Empty, Queue

from wadas.domain.actuation_event import ActuationEvent

logger = logging.getLogger(__name__)


@dataclass
class Command:
    id: str
    cmd: str
    payload: dict = field(default_factory=dict)
    time_stamp: datetime.datetime = field(default_factory=datetime.datetime.now)

    def to_json(self) -> str:
        return json.dumps(
            {
                "id": self.id,
                "cmd": self.cmd,
                "payload": self.payload,
                "time_stamp": self.time_stamp.isoformat(),
            }
        )


class Actuator:
    """Base class of an actuator."""

    actuators = {}

    class ActuatorTypes(Enum):
        ROADSIGN = "Road Sign"
        FEEDER = "Feeder"
        DETERRENT = "Deterrent"

    class Commands(Enum):
        TEST = "Test"

    def __init__(self, actuator_id, enabled=False):
        self.cmd_queue = Queue()
        self.id = actuator_id
        self.last_update = None
        self.enabled = enabled
        self.stop_thread = False
        self.type = None
        self.responses: deque[dict] = deque(maxlen=50)  # Actuator responses FIFO

    @classmethod
    def build_command(
        self, id: str, cmd: Commands, time_stamp: datetime, payload: dict = None
    ) -> Command:
        """Factory to create a Command object with unique ID and optional payload."""
        return Command(id=id, cmd=cmd.value, time_stamp=time_stamp, payload=payload or {})

    def queue_response_command(self, response: dict):
        """Method to insert an actuator response into a dedicated queue"""
        self.responses.append(response)
        self.last_update = datetime.datetime.now()

    @abstractmethod
    def send_command(self, command: Command):
        """Method to insert a command into the actuator queue"""

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
