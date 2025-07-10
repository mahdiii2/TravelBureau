// next.config.js
const path = require('path')

/** @type {import('next').NextConfig} */
module.exports = {
  reactStrictMode: true,

  // Alias “@” → project root
  webpack(config) {
    config.resolve.alias['@'] = path.resolve(__dirname)
    return config
  },

  // Proxy certain routes to your FastAPI backend on port 8000
  async rewrites() {
    return [
      {
        source: '/get-hotel-contracts',
        destination: 'http://localhost:8000/get-hotel-contracts',
      },
      {
        source: '/upload-file',
        destination: 'http://localhost:8000/upload-file',
      },
      {
        source: '/search-countries',
        destination: 'http://localhost:8000/search-countries',
      },
      {
        source: '/search-hotels',
        destination: 'http://localhost:8000/search-hotels',
      },
      // add more endpoints here as needed
    ]
  },
}
