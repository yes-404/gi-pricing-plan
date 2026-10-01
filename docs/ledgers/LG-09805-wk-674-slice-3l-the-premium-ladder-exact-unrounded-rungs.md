---
id: LG-9805
family: ledger
title: WK-674 Slice 3L (SL-1345) — the premium ladder, exact unrounded rungs, true operations, one rounding (RL-1329, RL-1346)
status: active
created: 2026-10-01
owner: executor
tree: 8933a29ee2658012ead53132c6e2909a2aa339d8
phase: P2
work: WK-674
plans: [PL-1348]
corrected_by: []
relates: [RL-1329, RL-1346, RL-1343, FD-1336, FD-1330, OQ-1316, RL-1263, PL-1342]
---

# LG-9805 — WK-674 Slice 3L (SL-1345)

Executed from `PL-1348` under the dispatch record below. Branch `sl-1345-premium-ladder`, from
`origin/main` `8933a29ee2658012ead53132c6e2909a2aa339d8`, lane A, executor-ladder. The id is a
working id (the lead allocates every id); it is minted at the merge turn. Append-only: a correction
is appended below, never edited in place. All times are `TZ=Europe/London date`, labelled BST.

Model / effort line, verbatim (`.claude/roles/executor.md:13`): "`sonnet` (currently Sonnet 5); medium, inherited from the lead — the highest-volume role; per-slice". `echo "CLAUDE_EFFORT=$CLAUDE_EFFORT"` printed `CLAUDE_EFFORT=medium`.

## Tasks

### Task 0 — preconditions

The dispatch record, quoted verbatim (`~/gi-pricing-plan.local/handover/DISPATCH-WK-674-SL1345-2026-10-01.md`, outside the repository, FINAL, lane A GO 2026-10-01 02:29:13 BST).

````text
# Dispatch record — WK-674 Slice 3L (SL-1345), from PL-1348 — FINAL

**Status: DISPATCHED 2026-10-01 02:29:13 BST** (lane A GO by the lead). Drafted 01:02:49 BST. The maintainer's GO check PASSED (their entry after the SL-1345 draft, conditions (a)–(c)), and all three hold: (a) #1032 merged (214fd4d7), with both statuses re-read `active` on main 8933a29e; (b) lane A is free, since WK-690 S2 (#1025) merged as 8933a29e; (c) the grant time below is from `TZ=Europe/London date`. The executor's ledger Task 0 quotes the FINAL record verbatim. PL-1348 is frozen by family: nothing in it is edited, and activation facts live here.

**The order:** the maintainer's entry "2026-09-30 23:57:25 BST — DECISION on the S3 halt: (A) carve the ladder half into its own slice; lane B takes WK-1250 S1 now", items 1, 4 and 5.

## Plan and slice status on main (the gate check, FIRST)
- **PL-1348:** `status: draft` at d2ac260d. It goes `active` in **#1032** (head 71bd0f8c).
- **SL-1345:** `status: draft` at d2ac260d. It goes `active` in #1032.
- **GO waits for #1032's merge**, and the lead re-reads both statuses on main (need 6's commands) before GO.

## Activation needs, run as PL-1348 specifies, at `M = d2ac260dc051cec9f9c018310e204a7112f937a5`, outputs pasted (run by the lead between the clock reads 2026-10-01 00:58:14 BST and 01:02:49 BST)
1. `git show "$M":docs/roadmap.md | awk '/^#### SL-1345 /{f=1} f && /^status:/{print; exit}'` → `status: draft                  # draft → active → closed | retired (§1.2a)`. **Met** (SL-1345 is on main).
2. `git grep -l -E '^slice: SL-1345$' "$M" -- docs/plans/` → `…:docs/plans/PL-01348-wk-674-slice-3l-…-leaf-plan.md`; `cut -c4-8` → `01348`. **Met** (minted).
3. `git grep -l -E '^title: .*DP-S3-1 decided' "$M" -- docs/rulings/` → `…:docs/rulings/RL-01346-dp-s3-1-decided-…md`; `cut -c4-8` → `01346`. **Met.** The diff against `2b98b5aa:docs/rulings/RL-09983-…`: 5 insertions and 5 deletions, all mint-only (`id:` RL-9983→RL-1346; H1; the RL-1347 re-point of "working id 9984, draft PR #1024"; the "Minted 2026-10-01 as RL-1346" disclosure; the RL-1347 re-point in the write-set note). **No substantive difference from the text Task 4 was written from.**
4. `git ls-tree --name-only "$M" docs/rulings/ docs/findings/ | grep -c -E '/(RL-01329|RL-01343|FD-01336|FD-01330)-'` → `4`. **Met.**
5. No decision point is open: DP-S3-1 → RL-1346 (need 3); DP-S3-5 → RL-1329; DP-S3-6 → D2 (the maintainer's call, entry "2026-09-30 22:45:30 BST"). DP-S3-2 (RL-1347) and DP-S3-3 belong to SL-1257, per PL-1348. **Met.**
6. The flip merged and the lead's go. **Flip met:** #1032 squash-merged on the maintainer's MERGE-ACK as `214fd4d7a1b3decc9bd6cb2ea12f92363166b739`. Need 6's commands at that main, run by the lead at 2026-10-01 01:27:51 BST: `git show "$M":"$P" | grep -m1 '^status:'` → `status: active                 # draft → active → superseded | retired (§1.2a)`; the roadmap awk → `status: active                   # draft → active → closed | retired (§1.2a)`. **Re-read at GO** on main `8933a29ee2658012ead53132c6e2909a2aa339d8`: both `status: active`. **The lead's go: 2026-10-01 02:29:13 BST.**

## Decision points: every one has a resolver; no task is held
See need 5. **No task is held for a DP.** Task 5 has a separate *order* hold (condition 3).

## Build-start conditions (PL-1348 §"Build-start conditions"; not activation needs)
- **A free lane** under RL-1263: **lane A, GRANTED 2026-10-01 02:29:13 BST** (WK-690 S2 merged as 8933a29e). Lane B holds WK-1250 S1, which is gated and audited CLEAN and waits for its mint. Both gate slots were free at the grant.
- **The salvage branch:** `git ls-remote origin refs/heads/sl-1257-ladder-exact` → `ceb23a001ccfa02ab37065dff65e303e5180d533	refs/heads/sl-1257-ladder-exact` (re-run by the lead at 2026-10-01 01:03:41 BST: `ceb23a001ccfa02ab37065dff65e303e5180d533	refs/heads/sl-1257-ladder-exact`). Task 0 re-runs it; a different SHA is a stop.

## Conditions
1. **Write set:** PL-1348's own write set, verbatim, including the carried D1/D2 text. PL-1348 quotes the halted S3 record's D1 and D2, and RL-1329 wins where they differ.
2. **RL-1263 write-set checks:**
   - **Against WK-1250 S1 (SL-1339, lane B, open):** both touch `packages/pricing-core/src/pricing_core/rating/compile.py` and `ALGORITHM_CHECKS`. WK-1250 S1 refactors `_producer_types` and `_check_result_types` (existing definitions), so it is NOT append-only. See condition 3. `model_schema/__init__.py`: both may append; append-only, and the second to merge re-gates. Generated contracts and INDEX: registry-exempt.
   - **Against WK-690 S2 (#1025):** that slice merges before this one starts on lane A, so no concurrent overlap. This slice's Task 0 merges main after #1025 and re-runs the checks.
   - **Against SL-1340 (WK-1250 Slice 2, draft):** it also edits compile.py; its dispatch record re-checks against this slice (PL-1348, F4).
3. **The compile.py order** (the maintainer's item 3): **Task 5 (`_check_clamp_placement`, LADDER_CLAMP_UNPLACEABLE, the two `valid_algorithm` fixtures) does not start until WK-1250 S1 merges**, unless this record later shows, by a dated delta with both diffs, that both slices are append-only on `ALGORITHM_CHECKS`. The salvage commit `ceb23a00` (the placement check) is HELD until then: Task 0 takes the first three salvage commits and verifies them by patch-id up to `14a1701a` (PL-1348, F2).
4. **The fixture edit** (the maintainer's item 5, the corrected name): the two `valid_algorithm` fixtures (`packages/pricing-core/tests/test_rating_compile.py:15`, `backend/tests/test_rating_algorithms.py:17`) get a placeable clamp, listed before and after in the ledger. The check is unchanged; a test keeps the old shape refused; the 0-count is recorded with its command (including PL-1348 F5's second, wider grep).
5. **The decimal-output guard** (the maintainer's entry "2026-09-30 22:43:26 BST"): no committed non-test algorithm, seed or example declares a `decimal` output. The ledger states it with the grep and its output.
6. **Merge-time obligations:**
   - the **FD-1336 hold lift**: WK-673/675 rung-reader slices are released, and the lead records the lift, dated;
   - the **release-note line** (RL-1329's visible rung change, and R2's JSON type change for non-rung `money_minor`, float → integer) in the squash body and ledger;
   - **the WK-1178 decimal-output fix slice (RL-1343) goes immediately after** this slice merges;
   - **the mint PR carries SL-1345 and the ledger → closed** (the auditor's flips; the maintainer's rule, entry "2026-10-01 00:06:43 BST").
7. **Gate evidence, for EVERY suite-level run, package and directory suites included, never unslotted:**
   - a clean checkout of the named SHA, with `git status --porcelain` empty;
   - `ruff check --no-cache`, and mypy on a fresh cache or with `--no-incremental`;
   - the dev-commands slot wrapper verbatim (`.claude/skills/dev-commands/SKILL.md:122-171`), plus `LOKY_MAX_CPU_COUNT=4`, in the foreground with a timeout (executor.md S-11);
   - `uptime` AND `free -h` at start and end;
   - the other holder as gate or not-gate via `flock -n`.
   **The wrapper exits 0 on failure: read the stage table.** The `bench-rating.py` timing runs only in a solo window the lead grants. A concurrent pair with WK-1250 S1 is an RL-1263 candidate; a missing field disqualifies it.
8. **After merging a main that adds a migration** (WK-1250 S1 adds one): run `alembic upgrade head` on the per-worktree test DB first.
9. **Ledger:** LG working id **9805**, reserved by the lead at 01:02 BST 1 Oct and checked free. The lead is the ONLY allocator (FD-1338). **The ledger is append-only: corrections are appended, never edited in place** (WK-690 S2's F5).
10. **Frozen records:** nothing in `docs/plans/` is edited, and no frozen record body.
11. **Executor:** a fresh `executor-ladder`, from `.claude/roles/executor.md` with its Model / effort line verbatim (sonnet, medium), in a new worktree from origin/main after #1025 and #1032 merge. It never `cd`s, not even `cd /tmp`.
12. **Gates run in a SEPARATE detached worktree** (the maintainer, at #1025's ACK): `git worktree add --detach <path> <named SHA>`, never in the executor's own worktree. Deleting caches is no substitute for `ruff check --no-cache` / `mypy --no-incremental`: run those flags.
13. **Clock:** every time in the ledger comes from `TZ=Europe/London date` and is labelled BST. The box clock is UTC (WK-1250 S1 mislabelled three gate windows).
````

**Task 0 entries (2026-10-01, BST).**

- **02:29:53 BST** worktree `~/gi-pricing-plan.local/trees/exec-ladder`, branch `sl-1345-premium-ladder`, created from `origin/main` = `8933a29ee2658012ead53132c6e2909a2aa339d8` (`git merge-base --is-ancestor 8933a29e HEAD` exit 0). `uv sync --all-packages` ran. WK-1250 S1 (#1034) is open, so no migration to apply.
- **Salvage branch:** `git ls-remote origin refs/heads/sl-1257-ladder-exact` printed `ceb23a001ccfa02ab37065dff65e303e5180d533	refs/heads/sl-1257-ladder-exact` (matches; not a stop).
- **Salvage taken (F2 rule): the first three code commits.** `ceb23a00` (the placement check) is **HELD**, Task 5, behind WK-1250 S1 (#1034), per record condition 3. Hold dated 2026-10-01 02:29 BST; the release is appended below when it lifts. Picks: `2fd447f8` → `1b480949`, `12a728b8` → `4ede332d`, `14a1701a` → `e926b333`. The two ledger commits are not taken. Each pick used `git cherry-pick -n`; `docs/INDEX.md` conflicted in `2fd447f8` (generated), so it was taken from HEAD and regenerated (`scripts/doc-index.py` wrote it, unchanged: no governed document was added). No other conflict.
- **Patch-id verification up to `14a1701a`:** `S` = `git diff --name-only 36b2a121 14a1701a` minus `docs/ledgers/`, `docs/INDEX.md`, `docs/contracts/schemas/generated/` = 17 paths. `git diff 36b2a121 14a1701a -- $S | git patch-id --stable` = `31241861da5546e46511452303156f2e5ba84097`; `git diff 8933a29e HEAD -- $S | git patch-id --stable` = `31241861da5546e46511452303156f2e5ba84097`. **Equal**, and equal per file for all 17. `generate-contracts.py --check` exit 0 (31 contracts match).
- **Salvage tests on the base** (detached checkout `exec-ladder-base` at `8933a29e`, test files only applied; run with `PYTHONPATH` set to the base's `src` dirs, because the shared venv's editable installs point at the slice worktree, which a first run without it wrongly showed green — discarded). Red, predicted cause each:
  - `model-schema/tests/test_money.py`: 2 failed (`test_positional_decimal_str_*`: no such name). 18 pass (controls).
  - `test_scoring_ladder.py`: 3 failed (`extra_forbidden` on the new rung fields; `clamp` not in `LadderOperationKind`; the hand-authored schema lacks the fields).
  - `test_rating_ladder_exact.py`: 16 failed, 3 pass. **Passing = controls, not red first:** `test_an_unclamped_quote_is_unchanged_and_constraints_is_none`, `test_a_clamped_declared_output_serves_the_bound` (RL-1329: green today; its red is the planted mutation, Task 3), `test_the_engines_precision_is_what_the_tolerance_rests_on`.
  - `test_rating_ladder_sweep.py`: collection ImportError (a name the slice adds).
  - `test_rating_score.py`: 2 failed (`test_the_ladder_reconciles_over_a_battery_of_generated_contexts`, `test_a_binding_clamp_is_attributed_to_the_constraints_rung`); `test_testing.py`: 1 failed (`test_run_ladder_reconciles_fails_when_the_payable_is_not_the_last_rung_priced`).
- **Premises a–l re-read at `8933a29e`:** a `money.py:55`, `score.py:769`, `properties.py:303` ✓; b `errors.py:339`, no raise site ✓; c `score.py:566/582/657` ✓; d `test_rating_score.py:224` ✓; f `compile.py:247`, `:277` ✓; g one `valid_algorithm` in each file ✓; i FR-248 `03:155`, NFR-496 `03:1165` ✓ and `money.py:63` "sampled in prod" ✓; j `settings.py:196` ✓; l the decimal grep prints one line, `scripts/bench-rating.py:213` (input contract) ✓. e, h, k not individually re-read yet (re-read at Tasks 3–4). No premise failed.
- **Open PRs read** (`gh pr list --state open`, 02:3x BST): #1034 WK-1250 S1 (`compile.py`, held-order); the rest are docs/finding PRs, none ruling on the ladder, `score.py` or the served outputs.

## PRs

None yet. Opened at Task 7.
