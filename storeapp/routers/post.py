from fastapi import APIRouter
from fastapi.exceptions import HTTPException

from storeapp.models.post import (
    CommentIn,
    CommentOut,
    UserPostIn,
    UserPostOut,
    UserPostWithComments,
)

router = APIRouter()


post_table = {}
comment_table = {}


def find_post(post_id: int):
    return post_table.get(post_id)


@router.post("/", response_model=UserPostOut, status_code=201)
async def create_post(post: UserPostIn):
    data = post.model_dump()
    post_id = len(post_table) + 1
    new_post = {"id": post_id, **data}
    post_table[post_id] = new_post
    return new_post


@router.get("/", response_model=list[UserPostOut])
async def read_posts():
    return list(post_table.values())


@router.post("/comment", response_model=CommentOut, status_code=201)
async def create_comment(comment: CommentIn):
    post = find_post(comment.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    data = comment.model_dump()
    comment_id = len(comment_table) + 1
    new_comment = {"id": comment_id, **data}
    comment_table[comment_id] = new_comment
    return new_comment


@router.get("/{post_id}/comments", response_model=list[CommentOut])
async def read_comments(post_id: int):
    print(comment_table)
    post = find_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return [
        comment for comment in comment_table.values() if comment["post_id"] == post_id
    ]


@router.get("/{post_id}", response_model=UserPostWithComments)
async def read_post(post_id: int):
    post = find_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return {"post": post, "comments": await read_comments(post_id)}
