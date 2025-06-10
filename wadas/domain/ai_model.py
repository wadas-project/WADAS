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
# Date: 2024-08-14
# Description: Module containing AI Model based logic (detection & classification).

import logging
import os

import cv2
import numpy as np
from PIL import Image, ImageFile, UnidentifiedImageError
from PytorchWildlife import utils as pw_utils

from wadas.ai import DetectionPipeline
from wadas.ai.object_tracker import ObjectTracker

logger = logging.getLogger(__name__)
ImageFile.LOAD_TRUNCATED_IMAGES = True


class AiModel:
    """Class containing AI Model functionalities (detection & classification)"""

    detection_device = "auto"
    classification_device = "auto"
    classification_threshold = 0.5
    detection_threshold = 0.5
    language = "en"
    video_fps = 1
    distributed_inference = False
    detection_model_version = "MDV5-yolov5"
    classification_model_version = "DFv1.2"
    use_case='MONITORING'

    def __init__(self):
        # Initializing the MegaDetectorV5 model for image detection
        logger.info(
            "Initializing %s AI detection model for image detection on '%s' device and"
            " %s model for classification on '%s' device...",
            AiModel.detection_model_version,
            AiModel.detection_device,
            AiModel.classification_model_version,
            AiModel.classification_device,
        )
        self.detection_pipeline = DetectionPipeline(
            detection_device=AiModel.detection_device,
            classification_device=AiModel.classification_device,
            language=AiModel.language,
            distributed_inference=AiModel.distributed_inference,
            megadetector_version=AiModel.detection_model_version,
            use_case=AiModel.use_case
        )

        self.original_image = ""

        # Create required output folders
        os.makedirs("detection_output", exist_ok=True)
        os.makedirs("classification_output", exist_ok=True)
        os.makedirs("wadas_motion_detection", exist_ok=True)
        os.makedirs("video_frames", exist_ok=True)

        logger.debug(
            "Detection threshold: %s, Classification threshold: %s.",
            self.detection_threshold,
            self.classification_threshold,
        )

    @staticmethod
    def check_model(detection_model, classification_model):
        """Method to check if model is initialized."""
        return DetectionPipeline.check_models(detection_model, classification_model)

    @staticmethod
    def download_models():
        """Method to check if model is initialized."""
        return DetectionPipeline.download_models()

    def process_image(self, img_path, save_detection_image: bool):
        """Method to run detection model on provided image."""

        logger.debug("Selected detection device: %s", AiModel.detection_device)

        try:
            img = Image.open(img_path)
            img.load()
        except FileNotFoundError:
            logger.error("%s is not a valid image path. Aborting.", img_path)
            return None, None
        except UnidentifiedImageError:
            logger.error("%s is not a valid image file. Aborting.", img_path)
            return None, None
        except OSError:
            logger.error("%s could not be opened.", img_path)
            return None, None

        logger.info("Running detection on image %s ...", img_path)

        img = img.convert("RGB")

        results = self.detection_pipeline.run_detection(img, AiModel.detection_threshold)
        detected_img_path = ""

        if len(results["detections"].xyxy) > 0 and save_detection_image:
            logger.info("Saving detection results...")
            results["img_id"] = img_path
            pw_utils.save_detection_images(
                results, os.path.join(".", "detection_output"), overwrite=False
            )
            detected_img_path = os.path.join("detection_output", os.path.basename(img_path))
        else:
            logger.info("No detected animals for %s. Removing image.", img_path)
            try:
                os.remove(img_path)
            except OSError:
                logger.warning("Could not remove %s", img_path)

        return results, detected_img_path

    def get_video_frames(self, video_path):
        """Method to extract frames from video."""
        try:
            video = cv2.VideoCapture(video_path)
            if not video.isOpened():
                logger.error("Error opening video file %s. Aborting.", video_path)
                return None, None
        except FileNotFoundError:
            logger.error("%s is not a valid video path. Aborting.", video_path)
            return None, None

        fps = video.get(cv2.CAP_PROP_FPS) #Ottiene il numero di frame per secondo dal video.
        if fps == 0:
            logger.error("Error reading video FPS. Aborting.")
            return None, None

        logger.debug("Video original FPS: %s", fps)

        downsample = max(int(round(fps / self.video_fps)), 1)

        logger.info("Effective FPS: %s", round(fps / downsample))

        # Initialize frame counter
        frame_count = 0
        while True:

            ret, frame = video.read()
            if not ret:
                break

            if frame_count % downsample:
                # Skip frames based on downsample value
                frame_count += 1
                continue

            # Convert frame to PIL image
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = Image.fromarray(frame)

            yield frame, frame_count
            frame_count += 1

    def process_video_offline(self, video_path):
        """Method to run detection model on provided video."""

        logger.debug("Selected detection device: %s", AiModel.detection_device)

        logger.info("Running detection on video %s ...", video_path)
        tracker = ObjectTracker(max_missed=10)

        frames = tuple(frame for frame, _ in self.get_video_frames(video_path))
        tracked_animals = []

        # Run the detection model on the video frames
        detection_lists = self.detection_pipeline.run_detection(frames, AiModel.detection_threshold)

        # Classify detected animals on all frames
        classification_lists = self.detection_pipeline.classify(
            frames, detection_lists, AiModel.classification_threshold
        )

        for frame, classified_animals in zip(frames, classification_lists):
            array = np.array(frame)
            tracked_animal = tracker.update(classified_animals, array.shape[:2])
            tracked_animals.append(tracked_animal)

        return tracked_animals

    def process_video(self, video_path, save_detection_image: bool):
        """Method to run detection model on provided video."""

        logger.debug("Selected detection device: %s", AiModel.detection_device)

        logger.info("Running detection on video %s ...", video_path)
        video_filename = os.path.basename(video_path)

        for frame, frame_count in self.get_video_frames(video_path):

            results = self.detection_pipeline.run_detection(frame, AiModel.detection_threshold)

            if len(results["detections"].xyxy) > 0:
                if save_detection_image:
                    # Saving original video frame
                    logger.debug("Saving video frame...")
                    frame_path = os.path.join(
                        "video_frames", f"{video_filename}_frame_{frame_count}.jpg"
                    )
                    frame.save(frame_path)
                    # Saving the detection results
                    logger.info("Saving detection results for frame %s...", frame_count)
                    detected_img_path = os.path.join("detection_output", f"frame_{frame_count}.jpg")
                    # Needs to be saved first as save_detection_images expects a path inside results
                    frame.save(detected_img_path)
                    results["img_id"] = detected_img_path
                    yield results, detected_img_path, frame_path
                else:
                    yield results, None, None
            else:
                logger.info("No detected animals for frame %s. Skipping image.", frame_count)

    def classify(self, img_path, results):
        """Method to perform classification on detection result(s)."""

        logger.debug("Selected classification device: %s", AiModel.classification_device)

        if not results:
            logger.warning("No results to classify. Skipping classification.")
            return ""

        logger.info("Running classification on %s image...", img_path)

        try:
            img = Image.open(img_path)
            img.load()
        except FileNotFoundError:
            logger.error("%s is not a valid image path. Aborting.", img_path)
            return None, None
        except UnidentifiedImageError:
            logger.error("%s is not a valid image file. Aborting.", img_path)
            return None, None
        except OSError:
            logger.error("%s could not be opened.", img_path)
            return None, None

        img = img.convert("RGB")

        classified_animals = None
        classified_img_path = None
        if not (
            classified_animals := self.detection_pipeline.classify(
                img, results, AiModel.classification_threshold
            )
        ):
            logger.debug("No classified animals, skipping img crops saving.")
        else:
            for classified_animal in classified_animals:
                # Cropping detection result(s) from original image leveraging detected boxes
                cropped_image = img.crop(classified_animal["xyxy"])
                cropped_image_path = os.path.join(
                    "classification_output", f"{classified_animal['id']}_cropped_image.jpg"
                )
                cropped_image.save(cropped_image_path)
                logger.debug("Saved crop of image at %s.", cropped_image_path)

            classified_img_path = self.build_classification_square(
                img, classified_animals, img_path
            )
        return classified_img_path, classified_animals

    def build_classification_square(self, img, classified_animals, img_path):
        """Build square on classified animals."""

        classified_image_path = ""
        # Build classification square
        orig_image = np.array(img)
        for animal in classified_animals:
            # Classification box attributes
            x1 = int(animal["xyxy"][0])
            y1 = int(animal["xyxy"][1])
            x2 = int(animal["xyxy"][2])
            y2 = int(animal["xyxy"][3])
            color = (255, 0, 0)
            classified_image = cv2.rectangle(orig_image, (x1, y1), (x2, y2), color, 2)

            # Round precision on classification score
            animal["classification"][1] = round(animal["classification"][1].item(), 2)

            # Draw black background rectangle to improve text readability.
            # Replicating Megadetector settings whenever possible.
            text = str(animal["classification"][0]) + " " + str(animal["classification"][1])
            font = cv2.FONT_HERSHEY_SIMPLEX
            text_scale = 1.5
            text_thickness = 2
            text_padding = 10

            text_x = x1 + text_padding
            text_y = y1 - text_padding
            text_width, text_height = cv2.getTextSize(
                text,
                font,
                text_scale,
                text_thickness,
            )[0]

            # Text background size is dependent on the size of the text
            text_background_x1 = x1
            text_background_y1 = y1 - 2 * text_padding - text_height
            text_background_x2 = x1 + 2 * text_padding + text_width
            text_background_y2 = y1

            classified_image = cv2.rectangle(
                classified_image,
                (text_background_x1, text_background_y1),
                (text_background_x2, text_background_y2),
                color,
                cv2.FILLED,
            )

            # Add label to classification rectangle
            cv2.putText(
                classified_image,
                text,
                (text_x, text_y),
                font,
                text_scale,
                (0, 0, 0),
                text_thickness,
                cv2.LINE_AA,
            )
            cimg = Image.fromarray(classified_image)

            # Save classified image
            detected_img_name = os.path.basename(img_path)
            classified_img_name = "classified_" + detected_img_name
            classified_image_path = os.path.join("classification_output", classified_img_name)
            cimg.save(classified_image_path)
        return classified_image_path
