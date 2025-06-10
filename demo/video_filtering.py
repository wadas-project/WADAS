from wadas.domain.ai_model import AiModel
from wadas.ai.object_tracker import ObjectTracker
import argparse


import numpy as np
import cv2
from PIL import Image


def draw_bbox(frame, animal, color=(0, 0, 255)):
    """Draw bounding box on frame"""
    x1, y1, x2, y2 = animal["xyxy"]
    # label = f"[{animal['id']}] {animal['classification'][0]}: {animal['classification'][1]:.2f}"
    label = animal["classification"][0]
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
    cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)


def main(video):

    ai_pipeline = AiModel()
    ai_pipeline.classification_threshold = 0.0
    ai_pipeline.detection_threshold = 0.0
    ai_pipeline.video_fps = 10

    tracker = ObjectTracker(max_missed=10)
    for result, _detected_image_path, frame_path in ai_pipeline.process_video(video, True):
        frame = np.array(Image.open(frame_path).convert("RGB"))
        frame_copy = frame.copy()

        _, classified_animals = ai_pipeline.classify(frame_path, result)

        if classified_animals:
            for animal in classified_animals:
                draw_bbox(frame, animal)

        tracked_animal = tracker.update(classified_animals, frame.shape[:2])

        if tracked_animal:
            for animal in tracked_animal:
                draw_bbox(frame_copy, animal)

        cv2.imshow("Detection & Classification", frame)
        cv2.imshow("Detection & Classification with Tracking", frame_copy)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("video", type=str)
    args = parser.parse_args()
    main(args.video)
