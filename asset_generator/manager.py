"""High-level facade for all asset generators."""
from __future__ import annotations

import random
from pathlib import Path
from typing import Literal

from .archives import ArchiveGenerator
from .audio import AudioGenerator
from .config import AssetGeneratorConfig
from .datafiles import DataFileGenerator
from .documents import DocumentGenerator
from .images import ImageGenerator
from .office import OfficeGenerator
from .utils import AssetMetadata, cleanup_registry
from .videos import VideoGenerator

AssetKind = Literal["image", "video", "audio", "document", "office", "data", "archive"]


class AssetManager:
    """Enterprise facade used by QA frameworks to create disposable test assets."""

    def __init__(self, output_dir: str | Path | None = None, config: AssetGeneratorConfig | None = None, cleanup_on_exit: bool | None = None) -> None:
        self.config = config or AssetGeneratorConfig(output_dir=Path(output_dir or "generated_assets"))
        if output_dir is not None:
            self.config.output_dir = Path(output_dir)
            self.config.output_dir.mkdir(parents=True, exist_ok=True)
        if cleanup_on_exit is not None:
            self.config.cleanup_on_exit = cleanup_on_exit
        random.seed(self.config.random_seed)
        self.images = ImageGenerator(self.config)
        self.videos = VideoGenerator(self.config)
        self.audio = AudioGenerator(self.config)
        self.documents = DocumentGenerator(self.config)
        self.office = OfficeGenerator(self.config)
        self.datafiles = DataFileGenerator(self.config)
        self.archives = ArchiveGenerator(self.config)

    def generate_image(self, fmt: str = "png", variant: str = "standard", **kwargs) -> AssetMetadata:
        return self.images.generate(fmt=fmt, variant=variant, **kwargs)

    def generate_video(self, fmt: str = "mp4", orientation: str = "landscape", **kwargs) -> AssetMetadata:
        return self.videos.generate(fmt=fmt, orientation=orientation, **kwargs)

    def generate_audio(self, fmt: str = "wav", **kwargs) -> AssetMetadata:
        return self.audio.generate(fmt=fmt, **kwargs)

    def generate_document(self, fmt: str = "pdf", **kwargs) -> AssetMetadata:
        return self.documents.generate(fmt=fmt, **kwargs)

    def generate_office(self, fmt: str = "docx", **kwargs) -> AssetMetadata:
        return self.office.generate(fmt=fmt, **kwargs)

    def generate_data_file(self, fmt: str = "json", **kwargs) -> AssetMetadata:
        return self.datafiles.generate(fmt=fmt, **kwargs)

    def generate_archive(self, fmt: str = "zip", **kwargs) -> AssetMetadata:
        return self.archives.generate(fmt=fmt, **kwargs)

    def generate_any(self, kind: AssetKind | None = None) -> AssetMetadata:
        selected = kind or random.choice(["image", "video", "audio", "document", "office", "data", "archive"])
        return {
            "image": self.generate_image,
            "video": self.generate_video,
            "audio": self.generate_audio,
            "document": self.generate_document,
            "office": self.generate_office,
            "data": self.generate_data_file,
            "archive": self.generate_archive,
        }[selected]()

    def cleanup(self) -> None:
        cleanup_registry.cleanup()
