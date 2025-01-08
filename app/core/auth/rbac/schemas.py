from enum import Enum
from typing import Optional, List

from pydantic import EmailStr, constr, ConfigDict
from sqlmodel import Field, SQLModel


class MenuActionEnum(str, Enum):
    hide = "hide"
    view = "view"
    edit = "edit"

    @classmethod
    def list_all(cls):
        return ",".join([f"{item.value}" for item in cls])

    @classmethod
    def to_list(cls):
        return [item.value for item in cls]


class UserBase(SQLModel):
    name: str = Field(..., description="Full name of the user",
                      schema_extra={"example": "John Doe"})
    email: EmailStr = Field(..., description="Email address of the user",
                            schema_extra={"example": "john.doe@example.com"})

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "name": "John Doe",
                "email": "john.doe@example.com"
            }
        }
    )


class UserCreate(UserBase):
    pass


class UserUpdate(UserBase):
    pass


class UserInDBBase(UserBase):
    id: int = Field(..., description="User ID")
    is_active: bool = Field(default=True, description="Is the user active")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "id": 1,
                "is_active": True
            }
        }
    )


class User(UserInDBBase):
    pass


class UserProfile(UserInDBBase):
    role: Optional[str] = Field(None, description="Role of the user",
                                schema_extra={"example": "admin"})

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "id": 1,
                "is_active": True,
                "role": "admin"
            }
        }
    )


class RoleBase(SQLModel):
    name: constr(min_length=1) = Field(..., description="Name of the role",
                                       schema_extra={"example": "admin"})
    description: Optional[str] = Field(None, description="Description of the role",
                                       schema_extra={"example": "Administrator"})
    is_preset: bool = Field(default=False, description="Is the role a preset role",
                            schema_extra={"example": True})

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "name": "admin",
                "description": "Administrator",
                "is_preset": True
            }
        }
    )


class RoleCreate(RoleBase):
    pass


class RoleUpdate(RoleBase):
    pass


class RoleInDBBase(RoleBase):
    id: int = Field(..., description="Role ID", schema_extra={"example": 1})

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "admin",
                "description": "Administrator",
                "is_preset": True
            }
        }
    )


class Role(RoleInDBBase):
    pass


class MenuBase(SQLModel):
    name: str = Field(..., description="Name of the menu",
                      schema_extra={"example": "New Parent Menu"})
    path: str = Field(..., description="API endpoint path of the menu",
                      schema_extra={"example": "/ParentMenu"})
    parent_id: Optional[int] = Field(None, description="Parent menu ID, if any",
                                     schema_extra={"example": None})
    super_only: Optional[bool] = Field(False, description="Is this menu super only",
                                       schema_extra={"example": False})

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "name": "Incident",
                "path": "/incident",
                "parent_id": None,
                "super_only": False
            }
        }
    )


class MenuInDBBase(MenuBase):
    id: int = Field(..., description="Menu ID")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Incident",
                "path": "/incident",
                "parent_id": None,
                "super_only": False
            }
        }
    )


class MenuCreate(MenuBase):
    pass


class MenuUpdate(MenuBase):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "name": "New Parent Menu updated",
                "path": "ParentMenuUpdated",
                "parent_id": None,
                "super_only": "False"
            }
        }
    )


class Menu(MenuInDBBase):
    pass


class MenuActions(Menu):
    action: str = Field(..., description=f"action for the menu, Possible values: {MenuActionEnum.list_all()}",
                        schema_extra={"example": "view"})

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Incident",
                "path": "/incident",
                "parent_id": None,
                "action": "view"
            }
        }
    )


class RoleMenus(Role, MenuActions):
    role: Role
    menus: List[MenuActions]

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "role": {
                    "id": 1,
                    "name": "admin",
                    "is_preset": True
                },
                "menus": [
                    {
                        "id": 1,
                        "name": "Incident",
                        "path": "/incident",
                        "parent_id": None,
                        "action": "view"
                    }
                ]
            }
        }
    )
