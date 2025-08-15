import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.dependencies import get_blob_service

client = TestClient(app)

@pytest.mark.anyio
async def test_get_blob_success():
    mock_blob_service = MagicMock()
    mock_blob_service.get_blob = AsyncMock(return_value={
        "data": b"some blob data",
        "media_type": "application/octet-stream"
    })

    app.dependency_overrides[get_blob_service] = lambda: mock_blob_service

    response = client.get("/v2/test/repo/blobs/sha256:12345")

    assert response.status_code == 200
    assert response.content == b"some blob data"

    app.dependency_overrides = {}

@pytest.mark.anyio
async def test_get_blob_not_found():
    mock_blob_service = MagicMock()
    mock_blob_service.get_blob = AsyncMock(return_value=None)

    app.dependency_overrides[get_blob_service] = lambda: mock_blob_service

    response = client.get("/v2/test/repo/blobs/sha256:nonexistent")

    assert response.status_code == 404

    app.dependency_overrides = {}

@pytest.mark.anyio
async def test_head_blob_success():
    mock_blob_service = MagicMock()
    mock_blob_service.get_blob_info = AsyncMock(return_value={
        "size": 123,
        "media_type": "application/octet-stream"
    })

    app.dependency_overrides[get_blob_service] = lambda: mock_blob_service

    response = client.head("/v2/test/repo/blobs/sha256:12345")

    assert response.status_code == 200
    assert response.headers["Content-Length"] == "123"
    assert response.headers["Docker-Content-Digest"] == "sha256:12345"
    assert response.headers["Content-Type"] == "application/octet-stream"

    app.dependency_overrides = {}

@pytest.mark.anyio
async def test_head_blob_not_found():
    mock_blob_service = MagicMock()
    mock_blob_service.get_blob_info = AsyncMock(return_value=None)

    app.dependency_overrides[get_blob_service] = lambda: mock_blob_service

    response = client.head("/v2/test/repo/blobs/sha256:nonexistent")

    assert response.status_code == 404

    app.dependency_overrides = {}

def test_start_blob_upload():
    mock_blob_service = MagicMock()
    app.dependency_overrides[get_blob_service] = lambda: mock_blob_service

    response = client.post("/v2/test/repo/blobs/uploads/")

    assert response.status_code == 202
    assert "Location" in response.headers
    assert "Docker-Upload-UUID" in response.headers

    app.dependency_overrides = {}

@pytest.mark.anyio
async def test_upload_blob_chunk():
    mock_blob_service = MagicMock()
    mock_blob_service.upload_chunk = AsyncMock(return_value="sha256:12345")

    app.dependency_overrides[get_blob_service] = lambda: mock_blob_service

    response = client.patch(
        "/v2/test/repo/blobs/uploads/some-uuid",
        files={"file": b"chunk data"},
        headers={"Content-Range": "0-9"}
    )

    assert response.status_code == 202
    assert "Location" in response.headers
    assert "Docker-Content-Digest" in response.headers

    app.dependency_overrides = {}

def test_commit_blob_upload():
    mock_blob_service = MagicMock()
    app.dependency_overrides[get_blob_service] = lambda: mock_blob_service

    response = client.put(
        "/v2/test/repo/blobs/uploads/some-uuid?digest=sha256:12345",
        content=b"blob data"
    )

    assert response.status_code == 201
    assert "Location" in response.headers
    assert "Docker-Content-Digest" in response.headers

    app.dependency_overrides = {}
