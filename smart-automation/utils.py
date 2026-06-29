"""Shared utilities."""
from __future__ import annotations

import hashlib
import logging
import re
from pathlib import Path
from urllib.parse import urlparse


def slugify(value: str, max_len: int = 90) -> str:
    parsed = urlparse(value)
    raw = f"{parsed.netloc}{parsed.path}" or value
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "-", raw).strip("-")
    if len(slug) > max_len:
        digest = hashlib.sha1(value.encode()).hexdigest()[:10]
        slug = f"{slug[:max_len-11]}-{digest}"
    return slug or "page"


def setup_logging(log_file: Path) -> None:
    log_file.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        handlers=[logging.FileHandler(log_file, encoding="utf-8"), logging.StreamHandler()],
        force=True,
    )


def suggested_fix(failures: list[str]) -> str:
    if not failures:
        return "No action required."
    joined = " ".join(failures).lower()
    if "404" in joined or "broken" in joined:
        return "Fix missing asset/page references or update links to valid resources."
    if "console" in joined or "referenceerror" in joined or "typeerror" in joined:
        return "Review browser console stack traces and add regression coverage for failing JavaScript."
    if "accessibility" in joined:
        return "Resolve axe violations, focusing on critical and serious issues first."
    if "seo" in joined:
        return "Add missing metadata, canonical tags, headings, alt text, and structured data."
    return "Inspect the captured screenshot, trace, console, and network logs for root cause."
