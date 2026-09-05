// @ts-check
import { defineConfig } from "astro/config";

export default defineConfig({
  site: "https://studio.alvaroalija.com",
  output: "static",
  markdown: {
    shikiConfig: {
      theme: "github-dark",
    },
  },
});
