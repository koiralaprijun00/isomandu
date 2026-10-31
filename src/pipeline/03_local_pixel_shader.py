"""
Local Pixel-Art Procedural Colorizer for Basantapur
====================================================
Transforms the raw orthographic isometric geometry and footprint edges
into an authentic 90s SimCity 2000 Newar architectural palette:
- Terracotta brick streets and courtyards (dachi appa)
- Multi-tiered pagoda roofs with red/brown tiles
- Dark carved wooden structural eaves and struts
- Whitewashed plaster accents and temple pinnacle brass
- Cobblestone square plazas
- Ground dither & quantized 16-bit retro shading

Runs 100% locally with zero external API fees or GPU requirements!
"""

import os
import sys
import numpy as np
import cv2
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from src.pipeline.config import DEFAULT_CONFIG


def colorize_basantapur(depth_path: str, canny_path: str, output_path: str):
    print("🎨 Generating local retro 16-bit Newar pixel-art composite...")
    depth = cv2.imread(depth_path, cv2.IMREAD_GRAYSCALE)
    canny = cv2.imread(canny_path, cv2.IMREAD_GRAYSCALE)

    if depth is None or canny is None:
        print("✗ Missing depth or canny input files.")
        return

    h, w = depth.shape
    # Canvas base in RGB
    art = np.zeros((h, w, 3), dtype=np.uint8)

    # 1. Ground plane: Kathmandu courtyard stone / dry earth
    art[:] = [42, 38, 34]  # BGR: dark earthy stone

    # Add classic SimCity dithering pattern to ground
    dither_mask = (np.indices((h, w)).sum(axis=0) % 2 == 0)
    art[dither_mask] = [48, 44, 40]

    # 2. Building heights & materials
    # Distinct threshold tiers for Newar brickwork and temple roofs
    is_building = depth > 30

    # Red brick facade (Newar terracotta red/brown)
    # BGR format:
    brick_shadow = np.array([32, 42, 110], dtype=np.uint8)   # dark brick red
    brick_lit    = np.array([45, 60, 150], dtype=np.uint8)   # warm terracotta
    roof_tile    = np.array([28, 38, 128], dtype=np.uint8)   # pagoda roof terracotta
    temple_gold  = np.array([40, 160, 210], dtype=np.uint8)  # gajur / pinnacle brass
    wood_trim    = np.array([20, 32, 55], dtype=np.uint8)    # dark carved timber

    # Fill base buildings with terracotta tones modulated by height
    for y in range(h):
        for x in range(w):
            d = depth[y, x]
            if d > 30:
                # Normalised height 0..1
                t = (d - 30) / 225.0
                if d > 190:
                    # Tallest monuments (Taleju Temple spire / pinnacles) -> Brass gold
                    art[y, x] = temple_gold
                elif d > 130:
                    # Pagoda tiered roofs
                    base_color = roof_tile if ((x + y) % 4 < 2) else wood_trim
                    art[y, x] = np.clip(base_color * (0.8 + 0.4 * t), 0, 255).astype(np.uint8)
                else:
                    # Traditional residential / courtyard red brick walls
                    # Directional sunlight from top-left (isometric light source)
                    is_lit = (x - y) % 3 == 0
                    base = brick_lit if is_lit else brick_shadow
                    art[y, x] = np.clip(base * (0.7 + 0.5 * t), 0, 255).astype(np.uint8)

    # 3. Superimpose crisp black & dark timber architectural outlines (Canny edges)
    edge_mask = canny > 120
    art[edge_mask] = [15, 20, 28]  # Crisp retro pixel outline

    # 4. Quantize to 16-bit retro color palette (SimCity 2000 style)
    # Downsample slightly and upsample with NEAREST to lock retro pixel chunks
    img = Image.fromarray(cv2.cvtColor(art, cv2.COLOR_BGR2RGB))
    # 512x512 quantization step
    pixelated = img.resize((512, 512), Image.Resampling.NEAREST)
    # Quantize palette to 32 colors
    quantized = pixelated.quantize(colors=32, dither=Image.Dither.FLOYDSTEINBERG).convert("RGB")
    final_art = quantized.resize((1024, 1024), Image.Resampling.NEAREST)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    final_art.save(output_path)
    print(f"✓ Saved authentic retro Newar pixel art to: {output_path}")


if __name__ == "__main__":
    colorize_basantapur(
        "output/renders/basantapur_depth.png",
        "output/renders/basantapur_canny.png",
        "output/generated/basantapur_art.png",
    )
