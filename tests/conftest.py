import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.dependencies import get_blob_service, get_manifest_service, get_session
from unittest.mock import MagicMock

@pytest.fixture(scope="module")
def client():
    def get_session_override():
        return MagicMock()

    def get_blob_service_override():
        return MagicMock()

    def get_manifest_service_override():
        return MagicMock()

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_blob_service] = get_blob_service_override
    app.dependency_overrides[get_manifest_service] = get_manifest_service_override

    # Remove the startup event handler to prevent it from running during tests
    app.router.on_startup = []

    with TestClient(app) as c:
        yield c

    app.dependency_overrides = {}
