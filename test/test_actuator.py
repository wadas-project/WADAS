from enum import Enum
from queue import Empty

import pytest

from wadas.domain.actuator import Actuator


class TestEnum(Enum):
    TEST_CMD = "test_command"


@pytest.fixture
def actuator():
    return Actuator(actuator_id="test_actuator")


def test_actuator_initialization(actuator):
    assert actuator.id == "test_actuator"
    assert actuator.enabled is False
    assert actuator.last_update is None
    assert actuator.stop_thread is False
    assert actuator.cmd_queue.empty()


def test_send_command(actuator):
    actuator.send_command(TestEnum.TEST_CMD)
    assert not actuator.cmd_queue.empty()
    assert actuator.cmd_queue.get() == "test_command"


def test_get_command_with_command(actuator):
    actuator.send_command(TestEnum.TEST_CMD)
    command = actuator.get_command()
    assert command == "test_command"
    assert actuator.last_update is not None
    assert actuator.cmd_queue.empty()


def test_get_command_without_command(actuator):
    command = actuator.get_command()
    assert command is None
    assert actuator.last_update is not None


def test_get_command_empty_queue(actuator):
    with pytest.raises(Empty):
        actuator.cmd_queue.get(block=False)
