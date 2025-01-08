from typing import Optional, Any, List

from pydantic import (ValidationInfo, field_validator)
from pydantic_settings import (BaseSettings, SettingsConfigDict)


class OTELConfigs(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    OTEL_ENABLED: bool = False
    OTEL_MODE: str = "HTTP"
    OTEL_GRPC_ENDPOINT: Optional[str] = None
    OTEL_HTTP_ENDPOINT: Optional[str] = None
    OTEL_ENDPOINT: Optional[str] = None
    OTEL_EXCLUDED_URLS: List[str] = [
        "https?:\/\/[a-zA-Z0-9.-]+(?::\d+)?\/(?:[\w-]+\/)*$",
        "/metrics"
    ]

    @field_validator("OTEL_ENDPOINT", mode="before")
    @classmethod
    def decide_otel_endpoint(cls, v: Optional[str], values: ValidationInfo) -> Any:
        if isinstance(v, str):
            return v

        if values.data.get("OTEL_MODE") == "HTTP":
            return values.data.get("OTEL_HTTP_ENDPOINT")
        else:
            return values.data.get("OTEL_GRPC_ENDPOINT")
