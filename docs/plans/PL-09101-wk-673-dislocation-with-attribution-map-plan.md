---
id: PL-9101
family: plan
kind: map
title: WK-673 — Dislocation with attribution: map plan
status: draft                   # draft → active → superseded | retired (§1.2a)
created: 2026-09-28
owner: planner
tree: 6c6f4532c7d0ec65646225108f8cf9f8f570c746
phase: P2
work: WK-673
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-930, PL-1177, RL-881, RL-885, RL-1172]
---

# PL-9101 — WK-673 — Dislocation with attribution: map plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or executing-plans to implement each slice's leaf plan task-by-task. This is a **map plan**: it cuts the Work into slices and states each slice's scope, dependencies and gate. Each slice gets its own leaf plan before it starts. Every executor also binds `python-test` (requirement markers, negative tests) and `dev-commands` (the gate and its traps), and reads `docs/plans/README.md`'s unchecked conventions before its first step.

## Goal

Build `03` §3.9 end to end. A Dislocation Run re-rates a fixed portfolio Dataset Version
under a baseline and a candidate Rating Version **on the ZEN engine, in integer minor
units**. It reports the distribution of change and slices it by Factor and by ladder rung.
Where the two versions differ in more than one respect, it attributes the change to its
declared causes by **exact Shapley** with largest-remainder allocation, and the parts plus
the residual line reconcile exactly. The result is a persisted, citable artifact, and a
Rating Version's approval cannot proceed without it. The Work is done when FR-263, FR-264,
FR-265 and FR-266 are built and tested, FR-257's dislocation limb and FR-224's
approximation-mode gate refuse on missing or failing evidence, and `06` FR-364's
`structural_diff` kind has a verifier.

**Architecture.** A map plan, per `docs/process/delivery-process.md` §3. It is the same
relationship `PL-930` has to `PL-1177`. Slice 1 is spec only. Slices 2 and 3 are
`pricing-core` (the run, then the attribution), reusing WK-671's `score_batch` unchanged.
Slice 4 is the backend (the `dislocation.run` Job, the two routes, the persisted
artifact, the generated contract). Slices 5 and 6 are the approval gate, split at the one
point where this Work waits on WK-672 (DP-4 below).

**Tech Stack.** `pricing-core` (`score_batch`, `compile_bundle`, `load_bundle`), the ZEN
engine (`zen-engine` 0.53.0, `uv.lock:2704-2705`), Polars and DuckDB for aggregation
(`03` §8), `model-schema` for every shape, FastAPI + Celery for the 202-plus-Job route,
PostgreSQL for the artifact row, the content-addressed blob store for large parts.

**Spec.** [`../specs/03-rating-engine.md`](../specs/03-rating-engine.md) — §3.9 (FR-263,
FR-264, FR-265, FR-266), §3.1 (FR-224), §3.8 (FR-257), §3.11 (FR-273), §4.6
(`DislocationRun`), §4.8 (the frame contract, which reserves the portfolio frame for this
Work), §5.1 (the two `dislocation-runs` routes), §5.2 (`dislocate`, `attribute`), §9
(NFR-495, NFR-496); and [`../specs/06-governance.md`](../specs/06-governance.md) FR-364
(the evidence floor). Executors read the spec section their task cites as well as this plan.

## Acceptance Standard

Every command runs in the executor's own worktree (`env -C <worktree> …`, the team's
process-cwd rule), against the range `origin/main...HEAD`, never a tip SHA alone.

1. **Each of the six slices has its own leaf plan** under `docs/plans/`, `kind: leaf`,
   `work: WK-673`, each with its own acceptance standard (check 28) and the literal
   `## Goal` and `## Tasks` headings (check 37). Checked by
   `git grep -l '^work: WK-673' origin/main -- docs/plans` listing this plan and six leaf
   plans at the Work's close.
2. **Every id in scope has a slice that builds it and a test that names it.** FR-263,
   FR-264, FR-265, FR-266, FR-224, FR-257 (limb 2 only), NFR-495, NFR-496 and `06` FR-364
   each appear in `uv run python scripts/req-coverage.py`'s output with at least one test
   at the Work's close. FR-257's markers name the limb, as the register row for it
   requires.
3. **FR-266's amendment names exact Shapley**, largest-remainder allocation with ties in
   declared order, the isolated and declared-order cumulative views, the residual line and
   the above-six rule. Checked by reading `03` §3.9's FR-266 row after Slice 1 merges
   against the deputy's F3 decision quoted in `## Inputs` below, item by item.
4. **Reconciliation is proven on deliberately broken input.** Slice 3's test suite holds at
   least one test in which a plain-rounding allocator and one in which a Shapley value
   perturbed by one minor unit are each **refused** by the reconciliation check, and the
   ledger quotes that test failing before the check was written.
5. **The cost is measured, not asserted.** Slice 3's ledger records the median of N = 5
   timings of the 2^K subset re-rates for K = 3, 4, 5 and 6 on freMTPL2, with the 1-minute
   load at each run (< 12), the tree and the command. A proposed NFR from those figures goes
   to the deputy before Slice 3's PR is ready.
6. **`dislocation-run` is compared, not hand-authored.** After Slice 4,
   `grep -n '"dislocation-run"' backend/tests/test_contracts.py` prints one line, inside
   `COMPARED_SLUGS`, and none inside `ONE_SIDED_SLUGS`; `uv run python
   scripts/generate-contracts.py --check` exits 0.
7. **The approval gate refuses.** After Slice 5, rating-version submission refuses with
   `EVIDENCE_INCOMPLETE` on no Dislocation Run, on a run against a version that is not the
   current live one, on a stale candidate bundle hash, and (for an `approximation`-mode
   version) on a deviation above the declared threshold; each case is a named test.
8. **Every slice closes on the deputy's acknowledgement and a clean audit.** The deputy's
   merge acknowledgement is recorded on each slice's PR before the lead merges, and the
   slice's clean audit is filed. Per `CLAUDE.md` §13 a Slice closes on a clean audit and the
   lead's merge — no maintainer acceptance line is required for a slice, and none is to be
   waited on. (This is `PL-1070`'s item 11 form, applied to each of Slices 1–6.)
9. **This plan's own docs checks pass** on a detached copy of its committed tree —
   `python3 scripts/audit-docs.py`, `python3 scripts/doc-id.py check`,
   `python3 scripts/doc-index.py --check`, `python3 scripts/register-lint.py` — with rc,
   the `FAILED (n)` line or "All checks passed.", and the `DISCLOSED (…)` line quoted.
10. **The Work closes by `close-workstream`**, and its close is accepted by the maintainer
    with a dated line (by the deputy under the maintainer's delegation of 2026-09-28, while
    it lasts).

## Global Constraints

- **Money is integer minor units, or `Decimal` in the rating path, never float**
  (`CLAUDE.md` §7). Every premium, isolated, cumulative, Shapley and residual figure this
  Work persists is an integer minor unit; a percentage is a derived view, never the stored
  value a reconciliation is checked on.
- **Money crosses the ZEN boundary only as integer minor units** (`03` FR-273). This is
  why the reconciliation is on rounded minor units and not "Decimal through the engine";
  see premise (a).
- **`pricing-core` stays importable standalone** (`CLAUDE.md` §2). `dislocate` and
  `attribute` live in `pricing_core/rating/analysis.py` (`03` §5.2) and acquire no Job,
  no output location and no database, the rule `score_batch`'s own docstring states
  (`score.py:979-1001`). The Job handler owns those (Slice 4).
- **Nobody hand-writes a shape `model-schema` already owns** (`CLAUDE.md` §2). The first
  slice that returns a type defines it in `model-schema`; see "Deviation from the adopted
  cut" under Tasks.
- **No pandas in new code** (`CLAUDE.md` §3). Aggregation is Polars or DuckDB (`03` §8).
- **Requirement ids are cited individually**, never as a numeric range
  (`.claude/roles/planner.md`).
- **One slice at a time within the Work** (`delivery-process.md` §8).
- **The permission catalogue is unresolved (#855's finding).** `06` and the code each name 24
  permissions and share only 7. Until the decision-maker's permission-catalogue ruling
  (the catalogue RL, not yet a PR) merges, a slice that adds or checks a permission states in its
  leaf plan **which name it uses and why, and cites #855's finding by its minted id**. It never silently picks
  either side. This is the deputy's rule, 2026-09-28 at 14:52:49 BST, item 4 (b). In
  this Work only Slice 4 adds a permission check. Slices 5 and 6 go through the existing
  `rating:submit` check in `submit_for_review` and add no new name.

## Inputs

**The deputy's F3 decision, by the maintainer's delegation** — the channel entry headed
"Spike F3 DECIDED on its RS record", 2026-09-28 at 12:10:21 BST. Its operative items:

1. The attribution of record is **exact Shapley over the declared changes, for K ≤ 6**,
   exact as a rational (× K!), allocated to integer minor units **by largest remainder,
   ties broken in the declared change order**. Plain rounding is forbidden by name.
2. **Isolated and declared-order cumulative figures stay** as FR-266's views beside the
   Shapley figures, not as the attribution. FR-266 gains a dated amendment naming Shapley.
   The `attribution` list's `mean_change_pct` per change is the Shapley value. The
   interaction residual `total − Σ isolated` is its own line.
3. **Above K = 6**, the analyst groups the changes into ≤ 6 declared groups and Shapley
   runs over the groups. Where that is refused, the isolated-plus-cumulative method with
   its residual line is shown with the measured S and R beside it, labelled
   order-dependent, never presented as a decomposition.
4. **The hard gate carries into WK-673 as requirements:** reconciliation on the rating
   path's own arithmetic; tested on deliberately broken input; run on the ZEN engine.
5. **Cost:** WK-673 measures the N = 5 medians at K = 3..6 on freMTPL2 under load < 12
   and proposes an NFR. If K = 6 proves unacceptable, the slice brings the figure to the
   deputy or the maintainer before building the fallback.
6. **Also carried:** repeat runs of the six sets, other portfolios, and the unexplained
   per-policy maxima of 690 and 976 in the cap-free sets.

The criterion it was read against is the entry headed "F3 pass criterion RULED",
2026-09-28 at 11:39:35 BST. The research record is PR #833 (working id, head
`d663acd8`, not merged); the spike's code is at the salvage ref
`refs/salvage/2026-09-28/spike-f3` = `2699fc82`.

**The FR-266 open question is decided (b)** in PR #830 (head `3319b34f`, not merged), in
its `docs/open-questions.md` row and the `03` §10 mirror: "DECIDED 2026-09-28 — option
(b), exact Shapley with largest-remainder allocation (deputy, on spike F3's RS record)".

**`06` FR-364's `structural_diff` has an owner, WK-673** — decision E4 in #830's ruling
record, as a dated amendment at the end of `06` FR-364: at submission WK-673 persists
`03` FR-219's structural diff as a content-addressed blob and registers a verifier for
the `structural_diff` kind, before it wires FR-257's gate (RL-881). It supersedes
`RL-885`'s spec change 1 for `structural_diff` only; `RL-885`'s owner for
`dislocation_run` (WK-673) and its invariant stand.

**Precondition:** #830 merges before Slice 1's leaf plan is filed, because Slice 1 cites
its decided OQ row and its FR-364 amendment.

## Scope

### Requirement coverage — each id individually

| Id | Where | What WK-673 builds | Slice |
|---|---|---|---|
| FR-263 | `03` §3.9 | the Dislocation Run: distribution, averages overall and by segment, band counts, movers with drill-down, total change | 2 (compute), 4 (Job, routes) |
| FR-264 | `03` §3.9 | slicing by any portfolio Factor and by originating ladder rung | 2 |
| FR-265 | `03` §3.9 | a persisted, citable artifact referenced by the approval request | 4 |
| FR-266 | `03` §3.9 | the dated amendment (Slice 1); exact Shapley, isolated and cumulative views, residual line, above-six rule (Slice 3) | 1, 3 |
| NFR-495 | `03` §9 | identical bundle hashes + portfolio Dataset Version + spec ⟹ byte-identical run and attribution, across processes | 2, 3 |
| NFR-496 | `03` §9 | no double rounding; the attribution reconciles to the minor unit, asserted on every run | 2, 3 |
| FR-224 | `03` §3.1 | the `approximation`-mode gate: a run against the same version in `exact` mode inside the declared threshold | 5 |
| FR-257 | `03` §3.8 | **limb (2) only**: a Dislocation Run against the current live version over an agreed portfolio | 5 |
| FR-364 | `06` §3.3 | the `structural_diff` verifier (E4), and the floor wiring for `rating_version` | 5, 6 |

**Contracts and interfaces in scope:** `03` §4.6 `DislocationRun`; the two §5.1 routes
(`POST /api/v1/dislocation-runs` 202, `GET /api/v1/dislocation-runs/{id}`); §5.2's
`dislocate` and `attribute`; the portfolio frame's schema, which §4.8 reserves for this
Work; the three types §5.2 names and nothing defines (`DislocationSpec`, `BundleDelta`,
`Attribution`).

**Not in scope:** the Dislocation view at `/rating/:slug/v/:version/dislocation`
(`03` §5.3) is WK-675's; this Work ships no frontend. FR-257 limbs (1), (3) and (4) are
not this Work's: (1) is WK-672 Slice 3's (RL-1172 item 4), (3) is already enforced, and
(4) is `04`'s.

### Premises re-derived at this tree

| # | The premise | At `6c6f4532` | Status |
|---|---|---|---|
| a | "Decimal through the engine" makes the reconciliation exact | `03` §3.11 says the engine's arithmetic is exact inside and the Python binding returns `float`; FR-273 therefore carries money across as integer minor units. `_round_minor(raw: float, mode)` at `packages/pricing-core/src/pricing_core/rating/score.py:526` converts each engine result with `Decimal(repr(raw))` and quantizes to an integer. | **Does not hold.** Exact reconciliation is possible only on the rounded integer minor units. Slice 1's amendment says so. |
| a′ | (found while checking a) where the float enters | `score.py:527-531`'s docstring speaks of "the engine's float64 arithmetic"; `03` §3.11 says the engine is exact and the float is the binding's. | **A spec-vs-code-comment disagreement.** It does not change the conclusion. Recorded for Slice 1, which quotes both and brings it to the lead rather than editing either silently (`CLAUDE.md` §0). |
| b | `dislocation-run.schema.json` is hand-written and drift-exempt | `backend/tests/test_contracts.py:81`, `"dislocation-run": "later-phase — 03 rating"`, inside `ONE_SIDED_SLUGS` (`:67`) | reproduces; the label "later-phase" stopped being true when P2 opened — Slice 1 corrects it, as `PL-1177` Task 4 did for `regression-suite` |
| c | the contract has no Shapley, isolated, residual or minor-unit attribution fields | `attribution[]` holds `change`, `mean_change_pct`, `cumulative_change_pct` (numbers); no isolated, Shapley or residual field; no minor-unit figure per change | reproduces (there **is** a `cumulative_change_pct`, which the premise did not name) |
| c′ | (found) the contract and `03` §4.6 disagree | the contract has `job_id`, `by_ladder_rung[]` (`rung`, `contribution_pct`) and `errors[]`; §4.6's example shows none of them | Slice 1 reconciles §4.6 with the contract before adding fields |
| d | `DislocationSpec`, `BundleDelta`, `Attribution` do not exist | no definition under `packages/` or `backend/src` (`grep -rn` over both); `dislocate` and `attribute` are unbuilt (`03` §4.8's own sentence) | reproduces |
| d′ | (found) `attribute`'s published signature cannot be implemented | `attribute(changes: Sequence[BundleDelta], portfolio: pl.LazyFrame) -> list[Attribution]` takes no baseline, and a `CompiledBundle` is hydrated and never serialised (FR-243), so subset bundles cannot be made from compiled ones | Slice 1 amends the §5.2 signature, per DP-1's answer |
| e | RL-881: `EVIDENCE_FLOOR["rating_version"]` names three kinds nothing can verify | `packages/model-schema/src/model_schema/approvals.py:106` is `("structural_diff", "regression_run", "dislocation_run")`; `DEFAULT_POLICY`'s entry at `:254-259` ships the same three; `effective_evidence("rating_version")` has no caller in `backend/src` (the three callers are `modelling.py:1246`, `objectives.py:845`, `metrics.py:797`) | **reproduces** |
| e′ | RL-881: `06` §4.2's restatement of the floor omits `rating_version` | `06-governance.md:290-294` now names `rating_version` — `structural_diff`, `regression_run` and `dislocation_run` | **no longer holds**; fixed since RL-881 |
| f | WK-671's batch scoring is reusable unchanged | `score_batch(bundle, frame, *, chunk_rows, progress) -> pl.LazyFrame` at `score.py:979`; row-by-row, not vectorised (its docstring) | reproduces; the cost figure in DP-1's note follows from it |
| g | the Job kind exists | `JobKind.DISLOCATION_RUN = "dislocation.run"` at `model_schema/jobs.py:63`, routed to `JobQueue.COMPUTE` at `backend/src/app/platform/jobs.py:79`; no handler is registered | reproduces; Slice 4 registers the handler |
| h | FR-219's structural diff exists to persist | `diff_algorithms(old, new) -> AlgorithmDiff` at `model_schema/rating.py:565`; `RatingVersionEvidence.structural_diff_blob: str \| None` at `:124`; served by `rating_algorithms.diff_between` | reproduces; Slice 5 persists it |
| i | the submission path | `rating_versions.submit_for_review` at `backend/src/app/platform/rating_versions.py:214`, calling `approvals.submit` at `:239` | reproduces; WK-672 Slice 3 and this Work's Slice 5 both edit it |

### Risks

- **The 2^K cost may be large.** `score_batch` scores row by row. At NFR-493's floor of
  1 M risks per hour per worker, K = 6 over freMTPL2 is 64 × 678 013 = 43 392 832
  ratings, about 43 worker-hours. The baseline and candidate are the empty and full
  subsets, so a run with attribution adds 2^K − 2 re-rates to `dislocate`'s two. The
  subsets are independent and NFR-493 is linear in workers, so they fan out. Slice 3
  measures before anything is assumed; the deputy's item 5 governs what happens if K = 6
  proves unacceptable.
- **A subset bundle can be invalid.** A candidate step that reads an input only another
  candidate change introduces fails validation when mixed with baseline steps. DP-1's
  recommendation refuses such a subset by name and asks for the dependent changes to be
  grouped.
- **WK-672 edits the same function.** WK-672 Slice 3 adds limb (1) to `submit_for_review`;
  Slice 5 adds limb (2). One merge at a time; whichever is second merges `origin/main`
  first (never a rebase).

## Decision points

Kind, blocking status and resolver per `document-ids.md` §1.7. DP-1, DP-2 and DP-3 are
the maintainer's, resolved by the deputy under the maintainer's delegation of 2026-09-28.
DP-4 is slice design, the planner's own (`.claude/roles/planner.md`), decided here.

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-1 | How are the 2^K subset bundles built? | (a) At the **artifact level**: each subset is a synthetic Rating Version holding the baseline's pins with the subset's changes substituted, the algorithm composed step by step, then compiled by `compile_bundle` and hydrated by `load_bundle` — a real, hash-identified bundle rated by ZEN. (b) At the **JDM graph level**: patch the baseline's `to_jdm` graph with each change's node edits and hash it with `bundle_hash`. (c) **Whole-pin swaps only**: a change is a pin (model, rate table, reference table, algorithm version); edits inside one algorithm version count as one change. | **(a)**, at step granularity from `diff_algorithms` plus the pin diff. Every subset goes through the same compile and validation path a real version does, so a subset the engine cannot rate is refused by `validate_algorithm` rather than priced. (b) bypasses compile-time validation (FR-274, FR-275, FR-276). (c) cannot isolate the `min_premium` change `03` §4.6's own example attributes, which is the interaction case the F3 decision turned on. | decision point | yes — Slice 1 | |
| DP-2 | Where does a "declared change" come from? | (a) **Derived**: every differing pin and every changed step is one change. (b) **Declared**: the analyst lists the changes in `DislocationSpec`. (c) **Derived default, analyst regroups**: the server proposes the derived list; the analyst may merge entries into ≤ 6 named groups; the server checks the groups partition the full diff exactly. | **(c).** (a) alone exceeds K = 6 on any real rate change and gives the analyst no way to apply the above-six rule. (b) alone lets a change be left out, and then the parts cannot sum to the whole. (c) keeps both: the derivation guarantees coverage and the partition check guarantees each difference is counted exactly once. | decision point | yes — Slice 1 | |
| DP-3 | Where does FR-224's threshold live? FR-224 leaves it to "the Phase 2 slice that builds this": a maximum absolute percentage deviation at a declared portfolio quantile, recorded on the approval. | (a) A **workspace setting** (`07` FR-446, FR-448; the `workspace_settings` table). (b) A field on the `rating_version` **`ApprovalPolicy` entry** (`06` §4.2), so it can vary by `risk_tier` (`06` FR-365). (c) Declared **on the Dislocation Run's spec** by the submitter. | **(b).** An approval threshold is governance: a policy entry is audited when edited and sits under FR-364's floor rule. (a) resolves environment variable before workspace setting (FR-446), so a deployment variable could loosen an approval gate. (c) lets the submitter set their own bar. | decision point | yes — Slice 5 only | |
| DP-4 | Does Slice 5 wait on WK-672, or is `structural_diff` split out early? | (a) **Hold** the whole gate until WK-672 Slice 3 merges. (b) **Split**: Slice 5 builds `structural_diff`, FR-257 limb (2) and FR-224 as direct checks now; Slice 6 wires the `effective_evidence("rating_version")` floor union after WK-672 Slice 3. | **(b), decided.** See Rationale below. | scope | no | PL-9101 (planner, slice design) |

**DP-4's rationale.** Only the floor wiring needs WK-672. Wiring
`effective_evidence("rating_version")` while `regression_run` is unverifiable refuses
every submission (RL-881 reason 1), so that one step waits for WK-672 Slice 3's
`RegressionRun`. Nothing else in the gate does: the structural diff is already computed
(premise h), limb (2) is a direct check exactly as RL-1172 item 4 makes limb (1), and
FR-224 reads only this Work's own artifact. Holding them would leave the Work idle behind
another Work for no reason. The split costs one extra slice, and Slice 6 is small: it
replaces the two direct limb checks with the `verifiable` map plus
`effective_evidence` loop that `modelling.py:1238-1261` already uses.

## Tasks

A map plan's tasks are its slices. Each is scoped here and task-broken in its own leaf
plan.

**Deviation from the adopted cut.** The adopted cut put "the contract into
`model-schema`" in Slice 4. `dislocate` returns `DislocationRun` from Slice 2 onward, and
`CLAUDE.md` §2 forbids a second definition of a shape, so **each type is defined in
`model-schema` by the slice that first returns it**: `DislocationSpec` and
`DislocationRun` (without the attribution part) in Slice 2, `BundleDelta` and
`Attribution` in Slice 3. Slice 4 keeps what the cut gave it: registering the artifact for
generation into `docs/contracts/`, replacing the hand-authored file, and lifting the slug
into `COMPARED_SLUGS`.

### Sequencing

```
Slice 1 (spec) → Slice 2 (run) → Slice 3 (attribution + cost) → Slice 4 (Job, routes, artifact)
                                                                        → Slice 5 (structural_diff, limb 2, FR-224)
                                                                             → Slice 6 (floor wiring) ← WK-672 Slice 3 merged
```

One slice at a time. Slice 1 waits on #830's merge and on DP-1 and DP-2. Slice 5 waits
on DP-3. Slice 4 depends on the permission-catalogue ruling (the catalogue RL, not yet a PR; #855's finding). Slice 6
waits on WK-672 Slice 3.

### Slice 1 — Spec: FR-266's amendment, the hard gate as requirements, the contract and the types

**Spec only; no application code** except one test-file label. Scope:

- **FR-266's dated amendment**, carrying the deputy's items 1–3 above: exact Shapley over
  the declared changes for K ≤ 6; largest-remainder allocation to integer minor units,
  ties in declared order, plain rounding forbidden; isolated and declared-order
  cumulative as views; the residual line `total − Σ isolated`; the above-six rule with S
  and R printed and the "order-dependent" label. It states that **exact reconciliation
  holds on the integer minor units each rating returns through FR-273's boundary**, not
  on a Decimal carried through the engine (premise a).
- **The hard gate as requirements**, appended to `03` §3.9 with ids from the lead:
  reconciliation on the rating path's own arithmetic, per policy and at portfolio level;
  the reconciliation check proven on deliberately broken input; attribution runs on the
  ZEN engine through the ordinary compile path.
- **`03` §4.6** reconciled with the contract first (premise c′), then extended with the
  attribution fields in minor units: per change the Shapley, isolated and cumulative
  figures in minor units (percentages derived), the residual line, the method
  (`shapley` or the labelled order-dependent fallback), S and R where the fallback
  applies, and the declared groups.
- **`03` §4.8** gains the portfolio frame's schema.
- **`03` §5.2**: `DislocationSpec`, `BundleDelta` and `Attribution` defined, and
  `attribute`'s signature amended to take the baseline and the spec (premise d′), per
  DP-1 and DP-2.
- **`00` §2 glossary first** (`CLAUDE.md` §7): any new term — Shapley attribution,
  interaction residual, declared change group — is defined there before first use.
- **The `test_contracts.py:81` label** corrected to name `03` and WK-673, the slug left in
  `ONE_SIDED_SLUGS` until Slice 4.
- **Premise a′** quoted both ways and brought to the lead.

Depends on: #830 merged; DP-1 and DP-2 resolved. Gate: the full two-half gate, the four
docs checks on a detached copy, the ACK/audit item (acceptance item 8).

### Slice 2 — The Dislocation Run on ZEN, in integer minor units

`dislocate(baseline, candidate, portfolio, spec)` in `pricing_core/rating/analysis.py`:
two `score_batch` passes over the portfolio frame, joined per policy on integer minor
units; the distribution bands, averages overall and by declared segment, exposure and
policy counts per band, movers beyond the spec's thresholds (FR-263); slicing by any
portfolio Factor and by the first ladder rung at which the two premiums differ (FR-264);
the movers' identities kept for drill-down to a trace. `DislocationSpec` and
`DislocationRun` defined in `model-schema`. Tests carry `req` markers for FR-263, FR-264,
NFR-495 (a repeat run in a separate process is byte-identical) and NFR-496 (the totals
equal the sum of per-policy minor units, no second rounding).

Depends on: Slice 1. Gate: as Slice 1, plus the tests above.

### Slice 3 — Attribution: exact Shapley, largest remainder, the broken-input proof, the cost

`attribute` per Slice 1's signature: the declared changes derived and grouped per DP-2;
the 2^K subset bundles built per DP-1 and rated on ZEN via `score_batch`; exact Shapley
per policy as a rational × K!; largest-remainder allocation to minor units, ties in
declared order; the isolated and cumulative views and the residual line; the above-six
fallback labelled with S and R. `BundleDelta` and `Attribution` in `model-schema`.

- **Reconciliation asserted on every run**, per policy and at portfolio level, and
  **proven on broken input** (acceptance item 4).
- **The cost measurement** (acceptance item 5), and the proposed NFR to the deputy. If
  K = 6 is unacceptable, the figure goes to the deputy before any fallback is built.
- **The F3 carried items**: the six change sets repeated on the ZEN path; a second
  portfolio if one is available that is public (`.claude/CLAUDE.md` forbids real policy
  data in the semantic pass; this is a measurement, but the same care applies); the
  per-policy maxima of 690 and 976 explained or shown not to recur on ZEN.

Depends on: Slice 2. Gate: as Slice 2, plus the tests and the measurement.

### Slice 4 — Backend: the Job, the routes, the persisted artifact, the generated contract

The `dislocation.run` handler (premise g), owning the Job identity, the output location
and resumability that `score_batch` may not acquire; the subset re-rates fanned out
across workers. `POST /api/v1/dislocation-runs` (202 plus a Job) and
`GET /api/v1/dislocation-runs/{id}` (`03` §5.1), with RBAC and RFC 9457 errors. The
artifact persisted as a citable row, large parts as content-addressed blobs (FR-265).
`DislocationRun` registered for generation: `docs/contracts/` regenerated, the
hand-authored schema replaced, the slug moved from `ONE_SIDED_SLUGS` to `COMPARED_SLUGS`
(acceptance item 6), per `contract-guard`. The generated frontend client regenerates;
nothing is hand-written there.

**The routes' permissions (#855's finding).** Neither side names a dislocation permission at
`6c6f4532`:
- `06` §4.1's catalogue example has none, and it spells rating permissions on
  `rating_version:` and `rating_algorithm:`.
- The code's closed `Permission` enum has none either. It spells them `rating:read`,
  `rating:write` and `rating:submit` (`packages/model-schema/src/model_schema/permissions.py:47-49`),
  and it has `score:batch` (`:59`) for the batch re-rate a Dislocation Run performs.

Slice 4's leaf plan states the name each route checks and why, and cites #855's finding by its minted id. If
the catalogue RL has merged by then, it follows that ruling instead. A permission that grants a
new capability is a scope change for the deputy, not the slice's pick.

Depends on: Slice 3, and **the permission-catalogue ruling (the catalogue RL) merged**,
or else the statement above in its leaf plan. Gate: as Slice 3, plus
`generate-contracts.py --check`.

### Slice 5 — The approval gate, part one: `structural_diff`, FR-257 limb (2), FR-224

- **`structural_diff`** (`06` FR-364's E4 amendment): at submission, FR-219's diff
  persisted as a content-addressed blob into `RatingVersionEvidence.structural_diff_blob`
  and a verifier registered for the kind.
- **FR-257 limb (2)** on `submit_for_review`: refuse with `EVIDENCE_INCOMPLETE` unless a
  Dislocation Run exists whose candidate bundle hash equals the version's current one and
  whose baseline is the current live version. Tested on no run, a stale hash and a wrong
  baseline; its `req("FR-257")` marker names limb (2) only.
- **FR-224**: for an `approximation`-mode version, a run whose baseline is the same
  version in `exact` mode (built by DP-1's mechanism with `model_reference_mode` set to
  `exact`), refused above the threshold DP-3 places, naming the quantile and the observed
  deviation. FR-136's fidelity statement runs first as the cheap pre-check.

Depends on: Slice 4; DP-3 resolved. Not on WK-672 (DP-4). Gate: as Slice 4, plus the
refusal tests (acceptance item 7).

### Slice 6 — The approval gate, part two: the floor wiring

`submit_for_review` checks `policy.effective_evidence("rating_version")` against a
`verifiable` map — `structural_diff` (Slice 5), `regression_run` (WK-672 Slice 3),
`dislocation_run` (Slice 5) — in the pattern of `modelling.py:1238-1261`, replacing the
two direct limb checks. A workspace policy that adds a kind nothing can verify is refused
by name, never passed. Tested with a policy at the floor, a policy above it, and each kind
missing in turn.

Depends on: Slice 5 and **WK-672 Slice 3 merged**. Gate: as Slice 5.

## Self-review

**1. Spec coverage.** FR-263 → Slices 2, 4. FR-264 → Slice 2. FR-265 → Slice 4. FR-266 →
Slices 1, 3. NFR-495, NFR-496 → Slices 2, 3. FR-224 → Slice 5. FR-257 limb (2) → Slice 5.
`06` FR-364 → Slices 5, 6. §4.6, §4.8's portfolio frame, the §5.1 routes, `dislocate`,
`attribute` and the three missing types → Slices 1–4. The deputy's six F3 items → Slice 1
(items 1–4 as spec), Slice 3 (items 1–3 and 5–6 as code and measurement).

**2. Placeholder scan.** This is a map plan: each slice is a scope statement, not a task
list, and each leaf plan carries its own steps. No new requirement id is written here;
Slice 1's ids come from the lead.

**3. Consistency.** Every locator was read at `6c6f4532`, the tree in the header. Premises
a, a′, c, c′, d′ and e′ record where a premise did not reproduce or something new was
found.

**4. Rulings between sweep and filing.** Open PRs read: #830 (the decided OQ row and the
FR-364 amendment, cited under Inputs), #833 (the F3 research record, cited). Neither is
merged; Slice 1's leaf plan re-reads both at main.
