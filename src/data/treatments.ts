/**
 * TREATMENT DATA: SINGLE SOURCE OF TRUTH
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
  /** Exact commercial name: placeholder pending verification */
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
    | "skincare"
    | "facial"
    | "vascular";
  verified: boolean;
  verifiedDate: string | null;
  availabilityAtCairns: TreatmentAvailability;
  clinicVerificationRequired: true;
  /**
   * The treatment's own official page on the Laser Clinics Australia
   * website (the same URL used for the "[X] treatment information" link
   * required by the permanent Laser Clinics linking rule in CLAUDE.md).
   * "Book a Consultation" on the matching Cairns Skin page links here
   * rather than to a generic LCA booking form, so visitors land on
   * genuine treatment-specific information with pricing, before/afters
   * and LCA's own booking CTA in context.
   */
  bookingUrl: string;
  notes?: string;
}

export const treatments: Record<string, TreatmentMeta> = {
  bbl: {
    key: "bbl",
    displayName: "BBL", // PLACEHOLDER: confirm exact Laser Clinics naming (e.g. "BBL Photorejuvenation")
    slug: "bbl",
    shortDescription:
      "Broadband light treatment used for concerns such as pigmentation and redness.",
    category: "skin-rejuvenation",
    verified: false,
    verifiedDate: null,
    availabilityAtCairns: "unconfirmed",
    clinicVerificationRequired: true,
    bookingUrl: "https://www.laserclinics.com.au/skin-care-treatments/bbl/",
    notes: "Do not label as IPL in published copy: confirm BBL is the correct current term for this location.",
  },
  rejuran: {
    key: "rejuran",
    displayName: "Rejuran", // PLACEHOLDER: confirm exact product/treatment line offered
    slug: "rejuran",
    shortDescription:
      "Polynucleotide skin treatment used for skin quality and texture.",
    category: "skin-rejuvenation",
    verified: false,
    verifiedDate: null,
    availabilityAtCairns: "unconfirmed",
    clinicVerificationRequired: true,
    bookingUrl: "https://www.laserclinics.com.au/cosmetic-aesthetics/rejuran/",
  },
  "skin-needling": {
    key: "skin-needling",
    displayName: "Skin Needling", // PLACEHOLDER: confirm exact current name (may be a branded device name)
    slug: "skin-needling",
    shortDescription:
      "Collagen induction treatment used for texture and acne scarring.",
    category: "skin-needling",
    verified: false,
    verifiedDate: null,
    availabilityAtCairns: "unconfirmed",
    clinicVerificationRequired: true,
    bookingUrl: "https://www.laserclinics.com.au/skin-care-treatments/skin-needling/",
  },
  "laser-hair-removal": {
    key: "laser-hair-removal",
    displayName: "Laser Hair Removal", // PLACEHOLDER: confirm exact platform/branding used at Cairns
    slug: "laser-hair-removal",
    shortDescription:
      "Laser-based hair reduction treatment.",
    category: "laser-hair-removal",
    verified: false,
    verifiedDate: null,
    availabilityAtCairns: "unconfirmed",
    clinicVerificationRequired: true,
    bookingUrl: "https://www.laserclinics.com.au/laser-hair-removal/",
  },
  "led-light-therapy": {
    key: "led-light-therapy",
    displayName: "LED Light Therapy", // PLACEHOLDER: confirm naming
    slug: "led-light-therapy",
    shortDescription:
      "Light-based adjunct treatment used for redness, acne-prone and post-procedure skin.",
    category: "light-therapy",
    verified: false,
    verifiedDate: null,
    availabilityAtCairns: "unconfirmed",
    clinicVerificationRequired: true,
    bookingUrl: "https://www.laserclinics.com.au/skin-care-treatments/led-light-therapy/",
  },
  "fractional-rf": {
    key: "fractional-rf",
    displayName: "Fractional RF", // PLACEHOLDER: confirm whether currently offered at Cairns
    slug: "fractional-rf",
    shortDescription:
      "Radiofrequency-based skin texture treatment.",
    category: "skin-rejuvenation",
    verified: false,
    verifiedDate: null,
    availabilityAtCairns: "unconfirmed",
    clinicVerificationRequired: true,
    bookingUrl: "https://www.laserclinics.com.au/skin-care-treatments/fractional-rf-treatment/",
  },
  "medical-grade-peels": {
    key: "medical-grade-peels",
    displayName: "Medical Grade Peels", // PLACEHOLDER: confirm exact peel range/brand
    slug: "medical-grade-peels",
    shortDescription:
      "Chemical exfoliation treatments used for tone and texture.",
    category: "peel",
    verified: false,
    verifiedDate: null,
    availabilityAtCairns: "unconfirmed",
    clinicVerificationRequired: true,
    bookingUrl: "https://www.laserclinics.com.au/booking/skin-treatments/",
  },
  skinstitut: {
    key: "skinstitut",
    displayName: "Skinstitut",
    slug: "skinstitut",
    shortDescription:
      "Cosmeceutical take-home skincare range recommended alongside in-clinic treatments.",
    category: "skincare",
    verified: true,
    verifiedDate: "2026-08-01",
    availabilityAtCairns: "confirmed",
    clinicVerificationRequired: true,
    bookingUrl: "https://www.laserclinics.com.au/skincare/",
    notes: "Confirmed directly by the site owner as the skincare brand used/recommended, 2026-08-01.",
  },
  microdermabrasion: {
    key: "microdermabrasion",
    displayName: "Microdermabrasion", // PLACEHOLDER: confirm exact current name/device used at Cairns
    slug: "microdermabrasion",
    shortDescription:
      "Mechanical exfoliation treatment used to smooth texture and refresh dull skin.",
    category: "peel",
    verified: false,
    verifiedDate: null,
    availabilityAtCairns: "unconfirmed",
    clinicVerificationRequired: true,
    bookingUrl: "https://www.laserclinics.com.au/skin-care-treatments/microdermabrasion/",
  },
  aquafacial: {
    key: "aquafacial",
    displayName: "AquaFacial", // PLACEHOLDER: confirm exact current branding used at Cairns
    slug: "aquafacial",
    shortDescription:
      "Multi-step hydrodermabrasion facial combining cleansing, exfoliation and hydration.",
    category: "facial",
    verified: false,
    verifiedDate: null,
    availabilityAtCairns: "unconfirmed",
    clinicVerificationRequired: true,
    bookingUrl: "https://www.laserclinics.com.au/skin-care-treatments/aquafacial/",
  },
  "capillary-reduction": {
    key: "capillary-reduction",
    displayName: "Capillary Reduction", // PLACEHOLDER: confirm exact current naming
    slug: "capillary-reduction",
    shortDescription:
      "Laser treatment targeting visible facial blood vessels and redness.",
    category: "vascular",
    verified: false,
    verifiedDate: null,
    availabilityAtCairns: "unconfirmed",
    clinicVerificationRequired: true,
    bookingUrl: "https://www.laserclinics.com.au/skin-care-treatments/capillary-reduction/",
  },
  "cosmetic-grade-facials": {
    key: "cosmetic-grade-facials",
    displayName: "Cosmetic Grade Facials", // PLACEHOLDER: confirm exact current naming/range
    slug: "cosmetic-grade-facials",
    shortDescription:
      "In-clinic facial treatments using professional-strength products to refresh and smooth skin's surface.",
    category: "facial",
    verified: false,
    verifiedDate: null,
    availabilityAtCairns: "unconfirmed",
    clinicVerificationRequired: true,
    bookingUrl: "https://www.laserclinics.com.au/skin-care-treatments/advanced-facials/",
  },
  "pigmentation-removal": {
    key: "pigmentation-removal",
    displayName: "Pigmentation Removal", // PLACEHOLDER: confirm exact current naming (may overlap with BBL)
    slug: "pigmentation-removal",
    shortDescription:
      "Treatment aimed at fading sun-related dark spots and evening out overall skin tone.",
    category: "skin-rejuvenation",
    verified: false,
    verifiedDate: null,
    availabilityAtCairns: "unconfirmed",
    clinicVerificationRequired: true,
    bookingUrl: "https://www.laserclinics.com.au/skin-care-treatments/pigmentation-removal/",
    notes: "Confirm how this is distinguished from BBL in current Laser Clinics Cairns service naming, to avoid overlapping/duplicate treatment claims.",
  },
  "melanopro-peel": {
    key: "melanopro-peel",
    displayName: "Melanopro Peel", // PLACEHOLDER: confirm exact current naming/availability at Cairns
    slug: "melanopro-peel",
    shortDescription:
      "Two-phase cosmetic-grade depigmentation peel aimed at superficial pigmentation and melasma.",
    category: "peel",
    verified: false,
    verifiedDate: null,
    availabilityAtCairns: "unconfirmed",
    clinicVerificationRequired: true,
    bookingUrl: "https://www.laserclinics.com.au/skin-care-treatments/melanopro/",
    notes: "Confirm availability at Laser Clinics Cairns specifically; only suited to superficial or mixed-depth melasma, not deep/dermal melasma.",
  },
  "kleresca-rosacea": {
    key: "kleresca-rosacea",
    displayName: "Kleresca Rosacea Treatment", // PLACEHOLDER: confirm exact current naming/availability at Cairns
    slug: "kleresca-rosacea",
    shortDescription:
      "Light-based biophotonic treatment used to calm inflammation and redness associated with rosacea.",
    category: "light-therapy",
    verified: false,
    verifiedDate: null,
    availabilityAtCairns: "unconfirmed",
    clinicVerificationRequired: true,
    bookingUrl: "https://www.laserclinics.com.au/skin-care-treatments/kleresca-skin-treatments/",
    notes: "Confirm availability at Laser Clinics Cairns specifically; distinct platform from standard LED light therapy.",
  },
};

export function getTreatment(key: string): TreatmentMeta | undefined {
  return treatments[key];
}

export function listTreatments(): TreatmentMeta[] {
  return Object.values(treatments);
}
