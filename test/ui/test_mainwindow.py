import logging
from unittest.mock import MagicMock

import pytest

from wadas.ui.mainwindow import MainWindow


@pytest.fixture
def mock_mainwindow_dependencies(monkeypatch):
    """Mock dependencies for MainWindow."""
    # Mock QSettings to avoid reading/writing real config
    mock_settings_instance = MagicMock()
    mock_settings_instance.value.return_value = None

    mock_settings_cls = MagicMock()
    mock_settings_cls.return_value = mock_settings_instance
    mock_settings_cls.IniFormat = 1

    monkeypatch.setattr("wadas.ui.mainwindow.QSettings", mock_settings_cls)

    # Mock RotatingFileHandler to avoid creating log files
    mock_file_handler = MagicMock()
    mock_file_handler.level = logging.INFO
    mock_file_handler_cls = MagicMock(return_value=mock_file_handler)
    monkeypatch.setattr("wadas.ui.mainwindow.RotatingFileHandler", mock_file_handler_cls)

    # Mock QTextEditLogger
    mock_text_logger = MagicMock()
    mock_text_logger.level = logging.INFO
    mock_text_logger_cls = MagicMock(return_value=mock_text_logger)
    monkeypatch.setattr("wadas.ui.mainwindow.QTextEditLogger", mock_text_logger_cls)

    # Mock other loggers
    monkeypatch.setattr("wadas.ui.mainwindow.initialize_fpts_logger", MagicMock())
    monkeypatch.setattr("wadas.ui.mainwindow.initialize_asyncio_logger", MagicMock())

    # Mock methods that show dialogs
    monkeypatch.setattr(MainWindow, "show_terms_n_conditions", MagicMock())
    monkeypatch.setattr(MainWindow, "check_wadas_runtime_library_version", MagicMock())

    # Mock keyring
    monkeypatch.setattr("wadas.ui.mainwindow.keyring", MagicMock())


def test_mainwindow_initialization(qtbot, mock_mainwindow_dependencies, mock_notifier_state):
    """Test that MainWindow initializes correctly."""
    window = MainWindow()
    qtbot.addWidget(window)

    # Check title contains version (checking if default_window_title is set correctly)
    assert "WADAS" in window.windowTitle()

    # Check if log widget is present
    assert window.ui.plainTextEdit_log is not None

    # Check if actions are connected
    assert window.ui.actionSelect_Mode is not None


def test_mainwindow_title_update(qtbot, mock_mainwindow_dependencies, mock_notifier_state):
    """Test that setting project name updates the title."""
    window = MainWindow()
    qtbot.addWidget(window)

    window.set_mainwindow_title("MyProject")
    assert "MyProject" in window.windowTitle()


def test_mainwindow_actions_enabled(qtbot, mock_mainwindow_dependencies, mock_notifier_state):
    """Test that certain actions are enabled/disabled by default."""
    window = MainWindow()
    qtbot.addWidget(window)

    # Run/Stop should be disabled/enabled based on state?
    # By default, Run is disabled because no mode is selected.
    assert window.ui.actionRun.isEnabled() is False
    assert window.ui.actionStop.isEnabled() is False
