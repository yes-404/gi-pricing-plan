---
id: LG-9932
family: ledger
title: WK-1178 slice SL-1455 — NFR-489, the /score request path meets its p99 budget at 25 to 200 rps (PL-1454 slice ledger)
status: active
created: 2026-10-11
owner: executor
tree: 5e00fa74f380b201c9f2a8d555822f91eacf2d0e
phase: P2
work: WK-1178
slice: SL-1455
plans: [PL-1454]
corrected_by: []
relates: [PL-1454, FD-1411, SL-1259, RL-1263, RL-921, RL-1379, RL-1685, "RL 8024 (working id)", NFR-489]
---

# LG-9932 — WK-1178 slice SL-1455: the NFR-489 remedy for `/score`

*(LG-9932 is a working id reserved by the lead; the lead mints it at the merge turn.)* Executed by
`executor-sl1455` from PL-1454, base `origin/main` `d699a561d6a93f33b74beb9c07023f8e655bb8c7`. Times are
BST (`TZ=Europe/London date`) unless marked. **This ledger covers Tasks 0–3** (the GO was "Task 0 only"; Tasks 1–3 followed once
RL-1685 ruled DP-1…DP-4 from Task 0's record); Tasks 4–6 are open.

**GO:** `to-lead.md` "2026-10-10 21:38:39 BST — DISPATCH GO: SL-1455 (Task 0; FD-1411's NFR-489 HTTP remedy) and WK-674 S3 (PL-1583); OP-1455-M1/M2/M3; the register :293 record", item 1: "GO SL-1455, Task 0 only (attribution, no fix). Tasks 1–6 wait on DP-1…DP-4, ruled from Task 0's record (need 5). Need 4: Task 0 re-derives bench-rating.py's cites and the model_call scoring path at its base, quoted in the record." Item 5: "MEASUREMENT WINDOW (need 3): the lead owns it. The sweep runs ALONE: both slots, no gate, no SL-1526 proving run, no migrate --verify. Task 0's own timing runs need the same. Book it in eta, with its start and end stamps in the LG." Corrected for Task 4 only by "2026-10-11 11:02:35 BST — DP-S5-a RULED (a) …" item 2 (SL-1455's Task 4 is the FD-1411 remedy proof; the NFR-489 exit verdict is SL-1259's). The timings are DIAGNOSTIC on this box: "2026-10-11 10:57:16 BST" item 3.
**MERGE-ACK:** not yet given.

## Tasks

### Scope

`PL-1454` (leaf plan, WK-1178), roadmap row `SL-1455` — "WK-1178 fix slice — NFR-489: the /score request path meets its p99 budget at 25 to 200 rps". Requirements: `03` NFR-489, `00` NFR-454 (held by the same measurement); preserved, not built: NFR-497, FR-243, FR-259; FR-268 not built. This ledger's part: PL-1454 Task 0 (attribution, no committed code) and Acceptance 1.

### Task list

- [x] Task 0, Step 0 — need 4 re-derived at the base (Build log).
- [x] Task 0, Steps 1–5 — AUTHORED as scratch scripts under `~/gi-pricing-plan.local/scratch/sl1455-t0/` (not in the repository; Task 0 commits "nothing but its ledger"). **Not run.**
- [x] Task 0, Steps 1, 3, 3b, 4 — the timings: RUN in the ALONE window 2026-10-11 23:41:11 – 2026-10-12 00:14:49 BST (Build log, last entry).
- [x] Task 0, rerun with asyncio debug off — RUN 2026-10-12 02:16:09 – 02:20:29 BST (Build log, last entry); both arms CLEAN by the pre-registered rule.
- [ ] Task 0, Step 5 — the tabulation: `results.md` is generated (path in the last Build log entry); the one-line (i)–(iii) statements and any rerun are the lead's ruling (asyncio debug mode swamps the run).
- [ ] Task 0, Step 6 — STOP; hand to the lead for DP-1…DP-4.
- [x] Task 1 — Steps 1–3 committed (`c9a64068`, `1ab36c9f`); Step 4's `--help` recorded; its `--rates 25` run is owed to Task 4's window (Build log, 2026-10-14 audit-fix entry).
- [x] Task 2 — the timing-free guard, red first (`d943c2d0`, `fecaf7b6`).
- [x] Task 3 — Steps 1–4 delivered (`0544220a`); Step 5's byte-identity is owed to Task 4's window (Build log).
- Tasks 4–6 — not started.

### Gate

Not applicable to Tasks 0–3 beyond the per-task runs in the Build log. The two-half gate is Task 5's.

### Audit

**Slice audit of Tasks 1–3 (SL-1455, WK-1178, NFR-489)** by `auditor-sl1455`, 2026-10-14 (Europe/London, read
between about 11:10 and 12:00 BST). Range: `origin/main...origin/sl-1455-wk1178-nfr489-http`, `origin/main`
`4420f91f`, branch tip `11677daa`. Method: **reading only** (gate-1 is held; no test, no `audit-docs`, no
run). Every "red on base" and "green" below is therefore the executor's recorded run in the Build log,
**not re-run by me**; what I verified is that the asserts that were recorded would fail for the stated cause,
by reading the test and the code. **Every verdict is PROPOSED; the lead decides.** This audit covers Tasks
1–3 only; Tasks 4–6 (the sweep, gate, DP-6) are not audited here, so **I do not set the `LG-` or the `SL-`
row `closed`**: the slice is not done.

**Overall: no HIGH finding. Two MEDIUM (F1, F2: both are connection-holding consequences of the shared
session, neither covered by a test), three LOW.** The ruled counts (1 checkout, 9 statements, one `UPDATE`
inside 60 s) are delivered.

#### 1. Scope from the spec, then evidence

Scope derived from `PL-1454` Tasks 1–3 (`docs/plans/PL-01454-…` at `origin/main`, Task 1 Steps 1–4, Task 2
Steps 1–3, Task 3 Steps 1–5) and `RL-1685` "Ruled" 1 (a)(b), 3, 4 and "What it obliges" (Task 1, 2, 3 bullets).

| Item | Evidence (file:line at `11677daa`, test and its asserts READ) | Proposed verdict |
|---|---|---|
| T1 S1: fetch label says "miss" | `scripts/bench-rating.py` `_report(f"_fetch_bundle alone, {label}, cold (slot miss …)")`; docstring of `_measure_fetch` rewritten | **Delivered but untested** (no run; ruff and `py_compile` only, from-lead 10:32:47) |
| T1 S2: warm figure (shared slot) | `_measure_fetch(…, warm=True)`, `_slot()` returns the one `shared` slot; second `_report(… warm (slot hit …))` | **Delivered but untested** |
| T1 S2b: default-live arm | `_seed` adds a `DeploymentRow` to `uat`; `live_body` pops `rating_version_ref`; its own rung per arm | **Delivered but untested**; Acceptance 2 and 9 need Task 4's run |
| T1 S3: `--workers N`, N in every header | `_serve(…, workers)` passes `--workers` only above 1; `main` prints `replica: N = …`; `backend/tests/test_bench_rating_header.py`: three tests, asserts `re.search(r"\bN = 4\b")`, `N = 1`, and `--workers` value in the `Popen` argv | **Delivered and tested** (the header is read from `main()` up to `_ctx`, not a mock of the print) |
| T1 S4: `--help` shows the flag; one `--rates 25` run prints both fetch lines | no entry in the Build log | **Not evidenced**: owed (see F3) |
| T2: `MAX_CHECKOUTS = 1`, `MAX_STATEMENTS = 9` at rate 0 | `backend/tests/test_score_request_cost.py` `one_warm_request` fixture (rate pinned to 0, warm-up request, `checkout` and `before_cursor_execute` listeners attached after the warm-up) and the two tests asserting `<= 1`, `<= 9` | **Delivered and tested** |
| T2 / DP-1 (b): two `last_used_at` tests | same file: `…_not_written_on_every_request` (stamp 30 s old, `== 0` `UPDATE api_keys` by statement text), `…_written_once_the_interval_has_passed` (120 s old, `== 1` and the stamp advances by more than 60 s, read back through a new session, so it proves the commit) | **Delivered and tested** |
| RL-1685 binding condition: sampling-rate read degrades | same file, `test_a_failed_sampling_rate_read_degrades_to_not_sampled`, two parametrisations ("raises", "aborts the transaction" by `SELECT 1/0` on the shared session); asserts the injected read was reached (`seen["hit"] == 1`), `200`, `outcome == "quoted"`, no trace row. `test_score.py` is not in the diff, so `test_a_trace_sampling_failure_does_not_turn_the_response_into_a_500` is unchanged | **Delivered and tested** (guard, labelled) |
| RL-1685 "add no cache test" | none added; `bundle_slot.py` untouched | Conforms |
| T3 S1 / DP-1 (a): one request-scoped session | `deps.py` `request_session` and `RequestSessionDep`; used by `require_caller`, `requires`, `_enforce_score_rate_limit`, `score`; `db/session.py` `reading()` | **Delivered and tested** for `/score`; **gaps for the other routes: F1** |
| T3 S2 / DP-1 (b): 60 s | `auth/service.py` `LAST_USED_WRITE_INTERVAL = timedelta(seconds=60)`; write only if `None` or `now - last_used_at >= 60 s` | **Delivered and tested** (the exact 60 s boundary is not tested; not required) |
| T3 S3 / DP-4: `gc.freeze()` | `main.py`, last statement before `yield`; pool arguments unchanged (`config.py` and `Database.__init__` pool arguments are not in the diff) | **Delivered and tested** (below) |
| T3 S4: regression files pass | Build log: `test_score.py` 52, `test_traces.py` 39, `test_score_rate_limit.py` 9+1 skipped, `test_auth_keys.py` 20, `test_score_compare.py` 20, `test_api_authorisation_sweep.py` 9, bench 4 | Recorded, **not re-run by me** |
| T3 S5: byte-identity of the `/score` body, `main` vs head | no entry | **Not evidenced**: owed (F3) |
| RL-1685 obliges: write set widening recorded in the LG | Build log last bullet lists seven source files | Delivered (the two new tests and the bench are not in that list: F3) |
| RL-1685 obliges: LG 9932's minted id into RL-1685 `relates` | owed at the mint (minter); LG 9932's own `relates` does not carry RL-1685 or RL 8024 | **Reassigned to the minter**, with F3's LG-side fix |

**Four-verdict note for the lead:** T1 S1/S2/S2b and T1 S4, T3 S5 are *delivered but untested* or *not
evidenced*; they are Task 4's run and a ledger entry, not missing code.

#### 2. Reds by cause, and guards labelled as guards

The Build log's "Phase 1 reds" bullet (this ledger, the entry headed "2026-10-14 — Phase 1 reds, then Task 3")
records, on the red tree `78177ec8` plus the test files: `assert 6 <= 1` (`{'checkouts': 6, 'statements': 10}`),
`assert 10 <= 9`, `assert 1 == 0` (one `UPDATE api_keys` inside 30 s). Each is a failure of the stated bound, so
the cause is the right one (the plan's Task 2 Step 2 expected checkouts 5 and statements at least 7; Task 0
re-measured 6 and 10, and RL-1685 fixed the bounds on that record). Stepwise: after the 60 s interval alone the
cost file is `1 failed, 5 passed` (statements 9, checkouts still 6), after the session `6 passed`: the two
changes are attributed separately. **Guards, green before and after, and labelled so** in the test
docstrings and the ledger: `…_written_once_the_interval_has_passed`, and the two parametrisations of the
degrade test. A guard that has never been red is not a regression proof of the fix, and the ledger does not
claim it is. I could not run them; the asserts are read and would fail as recorded.

**The gc test has BOTH asserts, each recorded red on the base** (`backend/tests/test_startup_gc_freeze.py`):
(1) CALL: `monkeypatch.setattr(gc, "freeze", _spy)` where `_spy` records `hasattr(app.state, "rate_limiter")`
and then calls the **real** `gc.freeze`; asserts `seen == [True]` (exactly one call, after the last start-up
step). Recorded red on base: `assert [] == [True]`. (2) EFFECT: no spy; `before = gc.get_freeze_count()` after
`create_app`, `at_yield` read inside `with TestClient(app)`; asserts `at_yield > before`. Recorded red on base:
`assert 0 > 0` (0 before, 0 at yield). Both are the two asserts the maintainer's (by delegation) entry
"2026-10-14 10:54:56 BST" rules; the spy wraps the real freeze, as ruled. The autouse `gc.unfreeze()` hands the
permanent generation back. Remaining caveat: **F4**.

Note on source: RL-1685's own form (count non-zero once started) is correctly **not** used; it is vacuous
and the correcting RL 8024 (working id, `origin/docs-d16-2026-10-14` `75f9b1ae`) is not yet at `origin/main`.
Until it merges, `docs/rulings/RL-01685-…` still says the vacuous form, and this slice's test follows the
maintainer's entry, not the merged ruling text. The lead should keep the merge order RL 8024 before or with this slice.

#### 3. The design risks, checked in the code

**(a) `require_caller` commits only `if session.dirty`: is any write lost? No.** `authenticate_api_key` now sets
`key.last_used_at` and does not flush (`auth/service.py`); `require_caller` commits when the session is dirty
(`deps.py`, API-key branch), so the stamp is persisted **before** any handler or unit-of-work reads, and the
`…_written_once_…` test reads it back from a new session. Unit-of-work callers open their own sessions
(`database.unit_of_work()`) and do not depend on the stamp's session. The stamp is the only write on this path.
Failure branches: every `_audit_auth_failure` row is added to the request session and the call then raises;
the session is closed, so the row is rolled back. **That is the same net outcome as the base**, where the raise
inside `async with database.unit_of_work()` rolled the same row back (the base lines are visible in the range
diff). It is **pre-existing, not introduced here** (the lead's candidate in from-lead "2026-10-14 11:08:09
BST" is right on this; I confirm it by reading both sides, not by a run): it stays with the maintainer.
`autoflush=False` (`db/session.py`) means no stray flush on the dirty check.

**(b) `requires()` closes by default, `keep_session=True` only on `/score`: is another route holding a
connection or using a closed session? Yes for holding: F1 (MEDIUM).** Using a closed session is not a defect:
`AsyncSession.close()` leaves it reusable and the next statement opens a new transaction. But
`require_caller` itself does **not** release when it did not commit. For an API-key caller the first
`SELECT` autobegins a transaction and holds a pool connection until the request ends. Routes that depend on
`require_caller` **directly**, not through `requires()`: `api/me.py:42`, `api/deployments.py:38`,
`api/approvals.py:66`, `api/demo.py:53`, `api/validation.py:68`. For those, the connection stays checked out
for the whole request **and** the handler then opens its own `database.session()` or `unit_of_work()`
(for example `me.py:110-111`, `approvals.py:80`, `validation.py:142`): two checkouts per request where the
base held one at a time, and the base released the first at once. At pool defaults this is a nested
checkout (see F2). No test covers it.

**(c) `_maybe_sample_trace` with `read_session`: sampling semantics unchanged? Yes; one new coupling: F2.**
Order is unchanged: resolve the rate, `decide_sampling(result.outcome, rate.effective_value,
roll=random.random())` (decline and error at 100 %, `roll < rate` for quoted, floor unchanged), return if not
sampled, then the `caller.environment is None` guard, then the write. Previously the guard ran inside the
`unit_of_work`; now it runs before the write session is opened, so the raise happens one step earlier and is
still caught by the same `try`, which logs and returns (the quote is still served). The rate is a read through
`reading(read_session or database)`; a caller with no request session (`read_session=None`) gets a fresh
`Database.session()`: the only `_maybe_sample_trace` caller in `backend/src` is `score()`, which passes it.
The write keeps its own `unit_of_work`, so FR-259's isolation holds (the degrade test's "aborts the
transaction" parametrisation shows the poisoned shared session does not change the status or the outcome).

**(d) `rate_limit.enforce` takes a session: all callers updated? Yes.** `grep -rn 'rate_limit.enforce'
backend/src packages scripts` finds one call: `_enforce_score_rate_limit` (`score.py:149`), now passing
`session`; `enforce` no longer imports `Database`. `test_score_rate_limit.py` (9 passed, 1 skipped, recorded)
exercises it through the app.

**(e) Cached once per request, released on every exit path? Cached: yes. Released: yes by construction, with
F1's holding window.** `request_session` is one callable used by `require_caller`, the `requires()` closure,
`_enforce_score_rate_limit` and `score`, so FastAPI's per-request cache resolves it once. It is
`async with database.session() as session: yield session`, so the session is closed when the dependency
exits, including after an exception thrown in (the context manager's exit runs). No streaming route uses it.
I did not verify FastAPI 0.142.2's exit point (before or after the response is sent); no venv is present in
this worktree and I ran nothing. On `/score` the connection is held until that exit, which is the ruled design.
The bearer and dev paths never touch the injected session (they take their own), so they cost no checkout.

#### 4. Write set against `PL-1454` §"Write set"

`git diff --stat origin/main...origin/sl-1455-wk1178-nfr489-http` lists 15 paths.
| Path | Admitted by |
|---|---|
| `api/authz.py`, `api/deps.py`, `auth/service.py`, `api/score.py`, `db/session.py`, `main.py`, `scripts/bench-rating.py`, `tests/test_score_request_cost.py` | the plan's write-set table |
| `platform/rate_limit.py` | **not in the plan's table;** RL-1685 "What it obliges", the last bullet (option (i): "if the Setting read moves, `rate_limit.py` (`enforce`)") |
| `tests/test_bench_rating_header.py` | not in the table; RL-1685 "What it obliges", Task 1 bullet ("a test asserts the header carries the N") |
| `tests/test_startup_gc_freeze.py` | not in the table; RL-1685 Task 3 bullet (the red-first freeze test); its **form** is the maintainer's 10:54:56 ruling |
| the LG, `docs/INDEX.md` | the table (ledger and generated registry) |
| the leaf plan (`status: draft → active`), `docs/roadmap.md` (row status) | activation by the dispatch GO, `to-lead.md` "2026-10-10 21:38:39 BST"; not Tasks 1–3 |

In the table and **not touched**, correctly: `config.py` (DP-1 (d) is not admitted), `bundle_slot.py`,
`test_score.py` (both read-only), `scripts/demo.py` and `test_demo_command.py` (DP-6 is (b)). No path outside
the plan plus RL-1685's three admissions. **Acceptance 8 is met.** The ledger's own write-set line lists seven
source files and omits the three tests and the bench (F3).

#### 5. Barred word

`git diff origin/main...origin/sl-1455-wk1178-nfr489-http -U0 | grep '^+' | grep -niE 'dep''uty'` prints
nothing, and `git log origin/main..origin/sl-1455-wk1178-nfr489-http --format=%B | grep -ciE 'dep''uty'` prints 0.
Clean over the range (added lines and every commit message).

#### 6. Closing acts

- **Reachability** (`git merge-base --is-ancestor <sha> origin/sl-1455-wk1178-nfr489-http`): `0544220a`,
  `fecaf7b6`, `d943c2d0`, `1ab36c9f`, `c9a64068`, `051f9b3d`, `9777184f`, `3c0e99a0`, `78177ec8` all exit 0.
  The ledger's red tree `78177ec8` and green tree `0544220a` are both reachable; the final test file is at the tip `11677daa`.
- **`LG-` and `SL-` rows:** left `active`. Tasks 4–6 are open, and the Task list still says "Tasks 1–6 — not
  started" (F3).
- **Minted-id relation:** RL-1685's front matter says "and LG working id 9932, added at its mint", and its
  "What it obliges" says the LG's minter adds it. That edit (`relates:` on `docs/rulings/RL-01685-…`) is owed at the mint of
  LG 9932; it is a front-matter-only change to a frozen record (the same form as the correcting RL's own
  `corrected_by`). Today `relates` lists neither the LG nor RL 8024 on either side.

#### Findings

- **F1 — MEDIUM.** `require_caller` leaves the request session's connection held for the whole request when
  an API-key caller reaches a route that does not use `requires()`.
  *File:line:* `backend/src/app/api/deps.py` (API-key branch of `require_caller`, `if session.dirty:` with no
  `else`), with the five direct users above (`me.py:42`, `deployments.py:38`, `approvals.py:66`,
  `demo.py:53`, `validation.py:68`).
  *Failure:* an API-key request to, for example, `GET /me` takes a checkout at the auth `SELECT`, does not
  commit (not dirty) and does not close, then `get_me` opens a second `database.session()`. Two connections
  per request instead of one at a time; at pool defaults (5 + 10, no pool arguments anywhere in
  `backend/src`) 15 concurrent such requests each hold one and wait for the second until `pool_timeout`.
  Not a correctness loss; a pool-exhaustion regression against the base, which released at once.
  No test in the range fails on it (the cost test counts `/score` only).
  *Proposed fix:* a `require_caller` variant used by those five modules that closes the session after
  authentication (`await session.close()`), leaving `CallerDep` (the base of `requires()`) as is; or have
  `require_caller` close in the not-dirty branch and let `/score`'s `requires(keep_session=True)` accept the
  re-checkout only if the cost test still shows 1 (it would not: keep a variant). Add one count test: an
  API-key `GET /me` has at most one connection checked out while its handler runs.
- **F2 — MEDIUM (latent).** A sampled `/score` outcome takes a second pool connection while the first is
  still held.
  *File:line:* `backend/src/app/api/score.py` `_maybe_sample_trace`, the `async with database.unit_of_work()`
  after the early `return`, with `read_session=session` still open (the request session is closed only at
  dependency exit).
  *Failure:* declines and errors are sampled at 100 % regardless of the rate, quoted outcomes at 1 % by
  default (`platform/settings.py`, `rating.trace_sample_rate` default 0.01). A burst of 15 concurrent sampled
  requests, one process, default pool: all hold the first connection and wait for the second; the write
  degrades to "logged" after `pool_timeout`, and the quote that was already priced is delayed by that time
  first. The base opened the read and the write in one `unit_of_work`, one connection.
  *Proposed fix:* when the outcome is sampled and before the write, `await read_session.close()` (the
  handler does not use the session after this call), which keeps the unsampled hot path at one checkout and
  the write at one at a time; add a test that a sampled outcome never has two connections checked out together.
- **F3 — LOW (ledger).** `LG-9932` is stale against its own build. (i) The header and the Task list say "This
  ledger covers Task 0 only" and "Tasks 1–6 — not started"; the Gate section says "Not applicable to Task 0".
  (ii) No Build log entry for **Task 1** (commits `c9a64068`, `1ab36c9f`): no recorded red of the header
  test on the base `_serve`/`main` (the commit order `d943c2d0` then `1ab36c9f` suggests it was red, but the
  failure line is not recorded), no `--help` or `--rates 25` run (Step 4). (iii) No **Task 3 Step 5**
  byte-identity entry. (iv) `relates:` lacks RL-1685 and RL 8024. (v) The write-set line omits the three
  tests and the bench. (vi) The `tree:` header is the Task 0 base, `d699a561`.
  *Fix:* an executor edit to the ledger before the ACK; (ii) and (iii) may be recorded as "owed to Task 4's
  window" rather than back-filled.
- **F4 — LOW (test hygiene).** `gc.freeze()` runs in the lifespan of **every** `TestClient(app)` in the suite,
  and only `test_startup_gc_freeze.py` unfreezes. Each start-up freezes whatever is tracked at that moment
  (including uncollected cyclic garbage) for the life of the pytest process, so memory is not reclaimed
  between tests. In addition the test module docstring states as fact that "`create_app(...)` alone leaves 375
  objects in the permanent generation"; the Build log itself records that the second `create_app` of a
  process showed 0, so the sentence overstates (the effect test is a delta and is unaffected).
  *Fix:* an autouse `gc.unfreeze()` in `backend/tests/conftest.py` (or the app fixture) and a docstring that
  says "in the first `create_app` of a process". Optional; no behaviour in the product depends on it.
- **F5 — INFORMATION (pre-existing, not this slice).** Failed-authentication audit rows are rolled back with
  the raised error on the base and on the head (see 3 (a)). Already with the maintainer (from-lead 11:08:09
  BST); this slice neither fixes nor worsens it. If the maintainer rules it a defect it needs its own FD, and
  the fix must commit the audit row before raising, on a session that the request session's close does not roll back.

**Proposed verdict on the slice's Tasks 1–3:** the ruled counts and the 60 s stamp are delivered and tested;
the gc test has both ruled asserts. Hold the ACK for **F1 and F2** (each is a small change and each needs one
test); F3 is the executor's ledger edit; F4 is optional. After F1 and F2 land, re-audit the specific
checks (cost file plus the two new tests) against the new tip, then the Task 4 sweep.

### Build log

- **2026-10-11 11:2x — base and set-up.** Worktree `.claude/worktrees/sl-1455`, branch `sl-1455-wk1178-nfr489-http`, base `origin/main` `d699a561d6a93f33b74beb9c07023f8e655bb8c7` (`git -C <wt> rev-parse HEAD` at creation); `uv sync --all-packages` ok. No ref matched the slice before (the planner's draft, `go-request-sl1455-2026-10-10.md` §1).
- **Task 0 Step 0 — need 4 re-derived at `d699a561`** (`git -C <wt> diff --name-only 47d770e8 origin/main -- backend/src/app/api/score.py backend/src/app/api/deps.py backend/src/app/api/authz.py backend/src/app/auth/service.py backend/src/app/db/session.py backend/src/app/main.py backend/src/app/platform/bundle_slot.py scripts/bench-rating.py` prints `backend/src/app/main.py` and `scripts/bench-rating.py`).
  - `main.py`: the diff is two added lines, the `dislocation_runs` import and `app.include_router(dislocation_runs.router, prefix=API_PREFIX)`; the lifespan and the slot construction are untouched. `score.py`, `deps.py`, `authz.py`, `auth/service.py`, `db/session.py` and `bundle_slot.py` are byte-identical to `47d770e8`.
  - `scripts/bench-rating.py` cites, PL-1454's line → the line at `d699a561` (each read at the line): `_ctx` `:1084` → `:473`; `QuoteContextOptions(rating_version_ref=_RATING_VERSION_REF)` `:347` → `:484` (the constant `:82`); the "every request pays this" label `:1075` → `:1253`; `_measure_fetch` (with its fresh `BundleSlot()` per call) `:709-722` → `:812-865` (`BundleSlot()` at `:851` and `:858`; its comment "a shared one would turn every call after the first into a hit" `:847`); the docstring claiming every request pays the miss `:678-688` → `:815-824`; `_serve` `:729-758` → `:866-896`; `Rung.implied_ceiling_rps` `:564-575` → `:701`; `_drive` `:776` → `:913` (`httpx.Limits(max_connections=1024…)` `:935`, `timeout=60.0` `:936`); the API key scoped to `uat` `:645-653` → `generate_key("uat")` `:784`, `environments=["uat"]` `:790`; `_seed` `:715`; the HTTP sweep `_run_http_sweep` `:1216`. The `--http` flow, the discarded 4 s warm-up rung at 25 rps, one server per GBM condition and the per-rung `_handler_ms` read are as the plan describes.
  - `score.py` handler cites (unchanged): `score` `:351`, `_serving_ref` `:169`, `_fetch_bundle` `:207`, `_maybe_sample_trace` `:464`, sampling resolve `:485`; `require_caller` `deps.py:201` with `unit_of_work` + `authenticate_api_key` at `:238-239`; `requires` `authz.py:54`; `Database.__init__` `db/session.py:40` (`pool_pre_ping=True`, no pool arguments).
  - **The `model_call` scoring path at the base** (the GO's second clause; A-2/A-3 changed it since FD-1411's tree): `score_one` `packages/pricing-core/src/pricing_core/rating/score.py:919` evaluates through `bundle.decision.async_evaluate(context, {"trace": trace})` (`:961`) with no I/O (NFR-491); each `model_call` step is a `customNode` (`runtime.py:440-454`) whose handler `_model_call_handler` (`runtime.py:712`) calls the one per-kind dispatch `_predict_model` (`runtime.py:594`): xgboost/lightgbm go to `predict_gbm(…, nthread=1)` (`:626`), a GLM to `glm_scorers[ref].predict(feature_row)` (`:628-629`), anything else is a `_ModelCallRefusal` (`:630`); a Peril Structure's components use the same dispatch (`:605-606`). `runtime.py` and `score.py` both changed since `47d770e8` (A-2, A-3), so Task 0's table re-baselines `score_one`'s share rather than reusing FD-1411's 11.3 / 7.8 ms.
- **Surprise found while authoring Step 3b (reported to the lead; no code touched).** `score()` (`backend/src/app/api/score.py:351-375`) passes the request's `ctx` to `score_one` unchanged after `_serving_ref` has resolved the live ref, and `score_one` refuses a `ctx` whose `options.rating_version_ref` is `None` with `INPUT_CONTRACT_VIOLATION` (`score.py:945-950` in pricing-core: "ctx.options.rating_version_ref is required — Slice 1 builds no default-live resolution"). The default-live tests (`backend/tests/test_score.py:1379` ff.) replace `score_one` with a stub that records the ref, so they do not exercise this. Read, not run: the default-live arm of Step 3b may answer 4xx on `main`. The driver therefore sends ONE untimed probe request per live arm against `main`'s handler unchanged (`T0_FILL_REF=0`) and records the answer, and the timed live passes run with the instrument injecting the resolved ref before `score_one` (`T0_FILL_REF=1`) — the path a corrected handler would run — each request recording `ref_filled`.
- **Task 0 Steps 1–5 authored — deviations from the plan's text, none changing what is attributed:**
  1. **Instruments are out-of-tree.** Step 2 describes a scratch patch to `score.py`, `deps.py`, `authz.py` and `session.py`. `t0_app.py` wraps the same functions at import time of the server process (`PYTHONPATH=<scratch> python -m uvicorn t0_app:create_app --factory`), so the repository is not edited and no second worktree is needed: this slice's worktree has the base's `backend/`, `packages/` and `scripts/` trees, which `run.sh` checks (HEAD guard: `git rev-parse HEAD:backend` = `b1619a4fb23b3a629c1b8cc8bb93e72039fb9a93`, `:packages` = `992973090a2b48e8a76eeda47934358349152ed6`, `:scripts` = `6a3e9185d3396863d6ee50186eb9df6e72481df3`, and those paths clean).
  2. **Phases timed:** `auth` (`authenticate_api_key`), `auth_scope` (the whole `unit_of_work`, commit included), `rbac` (`require_permission`), `rbac_scope`, `serving_ref`, `fetch_bundle`, `compiled_for`, `score_one`, `sample_trace`, `serialise` (`ScoringResult.model_dump_json`), `total`. Pool: `_ConnectionFairy._checkout` (includes `pool_pre_ping`) count, summed and longest milliseconds; statements and commits by SQLAlchemy engine events; slot hit/miss by wrapping `BundleSlot.get`; `gc.callbacks`; a 10 ms event-loop ticker recording overshoots of 50 ms or more; `PYTHONASYNCIODEBUG=1` with `slow_callback_duration = 0.05` (those lines land in the per-pass `server.log`).
  3. **py-spy's output is `--format raw`** (collapsed stacks; the analyser computes top frames by self time) rather than an SVG; Step 4's only exit stays as written: if `uvx py-spy --version` fails the script prints the error and skips the profile passes.
  4. **Passes:** four arms (`bench-gbm`, `bench-nogbm`, `live-gbm`, `live-nogbm` — Step 3b's default-live arm in both GBM conditions, seeded with a `uat` `DeploymentRow` in the scratch database only) × {25, 50} rps × 3 runs, each on a fresh server (cold slot) after the bench's discarded warm-up rung, plus one py-spy pass per arm at 25 rps: 24 + 4 passes, about 25–30 minutes.
- **The ALONE run, for the lead to book** (nothing on the box but the lead's held `gate-1`, `gate-2`, `small-test`): `bash ~/gi-pricing-plan.local/scratch/sl1455-t0/run.sh` — foreground, internal `timeout 5400`; it checks the head guard, `pgrep` for pytest/vitest (refuses if any, `T0_ALLOW_BUSY=1` for a rehearsal), records `uptime`, slot state and `df` at both ends, creates and drops a uniquely named scratch database (`createdb -T gipricing`, records the template's alembic version `e5b7d9f1a3c6` against the tree head `b8d2f4a6c0e1`, then `alembic upgrade head`), runs `t0_driver.py`, and writes `results.md` with `t0_analyse.py`. Subsets for a rehearsal: `T0_ARMS=… T0_RATES=… T0_RUNS=…`.
- **Not run yet, by design:** no instrument, driver or analyser has been run end to end. Checked statically: `bash -n`, `py_compile`; `t0_app.create_app()` imports and applies every patch against this tree (no server, no database); `t0_analyse.py` run on a hand-made fake tree. Untested until the window: the server start under the wrappers, the Step 3b seed, py-spy attach, and the pass-to-pass port reuse.
- **Barred word:** `git -C <wt> diff origin/main...HEAD | grep '^+' | grep -ciE 'dep''uty'` → 0 at the commit.
- **The ALONE run, 2026-10-11 23:41:11 – 2026-10-12 00:14:49 BST (diagnostic attribution, not an NFR-489 reading).** The lead's ALONE WINDOW OPEN is from-lead "2026-10-11 23:40:50 BST"; the wrapper was `flock -w 7200 /tmp/slots/gate-1 flock -w 600 /tmp/slots/gate-2 flock -w 600 /tmp/slots/small-test timeout 5700 bash ~/gi-pricing-plan.local/scratch/sl1455-t0/run.sh`, exit 0, `end 2026-10-12T00:14:49+01:00 rc=0`, driver rc 0, analyse rc 0.
  - **Objects.** Slice COMMIT `47cf560426a78f079a3fdf57cb935224dfd5ebcc` (parents slice `b00cde5e` and `origin/main` COMMIT `372fa92ae3ab306bc067c234487ce929dc0e2a04`; the head was pinned, not re-merged, by the lead's ruling). Pre-registered evidence COMMIT `c41475c2cae267bddf1e40dfe3ff654353eb518c` on `evidence/sl-1455-t0-2026-10-11` (parent `d87e354d`); blobs under `evidence/sl-1455-t0/`: `run.sh` `8b434dcb`, `t0_app.py` `cd6f6e69`, `t0_driver.py` `8991de25`, `t0_analyse.py` `37d7fe4f`; `run.sh` step 0 printed `prereg ok` for all four (byte-identical to the blobs) and the preflight printed `PREFLIGHT ok`. Earlier evidence commit `d87e354d` (t0_analyse.py blob `511c1e71`) was superseded before the run.
  - **Where.** Results: `~/gi-pricing-plan.local/scratch/sl1455-t0/out-20261011T234111/results.md`; the log `~/gi-pricing-plan.local/scratch/sl1455-t0/wrapper-2026-10-11.out`; per-pass START/END (Europe/London) and steal in that log and in each pass's `client.json`. Not in the repository.
  - **Passes.** 28: 4 arms x {25, 50} rps x 3 runs, plus one 25 rps py-spy pass per arm. Per-pass `/proc/stat` steal 0.23% – 1.21% (highest: `live-gbm` 50 rps run1 1.20%, `live-gbm` py-spy 1.21%, `live-nogbm` py-spy 0.88%). Load average 3.36 at the start, 2.06 at the end. Probes (main's handler, no ref in the body) on both live arms: HTTP 200 `quoted`.
  - **Co-tenant.** Another seat's `gh run list` CI poller ran during the window (from-lead "2026-10-12 00:00:41 BST": about 118% CPU per poll, stopped by the lead). The minter-d13a stat read, relayed in from-lead "2026-10-12 00:16:12 BST", puts the poller at 23:33:56 – 00:02:35 BST, inside the window (which began 23:41:11), and the worktree removals at 23:33:03 – 23:33:54 BST, before it. It is in-guest CPU, so steal does not show it. Note: `out-20261011T234111/CO-TENANT-NOTE.md`. `bench-gbm` 25 rps run1 (23:41:29 – 23:42:48, the first pass) is the one pass that stands apart from its siblings (26 errors, client p99 48.7 s against 32.0 s and 30.1 s for runs 2 and 3) and may be disturbed; no other pass is separable.
  - **What the run shows (server-side request ms, p50 / p99, pooled):** total `bench-gbm` 25 rps 20338 / 46779, 50 rps 42251 / 59056; `bench-nogbm` 12477 / 24755, 38307 / 54517; `live-gbm` 17306 / 32532, 43393 / 61236; `live-nogbm` 16429 / 29036, 42110 / 58873. `score_one` p50 / p99 23–35 / 38–70 ms (max 839). Every request: 6 pool checkouts, 10 statements, 2 commits (p50); checkout wait p99 24–60 s, longest single 21–30 s. `rate_limit` (new, #1280) p50 1.5–3.3 s at 25 rps and 8.9–10.9 s at 50 rps, the largest p50 of the phases in every cell, and one of the 6 checkouts. Slot hits = all requests, misses 0 in the measured window. GC gen2 longest 420–937 ms; loop stalls of 50 ms or more: 16–71 per cell, longest 430–960 ms. Errors at 50 rps: 135–314 of about 1000 per pass.
  - **py-spy (3 of 4 passes usable; the `live-gbm` pass returned n=0, errors=500):** top self-time frames are `linecache.checkcache` 14.6–18%, `traceback` frame extraction (`traceback.__init__`, `walk_stack`, `_extract_from_extended_frame_gen`) about 15–20% together, `asyncio/runners.run`; `asyncpg execute` about 1%.
  - **Recorded AS-IS (from-lead "2026-10-12 00:16:12 BST"; maintainer ruling to-lead "2026-10-12 00:16:39 BST").** This run's p50 / p99 are VOID as a stall diagnosis: asyncio debug mode (Step 2 of the plan) records a stack for every Task and Future, and is the dominant cost in the profiles, so the run is a saturated, instrumented process. The stall's cause (Step 5 (ii)) is unattributed and whether one process serves 200 rps (iii) is not answerable from it. **The structural facts stand**, because they count calls and do not depend on timing: 6 pool checkouts, 10 statements and 2 commits per scored request; `score_one` about 25–35 ms; the bundle slot is hit on every request; the result does not depend on the GBM; default-live does the same per-request work as the bench path (probes HTTP 200).
  - **Finding against the plan text, for the process backlog under Lean P2 (not an FD).** PL-1454 Task 0 Step 2 prescribes asyncio debug mode (`PYTHONASYNCIODEBUG=1`, `loop.slow_callback_duration = 0.05`) as the stall probe. At 25 rps on this box it saturates the loop it measures (server p50 12 – 20 s), so the probe voids the very reading it was prescribed to take. A stall probe for a loop-bound service has to be non-perturbing (a loop-lag ticker, sampling `py-spy`) before it is run alone; debug mode belongs in a separate, low-rate pass.
  - **The rerun is approved** (the maintainer, to-lead "2026-10-12 00:16:39 BST"): debug mode off, a true ALONE window with the pollers paused, `py-spy` in sampling mode only. Its pre-registration is the next Build log entry.

- **The debug-off rerun, PRE-REGISTERED (written before the run; the maintainer's approval is to-lead "2026-10-12 00:16:39 BST", conditions 1 to 4).** What the rerun runs, fixed here and in the evidence commit on `evidence/sl-1455-t0-2026-10-11` (that commit's sha is reported to the lead and recorded in the entry that records the rerun, because it cannot be written into a file the commit pins):
  - **The switch:** `T0_ASYNCIO_DEBUG=0`. It stops `loop.set_debug(True)` and `slow_callback_duration` in `t0_app.py` and does not set `PYTHONASYNCIODEBUG` in `t0_driver.py`. Every per-phase timer, the pool listeners, the GC callbacks and the 10 ms loop ticker stay.
  - **The arms:** `bench-nogbm` and `bench-gbm`, 25 rps, 3 repeats each, 20 s measured per repeat after the 4 s warm-up, one fresh server per repeat. `run2.sh` sets these and runs `run.sh`.
  - **`py-spy` in SAMPLING mode only:** one 25 rps pass per arm with `--nonblocking`, so it never pauses the process to read it, and no debug hooks.
  - **The reading rule, in numbers (`reading_rule` in `t0_analyse.py`).** Per repeat, over every request record of the measured window and the client's error count: *longest single pool checkout* `L`, *server `total` p99* `P`, *client errors* `E`. A repeat is **clean** when `L < 30000 ms` AND `P < 1000 ms` AND `E = 0`; it is **saturating** when `L >= 30000 ms` (the pool timeout) OR `E > 0`; any other repeat is neither. An arm is **CLEAN** if all 3 repeats are clean, **SATURATES** if any repeat saturates, and otherwise **MIXED**, which is reported as neither. Read together: both arms CLEAN means debug mode was the stall; either arm SATURATES means the 6-checkout, 10-statement shape saturates the pool at 25 rps without it. The rule was run on this ledger's first run (debug on): `bench-gbm` SATURATES, `bench-nogbm` MIXED; and on a synthetic clean input: both CLEAN.
  - **A TRUE ALONE window:** the lead pauses every poller first; `run.sh` writes `pgrep -af` of `gh`, `pytest`, `vitest`, `uvicorn`, `alembic`, `run-small` and `claude` processes, with the top processes by CPU, at OPEN and at CLOSE into `results.md`.
  - **Not an NFR-489 reading,** and not a stall verdict beyond the rule above.

- **The debug-off rerun, RUN 2026-10-12 02:16:09 – 02:20:29 BST (diagnostic attribution, not an NFR-489 reading).**
  - **Authority and window.** The maintainer's ruling, to-lead "2026-10-12 00:16:39 BST" (conditions 1 to 4); the lead's GO and window, from-lead "2026-10-12 02:15:54 BST" (ALONE WINDOW OPEN) and "2026-10-12 02:21:18 BST" (CLOSED). Wrapper: `flock -w 7200 /tmp/slots/gate-1 flock -w 600 /tmp/slots/gate-2 flock -w 600 /tmp/slots/small-test timeout 5700 bash ~/gi-pricing-plan.local/scratch/sl1455-t0/run2.sh`. Markers: `T0 start 2026-10-12 02:16:09 BST` … `T0 end 2026-10-12 02:20:28 BST`, `end 2026-10-12T02:20:29+01:00 rc=0`; driver rc 0, analyse rc 0; the scratch database was dropped.
  - **Pins.** Slice COMMIT `3c0e99a073887075478117c929753e7d6fec0f1d` (the preflight printed `HEAD=… expect=…` equal, and `PREFLIGHT ok`); evidence COMMIT `3200b5a507d28c13dfd04bbb449df4205c200f7d`, and `prereg ok` for `run.sh` `6b93eb08`, `run2.sh` `695c6bb1`, `t0_app.py` `25aaa6aa`, `t0_driver.py` `db862c8d`, `t0_analyse.py` `2d2d0f44` (all byte-identical to the blobs under `evidence/sl-1455-t0/`). Base `origin/main` COMMIT `372fa92ae3ab306bc067c234487ce929dc0e2a04`; main was not re-merged.
  - **Where.** `~/gi-pricing-plan.local/scratch/sl1455-t0/out-20261012T021609/results.md` (the OPEN and CLOSE process blocks are appended to it from the heading "Seat processes at OPEN and CLOSE", and are in `seat-procs-open.txt` and `seat-procs-close.txt` beside it); the log is `~/gi-pricing-plan.local/scratch/sl1455-t0/wrapper-rerun.out`. Not in the repository.
  - **The reading rule, quoted verbatim from `reading_rule` in `t0_analyse.py` (pre-registered in evidence `3200b5a5`):**

    > Per repeat (all request records of the measured window, whatever their status, and the client's error count): longest single pool checkout `L` (ms), server `total` p99 `P` (ms), client errors `E`.
    > CLEAN repeat = L < 30000 AND P < 1000 AND E == 0. SATURATING repeat = L >= 30000 OR E > 0. any other repeat = neither.
    > Arm verdict: CLEAN if all 3 repeats are clean; SATURATES if any repeat saturates; otherwise MIXED (reported as neither). Read together: both arms CLEAN = debug mode was the stall; either arm SATURATES = the 6-checkout / 10-statement shape saturates the pool at 25 rps without debug mode.

  - **The per-repeat table, verbatim from `results.md`:**

    | arm | run | longest checkout ms | server total p99 ms | client errors | repeat |
    |---|---|---|---|---|---|
    | bench-gbm | 1 | 9 | 146.2 | 0 | clean |
    | bench-gbm | 2 | 13 | 148.0 | 0 | clean |
    | bench-gbm | 3 | 11 | 140.2 | 0 | clean |
    | bench-nogbm | 1 | 13 | 131.0 | 0 | clean |
    | bench-nogbm | 2 | 17 | 115.9 | 0 | clean |
    | bench-nogbm | 3 | 13 | 109.2 | 0 | clean |

    Arm verdicts: bench-gbm = CLEAN; bench-nogbm = CLEAN. By the pre-registered sentence, both arms CLEAN = debug mode was the stall. The lead verified the reading against `reading_rule` and `results.md` (from-lead "2026-10-12 02:21:18 BST"). No interpretation is added here beyond the rule.
  - **Per arm, server-side `total` ms (p50 / p99 / max, 3 repeats pooled, 1500 requests, 25 rps):** `bench-gbm` 88.60 / 142.55 / 193.92; `bench-nogbm` 78.12 / 116.43 / 179.66.
  - **Phase table (p50 / p99 ms; `bench-gbm` | `bench-nogbm`):** auth 10.69 / 17.84 | 10.30 / 17.12; rbac 6.37 / 12.07 | 6.18 / 10.19; rate_limit 10.96 / 18.99 | 10.22 / 18.75; serving_ref 9.35 / 16.20 | 8.95 / 15.02; fetch_bundle 8.27 / 16.04 | 8.37 / 13.61; score_one 13.16 / 26.46 | 7.94 / 14.53; sample_trace 11.55 / 22.65 | 10.86 / 20.48; serialise 0.08 / 0.22 | 0.08 / 0.15.
  - **Structural facts (this run; the first run's agree).** Pool checkouts per request p50 6 (checkout ms p99 30.50 | 28.69; longest single 12.57 | 17.34), statements 10, commits 2; slot hits 1500, misses 0 in each arm; loop stalls of 50 ms or more: 0 and 0; new connections in the window: 0 and 0; GC gen2 3 collections, longest 369.24 | 360.00 ms; asyncio slow-callback lines 0 (debug mode off).
  - **py-spy, SAMPLING mode only (`--nonblocking`), top frames by self time; one 25 rps pass per arm.** `bench-nogbm`: `asyncio/runners.run` 32.2%, `_compile_bytecode` 2.8%, `asyncpg execute` 1.9%, pydantic `_generate_schema` 1.4%, `__subclasshook__` 1.3%, sqlalchemy `greenlet_spawn` 1.1%. `bench-gbm`: `asyncio/runners.run` 27.4%, `_compile_bytecode` 3.5%, xgboost `_from_numpy_array` 2.4%, `asyncpg execute` 2.1%, pandas accessor lambda 1.7%, xgboost `predict` 1.4%, `greenlet_spawn` 1.2%. No `traceback` or `linecache` frames appear. The `bench-gbm` py-spy pass has client p99 901.6 ms (n=500, errors 0); it is an instrumented pass and is not read by the rule.
  - **Per-pass START – END (BST) and steal:** `bench-nogbm` run1 02:16:18 – 02:16:49 0.63%; run2 02:16:49 – 02:17:19 0.65%; run3 02:17:19 – 02:17:50 0.63%; py-spy 02:17:50 – 02:18:19 0.63%. `bench-gbm` run1 02:18:21 – 02:18:52 0.55%; run2 02:18:52 – 02:19:24 0.60%; run3 02:19:24 – 02:19:56 0.65%; py-spy 02:19:56 – 02:20:27 1.03%. Load average 2.40 / 2.88 / 2.28 at the start, 2.70 / 2.88 / 2.45 at the end.
  - **Disturbance disclosure (condition 2).** No `gh`, `pytest`, `vitest`, `uvicorn` or `alembic` process was alive at OPEN (02:16:09) or at CLOSE (02:20:28). The box was not free of all CPU: the seats' Claude sessions were idle at 3–7% CPU each, and the harness's own hook processes burst (about 150%, 109% and 100%) at the instant a seat ran a tool call, at OPEN (the call that launched this wrapper); no burst appears at CLOSE. The largest consumers at CLOSE: a `claude bg-spare` 7.0%, `executor-sl1527` 6.7%, `docker-proxy` 4.5%, `minio` 2.8%. The OPEN and CLOSE blocks are in the files named above. Steal is 0.55% – 1.03%.

- **2026-10-14 10:3x BST — need 4 re-read at dispatch, `origin/main` `ba68a6da`.** `git diff --name-only 47d770e8 ba68a6da -- <need 4's eight files> backend/src/app/config.py scripts/demo.py backend/src/app/platform/rate_limit.py` prints `deps.py`, `score.py`, `auth/service.py`, `main.py`, `rate_limit.py`, `scripts/bench-rating.py`, `scripts/demo.py`. The commits behind it are #1157 `cdaaa573`, #1256 `84ff9f0b`, #1262 `2edc4d89`, #1265 `fe0b0627`, #1278 `fbde0f70`, #1280 `fe80aec6`, #1282 `13a02bba`, #1289 `073bf5b4`. Task 0's measured trees are slice commits `47cf5604` (first run) and `3c0e99a0` (debug-off rerun). `git merge-base --is-ancestor <commit> <tree>` for both trees: #1157, #1256, #1262, #1265, #1278 and #1280 are ancestors (rc 0); **#1282 `13a02bba` and #1289 `073bf5b4` are not (rc 1)**.
  - **Code-read re-derivation for the two (no timing run).** `git diff 3c0e99a0 78177ec8 -- backend/src/app/api/score.py` is 6 lines: a docstring sentence and `responses={**problems(...), 200: {"model": ...}}` on `/score` and `/score/compare`. `responses=` is read only when FastAPI builds the OpenAPI document, so the request path takes no statement, checkout or blob read from it. #1289's only `backend/src` change is `platform/workspaces.py`, which none of `api/score.py`, `api/deps.py` or `auth/service.py` imports; the rest is `scripts/demo.py`, `examples/` and tests. Over `3c0e99a0..78177ec8`, `auth/`, `db/`, `main.py`, `deps.py`, `authz.py`, `bundle_slot.py`, `rate_limit.py` and `settings_service.py` are unchanged, and the one `pricing_core/rating/score.py` change that adds a function is `_batch_error_row` (the batch path). Task 0's phase table therefore holds for the moved code: **the request path's statements, checkouts and blob reads are those Task 0 measured (6 checkouts, 10 statements), and the timing-free guard's 6/10 on this head agrees.** Need 4 is met.

- **2026-10-14 — Phase 1 reds, then Task 3 (RL-1685 DP-1 (a), (b), DP-4), `run-small.sh`, one file per call, DB `gipricing_sl-1455_df5ed723`.** Red tree `78177ec8` plus the test files; green tree `0544220a`, with the gc test's second assert added after it.
  - **Red by cause, then green.** `test_score_request_cost.py`: `assert 6 <= 1` (`{'checkouts': 6, 'statements': 10}`), `assert 10 <= 9`, and `assert 1 == 0` (one `UPDATE api_keys` inside the 30 s interval) are red; after the 60 s interval alone the cost file is `1 failed, 5 passed` (statements 9, checkouts still 6); after the request session it is `6 passed`. Guards, green before and after: the interval-passed test and `test_a_failed_sampling_rate_read_degrades_to_not_sampled` (both parametrisations). `test_startup_gc_freeze.py`: both asserts red on the base `main.py` (`assert [] == [True]`; `assert 0 > 0`, 0 objects before the lifespan and 0 at yield), `2 passed` with `gc.freeze()` before `yield`.
  - **The gc test's form.** RL-1685's "freeze count is non-zero once the app has started" cannot fail: in a probe test (the first `create_app` in the process) `gc.get_freeze_count()` was 0 after `gc.unfreeze()`, 375 after `create_app(settings)` and still 375 after `TestClient.__enter__`, with no `gc.freeze` in `backend/src` or `packages`, none seen by a wrapper plugin on `gc.freeze` and none by `sys.setprofile` on the calling thread. The ruling of the maintainer (by delegation), to-lead "2026-10-14 10:54:56 BST", replaced it with two asserts (a spy that wraps the real `gc.freeze`, and the delta of `get_freeze_count()` from just before the lifespan to `yield`), recorded in the correcting RL 8024 (working id).
  - **The 375 baseline's source is UNKNOWN, and is not chased (that ruling).** One further observation, not an explanation: in the final test file the second `create_app` in a process showed a baseline of 0, so the 375 may belong to the first `create_app` of a process.
  - **Regression, separate runs at `0544220a`:** `test_score.py` 52 passed; `test_traces.py` 39; `test_score_rate_limit.py` 9 passed, 1 skipped; `test_auth_keys.py` 20; `test_score_compare.py` 20; `test_api_authorisation_sweep.py` 9; `test_bench_rating_header.py` with `test_bench_rating_calls.py` 4. Static: `ruff check backend/src` clean, `mypy` no issues in 239 source files, `lint-imports` 4 kept 0 broken.
  - **Write set, widened by RL-1685 option (i):** `api/score.py`, `api/deps.py`, `api/authz.py`, `auth/service.py`, `db/session.py`, `main.py` and `platform/rate_limit.py` (`enforce` takes a session).

- **2026-10-14 — audit fixes F1–F4 (executor-sl1455b), code commit `5e00fa74`, DB `gipricing_sl-1455_df5ed723`, `run-small.sh`.**
  - **Task 1 Step 3, the header test's red line.** Script and test at `d943c2d0` (the script as of `c9a64068`), run from a scratch copy: `test_bench_rating_header.py` is `3 failed` — `AssertionError: machine: Intel(R) Xeon(R) CPU @ 2.20GHz, 8 cores, 32.9 GB RAM, 1-minute load average 6.08 at startup / warmup 200 calls, ...` with `assert None` from `re.search('\\bN = 1\\b', ...)`, `SystemExit: 2` for the flag, and `TypeError: _serve() got an unexpected keyword argument 'workers'`. On the branch tip the same file is `3 passed`.
  - **Task 1 Step 4.** `uv run python scripts/bench-rating.py --help` lists `--http`, `--rates RATES`, `--rung-seconds`, `--port`, `--speedup`, `--dsn`, `--bucket` and `--workers WORKERS` ("N, the uvicorn worker processes of the replica under test (RL-1685)"). The `--rates 25` invocation is **owed to Task 4's window**: `--http` "holds the compose stack exclusively" (its own help text) and spawns a server and a load generator, which this seat does not run beside a held gate (audit F3: "may be recorded as owed to Task 4's window").
  - **Task 3 Step 5, byte-identity.** **Owed to Task 4's window**, for the same reason: it needs the bench quote scored against a compiled bundle on `main` and on the head, which is the Task 4 fixture. The code-read half: this commit changes `score.py` only by closing the read session before the sampled write, and `deps.py`/`authz.py` only by who closes the session; neither touches `score_one`, `build_scoring_result` or the response serialisation.
  - **F1, red by cause then green.** `test_request_connections.py::test_an_api_key_request_to_a_require_caller_route_holds_no_connection_in_the_handler` (a second `GET /me` with a Service Account key; `pool.checkedout()` read when the handler begins its own reads): red `assert [1] == [0]` on `cc9512ca` (an unstamped key: the first request commits the `last_used_at` stamp, which releases the connection, so the first version of the test passed for the wrong reason and warms the key first), green `[0]` after `require_caller` closes the request session. `requires()` now depends on `resolve_caller` (the old body), so `/score` keeps its one checkout. The five modules named by the audit (`me.py`, `deployments.py`, `approvals.py`, `demo.py`, `validation.py`) all depend on `require_caller` and are fixed by that one change; the test drives `/me`.
  - **F2, red by cause then green.** `test_the_sampled_trace_write_starts_with_the_read_session_released` (a decline is sampled at 100 %; `pool.checkedout()` read when `write_pending_trace` is entered): red `assert [1] == [0]`, green `[0]` after `await read_session.close()` precedes the write; the trace row is still written (asserted).
  - **F4.** `_leave_no_frozen_objects` (autouse, `gc.unfreeze()`) moved from `test_startup_gc_freeze.py` to `conftest.py`; the gc test's docstring no longer states 375 as a fact (its source is UNKNOWN, and the final file read 0).
  - **Regression, separate runs at `5e00fa74`:** `test_request_connections.py` + `test_startup_gc_freeze.py` + `test_score_request_cost.py` 10 passed; `test_score.py` + `test_traces.py` + `test_score_rate_limit.py` 100 passed, 1 skipped; `test_auth_keys.py` + `test_api_me.py` + `test_api_approvals.py` 123 passed; `test_api_authorisation_sweep.py` + `test_workspace_identity.py` + `test_api_validation_rules.py` 25 passed; `test_deployments.py` + `test_workspace_switch.py` + `test_api_jobs.py` 82 passed. `ruff check backend` clean, `mypy` no issues in 239 source files, `lint-imports` 4 kept 0 broken. The gate is not run.
  - **Write set, complete:** `api/score.py`, `api/deps.py`, `api/authz.py`, `auth/service.py`, `db/session.py`, `main.py`, `platform/rate_limit.py`, `scripts/bench-rating.py`, `backend/tests/test_score_request_cost.py`, `backend/tests/test_bench_rating_header.py`, `backend/tests/test_startup_gc_freeze.py`, `backend/tests/test_request_connections.py` (new), `backend/tests/conftest.py`, and this ledger.
- **2026-10-16 09:3x BST — re-merge of `origin/main` before the ALONE re-gate (executor-1455).** `origin/main` `0877e6e7a756c4621890713a4d3b016e75e33654` merged into the branch (a merge, not a rebase) as COMMIT `49d7f086c9dbaf16a6149a7868d68ebc203909e0` (parents `34f08fdb900ba6d75764ba7fb65e7d5016af9c7d`, `0877e6e7`; tree `24b9a12437109a346f3e579da059072773c0eeb1`). Only `docs/INDEX.md` conflicted (taken from `origin/main`, regenerated with `scripts/doc-index.py`). The merge brings in `beee5ebe`, `d657736b` and `0877e6e7`, which the earlier base lacked. **Any earlier sha in this ledger that names the re-gate head or base (`34f08fdb` as head; `ba68a6da` or `372fa92e` as base) is superseded for the re-gate by this entry; the gate head is the head the lead's `EXPECT_HEAD` names, which is this merge plus the commit that adds this entry.** The ledger's Gate section names no head or base, so nothing in it is stale; the re-gate script is `~/gi-pricing-plan.local/scratch/sl1455-regate.sh`.

## PRs

(none yet; Task 0 is not a PR on its own — the slice's one PR carries this ledger at the slice's end.)
