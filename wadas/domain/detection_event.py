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
# Description: Detection event module.

import logging

logger = logging.getLogger(__name__)


class DetectionEvent:
    """Class to embed detection event information into a dedicated object."""

    def __init__(
        self,
        camera_id,
        time_stamp,
        original_image,
        detection_img_path,
        detected_animals,
        classification=True,
        classification_img_path=None,
        classified_animals=None,
    ):
        self.camera_id = camera_id
        self.time_stamp = time_stamp
        self.original_image = original_image
        self.detection_img_path = detection_img_path
        self.detected_animals = detected_animals
        self.classification = classification
        self.classification_img_path = classification_img_path
        self.classified_animals = classified_animals

    def serialize_classified_animals(self):
        """Method to prepare JSON serialization to db of classified_animals attribute."""

        return (
            [
                {
                    "id": animal["id"],
                    "classification": animal["classification"],
                    "xyxy": (
                        animal["xyxy"].tolist()
                        if hasattr(animal["xyxy"], "tolist")
                        else animal["xyxy"]
                    ),
                }
                for animal in self.classified_animals
            ]
            if self.classified_animals
            else []
        )
