import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  transpilePackages: ["@product-os/ui"],
  experimental: {
    serverActions: {
      bodySizeLimit: "2mb",
    },
  },
};

export default nextConfig;
