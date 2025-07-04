import pytest

from wadas.domain.telegram_notifier import TelegramNotifier
from wadas.domain.telegram_recipient import TelegramRecipient


@pytest.fixture
def telegram_notifier():
    return TelegramNotifier(
        [
            TelegramRecipient("user_id1", name="first recipient"),
            TelegramRecipient("user_id2", name="second recipient"),
        ],
        enabled=True,
        allow_images=True,
    )


def test_constructor(telegram_notifier):
    assert telegram_notifier is not None


def test_serialize(telegram_notifier):
    data = telegram_notifier.serialize()
    expected_data = {
        "recipients": [
            {"recipient_id": "user_id1", "name": "first recipient"},
            {"recipient_id": "user_id2", "name": "second recipient"},
        ],
        "enabled": True,
        "allow_images": True,
    }

    assert data == expected_data


def test_deserialize():
    data = {
        "recipients": [
            {"recipient_id": "user_id1", "name": "first recipient"},
            {"recipient_id": "user_id2", "name": "second recipient"},
        ],
        "enabled": True,
        "allow_images": True,
    }
    notifier = TelegramNotifier.deserialize(data)
    assert notifier.enabled == data["enabled"]
    assert len(notifier.recipients) == len(data["recipients"])
    assert notifier.recipients[0].recipient_id == data["recipients"][0]["recipient_id"]
