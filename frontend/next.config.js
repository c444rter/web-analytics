/** @type {import('next').NextConfig} */
const nextConfig = {
  // Remove the experimental.appDir property as it's now the default behavior in Next.js 15.
  
  // Add rewrites to handle API requests
  async rewrites() {
    return [
      {
        source: '/users/:path*',
        destination: `${process.env.NEXT_PUBLIC_BACKEND_URL}/users/:path*`,
      },
      {
        source: '/analytics/:path*',
        destination: `${process.env.NEXT_PUBLIC_BACKEND_URL}/analytics/:path*`,
      },
      {
        source: '/uploads/:path*',
        destination: `${process.env.NEXT_PUBLIC_BACKEND_URL}/uploads/:path*`,
      },
      {
        source: '/dashboard/:path*',
        destination: `${process.env.NEXT_PUBLIC_BACKEND_URL}/dashboard/:path*`,
      },
      {
        source: '/projections/:path*',
        destination: `${process.env.NEXT_PUBLIC_BACKEND_URL}/projections/:path*`,
      },
      {
        source: '/test-data/:path*',
        destination: `${process.env.NEXT_PUBLIC_BACKEND_URL}/test-data/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
