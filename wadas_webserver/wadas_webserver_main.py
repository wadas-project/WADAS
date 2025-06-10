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
# Description: Main for WADAS Web Interface.
import argparse
import base64
import logging
import os
import signal
import socket

from utils import cert_gen, setup_logger

from wadas_webserver.database import Database
from wadas_webserver.server_config import ServerConfig
from wadas_webserver.web_server import WebServer
from wadas_webserver.web_server_app import app

flag_run = True
webserver = None

logger = logging.getLogger(__name__)


def handle_shutdown():
    """Method to catch the SIGINT and SIGTERM signals to properly shut down the process"""
    global flag_run
    logger.info("Killing WADAS web server")
    stop_server()
    flag_run = False


def stop_server():
    """Method to properly handle the FastAPI server shutdown"""
    if webserver:
        webserver.server.should_exit = True


def start_web_server():
    """Method to start the WADAS FastAPI web server on a separate thread
    N.B. HTTPS certificates are built on-the-fly and stored under CERT_FOLDER
    """

    cert_filepath = ServerConfig.CERT_FILEPATH
    key_filepath = ServerConfig.KEY_FILEPATH

    if not os.path.exists(ServerConfig.CERT_FOLDER):
        os.makedirs(ServerConfig.CERT_FOLDER)
        cert_gen(key_filepath, cert_filepath)
    elif not os.path.exists(cert_filepath) or not os.path.exists(key_filepath):
        cert_gen(key_filepath, cert_filepath)

    app.server = WebServer("0.0.0.0", 443, cert_filepath, key_filepath)
    app.server.run()
    return app.server


def blocking_socket():
    """Method to instantiate a blocking socket on a fixed port
    to wait communication attempts from WADAS main process
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ("localhost", 65000)
    server_socket.bind(server_address)

    server_socket.listen(1)
    server_socket.settimeout(1)
    logger.info("WADAS Webserver listening on %s:%d", server_address[0], server_address[1])
    while flag_run:
        try:
            connection, client_address = server_socket.accept()
        except socket.timeout:
            continue

        try:
            logger.info("Connection established with %s", client_address)
            data = connection.recv(1024).decode("utf-8")
            match data:
                case "status":
                    logger.info("Received <status> command")
                    # TODO: check server status
                    response = "ok"
                case "kill":
                    logger.info("Received <kill> command")
                    handle_shutdown()
                    response = "killing"
                case _:
                    logger.info("Received unknown <%s> command", data)
                    response = "unknown"

            connection.sendall(response.encode("utf-8"))

        finally:
            connection.close()


if __name__ == "__main__":
    setup_logger()
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--enc_conn_string", type=str, required=True, help="Encoded connection string"
    )

    parser.add_argument("--project_uuid", type=str, required=True, help="WADAS Project UUID")

    try:
        args = parser.parse_args()
        encoded_string = args.enc_conn_string
        conn_string = base64.b64decode(encoded_string).decode("utf-8")
        project_uuid = args.project_uuid

        if config := ServerConfig(project_uuid):
            ServerConfig.instance = config
            Database.instance = Database(conn_string)
            webserver = start_web_server()
            signal.signal(signal.SIGINT, lambda signum, frame: handle_shutdown())
            signal.signal(signal.SIGTERM, lambda signum, frame: handle_shutdown())
            try:
                blocking_socket()
            except Exception:
                logger.error("Unable to create a listening socket.")
                webserver.stop()
        else:
            logger.error("Unable to initialize Config instance.")
    except Exception:
        logger.exception("Generic Exception.")

    logger.info("WADAS webserver exited.")
