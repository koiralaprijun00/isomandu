"""
Step 04 — Slice into Deep Zoom Image (DZI) Pyramid
====================================================
Takes the generated pixel-art PNG from Step 03 and slices it into
a multi-resolution Deep Zoom Image (DZI) pyramid compatible with
OpenSeadragon.

Requires: libvips installed on the system
  Windows:  https://www.libvips.org/install.html
  macOS:    brew install vips
  Ubuntu:   sudo apt install libvips-tools

Outputs:
  output/tiles/<slug>.dzi
  output/tiles/<slug>_files/   (tile pyramid directory)
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from src.pipeline.config import DEFAULT_CONFIG, PipelineConfig


def slice_to_dzi(input_path: str, output_name: str, config: PipelineConfig) -> str:
    """
    Slices a PNG into a DZI tile pyramid using pyvips.
    Returns the path to the .dzi descriptor file.
    """
    try:
        import pyvips
    except ImportError:
        print("✗ pyvips not installed. Run: pip install pyvips")
        print("  Also ensure libvips is installed on your system.")
        sys.exit(1)

    if not os.path.exists(input_path):
        print(f"✗ Input image not found: {input_path}")
        print("  Run 03_generate_tiles.py first.")
        sys.exit(1)

    print(f"\n🍕 Slicing {input_path} into Deep Zoom pyramid...")
    image = pyvips.Image.new_from_file(input_path, access="sequential")
    w, h = image.width, image.height
    print(f"   Image size: {w}×{h} px")

    os.makedirs(config.output_tiles_dir, exist_ok=True)
    out_base = os.path.join(config.output_tiles_dir, output_name)

    image.dzsave(
        out_base,
        tile_size=config.projection.dzi_tile_size,
        overlap=config.projection.dzi_overlap,
        suffix=".png",  # PNG preserves pixel art sharpness
    )

    dzi_path = out_base + ".dzi"
    print(f"  💾 DZI descriptor → {dzi_path}")
    print(f"  💾 Tile pyramid   → {out_base}_files/")
    return dzi_path


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Slice generated art into a DZI tile pyramid")
    parser.add_argument("--slug", default="basantapur", help="Landmark slug")
    args = parser.parse_args()

    config = DEFAULT_CONFIG
    input_path = os.path.join(config.output_generated_dir, f"{args.slug}_art.png")
    dzi_path = slice_to_dzi(input_path, args.slug, config)
    print(f"\n✅ Pyramid slicing complete: {dzi_path}")


if __name__ == "__main__":
    main()
