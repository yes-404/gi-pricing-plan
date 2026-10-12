---
id: LG-9880
family: ledger
title: WK-690 slice SL-1622 — the fix row, FD-1349, FD-1492 and FD-1512 fixed before close and FD-1294's discharge line (PL-1621, PL-1665), slice ledger
status: active                 # active → closed (§1.2a)
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

# LG-9880 — WK-690 slice SL-1622: the fix row

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

Not yet run.

### Audit

Not yet run.

### Build log

- 2026-10-12 05:3x BST — activation commit `64fe8254`. Per-branch check (`PL-1621:331-333`) at base `604ea084`, predicate `git diff --name-only origin/main...<b> -- backend/tests/test_contracts.py backend/src/app/platform/metrics.py packages/model-schema/src/model_schema/objectives.py docs/contracts/schemas/objective-certificate.schema.json` over every `refs/remotes/origin/*`: one hit, `origin/sl-1669-wk1178-bulk-op-typing` on `backend/tests/test_contracts.py`, which is the already-known `:80` and `:3189-3203` overlap and not the guard; this slice commits nothing to that file. Note: the fix touches `packages/pricing-core/src/pricing_core/modelling/objectives.py` (the loss), not `model_schema/objectives.py`.
- **T1 (F.1′, FD-1349) — red on BOGUS, then green.** Scratch edit in the worktree: `"analytic_vs_numeric_gradient", "analytic_vs_numeric_hessian"`, `"symbolic_vs_numeric_gradient", "symbolic_vs_numeric_hessian"` and `"finiteness"` replaced by `"BOGUS"` in `docs/contracts/schemas/objective-certificate.schema.json` (`git diff --stat`: 3 lines changed). Command: `run-small.sh uv run --directory <wt> pytest backend/tests/test_contracts.py -q -k certificate_check_name_enum_is_the_code_vocabulary`. Result (rc 1): `AssertionError: authored enum vs code vocabulary differ on: ['BOGUS', 'analytic_vs_numeric_gradient', 'analytic_vs_numeric_hessian', 'finiteness', 'symbolic_vs_numeric_gradient', 'symbolic_vs_numeric_hessian']` at `backend/tests/test_contracts.py:3009`; `1 failed, 172 deselected`. Restored with `git checkout -- <file>`; `git diff --stat` on the file printed nothing; the same command: `1 passed, 172 deselected`. FD-1349's register line is the auditor's write at the close (F.1′, F.4).
- **T2 (F.2, FD-1492) — red first, then fix.** Tests added to `backend/tests/test_custom_metrics_api.py`: `test_a_certificate_id_naming_no_certificate_row_is_refused_at_submit` and `test_another_metrics_certificate_is_no_evidence_for_this_one`. At the base: `pytest -q backend/tests/test_custom_metrics_api.py -k certificate` gave `2 failed, 1 passed`, each `assert 200 == 409` (the submit was accepted: `metrics.py:794` tests only `is not None`). Fix in `backend/src/app/platform/metrics.py` `submit`: after `_require_evidence`, the pointed row must exist, in this workspace, for this metric, else 409 `VALIDATION_FAILED`, the same check `objectives.submit_for_review` makes. After: `test_custom_metrics_api.py`, `test_custom_metrics.py` and `test_metrics.py`: `27 passed`.
- **T3 (F.3, FD-1512) — red first, then fix.** Tests added to `backend/tests/test_custom_objectives.py`: `test_pseudo_huber_is_not_failed_on_the_default_grid` (delta 1, 63, 100, 1000, 100000, over `objectives.default_sampling`) and `test_pseudo_huber_gradient_and_hessian_are_unchanged` (1e-12 against the closed forms, delta 1, 100, 1e5). At the base: `pytest -q backend/tests/test_custom_objectives.py -k pseudo_huber`: `4 failed, 2 passed`; the four are delta 63, 100, 1000, 100000, each `[('analytic_vs_numeric_gradient', 'failed')]`; delta 1 and the derivative test pass. Fix in `packages/pricing-core/src/pricing_core/modelling/objectives.py` `_pseudo_huber_loss`: `r**2 / (s + 1.0)`, the same function as `delta**2 * (s - 1.0)` without the cancellation (the register `:327` event's form). Gradient, hessian and Gauss-Newton are untouched. After: `backend/tests/test_custom_objectives.py` + `packages/pricing-core/tests/test_objectives.py`: `136 passed`; with `test_objective_submission.py` and `test_custom_metrics_api.py`: `72 passed`.
- Small checks at this tree: `ruff check .` all passed; `mypy` `Success: no issues found in 239 source files`. The full two-half gate is not run: it waits for the lead's "gate slot granted" for the head (S-13).

## PRs

Not yet opened.
