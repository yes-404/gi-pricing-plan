---
id: LG-8318
family: ledger
title: WK-1178 slice SL-8317 — FD-2001, scripts/bench-rating.py --http serves the login DSN (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-11-04
owner: executor
tree: 484b678730fe84ce827882d79459dcaf9dfb7b50   # sl-8317-fd2001-serve-dsn, the fix commit this was written against (base 181403d923a5ef7c5cde1533890421ebd1762b36)
slice: SL-8317
phase: P2
work: WK-1178
plans: [PL-8316]
corrected_by: []
relates: [FD-2001, FD-1729, PL-8316, FR-44, NFR-489]
---

# LG-8318 — WK-1178 slice SL-8317: `bench-rating.py --http` serves the login DSN

**GO:** to-lead "2026-11-04 16:42:29 GMT" (GO on PL 8316 / SL 8317; DP-1 (b), DP-2 (a), DP-3 (a); A1–A8 as proposed), amended by the entry of 2026-11-04 16:44:45 GMT (the seat runs on the evening of Wed 4 Nov; the gate is a separate SOLO seat after the executor's FINAL).
**MERGE-ACK:** (added at merge.)

## Tasks

### Scope

`PL-8316` (working id, written `PL 8316` in prose), "SL 8317 — FD-2001's fix: `scripts/bench-rating.py --http` serves the login DSN". Requirements: NFR-489 (the harness measures it; the new test carries its marker), FR-44 (read only — the refusal the harness now honours). Register: FD-2001 closes at the merge (A8, the mint's).

Rulings bound: DP-1 (b) `--serve-dsn`, default `os.environ.get("GIP_TEST_APP_DATABASE_URL")`, `parser.error` after parse when `--http` has no serve DSN, naming `--serve-dsn` and FD-1729; non-`--http` runs unchanged. DP-2 (a) `_seed` and `_measure_fetch` keep `--dsn` (the owner). DP-3 (a) the gate is a separate SOLO seat, not this executor's.

### Task list

1. **R1 — red first** (`f8e65afe`): `backend/tests/test_bench_rating_serve_dsn.py`, five tests, `pytestmark = pytest.mark.req("NFR-489")`, loading a `tmp_path` copy of the script (the `.bench-logs` trap). Acceptance: A2, A5.
2. **R2 — green** (`484b6787`): `scripts/bench-rating.py` only — parser, one `_serve(` call, `_serve`'s docstring, the module usage block. Acceptance: A3, A4, A5.
3. **Draft this ledger** (this commit). Acceptance: A1, A6.

### Gate

Not run by the executor (DP-3 (a)): the full SOLO gate, both halves, runs in a separate seat at the re-merged head. Owed. `ruff` and the small runs below were run on the executor's own tree.

**Small runs, DB-free, via `~/gi-pricing-plan.local/handover/run-small.sh <wt> <file>`, tree `sl-8317`, load1 < 2 at each start, dead-port DB/redis URLs:**

| Run | Head | Result |
|---|---|---|
| R1 red, `test_bench_rating_serve_dsn.py` | `181403d9` base script (new test uncommitted) | `4 failed, 1 passed, 2 warnings in 1.64s`, rc=1 |
| R2 green, `test_bench_rating_serve_dsn.py` | `f8e65afe` + the fix (working tree, then `484b6787`) | `5 passed, 2 warnings in 1.02s`, rc=0 |
| `test_bench_rating_calls.py` (unedited, A4) | same | `1 passed, 2 warnings in 0.39s`, rc=0 |
| `test_bench_rating_header.py` (unedited, A4) | same | `3 passed, 2 warnings in 0.96s`, rc=0 |
| `ruff check` on `scripts/bench-rating.py` and the new test, via `run-heavy.sh` | `484b6787` | `All checks passed!`, rc=0 |
| `ruff format --check`, the new test | `484b6787` | `1 file already formatted`, rc=0 |
| `ruff format --check`, `scripts/bench-rating.py` | `484b6787` | `1 file would be reformatted`, rc=1 — **pre-existing**: the base file at `181403d9` gives the same result; not reformatted, because a reformat would widen the diff past the Write set |

**A5, `.bench-logs`:** `ls -la <wt>/.bench-logs` printed `ls: cannot access '…/.bench-logs': No such file or directory` before and after the red run and before and after the green runs (identical).

**A6, the GREEN set:** the script is imported by no module of `backend/` or `packages/`; the three files that load it by path are the `test_bench_rating_*` files named above, and all three are in the table. No other hit.

### Audit

(The auditor's, at slice close.)

### Build log

- 2026-11-04 17:31 UTC — R1: the new test file, red at the base. Red lines quoted from the log `head=181403d923a5ef7c5cde1533890421ebd1762b36` … `rc=1`:
  - T1 `test_http_sweep_serves_the_login_dsn_and_seeds_with_the_owner_dsn`: `E       AssertionError: ['postgresql+asyncpg://owner-sentinel@localhost/db']` / `At index 0 diff: 'postgresql+asyncpg://owner-sentinel@localhost/db' != 'postgresql+asyncpg://login-sentinel@localhost/db'` — `_serve` got the OWNER sentinel (the cause, A2).
  - T2 `test_serve_dsn_option_parses`: `bench-rating.py: error: unrecognized arguments: --serve-dsn postgresql+asyncpg://login-sentinel@localhost/db`, `SystemExit: 2` (A2).
  - T3 (default from the env variable): `AttributeError: 'Namespace' object has no attribute 'serve_dsn'`.
  - T3 (`--http` with no serve DSN refused): `_StopError` — the base run reaches `machine()` instead of refusing at parse time.
  - T3 (no `--http`, no serve DSN): passes at the base — the unchanged-behaviour guard.
  - Summary: `4 failed, 1 passed, 2 warnings in 1.51s`, rc=1.
  - Committed alone as `f8e65afe`.
- 2026-11-04 17:33 UTC — R2: the fix, `484b6787`. `--serve-dsn` beside `--dsn`; `parser.error` naming `--serve-dsn` and FD-1729 when `--http` has none; `_run_http_sweep`'s one `_serve(` call passes `dsn=args.serve_dsn`; `_serve`'s docstring and the module usage block say the DSN is the login DSN. `_seed` and `_measure_fetch` calls unchanged.
- **A1, the write set:** `git diff --name-only 181403d9 HEAD` at the head that carries this ledger: `backend/tests/test_bench_rating_serve_dsn.py`, `docs/ledgers/LG-08318-wk-1178-slice-sl-8317-fd-2001-bench-rating-http-serves-the-login-dsn-slice-ledger.md`, `scripts/bench-rating.py`.

- **audit-docs** (`run-heavy.sh --light`, tree `sl-8317` at the commit before this ledger's own, log first line `head=484b678730fe84ce827882d79459dcaf9dfb7b50` … `rc=1`): `FAILED (2):` (1) `check 31: gap in the full allocation between 2002 and 8316` — the working ids PL 8316, SL 8317, LG 8318, expected until the mint; (2) `check 39: docs/INDEX.md is stale against a fresh regeneration (2186 governed record(s))` — this ledger is a new governed record and `docs/INDEX.md` is regenerated at the mint, not by the executor (the brief). The check 32 lines naming LG-8318 and SL-8317 (`does not resolve in docs/INDEX.md`) are the same cause. No other failing line.

## PRs

(Owed at the PR: number, title, merge commit. Branch `sl-8317-fd2001-serve-dsn`, unpushed at this entry.)
