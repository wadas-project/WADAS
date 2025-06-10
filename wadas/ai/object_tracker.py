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
# Date: 2025-03-14
# Description: Module containing object tracker logic.

import numpy as np
from scipy.optimize import linear_sum_assignment


class KalmanFilter:
    """Kalman filter for smoothing detection coordinates or class probabilities"""

    def __init__(
        self,
        initial_value: list | np.ndarray,
        process_variance: float = 1,
        measurement_variance: float = 10,
        extra: dict[any] = None,
    ):
        """
        Initializes the object tracker with the given parameters.
        Args:
            initial_value (list or np.array): Initial state estimate [x, y, vx, vy].
            process_variance (float, optional): Variance of the process noise.
            measurement_variance (float, optional): Variance of the measurement noise.
            extra (optional): Any additional parameters or configurations.
        Attributes:
            x (np.array): State estimate [x, y, vx, vy].
            dim (int): Dimension of the state.
            P float: Initial uncertainty covariance matrix.
            Q float: Process noise covariance matrix.
            R float: Measurement noise covariance matrix.
            extra: Any additional parameters or configurations.
        """

        self.x = np.array(initial_value, dtype=np.float32)  # State estimate [x, y, vx, vy]
        self.dim = len(initial_value) // 2  # Dimension of state
        self.P = np.eye(len(initial_value)) * 100.0  # Initial uncertainty
        self.Q = np.eye(len(initial_value)) * process_variance  # Process noise
        self.R = np.eye(len(initial_value[: self.dim])) * measurement_variance  # Measurement noise
        self.extra = extra

    def update(self, measurement: np.ndarray) -> np.ndarray:
        """
        Updates the state estimate and covariance matrix of the object tracker
        using the provided measurement.
        Args:
            measurement (np.array): The new measurement to update the state with.
        Returns:
            numpy.ndarray: The updated state estimate.
        """

        # Prediction
        for i in range(self.dim):
            self.x[i] += self.x[self.dim + i]  # Update position with velocity
        self.P += self.Q

        # Kalman Gain
        K = self.P[: self.dim, : self.dim] @ np.linalg.inv(self.P[: self.dim, : self.dim] + self.R)

        # Update state estimate
        self.x[: self.dim] += K @ (np.array(measurement) - self.x[: self.dim])
        self.P[: self.dim, : self.dim] = (np.eye(self.dim) - K) @ self.P[: self.dim, : self.dim]

        return self.x


def compute_iou(box1: list[int], box2: list[int]) -> float:
    """
    Compute the Intersection over Union (IoU) of two bounding boxes.
    Parameters:
    box1 (list[int]): A list of four integers representing the
                      first bounding box in the format [x1, y1, x2, y2].
    box2 (list[int]): A list of four integers representing the
                      second bounding box in the format [x1, y1, x2, y2].
    Returns:
    float: The IoU of the two bounding boxes.
    """
    x1, y1, x2, y2 = box1
    x1_p, y1_p, x2_p, y2_p = box2

    xi1, yi1 = max(x1, x1_p), max(y1, y1_p)
    xi2, yi2 = min(x2, x2_p), min(y2, y2_p)
    inter_area = max(0, xi2 - xi1) * max(0, yi2 - yi1)

    box1_area = (x2 - x1) * (y2 - y1)
    box2_area = (x2_p - x1_p) * (y2_p - y1_p)
    union_area = box1_area + box2_area - inter_area

    return inter_area / union_area


class ObjectTracker:
    """Tracks objects and smooths their class predictions over time"""

    def __init__(
        self,
        process_var: float = 30,
        measurement_var: float = 1,
        class_process_var: float = 0.00,
        class_measurement_var: float = 0.1,
        max_missed: int = 5,
    ):
        """
        Initializes the ObjectTracker with the given parameters.
        Args:
            process_var (float): The process variance for the Kalman filter.
            measurement_var (float): The measurement variance for the Kalman filter.
            class_process_var (float): The process variance for the class smoother.
            class_measurement_var (float): The measurement variance for the class smoother.
            max_missed (int): The maximum number of missed detections before
                              an object is considered lost.
        """
        self.trackers = {}  # ObjectID -> (KalmanFilter, KalmanClassSmoother, missed_count)
        self.next_id = 0

        # Kalman filter settings
        self.process_var = process_var
        self.measurement_var = measurement_var
        self.class_process_var = class_process_var
        self.class_measurement_var = class_measurement_var
        self.max_missed = max_missed

    def compute_centroid(self, xyxy: list[int]) -> tuple[int]:
        """
        Compute the centroid of a bounding box.
        Args:
            xyxy (list[int]): A list of four integers representing the coordinates
                              of the bounding box in the format [x1, y1, x2, y2].
        Returns:
            tuple[int]: A tuple containing the x and y coordinates of the centroid.
        """

        return (xyxy[0] + xyxy[2]) / 2, (xyxy[1] + xyxy[3]) / 2

    def associate_detections(self, detections: list[dict[any]]) -> dict[int]:
        """
        Associates detected objects with existing trackers using the Hungarian algorithm.
        This method takes a dictionary of detections and assigns each detection an ID.
        If there are no existing trackers, new IDs are assigned to all detections.
        If there are existing trackers, the method computes the Intersection over Union (IoU)
        between each tracker and detection, and uses the Hungarian algorithm to find the
        optimal assignment of detections to trackers. Detections that do not match any
        existing tracker with an IoU above a certain threshold are assigned new IDs.
        Args:
            detections (list[dict[any]]): A list of detected objects, where each item is
                                          a dictionary containing the bounding box coordinates
                                          under the key "xyxy" and the class probabilities
        Returns:
            dict[int]: A dictionary mapping each detection index to a tracker ID.
        """

        if not self.trackers:
            return {i: self.next_id + i for i in range(len(detections))}  # Assign new IDs

        # Compute IoU matrix
        track_ids = tuple(self.trackers)
        track_boxes = []
        for t in track_ids:
            h, w = self.trackers[t][0].extra["h"], self.trackers[t][0].extra["w"]
            x, y, _, __ = self.trackers[t][0].x
            xyxy = [x - w / 2, y - h / 2, x + w / 2, y + h / 2]
            track_boxes.append(xyxy)
        detected_boxes = [det["xyxy"] for det in detections]

        iou_matrix = np.zeros((len(track_boxes), len(detected_boxes)))
        for i, track_box in enumerate(track_boxes):
            for j, detected_box in enumerate(detected_boxes):
                iou_matrix[i, j] = compute_iou(track_box, detected_box)

        # Hungarian algorithm for optimal assignment
        row_ind, col_ind = linear_sum_assignment(-iou_matrix)

        # Assign IDs
        matches = {}
        for r, c in zip(row_ind, col_ind):
            if iou_matrix[r, c] > 0.1:  # Threshold for same object
                matches[c] = track_ids[r]
            else:
                matches[c] = self.next_id
                self.next_id += 1

        for j in range(len(detected_boxes)):
            if j not in col_ind:
                matches[j] = self.next_id
                self.next_id += 1

        return matches

    def update(self, detections: list[dict[any]], img_size: tuple[int]) -> list[dict[any]]:
        """
        Updates the object tracker with the given detections.
        Args:
            detections (list[dict[any]]): A list of detected objects, where each item is a dict
                                          containing the bounding box coordinates under the
                                          key "xyxy" and the class probabilities
            img_size (tuple[int]): The size of the image frame.
        Returns:
            list[dict[any]]: A list of updated tracks, where each track is a dictionary
                             containing the track ID, the smoothed bounding box coordinates
                             under the key "xyxy", and the smoothed class probabilities.
        """

        frame_width, frame_height = img_size
        # Compute the detections
        matches = self.associate_detections(detections)

        updated_tracks = []
        for det_idx, obj_id in matches.items():
            xyxy = detections[det_idx]["xyxy"]
            class_probs = detections[det_idx]["class_probs"]

            # Compute centroid
            x, y = self.compute_centroid(xyxy)
            h, w = xyxy[3] - xyxy[1], xyxy[2] - xyxy[0]

            if obj_id not in self.trackers:
                self.trackers[obj_id] = (
                    KalmanFilter(
                        [x, y, 0, 0], self.process_var, self.measurement_var, extra={"h": h, "w": w}
                    ),  # Position tracker with speed
                    {
                        cls: KalmanFilter(
                            [p, 0], self.class_process_var, self.class_measurement_var
                        )
                        for cls, p in class_probs.items()
                    },  # Class smoothers
                    0,  # Missed count
                )
            else:
                self.trackers[obj_id][0].extra = {"h": h, "w": w}
                self.trackers[obj_id] = (
                    self.trackers[obj_id][0],
                    self.trackers[obj_id][1],
                    0,
                )  # Reset missed count

            # Update position
            position_filter = self.trackers[obj_id][0]
            smoothed_pos = position_filter.update([x, y])

            # Convert smoothed_pos to xyxy
            smoothed_pos = [
                smoothed_pos[0] - w / 2,
                smoothed_pos[1] - h / 2,
                smoothed_pos[0] + w / 2,
                smoothed_pos[1] + h / 2,
            ]

            # Convert to int
            smoothed_pos = [int(p) for p in smoothed_pos]

            # Update classification
            class_filters = self.trackers[obj_id][1]
            smoothed_probs = {
                cls: class_filters[cls].update([p])[0] for cls, p in class_probs.items()
            }

            # Build classification result
            logits = np.array(list(smoothed_probs.values()))
            labels = tuple(smoothed_probs)
            classification_result = labels[np.argmax(logits)], max(logits)

            updated_tracks.append(
                {"id": obj_id, "classification": classification_result, "xyxy": smoothed_pos}
            )

        # Increment missed count for unmatched trackers
        for obj_id in self.trackers:
            if obj_id not in [track["id"] for track in updated_tracks]:
                self.trackers[obj_id] = (
                    self.trackers[obj_id][0],
                    self.trackers[obj_id][1],
                    self.trackers[obj_id][2] + 1,
                )
                if self.trackers[obj_id][2] <= self.max_missed:
                    # Process unmatched tracked objects
                    position_filter = self.trackers[obj_id][0]
                    smoothed_pos = position_filter.update(position_filter.x[:2])

                    # Convert smoothed_pos to xyxy
                    h, w = position_filter.extra["h"], position_filter.extra["w"]
                    smoothed_pos = [
                        smoothed_pos[0] - w / 2,
                        smoothed_pos[1] - h / 2,
                        smoothed_pos[0] + w / 2,
                        smoothed_pos[1] + h / 2,
                    ]

                    # Convert to int
                    smoothed_pos = [int(p) for p in smoothed_pos]

                    # Update classification
                    class_filters = self.trackers[obj_id][1]
                    smoothed_probs = {
                        cls: class_filters[cls].update([class_filters[cls].x[0]])[0]
                        for cls in class_filters
                    }

                    # Build classification result
                    logits = np.array(list(smoothed_probs.values()))
                    labels = tuple(smoothed_probs)
                    classification_result = labels[np.argmax(logits)], max(logits)

                    updated_tracks.append(
                        {
                            "id": obj_id,
                            "classification": classification_result,
                            "xyxy": smoothed_pos,
                        }
                    )

        # Remove lost tracks
        self.trackers = {
            k["id"]: self.trackers[k["id"]]
            for k in updated_tracks
            if self.trackers[k["id"]][2] <= self.max_missed
            and not (
                k["xyxy"][0] <= 5
                or k["xyxy"][1] <= 5
                or k["xyxy"][2] >= frame_width - 5
                or k["xyxy"][3] >= frame_height - 5
            )
        }

        return updated_tracks
