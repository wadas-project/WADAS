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
from typing import Optional

from wadas.domain.actuation_event import ActuationEvent
from wadas.domain.mqtt_broker import MqttBroker

logger = logging.getLogger(__name__)


@dataclass
class Command:
    actuator_id: str
    cmd: str
    response: Optional[bool] = None
    payload: dict = field(default_factory=dict)
    time_stamp: datetime.datetime = field(default_factory=datetime.datetime.now)
    response_timestamp: Optional[datetime.datetime] = None
    response_message: Optional[str] = None

    def to_json(self) -> str:
        return json.dumps(
            {
                "actuator_id": self.actuator_id,
                "cmd": self.cmd,
                "payload": self.payload,
                "time_stamp": self.time_stamp.isoformat(),
                "response": self.response,
                "response_timestamp": (
                    self.response_timestamp.isoformat() if self.response_timestamp else None
                ),
                "response_message": self.response_message,
            }
        )

    @classmethod
    def from_json(cls, s: str) -> "Command":
        """Deserialize command from JSON with ISO timestamp."""
        data = json.loads(s)
        return cls(
            actuator_id=data["actuator_id"],
            cmd=data["cmd"],
            payload=data.get("payload", {}),
            time_stamp=datetime.datetime.fromisoformat(data["time_stamp"]),
            response=data["response"],
            response_timestamp=datetime.datetime.fromisoformat(data["response_timestamp"]),
            response_message=data["response_message"],
        )


@dataclass
class ActuatorBatteryStatus:
    actuator_id: str
    voltage: float
    temperature: float
    humidity: float
    time_stamp: datetime.datetime = field(default_factory=datetime.datetime.now)

    def to_json(self) -> str:
        return json.dumps(
            {
                "actuator_id": self.actuator_id,
                "voltage": self.voltage,
                "time_stamp": self.time_stamp.isoformat(),
                "temperature": self.temperature,
                "humidity": self.humidity,
            }
        )


@dataclass
class ActuatorTemperatureStatus:
    actuator_id: str
    temperature: float
    humidity: float
    time_stamp: datetime.datetime = field(default_factory=datetime.datetime.now)

    def to_json(self) -> str:
        return json.dumps(
            {
                "actuator_id": self.actuator_id,
                "temperature": self.temperature,
                "humidity": self.humidity,
                "time_stamp": self.time_stamp.isoformat(),
            }
        )


class Actuator:
    """Base class of an actuator."""

    actuators = {}
    MQTT_STATUS_TOPIC = "actuators/status"
    MQTT_COMMAND_TOPIC = "actuators/{actuator_id}/command"
    MQTT_RESPONSE_TOPIC = "actuators/{actuator_id}/response"

    class ActuatorTypes(Enum):
        ROADSIGN = "Road Sign"
        FEEDER = "Feeder"
        DETERRENT = "Deterrent"

    class Commands(Enum):
        TEST = "test"
        SEND_LOG = "send_log"
        BATTERY_STATUS = "battery_status"
        TEMPERATURE_STATUS = "temperature_status"
        SHUT_DOWN = "shut_down"

    def __init__(self, actuator_id, enabled=False):
        self.cmd_queue = Queue()
        self.id = actuator_id
        self.last_update = None
        self.enabled = enabled
        self.stop_thread = False
        self.type = None
        self.responses: deque[dict] = deque(maxlen=50)  # Actuator responses FIFO
        self.log = None

    @classmethod
    def build_command(
        self, actuator_id: str, cmd: Commands, time_stamp: datetime, payload: dict = None
    ) -> Command:
        """Factory to create a Command object with unique ID and optional payload."""
        return Command(
            actuator_id=actuator_id, cmd=cmd.value, time_stamp=time_stamp, payload=payload or {}
        )

    @classmethod
    def get_mqtt_status_topic(self):
        return Actuator.MQTT_STATUS_TOPIC

    def get_mqtt_command_topic(self):
        return Actuator.MQTT_COMMAND_TOPIC.format(actuator_id=self.id)

    def get_mqtt_response_topic(self):
        return Actuator.MQTT_RESPONSE_TOPIC.format(actuator_id=self.id)

    def queue_response_command(self, response: dict):
        """Method to insert an actuator response into a dedicated queue"""
        self.responses.append(response)
        self.last_update = datetime.datetime.now()

    def send_command(self, command: Command):
        """Method to insert a command into the actuator queue"""
        # Check that the ID is valid
        if not command.actuator_id or not isinstance(command.actuator_id, str):
            logger.error("Actuator %s received a command without valid ID.", command.actuator_id)
            raise ValueError("Command must have a valid ID (non-empty string).")

        # Check that the command is a valid enum member
        if command.cmd not in {c.value for c in self.Commands}:
            logger.error(
                "Actuator %s with ID %s received an unknown command: %s.",
                self.type,
                command.actuator_id,
                command.cmd,
            )
            raise ValueError("Unknown command.")

        # Publish the command on the appropriate topic
        MqttBroker.broker.publish_message(self.get_mqtt_command_topic(), command.to_json())

        # Return command execution status
        return True

    def get_command(self):
        """Method to get the last command of the queue"""
        self.last_update = datetime.datetime.now()
        try:
            return self.cmd_queue.get(block=False)
        except Empty:
            return None  # if there are no commands, return None

    def update_status(self, obj):
        self.last_update = datetime.datetime.now()

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
