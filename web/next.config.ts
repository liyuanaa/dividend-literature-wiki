import type { NextConfig } from "next";
import path from "node:path";

// Static-export mode is opt-in via env, so local `pnpm dev`, Vercel, and Docker
// (all of which want the API routes + server rendering) are unaffected. Only the
// GitHub Pages build sets STATIC_EXPORT=true.
const isStaticExport = process.env.STATIC_EXPORT === "true";
const basePath = process.env.NEXT_PUBLIC_BASE_PATH ?? "";

const nextConfig: NextConfig = {
  // Pin the file-tracing root to this web project so Next.js does not infer a
  // different workspace root (which emits a warning) when the repo sits inside
  // a larger monorepo or alongside other lockfiles.
  outputFileTracingRoot: path.join(__dirname),
  ...(isStaticExport
    ? {
        output: "export", // emit a pure-static out/ directory
        trailingSlash: true, // /path/ -> /path/index.html so deep links don't 404
        images: { unoptimized: true }, // Pages has no image optimizer
        ...(basePath ? { basePath, assetPrefix: basePath } : {}),
      }
    : {}),
};

export default nextConfig;
