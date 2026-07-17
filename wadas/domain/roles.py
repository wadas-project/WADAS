from enum import Enum


class WadasRoles(Enum):
    ADMIN = "Admin"
    VIEWER = "Viewer"
    OPERATOR = "Operator"


# Roles allowed to access actuator-related endpoints (view status/detail and
# issue commands). Admin keeps full access; Operator gets the same standard
# read access as Viewer plus the Actuators page and its controls.
ACTUATOR_ROLES = {WadasRoles.ADMIN, WadasRoles.OPERATOR}
# Roles allowed to access admin-only endpoints (e.g. application logs).
ADMIN_ONLY_ROLES = {WadasRoles.ADMIN}
