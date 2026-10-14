---
id: PL-8042
family: plan
kind: map
title: WK-1178 — FD 8040's two limbs, a recipe cell that does not parse is never silently nulled and validation gives it a verdict (FR-32, VR-STR-2), SL-8043 — a dated Work-plan delta
status: draft                  # draft → active → superseded | retired (§1.2a)
created: 2026-10-14
owner: planner
tree: a3fc2e8dd384de6abf909f662f43011b8078fb4e
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1542, SL-1543]
---

# PL-8042 — WK-1178: FD 8040, silent coercion. A recipe cell that does not parse is never silently nulled, and validation gives it a verdict (SL-8043)

> **For agentic workers:** this is a **dated Work-plan delta** under Lean P2 L5
> (`document-ids.md` §1.6, PL row: *"one plan per Work, slices as rows, no per-slice `leaf`; a
> change is one dated Work-plan delta, a new `PL-` that `relates:` the Work's plan"*). WK-1178
> has no Work plan, so, as for `PL-1674` and PL 8030, this delta `relates:` the records it
> touches: `PL-1542` and `SL-1543` (A-4, the G2 path, whose seed ingest runs a recipe and whose
> fixture once relied on the nulling this plan removes). It adds **one slice row**, SL-8043
> (working id), under `### WK-1178` in [`../roadmap.md`](../roadmap.md). REQUIRED SUB-SKILL:
> subagent-driven-development (recommended) or executing-plans, task by task. Steps use
> checkbox (`- [ ]`) syntax. The executor also binds:
> - `test-driven-development`: every red below is seen red **by its cause** on main, through
>   the real Job path, before the code that turns it green;
> - `python-test`: the `req` marker and the negative tests;
> - `python-package`: `pricing-core` stays standalone (ADR-703); it never raises
>   `PlatformError`;
> - `spec-change`: Task 3;
> - `dev-commands`: `uv sync --all-packages`, `scripts/run-small.sh` for one-file runs, and both
>   gate halves;
> - `git-hygiene`.
>
> Read [`README.md`](README.md)'s five unchecked conventions before the first step. The executor
> is spawned from `.claude/roles/executor.md`.

Filed under **working id 8042**. Its slice row is **working id 8043** (`draft`). Both were
reserved to this planner by the lead (team-lead to planner-fd8040, 2026-10-14: *"The ids are
RESERVED to you"*). Written 2026-10-14 by the planner (seat planner-fd8040).
**Tree read:** `origin/main` `a3fc2e8dd384de6abf909f662f43011b8078fb4e` (committed
2026-10-14T11:55:40+01:00). Every `file:line` below is at that tree. The executor re-reads each
one at its base (Task 0). The finding is **FD 8040** (working id), filed by auditor-upload404 on
`fd-8039-upload-404-2026-10-14`; that branch was not on `origin` when this plan was written
(`git ls-remote --heads origin` listed no `fd-8039` or `fd-8040` head), so the finding's text is
taken from the lead's report and the maintainer's ruling below, and Task 0 re-reads the FD once
it is pushed.

## Authority

All three entries are the maintainer's (by delegation), in `to-lead.md`, read in full after
they were logged. The third rules this plan's decision points.

- **"2026-10-14 11:52:51 BST — PL 8030/SL 8031 DPs ruled; SL-1543 fixture fix accepted; NEW
  candidate: the recipe cast silently nulls unparseable values (re lead 11:51:03 / 11:52:02)"**,
  item (1), quoted in full (items (2) to (4) are not this plan's):
  > **(1) SL-1543: fixture cause ACCEPTED** (test_demo_peril_structure.py:81 wrote "np.float64(…)"); fix-forward @f52906ac, with no force-push. R1b criterion 4 (the cross-case discrimination run and the second silent-drop red) is owed as printed RUNS before the GO, as you ordered.
  > **BUT the mechanism is a candidate finding:** `packages/pricing-core/src/pricing_core/data/prepare.py:136` casts with `strict=False` (and :142 parses dates with `strict=False`), so an UNPARSEABLE cell becomes null with no error. That is exactly how 63/63 values vanished silently here. 01 FR-32: "Rows that cannot be parsed at all … are **rejected to a quarantine table** … rather than dropped silently"; 01 VR-STR-2: "no silent coercion". **Auditor RUN, read-only:** ingest a CSV whose declared-numeric column has one unparseable cell ("np.float64(3.0)", "12,5", "n/a") and one declared-date column with a bad date, through the real recipe path. Read: the validation report (does any check count or flag the coerced cells?), the quarantine table, and the resulting nulls. If the value silently becomes null with no report entry → an FD, proposed HIGH (silent data change feeding pricing models), owner WK-1178, fixed in P2. The fix's DESIGN (refuse vs quarantine vs a counted coercion with a validation verdict) is a planner DP against FR-32/VR-STR-2. Send me the output.
- **"2026-10-14 12:02:46 BST — FD 8040 (silent coercion) → HIGH CONFIRMED, remedy must make
  VALIDATION see it; PL 8002 hand-off (b) ADOPTED; tidy OK; SL-1695 gate result OWED (re lead
  12:02:15)"**, item (1), quoted in full (items (2) to (4) are not this plan's):
  > **(1) FD 8040 → HIGH, CONFIRMED** on the run (tree a3fc2e8d): 4 bad cells → ingest `succeeded` 4/4/0, no `_rejected` table, exactly 4 nulls written, then dataset.validate PASSED 5/5 approved rules. 01 FR-32 and VR-STR-2 are unmet on the production ingest path. Bad source data reaches pricing models as silent nulls, with a "validated" version on top. Owner WK-1178, fixed in P2.
  > **The remedy has TWO limbs, both in scope, and the design DP is the planner's (refuse / quarantine / counted coercion):**
  > - (a) **the coercion:** prepare.py:136/:142 `strict=False`; the Job handler (data_handlers.py:140) never passes `required_non_null`;
  > - (b) **the blind validation:** dtype_match passes by construction after the cast, date_parsed checks type only, range ignores nulls, and reject_rate reads an always-empty `_rejected`. Whatever the design, a coerced cell must produce a validation VERDICT (a counted check, fail or warn per its declaration) so the version cannot read "validated" over a silent change.
  > Reds by run through the real Job path, both limbs red on main by cause (the auditor's 4-row input is the fixture).
- **"2026-10-14 12:23:36 BST — PL 8042/SL 8043 (FD 8040 fix) DPs RULED: C1 → Q (quarantine), C3
  → (ii), C2 → (a) (re lead 12:23:06)"**, quoted in full:
  > - **DP-C1 → (Q) QUARANTINE the row** (source text into `PreparationResult.rejected` → the version's `_rejected` table with `_reject_column` / `_step` / `_reason`; counted in `rows_rejected`). It builds 01 FR-32's own mechanism, which already exists unfilled (the `_rejected` table 01:285, its endpoint :874, the drawer :1046, VR-STR-9, `prepare.py:85`'s declared `.rejected` field). (R) is refused: it contradicts FR-32 ("a version with rejects can still be validated") and gives no version to judge. (C) is refused: the null still reaches modelling. The quarantine must be COMPLETE for each row (no partially cast row written), and `rows_read == rows_written + rows_rejected` is asserted.
  > - **DP-C3 → (ii):** `reject_rate` PLUS `dtype_match` (VR-STR-2) and `date_parsed` (VR-STR-5) each report `measured.coerced_cells` for the columns they declare (= the cells quarantined because of that column), at their declared severity. This holds even when a rule set omits `reject_rate` (FR-45 does not mandate it). `range`'s null-ignoring is unchanged, but its guard is stated. warn + an FR-46 acknowledgement remains the user's knob, which is the governed path. (iii) tolerance: not now.
  > - **DP-C2 → (a):** no handler change (under Q every coercion is quarantined).
  > - **Reds:** R1–R5 by RUN via `execute_job` with the 4-row fixture + p5 "2024-13-01", each red on main by cause. Plus one assert the old behaviour cannot survive: after ingest, `null_count(claim_amount)` equals the SOURCE's genuine empty cells only (0 for the fixture), never the bad-cell count.
  > - **G2 condition (binding):** Task 0 re-counts through POLARS, with the same cast the recipe uses, over all 678,013 freMTPL2 rows and the seeded 20k. A non-zero count is a STOP to me before code (it would change the A-4/WF-699 seed's rows). The proxy regex count of 0 is noted, not relied on.
  > - The SL 8043 / SL 8031 roadmap adjacency: both go in P1 and are resolved in that one PR. OK.

The evidence is the lead's from-lead entry **"2026-10-14 12:02:15 BST"** (in
`from-lead-2026-10-09.md`), item (1), and the auditor's run it reports,
`/home/puzhenhao1989/.claude/jobs/b6860f8f/tmp/strictfalse/out.txt` with its script `run.py`
beside it, both read in full. The run, at tree `a3fc2e8d`, on a fresh migrated database:

- **Ingest** (`dataset.ingest` Job, the recipe below): `INGEST JOB: succeeded`;
  `INGESTION RUN rows_read/written/rejected: 4 4 0 reject_sample: []`; `VERSION tables:
  ["policy_exposure"]` (no `_rejected`); the parquet's
  `null_count: {'policy_id': 0, 'exposure': 0, 'claim_amount': 2, 'start_date': 2}`, which are
  exactly the four bad cells (p2 and p3).
- **Validate** (`dataset.validate` Job over five approved rules): `VALIDATE JOB: succeeded`;
  `REPORT overall: pass results: 5`. Each rule's measured value:
  `dtype` `{"mismatched_columns": {}}`; `datep` `{"unparsed_columns": {}}`; `cols`
  `{"missing": []}`; `claim-nonneg` `{"violating_rows": 0}`; `reject-rate`
  `{"rows_read": 4, "reject_rate": 0.0, "rejected_rows": 0}`.

## The fixture (the auditor's 4-row input, verbatim from `run.py`)

```python
CSV = (b"policy_id,exposure,claim_amount,start_date\n"
       b"p1,1.0,100.0,2024-01-15\n"
       b"p2,0.5,np.float64(1.0),2024-02-30\n"      # unparseable number + impossible/bad date
       b"p3,1.0,abc,not-a-date\n"                   # unparseable number + unparseable date
       b"p4,0.75,250.5,2024-03-01\n")
RECIPE = [
    {"step": "cast", "params": {"columns": {"claim_amount": "float64"}}},
    {"step": "parse_date", "params": {"column": "start_date", "format": "%Y-%m-%d"}},
]
```

and the five rules (`run.py`, `spec` list), as `(slug, layer, check, severity, target, params)`:

```python
T = {"table": "policy_exposure"}
("dtype", "structural", "dtype_match", "fail", T, {"columns": {"claim_amount": "float64", "start_date": "date"}}),
("datep", "structural", "date_parsed", "fail", T, {"columns": ["start_date"]}),
("cols", "structural", "column_presence", "fail", T, {"columns": ["policy_id", "claim_amount", "start_date"]}),
("claim-nonneg", "actuarial_sanity", "range", "fail", {"table": "policy_exposure", "column": "claim_amount"}, {"min_inclusive": 0, "key_columns": ["policy_id"]}),
("reject-rate", "structural", "reject_rate", "fail", T, {}),
```

**One added row, `p5`, ruled into the fixture** (the 12:23:36 entry: *"the 4-row fixture + p5
"2024-13-01""*). In the auditor's fixture both bad rows also carry a bad number, and the cast
step runs first, so under the quarantine neither row reaches `parse_date` and the 4 rows alone
cannot show a date verdict. **Every red below uses the five rows**: the auditor's four,
verbatim, then

```python
b"p5,1.0,80.0,2024-13-01\n"                       # a good number and a bad date
```

On it: `p2` and `p3` are quarantined by the `cast` step (`claim_amount`), `p5` by the
`parse_date` step (`start_date`); `p1` and `p4` are written. So `rows_read == 5`,
`rows_rejected == 3` and `rows_written == 2`. The source has no genuinely empty cell, so after
ingest `null_count` is 0 in every column.

## Evidence at `a3fc2e8d` (the owning code, read)

**Limb (a), the coercion.**

- `pricing_core/data/prepare.py:134-138`: `cast` is
  `pl.col(column).cast(_dtype(dtype), strict=False)`. `:139-144`: `parse_date` is
  `.str.strptime(pl.Date, params["format"], strict=False)`. A cell that does not parse becomes
  null, with no error and no count. These are the only two `strict=False` steps in
  `_apply_step`.
- `PreparationResult` (`prepare.py:81-86`) **already declares** `rejected: pl.DataFrame | None
  = None`, and `01` §5.2 (`01-data-management.md:952-956`) declares `apply_recipe` as returning
  `.tables, .rejected, .stats`. `apply_recipe` (`prepare.py:89-126`) never sets it: it returns
  `PreparationResult(tables=working, stats=stats)` (`:126`). The quarantine channel the spec
  describes exists in the type and is never filled.
- The source is read **as strings**: `app/data/formats.py:108-122` reads CSV with
  `infer_schema=False` (`:118`) and `null_values=["", "NA", "N/A", "NULL", "null"]` (`:120`).
  So every cell a recipe casts is a `String` before the step, and the only nulls before it are
  the cells the source left empty or wrote as one of those five tokens. A cell that is non-null
  before a `cast`/`parse_date` step and null after it is therefore a coercion, never a source
  null.
- `app/data/ingestion.py:164-178` applies the recipe **before** the reject partition (the
  comment at `:164-166` gives the reason). `:186` calls
  `partition_rejects(frame, required_non_null=required_non_null)`; `:204-211` stores
  `partition.rejected` as the `_rejected` table only when it has rows; `:246-247` and `:267`
  record `rows_rejected` and the sample.
- `partition_rejects` (`pricing_core/data/ingest.py:245-286`) rejects a row only when a
  **required** column is null; with no `required_non_null` it returns every row as clean
  (`:257-261`). Its docstring (`:248-255`) says *"an unparseable date in a required date column
  arrives here as a null, having failed non-strict parsing upstream"*: the design leans on
  `strict=False` and on the caller naming the required columns.
- The Job handler `app/worker/data_handlers.py:140-149` calls `ingest_upload` with `recipe=`
  and **no** `required_non_null`, so on the production path `partition_rejects` always takes
  the empty branch and `_rejected` is never written.
- The FR-29 correction path already refuses this exact loss: `correct_schema`
  (`ingestion.py:363`) recasts through the same `apply_recipe` (`:425-427`), and `:436-449`
  counts `added_nulls` per column and raises `SCHEMA_INFERENCE_CONFLICT` with *"A cast that
  silently nulls the column is worse than a refused one"* (`:436`). The ingest path has no
  such count.

**Limb (b), the blind validation** (`pricing_core/data/validate.py`).

- `dtype_match` (`:258-292`, VR-STR-2): compares `str(frame.schema[name])` with the declared
  dtype (`:279`). After a non-strict cast the dtype always matches, so it passes by
  construction: the coercion it exists to catch has already been turned into the right dtype.
- `date_parsed` (`:295-321`, VR-STR-5): checks the column's **type** only (`:313`). After a
  non-strict `parse_date` the type is `Date`, whatever was lost.
- `range` (`:671-704`): `:694` filters `pl.col(column).is_not_null() & predicate`. A coerced
  null is outside every range test.
- `reject_rate` (`:394-428`, VR-STR-9): reads `tables.get(... "_rejected")` (`:408-409`); on
  the Job path that table never exists, so `rejected_rows` is always 0.
- A check sees only the tables and `ValidationContext` (`:84-94`: reference tables and frames,
  the exposure column and the reference profile). Nothing the ingest learned about a coercion
  reaches a check unless it is stored **on the version** as a table.

**The spec** (`01-data-management.md`, read in full at the rows; no dated amendment sits on
either):

- **FR-32** (`:84`, `§3.1`): *"Rows that cannot be parsed at all (malformed CSV, unparseable
  dates in a required date column) are **rejected to a quarantine table** stored with the
  version rather than dropped silently. A version with rejects can still be validated; a
  configurable rule (`ingest.reject_rate`) fails it above a threshold."*
- **VR-STR-2** (`:392`, `§4.4`): *"`VR-STR-2` dtype-match | fail | Each column's Arrow dtype
  matches the declaration (no silent coercion)"*.
- Beside them in `§4.4`: VR-STR-3 nullability (`:393`), VR-STR-5 date-parse (`:395`, *"All
  date columns parsed to `date32`/`timestamp` with no fallback-to-string"*), and VR-STR-9
  reject-rate (`:399`, *"Quarantined rows ≤ threshold (default 0.1 % of rows read) — FR-32"*).
- `§4.2` shows the quarantine as a table on the version:
  `{"name": "_rejected", "record_grain": "quarantine", ...}` (`:285`). `§5.1` serves it
  (`:874`, `GET /api/v1/dataset-versions/{id}/rejected`), and the version detail view has a
  rejected-rows drawer (`:1046`).
- FR-45 (`:107`) requires four layers in every Rule Set, but **no requirement puts
  `reject_rate` in every Rule Set**, so a verdict carried by `reject_rate` alone is absent from
  any rule set that omits it. FR-46 (`:108`): `validated` needs zero `fail` and every `warn`
  acknowledged.

## Goal

A cell that is non-null in the source and does not survive a recipe `cast` or `parse_date`
is **never written as a silent null**. Its whole row is **quarantined** (DP-C1 (Q), ruled):
the row's source text goes to the version's `_rejected` table, named by column, step and reason,
and is counted in `rows_rejected`. The quarantine is **complete for each row**: no partially cast
row, and no row derived from a quarantined one, is written. Every such cell yields a
**validation verdict** at the declared severity of each rule that declares its column:
`reject_rate`, `dtype_match` and `date_parsed` (DP-C3 (ii), ruled). So a version over a
coerced cell cannot read `validated` unless that verdict passes or is acknowledged (FR-46), even
when its Rule Set has no `reject_rate`. The Job handler is unchanged (DP-C2 (a), ruled). `range`
is unchanged, and a guard test states why (DP-C3 (ii)). After ingest, a column's `null_count`
equals the source's genuinely empty cells, never the bad-cell count.

## Acceptance Standard

Each item is checked by a command that a fresh reviewer can run from the repository root on the
slice's merge tree.

1. **This delta passes the docs checks on its own branch.** At the branch head,
   `python3 scripts/audit-docs.py` prints no line naming this file or the SL-8043 row, apart
   from the working-id lines of checks 31 and 32, which are expected until the ids are minted.
   After minting, `python3 scripts/audit-docs.py`, `python3 scripts/doc-index.py --check` and
   `python3 scripts/register-lint.py` exit 0.
2. **No requirement range.** `grep -nE '(N?FR)-[0-9]+ *(-|to|–) *(N?FR-)?[0-9]+' <this file>`
   prints no line that stands for a set of ids.
3. **Spec first.** `git log --format=%s origin/main..<slice head> -- docs/specs/01-data-management.md`
   shows Task 3's dated clauses landing in a commit before or with the code, never after.
4. **No silent null on the Job path (R1, limb (a), red on main).** Through a real
   `dataset.ingest` Job (`execute_job`) over the five-row fixture, the version has a `_rejected`
   table holding exactly `p2`, `p3` and `p5`, each with **every** column as source text
   (`claim_amount` `"np.float64(1.0)"`, `"abc"`, `"80.0"`; `start_date` `"2024-02-30"`,
   `"not-a-date"`, `"2024-13-01"`), with `_reject_column`/`_reject_step` `claim_amount`/`cast`
   for `p2` and `p3`, and `start_date`/`parse_date` for `p5`. The `policy_exposure` table holds
   exactly `p1` and `p4`. The `IngestionRunRow` has `rows_read == 5`, `rows_rejected == 3`,
   `rows_written == 2`, and **`rows_read == rows_written + rows_rejected` is asserted** (the
   12:23:36 entry). On main the first assert fails: there is no `_rejected` table. A failure
   from any other cause is a plan defect.
5. **After ingest, a null is a source null and nothing else (R6, red on main; the 12:23:36
   entry's added assert).** Over the five-row fixture, the written table's
   `null_count(claim_amount) == 0` and `null_count(start_date) == 0`: the source's genuinely
   empty cells, of which it has none. The same test then ingests the fixture with `p1`'s
   `claim_amount` replaced by `""`. It asserts `null_count(claim_amount) == 1`, which is that one
   empty cell, never the bad-cell count. On main the first assert reads 2 for `claim_amount` and
   3 for `start_date`, which are the bad-cell counts.
6. **The quarantine is filled by `pricing-core`, completely (R2, red on main).** `apply_recipe`
   over an all-`String` frame returns `.rejected` with every failing row as its **input** text,
   and `.tables` without it. This holds for a `cast` failure and for a `parse_date` failure. It
   also holds for a row whose first step succeeded and whose second failed: that row is
   quarantined with its source text, not its step-1 cast value, so no partially cast row
   survives. On main `.rejected is None`.
7. **A later step cannot launder a coercion (R3, red on main).** Over the five-row fixture,
   the recipe plus
   `{"step": "fill_null", "params": {"column": "claim_amount", "value": 0}}` writes no row for
   `p2`, `p3` or `p5`. On main `p2` and `p3` are written with `claim_amount == 0.0`.
8. **Validation gives a verdict at the declared severity (R4, limb (b), red on main).** A
   `dataset.validate` Job over the R1 version with the fixture's five rules, approved, reports
   overall **`fail`**. Each of the three rules then fails as follows:
   - `reject-rate`: `measured.rejected_rows == 3` and `measured.rows_read == 5`;
   - `dtype`: `measured.coerced_cells == {"claim_amount": 2, "start_date": 1}`;
   - `datep`: `measured.coerced_cells == {"start_date": 1}`.

   On main the report is overall `pass`, with all five passing, as in the auditor's run. A
   matching `fail` from another rule or cause is a plan defect.
9. **Without `reject_rate`, the declared severity still decides (R5, red on main).** The same
   version, with `reject-rate` left out of the Rule Set, `dtype` declared `warn` and `datep`
   declared `warn`, reports overall `warn`. The version cannot move to `validated` until both
   warnings are acknowledged (FR-46). With `dtype` declared `fail` instead, it reports `fail`.
   On main both read `pass`.
10. **The guards stay green, at base and at head.**
    - G1: a source cell left empty, or written as one of `formats.py:120`'s null tokens, is a
      source null and not a coercion. It is written as null, and makes no `_rejected` row and no
      `coerced_cells` count.
    - G2: `test_data_jobs.py`'s existing recipe tests (`CAST_RECIPE`, `:57`) and
      `test_ingestion.py:149-153` (a required-null reject) pass unchanged.
    - G3: `correct_schema`'s refusal (`ingestion.py:436-449`) is unchanged.
    - G4, the `range` guard stated (DP-C3 (ii)): `range` (`validate.py:694`) still ignores a
      genuine null. Under the quarantine, no coerced null reaches it, so its null-ignoring
      cannot hide a coercion. A null in a column that must not be null is VR-STR-3's verdict. A
      test pins this.
    - G5: `rows_read == rows_written + rows_rejected` holds for every recipe without a
      row-changing step (`filter_rows`, `deduplicate`, `explode_period`). Under those steps
      `rows_written` counts what the steps wrote, so the identity cannot hold by definition. The
      LG records which recipes it was asserted for.

    The LG records each as a guard.
11. **The G2 probe gated the code (DP-G2, binding).** The LG carries Task 0 Step 3's output
    verbatim, one line per cast column for each of the two populations: all 678 013 freMTPL2
    rows, and the seeded 20 000-row portfolio sample. The first code commit comes after it. If
    any count is non-zero, the LG records the STOP to the maintainer, and no code commit follows
    without the maintainer's dated ruling.
12. **One reject shape.** `git grep -nE '"_reject_(column|step)"' -- packages backend/src`
    prints each literal once, as a constant beside `REJECT_REASON_COLUMN`
    (`pricing_core/data/ingest.py:242`); every other use imports it.
13. **The gate is green on the merge tree.** Both halves of the `CLAUDE.md` §11 commands pass,
    named against `origin/main...<slice branch>`.

## Global Constraints

- **`pricing-core` owns the coercion rule** (ADR-703; `CLAUDE.md` §2). A notebook that calls
  `apply_recipe` gets the quarantine as the Job does. `pricing-core` returns rejected rows; it
  never raises `PlatformError`.
- **A coercion is defined once:** a cell non-null before a `cast` or `parse_date` step and null
  after it. A source null is never a coercion (G1).
- **Evidence is kept, and the quarantine is complete for each row** (the 12:23:36 entry). A
  quarantined row keeps its **source** text (`01` FR-32: *"rather than dropped silently"*). It is
  taken from `apply_recipe`'s input, never from a partially cast intermediate frame, and the
  `_rejected` table is all-`String`. No row derived from a quarantined source row is written.
- **FR-32's wording is not changed.** The clause Task 3 adds is a dated amendment beside it;
  `ingest.reject_rate` keeps its threshold meaning.
- **No money becomes a float on the way.** The fixture's `claim_amount → float64` is the
  auditor's input, not a pattern: no new code here casts money to float (`CLAUDE.md` §7).
- **The barred word.** Write "the maintainer (by delegation)"; elide quoted text with a
  bracketed elision note.

## The G2 interaction (stated, per the brief)

**G2 (the WF-699 seed ingest).** The only ingest on the G2 path is `examples/fremtpl2/seed.py`,
which `scripts/demo.py:324` runs. Its recipe is `recipe()` (`seed.py:96-118`), submitted as a
`dataset.ingest` Job at `seed.py:507-517`, three times: version 1 (`:571`), version 2 (`:659`)
and the 20 000-row portfolio sample (`:741`). The steps are a `rename` (`RENAMES`, `:63-67`),
then **one `cast`** over `NUMERIC` (`:69-78`), verbatim:
`{"exposure_years": "float", "claim_count": "int", "veh_power": "int", "veh_age": "int",
"driv_age": "int", "bonus_malus": "int", "density": "int", "claim_amount_minor": "int"}`;
version 2 and the portfolio add one `filter_rows`. **There is no `parse_date` step on G2.** The
WF-699 journey test (`backend/tests/test_wf699_journey.py`) ingests nothing; it builds its
world directly.

**Would the fix refuse or flag freMTPL2's own data? Measured: no coercion on the frequency
file; the probe in Task 0 Step 3 is the authority.** The source is
`examples/fremtpl2/data/freMTPL2freq.arff` (fetched by `fetch.py`, sha256-pinned, git-ignored;
`arff.py:43` only strips quotes, so the cast sees the file's text). Run 2026-10-14 by this
planner, read-only, over all 678 013 data rows: a value is counted as failing an `int` cast
unless it matches `^-?\d+$`, and failing a `float` cast unless it matches a decimal or
exponent form. Result:
`{'ClaimNb': 0, 'VehPower': 0, 'VehAge': 0, 'DrivAge': 0, 'BonusMalus': 0, 'Density': 0}`
non-integer values, and `exposure_nonfloat 0`. **This is a proxy for Polars' own
`String → Int64` parse, not the parse itself.** It is noted, not relied on (the 12:23:36 entry).
Task 0 Step 3 re-counts through Polars, with the recipe's own cast, over the whole book and the
seeded 20 000-row portfolio sample, and that count is binding. `claim_amount_minor` is
computed by the seed itself as an `Int64` (`seed.py:141`) before it is written as text, so its
cells are integer strings. One side fact, not this plan's scope: `IDpol` holds one value
written `1e+05`, but `policy_id` is never cast, so nothing is coerced.

So, on that proxy measurement, the fix **would change nothing on G2**: no row is quarantined, no
`coerced_cells` count is non-zero, and the seed's rule set (`seed.py:254` onward) sees the same
tables. If the binding probe finds any non-zero count in either population, that column is
being nulled silently on main today, and that is a STOP to the maintainer before code (DP-G2,
ruled binding), because it would change the A-4/WF-699 seed's rows.

**SL-1543.** Its fixture once relied on the nulling: the 11:52:51 entry accepted the cause
(*"test_demo_peril_structure.py:81 wrote "np.float64(…)""*) and the fix-forward `@f52906ac`.
`test_demo_peril_structure.py` exists only on `origin/sl-1543-prep-on-1300`; there, commit
`4ec537c3` fixed the `np.float64(..)` repr (`:82`). Its clean book now writes `repr(float)`
values and leaves zero-claim severities empty, and its "null" bad row is `""`; all of these are
nulls **at read** (`formats.py:120`), not coercions. So, as that branch stands, it does not
depend on the cast nulling anything, and this slice does not touch its write set. **The
interaction is one of order, and it is a safety net:** if any SL-1543 fixture still wrote a
value a cast cannot parse, then after this slice merges that row is quarantined and
`reject_rate`/`dtype_match` fail, instead of a silent null. That is the failure the 11:52:51
entry wanted visible. Whichever of this slice and SL-1543 merges second re-merges `main` and
re-runs SL-1543's tests and the WF-699 journey test (Task 7). On `main` no test fixture relies
on a cast nulling a value: the `strict=False` hits under `backend/tests` and
`packages/*/tests` are `zip(..., strict=False)` and `pl.DataFrame(..., strict=False)`, not casts.

## Decision points

Every row is ruled by the maintainer's (by delegation) entry "2026-10-14 12:23:36 BST", quoted
in full under Authority. The options and recommendations are kept as they were weighed. The
"Resolved by" cell carries the ruling.

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-C1 | What happens to a source cell that is non-null and does not survive a recipe `cast` or `parse_date`? | **(R) Refuse:** the ingest fails and makes no version, in the form `correct_schema` already uses (`ingestion.py:436-449`). **(Q) Quarantine:** the row's source text goes into `PreparationResult.rejected` (`prepare.py:85`, declared and never filled), then into the version's `_rejected` table with `_reject_column`, `_reject_step` and `_reject_reason`, and is counted in `rows_rejected` (FR-31). **(C) Counted coercion:** the cell stays null in the row, and a `_coercions` table records it. | **(Q).** It is FR-32's own mechanism, which exists unfilled: the table (`01:285`), its endpoint (`01:874`), its drawer (`01:1046`), VR-STR-9 and the result field (`01:956`). (R) gives no version to judge, and FR-32 says *"a version with rejects can still be validated"*. Under (C) the null still reaches modelling. | design | no — ruled | **Ruled (Q)**, 2026-10-14, by the maintainer (by delegation), entry 2026-10-14 12:23:36 BST. (R) and (C) were refused. The quarantine is complete for each row, and `rows_read == rows_written + rows_rejected` is asserted. |
| DP-C2 | The Job handler (`data_handlers.py:140-149`) never passes `required_non_null`. Does this slice make it pass one, and from where? | **(a)** No change: under Q every coercion is quarantined, whatever the column. A **source** null in a column that must not be null is VR-STR-3's verdict (`not_null`, `validate.py:179`). **(b)** Add an optional list to the Job parameters and the route body (`api/datasets.py:556`); this is a contract change. **(c)** Derive it from a declared schema. No field exists to derive it from (`DataDictionaryEntry`, `model_schema/datasets.py:140-155`). | **(a).** FR-32's *"unparseable dates in a required date column"* is a subset of what Q quarantines. | design | no — ruled | **Ruled (a)**, 2026-10-14, by the maintainer (by delegation), entry 2026-10-14 12:23:36 BST: *"no handler change (under Q every coercion is quarantined)"*. |
| DP-C3 | Which checks carry the verdict for a quarantined coercion? `reject_rate` alone gives none when a Rule Set omits it, and FR-45 (`01:107`) does not require it. | **(i)** `reject_rate` (VR-STR-9) only. **(ii)** (i), plus `dtype_match` (VR-STR-2) and `date_parsed` (VR-STR-5): each reports `measured.coerced_cells` for the columns it declares, at its declared severity. `range` is unchanged, with a stated guard. **(iii)** (ii), with a tolerance parameter. | **(ii).** VR-STR-2's own text is *"(no silent coercion)"*. `warn` plus an FR-46 acknowledgement is the user's knob. | design | no — ruled | **Ruled (ii)**, 2026-10-14, by the maintainer (by delegation), entry 2026-10-14 12:23:36 BST. `coerced_cells` = the cells quarantined because of that column. The verdict holds without `reject_rate`. The `range` guard is stated (G4). (iii) is not taken now. |
| DP-G2 | Does the fix change G2's data? The seed's `cast` (`seed.py:69-78`) runs on every G2 ingest. | **The probe decides.** Task 0 Step 3 counts, through Polars and with the recipe's own cast, the cells the cast would quarantine. It counts over all 678 013 freMTPL2 rows and over the seeded 20 000-row portfolio sample. All zero: no G2 interaction. Any non-zero: STOP. | The planner's proxy regex count was 0 on every cast column. It is noted, not relied on. | scope | **yes, binding: blocks code until the probe is clean or the maintainer rules on it** | **Ruled binding**, 2026-10-14, by the maintainer (by delegation), entry 2026-10-14 12:23:36 BST, *"G2 condition (binding)"*. A non-zero count is a STOP to the maintainer before code. |

**The refused options, kept as the record of what was weighed** (DP-C1). The table below says
what would have changed under each one. It is not a live alternative.

| Item | (Q), ruled | (R) Refuse, refused | (C) Counted coercion, refused |
|---|---|---|---|
| R1 | `_rejected` holds `p2`, `p3` and `p5`, and the clean table holds `p1` and `p4` | the ingest Job fails and makes no version | the version keeps 5 rows, and a `_coercions` table holds the cells |
| R2 | `.rejected` holds the rows | `apply_recipe` raises `RecipeError` | a coercions frame holds the cells |
| R4, R5 | `reject-rate`, `dtype` and `datep` give the verdict | void: no version | `dtype` and `datep` read `_coercions` |

Every decision point is ruled. DP-G2's ruling leaves one gate inside the slice, Task 0 Step 3's
probe, which stops the slice, not the plan. This delta stays `draft` here. It is frozen at its
merge and made `active` by a dated line, and no status is set here.

## Tasks

| Order | Slice | Tasks | Requirements (each id) | Activation needs | Lane |
|---|---|---|---|---|---|
| 1 | SL-8043 — FD 8040: a recipe cell that does not parse is never silently nulled, and validation gives it a verdict | Tasks 0 to 7 below | `01` §3.1: FR-32 (the quarantine, and the Job path); `01` §4.4: VR-STR-2, VR-STR-5 and VR-STR-9 (catalogue rules; the checks that give the verdict); `01` §3.2: FR-35 (the steps whose behaviour changes); read only: FR-31, FR-45, FR-46, VR-STR-3 | FD 8040 minted; every DP ruled — MET, by the maintainer's (by delegation) entry "2026-10-14 12:23:36 BST"; this delta minted and made `active` by a dated line; Task 0 Step 3's G2 probe clean on both populations, or the maintainer's ruling on it; a free build lane | 1 |

### Task 0 — re-read at the base, enumerate, and probe (convention 4)

- [ ] **Step 1.** Re-read every `file:line` this plan cites at the slice's base, and record in the
  LG each one that moved. Re-read FD 8040 in full once it is on `origin`, and record its limbs.
- [ ] **Step 2.** Enumerate, and record in the LG:
  - every `strict=False` cast or parse in `packages/*/src` and `backend/src`:
    `git grep -nE "strict=False" -- packages/*/src backend/src`, keeping only the
    `.cast(`/`.strptime(` hits. At this plan's tree the hits are `prepare.py:136` and `:142`;
    any other is a site this slice must cover or name as out of scope;
  - every reader of `_rejected` or `REJECT_REASON_COLUMN`:
    `git grep -nE "_rejected|REJECT_REASON_COLUMN|_reject_reason" -- packages backend/src frontend/src`.
    Known at this tree: `validate.py:404-409`, `ingestion.py:204-211`,
    `dislocation_runs.py:170`, `ingest.py:242` and its uses. Each reader must accept the two
    new columns.
- [ ] **Step 3 — the G2 probe (DP-G2, binding; the 12:23:36 entry).** Run this before any code,
  with a throwaway script under the job's tmp directory that is never committed. It counts
  **through Polars, with the recipe's own cast**, over two populations:
  - **(i)** the whole book, the bytes `examples/fremtpl2/seed.py`'s `build_csv(None)` (`:121`)
    makes. It must report 678 013 rows read, and a different row count is itself a STOP;
  - **(ii)** the seeded portfolio sample, the bytes `build_portfolio_csv()` (`:170`) makes. It
    must report 20 000 rows (`PORTFOLIO_ROWS`, `:88`).

  For each population, read the bytes with `app.data.formats.read_tabular`, apply
  `normalise_columns`, then run `pricing_core.data.prepare.apply_recipe` with the seed's own
  `recipe(drop_implausible_exposure=False)`, using the **base tree's** code. For each column of
  `NUMERIC` (`:69-78`), print the number of cells that are non-null before the `cast` step and
  null after it. Print one line per population and column.
  - **All zero:** record the output verbatim in the LG and proceed.
  - **Any non-zero:** STOP to the lead for the maintainer before code. That count would change
    the A-4/WF-699 seed's rows.

  The planner's proxy count (regex, "The G2 interaction") is not evidence for this step.
- [ ] **Step 4.** Re-read `to-lead.md` from "2026-10-14 12:23:36 BST" on, for any ruling on
  this plan's subject, and name each one at every site it operates (convention 5).

### Task 1 — limb (a)'s reds, on main

**Files:** create `backend/tests/test_ingest_coercion.py`; modify
`packages/pricing-core/tests/test_prepare.py`.

Every red in this task and the next uses **the five-row fixture** ("The fixture") and the
auditor's `RECIPE`, through `execute_job`, as the 12:23:36 entry orders.

- [ ] **R1** (`test_ingest_coercion.py`, `@pytest.mark.req("FR-32")`).
  - Setup: seed a workspace, dataset and actor in the form of `test_data_jobs.py:119-165`
    (`_seed_dataset_and_rules`). Mirror its private helpers rather than importing them, because
    `_ingest` (`:167-199`) hard-codes `CAST_RECIPE`.
  - Run: put the five-row `CSV` in the blob store, submit `JobKind.DATASET_INGEST` with
    `"recipe": RECIPE`, and run `execute_job`.
  - Assert, in this order:
    1. the version's `tables` include `_rejected`;
    2. `_rejected` holds exactly `p2`, `p3` and `p5`, every column as source text, with
       `_reject_column`/`_reject_step` as Acceptance 4 lists;
    3. `policy_exposure` holds exactly `p1` and `p4`;
    4. `rows_read == 5`, `rows_rejected == 3`, `rows_written == 2`, and
       `rows_read == rows_written + rows_rejected`.

  **Expected on main:** assert 1 fails, because the version's only table is `policy_exposure`.
  Any other first failure is a plan defect.
- [ ] **R6, the old behaviour cannot survive** (`test_ingest_coercion.py`,
  `@pytest.mark.req("FR-32")`; the 12:23:36 entry's added assert).
  - Ingest as in R1. Assert `null_count` is 0 for `claim_amount` and 0 for `start_date` in the
    written parquet. The fixture has no genuinely empty cell.
  - Then ingest the fixture again with `p1`'s `claim_amount` replaced by `""`. Assert
    `null_count(claim_amount) == 1`, which is the source's one empty cell.

  **Expected on main:** the first assert reads `claim_amount` 2 and `start_date` 3, the
  bad-cell counts. The four nulls in the auditor's run were this.
- [ ] **R2** (`test_prepare.py`, `@pytest.mark.req("FR-32")`). Three cases, each over an
  all-`String` `pl.DataFrame` with a key column `k`:
  - a `cast` of `x` to `float64` over `["1.5", "abc"]`;
  - a `parse_date` of `d` with `"%Y-%m-%d"` over `["2024-01-15", "2024-02-30"]`;
  - **completeness:** a recipe `[cast x→float64, parse_date d]` over two rows: `k="a"` with
    `x="1.5"` and `d="2024-01-15"`, and `k="b"` with `x="2.5"` and `d="2024-13-01"`. `b`'s cast
    succeeds and its date fails.

  Assert, in each case, that `.tables[...]` holds only the good row, and that `.rejected` holds
  the bad row with every column as its **input** text and the three reject columns. In the
  completeness case `.rejected` has `x == "2.5"`, the source text, not a cast value.
  **Expected on main:** `.rejected is None`.
- [ ] **R3** (`test_ingest_coercion.py`). The five-row fixture with
  `RECIPE + [{"step": "fill_null", "params": {"column": "claim_amount", "value": 0}}]`; the
  params are the ones the `fill_null` case reads (`prepare.py:161-164`). Assert that no row of
  the clean table is `p2`, `p3` or `p5`. **Expected on main:** `p2` and `p3` are written with
  `claim_amount == 0.0`.
- [ ] **G1** (`test_prepare.py` and `test_ingest_coercion.py`). A cell `""` or `"NA"` in
  `claim_amount` is null **before** the cast. It is written as null and makes no reject row.
  This is green at base and at head.
- [ ] Run each file with `scripts/run-small.sh` at the base, and record each red line and its
  cause in the LG.

### Task 2 — limb (b)'s reds, on main

**Files:** `backend/tests/test_ingest_coercion.py`, `packages/pricing-core/tests/test_validate.py`.

- [ ] **R4** (`@pytest.mark.req("FR-32")`, `@pytest.mark.req("FR-46")`).
  - Setup: ingest as in R1. Create the fixture's five rules and approve them through
    `backend/tests/approved_rows.py:78` (`add_approved`), as `test_data_jobs.py` does. Attach
    them as the dataset's Rule Set.
  - Run: submit `JobKind.DATASET_VALIDATE` through `execute_job`, and read the report.
  - Assert, in this order:
    1. the overall outcome is `fail`;
    2. `reject-rate` fails with `measured.rejected_rows == 3` and `measured.rows_read == 5`;
    3. `dtype` fails with `measured.coerced_cells == {"claim_amount": 2, "start_date": 1}`;
    4. `datep` fails with `measured.coerced_cells == {"start_date": 1}`.

  **Expected on main:** assert 1 fails. The report is overall `pass` with all five rules
  passing, as in the auditor's run.
- [ ] **R5** (`@pytest.mark.req("FR-46")`). The R1 version with `reject-rate` **left out** of
  the Rule Set, and `dtype` and `datep` declared `warn`.
  - Assert the overall outcome is `warn`.
  - Assert that the promotion to `validated` is refused until both warnings are acknowledged.
    Mirror the existing acknowledgement test; find it with
    `git grep -n "acknowledg" -- backend/tests`, and do not invent its helpers.
  - Then, with `dtype` declared `fail`, assert the overall outcome is `fail`.

  **Expected on main:** overall `pass` both times.
- [ ] **G4, the `range` guard stated** (`packages/pricing-core/tests/test_validate.py`). `range`
  over a column with a source null and in-range values reports `violating_rows == 0`. The
  test's docstring says why that is safe: under the quarantine no coerced null reaches `range`
  (DP-C3 (ii)), and a null in a column that must not be null is VR-STR-3's verdict. This is
  green at base and at head.

### Task 3 — the spec (`spec-change`)

**Files:** `docs/specs/01-data-management.md`.

- [ ] One dated clause on **FR-32** (`:84`), citing the maintainer's (by delegation) entries
  "2026-10-14 12:02:46 BST" item (1) and "2026-10-14 12:23:36 BST" (DP-C1 (Q), DP-C2 (a)).
  It says:
  - a non-null source cell that does not survive a recipe `cast` or `parse_date` is a row
    *"that cannot be parsed"*;
  - the whole row goes to the quarantine table as its source text, with the column and the
    step named. The quarantine is complete for each row: no partially cast row, and no row
    derived from it, is written;
  - `rows_read == rows_written + rows_rejected` for a recipe without a row-changing step;
  - this holds on the Job path whatever columns are required (DP-C2 (a)).
  
  FR-32's sentence is not edited.
- [ ] Dated notes on the **VR-STR-2** row (`:392`) and the **VR-STR-5** row (`:395`): each
  counts the quarantined coercions of the columns it declares (`measured.coerced_cells`, the
  cells quarantined because of that column), violating at its declared severity, whether or not
  the Rule Set carries `reject_rate` (DP-C3 (ii), the 12:23:36 entry). There is no tolerance
  parameter.
- [ ] `§4.2`: the `_rejected` entry (`:285`) names its three reason columns, `_reject_reason`,
  `_reject_column` and `_reject_step`, and states that its columns are text.
- [ ] `§5.2`: one dated note at `apply_recipe` (`:952-956`): `.rejected` is now filled with
  each quarantined row's source text, named by the step that failed it. The signature is
  unchanged.
- [ ] No requirement id is added, renumbered or struck. No new term is used, so `00` §2 is
  unchanged. If the executor finds that one is needed, the glossary entry comes first.

### Task 4 — limb (a) in `pricing-core`

**Files:** `packages/pricing-core/src/pricing_core/data/prepare.py`,
`packages/pricing-core/src/pricing_core/data/ingest.py`.

- [ ] In `ingest.py`, beside `REJECT_REASON_COLUMN` (`:242`), add
  `REJECT_COLUMN_COLUMN: Final = "_reject_column"` and
  `REJECT_STEP_COLUMN: Final = "_reject_step"`, and export them. `partition_rejects` fills them
  for its rows: the column it found null, and the step `"required_non_null"`. Its rejected
  frame is otherwise unchanged.
- [ ] **The quarantine is complete for each row** (the 12:23:36 entry). On entry,
  `apply_recipe` keeps its input frames and adds a private row index, `_source_row`, to each
  working table. Normalised source columns never start with `_` (`ingest.py:240-241`), so the
  name cannot collide. Every step carries the index through. A row that a later step duplicates,
  such as `explode_period` or a join, keeps its source's index.
- [ ] In `prepare.py`, the `cast` and `parse_date` cases (`:134-144`) find each row where a named
  column is non-null before the step and null after it. For each such row:
  - its `_source_row` is quarantined;
  - **every** working row carrying that index leaves the table;
  - the quarantined row is taken from the **input** frame by index, with every column cast to
    `pl.String` (the source text, never a step-1 cast value), plus the three reject columns.
  
  `_reject_reason` reads `"<column>: <step> could not parse <value!r> as <dtype or format>"`,
  where `<value>` is the source text. When one step fails several columns in one row, the row is
  quarantined once, under the first failing column in the step's declared order. `_source_row`
  is dropped from every frame before `apply_recipe` returns.
- [ ] `apply_recipe` returns `PreparationResult(tables=..., rejected=<the frame, or None when
  empty>, stats=...)`. `stats["steps"]` gains `rows_rejected` per step.
- [ ] R2, including its completeness case, and G1 (`test_prepare.py`) are green, and
  `test_ingest.py` is green unchanged.

### Task 5 — limb (a) on the Job path

**Files:** `backend/src/app/data/ingestion.py`.

- [ ] At `:171`, keep the `PreparationResult`, not only `.tables[table_name]`.
- [ ] At `:186-211`, the `_rejected` table is the recipe's rejected rows followed by
  `partition.rejected`, each cast to all-`String`. Concatenate with
  `pl.concat(..., how="diagonal")`, so a column present in one and absent in the other is
  null. `rows_rejected` (`:246`), `reject_sample` (`:247`) and the totals (`:267`) count both,
  as source rows. `rows_read` stays the source row count, as at `:162`. So
  `rows_read == rows_written + rows_rejected` holds for a recipe without a row-changing step.
  R1 asserts it on the fixture, and G5 on the existing recipe tests (the 12:23:36 entry).
- [ ] `correct_schema` (`:363-449`) is not changed (G3). Its refusal is the right answer there,
  because a correction has no quarantine.
- [ ] `data_handlers.py:140-149` is not changed (DP-C2 (a), ruled).
- [ ] R1, R3 and R6 are green; G1, G2, G3 and G5 are green.

### Task 6 — limb (b) in validation

**Files:** `packages/pricing-core/src/pricing_core/data/validate.py`.

- [ ] One private helper beside `_reject_rate` (`:394`). It reads the Rule's `_rejected`
  table, in the way `:408` does, and returns `{column: count}` over rows whose
  `_reject_step` is in `{"cast", "parse_date"}`, keyed by `_reject_column`. That is *"the cells
  quarantined because of that column"* (the 12:23:36 entry). It imports the constants from `ingest.py`.
- [ ] `dtype_match` (`:258-292`) counts, for each declared column, the helper's value as
  `measured["coerced_cells"]`, listing only the columns with a non-zero count, so that a clean
  version reports `{}`. Its `violating_rows` becomes the mismatched columns **plus** the
  coerced cells, and `detail` names both. `date_parsed` (`:295-321`) does the same for its
  declared date columns.
- [ ] `range` is unchanged, and its guard is stated (G4). `reject_rate` is unchanged: a filled
  `_rejected` is its fix. No tolerance parameter is added (DP-C3 (iii) is not taken now).
- [ ] `test_validate.py`: one test each for `dtype_match` and `date_parsed` over a `tables`
  mapping with a `_rejected` frame, with `@pytest.mark.req("FR-32")`.
- [ ] R4, R5 and G4 are green.

### Task 7 — close

- [ ] Run `uv run python scripts/req-coverage.py`, then the gate, both halves. Then the LG's
  closing acts.
- [ ] Whichever of this slice and SL-1543 merges second re-merges `main`. It then re-runs
  `backend/tests/test_wf699_journey.py` and, on SL-1543's branch,
  `test_demo_peril_structure.py`, and records both in its LG ("The G2 interaction").

### Write set

- `docs/specs/01-data-management.md`: FR-32's clause; the VR-STR-2 and VR-STR-5 notes; the
  `§4.2` `_rejected` entry; the `§5.2` `apply_recipe` note.
- `packages/pricing-core/src/pricing_core/data/`: `prepare.py`, `ingest.py` and `validate.py`.
- `packages/pricing-core/tests/`: `test_prepare.py` and `test_validate.py`.
- `backend/src/app/data/ingestion.py`: the recipe's rejects, merged into `_rejected`.
- `backend/tests/test_ingest_coercion.py` (new).
- The `LG-`.

No `model-schema` change, and so no contract regeneration. `_rejected` is a parquet table on
the version, not a published model. `GET /api/v1/dataset-versions/{id}/rejected` (`01:874`) is
`rejected_rows` (`backend/src/app/api/dataset_versions.py:413-453`). It returns an untyped
`dict[str, Any]` whose `sample` is `run.reject_sample`, so the two new columns appear in the
sample with no contract change. If Task 0 finds that the route has been typed since, the
columns are a contract change: STOP to the lead.

## Hand-off (not this plan's writes)

- **The lead:** mint FD 8040 (auditor-upload404's record) before this delta. GO the executor.
  Relay Task 0 Step 3's probe output, and any STOP, to the maintainer (DP-G2, binding).
- **The P1 batch:** SL-8043's roadmap row sits next to SL-8031's (PL 8030), both before
  `### WK-1250`. The 12:23:36 entry rules that this adjacency is resolved in that one PR.

## Self-review

- **Spec coverage.** The plan names each requirement with its section:
  - FR-32 (`01` §3.1): the quarantine, and the Job path;
  - VR-STR-2, VR-STR-5 and VR-STR-9 (`01` §4.4): the checks that give the verdict;
  - FR-35 (`01` §3.2): the steps whose behaviour changes.

  FR-31, FR-45, FR-46 and VR-STR-3 are read only. No requirement id is added or changed. Each
  limb maps to tasks:
  - limb (a), the coercion: R1, R2, R3, R6, Tasks 4 and 5, and DP-C2 for the handler;
  - limb (b), the blind validation: R4, R5, G4, Task 6 and DP-C3.

  The 12:02:46 entry names four checks, and each is handled:
  - `dtype_match` and `date_parsed` are changed (DP-C3 (ii));
  - `reject_rate` is fixed by filling `_rejected`;
  - `range` is shown not to need a change, with a guard (G4).
- **The three entries at every site** (convention 5):
  - *"both limbs red on main by cause"*: R1 to R6, each with its expected cause on main;
  - *"through the real Job path"* and *"by RUN via `execute_job`"*: R1, R3, R4, R5 and R6 run
    `execute_job` on `dataset.ingest` and `dataset.validate`. R2 is the `pricing-core` unit red
    beside them, not a substitute;
  - *"the 4-row fixture + p5"*: "The fixture", with the auditor's four rows verbatim and `p5`;
    every red uses the five rows;
  - *"a coerced cell must produce a validation VERDICT … fail or warn per its declaration"*:
    R4 (`fail`), R5 (`warn` without `reject_rate`, then the FR-46 acknowledgement; `fail` when
    declared `fail`), Acceptance 8 and 9.
- **The 12:23:36 rulings at every site** (amended 2026-10-14, after the rulings):
  - DP-C1 (Q), *"COMPLETE for each row"*: Goal, Global Constraints, R1, R2's completeness
    case, Task 3, Task 4 (the `_source_row` index), Acceptance 4 and 6;
  - *"`rows_read == rows_written + rows_rejected` is asserted"*: R1, Task 3, Task 5,
    Acceptance 4 and G5. G5 states the one scope the identity cannot reach, a recipe with a
    row-changing step;
  - DP-C3 (ii), *"coerced_cells … = the cells quarantined because of that column"*, the
    verdict without `reject_rate`, and no tolerance: Goal, R4, R5, Task 3, Task 6,
    Acceptance 8 and 9;
  - *"`range`'s … guard is stated"*: G4 in Task 2 and Acceptance 10;
  - DP-C2 (a): Goal, Task 3 and Task 5;
  - the added assert (*"`null_count(claim_amount)` equals the SOURCE's genuine empty cells
    only"*): R6 and Acceptance 5;
  - *"G2 condition (binding)"*, Polars over 678 013 rows and the seeded 20k: DP-G2, Task 0
    Step 3, "The G2 interaction" (the proxy noted, not relied on), Acceptance 11 and the
    Tasks row;
  - the roadmap adjacency of SL-8043 and SL-8031, resolved in the one P1 PR: "Hand-off".

  Each DP row's "Resolved by" cell carries its ruling, and the refused options are kept only as
  a record.
- **The G2 and SL-1543 interactions:** "The G2 interaction", DP-G2, Task 0 Step 3, Task 7 and
  Acceptance 11.
- **Literals verified at `a3fc2e8d`** (conventions 1 and 3), each by `git show` or `git grep`:
  - `prepare.py`: `:81-86`, `:85`, `:89-126`, `:126`, `:134-144`, `:161-164`;
  - `ingest.py`: `:240-241`, `:242`, `:245-286`, `:248-255`, `:257-261`;
  - `validate.py`: `:84-94`, `:179`, `:258-292`, `:279`, `:295-321`, `:313`, `:394-428`,
    `:408-409`, `:671-704`, `:694`;
  - `ingestion.py`: `:162`, `:164-178`, `:171`, `:186`, `:204-211`, `:246-247`, `:267`,
    `:363`, `:425-427`, `:436-449`;
  - `data_handlers.py:140-149`, `formats.py:10-14`, `:108-122`, `:118`, `:120`, and
    `api/dataset_versions.py:413-453`;
  - `test_data_jobs.py`: `:57`, `:119-165`, `:167-199`, `:506`; `test_ingestion.py:149-153`;
    `backend/tests/approved_rows.py:78`;
  - `01-data-management.md`: `:84`, `:107`, `:108`, `:285`, `:392`, `:393`, `:395`, `:399`,
    `:874`, `:952-956`, `:1046`;
  - `examples/fremtpl2/seed.py`: `:63-67`, `:69-78`, `:88`, `:96-118`, `:121`, `:141`, `:170`, `:254`, `:507-517`,
    `:571`, `:659`, `:741`; `scripts/demo.py:324`; `arff.py:43`;
  - `backend/tests/test_wf699_journey.py` (exists), and `4ec537c3` on
    `origin/sl-1543-prep-on-1300`.

  `api/datasets.py:556` and `model_schema/datasets.py:140-155` come from a delegated read; the
  executor re-reads them at Task 0.
- **Convention 4.** `to-lead.md` was read through the entry "2026-10-14 12:23:36 BST". Only the
  11:52:51 entry (item (1)), the 12:02:46 entry (item (1)) and the 12:23:36 entry rule on this
  subject.
  `gh pr list` was not run, because the brief allows no GitHub posts. Task 0 Step 4 re-reads at
  dispatch.
- **Placeholders.** `<slice head>` and `<slice branch>` are values read when the slice runs.
  The `_reject_reason` text form in Task 4 is this plan's choice. The two column names are
  this plan's too, and the executor does not rename them without the lead.
