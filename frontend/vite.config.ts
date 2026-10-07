import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import { readConfig } from './src/lib/config/runtime.ts';

export default defineConfig(({ command, mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  readConfig(env, command === 'build');
  return {
    plugins: [react()],
    server: {
      host: '127.0.0.1',
      port: 3000,
      strictPort: true,
      watch: {
        ignored: [
          '**/.local/**',
          '**/test-results/**',
          '**/playwright-report/**',
        ],
      },
      proxy: {
        '/api': { target: env.SMOLINK_API_PROXY || 'http://127.0.0.1:8000' },
      },
    },
    build: { sourcemap: false },
  };
});
