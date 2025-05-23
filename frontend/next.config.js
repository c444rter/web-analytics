/** @type {import('next').NextConfig} */
const nextConfig = {
  // Remove the experimental.appDir property as it's now the default behavior in Next.js 15.
  
  // Disable ESLint during build to prevent build failures
  eslint: {
    // Warning: This allows production builds to successfully complete even if
    // your project has ESLint errors.
    ignoreDuringBuilds: true,
  },
  
  // Add rewrites to handle API requests
  async rewrites() {
    // Use NEXT_PUBLIC_API_URL as fallback if NEXT_PUBLIC_BACKEND_URL is not available
    const apiBaseUrl = process.env.NEXT_PUBLIC_BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || 'https://api.mydavids.com';
    
    return [
      {
        source: '/users/:path*',
        destination: `${apiBaseUrl}/users/:path*`,
      },
      {
        source: '/analytics/:path*',
        destination: `${apiBaseUrl}/analytics/:path*`,
      },
      {
        source: '/uploads/:path*',
        destination: `${apiBaseUrl}/uploads/:path*`,
      },
      {
        source: '/dashboard/:path*',
        destination: `${apiBaseUrl}/dashboard/:path*`,
      },
      {
        source: '/projections/:path*',
        destination: `${apiBaseUrl}/projections/:path*`,
      },
      {
        source: '/test-data/:path*',
        destination: `${apiBaseUrl}/test-data/:path*`,
      },
    ];
  },
  
  // Increase the response timeout for large file uploads and auth
  serverRuntimeConfig: {
    responseTimeout: 60000, // 60 seconds
  },
  
  // Increase function execution timeout
  experimental: {
    serverComponentsExternalPackages: ['bcrypt'],
    serverActions: {
      bodySizeLimit: '2mb',
    },
  },
};

module.exports = nextConfig;
