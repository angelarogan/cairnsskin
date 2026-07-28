# Contributing

## Branching

- `main` is production (auto-deployed by Netlify). Never commit
  directly to it.
- Create feature branches from `main`, e.g. `build/astro-v1`,
  `content/rejuran-hub`, `fix/nav-contrast`.
- Open a pull request into `main` when ready for review. Merge only
  after explicit approval.

## Commit messages

Use conventional, descriptive prefixes:

```
chore: initialise Astro project
feat: add global design system
feat: build homepage structure
feat: add content collections
feat: add question article template
feat: add treatment and concern routing
feat: add metadata and structured data
docs: add content and compliance guidance
fix: correct focus ring contrast on glass nav
content: add draft rejuran question set
```

## Before opening a PR

```bash
npm run check    # Astro + TypeScript diagnostics
npm run build    # production build must succeed
```

Health/treatment content changes must also pass
`COMPLIANCE_CHECKLIST.md`.
