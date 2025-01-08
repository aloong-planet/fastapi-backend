from enum import Enum


class REGIONS(str, Enum):
    US = "US"
    EU = "EU"
    JP = "JP"
    AU = "AU"


class AlertStatusEnum(str, Enum):
    FIRING = "firing"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"

    @classmethod
    def get_values(cls):
        return [item.value for item in cls]

    @classmethod
    def get_values_str(cls):
        return ",".join([f"{item.value}" for item in cls])


class HTTP_RESPONSE_CODE(Enum):
    # HTTP Response Code
    # confirm with frontend, they need a code to capture the error
    NOT_FOUND = 10000404


class AuditActionEnum(str, Enum):
    LOGIN = "login"
    LOGOUT = "logout"

class Incident_Notification_Draft_Code(Enum):
    Real_Code = 0
    Draft_Code = 1



