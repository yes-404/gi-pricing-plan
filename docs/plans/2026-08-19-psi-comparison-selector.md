# The PSI Comparison Selector (`01` §5.3, FR-DATA-28) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the one unbuilt item in `01` §5.3's Profile row — a reference-version picker
on `/data/:slug/v/:version/profile` that calls FR-DATA-28's already-served `compare`
endpoint and bands each column's PSI against `VR-DST-1`'s thresholds.

**Architecture:** The backend, the maths and the API client function already exist and are
untouched by this plan. `compareProfiles()` has been implemented, typed and exported with
**zero callers** since W6a; this slice gives it its caller. The view gains a `<select>`
populated from `listVersions(slug)` (siblings only, versions without a stored profile
disabled rather than offered), a second fetch for the comparison, and a per-column drift
block extracted into its own component. The chosen reference lives in the **route query**
(`?against=<version>`), which is the decision gate below.

**Tech Stack:** Vue 3 `<script setup lang="ts">`, vue-router 4, Vitest +
`@testing-library/vue`, Tailwind. No new dependency. **No Pinia store** — see the gate.

**Spec:**
- [`docs/specs/01-data-management.md`](../specs/01-data-management.md) §5.3 (the Profile
  row and its 2026-08-19 note), §5.1 (the `compare` endpoint row), FR-DATA-28, FR-DATA-25.
- `01` §4.4 `VR-DST-1` — the PSI thresholds: **warn above 0.10, fail above 0.25**.
- [`docs/roadmap.md`](../roadmap.md) line ~2265 (the unowned-divergence row) and line
  ~763 (the Pinia row).

---

## Global Constraints

Copied verbatim from `CLAUDE.md` and `.claude/skills/vue-frontend`. Every task's requirements
implicitly include this section.

- **Nobody hand-writes a shape that already exists in `model-schema`.** Every type in this
  plan comes from `components["schemas"][...]` via `frontend/src/api/generated/schema.d.ts`.
  The generated client is git-ignored and regenerated with `pnpm --dir frontend generate:api`.
- **`exactOptionalPropertyTypes` is on.** Spread an optional rather than assigning
  `undefined`: `...(x ? { k: x } : {})`.
- **Exact decimals are strings and are rendered, never parsed** (FR-OVR-7). `psi`,
  `mean_shift`, `null_rate_shift` and `row_count_ratio` are **float64 statistics**, not
  money and not exact decimals — they are `number` on the wire and `.toFixed()` is correct
  for them. Do not reach for `formatDecimalString` here; it is for `exposure_years`.
- **Every non-2xx is a `ProblemDetail` and you branch on `code`**, never on the message.
- **Collections are cursor-paginated**: `{ items, next_cursor, total_estimate }`;
  `next_cursor` is opaque. Never parse it.
- **`<script setup lang="ts">` only.** No Options API, no JSX.
- **A prop and a ref cannot share a name** — `vue/no-dupe-keys` is an error. The route prop
  `version` (a string) is already taken; the comparison state must not reuse it.
- **`pnpm` is at `~/.npm-global/bin` and not on the default PATH.** Prefix commands with
  `PATH="$HOME/.npm-global/bin:$PATH"` or export it once per shell.
- **Requirement IDs are permanent** (`CLAUDE.md` §5): append, never renumber, mark superseded
  rather than removing.
- **When code and spec disagree, resolve it — do not quietly change one to match the other**
  (`CLAUDE.md` §0).

### The gate (run both halves, read each command's own exit code)

```bash
export PATH="$HOME/.npm-global/bin:$PATH"

# Frontend — the half this slice actually touches.
pnpm --dir frontend generate:api
pnpm --dir frontend lint
pnpm --dir frontend type-check
pnpm --dir frontend test
pnpm --dir frontend build

# Docs — Task 1 and Task 6 touch docs/, so these must be green at those commits.
python3 scripts/audit-docs.py
uv run python scripts/req-coverage.py

# Python — untouched by this slice, but run once before the PR so the claim is measured.
uv run ruff check . && uv run mypy && uv run lint-imports && uv run pytest -q
```

`cmd | tail -1 && echo ok` reports **tail's** exit code and has produced a false clean here
more than once. Run each command on its own line.

### Baseline at the time of writing (2026-08-19, `main` at `e8f3bda`)

- Frontend suite: **113 tests**. Python suite: **1339**, zero skipped.
- Requirements: **482 specified, 227 marked (47.1 %)**.
- Highest ids in use: **FR-DATA-52**, **OQ-DATA-10**. Next free: `FR-DATA-53`, `OQ-DATA-11`.
  **Confirm both are still free before writing either** — a peer session may have taken one.
- `frontend/src/stores/` exists on disk, is **empty and untracked**. Git does not track empty
  directories, so it is a local leftover, not a committed decision.

---

## ⚠ Decision gate — read before starting

**Question: where does the chosen reference version live?**

`01` §5.3's note and `docs/roadmap.md`'s Pinia row both **predict** that this slice brings the
frontend's first Pinia store, on the premise that the picker is "the first piece of Profile
state that must outlive a route". That premise is a prediction, not a requirement: neither
FR-DATA-28 nor §5.3 asks the reference to survive navigation, and no other requirement does.

| | Option | What it buys | What it costs |
|---|---|---|---|
| **A** *(recommended)* | **Route query `?against=<version>`** | A comparison an actuary can **send to a colleague as a URL**, that survives reload and back/forward. vue-router already owns URL state, so no new state layer. | First `useRoute`/`useRouter` in the app (every view so far takes props). Eleven existing `ProfileView` tests need a `vue-router` mock added. Dropped when navigating to a different version's profile. |
| **B** | **Pinia store** | Survives navigation between profile routes. Matches what §5.3 and the roadmap predicted. | Global state for one view's selection; **not shareable, lost on reload**. Pinia is registered in `main.ts` and unused, so this is a new layer for a single consumer. |
| **C** | **Local `ref`** | Smallest possible surface; zero test churn. | No persistence at all — a reload loses the comparison. |

**Recommendation: A.** It delivers everything B does except cross-route persistence, which
nothing asks for, and adds shareability, which a platform built around reproducibility and
audit has an obvious use for. B's stated justification does not survive being checked.

**This plan is written for A.** If the maintainer picks **C** instead, the only change is to
Task 3: drop Steps 8–9 (the query sync and its tests) and keep `referenceId` as a plain `ref`;
Tasks 2, 4, 5 and 6 are unaffected. If the maintainer picks **B**, stop and re-plan Task 3 —
a store needs its own file, its own test, and a decision about its lifetime.

**Whichever is chosen, Task 1 records it as `OQ-DATA-11` with the options and the outcome.**
Picking A silently would leave two documents predicting a store that never arrived, which is
exactly the "built around in silence" failure `01` §5.3's own note was written to end.

---

## File Structure

### Created

| Path | Responsibility |
|---|---|
| `frontend/src/components/ColumnDrift.vue` | Renders one column's drift: the banded PSI badge, mean shift, null-rate shift, new/vanished levels — or "new in this version" when the reference profile had no such column. Owns **all** of the band-colour decisions. |
| `frontend/src/components/__tests__/ColumnDrift.test.ts` | Its tests, including the unmeasured-PSI case that must not render a band. |
| `frontend/src/api/__tests__/profiles.test.ts` | Tests for `psiBand`'s thresholds. There is no test file for `profiles.ts` today. |

### Modified

| Path | Change |
|---|---|
| `frontend/src/api/profiles.ts` | Export `ColumnComparison`; narrow `psiBand` to reject an absent PSI. |
| `frontend/src/views/ProfileView.vue` | Reference-version `<select>`, comparison fetch, row-count-ratio line, `ColumnDrift` on each card. |
| `frontend/src/views/__tests__/ProfileView.test.ts` | `vue-router` mock; versions + compare added to the `fetch` stub; the existing band-colour regression test re-aimed at "before a comparison is loaded". |
| `docs/specs/01-data-management.md` | §5.3's note resolved (Task 6); OQ-DATA-11 mirrored into §10 (Task 1). |
| `docs/open-questions.md` | OQ-DATA-11 raised and decided. |
| `docs/roadmap.md` | The §5.3-divergence row and the Pinia row both resolved. |

### Deliberately not touched

- `backend/`, `packages/pricing-core`, `packages/model-schema` — the endpoint, the PSI maths
  and the wire shapes all exist and are correct. **If this slice makes you want to change
  one, stop**: that is a spec-versus-code disagreement and `CLAUDE.md` §0 governs it.
- `docs/contracts/` — generated, and nothing here changes a shape.
- `frontend/src/router/index.ts` — under option A the view reads the query itself; the
  existing `props: true` entry stays as it is.
- `frontend/src/stores/` — stays empty. Option A is the reason, and Task 1 records it.

---

## Task 1: Raise `OQ-DATA-11`, and get it decided

**Files:**
- Modify: `docs/open-questions.md` (the DATA table, after the `OQ-DATA-10` row)
- Modify: `docs/specs/01-data-management.md` (§10, the open-questions mirror)

**Interfaces:**
- Consumes: nothing.
- Produces: the decision every later task is built on. **Task 3 depends on the outcome.**

- [ ] **Step 1: Confirm the id is free**

```bash
grep -rn "OQ-DATA-11" docs/ .claude/ || echo "FREE"
```

Expected: `FREE`. If it is taken, take the next free id and use it consistently everywhere
below — a peer session may have raised one since this plan was written.

- [ ] **Step 2: Append the row to `docs/open-questions.md`**

Find the `## DATA` table and add this row immediately after the `OQ-DATA-10` row. The table's
columns are `| ID | Question | Options / trade-offs | Recommendation | Owner | Status |`.

```markdown
| **OQ-DATA-11** | `01` §5.3's PSI comparison selector needs somewhere to keep the chosen reference version. §5.3's own note and `docs/roadmap.md`'s Pinia row both predict the frontend's first **Pinia store**, on the premise that this is "the first piece of Profile state that must outlive a route". Is that premise right, or does the reference belong in the **route query**? | Raised 2026-08-19 (W5, the comparison-selector slice), by checking the premise rather than inheriting it. **Nothing requires the reference to survive navigation** — not FR-DATA-28, not §5.3, not any other requirement; the prediction was made before the selector had a design. **Route query `?against=<version>`:** vue-router already owns URL state, so no new state layer; the comparison becomes a link an actuary can send to a colleague, and survives reload and back/forward. Costs the first `useRoute`/`useRouter` in an app where every view so far takes props, and a `vue-router` mock in eleven existing view tests. **Pinia store:** survives navigation between profile routes and matches the prediction, but is global state for a single consumer, is **not shareable**, and is lost on reload. **Local ref:** smallest surface, no persistence at all. | **The route query.** It delivers everything the store does except cross-route persistence, which nothing asks for, and adds shareability, which is worth more in a platform built around reproducibility than a selection surviving a click into the version detail page. The store's justification — state that must outlive a route — does not survive being checked, and a global store built for one view's `<select>` is a layer nobody can later remove without knowing why it was added. `frontend/src/stores/` stays empty and the first store waits for state that genuinely is global; the workspace selector W6b carries is the likelier candidate. | maintainer | **open** |
```

- [ ] **Step 3: Mirror the id into `01` §10**

`audit-docs.py` checks that every open question is mirrored in its module spec's §10. Find
§10 in `docs/specs/01-data-management.md` and add a line matching the format of the entries
already there (read two of them first and copy the shape exactly — do **not** invent one):

```markdown
- **OQ-DATA-11** — where the PSI comparison selector's chosen reference version lives: the
  route query, a Pinia store, or a local ref. Raised 2026-08-19 by the slice that builds §5.3's
  selector; §5.3's note and the roadmap both predicted a store, on a premise no requirement
  states.
```

- [ ] **Step 4: Run the docs audit**

```bash
python3 scripts/audit-docs.py
```

Expected: exit 0, and the question count one higher than the baseline's 65 (so **66**), all
mirrored. A non-zero exit here is almost always the mirror in Step 3 not matching the format
of its neighbours, or a `|` inside a code span splitting a table row.

- [ ] **Step 5: Commit**

```bash
git add docs/open-questions.md docs/specs/01-data-management.md
git commit -m "docs(data): OQ-DATA-11 — where the comparison selector's reference lives"
```

- [ ] **Step 6: Ask the maintainer to decide, and stop if the answer is B**

Present the three options and the recommendation. **Do not start Task 3 before this is
answered** — Task 2 is independent and may proceed meanwhile. If the answer is the Pinia
store, stop and re-plan Task 3 rather than improvising a store.

Once answered, update the row's Status to `**decided**` with the date and the reasoning
actually given, strike the question text (`~~…~~`) and prefix the id with
`~~**OQ-DATA-11**~~ ✔`, following the shape of the decided rows above it. Commit that as a
separate commit.

---

## Task 2: `psiBand` refuses a PSI that was never measured

**Files:**
- Modify: `frontend/src/api/profiles.ts:41-51`
- Create: `frontend/src/api/__tests__/profiles.test.ts`

**Interfaces:**
- Consumes: nothing.
- Produces: `psiBand(psi: number): "stable" | "shifted" | "broken"` — narrowed from
  `(psi: number | null | undefined)`. Task 5's `ColumnDrift.vue` is its only caller, and must
  guard `psi != null` before calling it.
- Produces: `export type ColumnComparison = components["schemas"]["ColumnComparison"];`

**Why this is its own task:** `psiBand(null)` currently returns `"stable"`. That is the exact
defect `01` §5.3's note records — *"`psiBand(null)` returned `"stable"` before any threshold,
so the badge was never showing a PSI band, only the colour of one"* — and the note fixed the
symptom by uncolouring the dtype label while leaving the function able to do it again. A
column with no non-null `top_levels` gets `psi: null` from `compare_profiles`, so under the
old signature every continuous column would render as green "stable" the moment this slice
gave the function a caller. Narrowing the type makes that a **compile error**, not a
judgement the next caller has to remember.

- [ ] **Step 1: Write the failing tests**

Create `frontend/src/api/__tests__/profiles.test.ts`:

```ts
import { describe, expect, it } from "vitest";

import { psiBand } from "@/api/profiles";

describe("psiBand", () => {
  // `01` §4.4's VR-DST-1: warn **above** 0.10, fail **above** 0.25. The boundaries are
  // exclusive, so a PSI landing exactly on a threshold is the calmer band — the same
  // reading the validation rule uses, because a rule's verdict and this badge must not
  // disagree about one number.
  it("bands strictly above each threshold, never on it", () => {
    expect(psiBand(0)).toBe("stable");
    expect(psiBand(0.1)).toBe("stable");
    expect(psiBand(0.1001)).toBe("shifted");
    expect(psiBand(0.25)).toBe("shifted");
    expect(psiBand(0.2501)).toBe("broken");
  });

  // A PSI that was never measured is not a stable one. `compare_profiles` returns
  // `psi: null` for any column whose `top_levels` carry no non-null level — every
  // continuous column, in practice. The old signature accepted null and answered
  // "stable", which is how a column nobody measured came to render as green.
  it("does not accept an absent PSI", () => {
    // @ts-expect-error — null is refused at the type level; the caller must guard.
    expect(() => psiBand(null)).toBeDefined();
  });
});
```

- [ ] **Step 2: Run them to verify they fail**

```bash
PATH="$HOME/.npm-global/bin:$PATH" pnpm --dir frontend test -- profiles
```

Expected: the threshold test **passes** already (the boundaries are unchanged), and the
second **fails** — `@ts-expect-error` reports "Unused '@ts-expect-error' directive" because
`null` is currently a legal argument. That unused-directive error is the failing test.

> If `vitest run -- profiles` does not filter as expected, run the whole suite; the file is
> small and the signal is the same. The `@ts-expect-error` failure surfaces under
> `type-check` even if `vitest` alone reports green, which is why Step 4 runs both.

- [ ] **Step 3: Narrow the signature and export the row type**

In `frontend/src/api/profiles.ts`, add the type export beside the others near the top:

```ts
export type ColumnComparison = components["schemas"]["ColumnComparison"];
```

and replace the `psiBand` declaration line:

```ts
export function psiBand(psi: number): "stable" | "shifted" | "broken" {
```

Leave the body exactly as it is **except** for deleting the `if (psi == null) return "stable";`
line, and extend the docstring:

```ts
/**
 * PSI bands, as `01` §4.4's VR-DST-1 states them: warn above 0.10, fail above 0.25.
 *
 * The same thresholds the validation rule uses, so a stable-looking column here and a
 * warning in the report cannot disagree about the same number.
 *
 * **Takes a `number`, not a nullable one.** `compare_profiles` returns `psi: null` for a
 * column it could not measure — every column with no non-null `top_levels`. An earlier
 * version answered `"stable"` for that, so an unmeasured column rendered as a calm band
 * rather than as no band at all; the caller now has to decide, and the type makes it.
 */
```

- [ ] **Step 4: Run the tests and the type-check**

```bash
PATH="$HOME/.npm-global/bin:$PATH" pnpm --dir frontend test
PATH="$HOME/.npm-global/bin:$PATH" pnpm --dir frontend type-check
```

Expected: both green. The suite is **115** now (113 + 2). `type-check` matters as much as the
test here — the narrowing is a type change, and `vitest` alone does not check types.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/api/profiles.ts frontend/src/api/__tests__/profiles.test.ts
git commit -m "refactor(frontend): psiBand refuses a PSI that was never measured"
```

---

## Task 3: The reference-version selector

**Files:**
- Modify: `frontend/src/views/ProfileView.vue`
- Modify: `frontend/src/views/__tests__/ProfileView.test.ts`

**Interfaces:**
- Consumes: `listVersions(slug, options)` from `@/api/datasets` → `Promise<VersionPage>`;
  `DatasetVersion` from `@/api/versions` (fields used: `id`, `version`, `profile_id`).
- Produces: `referenceId: Ref<string | null>` — a version **id**, which Task 4's comparison
  fetch reads; `siblings: Ref<DatasetVersion[]>`, which Task 4's `referenceLabel` reads; and
  the `<select>` labelled **"Compare against"**.

**Design, and the two refusals in it:**

1. **Siblings only, current version excluded.** Comparing a version with itself is PSI 0
   everywhere — a row of green that means nothing.
2. **A version with `profile_id === null` is listed but `disabled`, suffixed "(no profile)".**
   The compare endpoint 404s with `NOT_FOUND` and the detail *"This dataset version has no
   profile"* for such a reference. Offering it and then explaining the 404 is the pattern
   FR-DATA-27's one-way handling deliberately avoids; `DatasetVersion.profile_id` already
   carries the answer, so the picker refuses before the request rather than after it.

- [ ] **Step 1: Write the failing tests**

Add to `frontend/src/views/__tests__/ProfileView.test.ts`. First extend the fixtures near
`VERSION` at the top of the file:

```ts
const VERSIONS = {
  items: [
    { id: PROFILE.dataset_version_id, version: 2, profile_id: "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa" },
    { id: "33333333-3333-4333-8333-333333333333", version: 1, profile_id: "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb" },
    // A version that was ingested but never profiled: the endpoint would 404 for it, so
    // the picker must not offer it as a choice.
    { id: "44444444-4444-4444-8444-444444444444", version: 3, profile_id: null },
  ],
  next_cursor: null,
  total_estimate: 3,
};

// Replaced by a real fixture in Task 4. Declared here so the stub below compiles.
const COMPARISON: unknown = null;
```

Then the tests:

```ts
it("offers the other versions of the dataset, and never the one being viewed", async () => {
  render(ProfileView, { props, ...mounted });
  const select = await screen.findByLabelText("Compare against");
  const options = within(select).getAllByRole("option").map((o) => o.textContent?.trim());
  // v2 is the version on screen — comparing it with itself is PSI 0 everywhere.
  expect(options).not.toContain("v2");
  expect(options).toContain("v1");
});

it("disables a version that has no stored profile rather than offering a 404", async () => {
  // `compare` answers 404 NOT_FOUND for a reference with no profile. `profile_id` already
  // says so, so the refusal happens in the picker instead of after the request.
  render(ProfileView, { props, ...mounted });
  const select = await screen.findByLabelText("Compare against");
  const unprofiled = within(select).getByRole("option", { name: /v3 \(no profile\)/ });
  expect(unprofiled).toBeDisabled();
});
```

- [ ] **Step 2: Extend the `fetch` stub so the new calls are answered**

The existing `stub()` answers `/one-ways`, `/profile` and the version lookup. Each branch must
be explicit so one URL cannot match two. Replace the body of `stub()`:

```ts
function stub(
  oneWayStatus = 200,
  oneWayBody: unknown = ONE_WAY,
  compare: { status?: number; body?: unknown } = {},
): void {
  vi.stubGlobal(
    "fetch",
    vi.fn(async (input: string | URL) => {
      const url = String(input);
      const json = (body: unknown, status = 200): Response =>
        new Response(JSON.stringify(body), {
          status,
          headers: { "Content-Type": "application/json" },
        });

      if (url.includes("/one-ways")) return json(oneWayBody, oneWayStatus);
      if (url.includes("/compare")) return json(compare.body ?? COMPARISON, compare.status ?? 200);
      if (url.includes("/versions")) return json(VERSIONS);
      if (url.includes("/profile")) return json(PROFILE);
      return json(VERSION);
    }),
  );
}
```

> Order matters: `/datasets/{slug}/versions` and `/dataset-versions/{id}/profile` both contain
> the substring `version`, so the `/profile` branch must come **after** `/versions` and the
> bare version lookup must stay the fall-through.

- [ ] **Step 3: Add the `vue-router` mock (option A only)**

At the top of the test file, beside the existing `vi.mock` calls:

```ts
// The view reads `?against` and writes it back with `router.replace` (OQ-DATA-11). A real
// router would make every test in this file wait on navigation readiness; the mock keeps
// the query controllable and lets one test assert what the view wrote.
const routerReplace = vi.fn();
const routeQuery: { against?: string } = {};
vi.mock("vue-router", async (importOriginal) => ({
  ...(await importOriginal<typeof import("vue-router")>()),
  useRoute: () => ({ query: routeQuery }),
  useRouter: () => ({ replace: routerReplace }),
}));
```

and replace the existing `beforeEach(() => stub());`:

```ts
beforeEach(() => {
  routerReplace.mockClear();
  delete routeQuery.against;
  stub();
});
```

- [ ] **Step 4: Run the tests to verify they fail**

```bash
PATH="$HOME/.npm-global/bin:$PATH" pnpm --dir frontend test -- ProfileView
```

Expected: both new tests fail with `findByLabelText("Compare against")` timing out — there is
no such control yet. The **existing** eleven tests must still pass; if the `fetch` stub
rewrite broke one, fix that before going on rather than carrying it into the next step.

- [ ] **Step 5: Load the sibling versions**

In `frontend/src/views/ProfileView.vue`, extend the imports:

```ts
import { listVersions } from "@/api/datasets";
import type { DatasetVersion } from "@/api/versions";
```

and add state beside the existing refs (**not** named `version` — that is the route prop, and
`vue/no-dupe-keys` is an error):

```ts
const siblings = ref<DatasetVersion[]>([]);
const truncated = ref(false);
const referenceId = ref<string | null>(null);
```

Extend `load()` — after `profile.value` is set, inside the same `try`:

```ts
// `MAX_LIMIT` is 200 and versions come back newest-first, so one page is the selector's
// universe. If there is a cursor left, say so rather than silently offering a subset.
const page = await listVersions(props.slug, { limit: 200 });
siblings.value = page.items.filter((v) => v.id !== version.id);
truncated.value = page.next_cursor != null;
```

- [ ] **Step 6: Render the picker**

Insert this section in the template, immediately **after** the `<p>` row-count summary and
before the `One-way` section:

```html
<section class="mt-6">
  <div class="flex items-center gap-3">
    <h2 class="text-sm font-semibold uppercase tracking-wide text-slate-500">
      Drift
    </h2>
    <select
      v-if="siblings.length"
      v-model="referenceId"
      aria-label="Compare against"
      class="rounded-md border border-slate-300 px-2 py-1 text-sm"
    >
      <option :value="null">
        No comparison
      </option>
      <!-- A version with no stored profile cannot be compared against: the endpoint
           answers 404 and `profile_id` already says so, so it is shown as unavailable
           rather than offered and then explained. -->
      <option
        v-for="sibling in siblings"
        :key="sibling.id"
        :value="sibling.id"
        :disabled="sibling.profile_id == null"
      >
        v{{ sibling.version }}{{ sibling.profile_id == null ? " (no profile)" : "" }}
      </option>
    </select>
    <p
      v-else
      class="text-sm text-slate-500"
    >
      No other version of this dataset to compare against.
    </p>
  </div>
  <p
    v-if="truncated"
    class="mt-2 text-xs text-slate-500"
  >
    Showing the 200 most recent versions.
  </p>
</section>
```

- [ ] **Step 7: Run the tests to verify they pass**

```bash
PATH="$HOME/.npm-global/bin:$PATH" pnpm --dir frontend test -- ProfileView
```

Expected: 13 passing in this file (11 existing + 2 new). If `getByRole("option", { name: /v3 \(no profile\)/ })`
does not match, the accessible name has collapsed differently than expected — read the
rendered option's text before adjusting the regex, and do not adjust the template to suit the
test.

- [ ] **Step 8: Sync the selection to the route query (option A only)**

Add to the script, after the existing imports:

```ts
import { useRoute, useRouter } from "vue-router";
```

and after the refs:

```ts
const route = useRoute();
const router = useRouter();
```

Seed the selection from the query once the siblings are known — at the end of the block added
in Step 5:

```ts
// `?against=<version number>`, not an id: the URL is something an actuary reads and sends,
// and a version number is what the rest of the app routes on. A version with no profile is
// ignored rather than honoured — a stale link must not put the view into a state the
// endpoint refuses.
const wanted = typeof route.query.against === "string" ? route.query.against : null;
const seeded = siblings.value.find((v) => String(v.version) === wanted);
referenceId.value = seeded?.profile_id != null ? seeded.id : null;
```

and write it back on change:

```ts
watch(referenceId, (id) => {
  const chosen = siblings.value.find((v) => v.id === id);
  void router.replace({
    query: {
      ...route.query,
      ...(chosen ? { against: String(chosen.version) } : { against: undefined }),
    },
  });
});
```

> `replace`, not `push`: changing the comparison refines the same view, and `push` would make
> the browser's back button walk every selection the user tried.

- [ ] **Step 9: Test the query round trip**

Add `waitFor` to the `@testing-library/vue` import, then:

```ts
it("seeds the comparison from the URL and writes the choice back to it", async () => {
  routeQuery.against = "1";
  render(ProfileView, { props, ...mounted });
  const select = await screen.findByLabelText("Compare against");
  // Seeded from `?against=1` — the comparison is shareable as a link.
  await waitFor(() =>
    expect((select as HTMLSelectElement).value).toBe(VERSIONS.items[1]?.id),
  );

  await userEvent.selectOptions(select, "");
  expect(routerReplace).toHaveBeenCalledWith(
    expect.objectContaining({ query: expect.objectContaining({ against: undefined }) }),
  );
});

it("ignores an ?against pointing at a version with no profile", async () => {
  // A stale or hand-edited link must not put the view into a state the endpoint refuses.
  routeQuery.against = "3";
  render(ProfileView, { props, ...mounted });
  const select = await screen.findByLabelText("Compare against");
  await waitFor(() => expect((select as HTMLSelectElement).value).toBe(""));
});
```

Run them; expect both green.

- [ ] **Step 10: Lint, type-check, commit**

```bash
PATH="$HOME/.npm-global/bin:$PATH" pnpm --dir frontend lint
PATH="$HOME/.npm-global/bin:$PATH" pnpm --dir frontend type-check
git add frontend/src/views/ProfileView.vue frontend/src/views/__tests__/ProfileView.test.ts
git commit -m "feat(frontend): a reference-version picker on the profile view"
```

`eslint --fix` reformats as it goes, so if you edited the template with `sed`, re-read the
file before the next task rather than editing against the pre-fix layout.

---

## Task 4: Fetch the comparison, and say what it covers

**Files:**
- Modify: `frontend/src/views/ProfileView.vue`
- Modify: `frontend/src/views/__tests__/ProfileView.test.ts`

**Interfaces:**
- Consumes: `compareProfiles(versionId, against)` from `@/api/profiles` →
  `Promise<ProfileComparison>`; `referenceId` and `siblings` from Task 3.
- Produces: `comparison: Ref<ProfileComparison | null>` and
  `driftFor(name: string): ColumnComparison | null | undefined`, which Task 5's component
  consumes. **The three-way return is deliberate** and Task 5 depends on it: `undefined` = no
  comparison loaded, `null` = a comparison is loaded but this column is not in it (it did not
  exist in the reference version), a value = measured.

- [ ] **Step 1: Write the failing tests**

Replace the `COMPARISON` placeholder from Task 3 Step 1 with a real fixture, typed against the
generated contract so a `model-schema` rename fails `type-check` here rather than leaving a
test that passes against a shape the API no longer sends:

```ts
import type { ProfileComparison } from "@/api/profiles";

const COMPARISON: ProfileComparison = {
  current_version_id: PROFILE.dataset_version_id,
  reference_version_id: "33333333-3333-4333-8333-333333333333",
  row_count_ratio: 1.0203,
  columns: [
    {
      column: "veh_brand",
      psi: 0.31,
      mean_shift: null,
      null_rate_shift: 0.012,
      new_levels: ["B14"],
      vanished_levels: [],
    },
    // Continuous: `compare_profiles` measures PSI from non-null `top_levels`, and this
    // column has none — so `psi` is null and there is no band to draw.
    {
      column: "driv_age",
      psi: null,
      mean_shift: 1.35,
      null_rate_shift: 0,
      new_levels: [],
      vanished_levels: [],
    },
  ],
};
```

and add the tests:

```ts
it("states how the row count moved once a reference is chosen", async () => {
  render(ProfileView, { props, ...mounted });
  const select = await screen.findByLabelText("Compare against");
  await userEvent.selectOptions(select, VERSIONS.items[1]?.id ?? "");
  expect(await screen.findByText(/×1\.020 rows vs v1/)).toBeInTheDocument();
});

it("treats a reference version with no profile as an answer, not a failure", async () => {
  // The endpoint 404s when the *reference* has no stored profile. The picker disables
  // those, so this is the stale-link case: it must read as an explanation, not an alert.
  stub(200, ONE_WAY, {
    status: 404,
    body: {
      title: "This dataset version has no profile",
      status: 404,
      code: "NOT_FOUND",
      errors: [],
    },
  });
  render(ProfileView, { props, ...mounted });
  const select = await screen.findByLabelText("Compare against");
  await userEvent.selectOptions(select, VERSIONS.items[1]?.id ?? "");
  expect(await screen.findByText(/has no profile to compare against/)).toBeInTheDocument();
  expect(screen.queryByRole("alert")).not.toBeInTheDocument();
});
```

- [ ] **Step 2: Run them to verify they fail**

```bash
PATH="$HOME/.npm-global/bin:$PATH" pnpm --dir frontend test -- ProfileView
```

Expected: both fail — nothing calls `compareProfiles` yet, so neither string is on screen.

- [ ] **Step 3: Fetch the comparison**

Extend the import from `@/api/profiles` with `compareProfiles`, `type ColumnComparison` and
`type ProfileComparison`. Add state:

```ts
const comparison = ref<ProfileComparison | null>(null);
const referenceMissingProfile = ref(false);
```

and the watcher, beside the existing `selected` watcher:

```ts
watch(referenceId, async (id) => {
  comparison.value = null;
  referenceMissingProfile.value = false;
  if (!id || !versionId.value) return;
  try {
    comparison.value = await compareProfiles(versionId.value, id);
  } catch (error) {
    // A reference with no stored profile is an answer, the same as FR-DATA-27's missing
    // one-way: the picker disables those versions, so reaching here means a stale or
    // hand-edited link. It explains itself and leaves the rest of the view intact.
    if (isProblem(error, "NOT_FOUND")) referenceMissingProfile.value = true;
    else throw error;
  }
});
```

> This watcher and Task 3 Step 8's `router.replace` watcher both fire on `referenceId`. Keep
> them separate: one talks to the API and one to the URL, and folding them together makes a
> failed fetch and a failed navigation share an error path.

Add the lookup, whose three-way return Task 5 consumes:

```ts
/**
 * The comparison entry for a column, if there is one.
 *
 * Three answers, not two. `compare_profiles` **skips** a column the reference profile does
 * not have, so a missing entry means "this column is new in this version" — which is a
 * finding, not an absence. `undefined` means no comparison has been loaded at all.
 */
function driftFor(name: string): ColumnComparison | null | undefined {
  if (!comparison.value) return undefined;
  return comparison.value.columns.find((c) => c.column === name) ?? null;
}
```

- [ ] **Step 4: Render the summary line and the refusal**

Add a computed beside the existing ones:

```ts
const referenceLabel = computed(() => {
  const chosen = siblings.value.find((v) => v.id === referenceId.value);
  return chosen ? `v${chosen.version}` : "";
});
```

and inside the Drift section added in Task 3, after the `truncated` paragraph:

```html
<p
  v-if="referenceMissingProfile"
  class="mt-2 text-sm text-slate-500"
>
  {{ referenceLabel }} has no profile to compare against. Profiling runs after a
  successful ingestion (FR-DATA-25).
</p>
<p
  v-else-if="comparison"
  class="mt-2 text-sm text-slate-600 tabular-nums"
>
  <!-- A float ratio, not an exact decimal: it is `current.row_count / reference.row_count`
       computed in float64 by `compare_profiles`, so it is shown as the statistic it is. -->
  ×{{ comparison.row_count_ratio?.toFixed(3) ?? "—" }} rows vs {{ referenceLabel }}
</p>
```

- [ ] **Step 5: Run the tests to verify they pass**

```bash
PATH="$HOME/.npm-global/bin:$PATH" pnpm --dir frontend test -- ProfileView
```

Expected: green. If the first test finds `×1.020 rows` but not the `vs v1` suffix,
`referenceLabel` is being read before the versions page resolved — assert with `findByText`,
which retries, rather than `getByText`, which does not.

- [ ] **Step 6: Lint, type-check, commit**

```bash
PATH="$HOME/.npm-global/bin:$PATH" pnpm --dir frontend lint
PATH="$HOME/.npm-global/bin:$PATH" pnpm --dir frontend type-check
git add frontend/src/views/ProfileView.vue frontend/src/views/__tests__/ProfileView.test.ts
git commit -m "feat(frontend): the profile view fetches FR-DATA-28's comparison"
```

---

## Task 5: `ColumnDrift.vue` — the band, and the four things beside it

**Files:**
- Create: `frontend/src/components/ColumnDrift.vue`
- Create: `frontend/src/components/__tests__/ColumnDrift.test.ts`
- Modify: `frontend/src/views/ProfileView.vue` (mount it on each card)
- Modify: `frontend/src/views/__tests__/ProfileView.test.ts` (re-aim the band-colour guard)

**Interfaces:**
- Consumes: `psiBand` and `ColumnComparison` (Task 2), `driftFor()` (Task 4).
- Produces: `<ColumnDrift :drift="driftFor(column.name)" />`, where `drift` is
  `ColumnComparison | null | undefined`.

**The rendering rules, all four of them:**

| `drift` | Renders |
|---|---|
| `undefined` | **Nothing.** No comparison is loaded; the card looks exactly as it does today. |
| `null` | "new in this version" — the reference profile had no such column. |
| `psi === null` | "PSI not measured", **uncoloured**. `compare_profiles` measures PSI from non-null `top_levels`, which a continuous column does not have. |
| `psi` a number | The banded badge, plus whichever of mean shift, null-rate shift, new and vanished levels are non-zero. |

- [ ] **Step 1: Write the failing component tests**

Create `frontend/src/components/__tests__/ColumnDrift.test.ts`:

```ts
import { render, screen } from "@testing-library/vue";
import { describe, expect, it } from "vitest";

import type { ColumnComparison } from "@/api/profiles";

import ColumnDrift from "../ColumnDrift.vue";

const MEASURED: ColumnComparison = {
  column: "veh_brand",
  psi: 0.31,
  mean_shift: null,
  null_rate_shift: 0.012,
  new_levels: ["B14"],
  vanished_levels: ["B7"],
};

describe("ColumnDrift", () => {
  it("renders nothing at all when no comparison is loaded", () => {
    // `undefined` is not "no drift" — it is "nobody asked". The card must look exactly as
    // it did before a reference was chosen.
    const { container } = render(ColumnDrift, { props: { drift: undefined } });
    expect(container.textContent?.trim()).toBe("");
  });

  it("says a column is new rather than showing it as unchanged", () => {
    // `compare_profiles` skips a column the reference profile does not have, so a missing
    // entry is a finding: the column did not exist in the version being compared against.
    render(ColumnDrift, { props: { drift: null } });
    expect(screen.getByText(/new in this version/)).toBeInTheDocument();
  });

  it("bands a PSI above VR-DST-1's fail threshold", () => {
    render(ColumnDrift, { props: { drift: MEASURED } });
    expect(screen.getByText(/PSI 0\.310/)).toHaveClass("text-red-700");
  });

  it("does not band a PSI that was never measured", () => {
    // The defect `01` §5.3's note recorded: an unmeasured PSI rendered as a calm band.
    // It must read as absent, and carry no band colour at all.
    const { container } = render(ColumnDrift, {
      props: { drift: { ...MEASURED, psi: null } },
    });
    expect(screen.getByText(/not measured/)).toBeInTheDocument();
    expect(container.innerHTML).not.toContain("text-amber-700");
    expect(container.innerHTML).not.toContain("text-red-700");
    expect(container.innerHTML).not.toContain("text-emerald-700");
  });

  it("reports the level changes and the null-rate shift", () => {
    render(ColumnDrift, { props: { drift: MEASURED } });
    expect(screen.getByText(/\+1 new/)).toBeInTheDocument();
    expect(screen.getByText(/1 vanished/)).toBeInTheDocument();
    // A rate shift is percentage **points**, signed — 0.012 is +1.20pp, not 1.2%.
    expect(screen.getByText(/\+1\.20pp nulls/)).toBeInTheDocument();
  });

  it("omits a shift that did not happen", () => {
    render(ColumnDrift, {
      props: {
        drift: {
          column: "x",
          psi: 0.02,
          mean_shift: null,
          null_rate_shift: 0,
          new_levels: [],
          vanished_levels: [],
        },
      },
    });
    expect(screen.queryByText(/nulls/)).not.toBeInTheDocument();
    expect(screen.queryByText(/new/)).not.toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run them to verify they fail**

```bash
PATH="$HOME/.npm-global/bin:$PATH" pnpm --dir frontend test -- ColumnDrift
```

Expected: every test fails on `Failed to resolve import "../ColumnDrift.vue"`.

- [ ] **Step 3: Write the component**

Create `frontend/src/components/ColumnDrift.vue`:

```vue
<script setup lang="ts">
import { computed } from "vue";

import { psiBand, type ColumnComparison } from "@/api/profiles";

/**
 * One column's drift against a reference version (FR-DATA-28).
 *
 * `drift` carries three states, not two. `undefined` means no comparison has been loaded;
 * `null` means one has, and this column is **not in it** — `compare_profiles` skips a
 * column the reference profile does not have, so its absence says the column is new rather
 * than that it did not move.
 */
const props = defineProps<{ drift: ColumnComparison | null | undefined }>();

/**
 * The band, or `null` when there is nothing to band.
 *
 * `psi` is null for any column whose `top_levels` carry no non-null level — every
 * continuous column in practice. `psiBand` refuses that argument outright, and this guard
 * is why: an unmeasured PSI must render as absent, never as the calm end of a scale
 * nobody computed.
 */
const band = computed(() => (props.drift?.psi != null ? psiBand(props.drift.psi) : null));

const TONE = {
  stable: "text-emerald-700",
  shifted: "text-amber-700",
  broken: "text-red-700",
} as const;
</script>

<template>
  <p
    v-if="drift === null"
    class="mt-2 text-xs font-medium text-sky-700"
  >
    new in this version
  </p>
  <dl
    v-else-if="drift"
    class="mt-2 flex flex-wrap gap-x-3 gap-y-1 text-xs tabular-nums"
  >
    <div>
      <dt class="sr-only">
        PSI
      </dt>
      <dd
        v-if="band"
        :class="['font-medium', TONE[band]]"
      >
        PSI {{ drift.psi?.toFixed(3) }}
      </dd>
      <!-- Uncoloured on purpose: there is no band, because there was no measurement. -->
      <dd
        v-else
        class="text-slate-500"
      >
        PSI not measured
      </dd>
    </div>
    <div v-if="drift.mean_shift != null && drift.mean_shift !== 0">
      <dt class="sr-only">
        Mean shift
      </dt>
      <!-- An absolute difference in the column's own units: `current.mean − reference.mean`,
           not a ratio and not a percentage. -->
      <dd class="text-slate-600">
        {{ drift.mean_shift > 0 ? "+" : "" }}{{ drift.mean_shift.toFixed(3) }} mean
      </dd>
    </div>
    <div v-if="drift.null_rate_shift">
      <dt class="sr-only">
        Null-rate shift
      </dt>
      <!-- Percentage **points**: a null rate moving 0.010 → 0.022 is +1.20pp. Rendering it
           as a percentage would read as a relative change and overstate a small book. -->
      <dd class="text-slate-600">
        {{ drift.null_rate_shift > 0 ? "+" : "" }}{{ (drift.null_rate_shift * 100).toFixed(2) }}pp nulls
      </dd>
    </div>
    <div v-if="drift.new_levels.length">
      <dt class="sr-only">
        New levels
      </dt>
      <dd
        class="text-slate-600"
        :title="drift.new_levels.join(', ')"
      >
        +{{ drift.new_levels.length }} new
      </dd>
    </div>
    <div v-if="drift.vanished_levels.length">
      <dt class="sr-only">
        Vanished levels
      </dt>
      <dd
        class="text-slate-600"
        :title="drift.vanished_levels.join(', ')"
      >
        {{ drift.vanished_levels.length }} vanished
      </dd>
    </div>
  </dl>
</template>
```

- [ ] **Step 4: Run the tests to verify they pass**

```bash
PATH="$HOME/.npm-global/bin:$PATH" pnpm --dir frontend test -- ColumnDrift
```

Expected: 6 passing. If "renders nothing at all" fails on whitespace, there is a text node
between the `v-if` branches — the two roots must be `v-if` / `v-else-if` with nothing between
them.

- [ ] **Step 5: Mount it on each column card**

In `ProfileView.vue`, import it beside the other components:

```ts
import ColumnDrift from "@/components/ColumnDrift.vue";
```

and add it inside the `<article>`, immediately after the closing `</dl>` of the existing stats
list and before the `<HistogramChart>`:

```html
<ColumnDrift :drift="driftFor(column.name)" />
```

- [ ] **Step 6: Re-aim the band-colour regression guard**

The existing test *"does not colour the dtype label as though it were a PSI band"* asserts
`container.innerHTML` contains no `text-amber-700` or `text-red-700`. That guard is now
**wrong as written**: once a comparison is loaded, a band colour is exactly what the view
should show. It was a guard against colouring *without* a comparison, so re-aim it at that —
do not delete it, and do not weaken it to match whatever the code now does.

```ts
it("shows no PSI band until a comparison is loaded", async () => {
  // The original defect: the dtype label borrowed `psiBand`'s colour when there was no
  // comparison at all, so the badge showed the colour of a band without the band. The
  // selector now exists, so the guard is that no band appears *before* one is chosen.
  const { container } = render(ProfileView, { props, ...mounted });
  await screen.findByText(/29,970 rows/);

  expect(container.innerHTML).not.toContain("text-amber-700");
  expect(container.innerHTML).not.toContain("text-red-700");
  expect(screen.queryByText(/^PSI /)).not.toBeInTheDocument();
});

it("bands each column once a reference is chosen", async () => {
  render(ProfileView, { props, ...mounted });
  const select = await screen.findByLabelText("Compare against");
  await userEvent.selectOptions(select, VERSIONS.items[1]?.id ?? "");

  // veh_brand moved 0.31 — above VR-DST-1's 0.25 fail threshold.
  expect(await screen.findByText(/PSI 0\.310/)).toHaveClass("text-red-700");
  // driv_age is continuous: no non-null top_levels, so no PSI and no band.
  expect(screen.getByText(/PSI not measured/)).toBeInTheDocument();
});
```

- [ ] **Step 7: Prove the guard bites**

A check that has never failed is not known to work (`CLAUDE.md` §13.4). Temporarily change
`ColumnDrift.vue`'s `band` computed to `psiBand(props.drift?.psi ?? 0)` — the old
null-is-stable behaviour — and run:

```bash
PATH="$HOME/.npm-global/bin:$PATH" pnpm --dir frontend test -- ColumnDrift
```

Expected: *"does not band a PSI that was never measured"* fails, because an unmeasured column
now renders `PSI 0.000` in the stable tone. **Restore the line and re-run**, and confirm the
restore by reading the file rather than assuming it — a proof that leaves broken code behind
proves only that broken code fails.

- [ ] **Step 8: Full frontend gate and commit**

```bash
PATH="$HOME/.npm-global/bin:$PATH" pnpm --dir frontend lint
PATH="$HOME/.npm-global/bin:$PATH" pnpm --dir frontend type-check
PATH="$HOME/.npm-global/bin:$PATH" pnpm --dir frontend test
PATH="$HOME/.npm-global/bin:$PATH" pnpm --dir frontend build
```

Report the **real** test count the run prints; do not restate an estimate from this plan.

```bash
git add frontend/src/components/ColumnDrift.vue \
        frontend/src/components/__tests__/ColumnDrift.test.ts \
        frontend/src/views/ProfileView.vue \
        frontend/src/views/__tests__/ProfileView.test.ts
git commit -m "feat(frontend): band each column's PSI against its reference version"
```

---

## Task 6: Resolve the two documents that predicted this slice, and ship it

**Files:**
- Modify: `docs/specs/01-data-management.md` §5.3 (the 2026-08-19 note)
- Modify: `docs/roadmap.md` (the §5.3-divergence row ~2265, the Pinia row ~763)
- Modify: `docs/open-questions.md` (OQ-DATA-11's status, if Task 1 Step 6 left it open)

**Interfaces:**
- Consumes: everything above.
- Produces: a spec that describes the code, and a roadmap that does not claim an unbuilt item.

**The rule this task exists to obey:** `CLAUDE.md` §14 — *resolve, never soften*. The §5.3
note is not deleted when the work lands; it gains a dated resolution saying what was built and
what happened to the store it predicted. Deleting it would erase the record that the row was
once a divergence, which is what the note exists to preserve.

- [ ] **Step 1: Resolve `01` §5.3's note**

Replace the first paragraph of the 2026-08-19 note (the one beginning *"The Profile row's four
Contents items are now three built and one not"*) with:

```markdown
> *(2026-08-19)* **The Profile row's four Contents items are now all four built.** Histograms
> landed with FR-DATA-48; per-column cards and the one-way charts with their CI bands were
> built in W6a; the **PSI comparison selector** was built in the slice that closed this note.
> It reads FR-DATA-28's endpoint through `compareProfiles()` — implemented, typed and exported
> with zero callers until then — and bands each column against `VR-DST-1`'s thresholds, so a
> rule's verdict and the screen an actuary is reading cannot disagree about one number.
>
> **Three things the build settled that this note had left open.** The reference lives in the
> **route query** and not in a Pinia store (**OQ-DATA-11**): nothing required the selection to
> outlive a route, and a URL is shareable where a store is not — `frontend/src/stores/` is
> still empty, and the first store waits for state that is genuinely global. A version with no
> stored `profile_id` is **disabled in the picker** rather than offered and then explained,
> because the endpoint answers 404 for it and `DatasetVersion` already carries the answer. And
> `psiBand` now **refuses an absent PSI** at the type level: it answered `"stable"` for `null`,
> which is how an unmeasured continuous column would have rendered as a calm band the moment
> the function gained a caller — the defect this note recorded, fixed at the source rather
> than at the one call site that had it.
```

Leave the note's remaining paragraphs (the OQ-DATA-9 resolution) untouched.

- [ ] **Step 2: Resolve the roadmap's divergence row**

At `docs/roadmap.md` ~line 2265, replace the row's second cell:

```markdown
| **`01` §5.3's PSI comparison selector** | **Built 2026-08-19.** `compareProfiles()` has its caller; the reference-version picker lives in the route query (**OQ-DATA-11**), versions with no stored profile are disabled rather than offered, and each column card carries a `ColumnDrift` block banded against `VR-DST-1`. The Contents claim is now met rather than annotated. |
```

- [ ] **Step 3: Resolve the Pinia row honestly**

At ~line 763, the row predicts this slice brings the first store. It did not. Replace the
second cell:

```markdown
| Pinia stores | **Registered, still unused — and the predicted trigger did not fire.** This row named the PSI comparison selector as the first thing that would need state to outlive a route. When that slice was built (2026-08-19) the premise did not hold: nothing requires the reference version to survive navigation, and the route query gives the selection reload-survival and shareability a store cannot. Recorded as **OQ-DATA-11**. The next candidate is the workspace selector W6b carries, and that one should be checked the same way rather than assumed. |
```

- [ ] **Step 4: Close OQ-DATA-11 if it is still open**

If Task 1 Step 6's answer has not yet been written into `docs/open-questions.md`, do it now:
strike the question, prefix the id with `~~**OQ-DATA-11**~~ ✔`, set Status to `**decided**`,
and record what was decided and why — including anything the maintainer said that this plan
did not anticipate.

- [ ] **Step 5: Run the whole gate, both halves, reading each exit code**

`pytest` needs the database DSN or ~90 tests skip **silently**:

```bash
docker compose -f deploy/docker-compose.yml up -d --wait
export GIP_TEST_DATABASE_URL="postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing"
export GIP_DATABASE_URL="$GIP_TEST_DATABASE_URL"
```

```bash
python3 scripts/audit-docs.py
uv run python scripts/req-coverage.py
uv run python scripts/generate-contracts.py --check
uv run ruff check .
uv run mypy
uv run lint-imports
uv run pytest -q

export PATH="$HOME/.npm-global/bin:$PATH"
rm -rf frontend/node_modules
pnpm --dir frontend install --frozen-lockfile
pnpm --dir frontend generate:api
pnpm --dir frontend lint
pnpm --dir frontend type-check
pnpm --dir frontend test
pnpm --dir frontend build
```

The clean `node_modules` reinstall is what CI does, and a populated one hides a missing
dependency — this slice adds none, which is exactly the claim the reinstall proves.

Expected: Python **1339, zero skipped** and unchanged — this slice touches no Python. Docs
audit 0 with **66** questions. Frontend green, with the real count reported.

- [ ] **Step 6: Check the demo guide still derives**

```bash
uv run pytest backend/tests/test_demo_guide.py
```

FR-PLAT-54's guide is derived rather than written, so there is nothing to update — but the
derivation is what has to still hold.

- [ ] **Step 7: Commit, push, open the PR**

```bash
git add docs/specs/01-data-management.md docs/roadmap.md docs/open-questions.md
git commit -m "docs(data): §5.3's PSI selector built, and the store that did not arrive"

git push -u origin feat/psi-comparison-selector
gh pr create --title "feat(frontend): the PSI comparison selector (01 §5.3, FR-DATA-28)"
```

The PR body states: what was built; that `compareProfiles()` went from zero callers to one;
OQ-DATA-11 and its answer; that `psiBand` was narrowed and why; the measured test counts
before and after; and **what was not built** — nothing in `backend/`, `pricing-core` or
`model-schema` changed, and `frontend/src/stores/` is still empty.

`gh pr checks` answers *"Resource not accessible by personal access token"* here — a scope
limit, not a red build. Read CI with `gh pr view <n> --json mergeStateStatus`: `CLEAN` means
checks passed, `UNSTABLE` means pending or failing.

---

## Self-review

**Spec coverage.** `01` §5.3's Profile row names four Contents items; three existed and the
fourth — "PSI comparison selector" — is Tasks 3–5. FR-DATA-28's endpoint is consumed (Task 4)
and all four quantities it reports render (Task 5: PSI, mean shift, null-rate shift,
new/vanished levels), plus `row_count_ratio`, which the contract carries and §5.3 does not
name. `VR-DST-1`'s thresholds are the bands (Task 2). **No requirement is added**: FR-DATA-28
already states the capability and a view is not a second requirement — which also means this
slice adds no `req-coverage` marker, and its evidence is the §5.3 Contents claim becoming
true. Nothing here touches a later phase.

**Placeholders.** None: every step carries the code or the exact command. The one deliberate
forward reference — `COMPARISON` declared as `unknown = null` in Task 3 Step 1 and replaced by
a typed fixture in Task 4 Step 1 — is named in both places.

**Type consistency.** `driftFor()` returns `ColumnComparison | null | undefined` in Task 4 and
`ColumnDrift`'s prop is declared with exactly that union in Task 5. `psiBand` is narrowed to
`(psi: number)` in Task 2 and its one call site guards `psi != null`. `referenceId` is a
`string | null` version **id** throughout, while the route query carries a version **number** —
the conversion lives in Task 3 Step 8 and in `referenceLabel`, and nowhere else.

**The three risks worth naming before starting:**

1. **The `fetch` stub rewrite in Task 3 Step 2 touches all eleven existing tests.** Run the file
   after that step alone, before adding behaviour, so a stub regression is not diagnosed as a
   feature bug. `/versions` and `/profile` both contain the substring `version` — branch order
   is load-bearing.
2. **`vi.mock("vue-router")` is module-wide.** `RouterLink` is already stubbed via
   `global.stubs`, and the mock's `importOriginal` spread is what keeps the rest of the module
   working. Do not narrow it to a bare object.
3. **Task 5 Step 6 rewrites a passing test.** That is intended and it is the honest move, but
   it is the step most easily done wrong — re-aiming a guard at a narrower claim is correct
   here *only* because the original claim ("no band, ever") stopped being what the view should
   do. Say so in the commit message.
