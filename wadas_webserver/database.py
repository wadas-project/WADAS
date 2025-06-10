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
# Date: 2025-02-21
# Description: Base Class to handle interactions with WADAS Database.
import csv
import io
import logging
from contextlib import contextmanager
from typing import List, Optional, Tuple

from sqlalchemy import and_, create_engine
from sqlalchemy.orm import Query, Session, joinedload, sessionmaker

from wadas.domain.actuator import Actuator
from wadas.domain.db_model import ActuationEvent as DB_ActuationEvent
from wadas.domain.db_model import Actuator as DB_Actuator
from wadas.domain.db_model import Camera as DB_Camera
from wadas.domain.db_model import ClassifiedAnimals as DB_ClassifiedAnimal
from wadas.domain.db_model import DetectionEvent as DB_DetectionEvent
from wadas.domain.db_model import User as DB_User
from wadas_webserver.mapper import Mapper
from wadas_webserver.view_model import (
    ActuationEvent,
    ActuationsRequest,
    Camera,
    DetectionEvent,
    DetectionsRequest,
    User,
)

logger = logging.getLogger(__name__)


class Database:
    """Base Class to handle interactions with WADAS Database"""

    instance = None

    def __init__(self, connection_string):
        self.connection_string = connection_string
        self.engine = create_engine(self.get_connection_string())

    @contextmanager
    def get_session(self):
        """Context manager to handle session"""
        session = sessionmaker(bind=self.engine)()
        try:
            yield session
        except Exception:
            logger.exception("An error occurred while creating a session")
        finally:
            session.close()

    def get_connection_string(self):
        return self.connection_string

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Method to get a user object from his username"""
        with self.get_session() as session:
            db_user = session.query(DB_User).filter(DB_User.username == username).first()
            user = Mapper.map_db_user_to_user(db_user) if db_user else None
            return user

    def get_all_detection_events(self) -> Tuple[int, List[DetectionEvent]]:
        """Method to get all detection events in the database and their count."""
        with self.get_session() as session:
            result = session.query(DB_DetectionEvent).all()
            events = [Mapper.map_db_detectionevent_to_detectionevent(x) for x in result]
            return len(result), events

    def get_detection_event_by_id(self, event_id) -> Optional[DetectionEvent]:
        with self.get_session() as session:
            item = (
                session.query(DB_DetectionEvent).where(DB_DetectionEvent.db_id == event_id).first()
            )
            return Mapper.map_db_detectionevent_to_detectionevent(item) if item else None

    @staticmethod
    def _build_detection_events_query(
        session: Session, detection_filter: DetectionsRequest
    ) -> Query:
        """Method to build the detection events query from the specified filters"""
        query = session.query(DB_DetectionEvent)

        if detection_filter.camera_ids:
            query = query.filter(DB_DetectionEvent.camera_id.in_(detection_filter.camera_ids))
        if detection_filter.date_from:
            query = query.filter(DB_DetectionEvent.time_stamp >= detection_filter.date_from)
        if detection_filter.date_to:
            query = query.filter(DB_DetectionEvent.time_stamp <= detection_filter.date_to)
        if detection_filter.classified_animals:
            query = (
                query.join(DB_ClassifiedAnimal)
                .filter(
                    DB_ClassifiedAnimal.classified_animal.in_(detection_filter.classified_animals)
                )
                .options(joinedload(DB_DetectionEvent.classified_animals))
            )
        return query

    def get_detection_events_by_filter(
        self, detection_filter: DetectionsRequest
    ) -> Tuple[int, List[DetectionEvent]]:
        """Method to get paginated detection events filtered
        by different filters and their total count"""
        with self.get_session() as session:
            query = self._build_detection_events_query(session, detection_filter)
            # get the total number
            count = query.count()

            # order_by, offset, limit
            query = query.order_by(DB_DetectionEvent.time_stamp.desc())  # TODO: handle order_by
            query = query.offset(detection_filter.offset)
            query = query.limit(detection_filter.limit)

            result = query.all()
            events = [Mapper.map_db_detectionevent_to_detectionevent(x) for x in result]
            return count, events

    @staticmethod
    def _build_actuation_events_query(
        session: Session, actuation_filter: ActuationsRequest
    ) -> Query:
        """Method to build the actuation events query from the specified filters"""
        query = session.query(DB_ActuationEvent)

        if actuation_filter.detection_id:
            query = query.filter(
                DB_ActuationEvent.detection_event_id == actuation_filter.detection_id
            )
        if actuation_filter.date_from:
            query = query.filter(DB_ActuationEvent.time_stamp >= actuation_filter.date_from)
        if actuation_filter.date_to:
            query = query.filter(DB_ActuationEvent.time_stamp <= actuation_filter.date_to)
        if actuation_filter.commands:
            query = query.filter(DB_ActuationEvent.command.in_(actuation_filter.commands))
        if actuation_filter.actuator_types:
            try:
                enum_values = [
                    Actuator.ActuatorTypes(value) for value in actuation_filter.actuator_types
                ]
            except Exception:
                logger.exception("Unable to find appropriate ActuatorTypes Value")
                enum_values = []
            query = (
                query.join(DB_Actuator)
                .filter(DB_Actuator.type.in_(enum_values))
                .options(joinedload(DB_ActuationEvent.actuator))
            )
        return query

    def get_actuation_events_by_filter(
        self,
        actuation_filter: ActuationsRequest,
    ) -> Tuple[int, List[ActuationEvent]]:
        """Method to get paginated actuation events filtered
        by different filters and their total count"""
        with self.get_session() as session:
            query = self._build_actuation_events_query(session, actuation_filter)
            # get the total number
            count = query.count()

            # order_by, offset, limit
            query = query.order_by(DB_ActuationEvent.time_stamp.desc())  # TODO: handle order_by
            query = query.offset(actuation_filter.offset)
            query = query.limit(actuation_filter.limit)

            result = query.all()
            events = [Mapper.map_db_actuationevent_to_actuationevent(x) for x in result]
            return count, events

    def get_cameras(self) -> List[Camera]:
        """Method to get all the enabled cameras"""
        with self.get_session() as session:
            result = (
                session.query(DB_Camera)
                .filter(and_(DB_Camera.deletion_date.is_(None), DB_Camera.enabled.is_(True)))
                .all()
            )
            return [Mapper.map_db_camera_to_camera(x) for x in result]

    def get_known_animals(self) -> List[str]:
        """Method to get all the known animals"""
        with self.get_session() as session:
            result = (
                session.query(DB_ClassifiedAnimal.classified_animal)
                .distinct(DB_ClassifiedAnimal.classified_animal)
                .order_by(DB_ClassifiedAnimal.classified_animal)
                .all()
            )
            return [x[0] for x in result]

    def get_known_actuator_types(self) -> List[str]:
        """Method to get all the known types for actuator"""
        with self.get_session() as session:
            result = (
                session.query(DB_Actuator.type)
                .distinct(DB_Actuator.type)
                .order_by(DB_Actuator.type)
                .all()
            )
            return [x[0].value for x in result]

    def get_known_actuation_commands(self) -> List[str]:
        """Method to get all the known commands for actuation events"""
        with self.get_session() as session:
            result = (
                session.query(DB_ActuationEvent.command)
                .distinct(DB_ActuationEvent.command)
                .order_by(DB_ActuationEvent.command)
                .all()
            )
            return [x[0] for x in result]

    @staticmethod
    def _get_csv_string(
        headers: List[str], obj_list: List[DB_DetectionEvent | DB_ActuationEvent], obj_class: type
    ) -> str:
        """Method to build the csv file to be returned as export data"""
        if obj_class is DB_DetectionEvent:
            map_func = Mapper.map_db_detectionevent_to_attr_list
        elif obj_class is DB_ActuationEvent:
            map_func = Mapper.map_db_actuationevent_to_attr_list

        if map_func:
            with io.StringIO() as file_output:
                csv_writer = csv.writer(file_output, delimiter=",", quoting=csv.QUOTE_ALL)
                csv_writer.writerow(headers)
                for event in obj_list:
                    csv_writer.writerow(map_func(event))
                file_output.seek(0)
                return file_output.getvalue()
        else:
            raise Exception("Map function not found for the specified class.")

    def export_detection_events_as_csv(self, detection_filter: DetectionsRequest) -> str:
        """Method to build a csv file containing filtered detection events"""
        headers = [
            "event_id",
            "camera",
            "date",
            "# detected animals",
            "# classified animals",
            "classified animals",
        ]
        with self.get_session() as session:
            query = self._build_detection_events_query(session, detection_filter)
            result = query.all()
            return self._get_csv_string(headers, result, DB_DetectionEvent)

    def export_actuation_events_as_csv(self, actuation_filter: ActuationsRequest) -> str:
        """Method to build a csv file containing filtered detection events"""
        headers = ["date", "actuator", "command"]
        with self.get_session() as session:
            query = self._build_actuation_events_query(session, actuation_filter)
            result = query.all()
            return self._get_csv_string(headers, result, DB_ActuationEvent)
