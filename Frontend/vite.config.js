import { fileURLToPath, URL } from 'node:url';
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import vueDevTools from 'vite-plugin-vue-devtools';
import tailwindcss from '@tailwindcss/vite';
import os from 'os';

// 🧠 Automatically detect local IP address
function getLocalIp() {
  const nets = os.networkInterfaces();
  for (const name of Object.keys(nets)) {
    for (const net of nets[name]) {
      if (net.family === 'IPv4' && !net.internal) {
        return net.address;
      }
    }
  }
  return '127.0.0.1';
}

const localIP = process.env.HMR_HOST || getLocalIp();

export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
    tailwindcss(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
//   server: {
//     proxy: {
//       '/api/message': {
//         target: 'http://localhost:8000',
//         changeOrigin: true,
//         rewrite: (path) => path, // Keep the path as-is
//       },
//       '/api': {
//         target: 'http://localhost:8000',
//         changeOrigin: true,
//       },
//       '/media': {
//         target: 'http://localhost:8000',
//         changeOrigin: true,
//       },
//       '/users': {
//         target: 'http://localhost:8000',
//         changeOrigin: true,
//       },
//       '/conversations': {
//         target: 'http://localhost:8000',
//         changeOrigin: true,
//       },
//       '/private': {
//         target: 'http://localhost:8000',
//         changeOrigin: true,
//       },
//       '/group': {
//         target: 'http://localhost:8000',
//         changeOrigin: true,
//       },
//       '/requests': {
//         target: 'http://localhost:8000',
//         changeOrigin: true,
//       },
//       '/upload': {
//         target: 'http://localhost:8000',
//         changeOrigin: true,
//       },
//     },
//   },
  server: {
    host: '0.0.0.0',
    port: 5173,
    strictPort: false,
    allowedHosts: ['*'],
    hmr: {
      host: localIP,
    },
  },
});

console.log(`✅ Vite running with dynamic IP: ${localIP}`);
