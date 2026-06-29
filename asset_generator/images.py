"""Image asset generators."""
from __future__ import annotations

import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, PngImagePlugin

from .config import AssetGeneratorConfig
from .utils import AssetMetadata, cleanup_registry, ensure_dir, metadata_for, random_filename


class ImageGenerator:
    """Generates bitmap and SVG image assets for UI, upload, and conversion tests."""

    FORMATS = {"png", "jpg", "jpeg", "webp", "gif", "bmp", "tiff", "svg"}

    def __init__(self, config: AssetGeneratorConfig) -> None:
        self.config = config
        self.output_dir = ensure_dir(config.output_dir / "images")
        if config.cleanup_on_exit:
            cleanup_registry.register_atexit()

    def generate(self, fmt: str = "png", variant: str = "standard", width: int | None = None, height: int | None = None) -> AssetMetadata:
        fmt = fmt.lower().lstrip(".")
        if fmt not in self.FORMATS:
            raise ValueError(f"Unsupported image format: {fmt}")
        width, height = self._dimensions(variant, width, height)
        path = self.output_dir / random_filename(fmt, f"image_{variant}")
        if fmt == "svg":
            self._svg(path, width, height, variant)
        else:
            image = self._image(width, height, variant)
            save_format = "JPEG" if fmt in {"jpg", "jpeg"} else fmt.upper()
            if save_format == "JPG":
                save_format = "JPEG"
            params = {"format": save_format}
            if fmt == "png":
                pnginfo = PngImagePlugin.PngInfo(); pnginfo.add_text("generator", "asset_generator"); params["pnginfo"] = pnginfo
            image.save(path, **params)
        if self.config.cleanup_on_exit:
            cleanup_registry.add(path)
        return metadata_for(path, "image", fmt, {"width": width, "height": height, "variant": variant})

    def _dimensions(self, variant: str, width: int | None, height: int | None) -> tuple[int, int]:
        if width and height:
            return width, height
        presets = {
            "thumbnail": (150, 150), "small": (320, 240), "large": (2560, 1440),
            "landscape": (1280, 720), "portrait": (720, 1280), "square": (800, 800),
        }
        if variant in presets:
            return presets[variant]
        return random.randint(self.config.min_width, self.config.max_width), random.randint(self.config.min_height, self.config.max_height)

    def _image(self, width: int, height: int, variant: str) -> Image.Image:
        if variant == "transparent":
            img = Image.new("RGBA", (width, height), (0, 0, 0, 0)); ImageDraw.Draw(img).ellipse((10, 10, width - 10, height - 10), fill=(59, 130, 246, 160)); return img
        if variant == "gradient":
            arr = np.zeros((height, width, 3), dtype=np.uint8)
            arr[:, :, 0] = np.linspace(20, 240, width, dtype=np.uint8)
            arr[:, :, 1] = np.linspace(240, 80, height, dtype=np.uint8)[:, None]
            arr[:, :, 2] = 180
            return Image.fromarray(arr, "RGB")
        if variant == "noise":
            return Image.fromarray(np.random.randint(0, 255, (height, width, 3), dtype=np.uint8), "RGB").filter(ImageFilter.SMOOTH)
        img = Image.new("RGB", (width, height), random.choice(["#f8fafc", "#ecfeff", "#fff7ed"]))
        draw = ImageDraw.Draw(img)
        draw.rectangle((width * .1, height * .15, width * .9, height * .85), fill="#2563eb")
        draw.text((max(8, width * .15), max(8, height * .45)), f"{variant} {width}x{height}", fill="white")
        return img

    def _svg(self, path: Path, width: int, height: int, variant: str) -> None:
        path.write_text(
            f"<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}' viewBox='0 0 {width} {height}'>"
            f"<defs><linearGradient id='g'><stop offset='0%' stop-color='#06b6d4'/><stop offset='100%' stop-color='#7c3aed'/></linearGradient></defs>"
            f"<rect width='100%' height='100%' fill='url(#g)'/><circle cx='{width//2}' cy='{height//2}' r='{min(width,height)//4}' fill='white' opacity='.75'/>"
            f"<text x='20' y='40' font-family='Arial' font-size='24' fill='white'>{variant}</text></svg>",
            encoding="utf-8",
        )
