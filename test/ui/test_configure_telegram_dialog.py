from unittest.mock import MagicMock, patch

import pytest
from PySide6.QtWidgets import QDialogButtonBox

from wadas.domain.notifier import Notifier
from wadas.domain.telegram_notifier import TelegramNotifier
from wadas.ui.configure_telegram_dialog import DialogConfigureTelegram


@pytest.fixture
def mock_telegram_notifier(monkeypatch):
    """Mock TelegramNotifier to avoid network calls."""
    mock_notifier = MagicMock(spec=TelegramNotifier)
    mock_notifier.recipients = []
    mock_notifier.enabled = False
    mock_notifier.allow_images = False

    # Mock methods
    mock_notifier.set_org_code = MagicMock()
    mock_notifier.set_node_id = MagicMock()

    # When Notifier.notifiers is accessed, return this mock
    # But the dialog code does: Notifier.notifiers[...] = TelegramNotifier(...) if not exists
    # So we need to mock the class instantiation or pre-fill the dictionary

    return mock_notifier


def test_telegram_dialog_initial_state(qtbot, mock_notifier_state, mock_keyring):
    """Test that the dialog initializes correctly."""
    # Pre-fill notifier to avoid real instantiation
    mock_tn = MagicMock(spec=TelegramNotifier)
    mock_tn.recipients = []
    mock_tn.enabled = False
    mock_tn.allow_images = False
    Notifier.notifiers[Notifier.NotifierTypes.TELEGRAM.value] = mock_tn

    dialog = DialogConfigureTelegram()
    qtbot.addWidget(dialog)

    # Check initial state
    assert dialog.ui.pushButton_remove_receiver.isEnabled() is False
    assert dialog.ui.pushButton_test_message.isEnabled() is False
    # OK button is disabled initially? Code says:
    # self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
    assert dialog.ui.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is False


def test_telegram_dialog_enable_ok(qtbot, mock_notifier_state, mock_keyring):
    """Test that OK button is enabled when settings change."""
    # Pre-fill notifier
    mock_tn = MagicMock(spec=TelegramNotifier)
    mock_tn.recipients = []
    mock_tn.enabled = False
    mock_tn.allow_images = False
    Notifier.notifiers[Notifier.NotifierTypes.TELEGRAM.value] = mock_tn

    dialog = DialogConfigureTelegram()
    qtbot.addWidget(dialog)

    # Initially OK is disabled
    assert dialog.ui.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is False

    # Change checkbox state should enable OK button
    # The dialog connects stateChanged to enable_ok_button
    dialog.ui.checkBox_enable_telegram_notifications.setChecked(True)

    # Check if OK button is enabled
    assert dialog.ui.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is True


def test_telegram_dialog_add_receiver(qtbot, mock_notifier_state, mock_keyring):
    """Test adding a receiver (mocking the worker)."""
    mock_tn = MagicMock(spec=TelegramNotifier)
    mock_tn.recipients = []
    mock_tn.enabled = False
    mock_tn.allow_images = False
    Notifier.notifiers[Notifier.NotifierTypes.TELEGRAM.value] = mock_tn

    dialog = DialogConfigureTelegram()
    qtbot.addWidget(dialog)

    # Mock the worker thread to avoid real network call
    with patch("wadas.ui.configure_telegram_dialog.AddReceiverWorker") as MockWorker:
        mock_worker_instance = MockWorker.return_value

        # Trigger add receiver
        dialog.ui.pushButton_add_receiver.click()

        # Verify worker was started
        assert mock_worker_instance.start.called
