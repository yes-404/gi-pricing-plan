---
id: LG-8329
family: ledger
title: WK-1178 slice SL-8328 — FactorCreate.slug takes the Factor grammar at the write boundary (PL-8327, FD-1384)
status: active
created: 2026-11-05
owner: executor
tree: a3046f64bdbe6a2a4f19c574d5589a3dcc043fa8
phase: P2
work: WK-1178
slice: SL-8328
plans: [PL-8327]
corrected_by: []
relates: [FD-1384, RL-1383, SL-1806, PL-8327]
---

# LG-8329 — WK-1178 slice SL-8328: `FactorCreate.slug` takes the Factor grammar

**GO:** the order in to-lead "2026-11-05 09:58:58 GMT" (the slice plan) and "2026-11-05 10:31:31 GMT" (plans C and H accepted); brief `brief-exec-slices-ch-2026-11-05.md`, row exec-sl8328c.
**MERGE-ACK:** (added at merge)

## Tasks

### Scope

PL-8327, "SL 8328 — `FactorCreate.slug`": `POST /api/v1/factors` refuses a slug outside the
Factor pattern (`00` §4.3, RL-1383) with 422 `VALIDATION_FAILED` naming `slug`. Reads unchanged
(FR-209). Requirements: `02` FR-83; FR-209 (read). Register: FD-1384.

### Task list

1. **R0, spec first** — commit `fb5f7acc`: the `02` `POST /api/v1/factors` row gains the dated sentence.
   All cites re-read at base `c064a75d`: `api/models.py` `FactorCreate.slug: str` held; `refs.py`
   `_FACTOR_SLUG` and `Slug` held; Banding/Grouping `Slug` and `RatingVersionCreate.slug: Slug` held.
   Helper-argument sweep: the three files that POST `/factors` (`test_api_models.py`,
   `test_api_transformations.py`, `test_expression_factors_api.py`) use only slugs of the form
   `driver-age-<hex>` / `expr-<hex>`; the grep for slug literals outside the grammar printed nothing.
   No fixture changed.
2. **R1, red first, by cause** — commit `99120993`: `FactorSlug = str` (plain alias) plus T2
   (`test_a_factor_create_refuses_a_slug_outside_the_factor_grammar`, 7 params) and T3
   (`test_a_stored_factor_slug_is_not_revalidated_on_read`) in `packages/model-schema/tests/test_refs.py`
   (the only model-schema test file that exercises `refs`; `git grep -n Slug` finds no `Slug` unit test).
3. **R2, green** — commit `64525585`: `FactorSlug = Annotated[str, Field(pattern=rf"^{_FACTOR_SLUG}$")]`
   in `refs.py` (+ `__all__`), `FactorCreate.slug: FactorSlug`, T1
   (`test_a_factor_slug_outside_the_grammar_is_a_422_naming_the_field`, 5 params + a `veh_brand`
   positive control) in `backend/tests/test_api_models.py`, contract regenerated.

### Gate

Not run: the SOLO full gate is the lead's (brief). Run so far, DB-free, on branch `sl-8328-c-factor-slug`:

| Check | Result |
|---|---|
| `run-small.sh … packages/model-schema/tests/test_refs.py` at the red (`fb5f7acc` + uncommitted alias/tests) | `5 failed, 12 passed` — `Failed: DID NOT RAISE ValidationError`, params `[]`, `[Veh Brand]`, `[a:b@1]`, `[a×65]`, `[a]` |
| same file, green | `17 passed` rc 0 |
| `run-heavy.sh -- uv run ruff check .` | `All checks passed!` rc 0 |
| `generate-contracts.py --check` | `58 generated contracts match the models` rc 0 |
| A5 `git grep -n '\[a-z0-9\]\[a-z0-9_-\]' -- packages backend/src` | `refs.py:50` (the plan said `:42`) **and** `packages/pricing-core/src/pricing_core/rate_tables/operations.py:228` (an existing error-message string quoting the pattern, not a second grammar; outside the Write set; already at base) |
| A7 `generated.json` diff | one line: `"pattern": "^[a-z0-9][a-z0-9_-]{1,62}$"` |
| A6 `git diff origin/main...HEAD -- packages/model-schema/src/model_schema/modelling.py` | empty |

T1 is route-level and DB-backed; per the plan its green is the gate's (T1 was not run here).
`FactorSlug` is imported in `api/models.py` from `model_schema.refs`, not from the package root,
because `model_schema/__init__.py` is outside the Write set (it re-exports `Slug`).

GREEN set by import closure (common seat brief item 29), corrected 2026-11-05 16:38:04 GMT (audit A8; the earlier
"36 files" text grep of module names had no second importer level and missed `from model_schema import …`
importers, so it is withdrawn). Head `4abb37986ae3d79e2c5b738c8dc743b62f674fed`.

Predicate (verbatim, an AST scan, run as `python3 -I closure.py <wt>` over `backend/` and `packages/` `*.py`):
changed modules `T0 = {model_schema.refs, app.api.models}` (`git diff --name-only origin/main...HEAD -- <src>`:
`refs.py`, `api/models.py`); level 1 = every `.py` with `import X` / `from X import …` / `from X import N` where
`X` is in T0, or `X == model_schema` and `N` in the names `model_schema/__init__.py` re-exports from `refs`
(`ARTIFACT_TYPES, ArtifactRef, BlobRef, ModelRef, Slug`); level 2 = every `.py` importing a level-1 source module;
GREEN = the `test_*.py` files in level 1 ∪ level 2. `spec_from_file_location` loaders: `git grep -l
spec_from_file_location -- backend packages` names only backend tests (none loading a changed module by path;
each is already in the set where it imports one). Result: 294 test files (168 backend/tests, 48
packages/model-schema, 77 packages/pricing-core), of which 145 classed DB-free
and 148 DB-backed by a second AST pass (a fixture argument from `conftest_db.py`: `blob_store, database, grant,
membership, owner_database`, or a text hit on `conftest_db|GIP_(TEST_)?DATABASE|createdb|psycopg|asyncpg|redis|docker`).

**Run at this head (stopped by the lead's order, 2026-11-05 16:38:04 GMT):** 2 files of the 145, one pytest process each through
`run-heavy.sh --over-load "2026-11-05 15:37:39 GMT"`:
- `backend/tests/test_api_auth.py` — `1 passed, 2 warnings, 2 errors` rc=1: the 2 ERRORs are setup errors on a DB
  fixture (the classifier called the file DB-free wrongly), not an assertion against the slice. It is DB-backed → OWED-TO-GATE.
- `backend/tests/test_approval_guard.py` — `11 passed, 2 warnings` (the run was killed after the summary; no rc line).

**OWED-TO-GATE:** the other 143 DB-free files and all 148 DB-backed files. C's full suite is the decisive
green and covers them; none was run here beyond the two above.

DB-free list (145):
```
backend/tests/test_api_auth.py
backend/tests/test_approval_guard.py
backend/tests/test_bench_rating_calls.py
backend/tests/test_change_summary_draft.py
backend/tests/test_change_summary_purposes.py
backend/tests/test_error_sinks.py
backend/tests/test_errors.py
backend/tests/test_fremtpl2_algorithm.py
backend/tests/test_job_memory_budget.py
backend/tests/test_management_429_declared.py
backend/tests/test_model_specs_expression_estimate.py
backend/tests/test_objective_preview.py
backend/tests/test_rating_gbm_banded_save.py
backend/tests/test_revalidation_sweep.py
backend/tests/test_route_scope_guard.py
backend/tests/test_severity_population_golden.py
backend/tests/test_shadow_log_sanitised.py
backend/tests/test_spec_hash.py
backend/tests/test_startup_gc_freeze.py
backend/tests/test_startup_self_check.py
packages/model-schema/tests/test_approvals.py
packages/model-schema/tests/test_auth.py
packages/model-schema/tests/test_backtests.py
packages/model-schema/tests/test_banding_warnings.py
packages/model-schema/tests/test_comparison.py
packages/model-schema/tests/test_cross_validation_diagnostics.py
packages/model-schema/tests/test_dataset_derived_fields.py
packages/model-schema/tests/test_dataset_lineage.py
packages/model-schema/tests/test_dataset_version.py
packages/model-schema/tests/test_decimal_schema_pattern.py
packages/model-schema/tests/test_deployments.py
packages/model-schema/tests/test_dislocation.py
packages/model-schema/tests/test_dropped_eval_metrics.py
packages/model-schema/tests/test_ebm_prediction.py
packages/model-schema/tests/test_ebm_spec.py
packages/model-schema/tests/test_factor.py
packages/model-schema/tests/test_factor_expression.py
packages/model-schema/tests/test_gbm_spec.py
packages/model-schema/tests/test_glm_approximation.py
packages/model-schema/tests/test_glm_cv_spec.py
packages/model-schema/tests/test_glm_spec_theta.py
packages/model-schema/tests/test_graph_errors.py
packages/model-schema/tests/test_graph_invariant_issues.py
packages/model-schema/tests/test_input_free.py
packages/model-schema/tests/test_metrics.py
packages/model-schema/tests/test_model_lifecycle.py
packages/model-schema/tests/test_objectives.py
packages/model-schema/tests/test_offending_sample.py
packages/model-schema/tests/test_offset_model_spec.py
packages/model-schema/tests/test_partition_zero_weight_count.py
packages/model-schema/tests/test_perils.py
packages/model-schema/tests/test_permutation_importance.py
packages/model-schema/tests/test_profiles.py
packages/model-schema/tests/test_rate_tables.py
packages/model-schema/tests/test_rating.py
packages/model-schema/tests/test_rating_algorithm.py
packages/model-schema/tests/test_rating_algorithm_draft.py
packages/model-schema/tests/test_rating_ordered_input.py
packages/model-schema/tests/test_rating_version.py
packages/model-schema/tests/test_refs.py
packages/model-schema/tests/test_regression.py
packages/model-schema/tests/test_scoring_compare.py
packages/model-schema/tests/test_scoring_ladder.py
packages/model-schema/tests/test_scoring_outputs.py
packages/model-schema/tests/test_sub_graph.py
packages/model-schema/tests/test_tweedie_power_spec.py
packages/model-schema/tests/test_uncertainty_basis.py
packages/model-schema/tests/test_validation_catalogue.py
packages/pricing-core/tests/test_backtests.py
packages/pricing-core/tests/test_bandings.py
packages/pricing-core/tests/test_builtin_rule_checks.py
packages/pricing-core/tests/test_catalogue.py
packages/pricing-core/tests/test_comparison.py
packages/pricing-core/tests/test_demo_b4_premium.py
packages/pricing-core/tests/test_diagnostics.py
packages/pricing-core/tests/test_ebm.py
packages/pricing-core/tests/test_expression_factors.py
packages/pricing-core/tests/test_expression_objective.py
packages/pricing-core/tests/test_expression_profiles.py
packages/pricing-core/tests/test_factor_resolution.py
packages/pricing-core/tests/test_fremtpl2_rate_fixture.py
packages/pricing-core/tests/test_gbm.py
packages/pricing-core/tests/test_glm.py
packages/pricing-core/tests/test_glm_cv.py
packages/pricing-core/tests/test_glm_model_offset.py
packages/pricing-core/tests/test_glm_scalar_predict.py
packages/pricing-core/tests/test_groupings.py
packages/pricing-core/tests/test_interactions.py
packages/pricing-core/tests/test_metrics.py
packages/pricing-core/tests/test_model_round_trip.py
packages/pricing-core/tests/test_objectives.py
packages/pricing-core/tests/test_perils.py
packages/pricing-core/tests/test_prediction_interval.py
packages/pricing-core/tests/test_profile.py
packages/pricing-core/tests/test_quote_input_raise_sites.py
packages/pricing-core/tests/test_rate_table_bulk_ops.py
packages/pricing-core/tests/test_rate_table_operations.py
packages/pricing-core/tests/test_rate_table_weights.py
packages/pricing-core/tests/test_rating_attribution.py
packages/pricing-core/tests/test_rating_authored_fields.py
packages/pricing-core/tests/test_rating_column_collision.py
packages/pricing-core/tests/test_rating_committed_strings.py
packages/pricing-core/tests/test_rating_compile.py
packages/pricing-core/tests/test_rating_compile_bundle.py
packages/pricing-core/tests/test_rating_compile_completeness.py
packages/pricing-core/tests/test_rating_compile_fr240.py
packages/pricing-core/tests/test_rating_decimal_money_rounds_once.py
packages/pricing-core/tests/test_rating_decimal_outputs.py
packages/pricing-core/tests/test_rating_declared_reads.py
packages/pricing-core/tests/test_rating_dislocation.py
packages/pricing-core/tests/test_rating_gbm_banded_refusal.py
packages/pricing-core/tests/test_rating_glm_expression_inputs.py
packages/pricing-core/tests/test_rating_glm_model_call.py
packages/pricing-core/tests/test_rating_inline.py
packages/pricing-core/tests/test_rating_ladder_control.py
packages/pricing-core/tests/test_rating_ladder_exact.py
packages/pricing-core/tests/test_rating_ladder_refusal.py
packages/pricing-core/tests/test_rating_ladder_sweep.py
packages/pricing-core/tests/test_rating_lookup_as_at.py
packages/pricing-core/tests/test_rating_model_call_dropped_inputs.py
packages/pricing-core/tests/test_rating_mounted_model_call.py
packages/pricing-core/tests/test_rating_number.py
packages/pricing-core/tests/test_rating_ordered_input.py
packages/pricing-core/tests/test_rating_peril_scoring.py
packages/pricing-core/tests/test_rating_pin_membership.py
packages/pricing-core/tests/test_rating_purpose_mount.py
packages/pricing-core/tests/test_rating_purpose_mount_model_call_checks.py
packages/pricing-core/tests/test_rating_runtime.py
packages/pricing-core/tests/test_rating_score.py
packages/pricing-core/tests/test_rating_score_batch.py
packages/pricing-core/tests/test_rating_score_batch_outputs.py
packages/pricing-core/tests/test_rating_score_decimal_input.py
packages/pricing-core/tests/test_rating_shadowed_inputs.py
packages/pricing-core/tests/test_rating_wire_order.py
packages/pricing-core/tests/test_replay.py
packages/pricing-core/tests/test_safe_error.py
packages/pricing-core/tests/test_scoring_without_the_fitting_stack.py
packages/pricing-core/tests/test_severity_population.py
packages/pricing-core/tests/test_sql_check.py
packages/pricing-core/tests/test_testing.py
packages/pricing-core/tests/test_testing_determinism.py
packages/pricing-core/tests/test_trace_diff.py
packages/pricing-core/tests/test_transparency.py
packages/pricing-core/tests/test_tweedie_power.py
packages/pricing-core/tests/test_validate.py
```
DB-backed list (148):
```
backend/tests/test_api_approvals.py
backend/tests/test_api_audit.py
backend/tests/test_api_authorisation_sweep.py
backend/tests/test_api_backtests.py
backend/tests/test_api_blob_uploads.py
backend/tests/test_api_blobs.py
backend/tests/test_api_dataset_ingest_owner.py
backend/tests/test_api_datasets.py
backend/tests/test_api_diagnostics.py
backend/tests/test_api_jobs.py
backend/tests/test_api_me.py
backend/tests/test_api_model_lifecycle.py
backend/tests/test_api_models.py
backend/tests/test_api_rate_tables.py
backend/tests/test_api_reference.py
backend/tests/test_api_service_accounts.py
backend/tests/test_api_settings.py
backend/tests/test_api_transformations.py
backend/tests/test_api_validation_rules.py
backend/tests/test_application_role.py
backend/tests/test_approval_guard_allowance.py
backend/tests/test_approval_guard_decision.py
backend/tests/test_approval_guard_trigger.py
backend/tests/test_approval_request_shape.py
backend/tests/test_approvals.py
backend/tests/test_artifact_immutability.py
backend/tests/test_artifact_usage_counts.py
backend/tests/test_audit.py
backend/tests/test_auth_failure_audit.py
backend/tests/test_auth_failure_identity.py
backend/tests/test_auth_keys.py
backend/tests/test_auth_users.py
backend/tests/test_backtests.py
backend/tests/test_blobs.py
backend/tests/test_bundle_slot.py
backend/tests/test_celery_broker.py
backend/tests/test_check_rule_sets_runnable.py
backend/tests/test_contracts.py
backend/tests/test_custom_metrics.py
backend/tests/test_custom_metrics_api.py
backend/tests/test_custom_objectives.py
backend/tests/test_custom_objectives_api.py
backend/tests/test_custom_objectives_expression.py
backend/tests/test_data_jobs.py
backend/tests/test_data_nfrs.py
backend/tests/test_dataset_scoped_writes.py
backend/tests/test_datasets.py
backend/tests/test_demo_command.py
backend/tests/test_demo_guide.py
backend/tests/test_demo_peril_structure.py
backend/tests/test_demo_rating_evidence.py
backend/tests/test_deploy_stack_runtime.py
backend/tests/test_deploy_switch_runtime.py
backend/tests/test_deployment_route_types.py
backend/tests/test_deployment_switch_http.py
backend/tests/test_deployments.py
backend/tests/test_diagnostics.py
backend/tests/test_diff_cache.py
backend/tests/test_dislocation_runs.py
backend/tests/test_ebm_model_jobs.py
backend/tests/test_environments.py
backend/tests/test_expression_factors_api.py
backend/tests/test_expression_objective_fit.py
backend/tests/test_fr240_governance.py
backend/tests/test_glm_approximation_model.py
backend/tests/test_ingest_coercion.py
backend/tests/test_ingestion.py
backend/tests/test_interaction_factors.py
backend/tests/test_job_error_sanitiser.py
backend/tests/test_job_platform_build.py
backend/tests/test_jobs.py
backend/tests/test_lineage.py
backend/tests/test_management_rate_limit.py
backend/tests/test_metrics.py
backend/tests/test_migration_dataset_owner.py
backend/tests/test_migration_dataset_version_envelope.py
backend/tests/test_migration_deployments.py
backend/tests/test_migration_sub_graphs.py
backend/tests/test_model_comparison.py
backend/tests/test_model_jobs.py
backend/tests/test_model_jobs_gbm.py
backend/tests/test_model_lifecycle.py
backend/tests/test_model_nfrs.py
backend/tests/test_model_offset_jobs.py
backend/tests/test_model_specs.py
backend/tests/test_nfr498_audit_events.py
backend/tests/test_objective_preview_api.py
backend/tests/test_objective_submission.py
backend/tests/test_outbox.py
backend/tests/test_paired_quantile_models.py
backend/tests/test_peril_structure_approval.py
backend/tests/test_peril_structures.py
backend/tests/test_peril_structures_api.py
backend/tests/test_prediction.py
backend/tests/test_profile_refusal.py
backend/tests/test_rate_table_diff_portfolio.py
backend/tests/test_rate_tables_service.py
backend/tests/test_rating_algorithm_validate.py
backend/tests/test_rating_algorithms.py
backend/tests/test_rating_glm_model_call.py
backend/tests/test_rating_mode_mismatch_api.py
backend/tests/test_rating_peril_scoring_api.py
backend/tests/test_rating_pin_membership_api.py
backend/tests/test_rating_version_change_summary_route.py
backend/tests/test_rating_version_compile.py
backend/tests/test_rating_version_create_pins.py
backend/tests/test_rating_version_dislocation_gate.py
backend/tests/test_rating_version_evidence_floor.py
backend/tests/test_rating_versions.py
backend/tests/test_rbac.py
backend/tests/test_reference_pin.py
backend/tests/test_regression_runs.py
backend/tests/test_regression_suites.py
backend/tests/test_request_connections.py
backend/tests/test_reset_unbacked_rule_approvals.py
backend/tests/test_routing.py
backend/tests/test_routing_write.py
backend/tests/test_score.py
backend/tests/test_score_as_at.py
backend/tests/test_score_batch_api.py
backend/tests/test_score_compare.py
backend/tests/test_score_purpose_mount.py
backend/tests/test_score_rate_limit.py
backend/tests/test_score_request_cost.py
backend/tests/test_scoring_handlers.py
backend/tests/test_settings.py
backend/tests/test_settings_environment.py
backend/tests/test_shadow_scoring.py
backend/tests/test_shadow_write.py
backend/tests/test_sub_graphs_api.py
backend/tests/test_sub_graphs_service.py
backend/tests/test_tenant_binding.py
backend/tests/test_traces.py
backend/tests/test_traces_api.py
backend/tests/test_transformations.py
backend/tests/test_validation_reports.py
backend/tests/test_validation_rule_approval.py
backend/tests/test_wf01_journey.py
backend/tests/test_wf699_journey.py
backend/tests/test_wf701_journey.py
backend/tests/test_wf702_route_b.py
backend/tests/test_worker.py
backend/tests/test_worker_rate_tables.py
backend/tests/test_workspace_identity.py
backend/tests/test_workspace_members.py
backend/tests/test_workspace_selection.py
backend/tests/test_workspace_switch.py
backend/tests/test_workspaces.py
```

**Correction 2026-11-05 16:38:04 GMT (audit A5):** the predicate prints two lines, `refs.py:50` (the plan said `:42`) and
`operations.py:228` (an error string already at base); the table row above is read with that.

**Front matter `tree:`** is stale (`a3046f64` is the tree of `64525585`, not of the head); it is written at the mint, not chased here.

### Audit

(the auditor's)

### Build log

- 2026-11-05 R0 `fb5f7acc`; R1 `99120993`; R2 `64525585`. Ledger drafted before audit.

## PRs

(none yet — the seat ends unpushed)
