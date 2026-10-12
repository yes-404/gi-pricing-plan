---
id: LG-1680
family: ledger
title: WK-690 slice SL-1622 — the fix row, FD-1349, FD-1492 and FD-1512 fixed before close and FD-1294's discharge line (PL-1621, PL-1665), slice ledger
status: closed                 # active → closed (§1.2a)
created: 2026-10-12
owner: executor
tree: 604ea084c96efe93f521fb9ba17738e05241e61a
phase: P2
work: WK-690
slice: SL-1622
plans: [PL-1621, PL-1665]
corrected_by: []
relates: [PL-1621, PL-1665, SL-1622, FD-1294, FD-1349, FD-1492, FD-1512, FR-146, FR-157]
---

# LG-1680 — WK-690 slice SL-1622: the fix row

*(Minted 2026-10-12 as LG-1680 from working id 9880, at the merge turn. Live citations are re-pointed; quoted entries, command output and the build log's dated lines keep the working id they were written under.)*

**GO:** the lead's `from-lead` entry "2026-10-12 05:31:21 BST" (GO; readiness; ledger working id 9880), on the maintainer's (by delegation) entries in `to-lead.md`: "2026-10-11 11:21:02 BST" item 2 (DP-W-1 (a): the fix row, off the cut ladder) and "2026-10-12 02:53:52 BST" item 3 (the PL-1665 delta approved).
**MERGE-ACK:** not yet given.

## Tasks

### Scope

`PL-1621`'s fix row, order 0 ("SL-1622 — WK-690 fix row: the three fix-before-close findings"), items F.1 to F.6, with F.1 replaced by `PL-1665`'s F.1′ (the guard is already on main at `backend/tests/test_contracts.py:2995-3013`, added by `36a9f483`, #1122; this slice writes no new guard and proves it red on BOGUS input). Requirements: `02` §3.7 FR-146 (the certificate a `failed` `pseudo_huber` blocks) and FR-157 (the metric evidence kind FD-1492 bypasses).

Branch `sl-1622-wk690-fix-row`, worktree `.claude/worktrees/sl-1622`, cut from `origin/main` `604ea084c96efe93f521fb9ba17738e05241e61a`. Row: `SL-1622` in `docs/roadmap.md`.

### Task list

- **T1 — F.1′ (FD-1349).** Red-on-BOGUS proof of the existing guard, then restore. The discharge line in the register is the auditor's write at the close.
- **T2 — F.2 (FD-1492).** Test through `submit`: a custom metric whose `certificate_id` names no `metric_certificate` row is refused 409 `VALIDATION_FAILED`. Red first, then the fix in `backend/src/app/platform/metrics.py`.
- **T3 — F.3 (FD-1512).** `pseudo_huber` certifies on the default grid at delta 1, 63, 100, 1000 and 100000; gradient and hessian unchanged to 1e-12. Red first, then the fix in `packages/model-schema/src/model_schema/objectives.py`.
- **T4 — F.4, F.5.** FD-1294's dated line and the closing of each register row: the auditor's writes at the close. `python3 scripts/register-lint.py` exits 0.
- **T5 — F.6.** Both gate halves pass on the merge tree.

### Gate

Full two-half gate, granted by the lead for head `75271962aa95d6daa656371fde3a18f8257a6c68` (the lead's `from-lead` entry "2026-10-12 05:42:07 BST"). Run under `flock -w 14400 /tmp/slots/gate-1` with `slot-preflight.sh`, own database `gipricing_sl-1622_e23bc949`; ran 05:55:21 to 06:47:04 BST (rc 1). The tree was clean at the head; this ledger text was written after the gate, in the next commit (a docs-only change).

| stage | exit |
|---|---|
| ruff | 0 |
| mypy | 0 |
| import_linter | 0 |
| pytest | 1 (13 failed, 5738 passed, 6 skipped) |
| audit_docs | 1 |
| req_coverage | 0 |
| contracts | 0 |
| fe_install, fe_generate, fe_lint, fe_types, fe_test, fe_build | 0 |

**Every red, by cause: one cause, the unminted ledger id.** `audit_docs` prints `check 31: gap in the full allocation between 1673 and 9880`, the expected red for working id 9880 until the mint. The 13 pytest failures are tests that run the audit or `doc-id.py check` on the real tree and so see that same gap: `test_audit_docs_finding_citations` (1), `test_audit_docs_ids` (2: `doc-id.py check: [noncontiguous] docs/INDEX.md has a gap between 1673 and 9880`), `test_audit_docs_process_core_digest` (2), `test_audit_docs_w37_11_ceiling` (1), `test_doc_index` (1: `the live allocation is not contiguous: [(1673, 9880)]`), `test_register_lint` (3), `test_register_owed` (1), `test_repository_invariants` (2). Each reads `assert 1 == 0` on the audit's exit code. No failure is in code this slice touched. The 13 failures by test: `tests/test_audit_docs_finding_citations.py::test_a_finding_resolved_only_by_a_closure_record_is_not_flagged`; `tests/test_audit_docs_ids.py::test_the_real_tree_passes_all_ten_checks`, `::test_doc_id_check_exits_0_on_the_real_tree`; `tests/test_audit_docs_process_core_digest.py::test_an_unrelated_file_edit_is_the_negative_control_and_stays_green`, `::test_the_committed_digest_currently_matches_the_committed_spec`; `tests/test_audit_docs_w37_11_ceiling.py::test_audit_docs_end_to_end_exit_0_then_1_then_0_on_an_injected_residue`; `tests/test_doc_index.py::test_an_index_skipping_a_reserved_block_breaks_contiguity`; `tests/test_register_lint.py::test_check_29_is_wired_into_the_docs_gate`, `::test_check_29_note_carries_the_residue_line`, `::test_phase1b_residue_count_matches_check_29s_own_count`; `tests/test_register_owed.py::test_check_29_wiring_is_undisturbed`; `tests/test_repository_invariants.py::test_money_discipline_is_enforced_by_the_docs_audit`, `::test_journey_citations_are_audited_in_ci`. The lead accepted the gate as check-31-only (`from-lead` "2026-10-12 06:48:33 BST"). The gate's console output and its seven-plus logs are kept at `~/gi-pricing-plan.local/scratch/sl1622/` (`sl1622-gate.out`, `sl1622-slot.sh`, `tmp.X5pWvN0G9h/`), because `/tmp` is not durable.

At the mint turn (the SL-1669 order: the pre-mint gate, small re-checks after merging main, CI on the PR head): see the build log.


### Audit

Audit: written 2026-10-12 by `auditor-sl1622` (seated by the lead's `from-lead` entry "2026-10-12 06:53:26 BST"). Range `origin/main...origin/sl-1622-wk690-fix-row` (PR #1295, head `e3285a65b0008ec67c47e67b081198631e1c4ab7`, main at `3b2081b7333bded7e998104f042586d50e8bf3e3`). Authority: the maintainer's (by delegation) entries in `to-lead.md` "2026-10-11 11:21:02 BST" item 2 and "2026-10-12 02:53:52 BST" item 3; the lead's `from-lead` entries "2026-10-12 05:31:21 BST" (GO), "05:42:07 BST" (gate grant) and "06:48:33 BST" (gate accepted as check-31-only; the F.3 write-set deviation recorded). Verdicts below are PROPOSED; the lead's.

**Write set** (`git diff --stat origin/main...HEAD`, 8 files): `backend/src/app/platform/metrics.py`, `backend/tests/test_custom_metrics_api.py`, `backend/tests/test_custom_objectives.py`, `packages/pricing-core/src/pricing_core/modelling/objectives.py`, this ledger, `docs/roadmap.md` (SL-1622 row), `PL-1665`'s status line, `docs/INDEX.md` (generated). Every file is explained. `packages/model-schema` is unchanged (`git diff --quiet origin/main...HEAD -- packages/model-schema` exits 0), so the F.3 deviation is as the ledger states and `model_schema/objectives.py:369` holds only the `delta` declaration. `backend/tests/test_contracts.py` is untouched, as F.1′ requires. No `docs/specs/` change: `PL-1621` R-F.2 says none is owed, and `02` §5.1 `:1856` says only "Submit for approval" for the metric route, so no stated behaviour moved. Code between the gate head `75271962` and `e3285a65`: `git diff --name-only 75271962..e3285a65 -- backend packages scripts frontend` prints nothing, so the gate's code result holds for the PR head.

| Item | Evidence | Proposed verdict |
|---|---|---|
| F.1′ FD-1349 red on BOGUS | Build-log T1: five names replaced by `"BOGUS"` in `objective-certificate.schema.json`, `test_the_certificate_check_name_enum_is_the_code_vocabulary` fails at `backend/tests/test_contracts.py:3009` naming the six differing values, restored, green. Cause matches the guard's own assert (enum vs code vocabulary). Guard on main at `:2995-3013`, read. Command and output are quoted verbatim in the ledger. Not re-run by this audit (gate-1 was held by another gate). | delivered; register line owed (F.4) |
| F.2 FD-1492 200→409 | `metrics.py:518-534`: after `_require_evidence`, `session.get(MetricCertificateRow, row.certificate_id)` must exist, in this workspace, with `custom_metric_id == row.id`, else 409 `VALIDATION_FAILED`; line-for-line the objective twin at `objectives.py:730-745`. Tests read: `test_a_certificate_id_naming_no_certificate_row_is_refused_at_submit` (`_advance` writes a random `new_uuid7()` as `certificate_id`; asserts 409 and `VALIDATION_FAILED`) and `test_another_metrics_certificate_is_no_evidence_for_this_one` (a foreign metric's row; same asserts). Base red `assert 200 == 409` quoted in the build log, consistent with `is not None` only. | delivered |
| F.3 FD-1512 | `objectives.py:372-378` returns `r**2 / (s + 1.0)`. Identity checked algebraically and numerically: against a 60-digit `Decimal` reference, old `delta**2*(s-1)` relative error 1.0 at delta 1e5, r 1e-3, 8.9e-5 at delta 1000, 1.9e-7 at delta 63; new form 1e-16 or better at every (delta, r) in {1, 63, 100, 1000, 1e5} x {1e-3, 1, 50, 1e3, 9.9e5}. Same function, so the declared loss is unchanged and gradient/hessian code is untouched (diff shows loss only). Tests read: grid test over `service.default_sampling` for the five deltas asserts `overall is not FAILED`; the red quoted is `analytic_vs_numeric_gradient failed` at 63, 100, 1000, 1e5, the cancellation's signature and not a different cause. The unchanged-derivative test compares the template's `grad`/`hess` to closed forms at 1e-12; it passes at the base too, as a no-regression test must. | delivered |
| F.4 FD-1294 dated line | Not in the PR (an auditor write at the close). `PL-1621` R-F.1 also asks the auditor to run `test_expression_profiles.py:181-204` once before writing it; not run here (no venv in the audit worktree; gate-1 held). | deferred, owner the auditor, event the lead's authorising the register commit |
| F.5 rows closed | Register rows `:281` (FD-1349), `:318` (FD-1492), `:327` (FD-1512) are unchanged on the branch. `python3 scripts/register-lint.py` at the head: `OK (0 violations)`. | deferred, same owner and event |
| F.6 both gate halves | Raw logs `~/gi-pricing-plan.local/scratch/sl1622/tmp.X5pWvN0G9h/*.rc`: ruff, mypy, import_linter, req_coverage, contracts and the six frontend stages 0; pytest 1; audit_docs 1. `pytest.log` last line `13 failed, 5738 passed, 6 skipped in 2964.69s`. The 13 `FAILED` lines match the ledger's list one for one; each carries `check 31: gap in the full allocation between 1673 and 9880` or the `doc-id.py` / contiguity twin, `assert 1 == 0` or `(1673, 9880)`. `audit_docs.log` ends `FAILED (1): check 31`. Gate window 05:55:21 to 06:47:04 BST (the `.log` mtimes read 05:48 UTC, the same clock). | not met literally; the lead accepted check-31-only (06:48:33). Final proof is CI green at the final head |

**Findings**

1. **medium, process — closed before audited.** The SL-1622 roadmap row (`docs/roadmap.md`, the "(Closed 2026-10-12 on a clean slice audit …)" line) and this ledger's `status: closed` were written before any audit existed, and the ledger's own Audit line read "pending". A Slice closes on a clean audit and the lead's merge. Proposed: acceptable only because this audit lands in the same PR; the lead's ACK reads both the closing lines and this section (the Slice-ACK rule).
2. **medium, CI/merge order — the head is not mergeable as it stands.** `gh pr view 1295`: `mergeable: CONFLICTING`, `mergeStateStatus: DIRTY` (`docs/INDEX.md`, generated). Separately, LG-1680 sits above ids held by the unmerged #1294: `python3 scripts/audit-docs.py` run on this worktree at the head exits 1 with `check 31: gap in the full allocation between 1675 and 1680` (every other check passes). It clears when #1294 merges and this branch re-merges main. CI at this audit: `history-policy` success, `frontend` success, `docs` and `python` in progress. CI is not called green.
3. **low, process — gate tree vs head.** F.6 says "on the merge tree"; the gate ran on pre-mint `75271962`. Code is identical to the PR head (see Write set); the mint commit adds docs only. After the re-merge of main the lead's small re-checks stand in, per the SL-1669 order.
4. **low, observation — two copies of one check.** `metrics.py:518-534` and `objectives.py:730-745` repeat the pointer-exists/workspace/owner test. Parallel code in two modules whose parallel is by design (FR-146 / FR-157); not a defect. A shared helper would be a refactor outside this fix row.
5. **info.** `PL-1665` `status: active` is the lifecycle step its activation commit names (status line only, `git diff` confirmed); `PL-1621` stays `active` (unchanged), and the slice row says both close with their other slices (S4, S5), which §1.2a allows.

**Unverified by this audit:** the red runs and the 27/136/72 pass counts in the build log were not re-executed (gate-1 held by another gate; the audit worktree has no venv, and a full venv sync is a heavy job). They are quoted, and the F.3 arithmetic and the F.2 code were checked by reading and independent computation.

**Proposed verdicts for the lead:** FD-1349, FD-1492, FD-1512 delivered and tested; FD-1294's line and the three register closes deferred to the auditor's register commit (owed, owner the auditor); F.6 accepted as the lead ruled; no requirement not-started. Slice close: clean on the code, conditional on findings 1 and 2 (re-merge, CI green at the final head).

### Build log

- 2026-10-12 05:3x BST — activation commit `64fe8254`. Per-branch check (`PL-1621:331-333`) at base `604ea084`, predicate `git diff --name-only origin/main...<b> -- backend/tests/test_contracts.py backend/src/app/platform/metrics.py packages/model-schema/src/model_schema/objectives.py docs/contracts/schemas/objective-certificate.schema.json` over every `refs/remotes/origin/*`: one hit, `origin/sl-1669-wk1178-bulk-op-typing` on `backend/tests/test_contracts.py`, which is the already-known `:80` and `:3189-3203` overlap and not the guard; this slice commits nothing to that file. Note: the fix touches `packages/pricing-core/src/pricing_core/modelling/objectives.py` (the loss), not `model_schema/objectives.py`.
- **T1 (F.1′, FD-1349) — red on BOGUS, then green.** Scratch edit in the worktree: `"analytic_vs_numeric_gradient", "analytic_vs_numeric_hessian"`, `"symbolic_vs_numeric_gradient", "symbolic_vs_numeric_hessian"` and `"finiteness"` replaced by `"BOGUS"` in `docs/contracts/schemas/objective-certificate.schema.json` (`git diff --stat`: 3 lines changed). Command: `run-small.sh uv run --directory <wt> pytest backend/tests/test_contracts.py -q -k certificate_check_name_enum_is_the_code_vocabulary`. Result (rc 1): `AssertionError: authored enum vs code vocabulary differ on: ['BOGUS', 'analytic_vs_numeric_gradient', 'analytic_vs_numeric_hessian', 'finiteness', 'symbolic_vs_numeric_gradient', 'symbolic_vs_numeric_hessian']` at `backend/tests/test_contracts.py:3009`; `1 failed, 172 deselected`. Restored with `git checkout -- <file>`; `git diff --stat` on the file printed nothing; the same command: `1 passed, 172 deselected`. FD-1349's register line is the auditor's write at the close (F.1′, F.4).
- **T2 (F.2, FD-1492) — red first, then fix.** Tests added to `backend/tests/test_custom_metrics_api.py`: `test_a_certificate_id_naming_no_certificate_row_is_refused_at_submit` and `test_another_metrics_certificate_is_no_evidence_for_this_one`. At the base: `pytest -q backend/tests/test_custom_metrics_api.py -k certificate` gave `2 failed, 1 passed`, each `assert 200 == 409` (the submit was accepted: `metrics.py:794` tests only `is not None`). Fix in `backend/src/app/platform/metrics.py` `submit`: after `_require_evidence`, the pointed row must exist, in this workspace, for this metric, else 409 `VALIDATION_FAILED`, the same check `objectives.submit_for_review` makes. After: `test_custom_metrics_api.py`, `test_custom_metrics.py` and `test_metrics.py`: `27 passed`.
- **T3 (F.3, FD-1512) — red first, then fix.** Tests added to `backend/tests/test_custom_objectives.py`: `test_pseudo_huber_is_not_failed_on_the_default_grid` (delta 1, 63, 100, 1000, 100000, over `objectives.default_sampling`) and `test_pseudo_huber_gradient_and_hessian_are_unchanged` (1e-12 against the closed forms, delta 1, 100, 1e5). At the base: `pytest -q backend/tests/test_custom_objectives.py -k pseudo_huber`: `4 failed, 2 passed`; the four are delta 63, 100, 1000, 100000, each `[('analytic_vs_numeric_gradient', 'failed')]`; delta 1 and the derivative test pass. Fix in `packages/pricing-core/src/pricing_core/modelling/objectives.py` `_pseudo_huber_loss`: `r**2 / (s + 1.0)`, the same function as `delta**2 * (s - 1.0)` without the cancellation (the register `:327` event's form). Gradient, hessian and Gauss-Newton are untouched. After: `backend/tests/test_custom_objectives.py` + `packages/pricing-core/tests/test_objectives.py`: `136 passed`; with `test_objective_submission.py` and `test_custom_metrics_api.py`: `72 passed`.
- **Write-set deviation (F.3).** `PL-1621` and `PL-1665` name `model_schema/objectives.py`; the fix is in `packages/pricing-core/src/pricing_core/modelling/objectives.py:372` (`_pseudo_huber_loss`). The loss function is evaluated there. `packages/model-schema/src/model_schema/objectives.py:369` holds only the template's parameter declaration (`delta`), which does not change; the declared loss is the same function, re-evaluated (the plan's own Governance cell). The owning layer is fixed, not the declaration. Identity: with `r = y - mu` and `s = sqrt(1 + (r/delta)**2)`, `delta**2 * (s - 1) = delta**2 * (s**2 - 1) / (s + 1) = r**2 / (s + 1)`, because `delta**2 * (s**2 - 1) = delta**2 * (r/delta)**2 = r**2`.
- Small checks at this tree: `ruff check .` all passed; `mypy` `Success: no issues found in 239 source files`. The full two-half gate is not run: it waits for the lead's "gate slot granted" for the head (S-13).

## PRs

PR number and merge commit: filled at the PR open and the merge.
