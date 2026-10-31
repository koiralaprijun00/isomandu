import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Isomandu — Isometric Kathmandu",
  description:
    "An AI-generated retro isometric pixel-art map of Kathmandu, Nepal. " +
    "Explore Basantapur Durbar Square, Boudhanath, Swayambhunath, and more " +
    "rendered in classic SimCity 2000 style.",
  openGraph: {
    title: "Isomandu — Isometric Kathmandu",
    description: "Explore Kathmandu as a retro 16-bit pixel-art city",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
