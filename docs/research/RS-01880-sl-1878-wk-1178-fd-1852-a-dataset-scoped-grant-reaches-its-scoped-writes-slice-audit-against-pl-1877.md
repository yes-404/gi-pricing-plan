---
id: RS-1880
family: research
kind: audit
title: SL-1878 (WK-1178, FD-1852, a dataset-scoped grant reaches its scoped writes) slice audit against PL-1877, at 01eb5b05
status: draft
created: 2026-10-25                  # drafted 2026-10-25 under working id 8216; minted 2026-10-25 as RS-1880
owner: auditor
tree: 07391bb1f142733e71408eea7109ec2b0fba1e14
phase: P2
work: WK-1178
corrected_by: []
relates: [SL-1878, PL-1877, LG-1879, FD-1852, FD-1853, RL-1849, FR-343, FR-345, FR-452]
---

# RS-1880 — SL-1878 slice audit

*(Working id 8216, reserved by the lead. Written by `aud-8185` (Sonnet 5.5), 2026-10-25 UTC, from the brief `brief-aud-8185-2026-10-25.md` (lead 28). Check 31/32 on this id is expected until the mint. I propose a verdict; the lead adopts it. I fixed nothing.)*

## Question

Does `origin/main...origin/sl-8185-wk1178-fd8177-scoped-writes` meet the Acceptance Standard of PL-1877, and what does LG-1879 fail to evidence?

## Method

**Audited head:** `01eb5b05` ("Merge origin/main (ff976406) into sl-8185-…", tree `07391bb1f142733e71408eea7109ec2b0fba1e14`). The brief named `ac46ee7a`; the branch moved to `01eb5b05` while I worked. `git diff --name-only ac1dce42 origin/sl-8185-…` filtered by `grep -v '^docs/'` prints nothing: **every code and test byte of the slice is the one at `ac1dce42`**; all later commits are docs. `git merge-base --is-ancestor origin/main origin/sl-8185-…` rc 0 (main `ff976406` is in the head).

**Scope first.** The plan is not on the slice branch: PL-1877 is `docs/plans/PL-01877-…plan-delta.md` on `origin/draft/pl-8181` (head `c6f93d5d`, 506 lines) only (see B2). I derived the scope from its *Acceptance Standard* items 1 to 6, its Tasks 1 to 6, and the later rulings that change them: the maintainer's entries "2026-10-22 18:16:19 BST" (Task 4 carried), "2026-10-22 18:21:15 BST" (a load 404 is counted, DP-3 (b)), and "2026-10-23 10:48:01 BST" (C) (`ac1dce42` is "exactly the guard working"). All three read in `~/gi-pricing-plan.local/channel/to-lead.md` (lines 29797, and the 10:48:01 heading at 30126).

**Ledger SHAs.** Twelve SHAs LG-1879 cites as evidence (`40015b55 9b6c21bd f1454fc1 a5c49742 5c77f030 40de35f5 3f9c9155 66dbe5fb 3c39fd8b ac1dce42 d7d9727a 7d3f5b09`): every one exits 0 under `git merge-base --is-ancestor <sha> origin/sl-8185-…`. Two-way pairing: every Task row of the LG pairs with a commit above; every commit of `git log origin/main..origin/sl-8185-…` (21, plus the head merge) is a task, a merge, a docs or a ruled fix commit.

**Tests run by me:** none. Every criterion was decidable by reading, except the head-state DB run of AS 1, which needs a database and a gate slot; it is owed (below). Load1 read first: 3.31 (11:08 UTC); gate-1 held by slice A, so no heavy command ran.

## Scope against evidence

| # | Acceptance item (PL-1877) | Evidence found | Proposed verdict |
|---|---|---|---|
| AS1 | `test_dataset_scoped_writes.py`: exactly 13 red at base (rc 1); exit 0 at the head | **Base:** `~/gi-pricing-plan.local/scratch/sl-8185/task2-red-base.log`, line 1 `head=f1454fc1…`, `13 failed, 10 passed in 20.57s`, `rc=1`; the 13 names match the plan's list (3 routes × in-scope, out-of-scope, scoped-unknown-id, count-scoped = 12, plus DP-3's split = 13). **Head:** the last DB-backed run is `dp3b-green.log` (`35 passed, 5 xfailed`, rc=0, run on the tree of `66dbe5fb`; its `head=` line names `3c39fd8b`, the red test commit, because the fix was an uncommitted tree). The file now holds 4 strict xfails (rule-set; Task 4 carried by the maintainer, 18:16:19) and the DP-3 (b) test. **No DB-backed run of this file exists after the three re-merges** (`d7d9727a`, `134e8663`/`abeaf05d`, `01eb5b05`), only 14 DB-free closure files. | **Met at `66dbe5fb`; OWED at the head** (gate) |
| AS2 | Guard: base + guard file names exactly the 3 routes; head whole file exits 0 incl. both synthetic-route tests and the stale-exclusion test | `task5-red-base.log` line 1 `head=a5c49742…`: `2 failed, 7 passed`; the app-wide test names exactly the dictionary, rule-set and acknowledge routes; the second failure is the injection test (`TypeError: … 'held_anywhere'`, expected at base). The run used the guard file with the rule-set gap row removed (disclosed in LG), not "base + file only". **Head:** `ac1dce42-small-guard.log`, `10 passed, 2 warnings in 1.42s`, on the code tree that is the head's (no non-docs diff). I read `test_route_scope_guard.py` at the head: `ROUTE_SCOPES` has **48** rows, `KNOWN_SCOPE_GAPS` **26** (1 + 20 + 5, parsed from the file). The log has no `head=`/`rc=` lines (it predates brief item 37, 12:02 BST 2026-10-23). 5 mutations red (`task5-mutations.log`). `ac1dce42` is the guard's completeness test catching SL-1260's route: the maintainer noted it as "exactly the guard working". | **Met** |
| AS3 | Every `KNOWN_SCOPE_GAPS` row names an owner and a removing slice; stale-exclusion test exits 0; the LG quotes the row count | Owners are `RL-1849` (20), `FD-1853` (5), `SL 8192` (1); these re-point the plan's "RL 8182" and "FD 8184" to the minted records, which exist on the branch (`docs/rulings/RL-01849-…`, `docs/findings/FD-01853-…`). The owner test accepts a hyphen-form working id. The LG quotes **47** `ROUTE_SCOPES` rows, which became 48 at `ac1dce42`. | **Met, with B1 and B3** |
| AS4 | `test_api_authorisation_sweep.py`, `test_management_429_declared.py` pass with no diff | `git diff --stat origin/main...origin/sl-8185-… -- <both paths>` prints nothing (rc 0). Adjacent run `task3-adjacent.log` rc=0; `d7d9727a-small-aa.log` (`test_management_429_declared.py`) `18 passed`, rc=0. | **Met** |
| AS5 | Spec diff touches only FR-343 and FR-345 rows, carrying DP-2's texts; `audit-docs` clean there | `git diff origin/main...origin/sl-8185-… --stat -- docs/specs`: one file, `06-governance.md`, 2 lines (the FR-343 and FR-345 rows). `git diff --word-diff=porcelain -U0` shows additions only, no removed word: FR-343 gains its own dated pointer sentence; FR-345 gains "Order and count" plus the two 17:46:43 sentences. LG records `audit-docs` rc 0 at Task 1. The FR-345 text states the load-404-counted rule of 18:21:15. | **Met** |
| AS6 | The slice gate (both halves) is green at the head | **Not run to completion.** LG-1879 closing line: gate on `7d3f5b09` aborted at the python half, pytest 76%, on the user's pause 2026-10-23 12:14 BST; ruff, mypy, import-linter, req-coverage, contracts rc 0, `audit-docs` rc 1 "not yet analysed". The aborted run is not a gate. I also found no frontend-half record. | **OWED: re-run on the lead's grant** |
| T3 | `requires(held_anywhere=True)`; `TypeError` with a counted gate; dictionary and acknowledge switched; DP-3 split | `backend/src/app/api/authz.py` (head): `held_anywhere and management_counted` raises `TypeError`; the dependency admits on `permission.value in caller.permissions` or `rbac.holds_anywhere`, else `PermissionDeniedError(…, held_elsewhere=False)`; never counts; stamps `RESOURCE_CHECKED_IN_HANDLER_ATTRIBUTE`. Credential permissions only add (`rbac.py:201`, `granted` is a set union), so the route gate cannot widen a credential's ceiling. `platform/validation.py` raises `SCOPE_DENIED` when `holds_anywhere`, else keeps `ACKNOWLEDGE_FORBIDDEN_ROLE`. | **Met** |
| T4 | Rule-set route | Carried to SL 8192 by the maintainer (18:16:19, option (a)): `platform/validation_rules.py` untouched (not in the diff); 4 strict xfails; gap row owned by `SL 8192`. | **Reassigned, ruled** — but see B1 |
| T5 | Permanent guard, AST, red twice, extended predicate, owned exclusions | See AS2. Three synthetic/mutation reds exist; the table-driven predicate 2 and the completeness test are present. | **Met** |
| T6 | GREEN by import closure | 48 modules, 113 then 115 files; 12 DB-backed files ran in 4 batches before the loop was stopped (batch 4's summary line was lost; the LG says so), and 14 DB-free files re-ran after the merge (2 of the 5 batches red or errored: the `ac1dce42` row, and DB setup errors owed to the gate); the remaining 101 wait for the gate, which the LG calls decisive. | **Delivered but untested at the head** (gate owed) |

## Findings

| # | Severity | Finding | Exact remedy |
|---|---|---|---|
| B1 | MEDIUM | **The follow-on slice is named, not registered.** The maintainer's 18:16:19 entry: "Register the follow-on now: an SL working id for the micro-slice (Task 4 only), with SL-1736's merge as its activation need. LG-1879 names it, so it is not orphaned." `git grep -n -E "SL[- ]8192" and "LG[- ]8193" origin/sl-8185-… -- docs/roadmap.md docs/INDEX.md` finds one hit: prose in the SL-1878 roadmap row (`docs/roadmap.md:2985`). There is no SL 8192 row and no LG 8193. The guard's owner test (`test_every_known_gap_names_an_owner_in_the_index`) passes because it also accepts any hyphen-form working id, so the rule-set gap row's owner is not backed by any record. | Before the PR: add an `SL 8192` row under WK-1178 (activation need SL-1736 merged, Task 4 only, the four xfail tests) in `docs/roadmap.md`, and file `LG 8193` as a stub, minted with the slice's other ids. The lead may instead rule the prose sufficient, in an RL. |
| B2 | MEDIUM | **PL-1877 is on no mergeable branch.** It lives only on `origin/draft/pl-8181` (`c6f93d5d`); it is absent from the slice branch and from `origin/main` (`git grep -l "PL-1877" origin/main -- docs` prints nothing). The slice's LG, roadmap row, guard comments and `relates:` fields cite it. After the slice merges, `PL-1877` resolves nowhere. | At the mint (brief item 34's form): fold the plan file from `draft/pl-8181` into the slice branch, mint `PL-1877`, re-point every cite, then `audit-docs` rc 0. |
| B3 | LOW | **LG-1879 is stale in three places.** (i) `### Gate` still says "not yet run … Table empty", while the Build log ends with the aborted run; the Gate table has no row for it. (ii) Front matter `tree: 40de35f5…` (Task 5), not the head. (iii) Counts: "`ROUTE_SCOPES` 47 rows" is 48 at the head (`ac1dce42` added one). The `### Audit` section reads "Not yet written". | Update the Gate table with the aborted run as an explicit not-a-gate row, correct the count to 48, refresh `tree:`; the audit section is filled from this record. (The lead's choice whether the Audit section quotes RS-1880 or the RS is the record.) |
| B4 | LOW | **Evidence weakness in two logs.** `dp3b-green.log` carries `head=3c39fd8b` (the red test commit) for a run on the fix tree later committed as `66dbe5fb`; the DP-3 (b) green is therefore not tied to a commit by the log itself. The `d7d9727a-*` and `ac1dce42-small-guard.log` files have neither `head=` first nor `rc=` last (item 37 dates after them). | None needed beyond the gate: the head re-run supersedes both. Record the head and rc of the gate run in the LG. |
| O1 | observation | The guard's gap-owner of 20 rows is `RL-1849` and "the slice RL-1849 cuts": no slice id exists yet. This is by design (the maintainer's 17:36:24 entry) and not a finding. | — |

No product-code defect found. Read: `authz.py` (+34), `datasets.py` (+9), `validation.py` (+4), `platform/datasets.py` (+15), `platform/validation.py` (+26). No FD is filed by this audit.

## Gate evidence

| Item | Result |
|---|---|
| Gate on `7d3f5b09` (python half) | **ABORTED at pytest 76%**, 2026-10-23 12:14 BST, user pause. Not a gate. |
| Re-run at the head | **OWED** (lead's GATE GO; both halves; the MERGE-ACK quotes its `passed` line). The re-run must also cover the 101 DB-backed closure files and AS 1 at the head. |
| Static: ruff / mypy | LG: clean at `40de35f5` and on changed files since; not re-run by me (no code change since). |

## Proposed verdict

**CLEAN with conditions — the slice's code, tests and spec meet PL-1877's Acceptance Standard items 2 to 5 and its tasks as ruled; items 1 (at the head) and 6 are OWED to the gate, and B1 and B2 must be discharged at the mint.** If the lead holds that an owed gate makes the audit NOT-CLEAN, read it as NOT-CLEAN on B1, B2 and the gate alone; no B item is a code defect. The verdict is the lead's.

## Commands run (aud-8185, tree `ff976406` in my worktree unless named)

`git fetch origin` rc 0; `git rev-parse` of main and the slice head; `git merge-base --is-ancestor <sha> origin/sl-8185-…` for 12 SHAs, all rc 0; `git diff --stat`/`--name-only`/`--word-diff` between `origin/main...origin/sl-8185-…`; `git grep` for PL-1877, SL 8192, LG 8193; reads of the plan, LG, `authz.py`, `rbac.py`, the diff of `backend/src`, and `test_route_scope_guard.py` (AST-parsed row counts). Docs checks: see the commit report.

Adopted 2026-10-25 by the lead: CLEAN; B1 met as worded by to-lead 2026-10-22 18:16:19 BST (a); B2/B3 discharged d37510be; B4 superseded by the gate re-run.
