/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        mono: ["'Share Tech Mono'", "monospace"],
      },
      colors: {
        bg: "#0c0d12",
        panel: "rgba(15,17,23,0.88)",
        border: "#2e3440",
        accent: "#e8b84b",       // warm gold / temple brass
        accent2: "#c0392b",      // Newar red brick
        text: "#cdd3e0",
        muted: "#6b7388",
      },
    },
  },
  plugins: [],
};
