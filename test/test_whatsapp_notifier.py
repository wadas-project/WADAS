from unittest.mock import MagicMock, mock_open, patch

import pytest

from wadas.domain.detection_event import DetectionEvent
from wadas.domain.whatsapp_notifier import WhatsAppNotifier


@pytest.fixture
def whatsapp_notifier():
    with patch("wadas.domain.whatsapp_notifier.keyring.get_credential") as mock_cred:
        mock_credential = MagicMock()
        mock_credential.username = "sender_id_123"
        mock_credential.password = "fake_token"
        mock_cred.return_value = mock_credential

        return WhatsAppNotifier(
            sender_id="sender_id_123",
            recipient_numbers=["+1234567890", "+0987654321"],
            enabled=True,
            allow_images=True,
        )


def test_constructor(whatsapp_notifier):
    assert whatsapp_notifier is not None
    assert whatsapp_notifier.sender_id == "sender_id_123"
    assert len(whatsapp_notifier.recipient_numbers) == 2
    assert whatsapp_notifier.enabled is True
    assert whatsapp_notifier.allow_images is True


def test_serialize(whatsapp_notifier):
    data = whatsapp_notifier.serialize()
    expected_data = {
        "sender_id": "sender_id_123",
        "recipient_numbers": ["+1234567890", "+0987654321"],
        "enabled": True,
        "allow_images": True,
    }

    assert data == expected_data


def test_deserialize():
    data = {
        "sender_id": "sender_id_123",
        "recipient_numbers": ["+1234567890", "+0987654321"],
        "enabled": True,
        "allow_images": True,
    }

    with patch("wadas.domain.whatsapp_notifier.keyring.get_credential") as mock_cred:
        mock_credential = MagicMock()
        mock_credential.username = "sender_id_123"
        mock_credential.password = "fake_token"
        mock_cred.return_value = mock_credential

        notifier = WhatsAppNotifier.deserialize(data)

    assert notifier.enabled == data["enabled"]
    assert notifier.sender_id == data["sender_id"]
    assert notifier.recipient_numbers == data["recipient_numbers"]
    assert notifier.allow_images == data["allow_images"]


@patch("wadas.domain.whatsapp_notifier.keyring.get_credential")
def test_is_configured(mock_cred, whatsapp_notifier):
    # Mock credentials for is_configured
    mock_credential = MagicMock()
    mock_credential.username = "sender_id_123"
    mock_credential.password = "fake_token"
    mock_cred.return_value = mock_credential

    result = whatsapp_notifier.is_configured()
    assert result  # Check it's truthy (not False/None/empty)


@patch("wadas.domain.whatsapp_notifier.keyring.get_credential")
def test_is_not_configured_missing_credentials(mock_cred):
    mock_cred.return_value = None

    notifier = WhatsAppNotifier(
        sender_id="sender_id_123",
        recipient_numbers=["+1234567890"],
        enabled=True,
        allow_images=True,
    )

    # The is_configured() method will fail because credentials is None
    with pytest.raises(AttributeError):
        notifier.is_configured()


@patch("wadas.domain.whatsapp_notifier.keyring.get_credential")
@patch("wadas.domain.whatsapp_notifier.requests.post")
@patch("wadas.domain.whatsapp_notifier.is_video")
@patch("builtins.open", new_callable=mock_open, read_data=b"fake_image_data")
def test_send_whatsapp_message_with_image(mock_file, mock_is_video, mock_post, mock_cred):
    # Setup credentials
    mock_credential = MagicMock()
    mock_credential.username = "sender_id_123"
    mock_credential.password = "fake_token"
    mock_cred.return_value = mock_credential

    # Setup is_video
    mock_is_video.return_value = False

    # Setup requests.post for image upload and message sending
    mock_upload_response = MagicMock()
    mock_upload_response.status_code = 200
    mock_upload_response.json.return_value = {"id": "media_id_123"}

    mock_send_response = MagicMock()
    mock_send_response.status_code = 200

    # First call: image upload, subsequent calls: message sending
    mock_post.side_effect = [mock_upload_response, mock_send_response, mock_send_response]

    # Create notifier
    notifier = WhatsAppNotifier(
        sender_id="sender_id_123",
        recipient_numbers=["+1234567890", "+0987654321"],
        enabled=True,
        allow_images=True,
    )

    detection_event = MagicMock(spec=DetectionEvent)
    detection_event.camera_id = "camera_1"
    detection_event.classification = None
    detection_event.detection_media_path = "/path/to/image.jpg"
    detection_event.preview_image = None

    notifier.send_whatsapp_message(detection_event, "Test message")

    # Verify that requests.post was called 3 times
    # (1 upload + 2 sends for the 2 recipients)
    assert mock_post.call_count == 3


@patch("wadas.domain.whatsapp_notifier.keyring.get_credential")
@patch("wadas.domain.whatsapp_notifier.requests.post")
def test_send_whatsapp_message_text_only(mock_post, mock_cred):
    # Setup credentials
    mock_credential = MagicMock()
    mock_credential.username = "sender_id_123"
    mock_credential.password = "fake_token"
    mock_cred.return_value = mock_credential

    # Setup requests.post
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_post.return_value = mock_response

    # Create notifier without images
    notifier = WhatsAppNotifier(
        sender_id="sender_id_123",
        recipient_numbers=["+1234567890"],
        enabled=True,
        allow_images=False,
    )

    detection_event = MagicMock(spec=DetectionEvent)
    detection_event.camera_id = "camera_1"
    detection_event.classification = None
    detection_event.detection_media_path = "/path/to/image.jpg"

    notifier.send_whatsapp_message(detection_event, "Test message")

    # Verify that requests.post was called 1 time (text only)
    assert mock_post.call_count == 1

    # Verify that the message is of type text
    call_args = mock_post.call_args
    assert call_args[1]["json"]["type"] == "text"


@patch("wadas.domain.whatsapp_notifier.keyring.get_credential")
def test_send_whatsapp_message_no_credentials(mock_cred):
    mock_cred.return_value = None

    notifier = WhatsAppNotifier(
        sender_id="sender_id_123",
        recipient_numbers=["+1234567890"],
        enabled=True,
        allow_images=True,
    )

    detection_event = MagicMock(spec=DetectionEvent)
    detection_event.camera_id = "camera_1"

    # Should not raise exceptions, only log the error
    notifier.send_whatsapp_message(detection_event, "Test message")


@patch("wadas.domain.whatsapp_notifier.keyring.get_credential")
@patch("wadas.domain.whatsapp_notifier.requests.post")
@patch("builtins.open", new_callable=mock_open, read_data=b"fake_image_data")
def test_load_image_success(mock_file, mock_post, mock_cred):
    # Setup credentials
    mock_credential = MagicMock()
    mock_credential.username = "sender_id_123"
    mock_credential.password = "fake_token"
    mock_cred.return_value = mock_credential

    # Setup requests.post
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": "media_id_123"}
    mock_post.return_value = mock_response

    notifier = WhatsAppNotifier(
        sender_id="sender_id_123",
        recipient_numbers=["+1234567890"],
        enabled=True,
        allow_images=True,
    )

    media_id = notifier.load_image("fake_token", "/path/to/image.jpg")

    assert media_id == "media_id_123"
    mock_post.assert_called_once()


@patch("wadas.domain.whatsapp_notifier.keyring.get_credential")
@patch("wadas.domain.whatsapp_notifier.requests.post")
@patch("builtins.open", new_callable=mock_open, read_data=b"fake_image_data")
def test_load_image_failure(mock_file, mock_post, mock_cred):
    # Setup credentials
    mock_credential = MagicMock()
    mock_credential.username = "sender_id_123"
    mock_credential.password = "fake_token"
    mock_cred.return_value = mock_credential

    # Setup requests.post with error
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.text = "Error message"
    mock_post.return_value = mock_response

    notifier = WhatsAppNotifier(
        sender_id="sender_id_123",
        recipient_numbers=["+1234567890"],
        enabled=True,
        allow_images=True,
    )

    media_id = notifier.load_image("fake_token", "/path/to/image.jpg")

    assert media_id is False


@patch("wadas.domain.whatsapp_notifier.keyring.get_credential")
@patch("wadas.domain.whatsapp_notifier.requests.post")
@patch("wadas.domain.whatsapp_notifier.is_video")
@patch("builtins.open", new_callable=mock_open, read_data=b"fake_image_data")
def test_send_whatsapp_message_with_video_preview(mock_file, mock_is_video, mock_post, mock_cred):
    # Setup credentials
    mock_credential = MagicMock()
    mock_credential.username = "sender_id_123"
    mock_credential.password = "fake_token"
    mock_cred.return_value = mock_credential

    # Setup is_video
    mock_is_video.return_value = True

    # Setup requests.post
    mock_upload_response = MagicMock()
    mock_upload_response.status_code = 200
    mock_upload_response.json.return_value = {"id": "media_id_123"}

    mock_send_response = MagicMock()
    mock_send_response.status_code = 200

    mock_post.side_effect = [mock_upload_response, mock_send_response]

    notifier = WhatsAppNotifier(
        sender_id="sender_id_123",
        recipient_numbers=["+1234567890"],
        enabled=True,
        allow_images=True,
    )

    detection_event = MagicMock(spec=DetectionEvent)
    detection_event.camera_id = "camera_1"
    detection_event.classification = None
    detection_event.detection_media_path = "/path/to/video.mp4"
    detection_event.preview_image = "/path/to/preview.jpg"

    notifier.send_whatsapp_message(detection_event, "Test message")

    # Verify that requests.post was called
    assert mock_post.call_count == 2

    # Verify that the message contains the note about the video
    call_args = mock_post.call_args_list[1]
    message_caption = call_args[1]["json"]["image"]["caption"]
    assert "preview image" in message_caption
    assert "WADAS web interface" in message_caption
