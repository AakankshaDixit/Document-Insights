import pytest
from httpx import AsyncClient
from uuid import UUID
from app.main import app


pytestmark = pytest.mark.asyncio

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        yield ac


def valid_payload(user_id="user_123", content="This is a sample document for testing"):
    return {
        "user_id": user_id,
        "title": "Test Document",
        "content": content,
    }


async def test_submit_document_success(client):
    response = await client.post("/documents", json=valid_payload())

    assert response.status_code == 201

    body = response.json()

    assert "id" in body
    assert UUID(body["id"])
    assert body["user_id"] == "user_123"
    assert body["title"] == "Test Document"
    assert body["status"] in ["queued", "completed"]


async def test_submit_document_validation_failure(client):
    response = await client.post(
        "/documents",
        json={
            "user_id": "",
            "title": "",
            "content": ""
        },
    )

    assert response.status_code == 422


async def test_submit_document_rate_limit(client):
    user_id = "rate_limit_user"

    # Max allowed = 3
    for i in range(3):
        res = await client.post(
            "/documents",
            json=valid_payload(
                user_id=user_id,
                content=f"content {i}"
            ),
        )
        assert res.status_code == 201

    # 4th should fail
    fourth = await client.post(
        "/documents",
        json=valid_payload(
            user_id=user_id,
            content="extra content"
        ),
    )

    assert fourth.status_code == 429
    assert fourth.json()["detail"] == "Rate limit exceeded"


async def test_submit_document_cache_hit(client):
    payload = valid_payload(
        user_id="cache_user",
        content="duplicate content"
    )

    first = await client.post("/documents", json=payload)
    assert first.status_code == 201

    second = await client.post("/documents", json=payload)

    assert second.status_code == 201

    body = second.json()

    # Cached duplicate should likely be completed immediately
    assert body["status"] in ["completed", "queued"]


async def test_get_document_success(client):
    create = await client.post("/documents", json=valid_payload())
    doc_id = create.json()["id"]

    response = await client.get(f"/documents/{doc_id}")

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == doc_id
    assert body["title"] == "Test Document"


async def test_get_document_not_found(client):
    fake_id = "11111111-1111-1111-1111-111111111111"

    response = await client.get(f"/documents/{fake_id}")

    assert response.status_code == 404

async def test_list_user_documents_success(client):
    user_id = "list_user"

    for i in range(5):
        await client.post(
            "/documents",
            json=valid_payload(
                user_id=user_id,
                content=f"doc {i}"
            ),
        )

    response = await client.get(
        f"/users/{user_id}/documents?page=1&page_size=2"
    )

    assert response.status_code == 200

    body = response.json()

    assert "documents" in body
    assert len(body["documents"]) == 2
    assert body["page"] == 1
    assert body["page_size"] == 2
    assert body["total"] >= 5


async def test_list_user_documents_status_filter(client):
    user_id = "status_user"

    await client.post(
        "/documents",
        json=valid_payload(
            user_id=user_id,
            content="status content"
        ),
    )

    response = await client.get(
        f"/users/{user_id}/documents?status=queued"
    )

    assert response.status_code == 200

    body = response.json()

    for doc in body["documents"]:
        assert doc["status"] == "queued"


async def test_health_check(client):
    response = await client.get("/health")

    assert response.status_code in [200, 503]

    body = response.json()

    assert "status" in body
