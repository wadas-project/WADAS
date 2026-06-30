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
# Date: 2026-06-28
# Description: Notification area

import logging

logger = logging.getLogger(__name__)


class NotificationArea:
    """Represents a logical/geographical area grouping one or more cameras
    and, for each notification method (Email, WhatsApp, Telegram, ...),
    the list of contacts that should receive notifications for events
    detected by those cameras.

    This class is a plain data container: registry, lookups, and the
    decision of which contacts to use for a given send are owned by
    Notifier, which keeps the orchestration logic in one place.
    """

    def __init__(self, id, camera_ids=None, contacts=None):
        self.id = id
        self.camera_ids = list(camera_ids) if camera_ids else []
        # contacts: dict[str (notifier type value), list[str]]
        # e.g. {"WhatsApp": ["+391234567890"], "Telegram": ["123456"]}
        self.contacts = {k: list(v) for k, v in (contacts or {}).items()}

    def add_camera(self, camera_id):
        if camera_id not in self.camera_ids:
            self.camera_ids.append(camera_id)

    def remove_camera(self, camera_id):
        if camera_id in self.camera_ids:
            self.camera_ids.remove(camera_id)

    def add_contact(self, notifier_type_value, contact):
        self.contacts.setdefault(notifier_type_value, [])
        if contact not in self.contacts[notifier_type_value]:
            self.contacts[notifier_type_value].append(contact)

    def remove_contact(self, notifier_type_value, contact):
        if notifier_type_value in self.contacts and contact in self.contacts[notifier_type_value]:
            self.contacts[notifier_type_value].remove(contact)

    def serialize(self):
        """Serialize NotificationArea object into a dict, for config file."""
        return {
            "id": self.id,
            "camera_ids": list(self.camera_ids),
            "contacts": {k: list(v) for k, v in self.contacts.items()},
        }

    @staticmethod
    def deserialize(data):
        """Deserialize NotificationArea object from a dict."""
        return NotificationArea(
            data.get("id"),
            data.get("camera_ids", []),
            data.get("contacts", {}),
        )
