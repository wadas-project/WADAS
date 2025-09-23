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

import logging
from enum import Enum

from wadas.domain.actuation_event import ActuationEvent
from wadas.domain.actuator import Actuator, Command

logger = logging.getLogger(__name__)


class DeterrentActuator(Actuator):
    """Deterrent Actuator, specialization of Actuator."""

    class Commands(Enum):
        ON = "on"
        SEND_LOG = "send_log"
        TEST = "test"

    def __init__(self, id, enabled):
        super().__init__(id, enabled)
        self.type = Actuator.ActuatorTypes.DETERRENT

    def send_command(self, command: Command):
        """Send command to actuator queue with unique ID."""

        # Check that the ID is valid
        if not command.id or not isinstance(command.id, str):
            logger.error("Actuator %s received a command without valid ID.", command.id)
            raise ValueError("Command must have a valid ID (non-empty string).")

        # Check that the command is a valid enum member
        if command.cmd not in {c.value for c in DeterrentActuator.Commands}:
            logger.error(
                "Actuator %s with ID %s received an unknown command: %s.",
                self.type,
                command.id,
                command.cmd,
            )
            raise ValueError("Unknown command.")

        # Insert command in queue
        self.cmd_queue.put(command.to_json())

        # Return command execution status
        return True

    def actuate(self, actuation_event: ActuationEvent):
        """Method to trigger the Deterrent Actuator sending it the ON Command"""

        command = Actuator.build_command(
            actuation_event.actuator_id, DeterrentActuator.Commands.ON, actuation_event.time_stamp
        )
        if self.send_command(command):
            actuation_event.command = command.cmd

    def serialize(self):
        """Method to serialize Deterrent Actuator object into file."""

        return {"id": self.id, "enabled": self.enabled, "type": self.type.value}

    @staticmethod
    def deserialize(data):
        """Method to deserialize Actuator object from file."""

        return DeterrentActuator(data["id"], data["enabled"])
