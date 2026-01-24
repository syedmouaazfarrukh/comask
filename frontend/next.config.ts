import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Enable standalone output for Docker deployment
  output: 'standalone',

  // Configure allowed image domains if needed
  images: {
    remotePatterns: [],
  },

  // Empty turbopack config to silence the warning
  turbopack: {},
};

export default nextConfig;
