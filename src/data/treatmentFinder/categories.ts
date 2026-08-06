/**
 * TREATMENT CATEGORY TAXONOMY
 * ----------------------------------------------------------------
 * Generic, non-branded treatment categories used by the Treatment
 * Finder. These are deliberately NOT a copy of the Laser Clinics
 * Australia service menu (Cairns Skin is an information resource,
 * not a booking page), and they never include prescription-only
 * cosmetic medicines: there is no category for anti-wrinkle
 * injections, dermal fillers or prescription injectable
 * biostimulators anywhere in this file. That is the TGA/prescription
 * firewall described in publicMatcherStatus: it isn't a rule to
 * remember to apply, it's a category that was never created.
 *
 * internalLink only ever points to a real, already-published Cairns
 * Skin page, verified against the routes in src/pages and
 * src/content. Where no matching page exists yet, internalLink is
 * omitted rather than invented, and the result card falls back to
 * linking the general /treatments/ index.
 *
 * evidence is the category's default public label. It is never
 * upgraded based on how commonly a treatment is offered: where the
 * corresponding Cairns Skin treatment page's own evidenceLevel is
 * "clinical-experience" or "manufacturer-claim" (i.e. not yet backed
 * by independent published research on this site), or no Cairns Skin
 * page exists at all yet, the label here is "Evidence summary being
 * reviewed" rather than an invented rating.
 */

import type { TreatmentCategory } from "./types";

export const treatmentCategories: TreatmentCategory[] = [
  {
    id: "bbl",
    label: "BroadBand Light (BBL)",
    shortDescription:
      "A light-based treatment that targets pigment and small blood vessels near the skin's surface.",
    evidence: "Emerging evidence",
    internalLink: "/treatments/bbl/",
    downtime: "Minimal",
    publicMatcherStatus: "allowed",
  },
  {
    id: "pigmentation-light",
    label: "Pigmentation-Focused Light Treatment",
    shortDescription:
      "Light-based treatment aimed specifically at fading sun-related dark spots and evening out tone.",
    evidence: "Evidence summary being reviewed",
    internalLink: "/treatments/pigmentation-removal/",
    downtime: "Minimal",
    publicMatcherStatus: "allowed",
  },
  {
    id: "vascular-light",
    label: "Vascular / Capillary Light Treatment",
    shortDescription:
      "Light or laser-based treatment that targets visible blood vessels and redness near the skin's surface.",
    evidence: "Evidence summary being reviewed",
    internalLink: "/treatments/capillary-reduction/",
    downtime: "Minimal",
    publicMatcherStatus: "allowed",
  },
  {
    id: "fluorescent-light-energy",
    label: "Fluorescent Light Energy Therapy",
    shortDescription:
      "A non-invasive treatment that uses fluorescent light energy and may be considered for inflammatory skin concerns such as acne.",
    evidence: "Emerging evidence",
    internalLink: "/treatments/kleresca-rosacea/",
    downtime: "Minimal",
    publicMatcherStatus: "allowed",
  },
  {
    id: "led-light-therapy",
    label: "LED Light Therapy",
    shortDescription:
      "Gentle, non-invasive light treatment often used alongside other treatments to support recovery and calm inflammation.",
    evidence: "Emerging evidence",
    internalLink: "/treatments/led-light-therapy/",
    downtime: "Minimal",
    publicMatcherStatus: "allowed",
  },
  {
    id: "skin-needling",
    label: "Skin Needling",
    shortDescription:
      "Creates controlled micro-injuries to stimulate the skin's own collagen remodelling process.",
    evidence: "Emerging evidence",
    internalLink: "/treatments/skin-needling/",
    downtime: "Short",
    publicMatcherStatus: "allowed",
  },
  {
    id: "rf-microneedling",
    label: "RF Microneedling",
    shortDescription:
      "Combines radiofrequency energy with fine needling to stimulate collagen deeper in the skin.",
    evidence: "Evidence summary being reviewed",
    internalLink: "/treatments/fractional-rf/",
    downtime: "Minimal",
    publicMatcherStatus: "allowed",
  },
  {
    id: "resurfacing-treatments",
    label: "Resurfacing Treatments",
    shortDescription:
      "Broader category of treatments aimed at improving skin texture and surface quality over a course of sessions.",
    evidence: "Evidence summary being reviewed",
    publicMatcherStatus: "allowed",
  },
  {
    id: "brightening-peels",
    label: "Brightening / Pigmentation Peels",
    shortDescription:
      "Peel-based treatments aimed at fading dark spots and evening out tone.",
    evidence: "Evidence summary being reviewed",
    internalLink: "/treatments/melanopro-peel/",
    downtime: "Short",
    publicMatcherStatus: "allowed",
  },
  {
    id: "clarifying-peels",
    label: "Clarifying / Acne Peels",
    shortDescription:
      "Peel-based treatments aimed at decongesting pores and calming active breakouts.",
    evidence: "Evidence summary being reviewed",
    publicMatcherStatus: "allowed",
  },
  {
    id: "resurfacing-peels",
    label: "Resurfacing Peels",
    shortDescription:
      "Deeper peel-based treatments aimed at improving surface texture and tone.",
    evidence: "Evidence summary being reviewed",
    publicMatcherStatus: "allowed",
  },
  {
    id: "hydrating-peels",
    label: "Hydrating / Gentle Peels",
    shortDescription:
      "Gentler peel-based treatments aimed at refreshing dull or dehydrated-looking skin with minimal downtime.",
    evidence: "Evidence summary being reviewed",
    publicMatcherStatus: "allowed",
  },
  {
    id: "advanced-depigmentation",
    label: "Advanced Depigmentation Treatments",
    shortDescription:
      "Structured, multi-phase treatments aimed at more established or resistant pigmentation, used after proper assessment.",
    evidence: "Evidence summary being reviewed",
    internalLink: "/treatments/melanopro-peel/",
    downtime: "Short",
    publicMatcherStatus: "allowed",
  },
  {
    id: "microdermabrasion",
    label: "Microdermabrasion",
    shortDescription:
      "Mechanical exfoliation treatment used to smooth texture and refresh dull-looking skin.",
    evidence: "Evidence summary being reviewed",
    internalLink: "/treatments/microdermabrasion/",
    downtime: "Minimal",
    publicMatcherStatus: "allowed",
  },
  {
    id: "skin-tightening",
    label: "Skin Tightening Treatments",
    shortDescription:
      "Treatments aimed at improving skin firmness, generally using heat or radiofrequency-based technology.",
    evidence: "Evidence summary being reviewed",
    internalLink: "/treatments/fractional-rf/",
    downtime: "Minimal",
    publicMatcherStatus: "allowed",
  },
  {
    id: "polynucleotide",
    label: "Polynucleotide Skin Treatments",
    shortDescription:
      "Injectable skin-quality treatment aimed at supporting the skin's own repair processes, not a volumising filler.",
    evidence: "Emerging evidence",
    internalLink: "/treatments/rejuran/",
    downtime: "Minimal",
    publicMatcherStatus: "allowed",
  },
  {
    id: "cryolipolysis",
    label: "Cryolipolysis / Fat Reduction",
    shortDescription:
      "Non-surgical treatment that uses controlled cooling to reduce stubborn, localised fat.",
    evidence: "Evidence summary being reviewed",
    publicMatcherStatus: "allowed",
  },
  {
    id: "laser-hair-removal",
    label: "Laser Hair Removal",
    shortDescription:
      "Laser-based treatment that targets hair follicles to reduce hair growth over a course of sessions.",
    evidence: "Stronger evidence",
    internalLink: "/treatments/laser-hair-removal/",
    downtime: "Minimal",
    publicMatcherStatus: "allowed",
  },
];

export function getCategory(id: string): TreatmentCategory | undefined {
  return treatmentCategories.find((c) => c.id === id);
}
