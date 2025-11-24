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
# Description: Custom Classification module.

import logging
from queue import Empty

from wadas.domain.animal_detection_mode import AnimalDetectionAndClassificationMode
from wadas.domain.camera import media_queue
from wadas.domain.operation_mode import OperationMode
from wadas.domain.utils import is_image, is_video

logger = logging.getLogger(__name__)


class CustomClassificationMode(AnimalDetectionAndClassificationMode):
    """Custom Classification Mode class."""

    def __init__(self, custom_target_species=OperationMode.cur_custom_classification_species):
        super().__init__()
        self.process_queue = True
        self.type = OperationMode.OperationModeTypes.CustomSpeciesClassificationMode
        self.custom_target_species = custom_target_species

    def run(self):
        """WADAS custom classification mode"""

        self._initialize_processes()
        self.check_for_termination_requests()

        # Run detection model
        while self.process_queue:
            self.check_for_termination_requests()
            # Get image from motion detection notification
            # Timeout is set to 1 second to avoid blocking the thread
            try:
                cur_media = media_queue.get(timeout=1)
            except Empty:
                cur_media = None

            if cur_media and (
                is_image(cur_media["media_path"]) or is_video(cur_media["media_path"])
            ):
                logger.debug("Processing image from motion detection notification...")
                detection_event = self._detect(cur_media)

                self.check_for_termination_requests()
                if detection_event and self.enable_classification:
                    if detection_event.classification_media_path:
                        # Send notification and trigger actuators if any target animal is found
                        if any(
                            classified_animal["classification"][0] in self.custom_target_species
                            for classified_animal in detection_event.classified_animals
                        ):
                            # Notification
                            message = (
                                f"WADAS has classified '{self.last_classified_animals_str}' "
                                f"animal from camera {detection_event.camera_id}!"
                            )
                            logger.info(message)
                            self.send_notification(detection_event, message)

                            # Actuation
                            self.actuate(detection_event)

                            # Show processing results in UI
                            self._show_processed_results(detection_event)
                        else:
                            logger.info(
                                "Target animals '%s' not found, found '%s' instead. "
                                "Skipping notification.",
                                ", ".join(self.custom_target_species),
                                self.last_classified_animals_str,
                            )

                            # To enforce privacy, delete image if no target animal is classified
                            if (
                                OperationMode.enforce_privacy_remove_classification_img
                                or OperationMode.enforce_privacy_remove_original_img
                                or OperationMode.enforce_privacy_remove_detection_img
                            ):
                                self.enforce_privacy(detection_event)
                            else:
                                # Show processing results in UI
                                self._show_processed_results(detection_event)
                    else:
                        logger.info("No animal classified.")
                        self.enforce_privacy(detection_event)

        self.execution_completed()
