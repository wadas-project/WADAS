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
# Description: Module containing Class definitions for view-model objects.
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


# Request Models
class RefreshTokenRequest(BaseModel):
    refresh_token: str


class LoginRequest(BaseModel):
    username: str
    password: str


class DetectionsRequest(BaseModel):
    camera_ids: Optional[List[int]] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    classified_animals: Optional[List[str]] = None
    order_by: Optional[str] = "timestamp_desc"
    offset: Optional[int] = 0
    limit: Optional[int] = 20


class ActuationsRequest(BaseModel):
    detection_id: Optional[int] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    actuator_types: Optional[List[str]] = None
    commands: Optional[List[str]] = None
    offset: Optional[int] = 0
    limit: Optional[int] = 20


# View Models
class User(BaseModel):
    username: str
    password: str
    email: str
    role: str


class Actuator(BaseModel):
    id: int
    name: str
    type: str


class Camera(BaseModel):
    id: int
    name: str
    type: str
    enabled: bool
    actuators: Optional[List[Actuator]] = []


class ClassifiedAnimal(BaseModel):
    animal: str
    probability: float


class DetectionEvent(BaseModel):
    id: int
    camera_id: int
    detection_img_path: Optional[str]
    classification_img_path: Optional[str]
    detected_animals: int
    classification: bool
    classified_animals: Optional[List[ClassifiedAnimal]]
    timestamp: datetime


class ActuationEvent(BaseModel):
    actuator: Actuator
    detection_event_id: int
    command: str
    timestamp: datetime


class RefreshResponse(BaseModel):
    access_token: str
    token_type: str = "JWT"


class DataResponse(BaseModel):
    data: object


class PaginatedResponse(BaseModel):
    total: int
    count: int
    data: object


class ActuatorDetail(Actuator):
    enabled: bool
    creation_date: datetime
    deletion_date: Optional[datetime] = None
    last_update: Optional[datetime] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    log: Optional[str] = None


class ActuatorRuntimeView(BaseModel):
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    log: Optional[str] = None
    last_update: Optional[datetime] = None


def actuator_to_viewmodel(db_actuator, runtime_actuator=None) -> ActuatorDetail:
    """As ActuatorDetails class is intended to be for Admin only and contains data
    from runtime class, this method helps to build attributes info from both db and
    runtime class itself."""
    return ActuatorDetail(
        id=db_actuator.db_id,
        name=db_actuator.actuator_id,
        type=db_actuator.type.value if db_actuator.type else None,
        enabled=db_actuator.enabled,
        creation_date=db_actuator.creation_date,
        deletion_date=db_actuator.deletion_date,
        last_update=getattr(runtime_actuator, "last_update", None),
        temperature=getattr(runtime_actuator, "temperature", None),
        humidity=getattr(runtime_actuator, "humidity", None),
        log=getattr(runtime_actuator, "log", None),
    )


def runtime_actuator_to_viewmodel(runtime_actuator) -> ActuatorRuntimeView:
    """Returns only Actuator runtime class attributes. No db data."""
    return ActuatorRuntimeView(
        temperature=getattr(runtime_actuator, "temperature", None),
        humidity=getattr(runtime_actuator, "humidity", None),
        log=getattr(runtime_actuator, "log", None),
        last_update=getattr(runtime_actuator, "last_update", None),
    )
