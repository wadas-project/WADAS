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
# Description: Class implementing the HTTPS Server for WADAS Web Interface.
import datetime
import logging
import threading

import uvicorn

from wadas_webserver.web_server_app import app as server_app

logger = logging.getLogger(__name__)


class WebServer:
    """Class to handle the HTTPS Server"""

    current_server = None

    def __init__(
        self,
        ip: str,
        port: int,
        ssl_certificate: str,
        ssl_key: str,
    ):
        self.ip = ip
        self.port = port
        self.ssl_certificate = ssl_certificate
        self.ssl_key = ssl_key
        self.thread = None
        self.server = None
        self.startup_time = None

        self.config = uvicorn.Config(
            app=server_app,
            host=self.ip,
            port=self.port,
            ssl_certfile=self.ssl_certificate,
            ssl_keyfile=self.ssl_key,
            timeout_graceful_shutdown=5,
        )

    def run(self):
        self.server = uvicorn.Server(self.config)
        self.thread = threading.Thread(target=self.server.run)
        if self.thread:
            self.thread.start()
            self.startup_time = datetime.datetime.now()
        else:
            logger.error("Unable to create new thread for FastAPI Actuator Server.")
        return self.thread

    def stop(self):
        logger.info("Stopping FastAPI Actuator Server...")
        if self.server:
            self.server.should_exit = True
            self.startup_time = None
