import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://gboyee.github.io',
  markdown: {
    shikiConfig: { theme: 'nord' }
  },
  adapter: {
    name: '@astrojs/static'
  }
});
