import { fileURLToPath, URL } from 'node:url';
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import vueDevTools from 'vite-plugin-vue-devtools';
import tailwindcss from '@tailwindcss/vite';

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
});