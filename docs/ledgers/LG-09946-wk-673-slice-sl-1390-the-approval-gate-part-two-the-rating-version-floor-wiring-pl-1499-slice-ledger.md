---
id: LG-9946
family: ledger
title: WK-673 slice SL-1390 — the approval gate, part two — the rating_version floor wiring (PL-1499), slice ledger
status: active
created: 2026-10-10
owner: executor
tree: db0642c4b4f87e71dceff36d1ebd7c7ba4ef68f9
phase: P2
work: WK-673
slice: SL-1390
plans: [PL-1499]
corrected_by: []
relates: [PL-1499, RL-1504, RL-1445, RL-1263, SL-1389, FR-363, FR-364, FR-257, FR-352]
---

# LG-9946 — WK-673 slice SL-1390: the approval gate, part two — the floor wiring

**GO:** given, "2026-10-10 21:35:23 BST — DISPATCH GO: WK-673 Slice 6 (PL-1499 / SL-1390; PL-1544 need 6), with rulings 1–6" (`to-lead.md`, local); the original line read: not yet given. Authoring ahead of the GO at the user's order (the lead's brief `brief-executor-s6-authoring-2026-10-10.md`, local, authority "2026-10-10 03:07:11 BST — W3 pacing"): code and tests are written on a branch from `origin/main` `db0642c4b4f87e71dceff36d1ebd7c7ba4ef68f9`; no PR and no gate before the GO.
**MERGE-ACK:** not yet given.

## Tasks

### Scope

The slice's Work-plan row is `PL-1499`, slice `SL-1390`, WK-673 Slice 6: *"the approval gate, part two — the floor wiring"*. Its scope is `PL-1499` §"Scope" and §"Write set, and its contention", read at this branch's tree. Requirement ids covered: `06` FR-364, FR-363 (for `rating_version`), `03` FR-257 limbs (1) and (2) (re-routed, no new limb). DP-S6-1 is ruled (c) by `RL-1504` item 11; its T6 is the spec text Task 1 applies.

Per `Lean P2 L1 (a')` the slice's one PR sets `PL-1499`'s `status:` line to `active` (this branch's first commit) and closes this ledger and `SL-1390`'s roadmap row at its head.

Write set: `backend/src/app/platform/rating_versions.py` (`submit_for_review` and the verifier wrappers only), `docs/specs/06-governance.md` (FR-364, appended), `backend/tests/test_rating_version_evidence_floor.py` (new), this file, `docs/INDEX.md` (regenerated). Any other path is a stop to the lead. Not `compile.py`, `errors.py`, `packages/` or any route.

### Task list

Order and acceptance checks are `PL-1499` §"Tasks" and §"Acceptance Standard" (items 1 to 10). Each task below is added with its commit when it is pushed.

| Task | Commit | What |
|---|---|---|
| 0 | `eb096345` | PL-1499 active; this ledger; Task 0 steps 1–4 (step 5 OWED) |
| 1 | `ff630eef` | `06` FR-364 dated amendment (RL-1504 T6), appended at the row's end |
| 2 (tests) | `37a4ffa3` | `backend/tests/test_rating_version_evidence_floor.py`, Acceptance 1–4, 7, 10 |
| 2 (code) | `26f811e5` | the floor loop in `submit_for_review` |
| 2 (order pin) | `ae18907b` | `test_the_floor_is_checked_in_floor_order_and_the_diff_blob_is_stored_first` (ruling 3) |
| 2 (comment) | `e909db56` | the `FD 9952` comment re-pointed to FD-1589, comment only (ruling 6) |
| 3 | not started | gate and close: after the gate slot and the lead's merge word |

### Gate

| Command | rc | Tree | Excerpt |
|---|---|---|---|
| (empty: no gate yet; the gate runs after the lead's "gate slot granted" for the head) | | | |

### Audit

(Written by the auditor at slice close.)

### Build log

**2026-10-10, authoring phase.** Worktree `.claude/worktrees/sl-1390`, branch `sl-1390-wk673-s6-floor-wiring`, from `origin/main` `db0642c4b4f87e71dceff36d1ebd7c7ba4ef68f9` (`SL-1389` merged, #1260). Stamps are BST (`TZ=Europe/London date`). The gate-1 slot is held by A-2's code gate: no tests run while it does; DB tests are authored and marked OWED.

- Commit 1: `PL-1499`'s `status:` line `draft` to `active` (the 2026-10-09 13:29:49 BST ruling, item 3, `L1 (a')`), and this file.
- **Task 0, Step 1 (activation needs).** Need 2 (`SL-1389` closed): MET, #1260 `db0642c4`. Need 3 (the DP-S6-1 ruling): MET, `RL-1504` is on `origin/main`, item 11 = option (c). Need 1 (plan active): this commit. Needs 4 and 5 (lane, GO): the lead's, at the merge turn.
- **Task 0, Step 2:** `uv sync --directory <wt> --all-packages` ran.
- **Task 0, Step 3 (stored kinds outside the floor).** `git grep -n "rate_table_diffs\|gipp_check_if_enabled\|change_summary" -- examples backend/src`, at `db0642c4`: no seed policy (`examples/`) and no `backend/src` policy default names `rate_table_diffs` or `gipp_check_if_enabled`; every `change_summary` hit is the submit argument or column. No stored policy is refused by DP-S6-1 (c) from the seeds. Contention re-check: A-2 and A-3 edit `compile_rating_version`'s region of `rating_versions.py`; this slice stays inside `submit_for_review` and the verifier wrappers (hunks checked by `git diff -U0` at the merge turn).
- **Task 0, Step 4 — deltas from the plan's `137bc817` citations (merged code governs).**
  - `submit_for_review` is `rating_versions.py:337` (the plan: `:278-338`); `_regression_run_gate` `:793` (plan `:648`).
  - Slice 5's merged `submit_for_review` runs, in order, `_golden_quote_gate`, `_regression_run_gate`, `policy_for` (positional `(session, workspace_id)`), `_dislocation_baseline`, `_dislocation_gate`, `_approximation_gate`, `_structural_diff_gate`, then writes `row.evidence` once. The plan's order of the old direct calls was regression, dislocation, structural diff; the floor order is `structural_diff`, `regression_run`, `dislocation_run`, so the structural-diff blob is now stored before the other two refuse. A refusal rolls the transaction back, and the blob's `retain` with it, leaving at worst an unreferenced blob that FR-420's collector takes.
  - `structural_diff_verified` (`:1124`) and `dislocation_run_verified` (`:1130`) take a `RatingVersionRow` and read `row.evidence` after it is written; they are not callables of the plan's `verifiers` shape (`Callable[[], Awaitable[tuple[str, Any]]]`). The gates return the value to record, so the verifier wrappers wrap the gates; the two predicates stay public and unchanged (a test uses them). Each verifier returns a dict of the `row.evidence` entries it contributes (`dislocation_run` returns `dislocation_run_id` or `no_baseline`, so a first version still records its reason).
  - Signatures: `_regression_run_gate(session, *, workspace_id, row, ref, golden_quotes) -> UUID`; `_dislocation_baseline(session, *, workspace_id, row, policy) -> tuple[ArtifactRef | None, str]`; `_dislocation_gate(session, *, workspace_id, row, ref, baseline) -> UUID | None`; `_structural_diff_gate(session, *, workspace_id, row, ref, baseline, blob_store) -> str`; `_approximation_gate(session, *, workspace_id, row, ref, policy)`.
- **Task 0, Step 5 (baseline run): OWED.** The three Acceptance 6 files need Postgres and the gate-1 slot is held; the four docs checks wait for the gate slot too.

- **Task 1, 2026-10-10.** T6's find string (`which this requirement's 2026-08-29 invariant permits. |`) no longer resolves as the row's end: A-1 appended a dated line after it (`RL-1457`). The text is appended at the row's end instead, before the final ` |`; the date is 2026-10-10 and the ruling id RL-1504 (minted). `audit-docs` OWED (gate slot).
- **Task 2, 2026-10-10 — red/green OWED.** The new file needs Postgres and gate-1 is held (A-2): no test was run. Expected red on `origin/main` code, by cause: Acceptance 3 (blank summary under a `change_summary` policy gives `approvals.submit`'s refusal, not `EVIDENCE_INCOMPLETE` naming the kind), 4 (the submission succeeds), 10 (the submission succeeds on the first attempt). Acceptance 1, 2 and 7 guard behaviour the old direct checks already have (the plan's Task 2 Step 2 says 2 fails red; it does not, since the direct limb checks ignore the policy and still refuse; it is red only against a loop reading `entry.evidence`). The scratch-reverted broken-loop runs (`continue` on an unknown kind; `rate_table_diffs` mapped as met) are OWED. `import app.platform.rating_versions` succeeds and `ruff check` passes on both files; `mypy` is whole-tree and waits.
- **Deviations from the plan, for the lead.** (1) The verifiers are closures inside `submit_for_review` returning the `row.evidence` entries they contribute (a dict), not `(key, value)` tuples, because `dislocation_run` records `no_baseline` for a first version. (2) The three gates are now called once each inside those closures, so Acceptance 5's `git grep` prints each definition plus one call inside `submit_for_review`, not the map entry alone. (3) `_approximation_gate` runs after the loop, not before the structural diff. (4) Floor order puts `structural_diff` first: the blob is stored before the regression and dislocation refusals, as the Task 0 entry above records. (5) `rate_table_diffs` has its own verifier that raises a refusal naming the kind and its owner, rather than the unknown-kind text. (6) `structural_diff_verified` and `dislocation_run_verified` stay as they are, public, with two docstring lines no longer claiming to be Slice 6's map entries.
- **Owed runs, all for the gate slot:** Task 0 step 5's baseline (Acceptance 6's three files, the four docs checks); the red/green runs above; `mypy`; `audit-docs` and `docs/INDEX.md` regeneration for this ledger and the spec edit; the full two-half gate.

- **2026-10-10, GO turn (rulings 1–6 of the 21:35:23 BST dispatch record).** `origin/main` merged at `0ab0c7c7` (plain merge, rc 0; true base `db0642c4`).
  1. **Acceptance 2 is a GUARD** (green before and after, the house form). No code change was made to manufacture a red. The plan's Task 2 Step 2 says Acceptance 2 "FAIL[s] because the submission **succeeds**"; it does not, because the old direct checks ignore the policy and still refuse a version with no Dislocation Run. It is red only against a loop that reads `entry.evidence` instead of `effective_evidence`.
  2. **Acceptance 5, refined to the map entry.** The plan's `git grep` over the whole file prints 6 lines at this head (3 definitions, 3 calls). The refined predicate, run verbatim over `submit_for_review`'s body: `awk '/^async def submit_for_review\(/{f=1;next} f&&/^(async )?def /{f=0} f' backend/src/app/platform/rating_versions.py | grep -cE '_(regression_run|dislocation|structural_diff)_gate\('` prints **3** at this head, and the three hits are the calls inside the `structural_diff`, `regression_run` and `dislocation_run` verifier closures (`:394`, `:401`, `:407` of the file), no other call in the function.
  3. **Order.** The plan states one: PL-1499 §"Architecture" ("One loop over `effective_evidence("rating_version")` in floor-then-policy order"), §"Risks" ("The loop runs floor order (`structural_diff` first)") and Task 2 Step 3 ("keep the golden-quote gate before it and FR-224's gate after it"). The code follows it: golden quotes, loop (`structural_diff`, `regression_run`, `dislocation_run`, then policy kinds), `_approximation_gate`. The structural-diff blob is therefore stored before a regression or dislocation refusal. The test `test_the_floor_is_checked_in_floor_order_and_the_diff_blob_is_stored_first` pins refusal precedence and the stored blob (red/green OWED, DB).
  4. **`rate_table_diffs` owner, corrected.** `RL-1504` :69 names "WK-673 (the rate-table diff is S7's domain)"; WK-673 Slice 7 is `SL-1391` (FR-231's exposure weights, closed) and produced no `rate_table_diffs`. The owner is a NEW WK-673 slice row, working id **SL 9965** (reserved by the lead; the row is not created here): "rate_table_diffs evidence: persist the baseline-vs-candidate rate-table pin diff beside Slice 5's structural diff (DP-S6-1 option (a)'s mapping)". It is off the G2 path (`DEFAULT_POLICY` does not name it). Cited for the S7 correction: "2026-10-10 21:35:23 BST", item 4. `RL-1504` is frozen and not edited.
  5. **Unknown kind named as built:** `{kind!r}`; no enum branch (`ApprovalPolicyEntry.evidence` is `tuple[str, ...]`). Naming it is configuration, not quote or policy input (NFR-499); `modelling.py` names unknown kinds the same way.
  6. **Comment re-point:** `FD 9952` to `FD-1589` at the `except ValueError` comment in `compile_rating_version`, comment only, its own commit.

## PRs

(None yet: authoring ahead of the GO.)
