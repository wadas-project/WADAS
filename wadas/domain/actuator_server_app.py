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

import json
import logging

from fastapi import Body, FastAPI, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

from wadas.domain.actuator import Actuator

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
            "id": "1694789238123-a3f5c1",
            "cmd": "send_log",
            "response": True,
            "payload": {"logs": ["..."]},
        },
    ),  # noqa: B008
):
    """
    Endpoint used by a remote actuator device to send back the result of an executed command.

    Expected payload format:
    {
        "id": "<command-id>",
        "cmd": "<command-name>",
        "response": true|false,
        "payload": { ... }  # optional extra data
    }
    """

    if actuator_id not in Actuator.actuators:
        logger.error("No actuator found with ID: %s", actuator_id)
        raise HTTPException(status_code=404, detail="Actuator does not exist")

    actuator = Actuator.actuators[actuator_id]

    cmd_id = payload.get("id")
    cmd = payload.get("cmd")
    response_ok = payload.get("response")
    extra_payload = payload.get("payload", {})

    if not cmd_id:
        raise HTTPException(status_code=400, detail="Missing command 'id' in response")
    if response_ok is None:
        raise HTTPException(status_code=400, detail="Missing 'response' (True/False) in response")

    # Store responses in a dictionary {command_id: {cmd, response, payload}}
    if not hasattr(actuator, "responses"):
        actuator.responses = {}

    actuator.responses[cmd_id] = {"cmd": cmd, "response": response_ok, "payload": extra_payload}

    logger.info(
        "Actuator %s responded to command %s (%s) with %s, payload=%s",
        actuator_id,
        cmd,
        cmd_id,
        response_ok,
        extra_payload,
    )

    return {"status": "received", "id": cmd_id}
