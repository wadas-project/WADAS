import logging
from pathlib import Path

import cv2

logger = logging.getLogger(__name__)


def create_browser_compatible_video_writer(
    output_path: str | Path, fps: float, frame_size: tuple[int, int]
):
    output_path = str(output_path)
    codec_candidates = ("avc1", "H264", "X264", "mp4v")

    for codec in codec_candidates:
        writer = cv2.VideoWriter(
            output_path,
            cv2.VideoWriter_fourcc(*codec),
            fps,
            frame_size,
        )
        if writer.isOpened():
            logger.info("Video writer initialized with codec %s for %s", codec, output_path)
            return writer
        writer.release()

    raise RuntimeError(f"Unable to initialize video writer for {output_path}")
