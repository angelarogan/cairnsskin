import { defineCollection, reference, z } from "astro:content";

const reviewStatusEnum = z.enum([
  "draft",
  "clinical-review",
  "compliance-review",
  "approved",
  "published",
]);

const ahpraRiskEnum = z.enum(["low", "moderate", "high"]);

const evidenceLevelEnum = z.enum([
  "established",
  "emerging",
  "manufacturer-claim",
  "clinical-experience",
  "limited-evidence",
]);

const sourceSchema = z.object({
  label: z.string(),
  url: z.string().url().optional(),
  publisher: z.string().optional(),
  year: z.number().optional(),
});

const authors = defineCollection({
  type: "content",
  schema: z.object({
    name: z.string(),
    role: z.string(),
    credentials: z.string().optional(),
    bio: z.string(),
    avatar: z.string().optional(),
    isReviewer: z.boolean().default(false),
  }),
});

const concerns = defineCollection({
  type: "content",
  schema: ({ image }) =>
    z.object({
      title: z.string(),
      shortSummary: z.string().max(220),
      description: z.string(),
      heroImage: image().optional(),
      video: z
        .object({
          url: z.string().url(),
          title: z.string(),
          description: z.string(),
          thumbnailUrl: z.string().url(),
          uploadDate: z.date(),
          durationSeconds: z.number().optional(),
        })
        .optional(),
      relatedTreatments: z.array(reference("treatments")).default([]),
      relatedQuestions: z.array(reference("questions")).default([]),
      tropicalContext: z.string().optional(),
      seoTitle: z.string().optional(),
      seoDescription: z.string().max(160).optional(),
      canonicalUrl: z.string().url().optional(),
      reviewStatus: reviewStatusEnum.default("draft"),
      reviewedBy: reference("authors").optional(),
      reviewDate: z.date().optional(),
      publishDate: z.date().optional(),
      updatedDate: z.date().optional(),
      featured: z.boolean().default(false),
      draft: z.boolean().default(true),
    }),
});

const treatments = defineCollection({
  type: "content",
  schema: ({ image }) =>
    z.object({
      title: z.string(),
      treatmentDataKey: z.string(), // maps to src/data/treatments.ts entry
      shortSummary: z.string().max(220),
      description: z.string(),
      heroImage: image().optional(),
      relatedConcerns: z.array(reference("concerns")).default([]),
      relatedQuestions: z.array(reference("questions")).default([]),
      benefits: z.array(z.string()).default([]),
      limitations: z.array(z.string()).default([]),
      sideEffects: z.array(z.string()).default([]),
      suitability: z.string().optional(),
      downtime: z.string().optional(),
      sources: z.array(sourceSchema).default([]),
      seoTitle: z.string().optional(),
      seoDescription: z.string().max(160).optional(),
      canonicalUrl: z.string().url().optional(),
      reviewStatus: reviewStatusEnum.default("draft"),
      reviewedBy: reference("authors").optional(),
      reviewDate: z.date().optional(),
      publishDate: z.date().optional(),
      updatedDate: z.date().optional(),
      evidenceLevel: evidenceLevelEnum.default("clinical-experience"),
      ahpraRisk: ahpraRiskEnum.default("moderate"),
      clinicVerificationRequired: z.boolean().default(true),
      featured: z.boolean().default(false),
      draft: z.boolean().default(true),
    }),
});

const questions = defineCollection({
  type: "content",
  schema: z.object({
    title: z.string(),
    primaryQuestion: z.string(),
    shortAnswer: z.string().max(320),
    description: z.string(),
    category: z.string(),
    relatedConcern: z.array(reference("concerns")).default([]),
    relatedTreatments: z.array(reference("treatments")).default([]),
    relatedQuestions: z.array(reference("questions")).default([]),
    tags: z.array(z.string()).default([]),
    author: reference("authors"),
    reviewedBy: reference("authors").optional(),
    reviewStatus: reviewStatusEnum.default("draft"),
    reviewDate: z.date().optional(),
    publishDate: z.date().optional(),
    updatedDate: z.date().optional(),
    evidenceLevel: evidenceLevelEnum.default("clinical-experience"),
    sources: z.array(sourceSchema).default([]),
    seoTitle: z.string().optional(),
    seoDescription: z.string().max(160).optional(),
    canonicalUrl: z.string().url().optional(),
    featured: z.boolean().default(false),
    draft: z.boolean().default(true),
    ahpraRisk: ahpraRiskEnum.default("moderate"),
    clinicVerificationRequired: z.boolean().default(true),
  }),
});

export const collections = { questions, concerns, treatments, authors };
