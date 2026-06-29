"""Video asset generators."""
from __future__ import annotations

import random
from pathlib import Path

import cv2
import numpy as np

from .config import AssetGeneratorConfig
from .utils import AssetMetadata, cleanup_registry, ensure_dir, metadata_for, random_filename


class VideoGenerator:
    """Generates short synthetic videos in common upload-test formats."""

    FORMATS = {"mp4", "avi", "webm", "mov"}

    def __init__(self, config: AssetGeneratorConfig) -> None:
        self.config = config
        self.output_dir = ensure_dir(config.output_dir / "videos")
        if config.cleanup_on_exit:
            cleanup_registry.register_atexit()

    def generate(self, fmt: str = "mp4", orientation: str = "landscape", duration_seconds: float | None = None, fps: int = 12) -> AssetMetadata:
        fmt = fmt.lower().lstrip(".")
        if fmt not in self.FORMATS:
            raise ValueError(f"Unsupported video format: {fmt}")
        width, height = self._dimensions(orientation)
        duration = duration_seconds or random.uniform(self.config.min_duration_seconds, self.config.max_duration_seconds)
        path = self.output_dir / random_filename(fmt, f"video_{orientation}")
        self._write_video(path, fmt, width, height, duration, fps)
        if self.config.cleanup_on_exit:
            cleanup_registry.add(path)
        return metadata_for(path, "video", fmt, {"width": width, "height": height, "duration_seconds": round(duration, 3), "fps": fps, "orientation": orientation})

    def _dimensions(self, orientation: str) -> tuple[int, int]:
        return {"landscape": (640, 360), "portrait": (360, 640), "square": (480, 480)}.get(orientation, (640, 360))

    def _write_video(self, path: Path, fmt: str, width: int, height: int, duration: float, fps: int) -> None:
        fourcc_map = {"mp4": "mp4v", "avi": "XVID", "webm": "VP80", "mov": "mp4v"}
        writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*fourcc_map[fmt]), fps, (width, height))
        if not writer.isOpened():
            path.write_bytes(self._minimal_container(fmt))
            return
        frames = max(1, int(duration * fps))
        for idx in range(frames):
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            frame[:, :, 0] = (idx * 7) % 255
            frame[:, :, 1] = np.linspace(0, 255, width, dtype=np.uint8)
            frame[:, :, 2] = np.linspace(255, 0, height, dtype=np.uint8)[:, None]
            cv2.putText(frame, f"QA {fmt.upper()} {idx+1}/{frames}", (20, max(40, height // 2)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            writer.write(frame)
        writer.release()

    def _minimal_container(self, fmt: str) -> bytes:
        if fmt in {"mp4", "mov"}:
            return b"\x00\x00\x00\x18ftypisom\x00\x00\x02\x00isomiso2mp41\x00\x00\x00\x08free"
        if fmt == "webm":
            return b"\x1a\x45\xdf\xa3\x9fB\x86\x81\x01B\xf7\x81\x01B\xf2\x81\x04B\xf3\x81\x08"
        return b"RIFF\x24\x00\x00\x00AVI LIST\x10\x00\x00\x00hdrlavih"
