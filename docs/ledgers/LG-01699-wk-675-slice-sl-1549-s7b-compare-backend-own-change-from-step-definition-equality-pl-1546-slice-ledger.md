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

Audit: 2026-10-12, auditor-sl1549 (proposes; verdicts are the lead's). Range `origin/main...origin/sl-1549-wk675-s7b-compare-backend`, PR head `2bef30f19d67d0c9fc9fbc141c835272de870574`; run in a detached worktree at that head.

**Scope, derived from the spec first.** `PL-1546` order row 3 (S7b: `03` §4.10 `StepChange.own_change`; FR-262 backend limb; R7b.1 namespaced `step_id`) and `RL-1261`'s rule plus its five acceptance negatives, then evidence:

| requirement | evidence read | result |
|---|---|---|
| `own_change` true iff `diff_algorithms(...).changed_steps` has a non-`note` entry for the `step_id`; added/removed true | `trace_diff.py` `_edited_step_ids` (`c.field != "note"`) and `own_change=step_id in edited`; added/removed branches untouched | met |
| neg 1: edited downstream step with moved input reads true (F5) | `test_a_downstream_steps_own_edit_is_not_masked_by_its_moved_input` asserts `{"s_rate": True, "s_total": True}`; HTTP twin `test_a_downstream_edit_with_a_moved_input_is_an_own_change_at_the_http_layer` | met |
| neg 2: unchanged-definition downstream with moved input reads false | `test_a_downstream_step_with_an_unchanged_definition_and_a_moved_input_is_not_own` asserts `s_total: False` | met |
| neg 3: note-only edit on a step listed through `consumed` reads false | `test_a_note_only_edit_on_a_step_listed_through_consumed_reads_false` | met |
| neg 4: `own_change` agrees with `diff_algorithms` except `note` | `test_own_change_agrees_with_diff_algorithms_except_for_note[expr]`, `[label]` | met |
| neg 5: one changed `rate_table_ref` gives exactly one own change | `test_a_changed_rate_table_ref_gives_exactly_one_own_change` | met |
| `label` edit reads true | `test_a_label_edit_reads_true` | met |
| R7b.1 namespaced ids | `test_a_namespaced_step_inside_a_mounted_sub_graph_is_compared_by_its_namespaced_id` builds both algorithms with `inline_mounts`, asserts `{"m_ncd__s_ladder": True, "m_ncd__s_cap": False}`; `score.py` passes `compiled.algorithm` (the inlined one); no special case in `diff_traces` | met (unit level) |
| request/response shapes unchanged | contract hunks (below) | met |

**Reds by cause.** (a) `test_trace_diff.py` 19/19 red by `TypeError` on the 2-arg → 4-arg signature: confirmed by reading (main's `diff_traces` takes 2 parameters; every test calls 4 positionally); the file collects 19 tests, matching the ledger's "19 of 19". Not re-run against main's source. (b) HTTP red `{'s_adj': False} != {'s_adj': True}`: cause matches by reading (main's rule reads `consumed` moved → false); not re-run, it needs a database and gate-1 was held by another seat. (c) Guards (elapsed time, `1`/`1.0`/`true`, added/removed, identical, duplicate id, `test_exactly_one_step_is_the_own_change_at_the_http_layer`) are labelled GUARD and carried to the new signature. (d) The "known limit" test is flipped, not deleted: `..._not_masked_by_its_moved_input`. **Independent control, run at this head in the audit worktree and reverted:** replacing `own_change=step_id in edited` with the old `"consumed" not in fields` turns exactly 4 of 19 red (`not_masked_by_its_moved_input`, `an_own_change_with_identical_consumed_reads_false_when_the_definition_is_unchanged`, `agrees_with_diff_algorithms...[expr]`, `[label]`); with the real code: 24 passed (`test_trace_diff.py` + `test_scoring_compare.py`).

**Spec.** `03` §4.10: the `RL-1261` amendment bullet is unchanged in its text (git diff shows it as context); a `(Delivered 2026-10-12 by SL-1549 …)` line sits beneath it; the three bullets (`own_change`, `own_change: false` means, F5 known limit) are struck in place with a dated note each. Code and spec agree (`diff_traces` signature, namespaced-id handling, `StepChange` description).

**Contract.** `generated.json` and `score-comparison.schema.json`: each has two hunks, both `description` strings (`StepChange`, `own_change`); no `properties`, `required`, type or `$ref` hunk. `generate-contracts.py --check` at this head: "49 generated contracts match the models".

**Write set.** `git diff --stat origin/main...HEAD -- frontend` is empty. The 12-file change set is backend/pricing-core/model-schema/spec/ledger/roadmap/INDEX/contracts; nothing outside S7b's write set.

**Closing acts.** `SL-1549` is `closed` with a dated line (Audit: pending at that point; this section is what resolves it) and an activation line; `PL-1546` stays `active` (correct, other slices open). `LG-1699` is `closed` with the gate table. Raw logs under `~/gi-pricing-plan.local/scratch/sl1549/logs/` spot-checked: 13 `FAILED` lines in `pytest.log` ("13 failed, 5740 passed, 6 skipped"), all in docs-audit-dependent tests; `audit_docs.log` ends "FAILED (1): check 31: gap in the full allocation between 1673 and 9884"; every other stage `.rc` is 0. The gate ran at `d143f626`, not the PR head: the SL's own files (`trace_diff.py`, `score.py`, `scoring.py`, both test files) are byte-identical between `d143f626` and `2bef30f1` (`git diff --numstat` empty for each); the rest of the delta is the merge of `origin/main` and the mint. At the PR head `audit-docs.py` reports check 31 only, "gap in the full allocation between 1681 and 1699".

**CI.** Not green and not claimed so: check 31 stays red until #1297–#1300 merge and the allocation is contiguous; re-merge `origin/main` after they land.

**Findings.**
1. LOW, `LG-1699` Task 4: the authority is cited as "from-lead entry of 2026-10-12 after the 05:35:05 entries; relayed by message", with no entry time of its own. The spec delivery line and the strikes themselves are correct and the lead accepted them at "05:46:42 BST"; the citation should name that entry. Cosmetic, not a blocker.
2. LOW, test depth: R7b.1 is exercised at unit level only; no HTTP test mounts a sub-graph. The control above shows the namespaced test is not discriminating against the old `consumed` rule (it passes under both); it does depend on inlined input. Acceptable for S7b (the route passes the inlined algorithm by construction); flagged for `SL-1550`'s view tests if a mounted case is wanted.
3. INFO: the roadmap `SL-1549` closing line still reads "Audit: pending". It is a Slice row that closes on this audit and the lead's merge; updating the word is the lead's or executor's call at merge, not done here.

No HIGH or MEDIUM finding. **Proposed verdicts (the lead decides):** every PL-1546 S7b / `RL-1261` requirement above has evidence (no unevidenced requirement); slice acceptance: ACCEPT-ABLE on a clean audit once CI check 31 is cleared by the merges named above; findings 1–3 → carry or accept at the lead's choice.

### Build log

- 2026-10-12: activation commit 6b282198. `SL-1549` draft→active.
- 2026-10-12: build commit (this push): tasks 1–3 above. Small checks green: `test_trace_diff.py` 19, `test_score_compare.py` 21 (on a per-worktree database), `test_scoring_compare.py`, ruff, mypy, lint-imports, `generate-contracts.py --check`. Full gate: see the Gate section.

## PRs

(the slice PR is opened at the mint turn; number and merge commit are added at its merge.)

- 2026-10-12: doc commit d143f626 (03 §4.10 delivery line and strikes; lead accepted the extension, from-lead entry "2026-10-12 05:46:42 BST"). Gate at d143f626: see Gate.
- 2026-10-12: mint turn: merged `origin/main` `36e2610a`; LG working id 9884 minted as LG-1699; `SL-1549` and this ledger closed (Audit: pending).
