---
id: LG-8304
family: ledger
title: WK-673 Slice SL-8303 — FD-1495, a pinned model's consumed Factors derived per arm and refused when empty (red-first slice ledger)
status: active
created: 2026-11-03
owner: executor
tree: cc8fca15556365412a1ec1c972a1c1799bcb559f
phase: P2
work: WK-673
slice: SL-8303
plans: [PL-8302]
corrected_by: []
relates: [FD-1495]
---

# LG-8304 — SL-8303: FD-1495, S-a

**GO:** to-lead "2026-11-03 16:28:44 GMT", with "2026-11-03 16:19:35 GMT" (2) to (5) (binding remedy shape) and the DB-free single-file grant "2026-11-03 17:19:47 GMT" (load condition tuned to load1 < 4 by "2026-11-03 17:36:02 GMT").
**MERGE-ACK:** (added at merge)

## Tasks

### Scope

PL 8302 Row 1, S-a (FD-1495): Acceptance 1 to 6. Requirements: FR-88, FR-240. Base: `origin/draft/pl-wk673fix` a2679afe (`main` a8ef6f19, no merge needed).

### Task list

- T0 re-read at the base: every site matched the plan's line numbers (`compile.py:844/:992/:1059`, `runtime.py:621`, `rating_algorithms.py:142`). No open PR read (`gh pr list` printed nothing).
- T1 reds (`ada52401`, `c9142a2b`, `5c17c974`, `cc8fca15`); T2 fix (`c9a35475`); fixture fallout, one commit each (below).

Acceptance 1, departure recorded: the plan says the derivation "validates with `FIT_RESULT_ADAPTER`". Departed from on the lead's ruling (A), upheld by the maintainer: five fixture files (`test_rating_compile_bundle`, `_completeness`, `_fr240`, `test_rating_column_collision`, `test_rating_declared_reads`, `test_rating_gbm_banded_save` on the lead's count of six) feed compile PARTIAL `fit_result` dicts that full validation rejects. `consumed_features` (`modelling/factors.py`) dispatches on `model_type`: GBM requires a `feature_order` list of str; GLM reads `coefficients[*].term` (intercept dropped, slug = text before "["; the grammar is `predict._DUMMY`'s, which cannot be imported there without a cycle); anything else, a missing or mistyped field, or an empty set raises, and the callers refuse with `CONTROL_FACTOR_IN_RATEABLE_PATH`.

Acceptance 5, whole-tree grep (`git grep -n -E 'fit_result\.get\(|\.get\("feature_order"|fit_result or \{\}\)\.get\(' -- '*.py'`):
- Base (a2679afe): `compile.py:844,:992,:1033,:1059`; `runtime.py:621,:641,:1008`; `rating_algorithms.py:142`.
- Head: `compile.py:1051` (model_type), `runtime.py:641,:1008` (model_type), `factors.py:518,:521,:526` (inside `consumed_features`, which is the one derivation). Each `model_type` read dispatches on a required discriminator and feeds no refusal.

### Gate

Not yet run (full SOLO gate is a separate seat). Single-file runs below: tree = worktree sl-8303 at the head named per line; env for every run `GIP_TEST_DATABASE_URL`/`GIP_TEST_APP_DATABASE_URL` = `postgresql+asyncpg://nobody:nobody@127.0.0.1:1/none`, `GIP_REDIS_URL=redis://127.0.0.1:1/13` (dead ports) from the lead's urgent message; the conftest chain of `packages/pricing-core/tests` is root `conftest.py` (fcntl lock, no DB) and `packages/pricing-core/tests/conftest.py` (sys.path only); neither references `conftest_db`. No `backend/tests` file was run (their conftest reaches Postgres). Runs before the dead-port message (the first five logs) were pricing-core files with the same chain and the same empty grep for postgres/redis/database.

```text
== red.log
head=a2679afe src + ada52401 tests (base code, reds)
>       with pytest.raises(ValueError, match="CONTROL_FACTOR_IN_RATEABLE_PATH") as refused:
E       Failed: DID NOT RAISE ValueError
>       with pytest.raises(ValueError, match="CONTROL_FACTOR_IN_RATEABLE_PATH") as refused:
E       Failed: DID NOT RAISE ValueError
>       with pytest.raises(ValueError, match="CONTROL_FACTOR_IN_RATEABLE_PATH") as refused:
E       AssertionError: Regex pattern did not match.
packages/pricing-core/tests/test_rating_compile_fr240.py:328: AssertionError
>       with pytest.raises(ValueError, match="CONTROL_FACTOR_IN_RATEABLE_PATH") as refused:
E       AssertionError: Regex pattern did not match.
packages/pricing-core/tests/test_rating_compile_fr240.py:328: AssertionError
>       with pytest.raises(ValueError, match="CONTROL_FACTOR_IN_RATEABLE_PATH") as refused:
E       AssertionError: Regex pattern did not match.
packages/pricing-core/tests/test_rating_compile_fr240.py:328: AssertionError
>       with pytest.raises(ValueError, match="CONTROL_FACTOR_IN_RATEABLE_PATH") as refused:
E       AssertionError: Regex pattern did not match.
packages/pricing-core/tests/test_rating_compile_fr240.py:328: AssertionError
FAILED packages/pricing-core/tests/test_rating_compile_fr240.py::test_a_model_call_over_a_glm_fitted_on_a_control_factor_is_refused
FAILED packages/pricing-core/tests/test_rating_compile_fr240.py::test_a_model_call_over_a_glm_whose_offset_model_is_fitted_on_a_control_factor_is_refused
FAILED packages/pricing-core/tests/test_rating_compile_fr240.py::test_a_model_call_over_a_model_whose_fit_result_lacks_the_fields_is_refused[glm-no-coefficients]
FAILED packages/pricing-core/tests/test_rating_compile_fr240.py::test_a_model_call_over_a_model_whose_fit_result_lacks_the_fields_is_refused[glm-intercept-only]
FAILED packages/pricing-core/tests/test_rating_compile_fr240.py::test_a_model_call_over_a_model_whose_fit_result_lacks_the_fields_is_refused[gbm-no-feature_order]
FAILED packages/pricing-core/tests/test_rating_compile_fr240.py::test_a_model_call_over_a_model_whose_fit_result_lacks_the_fields_is_refused[gbm-empty-feature_order]
6 failed, 16 passed in 10.12s
rc=1
== red2.log
head=a2679afe src + tests worktree (base code, reds, fixture fix)
E       Failed: DID NOT RAISE ValueError
E       Failed: DID NOT RAISE ValueError
E       Failed: DID NOT RAISE ValueError
E       Failed: DID NOT RAISE ValueError
E       Failed: DID NOT RAISE ValueError
E       Failed: DID NOT RAISE ValueError
FAILED packages/pricing-core/tests/test_rating_compile_fr240.py::test_a_model_call_over_a_glm_fitted_on_a_control_factor_is_refused
FAILED packages/pricing-core/tests/test_rating_compile_fr240.py::test_a_model_call_over_a_glm_whose_offset_model_is_fitted_on_a_control_factor_is_refused
FAILED packages/pricing-core/tests/test_rating_compile_fr240.py::test_a_model_call_over_a_model_whose_fit_result_lacks_the_fields_is_refused[glm-no-coefficients]
FAILED packages/pricing-core/tests/test_rating_compile_fr240.py::test_a_model_call_over_a_model_whose_fit_result_lacks_the_fields_is_refused[glm-intercept-only]
FAILED packages/pricing-core/tests/test_rating_compile_fr240.py::test_a_model_call_over_a_model_whose_fit_result_lacks_the_fields_is_refused[gbm-no-feature_order]
FAILED packages/pricing-core/tests/test_rating_compile_fr240.py::test_a_model_call_over_a_model_whose_fit_result_lacks_the_fields_is_refused[gbm-empty-feature_order]
6 failed, 16 passed in 3.62s
rc=1
== green1.log
head=c9142a2b6619c0dac65e3c7a95cae22aeed253cd (fix)
E       pricing_core.safe_error.CodedError: CONTROL_FACTOR_IN_RATEABLE_PATH: model:motor-ad-frequency@7: the Factors it consumes cannot be derived (the fit result is not a mapping), so it cannot be shown not to price on a `control`-intent Factor (FR-88, FR-240)
E       pricing_core.safe_error.CodedError: CONTROL_FACTOR_IN_RATEABLE_PATH: model:motor-ad-frequency@7: the Factors it consumes cannot be derived (the fit result is not a mapping), so it cannot be shown not to price on a `control`-intent Factor (FR-88, FR-240)
E       pricing_core.safe_error.CodedError: CONTROL_FACTOR_IN_RATEABLE_PATH: model:motor-ad-frequency@7: the Factors it consumes cannot be derived (the fit result is not a mapping), so it cannot be shown not to price on a `control`-intent Factor (FR-88, FR-240)
E       pricing_core.safe_error.CodedError: CONTROL_FACTOR_IN_RATEABLE_PATH: model:motor-ad-frequency@7: the Factors it consumes cannot be derived (the fit result is not a mapping), so it cannot be shown not to price on a `control`-intent Factor (FR-88, FR-240)
FAILED packages/pricing-core/tests/test_rating_compile_fr240.py::test_an_approved_objective_reached_through_a_pinned_model_compiles
FAILED packages/pricing-core/tests/test_rating_compile_fr240.py::test_a_builtin_objective_needs_no_resolution
FAILED packages/pricing-core/tests/test_rating_compile_fr240.py::test_a_table_keyed_on_a_risk_factor_compiles
FAILED packages/pricing-core/tests/test_rating_compile_fr240.py::test_g1_an_approved_objective_in_a_pinned_sub_graph_compiles
4 failed, 18 passed in 3.48s
rc=1
== green2.log
head=412567d87e9693941fe01a30fb395006ca70af5f
E       pricing_core.safe_error.CodedError: CONTROL_FACTOR_IN_RATEABLE_PATH: model:planted@1: the Factors it consumes cannot be derived (the fit result is not a mapping), so it cannot be shown not to price on a `control`-intent Factor (FR-88, FR-240)
E       pricing_core.safe_error.CodedError: CONTROL_FACTOR_IN_RATEABLE_PATH: model:motor-ad-frequency@7: the Factors it consumes cannot be derived (the fit result is not a mapping), so it cannot be shown not to price on a `control`-intent Factor (FR-88, FR-240)
E       AssertionError: Regex pattern did not match.
E         Expected regex: '^MODEL_CALL_FEATURE_MAP_INVALID: '
E         Actual message: 'CONTROL_FACTOR_IN_RATEABLE_PATH: model:motor-ad-frequency@7: the Factors it consumes cannot be derived (the fit result is not a mapping), so it cannot be shown not to price on a `control`-intent Factor (FR-88, FR-240)'
E       pricing_core.safe_error.CodedError: CONTROL_FACTOR_IN_RATEABLE_PATH: model:motor-ad-frequency@7: the Factors it consumes cannot be derived (the fit result is not a mapping), so it cannot be shown not to price on a `control`-intent Factor (FR-88, FR-240)
E       pricing_core.safe_error.CodedError: CONTROL_FACTOR_IN_RATEABLE_PATH: model:motor-ad-frequency@7: the Factors it consumes cannot be derived (the fit result is not a mapping), so it cannot be shown not to price on a `control`-intent Factor (FR-88, FR-240)
E       pricing_core.safe_error.CodedError: CONTROL_FACTOR_IN_RATEABLE_PATH: model:motor-ad-frequency@7: the Factors it consumes cannot be derived (the fit result is not a mapping), so it cannot be shown not to price on a `control`-intent Factor (FR-88, FR-240)
E       pricing_core.safe_error.CodedError: CONTROL_FACTOR_IN_RATEABLE_PATH: model:motor-ad-frequency@7: the Factors it consumes cannot be derived (the fit result is not a mapping), so it cannot be shown not to price on a `control`-intent Factor (FR-88, FR-240)
FAILED packages/pricing-core/tests/test_rating_compile_fr240.py::test_g1_an_approved_objective_in_a_pinned_sub_graph_compiles
FAILED packages/pricing-core/tests/test_rating_compile_bundle.py::test_a_decimal_input_bound_hashes_deterministically
FAILED packages/pricing-core/tests/test_rating_compile_completeness.py::test_a_glm_model_call_missing_a_factor_is_refused_at_compile
FAILED packages/pricing-core/tests/test_rating_compile_completeness.py::test_a_complete_feature_map_compiles[glm]
FAILED packages/pricing-core/tests/test_rating_compile_completeness.py::test_a_complete_feature_map_compiles[surplus]
FAILED packages/pricing-core/tests/test_rating_compile_completeness.py::test_an_unmapped_offset_column_is_not_a_completeness_failure
FAILED packages/pricing-core/tests/test_rating_compile_completeness.py::test_the_compile_check_calls_the_one_required_inputs_helper
7 failed, 61 passed in 9.96s
rc=1
== green3.log
head=1a5be7391167c18a563c5749c9ea1b25e0d1ac2d
68 passed in 5.57s
rc=0
== green4.log
head=1a5be7391167c18a563c5749c9ea1b25e0d1ac2d
E       AssertionError: a `_raise_named` site is not accounted for: give it a sentinel case, or list it in _INPUT_FREE with why it is input-free. Found {('rating/compile.py', '_raise_named'): 1, ('rating/compile.py', '_refuse_mount_port_type_mismatch'): 1, ('rating/compile.py', 'check_step_refs_pinned'): 1, ('rating/compile.py', '_refuse_unapproved_objectives'): 1, ('rating/compile.py', '_refuse_control_factor_keys'): 1, ('rating/compile.py', '_consumed_features'): 1, ('rating/compile.py', '_refuse_control_factor_features'): 1, ('rating/compile.py', '_refuse_peril_model_calls'): 1, ('rating/compile.py', '_resolve_peril_components'): 3, ('rating/compile.py', 'check_model_call_coverage'): 1, ('rating/compile.py', 'check_model_call_gbm_factors'): 1, ('rating/compile.py', 'check_model_call_columns'): 1, ('rating/compile.py', 'compile_bundle'): 6, ('rating/inline.py', '_raise_named'): 1, ('rating/inline.py', '_port_mapping'): 4, ('rating/inline.py', '_inline_one'): 1, ('rating/inline.py', 'mounted_fragments'): 3, ('rating/inline.py', 'inline_mounts'): 3, ('rating/runtime.py', 'handler'): 4, ('rating/runtime.py', '_load_boosters'): 1, ('rating/runtime.py', '_check_graph_matches_inlined_algorithm'): 1, ('rating/score.py', '_raise_named'): 1, ('rating/score.py', '_engine_context'): 1, ('rating/score.py', '_check_purpose_mount'): 1, ('rating/score.py', '_check_billing_surface'): 1, ('rating/score.py', '_check_no_shadowed_produced_names'): 1, ('rating/score.py', '_check_as_at_values'): 1, ('rating/score.py', '_check_model_call_sentinel'): 1, ('rating/score.py', '_check_lookup_misses'): 2, ('rating/score.py', '_reraise_engine_failure'): 1, ('rating/score.py', '_build_outputs'): 1, ('rating/score.py', 'build_scoring_result'): 1, ('rating/score.py', 'score_one'): 1}
E       assert {('rating/com...ves'): 1, ...} == {('rating/com...mes'): 1, ...}
E         
E         Omitting 31 identical items, use -vv to show
E         Left contains 2 more items:
E         {('rating/compile.py', '_consumed_features'): 1,
E          ('rating/compile.py', '_refuse_control_factor_features'): 1}
E         Right contains 1 more item:
E         {('rating/compile.py', '_refuse_control_factor_model_calls'): 1}
E         Use -v to get more diff
FAILED packages/pricing-core/tests/test_quote_input_raise_sites.py::test_every_quote_input_raise_site_has_a_sentinel_case
1 failed, 65 passed in 8.85s
rc=1
== green5.log
head=50734f9b02d866bcc503a73acc33663f77971533
36 passed in 6.63s
rc=0
== green6.log
head=50734f9b02d866bcc503a73acc33663f77971533
E       pricing_core.safe_error.CodedError: CONTROL_FACTOR_IN_RATEABLE_PATH: model:ad-freq@1: the Factors it consumes cannot be derived (the fit result's model_type None has no derivation), so it cannot be shown not to price on a `control`-intent Factor (FR-88, FR-240)
E       AssertionError: Regex pattern did not match.
E         Expected regex: '^MODEL_CALL_FEATURE_MAP_INVALID: '
E         Actual message: "CONTROL_FACTOR_IN_RATEABLE_PATH: model:ad-freq@1: the Factors it consumes cannot be derived (the fit result's model_type None has no derivation), so it cannot be shown not to price on a `control`-intent Factor (FR-88, FR-240)"
FAILED packages/pricing-core/tests/test_rating_column_collision.py::test_frequency_and_severity_banding_one_column_differently_compile
FAILED packages/pricing-core/tests/test_rating_column_collision.py::test_a_collision_inside_one_component_is_refused
2 failed, 29 passed in 4.56s
rc=1
== green7.log
head=b0d00170c838bb8b0500fa45740be8302227f44f
12 passed in 3.99s
rc=0
== red-c.log
head=a2679afe src, 844 scratch-broken, tests cc8fca15 env=dead-port URLs
E       AssertionError: Regex pattern did not match.
E         Expected regex: 'CONTROL_FACTOR_IN_RATEABLE_PATH'
E         Actual message: "MODEL_CALL_FEATURE_MAP_INVALID: step 's_rp': the feature_map does not map ['year_of_account'], which model:motor-ad-frequency@7 requires (FR-240)"
E       Failed: DID NOT RAISE ValueError
E       Failed: DID NOT RAISE ValueError
E       Failed: DID NOT RAISE ValueError
E       Failed: DID NOT RAISE ValueError
E       Failed: DID NOT RAISE ValueError
E       Failed: DID NOT RAISE ValueError
FAILED packages/pricing-core/tests/test_rating_compile_fr240.py::test_a_model_call_over_a_gbm_fitted_on_a_control_factor_is_refused
rc=1
```
Closure sweep (37 importers of the changed modules, `closure.txt`, batches of 3): 12 batches rc=0, one rc=1 (`test_rating_declared_reads.py`, 2 failed, fixed in b0d00170, then 12 passed).

(c), the GBM arm: the scratch-broken base (`compile.py:844` read as `()`) turns the unedited GBM test red, but the later coverage check answers first, so it fails with MODEL_CALL_FEATURE_MAP_INVALID, not DID NOT RAISE (log `red-c.log` above). The scratch edit was reverted (clean worktree).

OWED (DB window): the save-check red `test_a_feature_map_over_a_model_whose_fit_result_lacks_the_fields_is_refused_at_save`, red at base and green at head, and the rest of `backend/tests/test_rating_algorithms.py`.

### Audit

(the auditor's)

### Build log

- 2026-11-03: fixture commits, each preserving every assertion: `412567d8` `test_rating_compile_bundle._resolver()` (model gets `feature_order` [driver_age, rating_area], exactly what its model_call maps); `5b1924b9` `_compile_with_decimal_bound`; `2eb8657f` `_planted_in_a_sub_graph` (feature_order [ncd_years]); `1a5be739` `test_rating_compile_completeness._glm_world` (GLM terms for its two Factors); `e055787c` `test_rating_column_collision._pin` (was `{feature_order: []}` with Factors; now GLM terms = the Factor slugs); `b0d00170` `test_rating_declared_reads._StubResolver` (stub model consumes what the example maps).
- `50734f9b` `test_quote_input_raise_sites.py`: the registry follows the moved raise sites (not a fixture; flagged to the lead).
- Fixture defect in my own reds (`c9142a2b`): case (d) used a feature_map that did not cover the model, so it raised MODEL_CALL_FEATURE_MAP_INVALID; expectation unchanged.

## PRs

(none yet)
