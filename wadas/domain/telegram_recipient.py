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
# Description: Module containing MainWindow class and methods.


class TelegramRecipient:

    def __init__(self, recipient_id, name=None):
        self.recipient_id = recipient_id
        self.name = name

    def __eq__(self, other):
        if not hasattr(other, "recipient_id"):
            return False
        return self.recipient_id == other.recipient_id

    def serialize(self):
        """Method to serialize TelegramRecipient object into file."""
        return {"recipient_id": self.recipient_id, "name": self.name}

    @staticmethod
    def deserialize(data):
        """Method to deserialize TelegramRecipient object from file."""
        return TelegramRecipient(**data)
