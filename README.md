# 🏔️ Isomandu — Isometric Kathmandu

> An AI-generated, retro isometric pixel-art map of Kathmandu, Nepal — inspired by [isometric.nyc](https://isometric.nyc)

![Isomandu Preview](docs/preview-placeholder.png)

Isomandu renders Kathmandu's iconic landmarks — Basantapur Durbar Square, Boudhanath, Swayambhunath, and the dense Newar courtyards of the old city — as a navigable, zoomable, SimCity-2000-style pixel-art map.

---

## ✨ Features

- 🗺️ Real geospatial data from OpenStreetMap / Kathmandu Living Labs
- 🏯 AI-generated isometric pixel art via ControlNet + Stable Diffusion
- 🔍 Smooth pan & zoom via OpenSeadragon (Deep Zoom Image pyramid)
- 🏛️ Clickable heritage hotspots (Durbar Squares, stupas, bahals)
- 🎮 Classic 16-bit SimCity 2000 aesthetic with Newar architectural language

---

## 🗂️ Project Structure

```
isomandu/
├── src/
│   ├── pipeline/           # Python AI + GIS pipeline
│   │   ├── config.py       # Coordinates, projection params
│   │   ├── 01_fetch_osm.py       # Download OSM building footprints
│   │   ├── 02_render_3d.py       # Orthographic 3D render (depth maps)
│   │   ├── 03_generate_tiles.py  # ControlNet AI tile generation
│   │   └── 04_slice_pyramid.py   # Slice output into DZI tile pyramid
│   └── app/                # Next.js frontend viewer
│       ├── app/
│       ├── components/
│       └── public/
├── output/
│   ├── renders/            # Raw 3D orthographic renders
│   ├── generated/          # AI-styled pixel art tiles
│   └── tiles/              # Deep Zoom Image pyramid (served to browser)
├── docs/
└── scripts/                # Helper shell scripts
```

---

## 🚀 Quick Start

### 1. Clone & Install Python deps

```bash
git clone https://github.com/koiralaprijun00/isomandu.git
cd isomandu
pip install -e .
# or with uv:
uv sync
```

### 2. Set up environment variables

```bash
cp .env.example .env
# Edit .env and add your API keys:
# REPLICATE_API_TOKEN=...
# GOOGLE_MAPS_API_KEY=...  (optional, for 3D tile capture)
```

### 3. Run the pipeline

```bash
# Step 1: Fetch OSM building footprints for Basantapur
python src/pipeline/01_fetch_osm.py

# Step 2: Generate orthographic 3D render
python src/pipeline/02_render_3d.py

# Step 3: AI pixel-art generation (requires REPLICATE_API_TOKEN)
python src/pipeline/03_generate_tiles.py

# Step 4: Slice into Deep Zoom Image pyramid
python src/pipeline/04_slice_pyramid.py
```

### 4. Launch the web viewer

```bash
cd src/app
npm install
npm run dev
# Open http://localhost:3000
```

---

## 🎨 The Pipeline

```
OSM Footprints + SRTM Elevation
         │
         ▼
  Orthographic 3D Render
  (Blender / Three.js / CesiumJS)
  Azimuth: 45°  Elevation: 26.565°
         │
         ▼
  Canny / Depth Maps
  (OpenCV ControlNet conditioning)
         │
         ▼
  SDXL ControlNet Generation
  Prompt: "Newar pagoda, SimCity 2000 pixel art…"
         │
         ▼
  Deep Zoom Image Pyramid (DZI)
  (libvips / pyvips, 256×256 tiles)
         │
         ▼
  OpenSeadragon Interactive Viewer
```

---

## 🏛️ Target Landmarks (v1)

| Landmark | Coordinates | Status |
|---|---|---|
| Basantapur Durbar Square | 27.7042° N, 85.3067° E | 🔄 In progress |
| Boudhanath Stupa | 27.7215° N, 85.3620° E | 📋 Planned |
| Swayambhunath (Monkey Temple) | 27.7149° N, 85.2904° E | 📋 Planned |
| Asan Bazaar | 27.7072° N, 85.3118° E | 📋 Planned |
| Patan Durbar Square | 27.6724° N, 85.3249° E | 📋 Planned |
| Pashupatinath Temple | 27.7105° N, 85.3487° E | 📋 Planned |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| GIS Data | OpenStreetMap · Kathmandu Living Labs · Overpass API |
| Elevation | SRTM 30m · Copernicus DEM |
| 3D Render | Three.js / CesiumJS (orthographic camera) |
| AI Generation | Stable Diffusion XL + ControlNet (Canny + Depth) |
| AI API | Replicate · RunPod · Fal.ai |
| Image Processing | OpenCV · Pillow · pyvips |
| Tile Serving | Deep Zoom Image (DZI) · libvips |
| Frontend | Next.js 14 · OpenSeadragon · TypeScript |
| Deployment | Vercel / GitHub Pages |

---

## 🙏 Inspiration & Credits

- [isometric.nyc](https://isometric.nyc) by Andy Coenen — the original inspiration
- [Kathmandu Living Labs](https://www.kathmandulivelabs.org/) — Kathmandu OSM mapping community
- [OpenStreetMap](https://www.openstreetmap.org/) — geospatial foundation

---

## 📄 License

MIT — see [LICENSE](LICENSE)
