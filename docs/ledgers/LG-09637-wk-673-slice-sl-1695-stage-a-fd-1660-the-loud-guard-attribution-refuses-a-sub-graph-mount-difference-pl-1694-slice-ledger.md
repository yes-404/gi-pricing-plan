---
id: LG-9637
family: ledger
title: WK-673 slice SL-1695 — Stage A, FD-1660 the loud guard; attribution refuses a sub-graph mount difference with a coded error, and WF-699 D6 asserts it (PL-1694), slice ledger
status: active                 # active → closed (§1.2a) — set `closed` only at slice close
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

Not yet run. The full gate starts only on the lead's explicit "gate slot granted" for the head (S-13).

### Audit

Not yet given.

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
- 2026-10-12 — **Condition (b)'s grep at the base `18803f1d`** (RL-1686 DP-W write 3, both predicates verbatim): `git grep -l -E 'attribute\(|derive_changes|dislocation-runs|dislocation_run|attribute_' 18803f1d -- 'packages/*/tests' backend/tests frontend/src` matches six files, all under `backend/tests/`: `test_approval_guard_decision.py`, `test_dislocation_runs.py`, `test_rating_version_dislocation_gate.py`, `test_rating_version_evidence_floor.py`, `test_rating_versions.py`, `test_worker_raise_sites.py`. `git grep -c -E 'sub_graph|SubGraphRef|mount_point|m_ncd' 18803f1d -- <the six>` prints `test_dislocation_runs.py:1` (`"sub_graphs": []`, a payload literal) and `test_rating_version_dislocation_gate.py:5` (one test, `test_the_persisted_structural_diff_carries_a_sub_graph_re_point`, which calls `_structural_diff_gate` and never `attribute`); the other four print no count. None runs D6 on a mount-changing fork. `test_wf699_journey.py` is named by hand (it reaches D6 through `journey.py`) and is updated.
- 2026-10-12 — **Task 3 red first, then green** (journey, test, README): with the guard call commented out in `analysis.py` (temporary, restored, never committed), `test_wf699_journey_runs_end_to_end` failed `D6: FD_1660_GUARD_NOT_RAISED` (D6's Job succeeded, its message empty): the updated test against the unguarded base fails at D6 because the Job succeeds. With the guard, `backend/tests/test_wf699_journey.py` passes, 11 of 11. No test was deleted.

## PRs

None yet.
