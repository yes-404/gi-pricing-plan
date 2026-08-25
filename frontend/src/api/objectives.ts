import { request } from "./client";
import type { components } from "./generated/schema";

export type CustomObjective = components["schemas"]["CustomObjective"];
export type ObjectiveStatus = components["schemas"]["ObjectiveStatus"];
export type ObjectivePage = components["schemas"]["Page_CustomObjective_"];

/**
 * How many pages `listObjectives` will fetch before it stops and says so.
 *
 * **OQ-MODEL-35.** `GET /custom-objectives` filters by `status` and `slug` only, so
 * applicability filtering — which FR-MODEL-44 makes necessary, since offering an
 * inapplicable objective manufactures the error the requirement prevents — happens in the
 * client, over a cursor-paginated list. A picker that filtered only the page it happened
 * to hold would render "no applicable objectives" while applicable ones sat on page two,
 * and an empty picker is indistinguishable from a workspace that owns none.
 *
 * A named constant rather than a bare `5` in the loop: the rationale lives in an open
 * question a future reader has no reason to know exists, and the name is what carries them
 * to it. The cap is the *point* of option (a) rather than an implementation detail — an
 * implementation that quietly stopped paging would reproduce the exact defect the question
 * exists to fix, which is why `truncated` below is part of the return type and not a log
 * line.
 */
export const OBJECTIVE_PAGE_CAP = 5;

/**
 * The statuses a fit accepts — `FITTABLE_OBJECTIVE_STATUSES` in `model-schema`, which
 * reaches no contract (OQ-MODEL-37's second surface, where option (a) cannot help because
 * a subset of an enum's members is not a field type).
 *
 * **A set, not a ladder.** `objectives.py`:160-161 permits `REVIEW → {APPROVED,
 * CERTIFIED}`, so an objective in review can return to certified, and neither `draft` nor
 * `certified` may jump straight to `approved`. Nothing here or in any caller may present
 * these three as a sequence.
 *
 * Distinct from R4's rule, which is `approved` alone and governs whether a **Model** may
 * reach approval — not whether a spec may be fitted. `builtinObjectives.test.ts` pins this
 * against `objectives.py` directly, in both directions.
 */
// `satisfies` stays on the line `as const` ends — a continuation line starting with
// `satisfies` is a parse error, because ASI has already closed the statement.
type Fittable = readonly ObjectiveStatus[];
export const FITTABLE_OBJECTIVE_STATUSES = ["certified", "review", "approved"] as const satisfies Fittable;

/** `MAX_LIMIT` server-side. Fewer, larger pages is fewer round trips for the same set. */
const PAGE_SIZE = 200;

export interface ObjectiveList {
  items: CustomObjective[];
  /**
   * `true` when the cap was reached with a cursor still outstanding — i.e. the platform
   * holds objectives this list has **not seen**. The picker must say so; a filtered list
   * presented as complete is the defect OQ-MODEL-35 describes.
   */
  truncated: boolean;
}

/**
 * The workspace's Custom Objectives, up to `OBJECTIVE_PAGE_CAP` pages.
 *
 * `status` is passed through to the server, which is the one axis it can filter on.
 * Applicability is the caller's to apply, because the route cannot (OQ-MODEL-35).
 */
export async function listObjectives(
  options: { status?: ObjectiveStatus | undefined } = {},
): Promise<ObjectiveList> {
  const items: CustomObjective[] = [];
  let cursor: string | undefined;

  for (let page = 0; page < OBJECTIVE_PAGE_CAP; page += 1) {
    const result = await request<ObjectivePage>("/custom-objectives", {
      query: { status: options.status, cursor, limit: PAGE_SIZE },
    });
    items.push(...result.items);
    if (!result.next_cursor) return { items, truncated: false };
    cursor = result.next_cursor;
  }

  // The cap was reached and a cursor is still outstanding.
  return { items, truncated: true };
}
