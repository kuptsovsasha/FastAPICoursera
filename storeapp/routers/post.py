import logging
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException

from storeapp.databse import comment_table, database, post_table
from storeapp.models.post import (
    CommentIn,
    CommentOut,
    UserPostIn,
    UserPostOut,
    UserPostWithComments,
)
from storeapp.models.user import UserIn
from storeapp.security import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()


async def find_post(post_id: int):
    query = post_table.select().where(post_table.c.id == post_id)
    return await database.fetch_one(query)


@router.post("/", response_model=UserPostOut, status_code=201)
async def create_post(
    post: UserPostIn, current_user: Annotated[UserIn, Depends(get_current_user)]
):
    data = {**post.model_dump(), "user_id": current_user.id}
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    logger.error("Creating post")
    logger.error(data)
    query = post_table.insert().values(data)
    record_id = await database.execute(query)
    return {**data, "id": record_id}


@router.get("/", response_model=list[UserPostOut])
async def read_posts():
    query = post_table.select()
    logger.debug("Reading posts")
    logger.debug(query)
    return await database.fetch_all(query)


@router.post("/comment", response_model=CommentOut, status_code=201)
async def create_comment(
    comment: CommentIn, current_user: Annotated[UserIn, Depends(get_current_user)]
):
    post = await find_post(comment.post_id)
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    data = {**comment.model_dump(), "user_id": current_user.id}
    query = comment_table.insert().values(data)
    record_id = await database.execute(query)
    return {**data, "id": record_id}


@router.get("/{post_id}/comments", response_model=list[CommentOut])
async def read_comments(post_id: int):
    query = comment_table.select().where(comment_table.c.post_id == post_id)
    return await database.fetch_all(query)


@router.get("/{post_id}", response_model=UserPostWithComments)
async def read_post(post_id: int):
    post = await find_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return {"post": post, "comments": await read_comments(post_id)}
