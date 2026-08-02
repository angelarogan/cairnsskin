#!/usr/bin/env python3
"""skin_question_radar.py

Finds new content opportunities for Cairns Skin by combining two real
demand signals:

  1. Google Autocomplete suggestions for Cairns, collected via
     DataForSEO's SERP "Google Autocomplete" Live Advanced endpoint.
  2. Real query performance for cairnsskin.com.au from Google Search
     Console (impressions, clicks, CTR, average position).

Both signals are cross-checked against the site's existing content
(src/content/questions, concerns, treatments) so an opportunity that's
already covered is deprioritised rather than suggested as new, matching
this project's standing "no duplication" content rule.

Credentials are read from environment variables only, never hardcoded.
In CI, a GitHub Actions workflow maps repository secrets onto these
variables in its `env:` block:

    DATAFORSEO_LOGIN               DataForSEO API login
    DATAFORSEO_PASSWORD            DataForSEO API password
    GOOGLE_SERVICE_ACCOUNT_JSON     Full service-account JSON (as a string)
    GSC_SITE_URL                   Optional. Defaults to the property below.

The Search Console service account must already be added as a user on
the target property in the Search Console UI; this script only reads
data, it cannot grant itself access.

Outputs (relative to the repo root):

    reports/latest.csv                  Today's run only, overwritten daily.
    reports/daily/YYYY-MM-DD.csv         Archived per-day snapshot.
    reports/content-opportunities.md     Today's opportunities, overwritten daily.
    reports/search-log.csv               Every day's rows, appended forever.
    reports/weekly-top-searches.md       Rolling 7-day top 10, recomputed daily
                                          from search-log.csv, cross-checked
                                          against current site content and
                                          against reports/articles-from-radar.csv
                                          (written by the separate content-
                                          drafting workflow) so it shows which
                                          weekly searches already have an
                                          article and which are still open
                                          ideas, e.g. for Instagram planning.

Usage:
    python scripts/skin_question_radar.py

Exit code is non-zero if required credentials are missing or if both
data sources fail, so a CI run fails loudly rather than silently
writing an empty report.
"""

from __future__ import annotations

import csv
import json
import logging
import os
import re
import sys
import time
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import requests
from google.oauth2 import service_account
from googleapiclient.discovery import build as build_google_service
from googleapiclient.errors import HttpError

# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = REPO_ROOT / "reports"
DAILY_REPORTS_DIR = REPORTS_DIR / "daily"
SEARCH_LOG_PATH = REPORTS_DIR / "search-log.csv"
WEEKLY_SUMMARY_PATH = REPORTS_DIR / "weekly-top-searches.md"
# Written by the separate daily content-drafting workflow, not this script.
# Read here (if present) purely to annotate the weekly summary with which
# searches already have an article.
ARTICLES_LOG_PATH = REPORTS_DIR / "articles-from-radar.csv"
WEEKLY_WINDOW_DAYS = 7
CONTENT_DIRS = (
    REPO_ROOT / "src" / "content" / "questions",
    REPO_ROOT / "src" / "content" / "concerns",
    REPO_ROOT / "src" / "content" / "treatments",
)

DATAFORSEO_AUTOCOMPLETE_URL = "https://api.dataforseo.com/v3/serp/google/autocomplete/live/advanced"
DATAFORSEO_LOCATION_NAME = "Cairns,Queensland,Australia"
DATAFORSEO_LANGUAGE_CODE = "en"
DATAFORSEO_TIMEOUT_SECONDS = 30
# Some DataForSEO account tiers only accept one task per request, so
# suggestions are fetched sequentially (see fetch_autocomplete_suggestions).
# This delay is between those sequential requests, to stay well clear of
# rate limits rather than to satisfy the one-task-per-request rule itself.
DATAFORSEO_REQUEST_DELAY_SECONDS = 1.0

# cairnsskin.com.au was verified in Search Console via the HTML-file
# method (googlede9df805273e22ad.html), which Google only supports for
# URL-prefix properties (Domain properties require DNS TXT verification
# instead), so this must be the URL-prefix form, not "sc-domain:...".
DEFAULT_GSC_SITE_URL = "https://cairnsskin.com.au/"
GSC_ROW_LIMIT = 5000
GSC_LOOKBACK_DAYS = 90

# Seed terms used to fan out autocomplete requests. Kept short and broad;
# Google's autocomplete does the work of surfacing real long-tail phrasing
# people actually type, rather than guessing phrasing ourselves.
AUTOCOMPLETE_SEED_TERMS: tuple[str, ...] = (
    "pigmentation",
    "melasma",
    "acne",
    "rosacea",
    "enlarged pores",
    "sun damage",
    "BBL",
    "skin needling",
    "laser hair removal",
    "microdermabrasion",
    "aquafacial",
    "fine lines",
    "sagging skin",
    "dry skin",
    "cairns skin",
)

CSV_FIELDNAMES: tuple[str, ...] = (
    "query",
    "source",
    "impressions",
    "clicks",
    "ctr",
    "position",
    "already_covered",
    "matched_slug",
    "score",
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("skin_question_radar")


class MissingCredentialError(RuntimeError):
    """Raised when a required environment variable / secret is not set."""


@dataclass
class Opportunity:
    """A single candidate query, scored against real demand and existing coverage."""

    query: str
    source: str  # "autocomplete" | "search_console" | "both"
    impressions: int = 0
    clicks: int = 0
    ctr: float = 0.0
    position: float = 0.0
    already_covered: bool = False
    matched_slug: str | None = None
    score: float = 0.0

    def as_row(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "source": self.source,
            "impressions": self.impressions,
            "clicks": self.clicks,
            "ctr": round(self.ctr, 4),
            "position": round(self.position, 2),
            "already_covered": self.already_covered,
            "matched_slug": self.matched_slug or "",
            "score": round(self.score, 2),
        }


# --------------------------------------------------------------------------
# Credential loading
# --------------------------------------------------------------------------


def require_env(name: str) -> str:
    """Reads a required environment variable, raising a clear error if unset.

    Secrets are never fetched from the GitHub API directly; GitHub Actions
    injects them as plain environment variables via the workflow's `env:`
    block, and this function is where the script expects to find them.
    """
    value = os.environ.get(name)
    if not value:
        raise MissingCredentialError(
            f"Required environment variable '{name}' is not set. "
            "In GitHub Actions this must be mapped from a repository "
            "secret of the same name in the workflow's 'env:' block."
        )
    return value


# --------------------------------------------------------------------------
# DataForSEO: Google Autocomplete
# --------------------------------------------------------------------------

# Bare seed terms like "acne" or "aquafacial" sometimes surface unrelated
# global-popularity results (a fashion brand, foreign-language phrases)
# rather than genuine Cairns skin queries, e.g. "acne" autocompleting to
# the clothing brand Acne Studios. Filtered out before scoring so this
# noise never reaches the daily report or a drafted article.
AUTOCOMPLETE_NOISE_PATTERNS: tuple[str, ...] = (
    "acne studios",
    "studios",
)


def _is_relevant_suggestion(suggestion: str) -> bool:
    lowered = suggestion.lower()
    if any(pattern in lowered for pattern in AUTOCOMPLETE_NOISE_PATTERNS):
        return False
    # Non-ASCII characters (umlauts etc) are a reliable signal of
    # foreign-language autocomplete leakage for this site's audience.
    if not suggestion.isascii():
        return False
    return True


def fetch_autocomplete_suggestions(
    login: str,
    password: str,
    seed_terms: tuple[str, ...],
) -> list[str]:
    """Calls DataForSEO's SERP Google Autocomplete Live Advanced endpoint
    once per seed term, scoped to Cairns, and returns the flattened,
    deduplicated list of suggested query strings.

    Docs: https://docs.dataforseo.com/v3/serp/google/autocomplete/live/advanced/

    Requests are sent one keyword at a time, sequentially, with a short
    delay between each, rather than batching every seed term into a
    single request. Some DataForSEO account tiers reject a multi-task
    request outright with "You can set only one task at a time", so
    sequential single-task requests are used unconditionally here since
    they work on every tier, at the cost of being slower than one batched
    call.

    A failure on any individual keyword (network issue or a per-task API
    error) is logged and that keyword is skipped, rather than aborting the
    whole run, so one bad request doesn't lose suggestions already
    collected from the rest.
    """
    suggestions: set[str] = set()

    for index, term in enumerate(seed_terms):
        task = [
            {
                "keyword": term,
                "location_name": DATAFORSEO_LOCATION_NAME,
                "language_code": DATAFORSEO_LANGUAGE_CODE,
            }
        ]

        try:
            response = requests.post(
                DATAFORSEO_AUTOCOMPLETE_URL,
                auth=(login, password),
                json=task,
                timeout=DATAFORSEO_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            logger.error("DataForSEO autocomplete request failed for '%s': %s", term, exc)
            continue

        try:
            payload = response.json()
        except ValueError as exc:
            logger.error("DataForSEO response for '%s' was not valid JSON: %s", term, exc)
            continue

        if payload.get("status_code") != 20000:
            logger.error(
                "DataForSEO API error for '%s': %s %s",
                term,
                payload.get("status_code"),
                payload.get("status_message"),
            )
            continue

        for task_result in payload.get("tasks", []):
            if task_result.get("status_code") != 20000:
                logger.warning(
                    "DataForSEO task error for keyword '%s': %s",
                    term,
                    task_result.get("status_message"),
                )
                continue
            for result in task_result.get("result") or []:
                for item in result.get("items") or []:
                    suggestion = item.get("suggestion")
                    if suggestion and _is_relevant_suggestion(suggestion):
                        suggestions.add(suggestion.strip())

        # Skip the delay after the last term; there's nothing left to wait for.
        if index < len(seed_terms) - 1:
            time.sleep(DATAFORSEO_REQUEST_DELAY_SECONDS)

    logger.info("Collected %d autocomplete suggestions", len(suggestions))
    return sorted(suggestions)


# --------------------------------------------------------------------------
# Google Search Console
# --------------------------------------------------------------------------


def fetch_search_console_queries(
    service_account_json: str,
    site_url: str,
    lookback_days: int = GSC_LOOKBACK_DAYS,
) -> list[dict[str, Any]]:
    """Queries the Search Console API for per-query performance over the
    last `lookback_days`, for the given verified property.

    Requires the service account to already be added as a user on the
    Search Console property; this script only reads data.
    """
    try:
        account_info = json.loads(service_account_json)
    except json.JSONDecodeError as exc:
        raise MissingCredentialError(
            "GOOGLE_SERVICE_ACCOUNT_JSON is not valid JSON."
        ) from exc

    credentials = service_account.Credentials.from_service_account_info(
        account_info,
        scopes=["https://www.googleapis.com/auth/webmasters.readonly"],
    )

    try:
        service = build_google_service("searchconsole", "v1", credentials=credentials)
    except Exception as exc:  # noqa: BLE001 - googleapiclient can raise several types here
        logger.error("Failed to build Search Console client: %s", exc)
        return []

    end_date = date.today()
    start_date = end_date - timedelta(days=lookback_days)

    request_body = {
        "startDate": start_date.isoformat(),
        "endDate": end_date.isoformat(),
        "dimensions": ["query"],
        "rowLimit": GSC_ROW_LIMIT,
    }

    try:
        response = (
            service.searchanalytics()
            .query(siteUrl=site_url, body=request_body)
            .execute()
        )
    except HttpError as exc:
        logger.error("Search Console API error: %s", exc)
        return []

    rows = response.get("rows", [])
    logger.info("Collected %d Search Console query rows", len(rows))
    return [
        {
            "query": row["keys"][0],
            "impressions": row.get("impressions", 0),
            "clicks": row.get("clicks", 0),
            "ctr": row.get("ctr", 0.0),
            "position": row.get("position", 0.0),
        }
        for row in rows
    ]


# --------------------------------------------------------------------------
# Existing content coverage (duplication check)
# --------------------------------------------------------------------------

def _extract_frontmatter_string(text: str, field_name: str) -> str | None:
    """Extracts a simple quoted-string frontmatter value, e.g. title: "...".

    Deliberately avoids a YAML parser dependency: every frontmatter field
    this script cares about is written as a single quoted string on its
    own line, consistently, across this project's content collections.
    """
    pattern = re.compile(rf'^{re.escape(field_name)}:\s*"([^"]+)"', re.MULTILINE)
    found = pattern.search(text)
    return found.group(1) if found else None


def load_existing_coverage() -> dict[str, str]:
    """Builds a lookup of lowercase title/question/summary text -> slug for
    every piece of content in the repo, so new opportunities can be checked
    against what the site already covers.
    """
    coverage: dict[str, str] = {}
    for directory in CONTENT_DIRS:
        if not directory.exists():
            continue
        for path in sorted(directory.glob("*.mdx")):
            text = path.read_text(encoding="utf-8")
            slug = path.stem
            for field_name in ("title", "primaryQuestion", "shortSummary"):
                value = _extract_frontmatter_string(text, field_name)
                if value:
                    coverage[value.lower()] = slug
    logger.info("Loaded %d existing content entries for duplication checks", len(coverage))
    return coverage


def find_existing_match(query: str, coverage: dict[str, str]) -> str | None:
    """Flags a query as already covered if a meaningful share of its
    significant words (longer than 3 characters) overlap with an existing
    title/question/summary. Deliberately approximate: the goal is to catch
    obvious duplicates, not to be a precise semantic matcher.
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


# --------------------------------------------------------------------------
# Scoring
# --------------------------------------------------------------------------


def score_opportunities(
    autocomplete_suggestions: list[str],
    gsc_rows: list[dict[str, Any]],
    coverage: dict[str, str],
) -> list[Opportunity]:
    """Combines both signals into a single, comparable opportunity score.

    Search Console rows are the primary signal (real impressions on the
    real site), weighted toward queries with meaningful impressions but a
    weak ranking position or low click-through, since that combination
    means real demand the site isn't yet capturing well. Autocomplete-only
    suggestions (no Search Console history yet, e.g. a topic not covered
    at all) get a smaller, flat score based on being a real, currently
    suggested phrase, since there is no performance data to weigh them
    against. Matching entries get a corroboration bonus. Anything that
    substantially overlaps existing content is heavily deprioritised
    rather than removed, so it stays visible for context.
    """
    opportunities: dict[str, Opportunity] = {}

    for row in gsc_rows:
        query = row["query"]
        position = row["position"]
        impressions = row["impressions"]
        ctr = row["ctr"]

        # Weak ranking (further down the results) means more room for a
        # dedicated article to improve on it; cap so one outlier position
        # doesn't dominate the score.
        position_factor = min(position / 10, 3.0)
        # Low CTR relative to impressions suggests the current result
        # isn't satisfying the query well.
        ctr_factor = max(0.0, 1 - (ctr * 20))
        score = impressions * (0.4 + position_factor * 0.3 + ctr_factor * 0.3)

        opportunities[query.lower()] = Opportunity(
            query=query,
            source="search_console",
            impressions=impressions,
            clicks=row["clicks"],
            ctr=ctr,
            position=position,
            score=score,
        )

    for suggestion in autocomplete_suggestions:
        key = suggestion.lower()
        if key in opportunities:
            opportunities[key].source = "both"
            opportunities[key].score += 25  # corroborated by a second, independent signal
        else:
            opportunities[key] = Opportunity(
                query=suggestion,
                source="autocomplete",
                score=15.0,
            )

    for opportunity in opportunities.values():
        matched_slug = find_existing_match(opportunity.query, coverage)
        opportunity.already_covered = matched_slug is not None
        opportunity.matched_slug = matched_slug
        if opportunity.already_covered:
            opportunity.score *= 0.1

    return sorted(opportunities.values(), key=lambda o: o.score, reverse=True)


# --------------------------------------------------------------------------
# Output
# --------------------------------------------------------------------------


def write_csv(opportunities: list[Opportunity], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=list(CSV_FIELDNAMES))
        writer.writeheader()
        for opportunity in opportunities:
            writer.writerow(opportunity.as_row())
    logger.info("Wrote %s (%d rows)", path, len(opportunities))


def append_search_log(opportunities: list[Opportunity], path: Path, today_str: str) -> None:
    """Appends today's full opportunity list to a persistent, never-
    overwritten log, so search-demand history accumulates across days
    instead of being lost when latest.csv is replaced tomorrow.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    is_new_file = not path.exists()
    with path.open("a", newline="", encoding="utf-8") as csv_file:
        fieldnames = ["date", *CSV_FIELDNAMES]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        if is_new_file:
            writer.writeheader()
        for opportunity in opportunities:
            writer.writerow({"date": today_str, **opportunity.as_row()})
    logger.info("Appended %d rows to %s", len(opportunities), path)


def _load_articles_log(path: Path) -> dict[str, str]:
    """Reads the query -> article_slug mapping written by the separate
    daily content-drafting workflow (reports/articles-from-radar.csv), so
    the weekly summary can show which searches already have an article.
    Returns an empty mapping if that log doesn't exist yet.
    """
    mapping: dict[str, str] = {}
    if not path.exists():
        return mapping
    with path.open(newline="", encoding="utf-8") as csv_file:
        for row in csv.DictReader(csv_file):
            query = row.get("query")
            slug = row.get("article_slug")
            if query and slug:
                mapping[query] = slug
    return mapping


def write_weekly_summary(
    search_log_path: Path,
    articles_log_path: Path,
    output_path: Path,
    coverage: dict[str, str],
    days: int = WEEKLY_WINDOW_DAYS,
) -> None:
    """Aggregates the trailing `days` of search-log.csv by query and writes
    a fresh top-10 markdown summary, recomputed every run.

    Coverage is re-checked at rollup time (rather than trusting the
    already_covered flag recorded on the day a query was first logged) so
    a query that has since been turned into an article shows up correctly.
    This is the file intended for weekly Instagram planning: queries with
    no article yet are open content ideas, queries with one are ready to
    repurpose as a post linking back to that page.
    """
    if not search_log_path.exists():
        logger.info("No search log yet at %s; skipping weekly summary", search_log_path)
        return

    cutoff = date.today() - timedelta(days=days - 1)
    aggregated: dict[str, dict[str, Any]] = {}
    with search_log_path.open(newline="", encoding="utf-8") as csv_file:
        for row in csv.DictReader(csv_file):
            try:
                row_date = date.fromisoformat(row["date"])
            except (KeyError, ValueError):
                continue
            if row_date < cutoff:
                continue
            query = row.get("query", "")
            if not query:
                continue
            score = float(row.get("score") or 0.0)
            existing = aggregated.get(query)
            if existing is None or score > existing["score"]:
                aggregated[query] = {
                    "score": score,
                    "source": row.get("source", ""),
                    "impressions": row.get("impressions", ""),
                }

    articles_by_query = _load_articles_log(articles_log_path)
    ranked = sorted(aggregated.items(), key=lambda item: item[1]["score"], reverse=True)

    today_str = date.today().isoformat()
    lines = [
        f"# Top searches this week: {today_str}",
        "",
        f"Rolling {days}-day window ending today, from {len(aggregated)} distinct "
        "queries seen. Queries with no article yet are open content ideas; "
        "queries that already have one are ready to repurpose as an "
        "Instagram post linking back to that page.",
        "",
        "| # | Query | Source | Score | Article |",
        "|---:|---|---|---:|---|",
    ]
    for rank, (query, info) in enumerate(ranked[:10], start=1):
        slug = articles_by_query.get(query) or find_existing_match(query, coverage)
        article_note = slug if slug else "_none yet_"
        lines.append(
            f"| {rank} | {query} | {info['source']} | {info['score']:.1f} | {article_note} |"
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    logger.info("Wrote %s", output_path)


def write_markdown_report(
    opportunities: list[Opportunity],
    path: Path,
    top_n: int = 20,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    today_str = date.today().isoformat()
    new_opportunities = [o for o in opportunities if not o.already_covered]
    covered_opportunities = [o for o in opportunities if o.already_covered]

    lines = [
        f"# Content opportunities: {today_str}",
        "",
        f"{len(opportunities)} queries analysed, {len(new_opportunities)} not yet "
        "covered by existing content.",
        "",
        "## Top opportunities",
        "",
        "| Query | Source | Impressions | Position | Score |",
        "|---|---|---:|---:|---:|",
    ]
    for opportunity in new_opportunities[:top_n]:
        lines.append(
            f"| {opportunity.query} | {opportunity.source} | "
            f"{opportunity.impressions} | {opportunity.position:.1f} | "
            f"{opportunity.score:.1f} |"
        )

    lines += [
        "",
        "## Already covered (for reference, not new opportunities)",
        "",
        "| Query | Matched page |",
        "|---|---|",
    ]
    for opportunity in covered_opportunities[:top_n]:
        lines.append(f"| {opportunity.query} | {opportunity.matched_slug} |")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    logger.info("Wrote %s", path)


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------


def main() -> int:
    try:
        dataforseo_login = require_env("DATAFORSEO_LOGIN")
        dataforseo_password = require_env("DATAFORSEO_PASSWORD")
        google_service_account_json = require_env("GOOGLE_SERVICE_ACCOUNT_JSON")
    except MissingCredentialError as exc:
        logger.error(str(exc))
        return 1

    gsc_site_url = os.environ.get("GSC_SITE_URL", DEFAULT_GSC_SITE_URL)

    autocomplete_suggestions = fetch_autocomplete_suggestions(
        dataforseo_login, dataforseo_password, AUTOCOMPLETE_SEED_TERMS
    )
    gsc_rows = fetch_search_console_queries(google_service_account_json, gsc_site_url)

    if not autocomplete_suggestions and not gsc_rows:
        logger.error(
            "No data collected from either DataForSEO or Search Console; "
            "aborting without writing reports."
        )
        return 1

    coverage = load_existing_coverage()
    opportunities = score_opportunities(autocomplete_suggestions, gsc_rows, coverage)

    today_str = date.today().isoformat()
    write_csv(opportunities, REPORTS_DIR / "latest.csv")
    write_csv(opportunities, DAILY_REPORTS_DIR / f"{today_str}.csv")
    write_markdown_report(opportunities, REPORTS_DIR / "content-opportunities.md")
    append_search_log(opportunities, SEARCH_LOG_PATH, today_str)
    write_weekly_summary(SEARCH_LOG_PATH, ARTICLES_LOG_PATH, WEEKLY_SUMMARY_PATH, coverage)

    logger.info("Done. %d total opportunities scored.", len(opportunities))
    return 0


if __name__ == "__main__":
    sys.exit(main())
