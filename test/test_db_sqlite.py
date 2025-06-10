import datetime
import logging

import pytest
from sqlalchemy import update
from sqlalchemy.engine import Engine
from sqlalchemy.orm.session import Session

from wadas._version import __dbversion__
from wadas.domain.database import DataBase, SQLiteDataBase
from wadas.domain.db_model import (
    ActuationEvent,
    Actuator,
    Camera,
    ClassifiedAnimals,
    DBMetadata,
    DetectionEvent,
    FeederActuator,
    FTPCamera,
    RoadSignActuator,
    USBCamera,
    camera_actuator_association,
)

logger = logging.getLogger(__name__)


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
def db(init):
    assert DataBase.initialize(DataBase.DBTypes.SQLITE, ":memory:", None, "", "") is True
    db = DataBase.get_instance()
    session = DataBase.create_session()
    assert db.create_database() is True
    yield db, session
    DataBase.destroy_instance()


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


def test_no_db_uuid_without_populated_db(db):
    db, session = db
    assert db.get_db_uuid() is None


def test_get_db_uuid(db):
    db, session = db
    db.populate_db("FAKE_UUID")
    assert db.get_db_uuid() == "FAKE_UUID"


def test_no_db_version_without_session(init):
    assert DataBase.get_db_version() is None


def test_no_db_version_without_populated_db(db):
    db, session = db
    assert db.get_db_version() is None


def test_get_db_version(db):
    db, session = db
    db.populate_db("FAKE_UUID")
    assert db.get_db_version() == __dbversion__


def test_bad_statement_on_run_query(db):
    db, session = db
    db.populate_db("FAKE_UUID")
    assert DataBase.run_query(None) is False


def test_run_query(db):
    db, session = db
    db.populate_db("FAKE_UUID")
    stmt = update(DBMetadata).values(project_uuid="NEW_FAKE_UUID")
    assert DataBase.run_query(stmt) is True
    assert db.get_db_uuid() == "NEW_FAKE_UUID"


def test_connection_string(db):
    db, session = db
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


def test_empty_database(db):
    db, session = db
    assert session.query(ActuationEvent).count() == 0
    assert session.query(Actuator).count() == 0
    assert session.query(Camera).count() == 0
    assert session.query(ClassifiedAnimals).count() == 0
    assert session.query(DBMetadata).count() == 0
    assert session.query(DetectionEvent).count() == 0
    assert session.query(FeederActuator).count() == 0
    assert session.query(FTPCamera).count() == 0
    assert session.query(RoadSignActuator).count() == 0
    assert session.query(USBCamera).count() == 0
    assert session.query(camera_actuator_association).count() == 0


def test_create_metadata(db):
    db, session = db
    db.populate_db("FAKE_UUID")
    rows = session.query(DBMetadata).all()
    assert len(rows) == 1
    row = rows[0]
    assert row.db_id == 1
    assert row.version == __dbversion__
    time_delta = datetime.datetime.now() - row.applied_at
    assert time_delta.days == 0
    assert time_delta.seconds == 0
    assert row.description == "WADAS database"
    assert row.project_uuid == "FAKE_UUID"
