---
id: PL-8280
family: plan
kind: map
title: WK-1178 — FD-1965, the examples seed fixture migrates its own scratch database (test-only, red-first) — a dated Work-plan delta cutting one slice
status: draft                   # draft → active → superseded | retired (§1.2a) — draft while DP-1 and DP-2 are open; L1: draft→active rides the slice's PR
created: 2026-10-29             # drafted 2026-10-29 under working id 8280
owner: planner
tree: 447bcfd6ea73739c1f327682c6ee9b0caa61470a
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [FD-1965, WK-1178, PL-1927]
---

# PL 8280 — WK-1178: FD-1965, the seed fixture migrates its own scratch database (a dated Work-plan delta)

> **For agentic workers:** a **dated Work-plan delta** under Lean P2 L5 (`document-ids.md` §1.6, PL
> row: one plan per Work, slices as rows, no per-slice leaf; a change is one dated delta, a new `PL-`
> that `relates:` the Work's plan). WK-1178 has no Work plan; as `PL-1927` did, this delta `relates:`
> the records it builds on. It cuts **one slice row**. REQUIRED SUB-SKILL: executing-plans, task by
> task; steps use checkbox (`- [ ]`) syntax. The executor also binds:
> - `test-driven-development`: every red is seen red **by its cause** at the slice's base, its line in
>   the `LG-` before the fix;
> - `python-test`: the `req` marker on the new test, and the negative (refusal) test;
> - `dev-commands`: the two DSNs (FD-1729), the template DB rule, the DB window;
> - `git-hygiene`: the two commits named below, Conventional Commits, the role/model trailer.
>
> The executor is spawned from `.claude/roles/executor.md` and reads [`README.md`](README.md)'s five
> unchecked conventions before the first step.

Filed under **working id 8280** (brief `~/gi-pricing-plan.local/handover/brief-plan-seedfix-2026-10-29.md`,
lead 29). The slice is **SL 8278** and its ledger **LG 8279**, reserved at the maintainer's entry
"2026-10-29 14:22:02 GMT" (minted in merge order at the slice's turn; that entry names the expected numbers). Written 2026-10-29 from
17:16 GMT by the planner (seat plan-seedfix, Opus 5.5, effort medium). **Tree read:** `origin/main`
`447bcfd6ea73739c1f327682c6ee9b0caa61470a` (#1404). Every `file:line` below is at that tree unless
marked otherwise; the executor re-reads its own at its base (Task 0).

## Where this row goes, and why a new delta

**A new delta, not a row in an open one.** At `447bcfd6`, 50 plans carry `work: WK-1178`; three are
`draft` (`PL-1520`, `PL-1705`, `PL-1735`) and none of the three names further rows
(`grep -n -i 'further rows' docs/plans/*.md` prints one line, `PL-1071:1413`, a W37-8 plan, not
WK-1178). `PL-1927` is `active` (frozen); its row 5 (S1c) was added in place by a dated line because
the ruling it executed named PL-1927 itself ("a follow-up slice under PL-1927 (a dated PL delta row,
SL reserved at that row)", to-lead "2026-10-26 11:38:32 GMT"). The ruling for this slice (below)
names no plan, and the frozen-plan rule (`planner.md` Lean P2 L5: "new slices … are one dated
Work-plan delta … a new `PL-` that `relates:` the Work's plan and leaves it unedited") applies. So this
file is a new delta; `PL-1927` is unedited.

## Authority

Read in full in `~/gi-pricing-plan.local/channel/to-lead.md` on 2026-10-29 between 17:05 and 17:15 GMT.

- **"2026-10-29 14:21:02 GMT — Maintainer: my 14:19:11 ruling (2) is WITHDRAWN on the lead's root
  cause, verified by me; (2') ADOPTED"**, item 2, verbatim: *"Fix **red-first in its own small
  test-only slice tomorrow, Fri 30 am** (not riding the beat slice — one thing per slice): the fixture
  also sets `GIP_MIGRATION_DATABASE_URL` to the scratch database as the owner role; red = the three
  tests with data present and the env pointing elsewhere; green = the three passing; plus a control
  that the fixture refuses when no migration URL can be formed. Its SL/LG reserved after S1c's ids."*
- **"2026-10-29 14:22:02 GMT"**: the ids — SL 8278 / LG 8279, minted in merge order (Fri 30 am).
- **"2026-10-29 14:42:55 GMT"**, the `ruff format --check` paragraph, verbatim: *"the one-file format
  fix rides the **first code slice that touches `backend/tests/test_transformations.py`** or, if none
  does before the freeze, Friday's seed-fixture slice as a named, separate commit — never the docs
  PR."* (Process-backlog row "2026-10-29 14:44 GMT", `docs/process/process-backlog.md:96`.)
- **"2026-10-29 17:11:12 GMT"** item (1): *"the data goes in a throwaway checkout, never a slice
  worktree"*.
- **The finding:** `FD-1965` (minted by #1405, merged as `7ceff4a1` after this plan's tree; this branch re-merges it): its Finding, Evidence and Remedy sections are the specification of this fix.

## Goal

`scratch_seed` (`examples/fremtpl2/test_seed.py:120–165`) migrates **and seeds** the scratch database it
creates and no other, whatever `GIP_MIGRATION_DATABASE_URL` the process inherits; and it refuses by
name, before creating anything, when it cannot form that URL. Test-only: no production line, price or
hash moves.

## Evidence at `447bcfd6` (read for this plan)

- **E1.** `backend/migrations/env.py:31–38`: `_migration_url = load_settings().migration_database_url`;
  `None` → `RuntimeError("GIP_MIGRATION_DATABASE_URL is not set: …")`. No fallback (FD-1729).
- **E2.** `examples/fremtpl2/test_seed.py:138–158`: `name = f"scratch_sl1409c_{uuid4().hex[:8]}"`; the
  admin URL is the literal `postgresql+asyncpg://gipricing:gipricing@localhost:5432/postgres` (:139);
  the fixture sets only `GIP_DATABASE_URL` (:151) and runs `uv run alembic upgrade head` with
  `env=dict(os.environ)` (:152–158). The skip is :135–136 (no `data/freMTPL2freq.arff`).
- **E3 — wider than migration.** `examples/fremtpl2/seed.py:448–466`: the seed itself reads
  `settings.migration_database_url` and runs `grant_demo_principals` (workspace, built-in roles, users,
  role assignments; `seed.py`, `async with database.unit_of_work()`) on **that** database. So with the
  variable pointing elsewhere, the seed **writes the demo principals into the foreign database**, not
  only migrates it. The fix below covers both, because the seed runs in-process after the
  fixture's `monkeypatch.setenv`. *Inferred from the code, not observed:* the proof run at
  `18728e68` (to-lead "2026-10-29 14:23:05 GMT", migration URL = the rebuilt template `gipricing`) may
  have committed those rows into the template. This plan does not read any database; see Hand-off.
- **E4.** The three tests: `test_the_seed_reruns_against_a_seeded_database` (:168, no `req` marker),
  `test_every_seeded_ingestion_run_balances_its_rows` (:191, FR-32, FR-31),
  `test_a_small_seed_is_refused_for_its_degenerate_fit` (:235, no `req` marker; calls
  `seed.run(2000)`).
- **E5 — CI.** `.github/workflows/python.yml:21,59` path-filters on `examples/**` and `backend/**`;
  `pyproject.toml` `testpaths` includes `examples/fremtpl2`. CI has no `.arff`, so it skips the three
  and runs every other test in the file (and the new control, which needs neither data nor a DB).
  `frontend.yml`'s paths (`frontend/**`, `docs/contracts/openapi/**`,
  `packages/pricing-core/src/pricing_core/modelling/**`, its own file) match neither changed file.
- **E6.** `backend/tests/test_transformations.py`: `ruff format --check` rc 1 at `18728e68` and at
  S1c's `eb64354f` (process-backlog `:96`). S1c (#1405, merged `7ceff4a1`) edited this file (a docstring
  re-point, to-lead "2026-10-29 14:42:55 GMT") and did not carry the format fix: `git show
  origin/main:backend/tests/test_transformations.py | uv run ruff format --check --stdin-filename
  backend/tests/test_transformations.py -` reads rc 1 at `7ceff4a1` (read 2026-10-29 ~17:25 GMT).
  #1405 also changed `backend/tests/conftest_db.py` (+96 lines); this slice does not touch it.

## Decision points

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-1 | What is "no migration URL can be formed" when the admin URL is a literal (E2)? | (a) the fixture derives the owner URL from the admin URL (`sqlalchemy.engine.make_url(admin).set(database=name)`) in a module-level helper that refuses by name when the admin URL has no user, password or host; the control calls the helper with such a URL · (b) the admin URL comes from a new env var with the literal as default; the control unsets it · (c) no control; record the case as unreachable | **(a)**: the only reachable failure is a malformed admin URL, and (a) tests exactly that, DB-free, in CI; (b) adds configuration for a fixed value; (c) drops a ruled control | decision point | yes (Task 3) | |
| DP-2 | Which gate does the slice need? (seat brief item 30: anything outside `docs/` → the full code gate by default) | (G1) the full code gate, both halves · (G2) the narrow cover below | **(G2)**, below; (G1) if G2 is not granted | decision point | yes (Task 6) | |

**DP-2 (G2), the narrow cover, proposed.** The diff is two test files and the slice's records. Nothing
imports a test file, so the import closure of `test_seed.py` is `test_seed.py` (seat brief item 29),
and the format commit changes no AST (DP-T27-6's criterion, to-lead "2026-10-26" item 6, applies to it
unstripped). The cover: (i) `uv run ruff check .` rc 0 and `uv run ruff format --check` on the two
files rc 0; (ii) `ast.dump` of `backend/tests/test_transformations.py` byte-equal before/after the
format commit (script and both digests in the `LG-`); (iii) `examples/fremtpl2/test_seed.py` whole
through `run-small.sh` with **no** data (the CI form: the three skip, the control runs); (iv) the DB
window on the throwaway checkout (Task 5); (v) the docs half of item 30 (the gate-2 checks and the
eight docs-audit pytest files via `run-small.sh`, whose failing ids at an unminted head are the 1(f)
13-id set, md5 `3de106a91734`, and must be 0 after the mint); (vi) PR CI: python, docs,
history-policy (frontend does not fire, E5). The frontend half adds nothing (E5); the backend suite
reads neither file's fixture. **Not a role, DSN or shared-fixture change**: `scratch_seed` is
file-local and `conftest*.py` is not touched, so the "full suite at the re-merged head" rule (26 Oct)
does not bite; if the slice's own diff (`origin/main...<slice branch>`) touches `conftest*.py`, `env.py`
or `seed.py`, G2 lapses and G1 applies.

## Tasks

| Order | Slice | Scope (what the `LG-` quotes) | Requirements, each id | Depends on | Lane | DB | Size |
|---|---|---|---|---|---|---|---|
| 1 | **SL 8278 / LG 8279** — FD-1965: the seed fixture migrates its own scratch database (test-only, red-first) | Tasks 0 to 7 below | none amended; the tests carry FR-31, FR-32 (existing markers, E4) | #1405 (S1c, which minted FD-1965) merged — met, `7ceff4a1`; DP-1 and DP-2 ruled; a granted DB window in a no-gate gap (seat brief items 12, 32) | examples (test-only) | **yes** — the shared server, Task 5 only | ½ day |

The SL row mints at the slice's turn, in the slice's own PR, as a row under WK-1178 in
`docs/roadmap.md` §6 (PL-1927's precedent, rows 1 to 5). The slice writes **no spec**: FD-1965 is a
test defect and no FR changes.

**Write set.** `examples/fremtpl2/test_seed.py`; `backend/tests/test_transformations.py` (format only,
its own commit); `LG 8279`; the SL row; FD-1965's close in place and its register row
(`docs/findings/register.md`).

- [ ] **Task 0. Base.** Branch from `origin/main` at or after `7ceff4a1` (#1405). Re-read E1–E4 at the base, and
  `git diff --name-only 447bcfd6..<base> -- examples/ backend/migrations/ backend/tests/conftest*.py`
  (quoted in the `LG-`; non-empty → re-read the changed lines and report before Task 1). Run
  `uv run ruff format --check backend/tests/test_transformations.py` at the base: rc 1 → Task 6's
  format commit is owed; rc 0 (a slice before this one fixed it) → the commit is dropped and the `LG-`
  says why.
- [ ] **Task 1. The throwaway checkout.** `git worktree add` a throwaway checkout of the base (a path
  under the executor's own scratch dir, never the slice worktree); `uv sync --all-packages --frozen`
  there; run `examples/fremtpl2/fetch.py` there (or copy the two `.arff` into **its** `data/`). The
  slice worktree never holds the `.arff` (`git -C <slice wt> status --ignored -- examples/fremtpl2/data`
  quoted at the END: no `.arff`).
- [ ] **Task 2. Reds R1–R3 (in the DB window, Task 5's setup first).** In the throwaway at the base,
  with the data present and `GIP_MIGRATION_DATABASE_URL` pointing at the **foreign** database (Task
  5's `scratch_pl8280_foreign`, at head — never the shared template, E3), run the three tests (E4) by
  node id. Each fails by cause `UndefinedTableError: relation "role_assignments" does not exist`; the
  three FAILED lines verbatim in the `LG-`. Also read back the foreign database's demo rows
  (`select count(*) from workspaces where name = 'freMTPL2 demo'`) before and after: the after count
  greater than the before count is the second red (E3: the seed wrote into the foreign database),
  quoted. **O1 (an observation, not a red):** the same three with `GIP_MIGRATION_DATABASE_URL`
  unset fail at the fixture with `CalledProcessError`, env.py's `RuntimeError` in the captured
  stderr; quote one line.
- [ ] **Task 3. The fix (on DP-1's ruling; (a) shown).** In `test_seed.py`: a module-level helper
  `_scratch_owner_url(admin: str, name: str) -> str` built on `make_url`, raising
  `RuntimeError("scratch_seed cannot form the owner URL for <name> …; it refuses rather than migrate
  an inherited GIP_MIGRATION_DATABASE_URL")` when the admin URL has no user, password or host. The
  fixture calls it **before** `CREATE DATABASE` and sets **both** `GIP_DATABASE_URL` and
  `GIP_MIGRATION_DATABASE_URL` to the result (the owner role `gipricing`, as today's URL). One commit:
  `test(examples): the seed fixture migrates and seeds its own scratch database (FD-1965)`.
- [ ] **Task 4. The control C1.** `test_the_scratch_fixture_refuses_when_no_owner_url_can_be_formed`,
  `@pytest.mark.req("FR-31")` *(the marker is the executor's to confirm against `01` §3 at the base;
  any FR the seed path already carries in this file is acceptable, none new)*: with
  `GIP_MIGRATION_DATABASE_URL` deleted (`monkeypatch.delenv(..., raising=False)`), the helper given
  `postgresql+asyncpg:///postgres` raises `RuntimeError` matching `cannot form the owner URL`. It needs
  neither data nor a DB, so it runs in CI. **Proved red on broken input:** with the helper's guard
  deleted (one edit, assert count 1), C1 fails `DID NOT RAISE`; restored, passes — both lines in the
  `LG-`. Same commit as Task 3, or the next.
- [ ] **Task 5. The DB window (the lead's written grant; load1 and `free -g` at start, item 15).**
  On the shared server (the fixture's admin URL is that server's, E2; the condition of
  "2026-10-29 14:22:02 GMT" applies): `select datname from pg_database order by 1` before; create
  `scratch_pl8280_foreign` as `gipricing` and `alembic upgrade head` it (owner DSN); Task 2's reds at
  the base; then, in the throwaway at the head, the **greens**: G1 the three pass with the same foreign
  URL set, and the foreign demo-row count before = after; G2 the three pass with
  `GIP_MIGRATION_DATABASE_URL` unset. Then drop `scratch_pl8280_foreign`; `select datname` after equals
  before (no `scratch_sl1409c_*`, no `scratch_pl8280_*` left); the shared `gipricing` database is never
  written; redis: the seed's own db is 11, 12 or 13 (item 33), `dbsize` 0 quoted after FLUSHDB; the
  window's two zeros (item 23).
- [ ] **Task 6. The format commit.** If Task 0 found rc 1:
  `uv run ruff format backend/tests/test_transformations.py`, its own commit,
  `style(backend): ruff format backend/tests/test_transformations.py (process-backlog 2026-10-29 14:44 GMT)`,
  no other change in it; `ast.dump` equal before/after (DP-2 (ii)). Then the gate DP-2 rules.
- [ ] **Task 7. Records.** `LG 8279` (`docs/_templates/LG.md`; scope = this row; every red/green line
  with `head=` first and `rc=` last, item 37); the SL row; FD-1965 closed in place with the merge
  reference at the read-back, its register row; mint SL 8278 / LG 8279 / PL 8280 at the slice's
  turn (items 17, 19, 26), PL 8280 `draft` → `active` in the same PR (L1).

## Acceptance Standard

Each item is checked by a command a fresh reviewer can run from the repository root, at the slice PR's
merge tree, with the range `origin/main...<slice branch>` named. "Red" means seen red **by the stated
cause** at the slice's base, its line verbatim in `LG 8279` before the fix.

**This delta**

1. At this branch's head, `python3 scripts/audit-docs.py` (one gate-2 docs check) names this file only
   in check 31/32's working-id lines for 8280, and check 28 does not name it;
   `python3 scripts/doc-index.py --check` exits 0.
2. `grep -nE '(N?FR)-[0-9]+ *(-|to|–) *(N?FR-)?[0-9]+' <this file>` prints no line that stands for a
   set of ids.

**The slice (SL 8278)**

3. `git diff --name-only origin/main...<slice branch>` lists only `examples/fremtpl2/test_seed.py`,
   `backend/tests/test_transformations.py` (only if Task 0 read rc 1), and files under `docs/`.
4. The format change is its own commit: `git log --format=%s origin/main..<slice branch> --
   backend/tests/test_transformations.py` prints exactly one subject, beginning `style(backend): ruff
   format`, and `git show --stat` of it lists that one file.
5. `LG 8279` carries R1–R3 red by cause `UndefinedTableError: relation "role_assignments" does not
   exist` at the base with data present and the migration URL on `scratch_pl8280_foreign`, each line
   with its node id, and the foreign demo-row count rising (the E3 red).
6. `LG 8279` carries G1 (the three passed, same foreign URL; foreign demo-row count before = after)
   and G2 (the three passed, migration URL unset) at the head, in the throwaway checkout.
7. `uv run pytest -q examples/fremtpl2/test_seed.py -k owner_url` passes with no data present (C1),
   and `LG 8279` carries C1's mutation red (`DID NOT RAISE`) and its restore green.
8. `grep -n 'GIP_MIGRATION_DATABASE_URL' examples/fremtpl2/test_seed.py` shows the fixture setting it,
   and the helper call precedes `CREATE DATABASE` in `scratch_seed` (read the lines).
9. `uv run ruff check .` rc 0; `uv run ruff format --check examples/fremtpl2/test_seed.py
   backend/tests/test_transformations.py` rc 0.
10. The window's read-backs in `LG 8279`: `pg_database` names before = after, no `scratch_pl8280_*`
    or `scratch_sl1409c_*` left; redis `dbsize` 0 on the seat's db; no `.arff` under the slice
    worktree.
11. The gate DP-2 rules, its END row and rc files in `LG 8279`; after the mint, audit-docs, doc-index
    `--check` and register-lint exit 0; PR CI python, docs and history-policy green.
12. FD-1965 reads closed in place and in `docs/findings/register.md`, naming the slice's minted `SL-` id.

## Global Constraints

- **Two DSNs (FD-1729):** migrations run as the owner; `env.py` never falls back
  (`backend/migrations/env.py:33–38`; `dev-commands` "Two DSNs"). The fixture's owner role is
  `gipricing`, as its URL already is (E2).
- **The template DB `gipricing` is migrations-only** (`dev-commands`, the template rule): no red, green
  or proof in this slice points `GIP_MIGRATION_DATABASE_URL` at it.
- **No data in a slice worktree** (to-lead "2026-10-29 17:11:12 GMT" item (1)).
- **No production or spec change**: `examples/fremtpl2/seed.py`, `backend/src/**`, `env.py` and
  `docs/specs/**` are outside the write set.
- **DB lane:** the window is the lead's to grant in writing (seat brief item 12); never beside a held
  gate (item 32).

## Hand-off (not this plan's writes)

- **For the lead (E3), unverified:** the seed's owner connection follows `GIP_MIGRATION_DATABASE_URL`,
  so a run with it on the template may have committed demo principals there. A read-only
  `select count(*) from workspaces` on `gipricing` would settle it; the template rule
  (`dev-commands`) names the rebuild if so. Whether to look, and when, is the lead's (DB lane).
- **The S1c gate** (`scratch/s1c-gate/s1c-gate.sh:72`) pointed the variable at the gate DB, so the
  seed's principals went there (dropped at END); no action.
- **DP-1, DP-2** are the decision-maker's / maintainer's to rule; the plan freezes (`active`) only after.
- **Not this plan:** which gate step should run `ruff format --check` (process-backlog `:96`'s second
  limb); the FD-1661 beat slice (SL 8275 / LG 8276).

## Self-review

- Every 14:21:02 (2') clause has a place: the fixture sets the migration URL to its scratch DB as the
  owner role (Task 3, Acceptance 8); red = the three with data present and the env elsewhere (Task 2,
  Acceptance 5); green = the three passing (Task 5, Acceptance 6); the refusal control (Task 4, DP-1,
  Acceptance 7); own small test-only slice (the row, Acceptance 3).
- The 14:42:55 format fix: a named separate commit, dropped only on a base reading rc 0 (Tasks 0, 6;
  Acceptance 4).
- The data rule: a throwaway checkout (Task 1, Acceptance 10).
- One departure from the brief's wording, named: the red's "other at-head database" is a disposable
  one, not the template, because of E3.
- The open choices are DP-1 and DP-2, never a silent pick; Task 3 and 4's names follow DP-1 (a) and
  change with the ruling.
