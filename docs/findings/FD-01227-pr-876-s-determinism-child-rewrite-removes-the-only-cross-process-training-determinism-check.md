---
id: FD-1227
family: finding
title: PR #876's determinism-child rewrite removes the only cross-process training-determinism check
status: active
created: 2026-09-29
owner: auditor
tree: ce9303b3dcf1007c6d97bf8e73e5b3e3f3174d1d
corrected_by: []
relates: [WK-1178]
---

# FD-1227 — PR #876's determinism-child rewrite removes the only cross-process training-determinism check

## Finding

**Severity: low.** A coverage loss with no
current requirement breach: `NFR-481` and `FR-11` (quoted below) do not say "across processes". It does not block #876.

At `ce9303b3`, `test_scoring_is_deterministic_across_a_subprocess` trains a booster in a second interpreter. PR #876 (open, head
`45c77f4d94f7…`, "fix(tests): the determinism child exits without interpreter teardown (FD-1199)") rewrites that child so it trains
nothing, and no other test trains in a second interpreter.

## Evidence

**The old child trained.** `packages/pricing-core/tests/test_rating_score.py:561` (at `ce9303b3`) runs a `python -c` script that
imports `_compiled` from the test module and calls it in the child. `_compiled` (`:136`) builds `_FakeResolver()` (`:102`), whose
constructor calls `_train_tiny_booster()` (`:104`), defined at `packages/pricing-core/tests/test_rating_runtime.py:30-39`: a raw
`xgb.train` on five rows for three rounds, serialised with `save_raw(raw_format="json")`. The child then scores and the parent
compares `hash`, `payable` and `outcome` with an in-process run.

**A correction to the account this finding was filed from.** That account said the compared `hash` covered the child-trained booster.
It does not. `content_hash` is `bundle_hash(graph, pins)` (`packages/pricing-core/src/pricing_core/rating/compile.py:404-417`), a hash of the
graph and the pins, and `Pins` (`packages/model-schema/src/model_schema/rating.py:63`) holds artifact **references** (`ArtifactRef`), not
booster bytes. What depended on the child-trained booster is `payable` (the premium) and `outcome`. So the old check compared a premium
in integer minor units drawn from a five-row, three-round booster, which is real but a weak proxy for booster identity.

**The new child does not train.** At `45c77f4d` the child (`_DETERMINISM_CHILD`) reads the artifact payloads and the quote inputs as JSON on
stdin, compiles and scores with `pricing_core.rating` alone; the parent builds `_FakeResolver()` and so trains the booster in the parent. The
child never calls `xgb.train`. Its own comment says it imports "`pricing_core.rating` and `model_schema` only".

**No other test trains in a second interpreter.** A search of `ce9303b3` for `subprocess.(run|Popen)`, `multiprocessing` and `ProcessPool`
under `packages`, `backend/tests` and `tests` finds, in the model-training area, only `test_model_round_trip.py`,
`test_scoring_without_the_fitting_stack.py` and `test_rating_score.py`; the others (`backend/tests/test_contracts.py`, `test_lineage*.py`, the
root `tests/test_audit_docs*`, `test_doc_*` and similar) contain no `fit_gbm`, `fit_glm`, `fit_ebm`, `xgb.train` or `lgb.train` call
(`git grep -c` prints nothing for the three backend files; the root `tests/` search prints nothing). In the two model tests the fit is in
the parent (`test_model_round_trip.py:108`; `test_scoring_without_the_fitting_stack.py:136` and `:203`) and only scoring runs in the child, and
the second file's child cannot import the fitting stack by design. The three refit tests run **in one process**:
`test_glm.py:731` (`test_two_fits_of_one_spec_reproduce_identical_coefficients`), `test_gbm.py:349-361`
(`test_the_same_spec_and_seed_produce_the_same_booster`, two `fit_gbm` calls then a `booster_blob.sha256` comparison) and `test_ebm.py:428`
(`test_the_fit_is_reproducible_under_the_spec_seed`).

**The requirements, in full, at `ce9303b3`.**

`docs/specs/02-modelling.md:2868`:

> | **NFR-481** | Determinism: identical `spec_hash` + seed reproduces identical coefficients to 1e-10 (GLM) and an identical booster hash (GBM), on the same library versions (FR-11). |

`docs/specs/00-overview.md:215`:

> | **FR-11** | Determinism: given identical inputs and pinned artifact versions, model fitting and scoring reproduce identical outputs. All stochastic operations take an explicit persisted `random_seed`. |

The 2026-08-22 verdict for NFR-481 (`docs/specs/02-modelling.md:3166-3192`, the WK-661 closure note) says both halves now carry markers: "Until this
date the single marker it carried was the **booster half** (`test_gbm.py:270`)", and the GLM half is `test_glm.py::test_two_fits_of_one_spec_reproduce_identical_coefficients`,
"It fits **one `GlmSpec` object twice** over one frame". **Neither text says "across processes"**, and the closure note's own evidence is an in-process double fit. So the
loss is of a check the requirements do not name.

## Disposition

**Deferred with an owner — WK-1178.** Event: the lead adopts, amends or rejects the proposal below, or #876 merges without one, and
the auditor reads the merged child at that time.

**Proposed open question, in this text only (no open-questions row is added here; that is a spec change for its owner):** should
`NFR-481` (or `FR-11`) say that a fit reproduces its result **across processes**? Options: (a) no, leave the wording; the in-process double fits are
what the requirement names, and this finding is a note; (b) yes, amend the requirement, and keep a child-side training test as its
evidence. **Recommendation:** first restore a small child-side training check as a test-only change, which needs no spec decision and is cheap, and put
the wording question to the maintainer; process-level nondeterminism (thread scheduling, hash randomisation) is exactly what an in-process double fit cannot see,
and FR-11's sentence "given identical inputs … reproduce identical outputs" does not limit itself to one process.

*(2026-09-29: since raised as OQ-1229.)*
