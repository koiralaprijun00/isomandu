"""
Step 03 — AI Tile Generation (ControlNet + Stable Diffusion)
=============================================================
Takes the Canny edge map from Step 02 and sends it to ControlNet Canny
via the Replicate REST API to generate isometric pixel-art tiles.

Outputs:
  output/generated/<slug>_art.png
"""

import os
import sys
import time
import base64
import requests
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from src.pipeline.config import DEFAULT_CONFIG, LandmarkConfig, PipelineConfig


LANDMARK_STYLE_OVERRIDES: dict[str, str] = {
    "basantapur": (
        "Basantapur Kathmandu Durbar Square heritage complex, Kasthamandap pavilion, Taleju Bhawani multi-tier pagoda temple, "
        "Gaddi Baithak white neoclassical palace, Kumari Ghar living goddess courtyard, red clay brick streets, "
        "terracotta paved courtyards, stone bahals, carved wooden struts, brass temple spire, dry ground, no water"
    ),
    "boudhanath": (
        "Boudhanath stupa, giant white dome, all-seeing Buddha eyes painted in gold, "
        "prayer flags radiating outward, monastery rooftops, butter lamp offerings"
    ),
    "swayambhunath": (
        "Swayambhunath stupa on hilltop, steep stone staircase, white stupa with golden spire, "
        "Buddha eyes, prayer flags, shrines, valley panorama"
    ),
    "asan": (
        "Asan Tole bazaar crossroads, dense merchant stalls, colorful spice sacks, "
        "overhead electric wires, wooden shopfronts, Annapurna shrine, narrow alley galli"
    ),
    "patan": (
        "Patan Durbar Square Lalitpur, Krishna Mandir stone temple, Vishwanath temple, "
        "Hiranyavarna Mahavihara Golden Temple, Newar brick architecture, paved courtyard"
    ),
    "pashupatinath": (
        "Pashupatinath temple complex, Bagmati river ghats, golden roof shikhara temple, "
        "Hindu pilgrims, stone lingams, ritual offerings, banyan trees"
    ),
}


def build_prompt(landmark: LandmarkConfig, config: PipelineConfig) -> str:
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
    token = os.getenv("REPLICATE_API_TOKEN")
    if not token:
        print("✗ REPLICATE_API_TOKEN not found in .env")
        sys.exit(1)

    if canny_path is None:
        canny_path = os.path.join(config.output_renders_dir, f"{landmark.slug}_canny.png")

    if not os.path.exists(canny_path):
        print(f"✗ Canny edge map not found: {canny_path}")
        sys.exit(1)

    prompt = build_prompt(landmark, config)
    print(f"\n🚀 Sending ControlNet generation request to Replicate...")
    print(f"   Landmark: {landmark.name}")
    print(f"   Prompt: {prompt[:100]}...\n")

    # Encode Canny edge image as Data URI
    with open(canny_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode("utf-8")
    data_uri = f"data:image/png;base64,{img_b64}"

    version = config.replicate_controlnet_model.split(":")[-1]

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    payload = {
        "version": version,
        "input": {
            "image": data_uri,
            "prompt": prompt,
            "negative_prompt": config.negative_prompt,
            "num_samples": "1",
            "image_resolution": "768",
            "low_threshold": 80,
            "high_threshold": 200,
            "ddim_steps": 30,
            "scale": 9.0,
            "seed": 42,
        },
    }

    res = requests.post(
        "https://api.replicate.com/v1/predictions",
        headers=headers,
        json=payload,
        timeout=30,
    )

    if res.status_code != 201:
        print(f"✗ Replicate error {res.status_code}: {res.text}")
        sys.exit(1)

    pred = res.json()
    get_url = pred["urls"]["get"]
    print(f"  → Prediction created: {pred['id']}")
    print(f"  ⏳ Generating (this usually takes ~15-25 seconds)...")

    while True:
        poll_res = requests.get(get_url, headers=headers, timeout=30)
        pred_data = poll_res.json()
        status = pred_data.get("status")

        if status == "succeeded":
            output = pred_data.get("output")
            img_url = output[1] if isinstance(output, list) and len(output) > 1 else output[0]
            print(f"\n  ✓ Generation succeeded!")
            print(f"  → Downloading image from: {img_url}")

            os.makedirs(config.output_generated_dir, exist_ok=True)
            out_path = os.path.join(config.output_generated_dir, f"{landmark.slug}_art.png")

            r = requests.get(img_url, timeout=60)
            with open(out_path, "wb") as f:
                f.write(r.content)

            print(f"  💾 Saved to {out_path}!")
            return out_path
        elif status == "failed":
            print(f"✗ Generation failed: {pred_data.get('error')}")
            sys.exit(1)
        elif status == "canceled":
            print("✗ Generation was canceled.")
            sys.exit(1)
        else:
            print(f"  ... status: {status}")
            time.sleep(3)


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
    print("\n✅ AI Generation complete.")


if __name__ == "__main__":
    main()
