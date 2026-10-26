---
id: RS-1940
family: research
kind: audit
title: SL-1938 (WK-675, PL-1937) slice audit — a mount never maps a port to a blank parent name (RL-1876, FR-217), at draft/pl-8205 dc4f061a
status: draft
created: 2026-10-26               # drafted 2026-10-25 under working id 8254
owner: auditor
tree: dc4f061a1f4b7b36bbb969bed3bb5d6035f26348
phase: P2
work: WK-675
corrected_by: []
relates: [PL-1937, LG-1939, RL-1876, OQ-1843, FD-1936, FR-212, FR-217, FR-1607]
---

# RS-1940 — SL-1938 (WK-675, PL-1937) slice audit

## Question

Does `draft/pl-8205` at dc4f061a (working id SL-1938, ledger LG-1939) meet the GO of the maintainer's
entry "2026-10-25 22:52:52 GMT" (conditions 1–8) and PL-1937's Acceptance Standard, and can it go to
the gate? Also: file FD-1936 (GO condition 4).

## Method

Scope from the GO and the plan row first, then evidence. Range `8c3d3013...dc4f061a` (merge-base of
the head and origin/main; origin/main now 0dc2fa71). `git diff --name-only`, each changed file read,
`git merge-base --is-ancestor` for each red/spec/code pair, LG-1939's Build log read for sha + rc.
Read-only: no test, no gate, no heavy command was run by this seat; every run line below is the
executor's, quoted from LG-1939, not re-measured. Tree for all reads: dc4f061a.

Diff files: INDEX, LG-1939, PL-1937, `open-questions.md`, `roadmap.md`, `03-rating-engine.md`,
`rating.py`, `test_graph_invariant_issues.py`, `MountInspector.test.ts`. Nothing under
`docs/contracts` or `frontend/src/api/generated`; no new `FR-` row (`grep -cE '^\+\| \*\*FR-[0-9]+\*\*'` = 0);
barred-word count on added lines = 0.

## Findings

Class B = blocking, N = non-blocking. **There is no B finding.**

### GO conditions

| # | Condition | Verdict | Evidence |
|---|---|---|---|
| 1 | SL + LG ids reserved | met | LG-1939 header: "LG-1939 and its slice SL-1938 (lead 28's reservation, eta 2026-10-25 22:53:50 UTC)" |
| 2 | K2 INDEX re-merge, decider with sha | met | merge f4422297 (parent 754efc9b + origin/main 8c3d3013); LG: `audit-docs` rc 1, own-id check 31 only (2 lines quoted); `doc-index --check` rc 0 |
| 3 | red-first; refusal names the port; validate route; `rating.py` shape | met | below |
| 4 | FD-1936 filed by the auditor | met by this record | FD-1936 + register row in this branch |
| 5 | red/green/gate lines in LG before the auditor | met for red/green/broken-input; gate owed (see N3) | LG Build log |
| 6 | gate in a free slot | owed | LG "Gate: Not yet run" |
| 7 | ids minted at merge turn | owed (mint time) | LG "PRs: Not yet opened" |
| 8 | one building seat | not an audit object | — |

### Condition 3 and the ordering checks

- Spec before code: `merge-base --is-ancestor 197a7df4 0a85d0cb` rc 0. 197a7df4 touches only INDEX,
  `open-questions.md`, `roadmap.md`, `03` (4 files, +8/−6).
- Red before code: `--is-ancestor 4290018b 0a85d0cb` rc 0; 4290018b changes only
  `test_graph_invariant_issues.py` (+28/−1), on parent fc68e16a, where `rating.py` equals base.
  LG red line: rc 1, `3 failed, 10 passed`, FAILED lines are the two input parametrizations
  (message names `''`, not the port) and the output test (`assert 0 == 1`) — the cause the plan's
  acceptance item 2 names. Green (0a85d0cb): rc 0, `13 passed`.
- Broken input: LG re-red with `if not name.strip():` → `if False:`, rc 1, `3 failed, 10 passed`;
  frontend `setInput` broken to delete the key: rc 1, `1 failed | 8 passed`; both reverted at once
  (rating.py and the test file at head show the real check).
- `rating.py` shape: diff is `graph_invariant_issues` only (docstring, one `Iterable` import, the
  blank-name loop, a local `_named`, a changed return `[*issues, *found.values()]`). No field,
  signature, public name or contract change. The spec hunk (`03` §4.1 clause, and the RL-1474 order
  clause "checked after a duplicate `step_id` and before a declared output with no output step")
  matches the code order: the blank check runs after the early return on duplicates and before the
  per-purpose passes where unresolved refs and the FR-214 output check are produced. Codes match the
  spec: input `RATING_GRAPH_UNRESOLVED_REF` naming the port as unmapped; output `VALIDATION_FAILED`.
- Acceptance 5 (one issue, not two): the input test asserts no `consumes undefined value` message and
  `[(code, step_id)]` is exactly one issue. Met by the test text.
- Acceptance 6/8/12 by diff reading: contracts/generated empty; no FR row added; barred word 0.
  (`generate-contracts --check` and `req-coverage.py` not re-run by this seat; the LG records
  `req-coverage.py` rc 0 at 197a7df4.)
- Acceptance 7: `OQ-1843` struck and decided by RL-1876 in `open-questions.md`, `03` §10 and the
  `roadmap.md` §10 row (line 3646), whose last cell reads `1 (0 open)` (read at dc4f061a).
- Frontend: only `MountInspector.test.ts` touched (one case). `MountInspector.vue` is
  `<script setup lang="ts">` and untouched, as the plan's out-of-scope says. No hand-written API
  shape; the case uses the file's own `FEES`/`PINS` fixtures.
- Write set (acceptance 10): the 9 files listed are all within the plan row's write set plus INDEX
  and the LG; FD-1936 and the register row are added by this record.

### Findings list

- **N1 — no separate control test.** PL-1937 Task 2 / acceptance 2 name three cases (input blank,
  output blank, control). The slice has two tests (input parametrized `""`/`"  "`, output). LG-1939
  discloses it and names the existing `test_a_pinned_mount_is_a_node_its_outputs_resolve` as the
  control. Evidence: LG Build log, Task 2 RED line. Accept as disclosed; no action.
- **N2 — activation and SL row ride the PR.** PL-1937 is `status: draft` at head and the roadmap has
  no SL-1938 row yet; the GO says the `draft → active` line rides the slice PR and the plan names
  the SL row for the minter. Owed at the mint, not a defect of this build.
- **N3 — owed to the gate and the decider.** LG-1939 "Owed to the gate": `vue-tsc`, project
  `mypy`, the import-closure GREEN set (common brief item 29; the model-schema members
  `test_graph_invariant_issues.py` and `test_rating_algorithm.py` and the closure beyond it),
  `generate-contracts --check`, `req-coverage`, and the full two-half gate. `ruff format --check` on `rating.py` is rc 1 on pre-existing hunks at base
  (LG: lines 57, 277, 751, 873, 1219, 1481, 1623, none in this diff); the gate's `ruff check` is
  the decider. None of these can be judged by reading; they are the gate's.
- **N4 — FD-1936 is open until merge.** Filed `active`, with the register row's
  "Resolved by this slice (SL-1938)" line. Setting it `closed` and adding the merge sha follow
  the merge (role file: closed in place citing the PR). FD-1936's own front-matter ids exclude the
  unminted SL-1938 (a front-matter id must resolve); the minter adds it.
- FD filed by this audit: **FD-1936** (LOW, owner WK-675; the mount-output hole RL-1876 found,
  fixed by this slice). No other FD.

### Four verdicts for requirements without evidence

FR-212, FR-217, FR-1607: no new FR; evidence is the three `@pytest.mark.req("FR-217")` cases and
the existing FR-212/FR-1607 tests, run green by the executor (13 passed). FR-1607's route is
unchanged and reports the new issue because it calls the one function. A name rule for every
value name (RL-1876 item 5) is not started: out of this slice by the plan, left to a new OQ the
lead raises.

### Proposed verdict

**CLEAN** for the build at dc4f061a, with the owed list N2, N3, N4 carried to the gate and the
mint. The lead adopts, amends or rejects.

### Owed list

1. Full two-half gate in a free slot (GO 6) and the import-closure GREEN set; `vue-tsc`, `mypy`.
2. Decider `audit-docs` with the sha at the mint; `doc-index --check` (this seat: rc 0, byte-stable, after regenerating INDEX).
3. PL-1937 `draft → active`; SL-1938 row in `roadmap.md`; mint of SL, LG, RL cites, RS-1940 and
   FD-1936 in merge order (GO 7), whole-tree id grep per common brief item 26.
4. FD-1936 `closed` with the PR and merge sha, after the merge.
