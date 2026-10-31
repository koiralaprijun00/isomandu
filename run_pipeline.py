"""
Isomandu Pipeline — convenience runner
=======================================
Runs all four pipeline steps in sequence for a given landmark slug.

Usage:
    python run_pipeline.py --slug basantapur
    python run_pipeline.py --slug boudhanath --skip-fetch
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.pipeline.config import DEFAULT_CONFIG
from src.pipeline import (
    fetch_osm_module,
    render_module,
    generate_module,
    slice_module,
)


def main():
    parser = argparse.ArgumentParser(description="Run the full Isomandu pipeline")
    parser.add_argument("--slug", default="basantapur", help="Landmark slug to process")
    parser.add_argument("--skip-fetch", action="store_true", help="Skip OSM fetch (reuse existing GeoJSON)")
    parser.add_argument("--skip-render", action="store_true", help="Skip 3D render (reuse existing depth/edge maps)")
    parser.add_argument("--skip-generate", action="store_true", help="Skip AI generation (reuse existing art)")
    args = parser.parse_args()

    config = DEFAULT_CONFIG
    landmark = next((lm for lm in config.landmarks if lm.slug == args.slug), None)
    if not landmark:
        print(f"✗ Unknown slug: '{args.slug}'")
        print(f"  Available: {[lm.slug for lm in config.landmarks]}")
        sys.exit(1)

    print(f"\n🏔️  Isomandu Pipeline — {landmark.name}")
    print("=" * 50)

    geojson_path = os.path.join(config.output_renders_dir, f"{args.slug}_footprints.geojson")
    if not args.skip_fetch:
        print("\n[1/4] Fetching OSM footprints...")
        from src.pipeline.fetch_osm import fetch_landmark
        fetch_landmark(landmark, config)
    else:
        print("\n[1/4] Skipping OSM fetch (--skip-fetch)")

    if not args.skip_render:
        print("\n[2/4] Rendering depth + edge maps...")
        from src.pipeline.render_3d import render_depth_and_edges
        render_depth_and_edges(geojson_path, landmark, config)
    else:
        print("\n[2/4] Skipping render (--skip-render)")

    if not args.skip_generate:
        print("\n[3/4] Generating pixel art via ControlNet...")
        from src.pipeline.generate_tiles import generate_tile
        generate_tile(landmark, config)
    else:
        print("\n[3/4] Skipping AI generation (--skip-generate)")

    print("\n[4/4] Slicing into DZI pyramid...")
    from src.pipeline.slice_pyramid import slice_to_dzi
    input_art = os.path.join(config.output_generated_dir, f"{args.slug}_art.png")
    slice_to_dzi(input_art, args.slug, config)

    print(f"\n🎉 Pipeline complete for {landmark.name}!")
    print(f"   Open web/index.html in a browser (serve with: python -m http.server 8000)")


if __name__ == "__main__":
    main()
