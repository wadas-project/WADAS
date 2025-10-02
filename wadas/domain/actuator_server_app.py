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
# Date: 2024-10-23
# Description: FASTAPI app for HTTPS Actuator Server
import datetime
import json
import logging

from fastapi import Body, FastAPI, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

from wadas.domain.actuator import Actuator, ActuatorBatteryStatus, Command
from wadas.domain.database import DataBase

logger = logging.getLogger(__name__)

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

app.add_middleware(CORSMiddleware, allow_origins=["*"])


@app.get("/api/v1/actuators/{actuator_id}")
async def get_actuator_command(actuator_id: str):
    """Method to give a command to an actuator when requested."""
    logger.debug("Connected remote actuator with ID: %s", actuator_id)

    if actuator_id in Actuator.actuators:
        cmd = Actuator.actuators[actuator_id].get_command()
        return JSONResponse(
            content=json.loads(cmd) if cmd else {"id": None, "cmd": None}, status_code=200
        )
    else:
        logger.error("No actuator found with ID: %s", actuator_id)
        raise HTTPException(status_code=404, detail="Actuator does not exist")


@app.post("/api/v1/actuators/{actuator_id}/response")
async def respond_actuator_command(
    actuator_id: str,
    payload: dict = Body(  # noqa: B008
        ...,
        example={
            "actuator_id": 5,
            "time_stamp": "2025-09-15T10:32:00.123456Z",
            "cmd": "send_log",
            "response": True,
            "response_timestamp": "2025-09-15T10:32:00.123456Z",
            "payload": {},
        },
    ),  # noqa: B008
):
    """
    Endpoint used by a remote actuator device to send back the result of an executed command.

    Expected payload format:
    {
        "actuator_id": "<actuator-id>",
        "cmd": "<command-name>",
        "time_stamp": <datetime>
        "response": true|false,
        "response_timestamp": <datetime>
        "payload": { ... }  # optional extra data
    }
    payload format should embedd a message reporting the command execution,
    by specifying whether is informative ("message": "..."), a warning ("warning":"...")
    or an error ("error": "...").
    """

    if actuator_id not in Actuator.actuators:
        logger.error("No actuator found with ID: %s", actuator_id)
        raise HTTPException(status_code=404, detail="Actuator does not exist")

    resp_actuator_id = payload.get("actuator_id")
    cmd = payload.get("cmd")
    response_ok = payload.get("response")

    if not actuator_id:
        raise HTTPException(status_code=400, detail="Missing actuator id in response")
    if resp_actuator_id != actuator_id:
        raise HTTPException(status_code=400, detail="Response actuator id differs from API one")
    if not cmd:
        raise HTTPException(status_code=400, detail="Missing command")
    if response_ok is None:
        raise HTTPException(status_code=400, detail="Missing response status")

    # Convert payload → Command object
    try:
        command = Command.from_json(json.dumps(payload))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid command format")

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
    elif "warning:" in command.response_message.lower():
        response_message = command.response_message.lower().replace("warning:", "", 1).strip()
        logger.warning(
            "Actuator %s responded to command '%s' (%s) with warning message: %s",
            command.actuator_id,
            command.cmd,
            command.time_stamp,
            response_message,
        )
    elif "error:" in command.response_message.lower():
        response_message = command.response_message.lower().replace("error:", "", 1).strip()
        logger.error(
            "Actuator %s responded to command '%s' (%s) with error message: %s",
            command.actuator_id,
            command.cmd,
            command.time_stamp,
            response_message,
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

    return {"status": "received"}


@app.post("/api/v1/actuators/{actuator_id}/battery_status")
async def receive_battery_status(actuator_id: str, payload: dict = Body(...)):  # noqa: B008
    """Receive actuator's battery status update.
    Battery and battery monitor are considered optional components
    of the actuator device.
    """

    resp_actuator_id = payload.get("actuator_id")
    cmd = payload.get("cmd")
    response_ok = payload.get("response")

    if not actuator_id:
        raise HTTPException(status_code=400, detail="Missing actuator id in API path")
    if resp_actuator_id != actuator_id:
        raise HTTPException(status_code=400, detail="Response actuator id differs from API one")
    if not cmd or cmd != "battery_status":
        raise HTTPException(status_code=400, detail="Invalid or missing command")
    if response_ok is None:
        raise HTTPException(status_code=400, detail="Missing response status")

    # Get actuator from list
    actuator = Actuator.actuators.get(actuator_id)
    if not actuator:
        raise HTTPException(status_code=404, detail="Actuator not found")

    voltage = payload.get("payload", {}).get("volt")
    if voltage is None:
        raise HTTPException(status_code=400, detail="Missing 'volt' in payload")

    # Timestamp set by server
    ts = datetime.datetime.now(datetime.timezone.utc)

    # Update Actuator class
    battery_status = ActuatorBatteryStatus(
        actuator_id=actuator_id,
        voltage=voltage,
        time_stamp=ts,
    )
    actuator.battery_status = battery_status
    logger.info("Received actuator %s battery status: %s", actuator_id, voltage)

    # Persist in DB
    if db := DataBase.get_enabled_db():
        logger.debug("Inserting battery status into db...")
        db.insert_into_db(battery_status)

    return {"status": "received"}
