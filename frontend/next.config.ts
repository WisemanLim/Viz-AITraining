import type { NextConfig } from "next";

const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

// `make publish` (scripts/publish-pages.sh) 가 정적 export 시 활성화.
// rewrites 는 output:'export' 와 호환되지 않으므로 export 모드에서는 비활성.
const staticExport = process.env.NEXT_PUBLIC_STATIC_EXPORT === "true";
const basePath = process.env.NEXT_PUBLIC_BASE_PATH ?? "";

const nextConfig: NextConfig = staticExport
  ? {
      output: "export",
      basePath,
      // GitHub Pages 정적 호스팅 — Next 이미지 최적화 서버 없음.
      images: { unoptimized: true },
      trailingSlash: true,
    }
  : {
      async rewrites() {
        return [
          {
            source: "/api/:path*",
            destination: `${apiUrl}/api/:path*`,
          },
        ];
      },
    };

export default nextConfig;
