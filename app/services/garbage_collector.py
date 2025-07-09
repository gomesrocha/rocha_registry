from sqlmodel import Session
from minio import Minio
from datetime import datetime, timedelta
import concurrent.futures
from app.models.blob import Blob
from app.models.manifest import Manifest
import time

class GarbageCollector:
    def __init__(self, session: Session, minio_client: Minio):
        self.session = session
        self.minio = minio_client
        self.bucket = "registry"
    
    def mark_unreferenced_blobs(self):
        
        referenced_blobs = set()
        
        
        manifests = self.session.query(Manifest).all()
        for manifest in manifests:
            config_blob = manifest.config_blob_digest
            referenced_blobs.add(config_blob)
            
            for layer in manifest.layers:
                referenced_blobs.add(layer.blob_digest)
        
       
        manifest_lists = self.session.query(ManifestList).all()
        for ml in manifest_lists:
            for entry in ml.manifests:
                manifest = self.session.query(Manifest).filter(Manifest.digest == entry.manifest_digest).first()
                if manifest:
                    referenced_blobs.add(manifest.config_blob_digest)
                    for layer in manifest.layers:
                        referenced_blobs.add(layer.blob_digest)
        
        
        all_blobs = self.session.query(Blob).all()
        for blob in all_blobs:
            if blob.digest not in referenced_blobs:
                blob.unreferenced = True
                blob.marked_unreferenced_at = datetime.utcnow()
        
        self.session.commit()
    
    def delete_marked_blobs(self, older_than_days: int = 7):
        cutoff = datetime.utcnow() - timedelta(days=older_than_days)
        
        
        blobs_to_delete = self.session.query(Blob).filter(
            Blob.unreferenced == True,
            Blob.marked_unreferenced_at <= cutoff
        ).all()
        
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for blob in blobs_to_delete:
                futures.append(executor.submit(self._delete_blob, blob))
            
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"Error deleting blob: {e}")
        
        self.session.commit()
    
    def _delete_blob(self, blob: Blob):
        try:

            self.minio.remove_object(self.bucket, blob.digest)
            
            
            self.session.delete(blob)
        except Exception as e:
            print(f"Error deleting blob {blob.digest}: {e}")
            raise