import os
import logging

from pydantic_settings import (BaseSettings, SettingsConfigDict)


class GeneralConfigs(BaseSettings):
    APP_TITLE: str = "Fastapi Backend API"
    APP_DESCRIPTION: str = "All of backend endpoint for Fastapi Backend."
    APP_VERSION: str = "1.0"
    LOG_LEVEL: int = logging.WARNING
