---
id: LG-8050
family: ledger
title: WK-673 slice SL-1696 — Stage B, the FD-1660 fix; a mount is a derived change, a subset carries its mounts, a mount is a dependence node, and WF-699 D7 decomposes (PL-1694), slice ledger
status: active                 # active → closed (§1.2a) — set `closed` only at slice close
created: 2026-10-14
owner: executor
tree: 8b21b8f457470c417445a2639caf6d4a7053f4c9
phase: P2
work: WK-673
slice: SL-1696
plans: [PL-1694]
corrected_by: []
relates: [PL-1694, SL-1695, SL-1696, LG-1718, FD-1660, RL-1686, FR-264, FR-266, FR-1398, FR-1399]
---

# LG-8050 — WK-673 slice SL-1696: Stage B, the FD-1660 fix

*(Working id 8050, reserved by the lead; it is minted at the slice's mint turn. Until then a citation of this ledger names "working id 8050". The base tree in the front matter is the merge of `origin/main` `beee5ebedcfebc03c1658728442827960975392a` into the prep branch, `8b21b8f4`.)*

**GO:** the early-build GO is the maintainer's (by delegation) `to-lead` entry "2026-10-14 15:25:12 BST", relayed in the lead's brief to the executor on 2026-10-14. Its conditions, each binding:
- **(a)** no gate, PR or status change until SL-1695 is merged on main. **Lifted** by the lead's message 2026-10-14: SL-1695 merged as `beee5ebedcfebc03c1658728442827960975392a`. The gate stays the lead's to grant.
- **(b)** if SL-1695's head changed before its merge, re-merge it at once. It did not: the branch was built on `f704f20f`, whose merge into main is `beee5ebe`.
- **(c)** after SL-1695 merges: re-merge `origin/main`, re-run the reds and the targeted tests, then report gate-ready. Done at `8b21b8f4` (merge) for the merge; the reds and targeted tests run in the gate's Step 0 (below).
- **(d)** SL-1696 strikes the interim 03 FR-264 / §4.6 line in place with `~~…~~` and a dated strike note; its ACK checks it (the maintainer's 2026-10-12 08:09:39 entry, item 4).
- **(e)** the reds are shown red by cause against `f704f20f`, before the fix.
**MERGE-ACK:** not yet given.

## Tasks

### Scope

`PL-1694`'s SL-1696 row, "Stage B, the fix": `03` FR-266, FR-1397 (reconciliation, unchanged), FR-1398 (T2), FR-1399 (T1), FR-264 (`WF-699` D7's question), FR-217 (read only). NFR-495 (determinism: item 17), NFR-496 (money exactness: items 11 to 13). Closes FD-1660 in full (L1, L2, L3). The slice's own ACK is not claimed here; the auditor re-checks.

Branch `sl-1696-build`, pushed as `origin/sl-1696-wk673-fd1660-fix`; worktree `.claude/worktrees/sl-1696`. Started from the prep branch `404ca262` (the Stage B reds with 10 pre-review fixes), `f704f20f` merged (`94a849c8`, no conflict), then `origin/main` `beee5ebe` merged (`8b21b8f4`; conflicts only in the spec cell, the tests, `docs/INDEX.md`, `docs/roadmap.md` and the plan; the spec and tests kept the slice's side, the other three took main's).

### Task list

- **T1 — spec first** (PL-1694 Stage B Task 1): both interim lines struck in place, T1 on FR-1399, T2 on FR-1398 as RL-1686 DP-T adopted them. Commit `8b36ae66`.
- **T2 and T3 — the fix** (Tasks 2 and 3): `_PIN_KINDS` gains `sub_graphs`; `_derive` derives each mount difference as one change; `_subset_algorithm` merges `sub_graphs`; `_subset_pins` covers them; `_check_dependence` treats a mount as a node; the guard, its class and its raise-site case are removed; the guard tests that asserted the refusal are flipped into the R tests. Commit `f8f9b1c0`.
- **T4 — D7 decomposes** (Task 4): the journey's FD-1660 refusal and skips removed, D7's two-group run re-landed from `e14a81e5`, the README sentence struck. Commit `cddf61bf`.
- **T5 — gate, LG, PR** (Task 5): the full two-half gate only on the lead's grant for the head; Step 0 of the gate script is condition (e).

### The planned flip (recorded, not a deletion of coverage)

**The plan clauses that permit it.** `PL-1694`'s write set, row `packages/pricing-core/tests/test_rating_attribution.py`, SL-1696 column: "**extends Stage A's tests:** G1 and G2 flip to R3 and R2, G4 to R1, G3 to a decomposing one-group run; R4 added; GT deleted with the guard (the planned flip, recorded in the LG). No test that exists at Stage A's base is edited otherwise". Stage B Task 3 Step 1 ("Flip G2 to R2, G4 to R1, G3 to item 15; write R4") and Step 5 ("Remove the rest of the guard, `_MountNotYetAttributable`, GT and the guard's `_INPUT_FREE` case"). **How each was done, flipped or removed:** the prep branch (`88f0a684`, `404ca262`) had already written the flipped forms as separate R tests beside the Stage A tests, so a second, in-place flip would have duplicated them. The Stage A refusal test of each pair is therefore *removed*, and the flipped form is the R test named below; GT has no flipped form (the text it proved is gone with the guard) and is deleted as the write set says. No test that exists at Stage A's base (before `590c5897`) is touched: the five removed tests are Stage A's own, written in SL-1695.

The Stage A guard tests that asserted the refusal are removed by Stage B's flip, as PL-1694's write set says ("G1 and G2 flip to R3 and R2, G4 to R1, G3 to a decomposing one-group run; GT deleted with the guard"): `test_guard_mount_difference_refuses_a_re_pointed_mount` (G1 → `test_mount_repoint_plus_table_edit_attributes_each_effect_to_its_own_change`), `test_guard_baseline_mount_k2_refuses_when_either_side_mounts` (G2 → `test_baseline_mount_k2_every_subset_inlines_the_baselines_mount`), `test_guard_mount_added_two_groups_refuses_before_any_compile` (G4 → `test_mount_added_two_groups_returns_and_reconciles`), `test_guard_one_group_refused_even_when_one_group_holds_every_change` (G3 → `test_one_group_holding_every_change_returns_one_item_equal_to_the_total`), `test_guard_text_survives_safe_error_text` (GT, deleted with the guard). `test_guard_does_not_refuse_a_mounted_k1_run_with_an_unchanged_mount`, `test_guard_three_edit_change_list_is_unchanged_without_a_mount` and the ladder-effect fixture test are kept. `test_wf699_journey.py` loses no test: the skip-line test drops D7's line, and the D7 skip test becomes `test_d7_is_not_a_skip_and_a_skip_without_an_owner_still_fails`; the D7 split test is re-landed.

### Gate

**Not yet granted.** The ALONE gate script is `/home/puzhenhao1989/.claude/jobs/b6860f8f/tmp/sl1696-gate.sh`, modelled on `sl1702-gate.sh` (three nested locks, a head guard, a PIDs-only wait, the demo with the frontend); its Step 0 is condition (e), below, and calls `/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl1696/reds.py`. Result: *(to be filled from the gate's output)*.

### Reds by cause (condition (e))

Run **by the gate's Step 0**, not by `run-small`, because the box's load and SL-1702's ALONE gate keep `run-small` from running (the lead's instruction, 2026-10-14): `analysis.py` is checked out from `beee5ebe` (the guard) and then from `beee5ebe^` (the tree before the guard), the red tests at HEAD run, each failure is read from the junit file, and the checker (`scratch/sl1696/reds.py`) asserts the red set and each red's cause. The twelve Stage B reds are `test_rating_attribution.py` lines 1190 to 1434 at the build head; three are red by `_derive`'s own cause (no mount change exists: `not enough values to unpack`), nine by the guard on `beee5ebe` (`VALIDATION_FAILED … FD-1660`) and by their own cause on `beee5ebe^`. The journey test `test_wf699_journey_runs_end_to_end` needs the database and is red on the guard base at D6 (the Job fails). *(Step 0's output to be pasted here after the gate; the 12 lines, each with its cause.)*

DB-needing: `backend/tests/test_wf699_journey.py` (the journey, `database` fixture). The pricing-core tests need no database.

### Broken-input proof

The proof that a check fails on broken input is Step 0 itself: the same test files run red on the unfixed code (the checker prints `NOT RED` for a test that passes there and `RED/WRONG` for a wrong cause) and green on the fixed code. *(Output to be pasted.)*

### The 02:20:32 lines (PL-1694 Acceptance 19)

- **Ladder versus lookup, why not separable:** *(to be written from the journey run: `s_premium` consumes both the ladder's output and the lookup's, so `_check_dependence` (DP-3) keeps them in one group.)*
- **Minimum-premium effect:** *(to be written from the journey run: whether the fork exercises it, a zero-effect group, or one line saying so.)*

### Deviations from the plan

- **The D7 split test's fixture is DP-1-shaped, not copied from a run.** Acceptance 18 asks for the ids, kinds and descriptions of the real derived list. The journey needs the database, which this seat may not use outside the gate. The fixture uses DP-1's forms (`m_ncd: mount added (sub_graph:ncd-ladder@1)`, kind `step_added`) and no `sub_graphs pin` row. **To do after the gate's journey run:** compare the fixture to the run's `derived_changes` and replace any mismatch.
- **Acceptance 13's and R3's numbers are asserted by the pre-existing red tests**, not re-derived here.

## PRs

None yet.

## Build log

- 2026-10-14 15:26 BST — setup: worktree from `origin/sl-1696-wk673-fd1660-fix` (`404ca262`), `f704f20f` merged without conflict (`94a849c8`), pushed.
- 2026-10-14 — spec first: `8b36ae66`. The FR-264 cell's interim line and the §4.6 paragraph are struck with `~~…~~` and a dated note citing SL-1696 and RL-1686; T1 and T2 appended verbatim.
- 2026-10-14 — `origin/main` `beee5ebe` merged: `8b21b8f4`.
- 2026-10-14 — the fix: `f8f9b1c0`. `git grep -n FD-1660 -- packages/pricing-core/src` is empty (rc 1).
- 2026-10-14 — D7 and the journey: `cddf61bf`.
