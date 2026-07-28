/**
 * TREATMENT DATA — SINGLE SOURCE OF TRUTH
 * ----------------------------------------------------------------
 * Every treatment name, description fragment and status flag used
 * anywhere on the site should be read from this file rather than
 * re-typed in content or components. This prevents inconsistent
 * naming (e.g. "IPL" vs "BBL") appearing across different pages.
 *
 * VERIFICATION REQUIRED BEFORE PUBLISH:
 * None of the entries below have been confirmed against the current
 * Laser Clinics Cairns service menu. `verified: false` on every
 * entry is intentional. A human must:
 *   1. Confirm the treatment is currently offered at Laser Clinics
 *      Cairns specifically (not just other locations).
 *   2. Confirm the exact current commercial name.
 *   3. Confirm the description against approved Laser Clinics copy.
 *   4. Flip `verified` to true and record `verifiedDate` once done.
 *
 * Nothing with `verified: false` should be presented as confirmed
 * fact in published (reviewStatus: "published") content.
 */

export type TreatmentAvailability = "unconfirmed" | "confirmed" | "not-offered";

export interface TreatmentMeta {
  key: string;
  /** Exact commercial name — placeholder pending verification */
  displayName: string;
  slug: string;
  shortDescription: string;
  category:
    | "laser-hair-removal"
    | "skin-rejuvenation"
    | "skin-needling"
    | "injectable-adjacent" // polynucleotide-based, non-prescription
    | "light-therapy"
    | "peel"
    | "skincare";
  verified: boolean;
  verifiedDate: string | null;
  availabilityAtCairns: TreatmentAvailability;
  clinicVerificationRequired: true;
  notes?: string;
}

export const treatments: Record<string, TreatmentMeta> = {
  bbl: {
    key: "bbl",
    displayName: "BBL", // PLACEHOLDER — confirm exact Laser Clinics naming (e.g. "BBL Photorejuvenation")
    slug: "bbl",
    shortDescription:
      "Broadband light treatment used for concerns such as pigmentation and redness. Description pending clinic verification.",
    category: "skin-rejuvenation",
    verified: false,
    verifiedDate: null,
    availabilityAtCairns: "unconfirmed",
    clinicVerificationRequired: true,
    notes: "Do not label as IPL in published copy — confirm BBL is the correct current term for this location.",
  },
  rejuran: {
    key: "rejuran",
    displayName: "Rejuran", // PLACEHOLDER — confirm exact product/treatment line offered
    slug: "rejuran",
    shortDescription:
      "Polynucleotide skin treatment used for skin quality and texture. Description pending clinic verification.",
    category: "skin-rejuvenation",
    verified: false,
    verifiedDate: null,
    availabilityAtCairns: "unconfirmed",
    clinicVerificationRequired: true,
  },
  "skin-needling": {
    key: "skin-needling",
    displayName: "Skin Needling", // PLACEHOLDER — confirm exact current name (may be a branded device name)
    slug: "skin-needling",
    shortDescription:
      "Collagen induction treatment used for texture and acne scarring. Description pending clinic verification.",
    category: "skin-needling",
    verified: false,
    verifiedDate: null,
    availabilityAtCairns: "unconfirmed",
    clinicVerificationRequired: true,
  },
  "laser-hair-removal": {
    key: "laser-hair-removal",
    displayName: "Laser Hair Removal", // PLACEHOLDER — confirm exact platform/branding used at Cairns
    slug: "laser-hair-removal",
    shortDescription:
      "Laser-based hair reduction treatment. Description pending clinic verification.",
    category: "laser-hair-removal",
    verified: false,
    verifiedDate: null,
    availabilityAtCairns: "unconfirmed",
    clinicVerificationRequired: true,
  },
  "led-light-therapy": {
    key: "led-light-therapy",
    displayName: "LED Light Therapy", // PLACEHOLDER — confirm naming
    slug: "led-light-therapy",
    shortDescription:
      "Light-based adjunct treatment used for redness, acne-prone and post-procedure skin. Description pending clinic verification.",
    category: "light-therapy",
    verified: false,
    verifiedDate: null,
    availabilityAtCairns: "unconfirmed",
    clinicVerificationRequired: true,
  },
  "fractional-rf": {
    key: "fractional-rf",
    displayName: "Fractional RF", // PLACEHOLDER — confirm whether currently offered at Cairns
    slug: "fractional-rf",
    shortDescription:
      "Radiofrequency-based skin texture treatment. Description pending clinic verification.",
    category: "skin-rejuvenation",
    verified: false,
    verifiedDate: null,
    availabilityAtCairns: "unconfirmed",
    clinicVerificationRequired: true,
  },
  "medical-grade-peels": {
    key: "medical-grade-peels",
    displayName: "Medical Grade Peels", // PLACEHOLDER — confirm exact peel range/brand
    slug: "medical-grade-peels",
    shortDescription:
      "Chemical exfoliation treatments used for tone and texture. Description pending clinic verification.",
    category: "peel",
    verified: false,
    verifiedDate: null,
    availabilityAtCairns: "unconfirmed",
    clinicVerificationRequired: true,
  },
  "medical-grade-skincare": {
    key: "medical-grade-skincare",
    displayName: "Medical Grade Skincare", // PLACEHOLDER — confirm stocked brands at Cairns
    slug: "medical-grade-skincare",
    shortDescription:
      "Clinically formulated take-home skincare recommended alongside in-clinic treatments.",
    category: "skincare",
    verified: false,
    verifiedDate: null,
    availabilityAtCairns: "unconfirmed",
    clinicVerificationRequired: true,
  },
};

export function getTreatment(key: string): TreatmentMeta | undefined {
  return treatments[key];
}

export function listTreatments(): TreatmentMeta[] {
  return Object.values(treatments);
}
