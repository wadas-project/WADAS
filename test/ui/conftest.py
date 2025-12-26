# Ensure we can import from wadas
import pathlib
import sys
from unittest.mock import MagicMock

import pytest

sys.path.append(str(pathlib.Path(__file__).parents[2]))

from wadas.domain.notifier import Notifier  # # noqa: E402


@pytest.fixture
def mock_notifier_state(monkeypatch):
    """Mock the global Notifier.notifiers dictionary."""
    # Save original state
    original_notifiers = Notifier.notifiers.copy()

    # Reset for test
    Notifier.notifiers = {
        Notifier.NotifierTypes.EMAIL.value: None,
        Notifier.NotifierTypes.TELEGRAM.value: None,
        Notifier.NotifierTypes.WHATSAPP.value: None,
    }

    yield

    # Restore original state
    Notifier.notifiers = original_notifiers


@pytest.fixture
def mock_keyring(monkeypatch):
    """Mock keyring to avoid system access."""
    mock = MagicMock()
    monkeypatch.setattr("wadas.ui.configure_email_dialog.keyring", mock)
    return mock
