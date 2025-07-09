# app/dependencies.py
from fastapi import Depends
from app.db import get_session
from redis import Redis
from minio import Minio
from app.services.blob_service import BlobService
from app.services.manifest_service import ManifestService
from app.config import settings
from sqlmodel import Session

# Configurações do Redis e MinIO
redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=False)

minio_client = Minio(
    settings.MINIO_ENDPOINT,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=False
)

def get_blob_service(session: Session = Depends(get_session)):
    return BlobService(session=session, redis=redis_client, minio_client=minio_client)

def get_manifest_service(session: Session = Depends(get_session)):
    return ManifestService(session=session, minio_client=minio_client)