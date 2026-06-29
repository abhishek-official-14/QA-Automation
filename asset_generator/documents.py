"""Document asset generators."""
from __future__ import annotations

import random
from html import escape

from .config import AssetGeneratorConfig
from .utils import AssetMetadata, cleanup_registry, ensure_dir, metadata_for, random_filename


class DocumentGenerator:
    """Generates portable text and document files."""

    FORMATS = {"pdf", "txt", "html", "md", "markdown"}

    def __init__(self, config: AssetGeneratorConfig) -> None:
        self.config = config
        self.output_dir = ensure_dir(config.output_dir / "documents")
        if config.cleanup_on_exit:
            cleanup_registry.register_atexit()

    def generate(self, fmt: str = "pdf", title: str | None = None) -> AssetMetadata:
        fmt = fmt.lower().lstrip(".")
        if fmt not in self.FORMATS:
            raise ValueError(f"Unsupported document format: {fmt}")
        extension = "md" if fmt == "markdown" else fmt
        title = title or f"QA Document {random.randint(1000, 9999)}"
        path = self.output_dir / random_filename(extension, "document")
        if extension == "pdf":
            path.write_bytes(self._pdf(title))
        elif extension == "html":
            path.write_text(f"<!doctype html><html><head><title>{escape(title)}</title><meta name='generator' content='asset_generator'></head><body><h1>{escape(title)}</h1><p>Generated QA test document.</p></body></html>", encoding="utf-8")
        elif extension == "md":
            path.write_text(f"# {title}\n\n- Generated\n- QA automation\n- Markdown asset\n", encoding="utf-8")
        else:
            path.write_text(f"{title}\n\nGenerated QA automation text document.\n", encoding="utf-8")
        if self.config.cleanup_on_exit:
            cleanup_registry.add(path)
        return metadata_for(path, "document", extension, {"title": title})

    def _pdf(self, title: str) -> bytes:
        text = f"BT /F1 18 Tf 72 720 Td ({title[:60]}) Tj ET"
        stream = text.encode("latin-1", errors="ignore")
        objects = [
            b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj",
            b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj",
            b"3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]/Resources<</Font<</F1 4 0 R>>>>/Contents 5 0 R>>endobj",
            b"4 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj",
            b"5 0 obj<</Length " + str(len(stream)).encode() + b">>stream\n" + stream + b"\nendstream endobj",
        ]
        body = b"%PDF-1.4\n" + b"\n".join(objects) + b"\ntrailer<</Root 1 0 R>>\n%%EOF"
        return body
