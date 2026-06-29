"""Asset Generator package for QA automation test fixtures.

The package creates disposable images, videos, audio clips, documents, office
files, structured data files, and archives with checksums and validation
metadata. Use :class:`asset_generator.manager.AssetManager` for most workflows.
"""
from .config import AssetGeneratorConfig, DEFAULT_CONFIG
from .manager import AssetManager
from .utils import AssetMetadata

__all__ = ["AssetGeneratorConfig", "DEFAULT_CONFIG", "AssetManager", "AssetMetadata"]
