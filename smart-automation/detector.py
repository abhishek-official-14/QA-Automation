"""DOM-driven page and tool detection."""
from __future__ import annotations

from dataclasses import dataclass, field
from playwright.async_api import Page


@dataclass
class ElementInventory:
    textareas: int = 0; inputs: int = 0; selects: int = 0; checkboxes: int = 0; radios: int = 0
    file_uploads: int = 0; canvas: int = 0; video: int = 0; audio: int = 0; tables: int = 0
    svg: int = 0; iframes: int = 0; dropzones: int = 0; contenteditable: int = 0; buttons: int = 0
    forms: int = 0; images: int = 0; code_blocks: int = 0; color_inputs: int = 0; numeric_inputs: int = 0

    @property
    def interactive_count(self) -> int:
        return sum([self.textareas, self.inputs, self.selects, self.checkboxes, self.radios,
                    self.file_uploads, self.contenteditable, self.buttons, self.forms])


@dataclass
class PageProfile:
    url: str
    title: str
    classification: str
    inventory: ElementInventory
    signals: list[str] = field(default_factory=list)


class SmartDetector:
    async def detect(self, page: Page) -> PageProfile:
        data = await page.evaluate("""
        () => {
          const count = s => document.querySelectorAll(s).length;
          const txt = (document.body?.innerText || '').toLowerCase();
          const labels = Array.from(document.querySelectorAll('label,button,input,textarea,select,h1,h2,[aria-label]'))
            .map(e => `${e.innerText || ''} ${e.placeholder || ''} ${e.name || ''} ${e.id || ''} ${e.getAttribute('aria-label') || ''}`).join(' ').toLowerCase();
          return {
            title: document.title || '', text: `${txt} ${labels}`.slice(0, 20000),
            inv: {
              textareas: count('textarea'), inputs: count('input:not([type=hidden])'), selects: count('select'),
              checkboxes: count('input[type=checkbox]'), radios: count('input[type=radio]'), file_uploads: count('input[type=file]'),
              canvas: count('canvas'), video: count('video'), audio: count('audio'), tables: count('table'), svg: count('svg'),
              iframes: count('iframe'), dropzones: count('[class*=dropzone i],[id*=dropzone i],[data-dropzone],.dz-clickable'),
              contenteditable: count('[contenteditable=true]'), buttons: count('button,input[type=button],input[type=submit],a[role=button]'),
              forms: count('form'), images: count('img'), code_blocks: count('pre,code'), color_inputs: count('input[type=color]'),
              numeric_inputs: count('input[type=number],input[inputmode=numeric]')
            }
          }
        }""")
        inv = ElementInventory(**data["inv"])
        classification, signals = self._classify(inv, data["text"])
        return PageProfile(page.url, data["title"], classification, inv, signals)

    def _classify(self, inv: ElementInventory, text: str) -> tuple[str, list[str]]:
        signals: list[str] = []
        def has(*words: str) -> bool:
            found = any(w in text for w in words)
            if found: signals.extend([w for w in words if w in text][:2])
            return found
        if inv.file_uploads and (inv.images or inv.canvas or has('image', 'png', 'jpg', 'webp')): return 'Image Tool', signals
        if inv.video or has('video', 'mp4'): return 'Video Tool', signals
        if inv.audio or has('audio', 'mp3', 'wav'): return 'Audio Tool', signals
        if has('pdf'): return 'PDF Tool', signals
        if has('json') or inv.code_blocks: return 'JSON Tool', signals
        if has('csv'): return 'CSV Tool', signals
        if has('xml'): return 'XML Tool', signals
        if inv.color_inputs or has('color', 'hex'): return 'Color Tool', signals
        if inv.svg and has('qr', 'barcode'): return 'QR Tool', signals
        if has('hash', 'sha', 'md5'): return 'Hash Tool', signals
        if has('base64', 'encode', 'decode', 'url encode'): return 'Encoding Tool', signals
        if inv.numeric_inputs >= 2 or has('calculate', 'calculator'): return 'Calculator', signals
        if has('seo', 'meta', 'canonical'): return 'SEO Tool', signals
        if has('developer', 'formatter', 'minify', 'beautify'): return 'Developer Tool', signals
        if has('convert', 'converter', 'conversion'): return 'Converter', signals
        if has('generate', 'generator', 'create'): return 'Generator', signals
        if inv.textareas or inv.contenteditable: return 'Text Tool', signals
        if inv.interactive_count == 0 and (inv.images or inv.svg): return 'Static Category Page', signals
        return ('Landing Page' if inv.interactive_count < 2 else 'Developer Tool'), signals
