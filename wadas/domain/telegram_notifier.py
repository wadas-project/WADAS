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
# Date: 2024-12-23
# Description: Telegram notifier module

import logging
import os

import requests

from wadas.domain.detection_event import DetectionEvent
from wadas.domain.notifier import Notifier
from wadas.domain.telegram_recipient import TelegramRecipient
from wadas.domain.utils import image_to_base64

logger = logging.getLogger(__name__)

module_dir_path = os.path.dirname(os.path.abspath(__file__))


class TelegramNotifier(Notifier):
    """Telegram Notifier Class"""

    BASE_URL = "https://api.wadas.it:8443/api/v1/telegram"
    REGISTRATION_URL = BASE_URL + "/users"
    NOTIFICATION_URL = BASE_URL + "/notifications"

    def __init__(self, org_code, recipients=None, enabled=True, allow_images=True):
        super().__init__(enabled)

        self.type = Notifier.NotifierTypes.TELEGRAM
        self.org_code = org_code
        self.recipients = recipients or []
        self.allow_images = allow_images

    def is_configured(self):
        """Method that returns configuration status as bool value."""
        return self.org_code is not None and len(self.recipients) > 0

    def get_recipient_by_id(self, recipient_id):
        """Method to return the TelegramRecipient having the specific recipient_id."""
        return next((item for item in self.recipients if item.recipient_id == recipient_id), None)

    def fetch_registered_recipient(self):
        """Update the list of the recipients fetching from remote."""
        if (
            res := requests.get(f"{self.REGISTRATION_URL}?org_code={self.org_code}", verify=False)
        ).status_code == 200:
            self.recipients = [
                (
                    known_recipient
                    if (known_recipient := self.get_recipient_by_id(user_id))
                    else TelegramRecipient(user_id)
                )
                for user_id in res.json()
            ]
        else:
            raise Exception("Unable to retrieve registered users")

    def register_new_recipient(self):
        """Method to enable Telegram notification to a new user."""
        if self.org_code:
            data = {"org_code": self.org_code}
            res = requests.post(self.REGISTRATION_URL, json=data, verify=False)
            if res.status_code == 200:
                recipient_id = res.json()["user_id"]
                telegram_recipient = TelegramRecipient(recipient_id)
                self.recipients.append(telegram_recipient)
                return telegram_recipient
            else:
                logger.error(
                    "Unable to retrieve user_id from Telegram backend. Error: %s - %s",
                    str(res.status_code),
                    res.text,
                )
                return None
        else:
            raise Exception("Organization code is not valid")

    def remove_registered_recipient(self, recipient):
        """Method to remove a registered recipient from remote."""
        res = requests.delete(
            f"{self.REGISTRATION_URL}?org_code={self.org_code}&user_id={recipient.recipient_id}",
            verify=False,
        )
        if res.status_code == 204:
            self.recipients.remove(recipient)
        else:
            raise Exception("Unable to delete the recipient")

    def send_notification(self, detection_event: DetectionEvent):
        """Implementation of send_notification method for Telegram notifier."""
        message = f"WADAS: Animal detected from camera {detection_event.camera_id}!"
        # Select image to attach to the notification: classification (if enabled) or detection image
        img_path = (
            (
                detection_event.classification_img_path
                if detection_event.classification
                else detection_event.detection_img_path
            )
            if self.allow_images
            else None
        )
        try:
            status, data = self.send_telegram_message(message, img_path=img_path)
            if status == 200:
                if data["status"] == "ok":
                    logger.info("Telegram notification sent!")
                else:
                    if data["succeed_user_ids"]:
                        logger.info(
                            "Telegram notification to UserIDs %s successfully sent.",
                            ",".join(data["succeed_user_ids"]),
                        )
                    logger.warning(
                        "Problem sending some Telegram notifications:\n\t%s",
                        "\n".join(data["error_msgs"]),
                    )
            else:
                logger.error(
                    "Problem sending Telegram notifications: %s - %s",
                    status,
                    data,
                )
        except Exception as e:
            logger.error("Problem sending Telegram notifications: %s", str(type(e)))

    def send_telegram_message(self, message, img_path=None):
        """Method to send Telegram message notification."""

        data = {
            "org_code": self.org_code,
            "user_ids": [recipient.recipient_id for recipient in self.recipients],
            "message": message,
        }

        if img_path:
            data["image_b64"] = image_to_base64(img_path)

        res = requests.post(self.NOTIFICATION_URL, json=data, verify=False)
        return res.status_code, res.json() if res.status_code == 200 else res.text

    def serialize(self):
        """Method to serialize Telegram notifier object into file."""
        return {
            "org_code": self.org_code,
            "recipients": [recipient.serialize() for recipient in self.recipients],
            "enabled": self.enabled,
            "allow_images": self.allow_images,
        }

    @staticmethod
    def deserialize(data):
        """Method to deserialize Telegram notifier object from file."""
        new_data = data.copy()
        recipient_list = new_data["recipients"]
        new_data["recipients"] = [
            TelegramRecipient.deserialize(recipient) for recipient in recipient_list
        ]
        return TelegramNotifier(**new_data)
