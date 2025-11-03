import pytest

from storeapp import security


@pytest.mark.anyio
async def test_get_user(registered_user):
    user = await security.get_user(registered_user["email"])
    assert user is not None
    assert user["email"] == registered_user["email"]


@pytest.mark.anyio
async def test_get_nonexistent_user():
    user = await security.get_user("nonexistent@example.com")
    assert user is None


@pytest.mark.anyio
async def test_verify_password(registered_user):
    password = "password"
    assert security.verify_password(password, security.get_password_hash(password))
