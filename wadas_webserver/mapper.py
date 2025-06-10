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
# Description: Class to map database-model objects to view-model objects.
from wadas.domain.db_model import ActuationEvent as DB_ActuationEvent
from wadas.domain.db_model import Actuator as DB_Actuator
from wadas.domain.db_model import Camera as DB_Camera
from wadas.domain.db_model import ClassifiedAnimals as DB_ClassifiedAnimals
from wadas.domain.db_model import DetectionEvent as DB_DetectionEvent
from wadas.domain.db_model import User as DB_User
from wadas_webserver.view_model import (
    ActuationEvent,
    Actuator,
    Camera,
    ClassifiedAnimal,
    DetectionEvent,
    User,
)


class Mapper:
    """Class to map database-model objects to view-model objects"""

    @staticmethod
    def map_db_user_to_user(db_user: DB_User) -> User:
        return User(
            username=db_user.username,
            password=db_user.password,
            email=db_user.email,
            role=db_user.role,
        )

    @staticmethod
    def map_db_camera_to_camera(db_camera: DB_Camera) -> Camera:
        return Camera(
            id=db_camera.db_id,
            name=db_camera.camera_id,
            type=db_camera.type,
            enabled=db_camera.enabled,
            actuators=[Mapper.map_db_actuator_to_actuator(x) for x in db_camera.actuators],
        )

    @staticmethod
    def map_db_actuator_to_actuator(db_actuator: DB_Actuator) -> Actuator:
        return Actuator(id=db_actuator.db_id, name=db_actuator.actuator_id, type=db_actuator.type)

    @staticmethod
    def map_db_detectionevent_to_detectionevent(db_detevent: DB_DetectionEvent) -> DetectionEvent:
        return DetectionEvent(
            id=db_detevent.db_id,
            camera_id=db_detevent.camera_id,
            detection_img_path=db_detevent.detection_img_path,
            classification_img_path=db_detevent.classification_img_path,
            detected_animals=db_detevent.detected_animals,
            classification=db_detevent.classification,
            classified_animals=[
                Mapper.map_db_animal_to_animal(x) for x in db_detevent.classified_animals
            ],
            timestamp=db_detevent.time_stamp,
        )

    @staticmethod
    def map_db_actuationevent_to_actuationevent(db_actevent: DB_ActuationEvent) -> ActuationEvent:
        return ActuationEvent(
            actuator=Mapper.map_db_actuator_to_actuator(db_actevent.actuator),
            detection_event_id=db_actevent.detection_event_id,
            command=db_actevent.command,
            timestamp=db_actevent.time_stamp,
        )

    @staticmethod
    def map_db_animal_to_animal(db_animal: DB_ClassifiedAnimals) -> ClassifiedAnimal:
        return ClassifiedAnimal(
            animal=db_animal.classified_animal, probability=db_animal.probability
        )

    @staticmethod
    def map_db_detectionevent_to_attr_list(db_detevent: DB_DetectionEvent):
        classified_animals = [x.classified_animal for x in db_detevent.classified_animals]
        return [
            db_detevent.db_id,
            db_detevent.camera.camera_id,
            db_detevent.time_stamp.strftime("%Y-%m-%d %H:%M"),
            db_detevent.detected_animals,
            len(classified_animals),
            classified_animals,
        ]

    @staticmethod
    def map_db_actuationevent_to_attr_list(db_actevent: DB_ActuationEvent):
        return [
            db_actevent.time_stamp.strftime("%Y-%m-%d %H:%M"),
            db_actevent.actuator.actuator_id,
            db_actevent.command,
        ]
