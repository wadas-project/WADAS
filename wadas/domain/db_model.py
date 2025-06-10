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
# Description: database model module, it contains ORM classes.

from sqlalchemy import Boolean, Column
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import Float, ForeignKey, Index, Integer, String, Table, Text
from sqlalchemy.ext import compiler
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.types import DateTime, TypeDecorator

from wadas._version import __dbversion__
from wadas.domain.actuator import Actuator as DomainActuator
from wadas.domain.camera import Camera as DomainCamera

Base = declarative_base()


# Custom DATETIME type with precision for MySQL/MariaDB
class MySQLDATETIME6(TypeDecorator):
    impl = DateTime
    cache_ok = True  # Set cache_ok to True for performance optimization

    @staticmethod
    def process_bind_param(value, dialect):
        # No conversion required for binding parameters
        return value

    def process_result_value(self, value, dialect):
        # No conversion required when retrieving the value
        return value


# Custom compilation rule for MySQL/MariaDB
@compiler.compiles(MySQLDATETIME6, "mysql")
def compile_datetime6(element, compiler, **kwargs):
    return "DATETIME(6)"


@compiler.compiles(MySQLDATETIME6, "mariadb")
def compile_datetime6_mariadb(element, compiler, **kwargs):
    return "DATETIME(6)"


# Classes
camera_actuator_association = Table(
    "camera_actuator_association",
    Base.metadata,
    Column("camera_id", Integer, ForeignKey("cameras.id", ondelete="CASCADE"), primary_key=True),
    Column(
        "actuator_id", Integer, ForeignKey("actuators.id", ondelete="CASCADE"), primary_key=True
    ),
)


class Camera(Base):
    __tablename__ = "cameras"

    db_id = Column(Integer, primary_key=True, autoincrement=True, name="id")
    camera_id = Column(String(255), nullable=False, name="name")
    type = Column(SqlEnum(DomainCamera.CameraTypes), nullable=False)
    enabled = Column(Boolean, default=False)
    creation_date = Column(MySQLDATETIME6(timezone=True), nullable=False)
    deletion_date = Column(MySQLDATETIME6(timezone=True), nullable=True)
    detection_events = relationship(
        "DetectionEvent", back_populates="camera", cascade="all, delete-orphan"
    )
    actuators = relationship(
        "Actuator",
        secondary=camera_actuator_association,
        back_populates="cameras",
    )

    __mapper_args__ = {
        "polymorphic_identity": "camera",
        "polymorphic_on": type,
    }


class USBCamera(Camera):
    __tablename__ = "usb_cameras"

    db_id = Column(Integer, ForeignKey("cameras.id"), primary_key=True, name="id")
    name = Column(String(255), nullable=True, name="product_name")
    en_wadas_motion_detection = Column(Boolean, default=False)
    pid = Column(String(255), nullable=True)
    vid = Column(String(255), nullable=True)
    path = Column(Text, nullable=True)

    __mapper_args__ = {"polymorphic_identity": DomainCamera.CameraTypes.USB_CAMERA}


class FTPCamera(Camera):
    __tablename__ = "ftp_cameras"

    db_id = Column(Integer, ForeignKey("cameras.id"), primary_key=True, name="id")
    ftp_folder = Column(Text, nullable=False)

    __mapper_args__ = {"polymorphic_identity": DomainCamera.CameraTypes.FTP_CAMERA}


class Actuator(Base):
    __tablename__ = "actuators"

    db_id = Column(Integer, primary_key=True, autoincrement=True, name="id")
    actuator_id = Column(String(255), nullable=False, name="name")
    type = Column(SqlEnum(DomainActuator.ActuatorTypes), nullable=False)
    enabled = Column(Boolean, default=False)
    creation_date = Column(MySQLDATETIME6(timezone=True), nullable=False)
    deletion_date = Column(MySQLDATETIME6(timezone=True), nullable=True)
    actuation_events = relationship(
        "ActuationEvent", back_populates="actuator", cascade="all, delete-orphan"
    )
    cameras = relationship(
        "Camera",
        secondary=camera_actuator_association,
        back_populates="actuators",
    )

    __mapper_args__ = {
        "polymorphic_identity": "actuator",
        "polymorphic_on": type,
    }


class RoadSignActuator(Actuator):
    __mapper_args__ = {
        "polymorphic_identity": DomainActuator.ActuatorTypes.ROADSIGN,
    }


class FeederActuator(Actuator):
    __mapper_args__ = {
        "polymorphic_identity": DomainActuator.ActuatorTypes.FEEDER,
    }


class DetectionEvent(Base):
    __tablename__ = "detection_events"

    db_id = Column(Integer, primary_key=True, autoincrement=True, name="id")
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=False)
    time_stamp = Column(MySQLDATETIME6(timezone=True), nullable=False)
    original_image = Column(Text, nullable=False)
    detection_img_path = Column(Text, nullable=False)
    detected_animals = Column(Integer, nullable=False)  # Use JSON if supported
    classification = Column(Boolean, default=True)
    classification_img_path = Column(Text, nullable=True)

    camera = relationship("Camera", back_populates="detection_events")
    actuation_events = relationship(
        "ActuationEvent", back_populates="detection_event", cascade="all, delete-orphan"
    )
    classified_animals = relationship(
        "ClassifiedAnimals", back_populates="detection_event", cascade="all, delete-orphan"
    )


class ClassifiedAnimals(Base):
    __tablename__ = "classified_animals"

    db_id = Column(Integer, primary_key=True, autoincrement=True, name="id")  # db ID
    detection_event_id = Column(Integer, ForeignKey("detection_events.id"), nullable=False)
    classified_animal = Column(Text, nullable=True)
    probability = Column(Float, nullable=True)

    detection_event = relationship("DetectionEvent", back_populates="classified_animals")


class ActuationEvent(Base):
    __tablename__ = "actuation_events"

    actuator_id = Column(Integer, ForeignKey("actuators.id"), primary_key=True, nullable=False)
    time_stamp = Column(MySQLDATETIME6(timezone=True), primary_key=True, nullable=False)
    detection_event_id = Column(Integer, ForeignKey("detection_events.id"), nullable=False)
    command = Column(Text, nullable=True)

    actuator = relationship("Actuator", back_populates="actuation_events")
    detection_event = relationship("DetectionEvent", back_populates="actuation_events")


# Database service tables, not mapped with any WADAS class
class User(Base):
    __tablename__ = "users"

    db_id = Column(Integer, primary_key=True, autoincrement=True, name="id")
    username = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    role = Column(String(255), nullable=False)
    created_at = Column(MySQLDATETIME6(timezone=True), nullable=False)


class DBMetadata(Base):
    __tablename__ = "db_metadata"

    db_id = Column(Integer, primary_key=True, autoincrement=True, name="id")
    version = Column(String(255), nullable=False, default=lambda: __dbversion__)
    applied_at = Column(MySQLDATETIME6(timezone=True), nullable=False)
    description = Column(Text, nullable=True)
    project_uuid = Column(Text, nullable=False)


# Indexes
Index("ix_detection_events_camera_time", DetectionEvent.camera_id, DetectionEvent.time_stamp)
Index("ix_actuation_events_actuator_time", ActuationEvent.actuator_id, ActuationEvent.time_stamp)
