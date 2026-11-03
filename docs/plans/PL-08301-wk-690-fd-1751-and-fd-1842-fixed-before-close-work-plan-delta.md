---
id: PL-8301
family: plan
kind: map
title: WK-690 — FD-1751 and FD-1842 fixed before close, one slice with two limbs (SL-8299) — Work-plan delta
status: draft                   # draft → active → superseded | retired (§1.2a)
created: 2026-11-03
owner: planner
tree: a8ef6f19c0be1142b0ac9dea88086f1ce6f95cbe
phase: P2
work: WK-690
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1268, PL-1621, PL-1665, SL-8299, FD-1751, FD-1842]
---

# PL-8301 — WK-690: FD-1751 and FD-1842 fixed before close (SL-8299): Work-plan delta

> **For agentic workers:** this is a **Work-plan delta** under Lean P2 L5 and L1 (a')
> (`.claude/roles/planner.md`, the Lean P2 bullet). It does not replace
> [`PL-1268`](PL-01268-wk-690-expression-custom-objectives-map-plan.md) (WK-690's map plan) or
> the deltas [`PL-1621`](PL-01621-wk-690-slices-4-and-5-expression-factors-and-the-authoring-view-work-plan-delta.md)
> and [`PL-1665`](PL-01665-wk-690-slices-4-and-5-acceptance-brought-to-rl-1615-and-rl-1616-work-plan-delta.md),
> and it leaves all three unedited. It `relates:` them and adds **one row**, cut here as
> SL 8299 (working id): FD-1751 and FD-1842, the two findings WK-690's close audit
> (CR 8291) lists as owed, fixed in one PR with two limbs, each red first. The slice's one
> ledger is LG 8300 (working id), which quotes this file as its scope. REQUIRED SUB-SKILL for
> the executor: subagent-driven-development (recommended) or executing-plans, task by task.
> The executor also binds `test-driven-development` (every red seen red **by its cause** on
> main before the code that turns it green), `python-test` (the `req` marker; negative tests),
> `python-package` (`pricing-core` stays standalone and never raises `PlatformError`),
> `spec-change` (Task 3), `dev-commands` (both gate halves, the slot wrapper) and
> `git-hygiene`. It reads [`README.md`](README.md)'s five unchecked conventions and is
> spawned from `.claude/roles/executor.md`, model `sonnet` (ruled, below).

Written 2026-11-03 by the planner (plan-wk690fix). Every literal below was read at
`origin/main` `a8ef6f19c0be1142b0ac9dea88086f1ce6f95cbe` (tree `598c8c3a`) unless marked
otherwise. The line numbers the findings cite (`diagnostics.py:957`, `:1213`, `:1056`) are
from older trees (`a2f77b2d`) and have moved; this plan cites main's.

## Authority

- **The GO**, the maintainer's (by delegation) entry "2026-11-03 16:02:43 GMT — Maintainer:
  WK-690 close audit CR 8291 @59a2cfe0 — NOT READY adopted; the two decisions" in `to-lead.md`,
  item (1): *"GO — FD-1751 + FD-1842 FIX BEFORE CLOSE, one WK-690 slice with two limbs, red
  first, sonnet, merged by Fri 6 … the remedy is a depth bound with a typed 422, never a bare
  500 … working ids SL 8299 / LG 8300 / PL 8301; GO request to me with the row; full SOLO gate;
  the slice's PR carries the row."*
- **The evidence**, CR 8291 (`docs/closures/CR-08291-wk-690-close-audit.md` at
  `origin/docs/wk690-close-audit-2026-11-03` `59a2cfe0`) §5b: *"Corrected owed list: FD-1751,
  FD-1842."*
- **The calendar**, the user's order of 15:38, entry "2026-11-03 15:38:58 GMT" in `to-lead.md`:
  code freeze Tue 10 Nov 2026, exit demo Wed 18 Nov 2026. Merge by **Fri 6 Nov 2026**
  (`date -d 2026-11-06 +%A` prints `Friday`; `date -d 2026-11-10 +%A` prints `Tuesday`).

## What is live at main (read, not run)

**FD-1751 is not a live wrong number at main; it is an undelivered requirement.** S4's
omission (DP-1274-DIAG (a), `to-lead.md` "2026-10-16 10:27:41 BST") guards both sites, as CR 8291
§5b also reads:

- permutation importance: `packages/pricing-core/src/pricing_core/modelling/diagnostics.py:1081-1088`
  omits an `expression` Factor as `PermutationOmissionReason.EXPRESSION_FACTOR` before the
  first-column read at `:1095` (`columns = tuple(factor.source_columns[:1])`) can run;
- partial dependence: `:1510-1520` emits it with no points and
  `PartialDependenceOmissionReason.EXPRESSION_FACTOR` before `_sweep` is called, so `:1351`
  (`columns = (factor.source_columns[0],)`) is not reached for it;
- `_TRANSFORMED_FACTOR_TYPES` (`:1194`) is `(FactorType.BANDING, FactorType.GROUPING)`, and
  `_resolved_axis` (`:1197-1213`) returns `None` for every other type;
- the monotonicity check omits it too, as `MonotonicityOmissionReason.EXPRESSION_FACTOR`
  (`:672-674`); FD-1751 does not name that block (DP-8301-3).

The pinning tests are `test_permutation_importance_omits_an_expression_factor_by_name` and
`test_partial_dependence_omits_an_expression_factor_by_name`
(`packages/pricing-core/tests/test_expression_factors.py:423-445`), over a **one-column**
expression (`half_age`). The residue is FR-174's *"permutation importance on the holdout,
partial dependence for declared factors"* (`docs/specs/02-modelling.md:306`, with its
2026-08-22 amendment: *"neither per-factor block may assume one source column per factor"*),
undelivered for an `expression` Factor; FR-178's 2026-10-16 amendment (`:310`) records the
omission and says *"Real diagnostics for an expression Factor are not delivered here, and are
owed to WK-690 as a finding."* The maintainer's 16:02:43 relay ("a silently wrong GBM
diagnostic number") describes the pre-S4 state; the remedy is the same either way.

**FD-1842 is live at main.** `parse_expression`
(`packages/pricing-core/src/pricing_core/data/expressions.py:288-304`) runs `_check` (`:299`,
iterative), then the recursive `_check_structure` (`:300`; it recurses at `:238`, `:253`,
`:255`, `:259`), then `_check_symbols`, and `_check_limits` last (`:303`). `_check_limits`
measures through `_measure` (`:139-155`), which is iterative ("Count iteratively, so a deep
tree cannot exhaust Python's own stack here"). `grammar_refusal`
(`backend/src/app/platform/objectives.py:295-318`) catches `ExpressionError` (`:309`) and
`SyntaxError` (`:315`) only; `_require_the_grammar` (`:321`) calls it; `create_objective` calls
`_require_the_grammar` at `:240`. `git grep -n RecursionError -- backend packages` prints nothing.
The preview route is not exposed: `app/api/custom_objectives.py:337` calls
`objective_preview.refuse_over_bound` (`platform/objective_preview.py:57-82`, iterative
`measure_expression`) first. **A second caller has the same mechanism:** the `factor` profile at
`backend/src/app/platform/modelling.py:295` (`parse_expression(expression, GrammarProfile.FACTOR,
…)`) catches the same two exceptions. Whether a 2000-deep factor expression reaches it was not
established here; DP-8301-1 (a) covers it either way.

**The bound is not open.** `02` §4.6 (`docs/specs/02-modelling.md:1039`): *"AST node count ≤ 200
(configurable); nesting depth ≤ 20."* `ExpressionLimits` (`expressions.py:123-128`) carries
`max_nodes = 200`, `max_depth = 20`. No decision point on the value.

**The create path's code is not open either, on the spec's reading (DP-8301-2 records the
alternative).** FR-150's amendment, as quoted by `RL-1410` R2
(`docs/rulings/RL-01410-…-task-4-s-three-refusals-stand.md:115-118`): *"A `loss` outside §4.6's
grammar is refused 422 `OBJECTIVE_GRAMMAR_VIOLATION`, with `line <L>, column <C>:` leading the
message of one `errors[]` entry on `loss`."* §4.6 includes the depth limit, and a loss of depth
21 already answers that code on create today (via `_check_limits` → `ExpressionError` →
`grammar_refusal`). `OBJECTIVE_GRAMMAR_VIOLATION` is registered (`02` §5.1 code list,
`:2192`). No new code, so no spec clause for a code.

## Goal

1. **Limb 1 (FD-1751).** An `expression` Factor in a GBM gets a real permutation importance and
   a real partial-dependence curve, each measured on the factor's **resolved** value through a
   **joint** operation over all its source columns (FR-177's mechanism for a cross), and the
   `expression_factor` omission is no longer emitted for either block.
2. **Limb 2 (FD-1842).** A loss (or any expression) over §4.6's depth or node bound is refused
   by the iterative bound check **before** the recursive structure walk runs, so no expression
   can raise `RecursionError`; `POST /api/v1/custom-objectives` answers 422
   `OBJECTIVE_GRAMMAR_VIOLATION`, never 500.

## Acceptance Standard

Each item is checkable by a command at the slice's head; "red" items are recorded in LG 8300
with the commit they were seen red on and the line that shows the cause.

1. **A1 red (FD-1751, permutation).** A new test over a GBM with an `expression` Factor reading
   **two** source columns, both backends (`xgboost`, `lightgbm`), seen red on main **because the
   factor is omitted** (`permutation_omitted` holds `(<slug>, "expression_factor")` and
   `permutation_importances` has no entry for it), not by any other error.
2. **A1 green.** The same test passes: the factor has one `PermutationImportance`; its
   `degradation` equals that of a **joint** shuffle of all its source columns under one shared
   order (computed in the test), and **differs** from a shuffle of the first source column
   alone (also computed in the test, so the old first-column behaviour is shown to fail it); no
   `expression_factor` omission is emitted in `permutation_omitted`.
3. **A2 red/green (FD-1751, partial dependence).** A new test, same fit: red on main because the
   curve has `points == ()` and `omitted.reason == expression_factor`; green when the curve's
   labels are the factor's **resolved** levels (for a banded expression, the banding's levels
   under FR-175's cap) and never raw first-column values, and each point is scored by holding
   **every** source column of the factor at **one real row** of that level (no synthesised
   operand combination).
4. **A3 (banded / non-banded).** A banded two-column expression is covered by A1–A2. A
   non-banded case is added only if `pricing-core` resolves one (FR-210 refuses an expression
   that is certainly numeric and pins no Banding); the executor quotes the line that decides,
   and LG 8300 records whether this item collapsed into A2.
5. **A4 (inversion).** `test_permutation_importance_omits_an_expression_factor_by_name` and
   `test_partial_dependence_omits_an_expression_factor_by_name`
   (`test_expression_factors.py:423-445`) are **inverted in the same commit series**, not
   deleted: they assert the factor now yields a number and the `expression_factor` reason is not
   emitted. (Removing either needs the lead's OK, common brief item 13.)
6. **A5 red (FD-1842, parser).** A new test in
   `packages/pricing-core/tests/test_expression_limits.py`: `parse_expression("-" * 1999 + "f",
   GrammarProfile.OBJECTIVE, symbols=frozenset({"y", "f", "w"}))` and `"f+" * 999 + "f"`, and
   the same depth in the `factor` profile, each seen red on main **by `RecursionError`**.
7. **A5 green.** Each raises `ExpressionError` whose message names the FR-145 limit (depth 20,
   or nodes 200), and `_check_structure` is not entered for it (the order in
   `parse_expression` is `_check`, `_check_limits`, then `_check_structure` and
   `_check_symbols`; or DP-8301-1's ruled alternative).
8. **A6 red/green (FD-1842, create path).** A new test in
   `backend/tests/test_custom_objectives_expression.py`, beside
   `test_grammar_violation_is_422_with_the_position_in_errors` (`:385`): `POST
   /api/v1/custom-objectives` with `loss = "-" * 1999 + "f"` (2000 characters, inside
   `CustomObjective.loss`'s 2000 cap). Red on main by the `RecursionError` (a 500, or the test
   client re-raising it; the LG quotes which). Green: 422, `code == "OBJECTIVE_GRAMMAR_VIOLATION"`,
   one `errors[]` entry on `loss`, and no `CustomObjectiveRow` written. **DB-backed** (the
   `database` fixture and the flag).
9. **A7 (no regression).** `test_expression_limits.py`, `test_objective_preview_api.py`
   (FR-1840 3a stays 422 `VALIDATION_FAILED` on the preview route) and
   `test_expression_factors_api.py` pass at the head; any existing test whose expected message
   changes because the bound now precedes the structure check is reported verbatim to the lead
   before it is edited.
10. **A8 (spec).** `docs/specs/02-modelling.md` carries the dated amendments of Task 3, and
    `python3 scripts/audit-docs.py` and `uv run python scripts/req-coverage.py` are rc 0 at the
    head (own working ids excepted until the mint, common brief item 31).
11. **A9 (the gate).** The full SOLO gate, both halves (`CLAUDE.md` §11), green at the
    re-merged head, run as the Gate section says.
12. **A10 (closing acts).** At the slice's close the auditor sets FD-1751 and FD-1842 `closed`,
    each with a dated register line citing the PR number and merge commit; the merge lands by
    **Fri 6 Nov 2026**, before the Tue 10 Nov 2026 freeze.

## Global Constraints

- Money is not touched. No pandas (`CLAUDE.md` §3). `pricing-core` keeps zero FastAPI deps and
  never raises `PlatformError` (`CLAUDE.md` §2).
- No hand-written shape: the omission enums live in `model-schema`
  (`packages/model-schema/src/model_schema/diagnostics.py`, `PermutationOmissionReason` and
  `PartialDependenceOmissionReason`); `expression_factor` **stays a member** (DP-8301-4), so
  `docs/contracts/` does not change by member. If a docstring or description change moves the
  generated contract, `uv run python scripts/generate-contracts.py` regenerates it in the same
  commit and `--check` is rc 0.
- The frontend's readable text for `expression_factor` (`GbmImportanceCharts.vue:109`,
  `PartialDependencePanel.vue:78`) stays: artifacts written before this slice carry the value.
- Requirement ids are append-only; amendments are dated lines (`CLAUDE.md` §5).
- Limb order: the two limbs are independent and may land as separate commits in one PR.
  If the slice slips, the lead decides whether one limb merges alone.

## Tasks

### Task 0 — premises re-read at the row's base

- [ ] Re-read every literal in "What is live at main" at the base the branch is cut from; a moved
  line is re-cited in LG 8300, a changed behaviour stops the task and is reported.

### Task 1 — Limb 1, FD-1751 (pricing-core, DB-free)

- [ ] Fixture: a two-column banded `expression` Factor (an expression over two numeric columns,
  with a `banding_id`), fitted with `fit_gbm` on a synthetic book in which **both** columns
  carry signal, so a first-column-only shuffle and a joint shuffle give different deviances.
- [ ] Red: A1 and A2 tests, both backends; run through `run-small.sh`; record the red lines.
- [ ] Green: in `diagnostics.py`, remove the two `EXPRESSION_FACTOR` early-outs from the
  permutation and partial-dependence blocks; an `expression` Factor's `columns` are all its
  `source_columns` (shuffled together under one shared order, as `_shuffled_together` already
  does for a cross); `_resolved_axis` resolves an `expression` Factor to its own levels; the
  sweep holds every source column at one real row per level (generalising what
  `_cell_representatives` does for a cross). `shared_source_columns` names any of those columns
  another factor also sources (DP-8301-5).
- [ ] A4: invert the two S4 tests.
- [ ] Green on `test_expression_factors.py`, `test_diagnostics.py`, `test_gbm.py` (≤ 3 files per
  run-small call).

### Task 2 — Limb 2, FD-1842

- [ ] Red: A5 (DB-free, `test_expression_limits.py`) and A6 (DB-backed); record the red lines.
- [ ] Green (DP-8301-1 (a)): in `parse_expression`, call `_check_limits(tree.body, limits)`
  before `_check_structure`. No `RecursionError` handler is added anywhere (a handler would hide
  the cause; the bound removes it).
- [ ] A7 runs; A6 green under the DB window the lead grants.

### Task 3 — spec (same PR)

- [ ] `02-modelling.md` FR-178: a dated amendment (`2026-11-0x, SL-8299 (WK-690), FD-1751`):
  an `expression` Factor is measured by both per-factor GBM blocks through a joint operation
  over all its source columns, on its resolved levels; `expression_factor` is kept as a
  **reserved** reason, no longer emitted by those two blocks, because artifacts written from
  2026-10-16 carry it; the monotonicity block's omission is unchanged (DP-8301-3 (a)).
- [ ] `02-modelling.md` FR-145 (or §4.6's limit line): a dated clarification that the limits are
  checked **before** the structure walk, so an over-bound expression is refused by its bound in
  every profile, and on create answers 422 `OBJECTIVE_GRAMMAR_VIOLATION` (FD-1842). No new
  error code.
- [ ] `model-schema` enum comments on `EXPRESSION_FACTOR` ("Real support is owed (WK-690)")
  re-pointed to "reserved, no longer emitted by permutation or partial dependence".

### Write set

`packages/pricing-core/src/pricing_core/modelling/diagnostics.py`;
`packages/pricing-core/src/pricing_core/data/expressions.py`;
`packages/model-schema/src/model_schema/diagnostics.py` (comments only);
`packages/pricing-core/tests/test_expression_factors.py`;
`packages/pricing-core/tests/test_expression_limits.py`;
`backend/tests/test_custom_objectives_expression.py`; `docs/specs/02-modelling.md`;
`docs/contracts/` only if regenerated; `docs/roadmap.md` (the row's status lines);
`docs/ledgers/` (LG 8300). Anything else is a write-set deviation, reported before it is made.

## The gate

- **A full SOLO gate** (ruled at 16:02:43): both halves of `CLAUDE.md` §11 at the re-merged head,
  in the slot the lead grants, `pytest -rs`, the template guard at START and END, and a skip
  count against the baseline the brief gives (22) — a skip count below it names what ran, above
  it fails the row.
- **DB or no DB per test:** A1–A5 are DB-free (`run-small.sh`); A6 is DB-backed and runs only in
  a DB window the lead grants in writing (common brief items 12 and 32); the full gate covers it
  regardless.
- The green set is derived by import closure (common brief item 29), quoted in LG 8300.

## Decision points

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-8301-1 | Where does the depth bound run before the recursive walk? | (a) In `pricing-core` `parse_expression`: `_check_limits` moves ahead of `_check_structure`, so every profile and both backend callers (`objectives.py:308`, `modelling.py:295`) are covered by one change. (b) FD-1842's shape (1): `create_objective` calls a `measure_expression` bound check before `_require_the_grammar`, as the preview does; `modelling.py:295` stays exposed. (c) FD-1842's shape (2): `_check_structure` made iterative. | **(a).** It fixes the cause in the layer that owns the bound, is a two-line reorder, and is the "depth bound checked before the recursive walk" the GO names. (c) is a rewrite of a 49-line walker to remove a depth the bound already forbids. | design | yes (Task 2) | the decision-maker |
| DP-8301-2 | The create path's 422 code for an over-bound loss. | (a) `OBJECTIVE_GRAMMAR_VIOLATION`, positioned on `loss`: FR-150's amendment (as RL-1410 R2 quotes it) and today's behaviour for depth 21. (b) `VALIDATION_FAILED`, as the preview's FR-1840 (3a) answers, which FD-1842's shape (1) implies; it changes create's answer for every over-bound loss and needs a dated FR-150 clause. | **(a).** It is the code the spec already gives a loss outside §4.6, it is registered, and create already uses it for the same limit at smaller depths; (b) makes one limit answer two codes on one route. | spec reading | yes (A6) | the decision-maker |
| DP-8301-3 | FR-174's monotonicity verification also omits an `expression` Factor (`diagnostics.py:672-674`; FR-89's `expression_factor`). FD-1751 names only permutation importance and partial dependence. | (a) Out of this row: the omission stays, recorded and visible; the lead decides whether it is a finding against WK-690's close or carried. (b) In this row as a third limb. | **(a).** The GO names two limbs, the register row's remedy names two blocks, and Fri 6 is three days away; the omission is named, not silent. The lead raises it at the close if it is owed. | scope | no | the lead |
| DP-8301-4 | What happens to `expression_factor` once both blocks measure the factor? | (a) Kept as a reserved, no-longer-emitted member of both enums (FR-177's precedent for `no_source_column`). (b) Removed. | **(a).** Artifacts written since 2026-10-16 carry it and must keep validating; the frontend keeps its readable text. | design | no | the decision-maker |
| DP-8301-5 | How is a factor that shares a source column with an `expression` Factor reported? (FD-1751 Disposition, the first open point.) | (a) Named, not refused: the expression's `PermutationImportance.shared_source_columns` lists the shared columns (FR-177's additive field, as for any factor today); the other factor is still measured. (b) Omit the other factor, as `operand_of_interaction` does for a cross. | **(a).** Varying a shared column alone builds no unseen level (an expression re-evaluates on any operand value, unlike a cross's cell map), so FR-178's reason for omitting does not apply; the existing field records the joint effect. | design | no | the decision-maker |

A plan is `draft` while a blocking decision point is open (`document-ids.md` §1.6). DP-8301-1 and
DP-8301-2 block; this file stays `draft` until they are ruled and goes `active` at its mint by a
status line.

## The row, cut

SL 8299 is cut in `docs/roadmap.md` under `### WK-690`, after `SL-1622`, as `draft`
(`document-ids.md` §1.6 SL row).

## Hand-off (not this plan's writes)

- **The lead:** the GO request with the row; list this delta on WK-690's roadmap row (L5); DP-8301-3.
- **The decision-maker:** DP-8301-1, -2, -4, -5.
- **The executor (sonnet):** Tasks 0–3, LG 8300, the gate.
- **The auditor:** the slice audit; FD-1751's and FD-1842's closing register lines citing the PR
  and merge commit (A10).
- **The minter:** PL 8301, SL 8299, LG 8300 at the slice's mint turn.

## Self-review

- **Spec coverage.** FR-174 (the PI/PD limb), FR-175 (banded axis), FR-177 (the joint
  mechanism reused), FR-178 (amended), FR-145 and §4.6 (the bound), FR-150 (the create code),
  FR-1840 (3a) (unchanged). FD-1751 and FD-1842 are register rows `:385` and `:410`. No
  requirement id is added.
- **Literals verified** at `a8ef6f19`: `diagnostics.py:672-676`, `:1081-1095`, `:1194-1213`,
  `:1259-1270`, `:1340-1420`, `:1505-1520`; `expressions.py:123-155`, `:213-303`;
  `objectives.py:240`, `:295-335`; `objective_preview.py:57-82`; `custom_objectives.py:337`;
  `modelling.py:280-310`; `test_expression_factors.py:395-445`;
  `test_custom_objectives_expression.py:385`; `02-modelling.md:306`, `:309`, `:310`, `:1039`,
  `:1920`, `:2192`; RL-1410 R2 `:93-125`; CR 8291 §5b at `59a2cfe0`.
- **Not run.** Every behavioural statement is read from code; the reds are the measurement.
- **Placeholders.** `2026-11-0x` (the amendment date) and the PR number are values the
  executor reads when it writes them.
