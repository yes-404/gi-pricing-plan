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
