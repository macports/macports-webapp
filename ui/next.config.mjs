/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Optional: Use a local proxy path to avoid CORS during development.
  // If you want to use it, set NEXT_PUBLIC_MACPORTS_API_BASE to "/macports-api"
  async rewrites() {
    return [
      {
        source: "/macports-api/:path*",
        destination: "https://ports.macports.org/api/v1/:path*"
      }
    ];
  }
};

export default nextConfig;
