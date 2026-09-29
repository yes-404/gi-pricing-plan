---
id: FD-1228
family: finding
title: test_ebm.py's reproducibility test is marked FR-140, a transparency requirement, so FR-11 gets no EBM determinism evidence
status: active
created: 2026-09-29
owner: auditor
tree: 6a8b8e7011e472586be559587561dde0479d491f
corrected_by: []
relates: [WK-1178]
---

# FD-1228 — test_ebm.py's reproducibility test is marked FR-140, a transparency requirement, so FR-11 gets no EBM determinism evidence

## Finding

**Severity: low.** `test_the_fit_is_reproducible_under_the_spec_seed`
(`packages/pricing-core/tests/test_ebm.py:427-428`, read at `6a8b8e70`) carries `@pytest.mark.req("FR-140")`, but `FR-140` is an EBM
**transparency** requirement and says nothing about reproducibility. Two effects, both named in the Evidence: the marker credits `FR-140` with evidence
it does not give, and the EBM's fit determinism is credited to no determinism requirement.

## Evidence

**The test.** `test_ebm.py:427` is `@pytest.mark.req("FR-140")` and `:428` is `def test_the_fit_is_reproducible_under_the_spec_seed()`. It fits the
same book twice with `fit_ebm` and asserts `first.terms == second.terms` and `first.intercept == second.intercept`, then fits with seeds 1 and 2 and
asserts the first term's scores differ. It is a determinism test: it says the same spec and seed give the same terms, in one process.

**FR-140, in full** (`docs/specs/02-modelling.md:199` at `6a8b8e70`):

> | **FR-140** | EBM (`interpret`) models are treated as transparent by construction: their term shape functions are exported directly as tables and require no approximation, but they still carry the fidelity/diagnostic sections in the same contract shape. |

**The later mentions of FR-140 carry no amendment about determinism.** `02-modelling.md` names it at `:275`, `:843`, `:1393`, `:1454` and `:2840`. `:275` is the FR-180
row ("FR-140 made an EBM storable and §5.2's `predict_ebm` made it scoreable"); `:843` is "Added 2026-08-21 (WK-661, the EBM slice, FR-140). The common block is
inherited"; `:1393` is "The fit result IS the model (2026-08-21, WK-661, the EBM slice, FR-140)"; `:1454` is "shape (FR-140's requirement text stays as the contract)";
`:2840` is the technology row "Transparent ML (FR-140) … Exporting term shape functions as tables". All five are about export, storage and scoring. A scan of the
whole file for a line that names EBM and also reproducibility, determinism, "same seed" or "identical" prints no line.

**Effect 1: `req-coverage` credits `FR-140` with evidence it does not have.** `scripts/req-coverage.py` (read, and run at `6a8b8e70` with rc=0) reads each
`@pytest.mark.req("<id>")`, maps it to the requirement and prints **the number of test files** per requirement: it prints `FR-140           36 test file(s)`.
Because it counts files, and `test_ebm.py` carries eight other `FR-140` markers (nine in all, including this one), removing this one marker would not change that number, so **the report cannot show this
mis-tag at test granularity**; it is visible only by reading the marker against the requirement's text. Also for the record, `test_ebm.py:444`
(`test_fit_seconds_and_library_versions_are_recorded`, `FR-140`) records `fit_seconds` and library versions, which is not transparency either; this record notes it and does not
decide it.

**Effect 2: EBM fit determinism is credited to `FR-11` or `NFR-481` by no test.** The same report prints `FR-11            1 test file(s)`, and the
only `FR-11` marker in the tree is `backend/tests/test_lineage.py:223`. `NFR-481` prints `2 test file(s)`, `test_gbm.py:349` and `test_glm.py:730`, and its own text names
only "coefficients … (GLM) and … booster hash (GBM)" (`02-modelling.md:2868`). `FR-11` (`docs/specs/00-overview.md:215`) reads:

> | **FR-11** | Determinism: given identical inputs and pinned artifact versions, model fitting and scoring reproduce identical outputs. All stochastic operations take an explicit persisted `random_seed`. |

An EBM fit is model fitting, so the EBM's determinism test is evidence for `FR-11`, and today it is not.

## Disposition

**Deferred with an owner — WK-1178.** A separate **test-only** change, not made here: re-tag `test_the_fit_is_reproducible_under_the_spec_seed` `FR-11` (it is not the
GLM or GBM clause `NFR-481` names; whether `NFR-481` should name the EBM is not decided here), and establish `FR-140`'s real evidence, that is, which test shows the term shape functions
are exported as tables with no approximation. Event: that change merges, and the auditor reads each `FR-140` marker in `test_ebm.py` against the requirement's text and re-runs
`scripts/req-coverage.py`.
