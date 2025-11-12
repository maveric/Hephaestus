import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig(({ mode }) => {
  // Load env file based on `mode` in the current working directory.
  const env = loadEnv(mode, process.cwd(), '')
  
  // Use environment variables with defaults
  const apiHost = env.VITE_API_HOST || 'localhost'
  const apiPort = env.VITE_API_PORT || '8000'
  const apiProtocol = env.VITE_API_PROTOCOL || 'http'
  const apiTarget = `${apiProtocol}://${apiHost}:${apiPort}`
  const wsProtocol = apiProtocol === 'https' ? 'wss' : 'ws'
  const wsTarget = `${wsProtocol}://${apiHost}:${apiPort}`

  return {
    plugins: [react()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
    server: {
      host: '0.0.0.0',  // Allow remote connections
      port: 5173,
      proxy: {
        '/api': {
          target: apiTarget,
          changeOrigin: true,
        },
        '/ws': {
          target: wsTarget,
          ws: true,
        },
      },
    },
  }
})
