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
# Date: 2025-01-04
# Description: Actuation event module.

import logging

logger = logging.getLogger(__name__)


class ActuationEvent:
    """Class to embed actuation event information into a dedicated object."""

    def __init__(self, actuator_id, time_stamp, detection_event, command=None):
        self.actuator_id = actuator_id
        self.time_stamp = time_stamp
        self.detection_event = detection_event
        self.command = command
