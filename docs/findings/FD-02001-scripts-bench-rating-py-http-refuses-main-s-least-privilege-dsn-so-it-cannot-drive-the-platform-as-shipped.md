---
id: FD-2001
family: finding
title: scripts/bench-rating.py --http refuses main's least-privilege DSN, so it cannot drive the platform as shipped
status: closed
created: 2026-11-04   # drafted 2026-11-04 under working id 8312
owner: auditor
tree: db92a7bc0424059ed0aff4e5cebf445661c3be81   # origin/main when read
corrected_by: []
relates: [WK-1178, FD-1729, LG-1760, PL-1454, SL-2005, LG-2006, PL-2004]
---

# FD-2001 — scripts/bench-rating.py --http refuses main's least-privilege DSN, so it cannot drive the platform as shipped

## Finding

**LOW, owner WK-1178.** `scripts/bench-rating.py --http` starts the application as a subprocess
(`_start_server`, `scripts/bench-rating.py:898-925`) with `GIP_DATABASE_URL` set to the harness's
`--dsn` (`:918`), the DSN `--dsn` takes from `GIP_TEST_DATABASE_URL` (`:1097-1099`). The application's
startup now calls `await database.assert_least_privilege()` (`backend/src/app/main.py:114`, FR-44,
FD-1729), which raises `LeastPrivilegeError` (`backend/src/app/db/immutability.py:39`, raised at
`:176`) for a process connected as an owner or a superuser. The harness's DSN is the owner's, so the
`--http` mode cannot start the platform as shipped. Wording and authority: the maintainer's entry
"2026-11-04 09:51:05 GMT" in `to-lead.md` (a local channel file): "The defect itself — `scripts/bench-rating.py --http` refuses main's least-privilege DSN (FD-1729's main.py:114) and so cannot drive the platform as shipped — is an FD, LOW, owner WK-1178, filed in the same docs PR".

## Evidence

The lines cited above, read at the tree `db92a7bc0424059ed0aff4e5cebf445661c3be81`; the record that
the nfr-bench-1 driver C' (`bench-c-nfr489-ladder.py`, `LG-1760`) takes the `--serve-dsn` route
instead is the same entry. Not re-run by the auditor: no database window is open.

## Severity

**LOW.** A measurement harness, not the platform; no price, no data and no security property is
affected. It costs a measurement route: `--http` readings for NFR-489 and its siblings cannot be taken
by this script until it passes the application a least-privilege DSN.

## Disposition

Open, owner WK-1178, **fix before close with an owner**. Fixed before P2 close if a gate slot frees
before Tue 10 Nov 2026, else carried to P3 with the C' driver as the interim harness (the maintainer's
"2026-11-04 09:51:05 GMT"). The event that next discharges it: the merge of the harness fix, or the
P3 plan review if carried. Filed under working id 8312 (minted as FD-2001).

***Resolved 2026-11-04*** — closed in place 2026-11-04 by the auditor, as the closing act of the audit of SL-2005 (WK-1178, LG-2006, PL-2004; this PR, its number and squash written at the merge's date-of-record), on the lead's brief under the maintainer's "2026-11-04 17:42:08 GMT" ruling (A8 (a), the FD-1842 form) and the GO "2026-11-04 16:42:29 GMT" (`to-lead.md`, a local channel file). Delivered remedy: `scripts/bench-rating.py` gains `--serve-dsn`, the application's least-privilege login DSN, defaulting to `$GIP_TEST_APP_DATABASE_URL`; `--http` without one is refused at parse time (`parser.error` naming `--serve-dsn` and FD-1729); `_run_http_sweep` passes it to `_serve`, and the owner DSN (`--dsn`) only seeds and times `_fetch_bundle` in-process (DP-1 (b), DP-2 (a)). No platform code changed. Red first, by cause, in LG-2006: at base `181403d9` the new test file gave `4 failed, 1 passed`, T1 failing with the OWNER DSN reaching `_serve` and T2 with `unrecognized arguments: --serve-dsn` (exit 2); green `5 passed`, with `test_bench_rating_calls.py` and `test_bench_rating_header.py` unedited and passing. Gate evidence is in LG-2006: the SOLO gate at `c726f68a` (pytest "13 failed, 7133 passed, 22 skipped" = the 13 item-31 docs-audit failures only; frontend all rc 0; demo designed stop 2037 s, dislocation #1 579 s), accepted under item 31.
