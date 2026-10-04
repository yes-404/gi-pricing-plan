---
id: LG-9732
family: ledger
title: WK-673 slice SL-1386 — the Dislocation Run on ZEN in integer minor units, spec first (PL-1403, RL-1402)
status: active
created: 2026-10-04
owner: executor
tree: bb12d1e5cc1f0bfc76a56dc1a6b3364a505d7349
phase: P2
work: WK-673
slice: SL-1386
plans: [PL-1403]
corrected_by: []
relates: [RL-1402, RL-1394, RL-1264, RL-1263, PL-1267, PL-1395, LG-1400]
---

# LG 9732 (working id) — WK-673 slice SL-1386, the Dislocation Run on ZEN

Executed from `PL-1403` by `executor-1386` (sonnet; `echo $CLAUDE_EFFORT` printed `medium`). Branch
`sl-1386-dislocation-run`. Stamps are BST (`TZ=Europe/London date`). The ledger's working id is `9732`, allocated by
the lead 2026-10-04 13:01:36 BST; it is renumbered at the mint. This ledger covers **Tasks 0 and 1** (the first
executor turn); later tasks are appended.

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

## Deviations and disclosures

1. **`<date>` is 2026-10-04**, the day of this commit; S1-S3 say "the merge date the executor writes", which this run cannot know. If the merge lands on a later day the lead may correct the three dated phrases (":1005", ":562", ":1077").
2. The ledger's front matter `id` carries the working id `LG-9732` in the form the branch's other working-id records use; no body header names it.

## PRs

None opened: this turn is Tasks 0 and 1 only; branch `sl-1386-dislocation-run` pushed, no PR (the lead's instruction).
