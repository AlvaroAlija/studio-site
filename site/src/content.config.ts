import { defineCollection, z } from "astro:content";
import { glob } from "astro/loaders";

const devlog = defineCollection({
  loader: glob({ pattern: "*.md", base: "../content/devlog" }),
  schema: z.object({
    title: z.string(),
    date: z.coerce.date(),
    tag: z.enum(["GODOT", "BLENDER", "DEVLOG", "STORE"]),
    excerpt: z.string(),
  }),
});

export const collections = { devlog };
