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
# Date: 2024-10-11
# Description: Module containing AI Model based logic (detection & classification).

import logging

import numpy as np
import ray
from PIL import Image

from wadas.ai.models import (
    Classifier,
    OVMegaDetectorV5,
    OVMegaDetectorV6YOLO9,
    OVMegaDetectorV6YOLO10,
    txt_animalclasses,
)

logger = logging.getLogger(__name__)

NAME_TO_DETECTOR = {
    "MDV5-yolov5": OVMegaDetectorV5,
    "MDV6b-yolov9c": OVMegaDetectorV6YOLO9,
    "MDV6-yolov10n": OVMegaDetectorV6YOLO10,
}


class DetectionPipeline:
    """Class containing AI Model functionalities (detection & classification)"""

    def __init__(
        self,
        detection_device="auto",
        classification_device="auto",
        language="en",
        distributed_inference=False,
        megadetector_version="MDV5-yolov5",
        deepfaune_version="DFv1.2",
    ):
        self.detection_device = detection_device
        self.classification_device = classification_device
        self.distributed_inference = distributed_inference
        if self.distributed_inference:
            ray.init()

        # Initializing the MegaDetectorV5 model for image detection
        logger.info("Initializing detection model to device %s...", self.detection_device)
        if not (detection_csl := NAME_TO_DETECTOR.get(megadetector_version)):
            raise ValueError("Invalid MegaDetector version: " + megadetector_version)

        self.detection_model = self.initialize_model(
            detection_csl, device=self.detection_device, model_name=megadetector_version
        )
        # Load classification model
        logger.info("Loading classification model to device %s...", self.classification_device)
        self.classifier = self.initialize_model(
            Classifier, device=self.classification_device, version=deepfaune_version
        )
        # Get the index of the animal class of the detection model
        self.animal_class_idx = next(
            key for key, value in OVMegaDetectorV5.CLASS_NAMES.items() if value == "animal"
        )
        self.language = language

    def initialize_model(self, cls, *args, **kwargs):
        """Method to initialize model locally or remotely."""
        if self.distributed_inference:
            return ray.remote(cls).remote(*args, **kwargs)
        return cls(*args, **kwargs)

    def run_model(self, fn, *args, **kwargs):
        """Method to run model locally or remotely."""
        func = fn.remote if self.distributed_inference else fn
        if isinstance(args[0], (list, tuple)):
            result = [func(arg0, *args[1:], **kwargs) for arg0 in args[0]]
        else:
            result = func(*args, **kwargs)
        return ray.get(result) if self.distributed_inference else result

    def set_language(self, language):
        if language not in txt_animalclasses[self.classifier.version]:
            raise ValueError("Language not supported")
        """Method to set the language for the classification labels."""
        self.language = language

    @staticmethod
    def check_models(detection_model, classification_model):
        """Method to check if models are initialized."""
        detector = NAME_TO_DETECTOR.get(detection_model)
        if detector is None:
            logger.error("Unknown detection model version: %s", detection_model)
            return False
        if not (detection_model_status := detector.check_model()):
            logger.error("Detection model version '%s' not found on the system.", detection_model)

        if not (classification_model_status := Classifier.check_model(classification_model)):
            logger.error(
                "Classification model version '%s' not found on the system.", classification_model
            )

        return detection_model_status and classification_model_status

    @staticmethod
    def download_models(force: bool = False):
        """Method to check if models are initialized."""
        return OVMegaDetectorV5.download_model(force) and Classifier.download_model(force)

    def run_detection(self, img: Image, detection_threshold: float):
        """Method to run detection model on provided image."""
        detection_results = []
        if isinstance(img, (list, tuple)):
            # Convert list of images to numpy array
            img_array = [np.array(_img) for _img in img]
        else:
            img_array = [np.array(img)]

        # Performing the detection on the list of images
        results_lst = self.run_model(
            self.detection_model.run, img_array, detection_threshold=detection_threshold
        )

        for results in results_lst:
            # Checks for non animal in results and filter them out
            animal_idx = np.where(results["detections"].class_id == self.animal_class_idx)
            # Filter out the non animal detections
            results["labels"] = [
                label
                for label, class_id in zip(results["labels"], results["detections"].class_id)
                if class_id == self.animal_class_idx
            ]
            results["detections"].xyxy = results["detections"].xyxy[animal_idx]
            results["detections"].confidence = results["detections"].confidence[animal_idx]
            results["detections"].class_id = results["detections"].class_id[animal_idx]

            detection_results.append(results)

        if len(detection_results) == 1:
            return detection_results[0]
        else:
            return detection_results

    def classify(self, img, results, classification_threshold):
        """Method to perform classification on detection result(s)."""
        if not isinstance(results, (list, tuple)):
            results = [results]

        if not isinstance(img, (list, tuple)):
            img = [img]

        if len(img) != len(results):
            raise ValueError("Number of images and results must match.")

        class_request = tuple(zip(img, results))

        logits_lst = self.run_model(self.classifier.predictOnImages, class_request)
        labels = txt_animalclasses[self.classifier.version][self.language]
        total_classification = []
        for logits, res in zip(logits_lst, results):
            classification_id = 0
            classified_animals = []
            for idx, xyxy in enumerate(res["detections"].xyxy):
                # Cropping detection result(s) from original image leveraging detected boxes

                crop_logits = logits[idx, :]
                detections = {key: val.item() for key, val in zip(labels, crop_logits)}
                classification_result = [labels[np.argmax(crop_logits)], max(crop_logits)]
                if max(crop_logits) < classification_threshold:
                    logger.info("Classification value under selected threshold.")
                else:
                    classified_animals.append(
                        {
                            "id": classification_id,
                            "classification": classification_result,
                            "xyxy": xyxy.astype(int).tolist(),
                            "class_probs": detections,
                        }
                    )
                    classification_id += 1

            total_classification.append(classified_animals)

        if len(total_classification) == 1:
            return total_classification[0]
        return total_classification
