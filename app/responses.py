from typing import TypeVar, Generic, Optional

from fastapi import Query
from pydantic import BaseModel, Field, ConfigDict

DataType = TypeVar("DataType")


class PaginatedParams:
    def __init__(self, page: int = Query(1, ge=1), size: int = Query(50, ge=0)):
        self.limit = size
        self.offset = (page - 1) * size


class PaginationData(BaseModel, Generic[DataType]):
    total: int = Field(0, description="The total number of items")
    items: list[DataType] = Field([], description="The items in the current page")


class GeneralResponse(BaseModel, Generic[DataType]):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    code: int = Field(0, description="The code of the response, 0 for success, others for failure")
    message: str = Field(..., description="A message providing more details about the response")
    data: Optional[DataType] = Field(None)
