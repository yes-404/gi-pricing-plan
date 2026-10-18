---
id: LG-8128
family: ledger
title: WK-1178 slice SL-1738 — FD-1744, a recipe cell that does not parse is never silently nulled and validation gives it a verdict (PL-1737) (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-10-18
owner: executor
tree: ~
phase: P2
work: WK-1178
slice: SL-1738
plans: [PL-1737]
corrected_by: []
relates: [PL-1737, SL-1738, FD-1744, FR-31, FR-32]
---

# LG-8128 — WK-1178 slice SL-1738: FD-1744, limb (a) the coercion and limb (b) the blind validation

Working id (lead-reserved). Executed by `exec-1738`, branch `sl-1738-wk1178-fd1744-coercion`, base `origin/main`
`84b0ff5765e55bc8edd139cd22bb57cd474de807`. **Authority:** the maintainer, to-lead "2026-10-18 22:50:32 BST" (GO SL-1738);
the plan is PL-1737.

## Tasks

- **Activation (own docs-only commit):** `35eb81868aa82ed3891287bf8543c7c69415b04f`. Needs at main `84b0ff57`: FD-1744 minted
  (`docs/findings/FD-01744-*.md`); DPs ruled (to-lead "2026-10-14 12:23:36 BST", "2026-10-14 12:42:55 BST"); plan and slice made
  `active` by that commit; Task 0 Step 3's probe clean (below).
- **Task 0 Step 3 — the G2 probe (DP-G2, binding), run before any code.** Base-tree code, Polars, `apply_recipe` with the
  seed's own `recipe(...)`. The `.arff` inputs match the sha256 pins in `examples/fremtpl2/fetch.py:29,33`
  (`a45363e0…`, `04763201…`). Script (throwaway, run from the job scratch dir, not part of the slice's code):

```python
import sys, io
from pathlib import Path
W="/home/puzhenhao1989/gi-pricing-plan/.claude/worktrees/sl-1738"
sys.path[:0]=[W+"/examples/fremtpl2", W+"/backend/src"]
import polars as pl
import seed
seed.DATA_DIR = Path("/home/puzhenhao1989/gi-pricing-plan/examples/fremtpl2/data")
from app.data.formats import read_tabular
from pricing_core.data.ingest import normalise_columns
from pricing_core.data.prepare import apply_recipe
def run(label, data, expect):
    df = read_tabular(data, "policy_exposure.csv")
    m = normalise_columns(df.columns)
    df = df.rename(m.rename_map)
    print(f"[{label}] rows_read={df.height} (expect {expect})")
    # after-rename names
    ren = seed.RENAMES
    for drop in (False, True):
        res = apply_recipe({"policy_exposure": df}, seed.recipe(drop_implausible_exposure=drop))
        out = res.tables["policy_exposure"] if hasattr(res,"tables") else None
        if not drop:
            pre = df.rename({k:v for k,v in ren.items() if k in df.columns})
            for c in seed.NUMERIC:
                nn_before = pre[c].is_not_null().sum()
                bad = (pre[c].is_not_null() & out[c].is_null()).sum()
                print(f"  {label} drop=False col={c} non-null-before={nn_before} nulled_by_cast={bad}")
        print(f"  {label} drop={drop} stats.steps={res.stats.get('steps')} rows_out={out.height}")
        print("  attrs:", [a for a in dir(res) if not a.startswith('_')])
        if drop: print(f"  identity: {df.height} - 0 - {df.height-out.height} + 0 == {out.height}")
run("whole", seed.build_csv(None), 678013)
run("portfolio", seed.build_portfolio_csv(), 20000)
```

  Output (condensed: the script printed one line per NUMERIC column per population, identical but for the column name; every `nulled_by_cast` was 0):

```text
[whole] rows_read=678013 (expect 678013)
  whole drop=False col=<each of the 9 NUMERIC columns> nulled_by_cast=0
    (non-null-before: 678013 ×7; claim_amount_minor 668897; claim_severity 24944)
  whole drop=True rows_out=677442; identity: 678013 - 0 - 571 + 0 == 677442
[portfolio] rows_read=20000 (expect 20000)
  portfolio drop=False col=<each of the 9 NUMERIC columns> nulled_by_cast=0
    (non-null-before: 20000 ×7; claim_amount_minor 19734; claim_severity 697)
  portfolio drop=True rows_out=19985; identity: 20000 - 0 - 15 + 0 == 19985
```

  Per-step (drop=True): rename/cast `rows_before == rows_after` (678013 / 20000); `filter_rows` 678013 → 677442 and 20000 → 19985.
- **Task 0 Step 2 enumeration (at the base).** `strict=False` cast/parse sites: `prepare.py` `cast` and `parse_date` only
  (no other `.cast(`/`.strptime(` hit in `packages/*/src`, `backend/src`). Readers of `_rejected`/`REJECT_REASON_COLUMN`:
  `validate.py` (`reject_rate`), `ingestion.py`, `dislocation_runs.py:170` (skips `_`-prefixed tables), `ingest.py`; the
  `rejected_rows` route returns the run's untyped `reject_sample`, so the new columns appear with no contract change.
  Row-changing steps implemented: `filter_rows`, `deduplicate` (removing); none adding. `IngestionRunRow` writers:
  `ingestion.py` (the one writer). Single alembic head at base, from the migration files: `f2b6d90a4c17`.
- **Commits:** limb (a) pricing-core (`prepare.py`, `ingest.py`; R2 set red at base: 5 failed, then 64 passed), limb (a)
  backend (`ingestion.py`, `models.py`, migration `5c8e3b71d094`), limb (b) (`validate.py`), spec (`01-data-management.md`
  FR-31 / FR-32 / VR-STR-2 / VR-STR-5 / §4.2 / §5.2), R4/R5, R8b.
- **Plan-wording note.** PL-1737 says R5's overall outcome is `warn`; the spec (01 §4.6, `overall: pass | pass_with_warnings |
  fail | error`) and the model enum say `pass_with_warnings`. Only the plan's wording is loose; R5 asserts
  `pass_with_warnings`.
- **Deviation.** `_reject_reason` quotes the value as it was before the failing step (equal to the source text unless an
  earlier step changed that column); the rejected row's cells are the input frame's own text, by column name, so a column
  renamed earlier appears under its source name.

## Guards (lists the recipes G5 is asserted for)

G1 `pricing-core` `test_an_empty_or_null_cell_is_null_not_a_coercion` and R6's second ingest; G2 `test_ingestion.py` required-null
reject and `test_data_jobs.py` unchanged; G3 `correct_schema` not touched; G4 `test_range_ignores_a_genuine_null…`; G5
`assert_row_identity` after every `test_data_jobs.py::_ingest` and in `test_ingestion.py` (required-null reject; the
`pseudonymise` recipe), plus R1/R3/R6/R7/R8a.

## DB window results

Granted window (lead, written, with its correction: no outer small-test flock). Tree `ac2849f0` plus the R8a test fix (own commit
after). Start 2026-10-18 23:25:16 BST, load1 2.26, available 25 GiB, gate-1 free. Own resources: Postgres `gip_test_1738`
(`createdb -T template0`, then `alembic upgrade head` rc 0, `e7c3a9b15d82 -> f2b6d90a4c17 -> 5c8e3b71d094`), redis db 13, MinIO bucket
`gip-test-blobs-1738`.

- **Run 1**, `run-small.sh` over `test_ingest_coercion.py`, `test_ingestion.py`, `test_data_jobs.py`: rc 1, `1 failed, 29 passed`.
  `FAILED backend/tests/test_ingest_coercion.py::test_the_identity_holds_on_the_g2_seed_recipe` — a **test defect**: the CSV
  had no `IDpol` column, so the seed recipe's `rename` raised `ColumnNotFoundError`. Fixed in the test (header gains `IDpol`).
- **Run 2**, `test_ingest_coercion.py` alone, same resources, start 23:26:35: rc 0, `7 passed`. With run 1, R1, R3, R4, R5, R6, R7,
  R8a, the G5 helper calls in the other two files, and the unchanged G2 tests are green.
- **Migration**, fresh `gip_mig_1738` (`-T template0`): `alembic upgrade head` rc 0, `downgrade -1` rc 0, `upgrade head` rc 0;
  `alembic_version` = `5c8e3b71d094`. Single head: `tests/test_repository_invariants.py` via run-small, `11 passed`.
- **Cleanup**: `redis-cli -n 13 dbsize` = 0 after FLUSHDB; bucket removed through the MinIO API (`mc rb --force`, rc 0) and
  `mc ls g/` lists `aud933-bucket`, `gip-bench-compiled-for`, `gip-bench-score-batch`, `gip-blobs`, `gip-test-blobs`, no
  `gip-test-blobs-1738`; `select count(*) from pg_database where datname in ('gip_test_1738','gip_mig_1738')` = 0. END 23:26:49 BST.
- **Reds at base for the backend set: not taken** (no base checkout run in a DB window); the pricing-core R2 set was red at base
  (5 failed). **R8b (the seed's run) is owed**: it needs the local stack, which is not granted.

## PRs

Recorded after the PR exists.

## Audit

Not yet.
