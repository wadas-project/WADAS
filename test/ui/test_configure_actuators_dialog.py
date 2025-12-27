from unittest.mock import patch

import pytest
from PySide6.QtWidgets import QComboBox, QDialogButtonBox, QLineEdit

from wadas.domain.actuator import Actuator
from wadas.domain.fastapi_actuator_server import FastAPIActuatorServer
from wadas.ui.configure_actuators_dialog import DialogConfigureActuators


@pytest.fixture
def mock_actuator_state(monkeypatch):
    """Mock Actuator and Server state."""
    # Save original state
    original_actuators = Actuator.actuators.copy()
    original_server = FastAPIActuatorServer.actuator_server

    # Reset
    Actuator.actuators = []
    FastAPIActuatorServer.actuator_server = None

    yield

    # Restore
    Actuator.actuators = original_actuators
    FastAPIActuatorServer.actuator_server = original_server


def test_actuators_dialog_initial_state(qtbot, mock_actuator_state, mock_notifier_state):
    """Test initial state of actuators dialog."""
    dialog = DialogConfigureActuators()
    qtbot.addWidget(dialog)

    # Check default values
    assert dialog.ui.lineEdit_server_ip.text() == "0.0.0.0"
    assert dialog.ui.lineEdit_server_port.text() == "8443"

    # Check buttons
    assert dialog.ui.pushButton_stop_server.isEnabled() is False
    assert dialog.ui.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is False


def test_actuators_dialog_add_actuator(qtbot, mock_actuator_state, mock_notifier_state):
    """Test adding an actuator row."""
    dialog = DialogConfigureActuators()
    qtbot.addWidget(dialog)

    # Initially one row is added by __init__
    # grid = dialog.findChild(QGridLayout, "gridLayout_actuators")
    # We can't easily count rows in QGridLayout, but we can check if widgets exist
    # Row 0 should exist
    assert dialog.findChild(QComboBox, "comboBox_actuator_type_0") is not None

    # Add another actuator
    dialog.ui.pushButton_add_actuator.click()

    # Row 1 should exist
    assert dialog.findChild(QComboBox, "comboBox_actuator_type_1") is not None


def test_actuators_dialog_validation(qtbot, mock_actuator_state, mock_notifier_state):
    """Test validation logic enables OK button."""
    dialog = DialogConfigureActuators()
    qtbot.addWidget(dialog)

    # Fill valid server info
    dialog.ui.lineEdit_server_ip.setText("127.0.0.1")
    dialog.ui.lineEdit_server_port.setText("8080")
    dialog.ui.lineEdit_actuator_timeout.setText("10")

    # Fill actuator info (row 0)
    # We need to find the widgets dynamically created
    # Based on code: lineEdit_actuator_id_{row}
    id_edit = dialog.findChild(QLineEdit, "lineEdit_actuator_id_0")

    # Ensure widgets are visible and active before interaction
    dialog.show()
    # qtbot.waitForWindowShown(dialog) # Deprecated

    # Mock file existence for SSL key/cert
    with patch("os.path.isfile", return_value=True):
        # Set valid file paths (mocked)
        dialog.ui.label_key_file.setText("key.pem")
        dialog.ui.label_cert_file.setText("cert.pem")

        # Set ID
        id_edit.setText("Actuator1")

        # Trigger validation
        dialog.validate()

        # Check if OK button is enabled
        assert dialog.ui.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is True

    # Check if OK button is enabled
    # Note: validation might require more fields or specific conditions
    # Let's check the validate method in code if possible, or just assert
    assert dialog.ui.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is True
