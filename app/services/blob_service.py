from minio import Minio
from minio.error import S3Error
from redis import Redis
from sqlmodel import Session
from app.models.blob import Blob
import hashlib
from datetime import datetime
import os
from io import BytesIO
import logging



logger = logging.getLogger(__name__)


class BlobService:
    def __init__(self, session: Session, redis: Redis, minio_client: Minio):
        self.session = session
        self.redis = redis
        self.minio = minio_client
        self.bucket = os.getenv("MINIO_BUCKET", "registry")
        
        try:
            if not self.minio.bucket_exists(self.bucket):
                self.minio.make_bucket(self.bucket)
        except S3Error as e:
            print(f"Error creating bucket: {e}")

    def create_upload_session(self, upload_id: str):
        """Function to create an upload session in Redis"""
        self.redis.hset(f"upload:{upload_id}", "chunks", "")
        self.redis.expire(f"upload:{upload_id}", 3600)  

    async def upload_chunk(self, upload_id: str, data: bytes, content_range: str = None) -> str:

        logger.info(f"UPLOAD chunl for {upload_id} and content '{content_range:}'")   

        digest = f"sha256:{hashlib.sha256(data).hexdigest()}"
        
        
        try:
            self.minio.put_object(
                self.bucket,
                digest,
                data,
                length=len(data)
            )
        except S3Error as e:
            print(f"Error uploading blob: {e}")
            raise
        
        
        blob = Blob(
            digest=digest,
            size=len(data),
            media_type="application/octet-stream"
        )
        self.session.add(blob)
        self.session.commit()
        
        return digest
    

    def save_blob(self, digest: str, data: bytes):
        self.minio.put_object(
            self.bucket,
            digest,
            BytesIO(data), 
            length=len(data)
        )
        blob = Blob(
            digest=digest,
            size=len(data),
            media_type="application/octet-stream"
        )
        self.session.add(blob)
        self.session.commit()


    async def get_blob_info(self, digest: str) -> dict:
        """Asynchronous function to obtain information about the blob, without downloading the content"""
        
        if self.redis.exists(f"blob_meta:{digest}"):
            size = self.redis.hget(f"blob_meta:{digest}", "size")
            media_type = self.redis.hget(f"blob_meta:{digest}", "media_type")
            if size and media_type:
                return {
                    "size": int(size),
                    "media_type": media_type,
                    "digest": digest
                }
        
        
        blob = self.session.query(Blob).filter(Blob.digest == digest).first()
        if blob:
           
            self.redis.hset(f"blob_meta:{digest}", "size", str(blob.size))
            self.redis.hset(f"blob_meta:{digest}", "media_type", blob.media_type)
            return {
                "size": blob.size,
                "media_type": blob.media_type,
                "digest": digest
            }
        
        
        try:
            stat = self.minio.stat_object(self.bucket, digest)
            return {
                "size": stat.size,
                "media_type": "application/octet-stream",
                "digest": digest
            }
        except S3Error:
            return None
        
    async def get_blob(self, digest: str) -> dict:
        """Recupera um blob do MinIO"""
        try:
            cached_blob = self.redis.get(f"blob:{digest}")
            if cached_blob:
                media_type = self.redis.hget(f"blob_meta:{digest}", "media_type") or "application/octet-stream"
                return {
                    "data": cached_blob,
                    "media_type": media_type,
                    "size": len(cached_blob),
                    "digest": digest  
                }

            
            response = self.minio.get_object(self.bucket, digest)
            data = response.read()

            
            self.redis.set(f"blob:{digest}", data, ex=3600)

            blob = self.session.query(Blob).filter(Blob.digest == digest).first()
            media_type = blob.media_type if blob else "application/octet-stream"
            if blob:
                self.redis.hset(f"blob_meta:{digest}", "media_type", media_type)

            return {
                "data": data,
                "media_type": media_type,
                "size": len(data),
                "digest": digest 
            }
        except S3Error as e:
            print(f"Error getting blob: {e}")
            return None
