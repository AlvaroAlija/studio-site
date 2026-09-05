// @ts-check
import { defineConfig } from "astro/config";

export default defineConfig({
  site: "https://alvaro.works",
  output: "static",
  markdown: {
    shikiConfig: {
      theme: "github-dark",
    },
  },
});
