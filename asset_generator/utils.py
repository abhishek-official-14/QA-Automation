"""Shared utilities for asset generation, validation, and cleanup."""
from __future__ import annotations

import atexit
import hashlib
import json
import mimetypes
import random
import shutil
import string
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


@dataclass(slots=True)
class AssetMetadata:
    """Metadata returned for every generated asset."""

    path: Path
    asset_type: str
    format: str
    checksum: str
    size_bytes: int
    valid: bool
    details: dict[str, object] = field(default_factory=dict)

    def as_dict(self) -> dict[str, object]:
        return {
            "path": str(self.path),
            "asset_type": self.asset_type,
            "format": self.format,
            "checksum": self.checksum,
            "size_bytes": self.size_bytes,
            "valid": self.valid,
            "details": self.details,
        }


class CleanupRegistry:
    """Tracks generated files and removes them on demand or at interpreter exit."""

    def __init__(self) -> None:
        self._paths: set[Path] = set()
        self._registered = False

    def add(self, path: Path) -> None:
        self._paths.add(path)

    def register_atexit(self) -> None:
        if not self._registered:
            atexit.register(self.cleanup)
            self._registered = True

    def cleanup(self) -> None:
        for path in sorted(self._paths, key=lambda p: len(p.parts), reverse=True):
            try:
                if path.is_file() or path.is_symlink():
                    path.unlink(missing_ok=True)
                elif path.is_dir():
                    shutil.rmtree(path, ignore_errors=True)
            except OSError:
                continue
        self._paths.clear()


cleanup_registry = CleanupRegistry()


def random_string(length: int = 12) -> str:
    alphabet = string.ascii_lowercase + string.digits
    return "".join(random.choice(alphabet) for _ in range(length))


def random_filename(extension: str, prefix: str = "asset") -> str:
    clean_ext = extension.lower().lstrip(".")
    return f"{prefix}_{random_string()}.{clean_ext}"


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def checksum(path: Path, algorithm: str = "sha256") -> str:
    h = hashlib.new(algorithm)
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def validate_non_empty(path: Path, allowed_extensions: Iterable[str] | None = None) -> bool:
    if not path.exists() or not path.is_file() or path.stat().st_size <= 0:
        return False
    if allowed_extensions is None:
        return True
    allowed = {ext.lower().lstrip(".") for ext in allowed_extensions}
    return path.suffix.lower().lstrip(".") in allowed


def metadata_for(path: Path, asset_type: str, fmt: str, details: dict[str, object] | None = None) -> AssetMetadata:
    valid = validate_non_empty(path, [fmt])
    return AssetMetadata(
        path=path,
        asset_type=asset_type,
        format=fmt.lower(),
        checksum=checksum(path) if path.exists() else "",
        size_bytes=path.stat().st_size if path.exists() else 0,
        valid=valid,
        details=details or {},
    )


def write_json(path: Path, payload: object) -> Path:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def guess_mime(path: Path) -> str:
    return mimetypes.guess_type(path.name)[0] or "application/octet-stream"
