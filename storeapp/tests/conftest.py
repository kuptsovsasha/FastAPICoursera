import os
from typing import AsyncGenerator, Generator

import pytest

os.environ["ENV_STATE"] = "test"

from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

from storeapp.databse import database
from storeapp.main import app


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    yield TestClient(app)


@pytest.fixture(autouse=True)
async def db() -> AsyncGenerator[None, None]:
    await database.connect()
    yield
    await database.disconnect()


@pytest.fixture
async def async_client(client) -> AsyncGenerator:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url=client.base_url
    ) as ac:
        yield ac


@pytest.fixture
async def registered_user(async_client: AsyncClient) -> dict:
    user_data = {"email": "test@example.com", "password": "password"}
    response = await async_client.post("/users/register", json=user_data)
    assert response.status_code == 201
    user_response = response.json()
    user_response["password"] = user_data["password"]
    return user_response
