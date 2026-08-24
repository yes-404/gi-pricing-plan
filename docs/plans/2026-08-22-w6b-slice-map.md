# W6b and W32 — the slice map

> **This is a decomposition, not an implementation plan.** It says what the work is, what
> order it can be done in, and what cannot start yet. The implementation plans are separate
> files, one per slice; the first is
> [`2026-08-22-w6b-contracts-and-drift-guard.md`](2026-08-22-w6b-contracts-and-drift-guard.md).

**Written:** 2026-08-22, immediately after W5 closed, from four investigation agents'
findings plus four checks run in the main thread. Frozen at that date per
[`README.md`](README.md) — it records what was believed then.

**Scope:** everything [`../roadmap.md`](../roadmap.md) assigns to W6b, gathered from its
Phase 1b row and from every closure record and plan review that named W6b as an owner.

---

## 1. Why this file exists

W6b's roadmap row names three things — factor workbench, model detail, diagnostics — plus
"the frontend platform". Sweeping every `W6b` mention across the suite finds **25 distinct
items**, of which the row names roughly half.

The house style for an implementation plan in this directory runs to about 1 300 lines for a
*single* view ([`2026-08-19-psi-comparison-selector.md`](2026-08-19-psi-comparison-selector.md)).
Twenty-five items is not one plan, and the `writing-plans` skill's scope check says so: a plan
should produce working, testable software on its own.

This map is the index those plans hang from.

### The split, and the id

Plan review 1 proposed that W6b be split — *"a row whose scope spans a Vue view, an OIDC flow
and a database trigger is a row nothing can be said to have closed"* — and the maintainer
accepted on 2026-08-15, deferring the id: *"The non-frontend half splits out when Phase 1b is
planned; W6b keeps the views and the browser. The id is assigned at that point, not here."*

**Assigned 2026-08-22: `W32`.** W1–W31 are all allocated. A suffix (`W6c`) would put the
non-frontend work back inside the W6 frontend family, which is the confusion the split existed
to end. A distinct number says "not frontend", and `W30` is the precedent for a workstream
discovered later and numbered outside its phase's block.

| Workstream | Holds |
|---|---|
| **W6b** | The Vue views and the browser — `02` §5.3's model surfaces, the `01` §5.3 remainder, browser authentication, accessibility, workspace selection |
| **W32** | Everything that is not a browser — contract guards, `model-schema` shapes, a migration, backend defects, endpoint tests, and one skill |

---

## 2. What the investigation changed

Three findings reshape the plan rather than merely populating it.

**The backend is far readier than the roadmap implies.** Every endpoint the W6b views need
already exists and is already published in
[`../contracts/openapi/generated.json`](../contracts/openapi/generated.json). W6b is genuinely
frontend-first. The exceptions are narrow and named in §4.

**About ten items cannot start, because the specification does not yet say what to build.**
[`../../CLAUDE.md`](../../CLAUDE.md) §0's table is explicit that a capability not yet specified
is a spec change first, then code. §4 is that backlog. Sequencing the buildable work ahead of
it is the whole point of this map.

**Writing the first slice's plan found six live contract defects before any code was
written**, because sizing its guards meant measuring them rather than estimating. They are
listed in
[`2026-08-22-w6b-contracts-and-drift-guard.md`](2026-08-22-w6b-contracts-and-drift-guard.md);
the one worth knowing here is that `objective-certificate` publishes a `minItems` of **8** on a
certificate's checks while the model requires **1**, which is a question about `FR-MODEL-76`'s
certification machinery rather than a schema typo. The measurement also caught a defect in the
*plan's own* first draft: a guard that unioned `required` across a discriminated `oneOf` would
have reported two false positives, and following it would have made the contract refuse every
valid categorical bin.

**One ownership contradiction is live.** [`../roadmap.md`](../roadmap.md) line 1871 says
`FR-GOV-16`'s approvals inbox "is W6b"; the Phase 3 workstream table says `W18` — *Approvals
inbox with inline evidence* — owns `FR-GOV-16`. Two rows disagree. Building it in Phase 1b
would also be building ahead of the phase. **Recommended resolution: `W18` owns it and line
1871 is a slip**, corrected with a dated note rather than deleted. This map does not make that
change; §0 reserves it.

---

## 3. The slices

Ordered by what unblocks what. A slice with no dependency listed can start today.

### W32 — the non-frontend half

| # | Slice | Depends on | Plan |
|---|---|---|---|
| **W32-1** | **Contracts and the drift guard** — `source_level_stats` on `GroupingEvidence`, the constraint-level half of the contract-drift guard, and the `contract-guard` knowledge | — | [written](2026-08-22-w6b-contracts-and-drift-guard.md) |
| **W32-2** | **Validation rule ids as data** — a `BUILTIN_RULES` catalogue in `model-schema`, seeded per workspace the way `BUILTIN_ROLES` is | — | not written |
| **W32-3** | **Dataset list projections** — `FR-DATA-50`'s two derived fields and `FR-DATA-51`'s `owner_id` migration | — | not written |
| **W32-4** | **The EBM predict arm** — `prediction.py` refuses EBM with `MODEL_TYPE_UNSUPPORTED` | — | not written |
| **W32-5** | **Two partial-dependence defects** — `_sweep` reports row-count share as exposure share, and the sweep runs over a factor's source column rather than its resolved levels | — | not written |
| **W32-6** | **Endpoint tests** for the backtest read route and the custom-objective routes, which are evidenced only as "the route is published" | — | not written |

### W6b — the views and the browser

| # | Slice | Depends on | Blocked by |
|---|---|---|---|
| **W6b-1** | **Model detail, the non-GLM arms** — GBM, quantile intervals, the surrogate link, EBM — and the diagnostics view with its GBM eval curves | W32-1 | §4 item 10 |
| **W6b-2** | **Model comparison** `/models/compare?ids=` | W6b-1 | — |
| **W6b-3** | **Dataset list Contents** — status badge, last validated, owner | W32-3 | — |
| **W6b-4** | **Model spec builder** `/models/new` | W6b-1 | §4 item 4 (the objective picker half) |
| **W6b-5** | **Factor workbench remainder** — intent controls, interaction suggestions, inline one-ways | W32-1 | §4 item 3 |
| **W6b-6** | **Backtest and prediction views** | W6b-1 | §4 item 9 |
| **W6b-7** | **Objective library and certificate** | — | §4 items 4, 5, 8 |
| **W6b-8** | **Peril structure view** | — | §4 item 5 |
| **W6b-9** | **Tabular chart fallback** (`NFR-OVR-10`) | — | — |
| **W6b-10** | **Browser authentication** (`FR-PLAT-55`) | — | §4 items 1, 2 |
| **W6b-11** | **Workspace selector** | W6b-10 | §4 item 2 |
| **W6b-12** | **Lineage graph** | — | §4 item 6 |
| **W6b-13** | **Rule set threshold editing** | W32-2 | §4 item 7 |

`W6b-9` is deliberately unblocked and independent. Two charts already exist —
`OneWayChart.vue` and `HistogramChart.vue` — so the tabular fallback has something to retrofit
rather than waiting on a chart that has not been drawn.

---

## 4. The specification backlog

Each item below stops a slice from starting. None is code; each is a spec change or a
resolution under [`../../CLAUDE.md`](../../CLAUDE.md) §0, and several are disagreements where
**which side is wrong is a real question**.

| # | What | Where it bites | The disagreement |
|---|---|---|---|
| 1 | The compose stack ships **no OIDC provider**. `deploy/docker-compose.yml` runs postgres, redis and minio | `W6b-10` | `07` `FR-PLAT-1` states *"A local development provider ships with the compose stack (R2)."* It does not. Spec and repository disagree; §0 says resolve, do not quietly edit either |
| 2 | **The workspace selector has no requirement.** `07` §3.1 holds `FR-PLAT-1`…`FR-PLAT-6` and `FR-PLAT-55` and names nothing about workspace selection | `W6b-11` | The roadmap assigns it citing §3.1, which does not contain it. A capability nobody specified |
| 3 | `ShapInteraction` carries `pair`, `strength` and `exposure_share` — **no holdout lift**, which appears nowhere in the repository | `W6b-5` | `FR-MODEL-79` and `02` §5.3 both require exposure share *and* holdout lift. Related: `interactions_available` is `False` on LightGBM, so the view needs a capability-absent state, not an empty list |
| 4 | **No collection endpoints** for custom objectives, custom metrics or peril structures | `W6b-4`, `W6b-7` | `02` §5.1 declares none either, so this is a spec gap before it is a code gap. `02` §5.3 asks `/objectives` to list "status, applicability, usage count" with nothing to call |
| 5 | `02` §5.3 addresses peril structures and objective certificates by `slug@version`; both backends resolve by **UUID only** | `W6b-7`, `W6b-8` | Either the spec's addressing is wrong or the routes are. The router already carries the precedent — `/models/:slug` uses `?version=` |
| 6 | The lineage handler returns `dict[str, Any]`, so the generated client type is `Record<string, unknown>` | `W6b-12` | §2's rule forbids hand-writing a shape that should live in `model-schema`; a graph view would have to |
| 7 | **Threshold editing is not expressible.** `RuleSetEntry` permits exactly two overrides, `enabled` and `severity_override`; thresholds live on the rule, not the set | `W6b-13` | Needs a decision: is a threshold edit a new rule version under `FR-DATA-21`'s reviewed path, or a third permitted set-level override? |
| 8 | `02` §5.3 describes the certificate's statuses as "pass/warn/fail" | `W6b-7` | `CheckStatus` has **four** values, and `violated` is the ordinary result for a legitimate non-convex pricing loss — not a failure |
| 9 | A **backtest view** is named as W6b's in a slice record, and `02` §5.3 has no row for it | `W6b-6` | The view is owed by a closure record and specified nowhere |
| 10 | The **model detail and diagnostics views have no requirement** — they exist only as a `02` §5.3 Contents column | `W6b-1` | The largest frontend slice in the workstream is unspecified as an obligation |
| 11 | `FR-GOV-16`'s approvals inbox is claimed by both W6b and `W18` | — | §2 above. Recommended: `W18` owns it |

**Highest ids in use, for whoever writes these.** Verified 2026-08-22 by scanning
[`../specs/`](../specs/) — a maximum, not the last id read, because `01`'s and `02`'s tables
are not in numeric order.

Highest ids in use: FR-OVR-19, NFR-OVR-11. Next free: `FR-OVR-20`, `NFR-OVR-12`.
Highest ids in use: FR-DATA-52, NFR-DATA-10. Next free: `FR-DATA-53`, `NFR-DATA-11`.
Highest ids in use: FR-MODEL-123, NFR-MODEL-14. Next free: `FR-MODEL-124`, `NFR-MODEL-15`.
Highest ids in use: FR-PLAT-56, NFR-PLAT-11. Next free: `FR-PLAT-57`, `NFR-PLAT-12`.
Highest ids in use: FR-GOV-45, NFR-GOV-8. Next free: `FR-GOV-46`, `NFR-GOV-9`.

---

## 5. Two things that will bite at closure

Recorded here because they are cheaper to know now than to discover at a §13 audit.

**Frontend requirement traceability does not exist.** Backend tests carry
`@pytest.mark.req`, which `scripts/req-coverage.py` reads. The frontend convention is
**prose** — the requirement id lives in the `it(...)` string, and nothing machine-reads it. So
every frontend requirement W6b delivers will read as unevidenced to the instrument that
decides whether a workstream can close. This is not a defect introduced by W6b; it is a gap
W6b is the first workstream large enough to be judged by. Either the coverage script learns to
read the frontend, or W6b's closure record states plainly why a test is the wrong instrument
there — §13 rule 1 accepts the second, but not silence.

**`docs/contracts/schemas/` holds 26 hand-authored schemas against 22 generated ones, and 12
have both sides.** The other **14 authored schemas have no generated counterpart at all** and
are therefore compared against nothing: approval-request, dataset-version, dislocation-run,
dossier, gipp-check, monitoring, optimisation-run, rate-table, rating-algorithm,
rating-version, regression-suite, scoring, validation-report, validation-rule. Most describe
Phase 2+ artifacts that no model backs yet, which is why they are uncompared and not
alarming — but `dataset-version`, `validation-report` and `validation-rule` describe artifacts
Phase 1a **built**. Those three are a genuine gap in the guard's reach and belong to `W32-1`'s
successor, not to `W32-1` itself, which has enough in it.

---

## 6. Maintainer acceptance

The split id was decided by the maintainer on 2026-08-22 and is recorded in §1.

Everything else on this page is a **proposal** under `CLAUDE.md` §14's rule that a review's
output is never a change: the slice boundaries in §3, the sequencing, the eleven-item backlog
in §4, and the `W18` resolution recommended in §2. None of it binds until accepted, and the
roadmap is not edited on this file's authority.

| Proposal | Accepted |
|---|---|
| The `W6b` / `W32` split, as scoped in §1 | 2026-08-22 |
| The slice boundaries and sequencing in §3 | **2026-08-24** — accepted, no boundary amended, via `2026-08-23-w32-closure-proposal.md` B2. W32-1 … W32-6 are accepted **as executed**: they were built and merged against these cuts while this row still read *pending*, which is the thing worth recording — the boundaries were load-bearing for two days before they were accepted |
| The specification backlog in §4, as the gate on the blocked slices | *pending* as an **acceptance** — **but its substance was discharged 2026-08-23**, and this row read bare *pending* until 2026-08-24, which misled in the one direction that matters to a session waiting on the gate. All eleven §4 items are resolved: four were spec gaps and are now requirements (`07` FR-PLAT-58, FR-PLAT-62, FR-PLAT-63, `01` FR-DATA-54, `02` FR-MODEL-127), four were the spec being wrong and are corrected on the spec's side, two were shapes that escaped the contract, and three new questions came out of the work — OQ-MODEL-31, OQ-PLAT-8, OQ-PLAT-9, each on a gate row. See `../roadmap.md`, the dated block "2026-08-23 — the W6b slice map's specification backlog is resolved". **What is not resolved is the code** — and note that the roadmap block's next clause, `W6b-11` staying blocked until OQ-PLAT-9 is decided, **was amended on 2026-08-23 in the same block**: OQ-PLAT-9 was decided that day (option (a), the verified `Workspace-Id` header, specified as `07` FR-PLAT-65), so `W6b-11` is no longer blocked on a decision and waits only on **W32 building the header half**. Quoting the clause without its amendment invents a second gate that does not exist. *(Deliberately still unsigned: the maintainer's 2026-08-24 instruction reached the closure proposal's Parts B, C and D, not this table's remaining rows, and a session does not sign an acceptance because the work happens to be done. The fact is recorded here; the signature is the maintainer's.)* |
| `W18` owns `FR-GOV-16`; roadmap line 1871 corrected with a dated note | *pending* |
| §5's two closure hazards, and who owns each | *pending* — **half discharged 2026-08-24.** The second hazard, the guard's reach, now has an owner: `dataset-version` and `validation-report` go to **W32-11** (closure proposal Part C), and `validation-rule` gained a generated side on 2026-08-23 in W32-2, so §5's counts above are one item stale and are left as written — a filed plan is frozen at its date. The **first** hazard is untouched: whether `req-coverage.py` learns to read the frontend, or W6b's closure record states why a test is the wrong instrument there, is a W6b closure question and was outside the instruction that decided the rest. The row stays *pending* on that half |
