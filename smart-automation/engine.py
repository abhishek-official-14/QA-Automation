from __future__ import annotations
import argparse, asyncio, logging
from dataclasses import asdict
from pathlib import Path
from playwright.async_api import async_playwright
from accessibility import AccessibilityAnalyzer
from config import CONFIG, FrameworkConfig
from console import ConsoleMonitor
from detector import SmartDetector
from downloads import DownloadManager
from executor import SmartExecutor
from network import NetworkMonitor
from performance import PerformanceAnalyzer
from report import PageResult, ReportBuilder
from screenshots import ScreenshotManager
from seo import SeoAnalyzer
from sitemap import SitemapParser
from test_data import TestDataFactory
from utils import setup_logging, slugify, suggested_fix
from validators import SmartValidator

class SmartAutomationEngine:
    def __init__(self, config: FrameworkConfig = CONFIG) -> None:
        self.config = config; self.config.ensure_dirs(); setup_logging(self.config.log_dir/'framework.log'); self.log = logging.getLogger(self.__class__.__name__)
        self.detector=SmartDetector(); self.perf=PerformanceAnalyzer(); self.seo=SeoAnalyzer(); self.a11y=AccessibilityAnalyzer(); self.validator=SmartValidator(); self.shots=ScreenshotManager(config.screenshot_dir)
        self.data=TestDataFactory(config.artifact_root/'generated-data'); self.executor=SmartExecutor(config,self.data)

    async def run(self, limit: int | None = None) -> list[PageResult]:
        urls = SitemapParser(self.config.sitemap_url).urls() or [self.config.base_url]
        if limit: urls = urls[:limit]
        sem = asyncio.Semaphore(self.config.max_workers)
        async with async_playwright() as p:
            browser = await getattr(p, self.config.browser).launch(headless=self.config.headless)
            tasks = [self._run_with_retry(browser, url, sem) for url in urls]
            results = await asyncio.gather(*tasks)
            await browser.close()
        ReportBuilder(self.config.report_dir).write(results)
        return results

    async def _run_with_retry(self, browser, url: str, sem: asyncio.Semaphore) -> PageResult:
        last: PageResult | None = None
        for attempt in range(1, self.config.retries + 1):
            async with sem:
                last = await self._run_page(browser, url, attempt)
            if last.status == 'PASSED': return last
        return last  # type: ignore[return-value]

    async def _run_page(self, browser, url: str, attempt: int) -> PageResult:
        viewport = self.config.viewports[0]; slug = slugify(url)
        downloads = DownloadManager(self.config.download_dir/slug)
        context = await browser.new_context(viewport={'width': viewport.width, 'height': viewport.height}, is_mobile=viewport.is_mobile, record_video_dir=str(self.config.video_dir), accept_downloads=True, user_agent=self.config.user_agent)
        await context.tracing.start(screenshots=True, snapshots=True, sources=True)
        page = await context.new_page(); page.set_default_timeout(self.config.action_timeout_ms); page.set_default_navigation_timeout(self.config.navigation_timeout_ms)
        net=NetworkMonitor(); con=ConsoleMonitor(); net.attach(page); con.attach(page)
        page.on('download', lambda d: asyncio.create_task(downloads.save(d)))
        trace_path = self.config.trace_dir / f'{slug}-attempt{attempt}.zip'; video_path=''; screenshot=''; failures=[]; profile=None
        try:
            await page.goto(url, wait_until='domcontentloaded')
            await page.wait_for_load_state('networkidle', timeout=15000)
            profile = await self.detector.detect(page)
            before = (await page.locator('body').inner_text(timeout=5000))[:10000]
            screenshot = await self.shots.capture(page, url, 'before', viewport.name)
            await self.executor.interact(page, profile)
            screenshot = await self.shots.capture(page, url, 'after', viewport.name)
            for vp in self.config.viewports[1:]:
                await page.set_viewport_size({'width': vp.width, 'height': vp.height})
                await self.shots.capture(page, url, 'responsive', vp.name)
            perf = await self.perf.collect(page); seo = await self.seo.analyze(page); a11y = await self.a11y.analyze(page)
            validation = await self.validator.validate(page, profile, before, len(downloads.records))
            failures.extend(validation.failures + seo.issues + [f"Accessibility violations: {len(a11y.violations)}"] if a11y.violations else validation.failures + seo.issues)
            failures.extend([i.message for i in net.issues if i.status and i.status >= 500])
            failures.extend([i.text for i in con.issues if i.type in {'error','pageerror'}])
            status = 'PASSED' if not failures else 'FAILED'; severity = 'none' if not failures else ('critical' if any('500' in f or 'critical' in f.lower() for f in failures) else 'major')
            return PageResult(url,status,severity,perf.load_time_ms,asdict(perf),asdict(seo),asdict(a11y),[asdict(i) for i in net.issues],[asdict(i) for i in con.issues],[asdict(d) for d in downloads.records],[asdict(i) for i in net.issues if i.status and i.status>=400],screenshot,video_path,str(trace_path),' | '.join(failures),suggested_fix(failures),profile.classification)
        except Exception as exc:
            failures=[str(exc)]
            return PageResult(url,'FAILED','critical',0,{}, {}, {}, [asdict(i) for i in net.issues],[asdict(i) for i in con.issues],[asdict(d) for d in downloads.records],[],screenshot,video_path,str(trace_path),str(exc),suggested_fix(failures),profile.classification if profile else 'Unknown')
        finally:
            try: await context.tracing.stop(path=trace_path)
            except Exception: pass
            try:
                if page.video: video_path = await page.video.path()
            except Exception: pass
            await context.close()

def main() -> None:
    parser=argparse.ArgumentParser(); parser.add_argument('--limit', type=int); args=parser.parse_args()
    asyncio.run(SmartAutomationEngine().run(limit=args.limit))

if __name__ == '__main__': main()
