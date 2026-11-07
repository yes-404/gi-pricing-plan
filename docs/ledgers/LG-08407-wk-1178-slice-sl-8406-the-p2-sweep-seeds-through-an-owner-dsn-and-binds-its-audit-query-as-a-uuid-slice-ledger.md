---
id: LG-8407
family: ledger
title: WK-1178 slice SL-8406 — FD-8403 and FD-8404, the P2 sweep seeds as the owner and binds its audit query as a UUID (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-11-07
owner: executor
tree: 1a18754a38df02057a48cd8531a8baad6f0a5f73   # the commit this was written against (sl-8406-sweep-owner-dsn; base c602a539df82aa0e6758176ed42b68e39ebd2ff8)
slice: SL-8406
phase: P2
work: WK-1178
plans: [PL-8405]
corrected_by: []
relates: [FD-8403, FD-8404, PL-8405, PL-1735, LG-2003]
---

# LG-8407 — WK-1178 slice SL-8406: the P2 sweep's two instrument defects

**GO:** to-lead "2026-11-07 19:10:01 GMT" (PL 8405 accepted, DP-1 to DP-6 all (a); conditions: A5 proves the DP-2 guard red on each broken input; window W under "2026-11-05 14:40:19 GMT"'s conditions, on the maintainer's word, beside a gate's pytest only; A8's empty `backend/src` diff quoted by its command; pairable, the pair word at the re-merged head with imports read).
**MERGE-ACK:** (added at merge.)

## Tasks

### Scope

PL 8405's SL 8406 row, A1 to A10. `01` NFR-468, NFR-470, FR-44; `03` NFR-1443 (measured by the instrument, not changed). FD 8403 (seed through an owner DSN) and FD 8404 (the storage arm's UUID bind). Write set: `scripts/measure-p2-nfr-sweep.py`, `tests/test_measure_p2_nfr_sweep.py`, `backend/tests/test_measure_p2_nfr_sweep_storage.py`, this ledger, the plan, the FD drafts. Working ids PL 8405, SL 8406, LG 8407, FD 8403, FD 8404; no other id.

### Task list

- R0 (`2e609db4`): `_grant`, `STORAGE_VERSION_QUERIES`, `_version_scalar` seams; no behaviour change.
- R1 (`1963f65a`): the failing tests, committed alone.
- R2 (i) (`588b87ef`): FD 8403. R2 (ii) (`1a18754a`): FD 8404.
- A5 mutation proofs, reverted and proved reverted.
- Owed to window W (the lead's written grant): A6's red/green run of the DB-backed storage test, A7. Owed to the gate: A9's second file, A10.

### Gate

Not run: no gate, no DB, no PR before W's grant (brief). DB-free runs only, each through `scripts/run-small.sh`, one file, load1 < 6, `pgrep -af '[d]emo.py'` empty before each.

Run logs (local, SHA-first, rc-last): `~/gi-pricing-plan.local/scratch/sl-8406/{r0,r1,r2}-small.log`, `a5-mutations.log`.

**R0** (head `d8596eb5` + the R0 edit): `tests/test_measure_p2_nfr_sweep.py` → `63 passed in 1.19s`, rc=0.

**R1 red** (head `2e609db4` + the R1 tests, before commit `1963f65a`): `10 failed, 63 passed in 16.44s`, rc=1. A3's red is by assertion: `AssertionError: the seed was handed the APP database, not the owner database` (`tests/test_measure_p2_nfr_sweep.py:404`). The other nine are the A4 and A5 seams, red as disclosed in the plan: `AttributeError: '_Env' object has no attribute 'owner_database'` (A4), `AttributeError: module 'measure_p2_nfr_sweep' has no attribute 'dsn_failure'` (A5 ×7), and A4's missing-variable test failing to raise. They are not counted as the red. `_Env()` itself builds DB-free under dead-port DSNs (PL 8405 self-review item 2, answered: yes), so A4 needed no fallback.

FAILED lines at R1:
```
FAILED tests/test_measure_p2_nfr_sweep.py::test_the_seed_runs_on_the_owner_database_and_never_on_the_app_database
FAILED tests/test_measure_p2_nfr_sweep.py::test_env_serves_through_the_app_dsn_and_seeds_through_the_owner_dsn
FAILED tests/test_measure_p2_nfr_sweep.py::test_env_without_an_owner_dsn_exits_naming_the_variable
FAILED tests/test_measure_p2_nfr_sweep.py::test_dsn_guard_accepts_an_app_and_an_owner_on_one_copy
FAILED tests/test_measure_p2_nfr_sweep.py::test_dsn_guard_refuses_an_unset_owner_dsn
FAILED tests/test_measure_p2_nfr_sweep.py::test_dsn_guard_refuses_the_template_database
FAILED tests/test_measure_p2_nfr_sweep.py::test_dsn_guard_refuses_an_app_and_an_owner_on_different_servers_or_databases[database]
FAILED tests/test_measure_p2_nfr_sweep.py::test_dsn_guard_refuses_an_app_and_an_owner_on_different_servers_or_databases[host]
FAILED tests/test_measure_p2_nfr_sweep.py::test_dsn_guard_refuses_an_app_and_an_owner_on_different_servers_or_databases[port]
FAILED tests/test_measure_p2_nfr_sweep.py::test_dsn_guard_refuses_one_user_on_both_dsns
```

**R2 green** (head `1a18754a`'s tree, before the commits): `73 passed in 8.35s`, rc=0.

**A6** (FD 8404, DB-backed): `backend/tests/test_measure_p2_nfr_sweep_storage.py` is written and committed at R1; it was **not run** (no DB before W). Its red at R1 and green at R2 are owed to W. Its queries are parametrised over every `STORAGE_VERSION_QUERIES` key except `dataset_versions_row`, named in the file as excluded.

### A5 — mutation proofs (head `1a18754a`)

Each refusal clause is neutralised in the script, the file's tests run, the script is restored with `git checkout -- scripts/measure-p2-nfr-sweep.py`, and `git diff --stat` is printed (empty = reverted). The log verbatim:

```
== mutation: unset
        If a :class:`.URL` object is passed, it is returned as is.
FAILED tests/test_measure_p2_nfr_sweep.py::test_dsn_guard_refuses_an_unset_owner_dsn
1 failed, 72 passed in 6.18s
revert proof: git diff --stat =[]
== mutation: template
FAILED tests/test_measure_p2_nfr_sweep.py::test_dsn_guard_refuses_the_template_database
1 failed, 72 passed in 6.19s
revert proof: git diff --stat =[]
== mutation: mismatch
FAILED tests/test_measure_p2_nfr_sweep.py::test_dsn_guard_refuses_an_app_and_an_owner_on_different_servers_or_databases[database]
FAILED tests/test_measure_p2_nfr_sweep.py::test_dsn_guard_refuses_an_app_and_an_owner_on_different_servers_or_databases[host]
FAILED tests/test_measure_p2_nfr_sweep.py::test_dsn_guard_refuses_an_app_and_an_owner_on_different_servers_or_databases[port]
3 failed, 70 passed in 6.48s
revert proof: git diff --stat =[]
== mutation: same_user
FAILED tests/test_measure_p2_nfr_sweep.py::test_dsn_guard_refuses_one_user_on_both_dsns
1 failed, 72 passed in 6.11s
revert proof: git diff --stat =[]
rc=0
```

The "unset" line above is superseded (the maintainer, to-lead "2026-11-07 19:35:11 GMT": A5 needs the guard's own refusal, a crash is not it). It reded as `sqlalchemy ArgumentError` from `make_url(None)`, a crash. `test_dsn_guard_refuses_an_unset_owner_dsn` now reads a raise as "no refusal" and asserts the refusal's message text (`GIP_MIGRATION_DATABASE_URL is not set`, `same -T copy as GIP_DATABASE_URL`). Re-proof at head `1a3924664bb0` with the new test, `unset` clause removed from `dsn_failure`:

```
head=1a3924664bb0794d09d3afd91e183d950315bb66 MUTATED(unset clause removed)
E       AssertionError: the guard must return a refusal for an unset owner DSN
E       assert None is not None
FAILED tests/test_measure_p2_nfr_sweep.py::test_dsn_guard_refuses_an_unset_owner_dsn
1 failed, 72 passed in 7.29s
rc=1
revert: git diff --stat -- scripts = []
```

Green after the revert: `head=1a3924664bb0794d09d3afd91e183d950315bb66` / `73 passed in 6.83s` / `rc=0`. `ruff check .` rc 0; `ruff format --check` on the test file rc 0. The mismatch test is three parametrised cases, so the single clause reds three.

### Other A-items, at head `1a18754a`

- **A2:** `git grep -n 'grant_demo_principals(' -- scripts/measure-p2-nfr-sweep.py` → `scripts/measure-p2-nfr-sweep.py:579:        return await _import_seed().grant_demo_principals(env.owner_database, workspace_id)` (one line, inside `_grant`). `git grep -n '_grant(' -- scripts/measure-p2-nfr-sweep.py` → :575 (def), :657, :713, :964 (the three replaced call sites).
- **A8:** `git diff --name-only origin/main...HEAD -- backend/src` prints nothing.
- **A1:** `git diff --name-only origin/main...HEAD` lists `backend/tests/test_measure_p2_nfr_sweep_storage.py`, `scripts/measure-p2-nfr-sweep.py`, `tests/test_measure_p2_nfr_sweep.py` and the records (`docs/INDEX.md`, the two FD drafts, `docs/findings/register.md`, the plan, this ledger).
- **Import closure (item 29):** changed module `scripts/measure-p2-nfr-sweep.py` (no `backend/src` file). `git grep -l -E 'measure-p2-nfr-sweep|measure_p2_nfr_sweep' -- tests backend/tests packages scripts examples` → the script, `tests/test_measure_p2_nfr_sweep.py`, `backend/tests/test_measure_p2_nfr_sweep_storage.py`. GREEN set = those two test files; the storage file is DB-backed, so it runs in W or a no-gate gap (item 32). Item 41: files under `tests`/`backend/tests` that `shutil.copy` and mention `scripts` — `test_bench_rating_serve_dsn.py`, `test_audit_docs_ids.py`, `test_doc_id_history_input.py`, `test_doc_id_migrate.py`, `test_doc_index.py`, `test_template_headers.py` — none names this script (the grep above does not list them). Items 43 and 45: no request shape and no error handler changes; they do not apply.

### Window W (A6, A7), 7 Nov 2026 20:43-21:02 GMT, exec-sl8406w

START 20:42:36 GMT beside FD 8366's gate (`sl8368-gate.sh`, gate-1), stage pytest, `| stage pytest START | load1 2.05 at 2026-11-07T20:41:39+00:00 |`; to-lead "2026-11-07 19:35:11 GMT" under "2026-11-05 14:40:19 GMT" (a)-(j). load1 2.23, MemAvailable 26765 MB, template guard 1|3|1, redis `-n 12` dbsize 0, `-n 0` dbsize 56, `PUBSUB NUMSUB gip:switch` 0. Own copies `gipricing_sl8406w_<n>` (`createdb -T gipricing`, mkdb retry), both URLs on each copy (app `gip_app_login`, owner `gipricing`), `GIP_GATE_SLOT=/tmp/slots/window-sl8406`, `GIP_REDIS_URL=.../12`, bucket `sl8406-w`; the slot, redis, bucket and both URLs read from a running child's `/proc/<pid>/environ`. Scratch worktrees at R1 (`1963f65a`) and R0 (`2e609db4`), each `uv sync --all-packages --frozen`. Every run through `run-heavy.sh --grant`, `nice -n 10`, `timeout 900`. Logs in `~/gi-pricing-plan.local/scratch/sl-8406/w-*.log` (head= first, rc= last).

- **A6 red** (R1 `1963f65ab353`, copy 1): `FAILED backend/tests/test_measure_p2_nfr_sweep_storage.py::test_a_storage_query_binds_a_uuid_version_id[audit_events_rows]`, `1 failed, 5 passed, 2 warnings in 2.21s`, `TypeError: expected str, got UUID`, rc=1. Only `audit_events_rows`.
- **A6 green** (head `86b63e54ed40`, copy 2): `6 passed, 2 warnings in 1.58s`, rc=0.
- **A7 red at R0** (`2e609db4832a`): `cells-diff --only rows-10000 --seeded-jobs 10`: `InsufficientPrivilegeError: permission denied for table workspaces`, rc=1. Plan sizes for `one-way --fremtpl2-rows 2000 --wide-rows 2000` and `storage --fremtpl2-rows 2000`: rc=1 on `model.DegenerateFitError: the fit is degenerate: 9 level(s) below the relativity floor 0.01`, in `seed.run`, before the code under test, and the same error at the head. **Deviation, disclosed:** 2000 rows cannot pass the seed's degenerate-fit refusal (20000 rows still refuses, `region[R43] = 2.15e-06`); 100000 rows passes. The arms were re-run at `--fremtpl2-rows 100000` (one-way keeps `--wide-rows 2000`): R0 `one-way`: `permission denied for table workspaces`, rc=1; R0 `storage`: `expected str, got UUID`, rc=1.
- **A7 green at the head** (`86b63e54ed40`): `cells-diff` rc=0 (`NFR-1443 ... rows-10000 ... DIAGNOSTIC-PASS`); `one-way --fremtpl2-rows 100000 --wide-rows 2000` rc=0; `storage --fremtpl2-rows 100000` rc=0 (twice, probe and named run). The 2000-row one-way and storage greens do not exist; the plan's sizes need a change (a plan question for the lead).
- **The guard on db gipricing** (the 29 Oct rule, mechanical; DSNs on port 5999, nothing connected, the guard refuses first): `the owner DSN names the template database 'gipricing': use a -T copy`, rc=1 (`w-guard-template.log`).
- A first one-way green pass was cut by my own 118 s wrapper timeout; I killed its three processes by pid, dropped copy 7, flushed db 12, and re-ran it whole.
- Data: the two freMTPL2 `.arff` files were copied into the three worktrees' `examples/fremtpl2/data/` (gitignored, `git status --porcelain` 0) and removed at END with `last-seed.json`.

END 21:01:50 GMT, gate sl8368 still in stage pytest. `pg_database` count 0 for each of `gipricing_sl8406w_1`..`_9`; datnames now `gipricing gipricing_sl8368_gate postgres template0 template1`; redis `-n 12` FLUSHDB then dbsize 0; `-n 0` dbsize 56; `mc rb --force g/sl8406-w` rc=0 and `mc ls g/` lists no `sl8406-w`; template guard 1|3|1; `PUBSUB NUMSUB gip:switch` 0; no container bind source under sl-8406 (`docker inspect` count 0); scratch worktrees r1 and r0 removed by exact path, `git worktree list` has no scratch entry.

### Audit

(The auditor's.)

### Build log

- 2026-11-07: worktree `sl-8406` from `origin/main` `c602a539df82` (merge 79); plan records merged from `origin/draft/pl-fd8403-2026-11-07` (`d8596eb5`; INDEX conflict taken theirs, regenerated, `doc-index.py --check` rc=0).
- 2026-11-07, R0: ruff F841 flagged two now-unused `seed = _import_seed()` locals in `_one_way` and `_cells_diff` once `_grant` took over; removed. No behaviour change.
- 2026-11-07, deviation from PL 8405 R2 (i): "each arm disposes `owner_database` when it ends" is done inside `_grant` (a `try/finally` around the seed call), which is the owner connection's only use; re-indenting three long arm bodies for the same effect was not warranted. The R1 test's two sentinels gained an `async dispose` at R2 so `_grant` can call it; the assertion is unchanged. The lead may rule otherwise.
- 2026-11-07, R2: `TEMPLATE_DATABASE = "gipricing"` constant added; the guard is called from `main()` before `asyncio.run` for `one-way`, `storage`, `cells-diff`.

## PRs

(None yet.)
