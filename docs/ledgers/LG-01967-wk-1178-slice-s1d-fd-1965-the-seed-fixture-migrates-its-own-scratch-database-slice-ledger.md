---
id: LG-1967
family: ledger
title: WK-1178 slice S1d — FD-1965, the seed fixture migrates its own scratch database, red first (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-10-29   # drafted 2026-10-29 under working id 8279
owner: executor
tree: 1e17ec6382de5919b6e3011242b584a59bb880e7   # origin/main at S1d's branch cut (#1407)
slice: SL-1966
phase: P2
work: WK-1178
plans: [PL-1927]
corrected_by: []
relates: [FD-1965, PL-1927, FR-31, FR-32]
---

# LG-1967 — WK-1178 slice S1d: FD-1965, the seed fixture migrates its own scratch database, red first

Working ids (space form in prose): **SL-1966** (this slice), **LG-1967** (this ledger). Executor seat
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
- [x] **S1d-6. The format commits, then the gate** (DP-S1d-2 G2 narrow cover; entries 3, 4, Gate).
- [x] **S1d-7. Records** (less the mint, which is the lead's).

### Gate

DP-S1d-2 G2 (the narrow cover), unminted head `8628ff39247d78316875df0df413740457096459` (docs half;
the code half is entry 3 and 4's lines, run at `5d8c2649`/`e7244a2a`, the format commit after it being
AST-equal). Logs under `~/gi-pricing-plan.local/scratch/s1d/`.

| Check | Result |
|---|---|
| `git diff --stat origin/main...HEAD` | only `backend/tests/test_transformations.py`, `examples/fremtpl2/test_seed.py`, `docs/ledgers/LG-1967-…`, `docs/process/process-backlog.md` |
| `uv run ruff check .` (at `5d8c2649`) | rc=0 |
| `ruff format --check` both files (at `e9d5d6fe`) | rc=0 |
| `test_seed.py`, no data, `run-small.sh` (at `5d8c2649`) | `15 passed, 3 skipped`, rc=0 |
| `audit-docs.py` | rc=1: check 32 on LG-1967, SL-1966 (unminted) and check 39 (INDEX stale), nothing else |
| `doc-index.py --check` | rc=1 (INDEX stale until the mint) |
| `register-lint.py` | rc=0 |
| `req-coverage.py` | rc=0 |
| `generate-contracts.py --check` | rc=0 ("58 generated contracts match the models") |
| 8 docs-audit pytest files, 3 `run-small.sh` runs | 6 + 4 + 3 = 13 failed (`docs-failed13.txt`), 118 + 106 + 20 passed |

The 13 are the 1(f) set (tests that run `audit-docs`, which fails on this slice's own unminted ids).
The row quotes md5 `3de106a91734` for it; its predicate is not stated, so no digest of mine is claimed
to match it. After the mint they are owed 0 (the lead's step).

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

### Audit (auditor, 2026-10-29)

Auditor seat aud-s1d (Sonnet 5.5, effort medium), read-only. Range: `origin/main...origin/draft/sl-8278`, head `2cf61612e0aeb79640f4dbef5263784d1fb7da46` (re-read by `git ls-remote` before and during the audit: unchanged). Base `origin/main` `1e17ec63`. Verdicts are proposals; the lead issues them.

**Scope (from the spec first).** PL-1927 "Delta, row 6 (S1d)" Tasks S1d-0..7, Evidence E-d1..E-d6, Acceptance d1–d10; FD-1965's remedy incl. its Widened paragraph (the fixture sets BOTH `GIP_DATABASE_URL` and `GIP_MIGRATION_DATABASE_URL` to its own scratch DB via `_scratch_owner_url`, refusing by name; the seed's `grant_demo_principals` write into a foreign DB is covered); control C1; DP-S1d-1 (a); DP-S1d-2 G2; and the rulings of to-lead "2026-10-29 19:03:34 GMT" ((1) a second format-only commit on `examples/fremtpl2/test_seed.py` with `ast.dump` equality, d7 and G2 (i) rc 0 on both files, d2 per file; (2) O1 accepted as quoted, gap noted) and "18:57:05 GMT" (foreign createdb/dropdb in the window).

| Item | Evidence | Proposed verdict |
|---|---|---|
| d1 | `git diff --name-only origin/main...origin/draft/sl-8278` = `backend/tests/test_transformations.py`, `docs/ledgers/LG-1967-…`, `docs/process/process-backlog.md`, `examples/fremtpl2/test_seed.py`. Nothing else; no `conftest*.py`, `env.py`, `seed.py` (G2 lapse condition not triggered). | delivered, evidenced |
| d2 | `git log --format=%s origin/main..HEAD -- backend/tests/test_transformations.py` = exactly one subject `style(backend): ruff format …` (5d8c2649), `show --stat`: that one file, 121+/76−. Per file for `test_seed.py` (ruling 1): `style(examples): ruff format …` (e9d5d6fe), `test(examples): control C1 …` (e7244a2a), `test(examples): the seed fixture … (FD-1965)` (c44fa2d7); e9d5d6fe touches that one file only. | delivered, evidenced |
| d3 | red.log (`head=1e17ec63…`, throwaway, data present, migration URL on `scratch_s1d_foreign`): lines 59–61 the three FAILED node ids, line 62 `3 failed in 36.99s`, line 63 `rc=1`; the cause read in the asserts: line 18 `error = UndefinedTableError('relation "role_assignments" does not exist')`, line 37 `sqlalchemy.exc.ProgrammingError … UndefinedTableError … "role_assignments" does not exist` (not only the summary). Foreign demo count 0 → 3 is in LG Build log entry 2 only; red.log carries no count line. | delivered; the count limb rests on the LG's prose alone (see Findings 2) |
| d4 | green.log (`head=e7244a2a…`): G1 `3 passed in 216.19s`, `G1 rc=0`, foreign demo before=3 after=3 (the 3 left by the reds, so "no new write" is what 3=3 proves); G2 (variable unset) `3 passed in 202.44s`, `G2 rc=0`, after=3. | delivered, evidenced from logs; throwaway removed, not re-runnable |
| d5 | c1.log: green `1 passed in 0.87s` (data-free, DB-free); mutated (`if False and missing`) `Failed: DID NOT RAISE RuntimeError`, `1 failed in 0.95s`; restored `1 passed in 0.86s`. CI-run form confirmed by g2cover.log (15 passed, 3 skipped, no data). | delivered, evidenced |
| d6 | `git show origin/draft/sl-8278:examples/fremtpl2/test_seed.py \| grep -n`: `_scratch_owner_url` called at :172, `CREATE DATABASE` at :182, `setenv("GIP_MIGRATION_DATABASE_URL", url)` at :185 (and `GIP_DATABASE_URL` :184). Refusal message (:143–148) = `scratch_seed cannot form the owner URL for {name}: the admin URL has no {user, password, host — whichever missing}; it refuses rather than migrate an inherited GIP_MIGRATION_DATABASE_URL`; it names the missing part(s); C1 asserts all three named for a bare `postgresql+asyncpg:///postgres`. | delivered, evidenced |
| d7 | Re-run by me, read-only, on the head blobs via `ruff … --stdin-filename`: `ruff format --check` rc 0 for both files; `ruff check` rc 0 for both. Repo-wide `ruff check .` rc 0 at 5d8c2649 is the LG's claim; no log file exists for it (the delta is two files, both checked clean). | delivered; repo-wide run unlogged |
| d8 | LG entry 2 END: datname after = before, no `scratch_s1d_*`, template non-empty tables unchanged (`alembic_version=1 environments=3 tenant_marker=1`), redis db 11/12/13 dbsize 0, no `.arff` in the slice worktree. Prose only; no log carries these read-backs. | delivered, prose-evidenced |
| d9 | Gate = G2 (DP-S1d-2). Code half: cover confirmed below. Docs half: unminted head 8628ff39: audit-docs rc 1 (4 FAILED: check 32 ×3 on LG-1967/SL-1966, check 39 INDEX stale), doc-index --check rc 1, register-lint rc 0, req-coverage rc 0, generate-contracts rc 0. The 13 pytest failures: see below. Post-mint audit-docs / doc-index / register-lint rc 0 and PR CI python/docs/history-policy green are owed to the mint and the PR. | not yet evidenced — owed to the mint (reassigned: lead/mint seat) |
| d10 | FD-1965 close drafted in `scratch/s1d-aud/fd1965-close.md`, both limbs named; lands in the PR. | not started (draft supplied) |
| O1 | o1.log: `CalledProcessError … ['uv','run','alembic','upgrade','head'] returned non-zero exit status 1` at the fixture; env.py's `RuntimeError` not in the captured text. Accepted by the lead (19:03:34 ruling 2). | observation delivered; gap noted, accepted |

**G2 cover confirmed.** d1 as above. d2 per file as above. `ast.dump` digests, recomputed by me with the seat's `astdump.py` on the blobs: `backend/tests/test_transformations.py` before (5d8c2649^) = after (5d8c2649) = `8b753a2242991fbf1e14ec472c8310f4826bdcc39d4a4c6cfe11d896c578e35a`; `examples/fremtpl2/test_seed.py` before (e9d5d6fe^) = after (e9d5d6fe) = `65ec15eceb97ded8c97b3f784c47a0883cae8b81d14473e171b91970e0bb7587`; both equal the LG. Format-only commits are therefore AST-neutral, so the 15 passed / 3 skipped run-small at 5d8c2649 and the greens at e7244a2a carry to the head. ruff rc 0 as d7.

**The 13 docs-audit failures (seat set md5 `728191af8eff0c79bdce0354cbf85e14`, reproduced from the three logs with the brief's predicate).** I read each test's assert at the branch: 11 assert `audit-docs.py` (directly or via `_run()`) exits 0 / prints "All checks passed" — `test_a_finding_resolved_only_by_a_closure_record_is_not_flagged`, `test_the_real_tree_passes_all_ten_checks`, both `process_core_digest` tests (rc 0 + "check 27 … matches"), `test_audit_docs_end_to_end_exit_0_then_1_then_0_on_an_injected_residue` (baseline rc 0), the three `test_register_lint` ones, `test_check_29_wiring_is_undisturbed`, and the two `test_repository_invariants` ones — and the standalone audit-docs run at the same head (docs-audit-docs.log) is rc 1 on exactly four items: check 32 on LG-1967 (×2) and SL-1966 (not in INDEX, unminted) and check 39 (INDEX stale). `test_doc_index_check_exits_0_on_the_real_tree` asserts `doc-index.py --check` rc 0, which is the stale INDEX (docs-doc-index.log rc=1). `test_every_check_30_to_39_reports_how_many_documents_it_examined` runs `check_ids_30_39()` in-process and needs a digit-bearing `check N:` note for each of 30–39; check 39 adds its counted note only on the byte-stable path (audit-docs.py:3586; the stale path fails instead), so it is the one I attribute by reading the code rather than by a captured assert line. All 13 are therefore explained by the unminted ids (check 32) or the stale INDEX (check 39 / doc-index). I could not compare to the reference `3de106a9…` set (not in the scratch tree); the 13 are the set the LG itself calls the 1(f) set. **The post-mint run reading 0 is the proof**, not this attribution.

**Window record.** Lead-granted, START 18:53:21 / END 19:02:46 GMT, load1 1.09, available 19 GB; slots free (gate-2 held ~15 s at 18:53:25, then free); `scratch_s1d_foreign` from template `gipricing` after the template non-empty list read exactly `alembic_version=1 environments=3 tenant_marker=1`; no seat URL named `gipricing`; redis db 11. Recorded foreign-tenant line (to-lead "2026-10-29 18:57:05 GMT"): a createdb/dropdb of `scratch_beatgate_guard` by another seat's gate-script proof occurred inside the window between 18:54 and 18:56; no `scratch_s1d_*` database was touched; the END datname list is compared with START excluding it (dropped before END). Plan said the window was single-tenant; that was breached by the lead's other seat, not by this slice; the process-backlog row "A DB window is single-tenant on the shared server" (ace4577e) records it. The window's tail ran ~9 min, inside the ≤ 60 min limit.

**Findings (all small; none moves the verdict).**
1. Log hygiene (seat brief item 37): c1.log and green.log have no numeric last-line `rc=` (green ends `rc=done`; c1 has none); `o1.log` and `red.log` carry `head=` of the base, correctly. Process-backlog class, not an FD.
2. d3's "foreign count rising" (0 → 3) and d8's END read-backs exist only as LG prose; no log. The reds' causes are read from red.log directly.
3. The reds/greens ran in a throwaway (`scratch/s1d/tw`) that no longer exists; they are not reproducible, only readable. Acceptable under the plan (S1d-1), noted.
4. G1's "before=3" is the residue of the reds in the same foreign DB, so G1 proves "no new write by the fixed fixture", which is what d4 asks; it does not show a clean-start zero.
5. The plan's quoted reference md5 `3de106a9…` has no stated predicate (the LG says so); the post-mint 0 supersedes it.

**Proposed overall verdict:** S1d delivers FD-1965 (both limbs) with evidence; d9 and d10 are owed to the mint/PR (reassigned to the lead / mint seat), nothing delivered-but-untested; the audit is clean on the code, with the conditions above for the docs half. Audit is by `origin/main...origin/draft/sl-8278`, head `2cf61612`; no tests, DB or git writes were run.

Verdicts (lead 29, 2026-10-29): d1–d8 delivered (d7's repo-wide ruff check . re-run at the mint head, quoted below; d8 by the window record, accepted by the maintainer 2026-10-29 19:03:34 GMT); d9 delivered by this mint's post-mint checks (quoted below); d10 open until the merge; O1 delivered with the stderr gap accepted 2026-10-29 19:03:34 GMT; the 13 docs-audit failures pre-mint explained by the unminted ids and the stale INDEX, 0 failed post-mint.
