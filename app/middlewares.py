from typing import List

from fastapi import Response, status
from sqlmodel import select
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.auth import models
from app.core.auth.service import decode_jwt_access_token
from app.database.postgres.session import ASYNC_SESSION
from app.log import logger


class CustomAuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, whitelist: List[str]):
        super().__init__(app)
        self.whitelist = whitelist

    async def dispatch(self, request, call_next):
        if request.url.path in self.whitelist:
            pass
        else:
            user = request.headers.get('user')
            token = request.headers.get('Authorization')
            if token is None or len(token) == 0:
                logger.info('Authorization token is None')
                return Response(status_code=status.HTTP_403_FORBIDDEN, content='Invalid token')
            else:
                try:
                    payload = await decode_jwt_access_token(token)
                    if payload is None:
                        return Response(status_code=status.HTTP_403_FORBIDDEN,
                                        content='Invalid token: decode failed')
                except Exception as err:
                    logger.info(f"Invalid token: {err}")
                    return Response(status_code=status.HTTP_403_FORBIDDEN, content='Invalid token')

                username: str = payload.get("user_id")

                if user != username:
                    return Response(status_code=status.HTTP_403_FORBIDDEN,
                                    content='Invalid token: username not match')

                # in the future, we may add app permission control, then we need to check username and app value...

                async with ASYNC_SESSION() as db:
                    token = (await db.exec(select(models.AuthToken).where(models.AuthToken.token == token))).first()

                    if token is None:
                        return Response(status_code=status.HTTP_403_FORBIDDEN,
                                        content='Invalid token: token not found in db')

        return await call_next(request)
