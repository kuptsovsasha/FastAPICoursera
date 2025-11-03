import pytest
from httpx import AsyncClient


async def register_user(async_client: AsyncClient, email: str, password: str) -> dict:
    user_data = {"email": email, "password": password}
    response = await async_client.post("/users/register", json=user_data)
    return response.json()


@pytest.mark.anyio
async def test_register_user(async_client: AsyncClient):
    email = "test@example.com"
    password = "password"
    user = await register_user(async_client, email, password)
    assert user["email"] == email
    assert "password" not in user


@pytest.mark.anyio
async def test_register_existing_user(async_client: AsyncClient):
    email = "test@example.com"
    password = "password"
    user = await register_user(async_client, email, password)
    assert user["email"] == email
    assert "password" not in user
    # Try to register the same user again
    response = await async_client.post(
        "/users/register", json={"email": email, "password": password}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


@pytest.mark.anyio
async def test_login_user(async_client: AsyncClient):
    email = "test@example.com"
    password = "password"
    await register_user(async_client, email, password)
    response = await async_client.post(
        "/users/token", json={"email": email, "password": password}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.anyio
async def test_login_invalid_user(async_client: AsyncClient):
    response = await async_client.post(
        "/users/token",
        json={"email": "invalid@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"
