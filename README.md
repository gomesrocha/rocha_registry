# Rocha Registry

A lightweight, self-hosted container image registry compatible with the [OCI Distribution Spec](https://github.com/opencontainers/distribution-spec) and Docker Registry HTTP API V2.

Built with **FastAPI**, **MinIO**, **PostgreSQL**, and **Redis**, Rocha Registry is designed for secure, scalable, and distributed internal usage.

> 🚀 Ideal for private environments requiring efficient blob storage and intelligent caching.

---

## 🧩 Architecture

- **FastAPI**: Main HTTP API implementing the Docker Registry specification.
- **PostgreSQL**: Metadata storage (blobs, manifests, repositories).
- **MinIO**: Object storage for image layers (S3-compatible).
- **Redis**: In-memory caching for frequently accessed blobs.
- **Docker Compose**: Container orchestration for local development and deployment.

---

## 📦 Features

- Upload and download of blobs (image layers).
- Manifest storage and retrieval.
- Support for multiple repositories.
- Redis-powered caching for blobs.
- MinIO-based blob storage.
- Fully compatible with `docker pull` and `docker push`.

---

## 🚀 Getting Started (Local Setup)

1. **Clone the repository**:

```bash
git clone https://github.com/your-username/rocha_registry.git
cd rocha_registry

docker compose up --build -d

curl http://localhost:5000/v2/

```
