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
            center_lat=27.7045,
            center_lon=85.3068,
            bbox_deg=0.0022,  # Tight ~240m focus on Durbar Square, Kasthamandap, Taleju & Hanuman Dhoka
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

    # AI Generation
    base_prompt: str = (
        "SimCity 2000 style, 16-bit retro isometric pixel art, orthographic dimetric projection, "
        "crisp pixel outlines, dry reddish clay brick paved plazas and stone courtyards, "
        "dithered shadows, warm golden hour afternoon sunlight, clean sharp 90s PC game aesthetic"
    )
    # Per-landmark style additions
    newar_style_prompt: str = (
        "traditional Kathmandu Newar architecture, multi-tiered pagoda temples with brown terracotta tile roofs, "
        "elaborately carved dark wood struts and jhyal window latticework, exposed red brick masonry walls, "
        "historic stone paved Durbar Square bahal courtyard, terracotta brick ground, pigeon flocks, brass pinnacles"
    )
    stupa_style_prompt: str = (
        "white stupa dome, all-seeing Buddha eyes, prayer flags strung overhead, "
        "monastery walls, butter lamp offerings, Buddhist iconography"
    )
    negative_prompt: str = (
        "water, ocean, river, sea, lake, pond, canal, blue ground, blue floor, blue puddles, puddles, swimming pool, "
        "green grass lawn, neon colors, photorealistic 3D, smooth gradient, modern glass skyscrapers, modern vehicles, "
        "blurry, anti-aliased, distortion, foggy, perspective vanishing point"
    )

    # Replicate model ID for ControlNet Canny
    replicate_controlnet_model: str = (
        "jagilley/controlnet-canny:"
        "aff48af9c68d162388d230a2ab003f68d2638d88307bdaf1c2f1ac95079c9613"
    )
    controlnet_low_threshold: int = 80
    controlnet_high_threshold: int = 200


# Singleton default config
DEFAULT_CONFIG = PipelineConfig()
