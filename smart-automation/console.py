from __future__ import annotations
from dataclasses import dataclass, field
from playwright.async_api import Page

@dataclass
class ConsoleIssue:
    type: str; text: str; location: str = ''

@dataclass
class ConsoleMonitor:
    issues: list[ConsoleIssue] = field(default_factory=list)
    keywords: tuple[str, ...] = ('react error','next.js','hydration','referenceerror','typeerror','unhandled promise','cors','failed fetch')

    def attach(self, page: Page) -> None:
        page.on('console', self._console)
        page.on('pageerror', lambda exc: self.issues.append(ConsoleIssue('pageerror', str(exc))))

    def _console(self, msg) -> None:
        text = msg.text
        if msg.type in {'error','warning'} or any(k in text.lower() for k in self.keywords):
            self.issues.append(ConsoleIssue(msg.type, text, str(msg.location)))
