from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class APIWhitelistConfigs(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    API_WHITELIST: List[str] = [
        "/",
        "/docs",
        "/redoc",
        "/metrics",
        "/openapi.json",
        "/api/v1/auth/login/aad",
        "/api/v1/auth/redirect",
        "/api/v1/auth/jwt/token",
    ]
