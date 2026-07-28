# Project overview

## Purpose

Cairns Skin answers the specific skin, skincare and non-prescription
treatment questions people ask search engines and AI assistants. It is
an educational resource, not a booking or e-commerce site — its job is
to be the clearest, most trustworthy answer to a given question, and to
connect readers to Laser Clinics Cairns when a consultation is the
right next step.

## Architecture

- **Astro** (static output) for pages and routing.
- **Tailwind CSS** for styling, configured with a bespoke neutral +
  eucalyptus design token set (see `tailwind.config.mjs`).
- **Astro Content Collections** (`src/content/`) for `questions`,
  `concerns`, `treatments`, `authors` — schema-validated in
  `src/content/config.ts`.
- **`src/data/treatments.ts`** is the single source of truth for
  Laser Clinics treatment names and verification status. Content
  files reference it by key rather than duplicating names.
- **Pagefind** generates a static search index at build time — no
  hosted search service, near-zero runtime JavaScript.
- Minimal client-side JS: only the mobile-menu toggle currently uses
  an inline `<script>`. No framework (React/Vue) is used unless a
  component genuinely requires interactivity.

## Design language

Black, soft black, white, warm white, stone/charcoal greys, with a
single restrained eucalyptus accent (`#9EADA3` family) used only for
small interface details — links, focus rings, active states, primary
CTAs. Glassmorphism is intentionally subtle: fine borders, light
backdrop blur, soft shadows — never neon, heavy blur or bright
gradients. See `.glass`, `.glass-nav`, `.glass-card` utility classes
in `src/styles/global.css`.

## Content principles

- Every question article answers one primary question directly in
  its opening paragraph, then expands.
- Treatment terminology always comes from `src/data/treatments.ts`,
  never typed freely into an article.
- All health/treatment content ships as `draft: true` until a human
  clinical and compliance reviewer marks it `reviewStatus: "published"`.
  See `COMPLIANCE_CHECKLIST.md`.

## GitHub workflow

- `main` is production and is what Netlify deploys.
- All work happens on branches (e.g. `build/astro-v1`), with logical,
  clearly-labelled commits.
- Nothing merges to `main` without explicit human review and approval.

## Deployment workflow

Netlify builds with `npm run build` and publishes `dist/`. No DNS or
domain configuration is touched by this repository — the custom
domain is managed directly in Netlify's site settings.

## Review process

Health and treatment content moves through `draft` →
`clinical-review` → `compliance-review` → `approved` → `published`
(the `reviewStatus` frontmatter field). Only `published` content with
`draft: false` is intended to render publicly — page-level guards
should filter on both fields.

## Future automation plan

The repository is structured so an automated pipeline can later:

1. Take a new question from a content backlog.
2. Generate a Markdown/MDX draft (`reviewStatus: "draft"`).
3. Commit the draft to a review branch.
4. Route it through human fact, tone, clinical and compliance review.
5. Merge via approved pull request once `reviewStatus: "published"`.
6. Let Netlify deploy automatically.

No part of this pipeline auto-publishes unreviewed health content.
