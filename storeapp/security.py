import datetime
import logging
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext

from storeapp.config import get_config
from storeapp.databse import database, user_table

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token")

config = get_config()

SECRET_KEY = config.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class UserNotFoundError(Exception):
    pass


def create_access_token(email: str) -> str:
    logger.debug("Creating access token", extra={"email": email})
    expire = datetime.datetime.now(datetime.UTC) + datetime.timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    jwt_data = {"sub": email, "exp": expire}
    encoded_jwt = jwt.encode(jwt_data, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def get_user(email: str):
    logger.debug("Fetching user with email", extra={"email": email})
    query = user_table.select().where(user_table.c.email == email)
    user = await database.fetch_one(query)
    if user:
        return user
    logger.warning(f"User not found: {email}")
    return None


async def authenticate_user(email: str, password: str):
    logger.debug("Authenticating user", extra={"email": email})
    user = await get_user(email)
    if not user:
        raise UserNotFoundError(email)
    if not verify_password(password, user["password"]):
        raise UserNotFoundError(email)
    return user


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    logger.debug("Getting current user from token")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise UserNotFoundError("No email in token")
    except jwt.ExpiredSignatureError as e:
        logger.error("Token has expired", exc_info=e)
        raise HTTPException(
            status_code=401,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

    except jwt.JWTError as e:
        logger.error("JWT decoding error", exc_info=e)
        raise UserNotFoundError("Invalid token")

    user = await get_user(email)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
