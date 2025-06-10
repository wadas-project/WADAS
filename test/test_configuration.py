from unittest.mock import MagicMock, Mock, patch

import pytest
from mocks import OpenStringMock
from packaging.version import Version

from wadas._version import __version__
from wadas.domain.actuator import Actuator
from wadas.domain.ai_model import AiModel
from wadas.domain.camera import Camera, cameras
from wadas.domain.configuration import (
    load_configuration_from_file,
    save_configuration_to_file,
)
from wadas.domain.email_notifier import EmailNotifier
from wadas.domain.fastapi_actuator_server import FastAPIActuatorServer
from wadas.domain.feeder_actuator import FeederActuator
from wadas.domain.ftp_camera import FTPCamera
from wadas.domain.ftps_server import DummyAuthorizer, FTPsServer, TLS_FTP_WADAS_Handler
from wadas.domain.notifier import Notifier
from wadas.domain.operation_mode import OperationMode
from wadas.domain.roadsign_actuator import RoadSignActuator
from wadas.domain.usb_camera import USBCamera


@pytest.fixture
def init():
    Notifier.notifiers = {"Email": None, "WhatsApp": None}
    FTPsServer.ftps_server = None
    Actuator.actuators.clear()
    cameras.clear()
    Camera.detection_params.clear()
    FastAPIActuatorServer.actuator_server = None
    AiModel.classification_model_version = "MDV5-yolov5"
    AiModel.classification_model_version = "DFv1.2"
    AiModel.classification_threshold = 0
    AiModel.detection_threshold = 0
    AiModel.language = ""
    AiModel.detection_device = "auto"
    AiModel.classification_device = "auto"
    AiModel.video_fps = 1
    OperationMode.cur_operation_mode = None


@patch(
    "builtins.open",
    new_callable=OpenStringMock,
    read_data="""
actuator_server:
actuators: []
ai_model:
  ai_class_threshold: 0
  ai_classification_device: auto
  ai_classification_model_version: DFv1.2
  ai_detect_threshold: 0
  ai_detection_device: auto
  ai_detection_model_version: MDV5-yolov5
  ai_language: ''
  ai_video_fps: 1
cameras: []
camera_detection_params: {}
database: ''
ftps_server: []
notification: []
operation_mode:
version: v0.1.0
uuid: 39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede
""",
)
def test_load_incompatible_older_version_config(mock_file, init):
    assert load_configuration_from_file("") == {
        "errors_on_load": False,
        "errors_log": "",
        "config_version": Version("v0.1.0"),
        "compatible_config": False,
        "valid_ftp_keyring": True,
        "valid_email_keyring": True,
        "valid_whatsapp_keyring": True,
        "uuid": "39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede",
    }
    assert Notifier.notifiers == {"Email": None, "WhatsApp": None}
    assert FTPsServer.ftps_server is None
    assert Actuator.actuators == {}
    assert cameras == []
    assert Camera.detection_params == {}
    assert FastAPIActuatorServer.actuator_server is None
    assert AiModel.detection_model_version == "MDV5-yolov5"
    assert AiModel.classification_model_version == "DFv1.2"
    assert AiModel.classification_threshold == 0
    assert AiModel.detection_threshold == 0
    assert AiModel.detection_device == "auto"
    assert AiModel.classification_device == "auto"
    assert AiModel.video_fps == 1
    assert AiModel.language == ""
    assert OperationMode.cur_operation_mode is None
    assert OperationMode.cur_operation_mode_type is None


@patch(
    "builtins.open",
    new_callable=OpenStringMock,
    read_data=f"""
actuator_server:
actuators: []
ai_model:
  ai_class_threshold: 0
  ai_classification_device: auto
  ai_classification_model_version: DFv1.2
  ai_detect_threshold: 0
  ai_detection_device: auto
  ai_detection_model_version: MDV5-yolov5
  ai_language: ''
  ai_video_fps: 1
cameras: []
camera_detection_params: {{}}
database: ''
ftps_server: []
notification: []
operation_mode:
version: {__version__}
uuid: 39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede
""",
)
def test_load_empty_config(mock_file, init):
    assert load_configuration_from_file("") == {
        "errors_on_load": False,
        "errors_log": "",
        "config_version": Version(__version__),
        "compatible_config": True,
        "valid_ftp_keyring": True,
        "valid_email_keyring": True,
        "valid_whatsapp_keyring": True,
        "uuid": "39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede",
    }
    assert Notifier.notifiers == {"Email": None, "WhatsApp": None}
    assert FTPsServer.ftps_server is None
    assert Actuator.actuators == {}
    assert cameras == []
    assert Camera.detection_params == {}
    assert FastAPIActuatorServer.actuator_server is None
    assert AiModel.detection_model_version == "MDV5-yolov5"
    assert AiModel.classification_model_version == "DFv1.2"
    assert AiModel.classification_threshold == 0
    assert AiModel.detection_threshold == 0
    assert AiModel.detection_device == "auto"
    assert AiModel.classification_device == "auto"
    assert AiModel.language == ""
    assert OperationMode.cur_operation_mode is None
    assert OperationMode.cur_operation_mode_type is None


@patch("builtins.open", new_callable=OpenStringMock, create=True)
def test_save_empty_config(mock_file, init):
    save_configuration_to_file("", "39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede")
    assert (
        mock_file.dump()
        == f"""actuator_server: ''
actuators: []
ai_model:
  ai_class_threshold: 0
  ai_classification_device: auto
  ai_classification_model_version: DFv1.2
  ai_detect_threshold: 0
  ai_detection_device: auto
  ai_detection_model_version: MDV5-yolov5
  ai_language: ''
  ai_video_fps: 1
camera_detection_params: {{}}
cameras: []
database: ''
ftps_server: ''
notification: ''
operation_mode: ''
uuid: 39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede
version: {__version__}
"""
    )


@patch(
    "builtins.open",
    new_callable=OpenStringMock,
    read_data="""
actuator_server:
actuators: []
ai_model:
  ai_detection_model_version: MDV5-yolov5
  ai_classification_model_version: DFv1.2
  ai_class_threshold: 0
  ai_classification_device: auto
  ai_detect_threshold: 0
  ai_detection_device: auto
  ai_language: ''
  ai_video_fps: 1
cameras: []
camera_detection_params: {}
database: ''
ftps_server: []
notification: []
operation_mode:
uuid: 39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede
""",
)
def test_load_wrong_format_config(mock_file, init):
    result = load_configuration_from_file("")
    assert result["errors_on_load"] is True
    assert isinstance(result["errors_log"], KeyError)
    assert repr(result["errors_log"]) == "KeyError('version')"
    assert result["config_version"] is None
    assert result["compatible_config"] is True
    assert result["valid_ftp_keyring"] is True
    assert result["valid_email_keyring"] is True
    assert result["valid_whatsapp_keyring"] is True
    assert Notifier.notifiers == {"Email": None, "WhatsApp": None}
    assert FTPsServer.ftps_server is None
    assert Actuator.actuators == {}
    assert cameras == []
    assert Camera.detection_params == {}
    assert FastAPIActuatorServer.actuator_server is None
    assert AiModel.detection_model_version == "MDV5-yolov5"
    assert AiModel.classification_model_version == "DFv1.2"
    assert AiModel.classification_threshold == 0
    assert AiModel.detection_threshold == 0
    assert AiModel.detection_device == "auto"
    assert AiModel.classification_device == "auto"
    assert AiModel.language == ""
    assert AiModel.video_fps == 1
    assert OperationMode.cur_operation_mode is None
    assert OperationMode.cur_operation_mode_type is None


@patch(
    "builtins.open",
    new_callable=OpenStringMock,
    read_data=f"""
actuator_server:
  actuator_timeout_threshold: 89
  ip: 1.2.3.4
  port: 567
  ssl_certificate: eshare_crt.pem
  ssl_key: eshare_key.pem
actuators: []
ai_model:
  ai_class_threshold: 0
  ai_classification_device: auto
  ai_classification_model_version: DFv1.2
  ai_detect_threshold: 0
  ai_detection_device: auto
  ai_detection_model_version: MDV5-yolov5
  ai_language: ''
  ai_video_fps: 1
cameras: []
camera_detection_params: {{}}
database: ''
ftps_server: []
notification: []
operation_mode:
uuid: 39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede
version: {__version__}
""",
)
def test_load_actuator_server_config(mock_file, init):
    assert load_configuration_from_file("") == {
        "errors_on_load": False,
        "errors_log": "",
        "config_version": Version(__version__),
        "compatible_config": True,
        "uuid": "39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede",
        "valid_ftp_keyring": True,
        "valid_email_keyring": True,
        "valid_whatsapp_keyring": True,
    }
    assert Notifier.notifiers == {"Email": None, "WhatsApp": None}
    assert FTPsServer.ftps_server is None
    assert Actuator.actuators == {}
    assert cameras == []
    assert Camera.detection_params == {}
    assert FastAPIActuatorServer.actuator_server is not None
    assert FastAPIActuatorServer.actuator_server.actuator_timeout_threshold == 89
    assert FastAPIActuatorServer.actuator_server.ip == "1.2.3.4"
    assert FastAPIActuatorServer.actuator_server.port == 567
    assert FastAPIActuatorServer.actuator_server.ssl_certificate == "eshare_crt.pem"
    assert FastAPIActuatorServer.actuator_server.ssl_key == "eshare_key.pem"
    assert FastAPIActuatorServer.actuator_server.thread is None
    assert FastAPIActuatorServer.actuator_server.server is None
    assert FastAPIActuatorServer.actuator_server.startup_time is None
    assert AiModel.detection_model_version == "MDV5-yolov5"
    assert AiModel.classification_model_version == "DFv1.2"
    assert AiModel.classification_threshold == 0
    assert AiModel.detection_threshold == 0
    assert AiModel.language == ""
    assert AiModel.video_fps == 1
    assert AiModel.detection_device == "auto"
    assert AiModel.classification_device == "auto"
    assert OperationMode.cur_operation_mode is None
    assert OperationMode.cur_operation_mode_type is None


@patch("builtins.open", new_callable=OpenStringMock, create=True)
def test_save_actuator_server_config(mock_file, init):
    FastAPIActuatorServer.actuator_server = FastAPIActuatorServer(
        "1.2.3.4", 567, "eshare_crt.pem", "eshare_key.pem", 89
    )
    save_configuration_to_file("", "39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede")
    assert (
        mock_file.dump()
        == f"""actuator_server:
  actuator_timeout_threshold: 89
  ip: 1.2.3.4
  port: 567
  ssl_certificate: eshare_crt.pem
  ssl_key: eshare_key.pem
actuators: []
ai_model:
  ai_class_threshold: 0
  ai_classification_device: auto
  ai_classification_model_version: DFv1.2
  ai_detect_threshold: 0
  ai_detection_device: auto
  ai_detection_model_version: MDV5-yolov5
  ai_language: ''
  ai_video_fps: 1
camera_detection_params: {{}}
cameras: []
database: ''
ftps_server: ''
notification: ''
operation_mode: ''
uuid: 39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede
version: {__version__}
"""
    )


@patch(
    "builtins.open",
    new_callable=OpenStringMock,
    read_data=f"""
actuator_server:
actuators:
- enabled: true
  id: Actuator4
  type: Road Sign
- enabled: false
  id: Actuator1
  type: Feeder
- enabled: false
  id: Actuator3
  type: Road Sign
- enabled: true
  id: Actuator2
  type: Feeder
ai_model:
  ai_class_threshold: 0.123
  ai_detect_threshold: 0.456
  ai_language: xyz
  ai_detection_device: auto
  ai_detection_model_version: MDV5-yolov5
  ai_classification_device: auto
  ai_classification_model_version: DFv1.2
  ai_video_fps: 1
cameras: []
camera_detection_params: {{}}
database: ''
ftps_server: []
notification: []
operation_mode:
uuid: 39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede
version: {__version__}
""",
)
def test_load_actuators_config(mock_file, init):
    assert load_configuration_from_file("") == {
        "errors_on_load": False,
        "errors_log": "",
        "config_version": Version(__version__),
        "compatible_config": True,
        "uuid": "39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede",
        "valid_ftp_keyring": True,
        "valid_email_keyring": True,
        "valid_whatsapp_keyring": True,
    }
    assert Notifier.notifiers == {"Email": None, "WhatsApp": None}
    assert FTPsServer.ftps_server is None
    actuators = ["Actuator1", "Actuator2", "Actuator3", "Actuator4"]
    assert sorted(Actuator.actuators.keys()) == actuators
    assert [Actuator.actuators[key].id for key in actuators] == actuators
    assert [Actuator.actuators[key].enabled for key in actuators] == [False, True, False, True]
    assert [Actuator.actuators[key].type for key in actuators] == [
        Actuator.ActuatorTypes.FEEDER,
        Actuator.ActuatorTypes.FEEDER,
        Actuator.ActuatorTypes.ROADSIGN,
        Actuator.ActuatorTypes.ROADSIGN,
    ]
    assert cameras == []
    assert Camera.detection_params == {}
    assert FastAPIActuatorServer.actuator_server is None
    assert AiModel.detection_model_version == "MDV5-yolov5"
    assert AiModel.classification_model_version == "DFv1.2"
    assert AiModel.classification_threshold == 0.123
    assert AiModel.detection_threshold == 0.456
    assert AiModel.language == "xyz"
    assert AiModel.detection_device == "auto"
    assert AiModel.classification_device == "auto"
    assert AiModel.video_fps == 1
    assert OperationMode.cur_operation_mode is None
    assert OperationMode.cur_operation_mode_type is None


@patch("builtins.open", new_callable=OpenStringMock, create=True)
def test_save_actuators_config(mock_file, init):
    Actuator.actuators["Actuator1"] = FeederActuator("Actuator1", False)
    Actuator.actuators["Actuator2"] = FeederActuator("Actuator2", True)
    Actuator.actuators["Actuator3"] = RoadSignActuator("Actuator3", False)
    Actuator.actuators["Actuator4"] = RoadSignActuator("Actuator4", True)
    save_configuration_to_file("", "39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede")
    assert (
        mock_file.dump()
        == f"""actuator_server: ''
actuators:
- enabled: false
  id: Actuator1
  type: Feeder
- enabled: true
  id: Actuator2
  type: Feeder
- enabled: false
  id: Actuator3
  type: Road Sign
- enabled: true
  id: Actuator4
  type: Road Sign
ai_model:
  ai_class_threshold: 0
  ai_classification_device: auto
  ai_classification_model_version: DFv1.2
  ai_detect_threshold: 0
  ai_detection_device: auto
  ai_detection_model_version: MDV5-yolov5
  ai_language: ''
  ai_video_fps: 1
camera_detection_params: {{}}
cameras: []
database: ''
ftps_server: ''
notification: ''
operation_mode: ''
uuid: 39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede
version: {__version__}
"""
    )


@patch(
    "builtins.open",
    new_callable=OpenStringMock,
    read_data=f"""
actuator_server:
actuators: []
ai_model:
  ai_class_threshold: 0.98
  ai_detect_threshold: 0.76
  ai_language: it
  ai_detection_device: auto
  ai_detection_model_version: MDV5-yolov5
  ai_classification_device: auto
  ai_classification_model_version: DFv1.2
  ai_video_fps: 1
cameras: []
camera_detection_params: {{}}
database: ''
ftps_server: []
notification: []
operation_mode:
uuid: 39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede
version: {__version__}
""",
)
def test_load_ai_model_config(mock_file, init):
    assert load_configuration_from_file("") == {
        "errors_on_load": False,
        "errors_log": "",
        "config_version": Version(__version__),
        "compatible_config": True,
        "uuid": "39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede",
        "valid_ftp_keyring": True,
        "valid_email_keyring": True,
        "valid_whatsapp_keyring": True,
    }
    assert Notifier.notifiers == {"Email": None, "WhatsApp": None}
    assert FTPsServer.ftps_server is None
    assert Actuator.actuators == {}
    assert cameras == []
    assert Camera.detection_params == {}
    assert FastAPIActuatorServer.actuator_server is None
    assert AiModel.detection_model_version == "MDV5-yolov5"
    assert AiModel.classification_model_version == "DFv1.2"
    assert AiModel.classification_threshold == 0.98
    assert AiModel.detection_threshold == 0.76
    assert AiModel.language == "it"
    assert AiModel.detection_device == "auto"
    assert AiModel.classification_device == "auto"
    assert AiModel.video_fps == 1
    assert OperationMode.cur_operation_mode is None
    assert OperationMode.cur_operation_mode_type is None


@patch("builtins.open", new_callable=OpenStringMock, create=True)
def test_save_ai_model_config(mock_file, init):
    AiModel.classification_model_version = "MDV5-yolov5"
    AiModel.classification_model_version = "DFv1.2"
    AiModel.classification_threshold = 0.98
    AiModel.detection_threshold = 0.76
    AiModel.language = "it"
    AiModel.classification_device = "GPU"
    AiModel.detection_device = "CPU"
    AiModel.video_fps = 1
    save_configuration_to_file("", "39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede")
    assert (
        mock_file.dump()
        == f"""actuator_server: ''
actuators: []
ai_model:
  ai_class_threshold: 0.98
  ai_classification_device: GPU
  ai_classification_model_version: DFv1.2
  ai_detect_threshold: 0.76
  ai_detection_device: CPU
  ai_detection_model_version: MDV5-yolov5
  ai_language: it
  ai_video_fps: 1
camera_detection_params: {{}}
cameras: []
database: ''
ftps_server: ''
notification: ''
operation_mode: ''
uuid: 39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede
version: {__version__}
"""
    )


@patch(
    "builtins.open",
    new_callable=OpenStringMock,
    read_data=f"""
actuator_server:
actuators: []
ai_model:
  ai_class_threshold: 0
  ai_classification_device: auto
  ai_classification_model_version: DFv1.2
  ai_detect_threshold: 0
  ai_detection_device: auto
  ai_detection_model_version: MDV5-yolov5
  ai_language: ''
  ai_video_fps: 1
cameras: []
camera_detection_params:
  detection_per_second: 12
  min_contour_area: 345
  ms_sample_rate: 67
  threshold: 89
database: ''
ftps_server: []
notification: []
operation_mode:
uuid: 39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede
version: {__version__}
""",
)
def test_load_camera_detection_params_config(mock_file, init):
    assert load_configuration_from_file("") == {
        "errors_on_load": False,
        "errors_log": "",
        "config_version": Version(__version__),
        "compatible_config": True,
        "uuid": "39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede",
        "valid_ftp_keyring": True,
        "valid_email_keyring": True,
        "valid_whatsapp_keyring": True,
    }
    assert Notifier.notifiers == {"Email": None, "WhatsApp": None}
    assert FTPsServer.ftps_server is None
    assert Actuator.actuators == {}
    assert cameras == []
    assert Camera.detection_params == {
        "detection_per_second": 12,
        "min_contour_area": 345,
        "ms_sample_rate": 67,
        "threshold": 89,
    }
    assert FastAPIActuatorServer.actuator_server is None
    assert AiModel.detection_model_version == "MDV5-yolov5"
    assert AiModel.classification_model_version == "DFv1.2"
    assert AiModel.classification_threshold == 0
    assert AiModel.detection_threshold == 0
    assert AiModel.language == ""
    assert AiModel.detection_device == "auto"
    assert AiModel.classification_device == "auto"
    assert AiModel.video_fps == 1
    assert OperationMode.cur_operation_mode is None
    assert OperationMode.cur_operation_mode_type is None


@patch("builtins.open", new_callable=OpenStringMock, create=True)
def test_save_camera_detection_params_config(mock_file, init):
    Camera.detection_params = {
        "detection_per_second": 12,
        "min_contour_area": 345,
        "ms_sample_rate": 67,
        "threshold": 89,
    }
    save_configuration_to_file("", "39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede")
    assert (
        mock_file.dump()
        == f"""actuator_server: ''
actuators: []
ai_model:
  ai_class_threshold: 0
  ai_classification_device: auto
  ai_classification_model_version: DFv1.2
  ai_detect_threshold: 0
  ai_detection_device: auto
  ai_detection_model_version: MDV5-yolov5
  ai_language: ''
  ai_video_fps: 1
camera_detection_params:
  detection_per_second: 12
  min_contour_area: 345
  ms_sample_rate: 67
  threshold: 89
cameras: []
database: ''
ftps_server: ''
notification: ''
operation_mode: ''
uuid: 39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede
version: {__version__}
"""
    )


@patch(
    "builtins.open",
    new_callable=OpenStringMock,
    read_data=r"""
actuator_server:
actuators: []
ai_model:
  ai_class_threshold: 0
  ai_classification_device: auto
  ai_classification_model_version: DFv1.2
  ai_detect_threshold: 0
  ai_detection_device: auto
  ai_detection_model_version: MDV5-yolov5
  ai_language: ''
  ai_video_fps: 1
cameras:
- actuators: []
  enabled: true
  ftp_folder: /Documents/ftp/Camera1
  id: Camera1
  type: FTP Camera
- actuators: []
  enabled: false
  ftp_folder: /Documents/ftp/Camera2
  id: Camera2
  type: FTP Camera
- actuators: []
  backend: 1400
  enable_mot_det: true
  enabled: false
  id: cvbdfg
  index: 0
  name: ASUS USB2.0 Webcam
  path: {}
  pid: 10371
  type: USB Camera
  vid: 7119
- actuators: []
  backend: 1401
  enable_mot_det: false
  enabled: true
  id: cvbdfg2
  index: 1
  name: ASUS USB3.1 Webcam
  path: {}
  pid: 10372
  type: USB Camera
  vid: 7120
camera_detection_params: {{}}
database: ''
ftps_server: []
notification: []
operation_mode:
uuid: 39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede
version: {}
""".format(
        r"\\?\usb#vid_1bcf&pid_2883&mi_00#7&e89baf7&0&0000#"
        r"{e5323777-f976-4f5b-9b55-b94699c46e44}\global",
        r"\\?\usb#vid_1bd0&pid_2884&mi_00#7&e89baf7&0&0000#"
        r"{e5323777-f976-4f5b-9b55-b94699c46e4X}\local",
        __version__,
    ),
)
def test_load_cameras_config(mock_file, init):
    with (
        patch("os.path.isdir") as is_dir_mock,
        patch("os.makedirs") as makedirs_mock,
        patch("keyring.get_credential") as get_credential_mock,
        patch("wadas.domain.ftps_server.FTPsServer.add_user") as add_user_mock,
    ):
        assert load_configuration_from_file("") == {
            "errors_on_load": False,
            "errors_log": "",
            "config_version": Version(__version__),
            "compatible_config": True,
            "uuid": "39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede",
            "valid_ftp_keyring": True,
            "valid_email_keyring": True,
            "valid_whatsapp_keyring": True,
        }
    is_dir_mock.assert_not_called()
    makedirs_mock.assert_not_called()
    get_credential_mock.assert_not_called()
    add_user_mock.assert_not_called()
    assert Notifier.notifiers == {"Email": None, "WhatsApp": None}
    assert FTPsServer.ftps_server is None
    assert Actuator.actuators == {}
    assert [type(camera) for camera in cameras] == [FTPCamera, FTPCamera, USBCamera, USBCamera]
    assert [
        getattr(cameras[0], name) for name in ("type", "id", "ftp_folder", "enabled", "actuators")
    ] == [Camera.CameraTypes.FTP_CAMERA, "Camera1", "/Documents/ftp/Camera1", True, []]
    assert [
        getattr(cameras[1], name) for name in ("type", "id", "ftp_folder", "enabled", "actuators")
    ] == [Camera.CameraTypes.FTP_CAMERA, "Camera2", "/Documents/ftp/Camera2", False, []]
    assert [
        getattr(cameras[2], name)
        for name in (
            "type",
            "id",
            "name",
            "enabled",
            "index",
            "backend",
            "en_wadas_motion_detection",
            "pid",
            "vid",
            "path",
            "actuators",
        )
    ] == [
        Camera.CameraTypes.USB_CAMERA,
        "cvbdfg",
        "ASUS USB2.0 Webcam",
        False,
        0,
        1400,
        True,
        10371,
        7119,
        r"\\?\usb#vid_1bcf&pid_2883&mi_00#7&e89baf7&0&0000#"
        r"{e5323777-f976-4f5b-9b55-b94699c46e44}\global",
        [],
    ]
    assert [
        getattr(cameras[3], name)
        for name in (
            "type",
            "id",
            "name",
            "enabled",
            "index",
            "backend",
            "en_wadas_motion_detection",
            "pid",
            "vid",
            "path",
            "actuators",
        )
    ] == [
        Camera.CameraTypes.USB_CAMERA,
        "cvbdfg2",
        "ASUS USB3.1 Webcam",
        True,
        1,
        1401,
        False,
        10372,
        7120,
        r"\\?\usb#vid_1bd0&pid_2884&mi_00#7&e89baf7&0&0000#"
        r"{e5323777-f976-4f5b-9b55-b94699c46e4X}\local",
        [],
    ]
    assert Camera.detection_params == {}
    assert FastAPIActuatorServer.actuator_server is None
    assert AiModel.detection_model_version == "MDV5-yolov5"
    assert AiModel.classification_model_version == "DFv1.2"
    assert AiModel.classification_threshold == 0
    assert AiModel.detection_threshold == 0
    assert AiModel.language == ""
    assert AiModel.detection_device == "auto"
    assert AiModel.classification_device == "auto"
    assert AiModel.video_fps == 1
    assert OperationMode.cur_operation_mode is None
    assert OperationMode.cur_operation_mode_type is None


@patch(
    "builtins.open",
    new_callable=OpenStringMock,
    read_data=rf"""
actuator_server:
actuators: []
ai_model:
  ai_class_threshold: 0
  ai_classification_device: auto
  ai_classification_model_version: DFv1.2
  ai_detect_threshold: 0
  ai_detection_device: auto
  ai_detection_model_version: MDV5-yolov5
  ai_language: ''
  ai_video_fps: 1
cameras:
- actuators: []
  enabled: true
  ftp_folder: /Documents/ftp/Camera1
  id: Camera1
  type: FTP Camera
camera_detection_params: {{}}
ftps_server:
  ftp_dir: /Documents/ftp
  ip: 1.2.3.4
  max_conn: 50
  max_conn_per_ip: 5
  passive_ports: [1234, 5678]
  port: 567
  ssl_certificate: /Documents/ssl/eshare_crt.pem
  ssl_key: /Documents/ssl/eshare_key.pem
database: ''
notification: []
operation_mode:
uuid: 39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede
version: {__version__}
""",
)
def test_load_cameras_config_with_ftp_and_folder_and_no_credentials(mock_file, init):
    with (
        patch("os.path.isdir") as is_dir_mock,
        patch("os.makedirs") as makedirs_mock,
        patch("keyring.get_credential") as get_credential_mock,
        patch("wadas.domain.ftps_server.FTPsServer.add_user") as add_user_mock,
    ):
        is_dir_mock.return_value = True
        get_credential_mock.return_value = None
        assert load_configuration_from_file("") == {
            "errors_on_load": False,
            "errors_log": "",
            "config_version": Version(__version__),
            "compatible_config": True,
            "uuid": "39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede",
            "valid_ftp_keyring": False,
            "valid_email_keyring": True,
            "valid_whatsapp_keyring": True,
        }
    assert is_dir_mock.call_args == (("/Documents/ftp/Camera1",),)
    makedirs_mock.assert_not_called()
    get_credential_mock.assert_called_once_with("WADAS_FTP_camera_Camera1", "")
    add_user_mock.assert_not_called()
    assert Notifier.notifiers == {"Email": None, "WhatsApp": None}
    assert FTPsServer.ftps_server is not None
    assert Actuator.actuators == {}
    assert type(cameras[0]) is FTPCamera
    assert [
        getattr(cameras[0], name) for name in ("type", "id", "ftp_folder", "enabled", "actuators")
    ] == [Camera.CameraTypes.FTP_CAMERA, "Camera1", "/Documents/ftp/Camera1", True, []]
    assert Camera.detection_params == {}
    assert FastAPIActuatorServer.actuator_server is None
    assert AiModel.detection_model_version == "MDV5-yolov5"
    assert AiModel.classification_model_version == "DFv1.2"
    assert AiModel.classification_threshold == 0
    assert AiModel.detection_threshold == 0
    assert AiModel.language == ""
    assert AiModel.detection_device == "auto"
    assert AiModel.classification_device == "auto"
    assert AiModel.video_fps == 1
    assert OperationMode.cur_operation_mode is None
    assert OperationMode.cur_operation_mode_type is None


@patch(
    "builtins.open",
    new_callable=OpenStringMock,
    read_data=f"""
actuator_server:
actuators: []
ai_model:
  ai_class_threshold: 0
  ai_classification_device: auto
  ai_classification_model_version: DFv1.2
  ai_detect_threshold: 0
  ai_detection_device: auto
  ai_detection_model_version: MDV5-yolov5
  ai_language: ''
  ai_video_fps: 1
cameras:
- actuators: []
  enabled: true
  ftp_folder: /Documents/ftp/Camera1
  id: Camera1
  type: FTP Camera
camera_detection_params: {{}}
ftps_server:
  ftp_dir: /Documents/ftp
  ip: 1.2.3.4
  max_conn: 50
  max_conn_per_ip: 5
  passive_ports: [1234, 5678]
  port: 567
  ssl_certificate: /Documents/ssl/eshare_crt.pem
  ssl_key: /Documents/ssl/eshare_key.pem
database: ''
notification: []
operation_mode:
uuid: 39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede
version: {__version__}
""",
)
def test_load_cameras_config_with_ftp_and_no_folder_and_no_credentials(mock_file, init):
    with (
        patch("os.path.isdir") as is_dir_mock,
        patch("os.makedirs") as makedirs_mock,
        patch("keyring.get_credential") as get_credential_mock,
        patch("wadas.domain.ftps_server.FTPsServer.add_user") as add_user_mock,
    ):
        is_dir_mock.return_value = False
        get_credential_mock.return_value = None
        assert load_configuration_from_file("") == {
            "errors_on_load": False,
            "errors_log": "",
            "config_version": Version(__version__),
            "compatible_config": True,
            "uuid": "39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede",
            "valid_ftp_keyring": False,
            "valid_email_keyring": True,
            "valid_whatsapp_keyring": True,
        }
    assert is_dir_mock.call_args == (("/Documents/ftp/Camera1",),)
    makedirs_mock.assert_called_once_with("/Documents/ftp/Camera1", exist_ok=True)
    get_credential_mock.assert_called_once_with("WADAS_FTP_camera_Camera1", "")
    add_user_mock.assert_not_called()
    assert Notifier.notifiers == {"Email": None, "WhatsApp": None}
    assert FTPsServer.ftps_server is not None
    assert Actuator.actuators == {}
    assert type(cameras[0]) is FTPCamera
    assert [
        getattr(cameras[0], name) for name in ("type", "id", "ftp_folder", "enabled", "actuators")
    ] == [Camera.CameraTypes.FTP_CAMERA, "Camera1", "/Documents/ftp/Camera1", True, []]
    assert Camera.detection_params == {}
    assert FastAPIActuatorServer.actuator_server is None
    assert AiModel.detection_model_version == "MDV5-yolov5"
    assert AiModel.classification_model_version == "DFv1.2"
    assert AiModel.classification_threshold == 0
    assert AiModel.detection_threshold == 0
    assert AiModel.language == ""
    assert AiModel.detection_device == "auto"
    assert AiModel.classification_device == "auto"
    assert AiModel.video_fps == 1
    assert OperationMode.cur_operation_mode is None
    assert OperationMode.cur_operation_mode_type is None


@patch(
    "builtins.open",
    new_callable=OpenStringMock,
    read_data=f"""
actuator_server:
actuators: []
ai_model:
  ai_class_threshold: 0
  ai_classification_device: auto
  ai_classification_model_version: DFv1.2
  ai_detect_threshold: 0
  ai_detection_device: auto
  ai_detection_model_version: MDV5-yolov5
  ai_language: ''
  ai_video_fps: 1
cameras:
- actuators: []
  enabled: true
  ftp_folder: /Documents/ftp/Camera1
  id: Camera1
  type: FTP Camera
camera_detection_params: {{}}
ftps_server:
  ftp_dir: /Documents/ftp
  ip: 1.2.3.4
  max_conn: 50
  max_conn_per_ip: 5
  passive_ports: [1234, 5678]
  port: 567
  ssl_certificate: /Documents/ssl/eshare_crt.pem
  ssl_key: /Documents/ssl/eshare_key.pem
database: ''
notification: []
operation_mode:
uuid: 39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede
version: {__version__}
""",
)
def test_load_cameras_config_with_ftp_and_folder_and_same_credentials(mock_file, init):
    with (
        patch("os.path.isdir") as is_dir_mock,
        patch("os.makedirs") as makedirs_mock,
        patch("keyring.get_credential") as get_credential_mock,
        patch("wadas.domain.ftps_server.FTPsServer.add_user") as add_user_mock,
    ):
        is_dir_mock.return_value = True
        get_credential_mock.return_value = Mock(username="Camera1", password="123")
        assert load_configuration_from_file("") == {
            "errors_on_load": False,
            "errors_log": "",
            "config_version": Version(__version__),
            "compatible_config": True,
            "uuid": "39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede",
            "valid_ftp_keyring": True,
            "valid_email_keyring": True,
            "valid_whatsapp_keyring": True,
        }
    assert is_dir_mock.call_args == (("/Documents/ftp/Camera1",),)
    makedirs_mock.assert_not_called()
    get_credential_mock.assert_called_once_with("WADAS_FTP_camera_Camera1", "")
    add_user_mock.assert_called_once_with("Camera1", "123", "/Documents/ftp/Camera1")
    assert Notifier.notifiers == {"Email": None, "WhatsApp": None}
    assert FTPsServer.ftps_server is not None
    assert Actuator.actuators == {}
    assert type(cameras[0]) is FTPCamera
    assert [
        getattr(cameras[0], name) for name in ("type", "id", "ftp_folder", "enabled", "actuators")
    ] == [Camera.CameraTypes.FTP_CAMERA, "Camera1", "/Documents/ftp/Camera1", True, []]
    assert Camera.detection_params == {}
    assert FastAPIActuatorServer.actuator_server is None
    assert AiModel.detection_model_version == "MDV5-yolov5"
    assert AiModel.classification_model_version == "DFv1.2"
    assert AiModel.classification_threshold == 0
    assert AiModel.detection_threshold == 0
    assert AiModel.language == ""
    assert AiModel.detection_device == "auto"
    assert AiModel.classification_device == "auto"
    assert AiModel.video_fps == 1
    assert OperationMode.cur_operation_mode is None
    assert OperationMode.cur_operation_mode_type is None


@patch(
    "builtins.open",
    new_callable=OpenStringMock,
    read_data=f"""
actuator_server:
actuators: []
ai_model:
  ai_class_threshold: 0
  ai_classification_device: auto
  ai_classification_model_version: DFv1.2
  ai_detect_threshold: 0
  ai_detection_device: auto
  ai_detection_model_version: MDV5-yolov5
  ai_language: ''
  ai_video_fps: 1
cameras:
- actuators: []
  enabled: true
  ftp_folder: /Documents/ftp/Camera1
  id: Camera1
  type: FTP Camera
camera_detection_params: {{}}
ftps_server:
  ftp_dir: /Documents/ftp
  ip: 1.2.3.4
  max_conn: 50
  max_conn_per_ip: 5
  passive_ports: [1234, 5678]
  port: 567
  ssl_certificate: /Documents/ssl/eshare_crt.pem
  ssl_key: /Documents/ssl/eshare_key.pem
database: ''
notification: []
operation_mode:
uuid: 39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede
version: {__version__}
""",
)
def test_load_cameras_config_with_ftp_and_folder_and_different_credentials(mock_file, init):
    with (
        patch("os.path.isdir") as is_dir_mock,
        patch("os.makedirs") as makedirs_mock,
        patch("keyring.get_credential") as get_credential_mock,
        patch("wadas.domain.ftps_server.FTPsServer.add_user") as add_user_mock,
    ):
        is_dir_mock.return_value = True
        get_credential_mock.return_value = Mock(username="UnknownUser", password="123")
        assert load_configuration_from_file("") == {
            "errors_on_load": False,
            "errors_log": "",
            "config_version": Version(__version__),
            "compatible_config": True,
            "uuid": "39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede",
            "valid_ftp_keyring": False,
            "valid_email_keyring": True,
            "valid_whatsapp_keyring": True,
        }
    assert is_dir_mock.call_args == (("/Documents/ftp/Camera1",),)
    makedirs_mock.assert_not_called()
    get_credential_mock.assert_called_once_with("WADAS_FTP_camera_Camera1", "")
    add_user_mock.assert_not_called()
    assert Notifier.notifiers == {"Email": None, "WhatsApp": None}
    assert FTPsServer.ftps_server is not None
    assert Actuator.actuators == {}
    assert type(cameras[0]) is FTPCamera
    assert [
        getattr(cameras[0], name) for name in ("type", "id", "ftp_folder", "enabled", "actuators")
    ] == [Camera.CameraTypes.FTP_CAMERA, "Camera1", "/Documents/ftp/Camera1", True, []]
    assert Camera.detection_params == {}
    assert FastAPIActuatorServer.actuator_server is None
    assert AiModel.detection_model_version == "MDV5-yolov5"
    assert AiModel.classification_model_version == "DFv1.2"
    assert AiModel.classification_threshold == 0
    assert AiModel.detection_threshold == 0
    assert AiModel.language == ""
    assert AiModel.detection_device == "auto"
    assert AiModel.classification_device == "auto"
    assert AiModel.video_fps == 1
    assert OperationMode.cur_operation_mode is None
    assert OperationMode.cur_operation_mode_type is None


@patch("builtins.open", new_callable=OpenStringMock, create=True)
def test_save_cameras_config(mock_file, init):
    cameras.extend(
        (
            FTPCamera("Camera1", "/Documents/ftp/Camera1", True, []),
            FTPCamera("Camera2", "/Documents/ftp/Camera2", False, []),
            USBCamera(
                "cvbdfg",
                "ASUS USB2.0 Webcam",
                False,
                0,
                1400,
                True,
                10371,
                7119,
                r"\\?\usb#vid_1bcf&pid_2883&mi_00#7&e89baf7&0&0000#"
                r"{e5323777-f976-4f5b-9b55-b94699c46e44}\global",
                [],
            ),
            USBCamera(
                "cvbdfg2",
                "ASUS USB3.1 Webcam",
                True,
                1,
                1401,
                False,
                10372,
                7120,
                r"\\?\usb#vid_1bd0&pid_2884&mi_00#7&e89baf7&0&0000#"
                r"{e5323777-f976-4f5b-9b55-b94699c46e4X}\local",
                [],
            ),
        )
    )
    save_configuration_to_file("", "39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede")
    assert (
        mock_file.dump()
        == r"""actuator_server: ''
actuators: []
ai_model:
  ai_class_threshold: 0
  ai_classification_device: auto
  ai_classification_model_version: DFv1.2
  ai_detect_threshold: 0
  ai_detection_device: auto
  ai_detection_model_version: MDV5-yolov5
  ai_language: ''
  ai_video_fps: 1
camera_detection_params: {{}}
cameras:
- actuators: []
  enabled: true
  ftp_folder: /Documents/ftp/Camera1
  id: Camera1
  type: FTP Camera
- actuators: []
  enabled: false
  ftp_folder: /Documents/ftp/Camera2
  id: Camera2
  type: FTP Camera
- actuators: []
  backend: 1400
  enable_mot_det: true
  enabled: false
  id: cvbdfg
  index: 0
  name: ASUS USB2.0 Webcam
  path: {}
  pid: 10371
  type: USB Camera
  vid: 7119
- actuators: []
  backend: 1401
  enable_mot_det: false
  enabled: true
  id: cvbdfg2
  index: 1
  name: ASUS USB3.1 Webcam
  path: {}
  pid: 10372
  type: USB Camera
  vid: 7120
database: ''
ftps_server: ''
notification: ''
operation_mode: ''
uuid: 39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede
version: {}
""".format(
            r"\\?\usb#vid_1bcf&pid_2883&mi_00#7&e89baf7&0&0000#"
            r"{e5323777-f976-4f5b-9b55-b94699c46e44}\global",
            r"\\?\usb#vid_1bd0&pid_2884&mi_00#7&e89baf7&0&0000#"
            r"{e5323777-f976-4f5b-9b55-b94699c46e4X}\local",
            __version__,
        )
    )


@patch(
    "builtins.open",
    new_callable=OpenStringMock,
    read_data=f"""
actuator_server:
actuators: []
ai_model:
  ai_class_threshold: 0
  ai_classification_device: auto
  ai_classification_model_version: DFv1.2
  ai_detect_threshold: 0
  ai_detection_device: auto
  ai_detection_model_version: MDV5-yolov5
  ai_language: ''
  ai_video_fps: 1
cameras: []
camera_detection_params: {{}}
ftps_server:
  ftp_dir: /Documents/ftp
  ip: 1.2.3.4
  max_conn: 50
  max_conn_per_ip: 5
  passive_ports: [1234, 5678]
  port: 567
  ssl_certificate: /Documents/ssl/eshare_crt.pem
  ssl_key: /Documents/ssl/eshare_key.pem
database: ''
notification: []
operation_mode:
uuid: 39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede
version: {__version__}
""",
)
def test_load_ftps_server_config(mock_file, init):
    assert load_configuration_from_file("") == {
        "errors_on_load": False,
        "errors_log": "",
        "config_version": Version(__version__),
        "compatible_config": True,
        "uuid": "39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede",
        "valid_ftp_keyring": True,
        "valid_email_keyring": True,
        "valid_whatsapp_keyring": True,
    }
    assert Notifier.notifiers == {"Email": None, "WhatsApp": None}
    assert FTPsServer.ftps_server is not None
    assert FTPsServer.ftps_server.ip == "1.2.3.4"
    assert FTPsServer.ftps_server.port == 567
    assert FTPsServer.ftps_server.max_conn == 50
    assert FTPsServer.ftps_server.max_conn_per_ip == 5
    assert FTPsServer.ftps_server.ftp_dir == "/Documents/ftp"
    assert FTPsServer.ftps_server.handler is TLS_FTP_WADAS_Handler
    assert FTPsServer.ftps_server.handler.passive_ports == [1234, 5678]
    assert FTPsServer.ftps_server.handler.certfile == "/Documents/ssl/eshare_crt.pem"
    assert FTPsServer.ftps_server.handler.keyfile == "/Documents/ssl/eshare_key.pem"
    assert FTPsServer.ftps_server.handler.banner == "WADAS FTPS server!"
    assert isinstance(FTPsServer.ftps_server.handler.authorizer, DummyAuthorizer)
    assert Actuator.actuators == {}
    assert cameras == []
    assert Camera.detection_params == {}
    assert FastAPIActuatorServer.actuator_server is None
    assert AiModel.detection_model_version == "MDV5-yolov5"
    assert AiModel.classification_model_version == "DFv1.2"
    assert AiModel.classification_threshold == 0
    assert AiModel.detection_threshold == 0
    assert AiModel.language == ""
    assert AiModel.detection_device == "auto"
    assert AiModel.classification_device == "auto"
    assert AiModel.video_fps == 1
    assert OperationMode.cur_operation_mode is None
    assert OperationMode.cur_operation_mode_type is None


@patch(
    "builtins.open",
    new_callable=OpenStringMock,
    read_data=f"""
actuator_server:
actuators: []
ai_model:
  ai_class_threshold: 0
  ai_classification_device: auto
  ai_classification_model_version: DFv1.2
  ai_detect_threshold: 0
  ai_detection_device: auto
  ai_detection_model_version: MDV5-yolov5
  ai_language: ''
  ai_video_fps: 1
cameras: []
camera_detection_params: {{}}
database: ''
ftps_server:
  ftp_dir: /Documents/ftp
  ip: 1.2.3.4
  max_conn: 50
  max_conn_per_ip: 5
  passive_ports: [1234, 5678]
  port: 567
  ssl_certificate: /Documents/ssl/eshare_crt.pem
  ssl_key: /Documents/ssl/eshare_key.pem
notification: []
operation_mode:
uuid: 39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede
version: {__version__}
""",
)
def test_load_ftps_server_config_with_existing_server(mock_file, init):
    FTPsServer.ftps_server = FTPsServer(
        "5.6.7.8", 321, [4321, 8765], 23, 7, "X/Y.pem", "A/B.pem", "/Z"
    )
    FTPsServer.ftps_server.server = old_server = MagicMock()
    assert load_configuration_from_file("") == {
        "errors_on_load": False,
        "errors_log": "",
        "config_version": Version(__version__),
        "compatible_config": True,
        "uuid": "39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede",
        "valid_ftp_keyring": True,
        "valid_email_keyring": True,
        "valid_whatsapp_keyring": True,
    }
    old_server.close_all.assert_called_once_with()
    assert Notifier.notifiers == {"Email": None, "WhatsApp": None}
    assert FTPsServer.ftps_server is not None
    assert FTPsServer.ftps_server.ip == "1.2.3.4"
    assert FTPsServer.ftps_server.port == 567
    assert FTPsServer.ftps_server.max_conn == 50
    assert FTPsServer.ftps_server.max_conn_per_ip == 5
    assert FTPsServer.ftps_server.ftp_dir == "/Documents/ftp"
    assert FTPsServer.ftps_server.handler is TLS_FTP_WADAS_Handler
    assert FTPsServer.ftps_server.handler.passive_ports == [1234, 5678]
    assert FTPsServer.ftps_server.handler.certfile == "/Documents/ssl/eshare_crt.pem"
    assert FTPsServer.ftps_server.handler.keyfile == "/Documents/ssl/eshare_key.pem"
    assert FTPsServer.ftps_server.handler.banner == "WADAS FTPS server!"
    assert isinstance(FTPsServer.ftps_server.handler.authorizer, DummyAuthorizer)
    assert Actuator.actuators == {}
    assert cameras == []
    assert Camera.detection_params == {}
    assert FastAPIActuatorServer.actuator_server is None
    assert AiModel.detection_model_version == "MDV5-yolov5"
    assert AiModel.classification_model_version == "DFv1.2"
    assert AiModel.classification_threshold == 0
    assert AiModel.detection_threshold == 0
    assert AiModel.language == ""
    assert AiModel.detection_device == "auto"
    assert AiModel.classification_device == "auto"
    assert AiModel.video_fps == 1
    assert OperationMode.cur_operation_mode is None
    assert OperationMode.cur_operation_mode_type is None


@patch("builtins.open", new_callable=OpenStringMock, create=True)
def test_save_ftps_server_config(mock_file, init):
    FTPsServer.ftps_server = FTPsServer(
        "1.2.3.4",
        567,
        [1234, 5678],
        50,
        5,
        "/Documents/ssl/eshare_crt.pem",
        "/Documents/ssl/eshare_key.pem",
        "/Documents/ftp",
    )
    save_configuration_to_file("", "39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede")
    assert (
        mock_file.dump()
        == f"""actuator_server: ''
actuators: []
ai_model:
  ai_class_threshold: 0
  ai_classification_device: auto
  ai_classification_model_version: DFv1.2
  ai_detect_threshold: 0
  ai_detection_device: auto
  ai_detection_model_version: MDV5-yolov5
  ai_language: ''
  ai_video_fps: 1
camera_detection_params: {{}}
cameras: []
database: ''
ftps_server:
  ftp_dir: /Documents/ftp
  ip: 1.2.3.4
  max_conn: 50
  max_conn_per_ip: 5
  passive_ports:
  - 1234
  - 5678
  port: 567
  ssl_certificate: /Documents/ssl/eshare_crt.pem
  ssl_key: /Documents/ssl/eshare_key.pem
notification: ''
operation_mode: ''
uuid: 39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede
version: {__version__}
"""
    )


@patch(
    "builtins.open",
    new_callable=OpenStringMock,
    read_data=f"""
actuator_server:
actuators: []
ai_model:
  ai_class_threshold: 0
  ai_classification_device: auto
  ai_classification_model_version: DFv1.2
  ai_detect_threshold: 0
  ai_detection_device: auto
  ai_detection_model_version: MDV5-yolov5
  ai_language: ''
  ai_video_fps: 1
cameras: []
camera_detection_params: {{}}
database: ''
ftps_server: []
notification:
  Email:
    enabled: false
    recipients_email:
    - foo@wadas.org
    - bar@wadas.org
    sender_email: development@wadas.org
    smtp_hostname: smtp.wadas.org
    smtp_port: 123
operation_mode:
uuid: 39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede
version: {__version__}
""",
)
def test_load_notification_config_with_no_credentials(mock_file, init):
    with patch("keyring.get_credential") as get_credential_mock:
        get_credential_mock.return_value = None
        assert load_configuration_from_file("") == {
            "errors_on_load": False,
            "errors_log": "",
            "config_version": Version(__version__),
            "compatible_config": True,
            "uuid": "39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede",
            "valid_ftp_keyring": True,
            "valid_email_keyring": False,
            "valid_whatsapp_keyring": True,
        }
    get_credential_mock.assert_called_once_with("WADAS_email", "development@wadas.org")
    assert sorted(Notifier.notifiers.keys()) == ["Email", "WhatsApp"]
    notifier = Notifier.notifiers["Email"]
    assert notifier.enabled is False
    assert notifier.type == Notifier.NotifierTypes.EMAIL
    assert notifier.sender_email == "development@wadas.org"
    assert notifier.smtp_hostname == "smtp.wadas.org"
    assert notifier.smtp_port == 123
    assert notifier.recipients_email == ["foo@wadas.org", "bar@wadas.org"]
    assert Actuator.actuators == {}
    assert FTPsServer.ftps_server is None
    assert Actuator.actuators == {}
    assert cameras == []
    assert Camera.detection_params == {}
    assert FastAPIActuatorServer.actuator_server is None
    assert AiModel.detection_model_version == "MDV5-yolov5"
    assert AiModel.classification_model_version == "DFv1.2"
    assert AiModel.classification_threshold == 0
    assert AiModel.detection_threshold == 0
    assert AiModel.language == ""
    assert AiModel.detection_device == "auto"
    assert AiModel.classification_device == "auto"
    assert AiModel.video_fps == 1
    assert OperationMode.cur_operation_mode is None
    assert OperationMode.cur_operation_mode_type is None


@patch(
    "builtins.open",
    new_callable=OpenStringMock,
    read_data=f"""
actuator_server:
actuators: []
ai_model:
  ai_class_threshold: 0
  ai_classification_device: auto
  ai_classification_model_version: DFv1.2
  ai_detect_threshold: 0
  ai_detection_device: auto
  ai_detection_model_version: MDV5-yolov5
  ai_language: ''
  ai_video_fps: 1
cameras: []
camera_detection_params: {{}}
database: ''
ftps_server: []
notification:
  Email:
    enabled: false
    recipients_email:
    - foo@wadas.org
    - bar@wadas.org
    sender_email: development@wadas.org
    smtp_hostname: smtp.wadas.org
    smtp_port: 123
operation_mode:
uuid: 39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede
version: {__version__}
""",
)
def test_load_notification_config_with_same_credentials(mock_file, init):
    with patch("keyring.get_credential") as get_credential_mock:
        get_credential_mock.return_value = Mock(username="development@wadas.org", password="123")
        assert load_configuration_from_file("") == {
            "errors_on_load": False,
            "errors_log": "",
            "config_version": Version(__version__),
            "compatible_config": True,
            "uuid": "39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede",
            "valid_ftp_keyring": True,
            "valid_email_keyring": True,
            "valid_whatsapp_keyring": True,
        }
    get_credential_mock.assert_called_once_with("WADAS_email", "development@wadas.org")
    assert sorted(Notifier.notifiers.keys()) == ["Email", "WhatsApp"]
    notifier = Notifier.notifiers["Email"]
    assert notifier.enabled is False
    assert notifier.type == Notifier.NotifierTypes.EMAIL
    assert notifier.sender_email == "development@wadas.org"
    assert notifier.smtp_hostname == "smtp.wadas.org"
    assert notifier.smtp_port == 123
    assert notifier.recipients_email == ["foo@wadas.org", "bar@wadas.org"]
    assert Actuator.actuators == {}
    assert FTPsServer.ftps_server is None
    assert Actuator.actuators == {}
    assert cameras == []
    assert Camera.detection_params == {}
    assert FastAPIActuatorServer.actuator_server is None
    assert AiModel.detection_model_version == "MDV5-yolov5"
    assert AiModel.classification_model_version == "DFv1.2"
    assert AiModel.classification_threshold == 0
    assert AiModel.detection_threshold == 0
    assert AiModel.language == ""
    assert AiModel.detection_device == "auto"
    assert AiModel.classification_device == "auto"
    assert AiModel.video_fps == 1
    assert OperationMode.cur_operation_mode is None
    assert OperationMode.cur_operation_mode_type is None


@patch(
    "builtins.open",
    new_callable=OpenStringMock,
    read_data=f"""
actuator_server:
actuators: []
ai_model:
  ai_class_threshold: 0
  ai_classification_device: auto
  ai_classification_model_version: DFv1.2
  ai_detect_threshold: 0
  ai_detection_device: auto
  ai_detection_model_version: MDV5-yolov5
  ai_language: ''
  ai_video_fps: 1
cameras: []
camera_detection_params: {{}}
database: ''
ftps_server: []
notification:
  Email:
    enabled: false
    recipients_email:
    - foo@wadas.org
    - bar@wadas.org
    sender_email: development@wadas.org
    smtp_hostname: smtp.wadas.org
    smtp_port: 123
operation_mode:
uuid: 39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede
version: {__version__}
""",
)
def test_load_notification_config_with_different_credentials(mock_file, init):
    with patch("keyring.get_credential") as get_credential_mock:
        get_credential_mock.return_value = Mock(username="UnknownEmail", password="123")
        assert load_configuration_from_file("") == {
            "errors_on_load": False,
            "errors_log": "",
            "config_version": Version(__version__),
            "compatible_config": True,
            "uuid": "39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede",
            "valid_ftp_keyring": True,
            "valid_email_keyring": False,
            "valid_whatsapp_keyring": True,
        }
    get_credential_mock.assert_called_once_with("WADAS_email", "development@wadas.org")
    assert sorted(Notifier.notifiers.keys()) == ["Email", "WhatsApp"]
    notifier = Notifier.notifiers["Email"]
    assert notifier.enabled is False
    assert notifier.type == Notifier.NotifierTypes.EMAIL
    assert notifier.sender_email == "development@wadas.org"
    assert notifier.smtp_hostname == "smtp.wadas.org"
    assert notifier.smtp_port == 123
    assert notifier.recipients_email == ["foo@wadas.org", "bar@wadas.org"]
    assert Actuator.actuators == {}
    assert FTPsServer.ftps_server is None
    assert Actuator.actuators == {}
    assert cameras == []
    assert Camera.detection_params == {}
    assert FastAPIActuatorServer.actuator_server is None
    assert AiModel.detection_model_version == "MDV5-yolov5"
    assert AiModel.classification_model_version == "DFv1.2"
    assert AiModel.classification_threshold == 0
    assert AiModel.detection_threshold == 0
    assert AiModel.language == ""
    assert AiModel.detection_device == "auto"
    assert AiModel.classification_device == "auto"
    assert AiModel.video_fps == 1
    assert OperationMode.cur_operation_mode is None
    assert OperationMode.cur_operation_mode_type is None


@patch(
    "builtins.open",
    new_callable=OpenStringMock,
    read_data=f"""
actuator_server:
actuators: []
ai_model:
  ai_class_threshold: 0
  ai_classification_device: auto
  ai_classification_model_version: DFv1.2
  ai_detect_threshold: 0
  ai_detection_device: auto
  ai_detection_model_version: MDV5-yolov5
  ai_language: ''
  ai_video_fps: 1
cameras: []
camera_detection_params: {{}}
database: ''
ftps_server: []
notification:
  Email:
    enabled: true
    recipients_email:
    - foo@wadas.org
    - bar@wadas.org
    sender_email: development@wadas.org
    smtp_hostname: smtp.wadas.org
    smtp_port: 123
operation_mode:
uuid: 39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede
version: {__version__}
""",
)
def test_load_enabled_notification_config(mock_file, init):
    with patch("keyring.get_credential") as get_credential_mock:
        get_credential_mock.return_value = None
        assert load_configuration_from_file("") == {
            "errors_on_load": False,
            "errors_log": "",
            "config_version": Version(__version__),
            "compatible_config": True,
            "uuid": "39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede",
            "valid_ftp_keyring": True,
            "valid_email_keyring": False,
            "valid_whatsapp_keyring": True,
        }
    get_credential_mock.assert_called_once_with("WADAS_email", "development@wadas.org")
    assert sorted(Notifier.notifiers.keys()) == ["Email", "WhatsApp"]
    notifier = Notifier.notifiers["Email"]
    assert notifier.enabled is True


@patch("builtins.open", new_callable=OpenStringMock, create=True)
def test_save_notification_config(mock_file, init):
    Notifier.notifiers["Email"] = EmailNotifier(
        "development@wadas.org", "smtp.wadas.org", 123, ["foo@wadas.org", "bar@wadas.org"], False
    )
    save_configuration_to_file("", "39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede")
    assert (
        mock_file.dump()
        == f"""actuator_server: ''
actuators: []
ai_model:
  ai_class_threshold: 0
  ai_classification_device: auto
  ai_classification_model_version: DFv1.2
  ai_detect_threshold: 0
  ai_detection_device: auto
  ai_detection_model_version: MDV5-yolov5
  ai_language: ''
  ai_video_fps: 1
camera_detection_params: {{}}
cameras: []
database: ''
ftps_server: ''
notification:
  Email:
    enabled: false
    recipients_email:
    - foo@wadas.org
    - bar@wadas.org
    sender_email: development@wadas.org
    smtp_hostname: smtp.wadas.org
    smtp_port: 123
operation_mode: ''
uuid: 39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede
version: {__version__}
"""
    )


@patch("builtins.open", new_callable=OpenStringMock, create=True)
def test_save_enabled_notification_config(mock_file, init):
    Notifier.notifiers["Email"] = EmailNotifier(
        "development@wadas.org", "smtp.wadas.org", 123, ["foo@wadas.org", "bar@wadas.org"], True
    )
    save_configuration_to_file("", "39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede")
    assert (
        mock_file.dump()
        == f"""actuator_server: ''
actuators: []
ai_model:
  ai_class_threshold: 0
  ai_classification_device: auto
  ai_classification_model_version: DFv1.2
  ai_detect_threshold: 0
  ai_detection_device: auto
  ai_detection_model_version: MDV5-yolov5
  ai_language: ''
  ai_video_fps: 1
camera_detection_params: {{}}
cameras: []
database: ''
ftps_server: ''
notification:
  Email:
    enabled: true
    recipients_email:
    - foo@wadas.org
    - bar@wadas.org
    sender_email: development@wadas.org
    smtp_hostname: smtp.wadas.org
    smtp_port: 123
operation_mode: ''
uuid: 39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede
version: {__version__}
"""
    )


@patch(
    "builtins.open",
    new_callable=OpenStringMock,
    read_data=f"""
actuator_server:
actuators: []
ai_model:
  ai_class_threshold: 0
  ai_classification_device: auto
  ai_classification_model_version: DFv1.2
  ai_detect_threshold: 0
  ai_detection_device: auto
  ai_detection_model_version: MDV5-yolov5
  ai_language: ''
  ai_video_fps: 1
cameras: []
camera_detection_params: {{}}
database: ''
ftps_server: []
notification: []
operation_mode:
    type: Test Model Mode
uuid: 39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede
version: {__version__}
""",
)
def test_load_test_model_mode_config(mock_file, init):
    assert load_configuration_from_file("") == {
        "errors_on_load": False,
        "errors_log": "",
        "config_version": Version(__version__),
        "compatible_config": True,
        "uuid": "39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede",
        "valid_ftp_keyring": True,
        "valid_email_keyring": True,
        "valid_whatsapp_keyring": True,
    }
    assert Notifier.notifiers == {"Email": None, "WhatsApp": None}
    assert FTPsServer.ftps_server is None
    assert Actuator.actuators == {}
    assert cameras == []
    assert Camera.detection_params == {}
    assert FastAPIActuatorServer.actuator_server is None
    assert AiModel.detection_model_version == "MDV5-yolov5"
    assert AiModel.classification_model_version == "DFv1.2"
    assert AiModel.classification_threshold == 0
    assert AiModel.detection_threshold == 0
    assert AiModel.language == ""
    assert AiModel.detection_device == "auto"
    assert AiModel.classification_device == "auto"
    assert AiModel.video_fps == 1
    assert OperationMode.cur_operation_mode is None
    assert OperationMode.cur_operation_mode_type == OperationMode.OperationModeTypes.TestModelMode


@patch("builtins.open", new_callable=OpenStringMock, create=True)
def test_save_test_model_mode_config(mock_file, init):
    OperationMode.cur_operation_mode_type = OperationMode.OperationModeTypes.TestModelMode
    save_configuration_to_file("", "39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede")
    assert (
        mock_file.dump()
        == f"""actuator_server: ''
actuators: []
ai_model:
  ai_class_threshold: 0
  ai_classification_device: auto
  ai_classification_model_version: DFv1.2
  ai_detect_threshold: 0
  ai_detection_device: auto
  ai_detection_model_version: MDV5-yolov5
  ai_language: ''
  ai_video_fps: 1
camera_detection_params: {{}}
cameras: []
database: ''
ftps_server: ''
notification: ''
operation_mode:
  type: Test Model Mode
uuid: 39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede
version: {__version__}
"""
    )


@patch(
    "builtins.open",
    new_callable=OpenStringMock,
    read_data=f"""
actuator_server:
actuators: []
ai_model:
  ai_class_threshold: 0
  ai_classification_device: auto
  ai_classification_model_version: DFv1.2
  ai_detect_threshold: 0
  ai_detection_device: auto
  ai_detection_model_version: MDV5-yolov5
  ai_language: ''
  ai_video_fps: 1
cameras: []
camera_detection_params: {{}}
database: ''
ftps_server: []
notification: []
operation_mode:
    type: Animal Detection Mode
uuid: 39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede
version: {__version__}
""",
)
def test_load_animal_detection_mode_config(mock_file, init):
    assert load_configuration_from_file("") == {
        "errors_on_load": False,
        "errors_log": "",
        "config_version": Version(__version__),
        "compatible_config": True,
        "uuid": "39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede",
        "valid_ftp_keyring": True,
        "valid_email_keyring": True,
        "valid_whatsapp_keyring": True,
    }
    assert OperationMode.cur_operation_mode is None
    assert (
        OperationMode.cur_operation_mode_type
        == OperationMode.OperationModeTypes.AnimalDetectionMode
    )


@patch("builtins.open", new_callable=OpenStringMock, create=True)
def test_save_animal_detection_mode_config(mock_file, init):
    OperationMode.cur_operation_mode_type = OperationMode.OperationModeTypes.AnimalDetectionMode
    save_configuration_to_file("", "39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede")
    assert (
        mock_file.dump()
        == f"""actuator_server: ''
actuators: []
ai_model:
  ai_class_threshold: 0
  ai_classification_device: auto
  ai_classification_model_version: DFv1.2
  ai_detect_threshold: 0
  ai_detection_device: auto
  ai_detection_model_version: MDV5-yolov5
  ai_language: ''
  ai_video_fps: 1
camera_detection_params: {{}}
cameras: []
database: ''
ftps_server: ''
notification: ''
operation_mode:
  type: Animal Detection Mode
uuid: 39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede
version: {__version__}
"""
    )


@patch(
    "builtins.open",
    new_callable=OpenStringMock,
    read_data=f"""
actuator_server:
actuators: []
ai_model:
  ai_class_threshold: 0
  ai_classification_device: auto
  ai_classification_model_version: DFv1.2
  ai_detect_threshold: 0
  ai_detection_device: auto
  ai_detection_model_version: MDV5-yolov5
  ai_language: ''
  ai_video_fps: 1
cameras: []
camera_detection_params: {{}}
database: ''
ftps_server: []
notification: []
operation_mode:
    type: Animal Detection and Classification Mode
uuid: 39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede
version: {__version__}
""",
)
def test_load_animal_detection_and_classification_mode_config(mock_file, init):
    assert load_configuration_from_file("") == {
        "errors_on_load": False,
        "errors_log": "",
        "config_version": Version(__version__),
        "compatible_config": True,
        "uuid": "39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede",
        "valid_ftp_keyring": True,
        "valid_email_keyring": True,
        "valid_whatsapp_keyring": True,
    }
    assert OperationMode.cur_operation_mode is None
    assert (
        OperationMode.cur_operation_mode_type
        == OperationMode.OperationModeTypes.AnimalDetectionAndClassificationMode
    )


@patch("builtins.open", new_callable=OpenStringMock, create=True)
def test_save_animal_detection_and_classification_mode_config(mock_file, init):
    OperationMode.cur_operation_mode_type = (
        OperationMode.OperationModeTypes.AnimalDetectionAndClassificationMode
    )
    save_configuration_to_file("", "39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede")
    assert (
        mock_file.dump()
        == f"""actuator_server: ''
actuators: []
ai_model:
  ai_class_threshold: 0
  ai_classification_device: auto
  ai_classification_model_version: DFv1.2
  ai_detect_threshold: 0
  ai_detection_device: auto
  ai_detection_model_version: MDV5-yolov5
  ai_language: ''
  ai_video_fps: 1
camera_detection_params: {{}}
cameras: []
database: ''
ftps_server: ''
notification: ''
operation_mode:
  type: Animal Detection and Classification Mode
uuid: 39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede
version: {__version__}
"""
    )


@patch(
    "builtins.open",
    new_callable=OpenStringMock,
    read_data=f"""
actuator_server:
actuators: []
ai_model:


  ai_class_threshold: 0
  ai_classification_device: auto
  ai_classification_model_version: DFv1.2
  ai_detect_threshold: 0
  ai_detection_device: auto
  ai_detection_model_version: MDV5-yolov5
  ai_language: ''
  ai_video_fps: 1
cameras: []
camera_detection_params: {{}}
database: ''
ftps_server: []
notification: []
operation_mode:
    type: Custom Species Classification Mode
    custom_target_species: chamois
uuid: 39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede
version: {__version__}
""",
)
def test_load_custom_species_classification_mode_config(mock_file, init):
    assert load_configuration_from_file("") == {
        "errors_on_load": False,
        "errors_log": "",
        "config_version": Version(__version__),
        "compatible_config": True,
        "uuid": "39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede",
        "valid_ftp_keyring": True,
        "valid_email_keyring": True,
        "valid_whatsapp_keyring": True,
    }
    assert OperationMode.cur_operation_mode is None
    assert (
        OperationMode.cur_operation_mode_type
        == OperationMode.OperationModeTypes.CustomSpeciesClassificationMode
    )
    assert OperationMode.cur_custom_classification_species == "chamois"


@patch("builtins.open", new_callable=OpenStringMock, create=True)
def test_save_custom_species_classification_mode_config(mock_file, init):
    OperationMode.cur_operation_mode_type = (
        OperationMode.OperationModeTypes.CustomSpeciesClassificationMode
    )
    OperationMode.cur_custom_classification_species = "chamois"
    save_configuration_to_file("", "39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede")
    assert (
        mock_file.dump()
        == f"""actuator_server: ''
actuators: []
ai_model:
  ai_class_threshold: 0
  ai_classification_device: auto
  ai_classification_model_version: DFv1.2
  ai_detect_threshold: 0
  ai_detection_device: auto
  ai_detection_model_version: MDV5-yolov5
  ai_language: ''
  ai_video_fps: 1
camera_detection_params: {{}}
cameras: []
database: ''
ftps_server: ''
notification: ''
operation_mode:
  custom_target_species: chamois
  type: Custom Species Classification Mode
uuid: 39f89e5c-56bb-4ab3-8cb0-dd8450cc8ede
version: {__version__}
"""
    )
