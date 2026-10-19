---
id: LG-1822
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

# LG-1822 — WK-1178 slice SL-1738: FD-1744, limb (a) the coercion and limb (b) the blind validation

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
- **Reds at base for the backend set (Task 1/2), taken.** Detached worktree at `84b0ff5765e55bc8edd139cd22bb57cd474de807` with only
  `backend/tests/test_ingest_coercion.py` copied in (the G5 helper calls in the other two files were not copied: they need the same
  file's helper and are covered by the head run). Own DB `gip_test_1738b` (`-T template0`, `alembic upgrade head` at base head
  `f2b6d90a4c17`, rc 0), redis db 13, bucket `gip-test-blobs-1738b`; start 2026-10-18 23:28:19 BST, load1 2.96, available 23 GiB.
  `run-small` rc 1, `7 failed`, each for its stated cause:
  - R1 `test_unparseable_cells_are_quarantined_with_their_source_text`: `assert ['policy_exposure'] == ['policy_exposure', '_rejected']`
    (no `_rejected` table).
  - R6 `test_a_null_after_ingest_is_a_source_null_and_nothing_else`: `assert 2 == 0` (`null_count` of `claim_amount` is the bad-cell count 2).
  - R3 `test_a_later_step_cannot_launder_a_coercion`: `assert ['p1', 'p2', 'p3', 'p4', 'p5'] == ['p1', 'p4']` (`fill_null` resurrects the bad rows).
  - R7 `test_the_identity_holds_through_a_row_removing_step`: `assert ['p1', 'p5'] == ['p1']` (the clean-table assert precedes the
    step-count assert here, so it is the first to fail; `p5`'s bad date is nulled and kept; the step-count assert is not reached).
  - R8a `test_the_identity_holds_on_the_g2_seed_recipe`: `AttributeError: 'IngestionRunRow' object has no attribute 'step_counts'`.
  - R4 `test_validation_fails_a_version_whose_cells_were_quarantined`: `assert <OverallOutcome.PASS: 'pass'> is <OverallOutcome.FAIL: 'fail'>`.
  - R5 `test_the_declared_severity_decides_without_reject_rate`: `assert <OverallOutcome.PASS: 'pass'> is <OverallOutcome.PASS_WITH_WARNINGS: ...>`.
  Cleanup: `redis-cli -n 13 dbsize` = 0; bucket removed through the MinIO API, `mc ls g/` shows no `gip-test-blobs-1738b`; `pg_database`
  count for `gip_test_1738`, `gip_mig_1738`, `gip_test_1738b` = 0; `docker inspect` of postgres, redis, minio and keycloak shows no bind
  source under the base worktree (0 matches); worktree removed.
- **idsweep** (`idsweep.sh origin/sl-1738-wk1178-fd1744-coercion`), whole output: `main: 1818 pairs; duplicate numbers: ` /
  `CROSS-BRANCH (same number, different id): ` — both empty. **req-coverage** (`scripts/req-coverage.py`, rc 0): `FR-31  6 test file(s)`,
  `FR-32  26 test file(s)`, `FR-46  19 test file(s)`; VR-STR-2 is not a marker id in this suite (the markers carry FR-32 and FR-45).
- **OWED, R8b** (needs the local stack; the gate's demo stage runs it): `GIP_REDIS_URL=redis://localhost:6379/<slot db> uv run --directory <wt> pytest -q examples/fremtpl2/test_seed.py -k test_every_seeded_ingestion_run_balances_its_rows -s`
  (skipped by its fixture unless `examples/fremtpl2/data/*.arff` is fetched and Postgres/MinIO are up); it must print one
  `run: <read> - <rejected> - <removed> + <added> == <written>` line per run, including the portfolio's `20000 - 0 - 0 + 0`-shaped line
  whose `rows_written` is 19985.

## PRs

Recorded after the PR exists.

## Audit

Pre-PR slice audit by `auditor-1738` (sonnet), 2026-10-19 01:11 BST, range `origin/main...HEAD` with `origin/main` =
`1fca3fc85710bdb19aab00efe7b9bf361d571a23`. **Tree audited:** HEAD `0fbea8ad2e141be0fca248ca3f83dff4dd61a1b0`, tree
`117a911d718db15a846d1ef0bbb5be6c4b4e3a6c`. **Gate of record:** `68bd622c2f59e42686545db691d61fb2c156596c`, tree
`c1881612b13b9994476c5ea889598fc62794d112`. Between them only the merge `7354ff9d` (main `1fca3fc8`), INDEX `bf8459c9`, the
mint `c5d1b9ea` and INDEX `0fbea8ad`; `git diff --name-only 68bd622c HEAD | grep -vE '^docs/'` prints only
`backend/migrations/versions/f2b6d90a4c17_…py` (docstring only), `backend/tests/test_bandings_downgrade_refusal.py` and
`deploy/README.md`, all from main, none this slice's. This audit proposes; the verdict is the lead's. No `status:` line was changed.

**A. Plan → evidence (PL-1737, Tasks 0–7 and Acceptance 1–15).** Reachability: `for s in $(git log --no-merges --format=%h
origin/main..HEAD); do git merge-base --is-ancestor $s HEAD; done` → rc 0 for all 12 (35eb8186, 119306ab, 05d5727c, 222ce881,
581681e0, ac2849f0, 662bd6b3, 422a57ec, 68bd622c, bf8459c9, c5d1b9ea, 0fbea8ad).

| Plan item | Evidence | Result |
|---|---|---|
| T0 step 3 / Acc 11 (G2 probe before code) | LG "Task 0 Step 3"; activation 35eb8186 and probe precede 119306ab | met; the LG output is condensed, not one line per column (F3) |
| T0 step 2 enumeration | LG "Task 0 Step 2"; `git grep -nE "strict=False" -- 'packages/*/src' backend/src \| grep -E '\.cast\(\|strptime'` at HEAD → empty | met |
| T1 R1 / Acc 4 | `test_ingest_coercion.py::test_unparseable_cells_are_quarantined_with_their_source_text`; base red `assert ['policy_exposure'] == ['policy_exposure','_rejected']` (LG) | met |
| T1 R6 / Acc 5 | `::test_a_null_after_ingest_is_a_source_null_and_nothing_else`; base red `assert 2 == 0` | met |
| T1 R3 / Acc 7 | `::test_a_later_step_cannot_launder_a_coercion`; base red `['p1','p2','p3','p4','p5'] == ['p1','p4']` | met |
| T1 R2 + completeness + step-count / Acc 6 | `packages/pricing-core/tests/test_prepare.py` (req FR-32, lines 349–452); LG "R2 set red at base: 5 failed, then 64 passed" | met |
| T1 G1 | `test_an_empty_or_null_cell_is_null_not_a_coercion` and R6's second ingest | met |
| T1 R7 / Acc 14 | `::test_the_identity_holds_through_a_row_removing_step`; base red `['p1','p5'] == ['p1']` (first assert differs from the plan's "no step counts"; LG says why) | met |
| T1 R8a / Acc 15 | `::test_the_identity_holds_on_the_g2_seed_recipe`; base red `AttributeError … 'step_counts'` | met |
| T1 R8b / Acc 15 | `examples/fremtpl2/test_seed.py::test_every_seeded_ingestion_run_balances_its_rows`; run `…/scratch/sl1738-r8b/r8b.log`: `run: 678013 - 0 - 0 + 0 == 678013`, `run: 678013 - 0 - 571 + 0 == 677442`, `run: 20000 - 0 - 15 + 0 == 19985`, `1 passed, 16 deselected`, rc 0, on head 68bd622c tree c1881612 | met (the LG still lists it as OWED, F4) |
| T2 R4 / Acc 8 | `::test_validation_fails_a_version_whose_cells_were_quarantined`; base red `PASS is FAIL` | met |
| T2 R5 / Acc 9 | `::test_the_declared_severity_decides_without_reject_rate`; base red `PASS is PASS_WITH_WARNINGS` (plan's "warn" is the enum `pass_with_warnings`, noted in the LG) | met |
| T2 G4 | `test_validate.py` `test_range_ignores_a_genuine_null…` (req FR-32, line 575–605 block) | met |
| T3 / Acc 3 (spec) | see C; ordering F1 | met, ordering deviates |
| T4 / Acc 12 | `ingest.py:248-249` define the two literals once; `validate.py` and `prepare.py` import them; tests spell them | met for `src`; F2 for the plan's predicate |
| T5 / Acc 4, G3 | `ingestion.py` diff: `PreparationResult` kept, `_quarantine()` concat, `step_counts` written; `correct_schema` and `data_handlers.py` absent from `git diff --stat` | met |
| T5 migration | see D | met |
| T6 | `validate.py` `_coerced_cells`, `dtype_match` and `date_parsed` report `coerced_cells`; `range` and `reject_rate` untouched; unit tests `test_validate.py` (req FR-32) | met; no recorded base-red for these two unit tests (F4) |
| G2, G5 | `test_data_jobs.py::_ingest`, `test_ingestion.py` (required-null reject, `pseudonymise` recipe) call `assert_row_identity`; LG "Guards" lists them | met |
| T7 / Acc 13 | gate rows, see F; wf-699 journey `demo.py --journey wf-699 rc=0`. No SL-1543 re-run record in the LG | met for wf-699; SL-1543's test file is not on this tree, carried to whichever merges second |

**B. FD-1744's limbs.** FD file `docs/findings/FD-01744-…` quotes the 12:02:46 ruling (a) the coercion, (b) the blind validation.
Limb (a): fix `119306ab` + `05d5727c`; red-first R1/R3/R6/R7/R8a/R2 per the table (seven backend reds at base,
`7 failed`, each for its stated cause, LG "Reds at base"). Limb (b): fix `222ce881`; red-first R4/R5 (backend, at base) and
`test_validate.py` units (no separate base record, F4).

**C. Spec amendments.** `git diff origin/main...HEAD -- docs/specs`: FR-31 and FR-32 cells keep their sentences and gain an
*(Amended 2026-10-18 …)* clause each; VR-STR-2 and VR-STR-5 rows gain dated clauses (`coerced_cells`, no tolerance); a dated §4.2
block names `_reject_reason`, `_reject_column`, `_reject_step`; a dated §5.2 comment. No id added, renumbered or struck; no
other spec file touched. Markers: FR-31, FR-32 and FR-46 carry the new tests (`grep -n "mark.req" -- <the five test
files>`); gate `req-coverage` rc 0.

**D. Migration `5c8e3b71d094`.** `down_revision = "f2b6d90a4c17"` (the sole earlier head, the file is the only revision naming it);
`upgrade` adds JSONB NOT NULL default `'[]'`, `downgrade` drops the column. Single head: `tests/test_repository_invariants.py::
test_the_migration_chain_has_exactly_one_head` is not among the gate's 13 FAILED ids (a quick regex of mine listed a second
"head" `a1b2c3d4e5f6`, an artifact of my parser on multi-parent revisions, not used as evidence). Docstring against FR-416 as
amended (07-platform.md:110): it is a plain reversible migration (it introduces no append-only artifact data), the docstring
states the downgrade drops the column and that every figure is recomputable from the stored recipe (FR-41); it does not use the
word "reversible" (F5). The LG records `upgrade head`, `downgrade -1`, `upgrade head` all rc 0 on a fresh DB.

**E. Shapes and money.** `git grep -n -E "step_counts|IngestionRun" -- packages/model-schema docs/contracts` → empty: no
model-schema shape for the run exists to duplicate, and `step_counts` is `list[dict[str, Any]]` like `reject_sample` beside it
(plan: no model-schema change). New fixtures are Polars/CSV literals in the tests, not API shapes. No money type touched.

**F. Gate rows** (`/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl1738-gate/`, tree c1881612). `diff <(grep -E '^FAILED'
…/sl1274-regate/pytest.log | cut -d' ' -f2 | sort) <(grep -E '^FAILED' …/sl1738-gate/pytest.log | cut -d' ' -f2 | sort)` → empty
(rc 0), 13 ids on each side, all in the check-31 / audit-docs class; `13 failed, 6479 passed, 18 skipped`. ruff, mypy,
import-linter, contracts, req-coverage rc 0; audit-docs rc 1 with `FAILED (1): check 31: gap in the full allocation between 1818
and 8128` only (the working id, now minted); demo `--journey wf-699` rc 0, D7 `ok 19985 policies in the sample`, zeros `own-DB
count=0 redis RT db 1 dbsize=0 redis RD db 3 dbsize=0`. In that gate the R8b row printed `FAIL: …/examples/fremtpl2/data already
exists, not touched` (a fixture precondition, not a test result); the separate R8b-only run (`sl1738-r8b`, head 68bd622c, tree
c1881612) passed: `1 passed, 16 deselected`, 0 pytest skips or errors (the three "skipped" lines in its log are the validation
report's `skipped vehicle-brand-mix`), sha256 of both `.arff` files MATCH `fetch.py`.

**G. This ledger.** Rulings cited by stamp (22:50:32 GO; 12:02:46, 12:23:36, 12:31:22, 12:42:55). `git grep -n -E 'LG[ -]0?8128'`
at HEAD → no hit (the body sentence now reads "Working id (lead-reserved)."): the mint re-pointed every cite. R8b OWED is
discharged by the run in F but the LG body still says OWED (F4).

**Docs checks at HEAD (one gate-2 flock block, gate-1 and gate-2 free beforehand):** `doc-index.py --check` rc 0 (INDEX.md
byte-stable); `audit-docs.py` rc 0 (no FAILED block); `register-lint.py` rc 0 (0 violations; residue line 263 of 325, not a
violation).

**Findings (all proposals to the lead):**

- **F1 (low).** Acceptance 3 says the spec clauses land "before or with the code, never after". `git log --format='%h %aI %s'
  origin/main..HEAD -- docs/specs/01-data-management.md` shows `581681e0` (22:06:00Z) after the three code commits `119306ab`
  (22:01:25Z), `05d5727c` (22:03:12Z), `222ce881` (22:04:12Z). One PR, squash-merged, so the merged tree has spec and code
  together; propose *accept* with this line as the record.
- **F2 (low).** Acceptance 12's predicate (`git grep -nE '"_reject_(column|step)"' -- packages backend/src`) also prints test
  literals (`test_prepare.py:346,361,…`, `test_validate.py:564,565,599`). `src` defines each literal once (`ingest.py:248-249`)
  and imports it elsewhere. Propose *accept* (the plan's predicate was wider than its intent) or have the tests import the constants.
- **F3 (low).** Acceptance 11 wants one verbatim line per cast column and population; the LG prints a condensed form with
  "(each of the 9 NUMERIC columns) nulled_by_cast=0". Counts are zero on both populations and the identity lines match
  (`678013 - 0 - 571 + 0 == 677442`, `20000 - 0 - 15 + 0 == 19985`), so no STOP is implied.
- **F4 (low, ledger completeness).** The LG does not yet carry: the R8b printed lines (it says OWED), the gate rows, a base-red
  line for the `test_validate.py` unit tests of `dtype_match`/`date_parsed`, or the Task 7 SL-1543 re-run note. Evidence for the
  first two is in F above; propose the lead's closing acts add or cite it.
- **F5 (info).** The migration's `Create Date` (`2026-10-18 23:40:00 +00:00`) is later than its commit (`05d5727c`,
  22:03:12Z); metadata only. Its docstring never says "reversible" in so many words, though it describes the downgrade.
- **Observation.** `_coercion_failures` builds `pl.Series([False] * before.height)` per parsing step (a Python list of the table
  height); the 678 013-row seed ran through the gate's demo without issue, so it is noted, not a finding.

No requirement is left without evidence, so no §13 verdict on an unevidenced requirement is proposed. **Proposed overall: CLEAN
with F1–F5 low/info, none blocking.**
