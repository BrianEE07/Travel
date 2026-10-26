import { defineConfig } from 'astro/config';
export default defineConfig({
  site: 'https://travel.yungwei.com',
  output: 'static',
  vite: {
    build: { cssMinify: true },
  },
});
