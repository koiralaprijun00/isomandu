"""
Step 01 — Fetch OSM Building Footprints
========================================
Downloads building footprints and road geometry for a given landmark
from OpenStreetMap via the Overpass API.

Outputs GeoJSON files to output/renders/<slug>_footprints.geojson
"""

import json
import os
import sys
import time

import requests

# Allow running as a script from the repo root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from src.pipeline.config import DEFAULT_CONFIG, LandmarkConfig, PipelineConfig


OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# Overpass QL template — fetches buildings, highways, waterways in bbox
OVERPASS_QUERY_TEMPLATE = """
[out:json][timeout:60];
(
  way["building"]({south},{west},{north},{east});
  way["highway"]({south},{west},{north},{east});
  way["waterway"]({south},{west},{north},{east});
  way["leisure"="park"]({south},{west},{north},{east});
  relation["building"]({south},{west},{north},{east});
);
out body;
>;
out skel qt;
"""


def get_bbox(landmark: LandmarkConfig) -> tuple[float, float, float, float]:
    """Returns (south, west, north, east) bounding box for a landmark."""
    half = landmark.bbox_deg / 2
    return (
        landmark.center_lat - half,
        landmark.center_lon - half,
        landmark.center_lat + half,
        landmark.center_lon + half,
    )


def fetch_overpass(query: str, retries: int = 3) -> dict:
    """Sends a query to the Overpass API with retry logic."""
    for attempt in range(retries):
        try:
            print(f"  → Querying Overpass API (attempt {attempt + 1}/{retries})...")
            response = requests.post(
                OVERPASS_URL,
                data={"data": query},
                timeout=90,
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"  ✗ Request failed: {e}")
            if attempt < retries - 1:
                wait = 5 * (attempt + 1)
                print(f"  ⏳ Retrying in {wait}s...")
                time.sleep(wait)
            else:
                raise


def osm_to_geojson(osm_data: dict) -> dict:
    """
    Converts raw Overpass JSON (nodes + ways) into a minimal GeoJSON FeatureCollection.
    Only converts ways that have enough node references to form a polygon/linestring.
    """
    # Build node id → (lon, lat) lookup
    nodes: dict[int, tuple[float, float]] = {}
    for element in osm_data.get("elements", []):
        if element["type"] == "node":
            nodes[element["id"]] = (element["lon"], element["lat"])

    features = []
    for element in osm_data.get("elements", []):
        if element["type"] != "way":
            continue
        node_ids = element.get("nodes", [])
        coords = [nodes[nid] for nid in node_ids if nid in nodes]
        if len(coords) < 2:
            continue

        tags = element.get("tags", {})
        is_building = "building" in tags
        # Close the ring if it's a polygon
        if is_building and coords[0] != coords[-1]:
            coords.append(coords[0])

        geometry = (
            {"type": "Polygon", "coordinates": [coords]}
            if is_building and len(coords) >= 4
            else {"type": "LineString", "coordinates": coords}
        )

        features.append({
            "type": "Feature",
            "properties": {
                "osm_id": element["id"],
                **tags,
            },
            "geometry": geometry,
        })

    return {"type": "FeatureCollection", "features": features}


def fetch_landmark(landmark: LandmarkConfig, config: PipelineConfig) -> str:
    """Fetches OSM data for a landmark and saves it as GeoJSON. Returns output path."""
    print(f"\n📦 Fetching OSM data for: {landmark.name}")
    south, west, north, east = get_bbox(landmark)
    print(f"   Bounding box: ({south:.5f}, {west:.5f}) → ({north:.5f}, {east:.5f})")

    query = OVERPASS_QUERY_TEMPLATE.format(
        south=south, west=west, north=north, east=east
    )
    osm_data = fetch_overpass(query)

    element_count = len(osm_data.get("elements", []))
    print(f"  ✓ Received {element_count} OSM elements")

    geojson = osm_to_geojson(osm_data)
    feature_count = len(geojson["features"])
    print(f"  ✓ Converted to {feature_count} GeoJSON features")

    os.makedirs(config.output_renders_dir, exist_ok=True)
    out_path = os.path.join(config.output_renders_dir, f"{landmark.slug}_footprints.geojson")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(geojson, f, indent=2)

    print(f"  💾 Saved: {out_path}")
    return out_path


def main():
    config = DEFAULT_CONFIG
    # Default to just Basantapur for first run; pass --all to fetch all landmarks
    import argparse
    parser = argparse.ArgumentParser(description="Fetch OSM footprints for Isomandu landmarks")
    parser.add_argument(
        "--slug",
        default="basantapur",
        help="Landmark slug to fetch (default: basantapur). Use 'all' to fetch all.",
    )
    args = parser.parse_args()

    landmarks_to_fetch = (
        config.landmarks
        if args.slug == "all"
        else [lm for lm in config.landmarks if lm.slug == args.slug]
    )

    if not landmarks_to_fetch:
        print(f"✗ No landmark found with slug '{args.slug}'")
        print(f"  Available slugs: {[lm.slug for lm in config.landmarks]}")
        sys.exit(1)

    for landmark in landmarks_to_fetch:
        fetch_landmark(landmark, config)

    print("\n✅ OSM fetch complete.")


if __name__ == "__main__":
    main()
