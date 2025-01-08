from datetime import datetime, timedelta
from urllib.parse import quote

import jwt
import requests
from fastapi import Depends
from msal import ConfidentialClientApplication
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.responses import RedirectResponse

from app.cache.module.base import RedisCache
from app.cache.session import get_redis_connection_pool
from app.configs import get_settings
from app.core.audit.service import create_audit_log
from app.enums import AuditActionEnum
from app.exceptions import NeedLoginException
from app.log import logger
from . import models
from .auth_cache import RedisTokenCache
from .rbac import service as rbac_service
from .rbac.schemas import UserCreate


async def get_auth_handler(config=Depends(get_settings), redis_conn=Depends(get_redis_connection_pool)):
    return AuthHandler(config, redis_conn)


async def sync_token_to_sac(username: str, token: str, user_id, sac_db: AsyncSession):
    """
    This is for sync token with sac (temporary workaround).
    """
    try:
        sac_auth_token = (
            await sac_db.exec(select(models.SACAuthToken).where(models.SACAuthToken.name == username))).first()
        if sac_auth_token:
            sac_auth_token.token = token
            sac_auth_token.aad_user_id = user_id
        else:
            new_sac_auth_token = models.SACAuthToken(
                name=username,
                token=token,
                aad_user_id=user_id,
            )
            sac_db.add(new_sac_auth_token)
        await sac_db.commit()
    except Exception as e:
        logger.error(f"Failed to sync token with sac: {e}")


class AuthHandler:
    def __init__(self, config, redis_conn):
        self.token_cache = RedisTokenCache(redis_conn, encryption_key=config.ENCRYPTION_KEY)
        self.app = ConfidentialClientApplication(
            config.CLIENT_ID,
            authority=config.AUTHORITY,
            client_credential=config.CLIENT_SECRET,
            token_cache=self.token_cache
        )
        self.config = config

        self.bc = RedisCache(redis_conn, "msal_auth:")
        self.fc = RedisCache(redis_conn, "msal_auth_flow:", 60 * 10)  # flow cache for 10 minutes

    async def login_handler(self, frontend_host: str):
        try:
            self.bc.set('frontend_host', frontend_host)
            flow = self.app.initiate_auth_code_flow(
                scopes=['.default'],
                redirect_uri=self.config.REDIRECT_URI,
            )
            self.fc.set(flow["state"], flow)
            return RedirectResponse(url=flow["auth_uri"])
        except Exception as e:
            logger.error(f"Failed to login by exception: {e}")
            return RedirectResponse(url=frontend_host + "/login-result?result=failure", status_code=302)

    async def redirect_handler(self, code: str, state: str, db: AsyncSession):
        try:
            frontend_host = self.bc.get('frontend_host')
        except Exception as e:
            frontend_host = 'http://localhost:3000'  # fallback to default
        frontend_fail_url = frontend_host + "/login-result?result=failure"
        logger.info(f'frontend host {frontend_host}, frontend fail url: {frontend_fail_url}')

        try:
            flow = self.fc.get(state)
            if flow is None:
                return RedirectResponse(url=frontend_fail_url, status_code=302)

            result = self.app.acquire_token_by_auth_code_flow(
                flow,
                {'code': code, 'state': state}
            )
            if "error" in result:
                logger.error(f"Failed to acquire a token: {result}")
                return RedirectResponse(url=frontend_fail_url, status_code=302)

            access_token = result.get('access_token')
            if not access_token:
                logger.error("Access token is missing")
                return RedirectResponse(url=frontend_fail_url, status_code=302)

            user_info = await get_user_info(access_token)
            if user_info:
                logger.debug(f"User info: {user_info}")
                username = user_info.get('mail').lower()
                user_id = user_info.get('id')
                if username:
                    self.token_cache.save(username)
                    # rbac: create or update rbac_user
                    db_user = (await db.exec(select(models.RUser).where(models.RUser.email == username))).first()
                    if not db_user:
                        user = UserCreate(name=user_info.get('displayName'), email=username)
                        await rbac_service.create_user(db, user)
                    # rbac end
                    token = await create_jwt_access_token(username, 60 * 60 * 12)
                    # save token to db
                    logger.debug(f"save token to db: models.AuthToken")
                    auth_token = (
                        await db.exec(select(models.AuthToken).where(models.AuthToken.name == username))).first()
                    if auth_token:
                        auth_token.token = token
                        auth_token.aad_user_id = user_id
                    else:
                        new_auth_token = models.AuthToken(
                            name=username,
                            token=token,
                            aad_user_id=user_id,
                        )
                        db.add(new_auth_token)

                    # audit log
                    await create_audit_log(db, username, AuditActionEnum.LOGIN, "success", "login success")

                    await db.commit()

                else:
                    logger.error("Username is missing")
                    return RedirectResponse(url=frontend_fail_url, status_code=302)
            else:
                logger.error("Failed to get user info")
                return RedirectResponse(url=frontend_fail_url, status_code=302)

            self.fc.delete(state)

        except Exception as e:
            logger.error(f"Failed to login by exception: {e}")
            return RedirectResponse(url=frontend_fail_url, status_code=302)

        frontend_success_url = frontend_host + "/login-result?result=success&username=" + quote(username)
        return RedirectResponse(url=frontend_success_url, status_code=302)

    async def logout_handler(self, username: str, db: AsyncSession) -> bool:
        try:
            # remove token from db
            auth_token = (await db.exec(select(models.AuthToken).where(models.AuthToken.name == username))).first()
            if auth_token:
                await db.delete(auth_token)
                self.token_cache.delete(username)
                await db.commit()
                # audit log
                await create_audit_log(db, username, AuditActionEnum.LOGOUT, "success", "logout success")
                return True
            else:
                raise Exception(f"Failed to logout: token not found for user {username}")
        except Exception as e:
            await db.rollback()
            msg = f"Failed to logout: {str(e)}"
            await create_audit_log(db, username, AuditActionEnum.LOGOUT, "failure", msg)
            logger.error(msg)
            return False

    def get_access_token_obo(self, username: str, scopes: list) -> str or None:
        logger.debug(f"get_access_token_obo: {username}")
        self.token_cache.set_user(username)
        self.token_cache.load()
        accounts = self.app.get_accounts()
        if not accounts:
            logger.debug(f"get_access_token_obo: no cache found for user: {username}")
            raise NeedLoginException(detail=f"Need login user: {username}")

        logger.debug("accounts found")
        result = self.app.acquire_token_silent(scopes, account=accounts[0])
        if result and "access_token" in result:
            return result['access_token']
        else:
            raise NeedLoginException(detail=f"Need login user: {username}")


async def get_user_info(access_token) -> dict or None:
    """
    Get user info from Microsoft Graph API
    """
    graph_api_url = 'https://graph.microsoft.com/v1.0/me'
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    response = requests.get(graph_api_url, headers=headers)
    if response.status_code == 200:
        user_info = response.json()
        return user_info
    else:
        logger.error(f'Failed to get user info: {response.text}')
        return None


async def create_jwt_access_token(username: str, sec: int):
    return jwt.encode({
        'user_id': username,
        'exp': datetime.utcnow() + timedelta(seconds=sec),
        'iat': datetime.utcnow()
    }, 'access_secret', algorithm='HS256')


async def get_jwt_access_token(username: str, db: AsyncSession) -> str or None:
    """
    get token from database with username
    """
    try:
        logger.debug(f'Get access token for user {username}')
        auth_token = (await db.exec(select(models.AuthToken).where(models.AuthToken.name == username))).first()
        return auth_token.token if auth_token else None
    except Exception as e:
        logger.error(f'Failed to get access token for user {username}: {e}')
        return None


async def decode_jwt_access_token(token: str) -> dict or None:
    try:
        return jwt.decode(token, 'access_secret', algorithms=['HS256'])
    except Exception as e:
        logger.error(f'Failed to decode access token: {e}')
        return None
