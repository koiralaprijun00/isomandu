import MapViewer from "@/components/MapViewer";
import HUD from "@/components/HUD";

export default function Home() {
  return (
    <main className="relative w-screen h-screen overflow-hidden bg-bg">
      <MapViewer />
      <HUD />
    </main>
  );
}
