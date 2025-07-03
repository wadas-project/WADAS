# This file is part of WADAS project.
#
# WADAS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# WADAS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with WADAS. If not, see <https://www.gnu.org/licenses/>.
#
# Author(s): Stefano Dell'Osa, Alessandro Palla, Cesare Di Mauro, Antonio Farina
# Date: 2024-10-20
# Description: Email notifier module

import logging
import os
import smtplib
import ssl
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import keyring

from wadas.domain.detection_event import DetectionEvent
from wadas.domain.notifier import Notifier
from wadas.domain.utils import is_image

logger = logging.getLogger(__name__)


class EmailNotifier(Notifier):
    """Email Notifier Class"""

    def __init__(self, sender_email, smtp_hostname, smtp_port, recipients_email, enabled=True):
        super().__init__(enabled)
        self.type = Notifier.NotifierTypes.EMAIL
        self.sender_email = sender_email
        self.smtp_hostname = smtp_hostname
        self.smtp_port = smtp_port
        self.recipients_email = recipients_email

    def send_email(self, detection_event, message=""):
        """Method to build email and send it."""

        credentials = keyring.get_credential("WADAS_email", self.sender_email)
        if (
            not credentials
            or not self.sender_email
            or not self.smtp_hostname
            or not self.smtp_port
            or not self.recipients_email
        ):
            logger.debug("Email not configured. Skipping email notification.")
            return False

        email_message = MIMEMultipart()
        # Set email required fields.
        email_message["Subject"] = "WADAS detection alert"
        email_message["From"] = self.sender_email
        email_message["To"] = ", ".join(self.recipients_email)

        # Select image to attach to the notification: classification (if enabled) or detection image
        img_path = (
            detection_event.classification_img_path
            if detection_event.classification
            else detection_event.detection_img_path
        )

        # Attach image, skip video
        if is_image(img_path):
            # HTML content with an image embedded
            html = f"""\
            <html>
                <body>
                    <p>Hi,<br>
                    Animal detected from camera {detection_event.camera_id}:
                    <img src="cid:image1"><br>
                    {message}</p><br>
                </body>
            </html>
            """
            # Attach the HTML part
            email_message.attach(MIMEText(html, "html"))

            # Open the image file in binary mode
            with open(img_path, "rb") as img:
                # Attach the image file
                msg_img = MIMEImage(img.read(), name=os.path.basename(img_path))
                # Define the Content-ID header to use in the HTML body
                msg_img.add_header("Content-ID", "<image1>")
                # Attach the image to the message
                email_message.attach(msg_img)
        else:
            # HTML content (text only)
            html = f"""\
                       <html>
                           <body>
                               <p>Hi,<br>
                               Animal detected from camera {detection_event.camera_id}!<br>
                               {message}</p><br>
                           </body>
                       </html>
                       """
            # Attach the HTML part
            email_message.attach(MIMEText(html, "html"))

        # Connect to email's SMTP server using SSL.
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(
            self.smtp_hostname,
            self.smtp_port,
            context=context,
        ) as smtp_server:
            # Login to the SMTP server
            smtp_server.login(self.sender_email, credentials.password)
            # Send the email to all recipients.
            for recipient in self.recipients_email:
                smtp_server.sendmail(self.sender_email, recipient, email_message.as_string())
                logger.debug("Email notification sent to recipient %s .", recipient)
            smtp_server.quit()
        logger.info("Email notification for %s sent!", img_path)

    def send_notification(self, detection_event: DetectionEvent, message=""):
        """Implementation of send_notification method specific for Email notifier."""
        self.send_email(detection_event, message)

    def is_configured(self):
        """Method that returns configuration status as bool value."""

        username = self.sender_email
        credentials = keyring.get_credential("WADAS_email", username)
        return bool(
            self.smtp_hostname and self.smtp_port and self.recipients_email and credentials.username
        )

    def serialize(self):
        """Method to serialize email notifier object into file."""
        return {
            "sender_email": self.sender_email,
            "smtp_hostname": self.smtp_hostname,
            "smtp_port": self.smtp_port,
            "recipients_email": self.recipients_email,
            "enabled": self.enabled,
        }

    @staticmethod
    def deserialize(data):
        """Method to deserialize email notifier object from file."""
        return EmailNotifier(**data)
