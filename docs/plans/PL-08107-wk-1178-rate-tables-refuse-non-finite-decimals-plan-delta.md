---
id: PL-8107
family: plan
kind: map
title: WK-1178 — a rate table refuses a non-finite decimal (NaN, sNaN, ±Infinity) as a named FR-234 issue, never a 500 (SL-8108) — a dated Work-plan delta
status: active                  # draft → active → superseded | retired (§1.2a) — activated 2026-10-17 on the maintainer's "planned + GO'd now" (2026-10-17 22:51:59 BST); no blocking decision point is open
created: 2026-10-17
owner: planner
tree: 9469721db3d26480824cc1d715da2ec4ca9044d0
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [SL-8108, SL-1543, FR-228, FR-229, FR-230, FR-231, FR-234, FR-235]
---

# PL-8107 — WK-1178: a rate table refuses a non-finite decimal as a named FR-234 issue (SL-8108)

> **For agentic workers:** a **dated Work-plan delta** under Lean P2 L5 (`document-ids.md`
> §1.6, PL row). It carries one fix slice, SL 8108 (roadmap row under WK-1178). The executor
> is spawned from `.claude/roles/executor.md` and binds `test-driven-development`,
> `python-test`, `python-package`, `dev-commands` and `git-hygiene`. Its ledger is
> **LG 8109**, filed by the executor at build; this plan names it and does not create it.

Written 2026-10-17 22:59 BST by the planner (seat planner-8107) on the lead's brief
`brief-planner-8107-2026-10-17.md`. Evidence read at `origin/main` `9469721d`. Every
`file:line` below is at that tree. Working ids PL 8107, SL 8108, LG 8109 are the lead's
(`eta.md` entry 22:52:26, as the brief relays it). The finding is FD 8106 (filed in D21).

## The ruling this plan carries out

The maintainer, `to-lead.md` entry "2026-10-17 22:51:59 BST — Maintainer: FD 8106 → HIGH
(verified by me); its own fix slice in P2, scheduled after the G2 path", verbatim in part:

> "VERIFIED: origin/main operations.py:306-313 catches only InvalidOperation around
> Decimal(raw). A stdlib probe (python3 -I): Decimal accepts "NaN", "sNaN", "Infinity",
> "-Infinity"; a NaN comparison RAISES InvalidOperation (uncaught at :314/:322 → a 500);
> Infinity compares fine (passes an unbounded or one-sided column). There is no is_finite
> check under rate_tables or model-schema src."
>
> "FIX: its OWN small slice in P2 (before the 4 Nov code freeze), planned + GO'd now, gated
> AFTER the G2 path (SL 8099 → SL-1543). Scope:
> - refuse non-finite at the PARSE point(s): validate_rate_table (:307) AND _index_rows
>   (:393) and any other Decimal(raw) on rate-table input (the seat greps and lists them),
>   returning the existing named issue with a clear message ("value … is not a finite
>   decimal number");
> - red-first with the 4 strings, each refused, plus NaN with bounds giving a named issue
>   (not a 500);
> - also check whether stored tables on the seed/demo hold any non-finite value (expected
>   none).
> No spec change unless FR-234's text says otherwise (the seat reads it)."

## Goal

No rate-table value that is NaN, sNaN, `Infinity` or `-Infinity` (any case, any sign) is
ever saved. Each is refused as FR-234's existing `OUT_OF_BOUNDS` issue with the message
`value '<raw>' for key <key> is not a finite decimal number`, on every save path, for an
unbounded, a one-sided and a two-sided value column. A NaN never reaches a bounds
comparison, so the uncaught `InvalidOperation` (a 500) cannot happen.

## The parse-site census — `Decimal(` under `rate_tables/`, at `9469721d`

Predicate, verbatim: `git -C <wt> grep -n 'Decimal(' -- packages/pricing-core/src/pricing_core/rate_tables`.
Every hit, with its verdict:

| Site | What it parses | Verdict |
|---|---|---|
| `operations.py:307` `_value_issue` | a cell value on every save: import (`_checked_import` → `validate_rate_table` :953), seed (`seed_from_model` → :252), bulk operations (`_validate_result` :554), manual edits (`apply_cell_edits` :590, which runs `_value_issue`) | **The fix.** The finite check goes here, before the bounds compare. |
| `operations.py:393` `_index_rows` | a stored cell value, for every diff (`_diff_cells` :414–415, so `diff_cells`, `diff_vs_previous`, `diff_vs_seed`) | **The fix (hardening).** Same predicate, same message, raised as `ValueError("OUT_OF_BOUNDS: …")`; reachable only on a row stored before this slice (DP-1). |
| `operations.py:166` `extract_relativity_table` | a fitted relativity, `Decimal(str(float))` — `inf`/`nan` become `Infinity`/`NaN` | Covered: `seed_from_model` validates the result at :252, which is the :307 fix. Test it (Acceptance 2c). |
| `operations.py:673` `_transform_rows`, `:740` `uplift_by_filter`, `:812`/`:819` `rebase_to_level` | stored cell values | Covered: inputs were validated at save, and each operation's result is validated by `_validate_result` (:554 → :307), so a non-finite result (e.g. a NaN percentage from a Python caller) is refused there. No change. |
| `operations.py:428` (`raw_weight`), `weights.py:219–220` | portfolio exposure weights, not rate-table input | Out of scope: `03` §4.8's `exposure_years` read refuses NaN/infinite already (`docs/specs/03-rating-engine.md:711`). |
| `operations.py:479`, `:481`, `:712`, `:734`, `:821` | constants and arithmetic | Not a parse. |

The API inputs to the bulk operations (`percentage`, `floor`, `cap`) are `DecimalStr`
(`packages/model-schema/src/model_schema/rating.py:1240`, `:1248`, `:1257–1258`); the value
bounds `min`/`max` are `SchemaDecimal` (`rating.py:1084–1085`), whose string pattern
`_DECIMAL_STRING_PATTERN` (`money.py:73`) refuses `NaN`, `sNaN`, `Infinity` and
`-Infinity` (probed with `re.match` at this tree: only `1.5` of the six strings tried
matched). The hole is `RateTableCell` (`rating.py:1088`), `RootModel[dict[str, str]]`: a
cell value is an unpatterned string. **Not verified here:** whether a JSON *number* bound
(e.g. `1e999`) reaches `min`/`max` as `Infinity`. It is out of this slice's scope; if the
executor sees it, it is reported as a finding, not fixed here.

## FR-234 — the text, and why there is no spec change

FR-234 (`docs/specs/03-rating-engine.md:127`), verbatim: *"Rate tables validate on save:
complete coverage of the declared key domain (or an explicit default row), no null values,
values within declared bounds, and no key duplication."* It names no issue messages, so the
new message needs no text change. The issue codes are the code's (`operations.py:66–67`,
`NULL_VALUE`, `OUT_OF_BOUNDS`) and the spec's 422 mapping (`03` §5.1, `:1040`: *"FR-234's
`NULL_VALUE` and `OUT_OF_BOUNDS` under code `RATE_TABLE_INCOMPLETE`"*) is unchanged.

**The existing text is "is not a decimal number"** (`operations.py:311`, the
`InvalidOperation` branch). **"is not a finite decimal number" does not exist** at this
tree (`git grep -n 'not a finite' -- backend frontend packages docs`: no hit). This plan
**keeps** :311's message for a string that does not parse, and **adds** "is not a finite
decimal number" for one that parses to a non-finite value. The ruling quotes the second
text, and two messages tell the actuary which fault they have. No test asserts :311's text
(`git grep -n 'not a decimal number'` hits only `operations.py:311`), so nothing else moves.

**Why the refusal stands on the spec without an amendment:** `03` §4.2 says *"Values are
stored as decimal strings, never JSON floats (R2)"* (`:391`) and `RateTableCell` is *"each
value a string (a key level or a decimal string)"* (`:475`). `NaN` and `Infinity` are not
decimal strings, and `CLAUDE.md` §7 puts the rating path on Decimal money. For an
**unbounded** column, "within declared bounds" is vacuous, so the refusal of `Infinity`
there rests on §4.2's "decimal string", not on FR-234's bounds clause. The ruling says no
spec change unless FR-234's text requires one; it does not. DP-2 records the optional
clarifying amendment and recommends against it.

## Design constraints (each is a review item)

1. **One predicate, one message format.** `Decimal.is_finite()` is the test. A small helper
   in `operations.py` serves :307 and :393 so the two sites cannot diverge. The message is
   exactly `f"value {raw!r} for key {key_values} is not a finite decimal number"`, with the
   `raw!r` and key form :311 already uses.
2. **Before the bounds.** In `_value_issue` the finite check runs immediately after the
   `Decimal(raw)` parse and before the `min`/`max` compares (:314, :322), so a NaN is never
   compared.
3. **The same code.** `OUT_OF_BOUNDS`, `field=value.name`. No new issue code, no new error
   code, no route change, no contract change (`generate-contracts.py --check` stays rc 0).
4. **sNaN.** `Decimal("sNaN")` parses without a signal and `is_finite()` is `False` without
   one; the check needs no `localcontext`. A test pins this.
5. **No pandas, no float.** The check is on the `Decimal`; nothing converts through `float`.
6. **Case and sign.** `Decimal` accepts `"nan"`, `"NAN"`, `"-NaN"`, `"inf"`, `"+Infinity"`.
   The four strings the ruling names are the required cases; the test adds `"inf"` and
   `"-nan"` so a case-sensitive string compare cannot pass for `is_finite()`.

## Decision points

None is blocking; the plan builds each recommendation.

- **DP-1 — a diff over a row stored before this slice.** After the fix no save stores a
  non-finite value, so :393 meets one only on a legacy row. (a) **Recommended:** :393 raises
  the named `ValueError("OUT_OF_BOUNDS: …")`; the backend diff routes are unchanged
  (`backend/src/app/platform/rate_tables.py:537–543`, `:608`, `:1057` do not catch it, so a
  legacy row still answers 500, now with a named cause in the log). The census below finds
  no such row in any committed table. (b) Map it in the diff routes to a 422: a §5.1
  change on three routes and a backend test on the DB lane, for a state no committed table
  has. Rejected for this slice; a finding if a live database census ever finds a row.
- **DP-2 — a clarifying FR-234 amendment ("each value a finite decimal").** (a)
  **Recommended:** none, per the ruling; §4.2 already carries it. (b) A one-line dated
  amendment to FR-234. The lead may order (b); it would be a `spec-change` hunk in the same
  PR, nothing else.

## Acceptance Standard

1. **Red first (i).** The first commit adds the tests below to
   `packages/pricing-core/tests/test_rate_table_operations.py`, with no code change. Run
   through `~/gi-pricing-plan.local/handover/run-small.sh` on that one file, they are red:
   the unbounded and one-sided `Infinity` cases return no issue, and NaN-with-bounds raises
   `decimal.InvalidOperation`. LG 8109 records the rc, the FAILED lines verbatim, the commit
   sha and the tree.
2. **The tests (i)**, each with `@pytest.mark.req("FR-234")`:
   (a) parametrised over `"NaN"`, `"sNaN"`, `"Infinity"`, `"-Infinity"` (plus `"inf"`,
   `"-nan"`, constraint 6) × three columns (unbounded; `min` only; `min` and `max`):
   `validate_rate_table` returns exactly one issue for the row, `code == OUT_OF_BOUNDS`,
   `field` the value name, and the message ends `is not a finite decimal number`;
   (b) NaN with bounds is that named issue and raises nothing (`pytest.raises` is not used;
   the call returns);
   (c) `seed_from_model` on a model whose relativity is `float("inf")` and one whose is
   `float("nan")` raises `ValueError` starting `OUT_OF_BOUNDS:` (the :166 → :252 path);
   (d) `apply_cell_edits` with a `"NaN"` edit returns an `EditIssue` with `OUT_OF_BOUNDS`
   (the manual-edit path);
   (e) `import_from_csv` with an `Infinity` cell raises `ValueError` starting
   `OUT_OF_BOUNDS:` (the import path);
   (f) `uplift_table` with `percentage=Decimal("NaN")` raises `ValueError` starting
   `OUT_OF_BOUNDS:` (a bulk operation, via `_validate_result`);
   (g) `diff_cells` with a baseline cell `"NaN"` raises `ValueError` starting
   `OUT_OF_BOUNDS:` and containing `not a finite decimal number` (the diff path, :393);
   (h) a string that does not parse (`"abc"`) still gives :311's `is not a decimal number`.
   Where a case's existing fixture builder in that file does not reach the function, the
   executor builds the smallest one in the file; no new test file.
3. **Green.** The same run-small on the same file: rc 0. The full file passes.
4. **The census (ii)** is re-run at the build's base (command below) and its output line
   goes into LG 8109 verbatim: `0 non-finite`. Any non-zero count is a STOP and a report.
5. **Spec (iii).** No `docs/specs/` hunk unless the lead rules DP-2 (b). If it does, the
   hunk is FR-234's dated amendment only and `python3 scripts/audit-docs.py` runs on it.
6. **Gate.** One full gate (both halves, `dev-commands`) on a free slot **after SL-1543
   merges**, when the lead grants it. Both halves rc 0; `audit-docs.py` rc 0 apart from the
   id-state reds the lead classes. `generate-contracts.py --check` rc 0 (constraint 3).

## The seed/demo census (ii) — at `9469721d`, run 2026-10-17 before the 22:59:10 BST clock read

Committed rate tables: the 18 files `examples/**/*.rate-table.*.json` (all under
`examples/fremtpl2/rating/`). The command, verbatim (a script in the seat's scratchpad,
run as `python3 -I census.py <wt>`):

```python
import json, sys, glob
from decimal import Decimal
fs = sorted(glob.glob(sys.argv[1] + "/examples/**/*.rate-table.*.json", recursive=True))
n = bad = 0
for f in fs:
    d = json.load(open(f)); v = d["value"]["name"]
    rows = list(d["rows"]) + ([d["default_row"]] if d.get("default_row") else [])
    for b in ("min", "max"):
        if d["value"].get(b) is not None and not Decimal(str(d["value"][b])).is_finite(): bad += 1; print("NONFINITE bound", f, b)
    for r in rows:
        n += 1
        if not Decimal(str(r[v])).is_finite(): bad += 1; print("NONFINITE", f, r)
print(len(fs), "files", n, "value cells", bad, "non-finite")
```

Output, verbatim: `18 files 3552 value cells 0 non-finite` (rc 0).

The **demo seeding** does not read these files: `examples/fremtpl2/seed.py:712–725` calls
`seed_demo_rate_tables` (`examples/fremtpl2/model.py:445`), which seeds each table with
`seed_from_model` from the fitted GLM (FR-230). Those tables are computed at seed time, so
the guard for them is :252's validation, which Acceptance 2(c) tests. A census of the
tables **stored in a live database** is a DB-lane action and is not in this slice; the lead
may grant it, and a hit is a STOP.

## Tasks

1. **Red first.** Add Acceptance 2's tests; no code change. Run them (Acceptance 1): red.
   Commit. Record in LG 8109.
2. **The fix.** The helper and the two sites (constraints 1–4). Run (Acceptance 3): green.
   Commit.
3. **Census and gate.** Re-run the census (Acceptance 4); the gate when granted after
   SL-1543 merges (Acceptance 6). Close the LG 8109 entry.

## Sequencing

SL 8099 (minting as SL-1773) → SL-1543 → **SL 8108**. SL 8108 may be built and run its
small runs at any time; its gate waits for SL-1543's merge (the ruling's order). It edits
`rate_tables/operations.py` and one test file only; no G2-path slice touches either at
`9469721d` (SL 8099's change set, `git diff --stat origin/main...origin/sl-8099-glm-scalar-predict`,
is under `modelling/`, `rating/runtime.py` and its own tests).

## Self-review before freeze

- Every acceptance item is a command or a recorded run.
- Every `Decimal(` hit under `rate_tables/` is listed with a verdict; none is a range.
- The message text the plan uses, and why the old one stays, are stated with their sources.
- No spec, contract, route or migration change; DP-1 and DP-2 name what would change one.
- FD 8106 is cited in prose only and is not in `relates:` (the maintainer, 22:41:59).
