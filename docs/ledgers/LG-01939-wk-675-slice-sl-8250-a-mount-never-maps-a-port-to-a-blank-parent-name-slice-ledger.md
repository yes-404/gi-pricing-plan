---
id: LG-1939
family: ledger
title: WK-675 slice SL-1938 — a mount never maps a port to a blank parent name (PL-1937; RL-1876) (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-10-26               # drafted 2026-10-25 under working id 8251
owner: executor
tree: f4422297
phase: P2
work: WK-675
plans: [PL-1937, PL-1546]
corrected_by: []
relates: [PL-1937, PL-1546, RL-1876, SL-1554]
---

# LG-1939 — WK-675 slice SL-1938: a mount never maps a port to a blank parent name

Working ids: this ledger is LG-1939 and its slice SL-1938 (lead 28's reservation, eta 2026-10-25 22:53:50 UTC); `slice:` is left for the mint. Executor seat `exec-8205build`, base `origin/main` 8c3d3013 (re-merged at `f4422297`), branch `draft/pl-8205`, worktree `.claude/worktrees/pl-8205`.

**GO:** the maintainer's entry in `to-lead.md`, header verbatim: "## 2026-10-25 22:52:52 GMT — Maintainer: GO — PL-1937 (WK-675 map delta: a mount never maps a port to a blank parent name; OQ-1843 closed; FD-1936) on `draft/pl-8205` @754efc9b", body:

> Verified by me: tip 754efc9b; RL-1876's squash 18be14a0 and SL-1554's ef3ac6c8 are ancestors of main 8c3d3013; `MountInspector.vue` + its test on main; plan front matter `id: PL-1937, kind: map, status: draft, work: WK-675, phase: P2` (drafted at tree 4e399fd0 — the planner's re-check against 8c3d3013 is accepted as reported: ids re-pointed, dry K2 INDEX re-merge only). Write-set clear as stated (7 open heads touch neither `rating.py` nor 03 §4.1/§10). DP-1 (a) default, DP-2 (a) via SL-1554 — accepted. **GO.** Conditions: (1) reserve the slice's SL + LG working ids now (free-check, then reserve); (2) K2 INDEX re-merge onto the then-current main before the build, decider audit-docs with the sha (own-id check 31 only); (3) build red-first: `graph_invariant_issues` refuses a blank mapped parent name on the mount naming the port; the designer shows it through the validate route (RL-1876 §3); no change to `rating.py`'s shape unless the spec hunk says so; (4) **FD-1936 is filed by the slice's auditor** (findings family, `document-ids.md` §1.6) in the slice audit RS, minted in the slice PR with its register row; (5) red/green/gate lines in the LG before the auditor is seated; (6) gate in a free slot (pairable under the 22:46:19 exception); (7) ids minted at its merge turn — after SL-1553's block unless SL-1553 is not PR-ready when PL-1937 is, in which case PL-1937 goes first and SL-1553's ids follow (merge order = mint order, decided at the PR); (8) one building seat (≤6 building). The plan's `status: draft → active` line rides the slice PR (L1 activation).

**MERGE-ACK:** not yet given.

## Tasks

### Scope

`PL-1937` (draft; its `draft → active` line rides this slice's PR): the one-row WK-675 Work-plan delta, Tasks 1 to 6. A mounted port is never mapped to a blank parent name; `graph_invariant_issues` (`packages/model-schema/src/model_schema/rating.py`) refuses it on the mount naming the port (input `RATING_GRAPH_UNRESOLVED_REF`, output `VALIDATION_FAILED`); the designer shows the refusal through the validate route (`RL-1876` §3); `OQ-1843` closed in both mirrors. Requirements: FR-212, FR-217, FR-1607 (no new FR). FD-1936 is filed by the slice's auditor (GO condition 4), not by this seat.

### Task list

- Step 1 (GO condition 2): K2 INDEX re-merge of `origin/main` 8c3d3013.
- Task 2: red-first tests in `packages/model-schema/tests/test_graph_invariant_issues.py`.
- Task 3: the invariant in `rating.py`.
- Task 4: the designer pin in `frontend/src/components/dag/__tests__/MountInspector.test.ts` (if the plan's hunk calls for it).
- Task 1 spec hunks, as the plan names them (dated, append-only).

### Gate

Not yet run. Owed (see the Build log): the full two-half gate in a free slot on the lead's grant (GO condition 6).

### Audit

Not yet seated (GO condition 5: red/green/gate lines are in this ledger first).

### Build log

Appended per task and per push, never rewritten; every stamp from `date`. Runs: `run-small.sh` and `run-heavy.sh --grant "2026-10-25 22:52:52 GMT"`; the model-schema and frontend files named, no DB.

- **2026-10-25 22:55 GMT, GO condition 2 (K2 re-merge).** `git merge --no-ff origin/main` (8c3d3013) onto 754efc9b; one conflict, `docs/INDEX.md` only, taken from main and regenerated under the gate-2 flock (`doc-index.py --check` rc 0). Merge commit f4422297. Decider `audit-docs.py` via run-heavy on f4422297: rc 1, `FAILED (2)`: "check 31: gap in the full allocation between 1904 and 8205" and "check 31: id 8205 is `created:` 2026-10-23, earlier than id 1904's 2026-10-25 — `created` must be non-decreasing with the number" (own-id check 31 only, as the GO expects).
- **2026-10-25 23:01 GMT, Task 2 RED**, `bash run-small.sh <wt> packages/model-schema/tests/test_graph_invariant_issues.py`, run on tree fc68e16a plus the test file, committed as 4290018b: rc 1, `3 failed, 10 passed`. FAILED: `test_an_input_port_mapped_to_a_blank_name_is_refused_naming_the_port[]`, `[  ]` (message names `''`, not the port: `assert "'claims'" in "step 's_ncd' consumes undefined value '' (FR-212)"`) and `test_an_output_port_mapped_to_a_blank_name_is_refused_naming_the_port` (`assert 0 == 1`, no issue). The control for non-blank names is `test_a_pinned_mount_is_a_node_its_outputs_resolve` (already in the file, same fixture shape), which passes; no new control test was added.
- **Task 1 spec**, 197a7df4: `03` §4.1 mount clause and `RL-1474` order clause (both dated 2026-10-25, `RL-1876`), `OQ-1843` decided in `docs/open-questions.md` and `03` §10, `docs/roadmap.md` §10 row recounted to `1 (0 open)`. `req-coverage.py` rc 0. `audit-docs.py` on that tree: rc 1, own-id check 31 only, plus check 39 (INDEX stale) which regenerating `docs/INDEX.md` cleared (`doc-index.py --check` rc 0).
- **Task 3 GREEN**, 0a85d0cb (`rating.py`: blank-name check after the duplicate/mount_point early return, blank names left out of `purpose_only` and the `_MountNode`s): `run-small.sh` on `test_graph_invariant_issues.py` rc 0, `13 passed`. `ruff check` on `rating.py` rc 0. `ruff format --check` on `rating.py` rc 1 on hunks this slice did not touch (lines 57, 277, 751, 873, 1219, 1481, 1623: the file was already unformatted at base); none of the slice's lines is in the diff it prints.
- **Broken input (acceptance 4)**: with `if not name.strip():` replaced by `if False:` (uncommitted, reverted at once), the same run: rc 1, `3 failed, 10 passed`.
- **Task 4**, a966d375: `MountInspector.test.ts`, one case (a cleared input port stays `""`). `vitest run src/components/dag/__tests__/MountInspector.test.ts` rc 0, `Test Files  1 passed`, `Tests  9 passed`. Broken input (acceptance 9): `setInput` changed to delete the key on `""` (uncommitted, reverted at once): rc 1, `1 failed | 8 passed`. `eslint` on the test file rc 0.
- **Owed to the gate:** `vue-tsc` type-check (whole-project), the import-closure GREEN set (common brief item 29), `mypy` (a single-file run reports a pre-existing `rating.py:35` import error under the bare invocation, so the project `uv run mypy` is the decider), the full two-half gate, acceptance items 1, 6, 7, 8, 10, 12.
- **2026-10-25 23:54 GMT, owed `vue-tsc` (run-heavy, grant, non-light), head dc4f061a1f4b7b36bbb969bed3bb5d6035f26348.** `pnpm install --frozen-lockfile`, `generate:api`, `vue-tsc --build --force`: rc 0 (finished 2026-10-25 23:52:20 GMT; log `exec-8205chk-step1.log`, carries `head=dc4f061a…` and ends `rc=0`).
- **2026-10-25 23:54 GMT, owed project `mypy` (run-heavy, grant), head dc4f061a1f4b7b36bbb969bed3bb5d6035f26348.** `uv run --directory <wt> mypy`: `Success: no issues found in 250 source files`, rc 0 (finished 2026-10-25 23:53:52 GMT; log `exec-8205chk-step2.log`).

- **2026-10-26 02:27 GMT, Audit.** RS-1940 (aud-8205, @d51b98c9) proposed CLEAN, ADOPTED CLEAN by the lead; accepted at to-lead 2026-10-25 23:40:16 GMT. Folded into this branch by the merge of `origin/aud-8205-2026-10-25` (blobs of RS-1940 and FD-1936 identical to d51b98c9).
- **2026-10-26 02:27 GMT, Gate of record.** Full code gate @40ca2645 (scratch/pl8205-gate/gate/): END rc=1, parts python 1 / fe 0 / demo 0 / restore rc_kc 0; rc files audit_docs=1 contracts=0 import_linter=0 mypy=0 pytest=1 req_coverage=0 ruff=0; pytest 13 failed (the 1(f) set) / 6896 passed / 21 skipped; audit_docs FAILED (3) = check 31 on own ids 8205/8251 incl. the created-order line; demo designed stop rc 0 (885 s); restore rc 0 - STANDS under 1(f), to-lead 2026-10-26 02:23:16 GMT.
- **2026-10-26 02:27 GMT, Delta.** The 40ca2645-vs-dc4f061a delta = LG-1939 +2 only (`git diff --stat dc4f061a 40ca2645`: one file changed, 2 insertions(+)).

## PRs

Not yet opened.
