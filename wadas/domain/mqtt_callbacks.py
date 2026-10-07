import json
import logging

from wadas.domain.actuator import Actuator, Command
from wadas.domain.database import DataBase

logger = logging.getLogger(__name__)


def actuators_mqtt_callback(message):
    """Method used to handle a message received on an MQTT subscribed topic"""
    payload = json.loads(message.data.decode())

    if message.topic == Actuator.MQTT_STATUS_TOPIC:
        if payload["actuator_id"] in Actuator.actuators:
            Actuator.actuators[payload["actuator_id"]].update_status(payload)
    elif "/response" in message.topic:
        actuator_id = message.topic.split("/")[1]
        if actuator_id not in Actuator.actuators.keys():
            raise Exception(f"Received message with an unknown actuator_id: {actuator_id}")

        resp_actuator_id = payload.get("actuator_id")
        cmd = payload.get("cmd")
        response_ok = payload.get("response")

        if resp_actuator_id != actuator_id:
            raise Exception(
                f"Response actuator id ({resp_actuator_id}) differs from expected one {actuator_id}"
            )
        if not cmd:
            raise Exception("Missing command")
        if response_ok is None:
            raise Exception("Missing response status")

        # Convert payload → Command object
        try:
            command = Command.from_json(json.dumps(payload))
        except Exception:
            raise Exception("Invalid command format")

        actuator = Actuator.actuators[actuator_id]

        # Save original payload
        actuator.queue_response_command(command)

        if response_ok:
            if command.response_message:
                logger.info(
                    "Actuator %s responded SUCCESS to command '%s' (%s). Message: %s",
                    command.actuator_id,
                    command.cmd,
                    command.time_stamp,
                    command.response_message,
                )
            else:
                logger.info(
                    "Actuator %s responded SUCCESS to command '%s' (%s).",
                    command.actuator_id,
                    command.cmd,
                    command.time_stamp,
                )
        elif command.response_message and "warning:" in command.response_message.lower():
            response_message = command.response_message.lower().replace("warning:", "", 1).strip()
            logger.warning(
                "Actuator %s responded to command '%s' (%s) with warning message: %s",
                command.actuator_id,
                command.cmd,
                command.time_stamp,
                response_message,
            )
        elif command.response_message and "error:" in command.response_message.lower():
            response_message = command.response_message.lower().replace("error:", "", 1).strip()
            logger.error(
                "Actuator %s responded to command '%s' (%s) with error message: %s",
                command.actuator_id,
                command.cmd,
                command.time_stamp,
                response_message,
            )
        else:
            if command.response_message:
                logger.error(
                    "Actuator %s responded to command '%s' (%s) with %s. Message: %s, payload=%s",
                    command.actuator_id,
                    command.cmd,
                    command.time_stamp,
                    command.response,
                    command.response_message,
                    payload.get("payload"),
                )
            else:
                logger.error(
                    "Actuator %s responded to command '%s' (%s) with %s, payload=%s",
                    command.actuator_id,
                    command.cmd,
                    command.time_stamp,
                    command.response,
                    payload.get("payload"),
                )

        # Insert actuation event into db, if enabled
        if db := DataBase.get_enabled_db():
            logger.debug("Updating Actuation event to add response info...")
            db.update_actuation_event(command)

    else:
        logger.info(f"Received message on an unhandled topic: {message.topic}")
