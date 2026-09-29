---
id: FD-1195
family: finding
title: A GBM declaring a sparse cross cannot produce diagnostics
status: active
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

