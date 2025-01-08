from pydantic import Field
from pydantic_settings import (BaseSettings, SettingsConfigDict)


class AADConfigs(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    AUTHORITY: str = Field(..., alias="AAD_AUTHORITY")
    CLIENT_ID: str = Field(..., alias="AAD_CLIENT_ID")
    CLIENT_SECRET: str = Field(..., alias="AAD_CLIENT_SECRET")
    ENCRYPTION_KEY: str = Field(..., alias="AAD_ENCRYPTION_KEY")
    TENANT_ID: str = Field(..., alias="AAD_TENANT_ID")
    REDIRECT_URI: str = Field(..., alias="AAD_REDIRECT_URI")
