from unittest.mock import MagicMock, patch

import pytest
from PySide6.QtWidgets import QCheckBox, QDialogButtonBox, QLineEdit

from wadas.ui.select_usb_cameras_dialog import DialogSelectLocalCameras


@pytest.fixture
def mock_usb_cameras(monkeypatch):
    """Mock enumerate_cameras."""
    mock_cam1 = MagicMock()
    mock_cam1.index = 0
    mock_cam1.name = "Camera 1"
    mock_cam1.vid = 1234
    mock_cam1.pid = 5678

    mock_cam2 = MagicMock()
    mock_cam2.index = 1
    mock_cam2.name = "Camera 2"
    mock_cam2.vid = 4321
    mock_cam2.pid = 8765

    monkeypatch.setattr(
        "wadas.ui.select_usb_cameras_dialog.enumerate_cameras", lambda x: [mock_cam1, mock_cam2]
    )

    # Mock cv2
    monkeypatch.setattr("wadas.ui.select_usb_cameras_dialog.cv2", MagicMock())


def test_usb_cameras_dialog_initial_state(qtbot, mock_usb_cameras, mock_notifier_state):
    """Test initial state of USB cameras dialog."""
    dialog = DialogSelectLocalCameras()
    qtbot.addWidget(dialog)

    # Check if cameras are listed
    # We look for checkboxes dynamically created
    cb0 = dialog.findChild(QCheckBox, "checkBox_camera_0")
    cb1 = dialog.findChild(QCheckBox, "checkBox_camera_1")

    assert cb0 is not None
    assert cb1 is not None

    # OK button disabled initially (no camera selected)
    assert dialog.ui.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is False


def test_usb_cameras_dialog_selection(qtbot, mock_usb_cameras, mock_notifier_state):
    """Test selecting a camera enables OK button."""
    dialog = DialogSelectLocalCameras()
    qtbot.addWidget(dialog)

    cb0 = dialog.findChild(QCheckBox, "checkBox_camera_0")

    # Select camera
    cb0.setChecked(True)

    # We also need to provide a WADAS ID for the camera to be valid?
    # Let's check the code. validate_cameras_selection checks if
    # at least one camera is selected AND has an ID.

    # Correct object name is lineEdit_cameraID_{index} (case sensitive)
    id_edit = dialog.findChild(QLineEdit, "lineEdit_cameraID_0")
    id_edit.setText("Cam1")

    # Trigger validation
    # The dialog connects checkStateChanged and textChanged to validate_cameras_selection
    # But we might need to trigger it manually or ensure signals are processed

    # Check if OK button is enabled
    assert dialog.ui.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is True


def test_usb_cameras_dialog_save(qtbot, mock_usb_cameras, mock_notifier_state):
    """Test saving selected cameras."""
    # Mock global cameras list
    with patch("wadas.ui.select_usb_cameras_dialog.cameras", []) as mock_cameras_list:
        dialog = DialogSelectLocalCameras()
        qtbot.addWidget(dialog)

        cb0 = dialog.findChild(QCheckBox, "checkBox_camera_0")
        id_edit = dialog.findChild(QLineEdit, "lineEdit_cameraID_0")

        cb0.setChecked(True)
        id_edit.setText("Cam1")

        dialog.accept_and_close()

        # Verify camera added to list
        # The logic in accept_and_close iterates over ALL enumerated cameras and adds them
        # to the list if the list was empty.
        # Since we mocked 2 cameras in enumerate_cameras, both are added.
        assert len(mock_cameras_list) == 2

        # Check the first one (which we modified)
        assert mock_cameras_list[0].id == "Cam1"
        assert mock_cameras_list[0].enabled is True

        # Check the second one (default)
        assert mock_cameras_list[1].id == ""
        assert mock_cameras_list[1].enabled is False
