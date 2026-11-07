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

The "unset" mutation reds as `sqlalchemy ArgumentError` from `make_url(None)` inside the test, not by the guard's own assertion: with the clause gone the function has nothing to return for `None`. The mismatch test is three parametrised cases, so the single clause reds three.

### Other A-items, at head `1a18754a`

- **A2:** `git grep -n 'grant_demo_principals(' -- scripts/measure-p2-nfr-sweep.py` → `scripts/measure-p2-nfr-sweep.py:579:        return await _import_seed().grant_demo_principals(env.owner_database, workspace_id)` (one line, inside `_grant`). `git grep -n '_grant(' -- scripts/measure-p2-nfr-sweep.py` → :575 (def), :657, :713, :964 (the three replaced call sites).
- **A8:** `git diff --name-only origin/main...HEAD -- backend/src` prints nothing.
- **A1:** `git diff --name-only origin/main...HEAD` lists `backend/tests/test_measure_p2_nfr_sweep_storage.py`, `scripts/measure-p2-nfr-sweep.py`, `tests/test_measure_p2_nfr_sweep.py` and the records (`docs/INDEX.md`, the two FD drafts, `docs/findings/register.md`, the plan, this ledger).
- **Import closure (item 29):** changed module `scripts/measure-p2-nfr-sweep.py` (no `backend/src` file). `git grep -l -E 'measure-p2-nfr-sweep|measure_p2_nfr_sweep' -- tests backend/tests packages scripts examples` → the script, `tests/test_measure_p2_nfr_sweep.py`, `backend/tests/test_measure_p2_nfr_sweep_storage.py`. GREEN set = those two test files; the storage file is DB-backed, so it runs in W or a no-gate gap (item 32). Item 41: files under `tests`/`backend/tests` that `shutil.copy` and mention `scripts` — `test_bench_rating_serve_dsn.py`, `test_audit_docs_ids.py`, `test_doc_id_history_input.py`, `test_doc_id_migrate.py`, `test_doc_index.py`, `test_template_headers.py` — none names this script (the grep above does not list them). Items 43 and 45: no request shape and no error handler changes; they do not apply.

### Audit

(The auditor's.)

### Build log

- 2026-11-07: worktree `sl-8406` from `origin/main` `c602a539df82` (merge 79); plan records merged from `origin/draft/pl-fd8403-2026-11-07` (`d8596eb5`; INDEX conflict taken theirs, regenerated, `doc-index.py --check` rc=0).
- 2026-11-07, R0: ruff F841 flagged two now-unused `seed = _import_seed()` locals in `_one_way` and `_cells_diff` once `_grant` took over; removed. No behaviour change.
- 2026-11-07, deviation from PL 8405 R2 (i): "each arm disposes `owner_database` when it ends" is done inside `_grant` (a `try/finally` around the seed call), which is the owner connection's only use; re-indenting three long arm bodies for the same effect was not warranted. The R1 test's two sentinels gained an `async dispose` at R2 so `_grant` can call it; the assertion is unchanged. The lead may rule otherwise.
- 2026-11-07, R2: `TEMPLATE_DATABASE = "gipricing"` constant added; the guard is called from `main()` before `asyncio.run` for `one-way`, `storage`, `cells-diff`.

## PRs

(None yet.)
