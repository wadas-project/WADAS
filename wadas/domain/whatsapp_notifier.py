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
# Date: 2024-12-16
# Description: WhatsApp notifier module

import logging
import os

import keyring
import requests

from wadas.domain.detection_event import DetectionEvent
from wadas.domain.notifier import Notifier

logger = logging.getLogger(__name__)

module_dir_path = os.path.dirname(os.path.abspath(__file__))


class WhatsAppNotifier(Notifier):
    """WhatsApp Notifier Class"""

    def __init__(self, sender_id, recipient_numbers, enabled=True, allow_images=True):
        super().__init__(enabled)
        self.type = Notifier.NotifierTypes.WHATSAPP
        self.sender_id = sender_id
        self.recipient_numbers = recipient_numbers
        self.allow_images = allow_images

    def is_configured(self):
        """Method that returns configuration status as bool value."""

        credentials = keyring.get_credential("WADAS_WhatsApp", self.sender_id)
        return (
            self.sender_id
            and self.recipient_numbers
            and credentials.username
            and credentials.password
        )

    def send_notification(self, detection_event: DetectionEvent):
        """Implementation of send_notification method for WhatsApp notifier."""

        self.send_whatsapp_message(detection_event)

    def send_whatsapp_message(self, detection_event):
        """Method to send WhatsApp message notification."""

        message = f"WADAS: Animal detected from camera {detection_event.camera_id}!"
        url = f"https://graph.facebook.com/v17.0/{self.sender_id}/messages"

        credentials = keyring.get_credential("WADAS_WhatsApp", self.sender_id)
        if not credentials or not credentials.password:
            logger.error("Unable to retrieve credentials for WhatsApp notifications.")
            return

        headers = {
            "Authorization": f"Bearer {credentials.password}",
            "Content-Type": "application/json",
        }

        # Select image to attach to the notification: classification (if enabled) or detection image
        img_path = (
            detection_event.classification_img_path
            if detection_event.classification
            else detection_event.detection_img_path
        )
        media_id = self.load_image(credentials.password, img_path) if self.allow_images else None

        for recipient_number in self.recipient_numbers:
            failed_txt_n_image = False

            if media_id:
                caption = message
                image_data = {
                    "messaging_product": "whatsapp",
                    "to": recipient_number,
                    "type": "image",
                    "image": {"id": media_id, "caption": caption},
                }
                response_image = requests.post(url, headers=headers, json=image_data)
                if response_image.status_code == 200:
                    logger.info("WhatsApp notification sent!")
                else:
                    logger.error(response_image.status_code, response_image.text)

            if not media_id or failed_txt_n_image:
                data = {
                    "messaging_product": "whatsapp",
                    "to": recipient_number,
                    "type": "text",
                    "text": {"body": message},
                }

                message_response = requests.post(url, headers=headers, json=data)

                if message_response.status_code == 200:
                    logger.info("WhatsApp notification sent!")
                else:
                    err_message = (
                        "Failed to send WhatsApp notification: "
                        f"{message_response.status_code}, {message_response.text}"
                    )
                    logger.error(err_message)

    def load_image(self, token, img_path):
        """Method to load image to send with notification."""

        upload_url = f"https://graph.facebook.com/v17.0/{self.sender_id}/media"
        headers = {"Authorization": f"Bearer {token}"}

        with open(img_path, "rb") as image_file:
            # files = {"file": image_file}
            files = {
                "file": (os.path.basename(img_path), image_file, "image/jpeg", {"Expires": "0"}),
            }
            params = {"messaging_product": "whatsapp"}
            response_upload = requests.post(upload_url, headers=headers, files=files, params=params)

        if response_upload.status_code == 200:
            media_id = response_upload.json().get("id")
            logger.debug("WatsApp image loaded successfully! Media ID: %s", media_id)
            return media_id
        else:
            logger.error(
                "Failed to load WhatsApp image: %s, %s",
                response_upload.status_code,
                response_upload.text,
            )
            return False

    def serialize(self):
        """Method to serialize email notifier object into file."""
        return {
            "sender_id": self.sender_id,
            "recipient_numbers": self.recipient_numbers,
            "enabled": self.enabled,
            "allow_images": self.allow_images,
        }

    @staticmethod
    def deserialize(data):
        """Method to deserialize email notifier object from file."""
        return WhatsAppNotifier(**data)
