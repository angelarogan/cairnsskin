/**
 * TREATMENT FINDER: PUBLIC DATA API
 * ----------------------------------------------------------------
 * Barrel export plus helper functions and the small amount of fixed
 * copy that isn't really "data" (disclaimer, hard-stop assessment
 * copy, medical safety note). Components should import from here
 * rather than reaching into individual data files directly.
 */

import { getCategory } from "./categories";
import { getMatches, introNotes } from "./matches";
import type { Match, TreatmentCategory } from "./types";

export { concerns, getConcern, getSubConcern } from "./concerns";
export { treatmentCategories, getCategory } from "./categories";
export { matches, getMatches, introNotes } from "./matches";
export { RELEVANCE_LABEL } from "./types";
export type * from "./types";

export interface ResolvedMatch {
  match: Match;
  category: TreatmentCategory;
}

/** Matches joined with their category data, ready to render. Excluded categories can never appear here. */
export function resolveMatches(concernSlug: string, subConcernSlug: string): ResolvedMatch[] {
  return getMatches(concernSlug, subConcernSlug)
    .map((match) => {
      const category = getCategory(match.treatmentCategory);
      return category && category.publicMatcherStatus === "allowed" ? { match, category } : null;
    })
    .filter((m): m is ResolvedMatch => m !== null);
}

export function getIntroNote(concernSlug: string, subConcernSlug: string): string | undefined {
  return introNotes[`${concernSlug}:${subConcernSlug}`];
}

export const ASSESSMENT_ONLY_COPY: Record<string, { heading: string; body: string }> = {
  "ageing:loss-of-volume": {
    heading: "Professional assessment recommended",
    body:
      "Changes in facial volume can involve several tissues and causes. Appropriate treatment depends on facial anatomy, skin quality, ageing patterns and individual goals. This concern is best assessed in person by a treating clinician.",
  },
};

export const NOT_SURE_PIGMENTATION = [
  {
    label: "Freckles",
    description: "Small, defined pigmented spots often associated with sun exposure.",
  },
  {
    label: "Sun spots",
    description: "Larger, persistent areas of pigmentation associated with cumulative UV exposure.",
  },
  {
    label: "Melasma",
    description: "Often broader patches of pigmentation that can have multiple triggers, including hormones.",
  },
  {
    label: "Post-inflammatory pigmentation",
    description: "Colour remaining on the skin after inflammation or injury, such as a breakout or bite.",
  },
];

export const NOT_SURE_CLOSING =
  "Because different pigmentation types respond differently to treatment, assessment is important when you're unsure.";

export const MEDICAL_SAFETY_NOTE =
  "Some skin changes should be assessed medically before considering cosmetic treatment. If a spot or lesion is new, changing, bleeding or concerning, seek assessment from an appropriate medical professional rather than using this tool.";

export const FINDER_DISCLAIMER =
  "This tool provides general educational information and does not diagnose skin conditions or determine individual treatment suitability. Skin concerns can have different causes, and appropriate treatment depends on individual assessment. Seek professional medical advice for persistent, changing or concerning skin conditions.";

export const LOCAL_CTA = {
  heading: "Want to discuss your options in person?",
  body: "An individual consultation can help determine which options may be appropriate for your skin.",
  linkLabel: "Laser Clinics Cairns Central",
  href: "https://www.laserclinics.com.au/skin-care-clinic/cairns-central/",
};
