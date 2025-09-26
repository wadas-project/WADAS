import datetime
import json

import pytest

from wadas.domain.actuation_event import ActuationEvent
from wadas.domain.actuator import Command
from wadas.domain.detection_event import DetectionEvent
from wadas.domain.deterrent_actuator import DeterrentActuator
from wadas.domain.utils import get_timestamp


def test_send_command_valid():
    actuator = DeterrentActuator(id="123", enabled=True)
    command = Command(actuator.id, DeterrentActuator.Commands.ON.value)
    actuator.send_command(command)
    # Assuming send_command method has some side effect or state change to verify
    # Here we just check if no exception is raised


def test_send_command_invalid():
    actuator = DeterrentActuator(id="123", enabled=True)
    invalid_command = Command(actuator.id, "INVALID_COMMAND")
    with pytest.raises(Exception) as excinfo:
        actuator.send_command(invalid_command)
    assert "Unknown command" in str(excinfo.value)


def test_actuate():
    detection_event = DetectionEvent(
        "TestCamera",
        get_timestamp(),
        "orig_img_path",
        "detected_img_path",
        detected_animals=None,
        classification=False,
    )
    actuation_event = ActuationEvent("TestActuator", datetime.datetime.now(), detection_event)
    actuator = DeterrentActuator(id="TestActuator", enabled=True)
    actuator.actuate(actuation_event)
    command_json = actuator.get_command()
    command_dict = json.loads(command_json)
    cmd_value = command_dict["cmd"]
    actuator_id = command_dict["actuator_id"]
    assert cmd_value == DeterrentActuator.Commands.ON.value
    assert actuator_id == "TestActuator"


def test_serialize():
    actuator = DeterrentActuator(id="123", enabled=True)
    serialized_data = actuator.serialize()
    expected_data = {
        "type": "Deterrent",
        "id": "123",
        "enabled": True,
    }
    assert serialized_data == expected_data


def test_deserialize():
    data = {
        "id": "123",
        "enabled": True,
    }
    actuator = DeterrentActuator.deserialize(data)
    assert isinstance(actuator, DeterrentActuator)
    assert actuator.id == "123"
    assert actuator.enabled is True
