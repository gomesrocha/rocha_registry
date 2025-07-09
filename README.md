# Rocha Registry

Um OCI Registry compatível com a especificação [OCI Distribution Spac](https://github.com/opencontainers/distribution-spec) e compatível com o Docker Registry, implementado com **FastAPI**, **MinIO**, **PostgreSQL** e **Redis**.

> 🚀 Projeto feito para uso interno seguro e escalável, com armazenamento distribuído e cache inteligente.

---

## 🧩 Arquitetura

- **FastAPI**: API HTTP principal (implementação da spec do Docker Registry).
- **PostgreSQL**: Armazenamento de metadados (blobs, manifests, repositórios).
- **MinIO**: Armazenamento dos blobs de imagens.
- **Redis**: Cache para blobs acessados frequentemente.
- **Docker Compose**: Orquestra os serviços para facilitar o deploy.

---

## 📦 Funcionalidades

- Upload e download de blobs (layers).
- Armazenamento de manifests.
- Suporte a múltiplos repositórios.
- Cache de blobs com Redis.
- Armazenamento de blobs no MinIO (compatível com S3).
- Compatível com `docker push` e `docker pull`.

---

## 🚀 Como subir localmente

1. **Clone o repositório**:

```bash
git clone https://github.com/seu-usuario/rocha_registry.git
cd rocha_registry
