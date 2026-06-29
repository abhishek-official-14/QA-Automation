from __future__ import annotations
from dataclasses import dataclass, field
from playwright.async_api import Page

@dataclass
class SeoResult:
    score: int; issues: list[str] = field(default_factory=list); details: dict = field(default_factory=dict)

class SeoAnalyzer:
    async def analyze(self, page: Page) -> SeoResult:
        d = await page.evaluate("""
        () => ({title: document.title, description: document.querySelector('meta[name="description"]')?.content || '',
          canonical: document.querySelector('link[rel="canonical"]')?.href || '', robots: document.querySelector('meta[name="robots"]')?.content || '',
          og: document.querySelectorAll('meta[property^="og:"]').length, twitter: document.querySelectorAll('meta[name^="twitter:"]').length,
          schema: document.querySelectorAll('script[type="application/ld+json"]').length, h1: document.querySelectorAll('h1').length,
          h2: document.querySelectorAll('h2').length, imgs: document.querySelectorAll('img').length,
          missingAlt: Array.from(document.querySelectorAll('img')).filter(i => !i.alt).length})
        """)
        issues=[]
        if not d['title']: issues.append('Missing title')
        if not d['description']: issues.append('Missing meta description')
        if not d['canonical']: issues.append('Missing canonical')
        if d['h1'] != 1: issues.append(f'Expected exactly one H1, found {d["h1"]}')
        if d['missingAlt']: issues.append(f'{d["missingAlt"]} images missing alt attributes')
        if not d['schema']: issues.append('Missing Schema.org structured data')
        return SeoResult(max(0, 100 - len(issues)*12), issues, d)
