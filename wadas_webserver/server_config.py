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
# Description: Class to handle WADAS Web Server configuration.
import logging
import secrets
from pathlib import Path

import keyring

logger = logging.getLogger(__name__)


class ServerConfig:
    """Class to handle WADAS Web Server configuration"""

    JWT_ENC_ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 15
    REFRESH_TOKEN_EXPIRE_DAYS = 7

    CURRENT_DIRECTORY = Path(__file__).resolve().parent
    CERT_FOLDER = CURRENT_DIRECTORY / "web_cert"
    CERT_FILEPATH = CERT_FOLDER / "cert.pem"
    KEY_FILEPATH = CERT_FOLDER / "key.pem"

    WADAS_ROOT_DIR = CURRENT_DIRECTORY.parent

    instance = None

    def __init__(self, project_uuid):
        self.project_uuid = project_uuid

    def _get_or_set_secret_key(self, key_type):
        service_name = f"WADAS_web_server_{key_type}_{self.project_uuid}"
        username = f"{key_type}_token"

        if cred := keyring.get_credential(service_name, username):
            return cred.password

        secret = secrets.token_hex(32)
        keyring.set_password(service_name, username, secret)
        return secret

    @property
    def access_secret_key(self):
        return self._get_or_set_secret_key("access")

    @property
    def refresh_secret_key(self):
        return self._get_or_set_secret_key("refresh")
