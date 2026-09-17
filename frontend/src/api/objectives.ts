import { request } from "./client";
import { pageThrough, type Paged } from "./paging";
import type { components } from "./generated/schema";

export type CustomObjective = components["schemas"]["CustomObjective"];
export type ObjectiveStatus = components["schemas"]["ObjectiveStatus"];

/**
 * How many pages `listObjectives` will fetch before it stops and says so.
 *
 * **OQ-605.** `GET /custom-objectives` filters by `status` and `slug` only, so
 * applicability filtering — which FR-153 makes necessary, since offering an
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
 * reaches no contract (OQ-607's second surface, where option (a) cannot help because
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

export type ObjectiveList = Paged<CustomObjective>;

export async function listObjectives(
  options: { status?: ObjectiveStatus | undefined } = {},
): Promise<ObjectiveList> {
  return pageThrough<CustomObjective>(
    "/custom-objectives", { status: options.status }, OBJECTIVE_PAGE_CAP,
  );
}

export type ObjectiveCertificate = components["schemas"]["ObjectiveCertificate"];

/**
 * FR-166's first read: status, certificate **outcome** and `approval_request_id` — not the
 * certificate itself, which is the second read below.
 */
export async function getObjective(id: string): Promise<CustomObjective> {
  return request<CustomObjective>(`/custom-objectives/${encodeURIComponent(id)}`);
}

/**
 * FR-166's second read: the latest `ObjectiveCertificate` for this version.
 *
 * **404 is a normal state, not an error.** A `draft` objective has not been certified, and
 * FR-166 specifies a 404 naming it. The caller branches on `ProblemError.code`, never on
 * the status — several codes share 404.
 */
export async function getObjectiveCertificate(id: string): Promise<ObjectiveCertificate> {
  return request<ObjectiveCertificate>(
    `/custom-objectives/${encodeURIComponent(id)}/certificate`,
  );
}
