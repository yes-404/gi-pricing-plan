---
id: LG-9442
family: ledger
title: WK-1178 slice SL-1462 — FD-1456 in full, the Peril Structure approval path and the compile resolver's peril branch (PL-1461), slice ledger
status: active
created: 2026-10-09
owner: executor
tree: 8af8a9b48e459c159666bd4e468d743719ade84c
phase: P2
work: WK-1178
slice: SL-1462
plans: [PL-1461]
corrected_by: []
relates: [PL-1461, RL-1457, FD-1456, RL-1445, RL-1263, FR-20, FR-191, FR-237, FR-255, FR-351, FR-355, FR-363, WK-1178]
---

# LG-9442 — WK-1178 slice SL-1462: FD-1456 in full, the Peril Structure approval path and the compile resolver's peril branch

**GO:** given — `to-lead.md` "2026-10-10 05:19:53 BST — DISPATCH GOs at main 84ff9f0b: A-1 (PL-1461/SL-1462) GO NOW on gate-1 …", conditions a–d (merge main never rebase with INDEX by script; stray pre-mint LG files removed and the merged tree equal to a clean 3-way merge tree; closing acts in the slice PR and red-first per task, NFR-499 in every new error message; one code gate on gate-1 with a docs check on gate-2). Before the GO this branch was authored at the user's order ("2026-10-09 15:22:26 BST — USER: 'worrying only one executor runs'. FILL THE VM NOW …", items 1–4, in `to-lead.md`, a local file): code and tests are written on a branch from S4's pushed head `8af8a9b4`; only small tests run (one file, no database), nothing merges before the GO, the full gate and the MERGE-ACK.
**MERGE-ACK:** not yet given.

## Tasks

### Scope

The slice's Work-plan row is `SL-1462` in `docs/roadmap.md` (WK-1178, Option A, A-1): *"FD-1456 in full, the Peril Structure approval path and the compile resolver's peril branch"*. Its scope is `PL-1461` §"Scope" (requirement coverage table) and §"Write set, and its contention", read at this branch's tree. Requirement ids covered: FR-20, FR-190, FR-191, FR-237, FR-255, FR-351, FR-355, FR-363. The ruling is `RL-1457` (DP-1 (a), DP-2 (a), DP-3 (b), and T1, the `06` §4.2 note).

Per `Lean P2 L1 (a')` the slice's one PR sets `PL-1461`'s `status:` line to `active` (this branch's first commit) and closes this ledger and `SL-1462`'s roadmap row at its head.

Write set: `PL-1461` §"Write set" only. Any other path is a stop to the lead.

**Serial with S4 on the resolver.** `PL-1461` was written against `_Resolver.resolve`. This branch is cut from S4's head, where S4's Task 3 has already lifted the class to module-level `WorkspaceResolver` (`rating_versions.py`). The peril branch goes into that class, re-anchored by symbol (Q1 (a) of planner-g2's GO request).

### Task list

Order and acceptance checks are `PL-1461` §"Tasks" and §"Acceptance Standard" (items 1 to 14). Each task below is added with its commit when it is pushed.

### Gate

**Gate 1, tree `a93fb9048c2ff5f7eeb92536f9a8c16d407c3513` (`git status --porcelain` empty before and after), gate-1 slot, 05:38:14 to 06:25:14 BST, load1 2.57 at start, 7.58 at the end of the frontend build; own test database `gipricing_sl-1462_8351cbfa`; the `dev-commands` gate body (seven Python stages in parallel) then the frontend half.** RED: 2 of the 15 pytest failures are code-linked and outside PL-1461's write set (stopped to the lead, below); 13 are the working-id audit red.

| Command | rc | Excerpt |
|---|---|---|
| `uv run ruff check .` | 0 | |
| `uv run mypy` | 0 | |
| `uv run lint-imports` | 0 | |
| `python3 scripts/audit-docs.py` | 1 | FAILED (4) at this tree: check 31 gap `1570`..`9442`; check 31 `created` order (9442 is 2026-10-09, 1570 is 2026-10-10) (both clear at the mint of this ledger); check 32 twice, two removed pre-mint ledgers named by working id in this ledger's own text (fixed in the next commit; audit-docs then prints FAILED (2), the two check-31 lines) |
| `uv run python scripts/req-coverage.py` | 0 | |
| `uv run python scripts/generate-contracts.py --check` | 0 | |
| `uv run pytest -q` | 1 | 15 failed, 5208 passed, 4 skipped in 2689.44 s (44:49) |
| `pnpm --dir frontend install --frozen-lockfile` / `generate:api` / `lint` / `type-check` | 0 / 0 / 0 / 0 | |
| `pnpm --dir frontend test` | 0 | 653 passed (653) |
| `pnpm --dir frontend build` | 0 | |

The 15 pytest failures. **Code-linked, two, outside the write set:** `backend/tests/test_approval_guard.py::test_the_carry_walker_reaches_the_five_artifact_tables` (the walker now reaches `peril_structures`: `Extra items in the left set: 'peril_structures'`; PL-1461 Step 5 and Task 0.5 expected this file to pass unchanged) and `packages/pricing-core/tests/test_quote_input_raise_sites.py::test_every_quote_input_raise_site_has_a_sentinel_case` (`{('rating/runtime.py', 'handler'): 3} != {('rating/runtime.py', 'handler'): 2}`: Task 4's early `_model_call_failure` for a `peril_structure_ref` step is a third site in `handler`; its message holds the step id and the ref string, no quote input). **Thirteen, the working-id audit red:** `tests/test_audit_docs_finding_citations.py`, `test_audit_docs_ids.py` (two), `test_audit_docs_process_core_digest.py` (two), `test_audit_docs_w37_11_ceiling.py`, `test_doc_index.py`, `test_register_lint.py` (three), `test_register_owed.py`, `test_repository_invariants.py` (two). Re-run alone at the next commit (small-test slot, 419.6 s): the same 13 fail, each asserting a green `audit-docs` or `doc-id check` run; `doc-id.py check` prints `[noncontiguous] docs/INDEX.md has a gap between 1570 and 9442` and `test_doc_index.py:773` prints `the live allocation is not contiguous: [(1570, 9442)]`. These clear at the mint of the working id (the known effect of a working-id ledger beside its INDEX row); the control is the same files on a minted tree.

### Audit

(Written by the auditor at slice close.)

### Build log

**2026-10-09, authoring phase.** Worktree `.claude/worktrees/sl-1462`, branch `sl-1462-a1-peril-approval`, from `8af8a9b48e459c159666bd4e468d743719ade84c` (S4's pushed head). Stamps are BST (`TZ=Europe/London date`).

- Commit 1: `PL-1461`'s `status:` line `draft` to `active` (the Q1 ruling, `L1 (a')`), and this file.
- **Red-first proof is OWED for every database-backed test.** The tests of items 1 to 9 need Postgres (`GIP_TEST_DATABASE_URL`), which the small-test rule bars; each is written before its code, and its red (by cause) is shown at the first gate-slot window. Item 10 (`packages/pricing-core/tests/test_rating_runtime.py`) needs no database and is run red then green here.
- **Tasks 1 and 2 (PL-1461 Tasks 1, 2), 2026-10-09.** `backend/tests/test_api_approvals.py`: `_AFTER["peril_structure"]` is `_moves("approved", "review", "reconciled")` and `_MOVE_ACTION` gains `peril_structure`. New module `backend/tests/test_peril_structure_approval.py`: items 4 (supersession), 5 (unapproved component refused, control approved), 13 (parametrised over every `ModelStatus` member, plus the accepted-set-inside-the-enum test), an `excess_model` case, and item 6 (`reconciled`/`review` refused `PIN_NOT_APPROVED`; approved structure compiles, Bundle `resolved_payloads[ref]["status"] == "approved"`). `backend/tests/test_rating_version_create_pins.py`: item 7, PL-1429's Acceptance 7 test renamed `test_a_peril_structure_pin_is_stored_and_compile_names_the_missing_structure`, asserting the ref in the message and not "has no backend table yet". **Red for all of these is OWED**: every one needs Postgres, which the small-test rule bars. Each is shown red by cause at the first gate-slot window, by running the file against the tree with Tasks 3 and 4's code absent.
- **Task 3 (PL-1461 Task 3), 2026-10-09.** `backend/src/app/platform/perils.py`: `apply_approval_decision`, `_target_status`, `_require_approved_components`, `_supersede_earlier_versions`, `APPROVED_COMPONENT_STATUSES` (`frozenset({ModelStatus.APPROVED})`); `api/approvals.py`: one call in `_carry_to_the_artifact`'s `approval_decision()` block, docstring corrected. **Implementation deltas from the plan's text (no spec change):** (1) `_target_status` also maps `WITHDRAWN → RECONCILED`, as every sibling does and as `withdraw_request` also calls the carry (`api/approvals.py`); without it a withdrawn request strands the structure in `review`. (2) `_require_approved_components` reads the stored `perils` through `PerilComponent.model_validate`, not `to_structure(row)`, so a stub `reconciliation` (as `test_api_approvals`'s table fixture inserts) cannot break the check; the `excess_model` is read from `large_loss`.
- **Task 4 (PL-1461 Task 4), 2026-10-09.** The peril branch is in `WorkspaceResolver.resolve` (S4's lifted `_Resolver`), before the final raise; `perils.load_structure_by_ref` added; the final raise now says the compile resolver has no branch for the artifact type (item 8). **Item 10 red then green (small test, no database):** `flock -w 300 /tmp/slots/small-test -c "nice -n 19 timeout 150 uv run --directory <wt> pytest -q packages/pricing-core/tests/test_rating_runtime.py -k peril_structure_model_call"`. RED, 1 failed in 10.60s, at `runtime.py:589`: `KeyError: 'fit_result'` (the cause the plan names). `_model_call_handler` now returns `_model_call_failure(...)` naming the ref and A-3 before the `payload["fit_result"]` read. GREEN: the same file, `pytest -q packages/pricing-core/tests/test_rating_runtime.py`, 12 passed in 3.47s.
- **Task 5 (PL-1461 Task 5), 2026-10-09.** RL-1457 T1 applied to `docs/specs/06-governance.md` §4.2's floor note, byte for byte except `<date>` = 2026-10-09 and `<RL>` = RL-1457. The find string counted 1 before the edit (`grep -cF`); after it, `git grep -n 'per-peril approvals half is unqueryable' -- docs/specs` prints nothing (rc 1): Acceptance 14.
- **Owed after Task 7:** red-by-cause for items 1, 4, 5, 6, 7, 13 (needs the database); `mypy`, `lint-imports`, `audit-docs`, the full gate. `model-schema`'s `DEFAULT_POLICY` comment block (`approvals.py`, "enforced nowhere") also describes the old state; it is outside the write set, so it is left and reported to the lead.

**2026-10-10, GO turn (executor-a1g).**

- **Step 1, the merge of main (BST 05:2x).** `git merge origin/main` (84ff9f0b8d5369d08559d030cf235c60ad51abd0) into f03792056c347429d0c2278cdbcec6208ee58921, never a rebase; merge commit 2b57f3beade262b69e925452d905a5af89553770. Conflicts (8): `backend/src/app/api/dislocation_runs.py`, `backend/src/app/platform/dislocation_runs.py`, `backend/src/app/worker/dislocation_handlers.py`, `backend/tests/test_dislocation_runs.py`, `docs/specs/03-rating-engine.md`, `scripts/measure-attribution-cost.py` (S4/S3 pre-squash files, none in A-1's write set; each taken from `origin/main` byte for byte); `backend/src/app/platform/rating_versions.py` (A-1 edits it: taken from `origin/main`, then A-1's own delta `git diff 8af8a9b4 f0379205 -- backend/src/app/platform/rating_versions.py` re-applied with `git apply`, clean); `docs/INDEX.md` (`git checkout origin/main -- docs/INDEX.md`, then `python3 scripts/doc-index.py`; `--check` rc 0, byte-stable). `git rm` of the two stray pre-mint slice ledgers (working ids 9440 and 9478, files under `docs/ledgers/`; their minted forms LG-1570 and LG-1545 are on main).
- **Merge proof.** `git merge-tree --write-tree --merge-base 8af8a9b48e459c159666bd4e468d743719ade84c origin/main f03792056c347429d0c2278cdbcec6208ee58921` printed T = `08fa5ee50d647526452500ec5df149382eb21470`, rc 1; `--name-only` shows the one conflicted path is `docs/INDEX.md` (generated; excluded from the comparison). `git diff --stat T HEAD -- . ':!docs/INDEX.md'` printed nothing, rc 0: the merged tree equals the clean 3-way tree everywhere except the regenerated INDEX. `git diff --name-only origin/main...HEAD` lists only A-1's write set: `api/approvals.py`, `platform/perils.py`, `platform/rating_versions.py`, `test_api_approvals.py`, `test_peril_structure_approval.py`, `test_rating_version_create_pins.py`, `docs/INDEX.md`, this ledger, PL-1461, `docs/specs/06-governance.md`, `pricing_core/rating/runtime.py`, `test_rating_runtime.py`.
- **Step 2, Task 0 at the merged tree.** Activation needs 1–4b and 5 are those the 05:19:53 entry reads at 84ff9f0b (FD-1456 active HIGH; SL-1430 and SL-1472 closed; DP-1..3 held by the 2026-10-05 17:02:50 entry; RL-1457 on main; the GO is that entry). `WorkspaceResolver` (`rating_versions.py:467`, constructor `(session, workspace_id, blob_store)`) is as S4 lifted it; the `peril_structure` branch sits before the final raise (`:608`). One migration head: `b8d2f4a6c0e1` (S4's), no A-1 migration. Line numbers PL-1461 quotes in `compile.py` have moved (`_APPROVED_OR_BETTER` `:404` → `:445`, `_MATURITY_CHECK_EXEMPT` `:431` → `:472`); the symbols and values are unchanged (`peril_structure` is not exempt), so item 6 still needs no `compile.py` edit. `model-schema`'s stale `DEFAULT_POLICY` comment is left, as the lead files it as an FD (owner WK-1178).

- **Step 3, red-first (BST 05:23–05:37, inside my gate-1 slot, test database `gipricing_sl-1462_8351cbfa` made with `createdb -T` and `alembic upgrade head`; load1 1.7–3.3).** Method: reverse-apply each task's source delta to the merged tree (`git apply -R`, rc 0), run, `git checkout HEAD -- backend/src packages/pricing-core/src`, `git status --porcelain` empty. Task 3 = `git diff 39966e39 25be30cc -- backend/src` (`perils.py`, `api/approvals.py`); Task 4 = `git diff 8af8a9b4 f0379205 -- backend/src/app/platform/rating_versions.py` (the resolver's peril branch). Command each: `uv run --directory <wt> pytest -q --tb=line <file>`.

| Item | Test (file) | Without | RED, by cause | At head |
|---|---|---|---|---|
| 1 | `test_api_approvals.py -k peril_structure` (3 cases) | Task 3 | rc 1, 3 failed / 8 passed: `:1186 assert 'review' == 'approved'` (approve), `'review' == 'reconciled'` (reject, request_changes): the decision moves nothing | rc 0, 11 passed |
| 4 | `test_peril_structure_approval.py::…supersedes_the_earlier_approved_version` | Task 3 | `:218 assert 'review' == 'approved'` | passed |
| 5 | `…unapproved_component_is_refused_at_approve`, `…all_approved_is_approved` | Task 3 | `:259` (approve returned 200, not the refusal), `:292 assert 'review' == 'approved'` is the control | passed |
| 13 | `…component_check_accepts_only_model_status_approved[6 statuses]`, `…accepted_set_is_inside_the_enum`, `…excess_model_is_checked_at_approve` | Task 3 | `:319`/`:321` (status stays `review`; the refusal absent), `:333 ImportError: cannot import name 'APPROVED_COMPONENT_STATUSES'` (a symbol of the task, stated as such), `:403` | passed |
| 6 | `…unapproved_peril_structure_pin_is_refused_at_compile[reconciled, review]`, `…approved_…_pin_compiles_…_payload` | Task 4 | `:456` job error `NOT_FOUND`, message "… has no backend table yet (Phase 2); a compile cannot e…" ; `:488 assert 'NOT_FOUND' == 'PIN_NOT_APPROVED'` | passed |
| 7 | `test_rating_version_create_pins.py::…compile_names_the_missing_structure` | Task 4 | `:248 assert 'has no backend table yet' not in 'peril_struc…ot embed it.'` | rc 0, 15 passed |

Head file totals: `test_peril_structure_approval.py` 14 passed (rc 0, 28.1 s); `test_rating_version_create_pins.py` 15 passed (rc 0); `test_api_approvals.py -k peril_structure` 11 passed. Note: `load_structure_by_ref` was added in Task 3's commit (`25be30cc`), not Task 4's, so with Task 3 reverted the compile tests fail with `AttributeError` (`JOB_HANDLER_FAILED`, `:456`/`:488`) rather than `NOT_FOUND`; their by-cause red for the resolver is the Task 4 row above.

- **Deviation: three fixtures corrected at the first database run (commit 66850d77, test file only, in the write set).** `test_peril_structure_approval.py` was authored with no database; the first run at the merged head (05:26) showed 3 of 14 failing at the head, each a test defect and none a source defect: (a) `…supersedes_the_earlier_approved_version` compared the whole `peril_structure.*` event list of `ps@1` (it also holds `created` and `submitted`); it now compares the `approved` and `superseded` events; (b) `…excess_model_is_checked_at_approve` inserted a `review` row with no `reconciliation` (CHECK `ck_peril_structures_reconciled_peril_structure_has_a_re_5529`) and no creation Audit Event (FR-353, `APPROVAL_AUTHOR_UNRESOLVED` 403); it now creates the row through `create_structure`, then sets `review` and a stub reconciliation, and builds the large-loss treatment with `LargeLossTreatment.model_validate` (the `model_copy(update={...})` of plain strings raised a Pydantic serializer warning); (c) `…approved_…_pin_compiles_…` read `resolved_payloads` from the `RatingVersionRow.bundle` summary dict; it now reads the Bundle from its blob (`_read_blob`, `Bundle.model_validate_json`) as `test_rating_version_compile.py` does. The reds above were run against the corrected file.
- **The SL-1436 notes.** `packages/pricing-core/tests/test_rating_wire_order.py` alone: rc 0, 14 passed in 3.4 s. PL-1435 Task 2c's replay script alone: the script inline in LG-1467 (sha256 `b43d213cdd4bae7c3b6d100933ba85875421ae15925a5eccde56832ecf71cfea` verified after extraction; its one edit is the `ROOT` path, this worktree). Its `record` mode ran with `origin/main`'s `runtime.py` checked out over A-1's (rc 0, 57 s; `base.jsonl` 3603 lines, sha256 `8c1cec7b09f15a050130a479c66fd4152bf4f22841fdba66084ecefdd3c3ac4c`), its `replay` mode at A-1's head (rc 0, 152 s): every case `equal N of N`, `DIFFS 0` (for example `bench-rating-gbm` 601 of 601, `score-fixture-glm` 730 of 730). Note the base is main, not the pre-chain tree LG-1467 recorded: SL-1436's chain has merged, so this measures A-1's own `runtime.py` delta, and finds none outside a `peril_structure` `model_call`.

## PRs
