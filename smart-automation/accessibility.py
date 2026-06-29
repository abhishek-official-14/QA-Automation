from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from playwright.async_api import Page

@dataclass
class AccessibilityResult:
    score: int; violations: list[dict] = field(default_factory=list)

class AccessibilityAnalyzer:
    async def analyze(self, page: Page) -> AccessibilityResult:
        axe_path = Path(__file__).resolve().parent / 'node_modules' / 'axe-core' / 'axe.min.js'
        if axe_path.exists():
            await page.add_script_tag(path=str(axe_path))
        else:
            await page.add_script_tag(url='https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.10.2/axe.min.js')
        result = await page.evaluate('async () => await axe.run(document)')
        violations = result.get('violations', [])
        penalty = sum({'minor': 2, 'moderate': 5, 'serious': 10, 'critical': 20}.get(v.get('impact'), 5) for v in violations)
        return AccessibilityResult(max(0, 100 - penalty), violations)
