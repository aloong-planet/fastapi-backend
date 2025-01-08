from fastapi import Depends, APIRouter, Request, Query, status
from fastapi import Header
from fastapi_versionizer import api_version
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database.postgres.session import get_session
from app.exceptions import http_exception
from app.responses import GeneralResponse
from .schemas import JWTTokenResponse
from .service import get_auth_handler, get_jwt_access_token

router = APIRouter()


@api_version(major=1)
@router.get("/login/aad")
async def aad_login(request: Request, auth_handler=Depends(get_auth_handler)):
    frontend_host = request.query_params.get("frontendHost")
    return await auth_handler.login_handler(frontend_host)


@api_version(major=1)
@router.get("/redirect")
async def redirect(code: str = Query(...), state: str = Query(...), auth_handler=Depends(get_auth_handler),
                   db: AsyncSession = Depends(get_session)):
    return await auth_handler.redirect_handler(code, state, db)


@router.get("/jwt/token", response_model=JWTTokenResponse)
async def jwt_token(user: str = Header(None), db: AsyncSession = Depends(get_session)):
    if user is None:
        raise http_exception(status_code=status.HTTP_401_UNAUTHORIZED, message="No user found in header")
    token = await get_jwt_access_token(user, db)
    return JWTTokenResponse(username=user, jwt_token=token)


@router.get("/logout", response_model=GeneralResponse)
async def logout(user: str = Header(None), db: AsyncSession = Depends(get_session),
                 auth_handler=Depends(get_auth_handler)):
    if user is None:
        raise http_exception(status_code=status.HTTP_401_UNAUTHORIZED,
                             message="User not found in header")
    ok = await auth_handler.logout_handler(user, db)
    if not ok:
        return GeneralResponse(code=1, message='Failed', data='')

    return GeneralResponse(code=0, message='Success', data='')
