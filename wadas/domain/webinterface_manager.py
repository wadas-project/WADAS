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
# Date: 2025-10-04
# Description: Main for WADAS Web Interface.
import logging
import threading
import time

from wadas_webserver.wadas_webserver_main import (
    handle_shutdown_threaded,
    run_webserver_threaded,
)

logger = logging.getLogger(__name__)


class WebInterfaceManager:
    """Singleton class to manage the WADAS Web Interface lifecycle."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(WebInterfaceManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        self.web_thread: threading.Thread | None = None
        self.stop_event = threading.Event()
        self._is_running = False
        self.enc_conn_str = None
        self.project_uuid = None

    def start(self, enc_conn_str: str, project_uuid: str):
        """Start the web interface server in a background thread."""
        if self.is_running():
            logger.warning("Web Interface already running.")
            return

        self.enc_conn_str = enc_conn_str
        self.project_uuid = project_uuid
        self.stop_event.clear()

        def target():
            try:
                run_webserver_threaded(enc_conn_str, project_uuid, self.stop_event)
            except Exception:
                logger.exception("Exception in webserver thread")

        self.web_thread = threading.Thread(target=target, daemon=True)
        self.web_thread.start()

        # Wait briefly to confirm startup
        time.sleep(1)
        if self.web_thread.is_alive():
            self._is_running = True
            logger.info("Web Interface started successfully.")
        else:
            logger.error("Failed to start Web Interface.")

    def stop(self):
        """Stop the running web interface server cleanly."""
        if not self.is_running():
            logger.info("Web Interface not running.")
            return

        logger.info("Stopping Web Interface...")
        self.stop_event.set()

        try:
            handle_shutdown_threaded()
        except Exception:
            logger.exception("Error while shutting down webserver (threaded mode)")

        # Give the thread time to exit
        self.web_thread.join(timeout=5)
        if self.web_thread.is_alive():
            logger.warning("Webserver thread did not exit within timeout.")

        self.web_thread = None
        self._is_running = False
        logger.info("Web Interface stopped successfully.")

    def is_running(self) -> bool:
        """Check if the web interface thread is active and running."""
        if self.web_thread and self.web_thread.is_alive() and not self.stop_event.is_set():
            return True
        return False
