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
# Description: Tests for role-based authorization on the web server, in
# particular the new "Operator" role introduced alongside "Admin"/"Viewer".
"""
Covers:
- The `require_role` helper used to gate endpoints.
- The actuator-related endpoints (/actuators, /actuators/{id}/detail,
  /actuators/{id}/log, /actuators/{id}/test, /actuators/{id}/last_update),
  which must allow both "Admin" and "Operator" and reject "Viewer".
- The /logs endpoint, which must remain "Admin"-only (Operator should NOT
  gain access to it).
"""

from datetime import datetime, timezone

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from wadas_webserver import web_server_app
from wadas_webserver.view_model import User
from wadas_webserver.web_server_app import (
    ACTUATOR_ROLES,
    ADMIN_ONLY_ROLES,
    app,
    require_role,
)

client = TestClient(app)


def make_user(role: str) -> User:
    return User(username="tester", password="unused", email="tester@example.com", role=role)


class TestRequireRoleHelper:
    """Unit tests for the require_role() helper directly."""

    @pytest.mark.parametrize("role", ["Admin", "Operator"])
    def test_allowed_roles_pass(self, role):
        # Should not raise for roles included in the allowed set.
        require_role(make_user(role), ACTUATOR_ROLES)

    def test_disallowed_role_raises_403(self):
        with pytest.raises(HTTPException) as exc_info:
            require_role(make_user("Viewer"), ACTUATOR_ROLES)
        assert exc_info.value.status_code == 403

    def test_admin_only_rejects_operator(self):
        with pytest.raises(HTTPException) as exc_info:
            require_role(make_user("Operator"), ADMIN_ONLY_ROLES)
        assert exc_info.value.status_code == 403

    def test_unknown_role_raises_403(self):
        with pytest.raises(HTTPException) as exc_info:
            require_role(make_user("SomeRandomRole"), ACTUATOR_ROLES)
        assert exc_info.value.status_code == 403


class MockActuator:
    """Minimal stand-in for wadas.domain.actuator.Actuator instances."""

    def __init__(self, actuator_id="cam-1"):
        self.id = actuator_id

        class _Type:
            value = "RoadSign"

        self.type = _Type()
        self.last_update = datetime.now(timezone.utc)
        self.log = ["line1", "line2"]
        self.responses = []
        self.cmd_queue = _FakeQueue()


class _FakeQueue:
    def put_nowait(self, item):
        pass


@pytest.fixture
def mock_actuator(monkeypatch):
    actuator = MockActuator("cam-1")
    monkeypatch.setattr(web_server_app.Actuator, "actuators", {"cam-1": actuator})
    return actuator


@pytest.fixture
def mock_database(monkeypatch):
    class MockDbActuator:
        name = "cam-1"

    class MockDatabase:
        def get_actuators(self):
            return [MockDbActuator()]

        def get_last_battery_status(self, actuator_id):
            return None

        def get_last_temperature_status(self, actuator_id):
            return None

    monkeypatch.setattr(web_server_app.Database, "instance", MockDatabase())
    return MockDatabase()


def override_verify_token(role: str):
    """Patch verify_token to skip JWT/DB lookups and return a fixed-role user."""

    def _verify_token(token, token_type="access"):
        return make_user(role)

    return _verify_token


ACTUATOR_ENDPOINTS_GET = [
    "/api/v1/actuators",
    "/api/v1/actuators/cam-1/detail",
    "/api/v1/actuators/cam-1/last_update",
]
ACTUATOR_ENDPOINTS_POST = [
    "/api/v1/actuators/cam-1/log",
    "/api/v1/actuators/cam-1/test",
]


@pytest.mark.parametrize("role", ["Admin", "Operator"])
@pytest.mark.parametrize("endpoint", ACTUATOR_ENDPOINTS_GET)
def test_actuator_get_endpoints_allow_admin_and_operator(
    monkeypatch, mock_actuator, mock_database, role, endpoint
):
    monkeypatch.setattr(web_server_app, "verify_token", override_verify_token(role))
    response = client.get(endpoint, headers={"x-access-token": "fake"})
    assert response.status_code != 403


def test_actuator_get_endpoints_reject_viewer(monkeypatch, mock_actuator, mock_database):
    monkeypatch.setattr(web_server_app, "verify_token", override_verify_token("Viewer"))
    for endpoint in ACTUATOR_ENDPOINTS_GET:
        response = client.get(endpoint, headers={"x-access-token": "fake"})
        assert response.status_code == 403, f"{endpoint} should reject Viewer role"


@pytest.mark.parametrize("role", ["Admin", "Operator"])
@pytest.mark.parametrize("endpoint", ACTUATOR_ENDPOINTS_POST)
def test_actuator_post_endpoints_allow_admin_and_operator(
    monkeypatch, mock_actuator, mock_database, role, endpoint
):
    monkeypatch.setattr(web_server_app, "verify_token", override_verify_token(role))
    response = client.post(endpoint, headers={"x-access-token": "fake"})
    # These endpoints poll for an actuator response and will time out (504)
    # in this test since no real actuator answers; what matters here is that
    # the role check itself does not reject the request (no 403).
    assert response.status_code != 403


def test_actuator_post_endpoints_reject_viewer(monkeypatch, mock_actuator, mock_database):
    monkeypatch.setattr(web_server_app, "verify_token", override_verify_token("Viewer"))
    for endpoint in ACTUATOR_ENDPOINTS_POST:
        response = client.post(endpoint, headers={"x-access-token": "fake"})
        assert response.status_code == 403, f"{endpoint} should reject Viewer role"


@pytest.mark.parametrize("role", ["Admin"])
def test_logs_endpoint_allows_admin(monkeypatch, role):
    monkeypatch.setattr(web_server_app, "verify_token", override_verify_token(role))
    response = client.get("/api/v1/logs", headers={"x-access-token": "fake"})
    # Admin should pass the role check (a 404 here just means no log file
    # exists in this test environment, which is fine).
    assert response.status_code != 403


@pytest.mark.parametrize("role", ["Operator", "Viewer"])
def test_logs_endpoint_rejects_non_admin(monkeypatch, role):
    """Operator must NOT inherit access to admin-only endpoints like /logs."""
    monkeypatch.setattr(web_server_app, "verify_token", override_verify_token(role))
    response = client.get("/api/v1/logs", headers={"x-access-token": "fake"})
    assert response.status_code == 403
