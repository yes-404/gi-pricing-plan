---
id: PL-1403
family: plan
kind: leaf
title: WK-673 Slice 2 — the Dislocation Run on ZEN, in integer minor units: leaf plan
status: draft                   # draft → active → superseded | retired (§1.2a)
created: 2026-10-04
owner: planner
tree: 1ab1776dae080dcde4eb8e79ac84f5f5f653136a
phase: P2
work: WK-673
slice: SL-1386
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1267, PL-1395, LG-1400, RL-1394, RL-1361, RL-1379, RL-1264, RL-1263, PL-1392, PL-1371, FD-1374]
---

# PL-1403 — WK-673 Slice 2: the Dislocation Run on ZEN, in integer minor units: leaf plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended)
> or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`)
> syntax for tracking. The executor is spawned from `.claude/roles/executor.md` and also
> binds `test-driven-development` (every task is red first), `python-package` (Tasks 2–5:
> where code lives, `model-schema` idioms), `python-test` (requirement markers, negative
> tests), `spec-change` (Task 1), `contract-schema` (Task 1: RL-1402 S5 edits the
> hand-authored contract), `dev-commands` (the two-half gate and its traps)
> and `git-hygiene`. Read [`README.md`](README.md)'s five unchecked conventions before the
> first step.

Filed 2026-10-03 under working id 9735, allocated by the lead; minted as `PL-1403` on 2026-10-04 (the GO entry in
`~/gi-pricing-plan.local/channel/to-lead.md` headed "2026-10-03 23:49:35 BST — GO:
planner-1386 (opus) writes WK-673 Slice 2's leaf plan …"). Drafted from 23:57:25 BST
(`TZ=Europe/London date`) against origin/main `1ab1776d` (#1094, SL-1385 closed). Every
locator below was read at that tree unless another tree is named.

**Pre-merge fix, 2026-10-04 (drafted from 12:20:37 BST, `TZ=Europe/London date`), by
planner-9735fix on the lead's instruction, before this plan's first merge.** It folds in three
sources. Each is named here so a reader can find what changed and why:
- **RL-1402**, the decision-maker's ruling on DP-S2-1 to DP-S2-7 (PR #1098, branch
  `rl-9734-wk-673-s2-dp-ruling`, head `6eb6d43e87e5d9cd3d4757ae085c26058c017dd5`; not on main,
  so it is named by PR and head). Its "What it obliges", PL-1403 items 1 to 5, are applied
  below. The ruling's texts are S1 to S5; the executor applies those, never this plan's Appendix.
- **The plan audit** (`~/gi-pricing-plan.local/handover/audit-9735-2026-10-03.md`, Sun
  2026-10-04 00:11:14 BST). B1 (check 32 on RL-1401) was resolved by merge order: #1096 merged
  RL-1401 to main at `7e2ee2ba`, which this branch has merged, and `audit-docs.py` then fails
  check 31 only. B2 is ruled by RL-1402 DP-S2-1 (`select_movers`). N1, N2, N3 and N6
  are ruled there too; N4, N5 and N7 are applied in Tasks 4 and 5 and Acceptance 3 and 6.
- **RL-1402's audit** (`~/gi-pricing-plan.local/handover/audit-9734-2026-10-04.md`; the lead's
  verdict CLEAN, with three non-blocking items to land in this plan, the ruling not edited for
  N1 and N3): N1 (a mover tie on |pct| broken by |change_minor|, Task 5), N2 (the banded set is
  `baseline_minor > 0`, Task 0 Step 4 and Task 5; ruled by RL-1402, Amendment N2,
  which adds the count `outcomes.negative_baseline`), N3 (a band's `exposure_share` is over the
  banded set, Task 5).

The premises below stay as read at `1ab1776d`. `git diff --stat 1ab1776d 7e2ee2ba` lists only
`docs/INDEX.md` and RL-1401's file, so every spec and code locator reads the same at both.

## Goal

Build `03` FR-263's **Dislocation Run** and FR-264's slicing as a pure `pricing-core`
computation, on the ZEN engine, in integer minor units:
- `pricing_core/rating/analysis.py` is created, holding `dislocate` with the signature
  `RL-1394` T7 fixed (`03` §5.2), plus the four public functions RL-1402 DP-S2-1
  rules: `read_portfolio`, `dislocation_frame`, `select_movers` and `summarise_dislocation`;
- the two passes are two `score_batch` calls over `03` §4.8's portfolio frame as `RL-1394`
  wrote it: each pass sees the stamped columns, `quote_id` and exactly its own bundle's
  `input_contract`, and every other column passes through beside the scored rows (`RL-1361`
  §E, `RL-1394` DP-S1-1 (b));
- the per-policy change is computed on the `payable_premium` rung's `value_minor`, as integers,
  and every money figure is a sum of those integers (FR-1397's exact reconciliation, applied
  here to the run's totals; NFR-496 as `PL-1267` applies it to this Work);
- `DislocationSpec` and `DislocationRun` (without the attribution part, which is Slice 3's)
  are defined in `model-schema` and match `03` §4.6 field for field.

This slice ships no route, no Job handler, no persisted artifact and no frontend. Those are
Slice 4's (`SL-1388`) and WK-675's.

**Architecture:** `analysis.py` reads a `pl.LazyFrame` portfolio, validates it against §4.8,
projects one frame per pass, rates each with the existing `score_batch` (unchanged), joins
the two output frames on `quote_id`, and aggregates in Polars plus exact integer and
`Decimal`/`Fraction` arithmetic. It takes two already-compiled `CompiledBundle`s and compiles
nothing (`RL-1379`, see "Bundles" under Inputs).

**Tech Stack:** Python 3.12, Polars, Pydantic v2 (`model-schema`), `zen-engine` through the
existing `score_batch`, pytest.

**Spec:** [`../specs/03-rating-engine.md`](../specs/03-rating-engine.md) §3.9 (FR-263,
FR-264, FR-1397), §4.6, §4.8 ("The portfolio frame (WK-673, added 2026-10-03)"), §5.2, §9
(NFR-495, NFR-496); the map plan
[`PL-01267`](PL-01267-wk-673-dislocation-with-attribution-map-plan.md) Slice 2; the ruling
[`RL-1394`](../rulings/RL-01394-pl-1395-dp-s1-1-to-6-decided-each-pass-sees-only-its-own-contract-purpose-and-date-are-stamped-exposure-years-is-fixed-and-a-change-is-one-step.md).

## Acceptance Standard

Every command runs in the executor's own worktree (`env -C <worktree> …`), against the range
`origin/main...HEAD`, never a tip SHA alone. "The ruling" is the decision-maker's record that
resolves DP-S2-1 to DP-S2-7 (activation need 1): RL-1402, minted 2026-10-04 in one PR
with this plan.

1. **Every blocking decision point has a resolver id before Task 1 starts.** The Decision
   points table of this plan's minted, `active` version shows a minted `RL-` id in the
   "Resolved by" cell of DP-S2-1 to DP-S2-7, and `python3 scripts/audit-docs.py` resolves
   each id.
2. **The ruled texts land verbatim.** For each of the ruling's texts S1 to S5 (its "The exact
   texts"; this plan's Appendix P1–P6 are the superseded proposals), the ledger shows a `diff`
   of the ruling's text against the committed text with no difference other than `<date>` and
   `RL-<n>`. For S4 and S5, which are edit lists, the ledger shows each listed edit in
   `git diff origin/main...HEAD -- docs/specs/03-rating-engine.md docs/contracts/schemas/dislocation-run.schema.json`
   and no other hunk in the contract.
3. **The module exists with the ruled surface.** `grep -n '^def \|^async def '
   packages/pricing-core/src/pricing_core/rating/analysis.py` prints exactly five public
   functions: `dislocate` with T7's signature (`baseline: CompiledBundle, candidate:
   CompiledBundle, portfolio: pl.LazyFrame, spec: DislocationSpec) -> DislocationRun`),
   `read_portfolio`, `dislocation_frame`, `select_movers` and `summarise_dislocation`, with the
   signatures of RL-1402 S1. Every other top-level `def` starts with `_`.
   `grep -n '^class ' …/analysis.py` prints `PortfolioFrameError(ValueError)` and no other
   public class, and `PortfolioFrameError.code == "VALIDATION_FAILED"` is asserted by Task 3's
   tests. `derive_changes` and `attribute` are **not** defined (Slice 3).
4. **Every id in scope has a test that names it.** `uv run python scripts/req-coverage.py`
   lists at least one test for each of FR-263, FR-264, NFR-495 and NFR-496 in
   `packages/pricing-core/tests/test_rating_dislocation.py`. FR-1397's own tests stay
   Slice 3's (it says "attribution"); this slice's integer-sum test carries `req("NFR-496")`.
5. **`RL-1394`'s four Slice-2 negative tests exist and were shown red** (its "Acceptance — the
   violation that must become detectable"; LG-1400's Task 7 table assigns no `RL-1264` row to
   Slice 2, so these four are this slice's whole negative-test inheritance). Each name below
   is defined once, and the ledger quotes each failing on the deliberately broken input
   named in its Task before the code that makes it pass:
   - `test_dislocation_undeclared_column_never_reaches_the_engine` (Task 4);
   - `test_dislocation_undeclared_billing_named_column_refuses_no_row` (Task 4);
   - `test_read_portfolio_refuses_a_purpose_column_by_name` (Task 3);
   - `test_read_portfolio_refuses_a_null_exposure_naming_the_column_and_count` (Task 3).
6. **Nothing compiles a Rating Version (`RL-1379`).** `git grep -nE
   'compile_bundle|compile_rating_version|rating\.compile|from \.compile|import compile' --
   packages/pricing-core/src/pricing_core/rating/analysis.py` prints nothing. The predicate is
   a name grep, so it also matches a comment or docstring that names a compile function: any
   hit fails, and the module neither calls, imports nor names one. The import alternatives
   catch a compile path reached through `pricing_core/rating/compile.py` under another name
   (plan audit N5). Test fixtures build bundles only from `status: "draft"` in-memory
   `RatingVersion`s (the `_compiled` pattern of `packages/pricing-core/tests/test_rating_score.py:137-140`).
7. **No float is summed after rounding (NFR-496 as `PL-1267` applies it).**
   `test_dislocation_totals_are_sums_of_per_policy_minor_units` asserts
   `totals.baseline_premium_minor` and `totals.candidate_premium_minor` equal the integer sums
   of the per-policy `payable_premium` `value_minor` over the compared set, and that both are
   `int`; the ledger quotes it red against a deliberately float-summing aggregation (Task 5
   Step 2).
8. **A repeat run is byte-identical across processes (NFR-495 as `PL-1267` applies it).**
   `test_dislocation_is_byte_identical_across_fresh_interpreters` runs the same run in two
   fresh interpreters with different `PYTHONHASHSEED`s and compares
   `DislocationRun.model_dump_json()` bytes, and its negative control (a run with one portfolio
   row's input changed) differs.
9. **`model-schema` matches `03` §4.6.** `test_dislocation_run_fields_match_the_hand_authored_contract`
   (in `packages/model-schema/tests/test_dislocation.py`) asserts that every property
   `DislocationRun.model_json_schema()` emits is a property of
   `docs/contracts/schemas/dislocation-run.schema.json` (with the same `required` set for the
   top level and for each item object it defines, `outcomes` among them), and that the contract
   properties it does not emit are exactly `attribution`, `derived_changes`, `change_groups`
   and `attribution_summary` (Slice 3's). It runs against the contract as S5 leaves it. It is
   shown red with one field renamed. The `required` comparison holds only while each item
   model's optional fields are the contract's optional fields, so a field the contract makes
   optional is optional in the model, and the reverse.
10. **The write set holds.** `git diff --name-only origin/main...HEAD` lists only paths in
    "Write set" below; in particular `git diff --stat origin/main...HEAD --
    packages/model-schema/src/model_schema/__init__.py backend/ frontend/
    packages/model-schema/src/model_schema/approvals.py docs/specs/06-governance.md
    packages/pricing-core/src/pricing_core/rating/score.py` prints nothing.
11. **The gate.** The full two-half gate (`CLAUDE.md` §11) passes on a clean detached checkout
    of the gated SHA, with the stage table in the ledger; and the four docs checks
    (`python3 scripts/audit-docs.py`, `python3 scripts/doc-id.py check`,
    `python3 scripts/doc-index.py --check`, `python3 scripts/register-lint.py`) on a detached
    copy of the committed tree, each with rc and its `FAILED (n)` or "All checks passed." and
    `DISCLOSED (…)` lines quoted.
12. **The slice closes on the maintainer's MERGE-ACK and a clean audit** (`PL-1267`
    Acceptance 8): the dated to-lead.md entry naming the PR's full head SHA, and the filed
    clean audit. No maintainer acceptance line is required for a Slice (`CLAUDE.md` §13).
13. **RL-1402's violations are detectable** (the ruling's "Acceptance — the violation that must
    become detectable", plus its audit's N1). The ledger quotes each named test failing on the
    broken implementation named, then passing on the real one:
    - `test_dislocation_movers_are_kept_for_drill_down` against `select_movers` sorted by signed
      change, and against one with no `quote_id` tie-break (Task 5);
    - `test_select_movers_breaks_a_pct_tie_by_absolute_minor_change` against `select_movers`
      with sort step 2 (`|change_minor|` descending) removed (Task 5; audit-9734 N1);
    - `test_dislocation_rounds_each_ratio_once` against a conversion through
      `Decimal(n) / Decimal(d)` at a low context precision followed by `quantize` (Task 5);
    - `test_dislocation_by_ladder_rung_parts_sum_to_the_total` against an origin that compares
      `unrounded_minor` alone (Task 5, the rounding-only fixture);
    - `test_dislocation_by_segment_reports_each_level` against `by_segment` with nulls filtered
      out (Task 5);
    - `test_read_portfolio_refuses_a_nan_exposure` against `read_portfolio` with the NaN check
      removed (Task 3).

## Global Constraints

- **Money is integer minor units, or `Decimal` in the rating path, never float** (`CLAUDE.md`
  §7; `03` FR-273). Every `*_minor` figure is an `int` summed from `value_minor` integers. A
  percentage or a share is a derived view, computed from integers (or exact `Decimal`) and
  converted to a JSON number only at the end (`03` §4.6's dated note: *"Money is integer minor
  units"*).
- **A ratio is rounded once** (RL-1402 DP-S2-3): a `fractions.Fraction` of Python
  `int`s, `round(fraction, n)` (exact, half-even), then `Decimal` exactly, and `float` only at
  the model boundary. A ratio whose denominator is 0 is `None`. Never divide the unrounded
  `Decimal`s and then `quantize`: that rounds twice (at the context precision, then at the
  quantum). Dividing is exact only on a `Fraction` already rounded (Task 5 Step 3).
- **`pricing-core` stays importable standalone** (`CLAUDE.md` §2): `analysis.py` acquires no
  Job, no output location, no database and no blob store, as `score_batch`'s own docstring
  states (`score.py:1154-1157`); `.importlinter`'s `core-has-no-infrastructure` contract
  enforces it.
- **`score_batch` is not edited.** Its tolerance of extra columns stays (`03` §4.8,
  "`score_batch`'s own tolerance of extra columns (above) is unchanged"); the projection is
  `analysis.py`'s. `score.py` is a contended file (`RL-1263` :89 names it).
- **Nobody hand-writes a shape `model-schema` owns** (`CLAUDE.md` §2): `DislocationSpec` and
  `DislocationRun` are defined once, in `packages/model-schema/src/model_schema/dislocation.py`.
- **No pandas** (`CLAUDE.md` §3): Polars only.
- **Messages are input-free** (NFR-499 as `score.py`'s `_batch_error_code` docstring applies
  it): a refusal names the column and the count, never a value from the portfolio.
- **Spec text only through the ruling** (the GO's item 4): the executor applies texts copied
  from the minted ruling, never from this plan's Appendix and never its own wording.
- **Requirement ids are cited individually** (`.claude/roles/planner.md`).
- **One slice at a time within WK-673** (`delivery-process.md` §8); up to two build slices from
  different Works under `RL-1263`.

## Inputs

**The map plan, `PL-1267` Slice 2** (`:481-494` at `1ab1776d`), verbatim in substance:
`dislocate(baseline, candidate, portfolio, spec)` in `pricing_core/rating/analysis.py`; two
`score_batch` passes over the portfolio frame, joined per policy on integer minor units;
distribution bands, averages overall and by declared segment, exposure and policy counts per
band, movers beyond the spec's thresholds (FR-263); slicing by any portfolio Factor and by
the first ladder rung at which the two premiums differ (FR-264); the movers' identities kept
for drill-down to a trace; `DislocationSpec` and `DislocationRun` in `model-schema`; tests for
FR-263, FR-264, NFR-495 (a repeat run in a separate process is byte-identical) and NFR-496
(the totals equal the sum of per-policy minor units, no second rounding). Its "Deviation from
the adopted cut" (`:380-387`): `DislocationRun` **without the attribution part** in Slice 2,
`BundleDelta` and `Attribution` in Slice 3.

**`RL-1394`'s adopted texts, as landed on main by #1094** (`03` at `1ab1776d`):
- `03` §3.9: FR-266 as amended (`:189`), **FR-1397** (`:190`), **FR-1398** (`:191`),
  **FR-1399** (`:192`). Slice 2 builds none of FR-1397–FR-1399 (they are attribution's), but
  it obeys FR-1397's arithmetic for every money figure it produces: integer minor units from
  the payable premium's `value_minor`, summed as integers, no float summed after rounding.
- `03` §4.6 (`:510-557`): the dated note and the example, and the hand-authored contract
  `docs/contracts/schemas/dislocation-run.schema.json` (one-sided, `backend/tests/test_contracts.py`
  `ONE_SIDED_SLUGS["dislocation-run"]`). Its required top-level fields are `baseline_ref`,
  `candidate_ref`, `portfolio_dataset_version_id`, `policy_count`, `exposure_years`, `totals`,
  `distribution`; `attribution` requires `derived_changes`, `change_groups`,
  `attribution_summary` (`dependentRequired`).
- `03` §4.8, "The portfolio frame (WK-673, added 2026-10-03)" (`:688-702`): `quote_id`
  (required, non-null, unique) and `exposure_years` (decimal, non-null, never negative); each
  bundle's declared inputs; a frame fault refused before any rating with `VALIDATION_FAILED`
  naming the column and the count; `purpose`, `effective_date` and `rating_version_ref`
  stamped from `DislocationSpec.purpose` and `DislocationSpec.as_at` and each pass's own ref;
  every other column passing through and never reaching the engine; a declared name the
  portfolio lacks is that row's `INPUT_CONTRACT_VIOLATION` `"error"` row.
- `03` §5.2 (`:985-992`, `:1052`): `dislocate`'s signature; the types paragraph, which fixes
  `DislocationSpec`'s fields — `baseline_ref`, `candidate_ref`, `portfolio_dataset_version_id`,
  `purpose`, `as_at`, `segments`, `band_edges_pct`, `mover_threshold_pct`, optional
  `change_groups` — and says the band and mover names *"are Slice 2's to confirm against FR-263,
  and may be amended there with a dated note"* (`RL-1394` T7, ruling file `:569-570`). DP-S2-4
  confirms them.

**`RL-1361`** (the portfolio frame and pass-through): §E (`:328-342`) requires that the
reader let columns outside §4.8's declared set pass through, and that a null exposure is
refused, never read as 0; Ruled item 1 (`:364-372`) makes **"PL-1267 Slice 2's reader"** the
reader Slice 7's diff route uses. So the reader this slice builds is a public function Slice 7
can call (DP-S2-1).

**Bundles, and `RL-1379` (compile only while `draft`).** `RL-1379` Ruled (`:128-137`): a
compile runs only while the Rating Version is `draft`; any other status is refused 409
`RATING_VERSION_IMMUTABLE`, at the route and in the service. **How this slice obtains its
baseline and candidate bundles:** it does not obtain them. `dislocate` takes two
`CompiledBundle`s from its caller (T7), and `analysis.py` calls neither `compile_bundle` nor
any platform compile (Acceptance 6).
- **In this slice's tests**, each bundle is built from an in-memory `RatingVersion` whose
  `status` is `"draft"`, by `compile_bundle` plus `load_bundle` with a fake resolver, exactly
  as `_compiled` does (`packages/pricing-core/tests/test_rating_score.py:118-140`). That is the
  pure function on a draft version, not `compile_rating_version`, so `RL-1379` is not engaged.
- **In production (Slice 4, not built here)**, the `dislocation.run` handler hydrates each
  version's **stored** compiled `Bundle` (written while the version was `draft`) with
  `load_bundle`, and never compiles. A version with no compiled bundle cannot be compiled once
  it has left `draft`, so the handler must refuse it. `RL-1401` (PR #1096; not on main at
  `1ab1776d`, merged to main at `7e2ee2ba`) item 2 rules the same case for a deployment as 409
  `BUNDLE_COMPILE_FAILED`; Slice 4's leaf plan rules its own route's refusal. This plan only
  names the obligation, so the Slice 4 planner inherits it.
- **The related finding** (holds-2026-10-01.md, "Next FD batch MUST include": an approved
  Rating Version may never have been compiled) is owned by WK-673's FR-257 submission gate,
  which is Slice 5's, not this slice's.

**RL-1402** (PR #1098, head `6eb6d43e`; DP-S2-1 to DP-S2-7 ruled, each amended
from the plan's recommendation except DP-S2-4). Its "Ruled" table is the Decision points
table's "Resolved by" column below. Its texts S1 (`03` §5.2 signatures), S2 (`03` §5.2 surface
paragraph), S3 (`03` §4.6 arithmetic block), S4 (five edits to §4.6's example) and S5 (the
contract: `outcomes`, six ratios nullable, `level` nullable, `errors.items`) are what Task 1
applies. It confirms OQ 9739 is not needed. Its PL-1267 delta ("Slice 4 writes `select_movers`'
rows to `largest_movers_blob` … Slice 7's diff route reads its portfolio with
`read_portfolio`") is carried by the dispatch record, not by this plan.

**OQ 9739** (the subset input-contract question, `RL-1394` "Not ruled here"): it concerns
which `input_contract` a **proper subset** bundle declares. This slice rates only the baseline
and the candidate, each with its own contract, and builds no subset. **Slice 2's text does not
need it, so it stays with SL-1387** (the GO's item 3; holds-2026-10-01.md, "SL-1387's and
SL-1388's leaf plans MUST carry").

**`RL-1264`'s negative tests.** LG-1400's Task 7 table (`docs/ledgers/LG-01400-wk-673-slice-sl-1385-the-portfolio-frame-and-the-types.md:159-167`)
assigns its three rows to Slice 4 (`SL-1388`) and Slice 3 (`SL-1387`); **none to Slice 2**.
`RL-1394`'s four Slice-2 tests are carried instead (Acceptance 5).

## Scope

### Requirement coverage, each id individually

| Id | Where | What this slice builds | Test |
|---|---|---|---|
| FR-263 | `03` §3.9 | the per-policy change on integer minor units; the distribution of change (bands), average change overall and by declared segment, exposure share and policy count per band, movers beyond the threshold, ordered and returned by `select_movers` for drill-down, total portfolio premium change | Task 5 |
| FR-264 | `03` §3.9 | slicing by any Factor on the portfolio (per DP-S2-6) and by the ladder rung at which the change originated (per DP-S2-5) | Task 5 |
| NFR-495 | `03` §9 | **its application to this Work only** (`PL-1267` scope row): identical bundles, portfolio and spec ⟹ a byte-identical `DislocationRun`, across processes | Task 6 |
| NFR-496 | `03` §9 | **its application to this Work only**: no second rounding in the run's totals; every money total is an integer sum of per-policy `value_minor` | Task 5 |

**Not in scope:** FR-265 (the persisted artifact, Slice 4); FR-266, FR-1397, FR-1398, FR-1399
(attribution, Slice 3); the Job, the routes, permissions, `docs/contracts/` generation and the
`ONE_SIDED_SLUGS` lift (Slice 4); the Dislocation view (WK-675); FR-231's weights (Slice 7,
which reuses this slice's reader).

### Premises re-derived at `1ab1776d`

| # | Premise | At `1ab1776d` | Status |
|---|---|---|---|
| P1 | `analysis.py` does not exist | `ls packages/pricing-core/src/pricing_core/rating/` lists `authored.py compile.py golden.py ladder.py properties.py replay.py runtime.py score.py testing.py trace_diff.py vocabulary.py` | holds; Task 3 creates it |
| P2 | no dislocation type exists | `grep -rn 'class Dislocation' packages/` prints nothing; `model_schema/rating.py:125` has only `dislocation_run_id: UUID \| None` on `RatingVersionEvidence` | holds; Task 2 creates `model_schema/dislocation.py` |
| P3 | `score_batch` forwards every non-reserved column | `score.py:262` `_BATCH_RESERVED_COLUMNS`; `_row_to_ctx` (`:1021-1042`) puts every other column into `QuoteContext.inputs` | holds; the projection (§4.8) is therefore `analysis.py`'s job |
| P4 | a billing-named input refuses the row | `score.py:425` `_check_billing_surface` | holds; `RL-1394`'s `instalment_count` test (Task 4) depends on the projection removing it |
| P5 | the output frame carries what the join needs | `score.py:280` `_BATCH_OUTPUT_SCHEMA`: `quote_id`, `outcome`, `rating_version_ref`, `bundle_hash`, `premium_ladder_json`, `outputs_json`, `decline_reasons`, `error_code`, `error_message` (`03` §4.8 output row) | holds |
| P6 | the payable premium is a ladder rung | `LadderRungName` (`model_schema/scoring.py:49-60`) ends with `"payable_premium"`; `LadderRung.value_minor: MoneyMinor` (`:160`); `premium_ladder_json` is `"[" + ",".join(rung.model_dump_json() …) + "]"` (`score.py:934-940`) | holds; the per-policy premium is that rung's `value_minor` |
| P7 | `CompiledBundle` carries the contract | `runtime.py:625-643`: `content_hash`, `decision`, `algorithm`, `boosters`; `algorithm.input_contract` is a list of `InputContractField` with `.name` (`model_schema/rating.py:207-212`) | holds; per-pass projection reads `bundle.algorithm.input_contract` |
| P8 | `CompiledBundle` carries no Rating Version ref | `runtime.py:625-643` | holds; each pass stamps `spec.baseline_ref` or `spec.candidate_ref` (§4.8) |
| P9 | `ArtifactRef` dumps as its canonical string | `model_schema/refs.py` `ArtifactRef._render_canonical` (`@model_serializer`) | holds |
| P10 | a typed pricing-core error mapped to `VALIDATION_FAILED` at the boundary has precedent | `backend/src/app/worker/data_handlers.py:408-411` maps `SplitError` to `PlatformError("VALIDATION_FAILED", …, 422, …)` | holds; RL-1402 DP-S2-1 rules `PortfolioFrameError` on the same pattern, with `code = "VALIDATION_FAILED"`; the mapping stays Slice 4's |
| P11 | stored exposure is a float upstream | `pricing_core/data/profile.py:413-421` `_stored_exposure(value: float) -> Decimal` (`Decimal(str(round(value, 6)))`, FR-62) | holds for the profiler; and the public example declares it a float: `examples/fremtpl2/seed.py:56` `"exposure_years": "float"`. RL-1402 DP-S2-7 rules (a), amended: a float column is read as `Decimal(str(round(v, 6)))`, NaN and infinity refused; Task 0 Step 5 re-reads the dtype at dispatch |
| P12 | a cross-process determinism test has precedent | `packages/pricing-core/tests/test_testing_determinism.py:136-146` (`subprocess.run([sys.executable, "-c", _CHILD, …], env={…, "PYTHONHASHSEED": …})`) | holds; Task 6 mirrors it |
| P13 | nothing requires a new `model-schema` class to be exported from `__init__.py` | the only `model_schema.__all__` reader is `backend/tests/test_contracts.py:2599`, an `ArtifactEnvelope` subclass sweep | holds; DP-S2-8 keeps `__init__.py` out of this slice |
| P14 | an undeclared engine read compiles today | `docs/findings/register.md`, FD-1374 (MEDIUM, owner WK-1178); RL 9771 (PR #1060, working id, not on main) would refuse it at save | holds at `1ab1776d`; Task 4's fixture handles either state (Task 4 Step 1) |

### Risks

- **A large DP set.** Seven decision points block activation, because FR-263 and FR-264 fix
  *what* is reported and §4.6 fixes the field names, but nothing fixes the arithmetic (which
  policies are compared, how a mean is taken, which band an edge belongs to, what "the rung at
  which the change originated" means). Picking any of these in code would be a silent pick
  (`CLAUDE.md` §10). One ruling takes all seven: RL-1402, which blocks activation
  until it is minted.
- **`score_batch` is row by row** (its docstring, `score.py:1148-1152`), so a full freMTPL2 run
  is slow. This slice measures nothing. The rate is Slice 3's to measure (`PL-1267` Acceptance 5).
  Tests use small fixture portfolios.
- **FR-246 enforcement may land first** (P14). Task 4's undeclared-read fixture then cannot
  come from `compile_bundle`. Step 1 builds it without the save-time check, the case `RL-1394`
  DP-S1-1 names ("a bundle compiled before FR-246's enforcement").
- **WK-674 S2 merges into the same spec file** (`03`). The sections are disjoint (contention
  table below). The second to merge re-merges main and re-runs its full gate.

## Decision points

Kind, blocking status and resolver per `document-ids.md` §1.7. Rows of kind "decision point"
are the decision-maker's, resolved in one `RL-` that also adopts or amends P1–P6. **The slice
may not move `draft → active` while any blocking row is open.** DP-S2-8 is slice design, the
planner's own, decided here. **DP-S2-1 to DP-S2-7 are ruled by RL-1402** (PR #1098);
each row stays blocking until that ruling is minted; it is minted as `RL-1402` in one PR with
this plan. The Options and Recommendation cells are the plan's proposals as the
ruling read them, and are not edited; where the ruling amended them, its "Resolved by" summary
and the Tasks below follow the ruling.

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-S2-1 | **What public surface does `analysis.py` have besides `dislocate`?** Two consumers need more than a `DislocationRun`: Slice 7's diff route needs "Slice 2's reader" (`RL-1361` Ruled item 1), and Slice 4 must write the movers' identities to `largest_movers_blob` (§4.6; `pricing-core` cannot write a blob) without rating the portfolio twice | (a) **Three public functions** added to `03` §5.2 beside `dislocate`: `read_portfolio(portfolio, *, segments=()) -> pl.LazyFrame` (validates §4.8 and the segment columns, raises `PortfolioFrameError`); `dislocation_frame(baseline, candidate, portfolio, spec) -> pl.DataFrame` (one row per policy: the two outcomes, the two `payable_premium` minor figures, the originating rung, the error codes, the pass-through columns); `summarise_dislocation(frame, spec) -> DislocationRun`. `dislocate` is exactly `summarise_dislocation(dislocation_frame(…), spec)`. `PortfolioFrameError(ValueError)` is mapped to `VALIDATION_FAILED` by the platform (P10). (b) **`dislocate` only**; the reader and the per-policy frame stay private; Slice 7 writes its own reader and Slice 4 rates twice or reimplements the join. (c) `dislocate` returns `tuple[DislocationRun, pl.DataFrame]` | **(a).** It keeps T7's `dislocate` signature unchanged, gives Slice 7 the one reader `RL-1361` requires (two readers of one schema would diverge, `CLAUDE.md` §2), and lets Slice 4 write the movers from the frame it already has. (b) duplicates the reader against `RL-1361`. (c) changes a signature `RL-1394` just fixed | decision point | yes — Tasks 1, 3, 4, 5 | RL-1402: **(a), amended to four functions** — `read_portfolio` (refuses at the call), `dislocation_frame` (sorted by `quote_id`, adds `change_minor`, refuses a colliding column), `select_movers` (exact integer membership; order \|pct\| desc, \|change_minor\| desc, `quote_id` asc), `summarise_dislocation`; `PortfolioFrameError.code = "VALIDATION_FAILED"` |
| DP-S2-2 | **Which policies are compared?** A policy can be `quoted`, `declined` or `"error"` in each pass (`ScoringOutcome`), and a quoted policy can have a baseline payable premium of 0. FR-263 does not say which enter the figures, and §4.6 has no field for the others | (a) **Quoted in both passes** enter every figure; every other policy is counted in `errors[]` — an `"error"` row under its `error_code` (the baseline pass's where both error), a decline under the literal `declined`. (b) **Quoted in both** enter every figure; a new required §4.6 field `outcomes` counts `quoted_both`, `quoted_to_declined`, `declined_to_quoted`, `declined_both`, `error` (summing to `policy_count`) and `zero_baseline`; `errors[]` keeps only real error codes, each with a `sample` of up to 10 `quote_id`s. (c) **Refuse the run** unless every policy is quoted in both | **(b).** A policy that moves from quoted to declined is the dislocation an approver most needs to see, and (a) hides it in an error list under a code that is not an error. (c) makes one decline fail a whole book. Under (b) a quoted-both policy with a zero baseline enters the money totals and `by_ladder_rung` but has no percentage, so it is outside the bands, the segment means and the movers, and counted in `zero_baseline`. Cost: a contract field (`dislocation-run.schema.json`, hand-authored, not shared with WK-674 S2) and a §4.6 note (P2) | decision point | yes — Tasks 1, 2, 5 | RL-1402: **(b), amended** — `outcomes`; the compared set (money, segments, rungs) and the banded set (bands, movers); `errors` sums to `outcomes.error`, `sample` as `{"quote_id"}` objects |
| DP-S2-3 | **How is an average change and a share computed?** FR-263 asks for the average change overall, by segment and per band, and exposure shares; §4.6 gives `change_pct`, `mean_change_pct` and `exposure_share` as JSON numbers | (a) **Ratio of sums:** a mean change is Σ(candidate − baseline) ÷ Σ baseline × 100 over the policies in the group, computed exactly (a `Fraction` of integers) and quantised once to 2 decimal places, `ROUND_HALF_EVEN`; an exposure share is Σ exposure in the group ÷ Σ exposure of the compared set, quantised to 6 places; `exposure_years` is the exact `Decimal` sum, quantised to 6 places. (b) Unweighted mean of per-policy percentages. (c) Exposure-weighted mean of per-policy percentages | **(a).** §4.6's own example satisfies it: (42 698 300 00 − 41 882 100 00) ÷ 41 882 100 00 = 1.9488…%, printed `1.95`. One definition then serves overall, segment and band figures, it is exact on the integers, and a few tiny premiums cannot dominate it, which they can in (b) and (c). The 6-place exposure quantum follows `profile.py`'s `_stored_exposure` (FR-62) | decision point | yes — Tasks 1, 5 | RL-1402: **(a), amended** — exact `Fraction`, rounded once with `round(…, n)`; a zero denominator is null |
| DP-S2-4 | **Bands and movers: membership, labels, defaults, and the field names `RL-1394` T7 leaves to Slice 2.** `band_edges_pct` and `mover_threshold_pct` are fixed as names but not as rules; §4.6's example labels are `"< -10%"` … `"> +10%"` | (a) **Half-open bands** `[lo, hi)` on the exact per-policy change (candidate − baseline) ÷ baseline × 100, compared as a `Fraction` against `Decimal` edges; labels `"< e₀%"`, `"e₍ᵢ₎% to e₍ᵢ₊₁₎%"`, `"≥ eₙ%"` with an explicit sign on positive edges; every band listed, empty ones with `policies` 0; a mover is a compared policy with \|change\| ≥ `mover_threshold_pct`; both fields **required** (no default), `band_edges_pct` strictly increasing with at least one edge, `mover_threshold_pct` positive; names kept as T7 wrote them; the example's top label is amended to `"≥ +10%"` by the dated note. (b) Bands **closed toward zero**, so the example's labels stand unchanged (below 0 `[lo, hi)`, from 0 up `(lo, hi]`, and 0 itself in `"0% to +5%"`). (c) As (a), plus a separate `"0%"` band for unchanged policies | **(a).** One rule, stated in one sentence, with no special case at zero; the only cost is one example label. (b) reproduces the example but needs a three-part rule. (c) is a presentational choice WK-675 can make from the data. No default, because any default would be a pricing judgement this slice has no source for | decision point | yes — Tasks 1, 2, 5 | RL-1402: **(a)** — half-open bands, label format stated, mover ≥ threshold, both fields required; `"≥ +10%"` |
| DP-S2-5 | **"The ladder rung at which the change originated" (FR-264).** `PL-1267` names "the first ladder rung at which the two premiums differ", but not what is compared, nor what `by_ladder_rung.contribution_pct` measures | (a) Walk `LadderRungName`'s order; a rung differs where its `unrounded_minor` differs between the two ladders (its `value_minor` where either lacks `unrounded_minor`), and a rung present in one ladder only differs; the first differing rung is the policy's origin; `contribution_pct[r]` = Σ(candidate − baseline) over compared policies whose origin is r ÷ Σ baseline × 100 (DP-S2-3's arithmetic); rows only for rungs with at least one policy, in ladder order. The unrounded contributions sum exactly to the total change. (b) Per-rung deltas: Σ(candidate rung − baseline rung) ÷ Σ baseline per rung (not additive: the rungs compound). (c) As (a), but comparing `value_minor` only | **(a).** It is `PL-1267`'s reading, made precise, and its parts add up to `totals.change_pct`. (c) misses a change smaller than one minor unit at an early rung that surfaces later; `unrounded_minor` is the column that replays (`LadderRung` docstring, FR-248). (b) does not add up | decision point | yes — Tasks 1, 4, 5 | RL-1402: **(a), amended** — a rung differs on presence, `value_minor` or `Decimal` `unrounded_minor`; the integer identity tested; the example's rungs corrected |
| DP-S2-6 | **What is a "segment" / "Factor available on the portfolio dataset"?** `DislocationSpec.segments` is "the Factors FR-263 averages by"; §4.6's `by_segment` item is `factor`, `level` (string, required), `policies`, `mean_change_pct`, `exposure_share` | (a) **A portfolio column name.** One `by_segment` row per (segment, distinct value) over the compared set, in `segments` order then by level; the level is the value's canonical string (`str` for strings and integers, ISO for dates, `true`/`false` for booleans); null values form one level reported as JSON `null`, so the contract's `level` widens to string-or-null; a segment column absent from the portfolio is a `PortfolioFrameError` naming it; a banded Factor is materialised as a column at data preparation. (b) **A Factor reference** resolved with `resolve_factors`, which needs a `factors` parameter on `dislocate` and Slice 4 loading them. (c) As (a), with nulls dropped and counted nowhere | **(a).** It keeps T7's signature, matches §4.6's example (`driver_age_band` reads as a column), and FR-264's "available on the portfolio dataset" reads as a column. (b) is a later amendment if analysts need bands they cannot materialise. (c) silently shrinks a segment, which an approver cannot see | decision point | yes — Tasks 1, 2, 3, 5 | RL-1402: **(a), amended** — a column of a stated dtype; levels in native order, null a level, last |
| DP-S2-7 | **What dtype may `exposure_years` have?** §4.8 says "decimal"; the profiler treats stored exposure as a float (P11) | (a) **Integer, `Decimal` or `Float64`**; a `Float64` value becomes `Decimal(str(round(v, 6)))` row by row (`_stored_exposure`'s rule, FR-62), the others are exact; any other dtype is a `PortfolioFrameError` naming the column and its dtype. (b) **Integer or `Decimal` only**; a `Float64` column is refused. (c) `Float64` via `Decimal(repr(v))`, unrounded | **(a).** "Decimal" then describes how the column is read, not how a parquet file must store it, and freMTPL2-shaped data needs no conversion step. (b) refuses the public example portfolio, whose seed declares `exposure_years` a float (`examples/fremtpl2/seed.py:56`). (c) puts binary noise into a figure the profiler already rounds | decision point | yes — Tasks 1, 3 | RL-1402: **(a), amended** — int, decimal or float (rounded to 6 places); NaN and infinity refused |
| DP-S2-8 | **Where do the types live, and does this slice export them?** | (a) A new module `packages/model-schema/src/model_schema/dislocation.py`; imported by `analysis.py` as `from model_schema.dislocation import …`; **not** exported from `model_schema/__init__.py` in this slice (Slice 4 exports and registers it for generation); `DislocationRun` has no attribution properties (Slice 3 adds them, `PL-1267` "Deviation from the adopted cut"). (b) Append to `model_schema/rating.py` and export now | **(a), decided.** `__init__.py` is edited by WK-674 S2 (26 lines on `origin/sl-1256-environment-and-deployment-record` at `14c7e805`), so exporting here would make the two slices edit one existing definition (`__all__`), which serialises them under `RL-1263` :89. Nothing requires the export (P13). A new module touches no existing class | scope | no | PL-1403 (planner, slice design) |

## Tasks

### Task 0: Preconditions

**Files:** the slice ledger (`docs/ledgers/LG-<working id>-….md`, the executor's).

- [ ] **Step 1:** Confirm the activation needs (Status) at the dispatch tree:
  `git -C <worktree> log -1 --format='%H %aI' origin/main`; the ruling's id resolves
  (`grep -l '^id: RL-<n>' docs/rulings/*.md`); this plan is `active`; `SL-1386` is `active`.
- [ ] **Step 2:** `uv sync --all-packages` (fresh worktree; `dev-commands`).
- [ ] **Step 3:** Baseline the four docs checks and `uv run pytest packages/pricing-core/tests/test_rating_score_batch.py -q`
  on the untouched tree; record rc and the summary lines in the ledger.
- [ ] **Step 4:** Copy the ruling's texts S1 to S5 ("The exact texts") into the ledger with the
  ruling's minted id and line range. Every later step applies the ledger copy, never this plan's
  Appendix. **Then check one reading against the copy.** This plan builds the banded set as the
  quoted-both policies with `baseline_minor > 0` (RL-1402, Amendment N2): a
  negative payable premium is not excluded by type (`MoneyMinor` is a strict `int`,
  `money.py`; "no-negative-premium" is a Regression Suite property in `03`'s glossary, not a
  runtime bound), and with a negative baseline the mover inequality holds for every change and
  the percentage's sign inverts. RL-1402, Amendment N2 resolves this case: the S3
  copied into the ledger is N2-a's text (and S4 edit 2 is N2-b's, S5 edit 1's `outcomes` is
  N2-c's), each in place of the text it replaces. Confirm the ledger copy defines the banded set
  as the compared policies with a baseline payable premium above 0.
- [ ] **Step 5:** Record the dtype of `exposure_years` in the public freMTPL2 portfolio the seed
  builds (`examples/fremtpl2/seed.py`; read it, do not guess), and quote the line. RL-1402 DP-S2-7 admits a `Float64` column (read rounded to 6 places), so no dtype stops
  the slice; the line is the input for Task 3's positive float-read test.
- [ ] **Step 6:** `gh pr list --state open` and read anything ruling on `03` §4.6, §4.8, §5.2,
  `score_batch` or the portfolio frame since this plan's tree (README convention 4); name the
  commit read.

### Task 1: Spec — the ruled texts

**Files:**
- Modify: `docs/specs/03-rating-engine.md` §5.2 (S1 and S2) and §4.6 (S3 and S4), as RL-1402 places them
- Modify: `docs/contracts/schemas/dislocation-run.schema.json` (S5: `outcomes`, six ratios
  nullable, `level` nullable, `errors.items`)

**Interfaces:** Produces the names Tasks 2–5 use, exactly as S1 and S2 spell them.

Every text comes from the ledger copy (Task 0 Step 4). `<date>` is the merge date; `RL-<n>` is
the ruling's minted id. Locators below are at `7e2ee2ba`; re-read them at the dispatch tree.

- [ ] **Step 1:** Apply **S1** to the `# pricing_core/rating/analysis.py` block of `03` §5.2: the
  four signatures, inserted directly after `dislocate`'s two lines (`03:986-987`) and before
  `async def derive_changes`.
- [ ] **Step 2:** Apply **S2**, a new paragraph directly after the `DislocationSpec` types
  paragraph (`03:1052`). The types paragraph itself is not edited.
- [ ] **Step 3:** Apply **S3**, a new dated block directly after §4.6's JSON example's closing
  fence and before `### 4.7` (`03:559` at `7e2ee2ba`), and **S4**'s five edits to that example.
  Not after the existing dated note at `03:512`: the ruling places it after the example.
- [ ] **Step 4:** Apply **S5** to the hand-authored contract in the **same commit** as Step 3
  (`RL-1394` DP-S1-7's reason: spec and contract must not disagree). Check the file parses with
  no duplicate key (`contract-schema`): `python3 -c "import json,sys; json.load(open(sys.argv[1]), object_pairs_hook=lambda p: (len(p)==len(dict(p)) or sys.exit('dup')) and dict(p))" docs/contracts/schemas/dislocation-run.schema.json`.
  Then confirm the six nullable places and no other `number` changed: `git diff -U0 origin/main -- docs/contracts/schemas/dislocation-run.schema.json | grep -c '^+.*"null"'`
  prints 7, one added line for each of the six ratios and `level` (each is on its own line of the
  contract at `7e2ee2ba`: `:23`, `:34`, `:35`, `:47`, `:49`, `:50`, `:60`); quote it.
- [ ] **Step 5:** `python3 scripts/audit-docs.py`; expect only the working-id check 31 (the
  ledger's working id) and check 39 (INDEX, regenerated in Task 7).
- [ ] **Step 6:** Commit: `docs(specs): WK-673 S2 — the Dislocation Run's arithmetic, per RL-<n>`.

### Task 2: `model-schema` — `DislocationSpec` and `DislocationRun`

**Files:**
- Create: `packages/model-schema/src/model_schema/dislocation.py`
- Test: `packages/model-schema/tests/test_dislocation.py`

**Interfaces:**
- Produces: `ChangeGroup`, `DislocationSpec`, `DislocationTotals`, `DislocationOutcomes`,
  `DislocationBand`, `SegmentSlice`, `RungContribution`, `ErrorSample`, `ErrorTally`,
  `DislocationRun`, all `frozen=True, extra="forbid"` (RL-1402 DP-S2-2 rules
  `outcomes` in).

- [ ] **Step 1: Write the failing tests.**

```python
"""DislocationSpec and DislocationRun (03 §4.6, §5.2; WK-673 Slice 2, PL-1403)."""

from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

import pytest
from pydantic import ValidationError

from model_schema.dislocation import DislocationRun, DislocationSpec

_CONTRACT = (
    Path(__file__).resolve().parents[3] / "docs/contracts/schemas/dislocation-run.schema.json"
)
_SLICE_3_FIELDS = {"attribution", "derived_changes", "change_groups", "attribution_summary"}


def _spec(**overrides: object) -> DislocationSpec:
    body: dict[str, object] = {
        "baseline_ref": "rating_version:motor-gb@26",
        "candidate_ref": "rating_version:motor-gb@27",
        "portfolio_dataset_version_id": "00000000-0000-0000-0000-000000000001",
        "purpose": "new_business",
        "as_at": "2026-10-01",
        "segments": ["driver_age_band"],
        "band_edges_pct": ["-10", "-5", "0", "5", "10"],
        "mover_threshold_pct": "10",
    }
    body.update(overrides)
    return DislocationSpec.model_validate(body)


@pytest.mark.req("FR-263")
def test_spec_refuses_a_purpose_the_frame_cannot_stamp() -> None:
    with pytest.raises(ValidationError, match="purpose"):
        _spec(purpose="mid_term_adjustment")


@pytest.mark.req("FR-263")
def test_spec_refuses_band_edges_that_do_not_increase() -> None:
    with pytest.raises(ValidationError, match="band_edges_pct"):
        _spec(band_edges_pct=["0", "-5"])


@pytest.mark.req("FR-263")
def test_spec_refuses_a_float_threshold() -> None:
    with pytest.raises(ValidationError, match="float"):
        _spec(mover_threshold_pct=10.0)


@pytest.mark.req("FR-264")
def test_spec_refuses_a_repeated_segment() -> None:
    with pytest.raises(ValidationError, match="segments"):
        _spec(segments=["driver_age_band", "driver_age_band"])


@pytest.mark.req("FR-263")
def test_outcomes_must_sum_to_policy_count() -> None:
    from model_schema.dislocation import DislocationOutcomes

    outcomes = DislocationOutcomes(
        quoted_both=3, quoted_to_declined=1, declined_to_quoted=0,
        declined_both=0, error=1, zero_baseline=0, negative_baseline=0,
    )
    with pytest.raises(ValidationError, match="policy_count"):
        DislocationRun.model_validate({
            "baseline_ref": "rating_version:motor-gb@26",
            "candidate_ref": "rating_version:motor-gb@27",
            "portfolio_dataset_version_id": "00000000-0000-0000-0000-000000000001",
            "policy_count": 6,  # 3 + 1 + 0 + 0 + 1 = 5
            "exposure_years": "1.000000",
            "totals": {"baseline_premium_minor": 1, "candidate_premium_minor": 1, "change_pct": None},
            "outcomes": outcomes.model_dump(),
            "distribution": [{"band": "< 0%", "policies": 0, "exposure_share": None, "mean_change_pct": None}],
        })


@pytest.mark.req("FR-263")
def test_dislocation_run_fields_match_the_hand_authored_contract() -> None:
    contract = json.loads(_CONTRACT.read_text())
    emitted = DislocationRun.model_json_schema(by_alias=True)
    assert set(emitted["properties"]) <= set(contract["properties"])
    assert set(contract["properties"]) - set(emitted["properties"]) == _SLICE_3_FIELDS
    assert set(emitted.get("required", [])) == set(contract["required"])
```

  Extend the last test, in the same function, to compare each item object the contract defines
  (`totals`, `outcomes`, `distribution.items`, `by_segment.items`, `by_ladder_rung.items`,
  `errors.items`, `errors.items.sample.items`) by property names and `required`, and, for the
  six ratios RL-1402 S5 makes nullable and for `level`, that the emitted schema
  admits `null` (an `anyOf` with `{"type": "null"}`), resolving the emitted `$ref`s
  through `emitted["$defs"]`. Mirror the walker style of `backend/tests/test_contracts.py`
  rather than inventing one; do not import it (backend tests are not importable from here).

- [ ] **Step 2: Run to verify they fail.** `uv run pytest packages/model-schema/tests/test_dislocation.py -q`
  Expected: collection error, `ModuleNotFoundError: No module named 'model_schema.dislocation'`.
  A failure for any other reason is a plan defect; report it.
- [ ] **Step 3: Implement** `dislocation.py`. Field names and requiredness are §4.6's and the
  contract's as S5 leaves it; the band, mover, outcome and level rules are RL-1402 (working
  id)'s. Skeleton, as ruled:

```python
"""The Dislocation Run's spec and result (03 §4.6, §5.2; FR-263, FR-264).

WK-673 Slice 2 defines the run without its attribution part; Slice 3 adds `derived_changes`,
`change_groups`, `attribution` and `attribution_summary` (PL-1267, "Deviation from the adopted
cut"). Money is integer minor units; percentages and shares are derived views (03 §4.6).
"""

from __future__ import annotations

from datetime import date
from typing import Annotated, Literal, Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from model_schema.money import DecimalStr, MoneyMinor
from model_schema.refs import ArtifactRef

_FROZEN = ConfigDict(frozen=True, extra="forbid")


class ChangeGroup(BaseModel):
    """One analyst group of derived changes (FR-1399); partition-checked by Slice 3."""

    model_config = _FROZEN
    name: str
    changes: Annotated[list[str], Field(min_length=1)]


class DislocationSpec(BaseModel):
    """What a run compares and how it reports (03 §5.2's types paragraph, RL-1394 T7)."""

    model_config = _FROZEN
    baseline_ref: ArtifactRef
    candidate_ref: ArtifactRef
    portfolio_dataset_version_id: UUID
    purpose: Literal["new_business", "renewal"]
    as_at: date
    segments: list[str] = []
    band_edges_pct: Annotated[list[DecimalStr], Field(min_length=1)]
    mover_threshold_pct: DecimalStr
    change_groups: Annotated[list[ChangeGroup], Field(max_length=6)] | None = None

    @model_validator(mode="after")
    def _edges_increase_and_threshold_positive(self) -> Self:
        if len(set(self.segments)) != len(self.segments):
            raise ValueError("segments must be distinct")  # DP-S2-6
        edges = self.band_edges_pct
        if any(b <= a for a, b in zip(edges, edges[1:], strict=False)):
            raise ValueError("band_edges_pct must be strictly increasing")
        if self.mover_threshold_pct <= 0:
            raise ValueError("mover_threshold_pct must be positive")
        return self


_Share = Annotated[float, Field(ge=0, le=1)]
_Count = Annotated[int, Field(ge=0)]


class DislocationTotals(BaseModel):
    model_config = _FROZEN
    baseline_premium_minor: MoneyMinor
    candidate_premium_minor: MoneyMinor
    change_pct: float | None  # required, null when the denominator is 0 (DP-S2-3)


class DislocationOutcomes(BaseModel):
    """Each policy once by its two outcomes; the first five sum to policy_count (DP-S2-2)."""

    model_config = _FROZEN
    quoted_both: _Count
    quoted_to_declined: _Count
    declined_to_quoted: _Count
    declined_both: _Count
    error: _Count
    zero_baseline: _Count
    negative_baseline: _Count


class DislocationBand(BaseModel):
    model_config = _FROZEN
    band: str
    policies: _Count
    exposure_share: _Share | None
    mean_change_pct: float | None


class SegmentSlice(BaseModel):
    model_config = _FROZEN
    factor: str
    level: str | None  # required; null is a level (DP-S2-6)
    policies: _Count
    mean_change_pct: float | None
    exposure_share: _Share | None = None


class RungContribution(BaseModel):
    model_config = _FROZEN
    rung: LadderRungName
    contribution_pct: float | None


class ErrorSample(BaseModel):
    model_config = _FROZEN
    quote_id: str


class ErrorTally(BaseModel):
    model_config = _FROZEN
    code: str
    count: Annotated[int, Field(ge=1)]
    sample: Annotated[list[ErrorSample], Field(max_length=10)] | None = None


class DislocationRun(BaseModel):
    """03 §4.6 without the attribution part (Slice 3)."""

    model_config = _FROZEN
    baseline_ref: ArtifactRef
    candidate_ref: ArtifactRef
    portfolio_dataset_version_id: UUID
    job_id: UUID | None = None
    policy_count: Annotated[int, Field(ge=0)]
    exposure_years: DecimalStr
    totals: DislocationTotals
    outcomes: DislocationOutcomes
    distribution: Annotated[list[DislocationBand], Field(min_length=1)]
    by_segment: list[SegmentSlice] = []
    by_ladder_rung: list[RungContribution] = []
    largest_movers_blob: str | None = None
    errors: list[ErrorTally] = []

    @model_validator(mode="after")
    def _outcomes_sum_to_policy_count(self) -> Self:
        o = self.outcomes
        if o.quoted_both + o.quoted_to_declined + o.declined_to_quoted + o.declined_both + o.error != self.policy_count:
            raise ValueError("outcomes must sum to policy_count")
        if sum(e.count for e in self.errors) != o.error:
            raise ValueError("errors counts must sum to outcomes.error")
        if sum(b.policies for b in self.distribution) != o.quoted_both - o.zero_baseline - o.negative_baseline:
            raise ValueError("distribution policies must equal quoted_both - zero_baseline - negative_baseline")
        return self
```

  Import `LadderRungName` from `model_schema.scoring`. `job_id` and `largest_movers_blob` stay
  `None` from `pricing-core`; Slice 4's handler sets them (`model_copy(update=…)`). Confirm
  `DecimalStr` refuses a float (`money.py:76-90`). The `None` ratios are required keys whose
  value may be null (S5), not optional fields, so the `required` comparison still holds.
- [ ] **Step 4: Run to verify they pass**, then rename one field (`policy_count` → `policies_count`)
  and confirm the contract-match test fails naming it; restore. Quote both runs in the ledger.
- [ ] **Step 5: Commit** `feat(model-schema): WK-673 S2 — DislocationSpec and DislocationRun (03 §4.6)`.

### Task 3: the portfolio reader

**Files:**
- Create: `packages/pricing-core/src/pricing_core/rating/analysis.py`
- Test: `packages/pricing-core/tests/test_rating_dislocation.py`

**Interfaces:**
- Consumes: `DislocationSpec` (Task 2).
- Produces (names as RL-1402 S1 and S2 spell them):
  `class PortfolioFrameError(ValueError)` with the class attribute `code = "VALIDATION_FAILED"`,
  and `def read_portfolio(portfolio: pl.LazyFrame, *, segments: Sequence[str] = ()) -> pl.LazyFrame`.
  It checks the frame **when it is called** (its counts are collected in one `select` inside the
  call), so the refusal reaches the caller, Slice 7 included, before anything is built on the
  result. It returns the frame with every column kept and `exposure_years` read per DP-S2-7 as
  ruled: an integer or decimal dtype exactly, a float dtype row by row as
  `Decimal(str(round(v, 6)))`, as a `pl.Decimal` column of scale 6.

- [ ] **Step 1: Write the failing tests** (one per §4.8 refusal; each asserts the column name and
  the count are in the message and that **no portfolio value** is):

```python
"""The Dislocation Run (03 FR-263, FR-264; §4.8's portfolio frame). WK-673 Slice 2, PL-1403."""

from __future__ import annotations

import polars as pl
import pytest

from decimal import Decimal

from pricing_core.rating.analysis import PortfolioFrameError, read_portfolio


def _book(**columns: list[object]) -> pl.LazyFrame:
    base: dict[str, list[object]] = {
        "quote_id": ["Q1", "Q2", "Q3"],
        "exposure_years": [1.0, 0.5, 0.0],
        "driver_age": [34, 22, 70],
    }
    base.update(columns)
    return pl.DataFrame(base, strict=False).lazy()


@pytest.mark.req("FR-263")
def test_read_portfolio_refuses_a_purpose_column_by_name() -> None:
    """RL-1394: a portfolio column named `purpose` is refused, never silently overridden."""
    with pytest.raises(PortfolioFrameError, match="purpose") as exc:
        read_portfolio(_book(purpose=["renewal", "renewal", "renewal"]))  # at the call
    assert exc.value.code == "VALIDATION_FAILED"
    assert "renewal" not in str(exc.value)


@pytest.mark.req("FR-263")
def test_read_portfolio_refuses_a_null_exposure_naming_the_column_and_count() -> None:
    """RL-1394 / RL-1361 §E: a null exposure is refused, never read as 0."""
    with pytest.raises(PortfolioFrameError, match=r"exposure_years.*\b1\b") as exc:
        read_portfolio(_book(exposure_years=[1.0, None, 0.5]))
    assert exc.value.code == "VALIDATION_FAILED"


@pytest.mark.req("FR-263")
def test_read_portfolio_refuses_a_nan_exposure() -> None:
    """RL-1402 DP-S2-7: a NaN is not null in Polars and passes `< 0`; it is refused with the nulls."""
    with pytest.raises(PortfolioFrameError, match=r"exposure_years.*\b2\b"):
        read_portfolio(_book(exposure_years=[float("nan"), float("inf"), 0.5]))


@pytest.mark.req("FR-264")
def test_read_portfolio_refuses_a_float_segment_column_naming_its_dtype() -> None:
    """RL-1402 DP-S2-6: a float level has no stable string."""
    with pytest.raises(PortfolioFrameError, match=r"vehicle_value.*Float64"):
        read_portfolio(_book(vehicle_value=[1.5, 2.5, 3.5]), segments=["vehicle_value"])


@pytest.mark.req("FR-263")
def test_read_portfolio_reads_a_float_exposure_rounded_to_six_places() -> None:
    """RL-1402 DP-S2-7: `_stored_exposure`'s rule (FR-62), the freMTPL2 dtype (Task 0 Step 5)."""
    out = read_portfolio(_book(exposure_years=[0.1234567, 0.5, 0.0])).collect()
    assert out["exposure_years"].to_list()[0] == Decimal("0.123457")
```

  Add, in the same style: a missing `quote_id` column; a null `quote_id`; a duplicated
  `quote_id` (count 2); a missing `exposure_years`; a negative `exposure_years`; `effective_date`
  and `rating_version_ref` columns (one test each, by name); a segment column absent from the
  portfolio (DP-S2-6); an `exposure_years` of a `pl.String` dtype (refused naming the column and
  its dtype, DP-S2-7); each asserting `exc.value.code == "VALIDATION_FAILED"`; and a positive test that
  an undeclared column (`region`) and every §4.8 column survive `read_portfolio` unchanged
  (`RL-1361` §E's frame premise, the reader keeping only declared columns is the broken input).
- [ ] **Step 2: Run to verify they fail.** `uv run pytest packages/pricing-core/tests/test_rating_dislocation.py -q`
  Expected: `ModuleNotFoundError: No module named 'pricing_core.rating.analysis'`.
- [ ] **Step 3: Implement** `PortfolioFrameError` (with `code = "VALIDATION_FAILED"`) and
  `read_portfolio`: from `portfolio.collect_schema()`, check the reserved names (`purpose`,
  `effective_date`, `rating_version_ref`) first, then the dtypes: `exposure_years` an integer,
  decimal or float dtype; each segment present and a string, categorical, enum, integer,
  boolean or date dtype (any other dtype refused naming the column and its dtype). Then, in one
  `select` collected inside the call, the counts: `quote_id` (present, null count, duplicate
  count via `pl.col("quote_id").is_duplicated().sum()`) and `exposure_years` (null count plus,
  for a float dtype, `is_nan() | is_infinite()` count, as one "null" count; negative count).
  Messages name the column and the count, or the column and its dtype, only. Return the lazy
  frame with `exposure_years` converted as Produces states.
- [ ] **Step 4: Show each refusal red on broken input.** For the two `RL-1394` tests, comment out
  the `purpose` check, and replace the null-exposure check with `fill_null(0)`; for the NaN test,
  remove the `is_nan() | is_infinite()` term; for the at-the-call property, move the count
  `select` into a `map_batches` evaluated only at `.collect()` and show the null-exposure test
  failing with `DID NOT RAISE` (it calls `read_portfolio` and never collects). Run; quote each failure in the ledger; restore; run green.
- [ ] **Step 5: Commit** `feat(rating): WK-673 S2 — the portfolio reader (03 §4.8)`.

### Task 4: the two passes and the per-policy frame

**Files:**
- Modify: `packages/pricing-core/src/pricing_core/rating/analysis.py`
- Test: `packages/pricing-core/tests/test_rating_dislocation.py`

**Interfaces:**
- Consumes: `read_portfolio` (Task 3); `score_batch(bundle: CompiledBundle, frame: pl.LazyFrame, *, chunk_rows: int = 100_000, progress: ProgressCallback | None = None) -> pl.LazyFrame` (`score.py:1135-1141`, unchanged).
- Produces: `def dislocation_frame(baseline: CompiledBundle, candidate: CompiledBundle, portfolio: pl.LazyFrame, spec: DislocationSpec) -> pl.DataFrame`
  (RL-1402 DP-S2-1 and S2). It calls `read_portfolio(portfolio, segments=spec.segments)`
  before any rating, and returns one row per policy, **sorted by `quote_id`**, with the columns in
  S2's order: `quote_id`; `baseline_outcome`, `candidate_outcome` (strings); `baseline_minor`,
  `candidate_minor` (`Int64`, the `payable_premium` rung's `value_minor`, null unless that pass
  quoted); `change_minor` (`Int64`, `candidate_minor − baseline_minor`, null unless both passes
  quoted); `baseline_error_code`, `candidate_error_code`; `origin_rung` (string, null unless both
  passes quoted and a rung differs); then every portfolio column, in the portfolio's order.
  Before any rating it raises `PortfolioFrameError` for a portfolio column named as one of its
  own columns other than `quote_id` (`baseline_outcome`, `candidate_outcome`, `baseline_minor`,
  `candidate_minor`, `change_minor`, `baseline_error_code`, `candidate_error_code`,
  `origin_rung`), naming the column (plan audit N2).
- Origin rule (DP-S2-5 as ruled): walk `RUNG_ORDER` (`pricing_core/rating/ladder.py:52-63`);
  the origin is the first rung that is present in one ladder only, **or** has a different
  `value_minor`, **or** a different `unrounded_minor` compared as `Decimal` values, never as
  strings (`Decimal("100") == Decimal("100.0")`; plan audit N6). A policy with no differing rung
  has `origin_rung` null and, as the ruling proves, `change_minor` 0.

- [ ] **Step 1: Write the failing tests.** Fixtures: import `_algorithm_payload`, `_compiled`,
  `_version` and the fake resolver from `test_rating_score` as `test_rating_score_batch.py:24-25`
  does. `_compiled` takes no algorithm argument, so write one local helper,
  `_compiled_from(algorithm: dict[str, object]) -> CompiledBundle`, that builds a `draft`
  `_version` around the given payload and compiles it exactly as `_compiled` does (plan audit
  N7). Build the candidate from a copy of `_algorithm_payload()` with one changed value (for
  example a rate-table relativity the fixture's `_rate_table_payload` serves; read
  `test_rating_runtime.py` and pick the smallest change that moves the premium), and a second
  candidate that changes **only one rung's rounding** (its `dp` or mode), so that rung's
  `value_minor` moves while its `unrounded_minor` does not. For the
  undeclared-read fixture: an algorithm whose one expression step reads `secret_loading`, a name
  absent from its `input_contract`; build it with `compile_bundle` if that still accepts it at the
  dispatch tree (P14), otherwise as `Bundle` via `to_jdm` and `bundle_hash` and hydrate it with
  `load_bundle` (the pre-enforcement case `RL-1394` names). Tests, all `req("FR-263")` unless
  noted:
  - `test_dislocation_undeclared_column_never_reaches_the_engine` — the portfolio carries
    `secret_loading` with a value that would change the premium; each pass's premium equals the
    premium of the same row with the column absent (`RL-1394`'s first Slice-2 violation).
  - `test_dislocation_undeclared_billing_named_column_refuses_no_row` — the portfolio carries
    `instalment_count`, undeclared; no row of either pass is an `"error"` row (P4).
  - `test_dislocation_stamps_purpose_date_and_each_passes_own_ref` — spy on `score_batch`
    (`monkeypatch.setattr(analysis, "score_batch", spy)`) and assert each pass's input frame has
    `purpose == spec.purpose`, `effective_date == spec.as_at.isoformat()`, and
    `rating_version_ref == str(spec.baseline_ref)` (resp. candidate) on every row.
  - `test_dislocation_each_pass_sees_only_its_own_contract` — a candidate declaring a new input
    `vehicle_group` the baseline does not: the spy shows the baseline pass's frame has no
    `vehicle_group` column and the candidate's has it.
  - `test_dislocation_missing_declared_input_is_that_rows_error` — a declared name absent from
    the portfolio gives `"error"` rows with `INPUT_CONTRACT_VIOLATION`, not a run refusal (§4.8).
  - `test_dislocation_frame_refuses_a_colliding_portfolio_column` — a portfolio column named
    `origin_rung` raises `PortfolioFrameError` naming it, with `code == "VALIDATION_FAILED"`,
    and the `score_batch` spy records **no call** (refused before any rating).
  - `test_dislocation_frame_is_sorted_by_quote_id_with_change_minor` — a portfolio given in
    the order `Q3, Q1, Q2` comes back `Q1, Q2, Q3`; `change_minor` equals
    `candidate_minor − baseline_minor` as `Int64` on quoted-both rows and is null elsewhere;
    the column order is S2's.
  - `test_dislocation_frame_origin_rung_is_the_first_differing_rung` — `req("FR-264")`; three
    cases: the relativity candidate gives the rung the relativity feeds; the rounding-only
    candidate gives the rung whose rounding changed (red against a rule comparing
    `unrounded_minor` alone, which gives null); and two ladders built by hand and passed to
    `analysis._origin_rung` with one rung's `unrounded_minor` written `"100"` in one and
    `"100.0"` in the other and nothing else different give null (red against a string
    comparison, which gives that rung).
- [ ] **Step 2: Run to verify they fail** (`ImportError: cannot import name 'dislocation_frame'`).
- [ ] **Step 3: Implement.** For each pass: `cols = ["quote_id", *(f.name for f in bundle.algorithm.input_contract if f.name in portfolio_columns)]`;
  `frame = portfolio.select(cols).with_columns(pl.lit(spec.purpose).alias("purpose"), pl.lit(spec.as_at.isoformat()).alias("effective_date"), pl.lit(str(ref)).alias("rating_version_ref"))`;
  `scored = score_batch(bundle, frame).collect()`. The portfolio is first read once with
  `read_portfolio(portfolio, segments=spec.segments)`, after the collision check. Extract the
  payable premium from
  `premium_ladder_json` by parsing the rung list (`json.loads`) and taking the
  `"payable_premium"` rung's `value_minor` as `int` — never via a float column. Join the two
  scored frames on `quote_id` and join the pass-through columns back from the read portfolio by
  `quote_id`, then `sort("quote_id")`. Compute `origin_rung` by the origin rule above in one
  private helper, `_origin_rung(baseline: Sequence[LadderRung], candidate: Sequence[LadderRung]) -> str | None`,
  over the two parsed ladders, comparing `Decimal(r.unrounded_minor)` values. A
  `quoted` row with no `payable_premium` rung is a defect: raise
  `ValueError("dislocation: a quoted row carries no payable_premium rung")`.
- [ ] **Step 4: Show the two `RL-1394` tests red.** Replace the projection with the whole portfolio
  (`portfolio.drop([])`); run; both fail (the premium moves, and every row is refused
  `INPUT_CONTRACT_VIOLATION`); quote both; restore; green.
- [ ] **Step 5: Commit** `feat(rating): WK-673 S2 — the two passes, projected per contract (03 §4.8)`.

### Task 5: the summary — `select_movers`, `summarise_dislocation` and `dislocate`

**Files:**
- Modify: `packages/pricing-core/src/pricing_core/rating/analysis.py`
- Test: `packages/pricing-core/tests/test_rating_dislocation.py`

**Interfaces:**
- Consumes: `dislocation_frame` (Task 4) and its columns, the Task 2 types.
- Produces (RL-1402 S1):
  `def select_movers(frame: pl.DataFrame, spec: DislocationSpec) -> pl.DataFrame`,
  `def summarise_dislocation(frame: pl.DataFrame, spec: DislocationSpec) -> DislocationRun`
  and `def dislocate(baseline: CompiledBundle, candidate: CompiledBundle, portfolio: pl.LazyFrame, spec: DislocationSpec) -> DislocationRun`
  (T7), defined as `summarise_dislocation(dislocation_frame(baseline, candidate, portfolio, spec), spec)`.

**The sets, as this plan builds them** (RL-1402 DP-S2-2, S3, with its Amendment N2
and audit-9734 N3 stated):
- the **compared set** is the rows with both outcomes `quoted`; `totals`, `by_segment` and
  `by_ladder_rung` are over it;
- the **banded set** is the compared rows with `baseline_minor > 0`. For `baseline_minor ≥ 0`
  this is S3's "the compared set less its `zero_baseline` policies". A negative baseline is
  outside it, and counted in `outcomes.negative_baseline` (RL-1402, Amendment
  N2; `zero_baseline` counts `baseline_minor == 0` only): it enters
  the money totals, `by_segment` and `by_ladder_rung`, and no band and no mover (Task 0 Step 4
  carries the spec-text check). Bands and movers are over the banded set only;
- an **`exposure_share`** is the group's Σ `exposure_years` ÷ the Σ over the set the group is
  part of (S3): **a band's denominator is the banded set's Σ `exposure_years`**; a segment
  level's is the compared set's (DP-S2-6). Either is `None` when that sum is 0.

**The mover order** (DP-S2-1, `select_movers`): membership is
`100 × |change_minor| ≥ mover_threshold_pct × baseline_minor`, decided on `int`s and
`Fraction(str(spec.mover_threshold_pct))`, over the banded set; the order is
(1) `Fraction(|change_minor|, baseline_minor)` descending, (2) `|change_minor|` descending,
(3) `quote_id` ascending as Python `str`. No cap. It returns the frame's rows in that order,
every column kept.

- [ ] **Step 1: Write the failing tests**, each against a hand-computed figure on a fixture book of
  at least ten policies spanning every band, two segment levels and a null level, one
  `quoted_to_declined`, one `declined_both`, one `"error"`, one `zero_baseline` and one
  negative-baseline policy. Hand-compute every expected figure in the test's docstring from the
  fixture's integers. The mover tests build their frame directly with a local
  `_frame(rows: list[dict[str, object]]) -> pl.DataFrame` that gives S2's columns, so their
  premiums are chosen exactly, without rating. Each test names, in its docstring, the one-line
  mutation of the implementation that turns it red (plan audit N4); Step 4 runs each mutation.
  - `test_dislocation_totals_are_sums_of_per_policy_minor_units` — `req("NFR-496")`; both totals
    are `int` and equal the sums of `baseline_minor` and `candidate_minor` over the compared
    set; mutation: sum over every quoted baseline row.
  - `test_dislocation_change_pct_is_the_ruled_ratio` — `req("FR-263")`; `totals.change_pct`
    equals `float(Decimal(round(Fraction(Σchange, Σbaseline) * 100, 2)))` hand-computed;
    mutation: an unweighted mean of per-policy percentages.
  - `test_dislocation_rounds_each_ratio_once` — `req("FR-263")`; a two-policy group whose exact
    ratio is a half-way case at 2 places under one rounding and not the other (choose the
    integers so `round(Fraction, 2)` and `Decimal(n) / Decimal(d)` at `prec=4` then `quantize`
    differ, and state both values in the docstring); mutation: that two-step conversion.
  - `test_dislocation_bands_count_policies_and_exposure_shares` — `req("FR-263")`; half-open
    `[lo, hi)` with a policy exactly on an edge (in the upper band); labels as S3 prints them
    (`"< -10%"`, `"-10% to -5%"`, …, `"≥ +10%"`); `Σ policies` equals the banded set's size
    (so the `zero_baseline` and negative-baseline policies are in no band), and
    `Σ distribution[].policies == quoted_both − zero_baseline − negative_baseline`
    (RL-1402, Amendment N2); each
    `exposure_share` is over the banded set's Σ `exposure_years`; mutation: the edge test
    `> lo` instead of `≥ lo`, and separately a denominator over the compared set.
  - `test_dislocation_empty_band_mean_is_none` — `req("FR-263")`; a band with no policy has
    `policies == 0` and `mean_change_pct is None`; mutation: return `0.0` for a zero denominator.
  - `test_dislocation_by_segment_reports_each_level` — `req("FR-264")`; per DP-S2-6: one row per
    level in native order with the null level last as `level is None`; `exposure_share` over
    the compared set; mutation: filter nulls out of `by_segment`.
  - `test_dislocation_by_ladder_rung_parts_sum_to_the_total` — `req("FR-264")`; per DP-S2-5 on
    a book holding the relativity candidate's and the rounding-only candidate's changes: rows
    only for originating rungs, in ladder order; **the integer sums of `change_minor` by
    `origin_rung` add up exactly to `candidate_premium_minor − baseline_premium_minor`**; and
    the `Fraction` parts sum exactly to `Fraction(Σchange, Σbaseline) × 100`; mutation: an
    origin comparing `unrounded_minor` alone.
  - `test_dislocation_outcomes_and_errors_are_counted` — `req("FR-263")`; the seven `outcomes`
    figures, with `negative_baseline == 1` on the fixture's negative-baseline policy
    (RL-1402, Amendment N2); the first five sum to `policy_count`; `Σ errors[].count == outcomes.error`; an
    error in both passes is counted under the baseline's code; each `sample` is a list of
    `{"quote_id": …}` objects, the first 10 by `quote_id`; mutation: count a both-pass error
    under both codes.
  - `test_dislocation_movers_are_kept_for_drill_down` — `req("FR-263")`; calls `select_movers`
    on a `_frame` with `mover_threshold_pct="10"` and asserts the exact ordered `quote_id` list:
    a mover at +20% first; then `"A"` at −12% and `"B"` at +12% on the same baseline (same
    \|pct\|, same \|change_minor\|), in that order by `quote_id`; a policy at exactly +10%
    (in, after them); a policy one minor unit below +10% (out); a `zero_baseline` policy, a
    negative-baseline policy and a `quoted_to_declined` policy (all out). Mutations: sort by
    signed change; drop the `quote_id` tie-break.
  - `test_select_movers_breaks_a_pct_tie_by_absolute_minor_change` — `req("FR-263")`
    (audit-9734 N1); two movers tied on \|pct\| and differing in \|change_minor\|:
    `"M1"` with baseline 1 000 and candidate 1 150, `"M2"` with baseline 2 000 and candidate
    2 300 (both +15%). Asserts `["M2", "M1"]`. Mutation: remove sort step 2, which gives
    `["M1", "M2"]` by `quote_id`; the ledger quotes that failure.
- [ ] **Step 2: Run to verify they fail** (`ImportError: cannot import name 'select_movers'`).
  Then, before Step 3, write the aggregation once with `pl.col("baseline_minor").cast(pl.Float64).sum()`
  for the totals, run `test_dislocation_totals_are_sums_of_per_policy_minor_units`, and quote
  its failure on the `int` assertion (Acceptance 7's red); delete that version.
- [ ] **Step 3: Implement.** Totals with `pl.col(...).sum()` on `Int64` and `int(...)`. Every
  percentage and share as `fractions.Fraction(numerator, denominator)` of Python `int`s (an
  exposure ratio from the exact `Decimal` sums as `Fraction(Decimal)`), rounded **once** with
  `round(fraction, n)` (n = 2 for a percentage, 6 for a share; exact, half-even), converted to
  `Decimal` exactly (`Decimal(r.numerator) / Decimal(r.denominator)` is exact once rounded,
  because the denominator then divides `10**n`, and the default 28-digit context holds the
  result), and `float(...)` last. A zero
  denominator gives `None`. `exposure_years` is the exact `Decimal` sum over every policy,
  `quantize(Decimal("0.000001"), ROUND_HALF_EVEN)` once. Bands by comparing each banded
  policy's exact `Fraction` change with `Fraction(str(edge))`. Sort every list deterministically
  (bands by edge, segments by `spec.segments` order then level in native order with the null
  level last, rungs by `RUNG_ORDER`, errors by code) so the dump is byte-stable.
- [ ] **Step 4: Run to verify they pass**, then run each test's named mutation once, quote the
  failure in the ledger, and restore.
  `uv run pytest packages/pricing-core/tests/test_rating_dislocation.py -q`.
- [ ] **Step 5: Commit** `feat(rating): WK-673 S2 — dislocate: bands, movers, segments, rungs, totals (FR-263, FR-264)`.

### Task 6: NFR-495 — byte-identical across processes

**Files:**
- Test: `packages/pricing-core/tests/test_rating_dislocation.py`

- [ ] **Step 1: Write the test**, mirroring `test_testing_determinism.py:136-146`: a `_CHILD`
  script string that inserts the tests directory on `sys.path`, builds the Task 5 fixture book and
  bundles, runs `dislocate`, and prints `run.model_dump_json()`; `_child(hashseed)` runs it with
  `subprocess.run([sys.executable, "-c", _CHILD, _TESTS_DIR], check=True, capture_output=True, text=True, env={**os.environ, "PYTHONHASHSEED": hashseed})`.

```python
@pytest.mark.req("NFR-495")
def test_dislocation_is_byte_identical_across_fresh_interpreters() -> None:
    assert _child("1") == _child("2")
    assert '"totals"' in _child("1")  # the run is really there to compare


@pytest.mark.req("NFR-495")
def test_the_comparator_can_fail_when_the_portfolio_changes() -> None:
    assert _child("1") != _child("1", mutate_first_row=True)
```

  (`_child` takes a `mutate_first_row` flag passed as a second argv value.)
- [ ] **Step 2: Run** both; the negative control must fail if the flag is ignored (check by
  ignoring it once; quote the failure; restore).
- [ ] **Step 3: Commit** `test(rating): WK-673 S2 — NFR-495 across interpreters`.

### Task 7: the gate, the ledger, the PR

- [ ] **Step 1:** `git diff --name-only origin/main...HEAD` against the Write set (Acceptance 10).
- [ ] **Step 2:** `git grep -n 'compile_bundle\|compile_rating_version' -- packages/pricing-core/src/pricing_core/rating/analysis.py`
  prints nothing (Acceptance 6).
- [ ] **Step 3:** The full two-half gate through the gate slot (`dev-commands`), on a clean
  detached checkout of the gated SHA; the stage table into the ledger, never the exit code alone.
  Record `uv run python scripts/req-coverage.py` for FR-263, FR-264, NFR-495, NFR-496.
- [ ] **Step 4:** `python3 scripts/doc-index.py` (regenerate `docs/INDEX.md`) in the last commit
  only; the four docs checks on a detached copy (Acceptance 11).
- [ ] **Step 5:** Open the draft PR; the body names the range `origin/main...<branch>`, the ruling
  id, the ledger's working id, the RL-1263 keys (none in `ONE_SIDED_SLUGS`), and contains no
  claude.ai/code link.

## Write set, and its serialisation (`RL-1263`)

Measured at `1ab1776d`, against WK-674 Slice 2 as the GO requires: `PL-1392`'s write set
(`docs/plans/PL-01392-…-leaf-plan.md:825-864`) plus RL 9736's (to be minted `RL-1401`; PR #1096
branch `mint-rl-1401` at `c66e4a21`, "Spec texts, with placement" and "What it obliges"; merged
to main as `RL-1401` at `7e2ee2ba`, and "RL 9736" in the table below names that record), and its
build branch `origin/sl-1256-environment-and-deployment-record` at `14c7e805`. `RL-1263` :89,
quoted: *"Two concurrent build slices may not both change the same **existing** function, class,
method, spec section, or policy table."* `RL-1263` :100: *"**Any other shared path serialises**
unless the lead's dispatch record names the path and the check showing that no existing
definition is edited by both."* The registry list is `delivery-process.core.json` `:391-408`,
including the 2026-10-03 21:11:06 BST amendment for `ONE_SIDED_SLUGS` (key-disjoint edits only;
each dispatch record names its keys; the second to merge re-runs its full gate including
`test_every_one_sided_slug_is_declared`).

| Path | This slice | WK-674 S2 (`PL-1392` + RL 9736) | Same existing definition? | Verdict |
|---|---|---|---|---|
| `docs/specs/03-rating-engine.md` | §4.6 (RL-1402 S3, a dated block after the example; S4, five edits inside the example); §5.2 (S1, four signatures in the `analysis.py` block; S2, a paragraph after the types paragraph, which is not edited) | §3.4 FR-239 row (`RL-1379` T2); §3.10 notes; a new §4.12 `Deployment` with its Deployment Request subsection, audit-actions bullet and invariants (RL 9736 T2, T3); §5.1 rows and the compile row and catalogue lines (`RL-1379` T3, T4; RL 9736 T4) | no: {§4.6, §5.2} against {§3.4, §3.10, §4.12, §5.1} | allowed under :100 (sections named) |
| `docs/specs/06-governance.md` | **none** | FR-353 (RL 9736 T1); §4.1, §4.2; the `settings:read` catalogue row (the 23:10:17 decision) | — | not shared |
| `docs/specs/00-overview.md` | **none** (`RL-1394` T8 defined this Work's terms) | §3 FR-4 row (`RL-1379` T1) | — | not shared |
| `packages/model-schema/src/model_schema/approvals.py`, `backend/src/app/platform/approvals.py` | **none** | `DEFAULT_POLICY`, the skip field, the predicate; `CREATION_ACTIONS` (RL 9736 item 1) | — | not shared |
| `packages/model-schema/src/model_schema/__init__.py` | **none** (DP-S2-8) | exports (+26 at `14c7e805`) | — | not shared |
| `backend/tests/test_contracts.py` `ONE_SIDED_SLUGS` | **no key touched** | adds `environment`, `environment-create`, `environment-update`, `deployment`, `deployment-create`, `deployment-request`, `deployment-request-create` (at `14c7e805`) | — | not shared; the dispatch record names this slice's keys as none |
| `docs/contracts/schemas/dislocation-run.schema.json` (hand-authored, not exempt) | edited (RL-1402 S5: `outcomes`, six ratios and `level` nullable, `errors.items`) | none (its write set touches `artifact-ref.schema.json` only among hand-authored schemas) | — | not shared |
| `packages/model-schema/src/model_schema/dislocation.py`, `packages/model-schema/tests/test_dislocation.py` | created | — | — | not shared |
| `packages/pricing-core/src/pricing_core/rating/analysis.py`, `packages/pricing-core/tests/test_rating_dislocation.py` | created | — | — | not shared |
| `packages/pricing-core/src/pricing_core/rating/score.py` | **none** (called, not edited) | none (WK-674 S2 edits `backend/src/app/api/score.py`, a different file) | — | not shared |
| the ledger; `docs/INDEX.md` | new; regenerated | regenerated | — | `INDEX.md` is registry-exempt (regenerate at the second merge) |

**Not written:** `docs/open-questions.md` and `03` §10 (no OQ; OQ 9739 stays with SL-1387);
`docs/roadmap.md`; `PL-1267`; `00`; `06`; `scripts/generate-contracts.py`; any `backend/` or
`frontend/` file. The dispatch record re-derives this table against every build PR open at
dispatch (`gh pr list --state open`), not only WK-674 S2.

## Status

`draft`. **Activation needs**, all required before `SL-1386` moves `draft → active`:

1. **The ruling is minted:** one decision-maker `RL-` resolving DP-S2-1 to DP-S2-7 and adopting
   or amending P1–P6, merged to main. That record is RL-1402, PR #1098, which
   adopts all six amended as S1 to S5; this need is met when it is minted and merged. **DP-S2-1, DP-S2-2, DP-S2-3, DP-S2-4, DP-S2-5, DP-S2-6 and
   DP-S2-7 all block activation.** DP-S2-8 is decided here (scope) and needs nothing.
2. **This plan is minted** (`PL-<n>`), its Decision points table carries the ruling's id, and
   `status: active`; `SL-1386`'s `relates` gains it.
3. **WK-673 Slice 1 is closed** — met: SL-1385 closed at `1ab1776d` (#1094).
4. **A gate slot is free** under `RL-1263` (at most two build slices, from different Works; none
   while an NFR measurement runs), in `PL-1371`'s G2 order as the lead reads it. This slice does
   not depend on WK-674 (`PL-1267` Sequencing, "No for Slices 1–4 and 7").

Not needs: RL 9736 / PR #1096 (cited for the contention table and Slice 4's obligation only);
OQ 9739 (SL-1387's); the FR-246 enforcement ruling on PR #1060 (Task 4 handles either state).

## Appendix — proposed texts P1–P6 (for the ruling to adopt, amend or reject)

These are proposals. The executor copies the **ruling's** texts (Task 0 Step 4), never these.
Each assumes the recommended option; the ruling rewrites any whose option it changes.
**Superseded by RL-1402**, which adopted all six amended, as S1 to S5 (P2 to P5
became one text, S3). They are kept unedited as the texts that ruling read.

### P1 — `03` §5.2, in the `# pricing_core/rating/analysis.py` block, after `dislocate`'s two lines (DP-S2-1 (a))

```python
def read_portfolio(portfolio: pl.LazyFrame, *,                     # added <date> (WK-673 S2, RL-<n>):
                   segments: Sequence[str] = ()) -> pl.LazyFrame    # §4.8's reader; Slice 7 reuses it
def dislocation_frame(baseline: CompiledBundle, candidate: CompiledBundle,
                      portfolio: pl.LazyFrame, spec: DislocationSpec) -> pl.DataFrame   # one row per policy
def summarise_dislocation(frame: pl.DataFrame, spec: DislocationSpec) -> DislocationRun  # dislocate = this ∘ dislocation_frame
```

And appended to the types paragraph (`03:1052`), as its last sentence:

```markdown
*`PortfolioFrameError` (added <date>, `RL-<n>`): a `ValueError` raised by `read_portfolio` for a portfolio that breaks §4.8's frame or names an absent segment column, naming the column and the count and never a value; the platform maps it to `VALIDATION_FAILED`. `dislocation_frame` returns, per policy, `quote_id`, each pass's outcome, `payable_premium` `value_minor` and error code, the originating rung (§4.6), and every pass-through column; Slice 4 writes the movers' rows from it to `largest_movers_blob`.*
```

### P2 — `03` §4.6, the compared set (DP-S2-2 (b)); first part of one new dated paragraph

```markdown
*(Amended <date>, WK-673 Slice 2, `RL-<n>`: the run's arithmetic.)* **The compared set** is the policies quoted under both versions. `outcomes` counts every policy once: `quoted_both`, `quoted_to_declined`, `declined_to_quoted`, `declined_both` and `error` (an `"error"` row in either pass), which sum to `policy_count`, and `zero_baseline`, the quoted-both policies whose baseline payable premium is 0. `errors` lists each error code with its count and a sample of at most 10 `quote_id`s. Every money figure is a sum over the compared set of the `payable_premium` rung's `value_minor`, as integers (FR-1397's arithmetic). A `zero_baseline` policy enters the money totals and `by_ladder_rung`, and no band, segment mean or mover, because it has no percentage change.
```

### P3 — `03` §4.6, the same paragraph continued: averages and shares (DP-S2-3 (a))

```markdown
A mean or total change in percent is Σ(candidate − baseline) ÷ Σ baseline × 100 over the policies it describes, computed exactly from the integers and quantised once to 2 decimal places, half-even. An `exposure_share` is that group's Σ `exposure_years` ÷ the compared set's, quantised to 6 places; `exposure_years` is the exact decimal sum over all policies, quantised to 6 places.
```

### P4 — `03` §4.6, continued: bands and movers (DP-S2-4 (a))

```markdown
A policy's change is (candidate − baseline) ÷ baseline × 100, exactly. `band_edges_pct` (required, strictly increasing, at least one edge) cuts it into half-open bands `[lo, hi)`, labelled "< e%", "e% to e′%" and "≥ e%", positive edges signed; every band is listed, an empty one with `policies` 0. A mover is a compared policy whose change has absolute value at least `mover_threshold_pct` (required, positive). The example's top band reads "≥ +10%" under this rule.
```

### P5 — `03` §4.6, continued: rungs and segments (DP-S2-5 (a), DP-S2-6 (a))

```markdown
A policy's **originating rung** is the first rung, in the ladder's declared order (FR-247), whose `unrounded_minor` differs between its two ladders (`value_minor` where either lacks it), a rung present in one ladder only counting as different. `by_ladder_rung` gives, for each rung that originates at least one compared policy's change, those policies' Σ(candidate − baseline) ÷ Σ baseline over the compared set × 100; the unrounded parts sum to `totals.change_pct`'s unrounded value. Each name in `segments` is a portfolio column; `by_segment` has one row per segment and distinct value over the compared set, in `segments` order then by level, the level being the value as a string (ISO for a date, `true`/`false` for a boolean) or `null` for nulls.
```

### P6 — `docs/contracts/schemas/dislocation-run.schema.json` (DP-S2-2 (b), DP-S2-6 (a)), in the same commit as P2–P5

Add to `properties`, and add `"outcomes"` to the top-level `required`:

```json
"outcomes": {
  "type": "object",
  "description": "Every policy counted once by its two outcomes; the first five sum to policy_count (03 §4.6).",
  "required": ["quoted_both", "quoted_to_declined", "declined_to_quoted", "declined_both", "error", "zero_baseline"],
  "properties": {
    "quoted_both": {"type": "integer", "minimum": 0},
    "quoted_to_declined": {"type": "integer", "minimum": 0},
    "declined_to_quoted": {"type": "integer", "minimum": 0},
    "declined_both": {"type": "integer", "minimum": 0},
    "error": {"type": "integer", "minimum": 0},
    "zero_baseline": {"type": "integer", "minimum": 0}
  }
}
```

and change `by_segment.items.properties.level` from `{"type": "string"}` to
`{"type": ["string", "null"]}`. §4.6's example gains `"outcomes"` with figures consistent with
its `policy_count`, which the ruling supplies.

## Self-review

**1. Spec coverage.** FR-263 → Tasks 4, 5 (change per policy, bands, overall and segment
averages, exposure and policy counts per band, movers kept for drill-down, total change).
FR-264 → Tasks 4, 5 (segments, originating rung). NFR-495 → Task 6. NFR-496 → Task 5. §4.8's
frame → Tasks 3, 4 (every refusal, the stamping, the per-pass projection, the pass-through).
§4.6 field-for-field → Task 2's contract test. `RL-1394`'s four Slice-2 tests → Tasks 3, 4.
`RL-1361` §E → Task 3 (null exposure; the pass-through positive test). `RL-1379` → Acceptance 6
and Inputs. LG-1400's `RL-1264` rows → none assigned to Slice 2, stated. OQ 9739 → not needed,
stated. FR-265, FR-266, FR-1397–FR-1399 → out of scope, owners named.

**2. Placeholder scan.** The arithmetic each test asserts was left to the ruling on purpose:
writing figures for an unruled rule would be the silent pick the GO forbids. RL-1402 (working
id) now fixes every rule, so Task 5 states the rules and the mover figures, and the executor
hand-computes the book's other figures from its integers in each docstring. Every test name,
file and broken input is named; Task 2 and Task 3 carry code; Tasks 4 and 5 name the functions,
the columns and the exact red each test must show.

**3. Type consistency.** `DislocationSpec`, `DislocationRun` and their item types are named once
(Task 2) and used as named in Tasks 3–6; `read_portfolio`, `dislocation_frame`,
`select_movers`, `summarise_dislocation` and `PortfolioFrameError` (with `code`) are RL-1402 S1 and S2's names, used as spelled there in Acceptance 3 and Tasks 3–5.

**5. Pre-merge fix check (2026-10-04).** RL-1402 "What it obliges", PL-1403
items 1 to 5 → Acceptance 3; Task 3 (at the call, `code`, NaN, float segment, float read);
Task 4 (`change_minor`, sorted, collision, rounding-only and `"100"`/`"100.0"` cases); Task 5
(`round(fraction, n)`, `select_movers` fixture, integer identity, errors sum and sample
objects, empty band `None`); Write set (contract edited). Its "Acceptance — the violation" list
→ Acceptance 13. Plan audit B2 → DP-S2-1 as ruled; N1, N2, N3, N6 → as ruled; N4 → Task 5's
named mutations; N5 → Acceptance 3, 6, 9; N7 → Task 4's `_compiled_from`. Audit-9734 N1 →
`test_select_movers_breaks_a_pct_tie_by_absolute_minor_change`; N2 → Task 5's sets and Task 0
Step 4; N3 → Task 5's sets and the bands test.

**4. Literals verified at `1ab1776d`:** `score_batch`'s signature (`score.py:1135-1141`),
`_BATCH_OUTPUT_SCHEMA`'s columns (`score.py:280`, §4.8), `LadderRungName` and `LadderRung`
(`scoring.py:49-60`, `:149-164`), `CompiledBundle` (`runtime.py:625-643`), `InputContractField.name`
(`rating.py:207-212`), `DecimalStr` and `MoneyMinor` (`money.py:69-104`), the `_compiled`
fixture (`test_rating_score.py:137-140`), the subprocess precedent
(`test_testing_determinism.py:136-146`), the contract's required lists
(`dislocation-run.schema.json`), and the WK-674 S2 `ONE_SIDED_SLUGS` keys
(`origin/sl-1256-environment-and-deployment-record` at `14c7e805`).
