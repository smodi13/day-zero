/** @type {import('next').NextConfig} */
const nextConfig = {
  // Multiple lockfiles exist above this directory; pin tracing to this app.
  outputFileTracingRoot: import.meta.dirname,
  output: "export",
  trailingSlash: true,
  images: { unoptimized: true },
  reactStrictMode: true,
};
export default nextConfig;
