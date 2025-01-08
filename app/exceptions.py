from fastapi import HTTPException, status, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.log import logger


def endpoint_not_found_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    error_detail = {
        "path": request.url.path,
        "method": request.method,
        "error_message": "Endpoint Not Found"
    }
    return JSONResponse(
        status_code=404,
        content={"code": 10000404, "message": str(error_detail)}
    )


def http_exception(status_code, message):
    credentials_exception = HTTPException(
        status_code=status_code,
        detail=message
    )
    return credentials_exception


class NeedLoginException(HTTPException):

    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


def need_login_exception_handler(request: Request, exc: NeedLoginException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": 10000401, "message": exc.detail}
    )


def validate_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    error_detail = {
        "path": request.url.path,
        "method": request.method,
        "error_type": "Validation Error",
        "error_message": exc.errors()
    }
    logger.error(f"Validation error: {error_detail}")
    return JSONResponse(
        status_code=422,
        content={"code": 10000422, "message": str(error_detail)}
    )
