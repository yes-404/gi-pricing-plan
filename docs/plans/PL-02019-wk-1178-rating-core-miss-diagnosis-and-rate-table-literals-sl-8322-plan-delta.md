---
id: PL-2019
family: plan
kind: map
title: WK-1178 — the rating-core group, a rate-table cell the engine can read and an exact refusal (FD-1648 HIGH, FD-1659, FD-1767, FD-1478, FD-1780, FD-1781), SL-2020 and SL 8345 — a dated Work-plan delta
status: active                   # draft → active → superseded | retired (§1.2a) — L1: draft→active rides the slice's PR
created: 2026-11-05             # filed under working id 8321
owner: planner
tree: dae9637ea6f6a56f6502e9db70392cdfb2f3983d
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [FD-1648, FD-1659, FD-1767, FD-1478, FD-1780, FD-1781, SL-1569, PL-1568, RL-1313, RL-1343, RL-1567, FR-214, FR-222, FR-234, FR-239, FR-255, FR-261, NFR-489]
---

# PL-2019 — WK-1178: the rating-core group (SL-2020 and SL 8345, a dated Work-plan delta)

> **For agentic workers:** this is a **dated Work-plan delta** under Lean P2 L1 (a')
> (`.claude/roles/planner.md`, "Lean P2"). It holds two slice rows and edits no filed plan. The
> executor's skills are `superpowers:test-driven-development`, `.claude/skills/python-test`,
> `.claude/skills/python-package`, `spec-change` and `git-hygiene`. PL 8321, SL 8322, LG 8323, SL 8345
> and LG 8346 are working ids reserved by the lead.

## Authority

- **The rulings on this plan, closed, verbatim** (the maintainer's entry "2026-11-05 10:11:39 GMT" in
  `~/gi-pricing-plan.local/channel/to-lead.md`):
  - "(1) FD-1767 does not reproduce at dae9637e because 96e1b369 (SL-1569) moved the declared-type form
    into `_build_outputs` shared by both paths — ACCEPTED: a guard test on BOTH paths (green at base; it
    is the essay's own discharge event, read to its asserts) and the closing act in the FD-1842 form
    naming 96e1b369; no code owed".
  - "(2) CONFIRMED: my 09:51:53 "the [mis-cited id, here elided so no unresolved id stands] rule" meant SL-1569's rule … my mis-citation; the plan quotes
    SL-1569 with that note". So the 09:51:53 ruling on FD-1767 stands with **SL-1569** read for the id it printed.
  - "(3) … SEVERITY RAISED TO HIGH for FD-1648 … R's DP RULED NOW so no seat waits: (i) `_format_value`
    writes FIXED-POINT, never an exponent — `format(value, 'f')` after quantising to the table's declared
    dp (or `.normalize()` only when it yields no exponent, with a test for 100, 1000, 0.5, 0.50, 1E+2
    inputs); (ii) WRITE-TIME REFUSAL: every rate-table write path (import, uplift, bulk operation)
    round-trips each cell through the engine's parser before commit and refuses the whole write with a
    coded 422 problem naming the first unparseable cell — a write never lands a cell the engine cannot
    read; (iii) SCORE-TIME: a cell that fails to parse is a HARD ERROR with a coded problem (never an
    omitted output, never a miss) — the same for FD-1478 (b); a catch-all rule is not a remedy. Red tests
    first for (i)–(iii), bit-identical goldens for every unchanged cell. R STAYS FIRST AFTER D; the plan
    re-sizes R with these three limbs (quote the hours) — if R exceeds ~14 h it splits into R1 (format +
    write-time refusal) and R2 (score-time error), R1 gated first. The widening is recorded as a dated
    line on FD-1648 and FD-1478, by the plan."
- **FD-1781, closed, verbatim** ("2026-11-05 09:51:53 GMT"): "(2) FD-1781 → a `TypeError` in `score` is a
  FAILURE of the property run, never a skip or a pass; `properties.py:118` catches it with the other two
  and reports it."
- **The order.** "2026-11-05 09:58:58 GMT": all FIX rows "coded and merged before Thu 12"; "only a slice
  still red at Wed 12:00 goes to the exception list".
- **FD-1478's own test of done.** "that change merges, proven on this table: case 2 must not raise
  `RATE_TABLE_MISS`, and case 1 must still raise it."
- **The triage.** `~/gi-pricing-plan.local/handover/p2-code-owed-triage-2026-11-05.md` (`b28ba8e9454c`) §3.

## Goal

A rate-table write never lands a cell the engine cannot read. A cell that is already stored and cannot be
read is a coded hard error at scoring, never an omitted output or a miss. A refused quote names what
happened. **No quote that prices correctly today changes, and the wire of a table with clean cells stays
byte-identical.**

## The split

The three limbs size at **14.25 h** (below), over the ~14 h line, so R splits as ruled:

| Slice | Ledger | Carries | h |
|---|---|---|---|
| **R1, SL-2020** | LG-2021 | Limbs (i) and (ii), compile's backstop, the goldens, FD-1767, FD-1780, FD-1781, the spec's FR-234 clause | 7.75 |
| **R2, SL 8345** | LG 8346 | Limb (iii), FD-1648 (b), FD-1478, FD-1659, the spec's FR-255 clause | 6.5 |

| Limb | h |
|---|---|
| Spec (both clauses) | 1 |
| (i) fixed point, `:166`, `_format_value` | 1 |
| (ii) write-time refusal over five paths, with the code | 3.5 |
| Compile's backstop | 0.5 |
| Goldens for unchanged cells | 0.75 |
| (iii) the sentinel and the post-evaluation check | 2 |
| The diagnosis (FD-1659, FD-1478) | 4 |
| FD-1767 0.5, FD-1780 0.5, FD-1781 0.75 | 1.75 |

Two SOLO gates, about 2.5 h each, not counted. R1 is gated first, and R2 branches from R1's merge.
**FD-1648 stays open across R1's merge and closes at R2's**; R1's register line says which limb landed.

## Evidence at `dae9637e`

Cites were read at `origin/main` `dae9637ea6f6a56f6502e9db70392cdfb2f3983d`. `git diff --stat dae9637e
2f108b1e -- packages backend scripts frontend deploy tests` is empty, so they hold at main of 10:36 UTC.
**Items marked RUN were executed by the planner** on tools-main's venv, read-only
(`PYTHONDONTWRITEBYTECODE=1`), scripts under `/tmp/plan-slices/`, on `zen-engine==0.53.0`.

**The engine's grammar (RUN).** `zen.evaluate_expression`:

| Literal | Engine | `Decimal` |
|---|---|---|
| `0.000000136`, `-1.5`, `+1.5`, `1.`, ` 1.5`, `1_000`, `1.36e-7`, `1e+2` | parses | parses |
| `1.36E-7`, **`1E+2`**, **`.5`** | `parserError: Incomplete parser output` | parses |

`evaluate_expression` costs about 1.1 µs a call (RUN), so 20 000 cells is about 22 ms. It is the engine's own
parser, as limb (ii) says; a regex would be a copy of its grammar.

**`_format_value`** (`rate_tables/operations.py:682-684`, `str(value.normalize())`) gives `1E+2` for 100 and
`1E+3` for 1000.00 (RUN). Its callers are every bulk operation through `_transform_rows` (`:687`) and
`uplift_by_filter` (`:751`). `_transform_rows` keeps the original string when `new == old`, so an unchanged
cell is already bit-identical.

**There is no declared dp.** `RateTableValue` (`packages/model-schema/src/model_schema/rating.py:1225`) has
`name`, `type`, `unit`, `min`, `max`. **The ruling's first form, "quantising to the table's declared dp", has
nothing to read**, and adding a field would change the contract and every stored version. So limb (i) takes the
ruling's second form: `format(value.normalize(), "f")`. For any value whose `str(normalize())` has no exponent
this is the same bytes as today (RUN: 0.5, 0.50 → `0.5`; 1E+2, 100, 1000 → `100`, `100`, `1000`), which is what
the goldens need.

**The write paths.** A class sweep, `git grep -n -E 'str\(Decimal|\.normalize\(\)|str\(value\b' origin/main --
packages/pricing-core/src/pricing_core/rate_tables backend/src/app/platform/rate_tables.py
backend/src/app/worker`, prints `:166` (`extract_relativity_table`) and `:684`. The paths that land a cell,
and the check each already runs:

| Path | Function | Check today |
|---|---|---|
| Seed from a model | `seed_from_model` (`:179`) via `:166` | the result is built here |
| Bulk | `uplift_table`, `uplift_by_filter`, `floor_and_cap`, `rebase_to_level` | `_validate_result` (`:577`) → `validate_rate_table` → `_value_issue` |
| Manual edit | `apply_cell_edits` (`:613`) | `_value_issue` per edit, raw text stored |
| Import | `_checked_import` (`:949`) | `validate_rate_table`, raw text stored; first issue raised |

**So `_value_issue` (`:299`) is the one choke point**: adding the parse there covers bulk, edit and import, and
`validate_rate_table` covers save. A refused import or edit stores nothing. **This replaces this plan's first
draft, which rewrote imported text positionally: the ruling is refuse.** `_map_operation_error`
(`backend/src/app/platform/rate_tables.py:126`) already turns `CODE: detail` into a 422 of that code, and
`_edit_failure` (`:971`) needs the new code in its `values_only` tuple (`:987`). `_validate_result` and
`_checked_import` raise `issues[0]`, which is the first by row order: the ruled "first unparseable cell".

**The essay's chain.** Step 2 says "Save, the bulk operations and compile all rely on this check". `compile.py`
has no call to `_value_issue` or `validate_rate_table`: **compile checks no cell today.** The backstop below
is in addition to limb (ii), for a stored version that predates it.

**A parse failure cannot be told from a miss by any field of the error (RUN).** One table `t`, one consumer `s`:

| Case | Engine outcome |
|---|---|
| `t` has no row | `NodeError … "a * 2" … nodeId: "s"` |
| `t`'s matched cell is `1.36E-7` | **the same**, nodeId `s`. The table silently omits its output |
| `t`'s cell is unparseable, nothing consumes it | evaluation succeeds; output absent |
| `s` fails on a good row (null division) | same type, nodeId `s` |
| catch-all rule, failing or sentinel output | no help (the ruling refuses it too) |
| `trace: true` on a failure | `"trace": null` |

**And `on_miss` does not bound this.** `RatingTableStep.on_miss` is `"error"` or `"default"` (`rating.py:385`).
`_check_lookup_misses` and the inference both look only at `"error"` steps. **On an `on_miss="default"` table an
unparseable cell reads as no value at all, and a consumer that tolerates that prices**: the ruled mis-price. So
limb (iii) must cover every table step. The first draft's guards covered `"error"` steps only and would not have.

**What does work (RUN).** Two generated pieces:

- **A sentinel cell.** Where a cell fails the parser, the wire carries `"'__UNPARSEABLE_CELL__'"`, a string
  literal, in place of the bad text. The output now exists: unconsumed it is in the result (`{'a':
  '__UNPARSEABLE_CELL__', 'b': 1}`); a tolerant consumer (`a == null ? 1 : 2`) passes and it is still in the
  result; an arithmetic consumer fails at nodeId `s`.
- **A guard node** after a table (only in the diagnostic decision), `a == '__UNPARSEABLE_CELL__' ? 1 * null : true`
  and `a == null ? 1 * null : true`: a failure then carries **the guard's own `nodeId`**. A good row passes, and a
  null division stays at `s`.

`decision.evaluate` inside a running event loop works on a handler-free decision (RUN); with a `customHandler`
it is R0's to confirm.

**FD-1659.** `_reraise_engine_failure` (`rating/score.py:550`) checks `tables` then `lookups` (`:585-588`). WF-699's
`s_premium` consumes both (`backend/tests/test_wf699_journey.py:582-588`).

**FD-1478.** Pinned by `test_the_stated_residual_still_reports_the_miss_code`
(`packages/pricing-core/tests/test_rating_score.py:882`), docstring `score.py:566-571`.

**FD-1767 does not reproduce (RUN).** `_probe_payload` (`test_rating_score_batch_outputs.py:132`) with `result_type`
`int` and `count`, a declared `decimal` output, dp 2, three rows: `score_one` serves `'18.00'`, `'22.00'`, `'25.00'`
and `score_batch`'s `outputs_json` the same. Both go through `_build_outputs` (`score.py:809`): `96e1b369`, #1387,
2026-10-25, after the essay's tree. No test holds the int-step form on both paths: `git grep -n 'FD-1767' origin/main
-- packages backend` prints nothing.

**FD-1780.** `predict` (`rating/runtime.py:881`): `if column in row and row[column] != value:`. Tests:
`packages/pricing-core/tests/test_rating_column_collision.py:153,168`.

**FD-1781.** `make_scorer.score` (`rating/properties.py:109-120`), the catch at `:118`, caching `None`.
`property_holds` `:326-327` returns `False`, and `monotone_sweep` `:275-276` returns `broken_at=(value, value)`. So
catching at `:118` is a failure in both, as ruled. The cause is not recorded: DP-R4.

**The tests a signature change touches.** `_reraise_engine_failure`'s direct callers: `test_rating_score.py:909,920,935`
and `test_safe_error.py:467`. `test_quote_input_raise_sites.py:76-77` counts raises (common seat brief, item 11).
`_failing_node` stays in `score.py`: `test_error_sinks.py`'s `_SINKS` lists it by function, and that file is H's.

**Hot path and hash.** `load_bundle` builds the decision from `to_wire(graph, payloads)` (`runtime.py:1112-1115`), so
the wire is derived on load and `bundle_hash` (`compile.py:676`) does not read it. `compile.py:25` already imports `zen`,
and `operations.py:59` already imports `pricing_core.rating.compile`, so `cell_parses` lives in `compile.py`.

## Decision points

The three limbs, FD-1767 and the mis-citation are ruled. **All three below are now ruled too** (the entry "2026-11-05 10:41:08
GMT"): DP-R1 (a); "THE CONSEQUENCE RULED: limb (iii) OVERRIDES FR-239 for a defective cell"; "a dated clause on FR-239 ("a
defective cell refuses regardless of hash; a clean bundle's wire is byte-identical") rides R2's PR as the spec change in the
same commit as the code; no opt-in flag"; the no-dp departure accepted; DP-R2 (a), `RATE_TABLE_CELL_UNPARSEABLE`; DP-R4 (a);
A12's inversion OK. The table is kept as the record of the options.

| DP | Question | Options | Recommendation |
|---|---|---|---|
| DP-R1 | **Does the mechanism satisfy limb (iii)? As a question, with the answer proposed.** The ruling says a bad cell is a hard error, and this plan keeps the live wire byte-identical for clean tables. | (a) **Yes: a sentinel cell + a post-evaluation check + the lazy guarded decision.** The wire changes only for a table holding a bad cell. Every such cell that a quote hits ends in a coded hard error, on every `on_miss`. Clean tables run the same bytes, so FR-239 and the readings stand. (b) Guards on the live decision: one more node per table on every quote, after the NFR-489 readings, and the sentinel is still needed. (c) Refuse the whole bundle at `load_bundle`: simple and total, but one bad cell then refuses quotes on keys that price correctly. | **(a).** **It changes one thing the first draft forbade, on purpose:** on an already-compiled bundle with a bad cell, a quote that hit it and passed through an `on_miss="default"` table now refuses on the same hash. That is limb (iii) overriding FR-239's "same hash, same answer" for a defective cell, and **the maintainer should say so in terms.** |
| DP-R2 | Which code for a cell the engine cannot parse, at write, compile and score? | (a) **A new `RATE_TABLE_CELL_UNPARSEABLE`**, one code for all three: `03` §5.2, `errors.py`, `_PER_QUOTE_CODES`. The ruling makes it a first-class failure and an HIGH finding, and neither "incomplete" nor "evaluation failed" says what to fix. (b) Reuse: `RATE_TABLE_INCOMPLETE` at write and compile, `RATING_EVALUATION_FAILED` at score. No new surface. | **(a).** Changed from the first draft's reuse, because the ruling widened the failure. The plan is written for (a); under (b) the code names change and nothing else. |
| DP-R4 | The ruling's "reports it" (FD-1781): is a `fail` status enough? `None` carries no cause. | (a) **Status only**: catch at `:118`, as ruled. (b) Also carry the exception type: a `PropertyResult` field and a contract change, for a latent LOW. | **(a).** The auditor's paragraph says the cause is not surfaced. |

**A12's test inversion:** OK given by the same entry (common seat brief, item 13).

## Acceptance Standard

Each item is checked by a command a fresh reviewer can run from the repository root on the named slice's merge tree.
Items 1 and 2 apply to this plan. **A1 to A11 are R1 (SL-2020). A12 to A18 are R2 (SL 8345).**

1. **This delta passes the docs checks on its branch.** `python3 scripts/audit-docs.py` prints no failing line except
   check 31 / check 32 lines naming working ids 8321, 8322, 8323, 8345 or 8346. After each mint, `audit-docs.py` and
   `doc-index.py --check` exit 0.
2. **No requirement range.** `grep -nE '(N?FR)-[0-9]+ *(-|to|–) *(N?FR-)?[0-9]+' <this file>` prints no line that stands
   for a set of ids.

**R1, SL-2020:**

- **A1. The write set.** `git diff --name-only origin/main...HEAD` lists only R1's Write set. Nothing under `frontend/`,
  `scripts/`, `deploy/` or `docs/contracts/`.
- **A2. Spec text first.** The `03` commit precedes the first code commit.
- **A3. Red first, by cause.** LG-2021 quotes T1 to T4, T10 and T11's reds from the slice's named base. A `NameError`,
  import or fixture failure is not the red.
- **A4. Limb (i).** T1 and T2 green: `_format_value` on 100, 1000, 0.5, 0.50 and 1E+2 gives `100`, `1000`, `0.5`, `0.5`,
  `100`, and a fitted `1.36e-7` is written `0.000000136`. `git grep -n -E 'str\(Decimal|\.normalize\(\)' --
  packages/pricing-core/src/pricing_core/rate_tables` prints only uses inside `_format_value`.
- **A5. Limb (ii).** T3 green, **on each of import, manual edit, uplift, uplift by filter, floor and cap, rebase and
  seed**: a cell of `1.36E-7`, `1E+2` or `.5` gives a 422 of the DP-R2 code naming the first such cell by key, and
  **nothing is written**. `1.36e-7` and `1_000`, which the engine reads, pass (T3's control). The route-level half
  (`test_api_rate_tables.py`) is proved in the gate.
- **A6. Compile's backstop.** T4 green: a stored version with such a cell does not compile; the code is DP-R2's, and the
  message names the table ref and the key. In addition to A5, not instead of it.
- **A7. Bit-identical goldens.** T8: over a fixture of at least 1 000 values, spanning magnitudes, for every value whose
  old form has no exponent, `_format_value` old == new, byte for byte, with the old expression held in the test. A bulk
  operation leaves every unchanged cell's bytes alone. No committed golden or fixture moves (`git diff
  origin/main...HEAD --stat -- '*golden*'` is empty).
- **A8. FD-1767.** T9 green at base and head, on both paths, recorded as a guard.
- **A9. FD-1780.** T10: two `float('nan')` on one column score; `Decimal('NaN')` likewise; NaN against a number raises
  `MODEL_CALL_FEATURE_COLLISION`; the existing two tests pass unedited.
- **A10. FD-1781.** T11: a `TypeError` from the evaluation makes `property_holds` `False` and `monotone_sweep` broken, and
  `build_run` gives `overall="fail"`. `NotImplementedError` still propagates, by the existing test.
- **A11. The gate and the closing acts.** The GREEN set by import closure (common seat brief, item 29). **The full code
  gate, both halves, SOLO**, green at the re-merged head, every rc quoted. **FD closing acts in the FD-1842 form, in the
  slice's own PR, by the slice's auditor:** FD-1767 (naming `96e1b369`, SL-1569), FD-1780, FD-1781. On FD-1648: **not a
  close**, the dated line recording the HIGH ruling, the widening to `_format_value`, and that limbs (i) and (ii) landed.
  **The LG Audit section, with the lead's adoption, lands in the audit's own commit**, and `docs/INDEX.md` is regenerated
  after the closing acts (common seat brief, item 17).

**R2, SL 8345:**

- **A12. The write set and the test changes.** `git diff --name-only origin/main...HEAD` lists only R2's Write set. Existing
  tests change in exactly three ways, each listed in LG 8346: the residual test, renamed and inverted (FD-1478 orders
  this); the four direct callers' arguments; the WF-699 comment. No assert is removed.
- **A13. Spec text first; red first.** The FR-255 clause precedes the code. LG 8346 quotes T5, T6 and T7's reds.
- **A14. Limb (iii).** T7 green on a hand-compiled bundle, four ways: a consumed table, an unconsumed one, an
  `on_miss="default"` table with a tolerant consumer, and a batch row. Each ends in the DP-R2 code. **None is
  `RATE_TABLE_MISS`, none is an omitted output, none is a quote.**
- **A15. The miss is exact.** T5: a step consuming a table and a lookup reports the one that missed, both ways round.
  T6: FD-1478's case 2 is `RATING_EVALUATION_FAILED`; case 1 stays `RATE_TABLE_MISS` by the unedited
  `test_a_rate_table_miss_is_refused_with_the_right_code`.
- **A16. The clean wire is byte-identical.** T12: the sha256 of `json.dumps(to_wire(graph, payloads), sort_keys=True)`
  for the fixtures equals the base's, the base's hash quoted from a run there. **A moved hash stops the slice.** A table
  with one bad cell differs in that cell only.
- **A17. The hot path.** LG 8346 quotes a before-and-after `timeit` of `score_one` on one fixture: the post-evaluation
  check is the only addition. No NFR reading is retaken or moved.
- **A18. The gate and the closing acts.** As A11, for R2's diff. **FD closing acts in the FD-1842 form, by R2's auditor:**
  FD-1648, FD-1659, FD-1478, with FD-1478's dated line recording the widening. **The LG Audit section, with the lead's
  adoption, lands in the audit's own commit.**

## Global Constraints

- **G1. No quote that prices correctly today changes.** The only changes on an existing bundle are the **code** of an
  already-refused quote, and a quote that hit an unparseable cell, which limb (iii) makes a hard error (DP-R1).
- **G2. A bad cell is never turned into a number at the wire.** `to_wire` either passes the text unchanged or carries the
  sentinel, which cannot price. Normalising `1E+2` to `100` there would quietly price what the ruling says to refuse.
- **G3. Money and exactness.** Positional text comes from `Decimal`, never a float (`CLAUDE.md` §7).
- **G4. `pricing-core` stays standalone.** No new dependency. `cell_parses` is in `rating/compile.py`, which both importers
  already reach; `uv run lint-imports` rc 0.
- **G5. `RateTableValue` gains no field,** and `model-schema` and the contracts do not change, under DP-R4 (a).
- **G6. Red first, by cause. No test is weakened** beyond A12.
- **G7. A message names no quote input** (NFR-499). FR-234's messages name the key and the submitted cell, as ruled for
  configuration (the entry "2026-10-10 22:16:18 BST").

## Needs

- **DB / Redis.** Neither slice needs a window: `packages/pricing-core/tests` run through
  `~/gi-pricing-plan.local/handover/run-small.sh`. `test_wf699_journey.py`, `test_score.py`, `test_score_compare.py` and
  `test_api_rate_tables.py` are in the gate's lane, not small runs (common seat brief, item 32). A pre-gate DB run, if
  wanted, is a lead grant, single-tenant on a `createdb -T` copy, never the template, on Redis `-n 11`, `12` or `13`, ending
  with the two quoted zeros. db 0 is live and is never touched.
- **Docker, NFR VM:** nothing.

## Tasks

### R1, SL-2020 — a write never lands a cell the engine cannot read

**The row.** First after SL-1689. WK-1178. One `sonnet` executor. Requirements: `03` FR-234, FR-214 (guard), FR-222,
FR-261. Register: FD-1767, FD-1780, FD-1781 close; FD-1648 gains its line. **Size 7.75 h.** Depends on: the GO; a gate slot.

**R1.0 — premises and spec.** Re-read every cite at the base. Amend `docs/specs/03-rating-engine.md` under `spec-change`,
dated, citing this plan and the 10:11:39 entry. **FR-234**, appended: every value is a decimal the rating engine's
expression parser reads. Every path that writes a value checks it before commit and refuses the whole write, naming the
first cell it refuses, with the DP-R2 code. A value the platform computes is written in fixed point, without an exponent.
`03` §5.2 gains the code. Commit alone.

**R1.1 — limb (i), red first.** `test_rate_table_operations.py` and `test_rate_table_bulk_ops.py`, `req("FR-234")`:

- **T1** `test_format_value_is_fixed_point`, the five inputs of A4. **Red:** `'1E+2'`, `'1E+3'`.
- **T2** `test_a_small_fitted_relativity_is_written_positionally`. **Red:** `'1.36E-7'`.

```python
def _format_value(value: Decimal) -> str:
    """Fixed point, trailing zeros dropped: never a float (R2), never an exponent (FD-1648).
    `RateTableValue` declares no dp, so this normalises and formats (the entry 10:11:39, (i))."""
    return format(value.normalize(), "f")
```

`:166`: `format(Decimal(str(level.relativity)), "f")`.

**R1.2 — limb (ii), red first.** **T3**, parametrised over the seven paths of A5, `req("FR-234")`. **Red:** each path
accepts, and the result holds the bad text.

```python
def cell_parses(raw: str) -> bool:
    """Whether the engine's own parser reads `raw` as a number (FD-1648): `Decimal` is wider."""
    try:
        return isinstance(zen.evaluate_expression(raw), (int, float))
    except RuntimeError:
        return False
```

in `rating/compile.py`. `_value_issue`, after `is_finite` and before the bounds: a `ValidationIssue` with the DP-R2 code
and FR-234's message form, `value {raw!r} for key {key_values} is not a number the rating engine can read`.
`backend/src/app/platform/rate_tables.py`: the code in `_VALIDATION_CODES` if `_map_operation_error` needs it, and in
`_edit_failure`'s `values_only`. `errors.py`: `RATING_ERROR_CODES`. **Edit and import keep the submitted text**: no rewrite.

**R1.3 — compile's backstop.** **T4** `test_a_stored_cell_the_engine_cannot_read_does_not_compile`, with the control
`1.36e-7`. `_refuse_unparseable_cells(version, payloads)` beside `_refuse_control_factor_keys`. `load_bundle` is not changed.

**R1.4 — goldens.** **T8** `test_format_value_is_bit_identical_where_it_was_already_fixed_point`.

**R1.5 — FD-1767.** **T9**, `test_rating_score_batch_outputs.py`, `req("FR-214")`:
`test_an_int_or_count_step_into_a_decimal_output_is_one_string_on_both_paths`, from `_probe_payload`, asserting `'18.00'` from
`score_one` and in `outputs_json`. Green at base.

**R1.6 — FD-1780.** **T10**, `test_rating_column_collision.py`, `req("FR-222")`. **Red:** the collision on two NaN.

```python
def _same_value(a: Any, b: Any) -> bool:
    """Equal, or both NaN: NaN is the one value unequal to itself (FD-1780)."""
    return bool(a == b or (a != a and b != b))
```

`runtime.py:881`: `if column in row and not _same_value(row[column], value):`.

**R1.7 — FD-1781.** **T11**, `test_testing.py`, `req("FR-261")`: monkeypatch
`pricing_core.rating.properties._score_context_sync` to raise `TypeError("x")`. **Red:** it propagates. `:118`: `except
(ValueError, RuntimeError, TypeError):`, and the docstring (`:101-103`) names it, citing the ruling.

**G.** Full code gate, both halves, SOLO, after a re-merge and the GREEN set. Small runs include
`test_quote_input_raise_sites.py` (item 11). CI set from the three-dot diff; `packages/pricing-core/**` modelling paths
fire `frontend.yml`.

**R1 write set.** `rate_tables/operations.py`; `rating/compile.py`, `rating/runtime.py` (`:881`), `rating/properties.py` under
`packages/pricing-core/src/pricing_core/`; `backend/src/app/platform/rate_tables.py`, `backend/src/app/errors.py`;
`test_rate_table_operations.py`, `test_rate_table_bulk_ops.py`, the compile test home, `test_rating_score_batch_outputs.py`,
`test_rating_column_collision.py`, `test_testing.py` under `packages/pricing-core/tests/`; `backend/tests/test_api_rate_tables.py`;
`docs/specs/03-rating-engine.md`; LG-2021. At the mint: the SL-2020 row, `docs/INDEX.md`, FD essays and `docs/findings/register.md`
(A11). **This plan's `status:` moves at R2's mint.**

### R2, SL 8345 — a bad cell is a hard error, and a refusal says why

**The row.** Branches from R1's merge. WK-1178. One `sonnet` executor. Requirements: `03` FR-255, FR-239 (the ruled clause), NFR-489
(read). Register: FD-1648, FD-1659, FD-1478 close. **Size 6.5 h.** Depends on: R1 merged; a gate slot.

**R2.0 — premises and spec.** Confirm a real bundle's decision, with its `customHandler`, evaluates from inside `async def`
(`test_rating_score_batch_outputs.py`'s GBM fixture). If not: `await async_evaluate` on the `score_one` path, `evaluate` on batch,
and the LG says why. **FR-255**, appended: a refused quote's code comes from what failed, not from what the failing step
consumes; an `on_miss="error"` step that found no row is `RATE_TABLE_MISS` or `REFERENCE_LOOKUP_MISS` for that step, a step
consuming both included; a cell the engine cannot parse is a hard error of the DP-R2 code, on every `on_miss`, never an omitted
output or a miss. Closes `RL-1313` DP-G4's stated limit. **FR-239**, the ruled dated clause: "a defective cell refuses
regardless of hash; a clean bundle's wire is byte-identical". The FR-255 clause commits alone; **the FR-239 clause rides the
code's commit, as ruled.**

**R2.1 — red first.** `test_rating_score.py`, `req("FR-255")`:

- **T5** `test_a_step_consuming_a_table_and_a_lookup_reports_the_one_that_missed`, both ways. **Red:** `RATE_TABLE_MISS` for the
  lookup.
- **T6** the residual test renamed `test_a_failure_in_a_step_consuming_a_table_is_not_a_miss`, `match` now
  `^RATING_EVALUATION_FAILED:`. **Red:** `RATE_TABLE_MISS`.
- **T7** `test_an_unparseable_cell_is_a_hard_error`, via `_hand_compiled`, A14's four cases. **Red:** `RATE_TABLE_MISS`, or a
  quote.
- **T12** `test_a_clean_table_has_a_byte_identical_wire`, a guard: the base's hash a constant, its tree in a comment.

**R2.2 — the sentinel, `rating/runtime.py`.** `UNPARSEABLE_CELL = "__UNPARSEABLE_CELL__"`. `:287`:

```python
"o0": cell if cell_parses(cell := str(row[value_column])) else json.dumps(UNPARSEABLE_CELL),
```

The parse runs at load: about 1.1 µs a cell, and a parquet-sized table's cost is quoted in the LG.

**R2.3 — the post-evaluation check, `rating/score.py`.** In `_check_lookup_misses` (`:517`, called at `:964`), or beside it,
for **every** `RatingTableStep`, whatever its `on_miss`, **before** the miss check: an output equal to `UNPARSEABLE_CELL` raises the
DP-R2 code, naming the step and not the value. `_build_outputs` never sees it.

**R2.4 — the diagnosis, `rating/runtime.py`.**

- `MISS_GUARD_PREFIX = "__miss_guard__"`, `CELL_GUARD_PREFIX = "__cell_guard__"`. `_guard_node(step_id, prefix, names, test)`: an
  `expressionNode`, one expression per name, `f"{test} ? 1 * null : true"`, `passThrough` true.
- `to_wire(graph, payloads=None, *, guards=None)`. `guards: Mapping[str, tuple[Sequence[str], bool]] | None` maps a table or lookup
  step to its produced names and whether `on_miss == "error"`. When `None`, nothing changes (T12). When given, the path at
  `:555-566` adds, after that step, a cell guard for a table, and a miss guard when the flag is set.
- `PurposeEvaluation` gains `diagnose: Callable[[Mapping[str, Any]], RuntimeError | None]`, a closure from `evaluation()` in
  `load_bundle` that on first call builds the guarded decision on the same `engine`, memoises it, evaluates the context, and
  returns the `RuntimeError` it raises, or `None`. Two first calls may both build: harmless.

**R2.5 — the refusal, `rating/score.py`.** `_reraise_engine_failure(evaluation, context, exc)`:

- `diagnosed = evaluation.diagnose(context)`, `node = _failing_node(diagnosed) if diagnosed else None`.
- `CELL_GUARD_PREFIX`: the DP-R2 code, naming the step. `MISS_GUARD_PREFIX`: `RATE_TABLE_MISS` or `REFERENCE_LOOKUP_MISS` by the
  step's type.
- Anything else, including `None` or the re-evaluation raising: `RATING_EVALUATION_FAILED`, the message keeping
  `_failing_node(exc)`'s step.
- `consumes_output_of` and the `tables` / `lookups` lists go. The "stated limit" paragraph goes; a new one says why the live
  wire has no guards (DP-R1).
- The two callers (`:1039`, `:1220`) pass `evaluation` and `context`. The four direct test calls gain them (A12): a stub with
  `diagnose=lambda _: None`.
- `backend/tests/test_wf699_journey.py:582-584`: the comment is corrected, and any assert that reads the code changes with it.

**G.** As R1. **Regression risk is high for a small diff:** `score.py` and `runtime.py` sit under every quote, which is what A16 is
for.

**R2 write set.** `rating/runtime.py`, `rating/score.py` under `packages/pricing-core/src/pricing_core/`; `backend/src/app/api/score.py`
only if `_PER_QUOTE_CODES` lives there; `packages/pricing-core/tests/test_rating_score.py`, `test_safe_error.py`,
`test_quote_input_raise_sites.py` if a count moves; `backend/tests/test_wf699_journey.py`; `docs/specs/03-rating-engine.md`; LG 8346.
At the mint: the SL 8345 row, `docs/INDEX.md`, this plan's `status:`, the three essays and `docs/findings/register.md` (A18).

*(2026-11-05 16:47 GMT, exec-sl8345j, to-lead "2026-11-05 16:41:58 GMT": R2's Write set is widened by `examples/fremtpl2/journey.py` (B3's refused-quote code, FD-1659), after the auditor's finding; with the earlier widenings by ruling named in LG-2039's Scope.)*

### Files shared with other groups

`03-rating-engine.md`: A (FR-235 pointer), a different row. `pricing-core/rating/*`: none of C, T, A, H, F write it. `errors.py`: **A adds
`PAYLOAD_TOO_LARGE`**, a different set: a textual re-merge at most. `test_error_sinks.py`: H; R adds no sink under the name census, and
H re-derives after R. **Safe in parallel with A, C, T, H, F. Before LAST-1.** R2 is serial after R1.

## Hand-off (not this plan's writes)

- All DPs ruled (10:41:08).
- The rows and mints, the gate slots: the lead. The LGs: the executors. A11 and A18: each slice's auditor.
- **For the lead, before the demo seed and SL-1913:** a stored Rate Table Version made by a bulk operation may already hold a `1E+2`
  cell. After R1 a new compile over it is refused, naming the key; after R2 a compiled bundle's quote that hits it is a hard error.
  **The read-only census is ruled and owned** (10:41:08 (4)): the lead's or a seat's, not this plan's. A hit is a MEDIUM data finding
  with its remediation, which may be "a re-format migration in R2's scope": then R2's write set and size change by a dated delta.

## Self-review

1. **Every cite was read** at `dae9637e`, and main at `2f108b1e` moved none of these trees. RUN items say so. The one premise left is
   R2.0's.
2. **Requirements by id**, no range. **No placeholder.**
3. **Each finding has its own red by cause**, except FD-1767, which has none to have.
4. **Rulings carried verbatim, and two departures named:** no declared dp exists, so limb (i) takes the ruling's second form; and DP-R1
   states the FR-239 consequence of limb (iii).
5. **The first draft's errors are gone:** it rewrote imported text (the ruling refuses), and its guards covered `on_miss="error"` only.
6. **Calendar:** `date -d 2026-11-12 +%A` is Thursday, and 11 Nov is Wednesday.
