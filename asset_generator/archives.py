"""Archive asset generators."""
from __future__ import annotations

import zipfile

from .config import AssetGeneratorConfig
from .utils import AssetMetadata, cleanup_registry, ensure_dir, metadata_for, random_filename


class ArchiveGenerator:
    """Generates ZIP archives containing representative nested test files."""

    FORMATS = {"zip"}

    def __init__(self, config: AssetGeneratorConfig) -> None:
        self.config = config
        self.output_dir = ensure_dir(config.output_dir / "archives")
        if config.cleanup_on_exit:
            cleanup_registry.register_atexit()

    def generate(self, fmt: str = "zip", files: dict[str, bytes | str] | None = None) -> AssetMetadata:
        fmt = fmt.lower().lstrip(".")
        if fmt not in self.FORMATS:
            raise ValueError(f"Unsupported archive format: {fmt}")
        path = self.output_dir / random_filename(fmt, "archive")
        contents = files or {
            "README.txt": "Generated QA archive\n",
            "data/sample.json": '{"generated": true}',
            "nested/info.csv": "id,name\n1,archive\n",
        }
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
            for name, payload in contents.items():
                zf.writestr(name, payload)
        valid_zip = zipfile.is_zipfile(path)
        meta = metadata_for(path, "archive", fmt, {"entries": len(contents), "zipfile_valid": valid_zip})
        meta.valid = meta.valid and valid_zip
        if self.config.cleanup_on_exit:
            cleanup_registry.add(path)
        return meta
