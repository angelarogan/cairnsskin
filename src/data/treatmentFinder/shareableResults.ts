/**
 * SHAREABLE / INDEXABLE RESULT PAGES
 * ----------------------------------------------------------------
 * A deliberately small, curated list of concern/sub-concern results
 * that get their own standalone, indexable static page at
 * /tools/skin-treatment-finder/[slug]/. This is NOT auto-generated
 * for every possible combination: only add an entry here when the
 * result is genuinely meaningful as a standalone page and there's
 * enough content to justify indexing it (per the finder brief's SEO
 * rules). Everything else is still fully reachable through the
 * interactive tool, just without its own dedicated URL.
 */

export interface ShareableResult {
  slug: string;
  concern: string;
  subConcern: string;
  seoTitle: string;
  seoDescription: string;
  h1: string;
  intro: string;
}

export const shareableResults: ShareableResult[] = [
  {
    slug: "acne-scarring",
    concern: "acne",
    subConcern: "acne-scarring",
    seoTitle: "Acne Scarring Treatment Options | Skin Treatment Finder",
    seoDescription:
      "Explore treatment categories commonly considered for acne scarring, why they may be relevant, and what the evidence and limitations tell us.",
    h1: "Treatment options for acne scarring",
    intro:
      "For acne scarring, treatment options generally focus on stimulating collagen remodelling. The most appropriate approach depends on scar type, depth, skin type and individual assessment.",
  },
  {
    slug: "pigmentation",
    concern: "pigmentation",
    subConcern: "sun-spots",
    seoTitle: "Pigmentation Treatment Options | Skin Treatment Finder",
    seoDescription:
      "Explore treatment categories commonly considered for sun-related pigmentation such as freckles and sun spots, why they may be relevant, and what the evidence tells us.",
    h1: "Treatment options for pigmentation",
    intro:
      "For sun-related pigmentation such as freckles and sun spots, treatment options generally focus on targeting melanin near the skin's surface. Melasma behaves differently and is covered separately, since it needs a more cautious approach.",
  },
  {
    slug: "redness",
    concern: "redness",
    subConcern: "general-redness",
    seoTitle: "Redness Treatment Options | Skin Treatment Finder",
    seoDescription:
      "Explore treatment categories commonly considered for facial redness and visible blood vessels, why they may be relevant, and what the evidence tells us.",
    h1: "Treatment options for redness",
    intro:
      "For general redness and visible blood vessels, treatment options generally focus on targeting haemoglobin near the skin's surface. Rosacea-related redness is covered separately, since it needs a more cautious, ongoing approach.",
  },
  {
    slug: "large-pores",
    concern: "texture",
    subConcern: "large-pores",
    seoTitle: "Large Pores Treatment Options | Skin Treatment Finder",
    seoDescription:
      "Explore treatment categories commonly considered for enlarged-looking pores, why they may be relevant, and what the evidence and limitations tell us.",
    h1: "Treatment options for large pores",
    intro:
      "For large or enlarged-looking pores, treatment options generally focus on collagen remodelling around the pore opening and improving overall skin texture, since pore size itself is largely structural.",
  },
];

export function getShareableResult(slug: string): ShareableResult | undefined {
  return shareableResults.find((r) => r.slug === slug);
}
