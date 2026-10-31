"""
Step 03 — AI Tile Generation (ControlNet + Stable Diffusion)
=============================================================
Takes the Canny edge map from Step 02 and sends it to a ControlNet
Stable Diffusion model via the Replicate API to generate isometric
pixel-art tiles in the Newar architectural style.

Requires: REPLICATE_API_TOKEN in your .env file

Outputs:
  output/generated/<slug>_art.png
"""

import os
import sys
import urllib.request

import replicate
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from src.pipeline.config import DEFAULT_CONFIG, LandmarkConfig, PipelineConfig


# ── Per-landmark prompt customisation ────────────────────────────────────────

LANDMARK_STYLE_OVERRIDES: dict[str, str] = {
    "basantapur": (
        "Basantapur Kathmandu Durbar Square, multi-tiered Newar pagoda temples, "
        "Taleju Bhawani temple, Kumari Ghar, red brick facade, intricate wooden struts, "
        "stone courtyard, pigeons on rooftop, brick-paved plaza"
    ),
    "boudhanath": (
        "Boudhanath stupa, giant white dome, all-seeing Buddha eyes painted in gold, "
        "prayer flags radiating outward, monastery rooftops, butter lamp offerings, "
        "pilgrims walking kora, colorful thangka banners"
    ),
    "swayambhunath": (
        "Swayambhunath stupa on hilltop, steep stone staircase, white stupa with golden spire, "
        "Buddha eyes, prayer flags, rhesus macaque monkeys, surrounding shrines, valley panorama"
    ),
    "asan": (
        "Asan Tole bazaar crossroads, dense merchant stalls, colorful spice sacks, "
        "overhead electric wires, wooden shopfronts, Annapurna shrine, crowd of people, "
        "narrow alley galli, corrugated tin rooftops"
    ),
    "patan": (
        "Patan Durbar Square Lalitpur, Krishna Mandir stone temple, Vishwanath temple, "
        "Hiranyavarna Mahavihara Golden Temple, Newar brick architecture, paved courtyard, "
        "lotus water fountain, stone guardian lions"
    ),
    "pashupatinath": (
        "Pashupatinath temple complex, Bagmati river ghats, golden roof shikhara temple, "
        "Hindu pilgrims, sadhus in orange robes, cremation ghats, stone lingams, "
        "ritual offerings, banyan trees"
    ),
}


def build_prompt(landmark: LandmarkConfig, config: PipelineConfig) -> str:
    """Assembles the full generation prompt for a landmark."""
    landmark_detail = LANDMARK_STYLE_OVERRIDES.get(landmark.slug, landmark.description)
    style_detail = (
        config.stupa_style_prompt
        if landmark.slug in ("boudhanath", "swayambhunath")
        else config.newar_style_prompt
    )
    return (
        f"{config.base_prompt}, {landmark_detail}, {style_detail}, "
        "Nepal, Himalayan foothills backdrop, warm golden hour lighting"
    )


def generate_tile(
    landmark: LandmarkConfig,
    config: PipelineConfig,
    canny_path: str | None = None,
) -> str:
    """
    Calls the Replicate ControlNet Canny model and saves the result.
    Returns the output file path.
    """
    token = os.getenv("REPLICATE_API_TOKEN")
    if not token:
        print("✗ REPLICATE_API_TOKEN not set in environment. Check your .env file.")
        sys.exit(1)

    if canny_path is None:
        canny_path = os.path.join(config.output_renders_dir, f"{landmark.slug}_canny.png")

    if not os.path.exists(canny_path):
        print(f"✗ Canny edge map not found: {canny_path}")
        print("  Run 02_render_3d.py first.")
        sys.exit(1)

    prompt = build_prompt(landmark, config)
    print(f"\n🤖 Generating pixel art for: {landmark.name}")
    print(f"   Model: {config.replicate_controlnet_model[:50]}...")
    print(f"   Prompt excerpt: {prompt[:120]}...")

    with open(canny_path, "rb") as img_file:
        output = replicate.run(
            config.replicate_controlnet_model,
            input={
                "image": img_file,
                "prompt": prompt,
                "negative_prompt": config.negative_prompt,
                "num_samples": "1",
                "image_resolution": str(config.projection.tile_render_size),
                "low_threshold": config.controlnet_low_threshold,
                "high_threshold": config.controlnet_high_threshold,
                "ddim_steps": 30,
                "scale": 9,
                "seed": 42,  # reproducible — change for variety
            },
        )

    # Replicate returns a list of URLs; index 1 is the generated image
    result_url = output[1] if isinstance(output, list) and len(output) > 1 else output[0]

    os.makedirs(config.output_generated_dir, exist_ok=True)
    out_path = os.path.join(config.output_generated_dir, f"{landmark.slug}_art.png")
    urllib.request.urlretrieve(result_url, out_path)

    print(f"  💾 Generated tile → {out_path}")
    return out_path


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate isometric pixel art via ControlNet")
    parser.add_argument("--slug", default="basantapur", help="Landmark slug")
    args = parser.parse_args()

    config = DEFAULT_CONFIG
    landmark = next((lm for lm in config.landmarks if lm.slug == args.slug), None)
    if not landmark:
        print(f"✗ Unknown slug '{args.slug}'")
        sys.exit(1)

    generate_tile(landmark, config)
    print("\n✅ Generation complete.")


if __name__ == "__main__":
    main()
