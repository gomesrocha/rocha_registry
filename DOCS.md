# Rocha Registry Documentation

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

## ⚙️ Configuration

The registry is configured using environment variables. You can set them in a `.env` file in the root of the project.

| Variable                      | Description                               | Default Value                               |
| ----------------------------- | ----------------------------------------- | ------------------------------------------- |
| `DATABASE_URL`                | The connection URL for the PostgreSQL database. | `postgresql://postgres:postgres@db:5432/registry` |
| `REDIS_URL`                   | The connection URL for the Redis server.      | `redis://redis:6379/0`                      |
| `MINIO_ENDPOINT`              | The endpoint for the MinIO S3 storage.      | `minio:9000`                                |
| `MINIO_ACCESS_KEY`            | The access key for MinIO.                 | `minioadmin`                                |
| `MINIO_SECRET_KEY`            | The secret key for MinIO.                 | `minioadmin`                                |
| `MINIO_BUCKET`                | The name of the bucket to store blobs in.   | `registry`                                  |
| `SECRET_KEY`                  | The secret key for signing JWTs.          | `your-secret-key-here`                      |
| `ALGORITHM`                   | The algorithm to use for signing JWTs.    | `HS256`                                     |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | The expiry time for access tokens in minutes. | `30`                                        |

---

## 📖 API Reference

The API is compatible with the Docker Registry HTTP API V2 and is served under the `/v2/` prefix.

### Authentication API

The registry uses a custom JWT-based authentication system.

#### `POST /v2/register`

Registers a new user.

-   **Request Body**:
    -   `username` (string): The desired username.
    -   `password` (string): The desired password.
-   **Responses**:
    -   `200 OK`: Returns a JWT access token.
    -   `400 Bad Request`: If the username is already registered.

#### `POST /v2/token`

Logs in a user and returns a JWT access token.

-   **Request Body** (`x-www-form-urlencoded`):
    -   `username` (string): The username.
    -   `password` (string): The password.
-   **Responses**:
    -   `200 OK`: Returns a JWT access token.
    -   `401 Unauthorized`: If the credentials are invalid.

### Blob API

Endpoints for managing image layers (blobs).

#### `POST /v2/{name}/blobs/uploads/`

Starts a blob upload session.

-   **Path Parameters**:
    -   `name` (string): The repository name.
-   **Responses**:
    -   `202 Accepted`: Returns a `Location` header with the upload URL and a `Docker-Upload-UUID` header with the upload session ID.

#### `PATCH /v2/{name}/blobs/uploads/{upload_id}`

Uploads a chunk of a blob.

-   **Path Parameters**:
    -   `name` (string): The repository name.
    -   `upload_id` (string): The upload session ID.
-   **Request Body**: The raw blob data.
-   **Responses**:
    -   `202 Accepted`: Returns a `Location` header pointing to the blob's final location.

#### `PUT /v2/{name}/blobs/uploads/{upload_id}`

Completes a blob upload.

-   **Path Parameters**:
    -   `name` (string): The repository name.
    -   `upload_id` (string): The upload session ID.
-   **Query Parameters**:
    -   `digest` (string): The digest of the blob (e.g., `sha256:...`).
-   **Request Body**: The raw blob data.
-   **Responses**:
    -   `201 Created`: Returns a `Location` header pointing to the blob and a `Docker-Content-Digest` header.

#### `GET /v2/{name}/blobs/{digest}`

Retrieves a blob.

-   **Path Parameters**:
    -   `name` (string): The repository name.
    -   `digest` (string): The blob's digest.
-   **Responses**:
    -   `200 OK`: Returns the raw blob data.
    -   `404 Not Found`: If the blob does not exist.

#### `HEAD /v2/{name}/blobs/{digest}`

Checks if a blob exists.

-   **Path Parameters**:
    -   `name` (string): The repository name.
    -   `digest` (string): The blob's digest.
-   **Responses**:
    -   `200 OK`: Returns headers with blob metadata (`Content-Length`, `Docker-Content-Digest`).
    -   `404 Not Found`: If the blob does not exist.

### Manifest API

Endpoints for managing image manifests.

#### `PUT /v2/{name}/manifests/{reference}`

Uploads an image manifest.

-   **Path Parameters**:
    -   `name` (string): The repository name.
    -   `reference` (string): The manifest reference (tag or digest).
-   **Request Body**: The manifest JSON.
-   **Responses**:
    -   `201 Created`: Returns a `Location` header and a `Docker-Content-Digest` header.
    -   `500 Internal Server Error`: If the manifest could not be saved.

#### `HEAD /v2/{name}/manifests/{reference}`

Checks if a manifest exists.

-   **Path Parameters**:
    -   `name` (string): The repository name.
    -   `reference` (string): The manifest reference.
-   **Responses**:
    -   `200 OK`: If the manifest exists.
    -   `404 Not Found`: If the manifest does not exist.

> **Note**: The `GET /v2/{name}/manifests/{reference}` endpoint to retrieve a manifest is not implemented in the current version. This means you can push images but cannot pull them using a standard Docker client.

---

## 🚀 Usage

### Authenticating

Before you can use the Docker client with the registry, you need to register a user and get an access token.

#### 1. Register a User

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"username": "myuser", "password": "mypassword"}' \
  http://localhost:5000/v2/register
```

This will return an access token. You don't need to save this initial token, as it's just a confirmation of registration.

#### 2. Log in with Docker

Because the registry uses a custom authentication flow, `docker login` requires the username and password to be passed directly.

```bash
docker login localhost:5000 -u myuser -p mypassword
```

**Note**: This command will fail because the `/v2/token` endpoint expects a standard OAuth2 password grant request, not the basic authentication that `docker login` sends. To work around this, you would typically configure your Docker client to use a credential helper that can handle the custom token exchange, or you would perform a manual login.

**Manual Login (for pushing/pulling)**

To manually authenticate for a `docker push` or `docker pull`, you would first get a token:

```bash
TOKEN=$(curl -s -X POST -d "username=myuser&password=mypassword" http://localhost:5000/v2/token | jq -r .access_token)
```

Then, you would use this token in the `Authorization` header for your requests. However, the Docker client does not directly support this. The recommended way to use this registry is via tools that can script the authentication process, or by implementing a proper credential helper.

### Pushing an Image

Once authenticated (assuming a working login method), you can tag and push an image.

```bash
# Tag an existing image
docker tag my-image:latest localhost:5000/my-repo/my-image:latest

# Push the image
docker push localhost:5000/my-repo/my-image:latest
```

### Pulling an Image

As noted in the API Reference, pulling images is not currently possible due to the missing `GET /v2/{name}/manifests/{reference}` endpoint.
