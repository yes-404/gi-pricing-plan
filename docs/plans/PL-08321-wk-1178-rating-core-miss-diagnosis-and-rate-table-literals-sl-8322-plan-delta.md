---
id: PL-8321
family: plan
kind: map
title: WK-1178 — the rating-core group, an engine-parseable rate-table cell, an exact miss diagnosis, and three small fixes (FD-1648, FD-1659, FD-1767, FD-1478, FD-1780, FD-1781), SL-8322 — a dated Work-plan delta
status: draft                   # draft → active → superseded | retired (§1.2a) — L1: draft→active rides the slice's PR
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

# PL-8321 — WK-1178: the rating-core group (SL 8322, a dated Work-plan delta)

> **For agentic workers:** this is a **dated Work-plan delta** under Lean P2 L1 (a')
> (`.claude/roles/planner.md`, "Lean P2"). It holds one slice row, SL 8322, and edits no filed plan.
> The executor's skills are `superpowers:test-driven-development`, `.claude/skills/python-test`,
> `.claude/skills/python-package`, `spec-change` (R0 only) and `git-hygiene`. PL 8321, SL 8322 and
> the ledger LG 8323 are working ids reserved by the lead.

## Authority

- **The user's decision and the order.** The maintainer's entry "2026-11-05 09:58:58 GMT" in
  `~/gi-pricing-plan.local/channel/to-lead.md`: "ALL 24 FIX-BEFORE-FREEZE rows AND FD-1337 (7 h) AND
  FD-1484 (8 h) are coded and merged before Thu 12"; "ORDER: WK-674's pair first … then the 7
  grouped slices by G1 value then hours (R, C, T, A, H, D, F)"; "a red gate = fix-and-regate within
  the chain, and only a slice still red at Wed 12:00 goes to the exception list".
- **The rulings, closed, verbatim** (the entry "2026-11-05 09:51:53 GMT"):
  - "(1) FD-1767 → (a) `/score` serialises by the declared output type exactly as batch does (one
    serialiser, the FD-1569 rule on every scoring path), not a compiler refusal." *(There is no
    FD-1569 on main. It reads as SL-1569; see DP-R3.)*
  - "(2) FD-1781 → a `TypeError` in `score` is a FAILURE of the property run, never a skip or a pass;
    `properties.py:118` catches it with the other two and reports it."
- **The triage.** `~/gi-pricing-plan.local/handover/p2-code-owed-triage-2026-11-05.md`
  (`b28ba8e9454c`) §3, Slice R.
- **FD-1478's own test of done.** "that change merges, proven on this table: case 2 must not raise
  `RATE_TABLE_MISS`, and case 1 must still raise it."
- **RL-1313 DP-G4 and the residual.** FD-1478 records the maintainer's acceptance of the residual
  (entry "2026-09-30 11:07:11 BST") with this finding as its owner; the fix discharges it.

## Goal

A rate-table cell is written in a form the engine parses, compile refuses one that is not, and a
refused quote names what actually happened: which table or lookup missed, or that the failure was
something else. FD-1648, FD-1659, FD-1478, FD-1767, FD-1780 and FD-1781 close. **No priced quote
changes, and the wire of a scored quote stays byte-identical.**

## Evidence at `dae9637e`

Cites were read at `origin/main` `dae9637ea6f6a56f6502e9db70392cdfb2f3983d`. **Items marked RUN were
executed by the planner** on tools-main's venv, read-only (`PYTHONDONTWRITEBYTECODE=1`), scripts
under `/tmp/plan-slices/`: `zen-engine==0.53.0` (`packages/pricing-core/pyproject.toml:64`).

**The engine's grammar (RUN).** `zen.evaluate_expression`:

| Literal | Engine | `Decimal` |
|---|---|---|
| `0.000000136`, `-1.5`, `+1.5`, `1.`, ` 1.5`, `1_000`, `1.36e-7`, `1e+2` | parses | parses |
| `1.36E-7`, **`1E+2`**, **`.5`** | `parserError: Incomplete parser output` | parses |

So the engine refuses the upper-case exponent and a leading point, and FD-1648's essay understates
the first: **`_format_value`** (`rate_tables/operations.py:682-684`, `str(value.normalize())`) gives
`1E+2` for 100 and `1E+3` for 1000.00 (RUN). Every uplift, floor-and-cap or rebase result that
normalises to a round power goes through it, on any book size. The essay's "not reached by the
demo's fits" is about `:166` only.

**Every write site (a class sweep).** `git grep -n -E 'str\(Decimal|\.normalize\(\)|str\(value\b'
origin/main -- packages/pricing-core/src/pricing_core/rate_tables
backend/src/app/platform/rate_tables.py backend/src/app/worker` prints exactly two: `:166`
(`extract_relativity_table`) and `:684` (`_format_value`). The other two ways in store the raw text:
`apply_cell_edits` (`:613`, `replaced[position[key]] = row[table.value.name]`) and the import path
(`_checked_import`, `:949`, `ImportResult(cells=tuple(file_rows), …)`).

**The essay's chain is out of date in two places.**

- Step 2 says "Save, the bulk operations and compile all rely on this check". `compile.py` has no
  call to `_value_issue` or `validate_rate_table` (`git grep -n
  'validate_rate_table\|_value_issue' origin/main -- packages/pricing-core/src/pricing_core/rating/compile.py`
  prints nothing). **Compile checks no cell today.**
- Limb (b) assumes a parse failure can be told from a miss at the failing step. **It cannot, by any
  field of the error (RUN):**

| Case, one table `t`, one consumer `s` | Engine outcome |
|---|---|
| `t` has no row | `NodeError … "a * 2" … nodeId: "s"` |
| `t`'s matched cell is `1.36E-7` | **the same**, nodeId `s`. The table silently omits its output |
| `t`'s cell is unparseable and nothing consumes it | evaluation succeeds; output absent |
| `s` itself fails on a good row (null division) | same type, nodeId `s` |
| catch-all rule with a failing or a sentinel output | **no help**: omitted, or fails at `s` |
| `trace: true` on a failure | `"trace": null` |

**The mechanism that works (RUN).** A generated expression node immediately after the table,
`a == null ? 1 * null : true`, gives: row hit → passes, no change to `b`; miss → `NodeError` with
**`nodeId` the guard's own id**; a string output → passes; a null division at `s` → `nodeId: "s"`, as
before. So a guard turns the inference into a fact: DP-R1. `decision.evaluate` called inside a running
event loop works on a handler-free decision (RUN); with a `customHandler` that is not yet run (R0).

**FD-1659.** `_reraise_engine_failure` (`rating/score.py:550`) checks `tables` then `lookups`
(`:585-588`). The cause is in the same inference. WF-699's `s_premium` consumes both
(`backend/tests/test_wf699_journey.py:582-588` carries the comment naming this).

**FD-1478.** The residual is pinned by `test_the_stated_residual_still_reports_the_miss_code`
(`packages/pricing-core/tests/test_rating_score.py:882`), in the docstring at `score.py:566-571`.

**FD-1767 does not reproduce (RUN).** The `_probe_payload` form from
`test_rating_score_batch_outputs.py:132`, with `result_type` set to `int` and to `count`, a declared
`decimal` output, dp 2, three rows: `score_one` serves `'18.00'`, `'22.00'`, `'25.00'` and
`score_batch`'s `outputs_json` carries the same strings. Both go through `_build_outputs`
(`score.py:809`, rounding by `round_to_text` for `_DECIMAL_FAMILY`). SL-1569 (#1387, `96e1b369`,
2026-10-25) landed that, after the essay's tree `cf509df8`. **`_coerce_output_value` being batch-only
(the triage's state line) is true and is not the defect:** it checks and converts nothing. No test
holds the int-step form on both paths: `git grep -n 'FD-1767' origin/main -- packages backend`
prints nothing. The essay's discharge event still names one. DP-R3.

**FD-1780.** `predict` (`rating/runtime.py:881`): `if column in row and row[column] != value:`. The
essay's branch lines became `:881` on main. Comment: "Equal values are the ordinary shared-column
case." Tests live in `packages/pricing-core/tests/test_rating_column_collision.py` (`:153`, `:168`).

**FD-1781.** `make_scorer.score` (`rating/properties.py:109-120`), `except (ValueError, RuntimeError):`
at `:118`, caching `None`. **What `None` then means, read:** `property_holds` `:326-327` returns
`False`; `monotone_sweep` `:275-276` returns `broken_at=(value, value)`. So catching at `:118`
is a *failure* in both and never a skip or a pass, as the ruling requires. The cause is not recorded
anywhere: DP-R4. `make_scorer` has callers in `rating/replay.py` and `rating/testing.py`; the catch is
one place.

**The tests a signature change touches.** `_reraise_engine_failure`'s direct callers:
`test_rating_score.py:909,920,935` and `test_safe_error.py:467`; `test_quote_input_raise_sites.py:76-77`
counts the function's raises (common seat brief, item 11, binds that file into every small run).

**Hot path and hash.** `load_bundle` builds the decision from `to_wire(graph, payloads)` at
`runtime.py:1112-1115`, so the wire is derived on load and `bundle_hash` (`compile.py:676`) does not
read it. `to_wire`'s linear path is `:555-566`.

## Decision points

For the maintainer, on the GO. Each is ruled before the slice starts.

| DP | Question | Options | Recommendation |
|---|---|---|---|
| DP-R1 | How does a refused quote learn its cause (FD-1648 (b), FD-1659, FD-1478)? | (a) **Guards on the live decision:** `to_wire` always adds a guard after each `on_miss="error"` step. Simple and exact; every quote pays one more node per such step, the trace must skip them, and the hot path changes after the NFR-489 readings. (b) **A diagnostic decision, built lazily:** the live wire stays byte-identical; on the first engine failure of a graph, that worker builds a second decision with guards, re-evaluates the failing context once on it, and takes the `nodeId`. (c) Truncate the graph at the failing step and re-evaluate. More code than (b), no more knowledge. (d) Report both candidates for FD-1659, as its essay allows, and leave FD-1478 open. | **(b).** A priced quote runs the same bytes, so FR-239 and the readings already taken are untouched, and the cost falls only on a refused quote: one more evaluation, and one `create_decision` per graph per worker, once. (a) is the shorter diff and the one to take only if a re-evaluation is ruled unacceptable. (d) leaves the triage's row open. |
| DP-R2 | Compile's refusal of a cell the engine cannot parse: which code? | (a) **`RATE_TABLE_INCOMPLETE`**, already where FR-234's value failures map (`backend/src/app/platform/rate_tables.py:114-120`) and already in `errors.py:348`. No contract or code-table change. (b) A new code, `03` §5.2 and `errors.py` first. Clearer to read; more surface before a freeze. | **(a).** The message carries the table ref and the key, so the code need not. |
| DP-R3 | FD-1767 does not reproduce. What is the row now? | (a) **A guard test, then the closing act**: the essay's named test over `int` and `count` steps into a `decimal` output on both paths, green at base, recorded as a guard; the ruling stands satisfied by SL-1569 (#1387). (b) Close it now by a dated line, with no test. | **(a).** The essay's discharge event names that test, nothing else holds that form, and it costs 0.5 h. **The ruling's "FD-1569" is read as SL-1569; the maintainer confirms.** |
| DP-R4 | The ruling's "reports it" (FD-1781): is a `fail` status enough? `None` carries no cause, so the run says which property and case failed and not that a `TypeError` was why. | (a) **Status only**: catch at `:118`, as ruled; the run is `fail`, the counterexample is the case. (b) Also carry the exception type: `Scorer` returns a failure record, `PropertyResult` gains a field, and the contract regenerates. | **(a).** The ruling names the line and "with the other two"; (b) is a contract change for a latent LOW (no seeded algorithm reaches it), and the essay's "lost message" stays with `SanitisedError`. If (a), the auditor's closing paragraph says the cause is not surfaced. |

## Acceptance Standard

Each item is checked by a command a fresh reviewer can run from the repository root on the slice's
merge tree. Items 1 and 2 apply to this plan; A1 to A14 apply to the slice.

1. **This delta passes the docs checks on its branch.** `python3 scripts/audit-docs.py` prints no
   failing line except check 31 / check 32 lines naming working ids 8321, 8322 or 8323. After the
   mint, `audit-docs.py` and `doc-index.py --check` exit 0.
2. **No requirement range.** `grep -nE '(N?FR)-[0-9]+ *(-|to|–) *(N?FR-)?[0-9]+' <this file>` prints
   no line that stands for a set of ids.

The slice:

- **A1. The write set.** `git diff --name-only origin/main...HEAD` lists only the Write set below.
  Nothing under `frontend/`, `scripts/`, `deploy/`, `docs/contracts/` or `packages/model-schema/`.
- **A2. Spec text first.** The `docs/specs/03-rating-engine.md` commit precedes the first code commit
  in `git log --reverse origin/main..HEAD`, and `audit-docs.py` passes at it but for the working ids.
- **A3. Red first, by cause, one per finding.** LG 8323 quotes, from the slice's named base, the
  red lines T1 to T7, T10 and T11. A `NameError`, an import or a fixture failure is not the red.
- **A4. Writes are positional.** T1, T2 and T3 green. `git grep -n -E 'str\(Decimal|\.normalize\(\)'
  -- packages/pricing-core/src/pricing_core/rate_tables` prints only uses inside the positional
  helper.
- **A5. Compile refuses.** T4 green: a table with `1.36E-7`, `1E+2` or `.5` in a cell does not
  compile, the code is as DP-R2 rules, and the message names the ref and the key and no value
  beyond the raw text FR-234 already prints. `1.36e-7` still compiles (T4's control).
- **A6. The miss is exact.** T5 and T6 green: a step consuming a table and a lookup reports the one
  that missed, both ways round; FD-1478's case 1 still raises `RATE_TABLE_MISS` by the unedited
  `test_a_rate_table_miss_is_refused_with_the_right_code`; case 2 raises `RATING_EVALUATION_FAILED`.
- **A7. A parse failure is not a miss.** T7 green, on a hand-compiled bundle, for a consumed table
  and an unconsumed one.
- **A8. The live wire is byte-identical.** T8 green: the sha256 of `json.dumps(to_wire(graph,
  payloads), sort_keys=True)` for the fixtures at the slice's base equals the head's. The LG quotes
  both hashes from a run on each. **A diff that moves this hash stops the slice.** (Under DP-R1 (a)
  this item becomes: the LG quotes before-and-after `decision.evaluate` timings on one fixture, and
  the lead rules on the readings.)
- **A9. FD-1767.** T9 green at base and head, recorded as a guard, under the ruled DP-R3.
- **A10. FD-1780.** T10: two `float('nan')` on one column score; `Decimal('NaN')` likewise; NaN
  against a number raises `MODEL_CALL_FEATURE_COLLISION`; the existing two tests pass unedited.
- **A11. FD-1781.** T11: a `TypeError` from the evaluation makes `property_holds` `False` and
  `monotone_sweep` broken, and `build_run` gives `overall="fail"`. `NotImplementedError` still
  propagates, by the existing test, unedited.
- **A12. The changed tests.** `git diff origin/main...HEAD -- '*test*.py'` changes existing tests in
  exactly three ways and the LG lists each: the residual test, renamed and inverted (FD-1478 orders
  this; **the lead's adoption of this plan is the OK of common seat brief item 13**); the four direct
  callers' argument lists; the WF-699 comment. No assert is removed.
- **A13. The GREEN set and the gate.** The GREEN set by import closure (common seat brief, item 29),
  commands and list in the LG. **The full code gate, both halves, SOLO**, green at the re-merged
  head, every rc quoted. `generate-contracts.py --check` rc 0; `req-coverage.py` rc 0. FR-255 and
  FR-234 tests carry their `req` markers.
- **A14. FD closing acts, in the FD-1842 form, in the slice's own PR, by the slice's auditor**, one
  for each of the six findings: the essay's `status: closed`, `relates:` gaining the slice's ids, a
  `***Resolved <date>***` paragraph naming the delivered remedy, its red and its LG, the same on
  the register row, and the PR number and squash at the merge's date of record. FD-1767's paragraph
  names SL-1569 as the fix. **The LG Audit section, with the lead's adoption, lands in the audit's own
  commit**, and `docs/INDEX.md` is regenerated after the closing acts (common seat brief, item 17).

## Global Constraints

- **G1. No priced quote changes.** Same bundle, same inputs, same outputs (FR-239). The only observable
  change on an existing bundle is the **code** of an already-refused quote.
- **G2. A cell is never rewritten at the wire.** `to_wire` keeps `str(row[value_column])` (`:287`).
  Normalising there would turn a refused quote into a priced one on the same hash. The same reason
  refuses a check at `load_bundle`: one bad cell would refuse quotes that price today.
- **G3. Money and exactness.** Positional text comes from `Decimal`, never a float (`CLAUDE.md` §7).
- **G4. `pricing-core` stays importable standalone**: no new dependency. `rate_tables` already imports
  `pricing_core.rating.compile` (`operations.py:59`); the engine check belongs in `rating/`, and
  `rate_tables` does not import `zen` directly unless `uv run lint-imports` allows it.
- **G5. `model-schema` and the contracts do not change** (under DP-R2 (a) and DP-R4 (a)).
- **G6. Red first, by cause. No test is weakened** beyond A12.
- **G7. The message names no input value** (NFR-499), as `_raise_named`'s callers do.

## Needs

- **DB / Redis.** R1 to R5 need none: `packages/pricing-core/tests` run through
  `~/gi-pricing-plan.local/handover/run-small.sh`. `backend/tests/test_wf699_journey.py`,
  `test_score.py` and `test_score_compare.py` are in the gate's lane, not small runs (common seat
  brief, item 32). If a pre-gate DB run is wanted, it is a lead grant, single-tenant on a `createdb
  -T` copy, never the template, on Redis `-n 11`, `12` or `13`, ending with the two quoted zeros. db 0
  is live and is never touched.
- **Docker, NFR VM:** nothing.

## Tasks

### SL 8322 — the rating-core group

**The row.** After SL-1689 in the 09:58:58 order. WK-1178 fix slice. One `sonnet` executor (the
charter's model line governs).

- **Scope (what LG 8323 quotes):** R0 to R5 and G below.
- **Requirements:** `03` §3: FR-234, FR-255, FR-214 (read, guard only), FR-222, FR-239 (read, as a
  constraint), FR-261 (the property runner); NFR-489 (read: A8 is why no reading moves).
- **Register:** FD-1648, FD-1659, FD-1767, FD-1478, FD-1780, FD-1781, all closing at the merge (A14).
- **Depends on:** DP-R1 to DP-R4 ruled; the maintainer's GO; a gate slot.
- **Size:** 10 h (triage 9.75 h: FD-1767 falls by 2 h; the mechanism and the wider write fix add
  about that). SOLO gate about 2.5 h, not counted. **Split point:** R4 and R5 can ride alone; R1 to R3
  are one change.
- **Calendar:** merged before Thu 12 Nov 2026; still red at Wed 11 Nov 12:00 → the exception list.

**R0 — spec text first, and premises.**

1. Re-read every Evidence cite at the slice's base; a changed fact stops the slice.
2. Confirm DP-R1's last premise: `evaluation.decision` as `load_bundle` builds it (a real handler,
   the `test_rating_score_batch_outputs.py` GBM fixture) evaluates from inside `async def`. If it does
   not, the diagnosis uses `await async_evaluate` on the `score_one` path and `evaluate` on the batch
   path, and the LG records why.
3. Amend `docs/specs/03-rating-engine.md` under `spec-change`, dated, citing this plan by id:
   - **FR-234**, appended clause: every value is a decimal the rating engine's expression grammar
     parses. Every path that writes a value writes it positionally, without an exponent. A cell the
     grammar refuses is refused at compile with `RATE_TABLE_INCOMPLETE`, naming the table and the key.
   - **FR-255**, appended clause: a refused quote's code comes from what failed, not from what the
     failing step consumes. An `on_miss="error"` step that found no row is `RATE_TABLE_MISS` or
     `REFERENCE_LOOKUP_MISS` for that step, a step that consumes both included. A table whose cell the
     engine cannot parse, or any other failure, is `RATING_EVALUATION_FAILED`. Closes `RL-1313`
     DP-G4's stated limit (FD-1478).
   - The `RATING_EVALUATION_FAILED` note (`:1198`) gains the unparseable cell.
4. Commit alone (A2).

**R1 — writes are positional (FD-1648 (a)), red first.** `packages/pricing-core/tests/test_rate_table_operations.py`
and `test_rate_table_bulk_ops.py`, `req("FR-234")`:

- **T1** `test_a_small_fitted_relativity_is_written_positionally`: a level of `1.36e-7` through
  `extract_relativity_table`. **Red:** `'1.36E-7'`.
- **T2** `test_a_bulk_result_on_a_round_power_is_written_positionally`: an uplift taking 50 to 100.
  **Red:** `'1E+2'`.
- **T3** `test_an_edit_and_an_import_store_positional_text`, parametrised on `1.36E-7`, `1E+2`, `.5`.
  **Red:** the raw text comes back. Control, same test: `1.50` stays `1.50`.

**Green.** One helper in `operations.py`:

```python
def _positional(value: Decimal) -> str:
    """Plain digits, whatever the exponent: the engine's grammar has no upper-case `E` and no
    leading point (FD-1648). Identity on text already positional, trailing zeros included."""
    return format(value, "f")
```

`:166`: `_positional(Decimal(str(level.relativity)))`. `_format_value`:
`_positional(value.normalize())`. `apply_cell_edits` and `_checked_import`: the stored value is
`_positional(Decimal(raw))` after the row has passed `_value_issue`, so a refused row is untouched.

**R2 — compile refuses (FD-1648 (a)), red first.** `test_rating_compile*`' home by `git grep`, `req("FR-234")`.
**T4** `test_a_cell_the_engine_cannot_parse_does_not_compile`, the same three literals, plus the
control `1.36e-7`. **Red:** `compile_bundle` returns. **Green:** in `rating/runtime.py`, beside
`_rate_table_rows`:

```python
def unparseable_cells(payload: Mapping[str, Any] | None) -> list[str]:
    """The value cells the engine's grammar refuses: the engine's own parser, not a copy of its
    grammar (RUN at PL 8321: about 1 µs a cell)."""
```

using `zen.evaluate_expression(str(cell))`, `except RuntimeError`. In `compile.py`, a
`_refuse_unparseable_cells(version, payloads)` called beside `_refuse_control_factor_keys`, `_raise_named`
with the code DP-R2 rules. `load_bundle` is **not** changed (G2).

**R3 — the exact diagnosis (FD-1648 (b), FD-1659, FD-1478), red first.** Written for DP-R1 (b).
`test_rating_score.py`, `req("FR-255")`:

- **T5** `test_a_step_consuming_a_table_and_a_lookup_reports_the_one_that_missed`, parametrised
  both ways. **Red:** `RATE_TABLE_MISS` for the lookup miss.
- **T6** the residual test renamed `test_a_failure_in_a_step_consuming_a_table_is_not_a_miss`, its
  `match` now `^RATING_EVALUATION_FAILED:`. **Red:** `RATE_TABLE_MISS`.
- **T7** `test_an_unparseable_cell_is_not_reported_as_a_miss`, via `_hand_compiled` (compile would
  refuse it), a consumed table and an unconsumed one. **Red:** `RATE_TABLE_MISS` in both.
- **T8** `test_the_live_wire_is_byte_identical` (guard; the base's hash is pasted as a constant
  with its tree named in a comment, taken by the same function at the base).

**Green, `rating/runtime.py`:**

- `MISS_GUARD_PREFIX = "__miss_guard__"`. `_miss_guard_node(step_id, names)`: an `expressionNode`
  with one expression per name, value `f"{name} == null ? 1 * null : true"`, `passThrough` true.
- `to_wire(graph, payloads=None, *, miss_guards=None)`, where `miss_guards: Mapping[str, Sequence[str]]
  | None` maps a step id to its produced names. When `None`, the output is byte-identical (T8). When
  given, the path at `:555-566` adds a guard node and edge after each named step.
- `PurposeEvaluation` gains `diagnose: Callable[[Mapping[str, Any]], RuntimeError | None]`, a closure from
  `evaluation()` in `load_bundle` that, on first call, builds the guarded decision on the same
  `engine` from the inlined algorithm's `on_miss="error"` `table` and `lookup` steps, memoises it,
  evaluates the context, and returns the `RuntimeError` it raises, or `None`. Two workers' or two
  tasks' first calls may both build: harmless, last write wins. **`_failing_node` stays in
  `score.py`:** `test_error_sinks.py`'s `_SINKS` lists it by file and function, and that file is H's.

**Green, `rating/score.py`:** `_reraise_engine_failure(evaluation, context, exc)`:

- `diagnosed = evaluation.diagnose(context)`, `node = _failing_node(diagnosed) if diagnosed else None`.
  If it starts with `MISS_GUARD_PREFIX`, take the step.
  If that step is a `table` and `unparseable_cells` of its payload is non-empty:
  `RATING_EVALUATION_FAILED`, "table step … holds a cell the engine cannot parse". Otherwise
  `RATE_TABLE_MISS` or `REFERENCE_LOOKUP_MISS` by the step's type.
- Anything else, including `None` or the re-evaluation raising: `RATING_EVALUATION_FAILED`, the
  message keeping `_failing_node(exc)`'s step.
- `consumes_output_of` and the `tables` / `lookups` lists go. The docstring's "stated limit" paragraph
  goes; a new paragraph says why the live wire has no guards (DP-R1, G2).
- **`_check_lookup_misses`** (`:517`, called at `:964`): an absent `table` output whose payload has an
  unparseable cell raises `RATING_EVALUATION_FAILED`, same text. The bundle's payloads reach it from
  `build_scoring_result`, which holds `bundle`.
- The two callers (`:1039`, `:1220`) pass `evaluation` and `context`. The four direct test calls
  gain them (A12): a small stub with `diagnose=lambda _: None`.
- `test_wf699_journey.py:582-584`: the comment is corrected (the finding is closed); any assert that
  reads the code changes with it. It is DB-backed: the gate proves it.

**R4 — FD-1767's guard and FD-1780.**

- **T9**, `test_rating_score_batch_outputs.py`, `req("FR-214")`:
  `test_an_int_or_count_step_into_a_decimal_output_is_one_string_on_both_paths`, parametrised on the
  producer type, from `_probe_payload`, asserting `'18.00'` from `score_one` and in `outputs_json`.
  Green at base; quoted in the LG as a guard. Under DP-R3 (b) it is not written.
- **T10**, `test_rating_column_collision.py`, `req("FR-222")`, the three cases of A10. **Red:** the
  collision raises on two NaN. **Green,** `runtime.py`:

  ```python
  def _same_value(a: Any, b: Any) -> bool:
      """Equal, or both NaN: NaN is the one value unequal to itself (FD-1780)."""
      return bool(a == b or (a != a and b != b))
  ```

  and `:881`: `if column in row and not _same_value(row[column], value):`.

**R5 — FD-1781.** **T11**, `test_testing.py` (the file that already drives `make_scorer`, `:571`),
`req("FR-261")`: monkeypatch `pricing_core.rating.properties._score_context_sync` to raise
`TypeError("x")`. `make_scorer(...)(ctx)` is `None`; `property_holds` on a `PremiumPositive` is
`False`; `monotone_sweep`'s `broken_at` is not `None`. **Red:** the `TypeError` propagates.
**Green:** `properties.py:118`: `except (ValueError, RuntimeError, TypeError):`, and the docstring at
`:101-103` names it, citing the ruling.

**G — the gate.** The diff leaves `docs/`, so the full code gate, both halves, SOLO, after a re-merge
of `origin/main` and the GREEN set. Small runs always include `test_quote_input_raise_sites.py`
(item 11). No migration, no contract regeneration. `frontend.yml` fires only if the path filters
say so; `packages/pricing-core/**` modelling paths are named there, so the executor derives the CI
set from the three-dot diff. **No shared fixture changes.** Regression risk is high for a small diff:
`score.py` and `runtime.py` sit under every quote, which is what A8 is for.

### Write set

- `packages/pricing-core/src/pricing_core/rate_tables/operations.py`,
  `packages/pricing-core/src/pricing_core/rating/compile.py`, `rating/runtime.py`, `rating/score.py`,
  `rating/properties.py`.
- `packages/pricing-core/tests/`: `test_rate_table_operations.py`, `test_rate_table_bulk_ops.py`, the
  compile test home, `test_rating_score.py`, `test_rating_score_batch_outputs.py`,
  `test_rating_column_collision.py`, `test_testing.py`, `test_safe_error.py`.
- `backend/tests/test_wf699_journey.py` (the comment; A12).
- `docs/specs/03-rating-engine.md` (FR-234, FR-255, the note at `:1198`).
- LG 8323 under `docs/ledgers/`.
- At the mint: the SL 8322 row in `docs/roadmap.md`, `docs/INDEX.md`, this plan's `status:`, the six
  essays and `docs/findings/register.md` (A14).

### Files shared with other groups

`03-rating-engine.md`: C-small's FD-1384 spec text is `02`/`00` by its finding; to be confirmed in
that plan. `pricing-core/rating/*`: LAST-1 (FD-1337) reads shared money shapes. Sequence R before
FD-1337 (the brief's order does). **Safe in parallel with D, A, H, F, T.** R's `test_wf699_journey.py`
comment is one line.

## Hand-off (not this plan's writes)

- DP-R1 to DP-R4 and the GO: the maintainer. The ruling's "FD-1569" reading: the maintainer.
- The SL 8322 row and mint, the gate slot: the lead. The LG: the executor. A14: the slice's auditor.
- **For the lead, before the demo seed and SL-1913:** a stored Rate Table Version made by a bulk
  operation may already hold a `1E+2` cell. Its bundles scored as a refused quote for that key. After
  this merge a new compile over it is refused, naming the key, and a bundle already compiled keeps
  its behaviour (G2). None is known: T4 and the gate's demo stage are the first evidence, and any
  hit is a new version by edit, not a data patch.

## Self-review

1. **Every cite was read** at `dae9637e`; the items marked RUN were run there, read-only, and each says
   so. The one premise left is named at R0.2.
2. **Requirements by id**, no range. **Placeholders:** `unparseable_cells`' body and the compile
   test's home are stated by fact, not left open.
3. **Each finding has its own red by cause**, except FD-1767, which has none to have, and says so.
4. **The triage is corrected:** FD-1767 is fixed; the compile "check" FD-1648's essay relies on does
   not exist; `_format_value` is a second, wider write path; a parse failure and a miss are not
   separable from the error.
5. **The rulings are carried verbatim** and closed; nothing here reopens them. DP-R3 and DP-R4
   question only their application.
6. **Calendar:** `date -d 2026-11-12 +%A` is Thursday, and 11 Nov is Wednesday.
