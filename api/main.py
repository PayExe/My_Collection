from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.db.database import close_database, create_db_and_tables
from api.routers.auth import router as auth_router

@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    await create_db_and_tables()
    yield
    await close_database()


app = FastAPI(
    title="Ma Collection API",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(
    _: Request,
    exception: HTTPException,
) -> JSONResponse:
    return JSONResponse(
        status_code=exception.status_code,
        content={
            "erreur": {
                "code": exception.status_code,
                "message": str(exception.detail),
            }
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    _: Request,
    __: RequestValidationError,
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "erreur": {
                "code": 422,
                "message": "Données invalides",
            }
        },
    )

app.include_router(auth_router)
