from typing import List

from fastapi import APIRouter, Depends, Request, Header
from fastapi_versionizer import api_version
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database.postgres.session import get_session
from app.responses import GeneralResponse, PaginatedParams, PaginationData
from app.sorting import SortingParams
from . import schemas
from . import service
from .decorator import admin_required
from .schemas import MenuActions

router = APIRouter()


@api_version(major=1)
@router.get("/users", response_model=GeneralResponse[PaginationData[schemas.UserProfile]])
async def read_users(db: AsyncSession = Depends(get_session),
                     p: PaginatedParams = Depends(PaginatedParams),
                     s: SortingParams = Depends(SortingParams),
                     ):
    result = await service.get_users(db, p.limit, p.offset, s)
    return GeneralResponse(code=0, message="Success", data=result)


@api_version(major=1)
@router.get("/users/{user_id}", response_model=GeneralResponse[schemas.UserProfile],
            summary="[TestOnly] Get a user")
async def read_user(user_id: int, db: AsyncSession = Depends(get_session)):
    db_user = await service.get_user(db, user_id=user_id)
    if db_user is None:
        return GeneralResponse(code=1, message="User not found", data=None)
    return GeneralResponse(code=0, message="Success", data=db_user)


@api_version(major=1)
@router.post("/users", response_model=GeneralResponse[schemas.User],
             summary="[TestOnly] Create a user")
@admin_required
async def create_user(user: schemas.UserCreate, request: Request, db: AsyncSession = Depends(get_session)):
    db_user = await service.create_user(db=db, user=user)
    if db_user is None:
        return GeneralResponse(code=1, message="User creation failed", data=None)
    return GeneralResponse(code=0, message="User created successfully", data=db_user)


@api_version(major=1)
@router.put("/users/{user_id}", response_model=GeneralResponse[schemas.User])
@admin_required
async def update_user(user_id: int, user: schemas.UserUpdate, request: Request,
                      db: AsyncSession = Depends(get_session)):
    db_user, error = await service.update_user(db, user_id=user_id, user=user)
    if error:
        return GeneralResponse(code=1, message=error, data=None)
    return GeneralResponse(code=0, message="User updated successfully", data=db_user)


@api_version(major=1)
@router.delete("/users/{user_id}", response_model=GeneralResponse[None],
               summary="[Test Only] Delete a user")
@admin_required
async def delete_user(user_id: int, request: Request, db: AsyncSession = Depends(get_session)):
    db_user, error = await service.delete_user(db, user_id=user_id)
    if error:
        return GeneralResponse(code=1, message=error, data=None)
    return GeneralResponse(code=0, message="User deleted successfully", data=None)


@api_version(major=1)
@router.get("/roles", response_model=GeneralResponse[PaginationData[schemas.Role]])
async def read_roles(db: AsyncSession = Depends(get_session),
                     p: PaginatedParams = Depends(PaginatedParams)):
    roles = await service.get_roles(db, p.limit, p.offset)
    if roles is None:
        return GeneralResponse(code=1, message="Roles not found", data=None)
    return GeneralResponse(code=0, message="Success", data=roles)


@api_version(major=1)
@router.get("/roles/{role_id}", response_model=GeneralResponse[schemas.Role])
async def read_role(role_id: int, db: AsyncSession = Depends(get_session)):
    db_role = await service.get_role(db, role_id=role_id)
    if db_role is None:
        return GeneralResponse(code=1, message="Role not found", data=None)
    return GeneralResponse(code=0, message="Success", data=db_role)


@api_version(major=1)
@router.post("/roles", response_model=GeneralResponse[schemas.Role])
@admin_required
async def create_role(role: schemas.RoleCreate, request: Request, db: AsyncSession = Depends(get_session)):
    db_role, error = await service.create_role(db=db, role=role)
    if error:
        return GeneralResponse(code=1, message=error, data=None)
    return GeneralResponse(code=0, message="Role created successfully", data=db_role)


@api_version(major=1)
@router.put("/roles/{role_id}", response_model=GeneralResponse[schemas.Role])
@admin_required
async def update_role(role_id: int, role: schemas.RoleUpdate, request: Request,
                      db: AsyncSession = Depends(get_session)):
    db_role, error = await service.update_role(db, role_id=role_id, role=role)
    if error:
        return GeneralResponse(code=1, message=error, data=None)
    return GeneralResponse(code=0, message="Role updated successfully", data=db_role)


@api_version(major=1)
@router.delete("/roles/{role_id}", response_model=GeneralResponse[None])
@admin_required
async def delete_role(role_id: int, request: Request, db: AsyncSession = Depends(get_session)):
    db_role, error = await service.delete_role(db, role_id=role_id)
    if error:
        return GeneralResponse(code=1, message=error, data=None)
    return GeneralResponse(code=0, message="Role deleted successfully", data=None)


@api_version(major=1)
@router.post("/menus", response_model=GeneralResponse[schemas.Menu])
@admin_required
async def create_menu(menu: schemas.MenuCreate, request: Request, db: AsyncSession = Depends(get_session)):
    db_menu, error = await service.create_menu(db=db, menu=menu)
    if error:
        return GeneralResponse(code=1, message=error, data=None)
    return GeneralResponse(code=0, message="Menu created successfully", data=db_menu)


# The default menus are initialized in init_data.py
@api_version(major=1)
@router.get("/menus", response_model=GeneralResponse[List[schemas.Menu]])
async def get_menus(db: AsyncSession = Depends(get_session)):
    """
    Get all menus, including parent and children menus.
    """
    menus = await service.get_menus(db)
    if menus is None:
        return GeneralResponse(code=1, message="Menus not found", data=None)
    return GeneralResponse(code=0, message="Success", data=menus)


@api_version(major=1)
@router.put("/menus/{menu_id}", response_model=GeneralResponse[schemas.Menu])
@admin_required
async def update_menu(menu_id: int, menu: schemas.MenuUpdate, request: Request,
                      db: AsyncSession = Depends(get_session)):
    db_menu, error = await service.update_menu(db, menu_id=menu_id, menu=menu)
    if error:
        return GeneralResponse(code=1, message=error, data=None)
    return GeneralResponse(code=0, message="Menu updated successfully", data=db_menu)


@api_version(major=1)
@router.delete("/menus/{menu_id}", response_model=GeneralResponse[None])
@admin_required
async def delete_menu(menu_id: int, request: Request, db: AsyncSession = Depends(get_session)):
    success, message = await service.delete_menu(db, menu_id)
    if not success:
        return GeneralResponse(code=1, message=message, data=None)
    return GeneralResponse(code=0, message=message, data=None)


@api_version(major=1)
@router.put("/users/{user_id}/role", response_model=GeneralResponse[None])
@admin_required
async def assign_user_role(user_id: int, role_id: int, request: Request, db: AsyncSession = Depends(get_session)):
    ok, error = await service.assign_role_to_user(db, user_id, role_id)
    if error:
        return GeneralResponse(code=1, message=error, data=None)
    return GeneralResponse(code=0, message="Roles assigned to user successfully", data=None)


@api_version(major=1)
@router.get("/my_role", response_model=GeneralResponse[schemas.Role])
async def get_my_role(user: str = Header(...), db: AsyncSession = Depends(get_session)):
    """
    Get the role of current user.
    """
    db_role = await service.get_my_role(db, user)
    if db_role is None:
        return GeneralResponse(code=1, message="Role not found", data=None)
    return GeneralResponse(code=0, message="Success", data=db_role)


@api_version(major=1)
@router.get("/my_menus", response_model=GeneralResponse[List[schemas.MenuActions]])
async def get_my_menus(db: AsyncSession = Depends(get_session), user: str = Header(...)):
    """
    Get all menus for the user, including parent and children menus.
    """
    menus = await service.get_my_menus(db, user)
    if menus is None:
        return GeneralResponse(code=1, message="Menus not found", data=None)
    return GeneralResponse(code=0, message="Success", data=menus)


@api_version(major=1)
@router.get("/roles/{role_id}/menus", response_model=GeneralResponse[List[MenuActions]])
async def read_role_menus(role_id: int, db: AsyncSession = Depends(get_session)):
    """
    Get all menus for a role, including parent and children menus.
    """
    # db_role = await service.get_role(db, role_id=_role_id)
    db_menus = await service.get_role_menus(db, role_id=role_id)
    if db_menus is None:
        return GeneralResponse(code=1, message="Role menus not found", data=None)
    return GeneralResponse(code=0, message="Success", data=db_menus)


@api_version(major=1)
@router.put("/roles/{role_id}/menus", response_model=GeneralResponse[List[MenuActions]])
@admin_required
async def assign_role_menus(role_id: int, menus: List[MenuActions], request: Request,
                            db: AsyncSession = Depends(get_session)):
    db_role, error = await service.update_role_menus(db, role_id=role_id, menu_assignments=menus)
    if error:
        return GeneralResponse(code=1, message=error, data=None)

    # Prepare the data to be returned
    result_menus = []
    for action in db_role.actions:
        menu = action.menu
        # Now we directly assign action string to the action attribute
        result_menus.append(MenuActions(
            id=menu.id,
            name=menu.name,
            path=menu.path,
            parent_id=menu.parent_id,
            action=action.action  # Directly use the action string
        ))

    return GeneralResponse(code=0, message="Menus assigned to role successfully", data=result_menus)
