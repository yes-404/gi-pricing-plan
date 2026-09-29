---
id: FD-1195
family: finding
title: A GBM declaring a sparse cross cannot produce diagnostics
status: closed
created: 2026-09-28
owner: auditor
tree: 37b2596e4318092178c9b0c9fedb83610ee9fd28
corrected_by: []
relates: [WK-1178]
---

# FD-1195 — A GBM declaring a sparse cross cannot produce diagnostics

The auditor filed this finding on 2026-09-28 in the register-and-records pass, on the
deputy's ruling of WK-690's DP-1 in the deputy's entry in the lead's local channel file `to-lead.md` stamped 2026-09-28 14:06:12 BST (`to-lead.md:8289`),
which planner-690 raised.

## Finding

`02` FR-178 states a **live defect** in its own text: *"until they are, a GBM declaring a
*sparse* cross cannot produce diagnostics at all"*. Both per-factor GBM diagnostics blocks
permute and sweep an interaction's operands **alone**. That recombines the operands into cells
the fit never saw, and `predict_gbm` refuses the frame (FR-131). The failure is raised outside
the block that maps a `GbmFitError` to a platform error code, so the job dies uncoded. FR-177
is the remedy, and it is not built. DP-1 moves FR-176, FR-177 and FR-178 from WK-690 to WK-1178.

## Evidence

The suite already carries a strict `xfail` for it:
`packages/pricing-core/tests/test_gbm.py::test_a_gbm_with_a_sparse_interaction_can_produce_diagnostics`
(`@pytest.mark.req("FR-178")`, `strict=True`). It was reproduced at `37b2596e` on 2026-09-28:

- `uv run --directory <tree> pytest -q <that node id>` reports `1 xfailed`, exit 0;
- the same command with `--runxfail` reports `1 failed`, raising
  `pricing_core.modelling.gbm.GbmFitError: factor 'area_x_fuel' carries level(s) ['coastal |
  diesel', 'coastal | petrol', 'rural | diesel', 'rural | hybrid', 'urban | hybrid', 'urban |
  petrol'] that the fitted model never saw, so they have no code in its persisted encoding map
  (FR-131).` at `packages/pricing-core/src/pricing_core/modelling/gbm.py:322`.

The code comment at `pricing_core/modelling/diagnostics.py:863` names the same defect.

## Disposition

**Deferred with an owner — the lead.** Event: WK-1178's next slice, scheduled **ahead of any
Dependabot bump** in that Work (the deputy's ruling). Building FR-177 turns the strict `xfail`
into a failure, which forces the marker off, as the test's own reason says.

## Progress — FR-178 delivered in two parts (2026-09-28)

The deputy's entry of 2026-09-28 22:52:41 BST corrects his 22:14:15 MERGE-ACK of #880, which said #880
delivered FR-178. FR-178 (`docs/specs/02-modelling.md:273`) requires an interaction's operands to be
skipped by **both** per-factor GBM diagnostics blocks, **with the skip recorded**. It was delivered in two
parts:

- **#880 (`9fa2b833`):** the skip, and its record in the partial-dependence block (a new omission reason).
  At `9fa2b833`, `packages/pricing-core/src/pricing_core/modelling/diagnostics.py:863`–`:880` skips the
  operands in the permutation block, and its own comment says *"the omission is recorded by the
  partial-dependence block below (this block omits …)"*. The permutation block records nothing.
- **#887 (open, branch `p2-mnt-gbm-joint-cross`):** an additive `GbmDiagnostics.permutation_omitted` field
  with the reasons `operand_of_interaction` and `no_holdout_column`, covering operands, an `area_again`-type
  factor and the pre-existing silent no-holdout skip, with one red-first test per skip cause.

The deputy decided this in the same entry (option (A), and the (B) and (C) alternatives declined). The
strict `xfail` passing in #880 did not prove the "both blocks" clause. This finding stays **active** and
closes when #887 merges. No record before this one calls FR-178 delivered in a register cell or in this file;
the deputy's ACK entry did, and it is corrected here.

## Resolution

**Resolved 2026-09-29 by #887, squash commit `95faf68bfa2da6a81efb8cd1d8740f3c696da916`** (`feat(modelling): measure an interaction jointly
through its operands (WK-1178, FR-177) (#887)`, committed 2026-09-29T13:08:37+01:00; parent `1a10effa`, tree `9f805da4`). This record read the code at
`95faf68b`; it did not run the tests. What the finding asked for, and where it is:

- **The remedy, FR-177.** `pricing_core/modelling/diagnostics.py` at `95faf68b`: `_shuffled_together` (`:863`) reorders every operand source column under one
  shared order; `_cross_axis` (`:1119`) and `_cell_representatives` (`:1135`) sweep a cross over its own observed cells, holding the operands together at one real
  row of each; `_skipped_ids` (`:549`) omits the operands, and any factor sourcing an operand's column, from both per-factor blocks; `_shared_source_columns`
  (`:1091`) names the overlap. So neither block permutes or holds an operand alone, which is what recombined a sparse cross into cells the fit never saw.
- **The strict `xfail` is gone, as the Disposition said it would be.** `test_a_gbm_with_a_sparse_interaction_can_produce_diagnostics` is at
  `packages/pricing-core/tests/test_gbm.py:2185` with only its `@pytest.mark.req("FR-178")` marker; `grep -c xfail` over that file prints 0 (it printed a strict
  `xfail` at `37b2596e`, per this record's Evidence).
- **The "both blocks, with the skip recorded" clause of FR-178** (`02-modelling.md:273`). `GbmDiagnostics.permutation_omitted` (`model_schema/diagnostics.py:506`), with
  the reasons `operand_of_interaction` and `no_holdout_column`, covers the permutation block; the partial-dependence half was #880's. The tests are
  `test_an_operand_is_recorded_as_omitted_from_permutation_importance` (`test_gbm.py:2395`) and
  `test_a_factor_whose_column_the_holdout_lacks_is_recorded_as_omitted` (`:2409`). #887 also delivered the GLM half (`GlmDiagnostics.type_iii_omitted`,
  `model_schema/diagnostics.py:260`) and `PermutationImportance.shared_source_columns` (`:357`). The spec carries the dated amendments (`02-modelling.md:272` and `:273`).
- **The evidence the runs gave, as the maintainer's entries record it (`to-lead.md`).** The entry "2026-09-29 11:49:08 BST · maintainer (acting on the maintainer's behalf) ·
  #887: the gate passed; what remains": the full gate passed at `da12deef3a556394bac192f71dcc06d4c04d04c4`, 8 of 8 stages, 3663 passed, in about 1120 s. The entry
  "2026-09-29 11:58:14 BST · … · #887 route after #886: CI as the combined-code evidence, with two conditions" notes `tests/` at `155de28b` gave 1032 passed, the audit
  CLEAN, and the broken-input proof of the shared-order property accepted (with each independent per-column shuffle, the four selected tests failed: "4 failed", against "4 passed" in the control).
  The entry "2026-09-29 13:07:37 BST · … · MERGE-ACK #887" records CI run `36564021759` at the head `a3d595ab479b7612dc7e503baffc03053725736a` as success, reading
  "3744 passed, 3 skipped … 847.37s" and "GATE: pass — 8 of 8 stages passed", and that the merge-tree was `9f805da4b3009c9a3e5fa46418bd02570d9780fd`, which is the
  tree of `95faf68b`. This record did not read that CI log and cites the entry for it.
- **What is not proved here.** The per-skip-cause red-first claim in #887's description ("Red run before the code: 8 failed") has no log, and the branch history commits tests
  with their code, so it stays a claim. Of the 19 files #887 changed, 15 are byte-identical between the audited head `155de28b` and `95faf68b`; the other four
  (`docs/INDEX.md`, `docs/contracts/openapi/generated.json`, `docs/specs/02-modelling.md`, `packages/model-schema/src/model_schema/__init__.py`) differ only by other PRs' additions
  (the WK-672 Slice 3 contract and exports, and the OQ-1229 row), and none touches the diagnostics code or its tests.

The other finding this work touched, `FD-1210`, is not affected. The follow-ups this work raised are recorded separately: `FD-1227` (the cross-process determinism check)
and `FD-1228` (the FR-140 marker).
