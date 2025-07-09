# app/api/manifests.py
from fastapi import APIRouter, Depends, Request, Response, HTTPException, Header
from app.services.manifest_service import ManifestService
from app.dependencies import get_manifest_service
import hashlib

router = APIRouter()

@router.put("/{name:path}/manifests/{reference}")
async def put_manifest(
    name: str,
    reference: str,
    request: Request,
    manifest_service: ManifestService = Depends(get_manifest_service),
    content_type: str = Header(
        default="application/vnd.docker.distribution.manifest.v2+json",
        alias="Content-Type"
    )
):
    try:
        # Lê o corpo da requisição
        manifest_data = await request.body()
        
        # Calcula o digest
        digest = f"sha256:{hashlib.sha256(manifest_data).hexdigest()}"
        
        # Salva o manifesto
        await manifest_service.save_manifest(
            name=name,
            reference=reference,
            data=manifest_data,
            content_type=content_type,
            digest=digest
        )
        
        return Response(
            status_code=201,
            headers={
                "Docker-Content-Digest": digest,
                "Location": f"/v2/{name}/manifests/{reference}"
            }
        )
    except Exception as e:
        print(f"Error saving manifest: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.head("/{name:path}/manifests/{reference}")
async def head_manifest(
    name: str,
    reference: str,
    manifest_service: ManifestService = Depends(get_manifest_service)
):
    exists = await manifest_service.manifest_exists(name, reference)
    if not exists:
        raise HTTPException(status_code=404)
    return Response(status_code=200)