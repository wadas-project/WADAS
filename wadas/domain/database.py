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
# Date: 2025-01-04
# Description: database module.

import json
import logging
from abc import ABC, abstractmethod
from enum import Enum

import keyring
from mariadb import OperationalError as mariadbOperationalerror
from pymysql import OperationalError as pymysqlOperationalError
from sqlalchemy import and_, create_engine, delete, select, text, update
from sqlalchemy.exc import IntegrityError, InterfaceError
from sqlalchemy.exc import OperationalError as SQLAlchemyOperationalError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from wadas._version import __dbversion__
from wadas.domain.actuation_event import ActuationEvent
from wadas.domain.actuator import Actuator
from wadas.domain.camera import cameras
from wadas.domain.db_model import ActuationEvent as ORMActuationEvent
from wadas.domain.db_model import Actuator as ORMActuator
from wadas.domain.db_model import Base
from wadas.domain.db_model import Camera as ORMCamera
from wadas.domain.db_model import ClassifiedAnimals as ORMClassifiedAnimals
from wadas.domain.db_model import DBMetadata as ORMDBMetadata
from wadas.domain.db_model import DetectionEvent as ORMDetectionEvent
from wadas.domain.db_model import FeederActuator as ORMFeederActuator
from wadas.domain.db_model import FTPCamera as ORMFTPCamera
from wadas.domain.db_model import RoadSignActuator as ORMRoadSignActuator
from wadas.domain.db_model import USBCamera as ORMUSBCamera
from wadas.domain.db_model import User as ORMUser
from wadas.domain.db_model import camera_actuator_association
from wadas.domain.detection_event import DetectionEvent
from wadas.domain.feeder_actuator import FeederActuator
from wadas.domain.ftp_camera import FTPCamera
from wadas.domain.roadsign_actuator import RoadSignActuator
from wadas.domain.usb_camera import USBCamera
from wadas.domain.utils import get_precise_timestamp

logger = logging.getLogger(__name__)


class DBMetadata:
    def __init__(self, description: str, project_uuid):
        self.version = __dbversion__
        self.applied_at = get_precise_timestamp()
        self.description = description
        self.project_uuid = project_uuid


class DBUser:
    def __init__(self, username, password, email, role):
        self.username = username
        self.password = password
        self.email = email
        self.role = role


class DataBase(ABC):
    """Base Class to handle DB object."""

    class DBTypes(Enum):
        SQLITE = "SQLite"
        MYSQL = "MySQL"
        MARIADB = "MariaDB"

    wadas_db = None  # Singleton instance of the database
    wadas_db_engine = None  # Singleton engine associated with the database
    max_reconn_retries = 3  # Max number of retry for re-connecting

    def __init__(self, host, enabled=True, version=__dbversion__):
        """Constructor is not public, no external code should call this directly"""

        if DataBase.wadas_db is not None:
            raise RuntimeError("Database instance already created.")

        self.host = host
        self.enabled = enabled
        self.version = version

    @classmethod
    def _create_instance(
        cls,
        db_type: DBTypes,
        host,
        port,
        username,
        database_name,
        enabled=True,
        version=__dbversion__,
    ):
        """Create the database instance."""

        if not host:
            return False

        # Create the appropriate database instance
        match db_type:
            case DataBase.DBTypes.MYSQL:
                return (
                    MySQLDataBase(host, port, username, database_name, enabled, version)
                    if (port and username and database_name)
                    else False
                )
            case DataBase.DBTypes.MARIADB:
                return (
                    MariaDBDataBase(host, port, username, database_name, enabled, version)
                    if (port and username and database_name)
                    else False
                )
            case DataBase.DBTypes.SQLITE:
                return SQLiteDataBase(host, enabled, version)
            case _:
                logger.error("Unsupported database type %s!", db_type)
                raise ValueError(f"Unsupported database type: {db_type}")

    @classmethod
    def initialize(
        cls,
        db_type: DBTypes,
        host,
        port,
        username,
        database_name,
        enabled=True,
        version=__dbversion__,
        log=True,
    ):
        """Initialize the singleton database instance."""

        if DataBase.wadas_db is not None:
            logger.error("Database is already initialized.")
            return False

        DataBase.wadas_db = cls._create_instance(
            db_type, host, port, username, database_name, enabled=enabled, version=version
        )
        if not DataBase.wadas_db:
            return False

        DataBase.wadas_db_engine = cls.get_engine()
        if log:
            logger.info("%s database initialized.", db_type.value)
        return True

    @classmethod
    def get_engine(cls):
        """
        Retrieve the singleton engine. If not initialized, raise an exception.

        :return: SQLAlchemy engine instance.
        """
        if DataBase.wadas_db_engine is None:
            if DataBase.wadas_db is None:
                logger.error("The database and db engine have not been initialized.")
                raise RuntimeError("The database and db engine have not been initialized.")
            else:
                logger.debug("Initializing engine...")
                DataBase.wadas_db_engine = (
                    create_engine(DataBase.wadas_db.get_connection_string())
                    if (DataBase.wadas_db.type == DataBase.DBTypes.SQLITE)
                    else create_engine(
                        DataBase.wadas_db.get_connection_string(),
                        pool_recycle=1800,  # Recycle connection every 30 minutes
                        pool_pre_ping=True,  # Check if connection is still valid
                    )
                )
        return DataBase.wadas_db_engine

    @classmethod
    def get_instance(cls):
        """
        Retrieve the singleton database instance.

        :return: The current database instance.
        """
        if DataBase.wadas_db is None:
            logger.debug("The database has not been initialized. Call 'initialize' first.")
            return None
        return DataBase.wadas_db

    @classmethod
    def get_enabled_db(cls):
        """Method that returns the db instance if enabled"""

        return db if (db := cls.get_instance()) and db.enabled else None

    @classmethod
    def destroy_instance(cls):
        """Destroy the current database instance and release resources."""

        logger.debug("Destroying db instance...")
        if DataBase.wadas_db_engine:
            try:
                DataBase.wadas_db_engine.dispose()
            except Exception:
                logger.warning("Failed to dispose the database engine.")
        DataBase.wadas_db_engine = None
        DataBase.wadas_db = None

    @classmethod
    def create_session(cls, retry_count=0):
        """Method to create a session to perform operations with the DB"""

        try:
            if engine := cls.get_engine():
                # If db is not SQLite, check engine status (SQLite has no pre-existing sessions)
                if DataBase.wadas_db.type != DataBase.DBTypes.SQLITE:
                    with engine.connect() as connection:
                        if connection.invalidated:
                            logger.warning("Connection invalidated, disposing engine...")
                            engine.dispose()
                            DataBase.wadas_db_engine = None  # Force new engine
                            engine = cls.get_engine()

                Session = sessionmaker(bind=engine)
                return Session()
            else:
                logger.error("Unable to create a session as DB engine is not initialized.")
                return None
        except (SQLAlchemyOperationalError, mariadbOperationalerror, pymysqlOperationalError):
            if retry_count < cls.max_reconn_retries:
                logger.warning(
                    "Database connection lost. Retrying... (%s/%s)",
                    retry_count + 1,
                    cls.max_reconn_retries,
                )
                if DataBase.wadas_db_engine:
                    DataBase.wadas_db_engine.dispose()
                DataBase.wadas_db_engine = None  # Force creation of new engine at next attempt
                return cls.create_session(retry_count=retry_count + 1)  # Retry to create session
            else:
                logger.error("Max retries reached. Could not create a session.")
                return None
        except Exception:
            logger.exception("An unexpected error occurred while creating a session")
            return None

    @classmethod
    def get_db_uuid(cls):
        """Method to return uuid from database"""

        if session := cls.create_session():
            try:
                result = session.query(ORMDBMetadata.project_uuid).first()
                return result[0] if result else None
            except Exception:
                return None
        else:
            return None

    @classmethod
    def get_db_version(cls):
        """Method to return version from db"""

        if session := cls.create_session():
            try:
                result = session.query(ORMDBMetadata.version).first()
                return result[0] if result else None
            except Exception:
                return None
        else:
            return None

    @classmethod
    def run_query(cls, stmt):
        """Generic method to run a query starting from a statement as input and handling
        exceptions (if any)."""

        logger.debug("Running query: %s", stmt)
        if session := cls.create_session():
            try:
                session.execute(stmt)
                session.commit()
                return True
            except SQLAlchemyError:
                # Rollback the transaction in case of an error
                session.rollback()
                logger.exception(
                    "SQLAlchemy error occurred while running the query: %s.", str(stmt)
                )
            except InterfaceError:
                session.rollback()
                logger.error("Database connection lost. Query operation failed.")
            except Exception:
                # Handle other unexpected errors
                session.rollback()
                logger.exception(
                    "SQLAlchemy error occurred while running the query: %s.", str(stmt)
                )
            finally:
                session.close()
        else:
            logger.error("DB session not initialized.")
        return False

    @classmethod
    def insert_into_db(cls, domain_object):
        """Method to insert a WADAS object into the db."""

        logger.debug("Inserting object into db...")
        if session := cls.create_session():
            try:
                foreign_key = []
                if isinstance(domain_object, DetectionEvent):
                    # If Camera associated to the detection event is not in db abort insertion
                    foreign_key.append(
                        session.query(ORMCamera.db_id)
                        .filter(
                            and_(
                                ORMCamera.camera_id == domain_object.camera_id,
                                ORMCamera.deletion_date.is_(None),
                            )
                        )
                        .scalar()
                    )
                    if not foreign_key:
                        logger.error(
                            "Unable to add Detection event into db as %s "
                            "camera id is not found in db.",
                            domain_object.camera_id,
                        )
                        return
                if isinstance(domain_object, ActuationEvent):
                    # If Actuator associated to the actuation event is not in db abort insertion
                    foreign_key.append(
                        session.query(ORMActuator.db_id)
                        .filter(
                            and_(
                                ORMActuator.actuator_id == domain_object.actuator_id,
                                ORMActuator.deletion_date.is_(None),
                            )
                        )
                        .scalar()
                    )
                    if not foreign_key:
                        logger.error(
                            "Unable to add Actuation event into db as %s actuator id is not found"
                            " in db.",
                            domain_object.actuator_id,
                        )
                        return
                    # If detection event associated to the actuation event is not in db
                    # abort insertion
                    foreign_key.append(cls.get_detection_event_id(domain_object.detection_event))
                    if not foreign_key[1]:
                        logger.error(
                            "Unable to add Actuation event into db as %s detection event id is not"
                            " found in db.",
                            domain_object.detection_event,
                        )
                        return

                orm_object = DataBase.domain_to_orm(domain_object, foreign_key)
                session.add(orm_object)

                # If instance is a camera, handle relationship with actuators
                if isinstance(domain_object, FTPCamera) or isinstance(domain_object, USBCamera):
                    for actuator in domain_object.actuators:
                        orm_actuator = (
                            session.query(ORMActuator).filter_by(actuator_id=actuator.id).first()
                        )
                        if orm_actuator:
                            orm_object.actuators.append(orm_actuator)

                session.commit()
                logger.debug(
                    "Object '%s' successfully added to the db!", type(domain_object).__name__
                )
            except IntegrityError:
                session.rollback()  # Cancel modifications in case of error
                logger.exception(
                    "Error while inserting object %s into db.", type(domain_object).__name__
                )
            except InterfaceError:
                session.rollback()
                logger.error("Database connection lost. Insert operation failed.")
            finally:
                session.close()
        else:
            logger.error("Failed to insert object into db as session could not been created.")

    def update_detection_event(cls, detection_event: DetectionEvent):
        """Update fields of a detection_events record in db.
        This is typically the case when classification details
        into an existing detection event object.
        """

        logger.debug("Updating detection event db entry...")
        # Retrieve the db id of the updated detection event
        detection_event_db_id = cls.get_detection_event_id(detection_event)
        if not detection_event_db_id:
            logger.error("Unable to update detection event as detection event not found in db.")

        if session := cls.create_session():
            try:
                # Update detection_event table
                stmt = (
                    update(ORMDetectionEvent)
                    .where(and_(ORMDetectionEvent.db_id == detection_event_db_id))
                    .values(
                        classification=detection_event.classification,
                        classification_img_path=detection_event.classification_img_path,
                    )
                )
                cls.run_query(stmt)

                if detection_event_db_id:
                    # Create ClassifiedAnimals table entries and link them with detection event
                    for classified_animal in detection_event.classified_animals:
                        orm_obj = ORMClassifiedAnimals(
                            detection_event_id=detection_event_db_id,  # Link to det event by ID
                            classified_animal=classified_animal["classification"][0],
                            probability=classified_animal["classification"][1],
                        )
                        session.add(orm_obj)
                    session.commit()

            except InterfaceError:
                session.rollback()
                logger.error("Database connection lost. Update operation failed.")
            except SQLAlchemyError:
                # Rollback the transaction in case of an error
                session.rollback()
                logger.exception("An error occurred while updating detection event into db.")
            except Exception:
                # Handle other unexpected errors
                session.rollback()
                logger.exception(
                    "Unexpected error occurred while updating detection event into db."
                )
            finally:
                session.close()
        else:
            logger.error(
                "Unable to update detection event into db as session could not be created."
            )

    @classmethod
    def update_camera(cls, camera, delete_camera=False):
        """Method to reflect camera fields update in db given a camera object"""

        if not cls.update_camera_by_db_id(
            cls.get_camera_id(camera.id), camera.enabled, delete_camera
        ):
            logger.error(
                "Unable to update camera. Camera ID %s not found or already deleted.", camera.id
            )

    @classmethod
    def update_camera_by_db_id(cls, camera_db_id, enabled, delete_camera=False):
        """Method to reflect camera fields update in db given a camera id"""

        logger.debug("Updating camera db entry...")

        if not camera_db_id:
            return False

        if delete_camera:
            deletion_date_time = get_precise_timestamp()
            stmt = (
                update(ORMCamera)
                .where(ORMCamera.db_id == camera_db_id)
                .values(deletion_date=deletion_date_time)
            )
            cls.run_query(stmt)
            # Delete camera association with actuators, if any
            stmt = delete(camera_actuator_association).where(
                camera_actuator_association.c.camera_id == camera_db_id
            )
            cls.run_query(stmt)
        else:
            stmt = update(ORMCamera).where(ORMCamera.db_id == camera_db_id).values(enabled=enabled)
            cls.run_query(stmt)
        return True

    @classmethod
    def update_actuator(cls, actuator, delete_actuator=False):
        """Method to reflect actuator fields update in db given an actuator object"""

        if not cls.update_actuator_by_db_id(
            cls.get_actuator_id(actuator.id), actuator.enabled, delete_actuator
        ):
            logger.error(
                "Unable to update actuator. Actuator ID %s not found or already deleted.",
                actuator.id,
            )

    @classmethod
    def update_actuator_by_db_id(cls, actuator_db_id, enabled, delete_actuator=False):
        """Method to reflect actuator fields update in db given an actuator id."""

        logger.debug("Updating actuator db entry...")

        if not actuator_db_id:
            return False

        if delete_actuator:
            deletion_date_time = get_precise_timestamp()
            stmt = (
                update(ORMActuator)
                .where(ORMActuator.db_id == actuator_db_id)
                .values(deletion_date=deletion_date_time)
            )
            cls.run_query(stmt)
            # Delete actuator association with cameras, if any
            stmt = delete(camera_actuator_association).where(
                camera_actuator_association.c.actuator_id == actuator_db_id
            )
            cls.run_query(stmt)
        else:
            stmt = (
                update(ORMActuator)
                .where(ORMActuator.db_id == actuator_db_id)
                .values(enabled=enabled)
            )
            cls.run_query(stmt)
        return True

    @classmethod
    def add_actuator_to_camera(cls, camera, actuator):
        """Method to add new actuator to a given camera actuators list."""

        if cls.get_instance():
            logger.debug("Adding actuator %s to camera %s in db.", actuator.id, camera.id)
            if session := cls.create_session():
                try:
                    # Retrieve camera and actuator db instances
                    camera = (
                        session.query(ORMCamera)
                        .filter(
                            and_(
                                ORMCamera.camera_id == camera.id, ORMCamera.deletion_date.is_(None)
                            )
                        )
                        .one()
                    )
                    actuator = (
                        session.query(ORMActuator)
                        .filter(
                            and_(
                                ORMActuator.actuator_id == actuator.id,
                                ORMActuator.deletion_date.is_(None),
                            )
                        )
                        .one()
                    )

                    # Add the actuator to the camera actuators list
                    camera.actuators.append(actuator)
                    session.commit()

                except InterfaceError:
                    session.rollback()
                    logger.error("Database connection lost. Add actuator operation failed.")
                except SQLAlchemyError:
                    # Rollback the transaction in case of an error
                    session.rollback()
                    logger.exception(
                        "SQLAlchemy error occurred while updating actuator "
                        "association to camera into db."
                    )
                except Exception:
                    # Handle other unexpected errors
                    session.rollback()
                    logger.exception(
                        "Unexpected error occurred while updating actuator "
                        "association to camera into db."
                    )
                finally:
                    session.close()
        else:
            logger.debug("No db configured, skipping actuator association insert.")

    @classmethod
    def remove_actuator_from_camera(cls, camera, actuator):
        """Remove an actuator from actuators list of a camera"""

        if cls.get_instance():
            logger.debug("Removing actuator %s from camera %s in db.", actuator.id, camera.id)
            if cls.create_session():
                # Retrieve camera and actuator db instances
                camera_db_id = cls.get_camera_id(camera.id)
                actuator_db_id = cls.get_actuator_id(actuator.id)

                stmt = delete(camera_actuator_association).where(
                    and_(
                        camera_actuator_association.c.actuator_id == actuator_db_id,
                        camera_actuator_association.c.camera_id == camera_db_id,
                    )
                )
                cls.run_query(stmt)
            else:
                logger.debug("Could not create db session, skipping actuator association insert.")

    @classmethod
    def get_camera_id(cls, camera_id):
        """Method to return camera database id (primary key)"""

        if session := cls.create_session():
            return (
                session.query(ORMCamera.db_id)
                .filter(
                    and_(
                        ORMCamera.camera_id == camera_id,
                        ORMCamera.deletion_date.is_(None),  # Avoid to return id of deleted camera
                    )
                )
                .scalar()
            )  # Use scalar() to retrieve the value directly
        else:
            logger.debug(
                "Could not get camera id %s since session has not been created.", camera_id
            )
            return None

    @classmethod
    def get_actuator_id(cls, actuator_id):
        """Method to return actuator database id (primary key)"""

        if session := cls.create_session():
            return (
                session.query(ORMActuator.db_id)
                .filter(
                    and_(
                        ORMActuator.actuator_id == actuator_id,
                        ORMActuator.deletion_date.is_(None),  # Avoid to return id of deleted camera
                    )
                )
                .scalar()
            )
        else:
            logger.debug(
                "Could not get actuator id %s since session has not been created.", actuator_id
            )
            return None

    @classmethod
    def get_detection_event_id(cls, detection_event: DetectionEvent):
        """Method to return detection event database id (primary key)"""

        if not (camera_db_id := cls.get_camera_id(detection_event.camera_id)):
            logger.error(
                "Unable to find Camera id %s while getting Detection event id.",
                detection_event.camera_id,
            )
            return None

        if session := cls.create_session():
            return (
                session.query(ORMDetectionEvent.db_id)
                .filter(
                    and_(
                        ORMDetectionEvent.camera_id == camera_db_id,
                        ORMDetectionEvent.time_stamp == detection_event.time_stamp,
                    )
                )
                .scalar()
            )  # Use scalar() to retrieve the value directly
        else:
            logger.error(
                "Could not retrieve detection event id as connection could not be created."
            )
            return None

    @staticmethod
    def domain_to_orm(domain_object, foreign_key=None):
        """Convert a domain object to an ORM object."""

        if isinstance(domain_object, FTPCamera):
            return ORMFTPCamera(
                camera_id=domain_object.id,
                enabled=domain_object.enabled,
                ftp_folder=domain_object.ftp_folder,
                creation_date=get_precise_timestamp(),
            )
        elif isinstance(domain_object, USBCamera):
            return ORMUSBCamera(
                camera_id=domain_object.id,
                name=domain_object.name,
                enabled=domain_object.enabled,
                pid=domain_object.pid,
                vid=domain_object.vid,
                path=domain_object.path,
                creation_date=get_precise_timestamp(),
            )
        elif isinstance(domain_object, RoadSignActuator):
            return ORMRoadSignActuator(
                actuator_id=domain_object.id,
                enabled=domain_object.enabled,
                creation_date=get_precise_timestamp(),
            )
        elif isinstance(domain_object, FeederActuator):
            return ORMFeederActuator(
                actuator_id=domain_object.id,
                enabled=domain_object.enabled,
                creation_date=get_precise_timestamp(),
            )
        elif isinstance(domain_object, ActuationEvent):
            command = json.loads(domain_object.command.value)

            return ORMActuationEvent(
                actuator_id=foreign_key[0],
                time_stamp=domain_object.time_stamp,
                detection_event_id=foreign_key[1],
                command=next(iter(command)),
            )
        elif isinstance(domain_object, DetectionEvent):
            return ORMDetectionEvent(
                camera_id=foreign_key[0],
                time_stamp=domain_object.time_stamp,
                original_image=domain_object.original_image,
                detection_img_path=domain_object.detection_img_path,
                detected_animals=len(
                    domain_object.detected_animals["detections"].xyxy
                ),  # detected_animals count
                classification=domain_object.classification,
                classification_img_path=domain_object.classification_img_path,
            )
        elif isinstance(domain_object, DBMetadata):
            return ORMDBMetadata(
                version=domain_object.version,
                applied_at=domain_object.applied_at,
                description=domain_object.description,
                project_uuid=str(domain_object.project_uuid),
            )
        elif isinstance(domain_object, DBUser):
            return ORMUser(
                username=domain_object.username,
                password=domain_object.password,
                email=domain_object.email,
                role=domain_object.role,
                created_at=get_precise_timestamp(),
            )
        else:
            raise ValueError(f"Unsupported domain object type: {type(domain_object).__name__}")

    @staticmethod
    def orm_to_domain(orm_object):
        """Convert an ORM object to a domain object."""

        try:
            if isinstance(orm_object, ORMFTPCamera):
                return FTPCamera(
                    id=orm_object.camera_id,
                    ftp_folder=orm_object.ftp_folder,
                    enabled=orm_object.enabled,
                )
            elif isinstance(orm_object, ORMUSBCamera):
                return USBCamera(
                    id=orm_object.camera_id,
                    name=orm_object.name,
                    enabled=orm_object.enabled,
                    pid=orm_object.pid,
                    vid=orm_object.vid,
                    path=orm_object.path,
                )
            elif isinstance(orm_object, ORMRoadSignActuator):
                return RoadSignActuator(id=orm_object.actuator_id, enabled=orm_object.enabled)
            elif isinstance(orm_object, ORMFeederActuator):
                return FeederActuator(id=orm_object.actuator_id, enabled=orm_object.enabled)
            else:
                raise ValueError(f"Unsupported ORM object type: {type(orm_object).__name__}")
        except AttributeError:
            logger.exception("Error mapping ORM object to domain.")
            raise

    @classmethod
    def populate_db(cls, uuid):
        """Method to create a db and optionally populate it with existing domain objects"""

        # Set db metadata
        db_metadata = DBMetadata("WADAS database", uuid)
        cls.insert_into_db(db_metadata)
        # Populate DB with existing cameras and actuators
        if Actuator.actuators:
            for actuator_id in Actuator.actuators:
                cls.insert_into_db(Actuator.actuators[actuator_id])
        if cameras:
            for camera in cameras:
                cls.insert_into_db(camera)

    @classmethod
    def sanitize_db(cls):
        """Method to align db tables with domain model"""

        if session := cls.create_session():
            try:
                # Check if actuators in model are reflected into db
                for actuator_id in Actuator.actuators:
                    cur_actuator = Actuator.actuators[actuator_id]
                    if actuator_db_id := cls.get_actuator_id(actuator_id):
                        # Check actuator attributes type, enabled
                        db_actuator = (
                            session.query(ORMActuator)
                            .filter(ORMActuator.db_id == actuator_db_id)
                            .one()
                        )
                        if db_actuator.type != cur_actuator.type:
                            # If type does not match, set to deleted the one in db
                            cls.update_actuator_by_db_id(actuator_db_id, db_actuator.enabled, True)
                            # Insert new actuator into db
                            cls.insert_into_db(cur_actuator)
                        if db_actuator.enabled != cur_actuator.enabled:
                            cls.update_actuator(cur_actuator, False)
                    else:
                        cls.insert_into_db(cur_actuator)

                # Check if cameras in model are reflected into db
                for camera in cameras:
                    if camera_db_id := cls.get_camera_id(camera.id):
                        db_camera = (
                            session.query(ORMCamera).filter(ORMCamera.db_id == camera_db_id).one()
                        )
                        if camera.type != db_camera.type:
                            cls.update_camera_by_db_id(camera_db_id, db_camera.enabled, True)
                            cls.insert_into_db(camera)
                        if camera.enabled != db_camera.enabled:
                            cls.update_camera(camera, False)
                        if camera.actuators != db_camera.actuators:
                            # Delete all associations for camera
                            stmt = delete(camera_actuator_association).where(
                                camera_actuator_association.c.camera_id == camera_db_id
                            )
                            cls.run_query(stmt)
                            # Pristine associations for camera
                            for actuator in camera.actuators:
                                actuator_db_id = cls.get_actuator_id(actuator.id)
                                stmt = camera_actuator_association.insert().values(
                                    camera_id=camera_db_id, actuator_id=actuator_db_id
                                )
                            cls.run_query(stmt)
                    else:
                        cls.insert_into_db(camera)

                # Check if actuators in db match the ones in domain
                actuator_ids = session.query(ORMActuator.actuator_id).all()
                actuator_ids_from_db = {actuator_id[0] for actuator_id in actuator_ids}
                db_extra_actuators_ids = actuator_ids_from_db - Actuator.actuators.keys()
                for extra_actuator_id in db_extra_actuators_ids:
                    deletion_date_time = get_precise_timestamp()
                    actuator_db_id = cls.get_actuator_id(extra_actuator_id)
                    stmt = (
                        update(ORMActuator)
                        .where(ORMActuator.db_id == actuator_db_id)
                        .values(deletion_date=deletion_date_time)
                    )
                    cls.run_query(stmt)
                    # Delete camera association with actuators, if any
                    stmt = delete(camera_actuator_association).where(
                        camera_actuator_association.c.actuator_id == extra_actuator_id
                    )
                    cls.run_query(stmt)

                # Check if cameras in db match the ones in domain
                camera_ids = session.query(ORMCamera.camera_id).all()
                camera_ids_from_db = {camera_id[0] for camera_id in camera_ids}
                camera_id_from_domain = {camera.id for camera in cameras}
                db_extra_camera_ids = camera_ids_from_db - camera_id_from_domain
                for extra_camera_id in db_extra_camera_ids:
                    deletion_date_time = get_precise_timestamp()
                    camera_db_id = cls.get_camera_id(extra_camera_id)
                    stmt = (
                        update(ORMCamera)
                        .where(ORMCamera.db_id == camera_db_id)
                        .values(deletion_date=deletion_date_time)
                    )
                    cls.run_query(stmt)
                    # Delete camera association with actuators, if any
                    stmt = delete(camera_actuator_association).where(
                        camera_actuator_association.c.camera_id == extra_camera_id
                    )
                    cls.run_query(stmt)

            except InterfaceError:
                session.rollback()
                logger.error("Database connection lost. Sanitize db operation failed.")
            except SQLAlchemyError:
                session.rollback()
                logger.exception("An error occurred while sanitizing the db.")
            except Exception:
                session.rollback()
                logger.exception("Unexpected error occurred while sanitizing the in db.")
            finally:
                session.close()
        else:
            logger.error("Could not sanitize db as session has not been created.")

    @classmethod
    def get_users(cls):
        """Method to retrieve users from db"""
        try:
            if session := DataBase.create_session():
                stmt = select(ORMUser.username, ORMUser.email, ORMUser.role)
                return session.execute(stmt)
            else:
                return None

        except InterfaceError:
            session.rollback()
            logger.error("Database connection lost. Query operation failed.")
        except Exception:
            logger.error("Please make sure db is healthy and properly configured.")
            return None
        finally:
            session.close()

    @classmethod
    def get_user_email_and_role(cls, username):
        """Method to retrieve user email and role from db"""

        try:
            if session := DataBase.create_session():
                stmt = select(ORMUser.email, ORMUser.role).where(ORMUser.username == username)
                return session.execute(stmt).fetchone()
            else:
                logger.error(
                    "Could not retrieve email and role for user %s since "
                    "session has not been created.",
                    username,
                )
                return None

        except InterfaceError:
            session.rollback()
            logger.error("Database connection lost. Query operation failed.")
        except SQLAlchemyError:
            logger.error("Could not fetch data for user '%s'.", username)
            return None
        finally:
            session.close()

    @classmethod
    def update_user_email(cls, username, email):
        """Method to update the email of a user in db"""

        try:
            if session := DataBase.create_session():
                # Update user email
                stmt = update(ORMUser).where(ORMUser.username == username).values(email=email)

                session.execute(stmt)
                session.commit()
                return True
            else:
                logger.error(
                    "Could not update email for user %s since session has not been created.",
                    username,
                )
                return False

        except InterfaceError:
            session.rollback()
            logger.error("Database connection lost. Update operation failed.")
        except SQLAlchemyError:
            session.rollback()
            logger.error("Could not update email for user '%s'.", username)
            return False
        finally:
            session.close()

    @classmethod
    def update_user_role(cls, username, role):
        """Method to update the role of a user in db"""

        try:
            if session := DataBase.create_session():
                # Update user role
                stmt = update(ORMUser).where(ORMUser.username == username).values(role=role)

                session.execute(stmt)
                session.commit()
                return True
            else:
                logger.error(
                    "Could not update role for user %s since session has not been created.",
                    username,
                )
                return False

        except InterfaceError:
            session.rollback()
            logger.error("Database connection lost. Update operation failed.")
        except SQLAlchemyError:
            session.rollback()
            logger.error("Could not update role for user '%s'.", username)
            return False
        finally:
            session.close()

    @classmethod
    def update_user_password(cls, username, hashed_password):
        """Method to update the password of a user in db"""

        try:
            if session := DataBase.create_session():
                # Update user password
                stmt = (
                    update(ORMUser)
                    .where(ORMUser.username == username)
                    .values(password=hashed_password)
                )

                session.execute(stmt)
                session.commit()
                return True
            else:
                logger.error(
                    "Could not update user %s password since session has not been created.",
                    username,
                )
                return False

        except InterfaceError:
            session.rollback()
            logger.error("Database connection lost. Update operation failed.")
        except SQLAlchemyError:
            session.rollback()
            logger.error("Could not update password for user '%s'.", username)
            return False
        finally:
            session.close()

    @classmethod
    def delete_user(cls, username):
        """Method to delete a given user from db."""

        try:
            if session := DataBase.create_session():
                stmt = delete(ORMUser).where(ORMUser.username == username)
                result = session.execute(stmt)

                if not result.rowcount:
                    logger.warning("Could not delete user '%s'.", username)
                    return False
                session.commit()
                return True
            else:
                logger.error(
                    "Could not delete user %s since session has not been created.", username
                )
                return None

        except InterfaceError:
            session.rollback()
            logger.error("Database connection lost. Delete user operation failed.")
        except SQLAlchemyError:
            session.rollback()
            logger.error("Could not delete user '%s'.", username)
            return False
        finally:
            session.close()

    @abstractmethod
    def get_connection_string(self):
        """Generate the connection string based on the database type."""

    @abstractmethod
    def serialize(self):
        """Method to serialize DataBase object into file."""

    @classmethod
    def deserialize(cls, data):
        """Method to deserialize DataBase object from file."""

        # If db is already initialized, destroy it before new init.
        if cls.get_instance():
            cls.destroy_instance()

        cfg_db_type = data["type"]
        match cfg_db_type:
            case DataBase.DBTypes.SQLITE.value:
                db_type = DataBase.DBTypes.SQLITE
                return cls.initialize(
                    db_type,
                    data["host"],
                    None,
                    "",
                    "",
                    data["enabled"],
                    data["version"],
                )
            case DataBase.DBTypes.MYSQL.value:
                db_type = DataBase.DBTypes.MYSQL
            case DataBase.DBTypes.MARIADB.value:
                db_type = DataBase.DBTypes.MARIADB
            case _:
                logger.error("Wrong deserialized db type!")
                return False

        return cls.initialize(
            db_type,
            data["host"],
            data["port"],
            data["username"],
            data["database_name"],
            data["enabled"],
            data["version"],
        )


class MySQLDataBase(DataBase):
    """MySQL DataBase class"""

    def __init__(self, host, port, username, database_name, enabled=True, version=__dbversion__):
        super().__init__(host, enabled, version)
        self.type = DataBase.DBTypes.MYSQL
        self.port = port
        self.username = username
        self.database_name = database_name

    def get_password(self):
        """Retrieve the password from the keyring."""

        if not self.username:
            raise ValueError("Username must be defined to retrieve the password.")
        return keyring.get_password("WADAS_DB_MySQL", self.username)

    def get_connection_string(self):
        """Generate the connection string based on the database type."""

        password = self.get_password()
        if not self.database_name:
            raise ValueError("Database name is required for MySQL.")
        return (
            "mysql+pymysql://"
            f"{self.username}:{password}@{self.host}:{self.port}/{self.database_name}"
        )

    def create_database(self):
        """Method to create a new database."""

        try:
            # Try to connect to db to check whether it exists
            with DataBase.wadas_db_engine.connect() as conn:
                logger.debug("Database exists.")
        except SQLAlchemyOperationalError:
            # If db does not exist, creates it
            logger.info("Creating Database...")
            temp_engine = create_engine(
                self.get_connection_string(), pool_recycle=1800, pool_pre_ping=True
            )
            with temp_engine.connect() as conn:
                conn.execute(f"CREATE DATABASE {self.database_name}")
            logger.info("Database '%s' successfully created.", self.database_name)

        # Create all tables
        Base.metadata.create_all(DataBase.wadas_db_engine)

    def serialize(self):
        """Method to serialize MySQL DataBase object into file."""

        return {
            "host": self.host,
            "port": self.port,
            "type": self.type.value,
            "username": self.username,
            "database_name": self.database_name,
            "enabled": self.enabled,
            "version": self.version,
        }


class MariaDBDataBase(DataBase):
    """MariaDB DataBase class"""

    def __init__(self, host, port, username, database_name, enabled=True, version=__dbversion__):
        super().__init__(host, enabled, version)
        self.type = DataBase.DBTypes.MARIADB
        self.port = port
        self.username = username
        self.database_name = database_name

    def get_password(self):
        """Retrieve the password from the keyring."""

        if not self.username:
            raise ValueError("Username must be defined to retrieve the password.")
        return keyring.get_password("WADAS_DB_MariaDB", self.username)

    def get_connection_string(self, create=False):
        """Generate the connection string based on the database type."""
        password = self.get_password()

        if not self.database_name and not create:
            raise ValueError("Database name is required for MariaDB.")

        base_string = (
            f"mariadb+mariadbconnector://{self.username}:{password}@{self.host}:{self.port}"
        )
        return base_string if create else f"{base_string}/{self.database_name}"

    def create_database(self):
        """Method to create a new database."""
        logger.info("Creating or verifying the existence of the database...")

        temp_engine = create_engine(
            self.get_connection_string(create=True), pool_recycle=1800, pool_pre_ping=True
        )

        with temp_engine.connect() as conn:
            # Create db if not already existing
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {self.database_name}"))
            logger.info("Database '%s' successfully created.", self.database_name)
        try:
            Base.metadata.create_all(DataBase.wadas_db_engine)
            logger.info("Tables created successfully in '%s'.", self.database_name)
        except Exception:
            logger.exception("Error while creating the tables...")
            return False
        return True

    def serialize(self):
        """Method to serialize MariaDB DataBase object into file."""

        return {
            "host": self.host,
            "port": self.port,
            "type": self.type.value,
            "username": self.username,
            "database_name": self.database_name,
            "enabled": self.enabled,
            "version": self.version,
        }


class SQLiteDataBase(DataBase):
    """SQLite DataBase class"""

    def __init__(self, host, enabled=True, version=__dbversion__):
        super().__init__(host, enabled, version)
        self.type = DataBase.DBTypes.SQLITE

    def get_connection_string(self):
        """Generate the connection string based on the database type."""

        return f"sqlite:///{self.host}"

    def create_database(self):
        """Method to create database by creating all tables"""

        if DataBase.wadas_db_engine:
            try:
                Base.metadata.create_all(DataBase.wadas_db_engine)
            except SQLAlchemyOperationalError:
                logger.exception("OperationalError during database creation.")
                return False
            except SQLAlchemyError:
                logger.exception("SQLAlchemyError during database creation.")
                return False
            except Exception:
                logger.exception("Unexpected error during database creation.")
                return False
            else:
                logger.info("SQLite Database created successfully.")
                return True
        else:
            logger.warning("Database engine is not initialized.")
            return False

    def serialize(self):
        """Method to serialize SQLite DataBase object into file."""

        return {
            "host": self.host,
            "type": self.type.value,
            "enabled": self.enabled,
            "version": self.version,
        }
