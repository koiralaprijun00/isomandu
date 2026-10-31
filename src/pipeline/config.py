"""
Isomandu Pipeline Configuration
================================
Central configuration for the isometric Kathmandu map pipeline.
Defines all geographic anchors, projection parameters, and output settings.
"""

from dataclasses import dataclass, field
from typing import Tuple


@dataclass
class LandmarkConfig:
    """A named geographic landmark to be rendered."""
    name: str
    slug: str               # used for file naming
    center_lat: float
    center_lon: float
    # Approximate bounding box width/height in degrees
    bbox_deg: float = 0.005
    description: str = ""


@dataclass
class ProjectionConfig:
    """Isometric / dimetric camera projection parameters."""
    # Classic SimCity 2000 / isometric.nyc dimetric angle
    # where pixel slope = 2:1, giving arctan(0.5) ≈ 26.565°
    azimuth: float = 45.0
    elevation: float = 26.565
    # Each output tile resolution (px)
    tile_render_size: int = 1024
    # Deep Zoom tile slice size (px) for OpenSeadragon
    dzi_tile_size: int = 256
    dzi_overlap: int = 1


@dataclass
class PipelineConfig:
    """Top-level pipeline configuration."""
    projection: ProjectionConfig = field(default_factory=ProjectionConfig)

    # ── Landmarks ─────────────────────────────────────────────────────────────
    landmarks: list = field(default_factory=lambda: [
        LandmarkConfig(
            name="Basantapur Durbar Square",
            slug="basantapur",
            center_lat=27.7042,
            center_lon=85.3067,
            bbox_deg=0.005,
            description="Historic royal palace complex, heart of old Kathmandu",
        ),
        LandmarkConfig(
            name="Boudhanath Stupa",
            slug="boudhanath",
            center_lat=27.7215,
            center_lon=85.3620,
            bbox_deg=0.004,
            description="One of the largest Buddhist stupas in the world",
        ),
        LandmarkConfig(
            name="Swayambhunath",
            slug="swayambhunath",
            center_lat=27.7149,
            center_lon=85.2904,
            bbox_deg=0.004,
            description="Ancient hilltop stupa, also known as the Monkey Temple",
        ),
        LandmarkConfig(
            name="Asan Bazaar",
            slug="asan",
            center_lat=27.7072,
            center_lon=85.3118,
            bbox_deg=0.003,
            description="Bustling historic market crossroads in the old city",
        ),
        LandmarkConfig(
            name="Patan Durbar Square",
            slug="patan",
            center_lat=27.6724,
            center_lon=85.3249,
            bbox_deg=0.005,
            description="Royal palace of the ancient Patan (Lalitpur) kingdom",
        ),
        LandmarkConfig(
            name="Pashupatinath Temple",
            slug="pashupatinath",
            center_lat=27.7105,
            center_lon=85.3487,
            bbox_deg=0.004,
            description="Sacred Hindu temple complex on the banks of the Bagmati",
        ),
    ])

    # ── Output directories ─────────────────────────────────────────────────────
    output_renders_dir: str = "output/renders"
    output_generated_dir: str = "output/generated"
    output_tiles_dir: str = "output/tiles"

    # ── AI Generation ─────────────────────────────────────────────────────────
    # Base prompt used for all tiles
    base_prompt: str = (
        "isometric pixel art, SimCity 2000 style, 16-bit retro game, "
        "orthographic dimetric projection, clean pixel edges, dithered shadows, "
        "warm afternoon sunlight, high detail"
    )
    # Per-landmark style additions
    newar_style_prompt: str = (
        "Newar pagoda architecture, multi-tiered clay tile roofs dachi appa, "
        "red brick walls, intricately carved wooden struts and jhyal window frames, "
        "stone-paved courtyards, chowk bahal layout, prayer flags, pigeons"
    )
    stupa_style_prompt: str = (
        "white stupa dome, all-seeing Buddha eyes, prayer flags strung overhead, "
        "monastery walls, butter lamp offerings, Buddhist iconography"
    )
    negative_prompt: str = (
        "photorealistic 3D render, smooth gradients, anti-aliasing, blurry, "
        "perspective vanishing point, modern glass skyscrapers, foggy, "
        "low quality, watermark"
    )

    # Replicate model ID for ControlNet Canny
    replicate_controlnet_model: str = (
        "jagilley/controlnet-canny:"
        "aff48af9c38d184738d8ac7ca7f3946a48d423c92a9a957a66cd5f59c25f54aa"
    )
    controlnet_low_threshold: int = 80
    controlnet_high_threshold: int = 200


# Singleton default config
DEFAULT_CONFIG = PipelineConfig()
