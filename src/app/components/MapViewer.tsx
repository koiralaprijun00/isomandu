"use client";

import { useEffect, useRef, useState } from "react";
import OpenSeadragon from "openseadragon";
import LandmarkHotspots from "./LandmarkHotspots";

// The DZI file is served from /tiles/<slug>.dzi
// After running the pipeline, copy output/tiles/ → src/app/public/tiles/
const DEFAULT_TILE_SOURCE = "/tiles/basantapur.dzi";

export default function MapViewer() {
  const containerRef = useRef<HTMLDivElement>(null);
  const viewerRef = useRef<OpenSeadragon.Viewer | null>(null);
  const [isReady, setIsReady] = useState(false);
  const [zoom, setZoom] = useState(1);

  useEffect(() => {
    if (!containerRef.current || viewerRef.current) return;

    const viewer = OpenSeadragon({
      element: containerRef.current,
      prefixUrl:
        "https://cdnjs.cloudflare.com/ajax/libs/openseadragon/4.1.0/images/",
      tileSources: DEFAULT_TILE_SOURCE,
      showNavigationControl: false,
      showZoomControl: false,
      showHomeControl: false,
      showFullPageControl: false,
      // Pixel-perfect settings — no smoothing so pixel art stays crisp
      maxZoomPixelRatio: 4,
      minZoomImageRatio: 0.3,
      imageSmoothingEnabled: false,
      // Smooth pan/zoom animation
      animationTime: 0.4,
      blendTime: 0.1,
      gestureSettingsMouse: {
        scrollToZoom: true,
        clickToZoom: false,
        dblClickToZoom: true,
      },
      gestureSettingsTouch: {
        pinchToZoom: true,
        flickEnabled: true,
      },
    });

    viewer.addHandler("open", () => setIsReady(true));
    viewer.addHandler("zoom", (e) => setZoom(Math.round(e.zoom * 100) / 100));

    viewerRef.current = viewer;

    return () => {
      viewer.destroy();
      viewerRef.current = null;
    };
  }, []);

  return (
    <>
      {/* OpenSeadragon canvas */}
      <div
        ref={containerRef}
        className="absolute inset-0 w-full h-full"
        style={{ background: "#0c0d12" }}
      />

      {/* Landmark hotspot overlays (rendered after viewer is ready) */}
      {isReady && viewerRef.current && (
        <LandmarkHotspots viewer={viewerRef.current} />
      )}

      {/* Loading screen */}
      {!isReady && (
        <div className="absolute inset-0 flex items-center justify-center bg-bg z-50">
          <div className="text-center">
            <div className="text-accent text-2xl mb-3 animate-pulse">
              ISOMANDU
            </div>
            <div className="text-muted text-xs tracking-widest">
              LOADING KATHMANDU…
            </div>
          </div>
        </div>
      )}
    </>
  );
}
