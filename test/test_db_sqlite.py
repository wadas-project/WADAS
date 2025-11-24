import datetime
import logging
from unittest.mock import patch

import pytest
from sqlalchemy import update
from sqlalchemy.engine import Engine
from sqlalchemy.orm.session import Session

import wadas.domain.db_model
from wadas._version import __dbversion__
from wadas.domain.actuation_event import ActuationEvent
from wadas.domain.database import DataBase, DBMetadata, DBUser, SQLiteDataBase
from wadas.domain.detection_event import DetectionEvent
from wadas.domain.feeder_actuator import FeederActuator
from wadas.domain.ftp_camera import FTPCamera
from wadas.domain.roadsign_actuator import RoadSignActuator
from wadas.domain.usb_camera import USBCamera

logger = logging.getLogger(__name__)
THE_ARRIVAL_DATE = datetime.datetime(1984, 5, 12, 1, 52)
SELF_AWARE_DATE = datetime.datetime(1997, 8, 29, 2, 14)


class Bag:
    """A base object where we can freely add any member"""

    pass


@pytest.fixture
def init():
    if DataBase.wadas_db_engine is not None:
        DataBase.destroy_instance()
        assert DataBase.wadas_db_engine is None
        assert DataBase.wadas_db is None
    if DataBase.wadas_db is not None:
        logger.debug("Found an active db instance before test execution...")
        DataBase.wadas_db = None


@pytest.fixture()
def empty_db(init):
    assert DataBase.initialize(DataBase.DBTypes.SQLITE, ":memory:", None, "", "") is True
    db = DataBase.get_instance()
    session = db.create_session()
    assert db.create_database() is True
    yield db, session
    db.destroy_instance()


@pytest.fixture()
def db(empty_db):
    db, session = empty_db
    db.populate_db("FAKE_UUID")
    yield db, session


def test_database_already_created(init):
    DataBase.wadas_db = True
    with pytest.raises(RuntimeError, match="Database instance already created."):
        SQLiteDataBase("NOT-USED-HOST")


def test_database_already_initialized(init):
    DataBase.wadas_db = True
    assert DataBase.initialize(DataBase.DBTypes.SQLITE, "NOT-USED-HOST", None, "", "") is False


def test_no_host(init):
    assert DataBase.initialize(DataBase.DBTypes.SQLITE, "", None, "", "") is False


def test_unsupported_database(init):
    with pytest.raises(ValueError, match="Unsupported database type: DUMMY-DB-TYPE"):
        DataBase.initialize("DUMMY-DB-TYPE", "NOT-USED-HOST", None, "", "")


def test_db_not_enabled(init):
    assert DataBase.initialize(DataBase.DBTypes.SQLITE, ":memory:", None, "", "", False) is True
    assert DataBase.wadas_db.enabled is False


def test_db_enabled(init):
    assert DataBase.initialize(DataBase.DBTypes.SQLITE, ":memory:", None, "", "") is True
    assert DataBase.wadas_db.enabled is True


def test_default_db_version(init):
    assert DataBase.initialize(DataBase.DBTypes.SQLITE, ":memory:", None, "", "") is True
    assert DataBase.wadas_db.version == __dbversion__


def test_set_db_version(init):
    assert (
        DataBase.initialize(DataBase.DBTypes.SQLITE, ":memory:", None, "", "", version="X.Y.Z")
        is True
    )
    assert DataBase.wadas_db.version == "X.Y.Z"


def test_no_engine_and_no_database(init):
    with pytest.raises(RuntimeError, match="The database and db engine have not been initialized."):
        DataBase.get_engine()


def test_get_engine(init):
    assert DataBase.wadas_db_engine is None
    assert DataBase.initialize(DataBase.DBTypes.SQLITE, ":memory:", None, "", "", False) is True
    assert DataBase.wadas_db is not None
    assert DataBase.get_engine() is DataBase.wadas_db_engine
    assert DataBase.wadas_db_engine is not None
    assert isinstance(DataBase.wadas_db_engine, Engine) is True


def test_no_database(init):
    assert DataBase.get_instance() is None


def test_get_instance(init):
    assert DataBase.wadas_db is None
    assert DataBase.initialize(DataBase.DBTypes.SQLITE, ":memory:", None, "", "") is True
    assert DataBase.get_instance() is DataBase.wadas_db
    assert DataBase.wadas_db is not None


def test_get_disabled_db(init):
    assert DataBase.wadas_db is None
    assert DataBase.get_enabled_db() is None
    assert DataBase.initialize(DataBase.DBTypes.SQLITE, ":memory:", None, "", "", False) is True
    assert DataBase.wadas_db is not None
    assert DataBase.get_enabled_db() is None
    assert DataBase.wadas_db is not None


def test_get_enabled_db(init):
    assert DataBase.wadas_db is None
    assert DataBase.get_enabled_db() is None
    assert DataBase.initialize(DataBase.DBTypes.SQLITE, ":memory:", None, "", "") is True
    assert DataBase.wadas_db is not None
    assert DataBase.get_enabled_db() is DataBase.wadas_db


def test_destroy_instance(init):
    DataBase.wadas_db_engine = True
    DataBase.destroy_instance()
    assert DataBase.wadas_db_engine is None


def test_no_session_without_engine(init):
    assert DataBase.create_session() is None


def test_create_session(init):
    assert DataBase.initialize(DataBase.DBTypes.SQLITE, ":memory:", None, "", "") is True
    session = DataBase.create_session()
    assert isinstance(session, Session) is True


def test_no_db_uuid_without_session(init):
    assert DataBase.get_db_uuid() is None


def test_no_db_uuid_without_populated_db(empty_db):
    db, session = empty_db
    assert db.get_db_uuid() is None


def test_get_db_uuid(db):
    db, session = db
    assert db.get_db_uuid() == "FAKE_UUID"


def test_no_db_version_without_session(init):
    assert DataBase.get_db_version() is None


def test_no_db_version_without_populated_db(empty_db):
    db, session = empty_db
    assert db.get_db_version() is None


def test_get_db_version(db):
    db, session = db
    assert db.get_db_version() == __dbversion__


def test_bad_statement_on_run_query(db):
    db, session = db
    assert db.run_query(None) is False


def test_run_query(db):
    db, session = db
    stmt = update(wadas.domain.db_model.DBMetadata).values(project_uuid="NEW_FAKE_UUID")
    assert db.run_query(stmt) is True
    assert db.get_db_uuid() == "NEW_FAKE_UUID"


def test_unknown_object_to_orm(db):
    db, session = db
    with pytest.raises(ValueError, match="Unsupported domain object type: NoneType"):
        db.domain_to_orm(None)


def test_ftpcamera_to_orm(db):
    db, session = db
    with patch("wadas.domain.database.get_precise_timestamp") as func:
        func.return_value = SELF_AWARE_DATE
        orm = db.domain_to_orm(FTPCamera("Camera1", "/Documents/ftp/Camera1", False))
    assert isinstance(orm, wadas.domain.db_model.FTPCamera)
    assert orm.camera_id == "Camera1"
    assert orm.enabled is False
    assert orm.ftp_folder == "/Documents/ftp/Camera1"
    assert orm.creation_date is SELF_AWARE_DATE


def test_usbcamera_to_orm(db):
    db, session = db
    with patch("wadas.domain.database.get_precise_timestamp") as func:
        func.return_value = SELF_AWARE_DATE
        orm = db.domain_to_orm(
            USBCamera(
                "cvbdfg",
                "ASUS USB2.0 Webcam",
                True,
                0,
                1400,
                True,
                10371,
                7119,
                r"\\?\usb#vid_1bcf&pid_2883&mi_00#7&e89baf7&0&0000#"
                r"{e5323777-f976-4f5b-9b55-b94699c46e44}\global",
                [],
            )
        )
    assert isinstance(orm, wadas.domain.db_model.USBCamera)
    assert orm.camera_id == "cvbdfg"
    assert orm.name == "ASUS USB2.0 Webcam"
    assert orm.enabled is True
    assert orm.pid == 10371
    assert orm.vid == 7119
    assert (
        orm.path == r"\\?\usb#vid_1bcf&pid_2883&mi_00#7&e89baf7&0&0000#"
        r"{e5323777-f976-4f5b-9b55-b94699c46e44}\global"
    )
    assert orm.creation_date is SELF_AWARE_DATE


def test_roadsignactuator_to_orm(db):
    db, session = db
    with patch("wadas.domain.database.get_precise_timestamp") as func:
        func.return_value = SELF_AWARE_DATE
        orm = db.domain_to_orm(RoadSignActuator("Actuator3", True))
    assert isinstance(orm, wadas.domain.db_model.RoadSignActuator)
    assert orm.actuator_id == "Actuator3"
    assert orm.enabled is True
    assert orm.creation_date is SELF_AWARE_DATE


def test_feederactuator_to_orm(db):
    db, session = db
    with patch("wadas.domain.database.get_precise_timestamp") as func:
        func.return_value = SELF_AWARE_DATE
        orm = db.domain_to_orm(FeederActuator("Actuator2", True))
    assert isinstance(orm, wadas.domain.db_model.FeederActuator)
    assert orm.actuator_id == "Actuator2"
    assert orm.enabled is True
    assert orm.creation_date is SELF_AWARE_DATE


def test_actuationevent_to_orm(db):
    db, session = db
    camera = db.domain_to_orm(FTPCamera("Camera2", "/Documents/ftp/Camera2", True))
    assert isinstance(camera, wadas.domain.db_model.FTPCamera)
    actuator = db.domain_to_orm(FeederActuator("TestActuator", True))
    assert isinstance(actuator, wadas.domain.db_model.Actuator)
    detections = {"detections": Bag()}
    detections["detections"].xyxy = ["Foo", "Bar"]
    detection_event = db.domain_to_orm(
        DetectionEvent(
            "Camera2",
            datetime.datetime.now(),
            "orig_img_path",
            "detected_img_path",
            detections,
            False,
            "cls_img_path",
        ),
        ["Camera2"],
    )
    assert isinstance(detection_event, wadas.domain.db_model.DetectionEvent)
    orm = db.domain_to_orm(
        ActuationEvent(
            "TestActuator", SELF_AWARE_DATE, detection_event, FeederActuator.Commands.OPEN
        ),
        [actuator.db_id, detection_event.db_id],
    )
    assert orm.actuator_id == actuator.db_id
    assert orm.time_stamp is SELF_AWARE_DATE
    assert orm.detection_event_id == detection_event.db_id
    assert orm.command == "open"


def test_detectionevent_to_orm(db):
    db, session = db
    camera = db.domain_to_orm(FTPCamera("Camera2", "/Documents/ftp/Camera2", True))
    assert isinstance(camera, wadas.domain.db_model.FTPCamera)
    detections = {"detections": Bag()}
    detections["detections"].xyxy = ["Foo", "Bar"]
    orm = db.domain_to_orm(
        DetectionEvent(
            "Camera2",
            SELF_AWARE_DATE,
            "orig_img_path",
            "detected_img_path",
            detections,
            False,
            "cls_img_path",
        ),
        ["Camera2"],
    )
    assert isinstance(orm, wadas.domain.db_model.DetectionEvent)
    assert orm.camera_id == "Camera2"
    assert orm.time_stamp is SELF_AWARE_DATE
    assert orm.original_image == "orig_img_path"
    assert orm.detection_img_path == "detected_img_path"
    assert orm.detected_animals == 2
    assert orm.classification is False
    assert orm.classification_img_path == "cls_img_path"


def test_dbmetadata_to_orm(db):
    db, session = db
    with patch("wadas.domain.database.get_precise_timestamp") as func:
        func.return_value = SELF_AWARE_DATE
        orm = db.domain_to_orm(DBMetadata("DB for test", "NEW_FAKE_UUID"))
    assert isinstance(orm, wadas.domain.db_model.DBMetadata)
    assert orm.version == __dbversion__
    assert orm.applied_at is SELF_AWARE_DATE
    assert orm.description == "DB for test"
    assert orm.project_uuid == "NEW_FAKE_UUID"


def test_dbuser_to_orm(db):
    db, session = db
    with patch("wadas.domain.database.get_precise_timestamp") as func:
        func.return_value = SELF_AWARE_DATE
        orm = db.domain_to_orm(DBUser("Foo", "Bar", "foo@bar.xyz", "Puppet"))
    assert isinstance(orm, wadas.domain.db_model.User)
    assert orm.username == "Foo"
    assert orm.password == "Bar"
    assert orm.email == "foo@bar.xyz"
    assert orm.role == "Puppet"
    assert orm.created_at is SELF_AWARE_DATE


def test_connection_string(empty_db):
    db, session = empty_db
    assert db is not None
    assert DataBase.wadas_db_engine is not None
    assert db.get_connection_string() == "sqlite:///:memory:"


# Specific SQLite tests start here.


def test_database_not_initialized(init):
    assert SQLiteDataBase("NOT-USED-HOST").create_database() is False


def test_serialize(init):
    assert SQLiteDataBase("NOT-USED-HOST").serialize() == {
        "host": "NOT-USED-HOST",
        "type": DataBase.DBTypes.SQLITE.value,
        "enabled": True,
        "version": __dbversion__,
    }
    assert SQLiteDataBase("NOT-USED-HOST2", False, "vX.Y.Z").serialize() == {
        "host": "NOT-USED-HOST2",
        "type": DataBase.DBTypes.SQLITE.value,
        "enabled": False,
        "version": "vX.Y.Z",
    }


def test_empty_database(empty_db):
    db, session = empty_db
    assert session.query(wadas.domain.db_model.ActuationEvent).count() == 0
    assert session.query(wadas.domain.db_model.Actuator).count() == 0
    assert session.query(wadas.domain.db_model.Camera).count() == 0
    assert session.query(wadas.domain.db_model.ClassifiedAnimals).count() == 0
    assert session.query(wadas.domain.db_model.DBMetadata).count() == 0
    assert session.query(wadas.domain.db_model.DetectionEvent).count() == 0
    assert session.query(wadas.domain.db_model.FeederActuator).count() == 0
    assert session.query(wadas.domain.db_model.FTPCamera).count() == 0
    assert session.query(wadas.domain.db_model.RoadSignActuator).count() == 0
    assert session.query(wadas.domain.db_model.USBCamera).count() == 0
    assert session.query(wadas.domain.db_model.camera_actuator_association).count() == 0


def test_create_metadata(db):
    db, session = db
    rows = session.query(wadas.domain.db_model.DBMetadata).all()
    assert len(rows) == 1
    row = rows[0]
    assert row.db_id == 1
    assert row.version == __dbversion__
    time_delta = datetime.datetime.now() - row.applied_at
    assert time_delta.days == 0
    assert time_delta.seconds == 0
    assert row.description == "WADAS database"
    assert row.project_uuid == "FAKE_UUID"
