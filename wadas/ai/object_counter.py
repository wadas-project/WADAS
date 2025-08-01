import logging
import os
from enum import Enum

import cv2
import numpy as np
from PIL import Image
from ultralytics import solutions

from wadas.ai.ov_predictor import __model_folder__, load_ov_model

logger = logging.getLogger(__name__)


class TrackingRegion(Enum):
    """Class to define tunnel entrance tracking region"""

    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"

    def to_region(self, width: int, height: int) -> list[tuple[int, int]]:
        """Method returning entrance tracking region coordinates"""
        margin = 1 / 6  # 1/6 of the width or height
        if self == TrackingRegion.UP:
            region = [(0, height * margin), (width, height * margin)]
        elif self == TrackingRegion.DOWN:
            region = [(0, height * (1 - margin)), (width, height * (1 - margin))]
        elif self == TrackingRegion.LEFT:
            region = [(width * margin, 0), (width * margin, height)]
        elif self == TrackingRegion.RIGHT:
            region = [(width * (1 - margin), 0), (width * (1 - margin), height)]

        return [(int(dim[0]), int(dim[1])) for dim in region]

    @classmethod
    def get_tracking_region(cls, value: str):
        """Method returning tracking region from corresponding value"""
        return cls.__members__.get(value.upper())


class ObjectCounter(solutions.ObjectCounter):

    def __init__(
        self,
        model: str,
        region: list[tuple[int, int]] | TrackingRegion,
        classes: list[int] = None,
        device: str = "CPU",
        batch_size: int = 1,
        iou_threshold: float = 0.5,
        confidence_threshold: float = 0.3,
        **kwargs,
    ):
        """
        Initializes the ObjectCounter class.
        Args:
            model (str): Path to the model file.
            region (list[tuple[int, int]] | TrackingRegion): List of tuples defining the
                                            region of interest. It is possible to define a line
                                            a polygon or an enum with predefined directions
            classes (list[int]): List of class indices to be counted.
            device (str, optional): Device to run the model on. Defaults to "CPU".
            batch_size (int, optional): Number of images to process in a batch. Defaults to 1.
            **kwargs: Additional keyword arguments.
        """
        model = os.path.join(__model_folder__, model)
        super().__init__(
            model=model,
            region=None,
            classes=classes,
            batch_size=batch_size,
            iou=iou_threshold,
            conf=confidence_threshold,
            **kwargs,
        )
        self.model.predictor.model.ov_compiled_model = load_ov_model(model, device)
        self.region = region

    def process_frames(self, frames: list[np.ndarray]) -> dict:
        """
        Processes a single frame.
        Args:
            frame (np.ndarray): Input frame.
        Returns:
            np.ndarray: Processed frame.
        """

        # If region is not initialized, set it to the first frame size
        if not self.region_initialized:
            if isinstance(self.region, TrackingRegion):
                self.region = self.region.to_region(frames[0].shape[1], frames[0].shape[0])

        for frame in frames:
            results = self(frame)

        # It will track the objects and count them at the end of the video
        # Result is in the form of a dictionary of classwise counts
        return results.classwise_count

    def get_video_frames(self, video_path):
        """Method to get frames from a video file"""

        try:
            if not (video := cv2.VideoCapture(video_path)).isOpened():
                logger.error("Error opening video file %s. Aborting.", video_path)
                return None, None
        except FileNotFoundError:
            logger.error("%s is not a valid video path. Aborting.", video_path)
            return None, None

        frames = []
        while video.isOpened():
            success, im0 = video.read()

            if not success:
                break

            frames.append(im0)

        return frames

    def init_region(self, frames):
        """Method to initialize region"""

        # If region is not initialized, set it to the first frame size
        if not self.region_initialized:
            if isinstance(self.region, TrackingRegion):
                self.region = self.region.to_region(frames[0].shape[1], frames[0].shape[0])

    def process_video_demo(self, video_path, save_detection_image: bool):
        """Method to process video in tunnel mode updating animals counter with frames feedback
        to UI for Test Model Mode."""

        logger.info("Running tunnel mode detection on video %s ...", video_path)

        frames = self.get_video_frames(video_path)
        self.init_region(frames)

        for i, frame in enumerate(frames, 1):
            results = self(frame)
            if save_detection_image:
                # Saving the detection results
                logger.debug("Saving detection results for frame %s...", i)
                detected_img_path = os.path.join("detection_output", f"frame_{i}.jpg")
                # Needs to be saved first as save_detection_images expects a path inside results

                # Convert the NumPy array to a PIL Image and save it
                Image.fromarray(frame).save(detected_img_path)

                yield detected_img_path
            else:
                yield None

        # It will track the objects and count them at the end of the video
        # Result is in the form of a dictionary of classwise counts
        return results.classwise_count

    def process_tunnel_mode_video(self, video_path, output_dir):
        """
        Processes a video in tunnel mode:
        - If at least one detection of 'animal' occurs, saves all annotated frames to an MP4 video.
        - Returns the total in/out object counts and the output video path
        (or None if no detection).

        Args:
            video_path (str): Path to the input video.
            output_dir (str): Directory where to save the output video.

        Returns:
            dict: {
                'in_count': int,
                'out_count': int,
                'video_path': str | None
            }
        """
        logger.info("Running tunnel mode detection on video %s ...", video_path)

        # Load all frames from the video
        frames = self.get_video_frames(video_path)
        if not frames:
            logger.error("No frames loaded. Exiting processing.")
            return {"in_count": 0, "out_count": 0, "video_path": None}

        # Initialize region of interest
        self.init_region(frames)

        # Get video FPS and frame size
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_size = (frames[0].shape[1], frames[0].shape[0])
        cap.release()

        annotated_frames = []
        detection_found = False

        for frame in frames:
            results = self(frame)  # Run detection and tracking

            # Get animal class counts (IN and OUT)
            animal_counts = results.classwise_count.get("animal", {})
            total_animals = animal_counts.get("IN", 0) + animal_counts.get("OUT", 0)

            if total_animals > 0:
                detection_found = True

            annotated_frames.append(frame)

        # Save video if animal(s) detected
        if detection_found:
            input_basename = os.path.basename(video_path)
            filename_wo_ext = os.path.splitext(input_basename)[0]
            output_path = os.path.join(output_dir, f"{filename_wo_ext}.mp4")

            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            logger.info("Animals detected. Saving annotated video to %s", output_path)

            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            out = cv2.VideoWriter(output_path, fourcc, fps, frame_size)

            for annotated_frame in annotated_frames:
                out.write(annotated_frame)

            out.release()
            video_result_path = output_path
        else:
            logger.info("No animal detections found. Skipping video save.")
            video_result_path = None

        # Return in/out counts and video path
        return {
            "in_count": self.in_count,
            "out_count": self.out_count,
            "video_path": video_result_path,
        }
