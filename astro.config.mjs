import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import { remarkBaseUrl } from './src/remark-base-url.mjs';

const base = '/PatOrt';

export default defineConfig({
  site: 'https://alessio-milano.github.io/PatOrt',
  base,
  markdown: {
    remarkPlugins: [[remarkBaseUrl, base]],
  },
  integrations: [mdx()],
});
