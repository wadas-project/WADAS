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
# Date: 2024-06-11
# Description: WADAS configuration module.

import logging
import os
import traceback

import keyring
import openvino as ov
import yaml
from packaging.version import Version

from wadas._version import __version__
from wadas.domain.actuator import Actuator
from wadas.domain.ai_model import AiModel
from wadas.domain.camera import Camera, cameras
from wadas.domain.database import DataBase
from wadas.domain.email_notifier import EmailNotifier
from wadas.domain.fastapi_actuator_server import FastAPIActuatorServer
from wadas.domain.feeder_actuator import FeederActuator
from wadas.domain.ftp_camera import FTPCamera
from wadas.domain.ftps_server import FTPsServer
from wadas.domain.notifier import Notifier
from wadas.domain.operation_mode import OperationMode
from wadas.domain.roadsign_actuator import RoadSignActuator
from wadas.domain.telegram_notifier import TelegramNotifier
from wadas.domain.usb_camera import USBCamera
from wadas.domain.whatsapp_notifier import WhatsAppNotifier

logger = logging.getLogger(__name__)

_OPERATION_MODE_TYPE_VALUE_TO_TYPE = {mode.value: mode for mode in OperationMode.OperationModeTypes}


def check_version_compatibility(config_file_version):
    wadas_version = Version(__version__.lstrip("v"))

    if wadas_version == config_file_version:
        return True
    if wadas_version < config_file_version:
        return False
    if wadas_version > config_file_version:
        # Example of compatibility check to list here:
        if config_file_version == Version("0.5.1") and wadas_version == Version("0.6.0"):
            return True
        # NOTE: prerequisite to this is that new yaml keys, absent in previous version, are handled
        # at load_configuration_from_file() time.
        return False


def load_configuration_from_file(file_path):
    """Load configuration from YAML file."""

    load_status = {
        "errors_on_load": False,
        "errors_log": "",
        "config_version": None,
        "compatible_config": True,
        "valid_ftp_keyring": True,
        "valid_email_keyring": True,
        "valid_whatsapp_keyring": True,
        "uuid": "",
    }

    with open(str(file_path)) as file_:
        logging.info("Loading configuration from file...")
        wadas_config = yaml.safe_load(file_)

    # Applying configuration to WADAS from config file values
    try:
        # Uuid
        load_status["uuid"] = wadas_config["uuid"]

        # Version
        config_file_version = Version(wadas_config["version"].lstrip("v"))
        load_status["config_version"] = config_file_version
        load_status["compatible_config"] = check_version_compatibility(config_file_version)

        # If version of provided configuration file is not compatible we return aborting
        # deserialization process.
        if not load_status["compatible_config"]:
            logger.error(
                "Provided WADAS configuration version is not compatible with current "
                "version of WADAS. "
                "Aborting configuration load."
            )
            return load_status

        # Notifiers
        for key, value in (wadas_config["notification"] or {}).items():
            if key in Notifier.notifiers and key == Notifier.NotifierTypes.EMAIL.value:
                email_notifier = EmailNotifier(**value)
                Notifier.notifiers[key] = email_notifier
                credentials = keyring.get_credential("WADAS_email", email_notifier.sender_email)
                if not credentials:
                    logger.error(
                        "Unable to find email credentials for %s stored on the system."
                        "Please insert them through email configuration dialog.",
                        email_notifier.sender_email,
                    )
                    load_status["valid_email_keyring"] = False
                elif credentials and credentials.username != email_notifier.sender_email:
                    logger.error(
                        "Email username on the system (%s) does not match with username "
                        "provided in configuration file (%s). Please make sure valid email "
                        "credentials are in use by editing them from email configuration "
                        "dialog.",
                        credentials.username,
                        email_notifier.sender_email,
                    )
                    load_status["valid_email_keyring"] = False
            elif key in Notifier.notifiers and key == Notifier.NotifierTypes.WHATSAPP.value:
                whatsapp_notifier = WhatsAppNotifier(**value)
                Notifier.notifiers[key] = whatsapp_notifier
                credentials = keyring.get_credential("WADAS_WhatsApp", whatsapp_notifier.sender_id)
                if not credentials:
                    logger.error(
                        "Unable to find WhatsApp credentials for %s stored on the system. "
                        "Please insert them through WhatsApp configuration dialog.",
                        whatsapp_notifier.sender_id,
                    )
                    load_status["valid_whatsapp_keyring"] = False
                elif credentials and credentials.username != whatsapp_notifier.sender_id:
                    logger.error(
                        "WhatsApp sender ID on the system (%s) does not match with sender ID "
                        "provided in configuration file (%s). Please make sure valid WhatsApp "
                        "credentials are in use by editing them from WhatsApp configuration "
                        "dialog.",
                        credentials.username,
                        whatsapp_notifier.sender_id,
                    )
                    load_status["valid_whatsapp_keyring"] = False
            elif key in Notifier.notifiers and key == Notifier.NotifierTypes.TELEGRAM.value:
                telegram_notifier = TelegramNotifier.deserialize(value)
                Notifier.notifiers[key] = telegram_notifier

        # FTP Server
        if FTPsServer.ftps_server and FTPsServer.ftps_server.server:
            FTPsServer.ftps_server.server.close_all()
        FTPsServer.ftps_server = (
            FTPsServer.deserialize(wadas_config["ftps_server"])
            if wadas_config["ftps_server"]
            else None
        )

        # Actuators
        Actuator.actuators.clear()
        for data in wadas_config["actuators"]:
            match data["type"]:
                case Actuator.ActuatorTypes.ROADSIGN.value:
                    actuator = RoadSignActuator.deserialize(data)
                    Actuator.actuators[actuator.id] = actuator
                case Actuator.ActuatorTypes.FEEDER.value:
                    actuator = FeederActuator.deserialize(data)
                    Actuator.actuators[actuator.id] = actuator

        # Camera(s)
        cameras.clear()
        for data in wadas_config["cameras"]:
            match data["type"]:
                case Camera.CameraTypes.USB_CAMERA.value:
                    usb_camera = USBCamera.deserialize(data)
                    cameras.append(usb_camera)
                case Camera.CameraTypes.FTP_CAMERA.value:
                    ftp_camera = FTPCamera.deserialize(data)
                    cameras.append(ftp_camera)
                    if FTPsServer.ftps_server:
                        if not os.path.isdir(ftp_camera.ftp_folder):
                            os.makedirs(ftp_camera.ftp_folder, exist_ok=True)
                        credentials = keyring.get_credential(
                            f"WADAS_FTP_camera_{ftp_camera.id}", ""
                        )
                        if credentials:
                            if credentials.username != ftp_camera.id:
                                logger.error(
                                    "Keyring stored user (%s) differs from configuration "
                                    "file one (%s)."
                                    " Please make sure to align system stored credential with"
                                    " configuration file. System credentials will be used.",
                                    ftp_camera.id,
                                    credentials.username,
                                )
                                load_status["valid_ftp_keyring"] = False
                            else:
                                FTPsServer.ftps_server.add_user(
                                    credentials.username,
                                    credentials.password,
                                    ftp_camera.ftp_folder,
                                )
                        else:
                            logger.error(
                                "Unable to find credentials for %s on this system. "
                                "Please add credentials manually from FTP Camera configuration "
                                "dialog.",
                                ftp_camera.id,
                            )
                            load_status["valid_ftp_keyring"] = False
        Camera.detection_params = wadas_config["camera_detection_params"]

        # FastAPI Actuator Server
        FastAPIActuatorServer.actuator_server = (
            FastAPIActuatorServer.deserialize(wadas_config["actuator_server"])
            if wadas_config["actuator_server"]
            else None
        )

        # Ai model
        available_ai_devices = ov.Core().get_available_devices()
        available_ai_devices.append("auto")
        AiModel.detection_model_version = wadas_config["ai_model"]["ai_detection_model_version"]
        AiModel.classification_model_version = wadas_config["ai_model"][
            "ai_classification_model_version"
        ]
        AiModel.detection_threshold = wadas_config["ai_model"]["ai_detect_threshold"]
        AiModel.classification_threshold = wadas_config["ai_model"]["ai_class_threshold"]
        AiModel.language = wadas_config["ai_model"]["ai_language"]
        detection_device = wadas_config["ai_model"]["ai_detection_device"]
        classification_device = wadas_config["ai_model"]["ai_classification_device"]
        AiModel.detection_device = (
            detection_device if detection_device in available_ai_devices else "auto"
        )
        AiModel.classification_device = (
            classification_device if classification_device in available_ai_devices else "auto"
        )
        AiModel.video_fps = wadas_config["ai_model"]["ai_video_fps"]

        # Operation Mode
        if operation_mode := wadas_config["operation_mode"]:
            operation_mode_type = _OPERATION_MODE_TYPE_VALUE_TO_TYPE.get(operation_mode["type"])
            OperationMode.cur_operation_mode_type = operation_mode_type
            if (
                operation_mode_type
                == OperationMode.cur_operation_mode_type.CustomSpeciesClassificationMode
            ):
                if operation_mode["custom_target_species"]:
                    OperationMode.cur_custom_classification_species = operation_mode[
                        "custom_target_species"
                    ]
                else:
                    logger.error("Custom target species not specified.")
                    load_status["errors_on_load"] = True
        else:
            OperationMode.cur_operation_mode = None

        # DataBase
        if database_cfg := wadas_config["database"]:
            if not DataBase.deserialize(database_cfg):
                logger.error("Unrecognized Database Type")
                load_status["errors_on_load"] = True
                load_status["errors_log"] = "Unrecognized Database Type"
                return load_status

    except Exception as e:
        load_status["errors_on_load"] = True
        load_status["errors_log"] = e
        logger.debug("Error occurred while loading configuration file. %s", traceback.format_exc())
        return load_status

    logger.info("Configuration loaded from file %s.", file_path)

    return load_status


def save_configuration_to_file(file_, project_uuid):
    """Save configuration to YAML file."""

    logger.info("Saving configuration to file...")

    # Prepare serialization for cameras per class type
    cameras_to_dict = [
        camera.serialize()
        for camera in cameras
        if camera.type in (Camera.CameraTypes.FTP_CAMERA, Camera.CameraTypes.USB_CAMERA)
    ]

    # Prepare serialization for notifiers per class type
    notification = {
        key: value.serialize() for key, value in Notifier.notifiers.items() if key and value
    }

    # Prepare serialization for actuators per class type
    actuators = [value.serialize() for key, value in Actuator.actuators.items() if key and value]

    # Prepare serialization for operation mode
    operation_mode = ""
    if OperationMode.cur_operation_mode_type:
        if OperationMode.cur_custom_classification_species:
            operation_mode = {
                "type": OperationMode.cur_operation_mode_type.value,
                "custom_target_species": OperationMode.cur_custom_classification_species,
            }
        else:
            operation_mode = {"type": OperationMode.cur_operation_mode_type.value}

    # Build data structure to serialize
    data = {
        "uuid": str(project_uuid),
        "version": __version__,
        "notification": notification or "",
        "cameras": cameras_to_dict,
        "camera_detection_params": Camera.detection_params,
        "actuators": actuators,
        "ai_model": {
            "ai_detection_model_version": AiModel.detection_model_version,
            "ai_classification_model_version": AiModel.classification_model_version,
            "ai_detect_threshold": AiModel.detection_threshold,
            "ai_class_threshold": AiModel.classification_threshold,
            "ai_language": AiModel.language,
            "ai_detection_device": AiModel.detection_device,
            "ai_classification_device": AiModel.classification_device,
            "ai_video_fps": AiModel.video_fps,
        },
        "operation_mode": operation_mode,
        "ftps_server": FTPsServer.ftps_server.serialize() if FTPsServer.ftps_server else "",
        "actuator_server": (
            FastAPIActuatorServer.actuator_server.serialize()
            if FastAPIActuatorServer.actuator_server
            else ""
        ),
        "database": db.serialize() if (db := DataBase.get_instance()) else "",
    }

    with open(file_, "w") as yaml_file:
        yaml.safe_dump(data, yaml_file)

    logger.info("Configuration saved to file %s.", file_)
