"use client";

import { useEffect, useRef, useState } from "react";
import type OpenSeadragon from "openseadragon";

// Landmark hotspots defined in image-space coordinates (0..1, 0..1)
// These map to positions within the generated isometric render.
// Adjust x/y values once you have the actual rendered image.
const HOTSPOTS = [
  {
    id: "taleju",
    label: "Taleju Bhawani Temple",
    x: 0.5,
    y: 0.35,
    description: "The tallest pagoda in Basantapur, built in 1564 AD",
  },
  {
    id: "kumari",
    label: "Kumari Ghar",
    x: 0.42,
    y: 0.52,
    description: "Home of the Living Goddess Kumari",
  },
  {
    id: "kasthamandap",
    label: "Kasthamandap",
    x: 0.38,
    y: 0.6,
    description: "The pavilion that gave Kathmandu its name",
  },
  {
    id: "shiva-parvati",
    label: "Shiva-Parvati Temple",
    x: 0.55,
    y: 0.48,
    description: "18th-century temple with deities looking out from the window",
  },
];

interface Props {
  viewer: OpenSeadragon.Viewer;
}

export default function LandmarkHotspots({ viewer }: Props) {
  const [positions, setPositions] = useState<
    Record<string, { x: number; y: number }>
  >({});
  const [activeHotspot, setActiveHotspot] = useState<string | null>(null);

  // Recompute screen positions whenever the viewer pans/zooms
  useEffect(() => {
    const update = () => {
      const next: Record<string, { x: number; y: number }> = {};
      HOTSPOTS.forEach((h) => {
        const pt = viewer.viewport.imageToViewerElementCoordinates(
          new (viewer as any).constructor.Point(
            h.x * (viewer.world.getItemAt(0)?.getContentSize()?.x ?? 1024),
            h.y * (viewer.world.getItemAt(0)?.getContentSize()?.y ?? 1024)
          )
        );
        next[h.id] = { x: pt.x, y: pt.y };
      });
      setPositions(next);
    };

    viewer.addHandler("update-viewport", update);
    viewer.addHandler("open", update);
    update();

    return () => {
      viewer.removeHandler("update-viewport", update);
    };
  }, [viewer]);

  return (
    <>
      {HOTSPOTS.map((h) => {
        const pos = positions[h.id];
        if (!pos) return null;
        return (
          <div
            key={h.id}
            className="absolute"
            style={{ left: pos.x, top: pos.y, transform: "translate(-50%, -50%)" }}
          >
            {/* Popup tooltip */}
            {activeHotspot === h.id && (
              <div className="landmark-popup">
                <div className="font-bold text-accent">{h.label}</div>
                <div className="text-muted mt-1">{h.description}</div>
              </div>
            )}

            {/* Pulsing marker dot */}
            <div
              className="hotspot-marker"
              onClick={() =>
                setActiveHotspot(activeHotspot === h.id ? null : h.id)
              }
              title={h.label}
            />
          </div>
        );
      })}
    </>
  );
}
