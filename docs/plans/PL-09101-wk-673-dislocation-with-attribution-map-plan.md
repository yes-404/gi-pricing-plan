---
id: PL-9101
family: plan
kind: map
title: WK-673 — Dislocation with attribution: map plan
status: draft                   # draft → active → superseded | retired (§1.2a)
created: 2026-09-28
owner: planner
tree: 19c395acad594d1b193da197461bec85201d2248
phase: P2
work: WK-673
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-930, PL-1177, RL-880, RL-881, RL-885, RL-1172, RL-1184, RL-1236, RS-1201, CR-1212]
---

# PL-9101 — WK-673 — Dislocation with attribution: map plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or executing-plans to implement each slice's leaf plan task-by-task. This is a **map plan**: it cuts the Work into slices and states each slice's scope, dependencies and gate. Each slice gets its own leaf plan before it starts. Every executor also binds `python-test` (requirement markers, negative tests) and `dev-commands` (the gate and its traps), and reads `docs/plans/README.md`'s unchecked conventions before its first step.

> **Revised 2026-09-29 22:56 BST by the planner, while `draft` and before acceptance, on the
> lead's instruction** (relaying the maintainer's to-lead.md entries of 2026-09-29 22:46:27 and
> 22:47:23 BST, which the planner read at source). The first draft was derived at
> `6c6f4532`. This revision re-derives it at origin/main `19c395ac`. It is a revision of a
> draft, not a replan of a frozen plan, so it is the same file. What changed, and why:
>
> 1. **F-W10-2 added as Slice 7** (FR-231's exposure-weight wiring). CR-1212 row L64
>    (CR-1212 at line 232) routed it to WK-673, and the finding resolutions were accepted at
>    `:275`. WK-675 Slice 5 depends on it. Slice 7 is appended rather than inserted so
>    Slices 1–6 keep the numbers other records already cite ("WK-675 S8 needs WK-673 S4").
>    It is sequenced straight after Slice 2. New DP-5 covers its one open design choice.
> 2. **DP-1, DP-2 and DP-3 are resolved.** The deputy's entry of 2026-09-28 14:05:30 BST
>    (quoted in `RS-1201`:263-292) is filed as the #845 ruling (the decision-maker's, working
>    id; **at the mint turn, each "the #845 ruling" here becomes its minted id, and that id
>    goes into `relates:`**). Its DP-1 conditions, DP-3's no-override rule and its five
>    named negative tests are carried into Slices 1, 3 and 5.
> 3. **The Shapley cost rule is replaced** by the 14:05:30 feasibility rule: measure first,
>    ladder replay as the primary route proven against re-rates, the estimated count shown
>    before launch, a sample never presented as exact, fallback trigger at K = 4, and the
>    figure going to the decision-maker. This changes Slice 3, acceptance item 5 and Risks.
> 4. **The hard-gate wording follows the deputy's 13:57:02 correction** (integer minor
>    units, as the rating path produces them). Premise a′ is resolved: the spec is right, and
>    Slice 1 corrects the docstring.
> 5. **Preconditions satisfied since the draft:** #830 merged (`RL-1184`, OQ-1187), #833
>    merged (`RS-1201`), the permission catalogue ruled (`RL-1236`; #855's finding is
>    FD-1197), and WK-672 Slice 3 merged (#886; WK-672 closed, CR-1243).
> 6. **Cross-Work dependencies re-derived** under the maintainer's 22:46:27 item 5 (CR-1212's
>    Work order relaxed to real dependencies). The only real WK-674 dependency is Slice 5's:
>    nothing can be `live` until WK-674 Slice 2's Deployment exists (premise j). The bare
>    "WK-674, then WK-673" order is lifted. The files shared with other Works are listed
>    under Sequencing, and those slices are serialised.
> 7. **Locators re-read at `19c395ac`**; main then moved to `97b15726` (#922's P2 dates,
>    #924's WK-674 SL rows, SL-1255 to SL-1260), which moves only roadmap lines (the WK-673 row cited in Self-review is re-read there) and gives
>    WK-674 Slice 2 its id, SL-1256, now cited. The header `tree:` is `19c395ac`, and the acceptance
>    wording aligned with `lead.md` rule 4 (the maintainer's MERGE-ACK).

## Goal

Build `03` §3.9 end to end. A Dislocation Run re-rates a fixed portfolio Dataset Version
under a baseline and a candidate Rating Version **on the ZEN engine, in integer minor
units**. It reports the distribution of change and slices it by Factor and by ladder rung.
Where the two versions differ in more than one respect, it attributes the change to its
declared causes by **exact Shapley** with largest-remainder allocation, and the parts plus
the residual line reconcile exactly. The result is a persisted, citable artifact, and a
Rating Version's approval cannot proceed without it. The Work is done when FR-263, FR-264,
FR-265 and FR-266 are built and tested, FR-257's dislocation limb and FR-224's
approximation-mode gate refuse on missing or failing evidence, `06` FR-364's
`structural_diff` kind has a verifier, and FR-231's rate-table diff carries the portfolio's
exposure weight behind each cell (F-W10-2).

**Architecture.** A map plan, per `docs/process/delivery-process.md` §3. It is the same
relationship `PL-930` has to `PL-1177`. Slice 1 is spec only. Slices 2 and 3 are
`pricing-core` (the run, then the attribution), reusing WK-671's `score_batch` unchanged.
Slice 4 is the backend (the `dislocation.run` Job, the two routes, the persisted
artifact, the generated contract). Slices 5 and 6 are the approval gate, split at the one
point where the first draft waited on WK-672 (DP-4 below; that wait is now satisfied).
Slice 7 is the backend wiring of FR-231's exposure weights through the portfolio frame
Slice 2 builds (F-W10-2).

**Tech Stack.** `pricing-core` (`score_batch`, `compile_bundle`, `load_bundle`), the ZEN
engine (`zen-engine` 0.53.0, `uv.lock:2763` at `19c395ac`), Polars and DuckDB for aggregation
(`03` §8), `model-schema` for every shape, FastAPI + Celery for the 202-plus-Job route,
PostgreSQL for the artifact row, the content-addressed blob store for large parts.

**Spec.** [`../specs/03-rating-engine.md`](../specs/03-rating-engine.md) — §3.9 (FR-263,
FR-264, FR-265, FR-266), §3.1 (FR-224), §3.8 (FR-257), §3.11 (FR-273), §4.6
(`DislocationRun`), §4.8 (the frame contract, which reserves the portfolio frame for this
Work), §5.1 (the two `dislocation-runs` routes), §5.2 (`dislocate`, `attribute`), §9
(NFR-495, NFR-496), §3.3 (FR-231, for Slice 7); and
[`../specs/06-governance.md`](../specs/06-governance.md) FR-364 (the evidence floor). Executors read the spec section their task cites as well as this plan.

## Acceptance Standard

Every command runs in the executor's own worktree (`env -C <worktree> …`, the team's
process-cwd rule), against the range `origin/main...HEAD`, never a tip SHA alone.

1. **Each of the seven slices has its own leaf plan** under `docs/plans/`, `kind: leaf`,
   `work: WK-673`, each with its own acceptance standard (check 28) and the literal
   `## Goal` and `## Tasks` headings (check 37). Checked by
   `git grep -l '^work: WK-673' origin/main -- docs/plans` listing this plan and seven leaf
   plans at the Work's close.
2. **Every id in scope has a slice that builds it and a test that names it.** FR-263,
   FR-264, FR-265, FR-266, FR-224, FR-257 (limb 2 only), FR-231 (F-W10-2's weight limb only),
   NFR-495, NFR-496 and `06` FR-364 each appear in `uv run python scripts/req-coverage.py`'s output with at least one test
   at the Work's close. FR-257's markers name the limb, as the register row for it
   requires.
3. **FR-266's amendment names exact Shapley**, largest-remainder allocation with ties in
   declared order, the isolated and declared-order cumulative views, the residual line and
   the above-six rule. Checked by reading `03` §3.9's FR-266 row after Slice 1 merges
   against the deputy's F3 decision quoted in `## Inputs` below, item by item, with its
   hard-gate wording read as the deputy's 13:57:02 correction states it (integer minor
   units, as the rating path produces them).
4. **Reconciliation is proven on deliberately broken input.** Slice 3's test suite holds at
   least one test in which a plain-rounding allocator and one in which a Shapley value
   perturbed by one minor unit are each **refused** by the reconciliation check, and the
   ledger quotes that test failing before the check was written.
5. **The cost is measured, not asserted, under the 14:05:30 feasibility rule.** Slice 3's
   ledger records the median of N = 5 timings of the real `score_batch` rate on freMTPL2,
   and of ladder replay and of the 2^K re-rates for K = 3, 4, 5 and 6, with the 1-minute
   load at each run (< 12), the tree and the command. Replay is proven equal to a true
   re-rate for every policy at K ≤ 3 and on a declared sample at K = 4–6, by a named test
   that is shown red on a deliberately wrong replay (the #845 ruling's *"a replayed v(S)
   that differs from a true re-rate for some policy, and is not recorded as falling
   back"*). The proposed dislocation-attribution NFR goes to the decision-maker before
   Slice 3's PR is ready.
6. **`dislocation-run` is compared, not hand-authored.** After Slice 4,
   `grep -n '"dislocation-run"' backend/tests/test_contracts.py` prints one line, inside
   `COMPARED_SLUGS`, and none inside `ONE_SIDED_SLUGS`; `uv run python
   scripts/generate-contracts.py --check` exits 0.
7. **The approval gate refuses.** After Slice 5, rating-version submission refuses with
   `EVIDENCE_INCOMPLETE` on no Dislocation Run, on a run against a version that is not the
   current live one, on a stale candidate bundle hash, and (for an `approximation`-mode
   version) on a deviation above the declared threshold; each case is a named test.
8. **Every slice closes on the maintainer's MERGE-ACK and a clean audit.** The MERGE-ACK
   is the dated to-lead.md entry `lead.md` rule 4 requires, given by the maintainer or on
   the maintainer's behalf and naming the PR's full head SHA, before the lead merges; the
   slice's clean audit is filed. Per `CLAUDE.md` §13 a Slice closes on a clean audit and the
   lead's merge — no maintainer acceptance line is required for a slice, and none is to be
   waited on. (This is `PL-1070`'s item 11 form, applied to each of Slices 1–7.)
9. **This plan's own docs checks pass** on a detached copy of its committed tree —
   `python3 scripts/audit-docs.py`, `python3 scripts/doc-id.py check`,
   `python3 scripts/doc-index.py --check`, `python3 scripts/register-lint.py` — with rc,
   the `FAILED (n)` line or "All checks passed.", and the `DISCLOSED (…)` line quoted.
10. **The Work closes by `close-workstream`**, and its close is accepted by the maintainer
    with a dated line (or on the maintainer's behalf, while that delegation lasts).
11. **The #845 ruling's negative tests exist and were shown red.** Slice 1's leaf plan names
    one test for each of: a subset bundle persisted as a Rating Version or visible in a
    version list; a subset that fails to compile and is skipped instead of failing the run
    by name; a regrouping that leaves a derived change out or puts one in two groups and is
    accepted. Slice 5 names one for FR-224's threshold resolved from an environment
    variable. Slice 3 names the replay-exactness test of item 5. Each ledger quotes its test
    failing on deliberately broken input.

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
  (`score.py:1011` at `19c395ac`). The Job handler owns those (Slice 4).
- **Nobody hand-writes a shape `model-schema` already owns** (`CLAUDE.md` §2). The first
  slice that returns a type defines it in `model-schema`; see "Deviation from the adopted
  cut" under Tasks.
- **No pandas in new code** (`CLAUDE.md` §3). Aggregation is Polars or DuckDB (`03` §8).
- **Requirement ids are cited individually**, never as a numeric range
  (`.claude/roles/planner.md`).
- **One slice at a time within the Work** (`delivery-process.md` §8). The maintainer's
  2026-09-29 22:46:27 BST entry runs Works in parallel lanes through a dated §8 amendment
  the lead files; it does not run two slices of one Work at once.
- **Permissions come from `RL-1236`'s catalogue** (`06-governance.md:253-300` at
  `19c395ac`; #855's finding is FD-1197, `docs/findings/register.md:184`). A slice that adds
  or checks a permission names the catalogue row it uses and cites FD-1197, and says whether
  it discharges it. A new permission lands with its `06` §4.1 row, its enum member and its
  check in one commit (CR-1247 Proposal 1 (c), lead verdict at its line 158). In this
  Work only Slice 4 adds a permission check (Slice 7 re-uses the diff route's existing
  one). Slices 5 and 6 go through the existing `rating:submit` check in `submit_for_review`
  and add no new name.

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
2026-09-28 at 11:39:35 BST. The research record is `RS-1201` (merged from #833 as
`122d6313`); the spike's code is at the salvage ref
`refs/salvage/2026-09-28/spike-f3` = `2699fc82`.

**Item 4's first bullet is corrected** by the deputy's entry of 2026-09-28 13:57:02 BST,
quoted whole in `RS-1201`:243-257: *"exact reconciliation in integer minor units, as the
rating path produces them"* — every attribution part, the residual line and the total are
integers taken from the engine's own `value_minor` outputs, summing exactly as integers,
per policy and at portfolio level, with no float summed after rounding. The broken-input
test and the "on ZEN, not a Polars mirror" requirement stand. Slice 1's FR-266 amendment
cites this line.

**Item 5 is amended** by the deputy's entry of 2026-09-28 14:05:30 BST, quoted whole in
`RS-1201`:263-292, into a feasibility rule: Slice 3 measures the real `score_batch` rate
first; evaluates **ladder replay** as the primary route (2 ratings per policy plus integer
arithmetic, where the declared changes are step-aligned), proven equal to a true re-rate
for every policy at K ≤ 3 and on a declared sample at K = 4–6, falling back to re-rates on
any mismatch, recorded on the artifact; shows the estimated rating count before launch;
never presents a sampled portfolio as exact Shapley; and brings the figure to the
decision-maker before any fallback if K = 4 does not fit. Exact Shapley (K ≤ 6) and
largest remainder stand as the method of record.

**DP-1, DP-2 and DP-3 are decided, and the §3.11-vs-docstring disagreement is resolved**,
by the same 14:05:30 entry, filed by the decision-maker as the #845 ruling ("Ruled — by
the decision-maker, 2026-09-29", re-verified at `ac8ab519`; read on its branch at
`335edce8`, not yet merged). See the DP table. The ruling's "What it obliges" section names
five negative tests, carried as acceptance item 11.

**The FR-266 open question is decided (b)**: OQ-1187, `docs/open-questions.md:131` and the
`03` §10 mirror (`03-rating-engine.md:1174`), filed by `RL-1184` (merged from #830 as
`3767b3b4`): "DECIDED 2026-09-28 — option (b), exact Shapley with largest-remainder
allocation (deputy, on spike F3's RS record)".

**`06` FR-364's `structural_diff` has an owner, WK-673** — decision E4 in #830's ruling
record, as a dated amendment at the end of `06` FR-364: at submission WK-673 persists
`03` FR-219's structural diff as a content-addressed blob and registers a verifier for
the `structural_diff` kind, before it wires FR-257's gate (RL-881). It supersedes
`RL-885`'s spec change 1 for `structural_diff` only; `RL-885`'s owner for
`dislocation_run` (WK-673) and its invariant stand.

**F-W10-2 is WK-673's.** `docs/findings/register.md:64`: *"exposure-weight wiring at the
diff endpoint: pricing-core accepts caller weights (DP1) but the endpoint passes none; the
portfolio-dataset join is scheduled in no slice"*, owner "portfolio-dataset integration".
Plan review 15 proposed WK-673 for it (CR-1212 at line 232, *"it reads the portfolio"*), and
the finding resolutions were accepted as proposed (`:275`). The register cell still names
the old owner; the auditor corrects it (not this plan's file). WK-675 Slice 5 depends on it
(the maintainer's 22:46:27 entry, item 5).

**The Work order is relaxed to real dependencies** by the maintainer's entry of 2026-09-29
22:46:27 BST, item 5 (to-lead.md), which amends CR-1212 Proposal 2's "WK-674, then WK-673,
then WK-675". This plan's cross-Work dependencies are re-derived under it in Sequencing.

**Preconditions:** #830 is merged (`RL-1184`), so Slice 1's OQ row and FR-364 amendment are
on main. **The #845 ruling must merge before Slice 1's leaf plan is filed**, because Slice 1
cites it for DP-1 and DP-2.

## Scope

### Requirement coverage — each id individually

| Id | Where | What WK-673 builds | Slice |
|---|---|---|---|
| FR-263 | `03` §3.9 | the Dislocation Run: distribution, averages overall and by segment, band counts, movers with drill-down, total change | 2 (compute), 4 (Job, routes) |
| FR-264 | `03` §3.9 | slicing by any portfolio Factor and by originating ladder rung | 2 |
| FR-265 | `03` §3.9 | a persisted, citable artifact referenced by the approval request | 4 |
| FR-266 | `03` §3.9 | the dated amendment (Slice 1); exact Shapley, isolated and cumulative views, residual line, above-six rule (Slice 3) | 1, 3 |
| NFR-495 | `03` §9 | **its application to this Work's artifacts only**: NFR-495 is "identical bundle hash + quote context ⟹ identical premium" (`03:1150`), measured by WK-669/671 (CR-1212). WK-673 evidences that the same holds for a run: identical bundle hashes + portfolio Dataset Version + spec ⟹ byte-identical run and attribution, across processes | 2, 3 |
| NFR-496 | `03` §9 | **its application to this Work's artifacts only**: NFR-496 is ladder exactness per scored quote (`03:1151`); its prod-sampling limb is WK-674's (CR-1212). WK-673 evidences no second rounding in the run's totals and the attribution reconciling to the minor unit, asserted on every run | 2, 3 |
| FR-224 | `03` §3.1 | the `approximation`-mode gate: a run against the same version in `exact` mode inside the declared threshold | 5 |
| FR-257 | `03` §3.8 | **limb (2) only**: a Dislocation Run against the current live version over an agreed portfolio | 5 |
| FR-364 | `06` §3.3 | the `structural_diff` verifier (E4), and the floor wiring for `rating_version` | 5, 6 |
| FR-231 (F-W10-2) | `03` §3.3 | **the exposure-weight limb only**: the rate-table diff shows "the exposure weight behind each cell (from the portfolio dataset)". The cell diff, absolute and relative change are built (WK-670); the endpoint passes no weights (`backend/src/app/platform/rate_tables.py:253-254` at `19c395ac`) | 7 |

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

First derived at `6c6f4532`; every row re-read at `19c395ac` for this revision. Where a
locator moved, the `19c395ac` one is given.

| # | The premise | At `19c395ac` | Status |
|---|---|---|---|
| a | "Decimal through the engine" makes the reconciliation exact | `03` §3.11 says the engine's arithmetic is exact inside and the Python binding returns `float`; FR-273 therefore carries money across as integer minor units. `_round_minor(raw: float, mode)` at `packages/pricing-core/src/pricing_core/rating/score.py:535` converts each engine result with `Decimal(repr(raw))` and quantizes to an integer. | **Does not hold**, and the deputy's 13:57:02 correction now says so: exact reconciliation is on the rounded integer minor units. Slice 1's amendment cites it. |
| a′ | where the float enters | `_round_minor`'s docstring (`score.py:539`) still speaks of "the engine's float64 arithmetic"; `03` §3.11 says the engine is exact and the float is the binding's. | **Resolved: the spec is right** (14:05:30 entry; the #845 ruling). Slice 1 corrects the docstring sentence to *"the binding's float64 return values (the engine's own arithmetic is exact, `03` §3.11)"*, no behaviour change. |
| b | `dislocation-run.schema.json` is hand-written and drift-exempt | `backend/tests/test_contracts.py:84`, `"dislocation-run": "later-phase — 03 rating"`, inside `ONE_SIDED_SLUGS` (`:69`) | reproduces; Slice 1 corrects the label, as `PL-1177` Task 4 did for `regression-suite` |
| c | the contract has no Shapley, isolated, residual or minor-unit attribution fields | `attribution[]` holds `change`, `mean_change_pct`, `cumulative_change_pct` (numbers); no isolated, Shapley or residual field; no minor-unit figure per change | reproduces |
| c′ | the contract and `03` §4.6 disagree | the contract has `job_id`, `by_ladder_rung[]` and `errors[]`; §4.6's example shows none of them | reproduces; noted by the 14:05:30 entry for Slice 1 |
| d | `DislocationSpec`, `BundleDelta`, `Attribution` do not exist | no definition under `packages/` or `backend/src`; `dislocate` and `attribute` are unbuilt (`03` §4.8) | reproduces |
| d′ | `attribute`'s published signature cannot be implemented | `attribute(changes: Sequence[BundleDelta], portfolio: pl.LazyFrame) -> list[Attribution]` (`03:883`) takes no baseline | reproduces; noted by the 14:05:30 entry; Slice 1 amends §5.2 |
| e | RL-881: `EVIDENCE_FLOOR["rating_version"]` names three kinds nothing can verify | `packages/model-schema/src/model_schema/approvals.py:106`; `DEFAULT_POLICY`'s entry at `:255-258`; `effective_evidence(` has three callers in `backend/src` (`modelling.py:1246`, `objectives.py:845`, `metrics.py:797`), none for `rating_version` | **reproduces**. `regression_run` is now verified by a direct check, `_regression_run_gate` (`rating_versions.py:619`, called at `:289`; WK-672 Slice 3, #886), not through the floor |
| e′ | RL-881: `06` §4.2's restatement of the floor omits `rating_version` | `06-governance.md:349` names `regression_run` and `dislocation_run` for `rating_version` | **no longer holds**. The stale clause in `RL-881` is the decision-maker's to supersede (the #845 ruling proposes it to the lead) |
| f | WK-671's batch scoring is reusable unchanged | `score_batch` at `score.py:1011`; row-by-row, not vectorised (its docstring) | reproduces |
| g | the Job kind exists | `JobKind.DISLOCATION_RUN = "dislocation.run"` at `model_schema/jobs.py:63`, routed to `JobQueue.COMPUTE` at `backend/src/app/platform/jobs.py:79`; no handler | reproduces; Slice 4 registers the handler |
| h | FR-219's structural diff exists to persist | `diff_algorithms` at `model_schema/rating.py:569`; `RatingVersionEvidence.structural_diff_blob` at `:125` | reproduces; Slice 5 persists it |
| i | the submission path | `rating_versions.submit_for_review` at `backend/src/app/platform/rating_versions.py:250`, calling `approvals.submit` at `:299` | reproduces; Slices 5 and 6 edit it |
| j | (new) FR-257 limb (2) needs "the current live version" | `VALID_RATING_VERSION_TRANSITIONS` (`model_schema/rating.py:50-60`) has no transition into `LIVE`. `RL-880` records that FR-238 makes `live` a property of a **Deployment** (FR-267), which with the Environment is WK-674's; `POST /api/v1/score` refuses with `NO_LIVE_RATING_VERSION` (`backend/src/app/api/score.py:144`) | **A real dependency on WK-674 Slice 2**, SL-1256 (the Deployment record and live resolution, `PL-1237` Task 2). Slice 5's limb (2) cannot name its baseline without it |
| k | (new) FR-231's weights are wired nowhere | `pricing_core/rate_tables/operations.py:336` takes `weights`; `backend/src/app/platform/rate_tables.py:237` `diff(…, portfolio_dataset_version_id=None)` passes none (`:253-254`); the route `rate_table_diff` (`backend/src/app/api/rate_tables.py:314`) has no portfolio parameter, and neither has `03` §5.1's route (`03:748`); the DP3 cache already keys on the portfolio identity (`backend/src/app/platform/diff_cache.py:81-88`); the 202 path runs `JobKind.RATE_TABLE_DIFF` (`backend/src/app/worker/rate_table_handlers.py:65`) | reproduces; Slice 7 wires it, after DP-5 |
| l | (new) FR-224's threshold has somewhere to live | `ApprovalPolicyEntry` (`approvals.py:111-122`) has `artifact_type`, `approvers_required`, `approver_roles`, `environment`, `evidence`, and no threshold field | the field is new: a `model-schema` shape change Slice 5 makes with the gate (the #845 ruling's premise note) |

### Risks

- **The 2^K cost may be large.** `score_batch` scores row by row. At NFR-493's **floor** of
  1 M risks per hour per worker (`03:1148`; a floor, not a measurement), K = 6 over
  freMTPL2 is 64 × 678 013 = 43 392 832 ratings, about 43 worker-hours. The 14:05:30
  feasibility rule answers it: measure first, and use ladder replay (2 ratings per policy)
  where the changes are step-aligned, proven against re-rates. Structural changes (steps
  added or removed) still need re-rates, which fan out across workers.
- **A subset bundle can be invalid.** A candidate step that reads an input only another
  candidate change introduces fails validation when mixed with baseline steps. DP-1 as
  ruled fails the run with the subset named; DP-2's regrouping is how the analyst groups
  dependent changes.
- **`compile_bundle` and the trace change under WK-1250.** WK-1250 (FR-217's sub-graph
  inlining, `PL-1254`) edits `compile_bundle`, which DP-1's subsets go through, and the
  step ladder that ladder replay reads (FR-248). Slice 3 and any WK-1250 slice touching
  either are serialised, and Slice 3's replay-exactness test is the guard.
- **MTA and cancellation quotes are refused.** Until FR-217's inlining is built, FR-218
  (`03:87`, `RL-1242`) refuses every `mid_term_adjustment` or `cancellation` quote with
  `INPUT_CONTRACT_VIOLATION`. A portfolio row with that `purpose` would fail a run. Slice 1
  states whether the portfolio frame admits such rows; Slice 2 refuses them by name if not.
- **FD-1245 may move FR-257's gate.** WF-699 E2 submits through `POST /approval-requests`,
  while FR-257's gate runs at `/rating-versions/{id}/submit`
  (`docs/findings/register.md:211`; open, the decision-maker's, before the P2 exit demo).
  Slices 5 and 6 build at `submit_for_review` and follow the ruling if it moves the gate.

## Decision points

Kind, blocking status and resolver per `document-ids.md` §1.7. DP-1, DP-2 and DP-3 were
decided by the deputy under the maintainer's delegation (2026-09-28 14:05:30 BST) and are
filed as the #845 ruling, which the decision-maker rules as technical decision points under
the maintainer's 2026-09-29 15:26:00 BST re-homing. DP-4 is slice design, the planner's own
(`.claude/roles/planner.md`), decided here. DP-5, added by this revision, is technical and
the decision-maker's; it is open.

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-1 | How are the 2^K subset bundles built? | (a) At the **artifact level**: each subset is a synthetic Rating Version holding the baseline's pins with the subset's changes substituted, the algorithm composed step by step, then compiled by `compile_bundle` and hydrated by `load_bundle` — a real, hash-identified bundle rated by ZEN. (b) At the **JDM graph level**: patch the baseline's `to_jdm` graph with each change's node edits and hash it with `bundle_hash`. (c) **Whole-pin swaps only**: a change is a pin (model, rate table, reference table, algorithm version); edits inside one algorithm version count as one change. | **(a)**, at step granularity from `diff_algorithms` plus the pin diff. Every subset goes through the same compile and validation path a real version does, so a subset the engine cannot rate is refused by `validate_algorithm` rather than priced. (b) bypasses compile-time validation (FR-274, FR-275, FR-276). (c) cannot isolate the `min_premium` change `03` §4.6's own example attributes, which is the interaction case the F3 decision turned on. | decision point | yes — Slice 1 | **(a), with conditions** — the #845 ruling. Subset bundles are ephemeral and content-addressed, never a Rating Version (no `rating_version` row; never approvable, deployable or listed), cached per run by content hash and discarded with the run's scratch; a subset that fails to compile fails the run with the subset named; the artifact records the bundles compiled and their hashes |
| DP-2 | Where does a "declared change" come from? | (a) **Derived**: every differing pin and every changed step is one change. (b) **Declared**: the analyst lists the changes in `DislocationSpec`. (c) **Derived default, analyst regroups**: the server proposes the derived list; the analyst may merge entries into ≤ 6 named groups; the server checks the groups partition the full diff exactly. | **(c).** (a) alone exceeds K = 6 on any real rate change and gives the analyst no way to apply the above-six rule. (b) alone lets a change be left out, and then the parts cannot sum to the whole. (c) keeps both: the derivation guarantees coverage and the partition check guarantees each difference is counted exactly once. | decision point | yes — Slice 1 | **(c)** — the #845 ruling. The server checks the groups partition the derived list exactly and refuses by name otherwise; both lists are on the artifact |
| DP-3 | Where does FR-224's threshold live? FR-224 leaves it to "the Phase 2 slice that builds this": a maximum absolute percentage deviation at a declared portfolio quantile, recorded on the approval. | (a) A **workspace setting** (`07` FR-446, FR-448; the `workspace_settings` table). (b) A field on the `rating_version` **`ApprovalPolicy` entry** (`06` §4.2), so it can vary by `risk_tier` (`06` FR-365). (c) Declared **on the Dislocation Run's spec** by the submitter. | **(b).** An approval threshold is governance: a policy entry is audited when edited and sits under FR-364's floor rule. (a) resolves environment variable before workspace setting (FR-446), so a deployment variable could loosen an approval gate. (c) lets the submitter set their own bar. | decision point | yes — Slice 5 only | **(b), with no environment-variable override** — the #845 ruling. The field does not exist yet on `ApprovalPolicyEntry` (premise l); Slice 5 adds it and keeps it out of FR-446's Settings path |
| DP-4 | Does Slice 5 wait on WK-672, or is `structural_diff` split out early? | (a) **Hold** the whole gate until WK-672 Slice 3 merges. (b) **Split**: Slice 5 builds `structural_diff`, FR-257 limb (2) and FR-224 as direct checks now; Slice 6 wires the `effective_evidence("rating_version")` floor union after WK-672 Slice 3. | **(b), decided.** See Rationale below. The deputy called the split "sound slice design" (14:05:30). WK-672 Slice 3 has since merged (#886), so the wait is satisfied; the split still keeps each slice small. | scope | no | PL-9101 (planner, slice design) |
| DP-5 | How does FR-231's diff get "the exposure weight behind each cell (from the portfolio dataset)"? Two parts: which portfolio, and how a portfolio row maps to a cell | (a) **A `portfolio` query parameter** naming a portfolio Dataset Version on `GET /api/v1/rate-tables/{slug}@{version}/diff`; a row maps to the cell whose key columns (`RateTable.keys`) equal the row's same-named columns; weight = Σ exposure per cell; a key column absent from the frame is refused by name. (b) **Through a Rating Algorithm Version**: the caller names an algorithm version as well, and the row's key values are those the algorithm's `lookup` step bindings feed the table, so derived keys (bands) are honoured. (c) **A workspace default portfolio**, with (a)'s join. | **(a) first, (b) where a key is derived.** (a) matches the cache key that already carries the portfolio identity (premise k) and needs no algorithm context, which a table edit often has not got. It cannot weight a table whose keys are derived by an earlier step (a banded age), and it says so by refusing. (b) handles that case but makes a table diff depend on an algorithm. (c) hides which portfolio weighted the figures, which an actuary must be able to cite. | decision point | yes — Slice 7 only | open (decision-maker) |

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
Slice 1 (spec) → Slice 2 (run) → Slice 7 (FR-231 weights) → Slice 3 (attribution + cost)
      → Slice 4 (Job, routes, artifact) → Slice 5 (structural_diff, limb 2, FR-224) → Slice 6 (floor wiring)
```

One slice at a time. Slice 7 runs straight after Slice 2, because it needs only Slice 2's
portfolio frame reader and WK-675 Slice 5 waits on it. Its number is appended so the
numbers other records cite stay fixed.

**Dependencies inside WK-673 and on decisions.** Slice 1 waits on the #845 ruling's merge.
Slice 7 waits on DP-5. Slice 5 cites DP-3 (decided).

**Cross-Work dependencies, re-derived under the maintainer's 22:46:27 item 5.** Only a named
slice, artifact or ruling counts. Bare order is lifted.

| Dependency | Real? | What is needed |
|---|---|---|
| "WK-674, then WK-673" (CR-1212 Proposal 2) | **No** for Slices 1–4, 6 and 7 | none of them reads an Environment, a Deployment or a live pointer; `dislocate` and `attribute` take two named versions |
| Slice 5 on WK-674 | **Yes** | FR-257 limb (2)'s baseline is "the current live version", and nothing can be `live` until WK-674 Slice 2's (SL-1256) Deployment record and live resolution land (premise j). Slice 5 starts after SL-1256 merges |
| Slice 6 on WK-672 Slice 3 | **Met** | #886 merged; WK-672 closed (CR-1243) |
| Slice 3 on WK-1250 | **No, but contended** | subsets compile through the current `compile_bundle`; WK-1250 changes it (see the file list) |
| WK-675 Slice 5 on this Work | **Yes** (the other direction) | Slice 7 (F-W10-2) |
| WK-675 Slice 8 on this Work | **Yes** (the other direction) | Slice 4 |
| The P2 exit demo | **Yes** | this Work closed |

**Files shared with other Works.** A slice here and a slice elsewhere that edit the same
file are serialised: the second one merges `origin/main` before its mint (never a rebase).
`docs/INDEX.md` conflicts are regeneration only.

| File | This Work's slice | Other Work's slice |
|---|---|---|
| `packages/model-schema/src/model_schema/approvals.py` | 5 (DP-3's threshold field on `ApprovalPolicyEntry`), 6 (reads the floor) | WK-674 Slice 2, SL-1256 (`deployment` entry in `DEFAULT_POLICY`, `PL-1237` Task 2); WK-1250 if its DP-1 is (a) |
| `docs/specs/03-rating-engine.md` | 1 (§3.9 FR-266, §4.6, §4.8, §5.2), 4 (§5.1), 5 (§3.1, §3.8 as needed), 7 (§5.1's diff route) | WK-674 Slices 2 and 6 (new §4 contracts after §4.8, §5.1 routes); WK-1250 (FR-217, FR-218); WK-690 (FR-244); WK-675 (§5.1). Section-scoped; the §4.8 neighbourhood is the likeliest textual conflict with WK-674 Slice 2 |
| `packages/pricing-core/src/pricing_core/rating/score.py` | 1 (`_round_minor`'s docstring only) | WK-1250; WK-675 Slice 7b |
| `compile_bundle` (`pricing_core/rating/compile.py`) and `TraceStep` | 3 (calls `compile_bundle`, reads the ladder for replay; no edit planned) | WK-1250 (edits both); WK-675 Slice 7b |
| `backend/src/app/platform/rating_versions.py` | 5, 6 (`submit_for_review`) | none planned at `19c395ac`; FD-1245's ruling may add one |
| `docs/specs/06-governance.md` | 5 (FR-364's `structural_diff`, §4.2's threshold field) | WK-674 Slices 2 and 3 (§4.1 rows, §4.2 `deployment` entry) |
| `docs/contracts/` (generated) | 2, 3, 4, 5, 7 | every Work that changes a `model-schema` shape; resolved by regenerating |

### Slice 1 — Spec: FR-266's amendment, the hard gate as requirements, the contract and the types

**Spec only; no application code** except one test-file label. Scope:

- **FR-266's dated amendment**, carrying the deputy's items 1–3 above and citing the
  13:57:02 correction for the hard gate: exact Shapley over
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
- **`03` §4.8** gains the portfolio frame's schema, including the exposure column Slice 7
  weights by, and whether rows with an MTA or cancellation `purpose` are admitted (Risks).
- **DP-1's conditions and DP-2's partition rule as spec text** (the #845 ruling's "What it
  obliges"): the ephemeral, content-addressed subset bundle with no Rating Version identity
  (never a `rating_version` row, never approvable, deployable or listed); a compile failure
  that names the subset; the compiled count and hashes on the artifact; changes derived
  from the structural diff, regrouped into at most 6 groups, the partition checked and
  refused by name; both lists on the artifact. **Where these describe the artifact's
  shape, §4.6 and the `model-schema` shape change together** (the #845 ruling: writing
  §4.6 ahead of the shape would make spec and generated contract disagree), so the shape
  parts land in the slice that first returns the type (Tasks, "Deviation"), in one commit
  with their §4.6 text.
- **`03` §5.2**: `DislocationSpec`, `BundleDelta` and `Attribution` defined, and
  `attribute`'s signature amended to take the baseline and the spec (premise d′), per
  DP-1 and DP-2.
- **`00` §2 glossary first** (`CLAUDE.md` §7): any new term — Shapley attribution,
  interaction residual, declared change group — is defined there before first use.
- **The `test_contracts.py:84` label** corrected to name `03` and WK-673, the slug left in
  `ONE_SIDED_SLUGS` until Slice 4.
- **`_round_minor`'s docstring sentence corrected** (premise a′) to the 14:05:30 wording, no
  behaviour change, in one commit with any spec text it touches.
- **The leaf plan names the #845 ruling's three Slice-1 negative tests** (acceptance item
  11) and the slice that builds each.

Depends on: the #845 ruling merged (#830 is). Not on WK-674. Gate: the full two-half gate, the four
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
- **The feasibility rule** (the 14:05:30 entry; acceptance item 5): the real `score_batch`
  rate measured first; **ladder replay** as the primary route where changes are
  step-aligned, proven equal to a true re-rate at K ≤ 3 on the full portfolio and on a
  declared sample at K = 4–6, falling back to re-rates on any mismatch and recording the
  fallback on the artifact; re-rates for structural changes; the estimated rating count
  (2^K × policies) shown before launch; no sampled figure ever presented as exact Shapley.
  The proposed dislocation-attribution NFR goes to the decision-maker; if neither route
  fits at K = 4, the figure goes to the decision-maker before any fallback is built.
- **The F3 carried items**: the six change sets repeated on the ZEN path; a second
  portfolio if one is available that is public (`.claude/CLAUDE.md` forbids real policy
  data in the semantic pass; this is a measurement, but the same care applies); the
  per-policy maxima of 690 and 976 explained or shown not to recur on ZEN.

Depends on: Slice 2 (and Slice 7, by the one-at-a-time order only). Serialised against any
WK-1250 slice that edits `compile_bundle` or the trace. Gate: as Slice 2, plus the tests,
the replay-exactness negative test, and the measurement.

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

**The routes' permissions (FD-1197).** `RL-1236`'s catalogue (`06-governance.md:253-300` at
`19c395ac`) rules `rating:read`, `rating:write`, `rating:submit` and `score:batch`, and names
no dislocation permission. Slice 4's leaf plan picks each route's name from that catalogue
(the likely pair is `score:batch` to start a run, which is a batch re-rate, and
`rating:read` to read one), cites FD-1197, and says whether the slice discharges it
(FD-1197's event is the next slice that touches permissions). A new dislocation permission
would grant a new capability: that is a scope change for the maintainer, not the slice's
pick, and it would land with its `06` row, enum member and check in one commit.

Depends on: Slice 3. Gate: as Slice 3, plus `generate-contracts.py --check`.

### Slice 5 — The approval gate, part one: `structural_diff`, FR-257 limb (2), FR-224

- **`structural_diff`** (`06` FR-364's E4 amendment): at submission, FR-219's diff
  persisted as a content-addressed blob into `RatingVersionEvidence.structural_diff_blob`
  and a verifier registered for the kind.
- **FR-257 limb (2)** on `submit_for_review`: refuse with `EVIDENCE_INCOMPLETE` unless a
  Dislocation Run exists whose candidate bundle hash equals the version's current one and
  whose baseline is the current live version. Tested on no run, a stale hash and a wrong
  baseline; its `req("FR-257")` marker names limb (2) only.
  The leaf plan states what happens when nothing is live yet (a first version), since
  "the current live version" then names nothing.
- **FR-224**: for an `approximation`-mode version, a run whose baseline is the same
  version in `exact` mode (built by DP-1's mechanism with `model_reference_mode` set to
  `exact`), refused above the threshold DP-3 places, naming the quantile and the observed
  deviation. FR-136's fidelity statement runs first as the cheap pre-check. **The threshold
  is a new field on `ApprovalPolicyEntry`** (premise l), a `model-schema` change generated
  to `docs/contracts/`, with its `06` §4.2 text, and **never read from Settings**: the
  #845 ruling's negative test (*FR-224's threshold resolved from an environment variable*)
  is this slice's.

Depends on: Slice 4; DP-3 (decided); **WK-674 Slice 2, SL-1256, merged** (premise j).
Serialised against SL-1256 on `approvals.py` and `06` §4.2 in any case. If FD-1245's ruling
moves FR-257's gate, the slice follows it. Gate: as Slice 4, plus the
refusal tests (acceptance item 7).

### Slice 6 — The approval gate, part two: the floor wiring

`submit_for_review` checks `policy.effective_evidence("rating_version")` against a
`verifiable` map — `structural_diff` (Slice 5), `regression_run` (WK-672 Slice 3's
`_regression_run_gate`, `rating_versions.py:619`), `dislocation_run` (Slice 5) — in the
pattern of `modelling.py:1238-1261`, replacing the direct limb checks, limb (1)'s
`_regression_run_gate` call at `rating_versions.py:289` included. A workspace policy that adds a kind nothing can verify is refused
by name, never passed. Tested with a policy at the floor, a policy above it, and each kind
missing in turn.

Depends on: Slice 5. WK-672 Slice 3 is merged (#886), so nothing outside the Work.
Gate: as Slice 5.

### Slice 7 — FR-231's exposure weights through the portfolio frame (F-W10-2)

Wires the weight limb of FR-231 that WK-670 left undone (premise k): the rate-table diff
shows the exposure weight behind each cell, from a portfolio Dataset Version.

- **Spec first:** `03` §5.1's diff route gains the portfolio parameter and the refusal DP-5
  settles on, and FR-231 gains a dated clarification naming how a row maps to a cell.
- **The join:** the portfolio frame (Slice 2's reader, `03` §4.8's schema from Slice 1)
  aggregated to Σ exposure per cell key, in Polars, passed as `weights` to
  `diff_vs_previous` / `diff_vs_seed`; the same weights on the 202 path
  (`JobKind.RATE_TABLE_DIFF`'s handler). The DP3 cache key already carries the portfolio
  identity; a test proves two portfolios give two entries.
- **Negative tests:** a key column absent from the frame refused by name; a diff without a
  portfolio still answers, unweighted and saying so; the weighted mean checked against a
  hand-computed figure.
- **Permissions:** the route's existing check (`RatingReadDep`,
  `backend/src/app/api/rate_tables.py:46`) plus read access to the portfolio Dataset
  Version; no new name. FD-1197 cited.
- **The register row** `FR-231 (F-W10-2)` is discharged on merge, by the auditor.

Depends on: Slice 2; DP-5. Unblocks WK-675 Slice 5. Gate: as Slice 2, plus
`generate-contracts.py --check`.

## Self-review

**1. Spec coverage.** FR-263 → Slices 2, 4. FR-264 → Slice 2. FR-265 → Slice 4. FR-266 →
Slices 1, 3. NFR-495, NFR-496 (their application to this Work's artifacts) → Slices 2, 3.
FR-224 → Slice 5. FR-257 limb (2) → Slice 5. `06` FR-364 → Slices 5, 6. FR-231's weight
limb (F-W10-2) → Slice 7. §4.6, §4.8's portfolio frame, the §5.1 routes, `dislocate`,
`attribute` and the three missing types → Slices 1–4. The deputy's six F3 items, as
corrected at 13:57:02 and amended at 14:05:30 → Slice 1 (items 1–4 as spec), Slice 3
(items 1–3 and 5–6 as code and measurement). The #845 ruling's five negative tests →
Slices 1, 3 and 5 (acceptance item 11).

**2. Placeholder scan.** This is a map plan: each slice is a scope statement, not a task
list, and each leaf plan carries its own steps. No new requirement id is written here;
Slice 1's ids come from the lead. "The #845 ruling" is a deliberate stand-in for an id
not yet minted, replaced at the mint turn (revision note, item 2).

**3. Consistency.** Every locator was re-read at `19c395ac`, the tree in the header.
Premises a, a′, c′, d′, e and e′ record what moved since `6c6f4532`; j, k and l are new.

**4. Rulings between sweep and filing.** Merged since the first draft and cited:
`RL-1184` (#830), `RS-1201` (#833), `RL-1236` (#856), WK-672 Slice 3 (#886), CR-1212's
acceptance, the maintainer's 22:46:27 and 22:47:23 entries. Open and cited: the #845
ruling (read at `335edce8`), FD-1245 (open, may move FR-257's gate). The WK-673 roadmap row
(`docs/roadmap.md:686` at `97b15726`) lists only FR-263 to FR-266; the scope table above is the fuller
list, and correcting the row is the lead's or decision-maker's, proposed in the report
that carries this revision.
