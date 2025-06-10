import pytest

from wadas.domain.actuation_event import ActuationEvent
from wadas.domain.detection_event import DetectionEvent
from wadas.domain.feeder_actuator import FeederActuator
from wadas.domain.utils import get_timestamp


def test_send_command_valid():
    actuator = FeederActuator(id="123", enabled=True)
    command = FeederActuator.Commands.CLOSE
    actuator.send_command(command)
    # Assuming send_command method has some side effect or state change to verify
    # Here we just check if no exception is raised


def test_send_command_invalid():
    actuator = FeederActuator(id="123", enabled=True)
    invalid_command = "INVALID_COMMAND"
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
    actuation_event = ActuationEvent("TestActuator", get_timestamp(), detection_event)
    actuator = FeederActuator(id="123", enabled=True)
    actuator.actuate(actuation_event)
    assert actuator.get_command() == FeederActuator.Commands.CLOSE.value


def test_serialize():
    actuator = FeederActuator(id="123", enabled=True)
    serialized_data = actuator.serialize()
    expected_data = {
        "type": "Feeder",
        "id": "123",
        "enabled": True,
    }
    assert serialized_data == expected_data


def test_deserialize():
    data = {
        "id": "123",
        "enabled": True,
    }
    actuator = FeederActuator.deserialize(data)
    assert isinstance(actuator, FeederActuator)
    assert actuator.id == "123"
    assert actuator.enabled is True
