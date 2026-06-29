from __future__ import annotations
import csv, json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from html import escape

@dataclass
class PageResult:
    url: str; status: str; severity: str; load_time_ms: float; performance: dict; seo: dict; accessibility: dict
    network_errors: list[dict] = field(default_factory=list); console_errors: list[dict] = field(default_factory=list)
    downloaded_files: list[dict] = field(default_factory=list); broken_resources: list[dict] = field(default_factory=list)
    screenshot_path: str = ''; video_path: str = ''; trace_path: str = ''; failure_reason: str = ''; suggested_fix: str = ''; classification: str = ''

class ReportBuilder:
    def __init__(self, report_dir: Path) -> None: self.report_dir = report_dir; self.report_dir.mkdir(parents=True, exist_ok=True)
    def write(self, results: list[PageResult]) -> None:
        data = [asdict(r) for r in results]
        (self.report_dir / 'report.json').write_text(json.dumps(data, indent=2, default=str), encoding='utf-8')
        with (self.report_dir / 'report.csv').open('w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=list(data[0].keys()) if data else ['url','status'])
            writer.writeheader(); writer.writerows(data)
        rows = ''.join(f"<tr><td>{escape(r.url)}</td><td class='{r.status.lower()}'>{r.status}</td><td>{r.severity}</td><td>{r.load_time_ms:.0f}</td><td>{escape(r.classification)}</td><td>{escape(r.failure_reason)}</td><td>{escape(r.suggested_fix)}</td></tr>" for r in results)
        html = f"""<!doctype html><html><head><meta charset='utf-8'><title>Smart Automation Report</title><style>body{{font-family:Arial;margin:2rem}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #ddd;padding:8px}}.passed{{color:green}}.failed{{color:#b91c1c}}.warning{{color:#a16207}}</style></head><body><h1>Smart Automation Dashboard</h1><p>Total: {len(results)}</p><table><thead><tr><th>URL</th><th>Status</th><th>Severity</th><th>Load Time</th><th>Type</th><th>Failure</th><th>Suggested Fix</th></tr></thead><tbody>{rows}</tbody></table></body></html>"""
        (self.report_dir / 'report.html').write_text(html, encoding='utf-8')
