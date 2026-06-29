"""Configuration objects for the asset generator package."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class AssetGeneratorConfig:
    """Runtime configuration shared by all generators.

    Attributes:
        output_dir: Root directory where generated assets are written.
        cleanup_on_exit: Register generated files for process-exit cleanup.
        min_width: Minimum random image/video width.
        max_width: Maximum random image/video width.
        min_height: Minimum random image/video height.
        max_height: Maximum random image/video height.
        min_duration_seconds: Minimum random audio/video duration.
        max_duration_seconds: Maximum random audio/video duration.
        random_seed: Optional deterministic seed for reproducible assets.
    """

    output_dir: Path = Path("generated_assets")
    cleanup_on_exit: bool = False
    min_width: int = 64
    max_width: int = 1920
    min_height: int = 64
    max_height: int = 1080
    min_duration_seconds: float = 0.5
    max_duration_seconds: float = 3.0
    random_seed: int | None = None
    metadata: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.output_dir = Path(self.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        if self.min_width <= 0 or self.min_height <= 0:
            raise ValueError("Minimum dimensions must be positive")
        if self.max_width < self.min_width or self.max_height < self.min_height:
            raise ValueError("Maximum dimensions must be greater than or equal to minimum dimensions")
        if self.max_duration_seconds < self.min_duration_seconds or self.min_duration_seconds <= 0:
            raise ValueError("Duration range must be positive and ordered")


DEFAULT_CONFIG = AssetGeneratorConfig()
