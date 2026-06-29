"""Configuration for the Smart E2E Automation Framework."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Viewport:
    name: str
    width: int
    height: int
    is_mobile: bool = False


@dataclass(frozen=True)
class FrameworkConfig:
    base_url: str = "https://www.easemytools.com"
    sitemap_url: str = "https://www.easemytools.com/sitemap.xml"
    headless: bool = True
    browser: str = "chromium"
    max_workers: int = 4
    retries: int = 3
    navigation_timeout_ms: int = 45_000
    action_timeout_ms: int = 10_000
    artifact_root: Path = Path(__file__).resolve().parent / "artifacts"
    report_dir: Path = artifact_root / "reports"
    screenshot_dir: Path = artifact_root / "screenshots"
    download_dir: Path = artifact_root / "downloads"
    video_dir: Path = artifact_root / "videos"
    trace_dir: Path = artifact_root / "traces"
    log_dir: Path = artifact_root / "logs"
    user_agent: str = "SmartAutomationBot/1.0 (+QA Automation)"
    viewports: tuple[Viewport, ...] = field(default_factory=lambda: (
        Viewport("desktop", 1440, 1000),
        Viewport("tablet", 768, 1024),
        Viewport("mobile", 390, 844, True),
    ))
    click_button_pattern: str = (
        "generate|convert|process|calculate|submit|run|create|download|encode|decode|"
        "compress|resize|format|minify|beautify|hash|copy|start|upload"
    )

    def ensure_dirs(self) -> None:
        for path in (self.report_dir, self.screenshot_dir, self.download_dir,
                     self.video_dir, self.trace_dir, self.log_dir):
            path.mkdir(parents=True, exist_ok=True)


CONFIG = FrameworkConfig()
