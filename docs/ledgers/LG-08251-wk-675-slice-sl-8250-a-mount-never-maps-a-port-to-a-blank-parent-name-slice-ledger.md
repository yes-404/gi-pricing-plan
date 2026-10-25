---
id: LG-8251
family: ledger
title: WK-675 slice SL 8250 — a mount never maps a port to a blank parent name (PL-8205; RL-1876) (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-10-25
owner: executor
tree: f4422297
phase: P2
work: WK-675
plans: [PL-8205, PL-1546]
corrected_by: []
relates: [PL-8205, PL-1546, RL-1876, SL-1554]
---

# LG-8251 — WK-675 slice SL 8250: a mount never maps a port to a blank parent name

Working ids: this ledger is LG 8251 and its slice SL 8250 (lead 28's reservation, eta 2026-10-25 22:53:50 UTC); `slice:` is left for the mint. Executor seat `exec-8205build`, base `origin/main` 8c3d3013 (re-merged at `f4422297`), branch `draft/pl-8205`, worktree `.claude/worktrees/pl-8205`.

**GO:** the maintainer's entry in `to-lead.md`, header verbatim: "## 2026-10-25 22:52:52 GMT — Maintainer: GO — PL 8205 (WK-675 map delta: a mount never maps a port to a blank parent name; OQ-1843 closed; FD 8204) on `draft/pl-8205` @754efc9b", body:

> Verified by me: tip 754efc9b; RL-1876's squash 18be14a0 and SL-1554's ef3ac6c8 are ancestors of main 8c3d3013; `MountInspector.vue` + its test on main; plan front matter `id: PL-8205, kind: map, status: draft, work: WK-675, phase: P2` (drafted at tree 4e399fd0 — the planner's re-check against 8c3d3013 is accepted as reported: ids re-pointed, dry K2 INDEX re-merge only). Write-set clear as stated (7 open heads touch neither `rating.py` nor 03 §4.1/§10). DP-1 (a) default, DP-2 (a) via SL-1554 — accepted. **GO.** Conditions: (1) reserve the slice's SL + LG working ids now (free-check, then reserve); (2) K2 INDEX re-merge onto the then-current main before the build, decider audit-docs with the sha (own-id check 31 only); (3) build red-first: `graph_invariant_issues` refuses a blank mapped parent name on the mount naming the port; the designer shows it through the validate route (RL-1876 §3); no change to `rating.py`'s shape unless the spec hunk says so; (4) **FD 8204 is filed by the slice's auditor** (findings family, `document-ids.md` §1.6) in the slice audit RS, minted in the slice PR with its register row; (5) red/green/gate lines in the LG before the auditor is seated; (6) gate in a free slot (pairable under the 22:46:19 exception); (7) ids minted at its merge turn — after SL-1553's block unless SL-1553 is not PR-ready when PL 8205 is, in which case PL 8205 goes first and SL-1553's ids follow (merge order = mint order, decided at the PR); (8) one building seat (≤6 building). The plan's `status: draft → active` line rides the slice PR (L1 activation).

**MERGE-ACK:** not yet given.

## Tasks

### Scope

`PL-8205` (draft; its `draft → active` line rides this slice's PR): the one-row WK-675 Work-plan delta, Tasks 1 to 6. A mounted port is never mapped to a blank parent name; `graph_invariant_issues` (`packages/model-schema/src/model_schema/rating.py`) refuses it on the mount naming the port (input `RATING_GRAPH_UNRESOLVED_REF`, output `VALIDATION_FAILED`); the designer shows the refusal through the validate route (`RL-1876` §3); `OQ-1843` closed in both mirrors. Requirements: FR-212, FR-217, FR-1607 (no new FR). FD 8204 is filed by the slice's auditor (GO condition 4), not by this seat.

### Task list

- Step 1 (GO condition 2): K2 INDEX re-merge of `origin/main` 8c3d3013.
- Task 2: red-first tests in `packages/model-schema/tests/test_graph_invariant_issues.py`.
- Task 3: the invariant in `rating.py`.
- Task 4: the designer pin in `frontend/src/components/dag/__tests__/MountInspector.test.ts` (if the plan's hunk calls for it).
- Task 1 spec hunks, as the plan names them (dated, append-only).

### Gate

Not yet run. Owed: the full two-half gate in a free slot on the lead's grant (GO condition 6).

### Audit

Not yet seated (GO condition 5: red/green/gate lines are in this ledger first).

### Build log

Appended per task and per push, never rewritten; every stamp from `date`.

## PRs

Not yet opened.
