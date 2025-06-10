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
# Description: Module containing generic utility functions.
import logging
import os
import sys
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler

from jose import jwt
from OpenSSL import crypto

from wadas_webserver.server_config import ServerConfig


def cert_gen(key_filepath, cert_filepath):
    """Generate a new certificate-key pair that
    will be stored into key_filepath and cert_filepath
    """
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 4096)
    # create a self-signed cert
    cert = crypto.X509()
    cert.get_subject().CN = "localhost"
    cert.set_serial_number(0)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(10 * 365 * 24 * 60 * 60)
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(k)
    cert.sign(k, "sha512")
    with open(cert_filepath, "wt") as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode("utf-8"))
    with open(key_filepath, "wt") as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k).decode("utf-8"))


def setup_logger():
    # fix: one of our import libraries is setting a root logger with a handler
    # we need to remove it to avoid duplicate logs
    for handler in logging.root.handlers[1:]:
        logging.root.removeHandler(handler)

    current_directory = os.path.dirname(os.path.abspath(__file__))
    log_dir = os.path.join(current_directory, "log")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s", "%Y-%m-%d %H:%M:%S")
    logging_level = logging.INFO

    # WADAS webserver log file
    log_file = os.path.join(log_dir, "WADAS_webserver.log")
    file_handler = RotatingFileHandler(log_file, maxBytes=10 * 1024 * 1024, backupCount=3)
    file_handler.setLevel(logging_level)
    file_handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.setLevel(logging_level)
    logger.addHandler(file_handler)

    class LoggerWriter:
        def __init__(self, write_func):
            self.write_func = write_func

        def write(self, message):
            if message.strip():
                self.write_func(message.strip())

        def flush(self):
            pass  # needed for compatibility with sys.stderr

    sys.stderr = LoggerWriter(logger.error)


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode, ServerConfig.instance.access_secret_key, algorithm=ServerConfig.JWT_ENC_ALGORITHM
    )


def create_refresh_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=7))
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode,
        ServerConfig.instance.refresh_secret_key,
        algorithm=ServerConfig.JWT_ENC_ALGORITHM,
    )
