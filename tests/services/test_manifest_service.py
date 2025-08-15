import pytest
from unittest.mock import MagicMock, AsyncMock
from app.services.manifest_service import ManifestService
from app.models.manifest import Manifest

@pytest.fixture
def mock_session():
    return MagicMock()

@pytest.fixture
def mock_minio():
    minio_mock = MagicMock()
    minio_mock.bucket_exists.return_value = True
    return minio_mock

@pytest.mark.anyio
async def test_save_manifest(mock_session, mock_minio):
    service = ManifestService(session=mock_session, minio_client=mock_minio)
    await service.save_manifest(
        name="test/repo",
        reference="latest",
        data=b'{"key": "value"}',
        content_type="application/json",
        digest="sha256:123"
    )
    mock_minio.put_object.assert_called_once()
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()

@pytest.mark.anyio
async def test_manifest_exists_true(mock_session, mock_minio):
    mock_session.query.return_value.filter.return_value.first.return_value = Manifest()
    service = ManifestService(session=mock_session, minio_client=mock_minio)
    exists = await service.manifest_exists("test/repo", "latest")
    assert exists is True

@pytest.mark.anyio
async def test_manifest_exists_false(mock_session, mock_minio):
    mock_session.query.return_value.filter.return_value.first.return_value = None
    service = ManifestService(session=mock_session, minio_client=mock_minio)
    exists = await service.manifest_exists("test/repo", "latest")
    assert exists is False
