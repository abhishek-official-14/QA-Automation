from __future__ import annotations
import re
from pathlib import Path
from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError
from config import FrameworkConfig
from detector import PageProfile
from test_data import TestDataFactory

class SmartExecutor:
    def __init__(self, config: FrameworkConfig, data: TestDataFactory) -> None:
        self.config = config; self.data = data; self.files = data.generate_files()

    async def interact(self, page: Page, profile: PageProfile) -> None:
        await self._fill_text(page); await self._select_options(page); await self._toggle(page); await self._upload(page, profile); await self._click_actions(page)

    async def _fill_text(self, page: Page) -> None:
        fields = page.locator('textarea, input:not([type=hidden]):not([type=file]):not([type=checkbox]):not([type=radio]):not([type=submit]):not([type=button]), [contenteditable=true]')
        for i in range(await fields.count()):
            el = fields.nth(i)
            try:
                typ = await el.get_attribute('type'); name = ' '.join(filter(None, [await el.get_attribute('name'), await el.get_attribute('placeholder'), await el.get_attribute('aria-label')]))
                await el.fill(self.data.text_for(typ, name), timeout=self.config.action_timeout_ms)
            except Exception: continue

    async def _select_options(self, page: Page) -> None:
        selects = page.locator('select')
        for i in range(await selects.count()):
            try:
                values = await selects.nth(i).locator('option').evaluate_all('(ops) => ops.map(o => o.value).filter(Boolean)')
                if values: await selects.nth(i).select_option(values[0], timeout=self.config.action_timeout_ms)
            except Exception: continue

    async def _toggle(self, page: Page) -> None:
        for sel in ['input[type=checkbox]', 'input[type=radio]']:
            loc = page.locator(sel)
            for i in range(await loc.count()):
                try: await loc.nth(i).check(timeout=self.config.action_timeout_ms)
                except Exception: continue

    async def _upload(self, page: Page, profile: PageProfile) -> None:
        uploads = page.locator('input[type=file]')
        for i in range(await uploads.count()):
            accept = (await uploads.nth(i).get_attribute('accept') or '').lower()
            paths = self._files_for_accept(accept, profile.classification)
            try: await uploads.nth(i).set_input_files([str(p) for p in paths], timeout=self.config.action_timeout_ms)
            except Exception: continue

    def _files_for_accept(self, accept: str, classification: str) -> list[Path]:
        if 'image' in accept or classification == 'Image Tool': return [self.files['png']]
        if 'video' in accept or classification == 'Video Tool': return [self.files['mp4']]
        if 'audio' in accept or classification == 'Audio Tool': return [self.files['mp3']]
        if 'pdf' in accept or classification == 'PDF Tool': return [self.files['pdf']]
        if 'csv' in accept: return [self.files['csv']]
        if 'json' in accept: return [self.files['json']]
        return [self.files['txt']]

    async def _click_actions(self, page: Page) -> None:
        pattern = re.compile(self.config.click_button_pattern, re.I)
        buttons = page.get_by_role('button', name=pattern).or_(page.locator('input[type=submit],input[type=button]'))
        for i in range(min(await buttons.count(), 8)):
            try:
                async with page.expect_download(timeout=3000) as dl:
                    await buttons.nth(i).click(timeout=self.config.action_timeout_ms)
                await dl.value
            except PlaywrightTimeoutError: continue
            except Exception: continue
        try:
            await page.wait_for_load_state('networkidle', timeout=15000)
        except Exception:
            pass
