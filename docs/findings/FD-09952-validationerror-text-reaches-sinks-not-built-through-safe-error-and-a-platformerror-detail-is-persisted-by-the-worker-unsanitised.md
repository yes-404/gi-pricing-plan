---
id: FD-9952
family: finding
title: A ValidationError's text reaches sinks not built through pricing_core.safe_error, and the worker persists a PlatformError's detail as given, so the compile Job stores a stored model's field values in its error
status: draft
created: 2026-10-10
owner: auditor
tree: 42e5d67f0e36264d7f7db0aa2d14476ddb4fb72c
corrected_by: []
relates: [WK-1178, FD-1578, NFR-499, RL-917, FR-119]
---

# FD-9952 — ValidationError sinks outside `pricing_core.safe_error`

**DRAFT**, filed on `draft/fd-9952-ve-sinks`, no PR, at the maintainer's ruling (`to-lead.md`,
"2026-10-10 09:33:03 BST — Premise correction ACCEPTED (my 09:15:25 premise was wrong). Ruling
(B) for A-2: no code change; the leak question becomes a scoped AUDIT, not an A-2 edit"):
*"An AUDITOR task (not A-2): list every sink on main (API problem responses, Job error fields,
log calls) that could receive a ValidationError and is NOT built through pricing_core.safe_error.
Each such sink is one row in a single FD (owner WK-1178, the NFR-499 class beside FD-1578), with
a proposed severity."* Every line number is at `origin/main` `42e5d67f0e36264d7f7db0aa2d14476ddb4fb72c`
(tree `75e21afb`). The entry cites `rating_versions.py:514` for the `to_model` call; at this tree
it is `:560` (A-2's merge moved it).

## The rule the rows are measured against

`packages/pricing-core/src/pricing_core/safe_error.py:3-9`: *"a Pydantic `ValidationError`
prints every failing `input_value` … an exception's text is kept only where it is ours and known
to be input-free"*. `_validation_detail` (`:104-116`, called at `:121-122`) rebuilds a
`ValidationError` from `errors(include_input=False)`. A sink is in scope here when an exception
whose text carries input can reach it and its text is not built through `safe_error_detail`,
`safe_error_text`, `safe_exc_info`, or the backend's `safe_job_error_text` / `safe_job_exc_info`
(`backend/src/app/platform/safe_exception.py:31-54`).

**`pydantic_core.ValidationError` is a `ValueError`.** So every `except ValueError` (and
`except Exception`) whose guarded body builds a Pydantic model admits one. That is how most of
the rows below are reached: none of them names `ValidationError`, except rows 2, 4 and 9.

## The structural cause behind row 1

`backend/src/app/worker/tasks.py:233-258`, the generic clause, sanitises (`safe_job_error_text`,
`:255`). The `PlatformError` clause before it (`:197-231`) logs safely (`safe_job_exc_info`) but
**persists `message=exc.detail or exc.title` (`:227`) as given**. So any `PlatformError` raised
inside a worker handler whose `detail` was built from `str(exc)` is written to the Job row
unsanitised and served by `GET /api/v1/jobs/{id}` (`backend/src/app/api/jobs.py:159-164`). The
allow-list of RL-917 holds for the generic clause and is bypassed by the coded one.

## Predicates (run at the tree above, read-only)

- P1 `git grep -n 'to_model(' 42e5d67f -- backend packages` → 42 hits (18 outside `tests/`;
  the `environments.py` and `sub_graphs.py` hits are local `_to_model` helpers, not
  `app.platform.modelling.to_model`).
- P2 `git grep -nE 'logger\.exception|log\.exception|str\(exc\)|repr\(exc\)|\{exc\}|\{exc!r\}|exc\.errors\(\)|exc_info=True|str\(e\)|\{e\}|\{err\}|str\(err\)' 42e5d67f -- backend/src packages | grep -c '/src/'`
  → 52; of them 0 for `logger.exception|exc_info=True`.
- P3 `git grep -nE '(logger|log|_log|LOG|logging)\.(exception|error|warning|warn|info|debug|critical)\(' 42e5d67f -- backend/src 'packages/**/src/**' | wc -l`
  → 30 (one is a comment, `config.py:133`).
- P4 `git grep -nE 'safe_error|safe_exc|safe_exception' 42e5d67f -- backend/src packages/pricing-core/src`
  → the sinks already built through the module.

Every hit was mapped to its enclosing `except` clause and the owning function read; a grep hit
was a candidate, not a row.

## Sinks

| # | Sink (file:line at `42e5d67f`) | Kind | How a ValidationError (or input-bearing text) reaches it | Expression | Proposed severity |
|---|---|---|---|---|---|
| 1 | `backend/src/app/platform/rating_versions.py:704-711`, persisted at `worker/tasks.py:227` | Job error field (DB) + `GET /jobs/{id}` | `rating.compile` Job (`worker/rating_handlers.py:61`) → `compile_rating_version` → `compile_bundle` → `WorkspaceResolver.resolve` → `to_model(model)` (`:560`) raises `ValidationError` (FR-119's `_the_fit_matches_the_specification`, `model_schema/modelling.py:2109`; or any other `Model` validator); also `RatingAlgorithm.model_validate` (`rating/compile.py:718`) and `ArtifactRef.model_validate` (`:633`, `:657`). Caught by `except ValueError` at `:704`. | `text = str(exc)`; not upper-case-coded, so `code, detail = "BUNDLE_COMPILE_FAILED", text` (`:705-708`) → `PlatformError(…, 422, detail)` → `JobError(message=exc.detail …)` | **MEDIUM.** Persisted, and served over the API, with the stored model row's field values (`input_value` of the fit / spec dicts); the exact path the 09:32:35 entry's red run raised. Not HIGH: the values are a model artifact's, not a quote input, and readable by the same workspace. |
| 2 | `backend/src/app/platform/rate_tables.py:1300-1305` (`bulk_operation`) | API problem (422) | `except ValidationError` around `_dispatch_operation(kind, parameters, baseline)` | `PlatformError("VALIDATION_FAILED", …, 422, str(exc))` | LOW. The caller's own request parameters, returned to that caller; `_handle_platform_error` (`errors.py:478-479`) renders without logging; HTTP route only (`api/rate_tables.py:152`). |
| 3 | `backend/src/app/platform/rate_tables.py:118` (`_map_operation_error`) | API problem (422) | `except ValueError` at `:156`, `:171`, `:885`, `:915`; the guarded bodies build `ImportVerdict(filename=…)` (`rate_tables/operations.py:887`), `ImportResult` (`:893`) and `RateTableDiffCell` (`:424`). Reach **not demonstrated**: the values are checked before construction. | `PlatformError("VALIDATION_FAILED", …, 422, str(exc))`; `:111` also partitions `str(exc)` | LOW. HTTP only (`api/rate_tables.py:105`, `:249`, `:260`); an upload's own name or cells back to its sender. |
| 4 | `backend/src/app/platform/rating_algorithms.py:60-65` (`graph_validation_error`) | API problem (422) | `except ValidationError` at `rating_algorithms.py:73`, `sub_graphs.py:111`, `:134`; its own docstring (`:36-37`) says the message text "echoes the input" | `PlatformError("VALIDATION_FAILED", …, 422, str(exc))` | LOW. The submitted algorithm / sub-graph content to its submitter; HTTP only. |
| 5 | `backend/src/app/platform/metrics.py:736-742` (`_validated`) | API problem (422) | `except ValueError` around `CustomMetric.model_validate(payload)` | `f"{exc}"` | LOW. Request body to its sender (`api/custom_metrics.py:255`). |
| 6 | `backend/src/app/platform/objectives.py:989-995` (`_validated`) | API problem (422) | `except ValueError` around `CustomObjective.model_validate(payload)` | `f"{exc}"` | LOW. Request body to its sender (`api/custom_objectives.py:274`). |
| 7 | `backend/src/app/platform/rating_versions.py:307-317` (`create_rating_version`) | API problem (422) | `except ValueError` around `to_schema(row)` and `RatingAlgorithm.model_validate(algorithm_row.content)` (`:309`) — a **stored** algorithm that no longer validates | `PlatformError("MODEL_REFERENCE_MODE_INCONSISTENT", …, 422, str(exc))` | LOW. Stored artifact content to a caller of the same workspace; it also labels a shape failure with the mode code, a misclassification. |
| 8 | `backend/src/app/errors.py:490-499` (`_handle_validation_error`) | API problem (422) | FastAPI's `RequestValidationError` | `FieldError(message=str(err["msg"]))`; `input` is never read, but a `value_error` `msg` carries whatever a custom validator interpolated | LOW. Response to the sender only; no `input_value`. Not swept: which request-model validators interpolate their value. |
| 9 | `backend/src/app/config.py:279-286` (`load_settings`) | Startup failure → process log | `except ValidationError` → `ConfigInvalidError(…) from exc`; the chained `ValidationError` keeps its `input_value` text, rendered by any traceback formatter (`observability/logging.py:61`) | `raise ConfigInvalidError(…) from exc` | LOW. Operator environment values (a DSN may carry a credential) into the operator's own logs; R3, not NFR-499. |
| 10 | `backend/src/app/platform/prediction.py:144-153` (`predict_rows`) | API problem (422) | Not a `ValidationError`: `pl.DataFrame(rows)` refusing a ragged / mixed body; the comment (`:145-147`) relies on polars naming the column, and polars may also quote a value (not verified here) | `f"{exc} Every row must carry …"` | LOW. Scoring rows to their sender; HTTP only (`api/models.py:1095`). |
| 11 | `packages/pricing-core/src/pricing_core/data/validate.py:2213-2214` and `:2104-2105` (`_run_one`, the SQL check) | Persisted validation report (`RuleResult.detail`) | `except Exception` around each of the catalogue's checks, and `except duckdb.Error` around a SQL rule; a check's library error (polars, DuckDB) may quote a dataset value (not verified here); a `ValidationError` reach is not demonstrated | `failed(type(exc).__name__, f"{type(exc).__name__}: {exc}")`; `SqlCheckError(f"{type(exc).__name__}: {exc}")` | LOW. Persisted, but the readers of a Dataset Version's report already hold its data. |

## Already built through `safe_error`, or not a sink for input text (excluded)

- **HTTP unexpected exceptions:** `observability/middleware.py:47-64` logs with
  `safe_job_exc_info(exc)` and returns `unexpected_problem()` (`errors.py:570-590`, fixed
  `detail`); the backstop `errors.py:593-595` is the same. So the five `api/models.py` `to_model`
  calls (`:545`, `:619`, `:651`, `:765`, `:801`) and `rate_tables.py:154` (outside its `try`,
  which begins at `:155`) end in a fixed 500.
- **Worker generic clause:** `worker/tasks.py:233-258` (`safe_job_error_text`, `safe_job_exc_info`);
  so a `ValidationError` from `to_model` in the dislocation paths (`worker/dislocation_handlers.py:196-199`,
  `:292-295`; `platform/dislocation_runs.py:291-298` catches only `AttributionError`) is safe.
- **Already `safe_error`:** `api/dislocation_runs.py:194`, `platform/dislocation_runs.py:297`,
  `worker/dislocation_handlers.py:321`, `rating/analysis.py:1021`, `rating/score.py:1063`,
  `platform/outbox.py:123`, `api/score.py:526-531`; `api/score.py:309-322` accepts a `CodedError`
  only, so `:397`'s `problem.detail` is coded text.
- **Type name only:** `api/health.py:91`, `db/session.py:95`, `platform/blobs.py:484`,
  `platform/diff_cache.py:151`, `:164`, `auth/oidc.py:104`, `:126`.
- **Own classes with input-free text, or our own blob:** `api/demo.py:77`, `data/ingestion.py:158`,
  `:177`, `:433`, `platform/modelling.py:1042`, `objectives.py:309`, `:360-362`,
  `regression_suites.py:127`, `transformations.py:507`, `worker/data_handlers.py:413`,
  `worker/model_handlers.py:405-414`, `:778`, `:1482`, `:1498`, `worker/rating_handlers.py:185`,
  `prediction.py:551`, `rate_tables/weights.py:119`, `worker/tasks.py:190`
  (`JobBudgetExceededError`, `worker/progress.py:63-65`: budget and elapsed seconds),
  `settings.py:76` (the `TypeError`s at `:60-72` name a type), `modelling/glm.py:174` (our own
  covariance blob).
- **Library text enumerated input-free:** `modelling/glm.py:689`, whose comment (`:669-678`)
  lists glum 3.4.1's refusals, none quoting a value.
- **Artifact text, not input:** `rating/compile.py:326` (an authored expression),
  `data/validate.py:2034` (a rule's own SQL).
- **A caller's own identifier, by design:** `validation_rules.py:234` (`builtin_rule`,
  `model_schema/validation.py:484-485`), `auth/oidc.py:127` (PyJWT reason).
- **Not exception text:** `settings.py:355` formats the environment override's `raw!r` on
  purpose; out of this predicate, noted for the lead.

**Residual, not a row:** `modelling/ebm.py:229` stores interpret's `ValueError` text in the fit
Job's error (`worker/model_handlers.py:400`); whether interpret quotes a value was not verified.

*Not run:* no check, no test (brief). Every quote above was read from the tree named.

## Disposition

**Proposed severity (the auditor proposes; the lead decides):** row 1 MEDIUM, rows 2–11 LOW,
for the reasons in each row. No row is HIGH: no sink found carries a **quote input** (NFR-499's
class) into a store; the scoring routes are already built through `safe_error`.

**Remedy, proposed:** (a) row 1 at its root: the worker's `PlatformError` clause persists
`exc.detail` only when the raise site built it input-free, which needs either `compile_rating_version`
to render a non-coded `ValueError` through `safe_error_text` (the A-2 option (A) shape, at
`:704-711`), or the `PlatformError` clause to stop trusting `detail`; with a test red at its
parent that stores a `ValidationError`'s `input_value` through the compile Job. (b) Rows 2–7:
`safe_error_detail(exc)` in place of `str(exc)` — one change per row, the 422 keeps its field
paths and types. (c) Rows 8–11: accept or carry forward, at the lead's choice.

**Owner: WK-1178** (the ruling). Event that next confirms or discharges it: the remedy PR for
row 1 with its red-first test; or the next slice that adds a `PlatformError(…, str(exc))` in a
worker path.
