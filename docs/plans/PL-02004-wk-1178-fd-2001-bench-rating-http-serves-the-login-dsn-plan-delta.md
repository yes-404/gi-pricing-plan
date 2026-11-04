---
id: PL-2004
family: plan
kind: map
title: WK-1178 — FD-2001's fix, scripts/bench-rating.py --http serves the application a least-privilege DSN and seeds with the owner DSN (--serve-dsn), SL-2005 — a dated Work-plan delta
status: active                  # draft → active → superseded | retired (§1.2a) — L1: draft→active rides the slice's PR
created: 2026-11-04             # filed under working id 8316
owner: planner
tree: 4daac1586df520b3e8ba12d58a88f12e0ad54034
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1927, FD-2001, FD-1729, SL-1948, LG-1760, FR-44, NFR-489]
---

# PL-2004 — WK-1178: FD-2001's fix. `scripts/bench-rating.py --http` serves the login DSN (SL-2005, a dated Work-plan delta)

> **For agentic workers:** this is a **dated Work-plan delta** under Lean P2 L1 (a')
> (`.claude/roles/planner.md`, "Lean P2"): a new `PL-` that `relates:` WK-1178's plan,
> `PL-1927` (the FD-1729 slices), and leaves it unedited. It holds one slice row, SL-2005. The
> executor's skills are `superpowers:test-driven-development` and `.claude/skills/python-test`.
> PL-2004 and SL-2005 were filed under the working ids 8316 and 8317, reserved by the lead, and
> minted at the SL-2005 mint. The slice's ledger is LG-2006 (filed under working id 8318).

## Authority

- **The finding.** `FD-2001` (LOW, owner WK-1178), `docs/findings/FD-02001-…md`, and its
  register row `docs/findings/register.md:435`. Its *Disposition*: "Open, owner WK-1178, **fix
  before close with an owner**. Fixed before P2 close if a gate slot frees before Tue 10 Nov 2026,
  else carried to P3 with the C' driver as the interim harness … The event that next discharges
  it: the merge of the harness fix, or the P3 plan review if carried."
- **The ruling.** The maintainer's entry "2026-11-04 09:51:05 GMT" in
  `~/gi-pricing-plan.local/channel/to-lead.md`, FINDING 1: "The defect itself —
  `scripts/bench-rating.py --http` refuses main's least-privilege DSN (FD-1729's main.py:114) and
  so cannot drive the platform as shipped — is an FD, LOW, owner WK-1178 … 'fixed before P2 close
  if a gate slot frees before Tue 10, else carried to P3 with the C' driver as the interim
  harness'; bench-rating's own readings before FD-1729 stand as taken."
- **The seating.** The lead's brief `brief-plan-fd2001-2026-11-04.md` (lead 30), and the user's
  order "plz keep the lead work in full speed" relayed in the entry "2026-11-04 16:27:58 GMT".
- **The calendar.** The code freeze is **Tue 10 Nov 2026** (the entry "2026-11-03 15:38:58 GMT",
  as `PL-1991` quotes it). The entry "2026-11-04 10:21:30 GMT" puts SL-1736's full SOLO gate on
  the shared box on **Thu 5** and its mint and PR on **Fri 6**, under the serial rule ("one gate on
  this box"). Weekdays were read with `date -d <d> +%A`.

## Goal

`scripts/bench-rating.py --http` starts the application under test as the least-privilege
login role, so `main.py`'s startup refusal (FR-44, FD-1729) lets it start, and keeps the owner
DSN for the harness's own seeding. The merge discharges FD-2001. No platform code changes.

## Evidence at `4daac158` (read, not run)

The file:line cites below were read at `4daac1586df520b3e8ba12d58a88f12e0ad54034` (origin/main
at 2026-11-04 16:30Z). `git diff --stat db92a7bc 4daac158 -- scripts/bench-rating.py
backend/src/app/main.py backend/src/app/db/immutability.py` is empty, so FD-2001's cites (read
at `db92a7bc`) hold unchanged.

- **The refusal.** `backend/src/app/main.py:114` is `await database.assert_least_privilege()`
  (comment `:111-113`: "a process connected as an owner or a superuser … does not start").
  `LeastPrivilegeError` is defined at `backend/src/app/db/immutability.py:39`.
- **The defect.** `_serve` (`scripts/bench-rating.py:897-933`; FD-2001 calls it
  `_start_server`, `:898-925`) builds the child's env with `"GIP_DATABASE_URL": dsn` (`:918`).
  Its one caller in the script, `_run_http_sweep`, passes `dsn=args.dsn` (`:1316-1319`).
  `--dsn` defaults to `GIP_TEST_DATABASE_URL`, else the compose owner
  `postgresql+asyncpg://gipricing:gipricing@localhost:5432/gipricing` (`:1096-1102`). So the
  server under test always connects as the owner, and FR-44 refuses it; `_await_ready`
  (`:936-948`) then times out after 60 s with "server did not become ready".
- **The owner DSN is right for everything else.** `_seed` (`:715`) inserts the workspace,
  rating version, deployment and service-account rows the route reads; `_measure_fetch`
  (`:838`) builds its own in-process `Database(settings)` (`:868`). Neither starts the
  application, so neither reaches `assert_least_privilege`. Both are called with `dsn=args.dsn`
  (`:1292`, `:1297`, `:1306`).
- **The seam is already proven.** The three accepted scratch drivers
  (`~/gi-pricing-plan.local/scratch/nfr-bench-1/`) call the script's own `_serve` with
  `dsn=args.serve_dsn or args.dsn` and add `--serve-dsn` with the help text "the app login DSN
  uvicorn connects as (FD-1729: the server refuses an owner/superuser); --dsn stays the owner
  DSN used to seed": B `bench-b-pl1665-57.py:328,:372`, C' `bench-c-nfr489-ladder.py:195,:237`,
  D `bench-d-nfr489-mount.py:305,:347`. Their hashes of record are in the entry "2026-11-04
  09:57:14 GMT" (B `c68de47c…` LG-1839, C' `130dfb17…` LG-1760, D `df6e7c9c…` CR 8309), and C'
  ran the real path in a window with that flag ("DRIVER C' ACCEPTED", same entry).
- **The repo's existing names for the login DSN.** The suite reads `GIP_TEST_APP_DATABASE_URL`
  as the application's DSN override (`backend/tests/conftest_db.py:175-192`,
  `test_database_url`). `scripts/demo.py:203-208` gives the app `GIP_DATABASE_URL`, default
  `postgresql+asyncpg://gip_app_login:gip_app_login@localhost:5432/gipricing`, with the comment
  "FD-1729: the application is the login role; migrations and the seed's owner step use the
  owner". CI's app job does the same (`.github/workflows/python.yml:343`).
- **The tests that already bind this script, both DB-free.**
  `backend/tests/test_bench_rating_calls.py` (36 lines: `_fetch_bundle` calls bind to the real
  signature, by AST) and `backend/tests/test_bench_rating_header.py` (85 lines,
  `pytestmark = pytest.mark.req("NFR-489")`; it loads the script with
  `importlib.util.spec_from_file_location` and stops `main()` at `_ctx`). No test reaches
  `_serve` or `_run_http_sweep`.
- **A trap for the new test.** `_run_http_sweep` removes and re-creates
  `Path(__file__).resolve().parent.parent / ".bench-logs"` (`:1273-1276`) before anything else.
  A test that calls it on the script in place deletes the worktree's `.bench-logs/` (ignored,
  `.gitignore:125-126`, but possibly holding a real run's server logs). R1 below avoids it.
- **The CI path filters.** `scripts/**` and `backend/**` are on `.github/workflows/python.yml`'s
  `paths` (`:7-16`), so the full code gate applies (the common seat brief, item 30). The slice's
  LG and roadmap row put `docs/**` in the diff too, so `docs.yml` fires; `history-policy` always
  fires; `frontend.yml` does not.

## Decision points

For the decision-maker; the GO request carries them to the maintainer. Each is ruled before
the slice starts.

| DP | Question | Options | Recommendation |
|---|---|---|---|
| DP-1 | What does `--http` do when no serve DSN is given? | (a) **Fall back to `--dsn`** (the drivers' `args.serve_dsn or args.dsn`, and the brief's "default = today's behaviour"). The run still fails at `_await_ready` after 60 s, with the cause only in the server log. (b) **Refuse at parse time.** `--serve-dsn` defaults to `os.environ.get("GIP_TEST_APP_DATABASE_URL")` (the suite's own name for the app DSN); after `parse_args`, `--http` with no serve DSN calls `parser.error(...)` naming `--serve-dsn`, the env variable and FD-1729. Non-`--http` runs are unchanged. (c) **Derive it** from `--dsn` with the login role's user and password (`conftest_db.py:183-192`'s form), so it works with no flag and always names the same database. | **(b).** After FD-1729 an owner serve DSN can never start, so (a)'s fallback is a guaranteed failure that costs 60 s and hides its cause. (b) fails at once and names the fix; the env default lets the one variable the suite already uses carry it. (c) works with no flag but copies the suite's derivation and password rule into a script, a second copy of a rule that can drift. Thursday's C' invocation passes `--serve-dsn` explicitly, so none of the three changes it. |
| DP-2 | Which DSN does `_measure_fetch` (the in-process `_fetch_bundle` timing, `:1295-1313`) use? | (a) **`--dsn`, the owner, as today.** (b) The serve DSN, so the in-process read runs as the role the server reads as. | **(a).** It never starts the application, so FR-44 does not refuse it, and FD-2001 does not name it. Changing it changes the conditions of a reported figure, and "bench-rating's own readings before FD-1729 stand as taken" (09:51:05). A role-matched fetch reading, if wanted, is its own item. |
| DP-3 | Where does the slice's full gate run? | (a) **Fri 6 Nov 2026 on the shared box**, after SL-1736's Thu 5 gate and in the serial rule's next free slot; **Mon 9 Nov 2026** the fallback; merge before the Tue 10 freeze. (b) Carry FD-2001 to P3 now, with C' as the interim harness, and spend no slot. | **(a).** The code and red-first are DB-free and done Thu 5 beside nothing timed; the gate is one ~2 h SOLO slot. If no slot frees by Mon 9, (b) applies by FD-2001's own disposition and needs no new ruling — the lead records the carry line. |

## Acceptance Standard

Each item is checked by a command a fresh reviewer can run from the repository root on the
slice's merge tree. Items 1 and 2 apply to this plan. Items A1 to A8 apply to the slice.

1. **This delta passes the docs checks on its own branch.** At the branch head,
   `python3 scripts/audit-docs.py` prints no failing line except check 31's lines for the working
   ids PL-2004 and SL-2005, expected until the mint. After the mint, `python3
   scripts/audit-docs.py` and `python3 scripts/doc-index.py --check` exit 0.
2. **No requirement range.** `grep -nE '(N?FR)-[0-9]+ *(-|to|–) *(N?FR-)?[0-9]+' <this file>`
   prints no line that stands for a set of ids.

The slice, SL-2005:

- **A1. The write set.** `git diff --name-only origin/main...HEAD` lists only
  `scripts/bench-rating.py`, the new `backend/tests/test_bench_rating_serve_dsn.py`, the slice's
  `LG-` under `docs/ledgers/`, `docs/INDEX.md`, `docs/roadmap.md` (the SL row), this plan (its
  `status:` only), and FD-2001's essay and `docs/findings/register.md` (A8). Nothing under
  `backend/src/`, `packages/`, `frontend/`, `deploy/` or `docs/specs/`.
- **A2. Red first, by its cause.** The `LG-` holds R1's red lines, run at the base `4daac158`
  (or the slice's base, named): T1 fails with an `AssertionError` whose actual value is the owner
  DSN given to `_serve`; T2 fails with the parser's `unrecognized arguments: --serve-dsn`
  (exit 2). A fixture, import or `NameError` is not the red.
- **A3. Green.** `backend/tests/test_bench_rating_serve_dsn.py` passes at the head:
  `_run_http_sweep` gives `_serve` the serve DSN, and `_seed` and `_measure_fetch` the `--dsn`
  (DP-2 (a)); the parser behaves as DP-1 is ruled.
- **A4. The sibling guards pass unedited.** `test_bench_rating_calls.py` and
  `test_bench_rating_header.py` pass, and `git diff origin/main...HEAD -- backend/tests/`
  touches neither.
- **A5. No worktree side effect.** The new tests never call `_run_http_sweep` on the script in
  place (R1, the `.bench-logs` trap); the `LG-` quotes `ls -la .bench-logs` (or its absence)
  before and after the small run, identical.
- **A6. The GREEN set** is derived by import closure (the common seat brief, item 29), and the
  `LG-` quotes the commands and the list. The script is imported by no module, so the set is
  expected to be the three `test_bench_rating_*` files; any other hit is listed.
- **A7. The full code gate, both halves, SOLO**, green at the re-merged head, every rc quoted
  (`CLAUDE.md` §11; the common seat brief, items 30 and 37). `generate-contracts.py --check`
  and `req-coverage.py` rc 0.
- **A8. FD-2001's closing act.** The auditor sets FD-2001 `status: closed` and marks register
  row `:435` resolved, citing the PR number and the merge commit by sha — the event FD-2001
  names ("the merge of the harness fix"). It rides the slice's mint and closing acts;
  `docs/INDEX.md` is regenerated after it (the common seat brief, item 17).

## Global Constraints

- **No platform code changes.** FR-44's refusal is the platform as shipped and stays exactly as
  it is; the harness adapts to it. A change under `backend/src/` stops the slice.
- **The script stays stdlib-only tooling** (its docstring, RL-872). The fix adds an argparse
  option and threads one value; no new dependency.
- **Owner for seeding, login role for serving.** `_seed` and (DP-2 (a)) `_measure_fetch` keep
  `--dsn`; only `_serve`'s `dsn=` changes, at its one caller.
- **No DB, no server, no network in the tests.** Everything `_run_http_sweep` calls before
  `_serve` is replaced by a recorder; the replaced `_serve` raises a sentinel, so nothing
  starts.
- **Red first, and red by its cause** (`superpowers:test-driven-development`). **No test is
  removed or weakened** (the common seat brief, item 13).
- **Readings already taken stand** (09:51:05). The slice re-takes no reading and edits no
  measurement record.

## Tasks

### SL-2005 — FD-2001's fix: `scripts/bench-rating.py --http` serves the login DSN

**The row.** Order 1 in this delta. A WK-1178 fix slice after `PL-1927`'s FD-1729 slices
(`SL-1942`, `SL-1948`), whose startup refusal it adapts to.

- **Scope:** R1, R2 and G below.
- **Requirements:** NFR-489 (`03` §9; the harness measures it, and the new test carries its
  marker as `test_bench_rating_header.py` does); FR-44 (`01` §3; read only — the refusal the
  harness now honours).
- **Register:** FD-2001 (LOW, owner WK-1178) closes at the merge (A8).
- **Depends on:** DP-1 to DP-3 ruled; the maintainer's GO on this row.
- **Size:** 1, with one `sonnet` executor (the executor charter's model line governs).
- **Schedule:**
  - **Thu 5 Nov 2026** — R1 and R2, DB-free, small runs only through
    `~/gi-pricing-plan.local/handover/run-small.sh`, never beside a timed stage of SL-1736's
    gate (the common seat brief, item 32; the 10:21:30 serial rule).
  - **Fri 6 Nov 2026** — G, the full SOLO gate on the shared box in the next free slot after
    SL-1736's; the mint, the PR and the ACK at green. **Mon 9 Nov 2026** is the fallback slot.
  - **Merged before the Tue 10 Nov 2026 code freeze.**
  - **Fallback:** no slot by Mon 9 → FD-2001 is carried to P3 by its own disposition, C'
    (`bench-c-nfr489-ladder.py`, sha256 `130dfb17…`, LG-1760) the interim harness, discharge
    event the P3 plan review; the lead records the carry line and the branch is kept, not
    merged.

**R1 — red first, at the base, with no database.**

New file `backend/tests/test_bench_rating_serve_dsn.py`, `pytestmark =
pytest.mark.req("NFR-489")`.

1. **Load a copy, not the script in place.** A fixture copies `scripts/bench-rating.py` to
   `tmp_path / "scripts" / "bench-rating.py"` and loads it with
   `importlib.util.spec_from_file_location`, registering it in `sys.modules` by
   `monkeypatch.setitem` (the `@dataclass` reason given in `test_bench_rating_header.py`). Then
   `_run_http_sweep`'s `.bench-logs` resolves under `tmp_path`, never the worktree (the trap
   above). The script's `sys.path` insert of `packages/` points into `tmp_path` and is harmless:
   the workspace packages are already importable from the venv.
2. **T1 `test_http_sweep_serves_the_login_dsn_and_seeds_with_the_owner_dsn`.** Build
   `argparse.Namespace(rates="25", rung_seconds=1, port=8099, dsn=OWNER, serve_dsn=LOGIN,
   bucket="b", workers=1, expr_steps=1, rounds=1, rows=1, speedup=2.1)` with two distinct
   sentinel DSN strings. Replace on the loaded module, each as an `async def` because the sweep calls them through
   `asyncio.run`: `_serialisable` (returns a sentinel), `_seed` (records its `dsn`, returns
   `("ws", "key")`), `_measure_fetch` (records its `dsn`, returns a stub `Measurement`); and,
   plain: `_report` (no-op), and `_serve` (records its `dsn`, then
   raises a sentinel exception). Call `_run_http_sweep(args)` under
   `pytest.raises(<sentinel>)`. Assert `_serve` got `LOGIN`, and `_seed` and every
   `_measure_fetch` call got `OWNER`.
   **The red, by its cause:** at the base `_serve` gets `dsn=args.dsn`, so the assert fails with
   the actual value `OWNER`. (The `finally:` that signals the process is not reached, because
   `_serve` raises before `proc` is bound, and the `try` opens after it.)
3. **T2 `test_serve_dsn_option_parses`.** Run `main()` with `monkeypatch.setattr(sys, "argv",
   [..., "--http", "--dsn", OWNER, "--serve-dsn", LOGIN])` and wrap
   `argparse.ArgumentParser.parse_args` (monkeypatched) to record the namespace and then raise a
   sentinel, so nothing after parsing runs. Assert `serve_dsn == LOGIN` and `dsn == OWNER`.
   **The red, by its cause:** at the base argparse exits 2 with `unrecognized arguments:
   --serve-dsn LOGIN`.
4. **T3 — DP-1's default, as ruled.** If (b): with `GIP_TEST_APP_DATABASE_URL` set and no flag,
   the namespace's `serve_dsn` is that value; with neither, `--http` exits 2 and the message names
   `--serve-dsn` (assert on `capsys`); without `--http` and with neither, parsing succeeds
   (non-`--http` runs unchanged). If (a): with neither, `_run_http_sweep` gives `_serve` the
   `--dsn`. If (c): with neither, `_serve` gets `--dsn` with the login role's user and password
   and the same host, port and database.
5. Run through `~/gi-pricing-plan.local/handover/run-small.sh` as one file. The `LG-` quotes
   each red's assert line or the argparse line, and the rc.

**R2 — green.**

- `main()`'s parser gains `--serve-dsn`, beside `--dsn`, with DP-1's default and help text
  naming FD-1729 and the login role (the drivers' wording is the model).
- DP-1 (b): after `parse_args`, `if args.http and not args.serve_dsn: parser.error(...)`.
- `_run_http_sweep`'s one `_serve(` call passes `dsn=args.serve_dsn` (or DP-1's resolved
  value). `_seed` and `_measure_fetch` calls are unchanged.
- `_serve`'s docstring gains one line: its `dsn` is the application's login DSN, never the
  owner's (FR-44, FD-1729).
- The module docstring's usage block gains the `--http` form with `--serve-dsn`.
- Nothing else in the script changes. `uv run ruff check .` and `ruff format --check` on the two
  changed files, rc quoted (the common seat brief, item 16).

**G — the gate.**

- The diff leaves `docs/` (`scripts/**`, `backend/**`), so the full code gate runs, both halves,
  SOLO in a gate slot (`CLAUDE.md` §11; the common seat brief, item 30). It never runs beside
  another gate or a timed stage (the 10:21:30 serial rule).
- The CI that fires: `python.yml`, `docs.yml` and `history-policy`. `frontend.yml` does not.
- No contract regeneration; no migration; no DB window is needed by the slice's own tests.

### Write set

- `scripts/bench-rating.py`: the parser (in `main`, `:1057`; `--dsn` at `:1096-1102`), the one `_serve(` call in
  `_run_http_sweep` (`:1316-1319`), `_serve`'s docstring (`:900-910`), and the module docstring.
- `backend/tests/test_bench_rating_serve_dsn.py`: new.
- The slice's `LG-` under `docs/ledgers/`.
- At the mint: the SL-2005 row under `### WK-1178` in `docs/roadmap.md`, `docs/INDEX.md`, the
  `status:` of this plan, and the FD-2001 closing act (A8).

## Hand-off (not this plan's writes)

- The rulings on DP-1 to DP-3 belong to the decision-maker; the GO on the row to the maintainer.
- The SL-2005 roadmap row, the `LG-` id and the mint belong to the lead; the `LG-` to the
  executor; FD-2001's closing act to the auditor; a P3 carry line (the fallback) to the lead.
- `PL-1927` is not edited.

## Self-review

1. **Every cite was read** at `4daac158`, and the channel entries in `to-lead.md`. The FD's
   own cites were checked unchanged since `db92a7bc` by an empty `git diff --stat`.
2. **Every requirement is named by id**: NFR-489 and FR-44; no range.
3. **No placeholders** except DP-1's ruled branch, which T3 states for each option.
4. **The red is by cause.** T1's red is the wrong DSN reaching `_serve`; T2's is the missing
   option. Both are DB-free, and the `.bench-logs` trap is closed by loading a copy.
5. **The calendar is stated once** and agrees with the channel: work Thu 5, gate Fri 6, Mon 9
   fallback, freeze Tue 10, P3 carry with C' if no slot.
