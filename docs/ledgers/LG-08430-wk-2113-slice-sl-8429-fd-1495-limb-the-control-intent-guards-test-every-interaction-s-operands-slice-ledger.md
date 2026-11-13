---
id: LG-8430
family: ledger
title: WK-2113 slice SL-8429 — FD-1495 limb: the control-intent guards test every interaction's operands (slice ledger)
status: active                 # active → closed (§1.2a)
created: 2026-11-13
owner: executor
tree: 2ba0d0d53142dacd6550cb314a4d65685b612bd1
phase: P3
work: WK-2113
slice: SL-8429
plans: []
corrected_by: []
relates: [SL-8429, FD-1495]
---

# LG-8430 — WK-2113 slice SL-8429: the control-intent guards test every interaction's operands

Filed 2026-11-13 under working id 8430 (lead-reserved); executed by seat `exec-sl8429`, branch `sl-8429-fd1495-interaction-operands` off `origin/main` `2ba0d0d53142dacd6550cb314a4d65685b612bd1`. Working ids in prose are in space form (SL 8429, OQ 8431) until the mint.

**GO:** the maintainer's entry, verbatim:

> ## 2026-11-13 19:51:15 GMT — Maintainer: FD-1495 PROBE READ (scratch/lead34-fd1495/rc-table.md b341f2abbcf8, at 2ba0d0d53142): CONFIRMED — the feature guard does not raise, compile_bundle compiles end to end, the instrument is proven red on the shipped GBM-on-control case, and predict_glm_row moves 0.105315 → 0.277157 on quotes differing only in the control Factor yoa. SEVERITY RULED: HIGH, on the probe, not on words — a `control` Factor moves a premium through a `risk` interaction, FR-88/FR-240's exact prohibition, a mispricing path reachable by any user-authored model with one interaction over a control operand. Shipped impact: none known (freMTPL2 seed: risk Factors only, no interactions; no non-template DB on this box) — that clause stays in the finding. GO, SLICE WK-2113 S1 "FD-1495 limb: the control-intent guards test every interaction's operands": plan, needs and census as sent (builder executor/sonnet, reviewer, auditor; one builder worktree off origin/main; gate-1 slot + createdb -T copy + redis db 1/3; no migration; 3 seats live, 0 builders, 0 gates). CONDITIONS: (1) RED FIRST, each test failing at 2ba0d0d5 with its failure line in the LG before the fix: the feature guard, `_refuse_control_factor_keys`, rate_tables/operations.py:233, and an end-to-end compile_bundle refusal with the named error CONTROL_FACTOR_IN_RATEABLE_PATH naming the OPERAND and the cross. (2) NESTED interactions: an interaction whose operand is itself an interaction over a control Factor is refused too — expand to leaves, with a test at depth 2. (3) The offset path (the same function's offset_source branch) gets the same expansion and a test. (4) The guard must hold when the operand Factor is not among the pin's resolved Factors: unknown operand = REFUSE (fail closed), never skip — the existing `by_slug.get(feature) is not None` shape skips silently; say in the LG what the fixed code does for a missing Factor and test it. (5) Same hash, same price (FR-239): the fix refuses at compile and changes no scoring arithmetic and no spec_hash of a bundle that compiled before WITHOUT a control operand — a regression test over the freMTPL2 fixtures' hashes. (6) Spec: FR-240 (and FR-88 if it speaks of operands) gets a dated clarification that "fitted on a control Factor" includes a control operand of an interaction at any depth; the spec change is in the same commit as the code (CLAUDE.md §2). A stricter rule — an interaction over a control operand may not be declared `risk` at all, refused at Factor definition — is a DESIGN CHOICE the specs leave open: an OQ with options and a recommendation, not built in this slice. (7) Full gate, both halves, at the re-merged head; ids minted before the PR; LG with the red and green lines; audit; then the grant request. C6's sweep reads the backend save/approval path and POST /score end to end for the same gap and reports before this slice's audit.

**MERGE-ACK:** not yet given.

## Tasks

### Scope

WK-2113 has no Work plan yet (the Work is `draft`); the slice's row is `docs/roadmap.md` `#### SL-8429` under WK-2113. Requirements: `FR-88` (`02`), `FR-240` and `FR-239` (`03`). Out of scope by the brief: sweep cells G3, G4, G6 (awaiting rulings); the stricter definition-time rule (OQ 8431, not built); WK-2113's own status line.

### Task list

1. **Red first** (condition 1): the tests, committed alone as `575a5a68`, run via `run-small` at that head: 13 failed, 35 passed, rc=1, each failure `Failed: DID NOT RAISE ValueError`. The five positive controls (risk operands compile / pass) passed at the same head, so the harness is proven, not only the failures.
2. **Fix**: `control_factor_in(factor, pool)` in `packages/pricing-core/src/pricing_core/modelling/factors.py` expands a Factor to itself plus its transitive operands (by `operand_factor_ids` against `pool`) and returns the first `control` Factor; `rateable()` (G5, had no caller) now uses it, so there is one definition. Used by the compile feature guard (`_refuse_control_factor_features`, including the `offset_source` recursion), the compile key guard (`_refuse_control_factor_keys`) and the seed (`rate_tables/operations.py`).
3. **Backend resolver**: the `factor` branch of the compile resolver (`backend/src/app/platform/rating_versions.py`) returns `factors=` the chain `load_factor_by_ref` already builds (the Factor and its operands). Without it a table key's operands are not visible to compile and the fail-closed rule would refuse every interaction-keyed table. Its DB-backed tests are owed to the gate.
4. **FR-239 regression** (condition 5): `test_the_control_operand_guards_leave_the_fixture_bundle_hashes_unchanged` pins the freMTPL2 baseline and full-candidate `content_hash` (measured at the pre-fix code and at the fixed code: identical, `scratch/sl-8429-fd1495-interaction-operands/hash_probe.py`). The older pins `_PINNED_PRE_DECIMAL_HASH` and `_SCORE_FIXTURE_HASH` stay green in the GREEN set. The guards only refuse; no scoring arithmetic is touched.
5. **Spec** (condition 6), same commit: dated clarifications on `FR-240` (`03`) and `FR-88` (`02`); `OQ 8431` in `docs/open-questions.md` and `03` §10, mirrored; FD-1495's register row gains the new limb (HIGH, owner WK-2113, shipped impact "none known: freMTPL2 seed risk Factors only, no interactions; no non-template DB on this box"); the `SL-8429` row, `active`.

### Gate

**Red** (head `575a5a6866b1a6db8cae95e4172125f66700cf5a`, tests only; log `red.log`, first line `head=`, last line `rc=1`), `run-small` on `test_rating_compile_fr240.py`: `13 failed, 35 passed in 4.44s`, rc=1. Each failure line (all `E       Failed: DID NOT RAISE ValueError`):

```
FAILED test_rating_compile_fr240.py::test_the_feature_guard_refuses_a_risk_interaction_over_a_control_operand
FAILED test_rating_compile_fr240.py::test_the_feature_guard_expands_a_nested_interaction_to_its_leaves
FAILED test_rating_compile_fr240.py::test_the_feature_guard_refuses_an_operand_that_is_not_among_the_pins_factors
FAILED test_rating_compile_fr240.py::test_the_feature_guard_refuses_a_control_operand_in_the_offset_model
FAILED test_rating_compile_fr240.py::test_the_feature_guard_refuses_a_missing_operand_in_the_offset_model
FAILED test_rating_compile_fr240.py::test_a_model_call_over_a_glm_with_a_control_operand_interaction_is_refused
FAILED test_rating_compile_fr240.py::test_a_model_call_over_a_glm_whose_interaction_operand_is_missing_is_refused
FAILED test_rating_compile_fr240.py::test_the_key_guard_refuses_a_table_keyed_on_an_interaction_of_a_control_operand
FAILED test_rating_compile_fr240.py::test_the_key_guard_expands_a_nested_interaction_to_its_leaves
FAILED test_rating_compile_fr240.py::test_the_key_guard_refuses_an_interaction_whose_operand_is_not_resolved
FAILED test_rating_compile_fr240.py::test_seeding_from_an_interaction_of_a_control_operand_is_refused
FAILED test_rating_compile_fr240.py::test_seeding_from_a_nested_interaction_expands_to_the_leaves
FAILED test_rating_compile_fr240.py::test_seeding_from_an_interaction_with_a_missing_operand_is_refused
```

**Green** (the fixed head; logs under `scratch/sl-8429-fd1495-interaction-operands/`, each `head=` first and `rc=` last):

| check | head | result | rc |
|---|---|---|---|
| import-closure set, pricing-core part: 67 test files in 23 `run-small` batches of at most three (`green-core.log`) | `3f0eebbd` | 22 batches rc 0; batch 8 (`test_prediction_interval.py`, `test_quantile_crossing.py`, `test_quote_input_raise_sites.py`) rc 1: `test_every_quote_input_raise_site_has_a_sentinel_case`, the census counted two `_raise_named` sites in each of `_refuse_control_factor_keys` and `_refuse_control_factor_features` where the allow-list said one | 1 |
| census fix `ae216c91`: `test_quote_input_raise_sites.py`, `test_rating_compile_fr240.py`, `test_fremtpl2_rate_fixture.py` (`green-census.log`) | `ae216c91cc55` | 71 passed | 0 |

The 107 backend test files the closure reaches need a database and are **owed to the gate** (brief: no DB lane for the seat). The closure is derived by `closure.py` (the changed source modules, every source file importing one, one more level of importers; GREEN = every test file importing anything in it): `git diff --name-only HEAD -- packages backend/src` for the changed modules, then an `ast` walk of `packages/**/src` and `backend/src`; lists in `changed.txt` and `green-tests.txt`. The route sweep `backend/tests/test_api_authorisation_sweep.py` is not in the closure (no request shape changed) and not run.

### Condition-by-condition evidence

1. **Red first**: above; four named tests (feature guard, `_refuse_control_factor_keys`, seed at `operations.py`, end-to-end `compile_bundle` naming the operand `yoa@1` and the cross `region_x_yoa`) are among the 13.
2. **Nested interactions**: `control_factor_in` walks to any depth (a visited set bounds a cycle); tests at depth 2 for the feature guard, the key guard and the seed. **Can a nested cross reach a pin?** `_cross` (`factors.py`) raises `FactorResolutionError` for an interaction operand at resolution, and the backend `load_factors` expands one level only, so a nested Factor can be stored but cannot be fitted or scored; the guard does not rely on that and refuses it by expansion, or by the missing deeper operand (fail closed).
3. **Offset branch**: `_refuse_control_factor_features` recurses into `offset_source` and now tests the closure there; tests for a control operand and for a missing operand in the offset model.
4. **Missing operand**: an operand id not among the pin's Factors raises `FactorResolutionError` in `control_factor_in`; every caller converts it to `CONTROL_FACTOR_IN_RATEABLE_PATH` naming the cross and the operand id. Tested for a model, an offset model, an end-to-end `compile_bundle`, a table key and a seed. **What the fixed code does for a consumed feature with NO Factor at all** (`by_slug.get(feature) is None`): kept, it is not refused. A feature with no Factor has no intent to be `control`; `03` FR-222's amendment names "its `feature_order` when it has no Factors" as a legal required-input set (a GBM on raw columns). A Factor the pin carries but whose operand it does not is refused. 
5. **Same hash, same price**: item 4 of the task list.
6. **Spec**: item 5; OQ 8431 given options and a recommendation, not built.
7. **Full gate, ids minted, audit, grant request**: not this seat's; the full gate is owed (no grant yet), ids stay working, no PR.

### Audit

Not yet written; the auditor re-checks.

### Build log

- 2026-11-13: `575a5a68` red tests (13 failed, rc=1). Pushed.
- 2026-11-13: `3f0eebbd` the fix, the backend resolver line, the FR-240/FR-88 clarifications, OQ 8431, the register limb and the `SL-8429` row.
- 2026-11-13: `ae216c91` the raise-site census counts the two new raise sites (found by the closure run: item 11 of the common brief).
- Note: the first docs-only commands of this seat used `cd` inside a compound command (the harness resets the cwd each call), against the no-`cd` rule; no write followed from a changed directory.

## PRs

None yet: the lead opens the PR.
