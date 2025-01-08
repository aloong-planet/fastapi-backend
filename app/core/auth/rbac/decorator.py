from functools import wraps

from fastapi import HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.auth import models
from app.core.auth.service import decode_jwt_access_token
from app.log import logger


def admin_required(f):
    @wraps(f)
    async def decorated_function(*args, **kwargs):
        db: AsyncSession = kwargs.get('db')
        request = kwargs.get('request')

        if request is None:
            raise HTTPException(status_code=500, detail="Request object is missing")

        token = request.headers.get('Authorization')
        if token is None or len(token) == 0:
            raise HTTPException(status_code=401, detail="Authorization token is None")
        else:
            try:
                payload = await decode_jwt_access_token(token)
                if payload is None:
                    raise HTTPException(status_code=401, detail="Invalid token: decode failed")
            except Exception as err:
                logger.info(f"Invalid token: {err}")
                raise HTTPException(status_code=401, detail="Invalid token: exception")

            try:
                email: str = payload.get("user_id")
                user = (await db.exec(select(models.RUser).where(models.RUser.email == email))).first()
                if user.roles is None or len(user.roles) == 0:
                    raise HTTPException(status_code=403, detail=f"Permission denied, no role assigned for user {email}")
                role_name = user.roles[0].name
                logger.debug(f"User: {email}, Role: {role_name}")

                if role_name not in ['admin', 'superAdmin']:
                    raise HTTPException(status_code=403, detail="Permission denied, admin required")
            except Exception as err:
                # If the rbac_user table is dropped, and the user has not login,
                # the decorator will fail and raise this exception
                logger.error(f"Failed to get user role: {err}")
                raise HTTPException(status_code=401, detail=f"Failed to get user role: {err}")

        return await f(*args, **kwargs)

    return decorated_function
