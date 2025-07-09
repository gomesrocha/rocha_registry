from fastapi import APIRouter, Depends, HTTPException, UploadFile, Header, Query, Request
import hashlib
from fastapi import UploadFile, Query
from fastapi.responses import Response
from app.services.blob_service import BlobService
from app.dependencies import get_blob_service
import uuid

router = APIRouter()

@router.post("/{name:path}/blobs/uploads/")
async def start_blob_upload(name: str, blob_service: BlobService = Depends(get_blob_service)):
    upload_id = str(uuid.uuid4())
    blob_service.create_upload_session(upload_id)
    return Response(
        status_code=202,
        headers={
            "Location": f"/v2/{name}/blobs/uploads/{upload_id}",
            "Range": "0-0",
            "Docker-Upload-UUID": upload_id
        }
    )


@router.put("/{name:path}/blobs/uploads/{upload_id}")
async def commit_blob_upload(
    name: str,
    upload_id: str,
    request: Request,  
    digest: str = Query(...),
    blob_service: BlobService = Depends(get_blob_service)
):
    data = await request.body()  

    blob_service.save_blob(digest, data)

    return Response(
        status_code=201,
        headers={
            "Location": f"/v2/{name}/blobs/{digest}",
            "Docker-Content-Digest": digest,
            "Content-Length": "0"
        }
    )



@router.patch("/{name:path}/blobs/uploads/{upload_id}")
async def upload_blob_chunk(
    name: str,
    upload_id: str,
    file: UploadFile,
    content_range: str = Header(None),
    blob_service: BlobService = Depends(get_blob_service)
):
    data = await file.read()
    blob_digest = await blob_service.upload_chunk(upload_id, data, content_range)
    
    return Response(
        status_code=202,
        headers={
            "Location": f"/v2/{name}/blobs/{blob_digest}",
            "Content-Length": "0",
            "Docker-Content-Digest": blob_digest
        }
    )


@router.get("/{name:path}/blobs/{digest}")
async def get_blob(
    name: str,
    digest: str,
    blob_service: BlobService = Depends(get_blob_service)
):
    blob_data = await blob_service.get_blob(digest)
    if not blob_data:
        raise HTTPException(status_code=404, detail="Blob not found")
    
    return Response(
        content=blob_data["data"],
        media_type=blob_data["media_type"]
    )


@router.head("/{name:path}/blobs/{digest}")
async def head_blob(
    name: str, 
    digest: str, 
    blob_service: BlobService = Depends(get_blob_service)
):
    # Verifica se o blob existe
    try:
        blob_info = await blob_service.get_blob_info(digest)
        if not blob_info:
            raise HTTPException(status_code=404)
        
        return Response(
            status_code=200,
            headers={
                "Content-Length": str(blob_info["size"]),
                "Docker-Content-Digest": digest,
                "Content-Type": blob_info["media_type"]
            }
        )
    except Exception as e:
        raise HTTPException(status_code=404)