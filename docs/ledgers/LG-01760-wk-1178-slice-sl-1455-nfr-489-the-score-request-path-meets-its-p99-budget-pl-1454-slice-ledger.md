---
id: LG-1760
family: ledger
title: WK-1178 slice SL-1455 — NFR-489, the /score request path meets its p99 budget at 25 to 200 rps (PL-1454 slice ledger)
status: closed
created: 2026-10-17 # original date 2026-10-11, set at the filing; minted 2026-10-17
owner: executor
tree: 2e5a8121bfa77353ac3260165cf19313fd390028
phase: P2
work: WK-1178
slice: SL-1455
plans: [PL-1454]
corrected_by: []
relates: [PL-1454, FD-1411, SL-1259, RL-1263, RL-921, RL-1379, RL-1685, RL-1716, RL-1755, NFR-489]
---

# LG-1760 — WK-1178 slice SL-1455: the NFR-489 remedy for `/score`

*(Minted 2026-10-17 as LG-1760 from working id 9932, in the SL-1455 PR; RL-1755 was minted from working id 8076 in the D18 batch mint PR.)* Executed by
`executor-sl1455` from PL-1454, base `origin/main` `d699a561d6a93f33b74beb9c07023f8e655bb8c7`. Times are
BST (`TZ=Europe/London date`) unless marked. **This ledger covers Tasks 0–3 as built, the re-gate of 2026-10-16 and the final slice audit** (the GO was "Task 0 only"; Tasks 1–3 followed once
RL-1685 ruled DP-1…DP-4 from Task 0's record). Tasks 4 and 6 are carried, not open without an owner (Task list below); the
front-matter `tree:` is the code tree gated at `787cfeed` (the re-gate section), not the Task 0 base it once named.

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
- [ ] Task 4 — **carried: the dedicated host's Task 4 session (nfr-bench-1), owner the maintainer** (lead verdicts, `from-lead-2026-10-09.md` "2026-10-16 22:22:11 BST"; the maintainer's 11:11:03 item 3 and 11:16:35). Owed to it: the NFR-489 and NFR-454 remedy-proof readings (the FD-1411 remedy proof only; the NFR-489 exit verdict stays SL-1259's, RL-1614, per the maintainer's correction "2026-10-17 11:22:47 BST"), Acceptance 2 and 3, the `--http` `--rates 25` run (Acceptance 6), Task 1 Step 4's one-line fetch run, Task 3 Step 5's byte-identity, and Acceptance 1's default-live arm limb (below). The shared-VM venue named in Acceptance 2 is superseded for this by RL-1755 (audit F1, discharged).
- [x] Task 5 — the two-half gate: run as the ALONE re-gate at `787cfeed` (Re-gate section); the maintainer accepted it.
- [ ] Task 6 — **carried: DP-6 (b)**, not this slice's. Under DP-6 (b) the scripted journey's `/score` step is built and accepted by the plan for `PL-1371` §3.8 item 7 (Acceptance 9 below).
- **Acceptance 1, default-live arm — OWED to Task 4.** The debug-off table for the default-live arm (and for 50 rps) and the one-line "same per-request work" answer for Step 3b are not recorded here; they travel with Acceptance 2's live readings to the dedicated-host session. Task 0 Step 5's tabulation is therefore recorded for the bench arms only.

### Gate

The per-task runs are in the Build log. The two-half gate is Task 5's and ran as the ALONE re-gate at `787cfeed` — see "Re-gate 2026-10-16 (head 787cfeed)" below for its stage rcs, the 13 pytest failures (all the check 31 cascade on this ledger's working id), and the NFR-489 line ("not measured by this gate").

### Acceptance 9 (DP-6 (b)) — the ruling and the owner

DP-6 was ruled (b) by the maintainer (by delegation), `to-lead.md` entry headed "2026-10-05 09:59:49 BST — A10 early ACCEPTED …". Its binding condition, verbatim: "item 7's record names NFR-489 (p99 < 50 ms with GBM, < 15 ms without, per replica) as an ACCEPTANCE of the demo's own /score call on the G2 path, measured uncontended, ≥3 runs. So the demo path cannot fall between the two owners." PL-1454 Hand-off item 4 line: "Until it is planned, the exit-demo `/score` risk is owned by WK-1178 through that item, not by this slice." The owner of the scripted journey's `/score` step is the plan for `PL-1371` §3.8 item 7 ("Exit demo (b): the scripted `WF-699` journey", WK-1178, unplanned); this slice touches neither `scripts/demo.py` nor `backend/tests/test_demo_command.py`.

### Audit findings of the final slice audit (2026-10-16), disposition

- **F1 (MEDIUM, process): discharged by RL-1755** — the maintainer's dated line of 2026-10-16 22:22:44 BST (`to-lead.md`), which supersedes PL-1454's shared-VM host clause for Task 4's Acceptance 2 and 3 sweep (nfr-bench-1, "measured, dedicated host (G4 discharge)", conditions (a)–(c)); the plan body is frozen from its merge and stays as written. Its item 2 was corrected on 2026-10-17 11:22:47 BST: the sweep is the G4 discharge of the FD-1411 remedy proof, not the NFR-489 exit verdict. Lead verdict: `from-lead-2026-10-09.md` "2026-10-16 22:23:23 BST".
- **F2 (LOW, ledger): fixed here** — the header, the Task list (Tasks 4–6), the Gate section, front-matter `tree:` and the default-live arm are updated above.
- **F3 (LOW, ledger): fixed here** — the DP-6 (b) ruling and the Hand-off item 4 line are quoted in the preceding subsection.


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
| RL-1685 obliges: LG-1760's minted id into RL-1685 `relates` | owed at the mint (minter); LG-1760's own `relates` does not carry RL-1685 or RL 8024 (since minted as RL-1716) | **Reassigned to the minter**, with F3's LG-side fix |

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
and the correcting RL-1716 (minted 2026-10-14 from working id 8024, branch `origin/docs-d16-2026-10-14` `75f9b1ae`) is now at `origin/main`.
Until it merges, `docs/rulings/RL-01685-…` still says the vacuous form, and this slice's test follows the
maintainer's entry, not the merged ruling text. The lead should keep the merge order RL 8024 (since minted as RL-1716) before or with this slice.

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
  LG 9932 (minted as LG-1760, 2026-10-17); it is a front-matter-only change to a frozen record (the same form as the correcting RL's own
  `corrected_by`). Today `relates` lists neither the LG nor RL 8024 (since minted as RL-1716) on either side.

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
- **F3 — LOW (ledger).** `LG-1760` is stale against its own build. (i) The header and the Task list say "This
  ledger covers Task 0 only" and "Tasks 1–6 — not started"; the Gate section says "Not applicable to Task 0".
  (ii) No Build log entry for **Task 1** (commits `c9a64068`, `1ab36c9f`): no recorded red of the header
  test on the base `_serve`/`main` (the commit order `d943c2d0` then `1ab36c9f` suggests it was red, but the
  failure line is not recorded), no `--help` or `--rates 25` run (Step 4). (iii) No **Task 3 Step 5**
  byte-identity entry. (iv) `relates:` lacks RL-1685 and RL 8024 (since minted as RL-1716). (v) The write-set line omits the three
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

#### Final slice audit, 2026-10-16 (auditor-sl1455c; supersedes the Tasks 1–3 audit's "Tasks 4–6 not audited")

Range: `origin/main...2c0bcc29` with `origin/main` measured as `6b25b9bcf11733fd3aa285ea9757aa7676520749`
(#1310, fetched 2026-10-16 22:2x BST); the merge base is `0877e6e7a756c4621890713a4d3b016e75e33654`, the main the
branch re-merged at `49d7f086`. 24 commits, 17 paths. Method: reading plus `git`; **no test, bench or gate run by me**.
Every verdict below is PROPOSED; the lead decides. I do not set `LG-1760` or `SL-1455` `closed`: the lead's merge does
that, and the slice's NFR-489 limb is carried (below).

**Gated tree vs this head.** `git diff --name-only 787cfeed 2c0bcc29` prints one path, this ledger
(`docs/ledgers/LG-01760-…-slice-ledger.md`); `git merge-base --is-ancestor 787cfeed 2c0bcc29` exits 0. Trees:
`787cfeed^{tree}` `2e5a8121…` (equals the `tree:` in `gate.log:1`), `2c0bcc29^{tree}` `7b3d3ba7…`. So the gate's code
verdict applies to `2c0bcc29`, docs-only delta.

**Gate (`~/gi-pricing-plan.local/scratch/sl1455-regate/gate.log`, ENDED 2026-10-16 11:05:17 BST).** Read: ruff, mypy,
import_linter, req_coverage, contracts rc 0; audit_docs rc 1; pytest rc 1 (`13 failed, 5858 passed, 6 skipped`, 
`gate.log:23`); six frontend stages rc 0; demo rc 124 (the script's own `timeout -s INT`, `demo.log` "journey done",
"served page … answered 200", "stopped."). The 13 `FAILED` lines are `pytest.log:10221-10233`; I matched them one by one to
the table in "Re-gate 2026-10-16 (head 787cfeed)" (b): the same 13 node ids, 7 pre-registered and 6 not. The
maintainer read the 6 and accepted the gate at "2026-10-16 11:11:03 BST" item 1 (each fails `assert result.returncode
== 0` on audit-docs with exactly the check 31 pair); the incomplete pre-registration is a review miss, recorded in the
re-gate section (c) as the maintainer's 11:09:05 item (2) asked. **I did not re-derive the six causes from the log; I
rely on the maintainer's reading and the executor's quoted assert lines.** `pytest -q` prints no per-test names, so the
new test files (`test_score_request_cost.py`, `test_request_connections.py`, `test_startup_gc_freeze.py`,
`test_bench_rating_header.py`) are evidenced green by "none of them is among the 13 FAILED" and by the executor's
per-file runs in the Build log, not by a printed pass line.

**Per-requirement table (scope from `PL-1454` §"Requirement coverage" and Acceptance 1–9).**

| Item | Evidence | Proposed verdict |
|---|---|---|
| NFR-489 (`03` §9) p99 < 50 ms / < 15 ms, 25–200 rps | no bench invocation exists for the remedy head; `gate.log:37`: "not measured by this gate"; Task 4 unchecked in the plan; Build log has only Task 0's diagnostic runs (base, not the remedy) | **Deferred with an owner**: the dedicated host (`nfr-bench-1`), Task 4 session, owner the maintainer per `docs/roadmap.md` §G4 (amended 2026-09-29), "to-lead.md 2026-10-16 11:11:03 BST" item 3 and "11:16:35" ("earliest Mon 19 Oct"). Acceptance 2 needs a dated line on `PL-1454` (see F1) |
| NFR-454 (`00`) held by the same measurement | as NFR-489 | **Deferred with an owner**, same |
| Acceptance 1 (Task 0 attribution) | Build log: ALONE run 2026-10-11 23:41–00:14 (void as stall diagnosis, asyncio debug), debug-off rerun 2026-10-12 02:16–02:20 (bench arms only, 25 rps, 3 runs, both CLEAN, phase table, py-spy sampling). No debug-off table for the default-live arm or for 50 rps; no one-line "same per-request work" answer for Step 3b; the Task list's Step 5 box is unchecked | **Delivered, partly**: the bench arms' table and events are recorded. The live-arm table and the one-line answer are **not evidenced**; propose **reassigned** with Acceptance 2's live readings to the Task 4 host session (the ruled DP-6 (b) path), and say so in the ledger (F2) |
| Acceptance 2 (12 invocations) | none | **Deferred with an owner** (as NFR-489) |
| Acceptance 3 (component half unchanged) | same invocations; none | **Deferred with an owner** (as NFR-489) |
| Acceptance 4 (timing-free guard, red first) | `test_score_request_cost.py` reds by cause `assert 6 <= 1`, `assert 10 <= 9`, `assert 1 == 0` (Build log, 2026-10-14 Phase 1 reds); file green in the gate (not among the 13); F1/F2 guards in `test_request_connections.py` and the cost file, red by cause `[1] == [0]` | **Delivered and tested** |
| Acceptance 5 (existing guards pass) | `test_score.py`, `test_traces.py`, `test_score_rate_limit.py` not among the 13; `test_score.py` not in the diff | **Delivered and tested** |
| Acceptance 6 (harness says what it measures) | `scripts/bench-rating.py:1308` prints "warm (slot hit: version row read only)" beside the cold figure; header prints `N`, `--workers` at `:1104`; header test red then green (Build log 2026-10-14, F3 entry); `--help` run recorded; the `--rates 25` run is owed | **Delivered and tested**, with the one `--http` run owed to Task 4 (same owner) |
| Acceptance 7 (two-half gate) | `gate.log` above, head `787cfeed`; only the check 31 cascade on working id 9932 is red; 13 of 13 failures are that class | **Delivered**, with the check 31 class standing until LG 9932 is minted (minted as LG-1760, 2026-10-17) (see "Closing acts") |
| Acceptance 8 (write set) | `git diff --stat origin/main...HEAD` lists 17 paths; the 12 source/test paths are the plan's table plus RL-1685's three admissions plus `conftest.py` and `test_request_connections.py` (F1/F2 fixes of the 14 Oct audit); `docs/INDEX.md`, the plan (`status: active`), `docs/roadmap.md` (row status) and the ledger are the activation and registry; the ledger's write-set line (Build log, F1–F4 entry) lists them | **Delivered** |
| Acceptance 9 (DP-6 (b)) | the plan's Hand-off item 4 quotes the 09:59:49 ruling and its binding condition and names `PL-1371` §3.8 item 7; **the ledger does not quote it** (grep of the ledger for "Hand-off item 4", "G2 path", "09:59:49": no hit) | **Delivered but untested** as to the ledger clause: the owner is named in the plan, not in this ledger (F3) |
| FR-243 / NFR-497 / FR-259 preserved | cost-file degrade test (read fails or aborts the shared transaction, 200, `quoted`, no trace row); `test_a_failed_sampling_rate_read…`; sampled write after `read_session.close()` with the trace row asserted | **Delivered and tested** |
| FR-268 not built | no path touches it | Conforms |
| Tasks 1–3 findings F1–F4 of the 14 Oct audit | fixed in `5e00fa74` (`require_caller` closes; `requires()` on `resolve_caller`; `read_session.close()` before the sampled write; autouse `gc.unfreeze()` in `conftest.py`), reds by cause in the Build log, F3 ledger edits `7d9f61b7` | **Discharged** (re-audited below) |

**RE-audit of the 14 Oct F1/F2 fixes, at `2c0bcc29`.** Scoped to what changed (`git diff 11677daa 5e00fa74`): read, not
run. Read at `2c0bcc29`: `deps.py:229` `resolve_caller` (the old body); `deps.py:288-297` `require_caller` depends on it
and ends `await session.close()`; `authz.py:42` `CallerDep` uses `resolve_caller`; `score.py:570` `await read_session.close()`;
`conftest.py:91` `gc.unfreeze()` — the split is as the Build log says; the `[1] == [0]` red lines are recorded; both tests were green in the 787cfeed pytest (not among
the 13). I did not re-read FastAPI's dependency-exit ordering and ran nothing.

**Reachability (charter two-way match).** `git merge-base --is-ancestor <sha> 2c0bcc29` exits 0 for every code or test
commit the ledger names: `c9a64068`, `1ab36c9f`, `d943c2d0`, `fecaf7b6`, `9777184f`, `051f9b3d`, `0544220a`, `11677daa`,
`5e00fa74`, `3c0e99a0`, `78177ec8`, `34f08fdb`, `49d7f086`, `787cfeed`. Not ancestors, and each is a reference to a
record outside this branch, not slice evidence: `c41475c2`/`3200b5a5`/`d87e354d` (the evidence branch
`evidence/sl-1455-t0-2026-10-11`), `75f9b1ae` (RL 8024's branch (since minted as RL-1716)), `372fa92e` (an old main commit absent from this
clone), and eight blobs (`run.sh`, `run2.sh`, `t0_*.py`, …) which `cat-file` reports as blobs by construction.

**Barred word.** `git diff origin/main...2c0bcc29 -U0 | grep '^+' | grep -ciE 'dep''uty'` prints 0; the same over
`git log origin/main..2c0bcc29 --format=%B` prints 0.

**Merge forecast (information, not a finding).** `git merge-tree --write-tree origin/main 2c0bcc29` exits 1 against
`6b25b9bc`; the only conflict is `docs/INDEX.md` (generated; take theirs, regenerate under the gate-2 flock). `docs/roadmap.md`
auto-merges. The maintainer's "11:11:03" item 1 says this slice merges after #1310 in id order.

**Closing acts.** (i) `LG-1760` still reads `status: active`, `tree: 5e00fa74…` (the Task 0 base) and "MERGE-ACK: not yet
given"; the header says "covers Tasks 0–3"; the Task list says "Tasks 4–6 — not started" and has Step 5/6 boxes open;
the Gate section says "not applicable to Tasks 0–3" (the re-gate section answers it but the Gate section is not
updated) — an executor edit (F2). (ii) LG 9932 is a working id (minted as LG-1760, 2026-10-17): the lead mints it at the merge turn; check 31 stays red on this branch until then,
by the known class. (iii) RL-1685's `relates` still needs LG 9932 (minted as LG-1760, 2026-10-17) (and RL 8024 (since minted as RL-1716)) added at the mint, as the 14 Oct
audit said; owner the minter. (iv) `PL-1454` is frozen from its merge: the Acceptance 2 dated line is a delta or ruling,
not an edit of the plan body. (v) FD-1411's discharge needs SL-1259's NFR-489 verdict or the maintainer's dated line
(plan Hand-off 2); not discharged by this merge.

**Findings.**
- **F1 — MEDIUM (process, not code).** The slice cannot reach its own Acceptance 2 before merge: Task 4's measurement
  is carried to the dedicated host. The plan's Acceptance 2 names the shared VM as the venue ("This sweep runs on the
  shared VM"); the maintainer's "11:16:35 BST" says Task 4 "needs a dated line on PL-1454 Acceptance 2". No such line
  is in the repository at `2c0bcc29`. *Failure:* the merge records a Slice closed on a clean audit with an acceptance
  item whose venue the plan still gets wrong, and the host session has no filed instruction to follow. *Proposed
  fix:* the maintainer's dated line filed as an RL (the lead routes), before or with the merge; owner the maintainer;
  until then this stays the open item the NFR-489 verdict waits on.
- **F2 — LOW (ledger).** The ledger's header, Task list, Gate section and `tree:` are stale as listed under Closing acts (i); and
  Acceptance 1's live-arm table and one-line answer are neither recorded nor marked owed. *Fix:* an executor edit
  (or the lead's) marking Tasks 4 and 6 "carried: dedicated host / DP-6 (b)", Step 5/6 per the lead's ruling, the Gate
  section pointing at the re-gate section, and the live-arm items listed as owed to Task 4.
- **F3 — LOW (ledger, Acceptance 9).** The ledger does not quote the DP-6 (b) ruling and Hand-off item 4 line. *Fix:* one
  sentence in the ledger quoting the 2026-10-05 09:59:49 BST ruling's binding condition and naming `PL-1371` §3.8 item 7
  as the owner of the exit-demo `/score` step.
- **F4 — INFORMATION.** The gate's pre-registered list was 7 of the 13 known (recorded in the re-gate section (c)); no
  further action here. Standing: the `gc.freeze()` lifespan call and the 60 s `last_used_at` interval are product
  behaviour changes (RL-1685 DP-1 (b), DP-4) that the cost file guards; the byte-identity of the `/score` body
  (Task 3 Step 5) is still owed to Task 4's window and is listed under the same owner.

**Proposed verdict for the lead.** The code half of the slice (Tasks 1–3, the F1–F4 fixes, Acceptance 4–8) is delivered
and tested, and the gate on `787cfeed` is accepted by the maintainer. **Merge-ready after F2 and F3 (a ledger edit,
no code) and with F1 filed by the maintainer.** NFR-489 and NFR-454, Acceptance 2 and 3, the `--http` run of
Acceptance 6, Task 3 Step 5's byte-identity and Acceptance 1's live-arm limb are **deferred with an owner**: the
dedicated host's Task 4 session, the maintainer. Nothing is "not started" without an owner. Per the maintainer's
"11:11:03" item 3 the verdict on NFR-489 is not made here and is not implied by this merge.

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

### Re-gate 2026-10-16 (head 787cfeed)

Recorded by executor-1455b on 2026-10-16, from the primary files under `~/gi-pricing-plan.local/scratch/sl1455-regate/` (below, `gate.log`, `pytest.log`, `audit_docs.log`, `demo.log`) and the channel `~/gi-pricing-plan.local/channel/`. The gate verdict applies to the code at `787cfeedcfad64364157f3bde476c674d287af67` (tree `2e5a8121bfa77353ac3260165cf19313fd390028`, branch `sl-1455-wk1178-nfr489-http`); the commit that adds this section is LG-only and is checked at the ACK as docs-only. Clock: BST = UTC+1.

**(a) The gate.** ALONE gate: `gate.log` START `2026-10-16T08:58:37+00:00` (09:58:37 BST, load 1.83 2.42 2.59), END `2026-10-16T10:05:17+00:00` (11:05:17 BST, load 1.21 0.70 1.21); locks gate-1, gate-2 and small-test held. Preflight: head guard, branch and clean tree ok; `createdb` rc 0; `alembic upgrade` rc 0, 1 head; the four containers healthy; `pg_isready` rc 0.

| Stage | rc |
|---|---|
| ruff | 0 |
| mypy | 0 |
| import_linter | 0 |
| audit_docs | 1 (check 31 only, see (b)) |
| req_coverage | 0 |
| contracts | 0 |
| pytest | 1 |
| pnpm install --frozen-lockfile | 0 |
| pnpm generate:api | 0 |
| pnpm lint | 0 |
| pnpm type-check | 0 |
| pnpm test | 0 (`fe-test.log`: "Tests  730 passed (730)") |
| pnpm build | 0 |
| demo `--journey wf-699` | 124 |

- pytest summary line, verbatim (`gate.log:23`; last line of `pytest.log`): `13 failed, 5858 passed, 6 skipped, 116 warnings in 2363.39s (0:39:23)`.
- Frontend: 6 of 6 stages rc 0.
- `gate.log`: "tree after gate: 0 changed path(s)" (the gate left the tree clean).
- audit_docs rc 1: its `FAILED (2)` block (`audit_docs.log:882`) is exactly two lines, both check 31: "gap in the full allocation between 1730 and 9932" and "id 9932 is `created:` 2026-10-11, earlier than id 1730's 2026-10-14". The check 36 lines in the log are the standing disclosed legacy-form class, not in the `FAILED` block.
- Demo rc 124 is the stop by design, not a failure: the script runs `timeout -s INT 1500 … scripts/demo.py --journey wf-699` (`sl1455-regate.sh:79`), so the INT after the journey ends the process with 124. `demo.log:708` "journey done in 80s"; `demo.log:716` "served page: http://localhost:5173/ answered 200"; then the clean stop sequence (`demo.log:732-748`, "stopped.").

**(b) Classification of all 13 pytest failures: the check 31 cascade on LG 9932.** LG 9932 is a working id (minted in the slice PR; minted as LG-1760, 2026-10-17), so main's allocation shows a gap 1730..9932 and 9932's `created:` precedes 1730's. Every failure is a test that runs the real-tree audit and asserts on its exit, and each captured audit output ends in the same two check 31 lines. `pytest.log` `FAILED` lines: 10221-10233.

| # | Test | Evidence in `pytest.log` | On the script's list? |
|---|---|---|---|
| 1 | `test_audit_docs_finding_citations.py::test_a_finding_resolved_only_by_a_closure_record_is_not_flagged` | `FAILED (2)` :996 | yes |
| 2 | `test_audit_docs_ids.py::test_the_real_tree_passes_all_ten_checks` | `FAILED (2)` :1894 | yes |
| 3 | `test_audit_docs_ids.py::test_doc_id_check_exits_0_on_the_real_tree` | "doc-id.py check: [noncontiguous] docs/INDEX.md has a gap between 1730 and 9932", assert at :1562 | yes |
| 4 | `test_audit_docs_process_core_digest.py::test_an_unrelated_file_edit_is_the_negative_control_and_stays_green` | `FAILED (2)` :2812 | yes |
| 5 | `test_audit_docs_process_core_digest.py::test_the_committed_digest_currently_matches_the_committed_spec` | `FAILED (2)` :3710 | yes |
| 6 | `test_audit_docs_w37_11_ceiling.py::test_audit_docs_end_to_end_exit_0_then_1_then_0_on_an_injected_residue` | `FAILED (2)` :4622 | yes |
| 7 | `test_doc_index.py::test_an_index_skipping_a_reserved_block_breaks_contiguity` | "the live allocation is not contiguous: [(1730, 9932)]" (test body at :4630) | yes |
| 8 | `test_register_lint.py::test_check_29_is_wired_into_the_docs_gate` | `FAILED (2)` :5554; `assert result.returncode == 0` at :4672 | NO |
| 9 | `test_register_lint.py::test_check_29_note_carries_the_residue_line` | `FAILED (2)` :6454; assert at :5572 | NO |
| 10 | `test_register_lint.py::test_phase1b_residue_count_matches_check_29s_own_count` | `FAILED (2)` :7359; assert at :6477 | NO |
| 11 | `test_register_owed.py::test_check_29_wiring_is_undisturbed` | `FAILED (2)` :8258; assert at :7376 | NO |
| 12 | `test_repository_invariants.py::test_money_discipline_is_enforced_by_the_docs_audit` | `FAILED (2)` :9166; assert at :8284 | NO |
| 13 | `test_repository_invariants.py::test_journey_citations_are_audited_in_ci` | `FAILED (2)` :10087; "assert 1 == 0 … returncode=1" at :10091 | NO |

- Each `FAILED (2)` block above is the same two check 31 lines as `audit_docs.log:882`; I counted 22 check 31 lines under the 11 `FAILED (2)` blocks in `pytest.log`. No other cause appears in any of the 13.
- Re-verified by the executor (2026-10-16): rows 8 and 9 read in `pytest.log` — the test headers at :4661 and :5562, the `assert result.returncode == 0` lines at :4672 and :5572, and the `FAILED (2)` blocks at :5554 and :6454, which lie inside the respective test sections. The lead's relay (`from-lead-2026-10-09.md`, "## 2026-10-16 11:10:37 BST" item (1)) gave these as "4661+894" and "5562+893", i.e. one line off for the first; the lines above are the file's.
- Classified: the check 31 cascade on LG-1760; no real red. The 7 pre-registered node ids are rows 1-7 (`sl1455-regate.sh:5-14`); rows 8-13 are the 6 the script did not list.

**(c) The incomplete pre-registered list.** The maintainer's 11:09:05 entry, item (2) (`to-lead.md`, "## 2026-10-16 11:09:05 BST — Maintainer: SL-1455 gate END"): the 14 Oct review accepted a 7-item pre-registered list after SL-1695 had shown 13. The primary records of SL-1695's 13: `from-lead-2026-10-09.md` "## 2026-10-14 12:13:57 BST" (11 named: test_audit_docs_finding_citations x1, test_audit_docs_ids x2, process_core_digest x2, w37_11_ceiling x1, test_doc_index x1, test_register_lint x3, test_register_owed x1; the 135 tests then unrun), "## 2026-10-14 13:26:19 BST" ("the 135 unrun tests: 2 more F (test_repository_invariants.py::test_money_discipline_is_enforced_by_the_docs_audit, ::test_journey_citations_are_audited_in_ci)… TOTAL 13 F, all the unminted LG 9637 check-31 class"), and the re-gate "## 2026-10-14 14:59:47 BST" ("13 failed, 5812 passed, 6 skipped in 4128.41s"). The script's 7 (`sl1455-regate.sh:5-14`) omit exactly SL-1695's last six: register_lint x3, register_owed x1, repository_invariants x2. The list was a review miss in the grant, not a defect of the code: the 6 are the same names as SL-1695's accepted 13, and (b) shows each fails on check 31 and nothing else.

**(d) NFR-489.** Not measured by this gate: `gate.log:37` "NFR-489 p99: not measured by this gate; any shared-VM p99 is DIAGNOSTIC, never a pass (Task 4's ALONE sweep owns it)". No bench script ran (`scripts/bench-rating.py` was not invoked) and `pytest.log` has no p50/p95/p99 output, so no readings exist from this run. NFR-489 stays unevidenced as to the p99 budget; the readings are owed (the Task 4 ALONE sweep, or the dedicated host), per the maintainer's ruling to come. The gate's verdict is on the code and tests, not on the latency.

## PRs

(none yet; Task 0 is not a PR on its own — the slice's one PR carries this ledger at the slice's end.)

## Pre-registration (dated line 2026-11-04, batch 8)

*(2026-11-04, on to-lead "2026-11-04 09:57:14 GMT" (driver C' accepted, hash of record) and "2026-11-04 10:00:29 GMT" (the pre-registration rides the docs PR).)* Driver C', `~/gi-pricing-plan.local/scratch/nfr-bench-1/bench-c-nfr489-ladder.py`, sha256 `130dfb174ac3ca0ce09c8ae3e1b4a3f3d829faec463badbd68f61b6e991f97ab`, the NFR-489 ladder (Thursday's invocation `--rates 25,50,100,200 --runs 4 --workers 4 --serve-dsn …`, nfr-bench-1 S1 Thu 5 Nov 2026). Driver D (`bench-d-nfr489-mount.py`, sha256 `df6e7c9c3216895d175434cf92bd5d26c0335fe7f48621dfee5c2919997513d3`) is carried by CR-1999's NFR-489 row, not here (09:45:54). **Reading owed.**

## Addendum 2026-11-05 — nfr-bench-1 session 1: item C, the NFR-489 ladder (exec-nfrs1)

*(2026-11-05; authority: to-lead "2026-11-04 09:57:14 GMT" (driver C' accepted), RL-1837 (N = 4), RL-1755 item 3; the lead's amendment that this addendum rides docs/nfrbench-s1-wk690-2026-11-05.)*

Main `dae9637ea6f6a56f6502e9db70392cdfb2f3983d`, tree `715a8fd2e8ddeb27b68414db85929ccac359d1ad`, checked out detached at `~/gi` on the dedicated VM `nfr-bench-1` (GCE e2-standard-8, 8 vCPU, 32 GB; CPU Intel Xeon @ 2.20 GHz, family 6 model 79 stepping 0, flags hash `9674b27761c0`, the same as the shared box on 3 Nov; cpubench x3 py-loop 1.512/1.504/1.547 s, sha256-64MB 0.194/0.192/0.197 s; pgbench -s 10 -c 4 -j 2 -T 20: 1324.96 tps, 3.019 ms; CTAS 1 M rows 2579 ms). Run logs and driver outputs: `~/gi-pricing-plan.local/scratch/nfr-bench-1/s1/` (shared box; not in the repository); on the VM `~/logs/s1/`. Nothing else ran on the VM during a timed item (quiet bar: load1 < 1.0, `pgrep -c pytest` 0, read before each start).

Bring-up lines: plan step 5 (pnpm frozen install) = not run, cause: no node/pnpm on the VM; no S1 item depends on it. The login role `gip_app_login` was missing on the VM's pre-FD-1729 volume: `deploy/postgres/app-login-role.sql` was applied with `-d postgres` (cluster-level, not the template database) and `scripts/provision-app-role.py` set its password (the lead accepted this). The `--serve-dsn` form passed was `postgresql+asyncpg://gip_app_login@127.0.0.1:5432/<item db>` (password not recorded); the owner `--dsn` was `postgresql+asyncpg://gipricing@127.0.0.1:5432/<item db>`. Each item ran on its own `createdb -T gipricing` copy migrated to head `b7e4c2a91d36` (the template stayed at `a4d1f08c3b97`, untouched); server redis db 11. `redis-cli -n 0 dbsize` was 1 at START (a stale `gip:tenant` key from 21 Oct, not written by this session) and is quoted again at END. The VM already held database `gipricing_sl1455_t4_1792592230` from 21 Oct; it was left alone.

Driver C' `bench-c-nfr489-ladder.py` sha256 `130dfb174ac3ca0ce09c8ae3e1b4a3f3d829faec463badbd68f61b6e991f97ab` (`--expect-sha256`), `--rates 25,50,100,200 --runs 4 --workers 4`, plain seeded bundle (no mount), DB `nfrs1_c`, default trace sampling. 10:19:20–10:28:58Z, load1 0.78 at the quiet bar, 0.80 at start, rc 0, log `itemC-run.log`. The first OVER stops an arm within a run (RL-1755 item 3), so most arms stopped at their first rung.

Median p99 ms over the runs that reached the rung (runs; over-runs):

| condition, arm | 25 rps | 50 rps | 100 rps | 200 rps |
|---|---|---|---|---|
| with GBM (< 50), explicit-ref | 40.775 (4; 1 over, max 83.765) | 48.717 (3; 1 over) | 50.732 (2; 1 over) | 44529.373 (1; over) |
| with GBM (< 50), default-live | 48.582 (4; 1 over, max 52.408) | 56.291 (3; 2 over) | 205.927 (1; over, 1 error) | not reached |
| without GBM (< 15), explicit-ref | 37.541 (4; 4 over) | not reached | not reached | not reached |
| without GBM (< 15), default-live | 41.226 (4; 4 over) | not reached | not reached | not reached |

Errors 0 except one at 100 rps default-live. Handler p99 without GBM 33–42 ms, handler mean 23–29 ms, against the 15 ms budget. Verdict: **NFR-489 UNMET on both conditions (OVER on the driver's own summary for every arm) → FD owed (owner WK-674, FD-1836's reading)**. The without-GBM arm is no faster than the with-GBM arm at 25 rps (mean 27 ms against 30 ms); the auditor should look at that before reading the budget miss as a GBM cost. No retry.

*(Dated line, 2026-11-05, docs batch 11, by the auditor, on to-lead "2026-11-05 11:23:52 GMT" (FD-1836 correction accepted): the addendum sentence "Handler p99 without GBM 33–42 ms" (S1 item C) reads 30.05 to 42.45 ms. At 25 rps the handler means per run are, with GBM, explicit-ref 25.3 to 26.7 ms and default-live 29.9 to 32.2 ms, and, without GBM, explicit-ref 23.2 to 24.2 ms and default-live 27.8 to 28.5 ms: the no-GBM arm is about 2.5 ms faster in both arms.)*


## Addendum 2026-11-07 — nfr-bench-1 session 2: item N, a profile of the 25 rps no-GBM handler (NFR-489's fixed cost): a CAUSE reading, not a budget reading (exec-nfrs2)

**Reading (cause, not a verdict): in a 12 s py-spy window on the uvicorn worker serving the no-GBM bundle, about half of the active samples sit inside asyncpg / SQLAlchemy calls on the `/score` request path, about a third in `app` and `pricing_core` code, and the rating evaluation itself (`pricing_core.rating.score.score_one`) is 2 of 522 active samples. No frame holds more than 3.6 % of the active samples by self time: the fixed cost is spread across the framework and the per-request database round trips, not concentrated in one hot function.** No NFR-489 budget verdict is drawn from this run: the profiler perturbed the arm it sampled.

- **Tool: `py-spy` 0.4.3** (absent on the VM; installed with `uv tool install py-spy`, nothing else added; `/proc/sys/kernel/yama/ptrace_scope` = 0). Its `--help` ON THE VM was read first (`py-spy record`: `-p/--pid`, `-d/--duration`, `-r/--rate`, `-f/--format {flamegraph,raw,speedscope,chrometrace}`, `-o/--output`, `--nonblocking`, `-i/--idle`, `-g/--gil` …). Used: `py-spy dump -p <pid>` once, then `py-spy record -p <pid> -d 12 -r 100 -f raw -o N-spy.raw` — **default blocking mode** (the worker is paused at each sample; `--nonblocking` was not used), idle threads excluded (default). cProfile was not needed.
- **Driver and run:** driver C' `bench-c-nfr489-ladder.py` sha256 `130dfb174ac3ca0ce09c8ae3e1b4a3f3d829faec463badbd68f61b6e991f97ab` (run with `--expect-sha256`, re-hashed on the VM), `--repo <vm wt> --rates 25 --runs 1 --workers 1`, `--dsn` owner and `--serve-dsn` `gip_app_login` on its own `createdb -T` copy `gipricing_nfrs2_n` (bucket `nfrs2-n`, redis db 11; dropped and zeroed after, template `a4d1f08c3b97` unchanged), through `run-item.sh` (quiet bar load1 0.00, `pytest` 0; start 2026-11-07T19:12:16Z, wall 102 s; `machine:` line "AMD EPYC 7B12, 8 cores", load 0.08 at start). The driver ran all four arms at 25 rps with N = 1; the sampler was fired by the log line `--- without GBM / explicit-ref` plus 4 s, and attached to the largest-RSS `uvicorn app.main:create_app` process (pid 97765, port 8099) from 19:13:20 to 19:13:32. Head `6f958137b227f1a9499a4ab00caf40f79ba2439c` (tree `a995b876dd07bbc8e6b5d8712fd085178ba77e91`); host `e2-standard-8`, AMD EPYC 7B12 (item-G addendum).
- **That the sampled process served the no-GBM bundle:** the raw stacks contain 0 `xgboost` frames and 6 `pricing_core` lines; the no-GBM and GBM servers have separate logs (`N-logdir/server-c-nogbm.log`, `server-c-gbm.log`). The pid was chosen by RSS, not read from the bundle, so this is an inference from the frames.
- **Perturbation:** the sampled arm read p99 145.306 ms, handler mean 34.907 ms; the next arm (`default-live`, not sampled) read p99 45.206 ms, handler mean 28.262 ms. The sampled arm is therefore not a budget reading. The other 25 rps arms, N = 1 each: with GBM explicit-ref p99 68.062 ms (handler mean 25.018), default-live 43.503 ms (27.782). Session 1's no-GBM handler means were 23 to 29 ms (LG-1760's S1 addendum), so the handler mean on this faster CPU (cpubench ≈ 1.5× to 4.5× quicker per the item-G addendum) is not lower; that observation is stated without a conclusion.
- **Totals:** 984 samples, 462 of them with an idle-loop or idle-thread leaf (`Runner.run` asyncio/runners.py:118, `Condition.wait`, the thread-pool `_worker`), 522 active. **Top 10 frames by self time (active samples):** (blank frame) 19 (3.6 %); `PreparedStatement.__do_execute` (asyncpg/prepared_stmt.py:257) 18 (3.4 %); `_EffectiveRouteContext.matches` (fastapi/routing.py:1571) 13 (2.5 %); `_IncludedRouter._match` (fastapi/routing.py:1804) 9 (1.7 %); `_IncludedRouter._match` (fastapi/routing.py:1796) 9 (1.7 %); `greenlet_spawn` (sqlalchemy/util/_concurrency_py3k.py:184) 6 (1.1 %); `_is_gen_callable` (fastapi/dependencies/models.py:164) 5 (1.0 %); `Connection.execute` (asyncpg/connection.py:377) 5 (1.0 %); `TypeAdapter.validate_python` (pydantic/type_adapter.py:410) 5 (1.0 %); `WeakKeyDictionary.__getitem__` (weakref.py:415) 5 (1.0 %).
- **Inclusive shares of the 522 active samples (overlapping, by frame path):** Starlette middleware 349 (67 %), FastAPI routing and dependencies 315 (60 %), asyncpg or SQLAlchemy 275 (53 %), `pricing_core` or `app/` code 176 (34 %), pydantic 12 (2 %). In `app/api/score.py`: `score` line 612 32 samples, `score_rate_limit` line 167 29, `score` line 584 12, line 595 6; `pricing_core/rating/score.py:1040` `score_one` 2. Method: leaf and path counts over `N-spy.raw` (`N-spy-analysis.txt` holds the script's output). One 12 s window of one arm is one observation.
- The no-GBM handler mean's rise since 21 Oct (18.4 → 23.2 to 24.2 ms, aud-wk674) is **not** attributed here: this profile has no 21 Oct counterpart, and FD-1729's role change and SL-1992's reconcile remain candidates only.
- Logs: `~/gi-pricing-plan.local/scratch/nfr-bench-1/s2/N-profile.log`, `N-spy.log`, `N-spy.raw`, `N-spy-analysis.txt`, `N-logdir/`, `N-prep.log`, `N-cleanup.log`.

## Dated line 2026-11-07 — platform change between nfr-bench-1 sessions (exec-nfrs2)

Brief amendment of 2026-11-07 17:31:43 GMT (on to-lead "2026-11-07 17:31:27 GMT"): session 1's NFR-489 ladder (item C above) ran on an Intel Xeon @ 2.20 GHz (family 6, model 79); session 2's host is an AMD EPYC 7B12. Any comparison of the item-N profile or of session 2's 25 rps arms with session 1's carries: AMD EPYC 7B12; not like-for-like with S1; 8 vCPU; lower bound on a non-spec host. Item C's re-run on this platform (the FD-1836 control) is NOT done in S2 and moves to S3.

*(Dated line, 2026-11-09, docs batch 27, by the executor, on to-lead "2026-11-09 10:00:22 GMT" item (4): this ledger's front matter reads `status: active` at origin/main `40ba57f4b320` while its slice SL-1455 reads `status: closed` in `docs/roadmap.md` there. The slice's code merged as #1323 (`9c602fec`, "perf(score): SL-1455 — the /score request path's per-request cost cut for NFR-489 (FD-1411; LG-1760) (#1323)"); its row was set `closed` by #1432 (`2f108b1e`, "docs: docs batch 10 — eleven + one WK-1178 slice closes, the gate and adoption lines, FD-1838 + FD-2001 closing acts, the SL-1736 + SL-1854 audits, process rows (#1432)"). Derived by the predicate: ledger front matter `status: active` and its `slice:` row reading `closed` in `docs/roadmap.md` at `40ba57f4b320`; 13 ledgers, LG-2003 (SL-1736) and LG-1977 (SL-1976) excluded as their slices read `active`. The front matter is flipped to `status: closed` in this batch, per to-lead "2026-11-09 10:28:26 GMT" (LEDGERS), so the record no longer says `active` for a closed slice.)*

## Addendum 2026-11-09 — nfr-bench-1 session 3: item C (the FD-1836 control) and D5.12 (the NFR-489 exit reading)

*(Filled by the planner (plan-s3fill), docs batch 32, from `~/gi-pricing-plan.local/scratch/nfr-bench-1/s3/`; the S2 lines above stand. The D-3 and WK-674 decisions are quoted in CR-2103's S3 addendum.)*

### C

- C, with GBM, default-live, offered 25 rps (per replica 25: one api, N = 4): median p99 53.921 ms, max 65.559 ms, n_runs 4, over_runs 4, errors 0, budget < 50 ms: over; plain seeded bundle, not the governed path; tree 374a22bf33ad; Intel(R) Xeon(R) CPU @ 2.20GHz; 8 vCPU; lower bound on a non-spec host.
- C, with GBM, explicit-ref, offered 25 rps (per replica 25: one api, N = 4): median p99 51.524 ms, max 78.173 ms, n_runs 4, over_runs 2, errors 0, budget < 50 ms: over; plain seeded bundle, not the governed path; tree 374a22bf33ad; Intel(R) Xeon(R) CPU @ 2.20GHz; 8 vCPU; lower bound on a non-spec host.
- C, with GBM, explicit-ref, offered 50 rps (per replica 50: one api, N = 4): median p99 50.006 ms, max 50.844 ms, n_runs 2, over_runs 1, errors 0, budget < 50 ms: over; plain seeded bundle, not the governed path; tree 374a22bf33ad; Intel(R) Xeon(R) CPU @ 2.20GHz; 8 vCPU; lower bound on a non-spec host.
- C, with GBM, explicit-ref, offered 100 rps (per replica 100: one api, N = 4): median p99 90.762 ms, max 90.762 ms, n_runs 1, over_runs 1, errors 0, budget < 50 ms: over; plain seeded bundle, not the governed path; tree 374a22bf33ad; Intel(R) Xeon(R) CPU @ 2.20GHz; 8 vCPU; lower bound on a non-spec host.
- C, without GBM, default-live, offered 25 rps (per replica 25: one api, N = 4): median p99 63.659 ms, max 74.627 ms, n_runs 4, over_runs 4, errors 0, budget < 15 ms: over; plain seeded bundle, not the governed path; tree 374a22bf33ad; Intel(R) Xeon(R) CPU @ 2.20GHz; 8 vCPU; lower bound on a non-spec host.
- C, without GBM, explicit-ref, offered 25 rps (per replica 25: one api, N = 4): median p99 44.024 ms, max 48.772 ms, n_runs 4, over_runs 4, errors 0, budget < 15 ms: over; plain seeded bundle, not the governed path; tree 374a22bf33ad; Intel(R) Xeon(R) CPU @ 2.20GHz; 8 vCPU; lower bound on a non-spec host.

Rungs not listed were not reached (the first OVER stops an arm, RL-1755 item 3): 200 rps in every arm; 50 and 100 rps in the default-live arm and in both without-GBM arms. VERDICT OVER means `over_runs` ≥ 1, as the driver prints it (with GBM, explicit-ref, 50 rps: median 50.006 ms, `over_runs` 1 of 2).

25 rps handler mean per run, ms (FD-1836's limb; `C-ladder.log` handler lines): with GBM explicit-ref 32.011, 29.597, 29.052, 29.147; with GBM default-live 38.395, 36.227, 35.683, 34.598; without GBM explicit-ref 27.261, 27.140, 28.455, 30.362; without GBM default-live 37.200, 33.469, 36.878, 34.842.

Load: the quiet bar read 0.48 before the invocation (`C-ladder.log:3`); the driver read load1 1.24 at its own start (`:17`); the without-GBM rungs ran at load1 1.15 to 2.65 (`:72` to `:107`). Log: `~/gi-pricing-plan.local/scratch/nfr-bench-1/s3/C-ladder.log` (`head=374a22bf33ad…` first, `rc=0` last); driver `bench-c-nfr489-ladder.py` sha256 `130dfb174ac3…`, `--rates 25,50,100,200 --runs 4 --workers 4` (`:2`, `:14`); SUMMARY `:111` to `:117`.

### D5.12

Driver `bench-d512-governed-v4.py` sha256 `70de8caead01…`; no-GBM limb only (O-3); no 409; deployments 2xx.

- **D5.12 (NFR-489 exit reading, through `live`, reading of record): n = 1 replica, N = 4 workers per replica (observed 4), at offered rate 100 of target 200 rps, after step-down from 200 (100 per replica); issued 100.03 rps; p99 101.915 ms / 15 ms (no-GBM limb; approved GLM workspace; structure step count not printed by v4); p50 38.321 ms; samples 3000; errors 0 (TALLY 200: 3000); client CPU per second mean 40.5 % max 47.0 %; api CPU mean 263.9 % max 305.4 % (100 = 1 core); load1 3.12 → 3.53: UNMET; tree 374a22bf33ad; Intel(R) Xeon(R) CPU @ 2.20GHz; 8 vCPU; lower bound on a non-spec host.** The run label reads `rate=200 exit` at every `--rate`; the rate is read from ISSUED (`D512-n1-N4-r100.log:119`, `:143` to `:146`).
- D5.12 SCALE CHECK (labelled; not the reading of record, to-lead "2026-11-09 12:07:49 GMT", "2026-11-09 16:37:51 GMT"): n = 2 replicas, N = 2 workers per replica (observed 2 and 2), at offered rate 100 total, 50 per replica, of target 200 per replica; issued 100.03 rps; p99 404.241 ms / 15 ms; p50 49.819 ms; samples 3000; errors 0; client CPU mean 46.3 % max 61.9 %; api CPU mean 144.9 % max 187.7 %; load1 at start 2.43: no-GBM limb unmet; tree 374a22bf33ad; Intel(R) Xeon(R) CPU @ 2.20GHz; 8 vCPU; lower bound on a non-spec host (`D512-n2-N2-r100.log:135`, `:145` to `:148`).
- D5.12 25 rps diagnostic (never the exit reading), offered 25, issued 25.03, 750/750 at 200, n = 1, N = 4: p99 109.514 ms, p50 30.265 ms, client CPU mean 10.3 % max 30.2 %, api CPU mean 71.5 % max 236.9 %, load_start 4.02 (`D512-n1-N4.log:74`, `:84` to `:87`); p99 96.046 ms, p50 31.400 ms, client CPU mean 10.4 % max 38.0 %, api CPU mean 74.3 % max 242.8 %, load_start 4.42 (`D512-n1-N4-r100.log:75`, `:85` to `:88`). n = 2, N = 2: p99 112.355 ms, load_start 3.4 (`D512-n2-N2-r100.log:76`, `:86`). tree 374a22bf33ad; Intel(R) Xeon(R) CPU @ 2.20GHz; 8 vCPU; lower bound on a non-spec host.
- D5.12 step, n = 1, N = 4, `--rate 200`: record; issued 199.46 rps, 6000 calls, TALLY 200: 6000; p50 61861.228 ms, p99 116834.128 ms; client CPU per second mean 99.8 % max 101.6 %; load_start 3.32; the run is **client-bound**: all 6000 calls were issued by t = 31.1 s (`D512-n1-N4.log:117` to `:118`), then issued/s reads 0 and the client stays at about 100 % of a core until t ≈ 125 s (`:207` to `:212`); log `D512-n1-N4.log:213` to `:240`. Step-down stopped at `--rate 100`, which completed with a record; 50 was not needed. `void` false, `void_reasons` empty, in every record. Limitation line, for FD-2105's client-ceiling limb and as an input to P3-A: client-bound at 200 rps on nfr-bench-1 (Intel(R) Xeon(R) CPU @ 2.20GHz, 8 vCPU); the single-process generator is the limit; the spec-host measurement needs a multi-process generator.

**The load caveat of record** (to-lead "2026-11-09 16:27:43 GMT"): the quiet bar was read before the invocation but the driver brings compose up after it, so load_start read 3.1 to 4.4 at each timed run against item C's 0.48; the D5.12 figures are inflated by that and by the live path's extra hop. Item C's 0.48 is its quiet-bar read, and its start load1 read 1.24 with rung loads 1.15 to 2.65 (to-lead "2026-11-09 18:38:40 GMT" (3)). The log's load_start values: n = 1, 4.02, 3.32, 4.42, 3.12; the labelled n = 2 runs, 3.4 and 2.43 (the D5.12 quiet bars read 0.69, 0.49 and 0.42). Item C (S3) still read 44 to 64 ms.
