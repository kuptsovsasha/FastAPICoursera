import pytest
from httpx import AsyncClient


async def create_post(
    body: str, async_client: AsyncClient, logged_in_token: str
) -> dict:
    response = await async_client.post(
        "/posts/",
        json={"body": body},
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )
    return response.json()


async def create_comment(
    post_id: int, content: str, async_client: AsyncClient, logged_in_token: str
) -> dict:
    response = await async_client.post(
        "/posts/comment",
        json={"post_id": post_id, "body": content},
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )
    return response.json()


@pytest.fixture(scope="function")
async def created_post(async_client: AsyncClient, logged_in_token: str) -> dict:
    post = await create_post("Test post body", async_client, logged_in_token)
    return post


@pytest.fixture(scope="function")
async def created_comment(
    created_post: dict, async_client: AsyncClient, logged_in_token: str
) -> dict:
    comment = await create_comment(
        created_post["id"], "Test comment content", async_client, logged_in_token
    )
    return comment


@pytest.mark.anyio
async def test_create_post(
    async_client: AsyncClient, registered_user: dict, logged_in_token: str
):
    response = await async_client.post(
        "/posts/",
        json={"body": "Hello, world!"},
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["body"] == "Hello, world!"
    assert data["user_id"] == registered_user["id"]
    assert "id" in data


@pytest.mark.anyio
async def test_create_post_missing_body(
    async_client: AsyncClient, logged_in_token: str
):
    response = await async_client.post(
        "/posts/", json={}, headers={"Authorization": f"Bearer {logged_in_token}"}
    )
    assert response.status_code == 422  # Unprocessable Entity


@pytest.mark.anyio
async def test_get_all_posts(async_client: AsyncClient, created_post: dict):
    response = await async_client.get("/posts/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(post["id"] == created_post["id"] for post in data)


@pytest.mark.anyio
async def test_create_comment(
    async_client: AsyncClient,
    created_post: dict,
    registered_user: dict,
    logged_in_token: str,
):
    response = await async_client.post(
        "/posts/comment",
        json={"post_id": created_post["id"], "body": "This is a comment."},
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["body"] == "This is a comment."
    assert data["user_id"] == registered_user["id"]
    assert data["post_id"] == created_post["id"]
    assert "id" in data


@pytest.mark.anyio
async def test_create_comment_invalid_post(
    async_client: AsyncClient, logged_in_token: str
):
    response = await async_client.post(
        "/posts/comment",
        json={"post_id": 9999, "body": "This comment should fail."},
        headers={"Authorization": f"Bearer {logged_in_token}"},
    )
    assert response.status_code == 404  # Not Found


@pytest.mark.anyio
async def test_get_comments_for_post(
    async_client: AsyncClient, created_post: dict, created_comment: dict
):
    response = await async_client.get(f"/posts/{created_post['id']}/comments")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    print(data)
    assert any(comment["id"] == created_comment["id"] for comment in data)
