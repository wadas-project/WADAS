from unittest.mock import patch

import pytest
from PySide6.QtWidgets import QDialogButtonBox, QLineEdit

from wadas.domain.ftps_server import FTPsServer
from wadas.ui.configure_ftp_cameras_dialog import DialogFTPCameras


@pytest.fixture
def mock_ftp_server_state(monkeypatch):
    """Mock FTP Server state."""
    # Save original state
    original_server = FTPsServer.ftps_server

    # Reset
    FTPsServer.ftps_server = None

    yield

    # Restore
    FTPsServer.ftps_server = original_server


def test_ftp_cameras_dialog_initial_state(qtbot, mock_ftp_server_state, mock_notifier_state):
    """Test initial state of FTP cameras dialog."""
    dialog = DialogFTPCameras()
    qtbot.addWidget(dialog)

    # Check default values
    assert dialog.ui.lineEdit_ip.text() == "0.0.0.0"
    assert dialog.ui.lineEdit_port.text() == "21"

    # Check buttons
    assert dialog.ui.pushButton_stopFTPServer.isEnabled() is False
    assert dialog.ui.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is False


def test_ftp_cameras_dialog_add_camera(qtbot, mock_ftp_server_state, mock_notifier_state):
    """Test adding an FTP camera row."""
    dialog = DialogFTPCameras()
    qtbot.addWidget(dialog)

    # Initially one row is added by __init__
    # We check for widgets
    assert dialog.findChild(QLineEdit, "lineEdit_camera_id_0") is not None

    # Add another camera
    dialog.ui.pushButton_addFTPCamera.click()

    # Row 1 should exist
    assert dialog.findChild(QLineEdit, "lineEdit_camera_id_1") is not None


def test_ftp_cameras_dialog_validation(qtbot, mock_ftp_server_state, mock_notifier_state):
    """Test validation logic enables OK button."""
    dialog = DialogFTPCameras()
    qtbot.addWidget(dialog)

    # Fill valid server info
    dialog.ui.lineEdit_ip.setText("127.0.0.1")
    dialog.ui.lineEdit_port.setText("2121")
    dialog.ui.lineEdit_passive_port_range_start.setText("60000")
    dialog.ui.lineEdit_passive_port_range_end.setText("60010")
    dialog.ui.lineEdit_max_conn.setText("10")
    dialog.ui.lineEdit_max_conn_ip.setText("5")

    # Mock file existence for SSL key/cert and folder
    with patch("os.path.isfile", return_value=True), patch("os.path.isdir", return_value=True):

        dialog.ui.label_key_file_path.setText("key.pem")
        dialog.ui.label_certificate_file_path.setText("cert.pem")
        dialog.ui.label_FTPServer_path.setText("/tmp/ftp")

        # Fill camera info (row 0)
        id_edit = dialog.findChild(QLineEdit, "lineEdit_camera_id_0")
        # There is no username field in add_ftp_camera, only ID and Password
        # The ID is used as username in test_ftp_server
        pass_edit = dialog.findChild(QLineEdit, "lineEdit_password_0")

        id_edit.setText("FTPCam1")
        pass_edit.setText("pass")

        # Trigger validation
        dialog.validate()

        # Check if OK button is enabled
        assert dialog.ui.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is True
