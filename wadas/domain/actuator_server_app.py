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

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

from wadas.domain.actuator import Actuator

logger = logging.getLogger(__name__)

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

app.add_middleware(CORSMiddleware, allow_origins=["*"])


@app.get("/api/v1/actuators/{actuator_id}")
async def get_actuator_command(actuator_id: str):
    """Method to give a command to an actuator when requested."""
    logger.info("Connected remote actuator with ID: %s", actuator_id)

    if actuator_id in Actuator.actuators:
        cmd = Actuator.actuators[actuator_id].get_command()
        return JSONResponse(content=json.loads(cmd) if cmd else {"cmd": None}, status_code=200)

    else:
        logger.info("No actuator found with ID: %s", actuator_id)
        raise HTTPException(status_code=404, detail="Actuator does not exist")
