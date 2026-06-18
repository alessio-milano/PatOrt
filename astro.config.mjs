import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';

export default defineConfig({
  site: 'https://alessio-milano.github.io/PatOrt',
  base: '/PatOrt',
  integrations: [mdx()],
});
