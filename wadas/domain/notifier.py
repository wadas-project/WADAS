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
# Description: Notification module

import logging
from abc import abstractmethod
from enum import Enum

logger = logging.getLogger(__name__)


class Notifier:
    """Base class for notifiers."""

    class NotifierTypes(Enum):
        EMAIL = "Email"
        WHATSAPP = "WhatsApp"
        TELEGRAM = "Telegram"

    notifiers = dict.fromkeys(
        [NotifierTypes.EMAIL.value, NotifierTypes.WHATSAPP.value, NotifierTypes.TELEGRAM.value]
    )

    def __init__(self, enabled=True, allow_images=True):
        self.type = None
        self.enabled = enabled
        self.allow_images = allow_images

    @staticmethod
    def send_notifications(detection_event, message=""):
        """Method to send notification through enabled protocols."""

        configured_notifier = False
        enabled_notifier = False
        for notifier in Notifier.notifiers:
            if Notifier.notifiers[notifier]:
                if Notifier.notifiers[notifier].is_configured:
                    configured_notifier = True
                    if Notifier.notifiers[notifier].enabled:
                        enabled_notifier = True
                        Notifier.notifiers[notifier].send_notification(detection_event)
        if not configured_notifier:
            logger.warning("No notification protocol configured. Skipping notification.")
        elif not enabled_notifier:
            logger.warning("No notification protocol enabled. Skipping notification.")

    @abstractmethod
    def is_configured(self):
        """Method to return whether a given Notifier is properly configured"""

    @abstractmethod
    def send_notification(self, img_path):
        """Method to send notification for specific Notifier."""

    @abstractmethod
    def serialize(self):
        """Method to serialize Camera object into file."""

    @staticmethod
    def deserialize(data):
        """Method to deserialize Camera object from file."""
