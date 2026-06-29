from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from playwright.async_api import Download

@dataclass
class DownloadRecord:
    suggested_filename: str; path: str; extension: str; size: int; valid: bool

class DownloadManager:
    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir; self.output_dir.mkdir(parents=True, exist_ok=True); self.records: list[DownloadRecord] = []

    async def save(self, download: Download) -> DownloadRecord:
        filename = download.suggested_filename or 'download.bin'
        target = self.output_dir / filename
        await download.save_as(target)
        rec = DownloadRecord(filename, str(target), target.suffix.lower(), target.stat().st_size, target.exists() and target.stat().st_size > 0)
        self.records.append(rec); return rec
