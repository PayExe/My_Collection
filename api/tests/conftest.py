import os
import tempfile
from collections.abc import Callable, Iterator
from pathlib import Path

import pytest

TEST_DATABASE = Path(tempfile.gettempdir()) / "ma_collection_test.db"
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{TEST_DATABASE.as_posix()}"
os.environ.setdefault("SECRET_KEY", "cle-utilisee-uniquement-pour-les-tests")

from fastapi.testclient import TestClient

from api.db.base import Base
from api.db.database import engine
from api.main import app
from api.seed import seed_catalog


async def reset_database() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
    await seed_catalog()


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        test_client.portal.call(reset_database)
        yield test_client


@pytest.fixture
def create_user(client: TestClient) -> Callable[[str], dict[str, str]]:
    def create(email: str) -> dict[str, str]:
        credentials = {"email": email, "password": "motdepasse"}
        client.post("/auth/register", json=credentials)
        token = client.post("/auth/login", json=credentials).json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    return create


@pytest.fixture
def auth_headers(create_user: Callable[[str], dict[str, str]]) -> dict[str, str]:
    return create_user("alice@exemple.fr")
