import { describe, expect, it } from "vitest";
import { createRouter, createMemoryHistory } from "vue-router";

import { routes } from "../index";

/**
 * Route **resolution** — asserted directly, because it is the property that matters.
 *
 * `/models/new` and `/models/:slug` both match the literal path `/models/new`. W6b-4a's
 * plan (F4) said declaration order decides which wins, and that a builder declared second
 * would be captured by `:slug`, mounting `ModelDetailView` with `slug: "new"`. **False, on
 * vue-router 5.2.0**: a static segment outranks a dynamic one from either position.
 *
 * The claim was caught because the mutation meant to prove the guard — moving the record
 * below — did not fail. It was then measured with a positive control: two *equal-rank*
 * dynamic routes, where nothing but declaration order can break the tie, do flip. A probe
 * that reports "order does not matter" is worth nothing unless it can detect order
 * mattering.
 *
 * **The repo already knew.** W6b-2 ran the same experiment on `/models/compare` vs
 * `/models/:slug` on 2026-08-24 and wrote the answer into the `/models/compare` entry,
 * twelve lines above the `/models/:slug` declaration the plan cited. Neither the plan nor
 * its review read up that far. A finding about a file is worth grepping that file for
 * first: the previous slice's measurement lives in the code as a comment, and no
 * requirement-id search will surface it.
 *
 * So these tests do not guard an ordering hazard; there is none to guard. They assert that
 * `/models/new` reaches the builder and that a real slug still reaches model detail, both
 * of which stay true under reordering and would break under a genuinely wrong path.
 */
function router() {
  return createRouter({ history: createMemoryHistory(), routes });
}

function matchedNames(path: string): string[] {
  return router().resolve(path).matched.map((record) => record.name as string);
}

describe("the /models routes", () => {
  it("resolves /models/new to the spec builder", () => {
    expect(matchedNames("/models/new")).toContain("model-spec-builder");
  });

  it("does not resolve /models/new to model detail with slug 'new'", () => {
    // The specific wrong answer, asserted as wrong rather than left to the test above:
    // both routes matching would still satisfy `toContain`.
    const resolved = router().resolve("/models/new");

    expect(matchedNames("/models/new")).not.toContain("model-detail");
    expect(resolved.params.slug).toBeUndefined();
  });

  it("still resolves a real slug to model detail", () => {
    // The control. A `/models/new` record that swallowed every model path would pass
    // both assertions above.
    const resolved = router().resolve("/models/motor-ad-frequency");

    expect(resolved.matched.map((r) => r.name)).toContain("model-detail");
    expect(resolved.params.slug).toBe("motor-ad-frequency");
  });
});
