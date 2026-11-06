---
id: LG-2049
family: ledger
title: WK-1178 slice SL-2048 — guards, fixtures and small fixes (FD-1488, FD-1507, FD-1509, FD-1749, FD-1228, FD-1662, FD-1493) (slice ledger)
status: closed                 # active → closed (§1.2a)
created: 2026-11-06   # original date 2026-11-05, working id 8335, minted 2026-11-06
owner: executor
tree: ec4c4240c6c20d3b75490a9cdeb9a88fe05efab4   # sl-8334-h-guards, the code head this was written against (base e8a597700687aff394e13da0035f10d2419ce893)
slice: SL-2048
phase: P2
work: WK-1178
plans: [PL-2047]
corrected_by: []
relates: [FD-1488, FD-1507, FD-1509, FD-1749, FD-1228, FD-1662, FD-1493, PL-2047, FR-11, FR-140, NFR-499]
---

# LG-2049 — WK-1178 slice SL-2048: guards, fixtures and small fixes

*(Minted 2026-11-06 as LG-2049 from working id 8335, with the plan PL-2047 (working id 8333) and the slice SL-2048 (working id 8334), in the SL-2048 PR.)*

**GO:** to-lead "2026-11-05 10:31:31 GMT" (plans C and H accepted; DP-H1 to DP-H5 ruled: stop by name with no auto-upgrade; a database ahead of the branch passes with a warning; no widening of sink shapes; the rest declared outside mypy; `check=True`, no prune; FD-1507's rule is handler-bound or a parameter named `exc`; FD-1662 re-measured at 2 errors, no carry), on the order of "2026-11-05 09:58:58 GMT".
**MERGE-ACK:** (added at merge.)

## Tasks

### Scope

PL-2047 (a dated Work-plan delta), "SL-2048 — guards, fixtures and small fixes". Seven findings, seven independent commits pairs (G5): FD-1488 (R1), FD-1507 (R2), FD-1509 (R3), FD-1749 (R4), FD-1228 (R5), FD-1662 (R6), FD-1493 (R7). Requirements touched: NFR-499 (the census and the oidc handler), FR-11 and FR-140 (R5), FR-428 (R3's tests keep their markers). Write set as the plan states; the only product files are `backend/src/app/auth/oidc.py` and `scripts/demo.py`'s annotation.

### Task list

1. **R1, FD-1488** — red `b96ea7da` (stub `migration_problem` returns `None`), green `970d4b62`: `backend/tests/conftest_db.py` (`migration_problem`, `_script_revisions` cached once, `_check_migrations_once`, a once-a-session flag in `database`), new `backend/tests/test_conftest_db_migration.py` (T1 four cases, T2 read-once, plus the exit/warn behaviour). A3's stamped proof: see Build log (owed until the DB window).
2. **R2, FD-1507** — red `2636dd39`, green `d849da2a`: `_sinks` keeps a set of enclosing `except … as` names and a parameter named `exc`; `_SINKS` gains six rows (A5, A6 below).
3. **R3, FD-1509** — red `846e71b0`, green `c896d015`: `route_class_problems` over the live app's routes (`body_field`, `response_model`; a `Page[Item]` through `__pydantic_generic_metadata__`), T5 on a minimal app with a local same-named class.
4. **R4, FD-1749** — red `626cb503`, green `3e1fc07b`: teardown extracted to `_remove_worktree`, `check=True`, `rmtree` in an inner `finally`; T6 on a throwaway `git init` repo.
5. **R5, FD-1228** — `b1140b0f`: `test_ebm.py` seed-reproducibility marker `FR-140` to `FR-11`.
6. **R6, FD-1662** — `48b745f6` (code), `8f3f537b` (DP-H4's line in `.claude/skills/repo-architecture/SKILL.md`): `check_environment` takes a `Mapping`; `scripts/demo.py` added to `pyproject.toml`'s `files`.
7. **R7, FD-1493** — red `aec3f2ea`, green `ec4c4240`: `except (DecodeError, RecursionError)` before the broad catch in `oidc.py`; T7 random bytes, T8 a signed 50 000-deep payload under the valid `kid`, T9 unknown `kid` control.

### Gate

Not run by the executor: the SOLO full gate at the re-merged head, after R's and A's (A12), is the lead's. Owed. Small runs below ran on the executor's own tree (`sl-8334`), `run-small.sh`, one file per call, dead-port DB and redis URLs, load1 under 6 at each start.

| Run (file) | rc | Summary line |
|---|---|---|
| `backend/tests/test_conftest_db_migration.py` | 0 | `6 passed, 3 warnings in 0.16s` |
| `backend/tests/test_error_sinks.py` | 1 | `9 passed, 2 warnings, 4 errors in 13.01s` — the 4 errors are DB-backed tests on the dead port (`ConnectionRefusedError`); not the census |
| `backend/tests/test_deployment_route_types.py` | 1 | `19 passed, 2 warnings, 1 error in 9.14s` — the error is `test_the_two_changed_approval_routes_return_exactly_the_declared_keys` (DB-backed), dead port |
| `tests/test_doc_id_migrate.py` | 0 | `306 passed in 153.69s (0:02:33)` (no gate slot held at the time) |
| `backend/tests/test_auth_oidc.py` | 0 | `13 passed, 2 warnings in 0.95s` |
| `test_error_sinks.py` + `packages/pricing-core/tests/test_quote_input_raise_sites.py` (ONE call, two files: a breach of the brief's one-file-per-call rule, reported to the lead; both files DB-free apart from the same 4 dead-port errors) | 1 | `28 passed, 2 warnings, 4 errors in 18.43s` |

`uv run mypy`: rc 0, `Success: no issues found in 253 source files`. `ruff check` on every touched Python file: rc 0 (`conftest_db.py`, `test_error_sinks.py`, `test_deployment_route_types.py` were already unformatted at the base; format was not applied to them).

### Audit

*Draft by aud-slh (auditor seat), 2026-11-05 16:51 GMT, for the lead's adoption; lands in the audit's own commit. Proposals only: the verdicts are the lead's (`delivery-process.md` §5). Range `origin/main...ca63dd15ede5f8c550964dcb759035784807abb3` (tree `ed71e53b0b7e4b3b08418dc49437ffba70356bfa`); every run below ran on that head in the auditor's own detached worktree `aud-slh`, and each log's first line is `head=SHA`, last line `rc=N` (logs under `~/gi-pricing-plan.local/scratch/aud-slh/`, local files, cited by name).*

**Scope, derived first.** From PL-2047 (read whole at `e8a59770`, byte-identical to the plan in range: `git diff --quiet e8a59770 HEAD -- docs/plans/PL-02047-*` rc 0) the scope is A1 to A13 and the seven essays' own remedies and discharge events (the essay of FD-1488, FD-1507, FD-1509, FD-1749, FD-1228, FD-1662, FD-1493), read to the clause that carries the claim. `scripts/scope-audit.py` was not run: it takes a module spec, and this slice implements no spec requirement; it moves a marker (FR-11), keeps markers (FR-428, NFR-499) and changes tests, so the requirement axis is `req-coverage.py` (below).

**Ledger two-way match.** Each of the seven task rows has its commit(s) in the Task list and its red/green in the Build log; every SHA the LG names (`b96ea7da 970d4b62 2636dd39 d849da2a 846e71b0 c896d015 626cb503 3e1fc07b b1140b0f 48b745f6 8f3f537b aec3f2ea ec4c4240`, and the plan's `e8a59770`) satisfies `git merge-base --is-ancestor SHA HEAD` rc 0. Each red commit touches tests only (`git show --stat`), so it was a red on its own.

#### Per-item verdicts (proposed)

| Item | Proposed verdict | Evidence read to the assert |
|---|---|---|
| A1 write set | **MET** | `git diff --name-only origin/main...HEAD` lists 14 paths, all in the Write set; the only product files are `backend/src/app/auth/oidc.py` and `scripts/demo.py`. PL-2047 and its INDEX row are in range because the branch carries `e8a59770`. The roadmap row, the seven essays and the register are the mint's (Write set, "At the mint"). |
| A2 red first, by cause | **MET-BY-RECORD**, three gaps named | Reds are in the Build log with their assert text (R1 `assert None is not None` at `test_conftest_db_migration.py:22,:35`; R2 `{} == {('renamed.py…'): 1}`; R3, R4 mutation proofs; R6 the two mypy lines; R7 `'signing key …: DecodeError' == 'malformed token'`). Gaps: **T2** (read once) and the wired stop in T-stop have no recorded red; the auditor supplied them (mutations 3 and 4 below). R6's two mypy lines are the executor's, not re-run (`mypy` over the repository is the gate's). |
| A3 FD-1488 stamped proof | **MET-BY-RECORD** (DB window) | The LG's window (START 11:01:49, END 11:06:48 GMT) quotes: one revision back → `Exit: the test database is at ['9b3e7c15d4a2'], the scripts' heads are ['b7e4c2a91d36']: run \`uv run alembic upgrade head\`…` rc 1; restamped → `2 passed`; unknown revision → `UserWarning … ahead of this checkout … (DP-H2)`, `2 passed`; both zeros at END. **Not re-run by the auditor: no DB (brief ban); OWED, not guessed.** The DB-free half re-ran: `test_conftest_db_migration.py` `6 passed, 3 warnings in 0.31s`, rc 0. |
| A4 cost once a session | **MET** | `_script_revisions` is `functools.cache`d and `_migrations_checked` gates the query once per process (`conftest_db.py`, `database`). T2 asserts `len(reads) == 1`. Mutation 3 (the `@functools.cache` line removed) → `1 failed, 5 passed` (`test_the_script_directory_is_read_once_across_two_calls`). |
| A5 FD-1507 | **MET** | `git grep -n '("exc", "e", "err")' -- backend/tests/test_error_sinks.py` rc 1, prints nothing. `_sinks` binds by enclosing `ExceptHandler.name`, or a parameter named `exc`. Six `_SINKS` rows added, each with a verdict. `test_error_sinks.py`: `9 passed, 2 warnings, 4 errors`; the 4 errors are the DB-backed tests (`RuntimeError: GIP_TEST_DATABASE_URL is not set…`, refused before any connection), the same 9/4 as the LG. The equality test and the injected-sink test (T3, T4) are among the 9. |
| A6 a real carrier stops the row | **MET** | Read at the raise sites. `runtime.py`: `_ModelCallRefusal` has one raise (`:660`), its text `model_call step {step.step_id!r} pins a {model_type!r} model, which no scorer is written for (FR-222).`, the step id authored in the graph and the model type from the stored fit result; no quote value. `deployments.py:520`: `SwitchIncompleteError(acknowledged, unacknowledged, receivers)` from `deployment_switch.py:315`, process ids. The other four are as the LG describes. No site holds a quote input. |
| A7 FD-1509 | **MET** | `route_class_problems` over the live routes (`body_field.field_info.annotation`, `response_model`, `Page[Item]` through `__pydantic_generic_metadata__`). `test_deployment_route_types.py`: `19 passed, 2 warnings, 1 error`; the 1 error is the DB-backed `test_the_two_changed_approval_routes_return_exactly_the_declared_keys`. The shipped-routes test and the same-named-local-class test (T5) are among the 19. The LG's A7 reading (the import-kept variant is caught by the live check, not the AST half) matches the essay's own step 2. |
| A8 FD-1749 | **MET** | `_remove_worktree` runs `check=True` with `rmtree` in an inner `finally`; `pre_migration_root` calls it. `git diff … -- tests/test_doc_id_migrate.py \| grep -ci prune` prints `0`. T6 on a throwaway `git init` repo: `1 passed, 305 deselected` rc 0, run by `-k` so the session fixture (which writes the shared `.git`) never ran. Mutation 1 (`check=True` → `False`) → `Failed: DID NOT RAISE CalledProcessError`, `1 failed`. The 306-test file was **not** re-run: its fixture writes the shared `.git` and a gate runs now. No stale `.git/worktrees` registration exists today (each `gitdir` target tested, read-only; nothing pruned). |
| A9 FD-1228 | **MET** | `req-coverage.py` at HEAD: `FR-11 2 test file(s)`, `FR-140 35 test file(s)`, rc 0 (log `reqcov.log`). Before: `git grep -l 'req("FR-11")' origin/main -- '*.py'` = 1 file; at HEAD 2. The remaining FR-140 markers read against FR-140's text ("term shape functions exported directly as tables, no approximation, still carrying the fidelity/diagnostic sections"): `:193`, `:223`, `:255`, `:294`, `:333` give that evidence; **`:391` and `:398` (monotone constraints refused by name) and `:448` (fit seconds and library versions recorded) do not**: they test `EBM_MONOTONE_CONSTRAINT_INCOMPLETE` (`02-modelling.md`, the 2026-08-21 WK-661 note, not FR-140's text; FR-122 is the monotone-constraint requirement) and a provenance record. The essay noted `:448` and left it; `:391`/`:398` are newly read. See proposal P3. |
| A10 FD-1662 | **MET-BY-RECORD** | `pyproject.toml` `files` gains `"scripts/demo.py"`; `check_environment(environ: Mapping[str, str] \| None)` with a local `env`; the callers pass dicts (`test_demo_command.py:37,:45`). `test_demo_command.py`: `33 passed, 2 warnings, 2 errors`, the 2 errors the DB-backed `test_the_seed_record_pre_flight_*` (same `RuntimeError`). The skill's Verified tree `b4f4f7e24efeea0ebfc84282fe8e94c88492a943` is `48b745f6^{tree}`, the parent of `8f3f537b` (the commit before that line). `uv run mypy` rc 0 over 253 files and the two-line red are the executor's; the gate's `mypy` stage is decisive. The 231/1983 counts are the triage's at `fc4401dc` (a commit; `git cat-file -t` = `commit`), quoted as such by the skill, each command run as named. |
| A11 FD-1493 | **MET** | `test_auth_oidc.py`: `13 passed, 2 warnings in 1.05s`, rc 0 (T7, T8, T9 among them). Mutation 2 (the new `except` retargeted) → T7 and T8 fail, `2 failed, 11 passed`; T9 (unknown `kid`) still passes as the control. pyjwt is 2.15.0 in this tree: `PyJWKClientError` is a `PyJWTError`, not a `DecodeError`, so key-resolution failures still reach the broad catch. The new handler logs the type only (`error_type`), reuses the file's own `extra` key, and adds no sink row. The 401 is unchanged: the reason still never reaches the caller (`test_rejection_reasons_are_not_returned_to_the_caller`, in the 13). The `RecursionError` arm is not exercised on pyjwt 2.15.0 (T8 raises `DecodeError` there; `jwt/api_jwt.py:299` converts it); it is kept for the older line, as the plan says. |
| A12 GREEN set and the gate | **OWED-TO-GATE** | See "What the gate must prove". |
| A13 closing acts | **proposed** | Seven acts in the FD-1842 form, written in the seven essays and the register (this commit); the PR number, squash and merge date are written at the merge's date-of-record. |

**Plan acceptance items 1 and 2.** (2) `git grep -cE '(N?FR)-[0-9]+ *(-|to|–) *(N?FR-)?[0-9]+' HEAD -- the plan file` prints no match (rc 1): MET. (1) `audit-docs.py` on this head (`auditdocs.log`, via run-heavy `--light`): rc 1, `FAILED (4)`: check 31 (allocation gap, working ids 8333 to 8335, as the item allows), check 32 twice (`LG-2049 does not resolve in docs/INDEX.md`), **check 39 (`docs/INDEX.md is stale against a fresh regeneration`)**. Item 1 allows only check 31/32 lines; check 39 is the same root as check 32: the LG's row is missing from `docs/INDEX.md`. `doc-index.py` regenerated the file in the auditor's worktree and changed exactly one line (`+| LG-2049 | ledger | … | active | executor | P2 |`); the change was reverted, not committed. **Proposal P1:** the audit's commit regenerates INDEX after the closing acts (seat brief item 17) and runs `doc-index.py --check`.

**NFRs measured, not asserted.** NFR-499 (the census): the guard is the equality test over the 167-file glob; `9 passed` here, and the six new rows are the only delta the LG's `_census()` run reports (the equality test would fail on any other difference, and passes). No NFR timing is claimed by the slice. The "stops in seconds" property of FD-1488 is the executor's 25 s `Exit` run (A3), not re-measured.

**Enforcement proved on broken input (the auditor's own, on the head, restored after each; `git status --short` empty).**

| Mutation (single edit, asserted once) | File run | Result |
|---|---|---|
| 1. `_remove_worktree`: `check=True` → `check=False` | `tests/test_doc_id_migrate.py -k a_failed_worktree_removal_is_loud` | `1 failed` — `DID NOT RAISE CalledProcessError`, rc 1 |
| 2. `oidc.py`: `except (DecodeError, RecursionError)` → `except ZeroDivisionError` | `backend/tests/test_auth_oidc.py` | `2 failed, 11 passed` (T7, T8), rc 1 |
| 3. `conftest_db.py`: `@functools.cache` removed | `backend/tests/test_conftest_db_migration.py` | `1 failed, 5 passed` (T2), rc 1 |
| 4. `conftest_db.py`: `pytest.exit(problem, returncode=1)` → `pass` | `backend/tests/test_conftest_db_migration.py` | `1 failed, 5 passed` (the stop test), rc 1 |

Not mutated by the auditor (the executor's reds stand): R2's census rule, R3's class check.

**Re-runs.** All DB-free, one file per call, through `run-heavy.sh --over-load "2026-11-05 15:37:39 GMT"` (non-timed work), **beside D's pytest in `sl-1689d` under `gate-1`, within the cap** (load1 8 to 17 at the starts); no DB, redis or docker touched; `GIP_*` URLs unset for each run. `uv sync --directory the worktree --all-packages --frozen` rc 0 first.

| File (head `ca63dd15`) | rc | Summary line |
|---|---|---|
| `backend/tests/test_conftest_db_migration.py` | 0 | `6 passed, 3 warnings in 0.31s` |
| `backend/tests/test_error_sinks.py` | 1 | `9 passed, 2 warnings, 4 errors in 3.80s` — 4 errors, DB fixture refused (`RuntimeError`) |
| `backend/tests/test_deployment_route_types.py` | 1 | `19 passed, 2 warnings, 1 error in 8.20s` — 1 error, DB fixture |
| `backend/tests/test_auth_oidc.py` | 0 | `13 passed, 2 warnings in 1.05s` |
| `backend/tests/test_demo_command.py` | 1 | `33 passed, 2 warnings, 2 errors in 4.31s` — 2 errors, DB fixture |
| `tests/test_doc_id_migrate.py -k a_failed_worktree_removal_is_loud` | 0 | `1 passed, 305 deselected in 2.62s` |
| `tests/test_repository_invariants.py` | 1 | `2 failed, 9 passed in 234.36s` — `test_money_discipline_is_enforced_by_the_docs_audit` and `test_journey_citations_are_audited_in_ci`: both are in the item-31 docs-audit set and run `audit-docs.py`, which fails here on the unminted working ids and the missing INDEX row (checks 31, 32, 39 above). Classified, not cleared: re-run after the mint and the regenerated INDEX (P1). |

#### What the gate must prove (FD-1488 changes what every DB test connects through)

`conftest_db.py` is imported by 81 test files directly and its `database` fixture serves every DB-backed test, so the GREEN set by import closure (seat brief item 29) is the suite: `git grep -l conftest_db -- 'backend/tests/*.py' 'tests/*.py' 'packages/*/tests/*.py'` names it in 81 files at this head, plus every file using the fixture through `backend/tests/conftest.py`. The `oidc.py` closure is `deps.py`, `service.py`, `main.py` (and so every `create_app` test) and six test files (`test_auth_failure_identity`, `test_auth_users`, `test_management_rate_limit`, `test_workspace_identity`, `test_workspace_members`, `test_workspace_selection`), none of them run by the auditor (DB-backed). The `scripts/demo.py` closure is its nine importing/loading test files and the generators that load it by path. The SOLO full gate at the re-merged head (A12) is the decisive green. It must show:

1. **No `pytest.exit` fired**: the run completes, so the gate database's `alembic_version` equals the scripts' heads at the re-merged tree. A stop here is the check working, not a slice defect: read the gate script's template check (`alembic_version=1 environments=3 tenant_marker=1`) against the new head first. If main gained a migration after the template was built, the gate stops by design in seconds.
2. **`skipped` at or below the baseline (22 on the last three gates), by name.** The new check sits behind `applied`, so a configured-but-empty database still fails or skips through `_unavailable` as before (G3).
3. **No new warning turned into a failure**: `pyproject.toml` has no `filterwarnings`, so the DP-H2 `UserWarning` ("ahead of this checkout") is only a warning; its presence on the gate DB would mean the template is ahead of the branch, to be named at the ACK.
4. **`test_conftest_db_migration.py` shows 6 passed**, and the pass count rises by the slice's new test functions, none removed (`git diff` shows no deleted test): 6 migration (new file), 3 `oidc` (13 now, 10 before), 2 route-type, 1 doc-id; the sink census's T3 and T4 extend an existing test.
5. **The four `test_error_sinks.py` and one `test_deployment_route_types.py` DB-backed tests pass** (they errored here for want of a database, not for the slice).
6. The failures, if any, are exactly the item-31 docs-audit set, and `audit-docs.py` fails only checks 31/32 on the slice's own working ids **after the INDEX is regenerated** (P1); a check 39 at the gate is the open item above.
7. `mypy` rc 0 over the 253-file set including `scripts/demo.py` (A10), and `ruff check .` rc 0 (item 16).

#### Verdicts on requirements and findings without evidence at this head

None of the seven is without an owner or a verdict. Open: **A3's DB half** (delivered, evidenced by the executor's quoted window, not re-run by the auditor) and **A12** (owed to the gate). No requirement is verdict-less: FR-11 gains evidence, FR-140's mis-tags are P3, NFR-499's guard is strengthened and its widening is P2.

#### Proposals for the lead

- **P1. INDEX.** Regenerate `docs/INDEX.md` in the audit's commit after the closing acts and run `doc-index.py --check` (rc quoted); today `LG-2049` is missing, which is checks 32 and 39.
- **P2. DP-H3 LOW (the plan says the auditor files it).** The census still does not see `repr(NAME)`, `NAME.args` or a bare handler-bound name as a logging argument; the essay's own step 4 shows `_log.warning("failed: %s", exc)` and `return repr(exc)` pass. Filed as `FD-2029` (working id 8384, minted in docs batch 12); owner WK-1178, LOW (a product defect is always an `FD-`; proposed owner WK-1178's tail or WK-673's next toucher of `test_error_sinks.py`, severity LOW).
- **P3. Residual FR-140 mis-tags, LOW.** `test_ebm.py` `:391` and `:398` (and `:448`, which FD-1228 noted) are tagged FR-140 and give it no evidence. Filed as `FD-2030` (working id 8385, minted in docs batch 12); owner WK-1178, test-only. This slice moves one marker only (FD-1228, `test_the_fit_is_reproducible_under_the_spec_seed`); the three tests FD-2030 records (`:391`, `:398`, `:448`) are untouched, so FD-2030 stays open. 
- **P4. FD-1507's severity.** Its row reads "MEDIUM, proposed; … the maintainer's to confirm at the mint". The ruling "(4) FD-1746, FD-1488, FD-1748 … MEDIUM" (to-lead "2026-11-05 09:51:53 GMT") does not name FD-1507, and the auditor found no other confirmation. The closing act records MEDIUM as the row states it, without claiming a confirmation; the lead may supply the line.
- **P5. PL-2047 `status: draft → active`** and the SL-2048 roadmap row ride the mint (Write set); neither is in the range. Not an audit defect.
- **P6. Process, backlog not FD.** The executor's one two-file `run-small` call (reported to the lead) and the auditor's two `cd /dev/null` attempts (both failed on "Not a directory", the shell's cwd unchanged, no other command was affected) are breaches of the NO-CD and one-file rules, reported for the record.

#### Proposed disposition

**Audit: CLEAN for the code, with P1 to fix in this commit and A3 (DB half) and A12 (the gate) owed.** Not NOT MET on any item. The lead adopts, amends or rejects.

#### Adoption, and A3's DB half and A12 from the gate

**Adopted.** The lead adopted this audit (`from-lead-2026-10-09.md`, "2026-11-05 16:51:59 GMT", aud-slh FINAL ADOPTED): H at `ca63dd15`, nothing NOT MET; A3's DB half and A12 owed to the gate; P1 (INDEX regeneration) at the audit commit. P2 and P3 were filed as FD-2029 and FD-2030 (working ids 8384 and 8385, docs batch 12), so this commit mints no FD. P4: FD-1507's closing paragraph records MEDIUM as its row states it, with no confirming ruling claimed. P5 rode the mint (PL-2047 `active`, the SL-2048 row). P6 is process-backlog, not an FD.

**The gate.** The SOLO gate ran at the re-merged head, on its own (`scratch/slh-gate/gate/gate.log`, local files cited by name, END `2026-11-06T04:14:47+00:00`). Its lines, read from the log, not from recollection:

| Stage | Result |
|---|---|
| ruff, mypy (incl. `scripts/demo.py`), import-linter, req-coverage, generate-contracts --check | rc 0 each |
| pytest | rc 1: `13 failed, 7224 passed, 27 skipped, 5 xfailed, 153 warnings in 4949.99s (1:22:29)`, alone |
| the 13 FAILED | exactly the item-31 docs-audit set (`test_audit_docs_finding_citations`, `_ids` x2, `_process_core_digest` x2, `_w37_11_ceiling`, `test_doc_index`, `test_register_lint` x3, `test_register_owed`, `test_repository_invariants` x2) |
| audit_docs | rc 1, the slice's own working ids (checks 31/32) and the missing INDEX row, as item 31 allows; rc 0 is owed at the minted head (below) |
| skipped | 27 = the baseline: D's runtime tests present in the gated tree |
| frontend: install, generate:api, lint, type-check, test, build | rc 0 each. A seat's audit-docs held `pnpm test` about a minute (03:45:41 to 03:46:41): one line, no effect on a verdict |
| demo | seeded in the gate, "seeded, digests equal"; `demo.py --journey wf-699 --no-compose` rc 0; 1523 s; dislocation 524 s. D7's total and both attribution limbs are equal on the 19985-policy sample |
| END | `rc=1` from the python limb alone (python max=1, frontend 0, demo 0, restore 0, role 0, skip 0, infra 0, template 0, db0 0) |

**A12, the five things the adoption said the gate must prove, by the log's lines.** (1) No `pytest.exit` fired: the run completed (7224 passed in 4949.99 s). (2) Skipped 27 = baseline, by name in the short summary: `test_deploy_stack_runtime.py` 13, `test_glm_scalar_predict.py` 4, `examples/fremtpl2/test_seed.py` 3, `test_contracts.py` 2, `test_wf701_journey.py` 2, `test_deploy_switch_runtime.py` 1, `test_score_rate_limit.py` 1, `tests/test_doc_id_verify.py` 1; none is a file this slice changes. (3) and (4), (5): no FAILED and no SKIPPED line names `test_conftest_db_migration.py`, `test_error_sinks.py`, `test_deployment_route_types.py` or `test_auth_oidc.py`; the sweep file `backend/tests/test_api_authorisation_sweep.py` has no FAILED and no SKIPPED line either. These are passes by absence from a `-q` log, not counted per-test lines. (6) The failures are the item-31 set above. (7) mypy rc 0, ruff rc 0.

**A3's DB half: MET by the gate's lines**, in the same sense: the DB-backed tests behind `database` ran against the gate database (`alembic upgrade` rc 0, template guard `alembic_version=1` at start and END) without the DP-H1 stop, so a database at the scripts' heads passes; the stop itself and the DP-H2 warning stay evidenced by the executor's DB window and the auditor's mutation 4. **Not claimed:** a per-test pass line for the five DB-backed tests, which the `-q` log does not print.

**Item 42.** The `SL-2048` row did not exist at `origin/main` `96481c413092`; the mint added it as `active` and this audit commit sets it `closed`, and the ledger `closed`. State found at `origin/main`: no row.

**After the mint (the item-31 conditions).** At this PR's head: INDEX regenerated, `doc-index.py --check`, audit-docs and the register lint are owed to the checks run after this commit (see the report to the lead); their lines are the PR's, not written here before they are read. The PR; its number, squash commit and merge date are written at the merge's date-of-record.

### Build log

**Reds, by cause, each committed alone before its green** (A2; the logs' first lines name the run, quotes are verbatim):

- **R1** (`b96ea7da`): `assert None is not None` at `test_conftest_db_migration.py:22` and `:35`; `2 failed, 2 passed`. Cause: the stub returns `None` for a database one revision behind.
- **R2** (`2636dd39`): `AssertionError: assert {} == {('renamed.py..., '{exc}'): 1}`; `FAILED backend/tests/test_error_sinks.py::test_the_census_sees_an_injected_sink`; `1 failed, 8 passed, 2 warnings, 4 errors`. Cause: `except ValueError as problem: return str(problem)` is missed by the name tuple. Census delta with the new rule: exactly the six new rows, no sink lost (`_census()` against `_SINKS`, `/tmp/sl8334-census.py`).
- **R3** (`846e71b0`, a mutation proof: `route_class_problems` stubbed to `[]`, the essay's `openapi_problems` blindness): `FAILED …::test_a_same_named_local_class_is_refused_by_the_class_check`; `1 failed, 18 passed, 2 warnings, 1 error`.
- **R4** (`626cb503`, a mutation proof: removal left at `check=False`): `Failed: DID NOT RAISE CalledProcessError`; `1 failed, 305 passed in 116.11s`.
- **R6**: `scripts/demo.py:77: error: Incompatible types in assignment (expression has type "_Environ[str] | dict[str, str]", variable has type "dict[str, str] | None")  [assignment]` and `scripts/demo.py:78: error: Item "None" of "dict[str, str] | None" has no attribute "get"  [union-attr]`; `Found 2 errors in 1 file (checked 253 source files)`, rc 1, with `scripts/demo.py` in `files` and the base `demo.py`. Exactly two, so the CARRY fallback is not taken.
- **R7** (`aec3f2ea`): `AssertionError: assert 'signing key ...: DecodeError' == 'malformed token'` for T7 and T8; `2 failed, 11 passed`. T9 passed at the base and after (control).

**A5.** `git grep -n '("exc", "e", "err")' -- backend/tests/test_error_sinks.py` prints nothing (rc 1). **A6.** No site can hold a quote input. `runtime.py:822` was read first: `_ModelCallRefusal` is raised once, `_predict_model`'s last statement, with the step id (authored in the graph) and the model_type (from the artifact). The other five: a `SwitchIncompleteError` (process ids), two `consumed_features` `ValueError`s on a stored model's fit result (fixed texts), a Custom Objective's `ObjectiveError` at compile, and a smoke fit over seeded synthetic rows.

**A7.** The live-route class check and T5 are in. With the import kept and a local same-named class appended, `ast_problems` reports nothing for the four Environment rows (the AST half checks only the imported set), so it is the live check that catches that variant; the existing import-removed variant still fails the AST half (`test_a_body_class_defined_in_the_api_module_is_refused`). Reported to the lead as a reading of A7, who accepted it: the live-route class check is what catches that case.

**A8.** `git diff e8a59770...HEAD -- tests/test_doc_id_migrate.py | grep -ci prune` prints `0`.

**A9.** `scripts/req-coverage.py` before and after `b1140b0f` (it counts markers): `FR-11 1 → 2`, `FR-140 36 → 35`, no other line differs. FR-11 (00-overview) is determinism: identical inputs and pinned versions reproduce identical outputs, with an explicit persisted seed. The moved test is that. The remaining FR-140 markers in `packages/pricing-core/tests/test_ebm.py`, for the auditor's own read against FR-140's text (the transparent-by-construction export of term shape functions as tables, no approximation, with the fidelity/diagnostic sections): `:193` `test_fit_returns_the_expected_tables`; `:223` `test_the_exported_tables_reproduce_interpret_predict`; `:255` `test_an_interaction_fit_exports_a_rectangular_grid`; `:294` `test_scoring_matches_interpret_on_a_held_out_frame`; `:333` `test_a_scored_term_resolves_from_the_artifact_alone`; `:391` `test_a_monotone_constraint_on_a_categorical_feature_is_refused_by_name`; `:398` `test_a_monotone_constraint_naming_an_unknown_slug_is_refused_by_name`; `:448` `test_fit_seconds_and_library_versions_are_recorded` (the essay "notes and does not decide": left as FR-140).

**A10.** `uv run mypy` rc 0 with `scripts/demo.py` in `files`; `.claude/skills/repo-architecture/SKILL.md` declares `scripts/` and `backend/tests/` outside the gate (DP-H4), its Verified line carrying the tree `b4f4f7e24efeea0ebfc84282fe8e94c88492a943`.

**A11.** T7, T8 and T9 green (`13 passed`); the new handler logs the type only and the census still passes with no new row.

**A3 (run, DB window granted by the lead, START 2026-11-05 11:01:49 GMT, END 11:06:48 GMT).** Tree `ec4c4240c6c20d3b75490a9cdeb9a88fe05efab4` (code head). Template guard before createdb and at END: `alembic_version=1 environments=3 tenant_marker=1`. Copy `gipricing_sl8334a3` (`createdb -T gipricing`), every URL (`GIP_DATABASE_URL`, `GIP_MIGRATION_DATABASE_URL`, `GIP_TEST_DATABASE_URL`) on the copy, redis `-n 11`; load1 4.40 and 8 GB available at start. One DB-backed file, `backend/tests/test_workspaces.py`, through run-small:
- stamped one back (`b7e4c2a91d36 -> 9b3e7c15d4a2`): rc 1 in 25 s, `_pytest.outcomes.Exit: the test database is at ['9b3e7c15d4a2'], the scripts' heads are ['b7e4c2a91d36']: run `uv run alembic upgrade head` against this database (FD-1488)`;
- restamped to head: rc 0 in 23 s, `2 passed, 2 warnings in 2.08s`;
- a revision the scripts do not know (set by SQL on the copy only, DP-H2): rc 0, `UserWarning: the test database is ahead of this checkout: ['zz_unknown_ahead'] is not a revision of these migration scripts (DP-H2)`, `2 passed, 3 warnings in 3.43s`.
END: `redis-cli -n 11 FLUSHDB` then `-n 11/12/13 dbsize` = 0, 0, 0; `-n 0 dbsize` = 56 before and after; copy dropped, `select count(*) from pg_database where datname='gipricing_sl8334a3'` = 0; datnames `gipricing postgres template0 template1`.

## PRs

(Added at the PR.)
