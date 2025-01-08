import os

from .aad import AADConfigs
from .api_whitelist import APIWhitelistConfigs
from .cache import RedisCacheConfigs
from .cors import CORSConfigs
from .database import DatabaseConfigs, ClickHouseConfigs, SACMySQLConfigs
from .general import GeneralConfigs
from .otel import OTELConfigs


class ENVConfigs(DatabaseConfigs,
                 ClickHouseConfigs,
                 SACMySQLConfigs,
                 RedisCacheConfigs,
                 OTELConfigs,
                 AADConfigs
                 ):
    """ Need read value from environment variables by env. """
    pass


class ProjectConfigs(GeneralConfigs,
                     CORSConfigs,
                     APIWhitelistConfigs):
    """ Used to define static configs, do not be changed by env. """
    pass


class Production(ENVConfigs, ProjectConfigs):
    ENV: str = "prod"


class Staging(ENVConfigs, ProjectConfigs):
    ENV: str = "stg"


class Int(ENVConfigs, ProjectConfigs):
    ENV: str = "int"


class Dev(ENVConfigs, ProjectConfigs):
    ENV: str = "dev"


class Local(ENVConfigs, ProjectConfigs):
    ENV: str = "local"


def get_settings():
    env = os.getenv("ENV", "local")
    if env == "prod":
        return Production()
    elif env == "stg":
        return Staging()
    elif env == "int":
        return Int()
    elif env == "dev":
        return Dev()
    return Local()


APP_SETTINGS = get_settings()
