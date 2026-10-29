---
id: LG-8279
family: ledger
title: WK-1178 slice S1d — FD-1965, the seed fixture migrates its own scratch database, red first (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-10-29
owner: executor
tree: 1e17ec6382de5919b6e3011242b584a59bb880e7   # origin/main at S1d's branch cut (#1407)
slice: SL-8278
phase: P2
work: WK-1178
plans: [PL-1927]
corrected_by: []
relates: [FD-1965, PL-1927, FR-31, FR-32]
---

# LG-8279 — WK-1178 slice S1d: FD-1965, the seed fixture migrates its own scratch database, red first

Working ids (space form in prose): **SL 8278** (this slice), **LG 8279** (this ledger). Executor seat
`exec-s1d`. Nothing is minted here.

**GO:** the lead's brief `brief-exec-s1d-2026-10-30.md`, pulled forward to Thu 2026-10-29 by to-lead
"2026-10-29 18:47:25 GMT"; authority PL-1927 row 6 (S1d), accepted at to-lead "2026-10-29 17:32:19 GMT".
**MERGE-ACK:** pending.

## Tasks

### Scope

PL-1927 "Delta, row 6 (S1d) — FD-1965: the seed fixture migrates its own scratch database (test-only,
red-first)" at `origin/main` `1e17ec63`: Tasks S1d-0 to S1d-7, Evidence E-d1 to E-d6, Acceptance d1 to
d10. The row is the scope; it is not restated here. Requirements: none amended (markers FR-31, FR-32
exist on the three tests). Write set: `examples/fremtpl2/test_seed.py`,
`backend/tests/test_transformations.py` (format only, its own commit), this ledger, the SL row,
FD-1965's close.

### Task list

- [x] **S1d-0. Base.** See the Build log, entry 1.
- [x] **S1d-1. The throwaway checkout.** See the Build log, entry 1.
- [x] **S1d-2. Reds R1 to R3** (DB window; Build log, entry 2).
- [x] **S1d-3. The fix** (DP-S1d-1 (a)); commit `c44fa2d7`.
- [x] **S1d-4. Control C1** and its mutation red; commit `e7244a2a`.
- [x] **S1d-5. Greens G1 and G2** (DB window; entry 2).
- [x] **S1d-6. The format commits, then the gate** (DP-S1d-2 G2 narrow cover; entries 3, 4, 6).
- [x] **S1d-7. Records** (less the mint, which is the lead's).

### Gate

Pending (S1d-6).

### Audit

Pending (the auditor's).

### Build log

1. **2026-10-29, Phase A (DB-free).** Base `origin/main` = `1e17ec6382de5919b6e3011242b584a59bb880e7`
   (merge 38, #1407), read by `git ls-remote origin refs/heads/main`.
   - S1d-0: `git diff --name-only 7ceff4a1..origin/main -- examples/ backend/migrations/` prints
     nothing (rc 0): E-d1 to E-d4 hold as the row states (read at the base: `env.py:31–38`,
     `test_seed.py` `scratch_seed`, `seed.py:448–466`).
   - E-d6 format check at the base, `head=1e17ec63`: `git show origin/main:backend/tests/test_transformations.py
     | uv run ruff format --check --stdin-filename backend/tests/test_transformations.py -` rc=1, so
     S1d-6's format commit is owed.
   - S1d-1: throwaway detached worktree of the base at `~/gi-pricing-plan.local/scratch/s1d/tw`
     (outside the slice worktree), `uv sync --all-packages --frozen` rc=0; the two `.arff` copied into
     **its** `examples/fremtpl2/data/` only, sha256 equal to the pins in `fetch.py`.

2. **2026-10-29, Phase B (the DB window, the lead's written start 18:53 GMT; START 18:53:21, END
   19:02:46).** START: load1 1.09, `free -g` available 19, slots gate-1, gate-1b, gate-2 (read HELD for
   about 15 s at 18:53:25, then free), small-test, verify-1, demo, seat-heavy free; `select datname`
   = `gipricing postgres template0 template1`; the template `gipricing` non-empty tables exactly
   `alembic_version=1 environments=3 tenant_marker=1`. `scratch_s1d_foreign` made by
   `create database … template gipricing`; no URL set by the seat names `gipricing`; redis db 11.
   Logs are under `~/gi-pricing-plan.local/scratch/s1d/` (`red.log`, `o1.log`, `c1.log`, `green.log`).
   - **R1 to R3 (red, `head=1e17ec6382de5919b6e3011242b584a59bb880e7`, throwaway, data present,
     `GIP_MIGRATION_DATABASE_URL` on `scratch_s1d_foreign`):**
     `FAILED examples/fremtpl2/test_seed.py::test_the_seed_reruns_against_a_seeded_database`,
     `FAILED examples/fremtpl2/test_seed.py::test_every_seeded_ingestion_run_balances_its_rows`,
     `FAILED examples/fremtpl2/test_seed.py::test_a_small_seed_is_refused_for_its_degenerate_fit`;
     `3 failed in 36.99s`, `rc=1`; each by `UndefinedTableError: relation "role_assignments" does not
     exist`. Foreign `select count(*) from workspaces where name = 'freMTPL2 demo'`: before 0, after 3
     (the E-d3 red).
   - **O1** (variable unset, one test, same base): fails at the fixture,
     `subprocess.CalledProcessError: Command '['uv', 'run', 'alembic', 'upgrade', 'head']' returned
     non-zero exit status 1`, `rc=1`. (env.py's RuntimeError text was not captured in the tail.)
   - **Fix and C1** (S1d-3, S1d-4; slice head `e7244a2a3f63e81841db58105527ee8cff70f9d9`, synced into
     the throwaway): C1 green `1 passed in 0.87s` (no database, no data). Guard mutated once (`if
     missing:` replaced by `if False and missing:`, assert count 1): `Failed: DID NOT RAISE
     RuntimeError`, `1 failed in 0.95s`. Restored: `1 passed in 0.86s`.
   - **G1** (`head=e7244a2a…`, the three, same foreign URL set): `3 passed in 216.19s`, `rc=0`; foreign
     demo count 3 before, 3 after. **G2** (variable unset): `3 passed in 202.44s`, `rc=0`; foreign count
     3 after.
   - **END:** `scratch_s1d_foreign` dropped; `select datname` after = before; no `scratch_s1d_*` (count
     0); template non-empty tables after `alembic_version=1 environments=3 tenant_marker=1`; redis db
     11, 12, 13 `dbsize` 0 after FLUSHDB. `git status --ignored -- examples/fremtpl2/data` in the slice
     worktree: nothing.
   - (Recorded 2026-10-29 by the lead, on to-lead "2026-10-29 18:57:05 GMT": a foreign createdb/dropdb of
     scratch_beatgate_guard (another seat's gate-script guard proof, under the lead's brief) occurred inside
     this window between 18:54 and 18:56. No scratch_s1d_* database was touched. The END datname list is
     compared against START excluding it; it was dropped before END.)
   - O1 gap, accepted by the lead (to-lead "2026-10-29 19:03:34 GMT" ruling (2)): env.py's `RuntimeError`
     text was cut from the captured stderr (tail), and there is no second window.
3. **2026-10-29, Phase C start.** S1d-6 format commit `5d8c2649`
   (`style(backend): ruff format backend/tests/test_transformations.py (process-backlog 2026-10-29
   14:44 GMT)`), alone. `ast.dump` equality: script `~/gi-pricing-plan.local/scratch/s1d/astdump.py`
   (sha256 of `ast.dump(ast.parse(source))`), before = after =
   `8b753a2242991fbf1e14ec472c8310f4826bdcc39d4a4c6cfe11d896c578e35a`.
   G2 precondition: `git diff --stat origin/main...HEAD` lists only `backend/tests/test_transformations.py`,
   `examples/fremtpl2/test_seed.py` and the ledger under `docs/`. `uv run ruff check .` rc=0 at
   `5d8c2649`. `examples/fremtpl2/test_seed.py` through `scripts/run-small.sh`, no data present (CI
   form): `15 passed, 3 skipped in 11.45s`, `rc=0`, `head=5d8c2649f009a5260fb92a39dc4bde2ef440353f`.
   **Open (reported to the lead):** `ruff format --check examples/fremtpl2/test_seed.py` reads rc=1 at
   the base `1e17ec63` over six pre-existing hunks outside this slice; acceptance d7 awaits the lead's
   ruling.
4. **2026-10-29, Phase C (ruling (A), the maintainer's, to-lead "2026-10-29 19:03:34 GMT").** Second
   named format commit `e9d5d6fe` (`style(examples): ruff format examples/fremtpl2/test_seed.py`), that
   file alone, after the fix and C1 commits. `ast.dump` equality, same script `astdump.py`: before = after =
   `65ec15eceb97ded8c97b3f784c47a0883cae8b81d14473e171b91970e0bb7587`. `uv run ruff format --check
   examples/fremtpl2/test_seed.py backend/tests/test_transformations.py` rc=0 ("2 files already
   formatted"). G1, G2 and C1 ran at `e7244a2a`, before this AST-equal commit. Per file, `git log
   --format=%s origin/main..HEAD -- <file>`: `backend/tests/test_transformations.py` prints exactly one
   subject (`style(backend): ruff format backend/tests/test_transformations.py (process-backlog
   2026-10-29 14:44 GMT)`); `examples/fremtpl2/test_seed.py` prints three (`style(examples): ruff format
   examples/fremtpl2/test_seed.py`, `test(examples): control C1 …`, `test(examples): the seed fixture
   migrates and seeds its own scratch database (FD-1965)`).
5. **2026-10-29, process-backlog row**, its own docs commit (the lead's instruction): "A DB window is
   single-tenant on the shared server" (`docs/process/process-backlog.md`, owner the lead).

## PRs

None yet (the lead opens the PR).
