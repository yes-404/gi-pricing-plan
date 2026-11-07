---
id: PL-8409
family: plan
kind: map
title: WK-1178 — OQ-2035 option D, a bulk rate-table operation computes its exact result and rounds it once, half-even, to the smaller of 28 significant digits and 28 decimal places, in a context it states, SL 8410 — a dated Work-plan delta
status: draft                   # draft → active → superseded | retired (§1.2a) — L1: draft→active rides the slice's PR
created: 2026-11-07             # draft under working id 8409
owner: planner
tree: a3db8fcec45b33a1a76ae642e72d203f24e9e99e   # origin/main 27d705552f89c4d3b4a39802acfe86068e4e1d1b
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-2040, FD-2028, FD-2032, OQ-2035, OQ-1784, FR-NEWID, FR-233, FR-234, FR-245, FR-275, FR-226, FR-229, FR-23, FR-273]
---

# PL 8409 — WK-1178: OQ-2035 option D. A bulk operation rounds its exact result once, in a context it states (SL 8410, a dated Work-plan delta)

> **For agentic workers:** a **dated Work-plan delta** under Lean P2 L1 (a'). It `relates:` `PL-2040`
> (the sibling delta that refused a bulk operation by value type, FD-2032) and edits no earlier plan. It
> carries the spec change, already written on this branch, and one code slice row, SL 8410, whose ledger
> is LG 8411. **It decides nothing.** Three decision points each carry a recommendation; the maintainer
> rules them. The executor's skills are `superpowers:test-driven-development`,
> `.claude/skills/python-test` and `.claude/skills/python-package`. PL 8409, SL 8410 and LG 8411 are
> working ids reserved by the lead; `FR-NEWID` is the requirement this branch appends to `03` §3.3.

## Authority

- **The decision.** `to-lead.md` "2026-11-07 23:22:37 GMT", the maintainer (by delegation) under the
  user's delegation "2026-11-07 17:30:49 GMT" item (1): OQ-2035 / FD-2028 = **option D**. Its words: *"a bulk
  operation's result is computed independently of the ambient decimal context, exactly or to a stated
  working precision for a division, rounded once half-even to the smaller of 28 significant digits and 28
  decimal places, trailing zeros dropped; floor_and_cap does no arithmetic."*
- **The sub-question.** The same entry: *"a money_minor uplift HOLDS THE FRACTION, (a)"*, against the
  draft's (b). The FR-23 / FR-273 wording goes to the `CLAUDE.md` §14 review as a Phase 3 spec proposal.
- **The consequence.** The same entry: *"the proposed requirement is minted as a new FR in 03 §3 …, and the
  code is ONE slice under WK-1178 (operations.py's arithmetic context + the rebase refusal removed + tests
  red-first; R2's 308 bound untouched): plan Sun 8, build Mon 9, gate Tue 10, merged inside Thu 12. If its
  gate cannot start by Tue 10 20:00 it is NOT started: D stands as the spec's rule with the code carried to
  P3 by name; the freeze wins."*
- **The input.** DM draft `~/gi-pricing-plan.local/scratch/dm-fd8383/oq-draft.md`, sha256 prefix
  `99d83663edf8` (the prefix the entry names, re-read 2026-11-07), Part 0 and Part 1, and its scripts
  `measure_rule.py`, `measure_engine.py` and their `.out` files.
- **This seat.** Brief `~/gi-pricing-plan.local/handover/brief-plan-oq2035-2026-11-07.md`, sha256 prefix
  `a3b92d33853c`: the spec change and this plan, one draft branch, no code.

## Goal

The three bulk operations that compute (`uplift_table`, `uplift_by_filter`, `rebase_to_level`) store the
same text for the same table and parameters in any caller, and that text is the exact result rounded once,
half-even, to the smaller of 28 significant digits and 28 decimal places. A non-terminating quotient below
0.1 is stored, not refused. No payable moves, `_format_value`'s 308 bound is unchanged, and a `money_minor`
uplift keeps its fraction.

## Evidence at `27d70555` (tree `a3db8fce`), read-only

**The arithmetic sites** (`packages/pricing-core/src/pricing_core/rate_tables/operations.py`):

| Op | Line | Arithmetic today | Context |
|---|---|---|---|
| `uplift_table` | `:796-797` | `factor = Decimal(1) + percentage`, then `lambda old: old * factor` in `_transform_rows` | ambient, both lines |
| `uplift_by_filter` | `:819`, `:826` | the same, inline | ambient, both lines |
| `floor_and_cap` | `:866-867` | `max(floor, min(old, cap))` | no arithmetic |
| `rebase_to_level` | `:909` | `Decimal(row[value_name]) / reference` | ambient |

- **No context is stated on this path.** `git grep -n -E 'getcontext|setcontext|localcontext' 27d70555 --
  packages/pricing-core/src/pricing_core/rate_tables/` prints nothing. The only `Context(...)` in the file
  is `_format_value`'s (`:722`), sized to the value's own digits so it cannot round.
- **`_format_value` (`:694-723`) is R2's.** It refuses an adjusted exponent beyond
  `MAX_POSITIONAL_EXPONENT` (`model_schema/money.py:132`, `308`) with `RATE_TABLE_CELL_UNPARSEABLE` before
  any text exists, then writes fixed point with trailing zeros dropped. **This plan does not touch it.**
- **The refusal is `_validate_result` (`:589-599`) → `validate_rate_table` → `_value_issue` → `cell_parses`
  (`:333`).** A rebase quotient below 0.1 that does not terminate has 28 significant digits and so 29
  decimal places, and `cell_parses` refuses it: `measure_rule.out` section (1), cells `0.05, 1, 1.5` on
  base `25-29` → `REFUSED RATE_TABLE_CELL_UNPARSEABLE: value '0.03333333333333333333333333333'`.
- **SL-2041 is already on `main`** (`_check_value_type`, `:766-772`; FR-233's 2026-11-05 amendment):
  `rebase_to_level` runs only on a `relativity` column, and `uplift_table` / `uplift_by_filter` on every
  type but `count`. So a `money_minor` uplift is allowed and stores a fraction today; option (a) keeps it.
- **The parameters reach the operation bounded through the API only.** `percentage` is `DecimalStr`
  (`model_schema/rating.py:1390`), which validates any exponent; the API writes the parameter before the
  platform call, so a `percentage` past 308 is a `422 DECIMAL_OUT_OF_RANGE`
  (`backend/tests/test_api_rate_tables.py:863-892`). A pure caller can pass any exponent, and
  `test_rate_table_bulk_ops.py:188-197` pins `uplift_table(…, percentage=Decimal("1E+999990"))` →
  `RATE_TABLE_CELL_UNPARSEABLE`, under 300 characters.

**The planner's spike** (`~/gi-pricing-plan.local/scratch/plan-oq2035/spike_ctx.py`, DB-free, Python 3
stdlib only, run 2026-11-07 beside gate-1's pytest with `pgrep -af '[d]emo.py|[v]itest'` empty and load1
2.59). It tests one stated context, `Context(prec=28, rounding=ROUND_HALF_EVEN, Emin=-1, Emax=999999,
traps=[InvalidOperation, DivisionByZero, Overflow])`, with uplift as `old.fma(percentage, old,
context=ctx)` and rebase as `ctx.divide(old, reference)`. `Emin = -1` sets `Etiny = Emin - prec + 1 = -28`,
so a result below 0.1 is subnormal and is rounded to 28 decimal places in the same single rounding.

```text
N 20000 mismatches vs exact-rational oracle 0
0.05 / 1.5 -> 0.0333333333333333333333333333
0.1 / 1.5 -> 0.0666666666666666666666666667
0.14 / 1.5 -> 0.0933333333333333333333333333
ambient 400 ROUND_HALF_EVEN 0.01276125 0.0333333333333333333333333333
ambient 10 ROUND_DOWN 0.01276125 0.0333333333333333333333333333
ambient 28 ROUND_HALF_EVEN 0.01276125 0.0333333333333333333333333333
huge pct 1.840000000000000000000000000E+999990 0.000006s
tiny pct 1.840000000000000000000000000 True 0.000005s
30-dp percentage: accepted-today cells whose bytes differ under D: 606 (Decimal('1.994'), Decimal('2.240172837290617283729061729'), Decimal('2.240172837290617283729061728'))
250k fma with fresh ctx 0.732s
250k today 0.251s
```

- **The oracle** is exact rational arithmetic (`fractions.Fraction`) rounded half-even with integers, so a
  match is single rounding, not agreement between two roundings. The generator is the seat's, so 0 is not
  a rate of anything; percentages up to 32 decimal places were included.
- **"Today's bytes" holds except for a long percentage.** Today rounds `1 + percentage` to 28 digits and
  then the product: two roundings. D rounds once. For a percentage whose `1 + percentage` has more than 28
  significant digits the result can differ in its 28th significant digit: 606 of 1,999 cells for one
  30-dp percentage. No payable moves. The DM draft's 20,000 pairs used factors of at most 6 decimal places,
  so they could not see this. `FR-NEWID` (6) states it, and DP-2 puts it to the maintainer.
- **Cost:** about 2.9 µs per cell against 1.0 µs today, a fresh context per call included; 0.73 s for a
  250,000-cell table (FR-232's rows threshold). No NFR budgets a bulk operation (`03` §9 read); NFR-498
  (audit) is unaffected.

### The chain's collisions (Gate form below)

Heads read 2026-11-07: `origin/sl-8370-permission-pin` `9c9cbdc4`, `origin/sl-8381-report-response`
`7ef66d7b`, `origin/sl-8406-sweep-owner-dsn` `c7cad487`. Each side's list is `git diff --name-only
origin/main...<branch>`.

## Decision points

No DP is the planner's to rule. Each states a recommendation; **DP-1 and DP-2 block R2**.

- **DP-1 (blocking): how the one rounding is computed.** (a) **One stated context with a subnormal floor**
  (`prec 28`, half-even, `Emin -1`): uplift is `old.fma(percentage, old, context)`, rebase is
  `context.divide(old, reference)`. Python's `decimal` rounds each operation once from its exact result, so
  there is no working precision to state. (b) **The DM draft's rule**: a 200-digit product or a 120-digit
  quotient, then `quantize` to the target exponent. That is two roundings for a division, which the draft
  itself left unproved (oq-draft.md `:220`), and a huge `percentage` makes the 200-digit product's factor
  inexact. (c) **Exact rationals** (`Fraction`) rounded with integers. Single rounding by construction, but
  slower, and an exponent past about 4,300 digits trips CPython's integer-to-string limit.
  **Recommendation (a).** It is the entry's "rounded once" for every operation, division included, without a
  second precision; it is about 15 lines; and the huge-percentage cases stay cheap (6 µs) and refused where
  they are today. Under (a), FR-NEWID (1) says "no intermediate is rounded", which is stronger than the
  entry's "or to a stated working precision for a division" and is what the entry's "rounded once" needs.
- **DP-2 (blocking): the long-percentage exception to "today's bytes".** (a) **Round once**, and state the
  exception in FR-NEWID (6): a percentage whose `1 + percentage` has more than 28 significant digits gives a
  result that can differ from today's in its 28th significant digit. (b) **Round the factor first, as
  today**, so every accepted-today result keeps its bytes. **Recommendation (a).** (b) is two roundings,
  which is the defect D removes, and it keeps a stored result that is not the exact result rounded. The
  difference is about 1e-27 relative and moves no payable. The entry's reason "it writes today's bytes
  wherever today succeeds" is true under (a) for every percentage of at most 27 decimal places on a
  1-digit integer part, which is every seeded and demo case; it is the maintainer's to note that the
  reason has this one exception.
- **DP-3: what "keeps its stored text" compares.** (a) **The rounded result** equals the current value
  (today's `_transform_rows`, `:734-736`, and `uplift_by_filter`, `:827`). (b) The exact result equals the
  current value (the DM draft's proposed wording, oq-draft.md `:118`). **Recommendation (a).** Under (b) a
  cell such as `1.8400` uplifted by `1E-40` would be re-written as `1.84` and counted as changed although
  its value did not move; (a) is today's behaviour and keeps today's bytes. FR-NEWID (4) is written as
  (a).

## Acceptance Standard

Each item is checked by a command a fresh reviewer can run. Items 1 to 5 apply to this branch (the spec
change and the plan); A1 to A11 to SL 8410.

1. **The docs checks pass on this branch.** `python3 scripts/audit-docs.py` prints no failing line except
   those for the working ids this branch uses (PL 8409, SL 8410, LG 8411, the new FR's), and
   `python3 scripts/doc-index.py --check` exits 0. After the mint both exit 0.
2. **No requirement range.** `grep -nE '(N?FR)-[0-9]+ *(-|to|–) *(N?FR-)?[0-9]+' <this file>` prints no
   line that stands for a set of ids.
3. **One new requirement, after FR-233.** `grep -c '^| \*\*FR-NEWID\*\* |' docs/specs/03-rating-engine.md`
   prints `1`, and `grep -n -A1 '^| \*\*FR-233\*\* |' docs/specs/03-rating-engine.md` shows it on the next
   line.
4. **OQ-2035 is decided in both places, the same way.** `grep -c '^| ~~\*\*OQ-2035\*\*~~ ✔ | \*\*DECIDED
   2026-11-07: option D' docs/open-questions.md docs/specs/03-rating-engine.md` prints `1` for each file,
   and each row cites `2026-11-07 23:22:37 GMT` and `FR-NEWID`.
5. **FR-23 and FR-273 are not changed.** `git diff origin/main...HEAD -- docs/specs/00-overview.md` prints
   nothing, and `git diff -U0 origin/main...HEAD -- docs/specs/03-rating-engine.md | grep -c '^[-+]|
   \*\*FR-273\*\*'` prints `0`.

SL 8410:

- **A1. The write set** is the Write set below, by `git diff --name-only origin/main...HEAD`, quoted.
- **A2. Red first, by cause, in LG 8411 before the green.** R1's four new tests run at the slice's base and
  fail for these causes, each failure quoted: T-rebase raises `RATE_TABLE_CELL_UNPARSEABLE`; T-ambient
  raises `RATE_TABLE_CELL_UNPARSEABLE` on `'3.37037036703703703670370370367'` under `prec=400`, a text
  the default context rounds and stores; T-long-percentage stores
  `2.240172837290617283729061729`, not `…728`; T-oracle reports a non-zero mismatch count. An import error,
  a fixture error or a `NameError` is not the red.
- **A3. The pin is green before and after.** T-money-minor (`12345` uplifted by `0.0375` stores
  `12807.9375`) passes at the base and at the head: option (a) is today's behaviour, and the test keeps it.
- **A4. Green.** `run-small.sh <wt> packages/pricing-core/tests/test_rate_table_bulk_ops.py
  packages/pricing-core/tests/test_rate_table_operations.py
  packages/pricing-core/tests/test_rate_table_weights.py` passes, the summary line and rc quoted whole.
- **A5. No ambient context, and the old arithmetic is gone.** `git grep -n -E
  'getcontext|setcontext|localcontext' -- packages/pricing-core/src/pricing_core/rate_tables/` prints
  nothing, and `grep -n -E 'Decimal\(1\) \+ percentage|old \* factor|\]\) / reference'
  packages/pricing-core/src/pricing_core/rate_tables/operations.py` prints nothing.
- **A6. R2's 308 bound is untouched.** `git diff origin/main...HEAD -- packages/model-schema` prints
  nothing; `git diff -U0 origin/main...HEAD -- packages/pricing-core/src/pricing_core/rate_tables/operations.py
  | grep -c -E '^[-+].*(MAX_POSITIONAL_EXPONENT|def _format_value)'` prints `0`; and
  `TestFormatValueIsBoundedBeforeItIsBuilt` passes inside A4.
- **A7. The requirement is evidenced.** `uv run python scripts/req-coverage.py` lists `FR-NEWID` with the
  new tests in `test_rate_table_bulk_ops.py` as its evidence (`@pytest.mark.req("FR-NEWID")`).
- **A8. GREEN by import closure (common seat brief, item 29),** the commands and the list quoted in LG 8411:
  changed modules `git diff --name-only origin/main...HEAD -- packages/*/src backend/src`; the closure
  read at `27d70555` is `operations.py` → `app/platform/rate_tables.py` → `app/api/rate_tables.py`,
  `app/platform/rating_versions.py`, `app/worker/rate_table_handlers.py`. Its DB-free test files are A4's
  three; the DB-backed ones (26 files at `27d70555` by the grep under Gate form, including
  `test_api_rate_tables.py`) run in the gate.
- **A9. The API's two bound tests pass in the gate,** by name:
  `test_bulk_operation_with_a_huge_percentage_is_a_coded_422_not_a_memory_fault` and
  `test_bulk_operation_whose_computed_cell_passes_the_bound_is_a_cell_422`
  (`backend/tests/test_api_rate_tables.py:863`, `:896`).
- **A10. The gate.** One full code gate, both halves, on the re-merged head, every rc quoted (`CLAUDE.md`
  §11), **started no later than Tue 10 Nov 2026 20:00 GMT**. If it cannot start by then it is not started:
  LG 8411 records "not started; FR-NEWID stands as the rule; the code is carried to Phase 3 by name", and the
  P2 closure record carries SL 8410 by name (the 23:22:37 entry).
- **A11. Nothing beyond the operations.** `git diff --name-only origin/main...HEAD` lists no file under
  `docs/contracts/`, `frontend/`, `backend/src/` or `packages/model-schema/`, so no contract is regenerated
  and no API behaviour changes except a rebase that was refused and now stores.

## Global Constraints

- **G1. Money and rates are never float** (`CLAUDE.md` §7; FR-245): `decimal` only; no `float()` on a cell
  or a parameter.
- **G2. `pricing-core` stays standalone** (`CLAUDE.md` §2): the change uses the standard library's
  `decimal` only; no new dependency, so `skills-map.md` does not change.
- **G3. `_format_value` and `MAX_POSITIONAL_EXPONENT` are not edited** (R2's 308 bound, the entry).
- **G4. A `money_minor` result is not rounded to whole minor units** (the entry's (a)).
- **G5. No schema field and no contract change**: a declared per-table dp is option A, open with
  `OQ-1784`.
- **G6. A failing test is never weakened or removed** (common seat brief, item 13). An existing test whose
  expected text moves only by DP-2's 28th-digit case is reported verbatim and STOPs for the lead; none is
  known at `27d70555` (`git grep -n -E '0\.[0-9]{29,}|[0-9]{30,}' -- packages/pricing-core/tests/test_rate_table_bulk_ops.py
  packages/pricing-core/tests/test_rate_table_operations.py` read for long percentages: none).
- **G7. Line numbers are `27d70555`'s** and are re-derived at the slice's base.
- **G8. Requirement and section ids are permanent** (`CLAUDE.md` §5); no range of ids in any file this plan
  writes.

## Needs

- **Seats:** one executor (model per `executor.md`) and one auditor. No decision-maker once the DPs are
  ruled.
- **Ids:** PL 8409, SL 8410, LG 8411 (reserved) and the new FR's (on this branch). No other id is foreseen.
- **DB:** none for R1 and R2: `operations.py` and its three test files are pure, run through `run-small.sh`
  (no `createdb`, no migration; common seat brief, item 32). The full gate brings its own DB as every gate
  does; no window of the slice's own.
- **Redis:** none outside the gate. **Docker:** only the stack already up from `tools-main`; no compose
  build, no restart. **MinIO:** none. **NFR VM:** none.
- **Gate cost:** one full code gate, about 2.5 h of wall time (PL-2059's, PL-2053's and PL 8405's estimate
  for a full gate; not measured for this slice). No migration, no contract change, no frontend path:
  `frontend.yml` does not fire (its filters are `frontend/**`, `docs/contracts/openapi/**` and
  `packages/pricing-core/src/pricing_core/modelling/**`); `python.yml` fires on `packages/**`. No timed path
  changes: a bulk operation is not inside an NFR measurement.
- **Hours, gate not counted, an estimate:** R1 1 h, R2 0.75 h, LG 8411 and records 1 h, so **about 2.75 h**,
  plus about 1 h of audit.
- **Calendar** (the entry; weekdays read from `date -d … +%A`): plan Sun 8 Nov, build Mon 9 Nov, gate Tue
  10 Nov, **not started if its gate cannot start by Tue 10 Nov 20:00 GMT**, merged inside Thu 12 Nov (the
  code freeze).

## Gate form: by FILE, against the chain's open branches

The slice's code paths: `packages/pricing-core/src/pricing_core/rate_tables/operations.py` and
`packages/pricing-core/tests/test_rate_table_bulk_ops.py`.

- **Code ∩ sl-8370, sl-8381, sl-8406: empty.** The command, per branch: `comm -12 <(printf '%s\n'
  packages/pricing-core/src/pricing_core/rate_tables/operations.py
  packages/pricing-core/tests/test_rate_table_bulk_ops.py | sort) <(git diff --name-only
  origin/main...origin/<branch> | sort)`. Their code lists at the heads above: sl-8370 `backend/src/app/api/models.py`,
  `backend/src/app/platform/modelling.py` and two backend tests; sl-8381 the validation report
  (`backend/src/app/{api,platform}/validation.py`, `packages/model-schema/src/model_schema/{__init__,validation}.py`,
  `scripts/audit-docs.py`, `scripts/generate-contracts.py`, `frontend/src/api/validation.ts` and tests);
  sl-8406 `scripts/measure-p2-nfr-sweep.py` and two tests.
- **Records ∩:** `docs/INDEX.md` with all three (regenerated, common seat brief item 5); `docs/specs/03-rating-engine.md`
  with sl-8381, whose hunks are fence lines in §4 (`:250`, `:374`, `:502`, … `:1021` at its base `e12dc849`),
  none in §3.3 or §10, where this branch writes; `docs/open-questions.md` with none.
- **Partition paths:** none in this slice: no `backend/migrations/`, `deploy/`, `conftest*`, `.github/`,
  `pyproject.toml`, `uv.lock` or `frontend/`.
- **Imports read (item 29), both ways.** Into the slice: `operations.py` imports `model_schema.modelling`,
  `model_schema.money`, `model_schema.rating`, `model_schema.refs` and `pricing_core.rating.compile`
  (`:31-60`), so every import runs `model_schema/__init__.py`, **which sl-8381 changes** (its exports). That is
  one-way and import-time only: nothing sl-8381 changes is read by the operations. Out of the slice: the
  closure in A8 reaches no file any of the three branches changes; sl-8370's `platform/modelling.py` is not
  imported by `platform/rate_tables.py` (its `from app.platform import` lines, `:39-41`, name `audit`,
  `datasets`, `transformations`, `jobs` and `settings`).
- **Verdict: pairable with any of the three** (no shared code file, no partition path). The one consequence
  is item 21: if sl-8381 merges before SL 8410's gate, SL 8410 re-merges `main` and re-runs A4's three files
  at the re-merged head before its PR. The maintainer gives the word for single or paired.

## Tasks

### SL 8410: the row. Scope: A1 to A11; `03` FR-NEWID (new), FR-233, FR-234 (the refusal it keeps), FR-245, FR-275, FR-226; lane WK-1178; after this plan's acceptance, gate by Tue 10 Nov 20:00 GMT

**Files:**
- Modify: `packages/pricing-core/src/pricing_core/rate_tables/operations.py` (`:21` the import; a new
  `_result_context` after `_format_value`, `:694-723`; `uplift_table` `:786-809`; `uplift_by_filter`
  `:812-848`; `rebase_to_level` `:880-924`)
- Test: `packages/pricing-core/tests/test_rate_table_bulk_ops.py` (a new class at the end of the file)
- Ledger: LG 8411 under `docs/ledgers/`

**Interfaces:**
- Consumes: `uplift_table(table, *, percentage)`, `uplift_by_filter(table, *, percentage, filter)`,
  `rebase_to_level(table, *, base_level)`, unchanged signatures; the test helpers `_version`, `_value`,
  `_cells`, `_key` and `_CODE` already in the test file (`:54-104`, `:201`).
- Produces: `_result_context() -> decimal.Context`, private to `operations.py`. No public name changes.

#### R0: base and set-up

- [ ] **Step 1:** Worktree from `origin/main` per the brief; `uv sync --directory <wt> --all-packages --frozen`.
  Quote `git -C <wt> rev-parse HEAD`.
- [ ] **Step 2:** Re-derive this plan's line numbers at the base:
  `grep -n -E 'Decimal\(1\) \+ percentage|old \* factor|\]\) / reference|def _format_value' packages/pricing-core/src/pricing_core/rate_tables/operations.py`.
  A changed site is reported before any edit.

#### R1: the red tests, first

- [ ] **Step 1: Write the failing tests.** Append to `packages/pricing-core/tests/test_rate_table_bulk_ops.py`
  (add `ROUND_DOWN, ROUND_HALF_EVEN, localcontext` to the `decimal` import and `from fractions import
  Fraction`):

```python
def _round_once(exact: Fraction) -> Decimal:
    """FR-NEWID's rule computed independently: exact rational, rounded half-even with integers
    to the smaller of 28 significant digits and 28 decimal places."""
    if exact == 0:
        return Decimal(0)
    magnitude = abs(exact)
    adjusted = len(str(magnitude.numerator)) - len(str(magnitude.denominator))
    if magnitude < Fraction(10) ** adjusted:
        adjusted -= 1
    exponent = max(-28, adjusted - 27)
    scaled = magnitude / Fraction(10) ** exponent
    quotient, remainder = divmod(scaled.numerator, scaled.denominator)
    if 2 * remainder > scaled.denominator or (
        2 * remainder == scaled.denominator and quotient % 2
    ):
        quotient += 1
    sign = 1 if exact < 0 else 0
    return Decimal((sign, tuple(int(d) for d in str(quotient)), exponent))


def _one_cell(value: str) -> RateTableVersion:
    return _version(
        rows=[{"driver_age_band": "17-20", "relativity": value}],
        value=_value(min=None, max=None),
    )


class TestABulkOperationRoundsOnceInAStatedContext:
    """FR-NEWID (OQ-2035 option D, to-lead "2026-11-07 23:22:37 GMT"): the exact result, rounded
    once, half-even, to the smaller of 28 significant digits and 28 decimal places, in a context
    the operation states and never the caller's."""

    @pytest.mark.req("FR-NEWID")
    def test_a_rebase_below_one_tenth_is_stored_not_refused(self) -> None:
        rows = [
            {"driver_age_band": "17-20", "relativity": "0.05"},
            {"driver_age_band": "21-24", "relativity": "1"},
            {"driver_age_band": "25-29", "relativity": "1.5"},
        ]
        result = rebase_to_level(
            _version(rows=rows, value=_value(min=None, max=None)),
            base_level={"driver_age_band": ["25-29"]},
        )
        assert _cells(result) == [
            {"driver_age_band": "17-20", "relativity": "0.0333333333333333333333333333"},
            {"driver_age_band": "21-24", "relativity": "0.6666666666666666666666666667"},
            {"driver_age_band": "25-29", "relativity": "1"},
        ]

    @pytest.mark.req("FR-NEWID")
    def test_the_stored_text_does_not_depend_on_the_callers_context(self) -> None:
        percentage = Decimal("0.123456789012345678901234567890")
        expected = [{"driver_age_band": "17-20", "relativity": "3.370370367037037036703703704"}]
        for prec, rounding in ((28, ROUND_HALF_EVEN), (400, ROUND_HALF_EVEN), (10, ROUND_DOWN)):
            with localcontext() as ambient:
                ambient.prec = prec
                ambient.rounding = rounding
                assert _cells(uplift_table(_one_cell("3"), percentage=percentage)) == expected
                assert _cells(
                    uplift_by_filter(
                        _one_cell("3"),
                        percentage=percentage,
                        filter={"driver_age_band": ["17-20"]},
                    )
                ) == expected
        for prec, rounding in ((28, ROUND_HALF_EVEN), (400, ROUND_HALF_EVEN), (10, ROUND_DOWN)):
            with localcontext() as ambient:
                ambient.prec = prec
                ambient.rounding = rounding
                rebased = rebase_to_level(
                    _version(
                        rows=[
                            {"driver_age_band": "17-20", "relativity": "0.1"},
                            {"driver_age_band": "21-24", "relativity": "3"},
                        ],
                        value=_value(min=None, max=None),
                    ),
                    base_level={"driver_age_band": ["21-24"]},
                )
                assert _cells(rebased)[0]["relativity"] == "0.0333333333333333333333333333"

    @pytest.mark.req("FR-NEWID")
    def test_the_factor_is_not_rounded_before_the_product(self) -> None:
        """DP-2 (a): one rounding. Today rounds 1 + percentage to 28 digits first and stores
        2.240172837290617283729061729."""
        result = uplift_table(
            _one_cell("1.994"), percentage=Decimal("0.123456789012345678901234567890")
        )
        assert _cells(result)[0]["relativity"] == "2.240172837290617283729061728"

    @pytest.mark.req("FR-NEWID")
    def test_every_result_is_the_exact_result_rounded_once(self) -> None:
        rng = random.Random(2035)
        mismatches = []
        for _ in range(2000):
            digits = rng.randint(1, 20)
            old = Decimal(rng.randint(1, 10**digits - 1)).scaleb(-rng.randint(digits, digits + 8))
            if rng.random() < 0.5:
                percentage = Decimal(rng.randint(0, 10**30)).scaleb(-rng.randint(2, 32))
                got = _cells(uplift_table(_one_cell(format(old, "f")), percentage=percentage))
                want = _round_once(Fraction(old) * (1 + Fraction(percentage)))
            else:
                reference = Decimal(rng.randint(1, 10**6)).scaleb(-rng.randint(0, 6))
                table = _version(
                    rows=[
                        {"driver_age_band": "17-20", "relativity": format(old, "f")},
                        {"driver_age_band": "21-24", "relativity": format(reference, "f")},
                    ],
                    value=_value(min=None, max=None),
                )
                got = _cells(rebase_to_level(table, base_level={"driver_age_band": ["21-24"]}))
                want = _round_once(Fraction(old) / Fraction(reference))
            if Decimal(got[0]["relativity"]) != want:
                mismatches.append((old, got[0]["relativity"], want))
        assert mismatches == []

    @pytest.mark.req("FR-NEWID")
    def test_a_money_minor_uplift_holds_the_fraction(self) -> None:
        """The entry's (a): no rounding to whole minor units at the operation."""
        table = _version(
            rows=[{"driver_age_band": "17-20", "relativity": "12345"}],
            value=RateTableValue(
                name="relativity",
                type=RateTableValueType.MONEY_MINOR,
                unit="pence",
                min=None,
                max=None,
            ),
        )
        result = uplift_table(table, percentage=Decimal("0.0375"))
        assert _cells(result)[0]["relativity"] == "12807.9375"
```

- [ ] **Step 2: Run the red at the base.** Before the run, `pgrep -af '[d]emo.py|[v]itest'` prints nothing
  and load1 < 6. Run: `run-small.sh <wt> packages/pricing-core/tests/test_rate_table_bulk_ops.py`. Expected,
  each quoted in LG 8411 (A2): `test_a_rebase_below_one_tenth_is_stored_not_refused` FAILS with
  `ValueError: RATE_TABLE_CELL_UNPARSEABLE: value '0.03333333333333333333333333333'`;
  `test_the_stored_text_does_not_depend_on_the_callers_context` FAILS at `prec=400` with
  `RATE_TABLE_CELL_UNPARSEABLE: value '3.37037036703703703670370370367'` (the default context stored
  `3.370370367037037036703703704` one iteration earlier); `test_the_factor_is_not_rounded_before_the_product` FAILS with `…729` !=
  `…728`; `test_every_result_is_the_exact_result_rounded_once` FAILS with a non-empty `mismatches` (or the
  refusal it raises on a rebase below 0.1). `test_a_money_minor_uplift_holds_the_fraction` PASSES (A3). Every
  other test in the file PASSES.
- [ ] **Step 3: Commit** the tests alone: `test(pricing-core): FR-NEWID red — a bulk operation rounds once in
  a stated context (SL 8410)`.

#### R2: the stated context

- [ ] **Step 1: Write the implementation.** In `operations.py`, the `decimal` import (`:21`) becomes:

```python
from decimal import (
    ROUND_HALF_EVEN,
    Context,
    Decimal,
    DivisionByZero,
    Inexact,
    InvalidOperation,
    Overflow,
)
```

  After `_format_value`, add:

```python
#: FR-NEWID (OQ-2035 option D): a bulk operation's result is rounded once, half-even, to the
#: smaller of 28 significant digits (FR-245) and 28 decimal places (FR-275's scale limit).
_RESULT_DIGITS = 28
_RESULT_PLACES = 28


def _result_context() -> Context:
    """FR-NEWID: the one context a bulk operation computes in, never the caller's.

    `decimal` rounds each operation once from its exact result, so `fma` (uplift) and `divide`
    (rebase) need no working precision. `Emin` puts `Etiny` (`Emin - prec + 1`) at -28, so a result
    below 0.1 is subnormal and lands on 28 decimal places in that same rounding. The traps are
    the default context's, so what raised under it still raises. A fresh context per call keeps
    its flags the call's own.
    """
    return Context(
        prec=_RESULT_DIGITS,
        rounding=ROUND_HALF_EVEN,
        Emin=_RESULT_DIGITS - _RESULT_PLACES - 1,
        Emax=999999,
        capitals=1,
        clamp=0,
        flags=[],
        traps=[InvalidOperation, DivisionByZero, Overflow],
    )
```

  `uplift_table`: replace `:796-797` with

```python
    context = _result_context()
    new_rows, changed = _transform_rows(
        rows, table.value.name, lambda old: old.fma(percentage, old, context=context)
    )
```

  `uplift_by_filter`: replace `factor = Decimal(1) + percentage` (`:819`) with
  `context = _result_context()`, and `new = old * factor` (`:826`) with
  `new = old.fma(percentage, old, context=context)`.

  `rebase_to_level`: before the loop add `context = _result_context()`, and replace `:909` with
  `quotient = context.divide(Decimal(row[value_name]), reference)`.

  Each of the three docstrings gains one line: "The result is rounded once, in `_result_context`
  (FR-NEWID)." `_format_value` is not edited (G3).
- [ ] **Step 2: Run green.** The STOP rule first. Run A4's three files through `run-small.sh`. Expected: all
  pass, including `TestFormatValueIsBoundedBeforeItIsBuilt` and the five new tests. Quote the summary line
  and rc whole.
- [ ] **Step 3: Static checks on the changed files.** `uv run --directory <wt> ruff check .`;
  `uv run --directory <wt> ruff format --check <the two files>`; `uv run --directory <wt> mypy`;
  `uv run --directory <wt> lint-imports`. Every rc quoted.
- [ ] **Step 4: A5 and A6's greps,** output quoted in LG 8411.
- [ ] **Step 5: Commit** `fix(pricing-core): FR-NEWID — a bulk operation rounds its exact result once, in a
  stated context (SL 8410, OQ-2035 D)`.

#### G: the gate

- [ ] **Step 1:** Re-merge `origin/main` (a merge, never a rebase; common seat brief item 5). If sl-8381 or any
  code merged since the base, run A4's three files at the re-merged head first (item 21).
- [ ] **Step 2:** One full code gate on the lead's word (single or paired, Gate form), **started by Tue 10 Nov
  2026 20:00 GMT** or not started (A10). Every rc quoted; A9's two tests named in the pytest output.
- [ ] **Step 3:** LG 8411 carries R1's red, R2's green, the GREEN derivation (A8) and the gate's rc table
  before the audit.

### Write set

`packages/pricing-core/src/pricing_core/rate_tables/operations.py`;
`packages/pricing-core/tests/test_rate_table_bulk_ops.py`; LG 8411; `docs/roadmap.md` (SL 8410's row, one
line, at the mint); this plan (`status:` only); `docs/INDEX.md`. The spec change (FR-NEWID and the two OQ-2035
rows) is already on this plan's branch and merges with it or before the slice.

### Files shared

Code: none with sl-8370, sl-8381 or sl-8406 (Gate form). Records: `docs/INDEX.md` with all three, and
`docs/specs/03-rating-engine.md` with sl-8381 (different sections), by re-merge.

## Hand-off (not this plan's writes)

- **The maintainer:** DP-1 to DP-3; this plan's acceptance; the slice GO; the gate's word (single or paired).
- **The `CLAUDE.md` §14 review (P3 spec proposal, the entry's words):** does `00` FR-23's `_minor` suffix
  promise integrality in a rate cell, and should FR-273's list ("relativities, loadings, factors") name a
  money cell? FR-NEWID (5) points there and changes neither. **D is carried into the §14 high re-read as a
  decision, not a proposal** (the entry).
- **The lead, or the next docs batch:** `docs/roadmap.md` §10's gate row for OQ-2035 (`:4453` at `27d70555`):
  strike the id and recount the row (spec-change: a decided question keeps its gate row); SL 8410's
  `docs/roadmap.md` row; FD-2028's dated line ("decided D, `to-lead.md` 2026-11-07 23:22:37 GMT; fixed by
  SL 8410, or carried to Phase 3 by name") and its register row; optionally one line in `04` §4.4 pointing at
  FR-NEWID. None of these is in this branch: the planner writes plans, closures and the SL rows it cuts
  (`planner.md`, Tools), and the brief limited this branch to the plan, the spec and `INDEX.md`.
- **The lead:** the build seat's brief; the mint order (ids land in merge order); the FR's working id at the
  mint, re-pointed across this branch, the slice and every `@pytest.mark.req` (the named mint exception
  template, `docs/process/process-backlog.md:85`).
- **The auditor:** A1 to A11 at `origin/main...<slice branch>`; FD-2028 closed by the slice's close commit;
  SL 8410's row read at `origin/main` after the merge (common seat brief item 42).

## Self-review

1. **Ruling coverage, 23:22:37.** Option D → FR-NEWID (1)-(4), R2, A2, A5. "Exactly or to a stated working
   precision for a division" → DP-1 (a), stronger: no working precision. "Rounded once half-even to the
   smaller of 28 significant digits and 28 decimal places" → `_result_context`, T-oracle. "Trailing zeros
   dropped" → `_format_value`, unchanged. "`floor_and_cap` does no arithmetic" → FR-NEWID (4), untouched.
   Sub-question (a) → FR-NEWID (5), G4, A3. FR-23 / FR-273 to §14 → acceptance item 5, Hand-off. "New FR in
   03 §3" → acceptance item 3. "OQ-2035 resolved both ways" → item 4. "FD-2028's fix line" → Hand-off
   (not the planner's file). "operations.py's arithmetic context + the rebase refusal removed + tests
   red-first" → R1, R2. "R2's 308 bound untouched" → G3, A6. "Plan Sun 8, build Mon 9, gate Tue 10; not
   started after Tue 10 20:00" → Needs, A10, FR-NEWID's Delivery line.
2. **A reason in the entry does not hold everywhere.** "It writes today's bytes wherever today succeeds" is
   false for a percentage whose `1 + percentage` has more than 28 significant digits (Evidence; DP-2). The
   plan does not decide it; it states it and recommends.
3. **Every cite read** at `27d70555`: `operations.py:21`, `:589-599`, `:694-723`, `:726-742`, `:766-772`,
   `:786-924`; `money.py:126-157`; `rating.py:1385-1411`; `test_rate_table_bulk_ops.py:54-104`,
   `:118-197`, `:313-341`, `:366-550`, `:822-871`; `test_api_rate_tables.py:863-920`; `03` FR-226, FR-233,
   FR-234, FR-245, FR-273, FR-275; `00` FR-23. **Run in scratch, not in the repo** (no code on this
   branch): R1's test text, extracted from this file into `~/gi-pricing-plan.local/scratch/plan-oq2035/red/test_r1.py`,
   against `27d70555`'s `operations.py`: 4 failed by the causes A2 names, 1 passed (the money_minor pin).
   R2's edits applied to a scratch copy (`…/green/src`): the 5 pass, and the three existing files of A4 pass
   against it (204 passed), so no existing test's expected text moves (G6). The executor's R1 run in the
   slice is still the record.
4. **Placeholders:** none in the tasks. `FR-NEWID` is the requirement token until the lead allocates its
   working id; it is replaced everywhere on this branch in one edit.
5. **Sums:** hours 1 + 0.75 + 1 = 2.75.
6. **Calendar**, from `date -d … +%A`: Sat 7 Nov (today), Sun 8, Mon 9, Tue 10, Thu 12 Nov (code freeze),
   Mon 16 Nov (the §14 review).
7. **No range of requirement ids.** Estimates are marked: the hours and the gate's 2.5 h.
8. **The plan rules nothing:** three DPs with recommendations; the gate form is a reading, and the word is
   the maintainer's.
