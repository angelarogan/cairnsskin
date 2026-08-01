import { defineConfig } from "astro/config";
import tailwind from "@astrojs/tailwind";
import mdx from "@astrojs/mdx";
import sitemap from "@astrojs/sitemap";
import { readdirSync, readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Maps each content page's URL path to a real editorial date (updatedDate,
// falling back to publishDate then reviewDate), read directly from
// frontmatter, so sitemap <lastmod> reflects actual content changes rather
// than incidental file-system timestamps from a git checkout.
function buildLastmodMap() {
  const map = {};
  const collections = [
    { dir: "questions", route: "questions" },
    { dir: "concerns", route: "skin-concerns" },
    { dir: "treatments", route: "treatments" },
  ];
  for (const { dir, route } of collections) {
    const collectionPath = path.join(__dirname, "src/content", dir);
    let files;
    try {
      files = readdirSync(collectionPath);
    } catch {
      continue;
    }
    for (const file of files) {
      if (!file.endsWith(".mdx") && !file.endsWith(".md")) continue;
      const slug = file.replace(/\.mdx?$/, "");
      const content = readFileSync(path.join(collectionPath, file), "utf-8");
      const match =
        content.match(/^updatedDate:\s*(\d{4}-\d{2}-\d{2})/m) ||
        content.match(/^publishDate:\s*(\d{4}-\d{2}-\d{2})/m) ||
        content.match(/^reviewDate:\s*(\d{4}-\d{2}-\d{2})/m);
      if (match) {
        map[`/${route}/${slug}/`] = match[1];
      }
    }
  }
  return map;
}

const lastmodMap = buildLastmodMap();

// https://astro.build/config
export default defineConfig({
  site: "https://cairnsskin.com.au",
  integrations: [
    tailwind({
      applyBaseStyles: false,
    }),
    mdx(),
    sitemap({
      serialize(item) {
        const lastmod = lastmodMap[new URL(item.url).pathname];
        if (lastmod) {
          item.lastmod = lastmod;
        }
        return item;
      },
    }),
  ],
  markdown: {
    shikiConfig: {
      theme: "github-light",
    },
  },
});
