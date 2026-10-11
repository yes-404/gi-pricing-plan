---
id: PL-9799
family: plan
kind: map
title: WK-1178 — exit demo (b), WF-699 D4's fixed property declaration, and the lines the 11 Oct merges made stale: a dated delta to PL-1544
status: draft                  # draft → active → superseded | retired (§1.2a)
created: 2026-10-11            # original date 2026-10-11, set at the draft
owner: planner
tree: 1b04cb05a72e2329d35f57dd87cb3be600096177
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1544, PL-1577, PL-1525, RL-1524, RL-1522, RL-1521, FD-1244, FD-1416, SL-1527, SL-1526, SL-1529, SL-1340, LG-1641, PL-1574, FD-1576, WF-699, FR-261]
---

# WK-1178, exit demo (b): WF-699 D4's fixed property declaration and the stale lines (delta to PL-1544)

*Disclosure: drafted under working id 9799, reserved by the lead (eta, "2026-10-11 23:17:40
BST"). It is not minted. Every mention of this file in its own text uses the working id.*

> **For agentic workers:** this is a **dated delta** under Lean P2 L5 (`document-ids.md` §1.6,
> PL row: *"a change is one dated Work-plan delta, a new `PL-` that `relates:` the Work's
> plan"*). It does not replace
> [`PL-1544`](PL-01544-wk-1178-exit-demo-slice-b-the-scripted-wf-699-journey-over-http-to-a-served-page-leaf-plan.md)
> (exit-demo slice (b), `SL-1527`, frozen since its merge in `61e2a8d9`). Its form follows
> [`PL-1577`](PL-01577-wk-1178-r6-the-exit-demo-dislocation-portfolio-a-20000-policy-sample-built-by-the-seed-plan-delta.md),
> the first delta to `PL-1544`. **Read `PL-1544` in full, then `PL-1577`, then this file.**
> Where they differ, this file is the latest statement. The executor of `SL-1527` binds
> `python-test`, `test-driven-development`, `dev-commands` and `git-hygiene`, and is spawned
> from `.claude/roles/executor.md`.

Written 2026-10-11 by the planner (planner-pl1544), on the lead's order of 2026-10-11 (after
the readiness note `handover/readiness-pl1544-2026-10-11.md`, local). Evidence was read at
`origin/main` `1b04cb05a72e2329d35f57dd87cb3be600096177` (#1285, 2026-10-11 23:12 BST).

## Status

`draft` until it mints. **DP-D4 is ruled (a)**: `bonus_malus`, increasing, over the NCD
ladder (the maintainer (by delegation), 23:18:17 BST, quoted below). It was drafted open with
both variants (commit `cf2d31a4` on this branch), and this file now carries only (a). It mints
first in the next docs PR, together with the decision-maker's WF-699 D4 T-text (working id
RL 9701, reserved in eta "2026-10-11 23:18:40 BST"), and before `SL-1527`'s activation (the 23:18:17 entry, item 4). `PL-1544`'s activation
needs 1 to 16 and 18 are **MET** at `1b04cb05`. Need 17, the lead's go, is **given
conditionally**: *"Its activation and gate wait for PL 9799 and the WF-699 T-text to MINT."*
§"Activation needs at `1b04cb05`" gives the evidence.

## The rulings this delta records

These entries are local channel entries (RFC-777). They are quoted so that this plan carries
them.

**DP-D4 ruled**: the maintainer (by delegation), `channel/to-lead.md`, entry headed
*"2026-10-11 23:18:17 BST — PL-1544 (SL-1527) re-check ACCEPTED: needs 1–16 and 18 MET. DP-D4 =
(a), bonus_malus increasing over the NCD ladder, WITH a dated WF-699 D4 amendment (spec text,
not a silent reading). SL-1527 authors NOW; the GO (need 17) is effective when PL 9799 + the
WF-699 T-text mint"*, items 1 to 4, verbatim:

> 1. DP-D4 = (a): premium increasing in bonus_malus on [50, 230] over the hand-written NCD-ladder sub-graph; grid spacing 45 (properties.py :75's 5-point grid). Reason, the 19:07:08 rule: the property cannot depend on the fit, so the D4 failure is the DELIBERATE inverted band, and D5's fix is provably the cure. (b) is rejected: driv_age's fitted effect on freMTPL2 is not guaranteed monotone (it is typically U-shaped), so the post-D5 pass would depend on the fit and the journey could not demonstrate a clean fix.
> 2. SPEC, NOT A SILENT READING: WF-699 D4 names "monotone_in_age … two rate tables band age differently". Choosing bonus_malus departs from that literal text, so a decision-maker T-text amends WF-699 D4 by a dated line: "the demo's monotone property is premium increasing in bonus_malus over the NCD ladder; the deliberate inversion is a ladder band wider than the grid spacing (amended 2026-10-11, <this entry>, RL-1524 DP-1 unchanged in substance)". The original text is struck, not deleted. Record: the T-text rides with PL 9799.
> 3. PL 9799 (a dated delta, PL-1577's form, relates PL-1544) carries items 1–6 exactly as listed in your 23:17:40, with (a) filled in. Item 5's STOP holds: if the property fails on the real bundle BEFORE the injection, or AFTER D5's fix → STOP to me; never re-chosen. Item 6, red-first: two different fits → the identical declared property.
> 4. GO (need 17), CONDITIONAL: SL-1527 AUTHORS NOW on the G2 path. Its activation and gate wait for PL 9799 and the WF-699 T-text to MINT. Put both FIRST in D13 (with the owed FD-1416 / FD-1244 / FD-1245 register lines, FD-1618 / FD-1611 closes, FD 9702, RS 9703 + its FDs, FD 9797, FD-1561's line), or in a small dedicated docs PR ahead of D13 if D13 is not ready within a few hours. Merge order: the docs PR, then SL-1527.

[Bracketed note on the quoted block: "PL 9799" is this file's working id, quoted as written.]

**The forward to SL-1527**: the maintainer (by delegation), `channel/to-lead.md`, entry headed
*"2026-10-11 19:07:08 BST — SL-1526 monotone proposal: "NONE" ACCEPTED; bonus_malus not
ratified; WF-699 D4's property demonstration is SL-1527's, declared deliberately"*, items 1 and
2, verbatim:

> 1. "NONE" ACCEPTED: SL-1526's suite declares only fit-independent properties (no-null-output, premium-bounded) via the parameterless declared_properties() (2deb3ebe; red-first: two fits → different lists on 386058fc, the same after). bonus_malus is NOT ratified. It is a raw int input; if the GLM carries it as a monotone term (e.g. linear on a log link), "premium increasing in bonus_malus" holds by the MODEL FORM and tests little. That is not the regression evidence a property should be.
> 2. FORWARD to SL-1527 (PL-1544): WF-699 D4 shows a property assertion FAILING (monotone, the counterexample with the base context and two grid values; RL-1524 DP-1). SL-1527's plan states, before building, which property it declares for D4 and why, as a fixed declaration (never derived from the fit), so D4's failing-property moment is deliberate and reproducible.

**The rule it rests on**: the same author, entry headed *"2026-10-11 18:59:23 BST — SL-1526
attempt b: (1) the DATA-DEPENDENT monotone declaration is a DEFECT, fixed before merge; …"*,
item 1, the lines that bind here, verbatim:

> 1. DEFECT, fixed in SL-1526 before its ACK. A regression property encodes a pricing EXPECTATION that a refit can VIOLATE. A property selected from the fit it is tested against can never fail ("perfect fit is not evidence"), and it vanishes silently on the refit that matters. This also bypasses my 2026-10-11 11:39:18 item 3 (a property failing on the real fit → STOP), because a failing property is simply never declared.
>    (a) Delete the selection logic. The suite's properties are FIXED declarations in the algorithm/suite definition, independent of any fit (name, input, direction).
>    (b) veh_age monotone is NOT declared: the real relativities above show it is not monotone (new vehicles highest). Record them in LG 9966 as the evidence. No demo text claims veh_age monotonicity.
>    (c) The seat PROPOSES to me AT MOST ONE fixed monotone declaration grounded in pricing INTENT, stated before checking the real fit (e.g. premium increasing in bonus_malus: a worse bonus-malus coefficient never lowers the premium), with its one-line actuarial reason. Once I accept, it is declared unconditionally. If the real fit then violates it → STOP to me (11:35:35 rule), never a silent drop. "No monotone property" is also an acceptable proposal, if stated as such.
>    (d) Red-first: a test that the suite's property list does NOT depend on the fit (two different fits → the same declared properties).

[Bracketed note on the quoted block: LG 9966 is minted as `LG-1641`.]

**The binding this plan never discharged**: [`RL-1524`](../rulings/RL-01524-fd-1244-and-fd-1245-wf-699-d4-and-e2-move-to-the-requirements-and-06-s-generic-approval-route-names-the-rating-version-submit-route.md)
DP-1, §"What it obliges": *"PL 9629 (planner-demo2): state the demo data's inverted band and
the grid spacing (DP-1's binding)."* Its §"Acceptance": *"A G2 demo run whose regression run
reports no `monotone` failure at D4 is the observable breach of DP-1's binding; PL 9629's
acceptance carries that check."* PL 9629 is `PL-1544`. `PL-1544` states neither of these. Its
D4 row (`PL-1544:362`) reads *"a `monotone_in_*` property that fails, shrunk; then the banding
fixed (A-phase) and passing | as FD-1244's ruling words it"*, and Acceptance 3 (`:226`) and
Task 3 Step 2 (`:554`) defer to the ruling in the same way. **This delta discharges the
binding.**

## Goal

Before `SL-1527` builds, state the D4 property as a FIXED declaration, together with the
deliberate defect that makes it fail, the grid spacing, the D5 fix that makes it pass, and the
STOP rule. D4's failing-property moment is then deliberate and reproducible, and no part of it
is chosen from a fit. In the same delta, record what the 11 Oct merges changed in `PL-1544`.

Done for this delta when its Acceptance Standard passes on `SL-1527`'s slice head: `SL-1527`
builds `PL-1544` as amended by `PL-1577` and by this file.

## D4: the fixed declaration

### What is fixed (items 1 to 6)

1. **The declaration.** One `monotone` property (`MonotoneInInput`,
   `packages/model-schema/src/model_schema/regression.py:95-108`: `input`, `direction`,
   `strict`, `lower`, `upper`), written as **one constant in `examples/fremtpl2/journey.py`**,
   named `D4_PROPERTY`. It reads no fit, no table and no database. D3's suite version adds it
   to slice (a)'s two fit-independent properties (`no-null-output`, `premium-bounded`;
   `examples/fremtpl2/model.py:559-571`). Slice (a)'s `declared_properties()` is not edited:
   the D4 property belongs to the journey's suite version, not the seed's.
2. **The defect.** In the A phase, the journey writes one deliberate inversion over HTTP, as a
   band of the swept input. The band is **wider than the grid spacing**, which `RL-1524` DP-1
   requires. The spacing is fixed by the engine: a `monotone` sweep visits
   `_GRID_POINTS = 5` uniform points over `[lower, upper]`, plus fixed sampled points
   (`packages/pricing-core/src/pricing_core/rating/properties.py:75`, `:200-217`). So the
   spacing is `(upper − lower) / 4`.
3. **D4.** The D4 regression run reports the `monotone` property **failed**, with its
   counterexample: the base context and two adjacent grid values (`grid: "uniform+sampled"`,
   `regression.py:298-303`). The journey asserts the property's name, the failure and the two
   grid values.
4. **D5.** The journey restores the inverted band over HTTP (the A-phase routes, as
   `PL-1544`'s D5 row says), recompiles, and re-runs the suite. The **same** declared
   property passes.
5. **STOP.** If the declared property fails **before** the defect is written (on the real fit,
   at D1–D2's suite run, which includes it), or still fails after D5, the journey raises
   `JourneyStepFailed("D4", …)` and the executor stops and reports to the maintainer (18:59:23
   item 1(c)). The property is never dropped, narrowed or re-chosen from the fit.
6. **Red first, independent of the fit.** `test_the_d4_property_does_not_depend_on_the_fit`:
   two different fits give the same `D4_PROPERTY`. This mirrors slice (a)'s test (18:59:23
   item 1(d)). It is red while the property is derived from anything other than the
   constant, and it is written first.

### The declaration, DP-D4 (a): `bonus_malus` over the NCD ladder

| | |
|---|---|
| `D4_PROPERTY` | `{"name": "premium-increasing-in-bonus-malus", "check": {"kind": "monotone", "input": "bonus_malus", "direction": "increasing", "strict": false, "lower": "50", "upper": "230"}}` |
| Intent (stated before any fit is read) | A worse bonus-malus coefficient never lowers the premium. That is the purpose of a bonus-malus scale |
| Range and spacing | freMTPL2's own range, `BONUS_MALUS_RANGE = (50, 230)` (`examples/fremtpl2/algorithm.py:40`). Spacing (230 − 50) / 4 = **45**. Uniform points 50, 95, 140, 185, 230 |
| What the premium depends on along the sweep | Only the ladder. The 7-factor GLM does not carry `bonus_malus` (`algorithm.py:36-38`: *"no step of this algorithm consumes it"*), so with the base context fixed, the premium moves only through the ladder's factor. That factor must enter the premium product: B7's mount is **wired into the output**, not only inlined |
| The ladder (A phase) | The rate table behind the `ncd-ladder` sub-graph keys `bonus_malus` in three demo bands: 50–99 → 1.00, 100–149 → 1.20, 150–230 → 1.50. **These are demo values, not a priced NCD scale, and the README says so** |
| The defect (D4) | The 100–149 band is set to 0.90. The band is **50 wide, wider than the spacing of 45**, so the uniform point 140 lies inside it, and the premium at 140 is below the premium at 95. The counterexample is the base context and the grid values 95 and 140 |
| D5 | The 100–149 band is set back to 1.20. The same property passes |
| Fit dependence | **None.** The pass, the fail and the counterexample depend only on the ladder table that the journey writes. Item 5's STOP stays armed regardless: a failure before the defect or after D5 is a STOP, never a re-choice (the 23:18:17 entry, item 3) |
| Spec | WF-699 D4 (`docs/workflows/WF-00699-…md:84`) names `monotone_in_age` and two tables banding age. The decision-maker's dated T-text (working id RL 9701) amends D4 to this property and this inversion, striking the old text, and it mints with this file (the 23:18:17 entry, item 2). `RL-1524` DP-1 is unchanged in substance: an inverted band wider than the grid spacing |

**Not taken: (b), `driv_age`.** It was drafted in full (`cf2d31a4`) and rejected by the 23:18:17
entry, item 1: *"driv_age's fitted effect on freMTPL2 is not guaranteed monotone (it is
typically U-shaped), so the post-D5 pass would depend on the fit"*. `veh_age` was never a
variant: its full-book relativities, 1.9533 / 1.1209 / 1.2534 / 1.2338 / 1.0 (`LG-1641`'s
corrective line), are not monotone, and 18:59:23 item 1(b) bars that claim.

### Who builds the NCD ladder (B7 and D4 both need it)

The seed does not build one. `git grep -l 'ncd-ladder\|ncd_ladder' 1b04cb05 -- backend
packages examples scripts` hits backend and package tests and the comment at
`examples/fremtpl2/algorithm.py:37` only. `PL-1544`'s B7 row (`:350`, *"mount
`sub_graph:ncd-ladder@4`"*) names no builder. **It is a task inside `SL-1527`** (Task 2a
below), over HTTP, in `examples/fremtpl2/journey.py`, so that it is inside `PL-1544`'s write
set and the "over HTTP only" constraint. The routes are on `main`: `POST /api/v1/sub-graphs`
and `POST /api/v1/sub-graphs/{slug}/versions` (`backend/src/app/api/sub_graphs.py:38`, `:53`),
with the rate table created through the A-phase rate-table routes. **`@4`:** WF-699 B7's
"`ncd-ladder@4`" names a pinned version. This plan reads it as *the version the journey saved,
mounted by exact pin*, and does not save four versions to reach the number 4. The lead
confirms or corrects that reading at this file's ACK.

## What changes in PL-1544

| `PL-1544` site (at `1b04cb05`) | Was | Now |
|---|---|---|
| D4 row `:362`; Acceptance 3 `:226`; Task 3 Step 2 `:554` | *"a `monotone_in_*` property … as FD-1244's ruling words it"* | §"D4" items 1–6, with the DP-D4 (a) declaration. Acceptance 3's D4 clause becomes Acceptance 1–3 below |
| B7 row `:350` | *"mount `sub_graph:ncd-ladder@4` … If `SL-1340` is not merged by Wed 4 Nov: `SKIPPED B7: SL-1340`"* | Need 18 is **MET** (`SL-1340` closed, `a3572d1a`, #1263), so the contingency is **moot**. B7 mounts and inlines, and Acceptance 2's `SKIPPED B7: SL-1340` line is never printed. The ladder is built by Task 2a below. Under (a) its factor enters the premium |
| Global Constraints, 2nd bullet `:110-113` | *"Until `FD-1416` is fixed, the approval routes' responses are untyped dicts, and `FD-1416`'s HOLD forbids a client that reads them (activation need 13)."* | **Stale.** `SL-1529` (`e3a98c97`, #1276) makes the `model-schema` `ApprovalRequest` the one definition and types every approval route. [`RL-1522`](../rulings/RL-01522-pl-9616-dp-1-to-10-decided-one-approvalrequest-shape-the-decision-values-are-the-code-s-verbs-a-comment-is-mandatory-only-when-requesting-changes-the-hand-authored-contract-is-retired.md) decides the decision values. The journey reads approval responses through `model_schema`'s `ApprovalRequest`. The HOLD text that survives on `docs/findings/register.md:286` and in `FD-1416` (`status: active`) is a closing act owed to the auditor, not a constraint on this slice |
| Task 1 Step 1 `:515-518`; §Size `:467-468` (*"The journey test runs a small seed in process"*) | the seed size is unstated | **The journey test seeds 20,000 rows** (`--rows 20000`, the size `PL-1544` Acceptance 5 already runs). At 2,000 rows the fit is degenerate: area F has no claims, the relativity is 0.0000 and scoring raises `RATE_TABLE_MISS` (the maintainer (by delegation), `to-lead.md` "2026-10-11 19:22:23 BST", first line: *"cause = a degenerate 2k fit (area F has no claims → quasi-separation, area[F] −15.808, relativity 0.0000) … The 20k control passes all 3 (area F 1.0354)"*). The seed now refuses a fit with a level below `RELATIVITY_FLOOR = 0.01` (`examples/fremtpl2/model.py:420`, `refuse_degenerate_fit` `:427`). 20,000 is the smallest size measured above that floor. A smaller seed is not used. The journey test needs the pinned ARFF. If the ARFF is absent the test is skipped, so the slice's gate record must show it **ran**, not skipped, on the box that has the ARFF |
| D1–D2 row `:359` (*"run passes on slice (a)'s golden quotes"*) | the golden values are unstated | Goldens are recomputed for each seed size (19:22:23, and the reconcile in `LG-1641`). The journey reads the expected values from the seeded suite over HTTP and never from constants |
| Write set, `examples/fremtpl2/README.md` `:451`; Task 6 | *"edited: the one command and what it shows"* | It also carries **the machine-requirement sentence**. The maintainer (by delegation), `to-lead.md` "2026-10-11 16:37:21 BST", item 3, verbatim: *"The README machine-requirement sentence goes to SL-1527, whose journey actually runs D6–D7 in the demo: it states the requirement measured on the real journey. Stage d's container sum is recorded in LG 9966 as the provisional figure and is not written to the README by SL-1526."* [LG 9966 is `LG-1641`.] The figure comes from `PL-1544` Acceptance 5's run: peak host plus container memory, sampled, with the tree and the time. It is never copied from `LG-1641`'s provisional figure |
| `PL-1577` Task 3 (`PL-1577:161-164`) | `PL-1577` assigns the honesty text to `SL-1527`, but `PL-1544`'s Acceptance does not list it | It becomes this delta's Acceptance 6. The D6/D7 output of `journey.py` and the README say *"20,000-policy sample"*, and they name `PL-1574` (full-book dislocation cost) and `FD-1576` (full-book attribution cost). The portfolio Dataset Version is read from `last-seed.json`'s `portfolio_dataset_version_id` (`examples/fremtpl2/seed.py:736-740`) |
| Status `:160-171`; needs table `:173-196` | the states at `cdaaa573` and `680fb9ac` | §"Activation needs at `1b04cb05`" below. Task 0 Step 2 still re-derives them at dispatch |
| `scripts/demo.py` anchors `:274`, `:346-355`, `:356-359` | — | **Not stale.** `git log 680fb9ac..1b04cb05 -- scripts/demo.py backend/tests/test_demo_command.py backend/src/app/platform/workspaces.py backend/tests/test_workspace_members.py` prints nothing |
| S1 row `:376` | *"works on `main` today"* | Now true, since `SL-1631` (`fbde0f70`, #1278) passes the resolved ref on default-live `/score`. `PL-1583` DP-S3E-1 (b) keeps `key` when exactly one Environment is granted, and S1 binds `prod` only. Task 0 Step 4 re-verifies it |

## Activation needs at `1b04cb05`

Method: each `SL-` row's `status:` in `git show 1b04cb05:docs/roadmap.md`, under its `id:`
line, and its merge commit from `git log origin/main --grep='SL-<n>\b'`. Each record's
`status:` is read from its own file.

| `PL-1544` need | State | Evidence |
|---|---|---|
| 1 `RL-1521` | MET | `status: active` |
| 2 `SL-1526` | MET | `closed`; `4af5997e` #1284 |
| 3 `SL-1387` | MET | `closed`; `e40ab532` |
| 4 `SL-1388` | MET | `closed`; `84ff9f0b`; `backend/src/app/api/dislocation_runs.py:87` |
| 5 E1 `SL-1503` (SL 9565); E3 `SL-1389` | MET | `closed`; `1b04cb05` #1285, `backend/src/app/api/models.py:1257`; `closed`, `db0642c4` |
| 6 `SL-1390` | MET | `closed`; `3065770c` #1279 |
| 7 `SL-1391` | MET | `closed`; `a9ef6777` #1206 |
| 8 `SL-1256` | MET | `closed`; `dfddfad8` |
| 9 `SL-1409` | MET | `closed`; `cdaaa573`. The Task 0 query is re-run at dispatch |
| 10 `SL-1430` | MET | `closed`; `5351f116` |
| 11 `SL-1448` | MET | `closed`; `680fb9ac` |
| 12 `SL-1472` | MET | `closed`; `7e3a4803` |
| 13 `FD-1416` fixed | MET (the fix) | `SL-1529` `closed`; `e3a98c97` #1276. The closing act on the finding is owed (Global Constraints row above) |
| 14 `FD-1244`, `FD-1245` ruled | MET (ruled) | `RL-1524` `status: active`. Its binding on this plan is discharged by §"D4" |
| 15 `FD-1494`, DP-b4 | MET | on `main`; this slice fixes it |
| 16 DPs ruled | MET | `PL-1544` Amendment 1 |
| 17 the lead's go | GIVEN, conditional | the 23:18:17 entry, item 4: `SL-1527` authors now; its activation and gate wait for the row below |
| 18 `SL-1340` | MET | `closed`; `a3572d1a` #1263 |
| **new: DP-D4 ruled** | **MET** | (a), the 23:18:17 entry, item 1 |
| **new: this file and the WF-699 D4 T-text (working id RL 9701) minted** | **OPEN** | the next docs PR, ahead of `SL-1527` (the 23:18:17 entry, item 4) |

## Decision points

| # | Question | Options | Recommendation | Owner | Blocking |
|---|---|---|---|---|---|
| DP-D4 | Which input does D4's fixed `monotone` property sweep? | (a) `bonus_malus` over the NCD ladder; (b) `driv_age`, WF-699-literal. Both were drafted in full (`cf2d31a4`) | **(a)** | the maintainer (by delegation) | **RULED (a)**, 2026-10-11 23:18:17 BST, with a WF-699 D4 T-text (item 2) |

## Tasks

Each task runs inside `SL-1527` and is added to `PL-1544`'s Tasks.

**Task 0, added Step 6.** Quote DP-D4's ruling verbatim in the ledger, and quote `D4_PROPERTY`
as written in this file. Check that the WF-699 D4 T-text is on `main`: `git grep -n 'premium
increasing in bonus_malus over the NCD ladder' -- docs/workflows/WF-00699-*.md` prints its
line. If it does not: STOP to the lead.

**Task 1, added test.** `test_the_d4_property_does_not_depend_on_the_fit` (§"D4" item 6).
Also, in `test_wf699_journey_runs_end_to_end`: D4 fails with the declared name and two adjacent
grid values, and passes after D5. Write both red first, with the rest of Task 1.

**Task 2a (new, between Tasks 2 and 3): the NCD ladder over HTTP.** In `journey.py`: create the
`ncd-ladder` rate table and the sub-graph (`POST /sub-graphs`, then `/versions`), keyed on
`bonus_malus` with the demo bands of §"D4". Mount it at B7 by exact pin, and wire its factor
into the premium. Assert B7's check (*"inlined at compile"*). Commit
`feat(examples): WF-699 B7, the NCD ladder sub-graph over HTTP`.

**Task 3 Step 2, replaced D4–D5 clause.** D4 writes the defect (the 100–149 band set to 0.90, §"D4"), runs the suite, and asserts the failure. D5 restores the band, recompiles, re-runs
and asserts the pass. Item 5's STOP applies at D1–D2 and after D5.

**Task 6, added.** The README's machine-requirement sentence, measured on the Acceptance 5 run.
The honesty text of `PL-1577` Task 3.

## Acceptance Standard

Each item is checked by a command run from the repository root on `SL-1527`'s slice head. These
items are added to `PL-1544`'s Acceptance Standard, and they replace Acceptance 3's D4 clause.

1. **The property is fixed.** `git grep -n 'D4_PROPERTY' -- examples/fremtpl2/journey.py`
   shows one constant that equals the declaration in §"D4". `uv run pytest -q
   backend/tests/test_wf699_journey.py -k does_not_depend_on_the_fit` passes, and its red
   (seen first) is recorded in the ledger.
2. **D4 fails deliberately, then D5 passes.** `uv run pytest -q
   backend/tests/test_wf699_journey.py` passes, and asserts: D1–D2's suite run includes
   `D4_PROPERTY` and passes; D4's run reports that property `failed`, with `grid:
   "uniform+sampled"` and two adjacent grid values; D5's run passes. A run in which D4 reports
   no `monotone` failure fails the test (`RL-1524` §"Acceptance").
3. **Band and spacing.** The ledger states the swept range, the spacing `(upper − lower) / 4`,
   and the inverted band's edges, and shows that the band is wider than the spacing.
4. **The ladder is built over HTTP.** `git grep -n -E 'sub-graphs' --
   examples/fremtpl2/journey.py` shows the create and version calls. B7's check passes in the
   journey test.
5. **The journey test's seed is 20,000 rows and it ran.** The ledger shows the test's seed
   size and the gate's pytest line for `test_wf699_journey.py` as passed, not skipped.
6. **Honesty text** (`PL-1577` Acceptance 4). `git grep -n -i 'sample' --
   examples/fremtpl2/README.md examples/fremtpl2/journey.py` shows *"20,000-policy sample"*
   with `PL-1574` and `FD-1576` named.
7. **The machine-requirement sentence.** `examples/fremtpl2/README.md` states the measured
   requirement from the Acceptance 5 run, with its tree and time. The ledger shows how it was
   measured.
8. **This file is consistent.** `python3 scripts/audit-docs.py` on the tree that mints it is
   clean apart from the working-id check before the mint.

## Self-review

1. **The 19:07:08 forward, clause by clause.** *"states, before building, which property it
   declares for D4 and why"*: §"D4", the declaration and its intent. *"as a fixed
   declaration (never derived from the fit)"*: items 1 and 6, Acceptance 1. *"deliberate and
   reproducible"*: item 2 and the defect row.
2. **`RL-1524`'s binding.** *"state the demo data's inverted band and the grid spacing"*: the
   range, spacing and defect rows, Acceptance 3. *"no `monotone` failure at D4 is the
   observable breach"*: Acceptance 2.
3. **The lead's list.** `PL-1577` Task 3 text: Acceptance 6. The README machine-requirement
   sentence: Acceptance 7, quoted from 16:37:21 item 3. The journey seed size: 20,000, with the
   floor. Global Constraint 2's HOLD text: its row. The moot B7 contingency: its row. Both
   DP-D4 variants were written in full (`cf2d31a4`), and (a) is kept as ruled. The NCD ladder's builder is named (Task 2a).
4. **Nothing was picked silently.** DP-D4 was drafted open, with a recommendation, and ruled by the maintainer (by delegation). The `@4` reading is
   flagged for the lead.
5. **What was not executed.** No code or test was run. The citations were read at `1b04cb05`.
   No fit was read.
