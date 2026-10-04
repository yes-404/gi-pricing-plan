---
id: LG-1406
family: ledger
title: WK-673 slice SL-1386 — the Dislocation Run on ZEN in integer minor units, spec first (PL-1403, RL-1402)
status: closed
created: 2026-10-04
owner: executor
tree: dfddfad890243a13b8c700f4f279f944125e777f
phase: P2
work: WK-673
slice: SL-1386
plans: [PL-1403]
corrected_by: []
relates: [RL-1402, RL-1394, RL-1264, RL-1263, PL-1267, PL-1395, LG-1400]
---

# LG-1406 — WK-673 slice SL-1386, the Dislocation Run on ZEN

Executed from `PL-1403` by `executor-1386` (sonnet; `echo $CLAUDE_EFFORT` printed `medium`). Branch
`sl-1386-dislocation-run`. Stamps are BST (`TZ=Europe/London date`). The ledger's working id was `9732`, allocated by
the lead 2026-10-04 13:01:36 BST; it was renumbered to LG-1406 at the mint (2026-10-04, `doc-id.py next` at origin/main dfddfad8). This ledger covers Tasks 0 to 6; the Task 7 entry follows the minted-head gate.

The executor charter's Model / effort line, verbatim: "`sonnet` (currently Sonnet 5); medium, inherited from the
lead — the highest-volume role; per-slice gates and the auditor's re-check bound the risk of a cheaper setting."

## Tasks

### Task 0 — preconditions

**Step 1 (activation needs, run 2026-10-04 13:24-13:27 BST).** `git log -1 --format='%H %aI' origin/main` printed
`bb12d1e5cc1f0bfc76a56dc1a6b3364a505d7349 2026-10-04T13:24:58+01:00`. The ruling resolves:
`grep -l '^id: RL-1402' docs/rulings/*.md` printed `docs/rulings/RL-01402-pl-1403-dp-s2-1-to-7-decided-four-public-functions-with-an-ordered-mover-selector-quoted-both-compared-ratio-of-sums-half-open-bands-first-differing-rung-column-segments-float-exposure-rounded.md`. `docs/plans/PL-01403-…` front matter
`status: active`; `docs/roadmap.md:724` (SL-1386's block) carries `status: active`.

**Step 2.** `uv sync --all-packages` ran clean in the fresh worktree.

**Step 3 (baseline, untouched tree `bb12d1e5`).** `python3 scripts/audit-docs.py` rc 0 ("All checks passed.");
`python3 scripts/doc-id.py check` rc 0; `python3 scripts/doc-index.py --check` rc 0 ("OK (byte-stable)");
`python3 scripts/register-lint.py` rc 0 ("OK (0 violations)");
`uv run pytest packages/pricing-core/tests/test_rating_score_batch.py -q` rc 0, "11 passed in 6.89s".
Load at the start: `uptime` load average 1.39, 0.84, 0.95.

**Step 4 — the ruling's texts, copied from `docs/rulings/RL-01402-pl-1403-dp-s2-1-to-7-decided-four-public-functions-with-an-ordered-mover-selector-quoted-both-compared-ratio-of-sums-half-open-bands-first-differing-rung-column-segments-float-exposure-rounded.md` (RL-1402, `active`)**, "The exact texts"
(ruling lines 280-369) with "Amendment N2, 2026-10-04" (ruling lines 433-561) applied in place of the texts it replaces.
`<date>` is written as `2026-10-04` (the day of this commit; the merge date is not known to the executor — see
Deviations) and `RL-<n>` as `RL-1402`. Ruling line ranges of each copied block: S1 :290-295; S2 :301-301;
S3 :307-319 with N2-a (:492-498) replacing the two sentences it names; S4 by the ruling's list
(:322-336) with N2-b in place of edit 2; S5 (:337-368) with N2-c (:515-528) in place of edit 1's property.
The blocks below are produced by extraction from the ruling file by script, not retyped.

#### S1 (§5.2, `analysis.py` block)

```python
def read_portfolio(portfolio: pl.LazyFrame, *,                     # added 2026-10-04 (WK-673 S2, RL-1402): §4.8's
                   segments: Sequence[str] = ()) -> pl.LazyFrame    # reader; refuses at the call; Slice 7 reuses it
def dislocation_frame(baseline: CompiledBundle, candidate: CompiledBundle,
                      portfolio: pl.LazyFrame, spec: DislocationSpec) -> pl.DataFrame   # one row per policy
def select_movers(frame: pl.DataFrame, spec: DislocationSpec) -> pl.DataFrame          # FR-263's movers, in §4.6's order
def summarise_dislocation(frame: pl.DataFrame, spec: DislocationSpec) -> DislocationRun  # dislocate = this ∘ dislocation_frame
```

#### S2 (§5.2 paragraph after the `DislocationSpec` types paragraph)

```markdown
*`analysis.py`'s public surface (added 2026-10-04, WK-673 Slice 2, `RL-1402`).* `read_portfolio` checks §4.8's frame and each name in `segments` (present, of a dtype §4.6 admits) when it is called, not when its result is collected, and returns the frame with every column kept and `exposure_years` read as §4.6 states. `PortfolioFrameError` is a `ValueError` with `code = "VALIDATION_FAILED"`, raised for any such fault, and by `dislocation_frame` for a portfolio column named as one of its own columns; its message names the column and the count, or the column and its dtype, and never a value; the platform maps it to `VALIDATION_FAILED`. `dislocation_frame` calls `read_portfolio(portfolio, segments=spec.segments)` before any rating and returns one row per policy, sorted by `quote_id`: `quote_id`; `baseline_outcome`, `candidate_outcome`; `baseline_minor`, `candidate_minor`, the `payable_premium` rung's `value_minor` as an integer, null unless that pass quoted; `change_minor`, `candidate_minor − baseline_minor`, null unless both passes quoted; `baseline_error_code`, `candidate_error_code`; `origin_rung` (§4.6), null unless both passes quoted and a rung differs; then every portfolio column, in the portfolio's order. `select_movers` returns the frame's rows for FR-263's movers, in §4.6's mover order; Slice 4 writes them to `largest_movers_blob`. `dislocate(b, c, p, s)` is exactly `summarise_dislocation(dislocation_frame(b, c, p, s), s)`. `band_edges_pct` and `mover_threshold_pct` keep the names `RL-1394` gave them; §4.6 states their rules.*
```

#### S3 as amended by N2-a (§4.6 dated block)

```markdown
*(Amended 2026-10-04, WK-673 Slice 2, `RL-1402`: the run's arithmetic, for FR-263 and FR-264. The example's top band label, its `exposure_years`, `by_ladder_rung` and `errors` were changed and `outcomes` added to match.)*

**Outcomes, and the two sets.** `policy_count` counts every portfolio row. `outcomes` counts each policy once by its two outcomes: `quoted_both`, `quoted_to_declined`, `declined_to_quoted`, `declined_both` and `error` (an `"error"` row in either pass), which sum to `policy_count`; `zero_baseline`, the quoted-both policies whose baseline payable premium is 0; and `negative_baseline`, those whose baseline payable premium is below 0. The **compared set** is the quoted-both policies. The **banded set** is the compared policies whose baseline payable premium is above 0: the compared set less its `zero_baseline` and `negative_baseline` policies, so Σ `distribution[].policies` = `quoted_both` − `zero_baseline` − `negative_baseline`. A negative baseline is a value a Rating Version can return, not an error (no-negative-premium is a Regression Suite property, not a runtime bound): it stays in the compared set and enters no band and no mover. `errors` has one item for each error code with at least one policy, in code order: an `error` policy is counted once, under its baseline pass's `error_code` where that pass errored and otherwise under its candidate pass's, so the counts sum to `outcomes.error`; `sample` holds up to 10 of those policies as `{"quote_id": …}`, the first 10 by `quote_id`.

**Money and ratios.** Every money figure is a sum over the compared set of the `payable_premium` rung's `value_minor`, as integers (FR-1397's arithmetic, NFR-496). A policy's change is its candidate minus its baseline payable premium. A mean or total change in percent over a group is the group's Σ change ÷ Σ baseline × 100, computed as an exact rational of the integers and rounded once to 2 decimal places, half-even. An `exposure_share` is the group's Σ `exposure_years` ÷ the Σ over the set the group is part of, rounded once to 6 places, half-even. A ratio whose denominator is 0 is `null`. `exposure_years` is the exact decimal sum over every policy, rounded once to 6 places, half-even. `totals`, `by_segment` and `by_ladder_rung` cover the compared set.

**Bands and movers** cover the banded set, because they need a per-policy percentage change, (candidate − baseline) ÷ baseline × 100, exactly. `band_edges_pct` (required; decimals; at least one; strictly increasing) cuts it into half-open bands `[lo, hi)`, labelled "< e₀%", "eᵢ% to eᵢ₊₁%" and "≥ eₙ%", each edge printed as its plain decimal string with no exponent and no trailing zeros, with "+" before a positive edge. Every band is listed, in edge order; an empty band has `policies` 0. A **mover** is a banded policy whose percentage change has an absolute value of at least `mover_threshold_pct` (required; a positive decimal), decided exactly on the integers. Movers are ordered by the absolute percentage change, largest first, then by the absolute change in minor units, largest first, then by `quote_id` in code-point order.

**Rungs.** A compared policy's **originating rung** is the first rung, in the ladder's fixed order (FR-247, FR-252), that differs between its two ladders: present in one ladder only, or with a different `value_minor`, or with a different `unrounded_minor` compared as decimal values. A policy with no differing rung has a change of 0. `by_ladder_rung` has one row for each rung that originates at least one compared policy's change, in ladder order; its `contribution_pct` is those policies' Σ change ÷ the compared set's Σ baseline × 100. The integer sums of change by originating rung add up exactly to `candidate_premium_minor − baseline_premium_minor`.

**Segments.** Each name in `segments` (distinct) is a portfolio column of a string, categorical, integer, boolean or date dtype; any other dtype, or an absent column, is refused with `VALIDATION_FAILED` naming the column. `by_segment` has one row per segment and level, in `segments` order, then by level in the value's own order (strings by code point, integers by value, `false` before `true`, dates by date), with the null level last. The level is the value as a string (an integer in decimal, a date in ISO form, a boolean as `true` or `false`), or `null`: null values form one level and are never dropped.

**`exposure_years` as read.** §4.8's "decimal" is how the column is read: an integer or decimal dtype exactly; a float dtype row by row as the decimal of the value rounded to 6 places (FR-62's rule); a NaN or infinite value is refused with the nulls; any other dtype is refused with `VALIDATION_FAILED` naming the column and its dtype.
```

#### S4 (§4.6 example, five edits; edit 2 is N2-b)

1. `"policy_count": 1_284_902, "exposure_years": "1240118.4",` becomes `"policy_count": 1_284_902, "exposure_years": "1240118.400000",`.
2. (N2-b) Insert directly after the `totals` object's closing line (`             "change_pct": 1.95},`):
```
  "outcomes": {"quoted_both": 1_284_902, "quoted_to_declined": 0, "declined_to_quoted": 0,
               "declined_both": 0, "error": 0, "zero_baseline": 0, "negative_baseline": 0},
```
3. `{"band": "> +10%", …}` becomes `{"band": "≥ +10%", …}`.
4. `"by_ladder_rung": [{"rung": "base_premium", "contribution_pct": 1.10}],` becomes `"by_ladder_rung": [{"rung": "risk_premium", "contribution_pct": 1.11},` / `{"rung": "constraints", "contribution_pct": 0.84}],`.
5. `"errors": [{"code": "INPUT_CONTRACT_VIOLATION", "count": 0}]` becomes `"errors": []`.

#### S5 (contract), edits 2-4 and N2-c

1. `"outcomes"` added to the top-level `required` after `"totals"`, and the property after `totals`: **N2-c's text** (below, in place of the ruling's S5 edit 1 property).
2. `"type": "number"` becomes `"type": ["number", "null"]` at six places: `totals.properties.change_pct`; `distribution.items.properties.mean_change_pct` and `.exposure_share`; `by_segment.items.properties.mean_change_pct` and `.exposure_share`; `by_ladder_rung.items.properties.contribution_pct`.
3. `by_segment.items.properties.level` becomes `{"type": ["string", "null"]}`.
4. `errors.items.properties.count` becomes `{"type": "integer", "minimum": 1}`; `errors.items.properties.sample` becomes `{"type": "array", "maxItems": 10, "items": {"type": "object", "required": ["quote_id"], "properties": {"quote_id": {"type": "string"}}, "additionalProperties": false}}`.

N2-c's `outcomes` property:

```json
"outcomes": {
  "type": "object",
  "description": "Every policy counted once by its two outcomes; the first five sum to policy_count. zero_baseline and negative_baseline count the quoted-both policies with a baseline payable premium of 0 and below 0; neither is in a band or a mover (03 §4.6).",
  "required": ["quoted_both", "quoted_to_declined", "declined_to_quoted", "declined_both", "error", "zero_baseline", "negative_baseline"],
  "properties": {
    "quoted_both": {"type": "integer", "minimum": 0},
    "quoted_to_declined": {"type": "integer", "minimum": 0},
    "declined_to_quoted": {"type": "integer", "minimum": 0},
    "declined_both": {"type": "integer", "minimum": 0},
    "error": {"type": "integer", "minimum": 0},
    "zero_baseline": {"type": "integer", "minimum": 0},
    "negative_baseline": {"type": "integer", "minimum": 0}
  }
}
```

**Banded-set check (Step 4's reading).** The copied S3 defines the banded set as "the compared policies whose baseline
payable premium is above 0: the compared set less its `zero_baseline` and `negative_baseline` policies" — i.e.
`baseline_minor > 0`. Confirmed by `grep -c 'whose baseline payable premium is above 0'` on this ledger and on
`docs/specs/03-rating-engine.md`: see Task 1 results.

**Step 5.** `examples/fremtpl2/seed.py:56`: `    "exposure_years": "float",` inside `NUMERIC` (the cast applied to
`policy_exposure` at :82), so the public freMTPL2 portfolio's `exposure_years` is a float column (Float64). RL-1402
DP-S2-7 admits it, read rounded to 6 places; this is the input for Task 3's positive float-read test.

**Step 6.** `gh pr list --state open` (read 2026-10-04 13:25 BST at origin/main `bb12d1e5`): no open PR carries a ruling
on `03` §4.6, §4.8, §5.2, `score_batch` or the portfolio frame. #1102 and #1100 are WK-674 S2's rulings (RL 9733 /
RL-1404 on Task 5 flags), #1073 and others are findings. `git log origin/main -- docs/specs/03-rating-engine.md`
newest: `1ab1776d` (SL-1385), which is PL-1403's tree. Commit read: `bb12d1e5`.

### Task 1 — spec, the ruled texts

**Red first (before any edit), at `bb12d1e5`.** `grep -c negative_baseline docs/specs/03-rating-engine.md
docs/contracts/schemas/dislocation-run.schema.json` printed `0` for each file;
`git diff -U0 origin/main -- docs/contracts/schemas/dislocation-run.schema.json | grep -c '^+.*"null"'` printed `0`
(Step 4 requires 7).

**Applied, in one working-tree change (one commit; spec and contract together), by script from the ruling's extracted
text** (`<date>` = 2026-10-04, `RL-<n>` = RL-1402). Placements in `docs/specs/03-rating-engine.md` at this commit:
- S1 (four signatures): :1005-1010, after `dislocate`'s two lines (:1003-1004) and before `async def derive_changes` (:1011).
- S2 (the `analysis.py` public-surface paragraph): :1077, directly after the `DislocationSpec` types paragraph (:1075), which is not edited.
- S3 with N2-a: the "Amended 2026-10-04" block from :562, directly after the §4.6 example's closing fence and before `### 4.7`; the "Outcomes, and the two sets" paragraph is :564.
- S4 edits 1-5 in the §4.6 example (:520-:555), edit 2 as N2-b (`"outcomes"` lines :523-:524).
- S5 in `docs/contracts/schemas/dislocation-run.schema.json`: `outcomes` required at :8 and the N2-c property at :26-:39; the six `["number", "null"]` places, `level` `["string", "null"]`, `errors.items.properties.count` minimum 1 and `sample` typed (:147).

**Checks.**
- Contract parses with no duplicate key: the `contract-schema` one-liner printed nothing, rc 0.
- `git diff -U0 origin/main -- docs/contracts/schemas/dislocation-run.schema.json | grep -c '^+.*"null"'` printed `7` (six ratios and `level`); `git diff -U0 docs/contracts | grep '^[-+]' | grep -c '"type": "number"'` printed `6` (the six removed lines, none added).
- `uv run pytest backend/tests/test_contracts.py -q`: 150 passed, 2 skipped, rc 0 (the `dislocation-run` entry in `ONE_SIDED_SLUGS` untouched).
- `grep -c 'whose baseline payable premium is above 0'`: the spec :1, this ledger :2 — the banded set is `baseline_minor > 0` (Step 4's confirmation).
- `python3 scripts/doc-index.py` then `python3 scripts/audit-docs.py`: rc 1 with only check 31 ("gap in the full allocation between 1403 and 9732", the ledger's working id, expected) after this ledger's `PRs` section was added (check 37 had named it missing).

### Task 2 — `model-schema`: `DislocationSpec` and `DislocationRun` (executor-1386b, `echo $CLAUDE_EFFORT` printed `medium`)

**Red.** `uv run pytest packages/model-schema/tests/test_dislocation.py -q -p no:cacheprovider` (new test file, no
module yet): `ModuleNotFoundError: No module named 'model_schema.dislocation'`, 1 error during collection. (An earlier
run before `uv sync --all-packages` failed on `No module named 'pydantic'`; it was discarded as an environment fault.)

**Green.** Same command after `packages/model-schema/src/model_schema/dislocation.py`: `10 passed`. The contract-match
test compares property names and `required` for the top level and for `totals`, `outcomes`, `distribution.items`,
`by_segment.items`, `by_ladder_rung.items`, `errors.items` and `errors.items.sample.items`, and that the seven
nullable places RL-1402 S5 names admit `null`. The N2 identity test builds a run with `negative_baseline: 1` and
shows `Σ distribution.policies = quoted_both - zero_baseline - negative_baseline` accepts 2 and refuses 3.

**Mutation (plan Step 4).** Renaming `policy_count` to `policies_count` in the model: `4 failed, 6 passed`; restored,
`uv run pytest packages/model-schema backend/tests/test_contracts.py -q` printed `615 passed, 2 skipped`.

**Checks.** `ruff check packages/model-schema` rc 0; `ruff format` applied; `mypy` "no issues found in 220 source
files"; `lint-imports` "4 kept, 0 broken"; `python3 scripts/audit-docs.py` fails check 31 (expected) and check 32 at
this ledger's Task 1 text naming RL-1404 (present before this task's change; not introduced here).

### Task 3 — the portfolio reader (executor-1386c, `echo $CLAUDE_EFFORT` printed `medium`)

**Red.** `uv run pytest packages/pricing-core/tests/test_rating_dislocation.py -q -p no:cacheprovider` (17 tests, no
module yet): `ModuleNotFoundError: No module named 'pricing_core.rating.analysis'`, 1 error during collection.

**Green.** Same command after `packages/pricing-core/src/pricing_core/rating/analysis.py`: `17 passed`. It covers the
reserved names (one test each), null, NaN or infinite, negative and missing exposure, a string exposure naming its
dtype, a missing, null and duplicated `quote_id`, a float and an absent segment, the admitted segment dtypes, the float
exposure read as `Decimal` of scale 6 (`0.1234567` → `0.123457`), the integer exposure read exactly, and every column
kept. Each refusal asserts `code == "VALIDATION_FAILED"` and, where a value could leak, that it is absent.

**Broken input (plan Step 4), each against the restored green file.** (1) The reserved-name loop emptied: `3 failed, 14
passed`. (2) `fill_null(0)` on exposure: `1 failed, 16 passed`. (3) The `is_nan() | is_infinite()` term removed: `1
failed, 16 passed`. (4) The counts moved into a `map_batches` evaluated only at `.collect()`: `5 failed, 12 passed` (the
tests call `read_portfolio` and never collect, so none raises). Restored: `17 passed`.

**Task 3 broken-input re-proof (2026-10-04 13:39 BST, executor-1386d, `echo $CLAUDE_EFFORT` printed `medium`).** The totals above were not
accepted alone, so each mutation was re-run against the green file at d2d6fe55 with `uv run pytest
packages/pricing-core/tests/test_rating_dislocation.py -q -rf --tb=line`, then restored (`git diff` empty after each).
Every failing line below is `test_rating_dislocation.py:26: Failed: DID NOT RAISE PortfolioFrameError`, the
`pytest.raises` in the `_refused` helper, so each fails because the refusal no longer happens, as the plan predicts.
(1) Reserved-name loop emptied (`_STAMPED = ()`): `3 failed, 14 passed`: `test_read_portfolio_refuses_a_purpose_column_by_name`,
`test_read_portfolio_refuses_each_other_stamped_column_by_name[effective_date]`, `[rating_version_ref]`. (2) `fill_null(0)`
on `exposure_years`: `1 failed, 16 passed`: `test_read_portfolio_refuses_a_null_exposure_naming_the_column_and_count`.
(3) `is_nan() | is_infinite()` term removed: `1 failed, 16 passed`: `test_read_portfolio_refuses_a_nan_exposure`.
(4) The count `select` moved into a `map_batches` evaluated only at `.collect()`: `5 failed, 12 passed`:
`..._a_null_exposure_naming_the_column_and_count` (the plan's named case), `..._a_nan_exposure`, `..._a_negative_exposure`,
`..._a_null_quote_id`, `..._a_duplicated_quote_id`. The four extra failures are the same property (the count-based refusals
are no longer at the call), not a different cause.

### Task 4 — the two passes and the per-policy frame (executor-1386d, `echo $CLAUDE_EFFORT` printed `medium`)

**Red.** `uv run pytest packages/pricing-core/tests/test_rating_dislocation.py -q` after adding the 10 Task 4 tests (27 in
the file): `ImportError: cannot import name 'dislocation_frame' from 'pricing_core.rating.analysis'`, 1 error during
collection. That is a whole-module red, not one per test; each test's own red is the broken-input runs below.

**Green.** Same command after `dislocation_frame`, `_score_pass` and `_origin_rung` in `analysis.py`: `27 passed`. Two
fixtures needed a change from the plan's sketch, found by running them: (a) `compile_bundle` and `_hand_compiled` both refuse
an expression step that consumes `secret_loading` (FR-212), so the step reads it as `(secret_loading ?? 0)` and lists no
`consumes`; with a bare `secret_loading` both runs were all `RATE_TABLE_MISS` error rows and the equality was vacuous; (b)
the rounding-only candidate sets `s_out_office` to `ceiling` (the fixture's risk premiums are whole numbers, so changing
`s_out_risk` moves nothing); office premiums 1435.5, 1631.25, 1864.5 give origin `[None, office_premium, office_premium]`.
`_origin_rung` compares `LadderRung.unrounded_minor`, already a `Decimal` on the model, so no second `Decimal(...)` is taken.

**Broken input (each against the restored green file; `-rf --tb=line`).** (1) Projection replaced by `portfolio.drop([])`:
`3 failed, 24 passed`: `test_dislocation_undeclared_column_never_reaches_the_engine` (`test_rating_dislocation.py:235:
AssertionError: assert False`, the with/without-column frames are unequal), `test_dislocation_undeclared_billing_named_column_refuses_no_row`
(`:245: assert 'error' not in ['error', 'error', 'error']`), `test_dislocation_each_pass_sees_only_its_own_contract`
(`:276: assert 'vehicle_group' not in ['quote_id', 'exposure_years', ...]`). (2) The collision loop emptied: `1 failed, 26
passed`: `test_dislocation_frame_refuses_a_colliding_portfolio_column` (`:296: Failed: DID NOT RAISE PortfolioFrameError`).
(3) `value_minor` comparison removed (an `unrounded_minor`-only rule): `1 failed, 26 passed`:
`test_dislocation_frame_origin_rung_is_the_first_differing_rung` (`:372: assert [None, None, None] == [None, 'offic...fice_premium']`).
(4) `str(...) != str(...)` on `unrounded_minor`: `1 failed, 26 passed`: `test_origin_rung_compares_unrounded_as_decimals_not_strings`
(`:379: assert 'risk_premium' is None`). A first version of (4) that compared the `Decimal` values directly passed 27 of 27,
because the model already holds a `Decimal`; the mutation was changed to compare `str()`. Restored: `27 passed`.

**Checks.** `ruff check .` all passed; `ruff format --check` on the two changed files clean; `mypy` "no issues found in 221
source files"; `lint-imports` "4 kept, 0 broken"; `python3 scripts/audit-docs.py` `FAILED (3)`: check 31 (gap 1403 to 9732) and
check 32 twice (this ledger's two earlier citations of #1102's ruling), the three Delta 2 expects.

### Task 5 — the summary: `select_movers`, `summarise_dislocation`, `dislocate` (executor-1386e, `echo $CLAUDE_EFFORT` printed `medium`)

**Red.** `uv run pytest packages/pricing-core/tests/test_rating_dislocation.py -q` after adding the 11 Task 5 tests (38 in
the file), no implementation: `ImportError: cannot import name 'dislocate' from 'pricing_core.rating.analysis'`, 1 error
during collection (`dislocate` is the first of the four new names in the import list; `select_movers` is the next). A whole-module red; each
test's own red is the mutation runs below. **Acceptance 7's red:** a first version of `summarise_dislocation` took the totals as
`pl.col("baseline_minor").cast(pl.Float64).sum()`; `test_dislocation_totals_are_sums_of_per_policy_minor_units` failed with
`pydantic_core._pydantic_core.ValidationError: 2 validation errors for DislocationTotals … baseline_premium_minor Input should be a
valid integer [type=int_type, input_value=8800.0, input_type=float]` (and `9580.0` for `candidate_premium_minor`). Before that, with the float
reaching `Fraction`, the same test failed `TypeError: both arguments should be Rational instances`. The float version was deleted; the totals are
`int(sum(...))` over the compared rows.

**Green.** Same file after the implementation in `analysis.py`: `38 passed`. The fixture is `_book16` (16 policies: nine at baseline 1000
spanning all six bands, two segment levels and a null level; a zero baseline P10; a negative baseline P11; one `quoted_to_declined`, one
`declined_both`, one `declined_to_quoted`, two `error` rows, one in both passes). Every expected figure is hand-computed in the test's
docstring from the fixture's integers. Percentages and shares are `Fraction` of ints rounded once with `round(fraction, n)`, converted to `Decimal`
exactly, and to `float` last. The banded set is `baseline_minor > 0`; the negative baseline is counted in `outcomes.negative_baseline` and enters the totals,
`by_segment` and `by_ladder_rung` only (RL-1402, Amendment N2). The mover order is `-Fraction(|chg|, base)`, `-|chg|`, `quote_id`.

**Mutations (each applied to the committed green `analysis.py`; `-q --tb=line`; restored with `git checkout -- analysis.py`, `git diff` empty after the run).**
(m1) totals summed over every quoted baseline row: `3 failed, 35 passed` — `totals_are_sums` `assert 9800 == 8800`; `change_pct_is_the_ruled_ratio` `assert -2.24 == 8.86`;
`by_ladder_rung_parts_sum_to_the_total` `1.73` against `1.93`. (m2) the unweighted mean of per-policy percentages: `3 failed, 35 passed` — `change_pct` `assert 2.0 == 8.86`;
two more fail with `ZeroDivisionError` on books with no banded policy (an artefact of the mutation). (m3) the two-step `Decimal` conversion (`prec=4`, then quantize): `3 failed, 35 passed` —
`test_dislocation_rounds_each_ratio_once` `assert 0.14 == 0.13`; the band shares (`0.1429` for `0.142857`) and the segment shares also fail, since four-digit contexts lose the
six-place share. (m4a) the edge test `>` for `>=`: `1 failed, 37 passed` — `bands_count_policies…` `assert [1, 1, 2, 2, 2, 1] == [1, 1, 1, 2, 2, 2]`. (m4b) the share denominator over the
compared set: `2 failed, 36 passed` — `bands_count…` `[0.111111, …] == [0.142857, …]` (and `empty_band_mean_is_none`). (m5) `0.0` for a zero denominator: `1 failed, 37 passed` —
`test_dislocation_empty_band_mean_is_none` `assert False`. (m6) nulls filtered out of `by_segment`: `1 failed, 37 passed` — `by_segment_reports_each_level` (the null row is missing).
(m7) every rung listed, no origin filter: `2 failed, 36 passed` — `by_ladder_rung_parts_sum…` and `dislocate_is_the_summary_of_the_frame_on_a_real_book` (`['risk_premiu…', …] == ['office_premium']`).
(m8) a both-pass error counted under both codes: `6 failed, 32 passed` — `ValidationError … DislocationRun` (the model's own `errors counts must sum to outcomes.error`), plus
`outcomes_and_errors_are_counted`. (m9a) movers sorted by signed change: `1 failed, 37 passed` — `assert ['X', 'B', 'E', 'A'] == ['X', 'A', 'B', 'E']`. (m9b) the `quote_id` tie-break dropped:
`1 failed, 37 passed` — `assert ['X', 'B', 'A', 'E'] == ['X', 'A', 'B', 'E']`. (m10) sort step 2 removed: `1 failed, 37 passed` —
`test_select_movers_breaks_a_pct_tie_by_absolute_minor_change`: `assert ['M1', 'M2'] == ['M2', 'M1']` (audit-9734 N1's quoted failure). (m11) the banded set `!= 0` for `> 0` (a negative baseline banded):
`6 failed, 32 passed` — `ValidationError` on the identity `distribution policies must equal quoted_both - zero_baseline - negative_baseline` (the Amendment N2 identity), plus the bands test.
Restored: `38 passed`.

**Checks.** `ruff check .` all passed; `ruff format --check` on the two changed files clean; `mypy` "no issues found in 221 source files"; `lint-imports` "4 kept, 0 broken";
`git grep -n 'compile_bundle\|compile_rating_version' -- packages/pricing-core/src/pricing_core/rating/analysis.py` printed nothing.

### Task 6 — NFR-495 across fresh interpreters (re-run at the mint step, executor-1386m, `echo $CLAUDE_EFFORT` printed `medium`; stamped 2026-10-04)

The Task 6 tests were committed at d538f3cb without a ledger entry (audit N-A). At the mint step only the two NFR-495 tests were re-run, each red produced by a throwaway edit to
`packages/pricing-core/tests/test_rating_dislocation.py`, restored with `git checkout -- <file>` (`git status --short` empty after each).
`test_dislocation_is_byte_identical_across_fresh_interpreters` compares `_child("1")` with `_child("2")` (`PYTHONHASHSEED` 1 and 2, one fresh interpreter each);
`test_the_comparator_can_fail_when_the_portfolio_changes` is its negative control.

**Red 1 (the `_child` helper renamed to `_child_x`).** `2 failed, 38 deselected`: both tests `NameError: name '_child' is not defined` (test file :800 and :806).
**Red 2 (the child's mutation switch disabled: `if len(sys.argv) > 2 and sys.argv[2] == "mutate":` replaced by `if False:`).** The comparator test alone: `1 failed, 39 deselected` with
`assert '{"baseline_ref":"rating_version:score-fixture@1",…"errors":[]}' != '{"baseline_ref":"rating_version:score-fixture@1",…"errors":[]}'` — the two runs are equal, so the `!=` comparator fails when the portfolio is not changed.
**Green (file restored).** `2 passed, 38 deselected in 13.11s` (`LOKY_MAX_CPU_COUNT=4`). No other test was run for this entry.

## Deviations and disclosures

1. **`<date>` is 2026-10-04**, the day of this commit; S1-S3 say "the merge date the executor writes", which this run cannot know. If the merge lands on a later day the lead may correct the three dated phrases (":1005", ":562", ":1077").
2. The ledger's front matter `id` carries the working id `LG-1406` in the form the branch's other working-id records use; no body header names it.
3. **Task 5 disclosure:** a `ruff format packages/pricing-core` run (broader than the two files) reformatted about ninety unrelated files; they were reverted with `git checkout --` before the commit, and the commit holds only `analysis.py`, `test_rating_dislocation.py` and this ledger.
4. **Task 5 deviation from the plan's sketch:** `by_ladder_rung`'s parts-sum test also checks the `Fraction` parts against the total by arithmetic on the frame's integer sums; the mutation named for it in the plan (an origin comparing `unrounded_minor` alone) belongs to Task 4's `_origin_rung`, so m7 above is this task's rung mutation.

5. **Delta 1 at the mint step:** the three `<date>` stamps (03:562, :1005, :1077) are left at 2026-10-04; the merge is expected the same day (mint-step brief, 2026-10-04). If it lands later, re-stamp them then.
6. **Delta 3 and N-C:** the Task 6 entry above was added and the stale `tree:` front matter corrected to origin/main `dfddfad8` (the merge base of the mint step). The Task 7 entry (gate stage table, wall times) belongs to the minted-head gate and is not written here.

## PRs

The slice's pull request is opened after the minted-head gate (Task 7); its number is recorded then. Until then the branch `sl-1386-dislocation-run` is pushed with no PR.
