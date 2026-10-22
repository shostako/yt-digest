/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  // 親ディレクトリに別の package-lock.json があっても frontend/ をルートとして扱う
  outputFileTracingRoot: __dirname,
}

module.exports = nextConfig
