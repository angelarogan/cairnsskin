/**
 * CONCERN TAXONOMY
 * ----------------------------------------------------------------
 * Step 1 (main concern) and step 2 (sub-concern) options for the
 * Treatment Finder. icon keys map to inline SVGs in FinderIcon.astro.
 * internalLink only points to a real, existing Cairns Skin concern
 * hub; omitted where no accurate single hub page exists yet.
 */

import type { Concern } from "./types";

export const concerns: Concern[] = [
  {
    slug: "pigmentation",
    label: "Pigmentation",
    shortDescription: "Sun spots, freckling, melasma and uneven dark patches.",
    icon: "pigmentation",
    internalLink: "/skin-concerns/pigmentation/",
    subConcerns: [
      { slug: "freckles", label: "Freckles" },
      { slug: "sun-spots", label: "Sun spots" },
      { slug: "melasma", label: "Melasma" },
      { slug: "uneven-pigmentation", label: "Uneven pigmentation" },
      { slug: "not-sure", label: "I'm not sure what type", pathway: "not_sure" },
    ],
  },
  {
    slug: "redness",
    label: "Redness",
    shortDescription: "Flushing, visible blood vessels and rosacea-related redness.",
    icon: "redness",
    internalLink: "/skin-concerns/redness-rosacea/",
    subConcerns: [
      { slug: "broken-capillaries", label: "Broken capillaries" },
      { slug: "flushed-skin", label: "Flushed skin" },
      { slug: "rosacea", label: "Rosacea" },
      { slug: "general-redness", label: "General redness" },
    ],
  },
  {
    slug: "acne",
    label: "Acne & Breakouts",
    shortDescription: "Active breakouts, congestion, scarring and the marks left behind.",
    icon: "acne",
    internalLink: "/skin-concerns/acne-reduction/",
    subConcerns: [
      { slug: "active-acne", label: "Active acne" },
      { slug: "blackheads", label: "Blackheads" },
      { slug: "congestion", label: "Congestion" },
      { slug: "acne-scarring", label: "Acne scarring" },
      { slug: "marks-after-acne", label: "Marks left after acne", pathway: "branching" },
    ],
  },
  {
    slug: "ageing",
    label: "Fine Lines & Ageing",
    shortDescription: "Fine lines, wrinkles, sagging and overall skin quality.",
    icon: "ageing",
    internalLink: "/skin-concerns/fine-lines-wrinkles/",
    subConcerns: [
      { slug: "fine-lines", label: "Fine lines" },
      { slug: "wrinkles", label: "Wrinkles" },
      { slug: "sagging-skin", label: "Sagging skin" },
      { slug: "loss-of-volume", label: "Loss of volume", pathway: "assessment_only" },
      { slug: "overall-skin-quality", label: "Overall skin quality" },
    ],
  },
  {
    slug: "skin-tone",
    label: "Skin Tone",
    shortDescription: "Dullness and general unevenness in overall skin colour.",
    icon: "skin-tone",
    subConcerns: [
      { slug: "dull-skin", label: "Dull skin" },
      { slug: "uneven-skin-colour", label: "Uneven skin colour" },
    ],
  },
  {
    slug: "texture",
    label: "Skin Texture",
    shortDescription: "Roughness, dehydration, enlarged pores and uneven texture.",
    icon: "texture",
    subConcerns: [
      { slug: "rough-skin", label: "Rough skin" },
      { slug: "dry-dehydrated", label: "Dry or dehydrated-looking skin" },
      { slug: "large-pores", label: "Large pores" },
      { slug: "uneven-texture", label: "Uneven texture" },
    ],
  },
  {
    slug: "body",
    label: "Body Concerns",
    shortDescription: "Localised fat, stretch marks and skin tightening.",
    icon: "body",
    subConcerns: [
      { slug: "localised-fat", label: "Stubborn fat" },
      { slug: "stretch-marks", label: "Stretch marks" },
      { slug: "skin-tightening", label: "Skin tightening" },
    ],
  },
  {
    slug: "hair",
    label: "Unwanted Hair",
    shortDescription: "Facial and body hair reduction.",
    icon: "hair",
    subConcerns: [
      { slug: "facial-hair", label: "Facial hair" },
      { slug: "body-hair", label: "Body hair" },
    ],
  },
];

export function getConcern(slug: string): Concern | undefined {
  return concerns.find((c) => c.slug === slug);
}

export function getSubConcern(concernSlug: string, subConcernSlug: string) {
  return getConcern(concernSlug)?.subConcerns.find((s) => s.slug === subConcernSlug);
}
