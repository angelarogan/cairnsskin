/**
 * TREATMENT FINDER: DATA MODEL
 * ----------------------------------------------------------------
 * Single authoritative data source for the Skin Concern Treatment
 * Finder (/tools/skin-treatment-finder/). The UI reads entirely from
 * this data layer (concerns.ts, categories.ts, matches.ts). To add a
 * new concern, sub-concern or treatment category, edit the data files
 * in this directory, not the components.
 *
 * publicMatcherStatus is the safety firewall: the renderer must never
 * display a treatment category whose status is not "allowed". There
 * is no "excluded" entry for prescription medicines anywhere in this
 * data set: they are simply never modelled, which is the strongest
 * form of exclusion available.
 */

export type PublicMatcherStatus = "allowed" | "assessment_only" | "excluded";

export type Relevance = "strong" | "consider" | "supportive" | "assess";

export type EvidenceLabel =
  | "Stronger evidence"
  | "Moderate evidence"
  | "Emerging evidence"
  | "Limited evidence"
  | "Evidence varies by indication"
  | "Evidence summary being reviewed";

export type DowntimeCategory = "Minimal" | "Short" | "Moderate" | "Varies";

export interface TreatmentCategory {
  id: string;
  label: string;
  shortDescription: string;
  /** Default evidence label, used when a match doesn't override it. Never invented: see EVIDENCE RATINGS rule in matches.ts. */
  evidence: EvidenceLabel;
  /** Real, verified Cairns Skin URL only. Omit rather than invent a URL. */
  internalLink?: string;
  /** Only set when grounded in an existing Cairns Skin treatment page's own downtime text. Omitted (renders as "Varies") otherwise. */
  downtime?: DowntimeCategory;
  publicMatcherStatus: PublicMatcherStatus;
}

export interface SubConcern {
  slug: string;
  label: string;
  /** Special pathways bypass normal matching entirely. */
  pathway?: "not_sure" | "assessment_only" | "medical_safety" | "branching";
}

export interface Concern {
  slug: string;
  label: string;
  shortDescription: string;
  icon: string;
  subConcerns: SubConcern[];
  /** Real, verified Cairns Skin concern hub URL only, when one exists. */
  internalLink?: string;
}

export interface Match {
  concern: string;
  subConcern: string;
  treatmentCategory: string;
  relevance: Relevance;
  shortReason: string;
  limitations: string;
  /** Overrides the category's default evidence label for this specific match, only when there is a real reason to. */
  evidenceOverride?: EvidenceLabel;
  publicMatcherStatus: PublicMatcherStatus;
}

export const RELEVANCE_LABEL: Record<Relevance, string> = {
  strong: "Strong option to explore",
  consider: "May be relevant",
  supportive: "Supportive option",
  assess: "Assessment recommended",
};
