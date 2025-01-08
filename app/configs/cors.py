from typing import List

from pydantic_settings import BaseSettings


class CORSConfigs(BaseSettings):
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_MAX_AGE: int = 3600
    CORS_ALLOW_ORIGINS: List[str] = [
        "*",
    ]
    CORS_ALLOW_METHODS: List[str] = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
    CORS_ALLOW_HEADERS: List[str] = [
        "Authorization",
        "Traceparent",
        "User",
        "DNT",
        "X-CustomHeader",
        "Keep-Alive",
        "User-Agent",
        "If-Modified-Since",
        "Cache-Control",
        "Content-Type",
        "Content-Range",
        "Range",
    ]
