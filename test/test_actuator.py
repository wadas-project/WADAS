import datetime
from queue import Empty

import pytest

from wadas.domain.actuator import Actuator, Command


class DummyActuator(Actuator):
    """Concrete subclass of Actuator for testing."""

    def send_command(self, command: Command):
        self.cmd_queue.put(command)


@pytest.fixture
def actuator():
    return DummyActuator(actuator_id="test_actuator")


def test_actuator_initialization(actuator):
    assert actuator.id == "test_actuator"
    assert actuator.enabled is False
    assert actuator.last_update is None
    assert actuator.stop_thread is False
    assert actuator.cmd_queue.empty()


def test_send_command(actuator):
    cmd = actuator.build_command(
        actuator_id="cmd1", cmd=Actuator.Commands.TEST, time_stamp=datetime.datetime.now()
    )
    actuator.send_command(cmd)
    assert not actuator.cmd_queue.empty()
    queued = actuator.cmd_queue.get()
    assert isinstance(queued, Command)
    assert queued.cmd == "Test"


def test_get_command_with_command(actuator):
    cmd = actuator.build_command(
        actuator_id="cmd2", cmd=Actuator.Commands.TEST, time_stamp=datetime.datetime.now()
    )
    actuator.send_command(cmd)
    command = actuator.get_command()
    assert isinstance(command, Command)
    assert command.cmd == "Test"
    assert actuator.last_update is not None
    assert actuator.cmd_queue.empty()


def test_get_command_without_command(actuator):
    command = actuator.get_command()
    assert command is None
    assert actuator.last_update is not None


def test_get_command_empty_queue(actuator):
    with pytest.raises(Empty):
        actuator.cmd_queue.get(block=False)
