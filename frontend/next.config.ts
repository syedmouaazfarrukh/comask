import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Enable standalone output for Docker deployment
  output: 'standalone',

  // Configure allowed image domains if needed
  images: {
    remotePatterns: [],
  },
};

export default nextConfig;
