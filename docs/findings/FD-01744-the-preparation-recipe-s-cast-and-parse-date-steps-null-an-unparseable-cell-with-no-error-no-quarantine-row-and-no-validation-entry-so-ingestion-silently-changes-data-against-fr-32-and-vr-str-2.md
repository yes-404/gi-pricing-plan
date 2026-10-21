---
id: FD-1744
family: finding
title: The Preparation Recipe's cast and parse_date steps null an unparseable cell with no error, no quarantine row and no validation entry, so ingestion silently changes data against FR-32 and VR-STR-2
status: active
created: 2026-10-17 # original date 2026-10-14, set at the filing; minted 2026-10-17
owner: auditor
tree: a3fc2e8dd384de6abf909f662f43011b8078fb4e
corrected_by: []
relates: [WK-1178, FR-32, FR-35, FR-41, FR-50, VR-STR-2, VR-STR-9, FD-1730, FD-1660, FD-1679, FD-1704, P2]
---

# FD-1744 — `strict=False` in `prepare.py` turns an unparseable cell into null, and nothing downstream counts it

*(Minted 2026-10-17 as FD-1744 from working id 8040, in the D18 batch mint PR.)*

*(Filed under working id 8040, reserved by the lead; a minter folds it into the docs batch.
Authority: the maintainer's (by delegation) entry "2026-10-14 11:52:51 BST" in
`channel/to-lead.md`, item (1): *"`packages/pricing-core/src/pricing_core/data/prepare.py:136`
casts with `strict=False` (and :142 parses dates with `strict=False`), so an UNPARSEABLE cell
becomes null with no error. That is exactly how 63/63 values vanished silently here. … If the
value silently becomes null with no report entry → an FD, proposed HIGH (silent data change
feeding pricing models), owner WK-1178, fixed in P2. The fix's DESIGN (refuse vs quarantine vs a
counted coercion with a validation verdict) is a planner DP against FR-32/VR-STR-2."*
The "63/63" is the maintainer's account of SL-1543's fixture, `test_demo_peril_structure.py:81`,
which wrote `"np.float64(…)"` into a numeric column. Every `file:line` below was read at
`origin/main` `a3fc2e8dd384de6abf909f662f43011b8078fb4e`, and the run was made at the same tree.
Run record: `~/.claude/jobs/b6860f8f/tmp/strictfalse/out.txt` (with `run.py`, `job.sh`).)*

## Finding

**Severity: HIGH, proposed by the auditor; RULED HIGH (CONFIRMED on the run) by the maintainer (by delegation), "2026-10-14 12:02:46 BST" in `channel/to-lead.md`, item (1): *"4 bad cells → ingest `succeeded` 4/4/0, no `_rejected` table, exactly 4 nulls written, then dataset.validate PASSED 5/5 approved rules. 01 FR-32 and VR-STR-2 are unmet on the production ingest path. Bad source data reaches pricing models as silent nulls, with a \"validated\" version on top. Owner WK-1178, fixed in P2."* Owner WK-1178, fixed in P2.** Run once,
through the real path, the result was: **silent**.

An analyst who ingests a file with a recipe `cast` or `parse_date` step gets a Dataset Version
in which every cell that step could not parse is null. The ingestion run reports no problem, the
quarantine is empty, and a validation report with five configured rules passes five of five. The
version can then be validated, promoted and fitted on. Nothing on any screen or API response says
that four values changed.

Two mechanisms hold this open, and both have to be fixed or the first one just moves.

1. **The steps coerce.** `packages/pricing-core/src/pricing_core/data/prepare.py:136`:
   `pl.col(column).cast(_dtype(dtype), strict=False)` and `:142`:
   `.str.strptime(pl.Date, params["format"], strict=False)`. With `strict=False`, Polars returns
   null for a value it cannot convert and raises nothing.
2. **Nothing counts it.** The recipe runs *before* the reject partition
   (`backend/src/app/data/ingestion.py:171`, `apply_recipe(...)`, then `:186`,
   `partition_rejects(frame, required_non_null=required_non_null)`). The partition quarantines only a
   null in a column named in `required_non_null`
   (`packages/pricing-core/src/pricing_core/data/ingest.py:245-257`; its docstring: *"an
   unparseable date in a required date column arrives here as a null, having failed non-strict
   parsing upstream"*). **The one production caller, the `dataset.ingest` handler
   (`backend/src/app/worker/data_handlers.py:140`), does not pass `required_non_null`**, and
   `git grep -n 'required_non_null='` over `backend/src` and `packages` at this tree finds the
   argument supplied only by tests (`backend/tests/test_ingestion.py:144`,
   `packages/pricing-core/tests/test_ingest.py`). So on the Job path the partition has no required
   column, and FR-32's quarantine cannot apply to any cell of any Job-ingested file.

## The specification it contradicts

`01-data-management.md:84`, **FR-32**, in full: *"Rows that cannot be parsed at all (malformed
CSV, unparseable dates in a required date column) are **rejected to a quarantine table** stored
with the version rather than dropped silently. A version with rejects can still be validated; a
configurable rule (`ingest.reject_rate`) fails it above a threshold."*

`01-data-management.md:392`, **VR-STR-2**, in full: *"`VR-STR-2` dtype-match | fail | Each column's
Arrow dtype matches the declaration (no silent coercion)"*.

Neither row carries a dated amendment (read at this tree). They bear on the finding differently,
and the difference matters for the fix:

- **FR-32's words cover dates in a *required* date column**, and malformed CSV rows. Read
  literally, it names no numeric cell. What it states as the principle is *"rather than dropped
  silently"*, and its stated mechanism, a required-column reject, is unreachable from the Job
  path, which is the defect for dates.
- **VR-STR-2 says "no silent coercion" and is structurally unable to see one.** It compares
  `str(frame.schema[name])` with the declared dtype (`packages/pricing-core/src/pricing_core/data/validate.py:258-285`,
  `_dtype_match`). After a cast to `float64` the dtype is `Float64`, so the check passes. The
  parenthesis is a promise the check cannot keep.
- `date_parsed` (`validate.py:295`) likewise checks the column's type is `Date`/`Datetime`,
  not that its values parsed. `reject_rate` (`validate.py:394`, VR-STR-9) reads the `_rejected` table,
  which does not exist when nothing was quarantined.

## Evidence

### 1. The run

2026-10-14T10:57:32 UTC, tree `a3fc2e8d`, scratch DB `gipricing_strictfalse_55638832` (`createdb -T
gipricing`, `alembic upgrade head`), a scratch bucket, behind `/tmp/slots/gate-1`; the DB, bucket
and worktree were removed afterwards. The path: a CSV blob put through `BlobStore`, a
`dataset.ingest` Job carrying the recipe, `execute_job` (the pattern of
`examples/fremtpl2/seed.py`: *"Every step goes through `ingest.upload → blob → Job → execute_job`"*),
then a `dataset.validate` Job against a five-rule set. **Set-up the run supplies, disclosed:**
the workspace, role assignments and approver principal were created in-process, and each rule was
dry-run, submitted and approved by a second principal, because a rule set runs only approved
rules (`FR-50`). The blob was put in-process, not through `upload-url`, which `FD-1730` shows
cannot reach ingestion.

Recipe: `[{"step":"cast","params":{"columns":{"claim_amount":"float64"}}},
{"step":"parse_date","params":{"column":"start_date","format":"%Y-%m-%d"}}]`. Input CSV:

```
policy_id,exposure,claim_amount,start_date
p1,1.0,100.0,2024-01-15
p2,0.5,np.float64(1.0),2024-02-30
p3,1.0,abc,not-a-date
p4,0.75,250.5,2024-03-01
```

Read back, verbatim:

```
INGEST JOB: succeeded
VERSION tables: ["policy_exposure"] status: draft
INGESTION RUN rows_read/written/rejected: 4 4 0 reject_sample: []
PARQUET table 'policy_exposure' schema={'policy_id': String, 'exposure': String, 'claim_amount': Float64, 'start_date': Date}
  p1 | 1.0  | 100.0 | 2024-01-15
  p2 | 0.5  | null  | null
  p3 | 1.0  | null  | null
  p4 | 0.75 | 250.5 | 2024-03-01
null_count: {'policy_id': 0, 'exposure': 0, 'claim_amount': 2, 'start_date': 2}
VALIDATE JOB: succeeded     job.error: None
REPORT overall: pass results: 5
```

The five results, every one with `"outcome": "pass"`: `dtype_match` (`measured`
`{"mismatched_columns": {}}` against declared `claim_amount: float64`, `start_date: date`),
`date_parsed` (`{"unparsed_columns": {}}`), `column_presence` (`{"missing": []}`), `range` on
`claim_amount` with `min_inclusive: 0` (`{"violating_rows": 0}`: the range check ignores the two
nulls) and `reject_rate` (`{"rows_read": 4, "reject_rate": 0.0, "rejected_rows": 0}`, threshold
`0.001`). Five further one-result reports in the same output are the rules' dry-run reports, also
"pass". No result names a cell, a column count or a row.

- **The four bad cells are exactly the four nulls**, and nothing records which they were.
- **No `_rejected` table exists** on the version; `rows_rejected` is 0 and `reject_sample` is empty.
- A bad date in a column nobody declared required was part of the run (in the Job path no column is
  required), so "dates in a non-required column" is covered, not open.

### 2. A guard the platform already wrote, one path over

`correct_schema` (`backend/src/app/data/ingestion.py:363`) recasts a draft version's column through
the *same* `apply_recipe` cast step (`ingestion.py:425`). It then refuses a cast that adds nulls
(`:436-449`), with the comment: *"A cast that silently nulls the column is worse than a refused
one: the version stays draft, looks corrected, and loses the data. `strict=False` is what makes
the cast survivable at all, so the check has to be here rather than in Polars."* and the error
*"Casting {column!r} to … would discard values … {added_nulls} of {frame.height} values do not
survive the cast and would become null."* So the code base has already decided that a nulling cast
is worse than a refused one, on the correction path, and left the ingest path, which is the
common one, without the guard. The two paths use one step and have two answers.

### 3. Not run

The following were not run, so they are not evidence either way:

1. **A direct `ingest_upload(..., required_non_null=[...])` call.** By `test_ingestion.py:144` and
   `partition_rejects`, a null in a named required column is quarantined. That is the mechanism FR-32
   describes; it is reachable by a service call and by no Job.
2. **A required *date* column on the Job path.** It cannot be set up: the handler passes no
   `required_non_null`, and `VersionCreate` (`api/datasets.py`) has no field for one.
3. **The other values the maintainer named, `"12,5"` and `"n/a"`.** The run used `np.float64(1.0)`
   and `abc`. Polars' non-strict cast gives null for any string it cannot parse, but this run does
   not show those two strings.
4. **A numeric column with no `cast` step**, and a malformed CSV row. Out of this finding's reach.
5. **Other `strict=False` sites.** `git grep -n 'strict=False' packages/pricing-core/src` at this tree
   also finds `ingest.py:221` (a sniffing sample, bounded), `profile.py:213`, `splits.py:124`,
   `validate.py:765,768,1641` and `rate_tables/weights.py:133,146,152`. They were not read for this
   finding and are not claimed; any that coerces stored data without a count deserves its own look.

## Severity: the proposal and its reasoning

**HIGH.** The comparators on this register:

- **Against FD-1660 and FD-1679 (HIGH): silently wrong evidence reachable by an ordinary call.**
  This is the same shape: a data change that no check reports, reached by the first thing an
  analyst does, with a clean report on top of it. The nulls are stored in the version's parquet, so whatever reads the column
  next (a profile, a fit, a split on a date) reads a missing value where the file held a bad one.
- **Against FD-1704 (MEDIUM).** That one needs a write path the application lacks. This needs only a
  recipe step the spec lists (`FR-35`: `cast`, `parse_date`).
- **What lowers it:** the damage needs a bad cell to exist, and the version's null counts are
  visible to someone who looks. Neither is a control; the validation report is where a
  governed platform says a version is fit, and here it says pass.
- **What raises it:** the validation report is the evidence a version is promoted on (`FR-46`).
  A report that passes over changed data is silent *approval evidence*, the class the maintainer
  has ruled HIGH.

## Disposition

**Fix with an owner: WK-1178, in P2** (the maintainer's (by delegation) "2026-10-14 11:52:51 BST"
item (1)). **Ruled 2026-10-14 12:02:46 BST by the maintainer (by delegation), `to-lead.md` item (1): the remedy has TWO limbs, both in scope, and the design DP is the planner's (refuse / quarantine / counted coercion).** *(a) the coercion:* `prepare.py:136` and `:142` `strict=False`, and the Job handler (`data_handlers.py:140`) never passes `required_non_null`. *(b) the blind validation:* `dtype_match` passes by construction after the cast, `date_parsed` checks type only, `range` ignores nulls, and `reject_rate` reads an always-empty `_rejected`. **Whatever the design, a coerced cell must produce a validation VERDICT** (a counted check, fail or warn per its declaration), so the version cannot read "validated" over a silent change. That is a constraint on every option in the table below: option A satisfies limb (b) only if the refusal is itself the verdict, and options B and C must add the counted check.

**The fix's design is a planner decision point against FR-32 and VR-STR-2, and this
finding takes no side.** The options, with what each needs, are:

| | What it does | Needs | Cost |
|---|---|---|---|
| **A. Refuse** | A `cast` or `parse_date` step that would turn a non-null value into null raises `RecipeError`; the Job fails with the `VALIDATION_FAILED` 422 and no version is created. The `correct_schema` guard (`ingestion.py:436-449`) generalised into the step. | No new table, no new rule. FR-41's "no partially prepared version" already says the failure shape (`ingestion.py:174-179`). Spec: a dated line on FR-35/FR-32 saying a step never nulls a value. | One bad cell blocks the whole file, and FR-32's quarantine intent (reject the *row*, keep the rest) is not met. |
| **B. Quarantine** | The rows with an unparseable cell go to `_rejected` with a per-column reason, and the rest are written. The reject-rate rule then governs. | The step must report which rows it could not parse (it returns a frame now). `partition_rejects` gets its input from the steps instead of `required_non_null`. FR-32's words widen from "dates in a required date column" to any recipe-parsed cell. `reject_rate` becomes the guard. | Changes the row count of a version. The default threshold of VR-STR-9 (0.1 %) turns a whole-column failure into a fail verdict, but a handful of bad rows in a large file passes. |
| **C. Counted coercion with a verdict** | The nulls stay. The step records, per column, how many values it could not parse; that count lands on the ingestion run and in a validation result that has a threshold. | A new mandatory rule or a non-optional built-in verdict (the run showed rules are opt-in via the dataset's rule set, so an optional rule leaves the hole open). A new field on the ingestion run. A new VR id. | Data with nulls is stored and can be promoted. The protection is only as strong as the verdict's threshold, and VR-STR-2's "no silent coercion" is met by *counting* rather than *preventing*. |

Cross-cutting questions the decision has to answer: whether the three are mutually exclusive
(B or C could apply to dates, A to numerics); what happens to a cell that was *already* null in the
source (it must not count as a coercion, which `correct_schema` handles by subtracting the
source's null count at `:440`); and whether the recipe's replay under `FR-41` must reproduce the
same quarantine. **No option is picked here.** The lead dispatches the planner, and the
decision-maker rules.

**The event that next discharges this finding** is the merge of the WK-1178 slice that implements
the ruled option, with a red that fails on the run's input above (the four bad cells) and passes on
the fix, green on `main`. The fix must also keep `VR-STR-2`'s parenthesis true or amend it, because
`dtype_match` cannot see a coercion by construction.
