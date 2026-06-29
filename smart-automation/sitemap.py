from __future__ import annotations
import logging
from bs4 import BeautifulSoup
import requests

class SitemapParser:
    def __init__(self, sitemap_url: str) -> None: self.sitemap_url = sitemap_url; self.log = logging.getLogger(self.__class__.__name__)
    def urls(self) -> list[str]:
        seen: set[str] = set(); pending = [self.sitemap_url]
        while pending:
            url = pending.pop(0)
            try:
                r = requests.get(url, timeout=30); r.raise_for_status()
            except requests.RequestException as exc:
                self.log.error('Unable to fetch sitemap %s: %s', url, exc); continue
            soup = BeautifulSoup(r.text, 'xml')
            sitemaps = [loc.text.strip() for loc in soup.find_all('loc') if loc.parent and loc.parent.name == 'sitemap']
            if sitemaps: pending.extend(sitemaps); continue
            for loc in soup.find_all('loc'):
                value = loc.text.strip()
                if value and value not in seen: seen.add(value)
        return sorted(seen)
