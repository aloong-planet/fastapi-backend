from pydantic import ConfigDict
from sqlmodel import Field, SQLModel


class ProductBase(SQLModel):
    code: str = Field(max_length=8, primary_key=True)  # product code in v1, such as 'iam', 'uic'
    name: str = Field(max_length=255, unique=True)

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "code": "iam",
                "name": "IAM"
            }
        }
    )


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "code": "iam",
                "name": "IAM Updated"
            }
        }
    )


class ProductInDBBase(ProductBase):
    id: int = Field(default=None, primary_key=True)

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "code": "iam",
                "name": "IAM"
            }
        }
    )


class ProductResponse(ProductInDBBase):
    pass
