"""Artifact storage — local filesystem or MinIO (S3-compatible)."""
from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from pathlib import Path

from app.core.config import PROJECT_ROOT, settings


class ArtifactStorage(ABC):
    @abstractmethod
    def put(self, key: str, data: bytes, content_type: str) -> str: ...

    @abstractmethod
    def get(self, key: str) -> bytes: ...

    @abstractmethod
    def backend_name(self) -> str: ...


class LocalArtifactStorage(ArtifactStorage):
    def __init__(self, root: Path | None = None) -> None:
        self.root = root or (PROJECT_ROOT / "backend" / "artifacts")
        self.root.mkdir(parents=True, exist_ok=True)

    def put(self, key: str, data: bytes, content_type: str) -> str:
        path = self.root / key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return key

    def get(self, key: str) -> bytes:
        return (self.root / key).read_bytes()

    def backend_name(self) -> str:
        return "local"


class MinioArtifactStorage(ArtifactStorage):
    def __init__(self) -> None:
        from minio import Minio

        endpoint = settings.minio_endpoint.replace("http://", "").replace(
            "https://", ""
        )
        secure = settings.minio_endpoint.startswith("https://")
        self._client = Minio(
            endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=secure,
        )
        self._bucket = settings.minio_bucket
        if not self._client.bucket_exists(self._bucket):
            self._client.make_bucket(self._bucket)

    def put(self, key: str, data: bytes, content_type: str) -> str:
        from io import BytesIO

        self._client.put_object(
            self._bucket,
            key,
            BytesIO(data),
            length=len(data),
            content_type=content_type,
        )
        return key

    def get(self, key: str) -> bytes:
        resp = self._client.get_object(self._bucket, key)
        try:
            return resp.read()
        finally:
            resp.close()
            resp.release_conn()

    def backend_name(self) -> str:
        return "minio"


def get_artifact_storage() -> ArtifactStorage:
    if settings.minio_endpoint and settings.minio_access_key:
        return MinioArtifactStorage()
    return LocalArtifactStorage()


def new_artifact_key(filename: str) -> str:
    ext = Path(filename).suffix or ".bin"
    return f"onnx/{uuid.uuid4().hex}{ext}"
