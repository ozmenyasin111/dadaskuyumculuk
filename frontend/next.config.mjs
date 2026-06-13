/** @type {import('next').NextConfig} */

// MOBILE_BUILD=1 → Capacitor için statik export (out/).
// Aksi halde Railway için "standalone" davranışı AYNEN korunur.
const isMobileBuild = process.env.MOBILE_BUILD === "1";

const nextConfig = {
  output: isMobileBuild ? "export" : "standalone",
  reactStrictMode: true,
  // Statik export'ta Next image optimizasyonu çalışmaz; mobilde kapatılır.
  images: { unoptimized: isMobileBuild },
};

export default nextConfig;
