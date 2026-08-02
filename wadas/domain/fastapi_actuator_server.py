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
import socket
import ssl
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
        self,
        ip: str,
        port: int,
        ssl_certificate: str,
        ssl_key: str,
        actuator_timeout_threshold=30,
        watchdog_interval_s: int = 900,
        watchdog_failure_threshold: int = 2,
        watchdog_probe_timeout_s: float = 5.0,
    ):
        self.ip = ip
        self.port = port
        self.ssl_certificate = ssl_certificate
        self.ssl_key = ssl_key
        self.thread = None
        self.server = None
        self.startup_time = None
        self.actuator_timeout_threshold = actuator_timeout_threshold

        # Watchdog: periodically verifies the accept loop is still alive and
        # transparently restarts the server if it stops responding (e.g. after
        # a transient network drop kills the asyncio Proactor accept task on
        # Windows without it ever being retried, see WinError 64 / OSError 22).
        self.watchdog_interval_s = watchdog_interval_s
        self.watchdog_failure_threshold = watchdog_failure_threshold
        self.watchdog_probe_timeout_s = watchdog_probe_timeout_s
        self._watchdog_thread = None
        self._watchdog_stop_event = threading.Event()
        self._consecutive_failures = 0

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
            self._start_watchdog()
        else:
            logger.error("Unable to create new thread for FastAPI Actuator Server.")
        return self.thread

    def stop(self):
        """Method to safely stop the FastAPIActuatorServer thread"""
        logger.info("Stopping FastAPI Actuator Server...")
        self._stop_watchdog()
        if self.server:
            self.server.should_exit = True
            self.startup_time = None

    def _start_watchdog(self):
        """Starts the background thread that periodically checks the server is
        still accepting connections and restarts it if it silently stopped."""
        self._watchdog_stop_event.clear()
        self._consecutive_failures = 0
        self._watchdog_thread = threading.Thread(target=self._watchdog_loop, daemon=True)
        self._watchdog_thread.start()
        logger.info("Started Actuator Server watchdog thread.")

    def _stop_watchdog(self):
        """Signals the watchdog thread to stop and waits for it to terminate."""
        self._watchdog_stop_event.set()
        if self._watchdog_thread and self._watchdog_thread.is_alive():
            self._watchdog_thread.join(timeout=self.watchdog_interval_s + 5)
        self._watchdog_thread = None

    def _watchdog_loop(self):
        """Background loop: probes the server port at a fixed interval. If the
        probe fails for `watchdog_failure_threshold` consecutive checks, the
        server is assumed to be stuck (accept loop dead) and is restarted."""
        while not self._watchdog_stop_event.wait(self.watchdog_interval_s):
            if self._is_server_responsive():
                if self._consecutive_failures:
                    logger.info("Actuator Server watchdog: server responsive again.")
                self._consecutive_failures = 0
                continue

            self._consecutive_failures += 1
            logger.warning(
                "Actuator Server watchdog: health check failed (%s/%s).",
                self._consecutive_failures,
                self.watchdog_failure_threshold,
            )

            if self._consecutive_failures >= self.watchdog_failure_threshold:
                logger.error(
                    "Actuator Server watchdog: server unresponsive after %s consecutive "
                    "failed checks. Restarting HTTPS Actuator Server...",
                    self._consecutive_failures,
                )
                self._restart_server()
                self._consecutive_failures = 0

    def _is_server_responsive(self) -> bool:
        """Performs a lightweight TLS handshake probe against the actuator
        server's own listening socket to verify the accept loop is alive.
        A plain TCP connect is not enough on some Windows network drop
        scenarios where the OS still completes the 3-way handshake locally
        even though the listener's accept loop is dead; the TLS handshake
        forces the app to actually process the connection."""
        host = self.ip if self.ip not in ("0.0.0.0", "") else "127.0.0.1"
        try:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            with socket.create_connection(
                (host, self.port), timeout=self.watchdog_probe_timeout_s
            ) as sock:
                with context.wrap_socket(sock, server_hostname=host) as tls_sock:
                    tls_sock.settimeout(self.watchdog_probe_timeout_s)
                    return True
        except (OSError, ssl.SSLError) as e:
            logger.debug("Actuator Server watchdog probe failed: %s", e)
            return False

    def _restart_server(self):
        """Stops the current uvicorn server/thread (without touching the
        watchdog) and starts a fresh one, mirroring what a manual app
        restart used to require."""
        if self.server:
            self.server.should_exit = True
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=self.config.timeout_graceful_shutdown + 5)

        self.server = uvicorn.Server(self.config)
        self.thread = threading.Thread(target=self.server.run)
        self.thread.start()
        self.startup_time = datetime.datetime.now()
        logger.info("HTTPS Actuator Server restarted by watchdog.")

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
