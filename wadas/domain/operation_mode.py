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
# Description: Module containing class to handle WADAS operation modes.

import logging
import os
import threading
import time
from abc import abstractmethod
from enum import Enum

from PySide6.QtCore import QObject, Signal

from wadas.domain.actuation_event import ActuationEvent
from wadas.domain.actuator import Actuator
from wadas.domain.ai_model import AiModel
from wadas.domain.camera import Camera, cameras
from wadas.domain.database import DataBase
from wadas.domain.detection_event import DetectionEvent
from wadas.domain.fastapi_actuator_server import (
    FastAPIActuatorServer,
    initialize_fastapi_logger,
)
from wadas.domain.ftps_server import FTPsServer
from wadas.domain.notifier import Notifier
from wadas.domain.utils import get_precise_timestamp, is_image

logger = logging.getLogger(__name__)


class OperationMode(QObject):
    """Class to handle WADAS operation modes."""

    class OperationModeTypes(Enum):
        TestModelMode = "Test Model Mode"
        AnimalDetectionMode = "Animal Detection Mode"
        AnimalDetectionAndClassificationMode = "Animal Detection and Classification Mode"
        TunnelMode = "Tunnel Mode"
        BearDetectionMode = "Bear Detection Mode"
        CustomSpeciesClassificationMode = "Custom Species Classification Mode"

    # Currently selected operation mode
    cur_operation_mode = None
    cur_operation_mode_type = None  # We need this separately as object is deleted after op_mode run
    cur_custom_classification_species = None

    # Signals
    update_image = Signal(object)
    update_actuator_status = Signal()
    update_info = Signal()
    run_finished = Signal()
    run_progress = Signal(int)
    play_video = Signal(str)
    error_occurred = Signal(str)
    update_tunnel_counter = Signal()

    flag_stop_update_actuators_thread = False
    enforce_privacy_remove_original_img = False
    enforce_privacy_remove_detection_img = False
    enforce_privacy_remove_classification_img = False
    enforce_privacy_blur_non_animals = True

    def __init__(self):
        super(OperationMode, self).__init__()
        self.type = None
        self.ai_model = None
        self.last_detection = ""
        self.last_classified_animals_str = ""
        self.camera_thread = []
        self.ftp_thread = None
        self.actuators_server_thread = None
        self.actuators_view_thread = None
        self.enable_classification = False
        self.is_notifier_enabled = Notifier.notifier_enabled()

    def init_model(self):
        """Method to run the selected WADAS operation mode"""

        if self.ai_model is None:
            logger.info("initializing model...")
            try:
                self.ai_model = AiModel()
            except Exception as e:
                self.error_occurred.emit(str(e))
                return False
        else:
            logger.debug("Model already initialized, skipping initialization.")
        return True

    def _initialize_cameras(self):
        """Method to initialize and run the FTP Server
        and threads associated to the cameras (both ftp and usb)"""
        logger.info("Instantiating cameras...")
        camera: Camera
        for camera in cameras:
            if camera.enabled:
                if camera.type == Camera.CameraTypes.USB_CAMERA:
                    # Create thread for motion detection
                    logger.info("Instantiating thread for camera %s", camera.id)
                    camera.stop_thread = False
                    self.camera_thread.append(camera.run())
                elif (
                    camera.type == Camera.CameraTypes.FTP_CAMERA
                    and FTPsServer.ftps_server
                    and not self.ftp_thread
                ):
                    logger.info("Instantiating FTPS server...")
                    self.ftp_thread = FTPsServer.ftps_server.run()
        logger.info("Ready for video stream from Camera(s)...")

    def _detect(self, cur_media):
        """Method to run the animal detection process on a specific image"""

        if is_image(cur_media["media_path"]):
            results, detected_img_path = self.ai_model.process_image(cur_media["media_path"], True)

            if results and detected_img_path:
                detection_event = DetectionEvent(
                    camera_id=cur_media["camera_id"],
                    time_stamp=get_precise_timestamp(),
                    original_media=cur_media["media_path"],
                    detection_media_path=detected_img_path,
                    detected_animals=results,
                    classification=self.enable_classification,
                )
                self.last_detection = detected_img_path
                # Insert detection event into db, if enabled
                if db := DataBase.get_enabled_db():
                    db.insert_into_db(detection_event)

                if self.enable_classification:
                    # Classify animal
                    self._classify(detection_event)

                return detection_event
            else:
                return None
        else:
            # Video processing
            tracked_animals, video_path, snapshot = self.ai_model.process_video_offline(
                video_path=cur_media["media_path"],
                classification=self.enable_classification,
                save_processed_video=True,
                save_snapshot=self.is_notifier_enabled,
            )
            if video_path:
                detection_path = video_path if not self.enable_classification else ""
                classification_path = video_path if self.enable_classification else ""
                classified_animals = (
                    self.ai_model.classification_from_video_tracking(tracked_animals)
                    if tracked_animals
                    else [
                        {
                            "class_probs": {},
                            "classification": [],
                            "id": 0,
                            "xyxy": [],
                        }
                    ]
                )

                detection_event = DetectionEvent(
                    camera_id=cur_media["camera_id"],
                    time_stamp=get_precise_timestamp(),
                    original_media=cur_media["media_path"],
                    detection_media_path=detection_path,
                    detected_animals={
                        "detections": None,
                        "img_id": "",
                        "labels": [],
                    },  # TODO: evaluate if store actual detection results in video processing
                    classification=self.enable_classification,
                    classification_media_path=classification_path,
                    classified_animals=classified_animals,
                    preview_image=snapshot,
                )
                self.last_detection = video_path
                self._format_classified_animals_string(classified_animals)

                # Insert detection event into db, if enabled
                if db := DataBase.get_enabled_db():
                    db.insert_into_db(detection_event)

                return detection_event
            else:
                return None

    def _format_classified_animals_string(self, classified_animals):
        """Prepare a list of classified animals to print in UI"""

        full_str = ", ".join(
            animal["classification"][0]
            for animal in classified_animals
            if animal.get("classification")
        )
        self.last_classified_animals_str = (
            full_str[:100] + "..." if len(full_str) > 100 else full_str
        )

    def _classify(self, detection_event: DetectionEvent):
        """Method to run the animal classification process
        on a specific image starting from the detection output"""

        # Classify if detection has identified animals
        if len(detection_event.detected_animals["detections"].xyxy):
            logger.info("Running classification on detection result(s)...")
            (
                classified_img_path,
                classified_animals,
            ) = self.ai_model.classify(
                detection_event.original_image, detection_event.detected_animals
            )
            if classified_img_path and classified_animals:
                self.last_detection = classified_img_path
                self._format_classified_animals_string(classified_animals)
                detection_event.classified_animals = classified_animals
                detection_event.classification_media_path = classified_img_path
                # Update detection event into db, if enabled
                if db := DataBase.get_enabled_db():
                    db.update_detection_event(detection_event)
            else:
                logger.debug("No classified animals or classification results below threshold.")

    def _show_processed_results(self, detection_event):
        """Method to show Ai inference results in WADAS UI"""

        if detection_event:
            if self.enable_classification:
                # Classification is enabled
                if detection_event.classification_media_path:
                    # Trigger image update in WADAS mainwindow with classification result
                    if is_image(detection_event.classification_media_path):
                        self.update_image.emit(detection_event.classification_media_path)
                    else:
                        self.play_video.emit(detection_event.classification_media_path)
                else:
                    logger.info("No animal classified.")
            else:
                # Trigger image update in WADAS mainwindow with detection result
                if is_image(detection_event.detection_media_path):
                    self.update_image.emit(detection_event.detection_media_path)
                else:
                    self.play_video.emit(detection_event.detection_media_path)
            self.update_info.emit()
        else:
            logger.info("No animal detected.")

    def ftp_camera_exist(self):
        """Method that returns True if at least an FTP camera exists, False otherwise."""

        return any(camera.type == Camera.CameraTypes.FTP_CAMERA for camera in cameras)

    def check_for_termination_requests(self):
        """Terminate current thread if interrupt request comes from Mainwindow."""

        if self.thread().isInterruptionRequested():
            logger.info("Request to stop received. Aborting...")
            # Stop FTPS Server (if running)
            if self.ftp_camera_exist() and self.ftp_thread and FTPsServer.ftps_server:
                FTPsServer.ftps_server.server.close_all()
                FTPsServer.ftps_server.server.close()
                self.ftp_thread.join()
            # Stop USB Cameras thread(s), if any.
            self.process_queue = False
            for camera in cameras:
                if camera.type == Camera.CameraTypes.USB_CAMERA:
                    camera.stop_thread = True

            self.stop_actuator_server()

            self.run_finished.emit()
            return

    def _initialize_processes(self):
        """Method to initialize the processes needed for the detection"""

        if self.init_model():
            self.check_for_termination_requests()
            self._initialize_cameras()
            self.start_actuator_server()
        else:
            self.execution_completed()

    def send_notification(self, detection_event: DetectionEvent, message):
        """Method to send notification(s) trough Notifier class (and subclasses)"""

        Notifier.send_notifications(detection_event, message)

    def actuate(self, detection_event: DetectionEvent):
        """Method to trigger actuators associated to the camera, when enabled"""

        cur_camera = None
        for cur_camera in cameras:
            if cur_camera.id == detection_event.camera_id:
                break
        if cur_camera:
            for actuator in cur_camera.actuators:
                if actuator.enabled:
                    actuation_event = ActuationEvent(
                        actuator.id, get_precise_timestamp(), detection_event
                    )
                    logger.info("Running actuation for actuator %s.", actuator.id)
                    actuator.actuate(actuation_event)
                    # Insert actuation event into db, if enabled
                    if db := DataBase.get_enabled_db():
                        db.insert_into_db(actuation_event)

    def delete_media(self, media_file):
        """Method to delete media file handling possible exceptions."""

        if os.path.isfile(media_file):
            try:
                os.remove(media_file)

                logger.debug("%s media removed successfully.", media_file)
            except FileNotFoundError:
                logger.error("%s does not exist", media_file)
            except PermissionError:
                logger.error("No permission to delete %s", media_file)
            except OSError:
                logger.error("OS Error deleting file: %s", media_file)

    def enforce_privacy(self, detection_event):
        """Method to enforce privacy by deleting unneeded images."""

        if OperationMode.enforce_privacy_remove_original_img and os.path.isfile(
            detection_event.original_image
        ):
            logger.debug("Removing original image due to privacy enforcement policy.")
            self.delete_media(detection_event.original_image)
        if (
            OperationMode.enforce_privacy_remove_detection_img
            and os.path.isfile(detection_event.detection_media_path)
            and self.enable_classification  # Detection img is deleted only in class mode.
        ):
            logger.debug("Removing detection image due to privacy enforcement policy.")
            self.delete_media(detection_event.detection_media_path)
        if (
            self.enable_classification
            and OperationMode.enforce_privacy_remove_classification_img
            and detection_event.classification_media_path
        ):
            self.delete_media(detection_event.classification_media_path)
            logger.debug("Removing classification image due to privacy enforcement policy.")

    def execution_completed(self):
        """Method to perform end of execution steps."""

        self.run_finished.emit()
        self.stop_ftp_server()
        logger.info("Done with processing.")

    def stop_ftp_server(self):
        """Method to stop FTP server thread"""

        if self.ftp_thread and FTPsServer.ftps_server:
            FTPsServer.ftps_server.server.close_all()
            FTPsServer.ftps_server.server.close()
            self.ftp_thread.join()

    def _scheduled_update_actuators_trigger(self):
        """Method to trigger the actuator(s) view update every 5 secs"""

        while not self.flag_stop_update_actuators_thread:
            time.sleep(5)
            self.update_actuator_status.emit()

    def start_actuator_server(self):
        """Method to start the HTTPS Actuator Server"""

        if Actuator.actuators and FastAPIActuatorServer.actuator_server:
            initialize_fastapi_logger()
            logger.info("Instantiating HTTPS Actuator server...")
            self.actuators_server_thread = FastAPIActuatorServer.actuator_server.run()
            self.actuators_view_thread = self.start_update_actuators_thread()
        else:
            logger.info("No actuator or actuator server defined")

    def start_update_actuators_thread(self):
        """Start the thread responsible for keeping the actuator(s) view updated"""

        update_thread = threading.Thread(target=self._scheduled_update_actuators_trigger)
        if update_thread:
            update_thread.start()
            logger.info("Starting thread for update actuators view...")
        else:
            logger.error("Unable to create new thread for update actuators view.")
        return update_thread

    def stop_update_actuators_thread(self):
        """Method to stop the thread responsible for keeping the actuator(s) view updated"""

        self.flag_stop_update_actuators_thread = True
        if self.actuators_view_thread:
            self.actuators_view_thread.join()

    def stop_actuator_server(self):
        """Method to Stop HTTPS Actuator Server"""

        if FastAPIActuatorServer.actuator_server:
            self.stop_update_actuators_thread()
            FastAPIActuatorServer.actuator_server.stop()
            if self.actuators_server_thread:
                self.actuators_server_thread.join()

    @abstractmethod
    def run(self):
        """Method to run the specific operation mode."""
