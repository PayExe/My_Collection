from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


def error_response(
    status_code: int,
    message: str,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"erreur": {"code": status_code, "message": message}},
        headers=headers,
    )


async def http_exception_handler(
    _: Request,
    exception: StarletteHTTPException,
) -> JSONResponse:
    return error_response(
        exception.status_code,
        str(exception.detail),
        exception.headers,
    )


async def validation_exception_handler(
    _: Request,
    exception: RequestValidationError,
) -> JSONResponse:
    first_error = exception.errors()[0]
    field = ".".join(str(part) for part in first_error["loc"] if part != "body")
    return error_response(
        status.HTTP_422_UNPROCESSABLE_CONTENT,
        f"Champ '{field}' invalide : {first_error['msg']}",
    )


async def unexpected_exception_handler(
    _: Request,
    __: Exception,
) -> JSONResponse:
    return error_response(
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        "Erreur interne du serveur",
    )
