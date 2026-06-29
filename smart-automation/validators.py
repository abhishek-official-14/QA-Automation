from __future__ import annotations
from dataclasses import dataclass, field
from playwright.async_api import Page
from detector import PageProfile

@dataclass
class ValidationResult:
    passed: bool; failures: list[str] = field(default_factory=list); observations: list[str] = field(default_factory=list)

class SmartValidator:
    async def validate(self, page: Page, profile: PageProfile, before_text: str, downloads: int) -> ValidationResult:
        failures=[]; obs=[]
        after_text = (await page.locator('body').inner_text(timeout=5000))[:10000]
        inv = profile.inventory
        outputs = await page.locator('[class*=result i], [id*=result i], output, pre, code, table, canvas, svg, img, video, audio, [class*=output i]').count()
        if outputs > 0: obs.append(f'Output-like elements found: {outputs}')
        if after_text != before_text: obs.append('Page text changed after interaction')
        if downloads: obs.append(f'Downloads captured: {downloads}')
        if inv.canvas and not await self._canvas_has_pixels(page): failures.append('Canvas was present but appears empty')
        if inv.video and await page.locator('video').count() == 0: failures.append('Video not rendered')
        if inv.audio and await page.locator('audio').count() == 0: failures.append('Audio not rendered')
        if profile.classification not in {'Landing Page','Static Category Page'} and not (outputs or downloads or after_text != before_text):
            failures.append('No generated output, download, or visible content change detected')
        return ValidationResult(not failures, failures, obs)

    async def _canvas_has_pixels(self, page: Page) -> bool:
        return bool(await page.evaluate("""() => Array.from(document.querySelectorAll('canvas')).some(c => {try {return c.getContext('2d').getImageData(0,0,Math.min(c.width,20)||1,Math.min(c.height,20)||1).data.some(v=>v!==0)} catch(e){return true}})"""))
