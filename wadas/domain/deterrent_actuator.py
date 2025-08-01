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
# Date: 2024-07-02
# Description: Module containing Deterrent Actuator class and methods.


import json
import logging
from enum import Enum

from wadas.domain.actuation_event import ActuationEvent
from wadas.domain.actuator import Actuator

logger = logging.getLogger(__name__)


class DeterrentActuator(Actuator):
    """Deterrent Actuator, specialization of Actuator."""

    class Commands(Enum):
        ON = json.dumps({"on": True})

    def __init__(self, id, enabled):
        super().__init__(id, enabled)
        self.type = Actuator.ActuatorTypes.DETERRENT

    def send_command(self, cmd):
        """Method to send the specific command to the Actuator superclass."""

        command_sent = False
        if isinstance(cmd, DeterrentActuator.Commands):
            super().send_command(cmd)
            command_sent = True
        else:
            logger.error(
                "Actuator %s with ID %s received an unknown command: %s.",
                self.type,
                self.id,
                cmd,
            )
            raise Exception("Unknown command.")
        return command_sent

    def actuate(self, actuation_event: ActuationEvent):
        """Method to trigger the Deterrent Actuator sending it the ON Command"""

        cmd = self.Commands.ON
        if self.send_command(cmd):
            actuation_event.command = cmd

    def serialize(self):
        """Method to serialize Deterrent Actuator object into file."""

        return {"id": self.id, "enabled": self.enabled, "type": self.type.value}

    @staticmethod
    def deserialize(data):
        """Method to deserialize Actuator object from file."""

        return DeterrentActuator(data["id"], data["enabled"])
