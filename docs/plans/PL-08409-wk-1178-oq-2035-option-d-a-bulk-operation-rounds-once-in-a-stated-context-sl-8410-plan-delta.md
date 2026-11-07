---
id: PL-8409
family: plan
kind: map
title: WK-1178 — OQ-2035 option D, a bulk rate-table operation computes its exact result and rounds it once, half-even, to the smaller of 28 significant digits and 28 decimal places, in a context it states and records, SL 8410 — a dated Work-plan delta
status: draft                   # draft → active → superseded | retired (§1.2a) — L1: draft→active rides the slice's PR
created: 2026-11-07             # draft under working id 8409
owner: planner
tree: a3db8fcec45b33a1a76ae642e72d203f24e9e99e   # origin/main 27d705552f89c4d3b4a39802acfe86068e4e1d1b
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-2040, FD-2028, FD-2032, OQ-2035, OQ-1784, FR-8412, FR-233, FR-234, FR-239, FR-245, FR-275, FR-226, FR-229, FR-23, FR-273, SL-8410]
---

# PL 8409 — WK-1178: OQ-2035 option D. A bulk operation rounds its exact result once, in a context it states and records (SL 8410, a dated Work-plan delta)

> **For agentic workers:** a **dated Work-plan delta** under Lean P2 L1 (a'). It `relates:` `PL-2040`
> (the sibling delta that refused a bulk operation by value type, FD-2032) and edits no earlier plan. It
> carries the spec change, already written on this branch (FR 8412 in `03` §3.3, OQ-2035 decided in both
> mirrored rows, a dated line on `04` §4.4, the roadmap gate row and SL 8410's row), and one code slice row,
> SL 8410, whose ledger is LG 8411. **It decides nothing.** DP-1 and DP-3 carry recommendations; DP-2 is
> ruled; DP-4 is new with the ruling and carries a recommendation. The executor's skills are
> `superpowers:test-driven-development`, `.claude/skills/python-test`, `.claude/skills/python-package` and
> `.claude/skills/contract-schema`. PL 8409, SL 8410, LG 8411 and FR 8412 are working ids reserved by the
> lead (FR 8412: the lead's message of 2026-11-07, "the new FR's working id is FR 8412").

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
- **The correction and the addition.** `to-lead.md` "2026-11-07 23:29:34 GMT", the maintainer (by
  delegation), on this plan's spike: *"'writes today's bytes wherever today succeeds' is FALSE for a
  percentage whose 1 + p exceeds 28 significant digits … D STANDS, option (i) with the reason re-worded as
  above, and ONE ADDITION to the FR: the operation's RECORDED PARAMETERS (FR-233) carry the arithmetic
  context's identity (precision, rounding, the context version), so FR-239's reproducibility reads 'same
  input AND same recorded context → same bytes', and a cell written before the change reads as 'ambient 28,
  two roundings' by the absence of that field. Not (ii): an opt-in keeps the ambient dependence as the
  default … A re-run of the same op after the change is a NEW table version with its own pin and hash …,
  never the same hash with different bytes, so FR-239's hash rule is not touched; the plan states this
  reading under its DP and the LG quotes the spike's counts. Plan acceptance on that text."*
- **The input.** DM draft `~/gi-pricing-plan.local/scratch/dm-fd8383/oq-draft.md`, sha256 prefix
  `99d83663edf8` (the prefix the 23:22:37 entry names, re-read 2026-11-07), Part 0 and Part 1, and its
  scripts `measure_rule.py`, `measure_engine.py` and their `.out` files.
- **This seat.** Brief `~/gi-pricing-plan.local/handover/brief-plan-oq2035-2026-11-07.md`, sha256 prefix
  `a3b92d33853c`, and the lead's messages of 2026-11-07 after 23:30 GMT (FR 8412; write both roadmap edits;
  the 23:29:34 ruling).

## Goal

The three bulk operations that compute (`uplift_table`, `uplift_by_filter`, `rebase_to_level`) store the
same text for the same table and parameters in any caller; that text is the exact result rounded once,
half-even, to the smaller of 28 significant digits and 28 decimal places; and each records, with its
parameters, the identity of the context it computed in. A non-terminating quotient below 0.1 is stored, not
refused. No payable moves, `_format_value`'s 308 bound is unchanged, and a `money_minor` uplift keeps its
fraction.

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

**Where the record lives (for the 23:29:34 addition).**

- **The shapes** are `model_schema/rating.py`: the request parameters `UpliftTableParameters` (`:1385`),
  `UpliftByFilterParameters` (`:1393`), `FloorAndCapParameters` (`:1402`), `RebaseToLevelParameters`
  (`:1411`), each `extra="forbid"`; the requests `UpliftTableRequest` … `RebaseToLevelRequest`; and the
  records `UpliftTableOperation` (`:1465`) … `RebaseToLevelOperation` (`:1477`), each `Request` +
  `BulkOperationBase`, so **a record's `parameters` is today the request's own class**. None is exported
  from `model_schema/__init__.py`.
- **The request path** parses the request class: `_dispatch_operation`
  (`backend/src/app/platform/rate_tables.py:1513-1540`) runs `UpliftTableParameters.model_validate` and
  friends, so a client cannot send a field the request class does not declare.
- **Storage** is a JSON column, `rate_table_versions.created_by_operation`
  (`backend/src/app/db/models.py:2438`), written by `model_dump(mode="json")`
  (`platform/rate_tables.py:1464-1467`): **a new optional key needs no migration.**
- **No hash covers the record.** `definition_hash` (`backend/src/app/platform/diff_cache.py:61-74`) takes
  `keys` and `value`; `version_content_hash` takes cells; the bundle's `content_hash` takes graph and pins
  (DM draft §0.6, `rating/compile.py`). So the field moves no stored hash.
- **The generated contracts** that carry the record: `docs/contracts/schemas/generated/rate-table-version.schema.json`
  and `docs/contracts/openapi/generated.json`; `bulk-operation-request.schema.json` carries the request and
  does not change. No hand-authored contract carries the bulk-operation shape
  (`git grep -l -E 'rebase_to_level|base_level' -- docs/contracts` lists only the three generated files).
- **The frontend** builds a request (`frontend/src/api/__tests__/rateTables.test.ts:111`) and reads no
  record parameter by name; an optional field adds no required property to the generated client.

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
  match is single rounding, not agreement between two roundings: **20,000 of 20,000 pairs equal.** The
  generator is the seat's, so the count is not a rate of anything; percentages up to 32 decimal places
  were included.
- **"Today's bytes" holds except where `1 + percentage` exceeds 28 significant digits.** Today rounds the
  factor and then the product: two roundings. D rounds once. **606 of 1,999 accepted-today cells** differ
  in the 28th significant digit for one 30-dp percentage. Relative 1e-27; no payable can move. The DM
  draft's 20,000 pairs used factors of at most 6 decimal places, so they could not see this. The 23:29:34
  entry corrects the 23:22:37 reason on this count, and FR 8412 (6) states it.
- **Cost:** about 2.9 µs per cell against 1.0 µs today, a fresh context per call included; 0.73 s for a
  250,000-cell table (FR-232's rows threshold). No NFR budgets a bulk operation (`03` §9 read); NFR-498
  (audit) is unaffected.

### The chain's collisions (Gate form below)

Heads read 2026-11-07: `origin/sl-8370-permission-pin` `9c9cbdc4`, `origin/sl-8381-report-response`
`7ef66d7b`, `origin/sl-8406-sweep-owner-dsn` `c7cad487`. Each side's list is `git diff --name-only
origin/main...<branch>`.

## Decision points

No DP is the planner's to rule. **DP-1 and DP-4 block R2.**

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
  they are today. Under (a), FR 8412 (1) says "no intermediate is rounded", which is stronger than the
  entry's "or to a stated working precision for a division" and is what the entry's "rounded once" needs.
- **DP-2: the long-percentage exception to "today's bytes". RULED 2026-11-07 23:29:34 GMT, option (i): round
  once.** Where `1 + percentage` has more than 28 significant digits, a result can differ from today's in its
  28th significant digit (relative 1e-27; the spike's 606 of 1,999 cells for one 30-dp percentage); no
  payable can move. (ii), rounding the factor first as an opt-in or a default, is refused: it keeps the
  ambient dependence as the default. **The reading the entry requires, stated here: FR-239's hash rule is
  not touched.** A re-run of the same operation after the change is a new Rate Table Version
  (`version + 1`, FR-229) with its own pin `rate_table:<slug>@<n+1>`; a Rating Version pinning it is a new
  Rating Version with its own `content_hash`, since the bundle hash takes the graph and the pins (DM draft
  §0.6). The same hash with different bytes cannot arise from this change. **Reproducibility then reads
  "same input and same recorded context, same bytes"** (FR 8412 (7)): the record of a version created after
  the change names the context, and a record without it was written under "ambient 28, two roundings".
- **DP-3: what "keeps its stored text" compares.** (a) **The rounded result** equals the current value
  (today's `_transform_rows`, `:734-736`, and `uplift_by_filter`, `:827`). (b) The exact result equals the
  current value (the DM draft's proposed wording, oq-draft.md `:118`). **Recommendation (a).** Under (b) a
  cell such as `1.8400` uplifted by `1E-40` would be re-written as `1.84` and counted as changed although
  its value did not move; (a) is today's behaviour and keeps today's bytes. FR 8412 (4) is written as (a).
- **DP-4 (blocking, new with the 23:29:34 addition): where the recorded context sits, and its shape.**
  (a) **Record-only parameter classes.** `UpliftTableRecordedParameters(UpliftTableParameters)`, and the same
  for `uplift_by_filter` and `rebase_to_level`, each adding `context: BulkOperationContext | None = None`;
  the three `…Operation` records narrow `parameters` to them. The request classes do not change, so
  `extra="forbid"` still refuses a client that sends `context`, and only the operation writes it. The field
  is inside `parameters`, the entry's words. (b) **A sibling field on the record**, `context` beside
  `parameters` on `BulkOperationBase`. One field, no subclasses; but it is not "the recorded parameters",
  and `floor_and_cap` would carry a context for no arithmetic. (c) **On the request parameters**, overwritten
  by the server. Fewest classes; but the request contract gains a field a client may send and the server
  ignores. **Recommendation (a).** **Shape:** `BulkOperationContext` = `precision` (int, 28), `places` (int,
  28), `rounding` (`Literal["half_even"]`) and `version` (int, 1); `extra="forbid"`, frozen. `places` is the
  planner's addition to the entry's list (precision, rounding, version): the 28-dp limit is half the rule,
  and a record that omitted it would not name the context. `floor_and_cap` records none (no arithmetic).
  **A pre-change record** parses with `context = None` and dumps without the key
  (`exclude_if`), so its stored bytes do not move: `packages/model-schema/tests/test_rate_tables.py`'s
  `test_a_bulk_operation_record_dumps_the_bytes_it_dumped_before_the_request_models` pins them, and a
  `context = None` default that dumped `"context": null` turned it red in the planner's scratch run. `version` changes only with a new
  requirement that changes the rule. The `04` §4.4 dated line on this branch states shape (a); a different
  ruling amends that line in the same edit.

## Acceptance Standard

Each item is checked by a command a fresh reviewer can run. Items 1 to 6 apply to this branch (the spec
change, the roadmap rows and the plan); A1 to A14 to SL 8410.

1. **The docs checks pass on this branch.** `python3 scripts/audit-docs.py` prints no failing line except
   those for the working ids this branch uses (PL 8409, SL 8410, LG 8411, FR 8412), and
   `python3 scripts/doc-index.py --check` exits 0. After the mint both exit 0.
2. **No requirement range.** `grep -nE '(N?FR)-[0-9]+ *(-|to|–) *(N?FR-)?[0-9]+' <this file>` prints no
   line that stands for a set of ids.
3. **One new requirement, after FR-233.** `grep -c '^| \*\*FR-8412\*\* |' docs/specs/03-rating-engine.md`
   prints `1`, and `grep -n -A1 '^| \*\*FR-233\*\* |' docs/specs/03-rating-engine.md` shows it on the next
   line; its text names clause (7), the recorded context, citing `2026-11-07 23:29:34 GMT`.
4. **OQ-2035 is decided in both places, the same way.** `grep -c '^| ~~\*\*OQ-2035\*\*~~ ✔ | \*\*DECIDED
   2026-11-07: option D' docs/open-questions.md docs/specs/03-rating-engine.md` prints `1` for each file,
   and each row cites `2026-11-07 23:22:37 GMT` and FR 8412; the register row also cites `23:29:34`.
5. **FR-23 and FR-273 are not changed.** `git diff origin/main...HEAD -- docs/specs/00-overview.md` prints
   nothing, and `git diff -U0 origin/main...HEAD -- docs/specs/03-rating-engine.md | grep -c '^[-+]|
   \*\*FR-273\*\*'` prints `0`.
6. **The roadmap carries both edits.** `grep -c '~~\*\*OQ-2035\*\*~~ ✔' docs/roadmap.md` prints `1` and the
   same row reads `**14 (9 open)**`; `grep -c '^id: SL-8410$' docs/roadmap.md` prints `1` with
   `status: draft`.

SL 8410:

- **A1. The write set** is the Write set below, by `git diff --name-only origin/main...HEAD`, quoted.
- **A2. Red first, by cause, in LG 8411 before the green.** R1's first class runs at the slice's base and
  fails for these causes, each failure quoted: T-rebase raises `RATE_TABLE_CELL_UNPARSEABLE`; T-ambient
  raises `RATE_TABLE_CELL_UNPARSEABLE` on `'3.37037036703703703670370370367'` under `prec=400`, a text the
  default context rounds and stores; T-long-percentage stores `2.240172837290617283729061729`, not `…728`;
  T-oracle raises the rebase refusal or reports a non-empty mismatch list. The record class runs after R2a
  (the `model-schema` classes) and before R2b (the operations), so its red is a record whose `context` is
  `None`. An import error, a fixture error or a `NameError` is not the red.
- **A3. The pin is green before and after.** T-money-minor (`12345` uplifted by `0.0375` stores
  `12807.9375`) passes at the base and at the head: option (a) is today's behaviour, and the test keeps it.
- **A4. Green.** `run-small.sh <wt> packages/pricing-core/tests/test_rate_table_bulk_ops.py
  packages/pricing-core/tests/test_rate_table_operations.py
  packages/pricing-core/tests/test_rate_table_weights.py` passes, the summary line and rc quoted whole.
- **A5. No ambient context, and the old arithmetic is gone.** `git grep -n -E
  'getcontext|setcontext|localcontext' -- packages/pricing-core/src/pricing_core/rate_tables/` prints
  nothing, and `grep -n -E 'Decimal\(1\) \+ percentage|old \* factor|\]\) / reference'
  packages/pricing-core/src/pricing_core/rate_tables/operations.py` prints nothing.
- **A6. R2's 308 bound is untouched.** `git diff origin/main...HEAD -- packages/model-schema/src/model_schema/money.py`
  prints nothing; `git diff -U0 origin/main...HEAD -- packages/pricing-core/src/pricing_core/rate_tables/operations.py
  | grep -c -E '^[-+].*(MAX_POSITIONAL_EXPONENT|def _format_value)'` prints `0`; and
  `TestFormatValueIsBoundedBeforeItIsBuilt` passes inside A4.
- **A7. The requirement is evidenced.** `uv run python scripts/req-coverage.py` lists FR 8412 with the new
  tests in `test_rate_table_bulk_ops.py` as its evidence (`@pytest.mark.req("FR-8412")`).
- **A8. The record carries the context, and only the operation writes it.** `TestTheRecordCarriesTheContext`
  passes: `uplift_table`, `uplift_by_filter` and `rebase_to_level` records carry `parameters.context ==
  BulkOperationContext(precision=28, places=28, rounding="half_even", version=1)`; a `floor_and_cap` record
  has no `context` field; `UpliftTableRequest.model_validate` with a `context` in `parameters` raises
  `ValidationError` (`extra_forbidden`); a stored record without `context` parses with `context is None`.
- **A9. The contracts follow the shape, generated, never hand-edited.** `uv run python
  scripts/generate-contracts.py --check` exits 0 at the head; `git diff --name-only origin/main...HEAD --
  docs/contracts` lists only `docs/contracts/schemas/generated/rate-table-version.schema.json` and
  `docs/contracts/openapi/generated.json`; `bulk-operation-request.schema.json` is not in it.
- **A10. GREEN by import closure (common seat brief, item 29),** the commands and the list quoted in LG 8411:
  changed modules `git diff --name-only origin/main...HEAD -- packages/*/src backend/src`.
  `model_schema/rating.py` is imported by most of the codebase, so the closure is wide; its test files beyond
  A4's run in the gate. The rate-table closure read at `27d70555` is `operations.py` →
  `app/platform/rate_tables.py` → `app/api/rate_tables.py`, `app/platform/rating_versions.py`,
  `app/worker/rate_table_handlers.py`, with 26 test files importing one of them (including
  `test_api_rate_tables.py`).
- **A11. The API's two bound tests pass in the gate,** by name:
  `test_bulk_operation_with_a_huge_percentage_is_a_coded_422_not_a_memory_fault` and
  `test_bulk_operation_whose_computed_cell_passes_the_bound_is_a_cell_422`
  (`backend/tests/test_api_rate_tables.py:863`, `:896`).
- **A12. Nothing beyond the operations and the record.** `git diff --name-only origin/main...HEAD` lists no
  file under `frontend/`, `backend/src/` or `backend/migrations/`, and not
  `packages/model-schema/src/model_schema/__init__.py`.
- **A13. The gate.** One full code gate, both halves, on the re-merged head, every rc quoted (`CLAUDE.md`
  §11), **started no later than Tue 10 Nov 2026 20:00 GMT**. If it cannot start by then it is not started:
  LG 8411 records "not started; FR 8412 stands as the rule; the code is carried to Phase 3 by name", and the
  P2 closure record carries SL 8410 by name (the 23:22:37 entry).
- **A14. The LG quotes the spike** (the 23:29:34 entry): "20,000 of 20,000 pairs equal to an exact-rational
  oracle" and "606 of 1,999 accepted-today cells differ in the 28th digit for one 30-dp percentage", with
  the script's path and this plan's Evidence block as the source.

## Global Constraints

- **G1. Money and rates are never float** (`CLAUDE.md` §7; FR-245): `decimal` only; no `float()` on a cell
  or a parameter.
- **G2. `pricing-core` stays standalone** (`CLAUDE.md` §2): the change uses the standard library's
  `decimal` only; no new dependency, so `skills-map.md` does not change.
- **G3. `_format_value` and `MAX_POSITIONAL_EXPONENT` are not edited** (R2's 308 bound, the entry).
- **G4. A `money_minor` result is not rounded to whole minor units** (the entry's (a)).
- **G5. One shape change only:** the record-side `context` of DP-4. No request field, no migration, no
  per-table dp (option A stays open with `OQ-1784`). The shape is written once, in `model-schema`
  (`CLAUDE.md` §2); `docs/contracts/` is regenerated, never hand-edited.
- **G6. A failing test is never weakened or removed** (common seat brief, item 13). An existing test whose
  expected text moves is reported verbatim and STOPs for the lead. None is known: the three files of A4 pass
  against R2's operations in scratch (Self-review 3).
- **G7. `model_schema/__init__.py` is not edited** (sl-8381 changes it; the bulk-operation classes are not
  exported today, and `BulkOperationContext` is imported from `model_schema.rating`).
- **G8. Line numbers are `27d70555`'s** and are re-derived at the slice's base.
- **G9. Requirement and section ids are permanent** (`CLAUDE.md` §5); no range of ids in any file this plan
  writes.

## Needs

- **Seats:** one executor (model per `executor.md`) and one auditor. No decision-maker once DP-1, DP-3 and
  DP-4 are ruled.
- **Ids:** PL 8409, SL 8410, LG 8411 and FR 8412, all reserved by the lead. No other id is foreseen.
- **DB:** none for R1 and R2: `operations.py`, the `model-schema` classes and the test file are pure, run
  through `run-small.sh` (no `createdb`, no migration; common seat brief, item 32). The full gate brings
  its own DB as every gate does; no window of the slice's own.
- **Redis:** none outside the gate. **Docker:** only the stack already up from `tools-main`; no compose
  build, no restart. **MinIO:** none. **NFR VM:** none.
- **Gate cost:** one full code gate, about 2.5 h of wall time (PL-2059's, PL-2053's and PL 8405's estimate
  for a full gate; not measured for this slice). No migration. **The contract changes**, so `frontend.yml`
  fires in CI (its filter `docs/contracts/openapi/**`) as well as `python.yml` (`packages/**`); the local
  gate runs both halves regardless (`CLAUDE.md` §11), with `pnpm --dir frontend generate:api` before the
  frontend half. No timed path changes: a bulk operation is not inside an NFR measurement.
- **Hours, gate not counted, an estimate:** R1 1.25 h, R2a 0.75 h, R2b 0.75 h, contracts 0.5 h, LG 8411 and
  records 1 h, so **about 4.25 h**, plus about 1 h of audit.
- **Calendar** (the entry; weekdays read from `date -d … +%A`): plan Sun 8 Nov, build Mon 9 Nov, gate Tue
  10 Nov, **not started if its gate cannot start by Tue 10 Nov 20:00 GMT**, merged inside Thu 12 Nov (the
  code freeze).

## Gate form: by FILE, against the chain's open branches

The slice's paths: `packages/pricing-core/src/pricing_core/rate_tables/operations.py`,
`packages/model-schema/src/model_schema/rating.py`, `packages/pricing-core/tests/test_rate_table_bulk_ops.py`,
and the generated `docs/contracts/schemas/generated/rate-table-version.schema.json` and
`docs/contracts/openapi/generated.json`.

- **Code ∩ sl-8370, sl-8381, sl-8406: empty.** The command, per branch: `comm -12 <(printf '%s\n'
  packages/pricing-core/src/pricing_core/rate_tables/operations.py
  packages/model-schema/src/model_schema/rating.py
  packages/pricing-core/tests/test_rate_table_bulk_ops.py | sort) <(git diff --name-only
  origin/main...origin/<branch> | sort)`. Their code lists at the heads above: sl-8370
  `backend/src/app/api/models.py`, `backend/src/app/platform/modelling.py` and two backend tests; sl-8381 the
  validation report (`backend/src/app/{api,platform}/validation.py`,
  `packages/model-schema/src/model_schema/{__init__,validation}.py`, `scripts/audit-docs.py`,
  `scripts/generate-contracts.py`, `frontend/src/api/validation.ts` and tests); sl-8406
  `scripts/measure-p2-nfr-sweep.py` and two tests.
- **Generated ∩ sl-8381: `docs/contracts/openapi/generated.json`.** Both regenerate it. Whichever merges
  second re-merges `main`, **regenerates** it with `scripts/generate-contracts.py` (never a hand merge of
  the generated file; `CLAUDE.md` §2), runs `--check` (rc 0) and the frontend half's `generate:api` and
  `type-check`. sl-8381 also changes `scripts/generate-contracts.py`; the regeneration after a re-merge uses
  `main`'s script.
- **Records ∩:** `docs/INDEX.md` with all three (regenerated, common seat brief item 5);
  `docs/specs/03-rating-engine.md` and `docs/specs/04-optimisation.md` with sl-8381, whose hunks there are
  fence lines (`03` `:250`, `:374`, `:502`, … `:1021`; `04` `:135`, `:174`, `:213`, `:254`, at its base
  `e12dc849`), none at `03` §3.3 or §10 or at `04`'s line after `:276`, where this branch writes;
  `docs/roadmap.md` and `docs/open-questions.md` with none.
- **Partition paths:** none in this slice: no `backend/migrations/`, `deploy/`, `conftest*`, `.github/`,
  `pyproject.toml`, `uv.lock` or `frontend/`.
- **Imports read (item 29), both ways.** Into the slice: `operations.py` imports `model_schema.modelling`,
  `model_schema.money`, `model_schema.rating`, `model_schema.refs` and `pricing_core.rating.compile`
  (`:31-60`), so every import runs `model_schema/__init__.py`, which sl-8381 changes (its exports): one-way
  and import-time only. Out of the slice: `model_schema/rating.py` is imported widely, but the change adds
  four classes and narrows three record fields, and nothing outside `operations.py` and the tests constructs
  a bulk-operation record (`git grep -n -E 'UpliftTableOperation|RebaseToLevelOperation|UpliftByFilterOperation'`
  at `27d70555`). sl-8370's `platform/modelling.py` is not imported by `platform/rate_tables.py` (its
  `from app.platform import` lines, `:39-41`).
- **Verdict: pairable with sl-8370 and sl-8406** (no shared file, no partition path). **With sl-8381,
  pairable, with the one generated file:** the second to merge regenerates `generated.json` and re-runs
  `--check` and the frontend half, and item 21 applies (re-merge, then A4's three files at the re-merged
  head before the PR). The maintainer gives the word for single or paired.

## Tasks

### SL 8410: the row. Scope: A1 to A14; `03` FR 8412 (new), FR-233, FR-234 (the refusal it keeps), FR-239 (unchanged, read), FR-245, FR-275, FR-226; `04` §4.4; lane WK-1178; after this plan's acceptance, gate by Tue 10 Nov 20:00 GMT

**Files:**
- Modify: `packages/model-schema/src/model_schema/rating.py` (after `RebaseToLevelParameters`, `:1411-1416`;
  the three records `:1465-1480`)
- Modify: `packages/pricing-core/src/pricing_core/rate_tables/operations.py` (`:21` the `decimal` import;
  `:31-58` the `model_schema.rating` import; a new `_result_context` after `_format_value`, `:694-723`;
  `uplift_table` `:786-809`; `uplift_by_filter` `:812-848`; `rebase_to_level` `:880-924`)
- Test: `packages/pricing-core/tests/test_rate_table_bulk_ops.py` (two new classes at the end of the file)
- Regenerate: `docs/contracts/schemas/generated/rate-table-version.schema.json`,
  `docs/contracts/openapi/generated.json`
- Ledger: LG 8411 under `docs/ledgers/`

**Interfaces:**
- Consumes: `uplift_table(table, *, percentage)`, `uplift_by_filter(table, *, percentage, filter)`,
  `rebase_to_level(table, *, base_level)`, `floor_and_cap(table, *, floor, cap)`, unchanged signatures; the
  test helpers `_version`, `_value`, `_cells`, `_key` and `_CODE` already in the test file (`:54-104`,
  `:201`).
- Produces: in `model_schema.rating`, `BulkOperationContext`, `UpliftTableRecordedParameters`,
  `UpliftByFilterRecordedParameters`, `RebaseToLevelRecordedParameters`; in `operations.py`, the private
  `_result_context() -> decimal.Context` and `_RESULT_CONTEXT_RECORD: BulkOperationContext`.

#### R0: base and set-up

- [ ] **Step 1:** Worktree from `origin/main` per the brief; `uv sync --directory <wt> --all-packages --frozen`.
  Quote `git -C <wt> rev-parse HEAD`.
- [ ] **Step 2:** Re-derive this plan's line numbers at the base:
  `grep -n -E 'Decimal\(1\) \+ percentage|old \* factor|\]\) / reference|def _format_value' packages/pricing-core/src/pricing_core/rate_tables/operations.py`
  and `grep -n -E '^class (UpliftTable|UpliftByFilter|RebaseToLevel)(Parameters|Operation)' packages/model-schema/src/model_schema/rating.py`.
  A changed site is reported before any edit.

#### R1: the red tests for the arithmetic, first

- [ ] **Step 1: Write the failing tests.** Append to `packages/pricing-core/tests/test_rate_table_bulk_ops.py`
  (add `ROUND_DOWN, ROUND_HALF_EVEN, localcontext` to the `decimal` import and `from fractions import
  Fraction`):

```python
def _round_once(exact: Fraction) -> Decimal:
    """FR 8412's rule computed independently: exact rational, rounded half-even with integers
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
    """FR 8412 (OQ-2035 option D, to-lead "2026-11-07 23:22:37 GMT"): the exact result, rounded
    once, half-even, to the smaller of 28 significant digits and 28 decimal places, in a context
    the operation states and never the caller's."""

    @pytest.mark.req("FR-8412")
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

    @pytest.mark.req("FR-8412")
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

    @pytest.mark.req("FR-8412")
    def test_the_factor_is_not_rounded_before_the_product(self) -> None:
        """DP-2, ruled (i): one rounding. Today rounds 1 + percentage to 28 digits first and
        stores 2.240172837290617283729061729."""
        result = uplift_table(
            _one_cell("1.994"), percentage=Decimal("0.123456789012345678901234567890")
        )
        assert _cells(result)[0]["relativity"] == "2.240172837290617283729061728"

    @pytest.mark.req("FR-8412")
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

    @pytest.mark.req("FR-8412")
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
  `3.370370367037037036703703704` one iteration earlier); `test_the_factor_is_not_rounded_before_the_product`
  FAILS with `…729` != `…728`; `test_every_result_is_the_exact_result_rounded_once` FAILS with the rebase
  refusal (`'0.001817401515196671574266691304'` in the planner's scratch run) or a non-empty `mismatches`.
  `test_a_money_minor_uplift_holds_the_fraction` PASSES (A3). Every other test in the file PASSES.
- [ ] **Step 3: Commit** the class alone: `test(pricing-core): FR 8412 red — a bulk operation rounds once in
  a stated context (SL 8410)`.

#### R2a: the record's shape (model-schema), then the record's red

- [ ] **Step 1: Write the classes.** In `model_schema/rating.py`, after `RebaseToLevelParameters`:

```python
class BulkOperationContext(BaseModel):
    """FR 8412 (7): the decimal context a computing bulk operation ran in, recorded with its
    parameters (04 §4.4). The operation writes it; no request carries it."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    precision: int = Field(ge=1)
    places: int = Field(ge=0)
    rounding: Literal["half_even"]
    version: int = Field(ge=1)


class UpliftTableRecordedParameters(UpliftTableParameters):
    """The record's parameters: the request's, plus the context (FR 8412). `None` on a record
    written before FR 8412, which reads as ambient 28 digits, factor and product each rounded.
    It is not dumped when `None`, so a stored record's bytes do not move."""

    context: BulkOperationContext | None = Field(
        default=None, exclude_if=lambda value: value is None
    )


class UpliftByFilterRecordedParameters(UpliftByFilterParameters):
    """As `UpliftTableRecordedParameters`, for `uplift_by_filter` (FR 8412)."""

    context: BulkOperationContext | None = Field(
        default=None, exclude_if=lambda value: value is None
    )


class RebaseToLevelRecordedParameters(RebaseToLevelParameters):
    """As `UpliftTableRecordedParameters`, for `rebase_to_level` (FR 8412)."""

    context: BulkOperationContext | None = Field(
        default=None, exclude_if=lambda value: value is None
    )
```

  and the three records become:

```python
class UpliftTableOperation(UpliftTableRequest, BulkOperationBase):
    parameters: UpliftTableRecordedParameters


class UpliftByFilterOperation(UpliftByFilterRequest, BulkOperationBase):
    parameters: UpliftByFilterRecordedParameters


class RebaseToLevelOperation(RebaseToLevelRequest, BulkOperationBase):
    parameters: RebaseToLevelRecordedParameters
```

  `FloorAndCapOperation` is unchanged. `model_schema/__init__.py` is not edited (G7).
- [ ] **Step 2: Write the record's tests.** Append to the test file (add `from pydantic import
  ValidationError`, and `BulkOperationContext` and `UpliftTableRequest` to its `model_schema.rating`
  import):

```python
class TestTheRecordCarriesTheContext:
    """FR 8412 (7), to-lead "2026-11-07 23:29:34 GMT": the recorded parameters name the context;
    the operation writes it, a request cannot; a record from before reads as None."""

    _CONTEXT = BulkOperationContext(precision=28, places=28, rounding="half_even", version=1)

    @pytest.mark.req("FR-8412")
    def test_each_computing_operation_records_its_context(self) -> None:
        records = [
            uplift_table(_version(), percentage=Decimal("0.10")).created_by_operation,
            uplift_by_filter(
                _version(),
                percentage=Decimal("0.10"),
                filter={"driver_age_band": ["17-20"]},
            ).created_by_operation,
            rebase_to_level(
                _version(value=_value(min=None, max=None)),
                base_level={"driver_age_band": ["25-29"]},
            ).created_by_operation,
        ]
        for record in records:
            assert record is not None
            assert record.parameters.context == self._CONTEXT

    @pytest.mark.req("FR-8412")
    def test_floor_and_cap_records_no_context(self) -> None:
        record = floor_and_cap(
            _version(), floor=Decimal("1.2"), cap=Decimal("1.5")
        ).created_by_operation
        assert record is not None
        assert "context" not in record.parameters.model_dump()

    @pytest.mark.req("FR-8412")
    def test_a_request_cannot_send_the_context(self) -> None:
        with pytest.raises(ValidationError, match="extra_forbidden|Extra inputs"):
            UpliftTableRequest.model_validate(
                {
                    "kind": "uplift_table",
                    "parameters": {"percentage": "0.10", "context": self._CONTEXT.model_dump()},
                }
            )

    @pytest.mark.req("FR-8412")
    def test_a_record_from_before_reads_as_no_context(self) -> None:
        stored = uplift_table(_version(), percentage=Decimal("0.10")).model_dump(mode="json")
        assert stored["created_by_operation"]["parameters"].pop("context") is not None
        legacy = RateTableVersion.model_validate(stored)
        assert legacy.created_by_operation is not None
        assert legacy.created_by_operation.parameters.context is None
```

  Run the file: `test_each_computing_operation_records_its_context` FAILS with `context` `None` (the
  operation does not write it yet); `test_a_record_from_before_reads_as_no_context` FAILS with
  `KeyError: 'context'` (a `None` context is not dumped); `test_floor_and_cap_records_no_context` and
  `test_a_request_cannot_send_the_context` PASS (the shape holds them). Quote each in LG 8411.
- [ ] **Step 3: Regenerate the contracts.** `uv run --directory <wt> python scripts/generate-contracts.py`,
  then `--check` (rc 0); quote `git diff --stat -- docs/contracts` (A9).
- [ ] **Step 4: Commit** `feat(model-schema): FR 8412 — a bulk operation's record names its arithmetic
  context (SL 8410)`.

#### R2b: the stated context (operations)

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

  The `model_schema.rating` import gains `BulkOperationContext`, `RebaseToLevelRecordedParameters`,
  `UpliftByFilterRecordedParameters` and `UpliftTableRecordedParameters`, and drops
  `RebaseToLevelParameters`, `UpliftByFilterParameters` and `UpliftTableParameters` if nothing else in the
  file uses them (`grep -n` them first). After `_format_value`, add:

```python
#: FR 8412: a bulk operation's result is rounded once, half-even, to the smaller of 28
#: significant digits (FR-245) and 28 decimal places (FR-275's scale limit).
_RESULT_DIGITS = 28
_RESULT_PLACES = 28

#: FR 8412 (7): the identity of `_result_context`, recorded with every computing operation's
#: parameters. `version` changes only with a requirement that changes the rule.
_RESULT_CONTEXT_RECORD = BulkOperationContext(
    precision=_RESULT_DIGITS, places=_RESULT_PLACES, rounding="half_even", version=1
)


def _result_context() -> Context:
    """FR 8412: the one context a bulk operation computes in, never the caller's.

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

  and its record's `parameters=UpliftTableParameters(percentage=percentage)` with
  `parameters=UpliftTableRecordedParameters(percentage=percentage, context=_RESULT_CONTEXT_RECORD)`.

  `uplift_by_filter`: replace `factor = Decimal(1) + percentage` (`:819`) with
  `context = _result_context()`, `new = old * factor` (`:826`) with
  `new = old.fma(percentage, old, context=context)`, and its record's parameters with
  `UpliftByFilterRecordedParameters(percentage=percentage, filter=filter, context=_RESULT_CONTEXT_RECORD)`.

  `rebase_to_level`: before the loop add `context = _result_context()`, replace `:909` with
  `quotient = context.divide(Decimal(row[value_name]), reference)`, and its record's parameters with
  `RebaseToLevelRecordedParameters(base_level=base_level, context=_RESULT_CONTEXT_RECORD)`.

  Each of the three docstrings gains one line: "The result is rounded once, in `_result_context`, and the
  record names it (FR 8412)." `_format_value` is not edited (G3).
- [ ] **Step 2: Run green.** The STOP rule first. Run A4's three files through `run-small.sh`. Expected: all
  pass, including `TestFormatValueIsBoundedBeforeItIsBuilt` and the nine new tests. Quote the summary line
  and rc whole.
- [ ] **Step 3: Static checks.** `uv run --directory <wt> ruff check .`;
  `uv run --directory <wt> ruff format --check <the three changed .py files>`; `uv run --directory <wt> mypy`;
  `uv run --directory <wt> lint-imports`; `uv run --directory <wt> python scripts/generate-contracts.py --check`.
  Every rc quoted. A mypy error on the narrowed `parameters` field is reported verbatim and STOPs for the
  lead (DP-4 (b) is the fallback); it is never silenced with an ignore.
- [ ] **Step 4: A5, A6, A9 and A12's commands,** output quoted in LG 8411.
- [ ] **Step 5: Commit** `fix(pricing-core): FR 8412 — a bulk operation rounds its exact result once, in a
  stated context it records (SL 8410, OQ-2035 D)`.

#### G: the gate

- [ ] **Step 1:** Re-merge `origin/main` (a merge, never a rebase; common seat brief item 5). If sl-8381 or any
  code merged since the base, regenerate the contracts (`--check` rc 0) and run A4's three files at the
  re-merged head first (item 21).
- [ ] **Step 2:** One full code gate, both halves, on the lead's word (single or paired, Gate form), **started
  by Tue 10 Nov 2026 20:00 GMT** or not started (A13). Every rc quoted; A11's two tests named in the pytest
  output.
- [ ] **Step 3:** LG 8411 carries R1's red, R2a's record red, R2b's green, the spike's counts (A14), the GREEN
  derivation (A10) and the gate's rc table before the audit.

### Write set

`packages/model-schema/src/model_schema/rating.py`;
`packages/pricing-core/src/pricing_core/rate_tables/operations.py`;
`packages/pricing-core/tests/test_rate_table_bulk_ops.py`;
`docs/contracts/schemas/generated/rate-table-version.schema.json` and `docs/contracts/openapi/generated.json`
(generated); LG 8411; SL 8410's roadmap row (`status:` and `tree:` only, at the mint and the close); this
plan (`status:` only); `docs/INDEX.md`. The spec change (FR 8412, the two OQ-2035 rows, the `04` §4.4 dated
line, the gate row and SL 8410's row) is already on this plan's branch and merges with it or before the
slice.

### Files shared

Code: none with sl-8370, sl-8381 or sl-8406. Generated: `docs/contracts/openapi/generated.json` with
sl-8381, regenerated after re-merge (Gate form). Records: `docs/INDEX.md` with all three;
`docs/specs/03-rating-engine.md` and `docs/specs/04-optimisation.md` with sl-8381 (different hunks), by
re-merge.

## Hand-off (not this plan's writes)

- **The maintainer:** DP-1, DP-3 and DP-4; this plan's acceptance; the slice GO; the gate's word (single or
  paired).
- **The `CLAUDE.md` §14 review (P3 spec proposal, the entry's words):** does `00` FR-23's `_minor` suffix
  promise integrality in a rate cell, and should FR-273's list ("relativities, loadings, factors") name a
  money cell? FR 8412 (5) points there and changes neither. **D is carried into the §14 high re-read as a
  decision, not a proposal** (the 23:22:37 entry), with the 23:29:34 correction.
- **The lead, or the next docs batch:** FD-2028's dated line ("decided D, `to-lead.md` 2026-11-07 23:22:37
  GMT, corrected 23:29:34; fixed by SL 8410, or carried to Phase 3 by name") and its register row. Not this
  branch's: the planner writes plans, closures and the SL rows it cuts (`planner.md`, Tools); the roadmap gate
  row is on this branch on the lead's instruction.
- **The lead:** the build seat's brief; the mint order (the lead's message: PL 8409, SL 8410, LG 8411 and
  FR 8412 mint at the spec change's PR, cited before citing); FR 8412 re-pointed across this branch, the
  slice and every `@pytest.mark.req` at the mint (the named mint exception template,
  `docs/process/process-backlog.md:85`).
- **The auditor:** A1 to A14 at `origin/main...<slice branch>`; FD-2028 closed by the slice's close commit;
  SL 8410's row read at `origin/main` after the merge (common seat brief item 42).

## Self-review

1. **Ruling coverage, 23:22:37.** Option D → FR 8412 (1)-(4), R2b, A2, A5. "Exactly or to a stated working
   precision for a division" → DP-1 (a), stronger: no working precision. "Rounded once half-even to the
   smaller of 28 significant digits and 28 decimal places" → `_result_context`, T-oracle. "Trailing zeros
   dropped" → `_format_value`, unchanged. "`floor_and_cap` does no arithmetic" → FR 8412 (4), untouched.
   Sub-question (a) → FR 8412 (5), G4, A3. FR-23 / FR-273 to §14 → acceptance item 5, Hand-off. "New FR in
   03 §3" → item 3. "OQ-2035 resolved both ways" → item 4. "FD-2028's fix line" → Hand-off. "operations.py's
   arithmetic context + the rebase refusal removed + tests red-first" → R1, R2b. "R2's 308 bound untouched"
   → G3, A6. "Plan Sun 8 … not started after Tue 10 20:00" → Needs, A13, FR 8412's Delivery line, SL 8410's
   row.
2. **Ruling coverage, 23:29:34.** The re-worded reason → FR 8412 (6), DP-2, the register row. The recorded
   context (precision, rounding, version) → FR 8412 (7), DP-4, R2a, A8, the `04` §4.4 line. "Same input and
   same recorded context → same bytes" → FR 8412 (7), DP-2. "Ambient 28, two roundings by absence" → FR 8412
   (7), DP-4, the legacy-record test. "Not (ii)" → FR 8412 (3), DP-2. "A re-run is a new version with its own
   pin and hash; FR-239's hash rule not touched" → DP-2, FR 8412 (7). "The LG quotes the spike's counts" →
   A14. **One addition of the planner's, marked:** `places` in the context's identity (DP-4).
3. **Every cite read** at `27d70555`: `operations.py:21`, `:31-60`, `:589-599`, `:694-723`, `:726-742`,
   `:766-772`, `:786-924`; `money.py:126-157`; `rating.py:1376-1490`; `db/models.py:2438`;
   `platform/rate_tables.py:39-41`, `:1464-1467`, `:1513-1540`; `diff_cache.py:61-74`;
   `test_rate_table_bulk_ops.py:54-104`, `:118-197`, `:313-341`, `:366-550`, `:822-871`;
   `test_api_rate_tables.py:863-920`; `03` FR-226, FR-233, FR-234, FR-239, FR-245, FR-273, FR-275; `00`
   FR-23; `04` §4.4. **Run in scratch, not in the repo** (no code on this branch), under
   `~/gi-pricing-plan.local/scratch/plan-oq2035/`: R1's class, extracted from this file, against
   `27d70555`'s `operations.py`: 4 failed by the causes A2 names, 1 passed (the money_minor pin). R2b's
   arithmetic applied to a scratch copy: the 5 pass, and the three existing files of A4 pass against it
   (204 passed), so no existing test's expected text moves (G6). After the 23:29:34 ruling, R2a and
   R2b applied together to a scratch copy (`…/green2/src`), every code block taken from this file: the 9
   new tests pass, and A4's three files plus `packages/model-schema/tests` pass (935 passed). The first shape
   tried, `context: … = None`, dumped `"context": null` and turned
   `test_a_bulk_operation_record_dumps_the_bytes_it_dumped_before_the_request_models` red, so the plan uses
   `exclude_if` (pydantic 2.14.1 in the venv). `mypy --strict` over the scratch `model_schema.rating` and
   `operations` reports no error on the narrowed `parameters` fields (only `unused-ignore` lines that
   `--ignore-missing-imports` causes). **Not run:** `generate-contracts.py` and the gate.
4. **Placeholders:** none. FR 8412 is the lead's working id, in space form in prose and `FR-8412` in ids
   and markers.
5. **Sums:** hours 1.25 + 0.75 + 0.75 + 0.5 + 1 = 4.25.
6. **Calendar**, from `date -d … +%A`: Sat 7 Nov (today), Sun 8, Mon 9, Tue 10, Thu 12 Nov (code freeze),
   Mon 16 Nov (the §14 review).
7. **No range of requirement ids.** Estimates are marked: the hours and the gate's 2.5 h.
8. **The plan rules nothing:** DP-2 is the maintainer's ruling, quoted; DP-1, DP-3 and DP-4 carry
   recommendations; the gate form is a reading, and the word is the maintainer's.
