from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class Audit(SQLModel, table=True):
    __tablename__ = "audit_logs"
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    username: str = Field(max_length=50, index=True)
    user_id: int = Field(max_length=8, index=True)
    audit_time: datetime = Field(default_factory=datetime.utcnow)
    action: str = Field(max_length=16, description="The action type to audit")
    result: str = Field(max_length=16)
    detail: str = Field(max_length=255, description="The detail of the action")
