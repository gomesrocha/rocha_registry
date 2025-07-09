from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel
from app.api import blobs, manifests, auth
from app.db import engine
import os

app = FastAPI(title="OCI Registry", version="0.1.0")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)


app.include_router(auth.router, prefix="/v2", tags=["Auth"])
app.include_router(blobs.router, prefix="/v2", tags=["Blobs"])
app.include_router(manifests.router, prefix="/v2", tags=["Manifests"])

@app.get("/v2/")
async def root():
    return {"message": "OCI Registry API V2"}