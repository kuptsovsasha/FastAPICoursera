from pydantic import BaseModel


class UserPostIn(BaseModel):
    body: str


class UserPostOut(UserPostIn):
    id: int
    user_id: int

    class ConfigDict:
        from_attributes = True


class CommentIn(BaseModel):
    post_id: int
    body: str


class CommentOut(CommentIn):
    id: int
    user_id: int

    class ConfigDict:
        from_attributes = True


class UserPostWithComments(BaseModel):
    post: UserPostOut
    comments: list[CommentOut] = []
