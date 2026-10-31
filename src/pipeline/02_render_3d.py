"""
Step 02 — Orthographic 3D Render (Depth + Edge Maps)
======================================================
Reads the OSM GeoJSON footprints and generates two conditioning images
for the ControlNet diffusion pass:

  A) A grayscale depth map (white = tallest, black = ground)
  B) A Canny edge map of building outlines

These are rendered in pure Python using Pillow + Shapely — no GPU needed.
The isometric projection used is the classic dimetric 2:1 ratio:
  azimuth = 45°, elevation = 26.565° (arctan(0.5))

Outputs:
  output/renders/<slug>_depth.png
  output/renders/<slug>_canny.png
"""

import json
import math
import os
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from src.pipeline.config import DEFAULT_CONFIG, LandmarkConfig, PipelineConfig


# ── Isometric Projection ──────────────────────────────────────────────────────

def lonlat_to_iso(
    lon: float,
    lat: float,
    center_lon: float,
    center_lat: float,
    scale: float,
    canvas_size: int,
    azimuth_deg: float = 45.0,
    elevation_deg: float = 26.565,
) -> tuple[float, float]:
    """
    Projects geographic (lon, lat) to isometric screen (x, y).
    Uses a simple flat-earth approximation valid for small tiles (~500m).
    """
    # Convert to local meters (approximate)
    cos_lat = math.cos(math.radians(center_lat))
    dx_m = (lon - center_lon) * 111_320 * cos_lat
    dy_m = (lat - center_lat) * 110_540

    # Rotate by azimuth
    az = math.radians(azimuth_deg)
    rx = dx_m * math.cos(az) - dy_m * math.sin(az)
    ry = dx_m * math.sin(az) + dy_m * math.cos(az)

    # Apply dimetric elevation squeeze (2:1 ratio)
    el = math.radians(elevation_deg)
    sx = rx * scale + canvas_size / 2
    sy = -ry * math.sin(el) * scale + canvas_size / 2

    return sx, sy


def get_building_height(tags: dict) -> float:
    """Extracts or estimates building height in metres from OSM tags."""
    if "height" in tags:
        try:
            return float(str(tags["height"]).replace("m", "").strip())
        except ValueError:
            pass
    if "building:levels" in tags:
        try:
            return float(tags["building:levels"]) * 3.5
        except ValueError:
            pass
    # Kathmandu default: 3-story brick house
    return 10.0


# ── Render ────────────────────────────────────────────────────────────────────

def render_depth_and_edges(
    geojson_path: str,
    landmark: LandmarkConfig,
    config: PipelineConfig,
) -> tuple[str, str]:
    """
    Reads GeoJSON footprints and renders depth + edge maps.
    Returns (depth_path, canny_path).
    """
    with open(geojson_path, encoding="utf-8") as f:
        geojson = json.load(f)

    canvas_size = config.projection.tile_render_size
    # Scale: meters per pixel (roughly 1m per 0.5px for a ~500m tile)
    bbox_m = landmark.bbox_deg * 111_000
    scale = (canvas_size * 0.8) / bbox_m

    # ── Build depth layer ──────────────────────────────────────────────────
    depth_img = Image.new("L", (canvas_size, canvas_size), 20)  # dark ground
    draw = ImageDraw.Draw(depth_img)

    buildings = []
    for feature in geojson.get("features", []):
        geom = feature.get("geometry", {})
        tags = feature.get("properties", {})
        if geom.get("type") != "Polygon":
            continue
        coords = geom["coordinates"][0]
        if len(coords) < 3:
            continue

        height = get_building_height(tags)
        screen_pts = [
            lonlat_to_iso(
                lon, lat,
                landmark.center_lon, landmark.center_lat,
                scale, canvas_size,
                config.projection.azimuth,
                config.projection.elevation,
            )
            for lon, lat in coords
        ]
        buildings.append((height, screen_pts, tags))

    if not buildings:
        print("  ⚠  No polygon buildings found in GeoJSON. Using placeholder.")
        _draw_placeholder(draw, canvas_size)
    else:
        # Sort by height so taller buildings paint last (on top)
        buildings.sort(key=lambda b: b[0])
        max_h = max(b[0] for b in buildings)
        for height, pts, tags in buildings:
            brightness = int(40 + (height / max_h) * 200)
            flat_pts = [(int(x), int(y)) for x, y in pts]
            if len(flat_pts) >= 3:
                draw.polygon(flat_pts, fill=brightness, outline=255)

    # ── Canny edge pass ────────────────────────────────────────────────────
    depth_np = np.array(depth_img)
    blurred = cv2.GaussianBlur(depth_np, (3, 3), 0)
    edges = cv2.Canny(
        blurred,
        config.controlnet_low_threshold,
        config.controlnet_high_threshold,
    )

    # ── Save outputs ───────────────────────────────────────────────────────
    os.makedirs(config.output_renders_dir, exist_ok=True)
    depth_path = os.path.join(config.output_renders_dir, f"{landmark.slug}_depth.png")
    canny_path = os.path.join(config.output_renders_dir, f"{landmark.slug}_canny.png")

    depth_img.save(depth_path)
    cv2.imwrite(canny_path, edges)

    print(f"  💾 Depth map → {depth_path}")
    print(f"  💾 Canny edges → {canny_path}")
    return depth_path, canny_path


def _draw_placeholder(draw: ImageDraw.ImageDraw, size: int):
    """Draws a simple placeholder grid when no real buildings are found."""
    step = size // 8
    for i in range(1, 8):
        for j in range(1, 8):
            x, y = i * step, j * step
            draw.rectangle([x - 20, y - 20, x + 20, y + 20], fill=160, outline=255)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Render depth/edge maps from OSM footprints")
    parser.add_argument("--slug", default="basantapur", help="Landmark slug")
    args = parser.parse_args()

    config = DEFAULT_CONFIG
    landmark = next((lm for lm in config.landmarks if lm.slug == args.slug), None)
    if not landmark:
        print(f"✗ Unknown slug '{args.slug}'")
        sys.exit(1)

    geojson_path = os.path.join(config.output_renders_dir, f"{args.slug}_footprints.geojson")
    if not os.path.exists(geojson_path):
        print(f"✗ GeoJSON not found: {geojson_path}")
        print("  Run 01_fetch_osm.py first.")
        sys.exit(1)

    print(f"\n🎨 Rendering depth + edge maps for: {landmark.name}")
    render_depth_and_edges(geojson_path, landmark, config)
    print("\n✅ Render complete.")


if __name__ == "__main__":
    main()
