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
# Date: 2024-10-01
# Description: FTPS server module

import logging
import os
import pathlib
import threading
from logging.handlers import RotatingFileHandler

import filetype
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import TLS_FTPHandler
from pyftpdlib.servers import ThreadedFTPServer

from wadas.domain.camera import media_queue

logger = logging.getLogger(__name__)


def initialize_fpts_logger():
    """Method to initialize FTPS server logger"""

    pyftpdlib_logger = logging.getLogger("pyftpdlib")
    logger.setLevel(logging.DEBUG)
    handler = RotatingFileHandler(
        os.path.join("log", "ftps_server.log"), maxBytes=100000, backupCount=3
    )
    formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s", "%Y-%m-%d %H:%M:%S")
    handler.setFormatter(formatter)
    pyftpdlib_logger.addHandler(handler)
    pyftpdlib_logger.propagate = False


class TLS_FTP_WADAS_Handler(TLS_FTPHandler):
    """Class to handle FTP communications with FTP Server"""

    # .txt is allowed for testing purpose by Reolink cameras
    ALLOWED_EXTS = frozenset(
        (".avi", ".jpg", ".jpeg", ".mov", ".mp4", ".png", ".txt", ".mkv", ".wmv")
    )

    def ftp_STOR(self, file, mode="w"):
        cur_ext = pathlib.Path(file.lower()).suffix
        if cur_ext in self.ALLOWED_EXTS:
            super().ftp_STOR(file, mode)
        else:
            logger.warning("Unsupported file extension for %s. Connection aborted.", file)
            self.ftp_ABOR(None)

    def on_connect(self):
        logger.info(
            "Connected remote camera %s from %s:%s", self.username, self.remote_ip, self.remote_port
        )

    def on_disconnect(self):
        logger.info(
            "Disconnected remote camera %s from %s:%s",
            self.username,
            self.remote_ip,
            self.remote_port,
        )

    def on_login(self, username):
        logger.info("%s camera logged in.", username)

    def on_logout(self, username):
        logger.info("%s camera logged out.", username)

    def on_file_received(self, file):
        logger.info("Received %s file from FTPS camera %s.", file, self.username)

        # check if the received file match one of the allowed extensions
        # (the check relies on an inspection of the file content)
        if (ftype := filetype.guess(file)) and f".{ftype.extension}" in self.ALLOWED_EXTS:
            media_queue.put(
                {
                    "media_path": file,
                    "media_id": pathlib.PurePath(file).parent.name,
                    "camera_id": self.username,
                }
            )
        else:
            logger.warning("Unsupported file %s. Removing file.", file)
            os.remove(file)

    def on_incomplete_file_received(self, file):
        logger.info("Partial file received. Removing %s", file)
        os.remove(file)


class FTPsServer:
    """FTP server class"""

    ftps_server = None

    def __init__(
        self, ip_address, port, passive_ports, max_conn, max_conn_per_ip, certificate, key, ftp_dir
    ):
        super(FTPsServer, self).__init__()
        # Store params to allow serialization
        self.ip = ip_address
        self.port = port
        self.passive_ports = passive_ports
        self.max_conn = max_conn
        self.max_conn_per_ip = max_conn_per_ip
        self.certificate = certificate
        self.key = key
        self.ftp_dir = ftp_dir

        # SSL handler
        self.handler = TLS_FTP_WADAS_Handler
        self.handler.certfile = self.certificate
        self.handler.keyfile = self.key
        self.handler.passive_ports = self.passive_ports
        # welcome banner
        self.handler.banner = "WADAS FTPS server!"

        # Authorizer
        self.authorizer = DummyAuthorizer()
        self.handler.authorizer = self.authorizer

        # TODO: check if ThrottledDTPHandler is needed

        # Server
        self.server = None

    def add_user(self, username, password, directory):
        """Method to add user(s) to the authorizer."""
        if not self.has_user(username):
            self.authorizer.add_user(username, password, directory, perm="elmwMT")
        else:
            logger.debug("%s user already exists. Skipping user addition...", username)

    def has_user(self, username):
        """Wrapper method of authorizer to check if a user already exists"""
        return self.authorizer.has_user(username)

    def remove_user(self, username):
        """Wrapper method of authorizer to remove a user."""
        return self.authorizer.remove_user(username)

    def run(self):
        """Method to create new thread and run a FTPS server."""
        self.server = ThreadedFTPServer((self.ip, self.port), self.handler)
        self.server.max_cons = self.max_conn
        self.server.max_cons_per_ip = self.max_conn_per_ip
        if self.server:
            thread = threading.Thread(target=self.server.serve_forever)

            if thread:
                thread.start()
                logger.info("Starting thread for FTPs Server...")
            else:
                logger.error("Unable to create new thread for FTPs Server.")

            return thread
        else:
            return None

    def serialize(self):
        """Method to serialize FTPS Server object"""

        return {
            "ssl_certificate": self.certificate,
            "ssl_key": self.key,
            "ip": self.ip,
            "port": self.port,
            "passive_ports": self.passive_ports,
            "max_conn": self.max_conn,
            "max_conn_per_ip": self.max_conn_per_ip,
            "ftp_dir": self.ftp_dir,
        }

    @staticmethod
    def deserialize(data):
        """Method to deserialize FTPS Server object from file."""
        return FTPsServer(
            data["ip"],
            data["port"],
            data["passive_ports"],
            data["max_conn"],
            data["max_conn_per_ip"],
            data["ssl_certificate"],
            data["ssl_key"],
            data["ftp_dir"],
        )
