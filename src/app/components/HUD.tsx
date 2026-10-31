"use client";

import { useState } from "react";
import clsx from "clsx";

const LANDMARKS = [
  { slug: "basantapur", label: "Basantapur Durbar Square", status: "active" },
  { slug: "boudhanath", label: "Boudhanath Stupa", status: "planned" },
  { slug: "swayambhunath", label: "Swayambhunath", status: "planned" },
  { slug: "asan", label: "Asan Bazaar", status: "planned" },
  { slug: "patan", label: "Patan Durbar Square", status: "planned" },
  { slug: "pashupatinath", label: "Pashupatinath Temple", status: "planned" },
];

export default function HUD() {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <>
      {/* ── Top-left title panel ─────────────────────────────────────── */}
      <div className="absolute top-4 left-4 z-30 hud-panel rounded-md px-4 py-3 select-none">
        <div className="text-accent text-base tracking-widest font-bold">
          ISOMANDU
        </div>
        <div className="text-muted text-xs mt-0.5 tracking-wider">
          ISOMETRIC KATHMANDU · NEPAL
        </div>
      </div>

      {/* ── Bottom-left coordinates ──────────────────────────────────── */}
      <div className="absolute bottom-4 left-4 z-30 hud-panel rounded-md px-3 py-2 select-none">
        <div className="text-muted text-xs">
          27.7042° N &nbsp;·&nbsp; 85.3067° E
        </div>
        <div className="text-xs text-text mt-0.5">
          Basantapur Durbar Square
        </div>
      </div>

      {/* ── Bottom-right: controls hint ──────────────────────────────── */}
      <div className="absolute bottom-4 right-4 z-30 hud-panel rounded-md px-3 py-2 select-none text-right">
        <div className="text-muted text-xs">Scroll to zoom · Drag to pan</div>
        <div className="text-muted text-xs">Double-click to zoom in</div>
      </div>

      {/* ── Top-right: landmark selector ────────────────────────────── */}
      <div className="absolute top-4 right-4 z-30">
        <button
          onClick={() => setMenuOpen(!menuOpen)}
          className="hud-panel rounded-md px-4 py-2 text-xs text-text tracking-wider hover:border-accent transition-colors"
        >
          ☰ LANDMARKS
        </button>

        {menuOpen && (
          <div className="hud-panel mt-2 rounded-md overflow-hidden min-w-[220px]">
            {LANDMARKS.map((lm) => (
              <button
                key={lm.slug}
                disabled={lm.status === "planned"}
                className={clsx(
                  "w-full text-left px-4 py-2 text-xs border-b border-border last:border-0 transition-colors",
                  lm.status === "active"
                    ? "text-text hover:bg-white/5 cursor-pointer"
                    : "text-muted cursor-not-allowed"
                )}
              >
                <span
                  className={clsx(
                    "inline-block w-2 h-2 rounded-full mr-2",
                    lm.status === "active" ? "bg-accent" : "bg-border"
                  )}
                />
                {lm.label}
                {lm.status === "planned" && (
                  <span className="ml-2 text-[10px] text-muted">(soon)</span>
                )}
              </button>
            ))}
          </div>
        )}
      </div>
    </>
  );
}
