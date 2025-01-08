import json
import os
from typing import Dict

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.auth.models import Menu, MenuAction, Role, HashValidation
from app.log import logger
from app.utils.checksum import calculate_file_hash

MENUS_FILE = f'{os.getcwd()}/app/database/postgres/seed/menus.json'


async def add_or_update_menu(db_session: AsyncSession,
                             menu_item: Dict,
                             parent_id: int = None,
                             super_only: bool = False) -> None:
    super_only = menu_item.get('superOnly', super_only)
    check_menu_existed_statement = select(Menu).where(Menu.path == menu_item['path'])
    menu_records = await db_session.exec(check_menu_existed_statement)
    menu = menu_records.first()

    if menu:
        menu.name = menu_item['name']
        menu.parent_id = parent_id
        menu.super_only = super_only
    else:
        menu = Menu(name=menu_item['name'],
                    path=menu_item['path'],
                    parent_id=parent_id,
                    super_only=super_only)
        db_session.add(menu)

    await db_session.commit()
    await db_session.refresh(menu)

    for action in ['view', 'edit', 'hide']:
        check_menu_action_existed_statement = select(MenuAction).where(
            MenuAction.menu_id == menu.id, MenuAction.action == action)

        menu_action_records = await db_session.exec(check_menu_action_existed_statement)
        menu_action = menu_action_records.first()

        if not menu_action:
            menu_action = MenuAction(menu_id=menu.id, action=action)
            db_session.add(menu_action)

    await db_session.commit()

    if 'children' in menu_item:
        for child in menu_item['children']:
            await add_or_update_menu(db_session=db_session,
                                     menu_item=child,
                                     parent_id=menu.id,
                                     super_only=super_only)


async def init_menus(db_session: AsyncSession) -> None:
    logger.info('Init menus and permissions')

    with open(MENUS_FILE) as f:
        menus_data = json.load(f)

    for menu_item in menus_data.get('menus'):
        await add_or_update_menu(db_session=db_session, menu_item=menu_item)

    logger.info('Init menus and permissions done')


async def add_preset_role(db_session: AsyncSession, role_name: str) -> None:
    check_role_existed_statement = select(Role).where(Role.name == role_name)
    role_records = await db_session.exec(check_role_existed_statement)
    role = role_records.first()

    if not role:
        role = Role(name=role_name, is_preset=True)
        db_session.add(role)
        await db_session.commit()
        await db_session.refresh(role)

    if role_name == 'superAdmin':
        list_superadmin_actions_statement = select(MenuAction).where(
            MenuAction.action == 'edit')
        superadmin_actions = await db_session.exec(list_superadmin_actions_statement)
        role.actions.extend(superadmin_actions.all())

        await db_session.commit()
        await db_session.refresh(role)

    if role_name == 'admin':
        list_admin_actions_statement = select(MenuAction).join(Menu).where(
            Menu.super_only == False, MenuAction.action == 'edit')
        admin_actions = await db_session.exec(list_admin_actions_statement)
        role.actions.extend(admin_actions.all())

        await db_session.commit()
        await db_session.refresh(role)

    if role_name == 'guest':
        list_guest_actions_statement = select(MenuAction).join(Menu).where(
            Menu.super_only == False, MenuAction.action == 'view')
        guest_actions = await db_session.exec(list_guest_actions_statement)
        role.actions.extend(guest_actions.all())

        await db_session.commit()
        await db_session.refresh(role)


async def init_role_menus(db_session: AsyncSession) -> None:
    logger.info('Init roles and menus')

    for role in ['superAdmin', 'admin', 'guest']:
        await add_preset_role(db_session, role)

    logger.info('Init roles and permissions done')


async def init_rbac_data(db_session: AsyncSession) -> None:
    try:
        rbac_hash_validation_statement = select(HashValidation).where(
            HashValidation.name == 'rbac_init')
        rbac_hash_records = await db_session.exec(rbac_hash_validation_statement)
        rbac_hash = rbac_hash_records.first()

        current_hash = calculate_file_hash(MENUS_FILE)
        if rbac_hash and rbac_hash.hash == current_hash:
            logger.debug("RBAC data is up to date, skip init")
            return
        else:
            logger.debug("RBAC data is outdated, re-init")
            await init_menus(db_session)
            await init_role_menus(db_session)

            if rbac_hash:
                rbac_hash.hash = current_hash
            else:
                db_session.add(HashValidation(name='rbac_init',
                                              type="initial",
                                              hash=current_hash))
            await db_session.commit()

    except Exception as e:
        logger.error(f"Failed to init rbac data: {e}")
        await db_session.rollback()
    finally:
        await db_session.close()
