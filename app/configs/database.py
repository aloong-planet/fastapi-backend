from typing import Union, Optional, Any

from pydantic import (PostgresDsn, ValidationInfo, field_validator, MySQLDsn)
from pydantic_settings import (BaseSettings, SettingsConfigDict)


class DatabaseConfigs(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    POSTGRES_HOST: Optional[str] = None
    POSTGRES_PORT: Optional[int] = 5432
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_DB: Optional[str] = None
    POSTGRES_URI: Union[Optional[PostgresDsn], Optional[str]] = None

    POOL_PRE_PING: bool = True
    POOL_SIZE: int = 10
    POOL_RECYCLE: int = 3600
    POOL_TIMEOUT: int = 30


    @field_validator("POSTGRES_URI", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], values: ValidationInfo) -> Any:
        if isinstance(v, str):
            return v

        return "{scheme}://{username}:{password}@{host}:{port}/{db}".format(
            scheme="postgresql+asyncpg",
            username=values.data.get("POSTGRES_USER"),
            password=values.data.get("POSTGRES_PASSWORD"),
            host=values.data.get("POSTGRES_HOST"),
            port=values.data.get("POSTGRES_PORT"),
            db=f"{values.data.get('POSTGRES_DB') or ''}")

        # [TODO]: pydantic PostgresDsn parse password with special have issue and still do not be solved, so currently we concat db uri string by ourselves.
        # Issue: https://github.com/pydantic/pydantic-core/pull/1369
        # return PostgresDsn.build(
        #     scheme="postgresql+asyncpg",
        #     username=values.data.get("POSTGRES_USER"),
        #     password=values.data.get("POSTGRES_PASSWORD").replace('%', '%%'),
        #     host=values.data.get("POSTGRES_HOST"),
        #     port=values.data.get("POSTGRES_PORT"),
        #     path=f"{values.data.get('POSTGRES_DB') or ''}",
        # ).unicode_string()

class SACMySQLConfigs(BaseSettings):
    # this is for sync token with sac (temporary workaround)
    MYSQL_HOST: Optional[str] = None
    MYSQL_PORT: Optional[int] = 3306
    MYSQL_USER: Optional[str] = None
    MYSQL_PASSWORD: Optional[str] = None
    MYSQL_DB: Optional[str] = None
    MYSQL_URI: Union[Optional[MySQLDsn], Optional[str]] = None

    @field_validator("MYSQL_URI", mode="before")
    @classmethod
    def assemble_mysql_connection(cls, v: Optional[str], values: ValidationInfo) -> Any:
        if isinstance(v, str):
            return v

        return "mysql+aiomysql://{username}:{password}@{host}:{port}/{db}".format(
            username=values.data.get("MYSQL_USER"),
            password=values.data.get("MYSQL_PASSWORD"),
            host=values.data.get("MYSQL_HOST"),
            port=values.data.get("MYSQL_PORT"),
            db=f"{values.data.get('MYSQL_DB') or ''}")


class ClickHouseConfigs(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    CLICKHOUSE_HOST: str = None
    CLICKHOUSE_PORT: int = 9000
    CLICKHOUSE_USER: str = "default"
    CLICKHOUSE_PASSWORD: Optional[str] = ""
    CLICKHOUSE_DB: str = "otel"
