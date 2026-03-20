from unittest.mock import MagicMock

import pytest
from PySide6.QtWidgets import QDialogButtonBox

from wadas.domain.ai_model import AiModel
from wadas.ui.configure_ai_model_dialog import ConfigureAiModel


@pytest.fixture
def mock_ai_model_state(monkeypatch):
    """Mock AiModel state."""
    # Mock class attributes
    monkeypatch.setattr(AiModel, "classification_threshold", 0.5)
    monkeypatch.setattr(AiModel, "detection_threshold", 0.5)
    monkeypatch.setattr(AiModel, "video_fps", 1)
    monkeypatch.setattr(AiModel, "tunnel_mode_detection_threshold", 0.5)
    monkeypatch.setattr(AiModel, "language", "en")
    monkeypatch.setattr(AiModel, "detection_device", "auto")
    monkeypatch.setattr(AiModel, "classification_device", "auto")
    monkeypatch.setattr(AiModel, "classification_model_version", "DFv1.2")

    # Mock txt_animalclasses
    mock_classes = {"DFv1.2": ["en", "it"]}
    monkeypatch.setattr("wadas.ui.configure_ai_model_dialog.txt_animalclasses", mock_classes)

    # Mock openvino
    mock_ov = MagicMock()
    mock_ov.Core.return_value.get_available_devices.return_value = ["CPU", "GPU"]
    monkeypatch.setattr("wadas.ui.configure_ai_model_dialog.ov", mock_ov)


def test_ai_model_dialog_initial_state(qtbot, mock_ai_model_state, mock_notifier_state):
    """Test initial state of AI model dialog."""
    dialog = ConfigureAiModel()
    qtbot.addWidget(dialog)

    # Check default values
    assert dialog.ui.lineEdit_classificationThreshold.text() == "0.5"
    assert dialog.ui.lineEdit_detectionThreshold.text() == "0.5"
    assert dialog.ui.lineEdit_video_fps.text() == "1"

    # Check dropdowns
    assert dialog.ui.comboBox_class_lang.currentText() == "en"
    assert dialog.ui.comboBox_detection_dev.currentText() == "auto"

    # OK button should be enabled if data is valid (default data is valid)
    assert dialog.ui.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is True


def test_ai_model_dialog_validation(qtbot, mock_ai_model_state, mock_notifier_state):
    """Test validation logic."""
    dialog = ConfigureAiModel()
    qtbot.addWidget(dialog)

    # Invalid threshold
    dialog.ui.lineEdit_classificationThreshold.setText("1.5")
    assert dialog.ui.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is False

    # Valid threshold
    dialog.ui.lineEdit_classificationThreshold.setText("0.8")
    assert dialog.ui.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is True

    # Invalid FPS
    dialog.ui.lineEdit_video_fps.setText("-1")
    assert dialog.ui.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is False


def test_ai_model_dialog_save(qtbot, mock_ai_model_state, mock_notifier_state):
    """Test saving configuration."""
    dialog = ConfigureAiModel()
    qtbot.addWidget(dialog)

    # Change values
    dialog.ui.lineEdit_classificationThreshold.setText("0.7")
    dialog.ui.comboBox_class_lang.setCurrentText("it")

    # Accept
    dialog.accept_and_close()

    # Verify AiModel updated
    assert AiModel.classification_threshold == 0.7
    assert AiModel.language == "it"
