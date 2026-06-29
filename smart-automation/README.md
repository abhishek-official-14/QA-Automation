# Smart End-to-End Automation Framework

Enterprise-grade Playwright/Python framework for automatically testing EaseMyTools utility pages from `sitemap.xml` without hardcoded tool names.

## Capabilities

- Parses sitemap indexes and URL sets.
- Visits every URL with retry support and concurrent workers.
- Detects page inventory from DOM elements: textareas, inputs, selects, checkboxes, radios, uploads, canvas, media, tables, SVG, iframes, dropzones, and contenteditable regions.
- Classifies pages using DOM text and controls into text, image, video, audio, PDF, JSON, CSV, XML, converter, generator, calculator, color, QR, hash, encoding, developer, SEO, category, and landing pages.
- Generates text data and files at runtime, including images, PDF, TXT, CSV, JSON, XML, ZIP, DOCX, MP3, MP4, and WAV.
- Performs smart interaction with fields, dropdowns, radios, checkboxes, uploads, and action buttons.
- Captures network errors, console errors, broken resources, downloads, traces, videos, and screenshots.
- Measures load time, DOM ready, TTFB, FCP, LCP, CLS, and INP where browser support exposes the metric.
- Checks SEO metadata, headings, alt text, canonical links, OpenGraph, Twitter, and structured data.
- Runs axe-core accessibility checks and calculates a score.
- Produces HTML, CSV, and JSON reports.

## Installation

```bash
cd smart-automation
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

## Run

```bash
python engine.py
```

Limit pages during smoke runs:

```bash
python engine.py --limit 10
```

## Reports and Artifacts

Artifacts are written under `artifacts/`:

- `reports/report.html`
- `reports/report.csv`
- `reports/report.json`
- `screenshots/`
- `downloads/`
- `videos/`
- `traces/`
- `logs/framework.log`

## Configuration

Edit `config.py` to change the base URL, sitemap URL, browser, concurrency, retry count, timeouts, viewports, and artifact locations.
