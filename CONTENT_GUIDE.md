# Content guide

## Adding a question article

1. Create a new `.mdx` file in `src/content/questions/`, slug-named
   (e.g. `what-is-rejuran.mdx`).
2. Fill in the frontmatter — see `src/content/config.ts` for the full
   schema. At minimum: `title`, `slug`, `primaryQuestion`,
   `shortAnswer`, `description`, `category`, `author`.
3. Leave `draft: true` and `reviewStatus: "draft"` until reviewed.
4. Reference related content by collection + id, e.g.:
   ```yaml
   relatedTreatments:
     - collection: treatments
       id: rejuran
   ```
5. Write the opening paragraph as a direct answer to
   `primaryQuestion` — no throat-clearing or generic intros.
6. If the article references treatment names, use the `displayName`
   from `src/data/treatments.ts`, not free text.

## Adding a concern or treatment page

Same pattern, in `src/content/concerns/` or `src/content/treatments/`.
Treatment pages must set `treatmentDataKey` to match an entry in
`src/data/treatments.ts`.

## Writing style

- Answer the question in the first sentence or two.
- Plain English. Define clinical terms the first time they're used.
- Discuss benefits *and* limitations, side effects, suitability and
  when a consultation is appropriate — see
  `COMPLIANCE_CHECKLIST.md`.
- Don't mechanically hedge every sentence with "may" — write
  naturally while staying accurate.
- Don't invent statistics, sources, credentials or outcomes.

## Publishing checklist

Before flipping `draft: false` / `reviewStatus: "published"`, run
through `COMPLIANCE_CHECKLIST.md` in full.
