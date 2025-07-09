# app/services/manifest_service.py
from minio import Minio
from sqlmodel import Session
from app.models.manifest import Manifest
from io import BytesIO  
import hashlib

class ManifestService:
    def __init__(self, session: Session, minio_client: Minio):
        self.session = session
        self.minio = minio_client
        self.bucket = "registry"
        
        
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        try:
            if not self.minio.bucket_exists(self.bucket):
                self.minio.make_bucket(self.bucket)
        except Exception as e:
            print(f"Bucket verification error: {e}")
    
    async def save_manifest(self, name: str, reference: str, data: bytes, content_type: str, digest: str):
        
        data_io = BytesIO(data)
        
        
        self.minio.put_object(
            self.bucket,
            f"manifests/{digest}",
            data_io,
            length=len(data),
            content_type=content_type
        )
        
        
        manifest = Manifest(
            name=name,
            reference=reference,
            digest=digest,
            content_type=content_type,
            size=len(data)
        )
        self.session.add(manifest)
        self.session.commit()
    
    async def manifest_exists(self, name: str, reference: str) -> bool:
        manifest = self.session.query(Manifest).filter(
            Manifest.name == name,
            Manifest.reference == reference
        ).first()
        return manifest is not None