---
id: LG-1732
family: ledger
title: WK-673 slice SL-1696 — Stage B, the FD-1660 fix; a mount is a derived change, a subset carries its mounts, a mount is a dependence node, and WF-699 D7 decomposes (PL-1694), slice ledger
status: closed                 # active → closed (§1.2a) — set `closed` only at slice close
created: 2026-10-14   # the same day as the working id's reservation; minted 2026-10-14
owner: executor
tree: 8b21b8f457470c417445a2639caf6d4a7053f4c9
phase: P2
work: WK-673
slice: SL-1696
plans: [PL-1694]
corrected_by: []
relates: [PL-1694, SL-1695, SL-1696, LG-1718, FD-1660, RL-1686, FR-264, FR-266, FR-1398, FR-1399]
---

# LG-1732 — WK-673 slice SL-1696: Stage B, the FD-1660 fix

*(Minted 2026-10-14 as LG-1732 from working id 8050, in the SL-1696 PR; the working id was reserved by the lead. Quoted entries keep the working ids they were written with: "SL 9850" is SL-1696, "FD 9804" is FD-1660, "RL 9852" is RL-1686, resolved by `PL-1694`'s header paragraph. Citations below of "working id 8050" or "LG 8050" are history or verbatim quotes and are left as written. The `tree:` in the front matter is the base `8b21b8f4`, the merge of `origin/main` `beee5ebe` into the prep branch.)*

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

**Gate at head `279970f52c73e8fc72f3b2cb7e24814744c35ccd`, tree `8c01e6a2adbe3ca9f5bd12db46c425c894e5d5b5`** (clean before and after), ALONE under the three locks `gate-1`, `gate-2`, `small-test`, granted by the lead 2026-10-14 18:23 BST (load1 10.95), run by `/home/puzhenhao1989/.claude/jobs/b6860f8f/tmp/sl1696-gate.sh` (md5 of the final form `4aabbd81…`, WANT moved with each head); START `2026-10-14T17:23:17+00:00`, END `2026-10-14T19:13:08+00:00`. Logs kept at `/home/puzhenhao1989/gi-pricing-plan.local/scratch/sl1696/gate-279970f5/`. **Two earlier starts did not count:** the 18:05 BST start aborted in preflight (the worktree's venv lacked `alembic`, a minimal `uv run` environment; fixed with `uv sync --all-packages --dev`), and the 18:06 start aborted in Step 0 on the checker (see the build log).

| stage | exit |
|---|---|
| Step 0a (guard base, reds) | checker rc 0, 12/12 + journey red |
| Step 0b (pre-guard base, reds) | checker rc 0, 12/12 |
| Step 0 restored run (both files green) | rc 0, 44 passed |
| ruff | 0 |
| mypy | 0 |
| import_linter | 0 |
| audit_docs | **1**, check 31 only (below) |
| req_coverage | 0 |
| contracts | 0 |
| pytest | **1**, 13 failed, 5852 passed, 6 skipped (below) |
| pnpm install, generate:api, lint, type-check, build | 0 each |
| pnpm test | 0 (116 files, 730 tests) |
| demo `--journey wf-699` (with the frontend) | 124, the designed stop: `journey done in 581s`, `served page: http://localhost:5173/ answered 200` |

**`audit-docs` rc 1 was one check: `check 31: gap in the full allocation between 1718 and 8050`.** The ledger carried the working id 8050 until the mint turn gave it its number (`PL-1694` Acceptance 10: check 31's working-id gap is excepted only while a working id remains); this PR mints it as LG-1732, and the audit run recorded in the build log (the mint commit) is the check that the gap is gone. No other check is listed under FAILED. **The 13 pytest failures, named, are the same gap read by tests that run the audit on the real tree (the check-31 cascade of this ledger's working id):** `tests/test_audit_docs_finding_citations.py::test_a_finding_resolved_only_by_a_closure_record_is_not_flagged`, `tests/test_audit_docs_ids.py::test_doc_id_check_exits_0_on_the_real_tree`, `tests/test_audit_docs_ids.py::test_the_real_tree_passes_all_ten_checks`, `tests/test_audit_docs_process_core_digest.py::test_an_unrelated_file_edit_is_the_negative_control_and_stays_green`, `tests/test_audit_docs_process_core_digest.py::test_the_committed_digest_currently_matches_the_committed_spec`, `tests/test_audit_docs_w37_11_ceiling.py::test_audit_docs_end_to_end_exit_0_then_1_then_0_on_an_injected_residue`, `tests/test_doc_index.py::test_an_index_skipping_a_reserved_block_breaks_contiguity`, `tests/test_register_lint.py::test_check_29_is_wired_into_the_docs_gate`, `tests/test_register_lint.py::test_check_29_note_carries_the_residue_line`, `tests/test_register_lint.py::test_phase1b_residue_count_matches_check_29s_own_count`, `tests/test_register_owed.py::test_check_29_wiring_is_undisturbed`, `tests/test_repository_invariants.py::test_journey_citations_are_audited_in_ci` and `tests/test_repository_invariants.py::test_money_discipline_is_enforced_by_the_docs_audit`; their output carries `check 31: gap in the full allocation between 1718 and 8050` 11 times, and none is in `pricing-core`, `backend` rating or the frontend. They are a consequence of the working id, not of the code; the mint turn clears them. No timing test failed.

**The two aborted starts, evidence kept.** (1) 2026-10-14 18:06 BST, END `2026-10-14T17:06:06+00:00` rc 97: preflight, `| alembic upgrade | rc=2 |`, `error: Failed to spawn: alembic`; the worktree's venv was the minimal one `uv run` had created, fixed by `uv sync --all-packages --dev`; no stage ran. (2) 2026-10-14 18:09 BST, END `2026-10-14T17:09:23+00:00` rc 95: Step 0a, whose checker printed `STEP0 guard FAILED reds=12/12` and `UNEXPECTED RED: test_wf699_journey_runs_end_to_end`, with `RED/WRONG` on the mount-alone test, R4 (`IndexError`) and the mount-removed test (`unpack`); evidence `scratch/sl1696/first-step0/` (`s0a.xml`, `s0b.xml`, `gate.log`); the build log has the reading against the plan and the fix. This run is the third start.

**The load series** (`load.log`, date, l1 l5 l15; the lead's 5-minute series is `tmp/load-series.txt`): before Step 0 17:23:25 `12.26 12.83 13.18`; before the python half 17:27:20 `15.92 14.20 13.64`; before ruff `15.92 14.20 13.64`; mypy 17:27:21 `15.04 14.05 13.60`; import_linter 17:28:35 `13.79 13.91 13.58`; audit_docs 17:28:36 `13.72 13.89 13.58`; req_coverage and contracts 17:29:25 `12.99 13.65 13.51`; pytest 17:29:41 `12.99 13.62 13.50`; after the python half 18:45:17 `11.76 11.31 11.17`; after the frontend half 18:47:57 `16.96 13.80 12.13`; after the demo 19:13:08 `16.21 16.00 14.10`. The pytest run (75 minutes) ran at load1 11 to 17, so no timing verdict is drawn from it; no failure was a timing test.

**The demo run, D6 to S1:** every step `ok` as the journey records it (E5, E7 and D9 keep their Phase 3 and 4 lines; A6, B9, B4 and C1′ their known gaps). D7: `19985 policies in the sample; rate table edits: +711315508; NCD ladder and expense loading: +6418545; sum +717734053 minor units`; the summary is `method shapley`, `total_change_minor 717734053`, `residual_minor 6413842`, `subset_bundle_count 4`. The demo prints `journey done in 581s`, then `served page: http://localhost:5173/ answered 200`; `rc=124` is the designed stop (`timeout -s INT 1500`, the demo waits for Ctrl-C after the journey and the page check).

**The D7 split-test fixture, checked against the demo output.** The run's `derived_changes` (read from `gipricing_sl-1696_demo`, run `01a13bca-2560-7003-a026-cc52d7aab2b3`) are `c1` `step_added` `m_ncd: mount added (sub_graph:ncd-ladder@3)`, `c2` `step_added` `s_loading: step added`, `c3` `step_changed` `s_premium: consumes […] → […, "ncd_factor", "expense_loading"]; expr … → … * ncd_factor * number(expense_loading)`, `c4` to `c10` `table_repointed` (the seven `rate_table_ref` repoints), `c11` `pin` `models pin model:fremtpl2-gbm-130a2e@1 added`; the stored `change_groups` are `rate table edits` `[c4..c10]` and `NCD ladder and expense loading` `[c1, c2, c3, c11]`, a partition of the eleven. **An observation only: this PR does not carry it.** The fixture of `test_d7_splits_the_derived_changes_into_the_journeys_own_effects` in this PR is the gated one, DP-1-shaped (a mount `step_added`, `m_ncd: mount added (sub_graph:ncd-ladder@1)`, and a `sub_graphs pin` row), not this list. A version of the test holding exactly this list passes when its function is called directly (pure, no database), but it was written after the gate and is not part of the gated code; see the owed follow-up below. The salvage's hand-written `sub_graphs pin … @1` row does not appear in the real list, as `PL-1694` Acceptance 18 says.

### Reds by cause (condition (e))

Run **by the gate's Step 0** at head `279970f5`, in the gate's own window (log `gate.log` lines 14 to 113 in the folder above). `analysis.py` was checked out from `beee5ebe` (the guard), then `beee5ebe^` (before the guard); the test files stayed at HEAD. **Step 0a (the guard base): 13 failed, 31 passed.** The 12 Stage B reds and the journey were red, each with the cause the checker (`scratch/sl1696/reds.py`, anchored) expects, and the checker printed `STEP0 guard OK reds=12/12`:
- **by `_derive`'s own cause** (`PL-1694` :156, L3): `ValueError: not enough values to unpack (expected 1, got 0)` for `test_mount_repoint_is_one_step_changed_change_naming_the_mount`, `test_mount_added_and_removed_are_step_added_and_step_removed`, `test_mount_ports_re_mapped_forms` and `test_mount_removed_two_groups_returns_and_reconciles`;
- **by the guard** (`_MountNotYetAttributable: VALIDATION_FAILED: sub-graph mount differences are not yet attributable (FD-1660); …`, with `a mount differs: m_ncd` or `a sub-graph is mounted and two or more groups are declared: m_ncd`) for `test_mount_repoint_plus_table_edit_attributes_each_effect_to_its_own_change`, `test_mount_added_two_groups_returns_and_reconciles`, `test_baseline_mount_k2_every_subset_inlines_the_baselines_mount`, `test_one_group_holding_every_change_returns_one_item_equal_to_the_total`, `test_mounted_empty_and_full_subsets_hash_equal_baseline_and_candidate` and `test_each_subset_pins_only_the_sub_graphs_of_the_mounts_it_holds`;
- **at the pair-naming assert, the text being the guard's refusal** for R4 (`test_mount_and_its_consumer_ungrouped_is_refused_naming_the_pair`) and `test_mount_alone_in_a_group_without_its_input_step_is_refused_naming_the_pair`: `AssertionError: assert 'dependent changes must share a group' in 'VALIDATION_FAILED: sub-graph mount differences are not yet attributable (FD-1660); … a mount differs: m_ncd'`;
- **the journey**: `Failed: D6: VALIDATION_FAILED :: ValueError: VALIDATION_FAILED: sub-graph mount differences are not yet attributable (FD-1660); … a mount differs: m_ncd`.

**Step 0b (no guard): 12 failed, 31 passed**, the checker `STEP0 preguard OK reds=12/12`: each red by the bug's own cause, with `FD-1660` absent, for example `AttributionError: the subset bundle for changes [c1] did not compile: ValueError: RATING_VERSION_UNPINNED: mount 'm_ncd' names sub_graph:ncd-ladder@4, which the rating version's pins do not carry at that exact version`, `… for changes [c1, c3] did not compile: ValidationError`, a subset that pins `@2` where DP-2 wants `@1`, and `_mount_changes(…) == []` for the one-group run. Then HEAD's `analysis.py` was restored, the tree was clean, and both files ran green (44 passed).

DB-needing: `backend/tests/test_wf699_journey.py` only. The pricing-core tests need no database.

### Broken-input proof

Step 0 above is the proof: the same test files ran red on the unfixed `analysis.py` (the checker prints `NOT RED` for a test that passes there and `RED/WRONG` for a wrong cause) and green on the fixed code in one run (`44 passed`, tree clean before and after). Its first form failed its own check on three tests and was corrected against the plan, not fitted to the result (the build log).

### The 02:20:32 lines (PL-1694 Acceptance 19)

- **Ladder versus lookup, why not separable:** `s_premium` (`c3`) consumes both the ladder mount's output `ncd_factor` and the loading step's output `expense_loading` (its derived description is `consumes […] → […, "ncd_factor", "expense_loading"]`), so `_check_dependence` (DP-3) pairs `c3` with the mount (`c1`) and with `s_loading` (`c2`), and the three must share a group: they are the one structure effect. A split of the ladder from the lookup is refused as a dependent pair.
- **Minimum-premium effect:** not exercised by the fork. The real derived list of the D7 run has eleven changes (the mount `c1`, `s_loading` `c2`, `s_premium` `c3`, seven `table_repointed` `c4` to `c10`, and the `models` pin `c11`) and none touches a minimum-premium step, so there is no zero-effect group to report.

### Deviations from the plan

- **The D7 split test's fixture is DP-1-shaped, not copied from a run.** Acceptance 18 asks for the ids, kinds and descriptions of the real derived list. The journey needs the database, which this seat may not use outside the gate. The fixture uses DP-1's forms (`m_ncd: mount added (sub_graph:ncd-ladder@1)`, kind `step_added`) and a `sub_graphs pin` row. **This deviation stays in this PR, and its fix is an OWED follow-up** (below): a post-gate edit of this test file was made and reverted, because the maintainer's ACK condition 4 is code blob-identical to the gated `279970f5`.
- **Acceptance 13's and R3's numbers are asserted by the pre-existing red tests**, not re-derived here.

### Proposed discharge of FD-1660 (for the auditor; `PL-1694` Task 5)

FD-1660's three limbs are closed by this slice, on the evidence above: **L1** (a partial subset kept the baseline's mounts) and **L2** (a subset's pins carried no sub-graph pin) by `_subset_algorithm` and `_subset_pins` with `sub_graphs` in `_PIN_KINDS` (R1, R2, the pin test, the empty and full hash test, all green at the head); **L3** (a mount was no derived change, so its effect was attributed to another change) by `_derive` (R3, the derive tests); **DP-3** by `_check_dependence` (R4 and the mount-alone test). The guard, its class and its raise-site case are gone (`git grep -n FD-1660 -- packages/pricing-core/src` is empty); D7 decomposes in the demo. The discharge itself is the auditor's to propose and the lead's to record.

### Audit

*(To be written by `auditor-sl1696` on the head of this PR, range `origin/main...` the branch.)*

## PRs

The SL-1696 PR, branch `sl-1696-wk673-fd1660-fix`, title `SL-1696: …` (RFC-937 §5.1); its number is the lead's to record at the open.

## Build log

- 2026-10-14 15:26 BST — setup: worktree from `origin/sl-1696-wk673-fd1660-fix` (`404ca262`), `f704f20f` merged without conflict (`94a849c8`), pushed.
- 2026-10-14 — spec first: `8b36ae66`. The FR-264 cell's interim line and the §4.6 paragraph are struck with `~~…~~` and a dated note citing SL-1696 and RL-1686; T1 and T2 appended verbatim.
- 2026-10-14 — `origin/main` `beee5ebe` merged: `8b21b8f4`.
- 2026-10-14 — the fix: `f8f9b1c0`. `git grep -n FD-1660 -- packages/pricing-core/src` is empty (rc 1).
- 2026-10-14 — D7 and the journey: `cddf61bf`.
- 2026-10-14 — **Step 0's first run aborted (rc 95, END 2026-10-14T17:09:23+00:00) on three checker mismatches, read against the plan, not fitted to the result.** Evidence kept at `scratch/sl1696/first-step0/`. On the guard base all 12 Stage B reds were red and 0b passed. (1) and (2): `test_mount_alone_in_a_group_without_its_input_step_is_refused_naming_the_pair` and R4 `test_mount_and_its_consumer_ungrouped_is_refused_naming_the_pair` failed with `IndexError` at `_mount_changes(changes)[0]`, before their own assert. `PL-1694` Stage B Task 3 Step 1: "see each red by its cause against the remaining guard limb (`VALIDATION_FAILED`), and R4 also by the absence of the pair". The tests were fixed, not the checker: each now asserts `mounts` is non-empty first (`no derived change names the mount: _derive does not read sub_graph_mounts`), so it fails at that assert, by the absence of the mount change that the pair depends on. (3): `test_mount_removed_two_groups_returns_and_reconciles` fails with `not enough values to unpack` at `(removed,) = _mount_changes(changes)`: a removed mount is derived as `step_removed` (`PL-1694` DP-1 and Task 2 Step 3: "one draft per `diff.sub_graph_mounts` entry … kind `step_added` / `step_removed` / `step_changed`"), and `_derive` does not read mounts until then; its cause is the derive limb, not the guard. (4): the journey test is an expected red on the guard base; the checker now requires it red with `D6` and `FD-1660` in its message.
- 2026-10-14 — **The maintainer's (by delegation) hold ("2026-10-14 18:11:13 BST", relayed by the lead): is any mount-changing input a hole in SL-1695's guard? No.** The first Step 0 run's three off-cause reds (`scratch/sl1696/first-step0/s0a.xml`): R4 and the mount-alone test failed with `IndexError` at `_mount_changes(changes)[0]`, in the test, before `attribute` was called; the mount-removed test failed with `ValueError: not enough values to unpack` at `(removed,) = _mount_changes(…)`, also before `attribute`. The guard (`analysis.py` at `beee5ebe`, `_check_mounts_attributable`, called after `_check_groups` and before `_check_dependence`) reads `diff_algorithms(baseline, candidate).sub_graph_mounts` itself, not the derived changes, and `_diff_mounts` reports an add, a remove, a re-point and a re-map. A probe (`tmp/probe_guard.py`, the guard base's `attribute` and `derive_changes` in the tests' own helpers, run under `flock gate-1` at load1 10.95) gave `_MountNotYetAttributable`, `code=VALIDATION_FAILED`, text naming `FD-1660` and `m_ncd` for each of: the mount-alone shape (a mount added, K=2, groups from the derived list), the R4 shape, a mount removed at K=2, and a mount removed with no groups. The derived lists on the guard base held no mount change (`s_in_ncd: step added` or `removed`, `s_instalment`, `s_office`), as the plan's L3 says (`PL-1694` :156). **No hole.** The failures were test-side. The two tests are edited: each builds its groups without needing the mount change (the mount-alone group falls back to the producer where none is derived), reaches `attribute`, and asserts the pair-naming text `dependent changes must share a group` and then the pair itself. Check `tmp/verify_edited.py`: on the Stage B head both PASS; on the guard base's `attribute`/`derive_changes` both FAIL at `assert "dependent changes must share a group" in text` (`test_rating_attribution.py:1320` and `:1428`), where the text is the guard's FD-1660 refusal. The mount-removed test stays a derive-limb red (`unpack`; `PL-1694` :156, DP-1 :203).
- 2026-10-14 — **Observation (a), the `_check_groups` nuance.** `_check_groups` runs before the guard (`analysis.py` at `beee5ebe`, `attribute`), so a group that names a mount-change id is refused there ("not derived changes") before the guard is reached. It is unreachable today: on the guard base `_derive` yields no mount-change id, so no caller can name one. It is removed with the guard's reach: from this slice a mount change has an id and `_check_groups` accepts it. No finding.
- 2026-10-14 — **Observation (b), the plan gap.** `PL-1694` names no cause per red for the derive-only reds beyond the L3 defect row (`PL-1694` :156); Task 2 Step 1 (:595-596) and Task 3 Step 1 (:610-611) name `VALIDATION_FAILED` only for the reds that reach `attribute`. The checker takes L3 as the cause of those four reds (`not enough values to unpack (expected 1, got 0)`, anchored). No record is filed.
- 2026-10-14 — **The gate at `279970f5` ran and ended 19:13:08 UTC** (the Gate section above).
- 2026-10-14 — **A post-gate edit was made and reverted; the fixture is an OWED follow-up, not part of this PR.** After the gate, `backend/tests/test_wf699_journey.py`'s D7 split test was rewritten to hold the real `derived_changes` of the demo run (`c1` the mount `m_ncd: mount added (sub_graph:ncd-ladder@3)`, `c2` `s_loading`, `c3` `s_premium`, `c4` to `c10` the seven repoints, `c11` the `models` pin `model:fremtpl2-gbm-130a2e@1 added`; run `01a13bca-2560-7003-a026-cc52d7aab2b3`, read from `gipricing_sl-1696_demo`; expected effects `c4` to `c10` and `c1`, `c2`, `c3`, `c11`). Called directly (pure, no database) it passed. The edit was **reverted** by the maintainer's ACK condition 4 ("code blob-identical to 279970f5 apart from main's files"), as a test file is code and the edit was never gated: `git checkout 279970f5 -- backend/tests/test_wf699_journey.py`. **Owed:** a later slice replaces the DP-1-shaped fixture with this real list and passes its own gate; until then `PL-1694` Acceptance 18's "the D7 split test built on the real derived list" is met by the demo run's output (the Gate section), not by the committed fixture.
