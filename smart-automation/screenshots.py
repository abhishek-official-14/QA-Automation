from __future__ import annotations
from pathlib import Path
from playwright.async_api import Page
from utils import slugify

class ScreenshotManager:
    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir; self.base_dir.mkdir(parents=True, exist_ok=True)

    async def capture(self, page: Page, url: str, label: str, viewport: str) -> str:
        path = self.base_dir / f"{slugify(url)}-{viewport}-{label}.png"
        await page.screenshot(path=path, full_page=True)
        return str(path)
