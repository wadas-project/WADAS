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
import os
import sys
import threading
from logging.handlers import RotatingFileHandler

import uvicorn

from wadas_webserver.web_server_app import app as server_app

logger = logging.getLogger(__name__)


class WebServer:
    def __init__(self, host, port, certfile=None, keyfile=None, threaded=False):
        self.host = host
        self.port = port
        self.certfile = certfile
        self.keyfile = keyfile
        self.threaded = threaded

        if self.threaded:
            self._setup_threaded_logging()

        # Uvicorn configuration
        self.config = uvicorn.Config(
            app=server_app,
            host=self.host,
            port=self.port,
            ssl_certfile=self.certfile,
            ssl_keyfile=self.keyfile,
            log_config=None if self.threaded else "default",  # custom logging only if threaded
        )
        self.server = uvicorn.Server(self.config)

    def _setup_threaded_logging(self):
        os.makedirs("log", exist_ok=True)

        formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s", "%Y-%m-%d %H:%M:%S")
        handler = RotatingFileHandler(
            os.path.join("log", "wadas_server.log"), maxBytes=10_000_000, backupCount=3
        )
        handler.setFormatter(formatter)
        level = logging.INFO

        # --- Root logger (stdout/stderr) ---
        root_logger = logging.getLogger()
        root_logger.setLevel(level)
        root_logger.addHandler(handler)

        class LoggerWriter:
            def __init__(self, write_func):
                self.write_func = write_func

            def write(self, message):
                if message.strip():
                    self.write_func(message.strip())

            def flush(self):
                pass

        sys.stdout = LoggerWriter(root_logger.info)
        sys.stderr = LoggerWriter(root_logger.error)

        # --- Logger Uvicorn ---
        uvicorn_loggers = ("uvicorn", "uvicorn.error", "uvicorn.access")
        for name in uvicorn_loggers:
            logger = logging.getLogger(name)
            for h in logger.handlers[:]:
                logger.removeHandler(h)
            logger.setLevel(level)
            logger.addHandler(handler)
            logger.propagate = False

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
