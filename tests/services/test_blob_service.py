import pytest
from unittest.mock import MagicMock, AsyncMock
from app.services.blob_service import BlobService
from app.models.blob import Blob
from minio.error import S3Error
from io import BytesIO

@pytest.fixture
def mock_session():
    return MagicMock()

@pytest.fixture
def mock_redis():
    return MagicMock()

@pytest.fixture
def mock_minio():
    minio_mock = MagicMock()
    minio_mock.bucket_exists.return_value = True
    return minio_mock

def test_create_upload_session(mock_session, mock_redis, mock_minio):
    service = BlobService(session=mock_session, redis=mock_redis, minio_client=mock_minio)
    upload_id = "test-upload-id"
    service.create_upload_session(upload_id)
    mock_redis.hset.assert_called_once_with(f"upload:{upload_id}", "chunks", "")
    mock_redis.expire.assert_called_once_with(f"upload:{upload_id}", 3600)

@pytest.mark.anyio
async def test_upload_chunk(mock_session, mock_redis, mock_minio):
    service = BlobService(session=mock_session, redis=mock_redis, minio_client=mock_minio)
    upload_id = "test-upload-id"
    data = b"test-data"
    digest = await service.upload_chunk(upload_id, data)
    assert digest is not None
    mock_minio.put_object.assert_called_once()
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()

def test_save_blob(mock_session, mock_redis, mock_minio):
    service = BlobService(session=mock_session, redis=mock_redis, minio_client=mock_minio)
    digest = "sha256:123"
    data = b"test-data"
    service.save_blob(digest, data)
    mock_minio.put_object.assert_called_once()
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()

@pytest.mark.anyio
async def test_get_blob_info_from_redis(mock_session, mock_redis, mock_minio):
    mock_redis.exists.return_value = True
    mock_redis.hget.side_effect = ["123", "application/octet-stream"]
    service = BlobService(session=mock_session, redis=mock_redis, minio_client=mock_minio)
    info = await service.get_blob_info("sha256:123")
    assert info["size"] == 123
    assert info["media_type"] == "application/octet-stream"

@pytest.mark.anyio
async def test_get_blob_info_from_db(mock_session, mock_redis, mock_minio):
    mock_redis.exists.return_value = False
    mock_session.query.return_value.filter.return_value.first.return_value = Blob(digest="sha256:123", size=123, media_type="application/octet-stream")
    service = BlobService(session=mock_session, redis=mock_redis, minio_client=mock_minio)
    info = await service.get_blob_info("sha256:123")
    assert info["size"] == 123
    assert info["media_type"] == "application/octet-stream"

@pytest.mark.anyio
async def test_get_blob_info_from_minio(mock_session, mock_redis, mock_minio):
    mock_redis.exists.return_value = False
    mock_session.query.return_value.filter.return_value.first.return_value = None
    mock_minio.stat_object.return_value = MagicMock(size=123)
    service = BlobService(session=mock_session, redis=mock_redis, minio_client=mock_minio)
    info = await service.get_blob_info("sha256:123")
    assert info["size"] == 123
    assert info["media_type"] == "application/octet-stream"

@pytest.mark.anyio
async def test_get_blob_from_redis(mock_session, mock_redis, mock_minio):
    mock_redis.get.return_value = b"test-data"
    mock_redis.hget.return_value = "application/octet-stream"
    service = BlobService(session=mock_session, redis=mock_redis, minio_client=mock_minio)
    blob = await service.get_blob("sha256:123")
    assert blob["data"] == b"test-data"

@pytest.mark.anyio
async def test_get_blob_from_minio(mock_session, mock_redis, mock_minio):
    mock_redis.get.return_value = None
    mock_minio.get_object.return_value = MagicMock(read=lambda: b"test-data")
    mock_session.query.return_value.filter.return_value.first.return_value = Blob(digest="sha256:123", size=123, media_type="application/octet-stream")
    service = BlobService(session=mock_session, redis=mock_redis, minio_client=mock_minio)
    blob = await service.get_blob("sha256:123")
    assert blob["data"] == b"test-data"
