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
# Description: FastAPI Actuator server module

import datetime
import logging
import os
import threading
from logging.handlers import RotatingFileHandler

import uvicorn

logger = logging.getLogger(__name__)


def initialize_fastapi_logger(handler=None, level=logging.DEBUG):
    """Method to initialize Fastapi server logger"""
    if not handler:
        handler = RotatingFileHandler(
            os.path.join("log", "fastapi_server.log"), maxBytes=100000, backupCount=3
        )
        formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s", "%Y-%m-%d %H:%M:%S")
        handler.setFormatter(formatter)

    logger_names = ("uvicorn", "uvicorn.error", "uvicorn.access")
    for logger_name in logger_names:
        server_logger = logging.getLogger(logger_name)
        for h in server_logger.handlers[:]:
            server_logger.removeHandler(h)

        server_logger.setLevel(level)
        server_logger.addHandler(handler)
        server_logger.propagate = False


class FastAPIActuatorServer:
    """FastAPI-based HTTPS Server used to communicate with actuators"""

    actuator_server = None

    def __init__(
        self, ip: str, port: int, ssl_certificate: str, ssl_key: str, actuator_timeout_threshold=30
    ):
        self.ip = ip
        self.port = port
        self.ssl_certificate = ssl_certificate
        self.ssl_key = ssl_key
        self.thread = None
        self.server = None
        self.startup_time = None
        self.actuator_timeout_threshold = actuator_timeout_threshold

        self.config = uvicorn.Config(
            app="wadas.domain.actuator_server_app:app",
            host=self.ip,
            port=self.port,
            ssl_certfile=self.ssl_certificate,
            ssl_keyfile=self.ssl_key,
            timeout_graceful_shutdown=5,
        )

    def run(self):
        """Method to run the FastAPI Actuator server with SSL in a separate thread."""
        self.server = uvicorn.Server(self.config)
        self.thread = threading.Thread(target=self.server.run)
        if self.thread:
            self.thread.start()
            self.startup_time = datetime.datetime.now()
            logger.info("Starting thread for HTTPS Actuator Server with FastAPI...")
        else:
            logger.error("Unable to create new thread for FastAPI Actuator Server.")
        return self.thread

    def stop(self):
        """Method to safely stop the FastAPIActuatorServer thread"""
        logger.info("Stopping FastAPI Actuator Server...")
        if self.server:
            self.server.should_exit = True
            self.startup_time = None

    def serialize(self):
        """Method to serialize FastAPIActuatorServer object."""
        return {
            "ssl_certificate": self.ssl_certificate,
            "ssl_key": self.ssl_key,
            "ip": self.ip,
            "port": self.port,
            "actuator_timeout_threshold": self.actuator_timeout_threshold,
        }

    @staticmethod
    def deserialize(data):
        """Method to deserialize FastAPIActuatorServer from file."""
        return FastAPIActuatorServer(**data)
