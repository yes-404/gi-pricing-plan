---
id: PL-8107
family: plan
kind: map
title: WK-1178 — a rate table refuses a non-finite decimal (NaN, sNaN, ±Infinity) as a named FR-234 issue, never a 500 (SL-8108) — a dated Work-plan delta
status: active                  # draft → active → superseded | retired (§1.2a) — activated 2026-10-17 on the maintainer's "planned + GO'd now" (2026-10-17 22:51:59 BST), re-cut spec-first on the 22:56:37 BST confirmation; no decision point is open
created: 2026-10-17
owner: planner
tree: 9469721db3d26480824cc1d715da2ec4ca9044d0
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [SL-8108, SL-1543, FR-228, FR-229, FR-230, FR-231, FR-233, FR-234, FR-235]
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
**Re-cut 2026-10-17 23:04 BST** by the same seat, before any merge, spec-first, on the
maintainer's 22:56:37 BST confirmation (next section); the first cut is at `98942ea5`.

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

## The confirmation: spec first

The maintainer, `to-lead.md` entry "2026-10-17 22:56:37 BST — Maintainer: FD 8105 widened
to the datasets upload; FR-234 amendment FIRST for FD 8106 confirmed", Correction 3,
verbatim:

> "FR-234 says nothing about finiteness, so the dated FR-234 amendment comes FIRST in
> PL 8107 (spec-first), carrying the rule + the issue text; the code follows in the same
> slice commit."

This supersedes the plan's first cut (pushed at `98942ea5`, unmerged), which read FR-234 as
needing no change. The same entry's "Correction 2 is noted" is the lead's relay of FD 8106's
line correction: `RateTableValue.min`/`max` are at `rating.py:1084–1085` (class at :1076),
not :1104–1105 as the brief said. This plan cites :1084–1085 throughout.

## Goal

FR-234 states, first, that every rate-table value is a finite decimal. Then the code
enforces it. No value that is NaN, sNaN, `Infinity` or `-Infinity` (any case, any sign) is
ever saved. Each is refused as FR-234's existing `OUT_OF_BOUNDS` issue with the message
`value '<raw>' for key <key> is not a finite decimal number`, on every save path, for an
unbounded, a one-sided and a two-sided value column. A NaN never reaches a bounds
comparison, so the uncaught `InvalidOperation` (a 500) cannot happen.

## The FR-234 amendment — the rule and the issue text (the slice's first hunk)

FR-234 (`docs/specs/03-rating-engine.md:127`), verbatim at `9469721d`: *"Rate tables
validate on save: complete coverage of the declared key domain (or an explicit default
row), no null values, values within declared bounds, and no key duplication."* It names
null, bounds, coverage and duplicates, and says nothing about finiteness (FD 8106 (filed in
D21), its "FR-234" section). For an unbounded column "within declared bounds" is vacuous, so
a refusal of `Infinity` there is a new rule. Per `CLAUDE.md` §0 it goes into the spec first.

**The hunk.** One dated amendment clause, appended to the end of FR-234's Requirement cell
on `:127` (the suite's form: FR-240's *"(Amended 2026-10-17, WK-1178, SL-1761, FD-1753
(HIGH): …)"*). The row keeps its id; nothing is renumbered (`spec-change`, append-only).
The executor writes it **verbatim**, with these two adjustments only: the working ids are
left in space form until the mint re-points them, and the date is the build's date if it is
not 2026-10-17:

> *(Amended 2026-10-17, WK-1178, SL 8108, FD 8106 (HIGH), on the maintainer's entries
> "2026-10-17 22:51:59 BST" and "2026-10-17 22:56:37 BST": **every value is a finite
> decimal.** A value that parses as a decimal but is not finite (`NaN`, `sNaN`, `Infinity`
> or `-Infinity`, in any case and with any sign) is refused on save with `OUT_OF_BOUNDS`
> and the message "value '<raw>' for key <key> is not a finite decimal number", whether or
> not the value column declares bounds. A non-finite value is never compared with a bound.
> A value that does not parse as a decimal keeps the message "value '<raw>' for key <key>
> is not a decimal number". The rule applies on every path that saves a Rate Table Version:
> import (FR-235), seeding from a model (FR-230), the bulk operations (FR-233) and manual
> edits (FR-229).)*

**The issue text, both cases** (code `OUT_OF_BOUNDS`, `field` the value column's name):

| Case | Message |
|---|---|
| parses, not finite (new) | `value '<raw>' for key <key> is not a finite decimal number` |
| does not parse (existing, `operations.py:311`, unchanged) | `value '<raw>' for key <key> is not a decimal number` |

`'<raw>'` is Python's `repr` of the raw string and `<key>` the key tuple, exactly as :311
formats them. "is not a finite decimal number" does not exist at this tree
(`git grep -n 'not a finite' -- backend frontend packages docs`: no hit). No test asserts
:311's text (`git grep -n 'not a decimal number'` hits only `operations.py:311`), so nothing
else moves.

**What does not change in the spec.** The issue codes stay the code's (`operations.py:66–67`,
`NULL_VALUE`, `OUT_OF_BOUNDS`). The 422 mapping stays as written (`03` §5.1, `:1040`:
*"FR-234's `NULL_VALUE` and `OUT_OF_BOUNDS` under code `RATE_TABLE_INCOMPLETE`"*). No
glossary term is new (`00` §2). §4.2's "decimal strings" (`:391`, `:475`) is consistent with
the amendment and is not edited. No §10 open question is raised or closed.

**One commit on main.** The amendment, the tests and the code land as one commit
(`CLAUDE.md` §2). The branch may carry the red-first commit separately (Acceptance 1). The
squash-merge makes the slice one commit on main. If the lead reads "the same slice commit"
as one commit on the branch too, the executor squashes locally before the PR and records
the red run's sha in LG 8109 before it squashes.

## The parse-site census — `Decimal(` under `rate_tables/`, at `9469721d`

**The scope is FD 8106's list** (its Evidence section; predicate verbatim there:
`git grep -n 'Decimal(' origin/main -- packages/pricing-core/src/pricing_core/rate_tables`):
`operations.py` :166, :307, :393, :428, :479, :481, :673, :712, :734, :740, :812, :819;
`weights.py` :219, :220. The same predicate run in this worktree also hits `operations.py:821`
(`quotient != Decimal(1)`), a constant, not a parse. FD 8106's list leaves it out, and that
does not change the scope. Every site, with its verdict:

| Site | What it parses | Verdict |
|---|---|---|
| `operations.py:307` `_value_issue` | a cell value on every save: import (`_checked_import` → `validate_rate_table` :953), seed (`seed_from_model` → :252), bulk operations (`_validate_result` :554), manual edits (`apply_cell_edits` :590, which runs `_value_issue`) | **The fix.** The finite check goes here, before the bounds compare. |
| `operations.py:393` `_index_rows` | a stored cell value, for every diff (`_diff_cells` :414–415, so `diff_cells`, `diff_vs_previous`, `diff_vs_seed`) | **The fix (hardening).** Same predicate, same message, raised as `ValueError("OUT_OF_BOUNDS: …")`; reachable only on a row stored before this slice (DP-1). |
| `operations.py:166` `extract_relativity_table` | a fitted relativity, `Decimal(str(float))`: `inf`/`nan` become `Infinity`/`NaN` | Covered: `seed_from_model` validates the result at :252, which is the :307 fix. Tested (Acceptance 3c). |
| `operations.py:673` `_transform_rows`, `:740` `uplift_by_filter`, `:812`/`:819` `rebase_to_level` | stored cell values | Covered: inputs were validated at save, and each operation's result is validated by `_validate_result` (:554 → :307), so a non-finite result is refused there; a NaN percentage never reaches it, because `UpliftTableParameters.percentage` (`DecimalStr`) refuses a non-finite percentage first (corrected 2026-10-18 on the maintainer's to-lead 2026-10-18 04:37:16 BST). No change. |
| `operations.py:428` (`raw_weight`), `weights.py:219–220` | portfolio exposure weights, not rate-table input | Out of scope: `03` §4.8's `exposure_years` read refuses NaN/infinite already (`docs/specs/03-rating-engine.md:711`). |
| `operations.py:479`, `:481`, `:712`, `:734` (and `:821`) | constants and arithmetic | Not a parse. |

The API inputs to the bulk operations (`percentage`, `floor`, `cap`) are `DecimalStr`
(`packages/model-schema/src/model_schema/rating.py:1240`, `:1248`, `:1257–1258`); the value
bounds `min`/`max` are `SchemaDecimal` (`rating.py:1084–1085`), whose string pattern
`_DECIMAL_STRING_PATTERN` (`money.py:73`) refuses `NaN`, `sNaN`, `Infinity` and
`-Infinity` (probed with `re.match` at this tree: of the six strings tried, only `1.5`
matched). The hole is `RateTableCell` (`rating.py:1088`), `RootModel[dict[str, str]]`: a
cell value is an unpatterned string. **Not verified here:** whether a JSON *number* bound
(e.g. `1e999`) reaches `min`/`max` as `Infinity`. It is outside this slice's scope; if the
executor sees it, it is reported as a finding, not fixed here.

## Design constraints (each is a review item)

1. **Spec first.** The FR-234 hunk above is written before any code or test. Every test
   below carries `@pytest.mark.req("FR-234")`.
2. **One predicate, one message format.** `Decimal.is_finite()` is the test. A small helper
   in `operations.py` serves :307 and :393 so the two sites cannot diverge. The message is
   exactly `f"value {raw!r} for key {key_values} is not a finite decimal number"`, with the
   `raw!r` and key form :311 already uses.
3. **Before the bounds.** In `_value_issue` the finite check runs immediately after the
   `Decimal(raw)` parse and before the `min`/`max` compares (:314, :322), so a NaN is never
   compared.
4. **The same code.** `OUT_OF_BOUNDS`, `field=value.name`. No new issue code, no new error
   code, no route change, no contract change (`generate-contracts.py --check` stays rc 0).
5. **sNaN.** `Decimal("sNaN")` parses without a signal and `is_finite()` is `False` without
   one; the check needs no `localcontext`. A test pins this.
6. **No pandas, no float.** The check is on the `Decimal`; nothing converts through `float`.
7. **Case and sign.** `Decimal` accepts `"nan"`, `"NAN"`, `"-NaN"`, `"inf"`, `"+Infinity"`.
   The four strings the ruling names are the required cases. The test adds `"inf"` and
   `"-nan"` so that a case-sensitive string compare cannot pass where `is_finite()` does.

## Decision points

None is open or blocking.

- **DP-1 — a diff over a row stored before this slice.** After the fix no save stores a
  non-finite value, so :393 meets one only on a legacy row. (a) **Recommended, and built:**
  :393 raises the named `ValueError("OUT_OF_BOUNDS: …")`; the backend diff routes are
  unchanged (`backend/src/app/platform/rate_tables.py:537–543`, `:608`, `:1057` do not catch
  it, so a legacy row still answers 500, now with a named cause in the log). The census
  below finds no such row in any committed table. (b) Map it in the diff routes to a 422: a
  §5.1 change on three routes and a backend test on the DB lane, for a state no committed
  table has. Rejected for this slice; a finding if a live database census ever finds a row.
  The FR-234 amendment covers saves only, so (a) does not contradict it.
- **DP-2 — the FR-234 amendment. Ruled:** spec first, by the maintainer, 22:56:37 (above).
  The first cut's recommendation of no amendment is withdrawn.

## Acceptance Standard

1. **Spec first (iii).** The branch's first commit carries the FR-234 amendment verbatim (the
   section above) and the tests (item 3), with no code change. `python3 scripts/audit-docs.py`
   (gate-2 flock) shows no new red beyond the id-state reds the lead classes.
2. **Red first (i).** On that commit, run through
   `~/gi-pricing-plan.local/handover/run-small.sh` on the one test file, the tests are red:
   the unbounded and one-sided `Infinity` cases return no issue, and NaN-with-bounds raises
   `decimal.InvalidOperation`. LG 8109 records the rc, the FAILED lines verbatim, the commit
   sha and the tree.
3. **The tests (i)**, in `packages/pricing-core/tests/test_rate_table_operations.py`, each
   with `@pytest.mark.req("FR-234")`:
   (a) parametrised over `"NaN"`, `"sNaN"`, `"Infinity"`, `"-Infinity"` (plus `"inf"`,
   `"-nan"`, constraint 7) × three columns (unbounded; `min` only; `min` and `max`):
   `validate_rate_table` returns exactly one issue for the row, `code == OUT_OF_BOUNDS`,
   `field` the value name, and the message ends `is not a finite decimal number`;
   (b) NaN with bounds is that named issue and raises nothing (the call returns);
   (c) `seed_from_model` on a model whose relativity is `float("inf")`, and on one whose is
   `float("nan")`, raises `ValueError` starting `OUT_OF_BOUNDS:` (the :166 → :252 path);
   (d) `apply_cell_edits` with a `"NaN"` edit returns an `EditIssue` with `OUT_OF_BOUNDS`
   (the manual-edit path);
   (e) `import_from_csv` with an `Infinity` cell raises `ValueError` starting
   `OUT_OF_BOUNDS:` (the import path);
   (f) replaced by the green pin `test_a_bulk_operation_cannot_be_given_a_non_finite_percentage`:
   `UpliftTableParameters.percentage` (`DecimalStr`) refuses a non-finite percentage before
   `_validate_result` is reached (corrected 2026-10-18 on the maintainer's to-lead 2026-10-18 04:37:16 BST);
   (g) `diff_cells` with a baseline cell `"NaN"` raises `ValueError` starting
   `OUT_OF_BOUNDS:` and containing `not a finite decimal number` (the diff path, :393);
   (h) a string that does not parse (`"abc"`) still gives :311's `is not a decimal number`.
   Where a case's existing fixture builder in that file does not reach the function, the
   executor builds the smallest one in the file; no new test file.
4. **Green.** After the code commit, the same run-small on the same file: rc 0. The full
   file passes.
5. **The census (ii)** is re-run at the build's base (command below) and its output line
   goes into LG 8109 verbatim: `0 non-finite`. Any non-zero count is a STOP and a report.
6. **One commit on main.** The PR's squash carries the FR-234 hunk, the tests and the code
   together (`CLAUDE.md` §2). No other `docs/specs/` hunk.
7. **Gate.** One full gate (both halves, `dev-commands`) on a free slot **after SL-1543
   merges**, when the lead grants it. Both halves rc 0; `audit-docs.py` rc 0 apart from the
   id-state reds the lead classes; `req-coverage.py` shows FR-234 covered;
   `generate-contracts.py --check` rc 0 (constraint 4).

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
the guard for them is :252's validation, which Acceptance 3(c) tests. A census of the
tables **stored in a live database** is a DB-lane action and is not in this slice; the lead
may grant it, and a hit is a STOP.

## Tasks

1. **Spec first, red first.** Write the FR-234 amendment verbatim (`spec-change`), then the
   tests (Acceptance 3); no code change. Run the docs check (Acceptance 1) and the tests
   (Acceptance 2): red. Commit. Record both in LG 8109.
2. **The fix.** The helper and the two sites (constraints 2–5). Run (Acceptance 4): green.
   Commit.
3. **Census and gate.** Re-run the census (Acceptance 5); the gate when granted after
   SL-1543 merges (Acceptance 7). Close the LG 8109 entry. The PR squashes to one commit
   (Acceptance 6).

## Sequencing

SL 8099 (being minted, not yet on main) → SL-1543 → **SL 8108**. SL 8108 may be built and run its
small runs at any time; its gate waits for SL-1543's merge (the ruling's order). It edits
`rate_tables/operations.py` and one test file only; no G2-path slice touches either at
`9469721d` (SL 8099's change set, `git diff --stat origin/main...origin/sl-8099-glm-scalar-predict`,
is under `modelling/`, `rating/runtime.py` and its own tests).

## Self-review before freeze

- The spec hunk comes first and is written out verbatim, with the issue text for both cases.
- Every acceptance item is a command or a recorded run.
- Every `Decimal(` hit under `rate_tables/` (FD 8106's list, plus :821) is listed with a
  verdict; none is a range.
- No contract, route or migration change; DP-1 names what would change a route.
- `RateTableValue.min`/`max` are cited at `rating.py:1084–1085`, not the brief's :1104–1105.
- FD 8106 is cited in prose only and is not in `relates:` (the maintainer, 22:41:59).
