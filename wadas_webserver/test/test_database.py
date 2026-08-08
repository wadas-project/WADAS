import csv
import io
import os
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from wadas.domain.db_model import ActuatorBatteryStatus as DB_ActuatorBatteryStatus
from wadas.domain.db_model import (
    ActuatorTemperatureStatus as DB_ActuatorTemperatureStatus,
)
from wadas.domain.db_model import Base
from wadas_webserver.database import Database
from wadas_webserver.view_model import (
    ActuationEvent,
    ActuationsRequest,
    Camera,
    DetectionEvent,
    DetectionsRequest,
)


def populate_fake_db(engine):
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    current_directory = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(current_directory, "test_data.txt")) as fin:
        for line in fin:
            line = line.strip()
            if line and not line.startswith("#"):
                session.execute(text(line.strip()))
    session.commit()
    session.close()


@pytest.fixture
def database():
    engine = create_engine("sqlite:///:memory:", echo=True)
    populate_fake_db(engine)
    db = Database("sqlite:///:memory:")
    db.engine = engine
    return db


def test_constructor(database):
    assert database is not None
    assert database.get_connection_string() == "sqlite:///:memory:"


def test_get_cameras(database):
    cameras = database.get_cameras()
    assert cameras
    assert all(isinstance(camera, Camera) for camera in cameras)
    assert all(camera.enabled for camera in cameras)


def test_get_known_animals(database):
    expected = "bear"
    known_animals = database.get_known_animals()
    assert known_animals
    assert all(isinstance(animal, str) for animal in known_animals)
    assert expected in known_animals


def test_get_known_actuators_types(database):
    expected = "Road Sign"
    actuators_types = database.get_known_actuator_types()
    assert actuators_types
    assert all(isinstance(act_type, str) for act_type in actuators_types)
    assert expected in actuators_types


def test_get_known_actuation_commands(database):
    expected = "display"
    known_commands = database.get_known_actuation_commands()
    assert known_commands
    assert all(isinstance(command, str) for command in known_commands)
    assert expected in known_commands


def test_get_detection_events(database):
    count, detection_events = database.get_all_detection_events()
    assert len(detection_events) == count
    assert all(isinstance(event, DetectionEvent) for event in detection_events)


def test_get_detection_events_by_camera_id(database):
    camera_id = 7

    request = DetectionsRequest(camera_ids=[camera_id])
    count, detection_events = database.get_detection_events_by_filter(request)
    assert detection_events
    assert all(isinstance(event, DetectionEvent) for event in detection_events)
    assert all(event.camera_id == camera_id for event in detection_events)


def test_get_detection_events_by_date(database):
    datefrom = datetime(2025, 2, 8)
    dateto = datetime(2025, 2, 15)

    request = DetectionsRequest(date_from=datefrom, date_to=dateto)
    count, detection_events = database.get_detection_events_by_filter(request)
    assert detection_events
    assert all(isinstance(event, DetectionEvent) for event in detection_events)
    assert all(datefrom <= event.timestamp <= dateto for event in detection_events)


def test_get_detection_events_by_animal(database):
    animals = ["cat"]

    request = DetectionsRequest(classified_animals=animals)
    count, detection_events = database.get_detection_events_by_filter(request)
    assert detection_events
    assert all(isinstance(event, DetectionEvent) for event in detection_events)
    assert all(
        any(animal.animal in animals for animal in event.classified_animals)
        for event in detection_events
    )


def test_get_detection_events_by_camera_animal_date(database):
    camera_id = 7
    animals = ["bear"]
    datefrom = datetime(2025, 2, 8)
    dateto = datetime(2025, 2, 15)

    request = DetectionsRequest(
        camera_ids=[camera_id], classified_animals=animals, date_from=datefrom, date_to=dateto
    )
    count, detection_events = database.get_detection_events_by_filter(request)
    assert detection_events
    assert all(isinstance(event, DetectionEvent) for event in detection_events)
    assert all(
        (
            event.camera_id == camera_id
            and datefrom <= event.timestamp <= dateto
            and any(animal.animal in animals for animal in event.classified_animals)
            for event in detection_events
        )
    )


def test_get_actuation_events(database):
    request = ActuationsRequest(limit=1000)

    count, actuation_events = database.get_actuation_events_by_filter(request)
    assert actuation_events
    assert all(isinstance(event, ActuationEvent) for event in actuation_events)


def test_get_actuation_events_by_actuator_type(database):
    actuator_type = "Feeder"

    request = ActuationsRequest(actuator_types=[actuator_type])
    count, actuation_events = database.get_actuation_events_by_filter(request)
    assert actuation_events
    assert all(isinstance(event, ActuationEvent) for event in actuation_events)
    assert all(event.actuator.type == actuator_type for event in actuation_events)


def test_get_actuation_events_by_command(database):
    command = "display"

    request = ActuationsRequest(commands=[command])
    count, actuation_events = database.get_actuation_events_by_filter(request)
    assert actuation_events
    assert all(isinstance(event, ActuationEvent) for event in actuation_events)
    assert all(event.command == command for event in actuation_events)


def test_get_actuation_events_by_date(database):
    datefrom = datetime(2025, 2, 8)
    dateto = datetime(2025, 2, 15)

    request = ActuationsRequest(date_from=datefrom, date_to=dateto)
    count, actuation_events = database.get_actuation_events_by_filter(request)
    assert actuation_events
    assert all(isinstance(event, ActuationEvent) for event in actuation_events)
    assert all(datefrom <= event.timestamp <= dateto for event in actuation_events)


def test_get_actuation_events_by_command_date(database):
    command = "display"
    datefrom = datetime(2025, 2, 8)
    dateto = datetime(2025, 2, 15)

    request = ActuationsRequest(commands=[command], date_from=datefrom, date_to=dateto)
    count, actuation_events = database.get_actuation_events_by_filter(request)
    assert actuation_events
    assert all(isinstance(event, ActuationEvent) for event in actuation_events)
    assert all(
        datefrom <= event.timestamp <= dateto and event.command == command
        for event in actuation_events
    )


def validate_csv_string(csv_string, headers_number):
    assert isinstance(csv_string, str)

    csv_file = io.StringIO(csv_string)
    reader = csv.reader(csv_file)

    lines = list(reader)
    assert len(lines) > 0

    header = lines[0]
    assert len(header) == headers_number

    if len(lines) > 1:
        first_data_row = lines[1]
        assert len(first_data_row) == len(header)


def test_export_filtered_detection_events(database):
    camera_id = 7
    datefrom = datetime(2025, 2, 8)
    dateto = datetime(2025, 2, 15)

    request = DetectionsRequest(camera_ids=[camera_id], date_from=datefrom, date_to=dateto)
    csv_string = database.export_detection_events_as_csv(request)
    validate_csv_string(csv_string, 6)


def test_export_filtered_actuation_events(database):
    command = "display"
    datefrom = datetime(2025, 2, 8)
    dateto = datetime(2025, 2, 15)

    request = ActuationsRequest(commands=[command], date_from=datefrom, date_to=dateto)
    csv_string = database.export_actuation_events_as_csv(request)
    validate_csv_string(csv_string, 3)


# ---------------------------------------------------------------------------
# Battery / temperature telemetry tests
# ---------------------------------------------------------------------------
# Timestamps are generated relative to "now" (rather than reusing the fixed
# dates in test_data.txt) so that day-range filtering (7d/30d/90d) behaves
# consistently regardless of when the test suite is actually run.

BATTERY_ACTUATOR_NAME = "1111"  # matches db_id=1 in test_data.txt
UNKNOWN_ACTUATOR_NAME = "does-not-exist"


@pytest.fixture
def database_with_telemetry(database):
    Session = sessionmaker(bind=database.engine)
    session = Session()

    now = datetime.now(timezone.utc)

    battery_readings = [
        # (age_in_days, voltage, temperature, humidity)
        (0.1, 12.41, 27.6, 58.0),
        (2, 12.55, 26.1, 55.0),
        (10, 12.80, 24.0, 50.0),
        (45, 11.90, 20.0, 60.0),
    ]
    for age_days, voltage, temperature, humidity in battery_readings:
        session.add(
            DB_ActuatorBatteryStatus(
                actuator_id=1,
                time_stamp=now - timedelta(days=age_days),
                voltage=voltage,
                temperature=temperature,
                humidity=humidity,
            )
        )

    temperature_readings = [
        # (age_in_days, temperature, humidity)
        (0.1, 31.2, 47.0),
        (2, 29.0, 45.0),
        (10, 25.0, 40.0),
        (45, 18.0, 55.0),
    ]
    for age_days, temperature, humidity in temperature_readings:
        session.add(
            DB_ActuatorTemperatureStatus(
                actuator_id=1,
                time_stamp=now - timedelta(days=age_days),
                temperature=temperature,
                humidity=humidity,
            )
        )

    session.commit()
    session.close()

    return database


def test_get_last_battery_status(database_with_telemetry):
    voltage, temperature, humidity = database_with_telemetry.get_last_battery_status(
        BATTERY_ACTUATOR_NAME
    )
    # the most recent reading is the one inserted with age_days=0.1
    assert voltage == pytest.approx(12.41)
    assert temperature == pytest.approx(27.6)
    assert humidity == pytest.approx(58.0)


def test_get_last_battery_status_no_data(database):
    # actuator '4444' (db_id=2) has no battery readings in test_data.txt
    assert database.get_last_battery_status("4444") is None


def test_get_last_battery_status_unknown_actuator(database_with_telemetry):
    assert database_with_telemetry.get_last_battery_status(UNKNOWN_ACTUATOR_NAME) is None


def test_get_battery_history_returns_readings_within_range(database_with_telemetry):
    readings = database_with_telemetry.get_battery_history(BATTERY_ACTUATOR_NAME, since_days=7)

    # only the readings with age_days 0.1 and 2 fall within the last 7 days
    assert len(readings) == 2
    assert all(r.voltage in (12.41, 12.55) for r in readings)


def test_get_battery_history_24h_range_only_includes_last_day(database_with_telemetry):
    readings = database_with_telemetry.get_battery_history(BATTERY_ACTUATOR_NAME, since_days=1)

    # only the reading with age_days=0.1 falls within the last 24 hours
    assert len(readings) == 1
    assert readings[0].voltage == pytest.approx(12.41)


def test_get_battery_history_wider_range_includes_older_readings(database_with_telemetry):
    readings = database_with_telemetry.get_battery_history(BATTERY_ACTUATOR_NAME, since_days=90)

    assert len(readings) == 4


def test_get_battery_history_is_chronologically_ordered(database_with_telemetry):
    readings = database_with_telemetry.get_battery_history(BATTERY_ACTUATOR_NAME, since_days=90)

    timestamps = [r.time_stamp for r in readings]
    assert timestamps == sorted(timestamps)


def test_get_battery_history_unknown_actuator_returns_empty(database_with_telemetry):
    readings = database_with_telemetry.get_battery_history(UNKNOWN_ACTUATOR_NAME, since_days=90)
    assert readings == []


def test_get_battery_history_no_data_returns_empty(database):
    # actuator '4444' (db_id=2) has no battery readings in test_data.txt
    readings = database.get_battery_history("4444", since_days=90)
    assert readings == []


def test_get_temperature_history_returns_readings_within_range(database_with_telemetry):
    readings = database_with_telemetry.get_temperature_history(BATTERY_ACTUATOR_NAME, since_days=7)

    # only the readings with age_days 0.1 and 2 fall within the last 7 days
    assert len(readings) == 2
    assert all(r.temperature in (31.2, 29.0) for r in readings)


def test_get_temperature_history_24h_range_only_includes_last_day(database_with_telemetry):
    readings = database_with_telemetry.get_temperature_history(BATTERY_ACTUATOR_NAME, since_days=1)

    # only the reading with age_days=0.1 falls within the last 24 hours
    assert len(readings) == 1
    assert readings[0].temperature == pytest.approx(31.2)


def test_get_temperature_history_wider_range_includes_older_readings(database_with_telemetry):
    readings = database_with_telemetry.get_temperature_history(BATTERY_ACTUATOR_NAME, since_days=90)

    assert len(readings) == 4


def test_get_temperature_history_is_chronologically_ordered(database_with_telemetry):
    readings = database_with_telemetry.get_temperature_history(BATTERY_ACTUATOR_NAME, since_days=90)

    timestamps = [r.time_stamp for r in readings]
    assert timestamps == sorted(timestamps)


def test_get_temperature_history_unknown_actuator_returns_empty(database_with_telemetry):
    readings = database_with_telemetry.get_temperature_history(UNKNOWN_ACTUATOR_NAME, since_days=90)
    assert readings == []
