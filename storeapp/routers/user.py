import logging

from fastapi import APIRouter, HTTPException

from storeapp.databse import database, user_table
from storeapp.models.user import UserIn
from storeapp.security import (
    UserNotFoundError,
    authenticate_user,
    creat_access_token,
    get_password_hash,
    get_user,
)

logger = logging.getLogger(__name__)


router = APIRouter()


@router.post("/register", status_code=201)
async def register_user(user: UserIn):
    existing_user = await get_user(user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(user.password)
    query = user_table.insert().values(email=user.email, password=hashed_password)
    logger.debug("Query to insert user", extra={"query": str(query)})
    user_id = await database.execute(query)
    return {"id": user_id, "email": user.email}


@router.post("/token")
async def login_user(user: UserIn):
    try:
        user = await authenticate_user(email=user.email, password=user.password)
    except UserNotFoundError:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = creat_access_token(email=user["email"])
    return {"access_token": access_token}
