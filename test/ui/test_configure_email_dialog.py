from PySide6.QtWidgets import QDialogButtonBox

from wadas.domain.email_notifier import EmailNotifier
from wadas.domain.notifier import Notifier
from wadas.ui.configure_email_dialog import DialogInsertEmail


def test_email_dialog_initial_state(qtbot, mock_notifier_state, mock_keyring):
    """Test that the dialog initializes correctly with empty state."""
    dialog = DialogInsertEmail()
    qtbot.addWidget(dialog)

    # Check initial state
    assert dialog.ui.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is False
    assert dialog.ui.pushButton_testEmail.isEnabled() is False
    assert dialog.ui.checkBox_email_en.isChecked() is True


def test_email_dialog_validation(qtbot, mock_notifier_state, mock_keyring):
    """Test that the OK button is enabled only when all fields are valid."""
    dialog = DialogInsertEmail()
    qtbot.addWidget(dialog)

    # Simulate typing valid data
    qtbot.keyClicks(dialog.ui.lineEdit_senderEmail, "sender@example.com")
    qtbot.keyClicks(dialog.ui.lineEdit_smtpServer, "smtp.example.com")
    qtbot.keyClicks(dialog.ui.lineEdit_port, "587")
    qtbot.keyClicks(dialog.ui.lineEdit_password, "password123")

    # Recipient email is a TextEdit, keyClicks might be slow or tricky,
    # use setText for simplicity or keyClicks if needed
    # dialog.ui.textEdit_recipient_email.setText("recipient@example.com")
    # But to trigger textChanged, we might need to simulate input or call
    # the slot manually if setText doesn't trigger it.
    # PySide6 setText usually triggers signals? No, usually not for QLineEdit/QTextEdit.
    # Let's use keyClicks for a short string.
    qtbot.keyClicks(dialog.ui.textEdit_recipient_email, "recipient@example.com")

    # Check if OK button is enabled
    # Note: The validation logic in the dialog seems to rely on individual validators setting flags
    # and then calling check_enable_ok_button (implied).
    # Let's verify if the button is enabled.
    assert dialog.ui.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is True


def test_email_dialog_save(qtbot, mock_notifier_state, mock_keyring):
    """Test that accepting the dialog saves the configuration."""
    dialog = DialogInsertEmail()
    qtbot.addWidget(dialog)

    # Fill data
    dialog.ui.lineEdit_senderEmail.setText("sender@example.com")
    dialog.ui.lineEdit_smtpServer.setText("smtp.example.com")
    dialog.ui.lineEdit_port.setText("587")
    dialog.ui.lineEdit_password.setText("password123")
    dialog.ui.textEdit_recipient_email.setText("recipient@example.com")

    # Manually trigger validation because setText doesn't always
    # trigger textChanged signals in tests or we can just call the
    # validation methods directly if we want to be sure,
    # but better to simulate user interaction if possible.
    # However, for saving, we just need the data to be there when accept_and_close is called.
    # The accept_and_close method reads from the UI elements.

    # We need to make sure the internal flags are set if accept_and_close checks them?
    # Looking at the code: accept_and_close reads text() from widgets.
    # It creates EmailNotifier.

    # Trigger accept
    dialog.accept_and_close()

    # Check if Notifier was updated
    email_notifier = Notifier.notifiers[Notifier.NotifierTypes.EMAIL.value]
    assert isinstance(email_notifier, EmailNotifier)
    assert email_notifier.sender_email == "sender@example.com"
    assert email_notifier.smtp_hostname == "smtp.example.com"
    assert email_notifier.smtp_port == "587"
    assert "recipient@example.com" in email_notifier.recipients_email
