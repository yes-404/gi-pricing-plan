---
id: LG-1370
family: ledger
title: WK-1178 slice — the permission-parity check (SL-1360, PL-1359, RL-1305)
status: closed
created: 2026-10-01
owner: executor
tree: 98d7191b62e73dcfba4bb294c743ee97cf6f6f59
phase: P2
work: WK-1178
slice: SL-1360
plans: [PL-1359]
corrected_by: []
relates: [RL-1305, CR-1247, RL-1236, RL-1263, PL-1279]
---

# LG-1370 — WK-1178 slice SL-1360, the permission-parity check

Executed from `PL-1359` by `executor-1360` (sonnet, medium). Branch `sl-1360-permission-parity-check`, from `origin/main` `19155b505741317da6967362707f387b39bd2cef` (#1046; tree `98d7191b62e73dcfba4bb294c743ee97cf6f6f59`). The ledger's id `9778` is a working id, reserved by the lead; the lead is the only allocator and mints the final id. Every time is `TZ=Europe/London date`, BST.

## Tasks

### Task 0 — preconditions

**Dispatch record, FINAL, quoted verbatim** (`gi-pricing-plan.local/handover/DISPATCH-WK-1178-SL1360-2026-10-01.md`; each line prefixed `> `):

> # Dispatch record — WK-1178 slice SL-1360 (the permission-parity check), from PL-1359 — FINAL
>
> **Status: FINAL — GO given 2026-10-01 09:13:18 BST by the lead (session gi-pricing-team), on the maintainer's GO check (passed, conditional on #1046) and #1046's merge.** Drafted 08:52:59 BST. Lane B. PL-1359 is frozen from its first merge (#1043, 42732321): nothing in it is edited, and every delta lives here.
>
> **The order:** the maintainer's entry "2026-10-01 08:04:53 BST — correction ACCEPTED (RL 9856 = RL-1305, already minted); lane B proposal AGREED, with the delta in the dispatch record", quoted:
> > LANE B proposal AGREED: 1. One activation PR: PL-1279 active, a new WK-1178 SL row (citing my entry), plus the Exit-demo scope line … 2. RL-1305's Task-3 changes go in the DISPATCH RECORD, not a superseding PL. … If any change alters a Task's ACCEPTANCE rather than its method, file a superseding PL and tell me. 3. A fresh executor (sonnet); state "no overlap with SL-1345" in the write set. My GO check starts from status on main, then the needs, the DP table (DP-1..3 → RL-1305), then the record.
>
> **Superseding PL instead of a delta (the maintainer's trigger fired):** RL-1305 changed PL-1279's ACCEPTANCE (the alias guard dropped; new check-site and reach cases; the count re-derived), so the maintainer's rule required a superseding PL. That PL is **PL-1359** (#1043), agreed in the maintainer's entry after 08:07 BST ("AGREED: PL 9781 superseding PL-1279"). It quotes RL-1305 verbatim, so **this record carries no Task-3 delta**: the plan itself is now the RL-1305 shape. The Exit-demo line landed separately in #1038 (the maintainer's change: "the NEXT roadmap docs PR").
>
> ## Plan and slice status on main (the gate check, FIRST)
> - **Main at GO:** `M=19155b505741317da6967362707f387b39bd2cef` (#1046 merged; read-back parent 42732321, tree 98d7191b = the ACK tree).
> - **PL-1359:** `git show "$M":docs/plans/PL-01359-… | grep -m1 '^status:'` → `status: active                  # draft → active → superseded | retired (§1.2a)`.
> - **SL-1360:** the roadmap awk → `status: active                  # draft → active → closed | retired (§1.2a)`.
> - **PL-1279:** `status: superseded`, `superseded_by: PL-1359` (#1043).
>
> ## Activation needs
> PL-1359 has no separate "Activation needs" section. Its §Status (`PL-1359:172-180`) reads: "`draft` until its activation. It has **no open blocking decision point**: `RL-1305` resolves `PL-1279`'s DP-1 to DP-3 (§"Decision points"), and its D4 amendment is on `main` (Task 0 Step 2). Activation is the lead's dispatch with the maintainer's agreement, in a separate PR. That PR carries the `SL-` row and this plan's status flip." The checks:
> 1. **No open blocking DP:** PL-1359 §"Decision points" (`:413-427`): "None is open. `RL-1305` resolves every one that `PL-1279` carried" (DP-1 → D1 (C) with STALE_OWNER; DP-2 → D2 (ii); DP-3 → D4 (a), on main; RL vs ADR → D3 (a)). **Met.**
> 2. **RL-1305 on main, `status: active`, not superseded:** at M, `git grep -n '^status:\|^superseded_by:' "$M" -- 'docs/rulings/RL-01305-*'` → `5:status: active …` and `12:superseded_by: ~`. **Met.**
> 3. **D4's 06 §4.1 amendment on main:** at M, the three header rows are inside the blockquote: `269:> | Permission | Governs | Check owner |`, `313:> | Name used before | Enum name |`, `333:> | Permission | Owner Work |`. **Met.**
> 4. **The maintainer's agreement:** the 08:04:53 BST entry above. **Met.**
> 5. **The separate activation PR merged, and the lead's go:** #1046 merged as 19155b50 on the maintainer's MERGE-ACK; **the lead's GO at 2026-10-01 09:13:18 BST.** **Met.**
>
> ## Decision points: every one has a resolver
> As need 1. **No task is held.**
>
> ## Task 0 (the executor's preconditions, quoted, run at the dispatch tree)
> Steps 1–4 as `PL-1359:431-447`: RL-1305 active and not superseded (stop otherwise); the M2 header rows match character for character (a change is a replan); re-run M3/M4/M5 with the predicates verbatim (M4's `comm` runs empty; M5's zero-site members = the owner rows; reach complete); `gh pr list --state open` for anything touching 06 §4.1, permissions.py or a check site, with head SHAs in the ledger.
>
> ## Conditions
> 1. **Write set:** `tests/test_permission_parity.py` (new), its ledger LG 9778 under `docs/ledgers/`, and the regenerated `docs/INDEX.md`. **No overlap with SL-1345** (PL-1348's write set): PL-1359 §"File contention" (`:342-377`) lists every PL-1348 path, and none is in this set; the slices meet only through reads (the live test imports `create_app`, and with it `api/score.py`; SL-1345 changes that file's responses and error mapping, not its `requires()` dependencies). Acceptance 8: `git diff --stat origin/main...HEAD` names nothing under `backend/src/`, `packages/*/src/`, `frontend/` or `docs/specs/`.
> 2. **RL-1263:** a different Work from lane A (WK-674), so allowed. No shared non-exempt file (INDEX is registry-exempt). The second to merge re-gates.
> 3. **Behavioural dependency** (`PL-1359:372-376`): if WK-674 Slice 2 merges first, its commit must have cleared the two owner cells (RL-1305 D1 item 4). If STALE_OWNER fires, that is a finding against WK-674 S2, not something to fix here; stop and report.
> 4. **Holds:** none apply (the slice reads no ladder rungs, consumes no /score route, and calls none of FD 9779's five routes); see `handover/holds-2026-10-01.md`.
> 5. **Gate evidence, for EVERY suite-level run:**
>    - a clean checkout of the named SHA with `git status --porcelain` empty;
>    - `uv sync --all-packages`;
>    - `ruff check --no-cache`, and `mypy --no-incremental`;
>    - the dev-commands slot wrapper verbatim (`.claude/skills/dev-commands/SKILL.md:122-171`) plus `LOKY_MAX_CPU_COUNT=4`, in the foreground with a timeout;
>    - `uptime` and `free -h` at start and end;
>    - the other holder via `flock -n`;
>    - the stage table read, never the exit code (the wrapper exits 0 on failure).
>    Single-file pytest runs are slot-exempt; nothing wider is.
> 6. **Red first:** every acceptance item, including both live red proofs (5(a): one line naming `dataset:read`; 5(b): 118 lines `route walk did not reach a published path:`, per the plan as fixed) and Task 3's red-first stubs (the `walk=lambda app: _top_level_only(app)` default).
> 7. **Task 4 Step 5:** record the first permissions.py-only push and its python.yml run, or mark it owed with the lead as owner. **No artificial commit** (Acceptance 8).
> 8. **Ledger:** LG working id **9778**, reserved by the lead at 08:52 BST on 1 Oct and checked free. The lead is the ONLY allocator (FD-1338). Append-only; Task 0 quotes this FINAL record verbatim; BST stamps.
> 9. **Frozen records:** nothing in `docs/plans/`, `docs/rulings/` or any frozen body is edited. The executor writes no spec text (executor.md, the maintainer's carve-out: only text a ruling carries verbatim; this slice has none).
> 10. **Executor:** a fresh `executor-1360`, spawned from `.claude/roles/executor.md` with its Model / effort line (sonnet, medium), in a new worktree from origin/main after the activation PR merges. It never `cd`s.
> 11. **PR:** a draft titled `test(governance): SL-1360 — the permission-parity check (WK-1178, PL-1359, LG 9778)`. The mint and the SL/LG closes come after the slice audit; the lead allocates the ids.
>
> ## Corroboration and disclosure (the maintainer's entry 08:04:53 BST)
> - **dm-9856's independent agreement:** a fresh effort-high decision-maker (dm-9856, PID 3077911, 1 Oct 08:01 BST), commissioned on my wrong premise that RL 9856 was unruled, re-derived D1–D4 independently at 101e32dc and AGREED with RL-1305 on every point. All locators held, and it tested two adversarial residuals (an unreachable require_permission site counts as checked; the Specified owner cell parsing), neither grounds to supersede. Its record: from-lead-2026-09-30.md, entry "CORRECTION: RL 9856 was already RULED and MINTED as RL-1305".
> - **Disclosure, the early status:** the RL-1305 record, while still working id 9856, was set `status: active` at 83aac898 (30 Sep 10:54:39 BST), 1 h 51 min before its mint commit 48f6fc17 (12:45:34 BST), contrary to "draft until the lead mints". It was harmless: the maintainer's #989 ACK accepted the file byte for byte, and a minted RL opens active. No correction to main is needed.
>
> ## Deltas
> (none yet)
> - **Delta 1 — 2026-10-01 09:20:24 BST (lead):** built in ~6 min by executor-1360; draft PR #1049 at 892ffd8f, 16 tests passing, the write set is the test file + LG 9778 + INDEX only. Task 0 at tree 98d7191b reproduces PL-1359's measurements (24/24; 145 contexts / 141 APIRoute / 120 paths; route leg 21, AST 11, union 22; the 2 unchecked = the 2 owner rows; STALE_OWNER clean). One count difference is recorded and accepted: 47 `require_permission(permission=…)` calls against the plan's 46. The extra is authz.py:67's `permission=permission` pass-through, which is not a member check site. Every red proof is in the ledger. Task 4 Step 5 is owed, with the lead as owner. **Gate slot granted** at 09:20:06 BST (both slots free; load 1.73). The gate on 892ffd8f is the gate of record; the check-31 family is the only allowed red.

**Step 1 (RL-1305 active, not superseded)**, 2026-10-01 09:14:17 BST, at `origin/main` 19155b50:
`git grep -n '^status:\|^superseded_by:' origin/main -- 'docs/rulings/RL-01305-*'` prints `5:status: active …` and `12:superseded_by: ~`. Met.

**Step 2 (the M2 header rows)**, same tree: `grep -nE '^> \| (Permission \| Governs \| Check owner|Name used before \| Enum name|Permission \| Owner Work) \|$' docs/specs/06-governance.md` prints `269`, `313` and `333`, and `### 4.1` is at `188`, `### 4.2` at `342`. `BUILT_HEADER`, `SPECIFIED_HEADER` and `ALIAS_HEADER` equal them without the `> ` prefix. No replan.

**Step 3 (M3, M4, M5 re-run at tree `98d7191b62e73dcfba4bb294c743ee97cf6f6f59`, working tree of branch head 19155b50 before the test file existed on it; 09:14 to 09:16 BST)**

| Measure | Predicate | Result |
|---|---|---|
| M3 | `grep -oE '= "[a-z_]+:[a-z_]+"' packages/model-schema/src/model_schema/permissions.py \| tr -d '=" ' \| sort -u \| wc -l` | 24 |
| M4 | the plan's `sed -n '188,341p' … \| awk … \| grep -oE …` over `docs/specs/06-governance.md` | 24 names; `comm -23` and `comm -13` against M3 both print nothing |
| M4 owners | rows of the Built table with a non-empty `Check owner` | `deployment:promote` and `admin:manage_environments`, each `WK-674` (so STALE_OWNER does not fire on the live tree) |
| M5 route leg | `iter_route_contexts(app.routes)` over `create_app(Settings(environment=Environment.LOCAL, version="parity", log_level="ERROR"))` | 145 contexts, 141 `APIRoute`, 120 distinct paths; `app.openapi()["paths"]` has 120; shortfall 0; 21 members through `PERMISSION_ATTRIBUTE` |
| M5 top-level walk | `app.routes` iterated directly | 29 entries, 2 `APIRoute`, 0 members, 118 of 120 paths unreached |
| M5 AST leg | `service_layer_checks` over `backend/src/**/*.py` | 11 members; the only one the route leg lacks is `admin:break_glass` |
| M5 AST call count | calls to `require_permission` with a `permission=` keyword | 47 by my loose predicate; the 47th is `backend/src/app/api/authz.py:67` (`permission=permission`, the variable passed through by `requires()`). The plan's 46 counts only the `<Permission>.<MEMBER>` form, so the figures agree |
| M5 union | route leg ∪ AST leg | 22; the two unchecked are exactly `deployment:promote` and `admin:manage_environments`, the two owner rows |
| M5 text-regex proxy | `(Perm\|Permission)\.<NAME>` on non-comment lines | 22, the same two unchecked |
| Cross-check greps | `grep -rnE --include='*.py' 'requires\((Perm\|Permission)\.' backend/src/app/api \| wc -l`; the same with `'requires('`; `grep -rnE --include='*.py' 'permission=(Perm\|Permission)\.' backend/src \| wc -l` | 54; 56; 48 (as PL-1359 M5) |

The reach is complete, M4's two `comm` runs are empty, and M5's zero-site members equal the owner rows. Task 0 passes. STALE_OWNER did not fire on the live tree (the first live run, 09:15:14 BST, passed).

**Step 4 (open PRs that touch 06 §4.1, `permissions.py` or a check site)**: `gh pr list --state open` at 09:14 BST listed 22 PRs; `gh pr diff <n> --name-only` over each, filtered for `permissions.py`, `06-governance.md`, `backend/src` and `packages/*/src`, matched two:
- #1045 (SL-1345, head `4dd138130342003afbde8e743626d7c5a8356d05`): `backend/src/app/api/score.py`, `errors.py`, `observability/metrics.py` and `packages/*/src` money, scoring and rating files. It touches no `requires()` dependency and no `permissions.py`; this slice's write set has no overlap with it.
- #979 (head `1d2b61322704411bc3ee8c3112ddd8a4e33ba355`): `06-governance.md`, but its hunks are an OQ row for the Validation Rule Set and not §4.1's permission tables (`gh pr diff 979` shows an OQ-632 row and an RL index row).

No other open PR touches those paths. The WK-674 S2 PR (#977 is a ruling) and WK-690 S3 have no code PR open yet.

### Task 1 — the pure comparison, each class proved red (commit c2ff3b3c)

Red first, 09:14:52 BST: `parity_violations` stubbed to `return []` (the real function renamed). `uv run pytest -q tests/test_permission_parity.py` printed `9 failed, 1 passed`. Each of the nine `test_broken_*` cases failed on `_only`'s length assertion with `AssertionError: []` (for example `assert 0 == 2` for `test_broken_name_in_two_tables`, `0 == 1` for the one-class cases). The clean control passed. Real implementation restored (09:14:57 BST): `10 passed`.

### Tasks 2 and 3 — the live test and the check-site predicate (commit 80798559)

**Task 3 Step 3, red against the two rejected proxies (09:15:07 BST).** `service_layer_checks` returned the text-regex proxy's result, and `route_checks`'s `walk` default was `lambda app: _top_level_only(app)`. `uv run pytest -q tests/test_permission_parity.py -k 'check_site or service_layer or flatten'` printed `2 failed, 2 passed, 11 deselected`:
- `test_broken_member_referenced_but_never_checked_has_no_check_site` failed (the proxy counted the role-set references);
- `test_flattened_route_walk_reaches_nested_routers` failed (`At index 0 diff: frozenset() != frozenset({'a:read'})`);
- the service-layer test and the non-flattening test passed.

Both stubs removed (09:15:14 BST): the module printed `15 passed` (10 + live test + 4 check-site tests), the live test included and green on the real tree.

**Acceptance 5 (b), the reach red proof on the real app (09:15:32 BST).** `checked_permissions()` was given `walk=_top_level_only`. The run printed `1 failed, 14 passed`: only `test_live_tree_has_no_parity_violations` failed. The first line printed: `AssertionError: route walk did not reach a published path: /api/v1/approval-policy`. The failure body held **118** shortfall lines (the first at output line 30, the last, `/readyz`, at line 147; pytest's own `assert not [...]` echo at 148 is not one of them), each beginning `route walk did not reach a published path:`. Edit reverted.

**Acceptance 5 (a), the catalogue red proof on the real tree (09:15:51 BST).** The `dataset:read` row was deleted from `06` §4.1's Built table (`sed -i '/^> | `dataset:read`/d'`, 1 deletion). The run printed `1 failed, 14 passed`; the failure line was exactly `enum member with no 06 §4.1 Built row: dataset:read`. Restored with `git checkout -- docs/specs/06-governance.md` (porcelain showed only the test file).

### Task 4 — the trigger proof (commit 5911f264)

The trigger test passed on the unmodified workflow (`16 passed`, 09:16 BST). Broken-input proof, two runs, each reverted with `git checkout -- .github/workflows/python.yml`:
- deleting `- 'docs/**'` from the `pull_request` block (line 69): the test failed with `python.yml no longer triggers on 'docs/**'`;
- deleting it from the `push` block (line 31): the same failure line.

The full collection is 16 tests: the clean control and nine `test_broken_*` cases (Task 1), the live test (Task 2), four check-site tests (Task 3) and the trigger test (Task 4).

**Acceptance 2 and 3.** Each `test_broken_*` case asserts through `_only`: exact message count and, per class, exactly one message beginning with that class's prefix constant. The `RL-1305` §Acceptance map of `PL-1359` is carried by the test names in the plan's table, unchanged. `test_broken_member_referenced_but_never_checked_has_no_check_site` also asserts that the text-regex proxy counts both members (so it fails under the old predicate).

## Task 4 Step 5 — the permissions.py-only push observed

**Owed. The lead is the owner.** No commit in this slice touches `packages/model-schema/src/model_schema/permissions.py`, and Acceptance 8 forbids one. The line is filled in on the first later push that touches `permissions.py` and no other file (its SHA, the `python.yml` run id it triggered, and that run's result for `tests/test_permission_parity.py`). The workflow's `paths` already show the trigger (Acceptance 6).

## PRs

None yet.

#1049 (draft), branch `sl-1360-permission-parity-check`, opened 2026-10-01 09:19 BST at head `892ffd8fe447e3c9eb2a7daa24c3d29d7907b659`, titled `test(governance): SL-1360 — the permission-parity check (WK-1178, PL-1359, LG 9778)`. Appended, not replaced (the ledger is append-only).

## Gate

Gate of record for the code: head `892ffd8fe447e3c9eb2a7daa24c3d29d7907b659` (tree = this branch's content before this ledger append), on a separate detached worktree (`.claude/worktrees/gate-1360`), `git status --porcelain` empty (0 lines). Lead's grant: 09:20:06 BST, both slots free by `flock -n`.

Condition 5 fields, per run:
- `uv sync --all-packages`: run in the gate worktree; `ruff check --no-cache .`: All checks passed; `mypy --no-incremental`: Success, no issues in 218 source files (09:20:46 BST).
- The dev-commands slot wrapper verbatim, with `LOKY_MAX_CPU_COUNT=4` exported and the pytest stage under `timeout 3300`, run in the foreground under `timeout 3600`. (The harness moved the call to the background at 590 s; the turn stayed open and waited on the gate's pid, which was checked by `readlink /proc/<pid>/cwd`.)
- Both runs took slot `gate-1`; at each end `flock -n` showed both slots free (no other holder).

**Run 1, 09:21:52 to 09:45:48 BST: invalid, environment.** `uptime` at start load 1.74, at end 3.60; `free -h` available 20Gi then 15Gi. The wrapper's per-worktree test database `gipricing_gate-1360_cc93f586` did not exist (the dev-commands block had not been run for the new worktree): 444 errors `InvalidCatalogNameError` and 2 worker-entrypoint failures that need the database. Not a reading of the code. I then ran the once-per-worktree block (`createdb -T gipricing`, `alembic upgrade head`, both rc 0).

**Run 2, 09:46:26 to 10:12:37 BST (26 min 11 s; pytest 1553.69 s), the run of record.** `uptime` at start load 4.47 (another job was running; `free` showed 350Mi free, 6.2Gi available), at end 2.23; end `free -h` available 20Gi.

Stage table as printed (the wrapper's `wrapper final=1`; read from the table):

| stage | result | detail |
|---|---|---|
| ruff | pass | exit=0 |
| mypy | pass | exit=0 |
| import_linter | pass | exit=0 |
| audit_docs | FAIL | exit=1 |
| req_coverage | pass | exit=0 |
| contracts | pass | exit=0 |
| pytest | FAIL | exit=1 |

`GATE: FAIL — 2 of 7 stages failed: audit_docs pytest`. The pytest line: `13 failed, 4503 passed, 3 skipped`.

**Every red is the check-31 family, the gap between 1360 and 9778 that the working id 9778 leaves until the lead mints the id, and nothing else.**
- `audit_docs`: `FAILED (1): check 31: gap in the full allocation between 1360 and 9778`. No other check failed.
- The 13 failed tests (each runs the audit or `doc-id.py check` on the real tree, and each printed that check 31 line or the matching noncontiguous line):
  1. `tests/test_audit_docs_finding_citations.py::test_a_finding_resolved_only_by_a_closure_record_is_not_flagged`
  2. `tests/test_audit_docs_ids.py::test_the_real_tree_passes_all_ten_checks`
  3. `tests/test_audit_docs_ids.py::test_doc_id_check_exits_0_on_the_real_tree` (`doc-id.py check: [noncontiguous] docs/INDEX.md has a gap between 1360 and 9778`)
  4. `tests/test_audit_docs_process_core_digest.py::test_an_unrelated_file_edit_is_the_negative_control_and_stays_green`
  5. `tests/test_audit_docs_process_core_digest.py::test_the_committed_digest_currently_matches_the_committed_spec`
  6. `tests/test_audit_docs_w37_11_ceiling.py::test_audit_docs_end_to_end_exit_0_then_1_then_0_on_an_injected_residue`
  7. `tests/test_doc_index.py::test_an_index_skipping_a_reserved_block_breaks_contiguity` (`the live allocation is not contiguous: [(1360, 9778)]`)
  8. `tests/test_register_lint.py::test_check_29_is_wired_into_the_docs_gate`
  9. `tests/test_register_lint.py::test_check_29_note_carries_the_residue_line`
  10. `tests/test_register_lint.py::test_phase1b_residue_count_matches_check_29s_own_count`
  11. `tests/test_register_owed.py::test_check_29_wiring_is_undisturbed`
  12. `tests/test_repository_invariants.py::test_money_discipline_is_enforced_by_the_docs_audit`
  13. `tests/test_repository_invariants.py::test_journey_citations_are_audited_in_ci`

  The text `check 31: gap in the full allocation between 1360 and 9778` appears 22 times in the pytest log. Zero other failures and zero errors. `tests/test_permission_parity.py` passed in full (16 of 16).

**Frontend half, same worktree, 10:13:17 to 10:14:33 BST** (load 7.89 at end, available 20Gi): `pnpm --dir frontend install --frozen-lockfile` rc 0, `generate:api` rc 0, `lint` rc 0, `type-check` rc 0, `test` rc 0, `build` rc 0.

Acceptance 7 therefore reads: green but for the check-31 family, which clears when the lead mints the id (the ledger then takes its real id and INDEX closes the gap).

**Note (F-B, 2026-10-01 BST):** Task 0's quote of the dispatch record is as of its Delta 1; Deltas 2–4 are in the dispatch record.

### Gate of record on the gate head, 11:19 to 11:51 BST

Gate head `759a524ff6f73c464d9292a75b9da37c174e2456` (the merge of `origin/main` 49cd25be, the LG-1370 mint and the SL-1360 close; the earlier gate at `892ffd8f` above covered the test file, whose content is unchanged). Separate detached worktree `.claude/worktrees/gate-1360b`, `git status --porcelain` empty (0 lines). The lead's slot grant: 11:18:15 BST, both slots free, load 2.00, 19Gi available.

- `uv sync --all-packages` done; `ruff check --no-cache .` All checks passed; `mypy --no-incremental` Success, no issues in 219 source files (11:19:54 BST).
- The per-worktree test database `gipricing_gate-1360b_d95449cd` was created first (`createdb -T gipricing`, `alembic upgrade head`, both rc 0).
- The dev-commands slot wrapper verbatim, `LOKY_MAX_CPU_COUNT=4` exported, pytest stage under `timeout 3300`, foreground under `timeout 3600` (the harness moved the call to the background at 590 s; the turn waited on the gate's pid after `readlink /proc/<pid>/cwd` named this worktree). It took slot `gate-1`; at the end `flock -n` showed both slots free. No other holder was seen at the start (both free) or the end.
- Start 11:21:16 BST: load 2.37, available 20Gi. End 11:49:16 BST: load 1.27, available 21Gi. Wall 28 min 00 s; pytest 1660.59 s (4579 passed, 3 skipped, 57 warnings). Load never rose above the slot's own, so no sign of an overlapping gate; I did not observe WK-675 S1's gate, so I record no contention pair.

Stage table as printed:

| stage | result | detail |
|---|---|---|
| ruff | pass | exit=0 |
| mypy | pass | exit=0 |
| import_linter | pass | exit=0 |
| audit_docs | pass | exit=0 |
| req_coverage | pass | exit=0 |
| contracts | pass | exit=0 |
| pytest | pass | exit=0 |

`GATE: pass — 7 of 7 stages passed` (`wrapper final=0`, read from the table). Check 31 is contiguous through 1370: the audit and the tests that run it are green.

Frontend half, same worktree, 11:49:41 to 11:50:53 BST: `pnpm --dir frontend install --frozen-lockfile`, `generate:api`, `lint`, `type-check`, `test` and `build`, each rc 0.

Acceptance 7 is met on the gate head with no red.

Opened as working id 9778; minted 2026-10-01 as LG-1370.
