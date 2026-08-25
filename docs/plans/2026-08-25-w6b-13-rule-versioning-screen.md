# W6b-13 — Rule Set Rule-Versioning Screen Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `FR-DATA-54`'s reviewed path reachable from the rule set editor — author the
next version of an existing rule with its current thresholds pre-filled — and replace the
hand-written create shape that has been silently dropping `catalogue_id` on the way out of the
browser.

**Architecture:** No new view and no new route. `frontend/src/api/rules.ts` stops hand-writing
the request body and takes the generated `RuleCreate`; `RuleBuilder.vue` gains an optional
"version this rule" seed and pre-fills its form from it; `RuleSetView.vue` grows one action per
rule row that supplies the seed. The `POST → dry-run → submit` chain the builder already
implements is reused unchanged — this slice makes it *reachable* from an existing rule, it does
not re-implement it.

**Tech Stack:** Vue 3 Composition API with `<script setup lang="ts">`, Vitest +
`@testing-library/vue`, types generated from OpenAPI into `frontend/src/api/generated`.

**Spec:** [`../specs/01-data-management.md`](../specs/01-data-management.md) — `FR-DATA-54`
(`:118`), `FR-DATA-53` (`:168`), `FR-DATA-21`, `FR-DATA-22`, and §5.3's *Rule set editor* row
(`:986`), which **this plan amends**; see Finding 1.

**Slice source:** [`2026-08-24-w6b-slice-map-revised.md`](2026-08-24-w6b-slice-map-revised.md)
§3, line 162 — *"Rule set rule-versioning screen, and the `profiles.ts` PSI bands"*, dep
`W6b-13b`. **Both halves are in scope**; the PSI half is Task 5, under a ruling that arrived
mid-draft and reversed this plan's own recommendation — see Finding 5.

**Highest ids in use, verified at `dcb0823` by scanning
[`../specs/01-data-management.md`](../specs/01-data-management.md):** FR-DATA-56, NFR-DATA-10,
OQ-DATA-15. Next free: `FR-DATA-57`, `NFR-DATA-11`, `OQ-DATA-16`.
**This plan mints none of them** — it cites `FR-DATA-54`, which already states the rule, and
amends a §5.3 Contents cell, which is not a requirement. The line is published because the
revised slice map's equivalent (*"Next free: `FR-DATA-55`"*, verified 2026-08-24 at `e2ae7c6`)
is now two ids stale, and a stale allocation aid is what mints a colliding id.

## Global Constraints

- **Never hand-write an API type in the frontend** ([`../../CLAUDE.md`](../../CLAUDE.md) §2 and
  §3). Shapes come from `frontend/src/api/generated`, which is VCS-ignored and therefore
  **cannot be cited as evidence** — cite `docs/contracts/openapi/generated.json`, which is
  committed, instead.
- **Vue 3 Composition API with `<script setup lang="ts">` only.** No Options API, no JSX.
- A threshold change **authors a new rule version** and moves only through `FR-DATA-21`'s
  reviewed path: draft → dry run against a chosen Dataset Version → submit → approval by
  somebody who is not the author. A Rule Set entry keeps exactly `enabled` and
  `severity_override` and **gains no third override** (`FR-DATA-54`).
- Both halves of the gate must pass locally before pushing ([`../../CLAUDE.md`](../../CLAUDE.md)
  §11). A Python-only run is not a gate run for a frontend slice.

---

## Findings the plan is built on

Each was verified against shipped source at `dcb0823`. They are recorded here rather than only
in the PR body because two of them change what the executor must build.

### Finding 1 — `01` §5.3 still specifies the operation `FR-DATA-54` forbids

`01-data-management.md:986` reads:

> `| Rule set editor | /data/:slug/rules | Rule list by layer, enable/disable, threshold editing, custom-rule builder with dry-run |`

`FR-DATA-54` (`:118`, appended 2026-08-23) says a Rule Set entry *"keeps exactly the two
overrides §4.3 declares, `enabled` and `severity_override`, and gains no third"*. §4.4 was
corrected the same day — `:420` now reads *"Every threshold shown here is a default carried by
the rule, and changing one authors a new rule version (FR-DATA-54)"*, and `:422` records the
withdrawal. **§5.3's Contents cell was not swept with them.**

This is a [`../../CLAUDE.md`](../../CLAUDE.md) §0 spec-versus-spec disagreement, and it is not
resolvable by silently building either reading. The revised slice map caught the *slice title*
(§5 proposal **P5**: *"`W6b-13`'s title is wrong and should be restated as rule versioning,
since `FR-DATA-54` forbids the set-level editing the title names"*) and did not reach the spec
cell the title was drawn from. **Task 4 amends the cell** — appending a dated note, never
rewriting the clause, per the same rule that governs an owner clause.

**The capability is not withdrawn, only relocated.** `roadmap.md:1701`'s gap column states it
in behavioural terms that survive the correction intact: *"thresholds render read-only;
changing one means retyping the whole rule into the builder"*. That is still true at `dcb0823`
and is what Tasks 2 and 3 close.

### Finding 2 — `createRule`'s body is hand-written, and has been dropping `catalogue_id`

`frontend/src/api/rules.ts:59-69` declares its request body as an inline object type:

```ts
export function createRule(body: {
  slug: string;
  layer: ValidationLayer;
  check: string;
  severity: Severity;
  target: Record<string, unknown>;
  params: Record<string, unknown>;
  rationale?: string;
}): Promise<ValidationRule> {
```

The committed contract disagrees. `docs/contracts/openapi/generated.json`'s `RuleCreate` has
properties `catalogue_id`, `check`, `layer`, `message`, `params`, `rationale`, `severity`,
`slug`, `target`, required `slug`, `layer`, `check`, `severity`. **`catalogue_id` and `message`
are absent from the hand-written shape.**

`catalogue_id` is the field `W6b-13b` added (`FR-DATA-53`'s tail: *"`RuleCreate` now carries
it, and `create_rule` refuses a `catalogue_id` naming no catalogue entry"*). It is what records
that a workspace's rule descends from a built-in. **A hand-written body is the mechanism by
which that backend change failed to reach the browser** — a generated type would have gained
the field the moment the contract regenerated. This is the standing architecture rule in
[`../../CLAUDE.md`](../../CLAUDE.md) §2 failing exactly as it predicts: *"A shape defined twice
will diverge."*

**Consequence for this slice, and why Task 1 comes first:** versioning a built-in rule is the
central case, and it is precisely the case that must carry `catalogue_id` through. Building
Tasks 2 and 3 on the current shape would ship a versioning screen that silently severs the
lineage `FR-DATA-53` relies on.

### Finding 3 — `RuleSetView.vue:348` quotes the struck §4.4 sentence verbatim

```
<!-- Thresholds are Rule Set configuration, not code (`01` §4.4). Shown as
     stored so an actuary reads the number the engine will use. -->
```

`01:422` records that sentence as withdrawn: *"This line read 'Thresholds are Rule Set
configuration, not code. Every threshold shown is a default.' The first sentence was never
implemented."*

**It is the sole survivor in code.** Re-run at `dcb0823`, the sweep returns exactly three hits:
this sentence at `RuleSetView.vue:348`, `01:422` (the correction note, which quotes the text in
order to withdraw it), and `2026-08-24-w6b-13b-catalogue-chain.md:430` (that plan echoing its
own command). Nothing else.

> **A peer reported a fourth, and it is not one.** `w6b-decision-maker` stated on 2026-08-25
> that *"profiles.ts:42 quotes the struck sentence verbatim"*. It does not — `profiles.ts` is
> absent from the grep above. What `:42` quotes is a **different** withdrawn text: VR-DST-1's
> **two-band form** (*"warn above 0.10, fail above 0.25"*), struck by the 2026-08-15 amendment,
> not §4.4's *"Thresholds are Rule Set configuration"* sentence struck on 2026-08-23. The
> conclusion drawn from it was right and is Task 5; the mechanism was not. Recorded because
> conflating them is actively harmful: the next reader greps the struck sentence, finds
> `profiles.ts` clean, and concludes the finding was already fixed.

The sweep that should have caught the real one was already run.
[`2026-08-24-w6b-13b-catalogue-chain.md`](2026-08-24-w6b-13b-catalogue-chain.md) `:430` runs
`git grep -n "Thresholds are Rule Set configuration" -- packages/ backend/ frontend/src docs/`
and `:327` acts on what it found in `packages/` — `BuiltinRule`'s docstring, which is clean at
`dcb0823`. The `frontend/src` member of the same result set was not fixed. Naming the member
that *did* move matters: the sweep was not skipped, it was half-applied, which is the failure
mode a re-run of the same grep would not have distinguished from success.

Task 3 replaces the comment as part of editing the cell it annotates.

### Finding 4 — `tolerance` and `scope` cannot be written through the API

`backend/src/app/platform/validation_rules.py:234-238` builds the row body with
`"scope": {}` and `"tolerance": {}` as **literals**, not parameters; `:147` does the same on
the seed path. Neither appears in `RuleCreate`. So no caller can set either, and every stored
rule has both empty.

This bounds the round-trip Task 2 must achieve: **every field a caller could have set does
round-trip** (`slug`, `layer`, `check`, `severity`, `target`, `params`, `message`, `rationale`,
`catalogue_id`), and the two that do not are two nobody can author in the first place.

`RuleSetView.vue:44`'s `thresholds()` merges `params` **and** `tolerance`, which is correct
defensive reading of `ValidationRule` (the read model does carry `tolerance`) and is currently
always fed an empty second half. **`frontend/src/views/__tests__/RuleSetView.test.ts:19` seeds
`tolerance: { max_fail_rate: 0.01 }`** — a shape the API cannot produce — and `:116` asserts on
it (*"shows the thresholds the engine will use, from params and tolerance alike"*). Left alone: it is the
only thing exercising the merge, and deleting it would silently drop that coverage. Recorded so
the next reader does not infer from the fixture that the write path exists.

---

### Finding 5 — the PSI half: my recommendation was overruled, and the ruling is right

`frontend/src/api/profiles.ts:52-55`'s `psiBand` hard-codes `0.25` (`:53`) and `0.1` (`:54`),
and its docstring at `:42` cites *"`01` §4.4's VR-DST-1 … warn above 0.10, fail above 0.25"* —
the **two-band form struck by the 2026-08-15 amendment** (see Finding 3's box: this is a
different struck text from `RuleSetView.vue:348`'s).

[`2026-08-24-w6b-13b-catalogue-chain.md`](2026-08-24-w6b-13b-catalogue-chain.md) records that
**VR-DST-1's catalogue entry carries `warn_above` only** — `FR-DATA-54`'s tail says the same at
`01:118` — and lists `profiles.ts:42,52-54` among three things belonging to *"a separate item
with its own owner"*.

I read that as blocking and **recommended deferring the whole PSI half**, on the reasoning that
sourcing `warn_above` while leaving `0.25` a literal would mix a sourced number with an
invented one. **`w6b-decision-maker` overruled it on 2026-08-25**, and the ruling is better than
the recommendation:

> *"(c) — not lossy. `01:996` says banding exists so the screen cannot disagree with the rule;
> `"broken"` asserts a fail severity no rule in the set can emit. Not blocked: `list_rules`
> (`FR-DATA-53`) returns `params` — fetch `warn_above`, zero literals. Beats (a), which sources
> one band and invents the severe one. (b) builds a governance rule to fit a UI, inverting the
> 2026-08-15 amendment. Defer the fail band, not the PSI half."*

The argument I missed is that **`"broken"` is not merely unsourced, it is a false statement**.
`01:996` is the 2026-08-19 note on the Profile row: the selector *"bands each column against
`VR-DST-1`'s thresholds, so a rule's verdict and the screen an actuary is reading cannot
disagree about one number"*. VR-DST-1 emits `warn` and nothing else. A screen rendering
`"broken"` claims a `fail` verdict **no rule in the set can produce** — which is precisely the
disagreement the banding exists to prevent. Deferring the half would have left that shipped.

So the third band goes, and both remaining numbers come from the catalogue. **This is Task 5.**

**Deferred, narrowly:** the `fail` band's restoration, which needs the second catalogue rule
(a §4.4 spec change plus backend seed — not browser work, and not this slice's). When it lands,
`psiBand` gains a third band from that rule's `fail_above`. Owner: whoever takes the second
catalogue rule.

**What the ruling assumes and the repository does not yet have.** `list_rules` is an *endpoint*
(`01:848`, `GET /api/v1/validation-rules`), **not a frontend client function**. At `dcb0823`
`frontend/src/api/rules.ts` exports `getRuleSet`, `replaceRuleSet`, `membersOf`, `createRule`,
`dryRun`, `submitRule`, `approveRule`, `byLayer` — and **no list**. Task 5 must add one.
Flagged because "just fetch it, zero literals" reads as though the call already exists.

## Out of scope

**The three lineage defects.** `01:846` still reads *"Three code defects go with it, owner
`W6b-13`"*. The revised slice map §3 line 161 moves them to `W6b-12`, and its proposal **P3**
amends `01:846` in the same commit as the reassignment. Both are marked *pending*. This slice
does not touch them and does not amend that row — doing so would execute someone else's
unaccepted proposal.

**Set-level threshold override.** Forbidden by `FR-DATA-54`. Not deferred — decided against.

---

## File Structure

| File | Change | Responsible for |
|---|---|---|
| `frontend/src/api/rules.ts` | Modify `:59-69` | `createRule` takes the generated `RuleCreate` |
| `frontend/src/api/__tests__/rules.test-d.ts` | Create | Type-level proof the body admits `catalogue_id` |
| `frontend/src/components/RuleBuilder.vue` | Modify `:9-31`, `:60-72`, template | Optional `seed` prop, pre-fill, `catalogue_id` pass-through |
| `frontend/src/components/__tests__/RuleBuilder.test.ts` | Modify | Pre-fill and lineage round-trip |
| `frontend/src/views/RuleSetView.vue` | Modify `:348-352`, `:190`, `:390` | Per-row "New version" action, corrected comment |
| `frontend/src/views/__tests__/RuleSetView.test.ts` | Modify | POST body capture, the action's wiring |
| `frontend/src/api/rules.ts` | Modify (Task 5) | `listRules`, which does not exist yet |
| `frontend/src/api/profiles.ts` | Modify `:41-55` | `psiBand` takes sourced thresholds; two bands |
| `frontend/src/api/__tests__/profiles.test.ts` | Modify | The band boundaries, from a rule not a literal |
| `docs/specs/01-data-management.md` | Modify `:986` | §5.3 Contents cell, dated note |
| `docs/roadmap.md` | Modify `:1701`, `:1766`, `:3287` | Record the gap closed, under `FR-DATA-54`'s semantics |

**`01:996` is *not* in this table.** `w6b-decision-maker` said *"I'll append the dated note to
`01:996`"* — that is their edit, in their commit. It is a different row from `:986` (the
2026-08-19 Profile note versus the Rule set editor Contents cell), so the two do not collide,
but do not write it here and do not assume it has landed.

---

### Task 1: `createRule` takes the generated request type

**Files:**
- Modify: `frontend/src/api/rules.ts:59-69`
- Test: `frontend/src/api/__tests__/rules.test-d.ts` (create)

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: `export type RuleCreate = components["schemas"]["RuleCreate"]` and
  `createRule(body: RuleCreate): Promise<ValidationRule>`. Tasks 2 and 3 rely on both names.

- [ ] **Step 1: Write the failing type test**

Create `frontend/src/api/__tests__/rules.test-d.ts`. Mirror
`frontend/src/api/__tests__/profiles.test-d.ts` for imports and `describe`/`it` style rather
than reinventing them — it is the module's only existing `test-d` file.

```ts
import { describe, expectTypeOf, it } from "vitest";

import { createRule, type RuleCreate } from "@/api/rules";

/**
 * `RuleCreate` is generated from the OpenAPI document, so this is not a restatement of the
 * backend's shape — it is the assertion that the frontend reads the generated one at all.
 * The hand-written body it replaces omitted `catalogue_id`, which is how `W6b-13b`'s
 * backend change never reached the browser (`FR-DATA-53`).
 */
describe("createRule's request body", () => {
  it("is the generated RuleCreate, so catalogue_id survives", () => {
    expectTypeOf(createRule).parameter(0).toEqualTypeOf<RuleCreate>();
    expectTypeOf<RuleCreate>().toHaveProperty("catalogue_id");
    expectTypeOf<RuleCreate>().toHaveProperty("message");
  });
});
```

- [ ] **Step 2: Run it and confirm it fails for the right reason**

Run: `pnpm --dir frontend type-check`

**Expected: FAIL, and the mode matters.** The predicted cause is that `RuleCreate` is not
exported from `@/api/rules` — a *module resolution* error naming `RuleCreate`, not a shape
mismatch. **If it fails for any other reason, that is a plan defect: record what you observed
rather than proceeding.** In particular, a failure complaining that
`frontend/src/api/generated` does not exist means the generated client was never built — run
`pnpm --dir frontend install --frozen-lockfile && pnpm --dir frontend generate:api` first and
re-run this step. That is an environment gap, not a result.

- [ ] **Step 3: Export the generated type and use it**

In `frontend/src/api/rules.ts`, add to the existing block of type re-exports at `:4-9`:

```ts
export type RuleCreate = components["schemas"]["RuleCreate"];
```

Then replace the inline body type at `:59-69`:

```ts
/**
 * Step 1 of `FR-DATA-21`'s chain. The body is the **generated** `RuleCreate` and is never
 * restated here: it carries `catalogue_id`, which is what records that a workspace rule
 * descends from a built-in (`FR-DATA-53`), and a hand-written copy of this shape is exactly
 * how that field failed to reach the browser once already.
 *
 * Re-using an existing rule's `slug` is not an error — the platform allocates the next
 * version, which is `FR-DATA-54`'s path for a threshold change.
 */
export function createRule(body: RuleCreate): Promise<ValidationRule> {
  return request<ValidationRule>("/validation-rules", { method: "POST", body });
}
```

Leave the `request` call untouched. Do not widen `RuleCreate` with a local intersection; if a
caller needs a field the contract lacks, that is a backend change and it stops this task.

- [ ] **Step 4: Run the type check and the suite**

Run: `pnpm --dir frontend type-check && pnpm --dir frontend test`

Expected: PASS. `RuleBuilder.vue` is the only existing caller (`:63`); it passes a subset of
`RuleCreate`'s optional fields and should still type-check unchanged. **If it does not, do not
cast at the call site** — read which field the generated type requires and record it; a
required field the builder never sent is a finding, not a lint error.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/api/rules.ts frontend/src/api/__tests__/rules.test-d.ts
git commit -m "refactor(w6b-13): createRule takes the generated RuleCreate"
```

---

### Task 2: `RuleBuilder` pre-fills from an existing rule

**Files:**
- Modify: `frontend/src/components/RuleBuilder.vue`
- Test: `frontend/src/components/__tests__/RuleBuilder.test.ts`

**Interfaces:**
- Consumes: `createRule(body: RuleCreate)` and the `RuleCreate` type from Task 1.
- Produces: `RuleBuilder` accepts an optional prop `seed?: ValidationRule | null`. When
  present the form opens populated from it and the authored body carries
  `catalogue_id: seed.catalogue_id`. Task 3 supplies the prop.

- [ ] **Step 1: Write the failing test**

Add to `frontend/src/components/__tests__/RuleBuilder.test.ts`. **Mirror that file's existing
fetch stub and its `rule(...)` factory if it has one rather than copying the fixture below
verbatim** — the shape here is taken from `RuleSetView.test.ts:9-25`, which is a different
file, and reinventing a module's fixtures is how a second mismatch enters.

```ts
it("opens populated when handed a rule to version", async () => {
  const seed = {
    id: "11111111-1111-4111-8111-111111111111",
    slug: "driv-age-range",
    version: 1,
    layer: "actuarial_sanity",
    check: "range",
    severity: "warn",
    target: { table: "policy_exposure", column: "driv_age" },
    params: { key_columns: ["policy_id"], min_inclusive: 18 },
    scope: {},
    tolerance: {},
    message: "",
    rationale: "Under 18 cannot hold a policy.",
    status: "approved",
    catalogue_id: "VR-ACT-3",
  };

  render(RuleBuilder, { props: { slug: "fremtpl2", seed } });

  // The slug is fixed, not merely defaulted: reusing it is what makes this the *next
  // version* of that rule rather than a new one (`FR-DATA-54`).
  expect(await screen.findByDisplayValue("driv-age-range")).toBeInTheDocument();
  // The thresholds an actuary came here to change, already in the box.
  expect(screen.getByDisplayValue(/"min_inclusive": 18/)).toBeInTheDocument();
});
```

- [ ] **Step 2: Run it and confirm the cause**

Run: `pnpm --dir frontend test -- RuleBuilder`

**Expected: FAIL because no element carries the display value `driv-age-range`** — the form
still initialises `slug: ""` (`RuleBuilder.vue:23`). A failure naming an unknown prop `seed`,
or a Vue warning about it, is the *same* prediction and also acceptable. **A failure that
renders nothing at all is not**: it means the stub is missing `listVersions`, which the
component calls in `onMounted` (`:38`) — fix the stub, not the assertion.

- [ ] **Step 3: Add the prop and the pre-fill**

In `RuleBuilder.vue`, extend the props at `:10` and seed the form. `ValidationRule` must be
imported from `@/api/rules`, which already exports it (`:5`).

```ts
const props = defineProps<{ slug: string; seed?: ValidationRule | null }>();

/**
 * `FR-DATA-54`: changing a threshold authors a new version, so the honest starting point
 * for that edit is the current rule rather than an empty form. Reusing the slug is what
 * makes the platform allocate the next version (`FR-DATA-21` step 4).
 *
 * `scope` and `tolerance` are not seeded because they cannot be authored at all —
 * `create_rule` writes both as literal `{}` — so carrying them would imply a round-trip
 * that does not exist.
 */
const form = ref({
  slug: props.seed?.slug ?? "",
  layer: (props.seed?.layer ?? "actuarial_sanity") as ValidationLayer,
  check: props.seed?.check ?? "range",
  severity: (props.seed?.severity ?? "warn") as "warn" | "fail",
  table: (props.seed?.target as { table?: string } | undefined)?.table ?? "policy_exposure",
  column: (props.seed?.target as { column?: string } | undefined)?.column ?? "",
  params: JSON.stringify(props.seed?.params ?? {}, null, 2),
  rationale: props.seed?.rationale ?? "",
  versionId: "",
});
```

- [ ] **Step 4: Carry the lineage into the authored body**

At `RuleBuilder.vue:63-70`, the `createRule({...})` call gains one field:

```ts
    const rule = await createRule({
      slug: form.value.slug,
      layer: form.value.layer,
      check: form.value.check,
      severity: form.value.severity,
      target: { table: form.value.table, column: form.value.column },
      params,
      rationale: form.value.rationale,
      // `FR-DATA-53`: what survives a workspace versioning a seeded rule. `null` for a
      // rule authored from scratch — the backend refuses a `catalogue_id` naming no
      // catalogue entry, so inventing one here is rejected on the way in.
      catalogue_id: props.seed?.catalogue_id ?? null,
    });
```

**Read the surrounding lines before editing**; `:63` is where the call begins at `dcb0823`, and
Task 1 changed nothing above it. Preserve the existing `params` local from `:51-53`.

- [ ] **Step 5: Run the test**

Run: `pnpm --dir frontend test -- RuleBuilder`
Expected: PASS.

- [ ] **Step 6: Add the lineage round-trip test**

```ts
it("carries catalogue_id, so a versioned built-in keeps its lineage", async () => {
  // The defect this guards is invisible on screen: the form renders identically whether or
  // not the field reaches the wire. Assert the posted body, never the rendering.
  // ...author the rule through the form as the neighbouring authoring test does...
  expect(postedBodies[0]).toMatchObject({ catalogue_id: "VR-ACT-3" });
});
```

Fill the elided middle by copying the driving steps from the file's existing authoring test —
do not reconstruct them. If that file captures POST **urls** only, extend its stub to push
`JSON.parse(String(init.body))` the way `RuleSetView.test.ts:50-51` already does for `PUT`.

- [ ] **Step 7: Run and commit**

```bash
pnpm --dir frontend test -- RuleBuilder
git add frontend/src/components/RuleBuilder.vue frontend/src/components/__tests__/RuleBuilder.test.ts
git commit -m "feat(w6b-13): RuleBuilder pre-fills from the rule being versioned"
```

---

### Task 3: The rule set editor offers the next version

**Files:**
- Modify: `frontend/src/views/RuleSetView.vue`
- Test: `frontend/src/views/__tests__/RuleSetView.test.ts`

**Interfaces:**
- Consumes: `RuleBuilder`'s `seed` prop from Task 2.
- Produces: nothing later tasks depend on.

- [ ] **Step 1: Write the failing test**

```ts
it("offers the next version of a rule rather than a threshold edit (FR-DATA-54)", async () => {
  render(RuleSetView, { props, ...mounted });
  const row = (await screen.findByText("driv-age-range")).closest("tr")!;

  await userEvent.click(within(row).getByRole("button", { name: /new version/i }));

  // The builder opens carrying this rule, so the thresholds are already in the box. The
  // set is untouched: a threshold is not a set-level override, and `FR-DATA-54` gives an
  // entry exactly `enabled` and `severity_override`.
  expect(await screen.findByDisplayValue("driv-age-range")).toBeInTheDocument();
  expect(putBodies).toHaveLength(0);
});
```

- [ ] **Step 2: Run it and confirm the cause**

Run: `pnpm --dir frontend test -- RuleSetView`

**Expected: FAIL from `getByRole` finding no button named "New version" in that row.** The
existing row already carries two buttons — the override toggle, whose label is the *expression*
`{{ entry.severity_override ? "Clear override" : "Raise to fail" }}` at `:345`, and the
submit/approve control below `:358` — so a failure reporting *multiple* matches means the name
is ambiguous against one of those, and the fix is a more specific accessible name, not a looser
query. `posted` is declared at `:41` and `putBodies` at `:42`.

- [ ] **Step 3: Add the action and correct the struck comment**

Replace the comment at `RuleSetView.vue:348-349` and the cell at `:350-352`. The old comment
quotes a sentence `01:422` withdrew — see Finding 3.

```html
              <!-- A threshold belongs to the rule, not to the set (`01` §4.4, corrected
                   2026-08-23). Read-only here by design: changing one authors a new rule
                   version through `FR-DATA-21`'s reviewed path, which is what the button
                   below starts. A Rule Set entry gets `enabled` and `severity_override`
                   and no third override (`FR-DATA-54`). -->
              <td class="py-2 font-mono text-xs text-slate-600">
                {{ thresholds(entry) || "—" }}
                <button
                  type="button"
                  class="ml-2 rounded border border-slate-300 px-2 py-0.5 text-xs hover:bg-slate-50"
                  @click="versioning = entry.rule"
                >
                  New version
                </button>
              </td>
```

Add the state beside the view's other `ref`s in `<script setup>`:

```ts
/** The rule whose next version is being authored, or `null`. */
const versioning = ref<ValidationRule | null>(null);
```

**Check `ValidationRule` is in the `@/api/rules` import list before adding it** — `rules.ts:5`
exports it, but this view's import currently names `RuleSetEntry` (used at `:44`) and may not
name `ValidationRule`.

- [ ] **Step 4: Hand the seed to both builders**

**There are two `<RuleBuilder>` usages, at `:190` and `:390`** — both bound `@authored="load"`.
Read both before editing: they are the empty-state and the populated-table renderings of the
same screen, and wiring only one gives a "New version" button that silently does nothing
whenever the other branch is showing. Pass the seed plus a key to **each**, so switching from
one rule to another re-initialises the form rather than keeping the first rule's values —
`form` is built once in `setup`, so without the key the second click renders stale.

```html
        <RuleBuilder
          :key="versioning?.id ?? 'new'"
          :slug="slug"
          :seed="versioning"
          @authored="load"
        />
```

`load` is the handler already bound at both sites; do not rename it, and preserve whatever
other props each site passes. Leave the conditions the two sites are rendered under alone.

- [ ] **Step 5: Run the test**

Run: `pnpm --dir frontend test -- RuleSetView`
Expected: PASS.

- [ ] **Step 6: Prove the negative on deliberately broken input**

Temporarily change the seed binding to `:seed="null"` and re-run. **Expected: the test from
Step 1 FAILS** at the `findByDisplayValue("driv-age-range")` assertion, because an unseeded
builder opens with an empty slug. Restore the binding and re-run to green.

This is the step that proves the assertion discriminates. A test that passes with the seed
wired and with it cut is testing that a button exists, which was never in doubt.

- [ ] **Step 7: Commit**

```bash
git add frontend/src/views/RuleSetView.vue frontend/src/views/__tests__/RuleSetView.test.ts
git commit -m "feat(w6b-13): version a rule from the rule set editor"
```

---

### Task 4: Reconcile the specification with what was built

**Files:**
- Modify: `docs/specs/01-data-management.md:986`
- Modify: `docs/roadmap.md:1701`, `:1766`, `:3287`

This task exists because of Finding 1: §5.3 specifies an operation `FR-DATA-54` forbids, and
[`../../CLAUDE.md`](../../CLAUDE.md) §0 requires that disagreement to be resolved openly rather
than by building either side.

- [ ] **Step 1: Amend the §5.3 Contents cell**

Replace the *Rule set editor* row's Contents cell at `:986`. **Append the note; do not delete
the old words** — a Contents cell records what was specified at the time, and overwriting it
destroys the record of which side was believed.

> `| Rule set editor | /data/:slug/rules | Rule list by layer, enable/disable, severity override, rule versioning with pre-filled thresholds, custom-rule builder with dry-run. *(Corrected 2026-08-25, W6b-13: this cell read "threshold editing", which FR-DATA-54 forbade on 2026-08-23 — a Rule Set entry gains no third override. §4.4 was swept the same day and this cell was not, so the spec specified an operation the spec elsewhere prohibited. The capability is relocated, not withdrawn: a threshold is changed by authoring the rule's next version through FR-DATA-21's reviewed path, started from this screen.)* |`

**Check the cell count before and after** — `docs/plans/README.md` convention 3, and this row
has three columns. An unescaped `|` inside the note silently shifts every column after it.

- [ ] **Step 2: Record the gap closed in the roadmap**

Three rows carry "threshold editing" as outstanding W6b work: `:1701` (gap column), `:1766`
(the six §5.3 Contents items) and `:3287` (the remaining four). Append a dated note to each
recording that it is delivered under `FR-DATA-54`'s semantics — versioning, not set-level
editing — and cite this plan. **Read each row before editing it**; `:1766` and `:3287` each
track several items and only one of them is this.

- [ ] **Step 3: Run the docs gate, and prove it reads this file**

```bash
python3 scripts/audit-docs.py
uv run python scripts/req-coverage.py
```

Expected: PASS.

**The mutation probe is already done, and it fired by accident.** An earlier draft of this step
spelled the probe id out literally, and `audit-docs.py` promptly failed on the plan's own
prose:

```
FAILED (1):
  - FR-DATA-<probe> referenced but never defined (in ['plans/2026-08-25-w6b-13-rule-versioning-screen.md'])
```

It named this file, so the pass above is not a pass by omission. **Do not write an undefined id
literally into this document** — check 2 reads plans, and the only exemption is the rest of a
`Next free:` line. To re-probe, append a `FR-DATA-` id well above the ceiling on its own line,
re-run, and delete it before committing; state the id in your shell, never in the file.

- [ ] **Step 4: Run both halves of the gate**

```bash
uv run ruff check . && uv run mypy && uv run lint-imports && uv run pytest -q
pnpm --dir frontend lint && pnpm --dir frontend type-check
pnpm --dir frontend test && pnpm --dir frontend build
```

All must pass. A Python-only run is not a gate run for a slice that is entirely frontend
([`../../CLAUDE.md`](../../CLAUDE.md) §11).

- [ ] **Step 5: Commit**

```bash
git add docs/specs/01-data-management.md docs/roadmap.md
git commit -m "docs(w6b-13): §5.3 specified the threshold edit FR-DATA-54 forbids"
```

---

### Task 5: `psiBand` reads VR-DST-1 instead of asserting it

**Files:**
- Modify: `frontend/src/api/rules.ts` (add `listRules`)
- Modify: `frontend/src/api/profiles.ts:41-55`
- Test: `frontend/src/api/__tests__/profiles.test.ts`, `frontend/src/api/__tests__/rules.test.ts`

**Interfaces:**
- Consumes: `RuleCreate`/`ValidationRule` from Task 1 (types only).
- Produces: `listRules(params?)` and `psiBand(psi: number, warnAbove: number)`.

**This task exists because of Finding 5, and it is the least-verified task in this plan** —
the ruling that put it in scope arrived after the other four were written and swept. Treat
every locator below as a candidate, not a reading.

- [ ] **Step 1: Add `listRules`, because it does not exist**

The endpoint is `01:848`, `GET /api/v1/validation-rules`, *"cursor-paginated and filterable by
`builtin`"*. **Do not invent its response envelope** — read the committed
`docs/contracts/openapi/generated.json` for the operation's `200` schema and re-use the
generated type, and mirror whichever existing client function in `frontend/src/api/` already
handles a cursor-paginated list (`paging.ts` has a test, so a convention exists). Hand-writing
the page shape here would reproduce Finding 2 in a new function.

- [ ] **Step 2: Write the failing band test**

```ts
it("bands against the rule's own warn_above, not a literal", () => {
  // 0.15 is above VR-DST-1's 0.10 default but below the 0.25 this function used to invent.
  // Under two bands it is "shifted"; the third band it used to return asserted a `fail`
  // severity VR-DST-1 cannot emit (`01:996`).
  expect(psiBand(0.15, 0.1)).toBe("shifted");
  expect(psiBand(0.05, 0.1)).toBe("stable");
  // A workspace that versioned VR-DST-1 to a tighter threshold gets its own answer.
  expect(psiBand(0.05, 0.02)).toBe("shifted");
});
```

Run: `pnpm --dir frontend test -- profiles`

**Expected: FAIL because `psiBand` takes one argument** — a TypeScript arity error, or the
second argument silently ignored and `psiBand(0.05, 0.02)` returning `"stable"`. **A failure
naming `"broken"` means you are running the old suite**: `profiles.test.ts` already asserts the
three-band behaviour, and those assertions are what this task deletes. Delete them in this
step, not later — leaving them makes Step 4 ambiguous.

- [ ] **Step 3: Collapse to two sourced bands**

```ts
/**
 * PSI bands, read from VR-DST-1 rather than restated here.
 *
 * **Two bands, not three.** The removed `"broken"` band asserted a `fail` severity VR-DST-1
 * cannot emit: the rule carries `warn_above` only, and the `fail_above` band is a second
 * catalogue rule that does not exist yet (`FR-DATA-54`, built note 2026-08-24). Banding
 * exists so the screen and the rule cannot disagree about one number (`01` §5.3, note of
 * 2026-08-19) — inventing the severe band was that exact disagreement, in the direction that
 * alarms an actuary about a verdict no report will ever carry.
 *
 * When the second rule lands, this gains a third band from *its* `fail_above`. It does not
 * regain a literal.
 *
 * **Takes a `number`, not a nullable one** — `compare_profiles` returns `psi: null` for a
 * column it could not measure, and the caller has to decide. Unchanged.
 */
export function psiBand(psi: number, warnAbove: number): "stable" | "shifted" {
  return psi > warnAbove ? "shifted" : "stable";
}
```

- [ ] **Step 4: Fix the callers, and source the threshold**

Find every `psiBand(` call: `grep -rn "psiBand" frontend/src`. Each must now supply
`warn_above`, fetched via `listRules` and read from VR-DST-1's `params` — **not** re-declared
at the call site, which would move the literal rather than remove it.

**Two things to decide by reading, not by guessing:** which component owns the fetch (the PSI
comparison selector on the Profile view is where §5.3 puts the banding), and what it renders
while the rules are in flight or if VR-DST-1 is absent from the workspace. **A missing rule
must not fall back to `0.1`** — that silently restores the literal this task removes. Render
"unbanded" and say so.

- [ ] **Step 5: Run both halves and commit**

```bash
pnpm --dir frontend type-check && pnpm --dir frontend test && pnpm --dir frontend build
git add frontend/src/api/profiles.ts frontend/src/api/rules.ts frontend/src/api/__tests__/
git commit -m "fix(w6b-13): psiBand reads VR-DST-1 rather than asserting a band no rule emits"
```

---

## Self-review

**Spec coverage.** `FR-DATA-54`'s reviewed path is reachable from the screen (Tasks 2–3);
`FR-DATA-53`'s `catalogue_id` lineage survives the browser (Tasks 1–2); §5.3's Contents cell
agrees with both (Task 4); §5.3's 2026-08-19 banding note stops being contradicted by the code
under it (Task 5). `FR-DATA-21` and `FR-DATA-22` are consumed unchanged — the builder already
implements the chain and `replaceRuleSet` already versions the set. **Not covered, and named
rather than silent:** the `fail` band's second catalogue rule and the three lineage defects,
both in Out of scope with a route and an owner.

**Unfinished, stated plainly.** This plan was filed under a stand-down, and **Task 5 did not
get the verification sweep the other four did** — it was added after `w6b-decision-maker`'s
ruling reversed this plan's own recommendation, and its two open reading-tasks (Step 4's owner
and its in-flight state) are deliberately left as instructions to read rather than as sample
code, per `docs/plans/README.md`'s "name the authority over supplying a sample". Tasks 1–4 were
swept against `dcb0823` literal by literal; Task 5 was not.

**Placeholders.** One deliberate elision, at Task 2 Step 6's authoring steps, and it is the
recommended form: the plan cannot verify that file's driving code, so it names the authority
(the neighbouring authoring test) instead of supplying a sample that would be invented.
`docs/plans/README.md`'s unenforced convention 3 is explicit that this beats a guess.

**Type consistency.** `RuleCreate` is introduced in Task 1 and used in Task 2; `seed` is
produced in Task 2 and consumed in Task 3; `versioning` is local to Task 3. `ValidationRule` is
already exported from `@/api/rules:5` and already imported in `RuleSetView.vue:17`.

**Literals.** Every `path:line` above was read at `dcb0823`. Two classes are **not** repository
facts and are marked where used: the accessible name "New version" is chosen by this plan, and
`catalogue_id: "VR-ACT-3"` in Task 2's fixture is an illustrative catalogue id — the executor
must use one the seed actually writes, since `create_rule` refuses a `catalogue_id` naming no
catalogue entry, and a wrong one fails at the boundary rather than in the assertion.

**Freeze note.** This plan is verified against `dcb0823`. Per the standing rule that a plan is
swept immediately before its build rather than at filing, **re-verify the `path:line`
citations against the tree you build on** — every one of them is in a file this slice edits,
so a rebase moves them.
