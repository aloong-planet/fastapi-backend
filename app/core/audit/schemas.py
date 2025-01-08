from datetime import datetime

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel


class AuditBase(SQLModel):
    username: str = Field(max_length=50, description="username")
    user_id: int = Field(description="user id")
    action: str = Field(max_length=50, description="action type to audit")
    detail: str = Field(max_length=255, description="detail of the action")
    audit_time: datetime = Field(default_factory=datetime.utcnow, description="action time")
    result: str = Field(max_length=16, description="result")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "username": "loong_zhou",
                "user_id": 1,
                "audit_time": "2024-07-05 01:36:29.748624",
                "action": "login",
                "result": "success",
                "detail": "login system"
            }
        }
    )


class AuditCreate(AuditBase):
    pass


class AuditInDBBase(AuditBase):
    id: int = Field(default=None, primary_key=True)

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "username": "admin",
                "user_id": 1,
                "audit_time": "2024-07-05 01:36:29.748624",
                "action": "login",
                "result": "success",
                "detail": "login system"
            }
        }
    )


class AuditResponse(AuditInDBBase):
    pass
