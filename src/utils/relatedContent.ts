import { getEntry, type CollectionEntry } from "astro:content";

/**
 * Resolves an array of content references into their entries,
 * silently skipping any that fail to resolve (e.g. draft content
 * removed) so templates never throw on a stale reference.
 */
type Collection = "questions" | "concerns" | "treatments" | "authors";

export async function resolveRefs<C extends Collection>(
  refs: { collection: C; slug: string }[] | undefined,
): Promise<CollectionEntry<C>[]> {
  if (!refs?.length) return [];
  const resolved: CollectionEntry<C>[] = [];
  for (const ref of refs) {
    try {
      const entry = (await getEntry(ref.collection, ref.slug)) as CollectionEntry<C>;
      if (entry) resolved.push(entry);
    } catch {
      // stale reference — skip silently rather than throwing at build time
    }
  }
  return resolved;
}

/** True only when content is safe to render in production. */
export function isPublishable(entry: { data: { draft: boolean; reviewStatus: string } }) {
  return entry.data.draft === false && entry.data.reviewStatus === "published";
}
