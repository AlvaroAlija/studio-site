// @ts-check
import { defineConfig } from "astro/config";

export default defineConfig({
  site: "https://alvaroalija.com",
  output: "static",
  markdown: {
    shikiConfig: {
      theme: "github-dark",
    },
  },
});
