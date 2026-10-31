/** @type {import('next').NextConfig} */
const nextConfig = {
  // Serve the output/tiles directory as static files
  // When running locally, symlink or copy output/tiles → public/tiles
  output: "export",
  trailingSlash: true,
  images: {
    unoptimized: true,
  },
};

module.exports = nextConfig;
