from typing import Optional

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel


class JWTTokenResponse(SQLModel):
    username: str = Field(..., description="The email of the user as username")
    jwt_token: Optional[str] = Field(..., description="The JWT access token for the user")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "test@gmail.com",
                "jwt_token": "jwt_token_string",
            }
        }
    )
