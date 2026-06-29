"""Runtime data and file generation. No external fixtures required."""
from __future__ import annotations

import base64
import csv
import io
import json
import math
import uuid
import wave
import zipfile
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, tostring

import numpy as np
from faker import Faker
from PIL import Image, ImageDraw

fake = Faker()


class TestDataFactory:
    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def text_for(self, input_type: str | None, name: str = "") -> str:
        key = f"{input_type or ''} {name}".lower()
        if "email" in key: return fake.email()
        if "password" in key: return fake.password(length=14)
        if "url" in key: return fake.url()
        if "phone" in key or "tel" in key: return fake.phone_number()
        if "address" in key: return fake.address()
        if "name" in key: return fake.name()
        if "date" in key: return fake.date()
        if "time" in key: return fake.time()
        if "color" in key: return fake.hex_color()
        if "number" in key or input_type == "number": return str(fake.random_int(1, 999))
        if "json" in key: return self.json_text()
        if "xml" in key: return self.xml_text()
        if "csv" in key: return self.csv_text()
        if "sql" in key: return "SELECT id, name FROM users WHERE active = TRUE;"
        if "html" in key: return "<article><h1>QA</h1><p>Automation</p></article>"
        if "markdown" in key or "md" in key: return "# Heading\n\n- Smart\n- Automation"
        if "base64" in key: return base64.b64encode(b"smart automation").decode()
        if "jwt" in key: return "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjMifQ.signature"
        if "uuid" in key: return str(uuid.uuid4())
        return fake.paragraph(nb_sentences=4)

    def json_text(self) -> str:
        return json.dumps({"id": str(uuid.uuid4()), "name": fake.name(), "active": True}, indent=2)

    def xml_text(self) -> str:
        root = Element("tool"); SubElement(root, "name").text = "Smart QA"; SubElement(root, "status").text = "active"
        return tostring(root, encoding="unicode")

    def csv_text(self) -> str:
        buf = io.StringIO(); writer = csv.writer(buf); writer.writerow(["id", "name"]); writer.writerow([1, fake.name()]); return buf.getvalue()

    def generate_files(self) -> dict[str, Path]:
        files = {
            "png": self._image("png", "PNG"), "jpg": self._image("jpg", "JPEG"),
            "webp": self._image("webp", "WEBP"), "gif": self._image("gif", "GIF"),
            "svg": self._write("sample.svg", '<svg xmlns="http://www.w3.org/2000/svg" width="120" height="80"><rect width="120" height="80" fill="#3b82f6"/></svg>'),
            "pdf": self._minimal_pdf(), "txt": self._write("sample.txt", fake.text()),
            "csv": self._write("sample.csv", self.csv_text()), "json": self._write("sample.json", self.json_text()),
            "xml": self._write("sample.xml", self.xml_text()), "docx": self._docx(),
            "zip": self._zip(), "mp3": self._write("sample.mp3", b"ID3\x03\x00\x00\x00\x00\x00\x21"),
            "mp4": self._write("sample.mp4", b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00mp42isom"),
            "wav": self._wav(),
        }
        return files

    def _write(self, name: str, data: str | bytes) -> Path:
        path = self.output_dir / name
        path.write_text(data, encoding="utf-8") if isinstance(data, str) else path.write_bytes(data)
        return path

    def _image(self, ext: str, fmt: str) -> Path:
        path = self.output_dir / f"sample.{ext}"
        img = Image.new("RGB", (160, 100), "white"); ImageDraw.Draw(img).rectangle((20, 20, 140, 80), fill="#22c55e")
        img.save(path, fmt); return path

    def _minimal_pdf(self) -> Path:
        return self._write("sample.pdf", b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Count 0>>endobj\ntrailer<</Root 1 0 R>>\n%%EOF")

    def _zip(self) -> Path:
        path = self.output_dir / "sample.zip"
        with zipfile.ZipFile(path, "w") as zf: zf.writestr("sample.txt", "smart automation")
        return path

    def _docx(self) -> Path:
        path = self.output_dir / "sample.docx"
        with zipfile.ZipFile(path, "w") as zf:
            zf.writestr("[Content_Types].xml", "<Types xmlns='http://schemas.openxmlformats.org/package/2006/content-types'/>")
            zf.writestr("word/document.xml", "<w:document xmlns:w='http://schemas.openxmlformats.org/wordprocessingml/2006/main'><w:body><w:p/></w:body></w:document>")
        return path

    def _wav(self) -> Path:
        path = self.output_dir / "sample.wav"; rate = 8000
        samples = (np.sin(2 * math.pi * 440 * np.arange(rate) / rate) * 32767).astype(np.int16)
        with wave.open(str(path), "wb") as wav: wav.setnchannels(1); wav.setsampwidth(2); wav.setframerate(rate); wav.writeframes(samples.tobytes())
        return path
