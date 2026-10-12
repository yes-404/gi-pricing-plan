---
id: LG-1699
family: ledger
title: WK-675 slice SL-1549 — S7b, compare backend: own_change from step-definition equality (PL-1546), slice ledger
status: closed                 # active → closed (§1.2a)
created: 2026-10-12
owner: executor
tree: 604ea084c96efe93f521fb9ba17738e05241e61a
phase: P2
work: WK-675
slice: SL-1549
plans: [PL-1546]
corrected_by: []
relates: [PL-1546, PL-1286, SL-1549, SL-1367, SL-1340, RL-1261, OQ-1231, FR-262, FR-219]
---

# LG-1699 — WK-675 slice SL-1549: S7b, compare backend

*(Minted 2026-10-12 as LG-1699 from working id 9884, at the mint turn. Live citations are re-pointed; quoted entries, command output and the build log's dated lines keep the working id they were written under.)*

**GO:** the lead's from-lead entry "2026-10-12 05:34:34 BST — LANE C READINESS (template, read-only at 604ea084): S7b SL-1549 (compare backend; own_change from step-definition equality) — needs MET (SL-1367 merged 13a02bba #1282; RL-1261 active); SCOPE NOTE: SL-1340 closed (#1263) so R7b.1's namespaced step_id limb is IN scope; backend-only; … GO S7b … LG working id 9884 RESERVED … Gate queues after SL-1669, SL-1543, SL-1622." Authority: the maintainer's (by delegation) entries in `to-lead.md` "2026-10-11 10:39:56 BST" items 2–3 (lane C order, S7b third after SL-1367; a backend WK-675 seat may run beside S5 under RL-1445 item 2), "2026-10-11 20:52:24 BST" (#1282 SL-1367 read-back verified; unblocks S6/S7b/S7) and "2026-10-12 05:32:12 BST" (lane C readiness for S7b as a no-gate candidate).
**MERGE-ACK:** not yet given.

## Tasks

Base: `origin/main` `604ea084c96efe93f521fb9ba17738e05241e61a`. The activation commit is the branch's first.

### Scope

`PL-1546` order table row 3: "SL-1549 — S7b: Compare backend | `PL-1286` S7b row, plus R7b.1 | `03` §4.10 `StepChange.own_change`; §3.8: FR-262 (backend limb) | `RL-1261` (met); **`SL-1367` merged first**". R7b.1's namespaced-`step_id` limb is in scope (`SL-1340` merged, #1263). `RL-1261`: `own_change` is true exactly when `diff_algorithms(base_alg, comparison_alg).changed_steps` holds an entry for the `step_id` whose `field` is not `note`; added and removed steps stay true. Backend-only: no `frontend/` file is touched.

### Task list

1. **Red, `diff_traces` (PL-1546 S7b; RL-1261 negatives 1–5).** `packages/pricing-core/tests/test_trace_diff.py` rewritten to the four-argument signature. Red by cause: 19 of 19 `TypeError: diff_traces() takes 2 positional arguments but 4 were given`. New tests: masked downstream edit reads true (flips the old "known limit" test); unchanged-definition downstream with moved input reads false; note-only edit on a step listed through `consumed` reads false; label edit reads true; one changed `rate_table_ref` gives exactly one own change; agreement with `diff_algorithms` except `note`; namespaced `m_ncd__s_ladder` / `m_ncd__s_cap` through `inline_mounts` (R7b.1). Existing tests that pass on main (elapsed time, 1 vs 1.0 vs true, added/removed, identical, duplicate id) are GUARDS, carried to the new signature.
2. **Red at the route, `backend/tests/test_score_compare.py`.** `test_a_downstream_edit_with_a_moved_input_is_an_own_change_at_the_http_layer`, run against main's `trace_diff.py` and `score.py`: `{'s_adj': False} != {'s_adj': True}`. `test_exactly_one_step_is_the_own_change_at_the_http_layer` is a GUARD (green on main).
3. **Green.** `diff_traces` takes both algorithms and reads `own_change` from `diff_algorithms(...).changed_steps` minus `note`; `score_compare` passes each side's `CompiledBundle.algorithm` (the inlined one, so namespaced ids need no special case). `StepChange` docstring and `own_change` description changed; `generate-contracts.py` regenerated `docs/contracts/openapi/generated.json` and `docs/contracts/schemas/generated/score-comparison.schema.json` (description text only; no shape change). `test_scoring_compare.py`'s description test updated.
4. **Spec `03` §4.10: delivery recorded, no rule changed.** The lead's ruling (to-lead channel, from-lead entry of 2026-10-12 after the 05:35:05 entries; relayed by message): append a dated delivery line under the `RL-1261` amendment, never rewrite it; strike a bullet that describes the removed `consumed` heuristic in place with a dated line. Done: the amendment keeps its "not yet built" text, a `(Delivered 2026-10-12 by SL-1549 …)` line follows it, and the three bullets that described the `consumed` rule (`own_change`, `false` means, F5 known limit) are struck in place with a dated line each.

### Gate

Full two-half gate at head `d143f626023ac44e24f308f4436d82dd09195f69` (the lead's grant, from-lead entry "2026-10-12 08:00:50 BST"), run in the gate-1 slot with this worktree's own database, ended 2026-10-12 09:15:24 BST (`gate.out`'s own end line), logs kept under the local scratch directory. The lead accepted it as check-31-only in the from-lead entry "2026-10-12 09:16:05 BST", having read all 13 failure bodies.

| stage | exit |
|---|---|
| ruff | 0 |
| mypy | 0 |
| import-linter | 0 |
| pytest | 1 (13 failed, 5740 passed, 6 skipped) |
| audit-docs | 1 (check 31 only: "gap in the full allocation between 1673 and 9884") |
| req-coverage | 0 |
| generate-contracts `--check` | 0 |
| frontend install, generate:api, lint, type-check, test, build | 0 |

The 13 pytest failures, all docs-audit tests and all from the same check 31 gap for the unminted working id: `test_audit_docs_finding_citations::test_a_finding_resolved_only_by_a_closure_record_is_not_flagged`; `test_audit_docs_ids::test_the_real_tree_passes_all_ten_checks`; `test_audit_docs_ids::test_doc_id_check_exits_0_on_the_real_tree`; `test_audit_docs_process_core_digest::test_an_unrelated_file_edit_is_the_negative_control_and_stays_green`; `test_audit_docs_process_core_digest::test_the_committed_digest_currently_matches_the_committed_spec`; `test_audit_docs_w37_11_ceiling::test_audit_docs_end_to_end_exit_0_then_1_then_0_on_an_injected_residue`; `test_doc_index::test_an_index_skipping_a_reserved_block_breaks_contiguity`; `test_register_lint::test_check_29_is_wired_into_the_docs_gate`; `test_register_lint::test_check_29_note_carries_the_residue_line`; `test_register_lint::test_phase1b_residue_count_matches_check_29s_own_count`; `test_register_owed::test_check_29_wiring_is_undisturbed`; `test_repository_invariants::test_money_discipline_is_enforced_by_the_docs_audit`; `test_repository_invariants::test_journey_citations_are_audited_in_ci`.

### Audit

Audit: pending.

### Build log

- 2026-10-12: activation commit 6b282198. `SL-1549` draft→active.
- 2026-10-12: build commit (this push): tasks 1–3 above. Small checks green: `test_trace_diff.py` 19, `test_score_compare.py` 21 (on a per-worktree database), `test_scoring_compare.py`, ruff, mypy, lint-imports, `generate-contracts.py --check`. Full gate: see the Gate section.

## PRs

(the slice PR is opened at the mint turn; number and merge commit are added at its merge.)

- 2026-10-12: doc commit d143f626 (03 §4.10 delivery line and strikes; lead accepted the extension, from-lead entry "2026-10-12 05:46:42 BST"). Gate at d143f626: see Gate.
- 2026-10-12: mint turn: merged `origin/main` `36e2610a`; LG working id 9884 minted as LG-1699; `SL-1549` and this ledger closed (Audit: pending).
