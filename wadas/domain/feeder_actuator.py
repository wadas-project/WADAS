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
# Date: 2024-10-23
# Description: Module containing Feeder Actuator class and methods.


import json
import logging
from enum import Enum

from wadas.domain.actuation_event import ActuationEvent
from wadas.domain.actuator import Actuator

logger = logging.getLogger(__name__)


class FeederActuator(Actuator):
    """FeederActuator, specialization of Actuator."""

    class Commands(Enum):
        OPEN = json.dumps({"open": True})
        CLOSE = json.dumps({"close": True})

    def __init__(self, id, enabled):
        super().__init__(id, enabled)
        self.type = Actuator.ActuatorTypes.FEEDER

    def send_command(self, cmd):
        """Method to send the specific command to the Actuator superclass."""

        command_sent = False
        if isinstance(cmd, FeederActuator.Commands):
            super().send_command(cmd)
            command_sent = True
        else:
            logger.error(
                "Actuator %s with ID %s received an unknown command: %s.",
                self.type,
                self.id,
                cmd,
            )
            raise Exception("Unknown command")
        return command_sent

    def actuate(self, actuation_event: ActuationEvent):
        """Method to trigger the FeederActuator sending it the CLOSE Command"""

        cmd = self.Commands.CLOSE
        if self.send_command(cmd):
            actuation_event.command = cmd

    def serialize(self):
        """Method to serialize Actuator object into file."""
        return {"id": self.id, "enabled": self.enabled, "type": self.type.value}

    @staticmethod
    def deserialize(data):
        """Method to deserialize Actuator object from file."""
        return FeederActuator(data["id"], data["enabled"])
