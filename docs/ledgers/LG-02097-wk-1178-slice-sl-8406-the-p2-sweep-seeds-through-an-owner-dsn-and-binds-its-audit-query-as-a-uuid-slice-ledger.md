---
id: LG-2097
family: ledger
title: WK-1178 slice SL-2096 — FD-2093 and FD-2094, the P2 sweep seeds as the owner and binds its audit query as a UUID (slice ledger)
status: closed                 # active → closed (§1.2a)
created: 2026-11-08   # original date 2026-11-07, draft under working id 8407; minted 2026-11-08
owner: executor
tree: 3a0bb563a378e4f8812093c4f2e698c4eb7d755b   # the tree of the gated head 7a640cf998ee (sl-8406-sweep-owner-dsn); was 1a18754a38df… (a commit id, not a tree), corrected 2026-11-08 on audit N2 and the lead's word
slice: SL-2096
phase: P2
work: WK-1178
plans: [PL-2095]
corrected_by: []
relates: [FD-2093, FD-2094, PL-2095, PL-1735, LG-2003]
---

# LG-2097 — WK-1178 slice SL-2096: the P2 sweep's two instrument defects

*Disclosure: drafted under working id 8407; minted as LG-2097 on 2026-11-08, in the SL-2096 mint (WK-1178). Closed 2026-11-08 by the mint commit on the clean audit (item 42).*

*Dated line, 2026-11-08 (lead 31, audit N2): the front matter `tree:` is the tree `3a0bb563a378e4f8812093c4f2e698c4eb7d755b` of the gated head `7a640cf998ee`, the head the slice's gate measured (gate.log START line). The Gate section's window runs are at head `86b63e54ed40`. The slice's three files (`scripts/measure-p2-nfr-sweep.py`, `tests/test_measure_p2_nfr_sweep.py`, `backend/tests/test_measure_p2_nfr_sweep_storage.py`) are byte-identical between the two heads (`git diff --stat 86b63e54ed40 7a640cf998ee -- <those three>` empty); the other differences are main's merges.*

**GO:** to-lead "2026-11-07 19:10:01 GMT" (PL-2095 accepted, DP-1 to DP-6 all (a); conditions: A5 proves the DP-2 guard red on each broken input; window W under "2026-11-05 14:40:19 GMT"'s conditions, on the maintainer's word, beside a gate's pytest only; A8's empty `backend/src` diff quoted by its command; pairable, the pair word at the re-merged head with imports read).
**MERGE-ACK:** (added at merge.)

## Tasks

### Scope

PL-2095's SL-2096 row, A1 to A10. `01` NFR-468, NFR-470, FR-44; `03` NFR-1443 (measured by the instrument, not changed). FD-2093 (seed through an owner DSN) and FD-2094 (the storage arm's UUID bind). Write set: `scripts/measure-p2-nfr-sweep.py`, `tests/test_measure_p2_nfr_sweep.py`, `backend/tests/test_measure_p2_nfr_sweep_storage.py`, this ledger, the plan, the FD drafts. Working ids PL-2095, SL-2096, LG-2097, FD-2093, FD-2094; no other id.

### Task list

- R0 (`2e609db4`): `_grant`, `STORAGE_VERSION_QUERIES`, `_version_scalar` seams; no behaviour change.
- R1 (`1963f65a`): the failing tests, committed alone.
- R2 (i) (`588b87ef`): FD-2093. R2 (ii) (`1a18754a`): FD-2094.
- A5 mutation proofs, reverted and proved reverted.
- Owed to window W (the lead's written grant): A6's red/green run of the DB-backed storage test, A7. Owed to the gate: A9's second file, A10.

### Gate

Not run: no gate, no DB, no PR before W's grant (brief). DB-free runs only, each through `scripts/run-small.sh`, one file, load1 < 6, `pgrep -af '[d]emo.py'` empty before each.

Run logs (local, SHA-first, rc-last): `~/gi-pricing-plan.local/scratch/sl-8406/{r0,r1,r2}-small.log`, `a5-mutations.log`.

**R0** (head `d8596eb5` + the R0 edit): `tests/test_measure_p2_nfr_sweep.py` → `63 passed in 1.19s`, rc=0.

**R1 red** (head `2e609db4` + the R1 tests, before commit `1963f65a`): `10 failed, 63 passed in 16.44s`, rc=1. A3's red is by assertion: `AssertionError: the seed was handed the APP database, not the owner database` (`tests/test_measure_p2_nfr_sweep.py:404`). The other nine are the A4 and A5 seams, red as disclosed in the plan: `AttributeError: '_Env' object has no attribute 'owner_database'` (A4), `AttributeError: module 'measure_p2_nfr_sweep' has no attribute 'dsn_failure'` (A5 ×7), and A4's missing-variable test failing to raise. They are not counted as the red. `_Env()` itself builds DB-free under dead-port DSNs (PL-2095 self-review item 2, answered: yes), so A4 needed no fallback.

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

**A6** (FD-2094, DB-backed): `backend/tests/test_measure_p2_nfr_sweep_storage.py` is written and committed at R1; it was **not run** (no DB before W). Its red at R1 and green at R2 are owed to W. Its queries are parametrised over every `STORAGE_VERSION_QUERIES` key except `dataset_versions_row`, named in the file as excluded.

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

DRAFT — proposal. Auditor aud-s8406s8410 (sonnet, medium), Sun 8 Nov 2026. Not adopted until the lead adopts, amends or rejects it (CLAUDE.md §12/§13).

## Audit — SL-2096 (PL-2095, FD-2093 + FD-2094), range `origin/main...origin/sl-8406-sweep-owner-dsn` @c7cad487c27d (merge of cdf3871c; code files byte-identical to window head 86b63e54ed40: `git diff 86b63e54 c7cad487 -- scripts tests backend` empty)

Scope derived from PL-2095 first (A1–A10 + dated delta 6a878875, ruling to-lead "2026-11-07 21:03:10 GMT"), then evidence. Read to the assert: script diff, both test files, LG-2097, window logs `~/gi-pricing-plan.local/scratch/sl-8406/w-*.log` (head= first line, rc= last line checked).
Own runs (tree = detached worktree `scratch/aud-s8406s8410/w8406` @c7cad487, `uv sync --all-packages --frozen`; pgrep demo/vitest empty before each): `run-small.sh` on `tests/test_measure_p2_nfr_sweep.py` → **73 passed in 15.69s, rc=0** (`small-8406.log`); `audit-docs.py` via gate-2 flock → rc=1 with ONE failure, `check 31: gap in the full allocation between 2073 and 8403` = the slice's own working ids (`audit-docs-8406.log`); `doc-index.py --check` rc=0.

| Item | Verdict | Evidence |
|---|---|---|
| A1 write set | MET | `git diff --name-only origin/main...HEAD`: script, two test files, PL/LG/FD×2/register/INDEX only; nothing under backend/src, packages, examples, migrations, deploy, conftest |
| A2 one seeding path | MET | `git grep -n 'grant_demo_principals('` → one line (:579) in `_grant` on `env.owner_database`; `_grant(` call sites :657, :713, :964 |
| A3 red by cause (FD-2093) | MET-BY-RECORD | LG R1 red `AssertionError: the seed was handed the APP database, not the owner database`; test text matches; green 73 passed re-run by me |
| A4 create_app never sees owner | MET | `test_env_serves_through_the_app_dsn_…` and `…without_an_owner_dsn_exits_naming_the_variable` in my 73-pass run; `_Env` code reads `migration_database_url`, raises SystemExit naming the variable |
| A5 guard + mutation proofs | MET-BY-RECORD | 5 DB-free tests pass (mine); LG a5-mutations log: 4 mutations red, `git diff --stat` empty after each; the "unset" proof was redone after maintainer 19:35:11 (assertion red, quoted) |
| A6 red by cause (FD-2094) | MET-BY-RECORD | `w-a6red.log` (head=1963f65ab353, rc=1) 6× `expected str, got UUID`, only `audit_events_rows`; `w-a6green.log` head=86b63e54ed40 rc=0; `dataset_versions_row` excluded and reasoned in the test file |
| A7 S2 failures reproduced then cleared | MET-BY-RECORD at 100000 rows (delta) | red R0: `w-a7red-cells.log` (rc=1, 3× `permission denied for table workspaces`), `w-bigred-oneway.log` (3×, rc=1), `w-bigred-storage.log` (4× `expected str, got UUID`, rc=1); green head 86b63e54ed40: cells rc=0, `w-biggreen-oneway.log` rc=0, `w-biggreen-storage.log` rc=0. All SHA-first/rc-last. Size 100000 is covered by the ruling "2026-11-07 21:03:10 GMT" and delta 6a878875 (2000-row green cannot exist: `DegenerateFitError`). I did not re-run the window (DB lane is the lead's) |
| A8 runtime untouched | MET | `git diff --name-only origin/main...HEAD -- backend/src` → 0 files |
| A9 closure tests green | PARTLY: file 1 MET (my run); file 2 MET-BY-RECORD (window A6 green); re-run at re-merged head OWED-TO-GATE | `backend/tests/test_measure_p2_nfr_sweep_storage.py` is DB-backed; I ran no DB (brief) |
| A10 gate | OWED-TO-GATE | not run; gate on the maintainer's word |
| G5 reading rules untouched | MET | diff touches no `NFR_*_RULE`, bands, `CELLS_DIFF_RUNS`, `NFR_1443_SEEDED_JOBS` |
| Item 43/45 | N/A | no route or handler changed |

### Findings (proposals)
- **N1 (LOW, deviation with no ruling found).** PL-2095 R2 (i) says "each arm disposes `owner_database` when it ends"; the build disposes inside `_grant` per call (LG build log: "The lead may rule otherwise"). Grep of from-lead/to-lead for `dispose` finds no ruling. Behaviour is sound — `one-way` calls `_grant` twice on one `_Env` and ran rc=0 at 100000 rows — so propose: lead records the deviation as accepted (one dated line in LG-2097), no code change.
- **N2 (LOW).** LG-2097 front matter `tree:` is `1a18754a…`, but its text cites later heads (`1a392466…`, `86b63e54`, `8881bb75`). Propose the closing act refreshes `tree:`/the head it was written against (git-hygiene: a Verified date carries the tree).
- **N3 (INFO).** Plan Evidence line numbers (`:604/:661/:897`) are `bfeedd9a`'s (G7); after the change they are `:657/:713/:964` — the LG records that.
- No NOT MET items. Two OWED-TO-GATE: A9 re-run at the re-merged head, A10.

### Closing acts (FD-1842 form) — NOT carried by the plan branch
Branch state: the FD-2093 and FD-2094 essays under `docs/findings/` are `status: active` with only a `## Disposition` section; register rows present with no closing note. So the closing acts below are owed at the mint (ids land in merge order, then regenerate INDEX under the gate-2 flock; item 17).
Proposed text to append to each FD after `## Disposition` and to set `status: closed`:

> ***Resolved <merge date>*** — closed in place by <role>, as the closing act of the mint of SL-<n> (WK-1178, LG-<n>, PL-<n>; [PR #<N>, squash commit <sha> on main, merged <time>]), on the GO to-lead "2026-11-07 19:10:01 GMT". FD-<n8403>: delivered remedy: `scripts/measure-p2-nfr-sweep.py` seeds through `_Env.owner_database` (built from `GIP_MIGRATION_DATABASE_URL`, as `seed.py` builds it) via the single `_grant`, and serves through the app DSN; `dsn_failure` refuses an unset owner DSN, the template database `gipricing`, a different host/port/database, and one user on both DSNs. Red first by assertion (LG-<n>: "the seed was handed the APP database"), A5 mutation proofs reverted; window W: R0 `permission denied for table workspaces`, head rc=0 for `cells-diff`, `one-way` and `storage` (100000 rows, by the ruling "2026-11-07 21:03:10 GMT"). Gate evidence: LG-<n>. FD-<n8404>: delivered remedy: `audit_events_rows` is `… cast(cast(:v as uuid) as text) …` (one site: `git grep -n -E 'cast\(:|::text|as text'` finds none left); red `expected str, got UUID` at R1 on `audit_events_rows` only, green at R2; `backend/tests/test_measure_p2_nfr_sweep_storage.py` holds it.

Register rows (`docs/findings/register.md`): both rows' resolution cell → `**resolved <date> — <SL-n>**` with the same PR/squash facts; keep the row, do not delete.
SL-2096's roadmap row and LG-2097 `status:` → `closed` on the clean audit and the lead's merge (item 42); read the row at `origin/main` after the merge.

**Dated line, 2026-11-08 (lead 31): audit N1 accepted as built.** PL-2095 R2 (i) says each arm disposes `owner_database` when it ends. The build disposes it in a `finally` inside `_grant` after every call (`scripts/measure-p2-nfr-sweep.py`, `_grant`). The owner connection lives for one grant call and is always disposed, including on error, which is tighter than per-arm. Accepted by the lead, from-lead 2026-11-08 04:37:46 GMT.

**Dated line, 2026-11-08 (lead 31): A9's second file at the re-merged head goes to the PR's python CI.** At the re-merged head `e18337239747`, `tests/test_measure_p2_nfr_sweep.py` and `backend/tests/test_route_permission_pin.py` gave "96 passed, 2 warnings in 1.58s", rc 0. `backend/tests/test_measure_p2_nfr_sweep_storage.py` gave 5 errors, one per parametrised query: "GIP_TEST_DATABASE_URL is not set, and the per-worktree test database 'gipricing_sl-8406_da05d927' does not exist yet". Its fixture refuses rather than skips, so a green python CI run on this PR, which runs pytest on a `postgres:16-alpine` service (`.github/workflows/python.yml`), means the file ran on Postgres and passed at the merged head. No local DB lane was granted. Running this file only in the PR's python CI was accepted by the maintainer, from-lead 2026-11-08 04:48:41 GMT. This supersedes "re-run at re-merged head OWED-TO-GATE" in the table above.

**Dated line, 2026-11-08 (written 06:05:29 GMT, docs batch 22, lead 31): A9's second file ran and passed in the PR's python CI, by predicate.** Read by the maintainer at MERGE-ACK of #1469 (to-lead, merge 94) from python run 42451096144, job `ruff · mypy · import-linter · pytest`: the job runs `uv run pytest -q`, which prints no per-test names, and it ended `7651 passed, 28 skipped, 5 xfailed, 156 warnings in 1785.37s` with 0 failed. `backend/tests/test_measure_p2_nfr_sweep_storage.py` is in the tree. CI sets `GIP_TEST_DATABASE_URL` on its Postgres service, so its fixture takes no skip path. The 28 skipped equal the baseline SL-2096's own gate read with this file present. So the file ran and passed at the merged head. This discharges the CI route in the line above.

### Build log

- 2026-11-07: worktree `sl-8406` from `origin/main` `c602a539df82` (merge 79); plan records merged from `origin/draft/pl-fd8403-2026-11-07` (`d8596eb5`; INDEX conflict taken theirs, regenerated, `doc-index.py --check` rc=0).
- 2026-11-07, R0: ruff F841 flagged two now-unused `seed = _import_seed()` locals in `_one_way` and `_cells_diff` once `_grant` took over; removed. No behaviour change.
- 2026-11-07, deviation from PL-2095 R2 (i): "each arm disposes `owner_database` when it ends" is done inside `_grant` (a `try/finally` around the seed call), which is the owner connection's only use; re-indenting three long arm bodies for the same effect was not warranted. The R1 test's two sentinels gained an `async dispose` at R2 so `_grant` can call it; the assertion is unchanged. The lead may rule otherwise.
- 2026-11-07, R2: `TEMPLATE_DATABASE = "gipricing"` constant added; the guard is called from `main()` before `asyncio.run` for `one-way`, `storage`, `cells-diff`.

## PRs

(None yet.)
