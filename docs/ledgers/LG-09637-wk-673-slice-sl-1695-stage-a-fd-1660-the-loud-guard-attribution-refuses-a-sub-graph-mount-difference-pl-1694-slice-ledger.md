---
id: LG-9637
family: ledger
title: WK-673 slice SL-1695 — Stage A, FD-1660 the loud guard; attribution refuses a sub-graph mount difference with a coded error, and WF-699 D6 asserts it (PL-1694), slice ledger
status: closed                 # active → closed (§1.2a) — set `closed` only at slice close
created: 2026-10-12
owner: executor
tree: 18803f1d074276052bfe74ee14196b2b0d531697
phase: P2
work: WK-673
slice: SL-1695
plans: [PL-1694]
corrected_by: []
relates: [PL-1694, PL-1267, SL-1695, SL-1696, FD-1660, RL-1686, FR-264, FR-1399]
---

# LG-9637 — WK-673 slice SL-1695: Stage A, the FD-1660 loud guard

*(Working id 9637, reserved by the lead; it is minted at the slice's mint turn. Until then a citation of this ledger names "working id 9637". Quoted entries keep the working ids they were written with: "SL 9850" is SL-1696, "FD 9804" is FD-1660, "RL 9852" is RL-1686, resolved by `PL-1694`'s header paragraph.)*

**GO:** the lead's `from-lead` entry "2026-10-12 08:15:37 BST" (GO for SL-1695; ledger working id 9637), on the maintainer's (by delegation) entries in `to-lead.md`: "2026-10-12 07:44:13 BST" item (1) (DP-G's consequence (A), conditions (a), (b), (c)) and "2026-10-12 08:09:39 BST" (ACK; the two fixed reason clauses; item 4, the interim `03` line in the same commit as the guard).
**MERGE-ACK:** not yet given.

## Tasks

### Scope

`PL-1694`'s SL-1695 row, "Stage A, the guard": `03` FR-1399 (existing refusal, no text change), FR-264 and §4.6 (the 08:09:39 interim line only), FR-266 and FR-1398 (read), FR-217 (read), `WF-699` D6 (asserted refusal), NFR-499 (the refusal text is input-free). Closes FD-1660's silent limb by a named refusal; FD-1660 stays open until SL-1696.

Branch `sl-1695-wk673-fd1660-guard`, worktree `.claude/worktrees/sl-1695`, cut from `origin/pl-9807-recut-2026-10-12` `18803f1d074276052bfe74ee14196b2b0d531697` (PR #1299's branch; `origin/main` was `2a81974184ee405536fb43d30f59a990b3953669`). Row: `SL-1695` in `docs/roadmap.md`.

### Task list

- **T1 — fixtures and reds on the base, by cause** (PL-1694 Task 1; Acceptance 1–4): the mounted fixture and G1–G4, GT in `packages/pricing-core/tests/test_rating_attribution.py`.
- **T2 — the guard, coded** (Task 2; Acceptance 1–6, 10): `_MountNotYetAttributable` in `analysis.py`, the guard in `attribute`, the raise-site case, and the two interim `03` lines in the same commit.
- **T3 — the journey asserts the refusal** (Task 3; Acceptance 7, 8): `journey.py`, `test_wf699_journey.py`, the README sentence; condition (b)'s grep.
- **T4 — gate, LG, PR** (Task 4; Acceptance 9, 10): the full two-half gate only on the lead's grant for the head.

### Gate

Granted by the lead on head `e6019598124bcc5e93d2aa4b9cc2c3eff6455244` (the lead's `from-lead` entry "2026-10-12 08:34:15 BST"); ran 09:15:24 BST under `flock /tmp/slots/gate-1` with `scratch/sl1695/slot.sh` (own database `gipricing_sl-1695_dfe5cf59`). **Stopped by the lead by PID, not a result:** the lead's `from-lead` entry "2026-10-12 09:31:18 BST" (handover freeze) stopped it during pytest, which could not finish by about 09:50. Before the stop: ruff rc 0, mypy rc 0, import_linter rc 0. No pytest, audit_docs, req_coverage, contracts or frontend result exists. The demo-journey run (Task 3 Step 7) did not run; its waiter was cancelled. A re-run needs a new grant (S-13) and a recreated database (S-14).

### Audit

**Auditor-sl1695, 2026-10-14. A reading audit: no test, no `audit-docs`, no gate was run** (gate-1 is held by SL-1683's gate). Range `origin/main...origin/sl-1695-wk673-fd1660-guard` at head `b6b13eee` (the executor's re-merge of `origin/main` `36e2610a` and of #1299's branch, after the `6c1913ed` the audit was dispatched on); the eleven-file change set read is the three-dot diff. The code files are unchanged between `6c1913ed` and `b6b13eee` (the later merges touched `docs/` only). Verdicts are **proposed**; the lead decides.

**Authority read in full.** The maintainer's (by delegation) `to-lead.md` entry "2026-10-12 07:44:13 BST" item (1): *"(a) The Job's refusal names FD-1660 and says attribution of sub-graph mount changes is unavailable until SL 9850. It must not fail generically. (b) The Stage A slice updates every merged test that runs D6 on a mount-changing fork … to assert that exact refusal, with no test deleted."* Its entry "2026-10-12 08:09:39 BST" items 2 and 4 (two fixed reason clauses; the interim `03` line). `RL-1686` DP-W (at `origin/rl-9852-pl9807-dps-2026-10-12` `9035e651`): write 1 the guard as `AttributionError` (`VALIDATION_FAILED`) and `CodedError`, declared in `analysis.py`, fixed text; write 2 the journey and its test; write 3 the grep. The lead's `from-lead` entries "2026-10-12 08:15:37 BST" (GO, LG 9637) and "2026-10-14 09:42:42 BST" (item 2: #1299 carries no code; three-dot diff has no `rating_versions.py`, which this audit confirms: no file outside the write set below).

**Scope from the spec first: `PL-1694` Stage A acceptance, item to evidence (proposed verdict).**

| Item | Evidence read | Proposed verdict |
|---|---|---|
| 1 G1 (L3) | `test_guard_mount_difference_refuses_a_re_pointed_mount` (`test_rating_attribution.py`): `pytest.raises(AttributionError)`; `_assert_refused` asserts `code == "VALIDATION_FAILED"` and `sub-graph mount`, `FD-1660`, `SL-1696`, `m_ncd` in the text; `"a mount differs"` in the text; `spy.attempts == 0`. Base red: `test_guard_mount_difference_base_outcome_is_a_silent_misattribution` at `70b0e464` (one `table_repointed` change, none naming `m_ncd`, `shapley_minor == total`, `ladder != 0`) | delivered; **untested at head** (F-1) |
| 2 G2 (L2) | `test_guard_baseline_mount_k2_refuses_when_either_side_mounts`: same asserts plus the second reason clause, spy 0. Base outcome recorded in the build log (`BUNDLE_COMPILE_FAILED`, `RATING_VERSION_UNPINNED`; the one compiled subset resolved the baseline's `@4`, so no STOP) | delivered; untested at head |
| 3 G3 | `test_guard_one_group_refused_even_when_one_group_holds_every_change`: refused, `m_ncd`, spy 0. Base: one lump equal to the total (1021) | delivered; untested at head |
| 4 G4 | `test_guard_mount_added_two_groups_refuses_before_any_compile`: refused, spy 0. Base `BUNDLE_COMPILE_FAILED` recorded with its inner text | delivered; untested at head |
| 5 GT | `test_guard_text_survives_safe_error_text`: `safe_error_text(exc)` contains `VALIDATION_FAILED`, `FD-1660`, `SL-1696`, `m_ncd`; `isinstance(exc, CodedError)`. Red first recorded at the intermediate commit `470b7af4` (`safe_error_text` keeps no uncoded text) | delivered; untested at head |
| 6 raise-site enumeration | `test_quote_input_raise_sites.py`: `_INPUT_FREE` case `("rating/analysis.py", "_check_mounts_attributable"): 1` and `"_MountNotYetAttributable"` in `_SITE_NAMES`; the red-first (`('rating/analysis.py', '_check_mounts_attributable'): 1`) is recorded | delivered; untested at head |
| 7 WF-699 D6 | `journey.py` D6: Job must be `failed`, `error.code == "VALIDATION_FAILED"`, message holding `FD-1660` and `SL-1696`, else `JourneyStepFailed("D6", "FD_1660_GUARD_NOT_RAISED")`; `SKIPS` lines exactly as Acceptance 7 (D7 `SKIPPED D7 — FD-1660 guard`; D8, E4, E6, E8, E9, DEP, S1 `SKIPPED <step>: FD-1660; SL-1696`); E5 and E7 keep their Phase-3 lines (`journey.py:74-75`; the E4 to E9 skip loop reuses them); `rating_version_id is None`, `bundle_hash == ""`, `prod_premium_minor == 0` with comments naming FD-1660 and SL-1696. `git diff origin/main...HEAD -- backend/tests \| grep -c '^-def test_'` prints 0 | delivered; untested at head |
| 8 condition (b) grep | Re-run by this audit at `b6b13eee` (both predicates verbatim): the same six `backend/tests/` files; counts `test_dislocation_runs.py` 1, `test_rating_version_dislocation_gate.py` 5, the other four none. Matches the LG's result at `18803f1d`; no new file | delivered |
| 9 no regression | The existing tests of `test_rating_attribution.py` carry no mount term; the shared helpers (`_run`, `_resolver`, `_candidate_version`) were extended (F-3) | delivered; untested at head |
| 10 interim line and gate | `grep -cF 'Interim, 2026-10-12, the maintainer'` of `03` at the head prints 2 (FR-264's cell, the end of §4.6); text identical to the 08:09:39 entry's quoted line; `git log -1 -S 'Interim, 2026-10-12'` and `git log -1 -S '_MountNotYetAttributable'` both print `590c5897`. The gate: **no result** (see Reds) | interim line delivered; the **gate is not started** |

**Reds by cause, and the gate.** The base outcomes (G1 to G4) are recorded in the build log with their causes and figures; their tests exist at `70b0e464` and the flipped ones fail on the base by the recorded cause. Each is reachable: `git merge-base --is-ancestor` exits 0 for `18803f1d`, `70b0e464`, `470b7af4`, `590c5897`, `acf20f73`, `e6019598` and `a8b8c3b9` against the head. The Gate section records `e6019598` as **stopped by the lead by PID, not a result**; this audit does not read it as one. Every pytest claim in the build log (G1 to G4 green, GT red then green, the journey test 11 of 11) is the executor's prose with no output kept, at a head older than `b6b13eee`.

**Conditions and DP-W.**
- **(a)**: met in code. The text is `VALIDATION_FAILED: sub-graph mount differences are not yet attributable (FD-1660); attribution of sub-graph mount changes is unavailable until SL-1696. <reason>: <mount points>` (`analysis.py`, `_MountNotYetAttributable`), naming FD-1660 and SL-1696, never generic. The two reason clauses are the 08:09:39 item 2 wording exactly.
- **(b)**: met by the journey and its test, as item 7 and 8 above.
- **DP-W exactly**: `class _MountNotYetAttributable(AttributionError, CodedError)` declared in `analysis.py` beside `AttributionError`; `code == "VALIDATION_FAILED"` by `super().__init__("VALIDATION_FAILED", …)`; fixed literal plus `mount_point`s (authored identifiers); no other `AttributionError` is made coded; `backend/src/` is not in the diff. The guard sits after `_check_groups` and before `_check_dependence`, not in `_derive`, as the plan's write set says. `# noqa: N818` carries its reason and the plan fixes the name in four clauses.
- **Interim `03` lines**: both agree with the build: the guard refuses any `sub_graph_mounts` difference at any K, and either-side-mounts with two or more groups, which is the line's two limbs.

**Write set.** Every file is in `PL-1694`'s Stage A write set (`analysis.py`, `test_rating_attribution.py`, `test_quote_input_raise_sites.py`, `journey.py`, `test_wf699_journey.py`, the README sentence after `:86`, `03` the two interim lines) or is the slice's record (this LG, `docs/roadmap.md`, generated `docs/INDEX.md`). Nothing under `backend/src/`, `packages/model-schema/`, `docs/contracts/` or `frontend/` changed. The plan file and the SL-1695/SL-1696 rows appear in the range only because #1299's branch is merged into this one (`b6b13eee`); see F-4.

**Barred word.** `git diff origin/main...origin/sl-1695-wk673-fd1660-guard -U0 | grep '^+' | grep -niE 'dep''uty'` prints nothing (rc 1), over the whole range including the plan carried from #1299.

**Closing acts.** `SL-1695` (`docs/roadmap.md:962`) and this LG are both `active`; neither is closed. They stay `active` until the gate has a result and the mint turn assigns the id: **pending, not done.** MERGE-ACK is not given.

**Findings.**
- **F-1 (MEDIUM, process): no verification result exists at the head.** The only gate run was stopped; the pricing-core and journey greens are unrecorded prose at an earlier head. Fix: the gate on `b6b13eee` or its successor (both halves, S-13 and S-14), the journey test and the journey run, with their output recorded in the Gate section. Until then items 1 to 7 and 9 are "delivered but untested".
- **F-2 (LOW) `packages/pricing-core/tests/test_rating_attribution.py` (`test_guard_fixture_has_a_non_zero_ladder_effect_that_attribution_would_misattribute`): a tautological assert.** `interaction` is defined as `total - ladder - table`, so `assert total == ladder + table + interaction` cannot fail; only `ladder != 0` carries the claim. The base test at `70b0e464` has the same shape (`item.shapley_minor - table == ladder + interaction`). The figures the build log quotes (21471, 2279, 2282) are asserted nowhere at the head. Fix: label it a guard against a vacuous fixture and assert `ladder != 0 and table != 0`; drop the identity.
- **F-3 (LOW) `test_rating_attribution.py:843` (the `test_attribute_undeclared_column_never_reaches_the_engine` hunk): an unrelated reformat of an existing test.** It collapses the `tuple(c for c … )` onto one line (99 characters); main has it split. It is the residue of the `ruff format` slip; the build log says only `analysis.py` was read hunk by hunk. It is outside the write set and Acceptance 9 says existing tests stay unedited. Fix: restore the three-line form. Separately, the shared helpers `_run`, `_resolver` (now `_MountAwareResolver`) and `_candidate_version` changed for every existing test; this is in the plan's write set (`_candidate_version` gains an optional pin) but `_run` and `_resolver` are wider, so the gate must show the old tests green.
- **F-4 (INFO): the range carries #1299's content** (the plan file, the SL-1695/SL-1696 rows, the roadmap G2 lines, 706 plan lines). #1299 is not on `main`; merge #1299 first so the slice PR's diff is the nine code and record files, or the squash will duplicate it.
- **F-5 (INFO): no test shows the guard does not over-refuse.** A mounted, unchanged mount, one change (K = 1) run passes through the guard by its code, but no test says so. Not in the plan's acceptance; one test would pin it.
- **F-6 (INFO): the LG front matter `tree:` is the base `18803f1d`, not the head.** Intended for the slice's base; the mint turn should keep it.

**Proposed verdict for the slice:** the change set agrees with the plan, the three conditions and DP-W; **not ready to close** until F-1's gate result exists (F-3 should be fixed before it, so the gate covers the fixed tree). No STOP, no HIGH.

### Build log

- 2026-10-12 08:17 BST — activation: `SL-1695` and `PL-1694` set `active`, this ledger opened (working id 9637), by the executor on the GO above. Base `18803f1d`. Activation commit `a8b8c3b9`.
- 2026-10-12 — **Task 1, the reds on the base, by cause** (commit `70b0e464`; every figure from `packages/pricing-core/tests/test_rating_attribution.py` at `18803f1d`'s `analysis.py`, seen through the committed base-outcome tests and a probe):
  - **G1 (limb 3, silent): confirmed HIGH.** Baseline mounts `m_ncd` at `@4`; the candidate re-points it to `@5` and edits one rate table; no groups. Attribution returned. One derived change, `c1` `table_repointed` (`s_expense: rate_table_ref … @1 → @2`), none names `m_ncd`. `c1.shapley_minor` = `total_change_minor` = 26032. Independently, through `compile_bundle` and `_score_pass` over the same 12-policy book: ladder-only effect 21471, table-only effect 2279, interaction 2282 (computed, not assumed zero), so 26032 − 2279 = 21471 + 2282: the table edit is credited with the ladder's effect. No STOP.
  - **G2 (limb 2): `BUNDLE_COMPILE_FAILED`.** Both versions mount `@4`; the candidate adds the table and instalment edits; K = 2. Text: `the subset bundle for changes [c1] did not compile: ValueError: RATING_VERSION_UNPINNED: mount 'm_ncd' names sub_graph:ncd-ladder@4, which the rating version's pins do not carry at that exact version (FR-237, RL-1309 G1)`. The one subset that compiled (`score-fixture-subset-00`) resolved `sub_graph:ncd-ladder@4`, the baseline's own pin. No partial subset compiled against another version: no STOP.
  - **G3 (DP-G exemption (i) refused): returns a lump.** Baseline without the mount; the candidate mounts `m_ncd` with its consumer edited and edits `s_instalment`; one group holding all three derived changes (`c1` `step_added` `s_in_ncd`, `c2` `step_changed` `s_instalment`, `c3` `step_changed` `s_office`). One item, `shapley_minor` = `total_change_minor` = 1021. Subsets compiled: `…-0` (no sub-graph), `…-1` (`@4`).
  - **G4 (limb 1): `BUNDLE_COMPILE_FAILED`.** Same candidate, two groups (`structure` = `c1`, `c3`; `instalment` = `c2`). Text: `the subset bundle for changes [c1, c3] did not compile: ValidationError: 1 validation error(s) for RatingAlgorithm: <root>: [value_error]`. Only `…-00` compiled, resolving no sub-graph.
  - The flipped (after Stage A) tests run on the unguarded base: G1, G3 and GT `DID NOT RAISE AttributionError`; G2 and G4 fail on `assert 'BUNDLE_COMPILE_FAILED' == 'VALIDATION_FAILED'`. Each by the cause above.
- 2026-10-12 — **Task 2 Step 1** (commit `470b7af4`): the guard as a plain `AttributionError`; G1 to G4 green, **GT red by cause**: `AssertionError: ('VALIDATION_FAILED', 'AttributionError')`, `assert 'VALIDATION_FAILED' in 'AttributionError'` (`safe_error_text` keeps no text of an uncoded `AttributionError`).
- 2026-10-12 — **Task 2 Steps 2 to 4** (commit `590c5897`): `_MountNotYetAttributable`, an `AttributionError` and a `CodedError`; GT green. `test_quote_input_raise_sites.py` stayed green with the guard raised through the new class (`_SITE_NAMES` lists call names, and the subclass construction is none), so **Step 4 applied**: `"_MountNotYetAttributable"` added to `_SITE_NAMES`; the enumeration then **failed naming `('rating/analysis.py', '_check_mounts_attributable'): 1`**; the `_INPUT_FREE` case added; green. The two `03` interim lines (FR-264's cell at `:191`, the end of §4.6 at `:713`), copied programmatically from the maintainer's (by delegation) entry "2026-10-12 08:09:39 BST" item 4, are in the same commit: `grep -c 'Interim, 2026-10-12' docs/specs/03-rating-engine.md` prints 2, and `git log -1 --format=%H -S 'Interim, 2026-10-12' -- docs/specs/03-rating-engine.md` and `git log -1 --format=%H -S '_MountNotYetAttributable' -- packages/pricing-core/src` both print `590c5897b640b4531ad32e8a308fc5619c554de2`. `ruff N818` wants an `Error` suffix; the class keeps the name `PL-1694` Acceptance 10 greps for, with `# noqa: N818`.
- 2026-10-12 — **The class name and `# noqa: N818`** (the lead's instruction, relayed to the executor): `PL-1694` fixes the name `_MountNotYetAttributable` in four clauses, at lines 364 to 365 (Acceptance 10: `` `git log -1 -S '_MountNotYetAttributable' -- packages/pricing-core/src` ``), 469 (Task 2 Step 2: `class _MountNotYetAttributable(AttributionError, CodedError):`), 502 (Step 4: `` Add `"_MountNotYetAttributable"` to `_SITE_NAMES` ``) and 621 (Stage B Task 3 Step 5, which removes it). So the `noqa` stays, with its reason.
- 2026-10-12 — **A formatting slip and its undo.** While adding the coded class the executor ran `ruff format` over `packages/pricing-core/src`, which reformatted 33 files. Nothing was committed: every file but `analysis.py` was restored (`git restore`), and the diff of `analysis.py` against the base `18803f1d` (`git diff --stat 18803f1d HEAD -- packages/pricing-core/src`: 38 insertions, 1 deletion) was read hunk by hunk and holds only the import, the class, the guard function and its call.
- 2026-10-12 — **Condition (b)'s grep at the base `18803f1d`** (RL-1686 DP-W write 3, both predicates verbatim): `git grep -l -E 'attribute\(|derive_changes|dislocation-runs|dislocation_run|attribute_' 18803f1d -- 'packages/*/tests' backend/tests frontend/src` matches six files, all under `backend/tests/`: `test_approval_guard_decision.py`, `test_dislocation_runs.py`, `test_rating_version_dislocation_gate.py`, `test_rating_version_evidence_floor.py`, `test_rating_versions.py`, `test_worker_raise_sites.py`. `git grep -c -E 'sub_graph|SubGraphRef|mount_point|m_ncd' 18803f1d -- <the six>` prints `test_dislocation_runs.py:1` (`"sub_graphs": []`, a payload literal) and `test_rating_version_dislocation_gate.py:5` (one test, `test_the_persisted_structural_diff_carries_a_sub_graph_re_point`, which calls `_structural_diff_gate` and never `attribute`); the other four print no count. None runs D6 on a mount-changing fork. `test_wf699_journey.py` is named by hand (it reaches D6 through `journey.py`) and is updated.
- 2026-10-12 — **Task 3 red first, then green** (journey, test, README): with the guard call commented out in `analysis.py` (temporary, restored, never committed), `test_wf699_journey_runs_end_to_end` failed `D6: FD_1660_GUARD_NOT_RAISED` (D6's Job succeeded, its message empty): the updated test against the unguarded base fails at D6 because the Job succeeds. With the guard, `backend/tests/test_wf699_journey.py` passes, 11 of 11. No test was deleted.

## PRs

None yet.
