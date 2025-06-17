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
# Date: 2024-08-16
# Description: Module containing Tunnel mode methods.

import logging
import os
from pathlib import Path
from queue import Empty

from wadas.ai.object_counter import ObjectCounter
from wadas.ai.openvino_model import __model_folder__
from wadas.domain.camera import media_queue
from wadas.domain.operation_mode import OperationMode
from wadas.domain.tunnel import Tunnel

logger = logging.getLogger(__name__)
module_dir_path = os.path.dirname(os.path.abspath(__file__))


class TunnelMode(OperationMode):
    def __init__(self):
        super().__init__()
        self.type = OperationMode.OperationModeTypes.TunnelMode
        self.process_queue = True
        self.model_path = Path(__model_folder__) / "detection" / "MDV6b-yolov9c_openvino_model"

    def run(self):
        """Method to run Tunnel Mode."""
        logger.info("Starting Tunnel Mode...")
        self._initialize_cameras()
        self.check_for_termination_requests()

        # Run video processing
        while self.process_queue:
            self.check_for_termination_requests()
            # Get media (videos) from motion detection notification
            # Timeout is set to 1 second to avoid blocking the thread
            try:
                cur_media = media_queue.get(timeout=1)
            except Empty:
                cur_media = None

            # Video processing
            if cur_media and OperationMode.is_video(cur_media["media_path"]):
                logger.debug("Processing video from motion detection notification...")

                self.check_for_termination_requests()
                video_path = cur_media["media_path"]
                cur_tunnel = None
                tunnel_entrance_direction = None
                # Get tunnel associated to camera providing video
                camera_id = cur_media["camera_id"]
                for tunnel in Tunnel.tunnels:
                    if camera_id == tunnel.camera_entrance_1:
                        tunnel_entrance_direction = tunnel.entrance_1_direction
                        cur_tunnel = tunnel
                    elif camera_id == tunnel.camera_entrance_2:
                        tunnel_entrance_direction = tunnel.entrance_1_direction
                        cur_tunnel = tunnel

                if not tunnel_entrance_direction or not cur_tunnel:
                    logger.error(
                        "Unable to match camera ID with any enabled tunnel, skipping processing."
                    )
                    continue

                self.check_for_termination_requests()
                obj_counter = ObjectCounter(
                    show=False,
                    region=tunnel_entrance_direction,
                    model=self.model_path,
                    classes=[0],
                )
                output_dir = Path(module_dir_path) / ".." / ".." / "detection_output"
                results = obj_counter.process_tunnel_mode_video(video_path, output_dir)

                self.check_for_termination_requests()
                if results and (output_video_path := results["video_path"]):
                    logger.info("Animal detected in video %s", video_path)
                    self.update_image.emit(output_video_path)
                    self.update_info.emit()
                    if in_count := results["in_count"]:
                        cur_tunnel.counter -= in_count
                        logger.info("Detected animal leaving the tunnel.")
                        self.update_tunnel_counter.emit()
                    elif out_count := results["out_count"]:
                        cur_tunnel.counter += out_count
                        logger.info("Detected animal entering the tunnel.")
                        self.update_tunnel_counter.emit()

                # TODO: implement notification
                self.check_for_termination_requests()
