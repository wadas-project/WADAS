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
from concurrent.futures import ThreadPoolExecutor
from enum import Enum

from wadas.domain.notification_area import NotificationArea

logger = logging.getLogger(__name__)

# Single shared executor for all notification sends: keeps threads bounded and
# avoids spawning one thread per event (which would pile up under load).
# max_workers=4 covers Email + WhatsApp + Telegram with one spare; tune if more
# notifier types are added.
_notification_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="wadas-notify")


def _on_notification_done(future):
    """Callback invoked when a notification thread completes.
    Logs any unhandled exception that escaped send_notification()."""
    exc = future.exception()
    if exc:
        logger.error("Unhandled exception in notification thread: %s", exc, exc_info=exc)


class Notifier:
    """Base class for notifiers."""

    class NotifierTypes(Enum):
        EMAIL = "Email"
        WHATSAPP = "WhatsApp"
        TELEGRAM = "Telegram"

    notifiers = dict.fromkeys(
        [NotifierTypes.EMAIL.value, NotifierTypes.WHATSAPP.value, NotifierTypes.TELEGRAM.value]
    )

    notification_areas: dict[str, NotificationArea] = {}

    def __init__(self, enabled=True, allow_images=True):
        self.type = None
        self.enabled = enabled
        self.allow_images = allow_images

    @classmethod
    def get_areas_for_camera(cls, camera_id):
        """Return all NotificationArea instances that include the given camera_id."""
        return [area for area in cls.notification_areas.values() if camera_id in area.camera_ids]

    @staticmethod
    def get_recipients_for_area(area, notifier_type):
        """Return the list of contacts configured in a single NotificationArea for
        a given notifier_type."""
        key = notifier_type.value if hasattr(notifier_type, "value") else notifier_type
        return list(area.contacts.get(key, []))

    @classmethod
    def get_recipients_for_camera(cls, camera_id, notifier_type):
        """Return the de-duplicated list of contacts to notify for a given
        camera_id and notifier_type, aggregating Notifier.get_recipients_for_area
        across all NotificationArea(s) that include camera_id.

        Returns None if no NotificationArea is configured at all, or if
        camera_id is None (no camera context, e.g. a test send from the
        configuration dialog): callers fall back to their full distribution
        list in that case.

        Returns a list (possibly empty) if at least one NotificationArea is
        configured AND camera_id is provided.
        """
        if camera_id is None or not cls.notification_areas:
            return None

        recipients = []
        for area in cls.get_areas_for_camera(camera_id):
            for contact in cls.get_recipients_for_area(area, notifier_type):
                if contact not in recipients:
                    recipients.append(contact)
        return recipients

    @staticmethod
    def send_notifications(detection_event, message=""):
        """Dispatch notifications through all enabled protocols.

        Each notifier's send_notification() is submitted to a shared thread
        pool so that network I/O (SMTP, Telegram API, WhatsApp API) does not
        block the main detection/classification loop.
        """
        configured_notifier = False
        enabled_notifier = False
        for notifier in Notifier.notifiers:
            if Notifier.notifiers[notifier]:
                if Notifier.notifiers[notifier].is_configured:
                    configured_notifier = True
                    if Notifier.notifiers[notifier].enabled:
                        enabled_notifier = True
                        future = _notification_executor.submit(
                            Notifier.notifiers[notifier].send_notification,
                            detection_event,
                            message,
                        )
                        future.add_done_callback(_on_notification_done)
        if not configured_notifier:
            logger.warning("No notification protocol configured. Skipping notification.")
        elif not enabled_notifier:
            logger.warning("No notification protocol enabled. Skipping notification.")

    @staticmethod
    def notifier_enabled():
        """Methods that returns bool value representing notifier(s) enablement status.
        returns true if at least a notifier is enabled, false otherwise."""

        return any(
            notifier.is_configured and notifier.enabled
            for notifier_id, notifier in Notifier.notifiers.items()
            if notifier
        )

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
