import { defineCollection, z } from 'astro:content';

const patologie = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string(),
    categoria: z.enum(['anca', 'ginocchio', 'colonna']),
    tags: z.array(z.string()).optional(),
    slug_wp: z.string().optional(), // original WP slug for redirects
    pubDate: z.date().optional(),
  }),
});

export const collections = { patologie };
