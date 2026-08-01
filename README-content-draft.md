# Daily content draft pipeline

Fully unattended daily drafting for the Knowledge Library. This is separate
from, and runs after, the [content-opportunity radar](README-radar.md).

## How it works

1. **Radar** (`.github/workflows/skin-question-radar.yml`, 20:30 UTC / 6:30am
   Queensland) collects real search demand and writes
   `reports/content-opportunities.md` straight to `main`.
2. **Draft** (`.github/workflows/daily-content-draft.yml`, 22:00 UTC / 8:00am
   Queensland) reads that report, drafts up to 3 new articles with the
   Anthropic API (`scripts/draft_daily_content.py`), verifies the site still
   builds, then opens a pull request. It never pushes to `main` directly.
3. **You** review the PR, on GitHub mobile or otherwise. Merging it publishes
   the new articles (they're written with publish-ready frontmatter, since
   merging the PR *is* the approval step); closing it discards them.

## One-time setup

- **Secret**: `ANTHROPIC_API_KEY` in Settings > Secrets and variables >
  Actions. This is billed to your own Anthropic Console account
  (console.anthropic.com), separate from any Claude Code subscription.
- **Repo setting**: Settings > Actions > General > Workflow permissions >
  enable "Allow GitHub Actions to create and approve pull requests". Without
  this, `gh pr create` in the workflow will fail.
- **GitHub mobile app**: enable push notifications for this repo (or at
  least "Participating and @mentions", since the workflow explicitly
  requests you as reviewer on every PR) so you're pinged the moment a draft
  is ready.

## Manual run

Trigger `Cairns Skin Daily Content Draft` from the Actions tab
(`workflow_dispatch`) to draft immediately instead of waiting for the
schedule.

## Fallback topics

If `reports/content-opportunities.md` has fewer than 3 usable (not already
covered) opportunities, the script falls back to
`.claude/content-rotation-state.json`, a fixed rotation of skin-concern
topics, advancing one step only if actually used.

## Query-to-article log

Every drafted article is appended to `reports/articles-from-radar.csv`
(date, source query, article slug/title), which the radar script reads back
into `reports/weekly-top-searches.md` so the weekly top-10 rollup shows
which searches already have an article.
