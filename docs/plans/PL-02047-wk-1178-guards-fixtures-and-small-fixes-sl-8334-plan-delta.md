---
id: PL-2047
family: plan
kind: map
title: WK-1178 — guards, fixtures and small fixes (FD-1488, FD-1507, FD-1509, FD-1749, FD-1228, FD-1662, FD-1493), SL-2048 — a dated Work-plan delta
status: active                   # draft → active → superseded | retired (§1.2a) — L1: draft→active rides the slice's PR
created: 2026-11-06   # original date 2026-11-05, working id 8333, minted 2026-11-06
owner: planner
tree: dae9637ea6f6a56f6502e9db70392cdfb2f3983d
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [FD-1488, FD-1507, FD-1509, FD-1749, FD-1228, FD-1662, FD-1493, PL-1392, FR-11, FR-140, NFR-499]
---

# PL-2047 — WK-1178: guards, fixtures and small fixes (SL-2048, a dated Work-plan delta)

*(Minted 2026-11-06 as PL-2047 from working id 8333, with the slice SL-2048 (working id 8334) and ledger LG-2049 (working id 8335), in the SL-2048 PR.)*

> **For agentic workers:** this is a **dated Work-plan delta** under Lean P2 L1 (a')
> (`.claude/roles/planner.md`, "Lean P2"). It holds one slice row, SL-2048, and edits no filed plan.
> The executor's skills are `superpowers:test-driven-development`, `.claude/skills/python-test`,
> `.claude/skills/fastapi-service`, `dev-commands` and `git-hygiene`. PL-2047, SL-2048 and LG-2049 are
> working ids reserved by the lead.

## Authority

- **The order.** The maintainer's entry "2026-11-05 09:58:58 GMT" in
  `~/gi-pricing-plan.local/channel/to-lead.md`: all FIX rows "coded and merged before Thu 12", "a red
  gate = fix-and-regate within the chain".
- **The ruling, closed, verbatim** (the entry "2026-11-05 09:51:53 GMT"): "(4) FD-1746, FD-1488,
  FD-1748 severities RULED MEDIUM as proposed."
- **FD-1749's requirement,** the maintainer's "2026-10-16 10:30:57 BST", in the essay: "**The fix must
  make a failed `git worktree remove` visible.** … A prune added to the fixture is not enough on its
  own".
- **The brief on FD-1662:** "FD-1662's re-measure with its CARRY fallback"; on FD-1488: "the full suite
  at the re-merged head before the PR".
- **The triage** (`b28ba8e9454c`) §3, Slice H.

## Goal

Each guard fails when it should. A test session on a database behind the head stops once, by name; the
NFR-499 census finds an exception by what it is; the route-type test can see a same-named local class;
a failed worktree removal is loud; the EBM test credits the right requirement; `scripts/demo.py` is type
checked; a malformed token is named as one. Seven findings close.

## Evidence at `dae9637e`

Cites were read at `origin/main` `dae9637ea6f6a56f6502e9db70392cdfb2f3983d`. **Items marked RUN were run
by the planner** on tools-main's venv, read-only (`/tmp/plan-slices/p4.py`; mypy with a cache under
`/tmp`).

**FD-1488.** `backend/tests/conftest_db.py:1203` `database`, function-scoped, an engine per test.
`:1236-1244`: `SELECT count(*) FROM alembic_version`, and `_unavailable` when zero. Nothing compares
revisions. `_unavailable` (`:1190-1193`) fails when configured and skips when not, by FD-1945's rule.
`alembic.ini` is at the repository root. pytest runs serially (`pyproject.toml:198`, no `xdist`).

**The trap the essay does not name.** A database can be **ahead** of the checkout, not only behind: a
slice on an older base runs on a template that main's migration has already reached, and that is
ordinary here. Its `alembic_version` holds a revision the branch's scripts do not know. "Compare `alembic
current` with the script heads" refuses that session too. So the check must separate *behind* (the
revision is in the script directory and is not a head) from *unknown* (it is not). DP-H2.

**FD-1507. The essay's "two" is now six, and its remedy would lose ten.**

- `backend/tests/test_error_sinks.py` `_sinks` (`:248`), the fixed tuple twice, the equality test at
  `:299`, `test_the_census_sees_an_injected_sink` at `:455`. `_GLOBS` (`:37-40`): 167 files.
- **RUN, handlers binding another name** (`str(<name>)` or `{<name>}`, name not in the tuple):

| Site | Name | Form | Read |
|---|---|---|---|
| `rating/runtime.py:822` | `refusal` | `str` | `_model_call_failure(step, str(refusal), context)`: **on the quote path**, the one to read first |
| `platform/deployments.py:525` | `short` | `{}` | a deployment switch's PREPARE message |
| `platform/rating_algorithms.py:154` | `error` | `{}` | a `ValueError` from `consumed_features`, a model artifact |
| `rating/compile.py:854` | `error` | `{}` | the same, at compile |
| `modelling/gbm.py:566` | `error` | `str` | `ObjectiveError`, compile of an objective |
| `modelling/objectives.py:1614` | `failure` | `{}` | a smoke fit's check detail |

- **RUN, the listed name, not bound by a handler:** ten hits, each a **function parameter named `exc`**:
  `api/score.py:531`, `platform/prediction.py:551`, `platform/rate_tables.py:128,135`,
  `platform/rating_algorithms.py:94`, `platform/transformations.py:514`, `rating/score.py:543`,
  `safe_error.py:192,196,204`. **Count only handler-bound names, as the essay's step 1 says, and all ten
  disappear from the census, with the allow-list itself (`safe_error_detail`) among them.** The
  positive control (`:455`) uses parameters too. Annotations will not separate them: `prediction.py:551`
  is `exc: Any`. So the rule is: **bound by an enclosing `except … as`, or a parameter named `exc`.**
  The false positive the essay names (`e` as a band edge) goes, and no listed sink is lost.

**FD-1509.** `backend/tests/test_deployment_route_types.py:135` `openapi_problems`, `:252` `ast_problems`,
`:308-310` builds the real app. Comparing names is the whole check, as the essay says. The app's routes
give the classes: `route.body_field`, `route.response_model`.

**FD-1749.** `tests/test_doc_id_migrate.py:159` `pre_migration_root`, the `finally` at `:189-194`
as the essay reads it: `check=False`, then `shutil.rmtree(tmp, ignore_errors=True)`.

**FD-1228.** `packages/pricing-core/tests/test_ebm.py:431` `@pytest.mark.req("FR-140")` above `:432`
`test_the_fit_is_reproducible_under_the_spec_seed`. FR-140 markers on this file: `:193`, `:223`, `:255`,
`:294`, `:333`, `:391`, `:398`, `:431`, `:448` (nine). `:448`
(`test_fit_seconds_and_library_versions_are_recorded`) the essay "notes and does not decide".

**FD-1662, re-measured (RUN).** `.venv/bin/mypy --config-file pyproject.toml scripts/demo.py` at
`dae9637e`: **still exactly 2 errors**, at `:77` and `:78` (`environ = os.environ if environ is None
else environ`), `Found 2 errors in 1 file`, in a 730-line file. **The triage's worry that it had grown
does not hold: the row stays at 1 h, and the CARRY fallback is not taken.** `pyproject.toml:130-139` is
the `files` list. CI's `mypy` runs that list.

**FD-1493.** `backend/src/app/auth/oidc.py:99-107`, the broad `except Exception` at `:101`.
`uv.lock:2012-2013`: pyjwt 2.15.0, so the applicable row of the essay's table is `DecodeError`, with
the name `RecursionError` kept for the older line. `from jwt.exceptions import InvalidTokenError` is at
`:27`. Test form: `backend/tests/test_auth_oidc.py:70` `_token`.

## Decision points

For the maintainer, on the GO. Each is ruled before its row starts; none blocks the others.

| DP | Question | Options | Recommendation |
|---|---|---|---|
| DP-H1 | FD-1488: what happens to a session behind the head? | (a) **Stop, once, by name:** `pytest.exit` with the revision, the head and the upgrade command. (b) Upgrade a per-worktree database automatically, never the shared one. Saves a step; makes a test run write a schema, and a wrong DSN guess has a large blast radius on this box. | **(a).** A database is a lead-granted thing here, so a fixture must not start migrating. The run stops in a second rather than in 33 minutes. |
| DP-H2 | A revision the branch's scripts do not know (the database is ahead)? | (a) **Pass, and warn once.** Today's behaviour, and any failure stays visible test by test. (b) Stop too. Strict, and stops every slice on an older base that uses a current copy. | **(a).** The finding is about *behind*. (b) would turn an ordinary state into a hard stop days before a freeze. |
| DP-H3 | FD-1507's step 2: widen to `repr(<name>)`, `<name>.args` and a bare name as a logging argument? | (a) **No:** the same name rule on today's two shapes; the essay calls this "a scoping choice" with its evidence. (b) Yes, in this slice, with each new hit's verdict. | **(a), and the auditor files a LOW with an owner.** Six new verdicts are this row's real work; widening adds an unknown number. |
| DP-H4 | FD-1662's rest (`mypy scripts`, 231 errors at `fc4401dc`; `mypy backend/tests`, 1983)? | (a) **Declare:** a dated line in `.claude/skills/repo-architecture` that those two trees are outside the gate, and why. (b) A per-tree baseline that may only shrink: a new tool, in a freeze week. | **(a).** The essay allows either; it makes `CLAUDE.md` §3's claim true at the least cost. |
| DP-H5 | FD-1749: which remedy (either is acceptable)? | (a) **`check=True` in the `finally`, `rmtree` in an inner `finally`.** (b) A local `git clone`, as `scripts/doc-id.py:163-166` chose. Removes the leak; costs a clone per session. | **(a).** Smallest change, and it meets the requirement as ruled. **No prune is added.** |

## Acceptance Standard

Each item is checked by a command a fresh reviewer can run from the repository root on the slice's merge
tree. Items 1 and 2 apply to this plan; A1 to A13 apply to the slice.

1. **This delta passes the docs checks on its branch.** `python3 scripts/audit-docs.py` prints no failing
   line except check 31 / check 32 lines naming working ids 8333, 8334 or 8335. After the mint,
   `audit-docs.py` and `doc-index.py --check` exit 0.
2. **No requirement range.** `grep -nE '(N?FR)-[0-9]+ *(-|to|–) *(N?FR-)?[0-9]+' <this file>` prints no
   line that stands for a set of ids.

The slice:

- **A1. The write set.** `git diff --name-only origin/main...HEAD` lists only the Write set below. The
  only product file is `backend/src/app/auth/oidc.py`, plus `scripts/demo.py`'s annotation.
- **A2. Red first, by cause, per finding.** LG-2049 quotes each of T1 to T9's red from the slice's
  named base, except T5 and T6, which are mutation proofs and quote their break. FD-1662's red is the
  two mypy lines. FD-1228 has no behaviour: its proof is `req-coverage.py` before and after.
- **A3. FD-1488.** T1 (pure) green. **A stamped proof in the DB window:** a `createdb -T` copy, `alembic
  stamp` one revision back, one DB-backed test file: the session stops with the named message, and the
  run takes seconds, quoted. Restamped to head: the same file passes. A revision unknown to the scripts
  behaves as DP-H2 rules.
- **A4. The cost of the check.** The script-directory read happens once a session, and the query
  once a session, not once a test: T2.
- **A5. FD-1507.** `test_every_failure_sink_on_a_quote_input_path_is_accounted_for` passes with `_SINKS`
  gaining the six rows, **each with a verdict read from its raise sites**. `git grep -n '("exc", "e",
  "err")' -- backend/tests/test_error_sinks.py` prints nothing. T3 and T4 hold both directions.
- **A6. A real carrier stops the row.** If a site's text can hold a quote input (NFR-499), the row stops
  and the lead is told. It is not listed with a reason. `runtime.py:822` is read first.
- **A7. FD-1509.** T5: the same-named local class fails the new check; the shipped routes pass; the
  import-kept variant still fails the AST half.
- **A8. FD-1749.** T6: with the removal forced to exit non-zero, the fixture's teardown raises, and
  the temporary directory is still gone. `git diff origin/main...HEAD -- tests/test_doc_id_migrate.py`
  adds no `prune`.
- **A9. FD-1228.** `test_ebm.py:431`'s marker is `FR-11`, and `scripts/req-coverage.py` prints `FR-11` at
  one more file than before. The LG lists each remaining FR-140 marker in the file against FR-140's text,
  for the auditor's own read.
- **A10. FD-1662.** `uv run mypy` rc 0 with `scripts/demo.py` in `files`, and the red shown by removing
  the fix. `.claude/skills/repo-architecture` as DP-H4 rules, its `Verified` line carrying the tree.
- **A11. FD-1493.** T8: a deeply nested token is a `TokenRejectedError` whose reason is `malformed token`,
  and an unknown `kid` keeps `signing key unavailable: …` (T9). The 401 through `authenticate_bearer` is
  unchanged.
- **A12. The GREEN set and the gate: the full suite at the re-merged head before the PR.** FD-1488 changes
  `conftest_db`, which every DB test passes through: the GREEN set is the suite, so **the SOLO full gate
  runs at the re-merged head, after the last re-merge, before the PR opens**, every rc quoted. If `main`
  moves with code after it, the gate is re-run or the lead rules (memory of #1398: a patch-id cover does
  not cover a shared fixture). `skipped` at or below the baseline, by name.
- **A13. FD closing acts, in the FD-1842 form, in the slice's own PR, by the slice's auditor**, for all
  seven: the essay's `status: closed`, `relates:` gaining the slice's ids, a `***Resolved <date>***`
  paragraph naming the delivered remedy, its red and its LG, the same on the register row, and the PR
  number and squash at the merge's date of record. FD-1488's row records the MEDIUM ruling. **The LG Audit
  section, with the lead's adoption, lands in the audit's own commit**, and `docs/INDEX.md` is
  regenerated after the closing acts (common seat brief, item 17).

## Global Constraints

- **G1. The fixture never writes a schema** (DP-H1). It reads `alembic_version` and the script directory.
- **G2. The check runs as the login role.** `database` already reads `alembic_version` that way
  (`:1236`). No owner connection is added.
- **G3. A skip stays a skip only when no database is configured** (FD-1945). The behind-head stop is not
  a skip.
- **G4. No prune, anywhere** (common seat brief, item 35): not in the fixture, and not by hand.
- **G5. Seven findings, one PR, one gate.** R1 to R7 are independent commits, so a row that stops is
  dropped from the PR without touching the others, and is reported.
- **G6. Red first, by cause. No test is removed or weakened** (common seat brief, item 13). A marker's
  move is not a weakening: FD-1228 orders it.

## Needs

- **A DB window, lead-granted in writing,** single-tenant, about 20 min, for A3 only: a `createdb -T` copy
  under the slice's name, **never the template**, `GIP_TEST_DATABASE_URL` and the login URL both at the
  copy, `GIP_REDIS_URL` on `-n 11`, `12` or `13`, never db 0, which is live. `alembic stamp` runs as the
  owner on the copy only. It ends with the two quoted zeros (common seat brief, items 22 and 23).
- **No build window, nothing on the NFR VM.** Everything else is a small run through
  `~/gi-pricing-plan.local/handover/run-small.sh`; `test_doc_id_migrate.py` is not to be run beside a gate
  (its fixture writes into the shared `.git`).

## Tasks

### SL-2048 — guards, fixtures and small fixes

**The row.** Sixth in the 09:58:58 order (R, C, T, A, H, D, F, after WK-674's pair). WK-1178 fix slice.
One `sonnet` executor. Register: the seven, closing at the merge (A13). Depends on: DP-H1 to DP-H5 ruled;
the GO; the DB window; a gate slot. **Size: 10 h** (triage 9.75 h): FD-1488 3, FD-1507 3.5 (six verdicts,
not two), FD-1509 1, FD-1749 0.5, FD-1228 0.5, FD-1662 0.5, FD-1493 1. SOLO gate about 2.5 h, not counted.
**Split point:** FD-1488 is the only row that needs the suite as its GREEN set; the other six can ride
apart. Merged before Thu 12 Nov 2026; still red at Wed 11 Nov 12:00 → the exception list.

**R1 — FD-1488.** New pure helper in `backend/tests/conftest_db.py`:

```python
def migration_problem(current: set[str], heads: set[str], known: set[str]) -> str | None:
    """The refusal for a database behind the script heads, or None (FD-1488). A revision the
    scripts do not know is a database *ahead* of this checkout: DP-H2 (a), a warning, not this."""
    behind = current & (known - heads)
    missing = heads - current
    if behind or (missing and current <= known):
        return (
            f"the test database is at {sorted(current)}, the scripts' heads are {sorted(heads)}: "
            "run `uv run alembic upgrade head` against this database (FD-1488)"
        )
    return None
```

**T1**, new `backend/tests/test_conftest_db_migration.py`,
DB-free, parametrised: `current == heads` → `None`; one behind → a message naming both revisions and
`uv run alembic upgrade head`; an unknown revision → `None`; two heads, one applied → the message. **Red:**
`AttributeError` is not the red, so add the helper returning `None` first and see the behind case fail.
In `database`, after the `applied` check, **once a session** (a module-level flag): read
`SELECT version_num FROM alembic_version`, `ScriptDirectory.from_config(Config(ROOT / "alembic.ini"))`,
and on a message call `pytest.exit(message, returncode=1)`. **T2**, same file: the script directory is
read once across two calls. Then A3's window.

**R2 — FD-1507.** `_sinks` keeps a stack of enclosing `except … as` names and, per function, its parameters
named `exc`. `_is_exception_name(name)` replaces both tuples. `_SINKS` gains the six, keyed as the test's
failure prints them, each with a one-line verdict from reading the raise sites of that exception. **T3,
T4**, added to `test_the_census_sees_an_injected_sink`: `except ValueError as problem: return str(problem)`
is seen; a variable `e = 1; return str(e)` outside a handler is not. A parameter `exc` still is, by the
existing lines. **Red:** T3 at the base, the census misses `problem`. A6 governs.

**R3 — FD-1509.** In `test_deployment_route_types.py`, a check over the live app's routes for each `ROWS`
row: `route.body_field.type_` (or the field's annotation) and `route.response_model`, each
`cls.__module__.startswith("model_schema")`. **T5** on the essay's minimal app, a local same-named
`EnvironmentCreate`. **Red:** by mutation at the base, `openapi_problems` returns `[]`, which the essay's
step 1 quotes.

**R4 — FD-1749.** DP-H5 (a):

```python
    finally:
        try:
            subprocess.run(["git", "worktree", "remove", "--force", str(worktree)],
                           cwd=ROOT, check=True, capture_output=True, text=True)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
```

**T6**: on a throwaway `git init` repository in `tmp_path`, never the real one, the same teardown shape
with a path that is not a worktree raises `CalledProcessError`. Extract the teardown to a small function
so the test calls the code, not a copy. **Never run this beside a gate.**

**R5 — FD-1228.** `test_ebm.py:431`: `FR-11`. A9's list. `req-coverage.py` before and after.

**R6 — FD-1662.** `scripts/demo.py`: the parameter's annotation widened to
`Mapping[str, str] | None`, or a separate local, so both lines pass; add `"scripts/demo.py"` to
`pyproject.toml`'s `files`. DP-H4's line. If mypy now reaches more than two errors through the
wider set, **stop: the CARRY fallback applies** by a dated line, the lead's, and R6 is dropped under G5.

**R7 — FD-1493.** In `oidc.py`'s first `try`, before the broad `except`:

```python
        except (DecodeError, RecursionError) as exc:
            _log.warning("malformed token", extra={"error_type": type(exc).__name__})
            raise TokenRejectedError("malformed token") from exc
```

`from jwt.exceptions import DecodeError, InvalidTokenError`. The broad catch's comment is unchanged. **T7**
a token of random bytes; **T8** a deeply nested payload, signed with the fixture's key, the valid `kid`, in
`test_auth_oidc.py`. **Red:** the reason is `signing key unavailable: DecodeError`. **T9** an unknown
`kid`, control. `test_error_sinks.py` covers the new handler: it logs the type only.

**G — the gate.** A12. After the last re-merge, SOLO, both halves. No migration, no contract regeneration.
CI set from the three-dot diff: `python`, `docs`, `history-policy`. **Shared-fixture risk:** R1 only; a
`pytest.exit` on a stale gate database stops the gate fast, which is the point, and the gate script's
template check is the first thing to read.

### Write set

- `backend/tests/conftest_db.py`, `backend/tests/test_conftest_db_migration.py` (new),
  `backend/tests/test_error_sinks.py`, `backend/tests/test_deployment_route_types.py`,
  `backend/tests/test_auth_oidc.py`, `tests/test_doc_id_migrate.py`,
  `packages/pricing-core/tests/test_ebm.py`.
- `backend/src/app/auth/oidc.py`, `scripts/demo.py`, `pyproject.toml`.
- `.claude/skills/repo-architecture/SKILL.md` (DP-H4).
- LG-2049 under `docs/ledgers/`.
- At the mint: the SL-2048 row in `docs/roadmap.md`, `docs/INDEX.md`, this plan's `status:`, the seven
  essays and `docs/findings/register.md` (A13).

### Files shared with other groups

**A:** A's purge test rests on `conftest_db`: a re-merge. **R:** `test_error_sinks.py` lists `rating/score.py`
`_failing_node`, and PL 8321 keeps it there for this reason; R adds no sink, so no textual collision,
but H must re-derive `_SINKS` after R merges. **LAST-1, LAST-2:** `pyproject.toml` only if they touch it.
**Safe in parallel for building: D, R, C, T, A, F.** Because of A12, **H's gate goes after R's and A's**, or
re-runs.

## Hand-off (not this plan's writes)

- DP-H1 to DP-H5 and the GO: the maintainer. The window and the gate slot: the lead. The row and the mint:
  the lead. The LG: the executor. A13: the auditor.
- **For the lead, on merge:** every seat's DB run will now stop on a stale copy. The gate template's
  and `dev-commands`' "alembic current == heads" line becomes redundant; retiring it is a separate
  record, not this slice's.
- **The two stale `.git/worktrees` entries of FD-1749's evidence** are reported, never pruned.

## Self-review

1. **Every cite was read** at `dae9637e`, and the marked items were run. 2. **Requirements by id**, no
range. 3. **No placeholder.** 4. **Each red is by cause**, and where a finding has no behaviour to redden, A2 says what stands
in. 5. **The triage is corrected:** FD-1662 did not grow; FD-1507 is six sites, and its essay's rule would
drop ten sinks; FD-1488 has an *ahead* case. 6. **The ruling is carried verbatim.** 7. **Calendar:** 12 Nov
2026 is a Thursday, 11 Nov a Wednesday.
