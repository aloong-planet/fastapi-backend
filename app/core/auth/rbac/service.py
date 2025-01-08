from typing import List

from sqlalchemy.orm import joinedload
from sqlmodel import select, func, delete
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.auth import models
from app.core.auth.models import RoleMenuActionLink
from app.log import logger
from app.sorting import SortingParams
from . import schemas
from .constants import SUPER_ADMIN_LIST
from .schemas import UserCreate, UserUpdate, RoleCreate, RoleUpdate, MenuActions, MenuActionEnum


async def get_user(db: AsyncSession, user_id: int):
    """
    Get user by user_id and include the associated role.
    """
    user = (await db.exec(select(models.RUser).options(joinedload(models.RUser.roles)).
                          where(models.RUser.id == user_id))).first()
    if user:
        # Construct user data with role
        user_data = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "is_active": user.is_active,
            "role": user.roles[0].name if user.roles else None
        }
        return user_data
    else:
        return None


async def get_users(db: AsyncSession, limit: int, offset: int, sorting: SortingParams) -> dict:
    """
    Get all users and their role with pagination.
    """
    try:
        # Getting the count of users
        count_result = await db.exec(select(func.count(models.RUser.id)))
        count = count_result.one()

        # Building the query
        query = select(models.RUser).options(joinedload(models.RUser.roles))
        query = sorting.apply_sorting(query, models.RUser)
        query = query.offset(offset).limit(limit)

        result = await db.exec(query)
        users = result.unique().all()

        # construct user data with role
        users_data = [
            {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "is_active": user.is_active,
                "role": user.roles[0].name if user.roles else ""
            }
            for user in users
        ]

    except Exception as e:
        logger.error(f"Failed to get users: {e}")
        return {"total": 0, "items": []}
    return {"total": count, "items": users_data}


async def create_user(db: AsyncSession, user: UserCreate):
    """
    Create user and return user object,
    Automatically assign guest role to new user.
    """
    try:
        existing_user = (await db.exec(select(models.RUser).where(models.RUser.email == user.email))).first()
        if existing_user:
            return None
        db_user = models.RUser(name=user.name, email=user.email)
        db.add(db_user)
        await db.flush()  # Use flush to get the user ID without committing the transaction

        role_name = 'admin'
        sa_list = SUPER_ADMIN_LIST
        # assign superAdmin to the user in sa_list, otherwise assign admin
        if user.email in sa_list:
            role_name = 'superAdmin'

        role_id = (await db.exec(select(models.Role.id).where(models.Role.name == role_name))).first()
        if role_id is None:
            logger.error(f"Role '{role_name}' not found in db")
            raise Exception(f"Role '{role_name}' not found in db")

        ok, error = await assign_role_to_user(db, db_user.id, role_id)
        if error:
            logger.error(f"User '{user.name}' created but failed to assign role '{role_name}' to user: {error}")
            raise Exception("Failed to assign role")

        await db.commit()
        return db_user

    except Exception as e:
        logger.error(f"Failed to create user: {e}")
        await db.rollback()
        return None


async def assign_role_to_user(db: AsyncSession, user_id: int, role_id: int):
    try:
        user = (await db.exec(select(models.RUser).where(models.RUser.id == user_id))).first()
        role = (await db.exec(select(models.Role).where(models.Role.id == role_id))).first()
        if not role:
            raise Exception(f"Role not found in db by id {role_id}")
        if user and role:
            user.roles.clear()
            user.roles.append(role)
            await db.commit()
            return True, None
        else:
            logger.error(f"Failed to assign role '{role.name}' to user '{user.name}'")
            raise Exception(f"Failed to assign role '{role.name}' to user '{user.name}'")
    except Exception as e:
        logger.error(f"Failed to assign role to user: {e}")
        await db.rollback()
        return False, f"Failed to assign role to user with error: {e}"


async def get_my_role(db: AsyncSession, user_mail: str):
    try:
        user = (await db.exec(select(models.RUser).where(models.RUser.email == user_mail))).first()
        if not user:
            logger.error(f"User '{user_mail}' not found")
            return None
        return user.roles[0]
    except Exception as e:
        logger.error(f"Failed to get role for user: {e}")
        return None


async def update_user(db: AsyncSession, user_id: int, user: UserUpdate):
    try:
        db_user = (await db.exec(select(models.RUser).where(models.RUser.id == user_id))).first()
        if db_user:
            db_user.name = user.name
            db_user.email = user.email
            await db.commit()
            await db.refresh(db_user)
    except Exception as e:
        logger.error(f"Failed to update user: {e}")
        await db.rollback()
        return None, f"Failed to update user with error: {e}"
    return db_user, None


async def delete_user(db: AsyncSession, user_id: int):
    try:
        db_user = (await db.exec(select(models.RUser).where(models.RUser.id == user_id))).first()
        if db_user:
            await db.delete(db_user)
            await db.commit()
    except Exception as e:
        logger.error(f"Failed to delete user: {e}")
        await db.rollback()
        return None, f"Failed to delete user with error: {e}"
    return db_user, None


async def get_role(db: AsyncSession, role_id: int):
    return (await db.exec(select(models.Role).where(models.Role.id == role_id))).first()


async def get_roles(db: AsyncSession, limit: int, offset: int) -> dict:
    try:
        count = (await db.exec(select(func.count(models.Role.id)))).one()
        roles = (await db.exec(select(models.Role).offset(offset).limit(limit))).all()
    except Exception as e:
        logger.error(f"Failed to get roles: {e}")
        return {"total": 0, "items": []}
    return {"total": count, "items": roles}


async def assign_menu_permissions_to_role(db: AsyncSession, role_id: int, action='view'):
    """
    Assign menu actions to role, by default assign 'view' action without super only menus.
    """
    try:
        db_role = (await db.exec(select(models.Role).where(models.Role.id == role_id))).first()
        target_actions = (await db.exec(select(models.MenuAction).join(models.MenuAction.menu).where(
            models.MenuAction.action == action,
            models.Menu.super_only == False))).all()
        if target_actions:
            # Clear any existing actions to avoid duplication
            db_role.actions = []  # This clears existing associations

            # Add new actions to the role
            for action in target_actions:
                db_role.actions.append(action)

            await db.commit()
            return True
        else:
            logger.error(f"No menus found for role '{db_role.name}' in db")
            return False
    except Exception as e:
        logger.error(f"Failed to assign menu actions to role: {e}")
        return False


async def update_role_menus(db: AsyncSession, role_id: int, menu_assignments: List[MenuActions]):
    try:
        db_role = (await db.exec(select(models.Role).where(models.Role.id == role_id))).first()
        if not db_role:
            raise Exception(f"No role found with ID: {role_id}")

        # Clear existing actions before updating
        db_role.actions = []

        for menu_data in menu_assignments:
            # Look for existing action or create a new one
            action = (await db.exec(select(models.MenuAction).join(models.Menu).where(
                models.MenuAction.menu_id == menu_data.id,
                models.MenuAction.action == menu_data.action))).first()

            if not action:
                # Create action if it doesn't exist
                action = models.MenuAction(menu_id=menu_data.id, action=menu_data.action)
                db.add(action)

            # Assign the action to the role
            db_role.actions.append(action)

        await db.commit()
        return db_role, None

    except Exception as e:
        logger.error(f"Failed to update role menus: {e}")
        await db.rollback()
        return None, f"Failed to update role menus with error: {e}"


async def get_role_menus(db: AsyncSession, role_id: int):
    """
    Get all menus for a role.
    """
    try:
        # Fetch role with eager loading of actions and corresponding menus
        db_role = (await db.exec(select(models.Role).options(
            joinedload(models.Role.actions).joinedload(models.MenuAction.menu)).where(
            models.Role.id == role_id))).first()

        if not db_role:
            return None

        # Build a list of MenuActions from the fetched data
        result_menus = []
        for action in db_role.actions:
            menu = action.menu
            # if db_role is not superAdmin, ignore super only menus
            if not db_role.name == 'superAdmin' and menu.super_only:
                continue
            # Since each menu corresponds to one action, directly set the action
            result_menus.append(MenuActions(
                id=menu.id,
                name=menu.name,
                path=menu.path,
                parent_id=menu.parent_id,
                super_only=menu.super_only,
                action=action.action  # Directly set the action from the action object
            ))

        return result_menus

    except Exception as e:
        logger.error(f"Failed to get role menus: {e}")
        return None


async def create_role(db: AsyncSession, role: RoleCreate):
    try:
        existing_role = (await db.exec(select(models.Role).where(models.Role.name == role.name))).first()
        if existing_role:
            return None, "Role already exists"
        db_role = models.Role(name=role.name, description=role.description)
        db.add(db_role)
        await db.commit()
        await db.refresh(db_role)
        logger.debug(f"Role '{role.name}' created")

        ok = await assign_menu_permissions_to_role(db, db_role.id)
        if not ok:
            logger.error(f"Role '{role.name}' created but failed to assign menu actions to role")
    except Exception as e:
        logger.error(f"Failed to create role: {e}")
        await db.rollback()
        return None, f"Failed to create role with error: {e}"
    return db_role, None


async def update_role(db: AsyncSession, role_id: int, role: RoleUpdate):
    try:
        db_role = await get_role(db, role_id)
        if db_role:
            db_role.name = role.name
            db_role.description = role.description
            await db.commit()
            await db.refresh(db_role)
    except Exception as e:
        logger.error(f"Failed to update role: {e}")
        await db.rollback()
        return None, f"Failed to update role with error: {e}"
    return db_role, None


async def delete_role(db: AsyncSession, role_id: int):
    try:
        db_role = await get_role(db, role_id)
        if db_role:
            # check if the role is assigned to any user
            if db_role.users:
                # get username list
                user_list = [user.email for user in db_role.users]
                err_msg = f"Role '{db_role.name}' is assigned to users: {user_list}, cannot be deleted"
                logger.error(err_msg)
                raise Exception(err_msg)

            if not db_role.is_preset:
                await db.delete(db_role)
                await db.commit()
            else:
                err_msg = f"Role '{db_role.name}' is preset, cannot be deleted"
                logger.error(err_msg)
                raise Exception(err_msg)
    except Exception as e:
        logger.error(f"Failed to delete role: {e}")
        await db.rollback()
        return None, f"Failed to delete role with error: {e}"
    return db_role, None


async def create_menu(db: AsyncSession, menu: schemas.MenuCreate):
    """
    Create menu and add actions to the menu. Return menu object.
    If the menu is a parent menu and marked as super only, all children should be super only.
    If the menu is a child menu, it should inherit the super only property from the parent.
    """
    try:
        parent_menu = (await db.exec(select(models.Menu).where(models.Menu.id == menu.parent_id))).first()
        if parent_menu and parent_menu.super_only:
            menu.super_only = True

        db_menu = models.Menu(name=menu.name, path=menu.path, parent_id=menu.parent_id, super_only=menu.super_only)
        db.add(db_menu)
        await db.commit()
        await db.refresh(db_menu)

        # Add actions to the menu
        action_objects = {}
        for action in MenuActionEnum.to_list():
            db_action = models.MenuAction(menu_id=db_menu.id, action=action)
            db.add(db_action)
            action_objects[action] = db_action
        await db.commit()

        # Find all roles and assign the new menu default action to them
        roles = (await db.exec(select(models.Role))).all()
        for role in roles:
            default_action = MenuActionEnum.edit if role.name in ['admin', 'superAdmin'] else MenuActionEnum.view
            role.actions.append(action_objects[default_action])
        await db.commit()

        return db_menu, None
    except Exception as e:
        logger.error(f"Failed to create menu: {e}")
        await db.rollback()
        return None, f"Failed to create menu with error: {e}"


async def get_menus(db: AsyncSession):
    try:
        menus = (await db.exec(select(models.Menu))).all()
        return menus
    except Exception as e:
        logger.error(f"Failed to get menus: {e}")
        return None


async def update_menu(db: AsyncSession, menu_id: int, menu: schemas.MenuUpdate):
    """
    Update menu and return menu object.
    If the menu is a child menu, it should inherit the super only property from the parent.
    """
    try:
        db_menu = (await db.exec(select(models.Menu).where(models.Menu.id == menu_id))).first()
        if db_menu:
            parent_menu = (await db.exec(select(models.Menu).where(models.Menu.id == menu.parent_id))).first()
            if parent_menu and parent_menu.super_only:
                menu.super_only = True

            db_menu.name = menu.name
            db_menu.path = menu.path
            db_menu.super_only = menu.super_only
            await db.commit()
            await db.refresh(db_menu)
    except Exception as e:
        logger.error(f"Failed to update menu: {e}")
        await db.rollback()
        return None, f"Failed to update menu with error: {e}"
    return db_menu, None


async def delete_menu(db: AsyncSession, menu_id) -> tuple[bool, str]:
    """
    Delete menu and related actions. If the menu is a parent menu (no parent_id),
    all its children and their related actions are also deleted. Otherwise, only delete the menu and its actions.
    """
    try:
        db_menu = (await db.exec(select(models.Menu).where(models.Menu.id == menu_id))).first()
        if not db_menu:
            raise Exception(f"Menu not found with ID: {menu_id}")

        # Prepare to delete all associated menus and actions
        menu_ids = [menu_id]
        if db_menu.parent_id is None:  # It's a parent menu
            child_menus = (await db.exec(select(models.Menu).where(models.Menu.parent_id == menu_id))).all()
            menu_ids.extend(child.id for child in child_menus)

        # Fetch all action IDs for these menus
        action_ids = (await db.exec(select(models.MenuAction.id).where(models.MenuAction.menu_id.in_(menu_ids)))).all()

        # Delete role-menu action associations
        await db.exec(delete(RoleMenuActionLink).where(RoleMenuActionLink.action_id.in_(action_ids)))
        await db.commit()  # Commit after each major operation to avoid lock issues

        # Delete menu actions
        await db.exec(delete(models.MenuAction).where(models.MenuAction.id.in_(action_ids)))
        await db.commit()

        # Delete child menus first if it's a parent
        if db_menu.parent_id is None:
            await db.exec(delete(models.Menu).where(models.Menu.parent_id == menu_id))
        # Delete the menu itself
        await db.exec(delete(models.Menu).where(models.Menu.id == menu_id))
        await db.commit()

        return True, "Menu and related actions deleted successfully"
    except Exception as e:
        logger.error(f"Failed to delete menu: {str(e)}")
        await db.rollback()
        return False, f"Failed to delete menu: {str(e)}"


async def get_my_menus(db, user):
    """
    Get the role of current user, and then use get_role_menus to get all menus.
    """
    try:
        role = await get_my_role(db, user)
        if not role:
            return None
        return await get_role_menus(db, role.id)
    except Exception as e:
        logger.error(f"Failed to get menus for user: {e}")
        return None
