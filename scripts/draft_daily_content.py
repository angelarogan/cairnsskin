#!/usr/bin/env python3
"""draft_daily_content.py

Fully unattended daily content drafting for Cairns Skin.

Reads real search-demand data from reports/content-opportunities.md
(written earlier the same morning by the separate
scripts/skin_question_radar.py, run by its own GitHub Actions workflow),
drafts up to 3 new Knowledge Library question articles using the
Anthropic API with its built-in web search tool for research, cross-
links them into the relevant existing concern/treatment pages, and
writes the files straight to disk.

This script never merges or pushes anything itself. The surrounding
GitHub Actions workflow (.github/workflows/daily-content-draft.yml)
commits whatever this script wrote to a fresh branch and opens a pull
request for human review on GitHub; nothing goes live until that PR is
merged by the site owner. Because merging the PR *is* the human
approval step, articles are written with publish-ready frontmatter
(reviewStatus: published, draft: false) rather than a draft flag: the
un-merged PR is the draft state.

Credentials are read from environment variables only:
    ANTHROPIC_API_KEY
    GITHUB_TOKEN, GITHUB_REPOSITORY   optional; both are auto-provided in
        GitHub Actions. If set, still-open content-draft PRs are checked
        for duplication too, not just what's merged on main. Without
        these the script still runs fine, just with a smaller view of
        what's already been drafted.

To keep daily drafting spread across all ten concerns rather than
repeatedly mining whichever one currently has the most autocomplete
variants, a concern that already had a question published (or is
sitting in a still-open PR) within CONCERN_COOLDOWN_DAYS is skipped in
favour of the next candidate.

Outputs (relative to repo root):
    src/content/questions/<new-slug>.mdx    one file per drafted article
    reports/articles-from-radar.csv         appended, links query -> slug

Usage:
    python scripts/draft_daily_content.py
"""

from __future__ import annotations

import base64
import csv
import json
import logging
import os
import re
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import anthropic
import requests

# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------

# Queensland has no daylight saving, so it's always a fixed UTC+10. GitHub
# Actions runners use UTC, so date.today() there can be a day behind what
# a Cairns reader would call "today" for several hours each morning.
# Matches the same helper in skin_question_radar.py, so both scripts'
# "today" always agrees.
QUEENSLAND_UTC_OFFSET = timezone(timedelta(hours=10))


def queensland_today() -> date:
    return datetime.now(QUEENSLAND_UTC_OFFSET).date()

REPO_ROOT = Path(__file__).resolve().parent.parent
QUESTIONS_DIR = REPO_ROOT / "src" / "content" / "questions"
CONCERNS_DIR = REPO_ROOT / "src" / "content" / "concerns"
TREATMENTS_DIR = REPO_ROOT / "src" / "content" / "treatments"
OPPORTUNITIES_REPORT = REPO_ROOT / "reports" / "content-opportunities.md"
ROTATION_STATE_PATH = REPO_ROOT / ".claude" / "content-rotation-state.json"
EXCLUDED_TOPICS_PATH = REPO_ROOT / ".claude" / "excluded-topics.json"
ARTICLES_LOG_PATH = REPO_ROOT / "reports" / "articles-from-radar.csv"
ARTICLES_LOG_FIELDNAMES: tuple[str, ...] = (
    "date",
    "query",
    "article_slug",
    "article_title",
    "collection",
)

MODEL = "claude-sonnet-5"
MAX_ARTICLES_PER_RUN = 3
# A cooldown skip still costs an API call, so cap total attempts per run
# well above MAX_ARTICLES_PER_RUN to bound worst-case cost if the
# candidate pool is unusually full of same-concern queries. Raised from
# an initial 8 to 20 after a real run's top opportunities were 8+
# variations of "aquafacial" (all landing on the same concern): once the
# first one succeeded, the cooldown correctly rejected the rest, but 8
# attempts wasn't enough headroom to reach 3 genuinely different
# concerns before running out.
MAX_DRAFT_ATTEMPTS = 20
MAX_TOKENS = 4096
GITHUB_API_URL = "https://api.github.com"
# Don't redraft into a concern that already had a question published (or
# is sitting in a still-open, unmerged PR) within this many days, so
# daily drafting spreads across all ten concerns rather than repeatedly
# mining whichever one currently has the most autocomplete variants
# (acne and pigmentation dominate the raw demand data).
CONCERN_COOLDOWN_DAYS = 3

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("draft_daily_content")


class MissingCredentialError(RuntimeError):
    """Raised when a required environment variable / secret is not set."""


def require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise MissingCredentialError(f"Required environment variable '{name}' is not set.")
    return value


# --------------------------------------------------------------------------
# Reading the repo's existing content (duplication checks + cross-link map)
# --------------------------------------------------------------------------


def _extract_frontmatter_string(text: str, field_name: str) -> str | None:
    """Extracts a simple quoted-string frontmatter value, e.g. title: "...".

    Deliberately avoids a YAML parser dependency, matching the convention
    already used by scripts/skin_question_radar.py: every frontmatter
    field this script cares about is written as a single quoted string on
    its own line, consistently, across this project's content.
    """
    pattern = re.compile(rf'^{re.escape(field_name)}:\s*"([^"]+)"', re.MULTILINE)
    found = pattern.search(text)
    return found.group(1) if found else None


def _extract_reference_slugs(text: str, field_name: str) -> list[str]:
    """Extracts slugs from a YAML list-of-references block, e.g.:

        relatedQuestions:
          - collection: questions
            slug: some-slug

    Regex-based rather than a YAML parser, matching this project's
    frontmatter convention.
    """
    block_pattern = re.compile(rf"^{re.escape(field_name)}:\s*\n((?:[ \t]+.*\n?)*)", re.MULTILINE)
    match = block_pattern.search(text)
    if not match:
        return []
    return re.findall(r"slug:\s*(\S+)", match.group(1))


def _extract_frontmatter_date(text: str, field_name: str) -> date | None:
    """Extracts a bare, unquoted YAML date value, e.g. publishDate: 2026-08-03
    (dates in this project's frontmatter are never quoted, unlike the
    string fields _extract_frontmatter_string handles)."""
    pattern = re.compile(rf"^{re.escape(field_name)}:\s*(\d{{4}}-\d{{2}}-\d{{2}})", re.MULTILINE)
    found = pattern.search(text)
    if not found:
        return None
    try:
        return date.fromisoformat(found.group(1))
    except ValueError:
        return None


def load_existing_coverage() -> dict[str, str]:
    """Builds a lookup of lowercase title/question/summary text -> slug
    for every piece of content in the repo, mirroring
    skin_question_radar.py's duplication check.
    """
    coverage: dict[str, str] = {}
    for directory in (QUESTIONS_DIR, CONCERNS_DIR, TREATMENTS_DIR):
        if not directory.exists():
            continue
        for path in sorted(directory.glob("*.mdx")):
            text = path.read_text(encoding="utf-8")
            slug = path.stem
            for field_name in ("title", "primaryQuestion", "shortSummary"):
                value = _extract_frontmatter_string(text, field_name)
                if value:
                    coverage[value.lower()] = slug
    return coverage


def find_existing_match(query: str, coverage: dict[str, str]) -> str | None:
    """Approximate duplicate check, identical logic to
    skin_question_radar.py's find_existing_match.
    """
    query_words = {word for word in query.lower().split() if len(word) > 3}
    if not query_words:
        return None
    for text, slug in coverage.items():
        text_words = set(text.split())
        overlap = query_words & text_words
        if len(overlap) >= max(2, len(query_words) // 2):
            return slug
    return None


def load_recently_used_concerns(cooldown_days: int) -> set[str]:
    """Concerns whose most recently published question falls within the
    cooldown window. See CONCERN_COOLDOWN_DAYS for why this exists.
    """
    cutoff = queensland_today() - timedelta(days=cooldown_days)
    recent: set[str] = set()
    for path in QUESTIONS_DIR.glob("*.mdx"):
        text = path.read_text(encoding="utf-8")
        publish_date = _extract_frontmatter_date(text, "publishDate")
        if publish_date and publish_date >= cutoff:
            recent.update(_extract_reference_slugs(text, "relatedConcern"))
    return recent


def fetch_open_pr_coverage(
    repo_full_name: str | None, github_token: str | None
) -> tuple[dict[str, str], set[str]]:
    """Extends duplication and concern-cooldown checking to cover
    questions sitting in still-open, unmerged content-draft PRs, not just
    what's already on main. Without this, two separate daily runs can
    each independently draft a very similar article on consecutive days,
    since neither run's coverage check can see the other's not-yet-merged
    work (this is exactly what produced two near-duplicate acne-scarring
    articles on 2026-08-03 and 2026-08-04).

    Best-effort: any failure (missing token, network issue, rate limit)
    is logged and treated as no extra coverage, rather than failing the
    whole run, since this is additive on top of the main-branch check,
    not a hard requirement.

    Returns (title_text_coverage, concern_slugs_pending_in_open_prs).
    """
    coverage: dict[str, str] = {}
    pending_concerns: set[str] = set()

    if not repo_full_name or not github_token:
        logger.info("No GITHUB_REPOSITORY/GITHUB_TOKEN set; skipping open-PR coverage check.")
        return coverage, pending_concerns

    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json",
    }

    try:
        prs_response = requests.get(
            f"{GITHUB_API_URL}/repos/{repo_full_name}/pulls",
            headers=headers,
            params={"state": "open", "base": "main", "per_page": 50},
            timeout=30,
        )
        prs_response.raise_for_status()
        pulls = prs_response.json()
    except requests.RequestException as exc:
        logger.warning("Could not list open pull requests: %s", exc)
        return coverage, pending_concerns

    for pr in pulls:
        head_sha = pr.get("head", {}).get("sha")
        if not head_sha:
            continue
        try:
            tree_response = requests.get(
                f"{GITHUB_API_URL}/repos/{repo_full_name}/git/trees/{head_sha}",
                headers=headers,
                params={"recursive": "1"},
                timeout=30,
            )
            tree_response.raise_for_status()
            tree = tree_response.json()
        except requests.RequestException as exc:
            logger.warning("Could not read tree for PR #%s: %s", pr.get("number"), exc)
            continue

        question_blobs = [
            item
            for item in tree.get("tree", [])
            if item.get("type") == "blob"
            and item.get("path", "").startswith("src/content/questions/")
            and item.get("path", "").endswith(".mdx")
        ]
        for item in question_blobs:
            try:
                blob_response = requests.get(item["url"], headers=headers, timeout=30)
                blob_response.raise_for_status()
                blob = blob_response.json()
                content = base64.b64decode(blob["content"]).decode("utf-8")
            except (requests.RequestException, KeyError, ValueError) as exc:
                logger.warning("Could not read blob %s: %s", item.get("path"), exc)
                continue
            slug = Path(item["path"]).stem
            for field_name in ("title", "primaryQuestion", "shortSummary"):
                value = _extract_frontmatter_string(content, field_name)
                if value:
                    coverage[value.lower()] = slug
            pending_concerns.update(_extract_reference_slugs(content, "relatedConcern"))

    logger.info(
        "Loaded coverage from %d open pull request(s), %d pending concern(s)",
        len(pulls),
        len(pending_concerns),
    )
    return coverage, pending_concerns


def build_site_map() -> dict[str, Any]:
    """Builds a compact catalogue of existing concerns, treatments, and
    their current sibling questions, so the model can pick accurate
    relatedConcern / relatedTreatments / relatedQuestions slugs instead
    of guessing at ones that don't exist.
    """
    question_titles: dict[str, str] = {}
    for path in sorted(QUESTIONS_DIR.glob("*.mdx")):
        text = path.read_text(encoding="utf-8")
        title = _extract_frontmatter_string(text, "title")
        if title:
            question_titles[path.stem] = title

    concerns: dict[str, dict[str, Any]] = {}
    for path in sorted(CONCERNS_DIR.glob("*.mdx")):
        text = path.read_text(encoding="utf-8")
        slug = path.stem
        concerns[slug] = {
            "title": _extract_frontmatter_string(text, "title") or slug,
            "shortSummary": _extract_frontmatter_string(text, "shortSummary") or "",
            "existingQuestions": _extract_reference_slugs(text, "relatedQuestions"),
        }

    treatments: dict[str, dict[str, Any]] = {}
    for path in sorted(TREATMENTS_DIR.glob("*.mdx")):
        text = path.read_text(encoding="utf-8")
        slug = path.stem
        treatments[slug] = {
            "title": _extract_frontmatter_string(text, "title") or slug,
            "shortSummary": _extract_frontmatter_string(text, "shortSummary") or "",
        }

    return {"concerns": concerns, "treatments": treatments, "question_titles": question_titles}


# --------------------------------------------------------------------------
# Reading today's real demand data
# --------------------------------------------------------------------------

_OPPORTUNITY_ROW_PATTERN = re.compile(
    r"^\|\s*(?P<query>[^|]+?)\s*\|\s*(?P<source>[^|]+?)\s*\|\s*"
    r"(?P<impressions>[^|]+?)\s*\|\s*(?P<position>[^|]+?)\s*\|\s*(?P<score>[^|]+?)\s*\|\s*$"
)


def read_top_opportunities(path: Path, limit: int = 10) -> list[dict[str, str]]:
    """Parses the "Top opportunities" markdown table written by
    skin_question_radar.py into a list of {query, source, score} dicts,
    highest score first. Returns an empty list if the report doesn't
    exist yet or has no usable rows.
    """
    if not path.exists():
        logger.warning("No opportunities report at %s", path)
        return []

    lines = path.read_text(encoding="utf-8").splitlines()
    try:
        start = next(i for i, line in enumerate(lines) if line.strip() == "## Top opportunities")
    except StopIteration:
        return []

    rows: list[dict[str, str]] = []
    for line in lines[start + 1 :]:
        if line.startswith("## "):
            break
        match = _OPPORTUNITY_ROW_PATTERN.match(line)
        if not match:
            continue
        query = match.group("query").strip()
        if query == "Query" or re.fullmatch(r"[-:]+", query):
            continue
        rows.append(
            {
                "query": query,
                "source": match.group("source").strip(),
                "score": match.group("score").strip(),
            }
        )
    return rows[:limit]


def load_excluded_topics() -> list[str]:
    """Reads a permanent, site-owner-maintained list of topics that should
    never be drafted again, e.g. because a previous draft on that topic
    was deliberately removed. Matched as a case-insensitive substring
    against each candidate query, since real demand data rarely repeats a
    topic with identical phrasing day to day.
    """
    if not EXCLUDED_TOPICS_PATH.exists():
        return []
    data = json.loads(EXCLUDED_TOPICS_PATH.read_text(encoding="utf-8"))
    return [str(topic).lower() for topic in data.get("excluded_query_substrings", [])]


def is_excluded_topic(query: str, excluded_substrings: list[str]) -> bool:
    lowered = query.lower()
    return any(substring in lowered for substring in excluded_substrings)


def load_rotation_state() -> dict[str, Any]:
    if not ROTATION_STATE_PATH.exists():
        return {"topics": [], "nextIndex": 0}
    return json.loads(ROTATION_STATE_PATH.read_text(encoding="utf-8"))


def save_rotation_state(state: dict[str, Any], used_slugs: list[str], today_str: str) -> None:
    state["lastRunDate"] = today_str
    state["lastRunSlugs"] = used_slugs
    ROTATION_STATE_PATH.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


# --------------------------------------------------------------------------
# Drafting via the Anthropic API
# --------------------------------------------------------------------------

SYSTEM_PROMPT = """You are drafting a Knowledge Library article for Cairns Skin \
(cairnsskin.com.au), an educational skin-knowledge site for a tropical Far \
North Queensland audience, connected to a real clinic but written as an \
independent, honest information resource rather than marketing copy.

Content rules, no exceptions:
- Australian English spelling throughout (colour, organise, recognise, \
moisturiser, ageing, etc).
- Never use an em dash. Use commas, colons, full stops, or rewrite instead.
- Never name "Laser Clinics" or any specific clinic brand in the body text.
- Never name or recommend a specific third-party retailer or store.
- Never frame shop-bought or pharmacy products as the primary or best way to \
solve a concern, even when the query is literally asking where to buy \
something. Reframe toward education instead: what actives/ingredients \
actually matter and why, what concentration and formulation questions to \
ask, and what limits a shop-bought product has. Where relevant, note that a \
professional consultation can identify what's actually right for someone's \
specific skin, a person considering shop-bought options because they \
haven't had professional advice yet is exactly who this framing should \
speak to, without ever naming a clinic or brand.
- `sources` always stays an empty array `[]`. This site deliberately \
doesn't link out to external articles or citations, for consistency \
across every page, so never populate this field even if your web search \
surfaced a genuine, checkable source. Use that research to write \
accurately and confidently in your own words instead (e.g. "research on \
combining X and Y has found..." rather than naming or linking a specific \
study), and never invent a study, statistic, or citation that doesn't \
correspond to something you actually found.
- `body_markdown` must be clean prose only, plain Markdown headings and \
paragraphs, nothing else. Never include HTML or citation markup such as \
`<cite>`, footnote brackets, or reference indices, these are search-tool \
artefacts and must not appear in the output. If you want to reference \
something a real source said, paraphrase it in plain English or use a \
short plain-text attribution phrase (e.g. "one pharmacy brand's own \
packaging states..."), don't embed markup in the body to mark where a \
quote came from, and remember `sources` stays `[]` regardless.
- Do not echo any clinic chain's marketing copy verbatim or near-verbatim; \
write independently in plain English, even when covering a treatment or \
product category they also offer.
- Do not contradict how a mainstream Australian clinic chain would describe \
a treatment (dermal fillers, laser, skin needling etc all carry real, \
non-guaranteed outcomes).
- No guaranteed-results language, no invented professional credentials.
- Answer the actual question directly in the first sentence or two, then \
cover realistic benefits and limitations where relevant.
- Body markdown should use "## Heading" sections, no leading title heading \
(the page template renders the title separately), roughly 300-500 words.

You will be given a raw search query or topic, and a catalogue of the \
site's existing concern and treatment pages (with their exact slugs) to \
cross-link into. Research the query with web search first to understand \
what people actually mean by it and what a genuinely useful, accurate \
answer looks like: a raw autocomplete fragment is not a finished question, \
turn it into a real, natural question that captures the real intent.

Respond with ONLY a single JSON object, no markdown code fences, no \
commentary before or after it, matching exactly this shape:

{
  "slug": "kebab-case-slug-for-the-url",
  "title": "The natural question as a title",
  "primaryQuestion": "The same natural question",
  "shortAnswer": "Direct answer in under 320 characters",
  "description": "One sentence meta description",
  "category": "short category label, e.g. pigmentation",
  "relatedConcern": "exact-slug-from-the-provided-concern-list",
  "relatedTreatments": ["exact-slug-1", "exact-slug-2"],
  "relatedQuestions": ["exact-sibling-slug-if-genuinely-relevant"],
  "tags": ["short", "lowercase", "tags"],
  "evidenceLevel": "established|emerging|manufacturer-claim|clinical-experience|limited-evidence",
  "ahpraRisk": "low|moderate|high",
  "sources": [],
  "body_markdown": "## First heading\\n\\nBody text..."
}

relatedConcern must be exactly one slug from the provided list. \
relatedTreatments and relatedQuestions may be empty arrays if nothing \
genuinely fits, do not force a link that isn't relevant."""


def _extract_json_object(text: str) -> dict[str, Any] | None:
    text = text.strip()
    candidates = [text]
    fence_match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.DOTALL)
    if fence_match:
        candidates.append(fence_match.group(1))
    first_brace = text.find("{")
    last_brace = text.rfind("}")
    if first_brace != -1 and last_brace > first_brace:
        candidates.append(text[first_brace : last_brace + 1])
    for candidate in candidates:
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            continue
    return None


def draft_article(
    client: anthropic.Anthropic,
    opportunity: dict[str, str],
    site_map: dict[str, Any],
    used_slugs: set[str],
) -> dict[str, Any] | None:
    concern_lines: list[str] = []
    for slug, info in site_map["concerns"].items():
        concern_lines.append(f"- {slug}: {info['title']} -- {info['shortSummary']}")
        for sibling_slug in info["existingQuestions"]:
            sibling_title = site_map["question_titles"].get(sibling_slug, sibling_slug)
            concern_lines.append(f"    sibling question slug: {sibling_slug} ({sibling_title})")

    treatment_lines = [
        f"- {slug}: {info['title']} -- {info['shortSummary']}"
        for slug, info in site_map["treatments"].items()
    ]

    user_prompt = (
        f'Search query to turn into an article: "{opportunity["query"]}"\n'
        f"Demand signal: source={opportunity['source']}, score={opportunity['score']}\n\n"
        "Existing concern pages (relatedConcern must be exactly one of these slugs):\n"
        + "\n".join(concern_lines)
        + "\n\nExisting treatment pages (pick 0-2 exact slugs for relatedTreatments, only if relevant):\n"
        + "\n".join(treatment_lines)
        + f"\n\nSlugs already used today, do not reuse: {sorted(used_slugs) or 'none'}\n\n"
        "Research this query with web search, then respond with only the JSON object described "
        "in your instructions."
    )

    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=SYSTEM_PROMPT,
        tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 5}],
        messages=[{"role": "user", "content": user_prompt}],
    )

    final_text = "".join(
        block.text for block in response.content if getattr(block, "type", None) == "text"
    )
    return _extract_json_object(final_text)


def check_content_rules(payload: dict[str, Any]) -> list[str]:
    """Hard gate mirroring this project's standing content rules. Any
    violation means the article is skipped entirely rather than
    auto-fixed, since silently rewriting text risks introducing new
    errors.
    """
    violations: list[str] = []
    required_fields = ("title", "primaryQuestion", "shortAnswer", "description", "category", "body_markdown")
    for field_name in required_fields:
        if not payload.get(field_name):
            violations.append(f"missing required field '{field_name}'")

    combined = "\n".join(str(payload.get(f, "")) for f in required_fields)
    if "—" in combined:
        violations.append("contains an em dash")
    if "laser clinics" in combined.lower():
        violations.append("mentions Laser Clinics by name")
    if re.search(r"<cite\b|<sup\b|\[\d+\]", str(payload.get("body_markdown", ""))):
        violations.append("body_markdown contains leftover citation/HTML markup")
    if len(str(payload.get("shortAnswer", ""))) > 320:
        violations.append("shortAnswer exceeds 320 characters")
    return violations


# --------------------------------------------------------------------------
# Writing output
# --------------------------------------------------------------------------


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def render_frontmatter(payload: dict[str, Any], today_str: str) -> str:
    def q(value: str) -> str:
        return json.dumps(value)

    lines = [
        "---",
        f"title: {q(payload['title'])}",
        f"primaryQuestion: {q(payload['primaryQuestion'])}",
        f"shortAnswer: {q(payload['shortAnswer'])}",
        f"description: {q(payload['description'])}",
        f"category: {q(payload['category'])}",
    ]

    related_concern = payload.get("relatedConcern")
    if related_concern:
        lines += ["relatedConcern:", "  - collection: concerns", f"    slug: {related_concern}"]

    related_treatments = payload.get("relatedTreatments") or []
    if related_treatments:
        lines.append("relatedTreatments:")
        for slug in related_treatments:
            lines += ["  - collection: treatments", f"    slug: {slug}"]

    related_questions = payload.get("relatedQuestions") or []
    if related_questions:
        lines.append("relatedQuestions:")
        for slug in related_questions:
            lines += ["  - collection: questions", f"    slug: {slug}"]

    tags = payload.get("tags") or []
    if tags:
        lines.append("tags:")
        for tag in tags:
            lines.append(f"  - {q(str(tag))}")

    lines += [
        "author:",
        "  collection: authors",
        "  slug: example-author",
        "reviewStatus: published",
        f"reviewDate: {today_str}",
        f"publishDate: {today_str}",
        f"evidenceLevel: {payload.get('evidenceLevel', 'clinical-experience')}",
    ]

    source_lines: list[str] = []
    for source in payload.get("sources") or []:
        if not isinstance(source, dict) or not source.get("label"):
            continue
        source_lines.append(f"  - label: {q(str(source['label']))}")
        if source.get("url"):
            source_lines.append(f"    url: {q(str(source['url']))}")
        if source.get("publisher"):
            source_lines.append(f"    publisher: {q(str(source['publisher']))}")
        if source.get("year"):
            source_lines.append(f"    year: {int(source['year'])}")

    if source_lines:
        # Only emit the "sources:" header once at least one entry survived
        # filtering: a header with no list items under it parses in YAML as
        # null, not [], which fails the schema's z.array() validation.
        lines.append("sources:")
        lines.extend(source_lines)
    else:
        lines.append("sources: []")

    lines += [
        "featured: false",
        "draft: false",
        f"ahpraRisk: {payload.get('ahpraRisk', 'low')}",
        "clinicVerificationRequired: true",
        "---",
        "",
    ]
    return "\n".join(lines)


def write_article(payload: dict[str, Any], slug: str, today_str: str) -> Path:
    frontmatter = render_frontmatter(payload, today_str)
    body = str(payload["body_markdown"]).strip() + "\n"
    path = QUESTIONS_DIR / f"{slug}.mdx"
    path.write_text(frontmatter + "\n" + body, encoding="utf-8")
    return path


def append_related_question(path: Path, new_slug: str) -> bool:
    """Appends `new_slug` to a concern/treatment file's relatedQuestions
    list. Returns False if the slug is already present or no
    relatedQuestions block was found to append to.
    """
    text = path.read_text(encoding="utf-8")
    entry = f"  - collection: questions\n    slug: {new_slug}\n"
    if entry in text:
        return False
    match = re.search(r"^relatedQuestions:\s*\n((?:[ \t]+.*\n?)*)", text, re.MULTILINE)
    if not match:
        logger.warning("No relatedQuestions block in %s; skipping cross-link", path)
        return False
    insertion_point = match.end()
    path.write_text(text[:insertion_point] + entry + text[insertion_point:], encoding="utf-8")
    return True


def append_articles_log(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    is_new_file = not path.exists()
    with path.open("a", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=list(ARTICLES_LOG_FIELDNAMES))
        if is_new_file:
            writer.writeheader()
        for row in rows:
            writer.writerow(row)
    logger.info("Appended %d rows to %s", len(rows), path)


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------


def main() -> int:
    try:
        api_key = require_env("ANTHROPIC_API_KEY")
    except MissingCredentialError as exc:
        logger.error(str(exc))
        return 1

    client = anthropic.Anthropic(api_key=api_key)
    today_str = queensland_today().isoformat()

    coverage = load_existing_coverage()
    site_map = build_site_map()

    excluded_topics = load_excluded_topics()

    pr_coverage, pending_concerns = fetch_open_pr_coverage(
        os.environ.get("GITHUB_REPOSITORY"), os.environ.get("GITHUB_TOKEN")
    )
    coverage.update(pr_coverage)
    avoid_concerns = load_recently_used_concerns(CONCERN_COOLDOWN_DAYS) | pending_concerns

    candidates = read_top_opportunities(OPPORTUNITIES_REPORT, limit=MAX_DRAFT_ATTEMPTS)
    candidates = [c for c in candidates if not find_existing_match(c["query"], coverage)]
    candidates = [c for c in candidates if not is_excluded_topic(c["query"], excluded_topics)]

    fallback_used = False
    if len(candidates) < MAX_ARTICLES_PER_RUN:
        state = load_rotation_state()
        topics = state.get("topics", [])
        if topics:
            next_index = state.get("nextIndex", 0) % len(topics)
            fallback_topic = topics[next_index]
            candidates.append(
                {"query": fallback_topic.replace("-", " "), "source": "fallback_rotation", "score": "0"}
            )
            fallback_used = True

    if not candidates:
        logger.info("No candidates available today; nothing to draft.")
        return 0

    used_slugs: set[str] = {p.stem for p in QUESTIONS_DIR.glob("*.mdx")}
    drafted: list[dict[str, str]] = []

    for attempt, opportunity in enumerate(candidates):
        if len(drafted) >= MAX_ARTICLES_PER_RUN or attempt >= MAX_DRAFT_ATTEMPTS:
            break
        try:
            payload = draft_article(client, opportunity, site_map, used_slugs)
        except Exception:
            logger.exception("Drafting failed for query '%s'", opportunity["query"])
            continue
        if payload is None:
            logger.error("Could not parse model output for query '%s'", opportunity["query"])
            continue

        violations = check_content_rules(payload)
        if violations:
            logger.error("Skipping '%s': %s", opportunity["query"], "; ".join(violations))
            continue

        # Drop any relatedConcern/relatedTreatments/relatedQuestions slug the
        # model invented that doesn't actually exist: Astro's reference()
        # schema validation fails the whole build on a dangling reference,
        # so an invalid slug here is worse than just omitting the link.
        if payload.get("relatedConcern") not in site_map["concerns"]:
            payload["relatedConcern"] = None

        related_concern = payload.get("relatedConcern")
        if related_concern and related_concern in avoid_concerns:
            logger.info(
                "Skipping '%s': concern '%s' was drafted too recently, trying the next candidate",
                opportunity["query"],
                related_concern,
            )
            continue

        slug = slugify(payload.get("slug") or payload["title"])
        if not slug or slug in used_slugs:
            slug = f"{slug or 'article'}-{today_str}"
        used_slugs.add(slug)

        payload["relatedTreatments"] = [
            s for s in (payload.get("relatedTreatments") or []) if s in site_map["treatments"]
        ]
        payload["relatedQuestions"] = [
            s
            for s in (payload.get("relatedQuestions") or [])
            if s in site_map["question_titles"] and s != slug
        ]

        path = write_article(payload, slug, today_str)
        logger.info("Wrote %s", path)

        # Keep this run's own picks spread across concerns too, and stop
        # a later candidate in the same batch matching this one's title.
        if related_concern:
            avoid_concerns.add(related_concern)
        for field_name in ("title", "primaryQuestion", "shortAnswer"):
            value = payload.get(field_name)
            if value:
                coverage[str(value).lower()] = slug

        if related_concern in site_map["concerns"]:
            concern_path = CONCERNS_DIR / f"{related_concern}.mdx"
            if concern_path.exists():
                append_related_question(concern_path, slug)

        for treatment_slug in payload.get("relatedTreatments") or []:
            if treatment_slug in site_map["treatments"]:
                treatment_path = TREATMENTS_DIR / f"{treatment_slug}.mdx"
                if treatment_path.exists():
                    append_related_question(treatment_path, slug)

        drafted.append(
            {
                "date": today_str,
                "query": opportunity["query"],
                "article_slug": slug,
                "article_title": str(payload["title"]),
                "collection": "questions",
            }
        )

    if not drafted:
        logger.info("No articles were successfully drafted today.")
        return 0

    append_articles_log(drafted, ARTICLES_LOG_PATH)

    if fallback_used:
        state = load_rotation_state()
        topics = state.get("topics", [])
        if topics:
            state["nextIndex"] = (state.get("nextIndex", 0) + 1) % len(topics)
            save_rotation_state(state, [d["article_slug"] for d in drafted], today_str)

    logger.info("Done. Drafted %d article(s): %s", len(drafted), [d["article_slug"] for d in drafted])
    return 0


if __name__ == "__main__":
    sys.exit(main())
