import logging

from fastapi import APIRouter
from fastapi.exceptions import HTTPException

from storeapp.databse import comment_table, database, post_table
from storeapp.models.post import (
    CommentIn,
    CommentOut,
    UserPostIn,
    UserPostOut,
    UserPostWithComments,
)

logger = logging.getLogger(__name__)

router = APIRouter()


async def find_post(post_id: int):
    query = post_table.select().where(post_table.c.id == post_id)
    return await database.fetch_one(query)


@router.post("/", response_model=UserPostOut, status_code=201)
async def create_post(post: UserPostIn):
    data = post.model_dump()
    query = post_table.insert().values(data)
    record_id = await database.execute(query)
    return {**data, "id": record_id}


@router.get("/", response_model=list[UserPostOut])
async def read_posts():
    query = post_table.select()
    logger.info("Reading posts")
    logger.debug(query)
    return await database.fetch_all(query)


@router.post("/comment", response_model=CommentOut, status_code=201)
async def create_comment(comment: CommentIn):
    post = await find_post(comment.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    data = comment.model_dump()
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
