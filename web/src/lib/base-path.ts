/**
 * Static-export helper. On GitHub Pages the site lives under a `/<repo>/` path
 * prefix (`NEXT_PUBLIC_BASE_PATH`). Next's `<Link>` and `assetPrefix` add that
 * prefix automatically, but a bare `fetch("/wiki-index.json")` does not — it
 * would 404. Wrap such absolute-path fetches in `withBasePath()`.
 *
 * When no base path is set (local dev, Vercel, Docker), this is a no-op.
 */
export const BASE_PATH = process.env.NEXT_PUBLIC_BASE_PATH ?? "";

export function withBasePath(path: string): string {
  const clean = path.startsWith("/") ? path : `/${path}`;
  return `${BASE_PATH}${clean}`;
}
