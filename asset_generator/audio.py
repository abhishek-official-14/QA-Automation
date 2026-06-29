"""Audio asset generators."""
from __future__ import annotations

import math
import random
import wave

import numpy as np

from .config import AssetGeneratorConfig
from .utils import AssetMetadata, cleanup_registry, ensure_dir, metadata_for, random_filename


class AudioGenerator:
    """Generates deterministic synthetic audio files for upload and media tests."""

    FORMATS = {"wav", "mp3", "ogg", "flac"}

    def __init__(self, config: AssetGeneratorConfig) -> None:
        self.config = config
        self.output_dir = ensure_dir(config.output_dir / "audio")
        if config.cleanup_on_exit:
            cleanup_registry.register_atexit()

    def generate(self, fmt: str = "wav", duration_seconds: float | None = None, sample_rate: int = 44100) -> AssetMetadata:
        fmt = fmt.lower().lstrip(".")
        if fmt not in self.FORMATS:
            raise ValueError(f"Unsupported audio format: {fmt}")
        duration = duration_seconds or random.uniform(self.config.min_duration_seconds, self.config.max_duration_seconds)
        path = self.output_dir / random_filename(fmt, "audio")
        if fmt == "wav":
            self._wav(path, duration, sample_rate)
        elif fmt == "mp3":
            self._framed_binary(path, b"ID3\x04\x00\x00\x00\x00\x00\x21", duration, sample_rate)
        elif fmt == "ogg":
            self._framed_binary(path, b"OggS\x00\x02", duration, sample_rate)
        else:
            self._framed_binary(path, b"fLaC\x00\x00\x00\x22", duration, sample_rate)
        if self.config.cleanup_on_exit:
            cleanup_registry.add(path)
        return metadata_for(path, "audio", fmt, {"duration_seconds": round(duration, 3), "sample_rate": sample_rate})

    def _samples(self, duration: float, sample_rate: int) -> np.ndarray:
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        tone = 0.45 * np.sin(2 * math.pi * random.choice([220, 330, 440, 880]) * t)
        return (tone * 32767).astype(np.int16)

    def _wav(self, path, duration: float, sample_rate: int) -> None:
        samples = self._samples(duration, sample_rate)
        with wave.open(str(path), "wb") as wav_file:
            wav_file.setnchannels(1); wav_file.setsampwidth(2); wav_file.setframerate(sample_rate); wav_file.writeframes(samples.tobytes())

    def _framed_binary(self, path, header: bytes, duration: float, sample_rate: int) -> None:
        samples = self._samples(duration, min(sample_rate, 12000)).tobytes()
        path.write_bytes(header + samples[: max(2048, len(samples) // 8)])
