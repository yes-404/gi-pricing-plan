---
id: FD-1965
family: finding
title: the examples seed fixture migrates whatever `GIP_MIGRATION_DATABASE_URL` names, not its own scratch database, since #1398
status: active
created: 2026-10-29               # drafted 2026-10-29 under working id 8277
owner: WK-1178
tree: e239733c1477c5ab0e8d4c897638767cb4c3e0b9   # origin/draft/s1c-fd1951 as read by the auditor, 2026-10-29
corrected_by: []
relates: [FD-1951, SL-1962, LG-1964, SL-8278, LG-8279]
---

# FD-1965 — the examples seed fixture migrates whatever `GIP_MIGRATION_DATABASE_URL` names, not its own scratch database, since #1398

## Finding

**MEDIUM; owner WK-1178; fix slice SL 8278 / LG 8279, Fri 30 Oct 2026 am, test-only, red-first.** Authority: the lead's
"2026-10-29 14:21:02 GMT" (2'). Filed under working id 8277.

Since #1398 (S1a), `backend/migrations/env.py:32–38` migrates only the URL in `GIP_MIGRATION_DATABASE_URL` and raises when it is
unset; it no longer falls back to `GIP_DATABASE_URL`. The fixture `scratch_seed` (`examples/fremtpl2/test_seed.py:138–158`)
creates its own scratch database (`CREATE DATABASE scratch_sl1409c_<hex>`, admin URL hard-coded), sets **only** `GIP_DATABASE_URL`
to it, and runs `uv run alembic upgrade head` with `env=dict(os.environ)`. The migration therefore runs against whatever
`GIP_MIGRATION_DATABASE_URL` the process inherits — or fails if it is unset — and **never against the scratch database**. In a
run where the variable names another database, that database is migrated (a no-op if already at head) and the scratch database
stays empty.

## Evidence

- `backend/migrations/env.py:32–38`: `_migration_url = load_settings().migration_database_url`; `if _migration_url is None: raise
  RuntimeError("GIP_MIGRATION_DATABASE_URL is not set ...")`.
- `examples/fremtpl2/test_seed.py:138–158`: `monkeypatch.setenv("GIP_DATABASE_URL", url)` only; no `GIP_MIGRATION_DATABASE_URL`.
- `scratch/s1c-gate/s1c-gate.sh:72`: the gate exports `GIP_MIGRATION_DATABASE_URL=…/gipricing_s1c_gate`, so the fixture's
  `alembic upgrade head` migrated the (already at head) gate database, a no-op (LG-1964 "Gate exception", `pre-upgrade.log`).
- The gate's three failures, `pytest.log` at head `eb64354f`: `examples/fremtpl2/test_seed.py::test_a_small_seed_is_refused_for_its_degenerate_fit`,
  `::test_every_seeded_ingestion_run_balances_its_rows`, `::test_the_seed_reruns_against_a_seeded_database`, each
  `UndefinedTableError: relation "role_assignments" does not exist`. They ran, rather than skipping, because the `.arff` files were
  present in the gate worktree (13 skipped, below the baseline of 21).
- The proof at `origin/main` `18728e68` (from-lead "2026-10-29 14:29:50 GMT"; LG-1964 "Gate exception"): with
  `GIP_MIGRATION_DATABASE_URL` naming an at-head database and the `.arff` files present, the same three tests fail with the same
  line at main, with no S1c code, "3 failed". The failure is main's, not S1c's.

## Severity

**MEDIUM.** Test-only: no production code path, price or hash moves. It is a latent red on main: the three tests skip when the
`.arff` data is absent (CI, fresh clones) and fail whenever the data and a Postgres are present, so they were not exercising the
seed on any gated run since #1398, and the S1c gate read 3 spurious reds that the named exception had to carry.

## Remedy

SL 8278 / LG 8279 (Fri 30 Oct am, test-only, red-first): the fixture also sets `GIP_MIGRATION_DATABASE_URL` to its scratch
database **as the owner role** (the same `gipricing` URL it already builds), so `alembic` migrates the scratch database. Red first:
with the variable set to a different database, the scratch database ends without `role_assignments`. Control: the fixture refuses
(fails loudly, never migrates a foreign database) when no migration URL can be formed.

## Provenance

Found by the S1c gate (gate-1 SOLO, 2026-10-29) and proved at main by exec-seedproof under the grant "2026-10-29 14:21:02 GMT".

## Disposition

Open, owner WK-1178, MEDIUM; fix slice SL 8278 / LG 8279, Fri 30 Oct 2026 am. Filed under working id 8277.
