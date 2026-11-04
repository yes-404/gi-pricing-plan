---
id: LG-1986
family: ledger
title: WK-673 Slice SL-1985 — FD-1495, a pinned model's consumed Factors derived per arm and refused when empty (red-first slice ledger)
status: closed                 # active → closed (§1.2a)
created: 2026-11-03   # drafted 2026-11-03 under working id 8304; minted as LG-1986
owner: executor
tree: cc8fca15556365412a1ec1c972a1c1799bcb559f
phase: P2
work: WK-673
slice: SL-1985
plans: [PL-1984]
corrected_by: []
relates: [FD-1495]
---

# LG-1986 — SL-1985: FD-1495, S-a

**GO:** to-lead "2026-11-03 16:28:44 GMT", with "2026-11-03 16:19:35 GMT" (2) to (5) (binding remedy shape) and the DB-free single-file grant "2026-11-03 17:19:47 GMT" (load condition tuned to load1 < 4 by "2026-11-03 17:36:02 GMT").
**MERGE-ACK:** ~~(added at merge)~~ *(filled 2026-11-04, docs batch 8, by the auditor, on to-lead "2026-11-04 09:57:14 GMT" and "10:00:29 GMT" closing acts)* to-lead "2026-11-03 22:46:58 GMT" — Maintainer: MERGE-ACK #1421 (SL-1985; head 13a94a07ffe5e13a7e034303de4ae65ab5a8cd94, expected squash tree 32f7ffc213c30d0f61478fe13ea1f5a06a8e711f). CI by id on that head: python 41730072490, docs 41730072225, history-policy 41730072007, frontend 41730072243 (all success).

## Tasks

### Scope

PL-1984 Row 1, S-a (FD-1495): Acceptance 1 to 6. Requirements: FR-88, FR-240. Base: `origin/draft/pl-wk673fix` a2679afe (`main` a8ef6f19, no merge needed).

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

DB window (own start 18:32:04 UTC, load1 2.87, avail 25G; `createdb -T gipricing` copy `gipricing_sl8303_fd1495`, redis db 12, bucket `gip-test-blobs-8303`; env `GIP_TEST_DATABASE_URL`, `GIP_REDIS_URL`, `GIP_TEST_BUCKET`; `run-small.sh`, each file singly; base src restored after each red with `git diff --quiet HEAD` rc=0). First red run: the save-check test's UPDATE of a fitted Model was rejected by the 02 R2 trigger ("a fitted Model is immutable"), a fixture defect, fixed in 6df5b95a by reserving the model and never fitting it (fit_result NULL); expectation unchanged. The red is then 201 != 422 at base (the empty-default read saved the algorithm), green at head. `test_rating_gbm_banded_save.py` went red at head (2 failed: its rows carried `{"feature_order": ...}` with no `model_type`, and a GLM row with `feature_order`), fixed in c336efdb (own commit, assertions unchanged), 10 passed.
```text
== db-red.log
head=a2679afe src + tests cef08e9d db=gipricing_sl8303_fd1495
E   asyncpg.exceptions.InsufficientPrivilegeError: a fitted Model is immutable (02 R2): UPDATE rejected
E   HINT:  Refitting produces a new version with parent_model_id set. A Rating Version pins a model version; rewriting one changes what every quote priced on it was priced with.
E                   sqlalchemy.dialects.postgresql.asyncpg.AsyncAdapt_asyncpg_dbapi.ProgrammingError: <class 'asyncpg.exceptions.InsufficientPrivilegeError'>: a fitted Model is immutable (02 R2): UPDATE rejected
E                   HINT:  Refitting produces a new version with parent_model_id set. A Rating Version pins a model version; rewriting one changes what every quote priced on it was priced with.
E                   sqlalchemy.exc.ProgrammingError: (sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError) <class 'asyncpg.exceptions.InsufficientPrivilegeError'>: a fitted Model is immutable (02 R2): UPDATE rejected
E                   HINT:  Refitting produces a new version with parent_model_id set. A Rating Version pins a model version; rewriting one changes what every quote priced on it was priced with.
E                   [SQL: UPDATE models SET fit_result=$1::JSONB WHERE models.model_family_slug = $2::VARCHAR AND models.version = $3::INTEGER]
E                   [SQL parameters hidden due to hide_parameters=True]
E                   (Background on this error at: https://sqlalche.me/e/20/f405)
backend/tests/test_rating_algorithms.py::test_an_unknown_field_named_cycle_note_is_validation_failed
FAILED backend/tests/test_rating_algorithms.py::test_a_feature_map_over_a_model_whose_fit_result_lacks_the_fields_is_refused_at_save
1 failed, 33 passed, 10 warnings in 44.35s
rc=1
== db-red2.log
head=a2679afe src + tests 6df5b95a db=gipricing_sl8303_fd1495
E       AssertionError: {"id":"01a1a2b0-eb4c-72a6-bdb4-ca3fbf1eeb82","slug":"motor-gb","version":1}
E       assert 201 == 422
E        +  where 201 = <Response [201 Created]>.status_code
backend/tests/test_rating_algorithms.py::test_an_unknown_field_named_cycle_note_is_validation_failed
FAILED backend/tests/test_rating_algorithms.py::test_a_feature_map_over_a_model_whose_fit_result_lacks_the_fields_is_refused_at_save
1 failed, 33 passed, 10 warnings in 40.99s
rc=1
== db-green.log
head=6df5b95a5d03660313c9ba444adc8a92229928bb (fix) db=gipricing_sl8303_fd1495
backend/tests/test_rating_algorithms.py::test_an_unknown_field_named_cycle_note_is_validation_failed
34 passed, 10 warnings in 44.06s
rc=0
== db-gbm.log
head=6df5b95a5d03660313c9ba444adc8a92229928bb db=gipricing_sl8303_fd1495
E           app.errors.PlatformError: model:banded-gbm@1 cannot be mapped: the Factors it consumes cannot be derived (the fit result's model_type None has no derivation), so it cannot be shown not to price on a `control`-intent Factor (FR-88, FR-240).
E           app.errors.PlatformError: model:banded-gbm@1 cannot be mapped: the Factors it consumes cannot be derived (the fit result's model_type None has no derivation), so it cannot be shown not to price on a `control`-intent Factor (FR-88, FR-240).
FAILED backend/tests/test_rating_gbm_banded_save.py::test_a_gbm_on_identity_factors_saves
FAILED backend/tests/test_rating_gbm_banded_save.py::test_a_glm_on_a_banded_factor_saves
2 failed, 8 passed, 1 warning in 2.42s
rc=1
== db-gbm2.log
head=c336efdb4850baf5a788ab4c8d3253fd08aa8d41 db=gipricing_sl8303_fd1495
10 passed, 1 warning in 2.23s
rc=0
```
END zeros: redis db 12 dbsize=0; `select count(*) from pg_database where datname='gipricing_sl8303_fd1495'` = 0 (datnames: gipricing postgres template0 template1); bucket removed via `mc rb --force`, `mc ls g/` has no 8303.

**Gate evidence, verdict (2026-11-03, by stamp; written at the mint by the executor from the lead's entries, which are the record):** gate 1 on `1e77bd04`, window 18:39:53 to 20:33:59 UTC (to-lead entry "2026-11-03 20:36 GMT"): ruff 0, mypy 0, import-linter 0, req-coverage 0, generate-contracts 0, audit-docs 1 (check 31 only, the slice's own unminted ids, the item-31 class), pytest 1 ("13 failed, 7032 passed, 22 skipped, 5 xfailed, 146 warnings in 5010.66s (1:23:30)", the 13 all docs-audit tests, skipped 22 = baseline), frontend all 0 (vitest 137 files, 905 tests passed). Its demo stage was cap-stopped at 1500 s (rc 124) on this box's environment; the demo-only re-gate on the same head `1e77bd04` (window 21:21:42 to 21:47:32 UTC, cap 2400 s) PASSED: "designed stop at 2026-11-03T21:47:20+00:00 (both lines seen)", demo.py rc 0, 1529 s, dislocation #1 540 s. The three limbs together stand as the gate under common-brief item 31; the item-31 conditions (the mint, audit-docs rc 0, the docs-audit tests re-run via run-small at the minted head, CI including python) are in the PR.

**The gate predates main's `uv.lock` and `python.yml` changes (#1414, #1417).** The re-merge of `origin/main` (`55bddaf2`) moved two non-docs files that are main's own, `.github/workflows/python.yml` and `uv.lock`. Lead ruling (a), upheld by the maintainer: `git diff --name-only origin/main HEAD -- . ':!docs'` at `f322e1a6` lists only the slice's twelve files (`backend/src/app/platform/rating_algorithms.py`, `backend/tests/test_rating_algorithms.py`, `backend/tests/test_rating_gbm_banded_save.py`, `pricing_core/modelling/factors.py`, `pricing_core/rating/compile.py`, `pricing_core/rating/runtime.py`, and the six pricing-core test files), and `git diff 1e77bd04 HEAD` over those files was empty. The PR's own python CI on the merged head (the full suite) is the evidence for the combination.

Second re-merge, `origin/main` `4df71cd7` (#1420, docs batch 7; `docs/` only, its `INDEX.md` conflict taken from main and regenerated): the non-docs diff to `origin/main` is still the slice's twelve files and their diff to `1e77bd04` is the mint's comment re-points only (`SL 8303` to `SL-1985`, seven lines in seven files). `uv sync --directory <wt> --all-packages --frozen` on the merged head: rc 0 (it installed main's #1414 lock, `fastapi==0.162.0`). Batch 7's records FD-1982 and FD-1983 and the register row cited `PL 8302` as a working id; re-pointed to `PL-1984` in this PR (their `SL 8305` citations stay for S-b's mint).

**Comment-only working-id re-point, proof (lead approval, to-lead 2026-11-03 21:5x GMT; the DP-T27-6 form).** The mint re-pointed seven `SL 8303` tokens in seven `.py` files (`SL-1985`); three sit in docstrings and four in comments. `python3 -I` over `git show 1e77bd04:<path>` and `git show HEAD:<path>`, parsed, docstrings stripped, `ast.dump` compared: EQUAL for all seven (`backend/tests/test_rating_algorithms.py`, `pricing_core/modelling/factors.py`, `pricing_core/rating/compile.py`, and the four pricing-core tests `test_quote_input_raise_sites`, `test_rating_compile_bundle`, `test_rating_compile_fr240`, `test_rating_declared_reads`). `uv run --directory <wt> ruff check .` rc 0. `ruff format --check` on the seven files reports 6 would reformat at HEAD and the same 6 at `1e77bd04` (pre-existing, unchanged by the re-point). The whole `git diff -U0 1e77bd04 HEAD -- '*.py'`, `-`/`+` pairs identical apart from `SL 8303` to `SL-1985`:

```text
-    """FD-1495 (SL 8303): the save check derives a model's consumed Factors from the fields its
+    """FD-1495 (SL-1985): the save check derives a model's consumed Factors from the fields its
-    FD-1495 (SL 8303, ruled 2026-11-03 16:19:35 (2)): a GBM's required `feature_order`, a GLM's
+    FD-1495 (SL-1985, ruled 2026-11-03 16:19:35 (2)): a GBM's required `feature_order`, a GLM's
-    `fit_result` that yields no consumed feature is refused too (FD-1495, SL 8303). A
+    `fit_result` that yields no consumed feature is refused too (FD-1495, SL-1985). A
-    # FD-1495 (SL 8303): model ref and the fit-result field that could not be read: authored
+    # FD-1495 (SL-1985): model ref and the fit-result field that could not be read: authored
-        # FD-1495 (SL 8303): a pinned model carries the fields its consumed Factors are derived
+        # FD-1495 (SL-1985): a pinned model carries the fields its consumed Factors are derived
-# -- FD-1495's GLM arm: the consumed Factors come from the fields each arm carries (SL 8303) --
+# -- FD-1495's GLM arm: the consumed Factors come from the fields each arm carries (SL-1985) --
-            # FD-1495 (SL 8303): a pinned model carries the fields its consumed Factors are
+            # FD-1495 (SL-1985): a pinned model carries the fields its consumed Factors are
```

### Audit

~~(the auditor's)~~

*(Dated line 2026-11-04, docs batch 8, by the auditor.)* The slice audit is CR 8310 §1b (SL-1985 and SL-1997, per-requirement evidence), by route (a) of to-lead "2026-11-04 09:57:14 GMT", adopted for these two slices in "2026-11-04 10:00:29 GMT" (closing acts 1–4). The gap is accepted by that dated line; this record stands in the slice audit's place for the two-way ledger check, the build log and the gate of record above being the executor's record.

### Build log

- 2026-11-03: fixture commits, each preserving every assertion: `412567d8` `test_rating_compile_bundle._resolver()` (model gets `feature_order` [driver_age, rating_area], exactly what its model_call maps); `5b1924b9` `_compile_with_decimal_bound`; `2eb8657f` `_planted_in_a_sub_graph` (feature_order [ncd_years]); `1a5be739` `test_rating_compile_completeness._glm_world` (GLM terms for its two Factors); `e055787c` `test_rating_column_collision._pin` (was `{feature_order: []}` with Factors; now GLM terms = the Factor slugs); `b0d00170` `test_rating_declared_reads._StubResolver` (stub model consumes what the example maps).
- `50734f9b` `test_quote_input_raise_sites.py`: the registry follows the moved raise sites (not a fixture; flagged to the lead).
- Fixture defect in my own reds (`c9142a2b`): case (d) used a feature_map that did not cover the model, so it raised MODEL_CALL_FEATURE_MAP_INVALID; expectation unchanged.
- 2026-11-03, the new raise site `_consumed_features` (`compile.py`, registry entry in `test_quote_input_raise_sites.py`), quoted from the source: `CONTROL_FACTOR_IN_RATEABLE_PATH: {model_ref}: the Factors it consumes cannot be derived ({error}), so it cannot be shown not to price on a `control`-intent Factor (FR-88, FR-240)`. `model_ref` is the pin's authored ref; `{error}` is one of the fixed texts of `consumed_features` ("the fit result is not a mapping", "the GBM fit result carries no `feature_order` list of names", "the GLM fit result carries no `coefficients` list", "a GLM coefficient carries no `term` name", "the fit result consumes no feature") or "the fit result's model_type {model_type!r} has no derivation", where `model_type` is the stored fit result's discriminator, an authored model field. No quote value reaches the message.

## PRs

~~(none yet)~~

#1421, squash commit dfbce89be6370f69c12eb4bd4f6fb5414c28d21f (tree 32f7ffc213c30d0f61478fe13ea1f5a06a8e711f), merged 2026-11-03T22:47:47Z; on main. Filled 2026-11-04 in docs batch 8.

(Closed 2026-11-04 by the auditor in docs batch 8, on to-lead "2026-11-04 09:57:14 GMT" and "2026-11-04 10:00:29 GMT" (the six-slice closing acts): SL-1985 merged as #1421, squash commit dfbce89be6370f69c12eb4bd4f6fb5414c28d21f on main, tree 32f7ffc213c30d0f61478fe13ea1f5a06a8e711f.)
