import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.dependencies import get_manifest_service

client = TestClient(app)

@pytest.mark.anyio
async def test_put_manifest_success():
    mock_manifest_service = MagicMock()
    mock_manifest_service.save_manifest = AsyncMock()

    app.dependency_overrides[get_manifest_service] = lambda: mock_manifest_service

    manifest_data = b'{"key": "value"}'
    response = client.put(
        "/v2/test/repo/manifests/latest",
        content=manifest_data,
        headers={"Content-Type": "application/vnd.docker.distribution.manifest.v2+json"}
    )

    assert response.status_code == 201
    assert "Docker-Content-Digest" in response.headers
    assert "Location" in response.headers

    app.dependency_overrides = {}

@pytest.mark.anyio
async def test_head_manifest_success():
    mock_manifest_service = MagicMock()
    mock_manifest_service.manifest_exists = AsyncMock(return_value=True)

    app.dependency_overrides[get_manifest_service] = lambda: mock_manifest_service

    response = client.head("/v2/test/repo/manifests/latest")

    assert response.status_code == 200

    app.dependency_overrides = {}

@pytest.mark.anyio
async def test_head_manifest_not_found():
    mock_manifest_service = MagicMock()
    mock_manifest_service.manifest_exists = AsyncMock(return_value=False)

    app.dependency_overrides[get_manifest_service] = lambda: mock_manifest_service

    response = client.head("/v2/test/repo/manifests/nonexistent")

    assert response.status_code == 404

    app.dependency_overrides = {}
