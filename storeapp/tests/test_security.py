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


@pytest.mark.anyio
async def test_get_current_user(registered_user):
    token = security.create_access_token(registered_user["email"])
    user = await security.get_current_user(token)
    assert user is not None
    assert user["email"] == registered_user["email"]


@pytest.mark.anyio
async def test_get_current_user_invalid_token():
    invalid_token = "invalid.token.here"
    with pytest.raises(security.UserNotFoundError):
        await security.get_current_user(invalid_token)
