export const SITE_NAME = "Cairns Skin";
export const SITE_URL = "https://cairnsskin.com.au";
export const DEFAULT_DESCRIPTION =
  "Clear, evidence-informed answers about skin concerns, skincare and non-prescription skin treatments, connected to Laser Clinics Cairns.";

export interface SeoProps {
  title: string;
  description?: string;
  canonicalUrl?: string;
  path: string;
  noindex?: boolean;
}

export function formatDisplayDate(date: Date): string {
  return date.toLocaleDateString("en-AU", { day: "numeric", month: "long", year: "numeric" });
}

export function buildSeo({ title, description, canonicalUrl, path, noindex }: SeoProps) {
  const fullTitle = title.includes(SITE_NAME) ? title : `${title} | ${SITE_NAME}`;
  const canonical = canonicalUrl ?? new URL(path, SITE_URL).toString();
  return {
    title: fullTitle,
    description: description ?? DEFAULT_DESCRIPTION,
    canonical,
    noindex: Boolean(noindex),
  };
}
