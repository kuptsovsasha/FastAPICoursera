from pydantic import BaseModel


class UserPostIn(BaseModel):
    body: str


class UserPostOut(UserPostIn):
    id: int

    class ConfigDict:
        from_attributes = True


class CommentIn(BaseModel):
    post_id: int
    body: str


class CommentOut(CommentIn):
    id: int

    class ConfigDict:
        from_attributes = True


class UserPostWithComments(UserPostOut):
    post: UserPostOut
    comments: list[CommentOut] = []
