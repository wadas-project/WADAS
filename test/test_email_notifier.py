from unittest.mock import MagicMock, mock_open, patch

import pytest

from wadas.domain.detection_event import DetectionEvent
from wadas.domain.email_notifier import EmailNotifier


@pytest.fixture
def email_notifier():
    with patch("wadas.domain.email_notifier.keyring.get_credential") as mock_cred:
        mock_credential = MagicMock()
        mock_credential.username = "sender@example.com"
        mock_credential.password = "fake_password"
        mock_cred.return_value = mock_credential

        return EmailNotifier(
            sender_email="sender@example.com",
            smtp_hostname="smtp.example.com",
            smtp_port=465,
            recipients_email=["recipient1@example.com", "recipient2@example.com"],
            enabled=True,
        )


def test_constructor(email_notifier):
    assert email_notifier is not None
    assert email_notifier.sender_email == "sender@example.com"
    assert email_notifier.smtp_hostname == "smtp.example.com"
    assert email_notifier.smtp_port == 465
    assert len(email_notifier.recipients_email) == 2


def test_serialize(email_notifier):
    data = email_notifier.serialize()
    expected_data = {
        "sender_email": "sender@example.com",
        "smtp_hostname": "smtp.example.com",
        "smtp_port": 465,
        "recipients_email": ["recipient1@example.com", "recipient2@example.com"],
        "enabled": True,
    }

    assert data == expected_data


def test_deserialize():
    data = {
        "sender_email": "sender@example.com",
        "smtp_hostname": "smtp.example.com",
        "smtp_port": 465,
        "recipients_email": ["recipient1@example.com", "recipient2@example.com"],
        "enabled": True,
    }

    with patch("wadas.domain.email_notifier.keyring.get_credential") as mock_cred:
        mock_credential = MagicMock()
        mock_credential.username = "sender@example.com"
        mock_credential.password = "fake_password"
        mock_cred.return_value = mock_credential

        notifier = EmailNotifier.deserialize(data)

    assert notifier.enabled == data["enabled"]
    assert notifier.sender_email == data["sender_email"]
    assert notifier.smtp_hostname == data["smtp_hostname"]
    assert notifier.smtp_port == data["smtp_port"]
    assert notifier.recipients_email == data["recipients_email"]


@patch("wadas.domain.email_notifier.keyring.get_credential")
def test_is_configured(mock_cred, email_notifier):
    # Mock delle credenziali per is_configured
    mock_credential = MagicMock()
    mock_credential.username = "sender@example.com"
    mock_credential.password = "fake_password"
    mock_cred.return_value = mock_credential

    assert email_notifier.is_configured() is True


@patch("wadas.domain.email_notifier.keyring.get_credential")
def test_is_not_configured_missing_credentials(mock_cred):
    mock_cred.return_value = None

    notifier = EmailNotifier(
        sender_email="sender@example.com",
        smtp_hostname="smtp.example.com",
        smtp_port=465,
        recipients_email=["recipient@example.com"],
        enabled=True,
    )

    # Il metodo is_configured() fallirà perché credentials è None
    with pytest.raises(AttributeError):
        notifier.is_configured()


@patch("wadas.domain.email_notifier.keyring.get_credential")
@patch("wadas.domain.email_notifier.smtplib.SMTP_SSL")
@patch("wadas.domain.email_notifier.is_image")
@patch("wadas.domain.email_notifier.MIMEImage")
@patch("wadas.domain.email_notifier.MIMEText")
@patch("wadas.domain.email_notifier.MIMEMultipart")
@patch("builtins.open", new_callable=mock_open, read_data=b"fake_image_data")
def test_send_email_with_image(
    mock_file, mock_multipart, mock_text, mock_mime_image, mock_is_image, mock_smtp, mock_cred
):
    # Setup credenziali
    mock_credential = MagicMock()
    mock_credential.username = "sender@example.com"
    mock_credential.password = "fake_password"
    mock_cred.return_value = mock_credential

    # Setup SMTP
    mock_is_image.return_value = True
    mock_smtp_instance = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_smtp_instance

    # Setup MIME components
    mock_email_message = MagicMock()
    mock_email_message.as_string.return_value = "fake email string"
    mock_multipart.return_value = mock_email_message

    # Crea notifier
    email_notifier = EmailNotifier(
        sender_email="sender@example.com",
        smtp_hostname="smtp.example.com",
        smtp_port=465,
        recipients_email=["recipient1@example.com", "recipient2@example.com"],
        enabled=True,
    )

    detection_event = MagicMock(spec=DetectionEvent)
    detection_event.camera_id = "camera_1"
    detection_event.classification = None
    detection_event.detection_media_path = "/path/to/image.jpg"

    email_notifier.send_email(detection_event, "Test message")

    # Verifica che login sia stato chiamato con le credenziali corrette
    mock_smtp_instance.login.assert_called_once_with("sender@example.com", "fake_password")

    # Verifica che sendmail sia stato chiamato per ogni destinatario
    assert mock_smtp_instance.sendmail.call_count == 2

    # Verifica che quit sia stato chiamato
    mock_smtp_instance.quit.assert_called_once()


@patch("wadas.domain.email_notifier.keyring.get_credential")
def test_send_email_not_configured(mock_cred):
    mock_cred.return_value = None

    notifier = EmailNotifier(
        sender_email="sender@example.com",
        smtp_hostname="smtp.example.com",
        smtp_port=465,
        recipients_email=["recipient@example.com"],
        enabled=True,
    )

    detection_event = MagicMock(spec=DetectionEvent)
    result = notifier.send_email(detection_event, "Test message")

    assert result is False
