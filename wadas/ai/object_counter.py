import os

import numpy as np
from ultralytics import solutions

from wadas.ai.ov_predictor import __model_folder__, load_ov_model


class ObjectCounter(solutions.ObjectCounter):

    def __init__(
        self,
        model: str,
        region: list[tuple[int, int]],
        classes: list[int] = None,
        device: str = "auto",
        batch_size: int = 1,
        iou_threshold: float = 0.5,
        confidence_threshold: float = 0.3,
        **kwargs
    ):
        """
        Initializes the ObjectCounter class.
        Args:
            model (str): Path to the model file.
            region (list[tuple[int, int]]): List of tuples defining the region of interest.
                                            It is possible to define a line or a polygon
            classes (list[int]): List of class indices to be counted.
            device (str, optional): Device to run the model on. Defaults to "auto".
            batch_size (int, optional): Number of images to process in a batch. Defaults to 1.
            **kwargs: Additional keyword arguments.
        """
        model = os.path.join(__model_folder__, model)
        super().__init__(
            model=model,
            region=region,
            classes=classes,
            batch_size=batch_size,
            iou=iou_threshold,
            conf=confidence_threshold,
            **kwargs
        )
        self.model.predictor.model.ov_compiled_model = load_ov_model(model, device)

    def process_frames(self, frames: list[np.ndarray]) -> dict:
        """
        Processes a single frame.
        Args:
            frame (np.ndarray): Input frame.
        Returns:
            np.ndarray: Processed frame.
        """
        for frame in frames:
            results = self.__call__(frame)

        # It will track the objects and count them at the end of the video
        # Result is in the form of a dictionary of classwise counts
        return results.classwise_count
