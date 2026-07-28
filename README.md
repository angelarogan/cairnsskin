# Cairns Skin

Educational skin knowledge platform connected to Laser Clinics Cairns.
Live at [cairnsskin.com.au](https://cairnsskin.com.au).

Built with Astro, TypeScript and Tailwind CSS. Deployed on Netlify from
the `main` branch of this repository.

## Quickstart

```bash
npm install
npm run dev       # http://localhost:4321
npm run build     # static build to /dist, includes Pagefind search index
npm run preview   # preview the production build locally
npm run check     # Astro + TypeScript diagnostics
```

## Documentation

- [`PROJECT.md`](./PROJECT.md) — architecture, design language, workflow
- [`CONTENT_GUIDE.md`](./CONTENT_GUIDE.md) — how to add or edit content
- [`COMPLIANCE_CHECKLIST.md`](./COMPLIANCE_CHECKLIST.md) — pre-publication
  review checklist for health and treatment content
- [`CONTRIBUTING.md`](./CONTRIBUTING.md) — branching and commit conventions

## Deployment

Netlify auto-deploys every commit pushed to `main`. Feature work happens
on branches (e.g. `build/astro-v1`) and is merged via reviewed pull
request — never pushed to `main` directly.
