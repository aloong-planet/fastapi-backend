from typing import Any, Optional, Union

from pydantic import (RedisDsn, ValidationInfo, field_validator, model_validator)
from pydantic_settings import (BaseSettings, SettingsConfigDict)


class RedisCacheConfigs(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    ENV: Optional[str] = None

    REDIS_HOST: str = None
    REDIS_PORT: Optional[int] = 6379
    REDIS_USERNAME: Optional[str] = None
    REDIS_CLUSTER_NAME: Optional[str] = None
    REDIS_URI: Union[Optional[RedisDsn], Optional[str]] = None
    REDIS_DECODE_RESPONSES: bool = False
    REDIS_SSL: bool = False
    REDIS_SOCKET_CONNECT_TIMEOUT: int = 5
    REDIS_SOCKET_TIMEOUT: int = 5

    REDIS_IAM_TOKEN_MAX_SIZE: int = 128
    REDIS_IAM_TOKEN_TTL: int = 600

    @field_validator("REDIS_URI", mode="before")
    @classmethod
    def assemble_cache_connection(cls, v: Optional[str], values: ValidationInfo) -> Any:
        if isinstance(v, str):
            return v

        env = values.data.get("ENV")

        return RedisDsn.build(scheme="rediss" if env != 'local' else "redis",
                              host=values.data.get("REDIS_HOST"),
                              port=values.data.get("REDIS_PORT")).unicode_string()

    @model_validator(mode='before')
    @classmethod
    def assemble_auth_config(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if data.get('ENV') != 'local':
                data['REDIS_SSL'] = True
                data['REDIS_SOCKET_CONNECT_TIMEOUT'] = 10
                data['REDIS_SOCKET_TIMEOUT'] = 10

        return data
