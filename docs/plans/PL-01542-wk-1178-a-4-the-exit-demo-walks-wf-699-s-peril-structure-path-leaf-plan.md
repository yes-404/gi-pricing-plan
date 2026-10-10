---
id: PL-1542
family: plan
kind: leaf
title: WK-1178 — A-4, the exit demo walks WF-699's Peril Structure path (a severity GLM, the AD Peril Structure reconciled and approved, B4's model_call, the C1 pin): leaf plan
status: draft                  # draft → active → superseded | retired (§1.2a)
created: 2026-10-09            # original date 2026-10-05, set at the draft; minted 2026-10-09
owner: planner
tree: 137bc817ef1fb40ea57e9053e0ad40b73bdff3a8
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1371, FD-1209, FD-1374, RL-1263, RL-1343, SL-1409]
---

# PL-1542 — WK-1178: A-4, the exit demo walks `WF-699`'s Peril Structure path, leaf plan

*(Minted 2026-10-09 as PL-1542 from working id 9593, with its slice SL-1543 from working id 9594, in the G2-b batch mint PR; every citation of a minted id in this record is re-pointed, and quoted entries stay as quoted.)*

This plan is filed under working id 9593. Its `SL-` row under WK-1178 in
[`../roadmap.md`](../roadmap.md) is working id 9594, `draft`. Both ids were reserved by the
lead (`handover/eta.md`, 2026-10-05 16:46:27 BST, *"CONDITIONAL: Option A A-4, only if it needs
its own slice rather than amending PL-1525/9629"* [PL 9624 is PL-1525; PL 9629 is PL-1544]). **The planner took the "own slice"
branch.** §"Why A-4 is its own slice" gives the reasons. The lead was told at 16:48:17 BST.

It is the fourth of the four Option A build slices (A-1 to A-4). The maintainer ordered them
in the entry quoted in §"The decisions this plan rests on". The others are A-1 (SL-1462 /
PL-1461), A-2 (SL-1463 / PL-1464) and A-3 (SL-1466 / PL-1465), all working ids, planned in
parallel by other planners in this wave.

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended)
> or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`)
> syntax for tracking. The executor also binds `python-test` (the `req` marker, negative
> tests), `test-driven-development` (every acceptance item is seen red, by its cause, before
> the code that turns it green), `python-package` (the uv workspace, no pandas), `dev-commands`
> (the two-half gate, `uv sync --all-packages`, the demo command) and `git-hygiene`. Read
> [`README.md`](README.md)'s five unchecked conventions before the first step. The executor
> is spawned from `.claude/roles/executor.md`, model sonnet.

### Pre-mint delta, 2026-10-05

Edited 2026-10-05 from 18:39:52 BST (`TZ=Europe/London date`), before this plan's mint, by the
planner, on the lead's brief `~/gi-pricing-plan.local/handover/brief-capacity-fill-2026-10-05.md`
Part C. origin/main `116a0da6f63cd7733335d6c2c6975c219b4e0e3d` was merged in first (only the
generated `docs/INDEX.md` conflicted, and was regenerated). Nothing is re-decided here. What this
delta changed, each marked in place, nothing deleted:

1. **RL-1459's P3 and P4, applied byte for byte.** The authority is RL-1459 (working id,
   unminted; #1188 @`cc5d0d61`), §"The plan texts (P-texts)" (`:258-301` of the record at that
   head): P3 at `:284-289`, P4 at `:291-301`. `<RL>` inside a P-text is filled with `RL-1459`,
   as the record's `:25-27` says ("`<date>` and `<RL>` inside the T- and P-texts, which the
   applying slice fills"); it is re-pointed at the mint. P4 replaces its find string "through
   'then passes once approved.'", which in this file is the sentence across two lines of
   Acceptance 5 (the span below). Counts are exact-substring counts in this file (`grep -c -F`
   semantics), read before and after the edit:

   | P-text | Find string | Find before → after | New text before → after |
   |---|---|---|---|
   | P3 | the line `## Decision points` (an insertion after it; the line is kept) | 1 → 1 | 0 → 1 |
   | P4 | `` `test_wf699_journey.py` asserts that a version pinning an **unapproved** `` | 1 → 0 | 0 → 1 |
   | P4 span | the above, through "`PIN_NOT_APPROVED`, then passes once approved." | 1 → 0 | — |

2. **Activation needs 1 and 7 are ruled, not yet minted:** need 1 by RL-1538 (#1179), need 7
   by RL-1459 (#1188), each marked in its row. Both records stay needs until merged and minted;
   RL-1459's §"What it obliges" has this plan cite both.
3. **Serialisation.** This plan's write set has no path under `backend/src/` or `packages/`
   (§"Write set", "Not written"), so it shares no path with SL-1436 (PL-1435, #1193;
   `_model_call_handler`) or A-2 (#1178 @`176a6a75`). It follows both only through the chain:
   A-2 by activation need 3, and SL-1436 through A-3 (need 4), which serialises with it.

### Pre-mint delta 2, 2026-10-05

Edited 2026-10-05 from 19:08:28 BST (`TZ=Europe/London date`), before this plan's mint, by the
planner, on the lead's brief `~/gi-pricing-plan.local/handover/brief-pl9494-ruled-2026-10-05.md`
Part A item 2. Nothing is re-decided here; one need is added, marked in place, nothing deleted.
The authority is the maintainer's (by delegation) entry in
`~/gi-pricing-plan.local/channel/to-lead.md` headed *"2026-10-05 19:03:24 BST — PL 9494 (#1216 @b4e4fdf5): the order change, A-4's need, DP-1 and R-a all ACCEPTED; DP-1's helper is BORN IN A-2"*, items 1 and 2, read in full by
this planner. Verbatim:

> 1. ORDER: A-2 → A-3 → SL 9495 → A-4, ACCEPTED (the per-component limb needs A-3's _resolve_peril_components; it still satisfies after A-2 and before A-4). The need "PL 9649 merged" (ResolvedArtifact.factors): accepted.

> 2. A-4 (PL 9593 #1175) gains the need "SL 9495 merged": YES, a pre-mint planner edit.

1. **Activation need 4a, "SL-1541 merged"** (PL-1540, working ids, #1216, the compile
   completeness check), added to §"Activation needs" after need 4, and named in Task 0
   Step 1.

## Goal

The freMTPL2 demo walks `WF-699`'s **literal** Peril Structure path, so that G2 (*"`WF-699`
end to end"*) holds on the workflow's own text:

- the trigger, *"An approved Peril Structure exists and needs to become a price"*
  (`docs/workflows/WF-00699-approved-models-to-approved-rating-version.md:19`);
- the precondition, *"An `approved` Peril Structure with a passing reconciliation"* (`:28`);
- B4, *"Adds a `model_call` step referencing the Peril Structure, `mode: exact`, with an
  explicit feature map"* (`:59`);
- C1, *"declares the algorithm version and every pin: rate tables, peril structure, reference
  tables"* (`:70`).

Concretely, the seed fits a **severity GLM** on `freMTPL2sev` (`02` FR-111's severity
default: Gamma, log link, `weight = claim_count`). It builds the **AD Peril Structure**
(`frequency_severity`: slice (a)'s 7-factor frequency GLM × this severity GLM, `02` FR-188).
It runs the structure's **reconciliation** (FR-190) and gets it **approved through the
approval workflow**, which A-1's carry makes possible. Slice (a)'s algorithm gains B4's
`model_call` on the structure, combined with the seeded tables **as the double-count ruling
decides** (DP-A4-1). Slice (b)'s journey walks B4 and pins the structure at C1. The two
`SKIPPED` lines slice (b) prints for them (B4's `model_call` clause and C1′) are removed. The
golden quotes and every expected premium are re-derived under the ruled combination.

When this slice merges, G2 is met (PL-1544 Hand-off 6).

**Architecture:** no backend or `packages/` code. A-1 to A-3 build the engine paths: the peril
approval carry and resolver branch (A-1), GLM scoring through `model_call` (A-2), and Peril
Structure scoring (A-3). This slice is demo content and the journey only. Model and structure
creation stay in `examples/fremtpl2/model.py`, beside `fit_demo_models` and
`compare_and_approve`, because the seed calls platform services directly (`seed.py:run`,
`:279-288`). The algorithm change goes in slice (a)'s builder (`examples/fremtpl2/algorithm.py`,
PL-1525's new module). The journey change goes in slice (b)'s `examples/fremtpl2/journey.py`.

**Tech Stack:** Python 3.12, Polars, `glum` (through the platform's fit job), pytest, `httpx`
(slice (b)'s journey client).

**Spec, workflow and map plan:**
- [`../workflows/WF-00699-approved-models-to-approved-rating-version.md`](../workflows/WF-00699-approved-models-to-approved-rating-version.md)
  `:19`, `:28`, B4 `:59`, C1 `:70`, and C4/C5 (compile refuses an unapproved pin);
- [`../specs/02-modelling.md`](../specs/02-modelling.md): FR-111 (`:141`), FR-128 (`:182`),
  FR-188 (`:294`), FR-190 (`:296`), FR-191 (`:297`), FR-192 (`:298`);
- [`../specs/03-rating-engine.md`](../specs/03-rating-engine.md): FR-222 (`:108`), FR-237
  (`:134`), FR-247 (`:154`), FR-249 (`:156`);
- `docs/roadmap.md` G2 and the Exit demo row;
- `docs/plans/PL-01371-p2-scope-freeze-lane-loading-plan-every-remaining-slice-against-the-code-freeze-map-plan.md`
  §7 (exit demo (a) and (b)) and §5 rule 4 (serialisation).

All line cites are at `origin/main` `137bc817` unless a PR head is named.

## The decisions this plan rests on, quoted

**Option A**, the maintainer's entry headed *"2026-10-05 16:43:31 BST — THE MAINTAINER'S
DECISION (asked live): G2 takes OPTION A, WF-699's literal Peril Structure path is BUILT IN P2;
and the FD-1458 approval, now on the record"* (`channel/to-lead.md`), items 1, 3 and 4, verbatim:

> 1. Four serial build slices under WK-1178, as sized: A-1 FD 9995 in full (the peril approval carry plus the _Resolver peril branch; it flips PL 9683's Acceptance 7); A-2 GLM via model_call (FD 9605); A-3 Peril Structure scoring (compile resolves and maturity-checks the component models; the runtime calls assemble_risk_premium, fixing the bare KeyError on payload["fit_result"] at runtime.py:540); A-4 the demo scope on PL 9624/PL 9629 (a severity GLM, the peril structure, reconcile, approve, the B4 model_call, the C1 pin). About 5 executor-days likely (3.5–8), a chain after PL 9683 and PL 9649.

> 3. Planning starts now: leaf plans for A-1..A-4, red first, with contention against the in-flight plans.

> 4. The DOUBLE-COUNT design point (A1 seeds tables from the AD frequency model while B4's model_call scores a Peril Structure containing it, so the factor effects may count twice; WF-699 does not say how they combine) needs a DM's options and a recommendation, ruled BEFORE A-4's plan activates.

The entry is a local channel entry (RFC-777). It is quoted here so the plan carries it. Its
item 5 (the fit risk, *"3 lanes every day"*) is this plan's §"Size" constraint.

**The sizing this plan follows**: `handover/sizing-g2-peril-path-2026-10-05.md` §2, the A-4
row (local memo; its figures are 0.75 / 1 / 2 executor-days best / likely / worst).

### Why A-4 is its own slice, not edits to PL-1525 and PL-1544

The brief asked the planner to decide this first. Item 1's *"the demo scope on PL-1525/PL
9629"* is read as **the demo scope those plans own, extended by a follow-on slice**. It is not
read as an order to edit them. If it was meant as an order to edit them, this plan is withdrawn
and its content folds into both. The reasons:

1. **Dependencies.** PL-1525's only build need is the FD-1357 fix, and that need is met.
   A-4 needs A-1, A-2 and A-3 merged, and the double-count ruling. If A-4 were folded into
   PL-1525 or PL-1544, both would wait behind PL-1429, then PL-1471, then the whole A chain.
   As a separate slice, PL-1525 and PL-1544 have no plan dependency on the A chain. Under
   RL-1445's same-Work rule they can then run beside it, and item 5's 3-lane fit needs that
   parallelism.
2. **Ruled decision points.** PL-1525's DP-a0 is ruled *"do NOT adopt S3's model_call fixture
   (a GLM cannot be scored via model_call on main)"*. Its DP-a2 (the base rate) is also ruled.
   Folding B4 into PL-1525 would reverse a ruled DP in a draft plan, which the planner may not
   do (prep-wave Common rule 6). A follow-on slice adds the `model_call` once A-2 makes it
   possible, and the ruling (DP-A4-1) decides its form.
3. **Freezing.** PL-1525 and PL-1544 can mint now with their scope unchanged. This plan stays
   `draft` while DP-A4-1 is open.
4. **Write set.** A-4 edits the same files as both plans. It must therefore run after both
   anyway, which is the natural order for a delta slice.

**Cost:** one more plan and one more slice audit, and the golden quotes are re-derived twice
(once in slice (a), once here). The sizing memo's A-4 figure already includes the
re-derivation.

## Status

`draft`. **DP-A4-1 (the double count) is open and blocking.** The maintainer (by delegation)
rules it on the decision-maker's memo, before this plan activates (item 4). DP-A4-2 and DP-A4-3
are open and do not block planning. The plan moves to `active` only through a separate
activation PR, after every activation need below holds. That PR carries the `SL-` row's
status flip and this plan's.

### Activation needs, in order

| # | Need | Why | State at `137bc817` (2026-10-05 16:54 BST) |
|---|---|---|---|
| 1 | **DP-A4-1 ruled** (the double count; item 4) | Task 3's algorithm form and Task 4's expected premiums | memo by dm-doublecount, local (`handover/dp-memo-doublecount-2026-10-05.md`), not ruled. *(Pre-mint delta 2026-10-05, RL-1459; see §"Pre-mint delta, 2026-10-05". Ruled (B1) by RL-1538, #1179, unminted.)* |
| 2 | **A-1 merged** (SL-1462 / PL-1461, working ids): the peril approval carry and the `_Resolver` peril branch (FD-1456, working id, #980) | Task 2's approval moves the structure to `approved`; Task 3's C1 pin resolves at compile | plan in preparation. On `main`, `decide_request`'s fan-out has no peril branch: *"a Peril Structure and a Rating Version each gain one with the slice that builds them, and until then their requests decide without an artifact to move"* (`backend/src/app/api/approvals.py:537-538`, fan-out `:540-571`) |
| 3 | **A-2 merged** (SL-1463 / PL-1464): GLM scoring through `model_call` (FD-1458, working id, #1172) | B4 scores GLM components | plan in preparation. On `main`, `_model_call_handler` refuses a GLM: the `else:` at `packages/pricing-core/src/pricing_core/rating/runtime.py:568-579`, *"predict_glm has no such fallback"* |
| 4 | **A-3 merged** (SL-1466 / PL-1465): Peril Structure scoring | B4's `model_call` on `peril_structure_ref` | plan in preparation. On `main`, `handler` reads `payload["fit_result"]` (`runtime.py:539`), which a structure payload does not carry; `assemble_risk_premium` (`pricing_core/modelling/perils.py:104`) has one production caller, `_reconcile` (`backend/src/app/worker/model_handlers.py:1486`) |
| 4a | **SL-1541 merged** (PL-1540, working ids, #1216): compile refuses a `model_call` whose `feature_map` misses an input its pinned model needs, per component for a Peril Structure *(added 2026-10-05, pre-mint delta 2; the entry headed "2026-10-05 19:03:24 BST — PL 9494 (#1216 @b4e4fdf5): the order change, A-4's need, DP-1 and R-a all ACCEPTED; DP-1's helper is BORN IN A-2", item 2)* | the order is A-2 → A-3 → SL-1541 → A-4 (the same entry, item 1). B4's `model_call` on the structure is compiled under that check, so its `feature_map` must cover every component's inputs | plan `draft`, #1216, unminted |
| 5 | **Exit-demo slice (a) merged** (SL-1526 / PL-1525, #1161) | the builder, banded factors and golden quotes this slice extends | draft |
| 6 | **Exit-demo slice (b) merged** (SL-1527 / PL-1544, #1164) | the journey and its two `SKIPPED` lines this slice removes | draft |
| 7 | DP-A4-2 and DP-A4-3 ruled | Tasks 1 and 2 | open. *(Pre-mint delta 2026-10-05, RL-1459; see §"Pre-mint delta, 2026-10-05". Ruled by RL-1459, #1188 @`cc5d0d61`, unminted.)* |
| 8 | The lead's go, in an activation PR | — | — |

PL-1429 (#1140) and PL-1471 (#1152) are not needs of this slice directly. A-1 to A-3 follow
them, so they are met when need 2 is met.

## Acceptance Standard

Each item is checked by a command run from the repository root on the merge tree. "Red first"
means the named test was run and failed **for the stated cause** before the code that turns it
green ([`README.md`](README.md) rule 2). Each red is recorded in the slice's ledger, with the
failure line as printed. Item numbers are referred to by Tasks.

1. **A severity GLM is fitted and approved** (`02` FR-111, FR-188). The seed fits a GLM with
   response type `claim_severity` (`model_schema/modelling.py`, `ResponseType.CLAIM_SEVERITY`),
   family `gamma`, link `log`, `weight = claim_count`, `peril="AD"`, on the policies with at
   least one claim, using `freMTPL2sev`'s claim amounts (`seed.py:109-119` loads them today
   and sums them per `IDpol`). It is approved through `compare_and_approve`'s path
   (`examples/fremtpl2/model.py:254`). `test_seed_fits_and_approves_a_severity_glm` in
   `backend/tests/test_demo_peril_structure.py` asserts each of these fields on the persisted
   model. Red first: on the base tree no `claim_severity` model exists in the seed.
2. **The AD Peril Structure exists, reconciles and is approved through the workflow**
   (FR-188, FR-190, FR-191). One `PerilComponent` (`model_schema/perils.py:214`) with
   `method=frequency_severity`, `frequency_model` = slice (a)'s frequency GLM,
   `severity_model` = item 1's model, and its `large_loss` treatment as DP-A4-3 rules. The
   reconciliation runs as the `PERIL_STRUCTURE_RECONCILE` job (`platform/jobs.py:69`; handler
   `_reconcile`, `worker/model_handlers.py:1348`), passes within the declared tolerance, and
   is persisted. `GET /api/v1/peril-structures/{id}` returns it (FR-192). The structure is
   submitted (`submit_for_review`, `platform/perils.py`) and approved by
   `approval_service.decide`, and **A-1's carry**, not a direct status write, moves it to
   `approved`. Tests: `test_the_ad_peril_structure_reconciles` and
   `test_the_ad_peril_structure_is_approved_through_the_workflow`, which asserts the approval
   event, the decision and the status. **Negative:** a grep shows no direct status write in
   `examples/`. The command `git grep -n -E 'PerilStructureStatus\.APPROVED|status *= *["'"'"']approved' -- examples/`
   prints nothing.
3. **B4: the algorithm has a `model_call` on the structure** (FR-222, `WF-699` `:59`). Slice
   (a)'s builder emits one `model_call` step with `peril_structure_ref` set, `mode: exact`,
   and an explicit feature map naming every model feature. It combines that step with the
   seeded tables **in the form DP-A4-1 rules**. `test_fremtpl2_algorithm.py` gains
   `test_b4_model_call_references_the_peril_structure`. Slice (a)'s reads ⊆ consumes test
   (FD-1374's interim guard) and its extractor-vs-engine cross-check pass unchanged on the new
   algorithm. Every declared output stays `money_minor` while the `RL-1343` fix is unmerged.
4. **The premium is the ruled combination, checked against an independent computation.**
   Under DP-A4-1 (B), mechanism B1 (the memo's recommendation; Task 3 gives the form for each
   option):
   - with unedited tables, `risk_premium_minor` equals the structure's prediction for the row
     (frequency × severity from `predict_glm` on each component, rounded once as FR-250's
     provisional convention says);
   - with one seeded cell edited, `risk_premium_minor` equals that prediction × (edited cell
     ÷ seed-origin cell) on rows in that cell, and the prediction elsewhere.

   The expected values are computed in the test from `predict_glm` and the table cells. They
   are never read back from the engine. `test_premium_is_the_ruled_combination` checks this
   on at least 5 rows, one of them in the edited cell. Red first: on the base tree (slice
   (a)'s algorithm) the unedited-table assertion fails, because the premium is
   `base × Π relativities`, not the structure's prediction.
5. **C1 pins the structure, and compile refuses it unapproved** (FR-237, `WF-699` `:70`,
   C4). In the journey's C1 request, `pins` carries the structure's `ArtifactRef` and the
   echo shows it. `test_wf699_journey.py` asserts C4 live by RL-1459 item 6: after a later version of a component model is approved (superseding the earlier one), a version pinning an `approved` structure composed over the superseded version fails compile with `PIN_NOT_APPROVED` naming the component. **That structure has its own slug**, not an earlier version of the demo structure's slug: approving a later version of a structure supersedes the earlier one (PL-1461 DP-2 (a)), and compile would then refuse the structure itself before reaching its components. The main path then pins the demo structure, composed over the current approved versions, and compiles.
   This is the journey's view of A-1's discharge test, not a second copy of it.
6. **The two `SKIPPED` lines are gone.** `git grep -n -E 'SKIPPED (C1′|B4)' -- examples
   scripts backend/tests` prints nothing. The journey test asserts that B4 and C1′ are walked,
   no longer that they are skipped. Red first: slice (b)'s test asserts the skips, so it goes
   red on the new journey until updated, and that red is recorded.
7. **One command, timed.** `uv run python scripts/demo.py --journey wf-699 --rows 20000` exits
   0 on the slice head. It prints a B4 line and a C1 line naming the structure's ref. It is
   run once, alone on the box with no gate slot held. Its elapsed time is recorded next to
   slice (b)'s recorded time, so the severity fit's added cost (item 5's risk) is measured.
8. **The gate.** Both halves green on the slice head, through the gate-runner holding a slot
   (`RL-1263`; one full gate at a time). `generate-contracts.py --check` rc 0.
   `audit-docs.py` red only on check 31 before the mint and clean after. `req-coverage.py`
   lists FR-188, FR-190 and FR-222 against the new tests.
9. **Scope held.** `git diff --stat origin/main...HEAD` touches only §"Write set"'s paths.
   In particular it touches nothing under `backend/src/`, `packages/` or `docs/specs/`.

## Global Constraints

- **Money is integer minor units, never float** (`CLAUDE.md` §7). Every premium in the tests
  is an `int` of pence/cents, or a `Decimal` in the rating path.
- **No pandas in new code** (`CLAUDE.md` §3). The severity aggregation stays in Polars, as at
  `seed.py:109-119`.
- **Modelling references a Dataset Version, never a Dataset** (`CLAUDE.md` §7). The severity
  GLM fits on the seed's validated Dataset Version.
- **No shape hand-written that `model-schema` defines** (`CLAUDE.md` §2). `PerilStructure`,
  `PerilComponent`, `GlmSpec` and the step types are imported, never re-declared.
- **FR-111's defaults, or an override with a recorded justification.** Severity → Gamma, log
  link, `weight = claim_count` (`02-modelling.md:141`).
- **No decimal output** while the `RL-1343` fix is unmerged (`PL-1371` §7's guard for slice
  (a), inherited by its builder).
- **Run nothing heavy beside a held gate slot** (`.claude/roles/executor.md`). One full gate
  at a time.

## Scope

### Requirement coverage, each id individually

| Spec | Ids | How |
|---|---|---|
| `02` | FR-111 (severity default) | Acceptance 1 |
| `02` | FR-128 (reconciliation accounts for the large-loss treatment) | Acceptance 2, DP-A4-3 |
| `02` | FR-188 | Acceptance 1, 2 |
| `02` | FR-190 | Acceptance 2 |
| `02` | FR-191 | Acceptance 2 |
| `02` | FR-192 | Acceptance 2 (the GET) |
| `03` | FR-222 | Acceptance 3 |
| `03` | FR-237 | Acceptance 5 |
| `03` | FR-247 | Acceptance 4 (under DP-A4-1 (B), `risk_premium` comes from the Peril Structure) |
| `03` | FR-249 | Acceptance 4: the AD component is available as an output (one peril, so it equals the total) |
| `WF-699` | trigger `:19`, precondition `:28`, B4 `:59`, C1 `:70`, C4 | Acceptance 2, 3, 5, 6 |

Each id is tested here only as the demo exercises it. A-1 to A-3 own the engine behaviour and
its unit tests.

### Premises, read at `137bc817` (each re-checked at Task 0)

- **P1. The seed calls platform services, not HTTP.** `seed.py:run` imports `app.platform`
  services at `:279-285` and `app.worker.tasks.execute_job` at `:288`. Models are created
  and approved in `model.py` (`fit_demo_models` `:194`, `compare_and_approve` `:254`), called
  from `seed.py:651-662`.
- **P2. No severity model exists.** `fit_demo_models` fits a frequency GLM (`peril="AD"`
  `:223`, `response_column="claim_count"` `:224`) and a frequency GBM (`:237-238`,
  `count:poisson`). `freMTPL2sev` is read only at `seed.py:109`.
- **P3. The Peril Structure routes and services exist.** These are `POST /peril-structures`
  (`create_peril_structure`), `POST …/{id}/reconcile` (202 + Job), `POST …/{id}/submit` and
  `GET …/{id}`, all in `backend/src/app/api/peril_structures.py`. The services are
  `create_structure`, `request_reconciliation`, `record_reconciliation`, `submit_for_review`
  and `load_structure`, all in `backend/src/app/platform/perils.py`. Approval goes through the
  generic `POST /approval-requests/{id}/decide` (`api/approvals.py:205-209`). Today nothing
  moves the structure on a decision (P-need 2).
- **P4. `PerilComponent` requires a `large_loss` treatment** (`model_schema/perils.py:214`,
  the `large_loss: LargeLossTreatment` field), and `frequency_severity` requires both model
  refs (its `_models_match_the_method` validator).
- **P5. No golden-quote or dislocation-baseline data file is committed.**
  `test_demo_rating_evidence.py:72-73` asserts the fixture's golden quote
  (`DEMO_PREMIUM_IN * 2`). Slice (a) replaces that. "Regenerated" in the sizing memo
  therefore means: **the expected values slice (a) and slice (b) commit in tests are
  re-derived here**, and no data file is involved.

### Write set, and its contention (`RL-1263`)

| Path | Change | Other slices touching it | Consequence |
|---|---|---|---|
| `examples/fremtpl2/model.py` | added: `fit_severity_glm`, `create_ad_peril_structure` (create, reconcile, submit, approve); edited: `fit_demo_models` or the seed's call order | **PL-1525** (`_create_factor`, `fit_demo_models`, `author_demo_rating_evidence`); **PL-1429** (#1140: `save_demo_algorithm`, `author_demo_rating_evidence`) | **serial**: both merge first (needs 5, 2) |
| `examples/fremtpl2/seed.py` | edited: `run`'s order, the severity fit and the structure after `compare_and_approve`, before the Rating Version | **PL-1525**; SL-1409 (merged) | serial (need 5) |
| `examples/fremtpl2/algorithm.py` | edited (PL-1525's new module): `build_fremtpl2_algorithm` gains B4's `model_call` and the DP-A4-1 combination | **PL-1525** creates it | serial (need 5) |
| `examples/fremtpl2/journey.py` | edited (PL-1544's new module): B4 and C1′ walked; the two `SKIPPED` branches removed | **PL-1544** creates it | serial (need 6) |
| `backend/tests/test_demo_peril_structure.py` | added: Acceptance 1, 2 and 4 | none | none |
| `backend/tests/test_fremtpl2_algorithm.py` | edited (PL-1525's): Acceptance 3 | PL-1525 | serial (need 5) |
| `backend/tests/test_wf699_journey.py` | edited (PL-1544's): Acceptance 5, 6 | PL-1544 | serial (need 6) |
| `backend/tests/test_demo_rating_evidence.py` | edited: the golden expectations slice (a) sets, re-derived (P5) | PL-1525, PL-1429; PL-1447 and PL-1520 name it | serial (needs 2, 5) |
| `examples/fremtpl2/README.md` | edited: the Peril Structure paragraph | PL-1525, PL-1544 (other paragraphs) | different paragraphs |
| the slice's ledger `docs/ledgers/LG-<n>`; `docs/INDEX.md` | added; regenerated | every PR | registry |

**Not written:** `backend/src/`, `packages/`, `frontend/`, `docs/specs/`, `scripts/demo.py`.
`scripts/demo.py` is not edited because slice (b)'s journey module prints the step lines, so
this slice changes the journey, not the script. If Task 0 finds the `SKIPPED` lines in
`demo.py` instead, `demo.py` joins the write set, serial with **PL-1454** (#1113), which edits
it. Spec text that DP-A4-1's ruling may add (the memo's §4 proposes `WF-699` and `03` text)
lands with that ruling's own record, not in this slice.

**Contention with other in-flight plans** (`gh pr list --state open`, 2026-10-05 16:5x BST;
each plan file's write-set rows grepped for `examples/fremtpl2`, `scripts/demo.py` and the
demo test files):
- **PL-1525 (#1161), PL-1544 (#1164):** same files, so serial; both are activation needs.
- **PL-1429 (#1140):** `examples/fremtpl2/model.py` and `test_demo_rating_evidence.py`, so
  serial. A-1 follows PL-1429, so this is met through need 2.
- **PL-1452 (#1138, WK-673 S3):** adds `examples/fremtpl2/rating/` (a new directory). It is
  disjoint from this write set, but WK-673 is a different Work. Under `RL-1263` it can run
  beside this slice. Re-checked at Task 0.
- **PL-1454 (#1113):** `scripts/demo.py` and `test_demo_command.py`. These are disjoint
  unless the conditional row above applies.
- **A-1 (PL-1461), A-2 (PL-1464), A-3 (PL-1465):** they write `backend/src` and
  `packages/`, which is disjoint from this write set. They are **plan dependencies**
  (needs 2–4). All four are WK-1178, and under RL-1445's same-Work rule (the 15:15:11 entry,
  item 2) a pair with a plan dependency does not run together. **The chain is serial:
  A-1 → A-2 → A-3 → A-4** (the sizing memo's critical path).
- PL-1528 (#1168), PL 9617 (#1165), PL-1471 (#1152), PL-1447 (#1145), PL 9609 (#1173),
  PL 9610 (#1170), PL 9662 (#1146), PL-1476 (#1131) and PL-1520 (#1051): no write-set row
  names these paths. (PL-1528 and PL-1520 mention one of the patterns in prose, not in a
  write-set row.)

### Size

Small to medium. The sizing memo's A-4 row gives **0.75 / 1 / 2 executor-days**. Six tasks
after the preconditions, and one full two-half gate (a gate slot under `RL-1263`). The
severity fit adds seed time on every demo run. Acceptance 7 measures it. On the critical path
this slice is last: it starts only after A-3 merges and DP-A4-1 is ruled (item 5's fit risk).

## Decision points

**Ruled 2026-10-05 by RL-1459.** DP-A4-1: `RL-1538` (B1). DP-A4-2 (c), the lead's, on the maintainer's (by delegation) 17:01:30 condition: the structure is approved through A-1's workflow service, never by SQL, and the journey's B4 `model_call` and C1 pin run over HTTP. DP-A4-3: the severity factors (a), the 7, the lead's; large loss **uncapped**, labelled in this plan and in the script as a simplification (no large-loss loading), the maintainer's. **Tolerance 0.05** on |ratio − 1|, requested by the seed. Task 0 Step 4's probe runs at the demo's full row count (and may also run at `--rows 20000`); the measured ratio is recorded verbatim in the ledger; if |ratio − 1| > 0.05, STOP to the maintainer with the ratio, never widened silently. The frequency GLM's `exposure_years` offset reaches B4 through its `feature_map`. WF-699 C4 is shown live under P4.

| DP | Question | Options | Recommendation | Owner | Blocks |
|---|---|---|---|---|---|
| **DP-A4-1** | **The double count** (item 4): A1 seeds tables from the AD frequency GLM, and B4's `model_call` scores a structure that contains that same GLM. How do they combine? | As dm-doublecount's memo (`handover/dp-memo-doublecount-2026-10-05.md` §2, local) states them: **(A)** the tables carry the price, and the `model_call` feeds a non-ladder technical output only. **(B)** the model is the price, and each seeded table enters as its ratio to its own seed origin, by **B1** (existing step types: two `table` steps per seeded table, the pinned version and its seed origin, with one `expression` step) or **B2** (a declared `relative_to: seed` field and a compile guard). **(C)** the tabled factors are neutralised inside the `model_call`'s feature map. **(D)** the workflow is silent and the actuary composes the two | **(B) by B1**, the memo's recommendation, for the memo's reasons: it is the only option under which FR-247 (*"`risk_premium` (from the Peril Structure)"*) and `WF-699` D7/D8 hold as written, and B1 needs no schema change, so it fits item 5's slack. Task 3 is written for B1, with the form under (A) beside it. Under B2 this plan is re-cut, because B2 adds `packages/` work | the maintainer (by delegation), on the memo (item 4) | activation need 1; Tasks 3, 4 |
| **DP-A4-2** | Where are the severity GLM and the Peril Structure created, reconciled and approved? | (a) **in the seed**, through platform services, as `compare_and_approve` does for the frequency GLM. The structure is a `WF-699` **precondition** (`:28`), not a step. (b) in slice (b)'s journey, over HTTP, as a phase before A. (c) the seed creates and approves it, and the journey also reads it once over HTTP (`GET /peril-structures/{id}`, FR-192) as a check before B4 | **(c).** (a) keeps `WF-699`'s A to E unchanged, matching where the workflow places the structure. The single GET shows the precondition over HTTP without adding a phase `WF-699` does not have. (b) would walk `WF-698`'s territory inside `WF-699`'s journey | the lead | Tasks 1, 2, 5 |
| **DP-A4-3** | The severity GLM's factors and the structure's `large_loss` treatment (FR-128) | Factors: (a) the same 7 factors as the frequency GLM (slice (a)'s bandings), (b) a smaller set, picked at Task 0 by fit statistics. Large loss: (x) none, uncapped, declared with a reason, (y) capped at a declared threshold, with the excess loaded | **(a) + (x)**, provided Task 0's probe shows the reconciliation passes within the declared tolerance on the holdout. If it fails, **STOP** and return to the lead with the measured gap. (y) is then the likely answer, but its threshold is an actuarial choice that should not be guessed. (a) reuses slice (a)'s bandings and keeps one factor list | the maintainer (by delegation) for the large-loss choice; the lead for the factor set | Tasks 1, 2 |

## Tasks

### Task 0: Preconditions (no code)

- [ ] **Step 1.** Confirm each activation need holds at `origin/main`: A-1, A-2, A-3, SL-1541
  *(added 2026-10-05, pre-mint delta 2)*, slice (a) and slice (b) merged; DP-A4-1 to DP-A4-3
  ruled. If any is unmet, STOP.
- [ ] **Step 2.** Re-check P1 to P5 at the dispatch tree, by symbol. Record any moved line in
  the ledger.
- [ ] **Step 3.** Find where slice (b) prints the two `SKIPPED` lines:
  `git grep -n SKIPPED -- examples scripts`. If any is in `scripts/demo.py`, add it to the
  write set and serialise with PL-1454 (§"Write set").
- [ ] **Step 4 (DP-A4-3 probe, local, small seed).** Fit the severity GLM and run the
  structure's reconciliation on a `--rows 20000` seed. Record the reconciled ratio, the
  declared tolerance and the pass or fail. If it fails, STOP (DP-A4-3).
- [ ] **Step 5 (DP-A4-1 (B1) probes, red-first, from the memo's "Not verified" list).** Check
  three things: (i) the Rating Version create path accepts two versions of one rate-table
  slug in `pins.rate_tables`; (ii) the JDM `table` node reads both; (iii) the engine's
  decimal division gives the ratio a golden test can reproduce. Any refusal is a STOP back to
  the maintainer (the memo's route to B2).

### Task 1: The severity GLM, red first (Acceptance 1; DP-A4-2, DP-A4-3)

- [ ] **Step 1.** Write `test_seed_fits_and_approves_a_severity_glm`. Run it and record the
  red (no `claim_severity` model).
- [ ] **Step 2.** In `model.py`, add `fit_severity_glm`. It builds the claims-only frame from
  the seed's per-policy `claim_amount_minor` and `claim_count` (Polars), with response
  `claim_amount_minor / claim_count`, `ResponseType.CLAIM_SEVERITY`, family `gamma`, link
  `log`, weight `claim_count`, `peril="AD"`, and the factors as DP-A4-3 rules. It fits
  through the platform's fit job, as `_fit` does (`model.py:169`), and approves it as
  `compare_and_approve` does.
- [ ] **Step 3.** Record the fit statistics (deviance, AIC, the factor list) in the ledger.
  Run the test green.

### Task 2: The AD Peril Structure, reconciled and approved, red first (Acceptance 2)

- [ ] **Step 1.** Write `test_the_ad_peril_structure_reconciles` and
  `test_the_ad_peril_structure_is_approved_through_the_workflow`. Run them and record the
  reds.
- [ ] **Step 2.** Add `create_ad_peril_structure` to `model.py`. It calls
  `perils.create_structure` with one `frequency_severity` component (slice (a)'s frequency
  GLM and Task 1's severity GLM, `large_loss` per DP-A4-3). It then calls
  `request_reconciliation`, runs the job through `execute_job` as the seed does, then calls
  `submit_for_review` and `approval_service.decide` with two principals who are neither
  submitter nor author. A-1's carry moves the structure to `approved`. **No direct status
  write** (Acceptance 2's negative grep).
- [ ] **Step 3.** Call it from `seed.py:run` after `compare_and_approve`, before the Rating
  Version. Write the structure's ref to the seed record if slice (b)'s journey reads refs
  from there (`last-seed.json`, slice (b)'s Task 5). Run green.

### Task 3: B4, the `model_call` in the builder (Acceptance 3; DP-A4-1)

- [ ] **Step 1.** Write `test_b4_model_call_references_the_peril_structure`. Run it and
  record the red.
- [ ] **Step 2.** In `build_fremtpl2_algorithm`, add one `model_call` step with
  `peril_structure_ref`, `mode: exact`, and a feature map naming each model feature
  explicitly. Combine it as ruled:
  - **(B), B1:** for each seeded table, add a second `table` step on its seed-origin version
    (03 §4.2's note: the lowest-numbered version whose `seeded_from` equals the pinned
    version's), and one `expression` step that multiplies the `model_call` value by
    Π(pinned ÷ origin). The ladder's `risk_premium_minor` reads the product, and the raw
    `model_call` value is a second declared output (FR-214, FR-249).
  - **(A):** the price path is unchanged (slice (a)'s `base × Π relativities`). The
    `model_call` feeds one declared non-ladder output.
- [ ] **Step 3.** Run slice (a)'s reads ⊆ consumes test and its cross-check unchanged. Both
  must pass. Run green.

### Task 4: The premium is the ruled combination (Acceptance 4)

- [ ] **Step 1.** Write `test_premium_is_the_ruled_combination`. Compute the expected values
  independently from `predict_glm` and the table cells. Run it on slice (a)'s algorithm and
  record the red.
- [ ] **Step 2.** Re-derive the golden expectations in `test_demo_rating_evidence.py` (P5)
  the same way, never by reading the engine's output back. Run green.

### Task 5: The journey walks B4 and C1′ (Acceptance 5, 6; DP-A4-2 (c))

- [ ] **Step 1.** Change `test_wf699_journey.py`: B4 and C1′ are asserted walked, and the
  unapproved-structure compile refusal is asserted with `PIN_NOT_APPROVED`. Run it and record
  the red.
- [ ] **Step 2.** In `journey.py`, add the `GET /peril-structures/{id}` precondition check,
  add the structure to C1's `pins`, and remove the two `SKIPPED` branches. Run green.
  Acceptance 6's grep prints nothing.

### Task 6: The demo run, the gate and the ledger (Acceptance 7–9)

- [ ] **Step 1.** Check `pgrep -af 'pytest|vitest|flock'` and both gate slots. Then run
  Acceptance 7's command once, alone on the box, and record the output lines and the elapsed
  time.
- [ ] **Step 2.** Run the gate through the gate-runner holding a slot. Record the exit-code
  table.
- [ ] **Step 3.** Write the ledger: every red as printed, the fit statistics, the
  reconciliation figures, Task 0's probes, and the timings.

## Hand-off

1. The lead mints PL-1542 and SL-1543 (working ids) in their own mint commit, after #1161 and
   #1164 have merged or minted. The plan dispatches only after §"Activation needs" hold, in a
   separate activation PR.
2. **Post-mint working-id sweep** (the lead's item 7a): re-point every working id this plan
   cites to its minted id where one exists at the mint tree: SL-1543, PL-1542, SL-1462,
   PL-1461, SL-1463, PL-1464, SL-1466, PL-1465, SL-1526, PL-1525, SL-1527, PL-1544, PL-1429,
   PL-1471, PL-1447, PL-1452, PL-1454, PL-1520, PL-1528, PL 9617, PL 9609, PL 9610, PL 9662,
   PL-1476, FD-1456, FD-1458, RL-1445. List the ids not yet minted in the mint PR body.
3. **The `roadmap.md` row conflicts textually with #1161.** Both insert `SL-` rows at the end
   of WK-1178's slice list. Whichever merges second re-merges `origin/main` and keeps both
   rows (no hand-resolved INDEX; `doc-index.py` regenerates it).
4. When this slice merges, **G2's `WF-699` literal path is complete**. The lead re-checks G2
   at the pre-exit-demo plan review (`CLAUDE.md` §14).
5. If DP-A4-1 is ruled B2, this plan is **superseded** by a new `PL-` (a replan; the lead's
   call). B2 adds a `packages/` write set and a contract regeneration, which this plan's
   scope excludes.

## Self-review

1. **Coverage of the maintainer's A-4 clause, item by item.** "a severity GLM": Acceptance 1,
   Task 1. "the peril structure": Acceptance 2, Task 2. "reconcile": Acceptance 2, Task 2
   Step 2, Task 0 Step 4. "approve": Acceptance 2 (through A-1's carry). "the B4 model_call":
   Acceptance 3, Task 3. "the C1 pin": Acceptance 5, Task 5. The sizing memo's "golden
   quotes … regenerated" is covered by Acceptance 4 and Task 4 Step 2 (P5 says what
   "regenerated" means here). Its "`SKIPPED` lines … go" is covered by Acceptance 6.
2. **Item 4 is honoured.** DP-A4-1 is activation need 1, and nothing in Tasks 1–6 runs before
   it is ruled (Task 0 Step 1).
3. **Red first.** Every acceptance item that tests behaviour names its red and its cause
   (1–6). Items 7–9 are measurements and gates.
4. **Contention** is listed against every open plan PR at 16:5x BST, by a grep of each plan's
   write-set rows, with the hits named.
5. **What was not executed.** No code or test was run (docs-only preparation wave). The
   premises are read at `137bc817` and re-checked at Task 0. A-1 to A-3's plans were not yet
   filed when this was written, so the needs name their working ids and the sizing memo's
   descriptions. The executor re-reads their merged text at Task 0.
6. **Type consistency.** `fit_severity_glm` and `create_ad_peril_structure` are defined in
   Tasks 1 and 2 and used with those names in Task 2 Step 3 and Task 5.
