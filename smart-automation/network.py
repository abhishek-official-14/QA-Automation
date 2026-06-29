from __future__ import annotations
from dataclasses import dataclass, field
from playwright.async_api import Page, Response

@dataclass
class NetworkIssue:
    url: str; status: int | None; resource_type: str; message: str

@dataclass
class NetworkMonitor:
    issues: list[NetworkIssue] = field(default_factory=list)
    responses: list[dict] = field(default_factory=list)

    def attach(self, page: Page) -> None:
        page.on('response', self._on_response)
        page.on('requestfailed', lambda req: self.issues.append(NetworkIssue(req.url, None, req.resource_type, req.failure or 'request failed')))

    async def _on_response(self, response: Response) -> None:
        req = response.request; status = response.status
        self.responses.append({'url': response.url, 'status': status, 'type': req.resource_type})
        if status >= 400:
            self.issues.append(NetworkIssue(response.url, status, req.resource_type, f'HTTP {status}'))
