from __future__ import annotations
from dataclasses import dataclass
from playwright.async_api import Page

@dataclass
class PerformanceMetrics:
    load_time_ms: float = 0; dom_ready_ms: float = 0; ttfb_ms: float = 0; lcp_ms: float | None = None; cls: float | None = None; fcp_ms: float | None = None; inp_ms: float | None = None

class PerformanceAnalyzer:
    async def collect(self, page: Page) -> PerformanceMetrics:
        data = await page.evaluate("""
        () => {
          const nav = performance.getEntriesByType('navigation')[0];
          const paints = Object.fromEntries(performance.getEntriesByType('paint').map(p => [p.name, p.startTime]));
          const lcp = performance.getEntriesByType('largest-contentful-paint').pop()?.startTime ?? null;
          let cls = 0; performance.getEntriesByType('layout-shift').forEach(e => { if (!e.hadRecentInput) cls += e.value; });
          const ev = performance.getEntriesByType('event').sort((a,b)=>(b.duration||0)-(a.duration||0))[0];
          return nav ? {load: nav.loadEventEnd-nav.startTime, dom: nav.domContentLoadedEventEnd-nav.startTime,
            ttfb: nav.responseStart-nav.requestStart, fcp: paints['first-contentful-paint'] ?? null, lcp, cls, inp: ev?.duration ?? null} : {};
        }""")
        return PerformanceMetrics(data.get('load',0), data.get('dom',0), data.get('ttfb',0), data.get('lcp'), data.get('cls'), data.get('fcp'), data.get('inp'))
