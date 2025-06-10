import json
import os
import tempfile
import time

import pytest
import requests
import util
from fastapi.testclient import TestClient

from wadas.domain.actuator import Actuator
from wadas.domain.actuator_server_app import app
from wadas.domain.fastapi_actuator_server import FastAPIActuatorServer
from wadas.domain.roadsign_actuator import RoadSignActuator

client = TestClient(app)

HTTPS_PORT = 8443


@pytest.fixture
def mock_actuators(monkeypatch):
    class MockActuator:
        def get_command(self):
            return json.dumps({"cmd": "test_string"})

    actuators = {"123": MockActuator()}
    monkeypatch.setattr(Actuator, "actuators", actuators)


@pytest.fixture
def actuator_server():
    temp_dir = tempfile.gettempdir()
    cert_path = os.path.join(temp_dir, "server.pem")
    key_path = os.path.join(temp_dir, "keyserver.pem")
    util.cert_gen(key_path, cert_path)
    return FastAPIActuatorServer(
        "127.0.0.1",
        HTTPS_PORT,
        cert_path,
        key_path,
    )


@pytest.fixture
def actuator():
    actuator = RoadSignActuator(id="123", enabled=True)
    return actuator


def test_get_actuator_command_existing(mock_actuators):
    response = client.get("/api/v1/actuators/123")
    assert response.status_code == 200
    assert response.json() == {"cmd": "test_string"}


def test_get_actuator_command_non_existing(mock_actuators):
    response = client.get("/api/v1/actuators/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Actuator does not exist"}


def test_server_serialize():
    server = FastAPIActuatorServer("127.0.0.1", 443, "mycert.pem", "mykey.pem")
    serialized_data = server.serialize()
    expected_data = {
        "ssl_certificate": "mycert.pem",
        "ssl_key": "mykey.pem",
        "ip": "127.0.0.1",
        "port": 443,
        "actuator_timeout_threshold": 30,
    }
    assert serialized_data == expected_data


def test_server_deserialize():
    data = {
        "ssl_certificate": "mycert.pem",
        "ssl_key": "mykey.pem",
        "ip": "127.0.0.1",
        "port": 443,
        "actuator_timeout_threshold": 30,
    }
    server = FastAPIActuatorServer.deserialize(data)
    assert isinstance(server, FastAPIActuatorServer)
    assert server.ip == "127.0.0.1"
    assert server.port == 443
    assert server.ssl_certificate == "mycert.pem"
    assert server.ssl_key == "mykey.pem"


def test_server_working(actuator_server):
    thread = actuator_server.run()
    assert thread is not None
    time.sleep(3)
    path = app.routes[0].path.format(actuator_id="test_id")
    response = requests.get(f"https://127.0.0.1:{HTTPS_PORT}{path}", verify=False)
    assert response.status_code == 404
    actuator_server.stop()
    thread.join()


def test_actuator_exists(actuator_server, actuator):
    thread = actuator_server.run()
    assert thread is not None
    Actuator.actuators[actuator.id] = actuator
    time.sleep(3)
    path = app.routes[0].path.format(actuator_id=actuator.id)
    response = requests.get(f"https://127.0.0.1:{HTTPS_PORT}{path}", verify=False)
    assert response.status_code == 200
    actuator_server.stop()
    thread.join()


def test_actuator_command(actuator_server, actuator):
    thread = actuator_server.run()
    assert thread is not None
    Actuator.actuators[actuator.id] = actuator
    actuator.send_command(RoadSignActuator.Commands.DISPLAY_ON)
    time.sleep(3)
    path = app.routes[0].path.format(actuator_id=actuator.id)
    response = requests.get(f"https://127.0.0.1:{HTTPS_PORT}{path}", verify=False)
    assert response.status_code == 200
    assert response.json() == json.loads(RoadSignActuator.Commands.DISPLAY_ON.value)
    actuator_server.stop()
    thread.join()


def test_server_restart(actuator_server):
    thread = actuator_server.run()
    assert thread is not None
    time.sleep(3)
    path = app.routes[0].path.format(actuator_id="test_id")
    response = requests.get(f"https://127.0.0.1:{HTTPS_PORT}{path}", verify=False)
    assert response.status_code == 404
    actuator_server.stop()
    thread.join()
    time.sleep(3)
    thread = actuator_server.run()
    assert thread is not None
    time.sleep(3)
    path = app.routes[0].path.format(actuator_id="test_id")
    response = requests.get(f"https://127.0.0.1:{HTTPS_PORT}{path}", verify=False)
    assert response.status_code == 404
    actuator_server.stop()
    thread.join()
