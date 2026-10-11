from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from api.core.errors import (
    http_exception_handler,
    unexpected_exception_handler,
    validation_exception_handler,
)
from api.db.database import close_database, create_db_and_tables
from api.routers.auth import router as auth_router
from api.routers.auth import token_router
from api.routers.catalog import router as catalog_router
from api.routers.collection import router as collection_router


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

app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, unexpected_exception_handler)

app.include_router(auth_router)
app.include_router(token_router)
app.include_router(catalog_router)
app.include_router(collection_router)
