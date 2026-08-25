import { request } from "./client";

/**
 * A list gathered across pages, and whether the gathering stopped early.
 *
 * `truncated` is **in the return type on purpose**. The defect this guards is a filtered
 * list presented as complete: a caller that filters one page renders "none" while matches
 * sit on a later one, and an empty result is then indistinguishable from a genuinely empty
 * one. A `console.warn` would let a caller not handle it; a field will not.
 */
export interface Paged<T> {
  items: T[];
  /** `true` when the cap was reached with a cursor outstanding — more exist, unseen. */
  truncated: boolean;
}

/** The server's `MAX_LIMIT`. Fewer, larger pages is fewer round trips for one set. */
export const PAGE_SIZE = 200;

/**
 * Follow a cursor to exhaustion or to `cap` pages, whichever comes first.
 *
 * Extracted when the second caller arrived, which is where extraction pays: `listObjectives`
 * had this shape for `OQ-MODEL-35` — applicability is not a filter the objectives route
 * offers, so the client filters over a paginated list — and `listModels` needs it for
 * `OQ-MODEL-40`, the same shape one route over, since `GET /models` cannot filter by dataset
 * version either.
 *
 * **The cap belongs to the caller, not here.** Each caller names its own constant citing its
 * own open question: a shared cap would put one number in front of two different questions,
 * and a constant named for objectives appearing in a model path reads as deliberate to
 * whoever finds it next.
 *
 * **Order is preserved.** Pages are concatenated in the order the route returned them, and
 * callers depend on that — `listModels`' default is "the first row", which is only "most
 * recent" because the route orders by a UUIDv7 id. Nothing here sorts.
 */
export async function pageThrough<T>(
  path: string,
  query: Record<string, string | number | undefined>,
  cap: number,
): Promise<Paged<T>> {
  const items: T[] = [];
  let cursor: string | undefined;

  for (let page = 0; page < cap; page += 1) {
    const result = await request<{ items: T[]; next_cursor?: string | null }>(path, {
      query: { ...query, cursor, limit: PAGE_SIZE },
    });
    items.push(...result.items);
    if (!result.next_cursor) return { items, truncated: false };
    cursor = result.next_cursor;
  }

  // The cap was reached and a cursor is still outstanding.
  return { items, truncated: true };
}
