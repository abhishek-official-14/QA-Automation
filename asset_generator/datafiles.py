"""Structured data file generators."""
from __future__ import annotations

import csv
import json
import random
from xml.etree.ElementTree import Element, SubElement, tostring

from .config import AssetGeneratorConfig
from .utils import AssetMetadata, cleanup_registry, ensure_dir, metadata_for, random_filename


class DataFileGenerator:
    """Generates CSV, JSON, XML, YAML, and SQL test data files."""

    FORMATS = {"csv", "json", "xml", "yaml", "yml", "sql"}

    def __init__(self, config: AssetGeneratorConfig) -> None:
        self.config = config
        self.output_dir = ensure_dir(config.output_dir / "data")
        if config.cleanup_on_exit:
            cleanup_registry.register_atexit()

    def generate(self, fmt: str = "json", rows: int | None = None) -> AssetMetadata:
        fmt = fmt.lower().lstrip(".")
        if fmt not in self.FORMATS:
            raise ValueError(f"Unsupported data file format: {fmt}")
        rows = rows or random.randint(3, 20)
        extension = "yaml" if fmt == "yml" else fmt
        path = self.output_dir / random_filename(extension, "data")
        records = [{"id": i, "name": f"user_{i}", "active": i % 2 == 0} for i in range(1, rows + 1)]
        if extension == "json":
            path.write_text(json.dumps(records, indent=2), encoding="utf-8")
        elif extension == "csv":
            with path.open("w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["id", "name", "active"]); writer.writeheader(); writer.writerows(records)
        elif extension == "xml":
            root = Element("records")
            for rec in records:
                node = SubElement(root, "record")
                for key, value in rec.items(): SubElement(node, key).text = str(value)
            path.write_text(tostring(root, encoding="unicode"), encoding="utf-8")
        elif extension == "yaml":
            path.write_text("\n".join(f"- id: {r['id']}\n  name: {r['name']}\n  active: {str(r['active']).lower()}" for r in records), encoding="utf-8")
        else:
            values = ",\n".join(f"({r['id']}, '{r['name']}', {1 if r['active'] else 0})" for r in records)
            path.write_text("CREATE TABLE qa_users (id INTEGER, name TEXT, active INTEGER);\nINSERT INTO qa_users VALUES\n" + values + ";\n", encoding="utf-8")
        if self.config.cleanup_on_exit:
            cleanup_registry.add(path)
        return metadata_for(path, "data", extension, {"rows": rows})
