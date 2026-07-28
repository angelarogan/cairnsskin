import { SITE_NAME, SITE_URL } from "./seo";

export function breadcrumbSchema(items: { name: string; url: string }[]) {
  return {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: items.map((item, i) => ({
      "@type": "ListItem",
      position: i + 1,
      name: item.name,
      item: new URL(item.url, SITE_URL).toString(),
    })),
  };
}

export function faqSchema(items: { question: string; answer: string }[]) {
  return {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: items.map((item) => ({
      "@type": "Question",
      name: item.question,
      acceptedAnswer: {
        "@type": "Answer",
        text: item.answer,
      },
    })),
  };
}

export function articleSchema(params: {
  headline: string;
  description: string;
  authorName: string;
  reviewerName?: string;
  publishDate?: Date;
  updatedDate?: Date;
  url: string;
}) {
  return {
    "@context": "https://schema.org",
    "@type": "MedicalWebPage",
    headline: params.headline,
    description: params.description,
    url: new URL(params.url, SITE_URL).toString(),
    author: {
      "@type": "Person",
      name: params.authorName,
    },
    ...(params.reviewerName
      ? {
          reviewedBy: {
            "@type": "Person",
            name: params.reviewerName,
          },
        }
      : {}),
    ...(params.publishDate ? { datePublished: params.publishDate.toISOString() } : {}),
    ...(params.updatedDate ? { dateModified: params.updatedDate.toISOString() } : {}),
    publisher: {
      "@type": "Organization",
      name: SITE_NAME,
      url: SITE_URL,
    },
  };
}
