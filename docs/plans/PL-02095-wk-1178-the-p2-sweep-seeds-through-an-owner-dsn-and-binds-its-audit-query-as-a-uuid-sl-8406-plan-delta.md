---
id: PL-2095
family: plan
kind: map
title: WK-1178 — FD-2093 and FD-2094, the P2 NFR sweep seeds through a separate owner DSN and serves through the app DSN, and its storage arm binds its audit_events query as a UUID, SL-2096 — a dated Work-plan delta
status: active                  # draft → active → superseded | retired (§1.2a) — L1: draft→active rides the slice's PR
created: 2026-11-08             # original date 2026-11-07, draft under working id 8405; minted 2026-11-08
owner: planner
tree: 20087ba79fe33e15d30f4a68ed6b0d49264ff98f   # origin/main bfeedd9a282ee0180be54bf201b17930fc4bd2d0
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1856, PL-1735, SL-1736, LG-2003, FD-1729, FD-2093, FD-2094, FR-44, NFR-1443, NFR-468, NFR-470]
---

# PL-2095 — WK-1178: the P2 sweep instrument's two defects. Seed as the owner, serve as the app, bind the audit query as a UUID (SL-2096, a dated Work-plan delta)

*Disclosure: drafted under working id 8405; minted as PL-2095 on 2026-11-08, in the SL-2096 mint (WK-1178). Status draft → active rides the slice's PR (L1 (a')).*

> **For agentic workers:** a **dated Work-plan delta** under Lean P2 L1 (a'). It `relates:` `PL-1735`
> (the sweep's own delta, the instrument's plan) and `PL-1856` (the WK-1178 parent PL-2059 also relates), and edits neither. It has one slice row,
> SL-2096, whose ledger is LG-2097. **It decides nothing.** Six decision points each carry a
> recommendation; the maintainer rules them. The build seat starts when the pin lands, and the gate runs
> on the maintainer's word (to-lead "2026-11-07 18:54:59 GMT"). The executor's skills are
> `superpowers:test-driven-development`, `.claude/skills/python-test` and `.claude/skills/dev-commands`.
> PL-2095, SL-2096, LG-2097, FD-2093 and FD-2094 are working ids reserved by the lead.

## Authority

- **FD-2093.** To-lead "2026-11-07 18:49:24 GMT" item I: "FD, YES … severity MEDIUM (blocks a measurement;
  no mispricing), owner WK-1178". "Scope: the harness's shared _Env, so J and K join the same FD by dated
  line if they hit the wall; one FD, one fix." "FIX, code before Thu 12, after the pin in the queue:
  scripts/measure-p2-nfr-sweep.py seeds through a SEPARATE owner DSN and serves through the app DSN; red
  first (the S2 failure reproduced in a test against a -T copy), green after; the app's runtime code is not
  touched; the seed URL never names the template (29 Oct rules); gate single or paired on my word."
- **FD-2094.** To-lead "2026-11-07 18:54:18 GMT" item (1): "FD-2093 joins by dated line for the one-way
  corpus (grant_demo_principals as gip_app_login at :661). The storage arm's asyncpg DataError at :841 →
  :815 … is a SECOND defect: FD-2094, YES, MEDIUM, owner WK-1178, titled on the UUID binding; fixed in the
  SAME instrument slice as FD-2093, after the pin, each red first against a -T copy; J runs in S3 with I."
- **This plan.** To-lead "2026-11-07 18:54:59 GMT": "a dated delta under WK-1178's plan, with FD-2093 and
  FD-2094 essays as its evidence", stating (a) to (f), which are answered here in order: (a) DP-1 and
  Task R2; (b) DP-3, and the sibling grep in Evidence; (c) Tasks R1 and W, with Needs; (d) Gate form;
  (e) Needs; (f) S3 form.

## Goal

After SL-2096, `scripts/measure-p2-nfr-sweep.py` runs its three database arms against one `-T` copy with
two env-named DSNs: the **owner** DSN for the seed alone, and the **app** DSN for everything `create_app`
and the measured paths touch. `storage`'s per-version queries also bind. Nothing under `backend/src/`
changes. Then I (NFR-1443), J one-way (NFR-468) and J storage (NFR-470) can run in S3 on Fri 13 Nov.

## Evidence at `bfeedd9a` (tree `20087ba7`), read-only

The instrument at `origin/main` has sha256 `093928d1ca4f2718525d1ec2765ec8ebb29cab230e468fef8a3c0d5f9d3e2eba`,
re-hashed by `git show origin/main:scripts/measure-p2-nfr-sweep.py | sha256sum`. It is the same file S2 ran:
`git diff 6f958137 bfeedd9a -- scripts/measure-p2-nfr-sweep.py examples/fremtpl2/seed.py backend/src/app/db/immutability.py backend/src/app/main.py backend/src/app/config.py`
prints nothing.

| Locus | What it says |
|---|---|
| `scripts/measure-p2-nfr-sweep.py:499-516` `_Env` | one `Database(self.settings)` at `:514`; `create_app(self.settings)` at `:516`; settings from `load_settings(dev_auth_enabled=True)` at `:513` |
| `:604` (`_fremtpl2`), `:661` (`_one_way`), `:897` (`_cells_diff`) | `seed.grant_demo_principals(env.database, …)`. The predicate: `git grep -n 'grant_demo_principals(' -- scripts/measure-p2-nfr-sweep.py` prints these three |
| `:814-815` `scalar` | `session.execute(text(query), {"v": version_id})`, with `version_id` a `UUID` |
| `:841-844` | `entity_ref like '%' \|\| cast(:v as text) \|\| '%'`, the one text-typed bind |
| `:901` | `async with env.app.router.lifespan_context(env.app), env.client() as client:`, the lifespan that refuses an owner |
| `examples/fremtpl2/seed.py:346` | `grant_demo_principals(database, workspace_id)` writes `workspaces`, roles and members through `database.unit_of_work()` |
| `seed.py:448-461` | the FD-1729 split already made for the seed: `owner_database = Database(settings.model_copy(update={"database_url": settings.migration_database_url}))`, and a `SystemExit` naming `GIP_MIGRATION_DATABASE_URL` when it is unset |
| `backend/src/app/config.py:121-129` | `database_url` is the application's (`gip_app`); `migration_database_url` (`GIP_MIGRATION_DATABASE_URL`) is "optional: the application never needs it" |
| `backend/src/app/main.py:114` | `await database.assert_least_privilege()` in the lifespan; `immutability.py:171` raises `LeastPrivilegeError` |
| `backend/src/app/main.py:278` | `app.state.settings = settings`, the attribute A4 reads |
| `backend/migrations/versions/b7e4c2a91d36_application_role_grants.py` | `workspaces`, `workspace_members`, `roles`, `role_assignments`: `READ` (`:165`, `:163`, `:147`, `:146`). `workspace_settings` `_moves("value")` (`:164`), `factors` `APPEND` (`:123`), `models` `LIFECYCLE` (`:130`), `jobs` `LIFECYCLE` (`:127`), `audit_events` `APPEND` (`:107`) |
| `scripts/provision-app-role.py:4-6` | the login role's password comes from `GIP_APP_DB_PASSWORD`; the role is cluster-wide, so every `-T` copy has it |
| `backend/tests/conftest_db.py:1307` `owner_database` | fails any test that is not in `OWNER_FIXTURE_USERS` (`:205`); `database` (`:1252`) is the login role |
| `.github/workflows/python.yml:118`, `:343-344` | CI's service database **is named `gipricing`**, owner and app DSNs both on it |
| `LG-2003` | the harness's DB arms are "wiring only until their first smoke"; `storage` and `one-way` never ran; the one NFR-1443 reading (2026-10-22) ran as the owner, before FD-1729 merged (`#1398` `1e0a8abb`, `#1399` `eaddb4d9`, 2026-10-26); the harness merged after it (`#1429` `c796e4c0`, 2026-11-04) |

**The S2 tracebacks** are quoted with their log lines in FD-2093 and FD-2094. In short: I as
`gip_app_login` → `permission denied for table workspaces` at `:897`; I as the owner → `LeastPrivilegeError`
at `:901`; J one-way as `gip_app_login` → the same denial at `:661`; J storage → `DataError … (expected str,
got UUID)` at `:841` → `:815`.

**Sibling binds (brief item (b)).** `git grep -n -E 'cast\(:|::text|as text' -- scripts/measure-p2-nfr-sweep.py`
prints `:843` alone. Every other bind is typed by a column comparison: `:700-704`, `:790-794`, `:804-805`,
and `:818-840`. **One site.**

**The cells-diff helpers after the seed.** `_set_threshold` and `_seed_approved_model`
(`backend/tests/test_rate_tables_service.py:46`, `:54`) run on `env.database`. After the owner has created
the workspace, `ensure_workspace` only reads it (`app/platform/workspaces.py:35-37`). `workspace_settings`,
`factors` and `models` are granted. **By grant they pass as the login role. Nothing has run them as the
login role:** S2 stopped at `:897`. Window W is the first run (DP-6).

## Decision points

No DP is the planner's to rule. Each has a recommendation. **DP-1 and DP-4 are blocking**: Tasks R1 and R2
are written to them.

- **DP-1 (blocking): the owner DSN's env name.** (a) **`GIP_MIGRATION_DATABASE_URL`**, read through
  `settings.migration_database_url`, built as `seed.py:458-460` builds it. (b) A new harness-only
  `GIP_SEED_DATABASE_URL`. **Recommendation (a).** `seed.run`, called inside `_fremtpl2`, already reads
  `GIP_MIGRATION_DATABASE_URL` for the same purpose, so (b) would put two owner DSNs in one process. S2's
  `db-window.sh:16` already exports both variables in this form. The `Settings` field exists. A missing
  owner DSN exits naming the variable, as `seed.py:454-457` does.
- **DP-2: the template guard, "the seed URL never names the template (29 Oct rules)".** (a) A pure
  function `dsn_failure(app_url, owner_url) -> str | None` in the harness, called by `main()` before any
  database subcommand, never inside `_Env`. It refuses: no owner DSN; an owner DSN whose database is
  `gipricing`; app and owner DSNs naming different host, port or database; the same user on both.
  (b) No guard; only the briefs enforce the rule. **Recommendation (a).** On 29 Oct a URL aimed at the
  template wrote demo rows into it. The guard costs one function and DB-free tests. It sits in `main()`,
  not in `_Env`, because CI's own database is named `gipricing` (`python.yml:118`) and tests build `_Env`
  directly. The guard protects the operator's command, not the test fixture.
- **DP-3: FD-2094's fix.** (a) The SQL types the parameter:
  `entity_ref like '%' || cast(cast(:v as uuid) as text) || '%'`. The bind stays the one `UUID` that all six
  queries share. (b) The query binds `str(version_id)` under its own name. **Recommendation (a).** One
  token-level change. `scalar` keeps one signature and one bind. The parameter's type is stated where it is
  used. `::` is not available: SQLAlchemy's `text()` would read `:v::uuid` as a bind name.
- **DP-4 (blocking): where the reds live.** (a) **Three layers.**
  - FD-2093's red is DB-free, in `tests/test_measure_p2_nfr_sweep.py`: a recorder stands in for
    `grant_demo_principals` and fails when it is handed the app database.
  - FD-2094's red is DB-backed, in a new `backend/tests/test_measure_p2_nfr_sweep_storage.py`, on the
    `database` fixture (the login role on the per-worktree `-T` copy). This needs no `OWNER_FIXTURE_USERS`
    row.
  - Both are reproduced from S2 as harness runs in one DB window on a `createdb -T` copy: red at R0's head,
    green at R2's.

  (b) Window runs only. (c) A DB-backed FD-2093 test on `owner_database`, which needs a
  `backend/tests/conftest_db.py` allow-list row. **Recommendation (a).** (b) leaves CI blind again: the
  reason both defects reached S2 is that no test touches the DB arms (`LG-2003` A4). (c) edits the fixture
  file every DB-backed test loads, which would break the clean file overlap of the Gate form. The ruling's
  "the S2 failure reproduced in a test against a -T copy" is met by the window (the exact S2 commands at
  small sizes) and by the DB-backed storage test (the per-worktree database is a `-T gipricing` copy,
  `conftest_db.py:153`).
- **DP-5: `:604`.** (a) All three `grant_demo_principals` calls go through one `_grant(env, workspace_id)` on
  the owner database. (b) Only `:661` and `:897`. **Recommendation (a).** `:604` passed in S2 only because
  `seed.run` had just created the workspace as the owner. It has the same shape, and "one FD, one fix"
  (18:49:24). A new member in `DEMO_PRINCIPALS` would make it write.
- **DP-6: the cells-diff helpers' connection.** (a) `_set_threshold`, `_seed_approved_model`, the 10 000
  seeded Jobs and the rate-table seeding stay on the app DSN. (b) Move them to the owner pre-emptively.
  **Recommendation (a).** They write what the application writes, under grants (Evidence). Moving them
  would hide from the measurement a wall the application itself would hit. If W's green run stops on one,
  that is a STOP to the lead, and a dated line on FD-2093 by the scope rule "J and K join the same FD by
  dated line". It is never a silent move to the owner.

## Acceptance Standard

Each item is checked by a command a fresh reviewer can run. Items 1 and 2 apply to this plan.

1. **This delta passes the docs checks on its own branch.** `python3 scripts/audit-docs.py` prints no
   failing line except those for the working ids this branch uses (PL-2095, FD-2093, FD-2094, and SL-2096 and
   LG-2097 cited), and `python3 scripts/doc-index.py --check` agrees. After the mint both exit 0.
2. **No requirement range.** `grep -nE '(N?FR)-[0-9]+ *(-|to|–) *(N?FR-)?[0-9]+' <this file>` prints no line
   that stands for a set of ids.

SL-2096:

- **A1. The write set** is the Write set below, by `git diff --name-only origin/main...HEAD`. Nothing under
  `backend/src/`, `packages/`, `examples/`, `backend/migrations/`, `deploy/` or `backend/tests/conftest*.py`.
- **A2. One seeding path.** `git grep -n 'grant_demo_principals(' -- scripts/measure-p2-nfr-sweep.py` prints
  exactly one line, inside `_grant`, and that line names `env.owner_database`. `git grep -n '_grant(' -- scripts/measure-p2-nfr-sweep.py`
  shows the call sites that replaced `:604`, `:661` and `:897`.
- **A3. Red by cause, in the LG before the green (FD-2093).** At R1's commit,
  `test_the_seed_runs_on_the_owner_database_and_never_on_the_app_database` fails with its own assertion
  message naming the app database. A fixture, import, `AttributeError` or `NameError` is not the red. At
  R2's commit it passes.
- **A4. `create_app` never sees the owner.** A DB-free test builds `_Env` under dead-port DSNs, with app
  user `gip_app_login` and owner user `gipricing` on one database. It asserts
  `env.app.state.settings.database_url.get_secret_value()` equals `GIP_DATABASE_URL`, and that
  `env.owner_database`'s URL equals `GIP_MIGRATION_DATABASE_URL`. With `GIP_MIGRATION_DATABASE_URL` unset,
  `_Env()` exits with a message naming that variable.
- **A5. The guard, proven on broken input (DP-2 (a)).** One DB-free test per refusal: unset, template,
  different database, same user, and one accepting case. Each refusal is shown red by deleting its clause,
  the mutation is reverted, and the revert is proved by `git diff --stat` empty. The commands and outputs are
  in the LG.
- **A6. Red by cause (FD-2094).** At R1's commit, `backend/tests/test_measure_p2_nfr_sweep_storage.py` fails
  on `audit_events_rows` with `DataError` and `expected str, got UUID` in the text. Every other
  coalesce-shaped storage query in the same test passes. At R2's commit all pass. `dataset_versions_row`
  (a `scalar_one` over a row the empty database lacks) is named in the test as excluded, with that reason.
- **A7. The S2 failures reproduced, then cleared, on a `-T` copy (window W).** The red pass at R0's head
  prints `permission denied for table workspaces` from `cells-diff` and from `one-way`, and
  `expected str, got UUID` from `storage`. The green pass at R2's head ends `rc=0` for all three, at the
  sizes Task W names. They are wiring runs, not readings. Logs are SHA-first and rc-last (common brief item
  37), quoted in the LG.
- **A8. The app's runtime is untouched:** `git diff --name-only origin/main...HEAD -- backend/src` is empty.
- **A9. The import closure's tests are green** (common brief items 29 and 41).
  `tests/test_measure_p2_nfr_sweep.py` and `backend/tests/test_measure_p2_nfr_sweep_storage.py` pass, the
  second in a no-gate gap (item 32), with the closure's commands quoted in the LG. If LAST-2 has merged by
  then, they are re-run at the re-merged head (item 21; see Gate form).
- **A10. The gate:** one full code gate on the re-merged head, single or paired on the maintainer's word,
  every rc quoted, the skipped count not above baseline.

## Global Constraints

- **G1. The app's runtime code is not touched** (18:49:24). Nothing under `backend/src/`.
- **G2. The seed URL never names the template**: no command, test or window points either DSN at
  `gipricing` on the shared server (memories of 29 Oct; DP-2).
- **G3. Seed as the owner, serve as the app; nothing else moves to the owner** (DP-6).
- **G4. A failing test is never weakened** (common seat brief, item 13).
- **G5. Reading rules are not changed:** the module constants (`NFR_*_RULE`, bands, `CELLS_DIFF_RUNS`,
  `NFR_1443_SEEDED_JOBS`) are untouched. PL-1735 pre-registers them, and this slice is wiring.
- **G6. No range of ids in any file this plan writes.**
- **G7. Line numbers are re-derived at the slice's base.** This plan's are `bfeedd9a`'s.

## Needs

- **Seats:** one executor (model per `executor.md`) and one auditor. No decision-maker is needed once the
  DPs are ruled.
- **Ids:** PL-2095, SL-2096, LG-2097, FD-2093, FD-2094, all reserved. No other id is foreseen. A wall in W's
  green run is a dated line on FD-2093 (DP-6), not a new id.
- **DB:** one window, W, of about 45 min, on its own `createdb -T gipricing` copy per pass, granted in writing
  by the lead (common brief items 6 and 12).
  - Each pass gets a fresh copy, `gipricing_sl8406_<red|green>`. Both DSNs point at the copy:
    `GIP_DATABASE_URL=postgresql+asyncpg://gip_app_login:${GIP_APP_DB_PASSWORD:-gip_app_login}@localhost:5432/<copy>`
    and `GIP_MIGRATION_DATABASE_URL=postgresql+asyncpg://gipricing:gipricing@localhost:5432/<copy>`.
    The template's `alembic_version` is quoted at both ends.
  - Load: load1 and `free -g` are printed at START. It does not start at load1 ≥ the lead's grant limit (item
    15). It runs never beside a timed stage, a measurement or an ALONE window, and beside a gate only in that
    gate's pytest stage with 30 min of margin, as PL-2059's window rules state.
  - **Redis:** db 12. Every command is `redis-cli -n 12`, with `-n 12 dbsize` = 0 at START and END, and
    `-n 0 dbsize` quoted at both ends (item 33). The harness is switch-touching: its lifespan subscribes to
    `gip:switch:<env>:<tenant>`, which is not scoped by db (FD-1838). The window reads `PUBSUB NUMSUB` on
    that channel at START. No gate is in `test_deployment_switch*.py` during the window.
  - **MinIO:** the bucket `sl8406-w`, removed through the MinIO API only (item 18).
  - **END:** two quoted zeros (items 22 and 23): `redis-cli -n 12 dbsize` = 0, and the copy's
    `pg_database` count = 0.
  - The freMTPL2 data comes from the digest cache (`~/gi-pricing-plan.local/data/fremtpl2`). A third-party
    fetch failure is NOT RUN, not RED.
- **Gate cost:** one full code gate, about 2.5 h of wall time (PL-2059's and PL-2053's estimate for a full
  gate; not measured for this slice). No compose build, no migration, no contract change, and no frontend
  path, so `frontend.yml` does not fire (its filters: `frontend/**`, `docs/contracts/openapi/**`,
  `packages/pricing-core/src/pricing_core/modelling/**`). `python.yml` fires on `scripts/**`, `tests/**`
  and `backend/**`. No timed path changes: the harness is not run inside a gate.
- **Hours, gate not counted, an estimate:** R0 0.75 h, R1 1.5 h, R2 1 h, W 1 h with set-up, LG and records
  1 h, so **about 5.25 h**, plus about 1 h of audit.
- **Docker:** only the compose stack already up from tools-main. No compose up or restart. **NFR VM:**
  only S3 (below).

## Gate form (brief item (d)): by FILE, not directory

The slice's code paths are `scripts/measure-p2-nfr-sweep.py`, `tests/test_measure_p2_nfr_sweep.py` and
the new `backend/tests/test_measure_p2_nfr_sweep_storage.py`. The other heads, read on 2026-11-07:

- LAST-2: `#1454`, `sl-8343-table-row-parser` at `c43109a7f309e649d282998d3bd393777e1bcab6`.
- SL 8373: `sl-8373-spec-examples` at `a357933a606d3a9179961d8a8b1f8cee25591d0f`.

Each side's file list is `git diff --name-only origin/main...origin/<branch> | sort`.

- **Code ∩ LAST-2: empty. Code ∩ SL 8373: empty.** The command:
  `comm -12 <(printf '%s\n' scripts/measure-p2-nfr-sweep.py tests/test_measure_p2_nfr_sweep.py backend/tests/test_measure_p2_nfr_sweep_storage.py | sort) <(git diff --name-only origin/main...origin/<branch> | sort)`.
- **Records ∩:** `docs/INDEX.md` with both; `docs/findings/register.md` and `docs/roadmap.md` with LAST-2.
  These are mechanical merges: INDEX is regenerated, the register is rebuilt, and each roadmap row is its
  own line (common brief item 5; `mint-and-finish`).
- **Partition paths:** none in any of the three. Read as any path under `backend/migrations/`, `deploy/`,
  `backend/tests/conftest*`, `tests/conftest*`, `.github/`, `pyproject.toml`, `uv.lock` or `frontend/`;
  `grep -E` over both lists printed nothing. DP-4 (a) keeps this slice off `conftest_db.py`; (c) would put
  it there.
- **Imports read (item 29), both ways.** Into the slice: the harness is imported by path only, by its two
  test files. No test copies `scripts/` wholesale for it: `tests/test_doc_id_migrate.py` copies a fixture
  corpus and `doc-id.py`, `:40` and `:119-128`. Out of the slice: `_Env` builds `create_app`, which imports
  `app.api.demo` (`main.py:29`), which imports `app.demo.guide` (`api/demo.py:27`). **LAST-2 changes
  `backend/src/app/demo/guide.py`.** That is one-way: nothing LAST-2 runs imports this slice. SL 8373's code
  is `scripts/audit-docs.py`, `tests/test_spec_examples.py` and a fixture, and neither slice reads the other.
- **Verdict: pairable with either** (no shared code file, no partition path). The one consequence is item 21:
  if LAST-2 merges before SL-2096's gate, SL-2096 re-merges main and re-runs A9's two files at the re-merged
  head before its PR. The maintainer gives the word for single or paired.

## S3 form (brief item (f))

The fixed harness runs on nfr-bench-1 on Fri 13 Nov, on the frozen tree (which holds SL-2096, merged
before Thu 12). Each of **I** (`cells-diff`, all five runs, `--seeded-jobs` default 10 000), **J one-way**
(`one-way`, defaults) and **J storage** (`storage`, defaults) gets its own `createdb -T gipricing` copy,
`gipricing_nfrs3_<item>`, migrated to head, with **both DSNs naming that copy**:

```bash
export GIP_DATABASE_URL=postgresql+asyncpg://gip_app_login:<the VM's GIP_APP_DB_PASSWORD>@localhost:5432/$DB
export GIP_MIGRATION_DATABASE_URL=postgresql+asyncpg://gipricing:gipricing@localhost:5432/$DB
```

This is S2's `db-window.sh:16` form unchanged. **S2's `I-window.sh:14`, which exported the owner as
`GIP_DATABASE_URL`, is the form the ruling rejects, and is retired.**

What S3's brief (`brief-exec-nfrs3-2026-11-13.md`, a stub of 2026-11-05) gains when the lead completes it,
as a proposal for the lead:

- (1) A **DSNs** line naming both variables as above, `$DB` per item, never `gipricing`. The harness's
  guard (DP-2) refuses a template-named owner DSN in any case.
- (2) The login-role **provisioning** (`scripts/provision-app-role.py`, S2's `bringup-5`) **before any
  item**: I's first S2 attempt failed on `InvalidPasswordError` because it ran before provisioning.
- (3) **I, J one-way and J storage** in the cut-items list, each a `db-window.sh`-form window, one timed
  stage at a time, with `python -u`.
- (4) LG-1760 and CR 8315 / CR 8314 change from "BLOCKED, instrument" only on S3's reading lines.

K (contention) touches no database and is not affected.

## Tasks

### SL-2096: the row. Scope: A1 to A10; `01` NFR-468, NFR-470, FR-44; `03` NFR-1443 (measured by the instrument, not changed); lane WK-1178; after the pin, before Thu 12 Nov

Worktree `sl-8406-sweep-dsn`, from `origin/main` at its seat. Every line number above is re-derived at that
base (G7).

- [ ] **R0. Seams, no behaviour change (one commit).** Extract
  `async def _grant(env: _Env, workspace_id: UUID) -> dict[str, Any]`, which returns
  `seed.grant_demo_principals(env.database, workspace_id)`, still the app database. Route `:604`, `:661`
  and `:897` through it. Lift `_storage`'s per-version queries into a module constant
  `STORAGE_VERSION_QUERIES: dict[str, str]`, keyed by the names the reading prints (`dataset_versions_row`,
  `validation_reports`, `profiles`, `ingestion_runs_rows`, `ingestion_runs_source_bytes_read`,
  `audit_events_rows`), with the SQL text unchanged. Add a module-level
  `async def _version_scalar(session, query: str, version_id: UUID) -> int`, the body of today's `scalar`;
  `_storage` calls it. `tests/test_measure_p2_nfr_sweep.py` stays green (run-small). Record the R0 sha in
  LG-2097: W's red pass runs there.
- [ ] **R1. The failing tests, committed alone.**
  - In `tests/test_measure_p2_nfr_sweep.py`, add
    `test_the_seed_runs_on_the_owner_database_and_never_on_the_app_database`. It uses a stand-in `env`
    whose `database` and `owner_database` are distinct sentinels, and a `monkeypatch` of `_import_seed`
    returning a recorder for `grant_demo_principals`. It asserts the recorder saw `owner_database`, with a
    message naming which handle it saw. It is red at R1 by its assertion (A3).
  - The A4 and A5 tests are new seams. They are written here and fail at R1 as missing names; that is
    disclosed in the LG, and they are not counted as the red. A5's mutation proofs follow R2.
  - Create `backend/tests/test_measure_p2_nfr_sweep_storage.py`. It loads the script by path (the
    `importlib` form of `tests/test_measure_p2_nfr_sweep.py:29-30`). On the `database` fixture, it runs
    every `STORAGE_VERSION_QUERIES` entry except `dataset_versions_row` through `_version_scalar` with
    `new_uuid7()`, expecting `0`. It is red at R1 on `audit_events_rows` only (A6). It is DB-backed, so it
    runs in a no-gate gap or in W, never beside a gate (item 32).
- [ ] **R2. Green (one commit per defect).**
  - (i) FD-2093: `_Env` adds `self.owner_database`, built as `seed.py:458-460` builds it, and exits naming
    `GIP_MIGRATION_DATABASE_URL` when that is unset. `_grant` passes `env.owner_database`. Each arm disposes
    `owner_database` when it ends. `main()` calls `dsn_failure` (DP-2) before `asyncio.run` for `one-way`,
    `storage` and `cells-diff`, and exits with its message.
  - (ii) FD-2094: `audit_events_rows` becomes
    `… like '%' || cast(cast(:v as uuid) as text) || '%'` (DP-3).
  - Then A5's four mutations, each reverted. ruff, ruff format on the changed files, and mypy, each rc
    quoted (item 16).
- [ ] **W. The window (A7).** Red pass from a detached worktree of the seat's own at the R0 sha; green pass
  at R2's head. Each pass runs on a fresh copy:
  `cells-diff --only rows-10000 --seeded-jobs 10`, `one-way --fremtpl2-rows 2000 --wide-rows 2000`,
  `storage --fremtpl2-rows 2000`. Each command is under `timeout`, with `python -u`, and its log is
  SHA-first and rc-last. W also runs `backend/tests/test_measure_p2_nfr_sweep_storage.py` at R1 (red) and at
  R2 (green) if no no-gate gap came first. Clean-up is as Needs states. A wall past the seed is a STOP
  (DP-6).
- [ ] **G. The gate (A10).** Re-merge `origin/main` (a merge, never a rebase). Run A9's files at the
  re-merged head, then one full code gate on the maintainer's word, single or paired. The gate's lines go
  in LG-2097 before the auditor is seated.

### Write set

`scripts/measure-p2-nfr-sweep.py`; `tests/test_measure_p2_nfr_sweep.py`; new
`backend/tests/test_measure_p2_nfr_sweep_storage.py`; LG-2097; `docs/roadmap.md` (SL-2096's row, one
line, at the mint); this plan (`status:` only); FD-2093 and FD-2094 and their register rows (drafted on
this branch, minted with the slice); `docs/INDEX.md`.

### Files shared

Code: none with LAST-2 or SL 8373 (Gate form). Records: `docs/INDEX.md` with both, and
`docs/findings/register.md` and `docs/roadmap.md` with LAST-2, by re-merge.

## Hand-off (not this plan's writes)

- **The maintainer:** DP-1 to DP-6; the slice GO when the pin lands; the gate's word (single or paired).
- **The lead:** window W's grant and brief; the build seat; S3's brief items (1) to (4); the mint order
  (ids land in merge order: this slice's block after whatever merges before it).
- **The auditor:** A1 to A10 at `origin/main...sl-8406-sweep-dsn`; FD-2093 and FD-2094 closed by the
  slice's close commit, and SL-2096's row read at `origin/main` after the merge (common brief item 42).

## Self-review

1. **Ruling coverage.**
   - 18:49:24: separate owner DSN (DP-1, R2 (i)); app DSN serves (A4); red first on a `-T` copy (A3, A6,
     A7); app runtime untouched (A8, G1); seed URL never the template (DP-2, G2); gate single or paired on
     the word (A10, Gate form); J and K join by dated line (DP-6).
   - 18:54:18: `:661` joins FD-2093 (DP-5, A2); `:841` → `:815` is FD-2094, the same slice (DP-3, A6).
   - 18:54:59 (a) to (f): each is mapped under Authority.
2. **Every cite read** at `bfeedd9a`: the script lines in Evidence; `seed.py:346`, `:448-461`;
   `config.py:121-129`; `main.py:29`, `:114`, `:278`; `immutability.py:171`; the grants migration's rows;
   `conftest_db.py:153`, `:205`, `:1252`, `:1307`; `python.yml:118`, `:343-344`; `api/demo.py:27`;
   `test_doc_id_migrate.py:40`, `:119-128`; S2's logs by line. **Not run:** whether `_Env()` builds with no
   network under dead-port DSNs (A4). If it does not, the executor reports it, and A4 falls back to
   asserting on a constructed `Settings` pair. That is a STOP, not a silent change.
3. **Placeholders:** none. Test names, `_grant`, `_version_scalar`, `STORAGE_VERSION_QUERIES` and
   `dsn_failure` agree across DPs, Acceptance and Tasks.
4. **Sums:** hours 0.75 + 1.5 + 1 + 1 + 1 = 5.25.
5. **Calendar**, from `date -d … +%A`: Sat 7 Nov (today), Thu 12 Nov (freeze), Fri 13 Nov (S3).
6. **No range of requirement ids.** Estimates are marked: the hours, W's 45 min and the gate's 2.5 h.
7. **The plan rules nothing:** six DPs, each with a recommendation; the gate form is a reading, and the
   word is the maintainer's.

## Dated delta, Sat 7 Nov 2026 (task W and A7): the accepted size is 100000 rows for one-way and storage

This section is appended. No sentence above it is edited: Task W and A7 still read "2000" as written, and
this delta is the record that the 2000-row green could not exist.

**Ruling.** To-lead "2026-11-07 21:03:10 GMT" (the maintainer, by delegation): "A7 one-way and storage:
ACCEPT 100000 rows as A7's size, by dated delta on PL-2095 task W and A7". The reason it quotes: "at 2000
and 20000 rows the SEED's own fit raises DegenerateFitError ("9 level(s) below the relativity floor 0.01")
at R0 and at the head alike, before any code under test; at 100000 the red/green splits exactly on the two
defects". A7's `cells-diff --only rows-10000 --seeded-jobs 10` stays at its size and is MET.

**The size now accepted.** `one-way --fremtpl2-rows 100000 --wide-rows 2000` and
`storage --fremtpl2-rows 100000` (the one-way `--wide-rows` stays 2000). Task W's
`--fremtpl2-rows 2000` for the same two arms is superseded by this line, not edited.

**Evidence.** Logs are in `~/gi-pricing-plan.local/scratch/sl-8406/`; each is SHA-first and rc-last.
R0 is `2e609db4832ac428e9877d4335de6e32f71b529c`; the head the window ran on is
`86b63e54ed40e41f3318c7ce276c33563f130268` (not this branch's later tip).

- **At 2000 rows, the seed's fit raises before any code under test.** The line is, verbatim to the colon:
  `model.DegenerateFitError: the fit is degenerate: 9 level(s) below the relativity floor 0.01: area[F] = 1.36e-07, region[R23] = 1.16e-07, region[R42] = 5.7e-08, ...`
  - at R0: `w-a7red-oneway.log:103` and `w-a7red-storage.log:103`, both rc=1.
  - at the head: `w-a7green-storage.log:103`, rc=1. A one-way run at 2000 rows at the head was not logged
    (no `w-a7green-oneway.log`); its seed path is the same one `w-a7red-oneway.log` shows failing.
- **At 20000 rows it still raises, with one level.** `w-probe-storage-20000.log:103` (head, `storage`, rc=1):
  `model.DegenerateFitError: the fit is degenerate: 1 level(s) below the relativity floor 0.01: region[R43] = 2.15e-06. The seed holds too few rows for these levels to carry a claim; seed more rows ...`
  There is no 20000-row log at R0. The ruling's "both ends" is quoted here for 2000 only, at R0 and at the head.
- **At 100000 rows the red/green splits on the two defects.**
  - R0 red: `w-bigred-oneway.log:120` `asyncpg.exceptions.InsufficientPrivilegeError: permission denied for table workspaces`;
    `w-bigred-storage.log:115` `TypeError: expected str, got UUID`. Both rc=1.
  - head green: `w-biggreen-oneway.log` rc=0; `w-biggreen-storage.log` rc=0; `w-probe-storage-100000.log` rc=0.
- **Process note carried from the ruling:** a plan's run size is proved by one run before it is written as
  the acceptance size. A7's 2000 was not.
