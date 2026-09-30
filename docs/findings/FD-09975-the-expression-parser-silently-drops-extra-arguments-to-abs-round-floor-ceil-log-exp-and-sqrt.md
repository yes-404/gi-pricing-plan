---
id: FD-9975
family: finding
title: The expression parser silently drops extra arguments to abs, round, floor, ceil, log, exp and sqrt
status: active
created: 2026-09-30
owner: auditor
tree: 095dd400918348b32ee6eab1db7915faaa9dfe35
corrected_by: []
relates: [WK-690, SL-1271, FD-1241, FR-36]
---

# FD-9975 — The expression parser silently drops extra arguments to seven functions

## Finding

**Severity: high** (filed as a critical candidate; set to high on 2026-09-30, see the dated line below). On `origin/main` `095dd400918348b32ee6eab1db7915faaa9dfe35`,
`pricing_core.data.expressions._call` (`packages/pricing-core/src/pricing_core/data/expressions.py:228-253`)
returns `args[0].<fn>()` for each of `abs round floor ceil log exp sqrt` and discards every argument
after the first without a message. `round` hard-codes `digits = 0` (`:235`). The caller-side checks
(`:118-132`) test only the function *name* and that no keyword argument is used, never the argument
count. So an analyst who writes `round(x, 2)` gets 0 decimals, `log(x, 10)` gets the natural log, and
`abs(a, b)` becomes `abs(a)`, with no error, no warning and no trace. **Proposed by the auditor; the
disposition is the lead's.** FD-9975 is a working id, minted at the records PR.

It has the same shape as FR-218 (`FD-1241`): a silent wrong result in a pricing path, not a crash.
It is found in the DM's proof for DP-S1-2 (PR #957, working id 9972, branch `dm-rl-9972-dp-s1-2`, head
`b58e5d7f070995e91ac9538a4daf4c396431e461`), which rules exact arity for WK-690 Slice 1 (SL-1271); the
maintainer's entry of 2026-09-30 08:59:39 BST (`~/gi-pricing-plan.local/channel/to-lead.md`) ordered this
finding and the data check below.

*(Severity set 2026-09-30 by the auditor, with the lead's verdict that agrees: the maintainer's entry of
2026-09-30 09:10:46 BST, "DATA CHECK 0 ACCEPTED" (`~/gi-pricing-plan.local/channel/to-lead.md`), holds that a
defect that is **latent, with zero occurrences in every reachable store, confined to dataset preparation,
with scoring unaffected**, reads as high rather than critical. It would be critical if a stored expression
used the forms or a rating price read them; neither is true. The entry also accepts the data check below
as proven and rules out an off-box check: there is no production deployment yet (WK-674 builds one), this
box holds the only PostgreSQL, MinIO and Redis, and CI databases are built from the repository fixtures,
which were scanned.)*

## Evidence

### 1. Reproduced at `095dd400` (the auditor's run, not quoted from #957)

`/tmp/repro.py` (kept with the evidence, below) compiles each expression with the real
`compile_expression` over `{"a": [-3.0, 2.5], "b": [10.0, 10.0], "x": [1234.5678, 100.0]}` after
`uv sync --all-packages` at `095dd400`. Its output, verbatim:

```text
abs(a, b)        -> ACCEPTED [3.0, 2.5]
round(x, 2)      -> ACCEPTED [1235.0, 100.0]
floor(x, 2)      -> ACCEPTED [1234.0, 100.0]
ceil(x, 2)       -> ACCEPTED [1235.0, 100.0]
log(x, 10)       -> ACCEPTED [7.118476228297786, 4.605170185988092]
exp(a, b)        -> ACCEPTED [0.049787068367863944, 12.182493960703473]
sqrt(x, 3)       -> ACCEPTED [35.13641700572214, 10.0]
round(x)         -> ACCEPTED [1235.0, 100.0]
log(x)           -> ACCEPTED [7.118476228297786, 4.605170185988092]
round(x, 2, 3)   -> ACCEPTED [1235.0, 100.0]
expected: round(x,2)= [1234.57, 100.0]  log10(x)= [3.0915, 2.0]
```

All seven functions accept extra arguments, and the result equals the one-argument call. This
agrees with #957's three failing tests (`abs(a, b)` → `[3.0, 2.5]`; `round(x, 2)` → `[1235.0, 100.0]`;
`log(x, 10)` → `[7.118476228297786, 4.605170185988092]`). `min`, `max` and `coalesce` legitimately
take several arguments and are not affected. Keyword arguments are already refused (`:129-132`).

### 2. Where the parser is reachable today

`compile_expression` has three callers outside tests (`git grep -n "compile_expression" -- '*.py'`
minus tests), and `referenced_columns` (`expressions.py:135`) parses but does not evaluate.

| Caller | Reached by | What a stored expression silently computes |
|---|---|---|
| `prepare.py:167` (`derive_expression` recipe step) | `apply_recipe`, called from ingestion (`backend/src/app/data/ingestion.py:168-171`, the `recipe` of `POST /datasets/{slug}/versions`, `backend/src/app/api/datasets.py:159`, run by the ingestion job, `worker/data_handlers.py:148`) and `scripts/bench-data.py:248` | A **derived column**: every row of the dataset version, so every downstream factor, model fit and diagnostic reads the wrong number |
| `prepare.py:170` (`filter_rows` recipe step) | the same | **Which rows are kept**: a wrong rounding or logarithm changes which rows pass the filter, so a dataset version is silently short of rows |
| `validate.py:1892-1899` (the `expression` validation check, `01` §4.5) | a rule in a rule set, run by a validation job | A **row-level predicate**: a rule that should flag a row does not, or flags one it should not, so a validation report reads green or red wrongly |

Callers that are **not** affected, checked so this record does not over-claim:
- **Rating `expression` steps** (`RatingExpressionStep.expr`, `model_schema/rating.py:291`) are compiled
  and evaluated by the GoRules ZEN engine (`rating/compile.py:245`, `zen.compile_expression`), which has
  its own function table and its own semantics. They do not reach `compile_expression`.
- **`expression` custom objectives** are refused by the API before storage
  (`OBJECTIVE_KIND_NOT_ENABLED`, `features.expression_objectives_enabled` defaults to `False`,
  `backend/src/app/platform/settings.py:273`); WK-690 builds them. Today they cannot be stored, but they
  are the reason Slice 1 exists: the same parser will feed objectives, and a silent drop there would be
  a mispriced model.
- Factors (`transformations`), the frontend and `examples/` carry no expression string for this parser
  (the repository scan in evidence item 3 finds none).

The chain from a stored expression to a price is therefore *dataset preparation*, not scoring: a
wrong derived column changes what a model is trained on, and a wrong filter changes which policies it
sees. Neither shows in a trace, because the recipe step succeeded.

### 3. Read-only data check (the maintainer's 08:59:39 BST order)

**Question.** Does any stored expression in any reachable store call `abs`, `round`, `floor`, `ceil`,
`log`, `exp` or `sqrt` with more than one argument?

**Predicate**, the same for every store (`analyse.py`, kept with the evidence). A store is searched for the
text `\m(abs|round|floor|ceil|log|exp|sqrt)\s*\(` (case-insensitive); for each hit the Python function
`multi_arg_hits` counts the top-level commas up to the matching `)`, respecting nested parentheses and
single-quoted strings. A call counts if it has **more than one** top-level argument; an unterminated call
is counted separately as `unbalanced`. It is a text predicate over stored bytes, wider than the parser's
own AST walk (it also matches prose and other languages), so it can over-count and cannot under-count
for a call written in the grammar.

**Run**: 2026-09-30, 08:59 to 09:08 BST, from the auditor's worktree at `095dd400`. Everything was read
only; no store was written. The scripts and logs are kept in
`~/gi-pricing-plan.local/evidence/expr-arity-data/` with `SHA256SUMS`.

| Store | Corpus scope | Command | Function-call sites (any arity) | **More than one argument** |
|---|---|---|---|---|
| **PostgreSQL 16**, container `gi-pricing-postgres-1`, `localhost:5432` | Every `pg_database` with `datallowconn`: **78 databases** (FD-1241's 81 minus three since dropped); **3679 tables** (`relkind` `r`, `p`, `m`, outside `pg_catalog`, `information_schema`, `pg_toast`, `pg_temp*`); every column of every row, as `r::text` | `python3 scan_db.py`: per database, one `SELECT` of `select '<table>', m[1] from "<schema>"."<table>" r, regexp_matches(r::text, '(\m(?:abs\|round\|floor\|ceil\|log\|exp\|sqrt)\s*\([^"]{0,250})', 'gi') m` joined by `union all` over its tables, inside `BEGIN TRANSACTION READ ONLY` with `PGOPTIONS='-c default_transaction_read_only=on'` through `docker exec … psql` | **128**, every one in `public.objective_certificates`, in 2 of the 78 databases | **0** (0 unbalanced; 0 database errors) |
| **MinIO**, container `gi-pricing-minio-1`, `localhost:9000` | All **5 buckets**, **14 601 objects**, 76 738 589 bytes: `gip-test-blobs` 14 577, `gip-blobs` 10, `gip-bench-score-batch` 11, `gip-bench-compiled-for` 2, `aud933-bucket` 1. By leading bytes: 12 518 JSON-like, 87 parquet, 1996 other | `uv run --no-sync python scan_blobs.py`: boto3 `ListObjectsV2` and `GetObject` only, each object decoded as UTF-8 and scanned | **0** | **0** |
| **Redis**, container `gi-pricing-redis-1`, db0 | All **8 keys** (`SCAN`, then `GET`, `LRANGE`, `SMEMBERS`) | `python3 scan_redis.py` | **0** | **0** |
| **This repository** at `095dd400` | All **1865** tracked files. Whole-file: every file. Expression-bearing content only: the string literals of 498 `.py`, the quoted literals of 207 `.ts`/`.js`/`.vue`, and the whole of 139 data files (`.json .csv .yaml .yml .toml .sql .txt`); 981 `.md` files are prose and were counted apart. This covers `examples/`, every golden and seed fixture, and every test string | `python3 scan_repo.py .` and `python3 scan_repo_strings.py` | whole-file **740**, of which **121** have more than one argument (Python code such as `math.log(x, 2)`, docs and skills prose); in string/data content **107**, of which **2** have more than one argument and 3 are unbalanced | **0** in a string that reaches the parser. Five string/data hits (2 multi-argument, 3 unbalanced), none an expression: `safe_error.py` (a docstring), `profile.py:639` (a DuckDB SQL fragment, unbalanced), `bench-trace-size.py:178` (prose, unbalanced), `.claude/skills/ui-ux-pro-max/data/stacks/javafx.csv` (Java code), `.claude/skills/writing-skills/render-graphs.js` (prose, unbalanced) |

What the 128 PostgreSQL sites are: all in `public.objective_certificates`, none multi-argument. They are
not parser input (custom objectives do not reach `compile_expression` today, item 2).

**Population, so a 0 is not read from an empty store.** In the same 78 databases, counted with
`db_pop.py`: 0 rows contain `derive_expression`; **6 rows** contain `filter_rows` (3 in
`public.dataset_versions`, 3 in `public.jobs`, in 3 databases), and none of those calls any of the seven
functions; 0 rows carry an `expression` check (`"(check|kind|type)": "expression"`). So the live stores
hold six stored `filter_rows` recipes, and no stored `derive_expression` or `expression` rule at all.

**Positive controls (the predicate can fail).**
- *PostgreSQL path.* `control_db.py` creates a `TEMP` table (session-local, gone at disconnect) holding
  five rows and runs the **same query shape and the same Python predicate**: `round(x, 2)`, `abs(a, b) + 1`
  and `log(x, 10)` are counted (3 planted positives), `round(x)` and `sqrt(max(a, b))` are not (1 nested
  negative). The first run of this control **failed** with `invalid regular expression: invalid repetition
  count(s)`: the pattern's `{0,400}` exceeds PostgreSQL's limit of 255. The scan would have errored on every
  database. It was changed to `{0,250}` and the control re-run before the real scan. That is the control doing its job.
- *Repository path.* `control_repo_blob.py` builds a scratch git repository holding `a.py` (a
  `derive_expression` recipe with `round(x, 2)`), `b.json` (`log(x, 10)`) and `c.ts` (`abs(a, b)`), runs
  `scan_repo_strings.py` over it and prints three `HIT` lines, one per planted file. The scratch directory was removed.
- *Blob path.* The same script feeds `scan_bytes` a planted object body (`round(x, 2)` counted) and a
  single-argument negative (`round(x)` not counted). The MinIO client itself is read-only by construction (list and get).
- `analyse.py` carries a ten-case self-test (nested calls, quoted commas, three arguments) that exits 0.

**Stores not reached, stated so that "not reachable" is not read as zero.**
- **A dev or uat stack other than this box's**: there is none here. One PostgreSQL server listens on `5432`,
  one MinIO on `9000`, one Redis on `6379`. Whatever the maintainer runs elsewhere is unread.
- **`spike-f1-redis`**: the container is `Exited` (45 hours); it was not started and not read.
- **Parquet and other compressed objects**: the 87 parquet objects and 1996 `other` objects in MinIO were
  decoded as text and matched, but a compressed parquet page is not searchable as text. They hold data, not
  expression strings, so this is a limit on the MinIO count, not on any expression-bearing store.
- **CI databases** are ephemeral and out of scope. **Production** is not this repository's.
- **Untracked files** in other worktrees under `.claude/worktrees/` and `~/gi-pricing-plan.local/` were not scanned.

**Result: 0 stored expressions call any of the seven functions with more than one argument, over every
reachable store.** The one place the silent drop could have bitten is empty of it.

## Disposition

**Proposed by the auditor; the verdict is the lead's.** The defect is real, live and reproduced, and no
reachable stored data is affected. The maintainer's rule (`to-lead.md`, 08:59:39 BST, item 3): with a count
of 0, **#957's exact-arity rule landing in WK-690 Slice 1 is the fix** and this finding resolves when
Slice 1 merges; with a count above 0 the maintainer decides remediation first. The count is 0.

- **Effect of the fix, disclosed** (from #957): a stored expression *outside* this box that relies on the
  silent drop would be refused at its next compile with `ExpressionError("<fn>() takes exactly 1 argument, got n")`.
  That is fail-closed and correct; it is the case this check could not see.
- **Until Slice 1 merges** the defect stays live for any new recipe or rule a user writes, so Slice 1 is
  now also a correctness fix and belongs at the front of its lane.

**Event that next confirms or discharges it:** WK-690 Slice 1 (SL-1271) merges with the exact-arity rule
of #957 (DP-S1-2), **and its acceptance proves the refusal through each of the three reachable callers**,
not only the parser: a `derive_expression` step, a `filter_rows` step and an `expression` validation check,
each refused on `round(x, 2)` (red before the rule, green after). The finding resolves at Slice 1's merge.
Until then no action is needed: the window is small, this is a single-VM dev box, and there are 0 current uses.

## Decision

Not yet decided. The proposal above is the auditor's; the lead adopts, amends or rejects it. The
maintainer's entry of 2026-09-30 09:10:46 BST has already accepted the count of 0 and named the fix
(#957's exact-arity rule in WK-690 Slice 1) and the resolving event above.

Ownership shape: event
