---
id: PL-753
family: plan
kind: map
title: WK-664 and WK-692 — the slice map
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-08-22
owner: planner
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                     # ids only
was: docs/plans/2026-08-22-w6b-slice-map.md
---

# WK-664 and WK-692 — the slice map

> **This is a decomposition, not an implementation plan.** It says what the work is, what
> order it can be done in, and what cannot start yet. The implementation plans are separate
> files, one per slice; the first is
> [`PL-00752-w32-1-contracts-and-the-drift-guard-implementation-plan.md`](PL-00752-w32-1-contracts-and-the-drift-guard-implementation-plan.md).

**Written:** 2026-08-22, immediately after WK-661 closed, from four investigation agents'
findings plus four checks run in the main thread. Frozen at that date per
[`README.md`](README.md) — it records what was believed then.

**Scope:** everything [`../roadmap.md`](../roadmap.md) assigns to WK-664, gathered from its
Phase 1b row and from every closure record and plan review that named WK-664 as an owner.

---

## 1. Why this file exists

WK-664's roadmap row names three things — factor workbench, model detail, diagnostics — plus
"the frontend platform". Sweeping every `WK-664` mention across the suite finds **25 distinct
items**, of which the row names roughly half.

The house style for an implementation plan in this directory runs to about 1 300 lines for a
*single* view ([`PL-00739-the-psi-comparison-selector-01-5-3-fr-63-implementation-plan.md`](PL-00739-the-psi-comparison-selector-01-5-3-fr-63-implementation-plan.md)).
Twenty-five items is not one plan, and the `writing-plans` skill's scope check says so: a plan
should produce working, testable software on its own.

This map is the index those plans hang from.

### The split, and the id

Plan review 1 proposed that WK-664 be split — *"a row whose scope spans a Vue view, an OIDC flow
and a database trigger is a row nothing can be said to have closed"* — and the maintainer
accepted on 2026-08-15, deferring the id: *"The non-frontend half splits out when Phase 1b is
planned; WK-664 keeps the views and the browser. The id is assigned at that point, not here."*

**Assigned 2026-08-22: `WK-692`.** WK-657–WK-691 are all allocated. A suffix (fenced below — never a
real historical id, only illustrating the rejected alternative) would put the
non-frontend work back inside the WK-662 frontend family, which is the confusion the split existed
to end. A distinct number says "not frontend", and `WK-690` is the precedent for a workstream
discovered later and numbered outside its phase's block.

```
W6c
```
*Fenced 2026-09-04 under RL-1044 §5.1; value unchanged (row (d8), task #30) — the
rejected-alternative suffix above, never a real historical id, was tripping the bare
work-key check.*

| Workstream | Holds |
|---|---|
| **WK-664** | The Vue views and the browser — `02` §5.3's model surfaces, the `01` §5.3 remainder, browser authentication, accessibility, workspace selection |
| **WK-692** | Everything that is not a browser — contract guards, `model-schema` shapes, a migration, backend defects, endpoint tests, and one skill |

---

## 2. What the investigation changed

Three findings reshape the plan rather than merely populating it.

**The backend is far readier than the roadmap implies.** Every endpoint the WK-664 views need
already exists and is already published in
[`../contracts/openapi/generated.json`](../contracts/openapi/generated.json). WK-664 is genuinely
frontend-first. The exceptions are narrow and named in §4.

**About ten items cannot start, because the specification does not yet say what to build.**
[`../../CLAUDE.md`](../../CLAUDE.md) §0's table is explicit that a capability not yet specified
is a spec change first, then code. §4 is that backlog. Sequencing the buildable work ahead of
it is the whole point of this map.

**Writing the first slice's plan found six live contract defects before any code was
written**, because sizing its guards meant measuring them rather than estimating. They are
listed in
[`PL-00752-w32-1-contracts-and-the-drift-guard-implementation-plan.md`](PL-00752-w32-1-contracts-and-the-drift-guard-implementation-plan.md);
the one worth knowing here is that `objective-certificate` publishes a `minItems` of **8** on a
certificate's checks while the model requires **1**, which is a question about `FR-151`'s
certification machinery rather than a schema typo. The measurement also caught a defect in the
*plan's own* first draft: a guard that unioned `required` across a discriminated `oneOf` would
have reported two false positives, and following it would have made the contract refuse every
valid categorical bin.

**One ownership contradiction is live.** [`../roadmap.md`](../roadmap.md) line 1871 says
`FR-358`'s approvals inbox "is WK-664"; the Phase 3 workstream table says `WK-678` — *Approvals
inbox with inline evidence* — owns `FR-358`. Two rows disagree. Building it in Phase 1b
would also be building ahead of the phase. **Recommended resolution: `WK-678` owns it and line
1871 is a slip**, corrected with a dated note rather than deleted. This map does not make that
change; §0 reserves it.

---

## 3. The slices

Ordered by what unblocks what. A slice with no dependency listed can start today.

### WK-692 — the non-frontend half

| # | Slice | Depends on | Plan |
|---|---|---|---|
| **W32-1** | **Contracts and the drift guard** — `source_level_stats` on `GroupingEvidence`, the constraint-level half of the contract-drift guard, and the `contract-guard` knowledge | — | [written](PL-00752-w32-1-contracts-and-the-drift-guard-implementation-plan.md) |
| **W32-2** | **Validation rule ids as data** — a `BUILTIN_RULES` catalogue in `model-schema`, seeded per workspace the way `BUILTIN_ROLES` is | — | not written |
| **W32-3** | **Dataset list projections** — `FR-55`'s two derived fields and `FR-82`'s `owner_id` migration | — | not written |
| **W32-4** | **The EBM predict arm** — `prediction.py` refuses EBM with `MODEL_TYPE_UNSUPPORTED` | — | not written |
| **W32-5** | **Two partial-dependence defects** — `_sweep` reports row-count share as exposure share, and the sweep runs over a factor's source column rather than its resolved levels | — | not written |
| **W32-6** | **Endpoint tests** for the backtest read route and the custom-objective routes, which are evidenced only as "the route is published" | — | not written |

### WK-664 — the views and the browser

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
| **W6b-9** | **Tabular chart fallback** (`NFR-463`) | — | — |
| **W6b-10** | **Browser authentication** (`FR-393`) | — | §4 items 1, 2 |
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
| 1 | The compose stack ships **no OIDC provider**. `deploy/docker-compose.yml` runs postgres, redis and minio | `W6b-10` | `07` `FR-387` states *"A local development provider ships with the compose stack (R2)."* It does not. Spec and repository disagree; §0 says resolve, do not quietly edit either |
| 2 | **The workspace selector has no requirement.** `07` §3.1 holds `FR-387`…`FR-392` and `FR-393` and names nothing about workspace selection | `W6b-11` | The roadmap assigns it citing §3.1, which does not contain it. A capability nobody specified |
| 3 | `ShapInteraction` carries `pair`, `strength` and `exposure_share` — **no holdout lift**, which appears nowhere in the repository | `W6b-5` | `FR-135` and `02` §5.3 both require exposure share *and* holdout lift. Related: `interactions_available` is `False` on LightGBM, so the view needs a capability-absent state, not an empty list |
| 4 | **No collection endpoints** for custom objectives, custom metrics or peril structures | `W6b-4`, `W6b-7` | `02` §5.1 declares none either, so this is a spec gap before it is a code gap. `02` §5.3 asks `/objectives` to list "status, applicability, usage count" with nothing to call |
| 5 | `02` §5.3 addresses peril structures and objective certificates by `slug@version`; both backends resolve by **UUID only** | `W6b-7`, `W6b-8` | Either the spec's addressing is wrong or the routes are. The router already carries the precedent — `/models/:slug` uses `?version=` |
| 6 | The lineage handler returns `dict[str, Any]`, so the generated client type is `Record<string, unknown>` | `W6b-12` | §2's rule forbids hand-writing a shape that should live in `model-schema`; a graph view would have to |
| 7 | **Threshold editing is not expressible.** `RuleSetEntry` permits exactly two overrides, `enabled` and `severity_override`; thresholds live on the rule, not the set | `W6b-13` | Needs a decision: is a threshold edit a new rule version under `FR-50`'s reviewed path, or a third permitted set-level override? |
| 8 | `02` §5.3 describes the certificate's statuses as "pass/warn/fail" | `W6b-7` | `CheckStatus` has **four** values, and `violated` is the ordinary result for a legitimate non-convex pricing loss — not a failure |
| 9 | A **backtest view** is named as WK-664's in a slice record, and `02` §5.3 has no row for it | `W6b-6` | The view is owed by a closure record and specified nowhere |
| 10 | The **model detail and diagnostics views have no requirement** — they exist only as a `02` §5.3 Contents column | `W6b-1` | The largest frontend slice in the workstream is unspecified as an obligation |
| 11 | `FR-358`'s approvals inbox is claimed by both WK-664 and `WK-678` | — | §2 above. Recommended: `WK-678` owns it |

**Highest ids in use, for whoever writes these.** Verified 2026-08-22 by scanning
[`../specs/`](../specs/) — a maximum, not the last id read, because `01`'s and `02`'s tables
are not in numeric order.

Highest ids in use: FR-22, NFR-464. Next free: `FR-23`, `NFR-OVR-12`.
Highest ids in use: FR-67, NFR-474. Next free: `FR-68`, `NFR-DATA-11`.
Highest ids in use: FR-179, NFR-488. Next free: `FR-180`, `NFR-MODEL-15`.
Highest ids in use: FR-436, NFR-535. Next free: `FR-417`, `NFR-PLAT-12`.
Highest ids in use: FR-362, NFR-525. Next free: `FR-GOV-46`, `NFR-GOV-9`.

---

## 5. Two things that will bite at closure

Recorded here because they are cheaper to know now than to discover at a §13 audit.

**Frontend requirement traceability does not exist.** Backend tests carry
`@pytest.mark.req`, which `scripts/req-coverage.py` reads. The frontend convention is
**prose** — the requirement id lives in the `it(...)` string, and nothing machine-reads it. So
every frontend requirement WK-664 delivers will read as unevidenced to the instrument that
decides whether a workstream can close. This is not a defect introduced by WK-664; it is a gap
WK-664 is the first workstream large enough to be judged by. Either the coverage script learns to
read the frontend, or WK-664's closure record states plainly why a test is the wrong instrument
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
in §4, and the `WK-678` resolution recommended in §2. None of it binds until accepted, and the
roadmap is not edited on this file's authority.

| Proposal | Accepted |
|---|---|
| The `WK-664` / `WK-692` split, as scoped in §1 | 2026-08-22 |
| The slice boundaries and sequencing in §3 | **2026-08-24** — accepted, no boundary amended, via `PL-00776-wk-692-what-closure-needs-and-why-it-cannot-happen-yet.md` B2. W32-1 … W32-6 are accepted **as executed**: they were built and merged against these cuts while this row still read *pending*, which is the thing worth recording — the boundaries were load-bearing for two days before they were accepted |
| The specification backlog in §4, as the gate on the blocked slices | *pending* as an **acceptance** — **but its substance was discharged 2026-08-23**, and this row read bare *pending* until 2026-08-24, which misled in the one direction that matters to a session waiting on the gate. All eleven §4 items are resolved: four were spec gaps and are now requirements (`07` FR-398, FR-395, FR-396, `01` FR-56, `02` FR-167), four were the spec being wrong and are corrected on the spec's side, two were shapes that escaped the contract, and three new questions came out of the work — OQ-601, OQ-647, OQ-648, each on a gate row. See `../roadmap.md`, the dated block "2026-08-23 — the WK-664 slice map's specification backlog is resolved". **What is not resolved is the code** — and note that the roadmap block's next clause, `W6b-11` staying blocked until OQ-648 is decided, **was amended on 2026-08-23 in the same block**: OQ-648 was decided that day (option (a), the verified `Workspace-Id` header, specified as `07` FR-397), so `W6b-11` is no longer blocked on a decision and waits only on **WK-692 building the header half**. Quoting the clause without its amendment invents a second gate that does not exist. *(Deliberately still unsigned: the maintainer's 2026-08-24 instruction reached the closure proposal's Parts B, C and D, not this table's remaining rows, and a session does not sign an acceptance because the work happens to be done. The fact is recorded here; the signature is the maintainer's.)* |
| `WK-678` owns `FR-358`; roadmap line 1871 corrected with a dated note | *pending* |
| §5's two closure hazards, and who owns each | *pending* — **half discharged 2026-08-24.** The second hazard, the guard's reach, now has an owner: `dataset-version` and `validation-report` go to **W32-11** (closure proposal Part C), and `validation-rule` gained a generated side on 2026-08-23 in W32-2, so §5's counts above are one item stale and are left as written — a filed plan is frozen at its date. The **first** hazard is untouched: whether `req-coverage.py` learns to read the frontend, or WK-664's closure record states why a test is the wrong instrument there, is a WK-664 closure question and was outside the instruction that decided the rest. The row stays *pending* on that half |
