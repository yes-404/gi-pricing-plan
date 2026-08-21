"""Turning failures into the one error shape the API promises (`00` §5.3, FR-PLAT-47).

Two rules hold this together:

* Every non-2xx response is a `ProblemDetail`, including the ones FastAPI and Starlette
  raise on their own. A framework default that leaks `{"detail": "..."}` is a second error
  shape, and a client cannot branch on a shape it was not told about.
* Every problem carries the request's `trace_id` (R4, FR-PLAT-42), so a support
  conversation starts with an identifier rather than a screenshot.
"""

from __future__ import annotations

from typing import Final

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.observability.trace import current_trace_id
from model_schema import FieldError, ProblemDetail

__all__ = [
    "DATA_ERROR_CODES",
    "GOVERNANCE_ERROR_CODES",
    "MODELLING_ERROR_CODES",
    "PLATFORM_ERROR_CODES",
    "PlatformError",
    "install_error_handlers",
    "problem_response",
    "unexpected_problem",
]

PROBLEM_MEDIA_TYPE: Final = "application/problem+json"
_DOC_BASE: Final = "https://docs.gi-pricing.dev/errors/"

#: Error codes owned by `07 — Platform` (§5.1). Kept as a frozenset so a typo raises here
#: rather than reaching a client as an unbranchable code.
PLATFORM_ERROR_CODES: Final[frozenset[str]] = frozenset(
    {
        "UNAUTHENTICATED",
        "TOKEN_EXPIRED",
        "API_KEY_INVALID",
        "API_KEY_EXPIRED",
        "ENVIRONMENT_SCOPE_DENIED",
        "JOB_NOT_CANCELLABLE",
        "JOB_RESOURCE_BUDGET_EXCEEDED",
        "JOB_HANDLER_NOT_REGISTERED",
        "JOB_HANDLER_FAILED",
        "IDEMPOTENCY_KEY_CONFLICT",
        "RATE_LIMITED",
        "BLOB_NOT_FOUND",
        "SECRET_NOT_FOUND",
        "SETTING_INVALID",
        "PROMOTION_ORDER_VIOLATION",
        "MIGRATION_REQUIRED",
        # `00` §5.4's optimistic concurrency, owned by `07` because FR-PLAT-47 owns "the API
        # implements `00` §5 exactly". Registered with the first routes that require the
        # header (the model lifecycle, W5) rather than when the convention was written —
        # W2 and W4 both recorded it as still absent, which is what made it findable.
        "CONFLICT_STALE_WRITE",
    }
)

#: Error codes owned by `01 — Data Management` (§5.1).
DATA_ERROR_CODES: Final[frozenset[str]] = frozenset(
    {
        "DATASET_NOT_VALIDATED",
        "DATASET_VERSION_IMMUTABLE",
        "SCHEMA_INFERENCE_CONFLICT",
        "COLUMN_NAME_COLLISION",
        "DIRECT_IDENTIFIER_PRESENT",
        "VALIDATION_HAS_FAILURES",
        "WARN_NOT_ACKNOWLEDGED",
        "ACKNOWLEDGE_FORBIDDEN_ROLE",
        "RULE_NOT_APPROVED",
        "RULE_SEVERITY_DOWNGRADE_FORBIDDEN",
        "RULE_TIMEOUT",
        "ACKNOWLEDGEMENT_ALREADY_RECORDED",
        "REFERENCE_INTERVAL_OVERLAP",
        "REFERENCE_VERSION_NOT_PINNED",
        "SOURCE_UNREACHABLE",
        "REJECT_RATE_EXCEEDED",
        # OQ-DATA-8, decided 2026-08-17. Every declared derivation except `split` is
        # refused until it is materialised (FR-DATA-45), and the refusal needs its own
        # code rather than `VALIDATION_FAILED`: the request is well formed and will be
        # valid unchanged once the operation is built, which is the opposite of what a
        # validation failure tells a caller.
        "DERIVATION_NOT_MATERIALISED",
    }
)

#: Error codes owned by `02 — Modelling` (§5.1).
#:
#: **Only the ones something can raise.** `02` §5.1 declares twenty-two; registering all of
#: them would repeat the mistake `01` made with `RULE_TIMEOUT` and `SOURCE_UNREACHABLE` —
#: codes in the catalogue, raised nowhere, indistinguishable from codes that work. The rest
#: arrive with the slices that raise them.
MODELLING_ERROR_CODES: Final[frozenset[str]] = frozenset(
    {
        "FACTOR_PROHIBITED",
        "FACTOR_RESOLUTION_FAILED",
        "BAND_EMPTY",
        "BAND_BELOW_MIN_EXPOSURE",
        "GROUPING_NOT_EXHAUSTIVE",
        "GLM_DID_NOT_CONVERGE",
        "GLM_RANK_DEFICIENT",
        # Raised by `pricing-core` since the spine and **registered only now**: the fit
        # handler maps a `GlmFitError`'s code straight into a `PlatformError`, so a
        # perfectly separated fit raised `ValueError: unknown error code` from inside the
        # error path instead of the named refusal FR-MODEL-23 promises.
        "GLM_SEPARATION_DETECTED",
        "OFFSET_REQUIRED_FOR_FREQUENCY",
        "MODEL_IMMUTABLE",
        # The diagnostics slice. A spec with no `split_ref` has no holdout, so it can
        # produce no diagnostics (FR-MODEL-54) and therefore cannot reach `fitted`
        # (`02` §4.8) — refused before the fit rather than after it.
        "MODEL_SPLIT_REQUIRED",
        # FR-MODEL-81's gate half, 2026-08-16. The diagnostic half shipped with the
        # diagnostics slice and this did not — a requirement counted as evidenced because
        # a test marked it, which is the "a marker is a claim, not a proof" trap
        # `CLAUDE.md` §13 names.
        "MODEL_SPEC_EXCEEDS_COMPLEXITY_LIMIT",
        # The comparison slice, 2026-08-17. `02` §5.1 declared no code for it, and
        # `VALIDATION_FAILED` would have done — but "these models cannot be compared" is a
        # state the compare screen branches on, and it has four distinct causes it must be
        # able to tell apart from a malformed request. Added to `02` §5.1's catalogue in the
        # same commit, and raised by `pricing-core` as well as by the platform.
        "MODELS_NOT_COMPARABLE",
        # The GBM slice, 2026-08-17. Every one of these is raised by `pricing-core` and
        # mapped straight into a `PlatformError` by the fit handler — which is exactly the
        # path that raised `ValueError: unknown error code` for `GLM_SEPARATION_DETECTED`
        # until the diagnostics slice noticed. Registering them with the code that raises
        # them, rather than when a caller trips one in production.
        "MONOTONE_CONSTRAINT_CONFLICT",
        "EARLY_STOPPING_REQUIRES_HOLDOUT",
        "OBJECTIVE_NOT_APPLICABLE",
        "OBJECTIVE_NOT_APPROVED",
        "UNSEEN_LEVEL_BEHAVIOUR_REQUIRED",
        # FR-MODEL-71's own code, and it earns one: "the offset cannot be reconstructed" is
        # a distinct failure from "this frame is missing a feature", and it is the one that
        # would otherwise score silently wrong on both backends.
        "OFFSET_NOT_RECONSTRUCTABLE",
        "GBM_NO_FEATURES",
        "SCORING_FEATURES_MISMATCH",
        "INTERACTION_FEATURE_UNKNOWN",
        "LOSS_TREATMENT_UNIMPLEMENTED",
        # The transparency slice. `MODEL_ALREADY_TRANSPARENT` is a refusal rather than a
        # no-op on purpose: a GLM approximating itself reports perfect fidelity, and an
        # artifact that satisfies R3 while carrying no information is worse than none.
        "MODEL_NOT_FITTED",
        "MODEL_ALREADY_TRANSPARENT",
        "MODEL_TYPE_UNSUPPORTED",
        "APPROXIMATION_TARGET_NOT_POSITIVE",
        "SHAP_SAMPLE_EMPTY",
        # The custom-objectives slice, 2026-08-18. Six refusals from the fit path, and
        # four that have been reachable since the prediction slice: `predict.py`'s codes go
        # into `PlatformError(exc.code, ...)` through `_unscoreable`, so every one of them
        # was an `unknown error code` waiting in the error path. The invariant test could
        # not see them because it scanned a hand-listed set of exception names that had
        # never gained `PredictionError`; it now derives the set from the module.
        "OBJECTIVE_NOT_SUPPLIED",
        "OBJECTIVE_REF_MISMATCH",
        "OBJECTIVE_RESPONSE_UNDECLARED",
        "OBJECTIVE_REQUIRES_OFFSET",
        "OBJECTIVE_EARLY_STOPPING_UNSUPPORTED",
        "OBJECTIVE_HESSIAN_STRATEGY_UNSUPPORTED",
        "OBJECTIVE_KIND_NOT_ENABLED",
        "MODEL_TERM_UNRESOLVED",
        "MODEL_LINK_UNSUPPORTED",
        "MODEL_OFFSET_MISSING",
        # FR-MODEL-24, 2026-08-21, the offset-from-another-model slice. The fit job's
        # resolver raises it when `offset_model_ref` names a model that cannot serve as
        # the offset — not fitted, not a GLM, or fitted with a link that is not the new
        # spec's. A ref that names no model at all is `NOT_FOUND`: this code is for the
        # refs that resolve to something, just something unusable.
        "MODEL_OFFSET_REF_INVALID",
        "MODEL_INTERVAL_UNAVAILABLE",
        "MODEL_INTERVAL_PAIR_INVALID",
        # FR-MODEL-96, 2026-08-19. The surrogate the transparency Job reserves is an
        # ordinary Model, so `POST /api/v1/models` can be handed a spec claiming to
        # approximate anything at all.
        "MODEL_APPROXIMATION_INVALID",
        # The peril-structure slice, 2026-08-18. `02` §5.1 has declared this code since
        # Phase 0 and nothing raised it; `LOSS_TREATMENT_UNIMPLEMENTED` above was
        # registered by the GBM slice for the same reason and is raised for the first time
        # here, by `separate_model`.
        "PERIL_STRUCTURE_RECONCILIATION_FAILED",
        # The custom-metrics slice, 2026-08-19 (FR-MODEL-108). `METRIC_REF_UNRESOLVED` is
        # raised by this slice's `resolve_ref`; `METRIC_NOT_APPLICABLE` and
        # `METRIC_NOT_FITTABLE` are FR-MODEL-106's refusals from the GBM fit path (the
        # slice that wires `GbmSpec.eval_metrics`) and are registered here, with the
        # artifact they belong to, rather than left for that slice to discover unregistered
        # the way `GLM_SEPARATION_DETECTED` was.
        "METRIC_REF_UNRESOLVED",
        "METRIC_NOT_APPLICABLE",
        "METRIC_NOT_FITTABLE",
        # The regularisation-and-CV slice, 2026-08-21 (FR-MODEL-20, FR-MODEL-53). Raised
        # by `_fit_cv_path` when a fold has no held-out rows (or no training rows) at some
        # alpha on the scanned path — `key_column`/`time_column` skew that a fold count
        # chosen against the whole book does not guarantee against, per fold.
        "GLM_CV_FOLD_EMPTY",
        # GLM_TWEEDIE_POWER_GRID_EDGE (2026-08-21, FR-MODEL-22): the profile over
        # tweedie.p_grid is maximised at a scan edge, so the estimate would report the
        # scan's boundary as the answer.
        "GLM_TWEEDIE_POWER_GRID_EDGE",
    }
)

#: Error codes owned by `06 — Governance` (§5.1).
GOVERNANCE_ERROR_CODES: Final[frozenset[str]] = frozenset(
    {
        "PERMISSION_DENIED",
        "SCOPE_DENIED",
        "SUBMITTER_CANNOT_APPROVE",
        "DUPLICATE_APPROVER",
        "EVIDENCE_INCOMPLETE",
        "POLICY_BELOW_EVIDENCE_FLOOR",
        "CHECKLIST_INCOMPLETE",
        "ARTIFACT_FLAGGED",
        "APPROVAL_PINNED_ARTIFACT_CHANGED",
        "APPROVAL_ALREADY_DECIDED",
        "WITHDRAW_AFTER_DEPLOY_FORBIDDEN",
        "BREAK_GLASS_REASON_REQUIRED",
        "AUDIT_CHAIN_BROKEN",
        "ATTESTATION_OVERDUE",
    }
)

#: Codes raised by the shared request machinery rather than owned by one module.
_GENERIC_ERROR_CODES: Final[frozenset[str]] = frozenset(
    {"VALIDATION_FAILED", "NOT_FOUND", "METHOD_NOT_ALLOWED", "INTERNAL_ERROR"}
)

_KNOWN_CODES: Final[frozenset[str]] = (
    PLATFORM_ERROR_CODES
    | GOVERNANCE_ERROR_CODES
    | DATA_ERROR_CODES
    | MODELLING_ERROR_CODES
    | _GENERIC_ERROR_CODES
)


def _type_uri(code: str) -> str:
    return _DOC_BASE + code.lower().replace("_", "-")


class PlatformError(Exception):
    """An expected failure with a stable code, renderable as a problem response.

    Deliberately not a subclass of `HTTPException`: the code — not the status — is the
    contract, and several codes share a status.
    """

    def __init__(
        self,
        code: str,
        title: str,
        status_code: int,
        detail: str | None = None,
        *,
        errors: tuple[FieldError, ...] = (),
    ) -> None:
        if code not in _KNOWN_CODES:
            raise ValueError(
                f"unknown error code {code!r}. Codes are enumerated in the owning spec's "
                "Interfaces section; add it there before raising it."
            )
        super().__init__(detail or title)
        self.code = code
        self.title = title
        self.status_code = status_code
        self.detail = detail
        self.errors = errors

    def to_problem(self, instance: str | None = None) -> ProblemDetail:
        return ProblemDetail(
            type=_type_uri(self.code),
            title=self.title,
            status=self.status_code,
            code=self.code,
            detail=self.detail,
            instance=instance,
            errors=self.errors,
            trace_id=current_trace_id(),
        )


def problem_response(problem: ProblemDetail) -> JSONResponse:
    """Render a problem as `application/problem+json`, as RFC 9457 requires."""
    return JSONResponse(
        status_code=problem.status,
        content=problem.model_dump(mode="json", exclude_none=True),
        media_type=PROBLEM_MEDIA_TYPE,
    )


async def _handle_platform_error(request: Request, exc: PlatformError) -> JSONResponse:
    return problem_response(exc.to_problem(instance=request.url.path))


async def _handle_validation_error(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Render FastAPI's request-validation failure as a problem with field-level errors.

    FR-PLAT-11's principle applies to synchronous rejections too: a deterministic failure
    should name the field, so the UI can mark it rather than showing a banner.
    """
    field_errors = tuple(
        FieldError(
            # Drop the leading location segment ('body', 'query'): the client sent one
            # document and does not need our parser's internal framing.
            field=".".join(str(part) for part in err["loc"][1:]) or str(err["loc"][0]),
            code=str(err["type"]).upper().replace(".", "_"),
            message=str(err["msg"]),
        )
        for err in exc.errors()
    )
    problem = ProblemDetail(
        type=_type_uri("VALIDATION_FAILED"),
        title="Request validation failed",
        status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        code="VALIDATION_FAILED",
        detail=f"{len(field_errors)} field(s) failed validation.",
        instance=request.url.path,
        errors=field_errors,
        trace_id=current_trace_id(),
    )
    return problem_response(problem)


_STATUS_CODES: Final[dict[int, tuple[str, str]]] = {
    status.HTTP_404_NOT_FOUND: ("NOT_FOUND", "Resource not found"),
    status.HTTP_405_METHOD_NOT_ALLOWED: ("METHOD_NOT_ALLOWED", "Method not allowed"),
}


async def _handle_http_exception(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """Convert framework-raised HTTP errors into problems.

    Without this, a 404 from the router returns `{"detail": "Not Found"}` — a second error
    shape, with no code and no `trace_id`.
    """
    code, title = _STATUS_CODES.get(exc.status_code, ("INTERNAL_ERROR", "Request failed"))
    problem = ProblemDetail(
        type=_type_uri(code),
        title=title,
        status=exc.status_code,
        code=code,
        detail=str(exc.detail) if exc.detail else None,
        instance=request.url.path,
        trace_id=current_trace_id(),
    )
    return problem_response(problem)


def unexpected_problem(instance: str | None = None) -> ProblemDetail:
    """The problem returned for an unhandled exception.

    The message is deliberately fixed. An exception string can carry a connection URL or a
    row of data, and R3 puts secrets out of API responses; the `trace_id` is how the
    detail is retrieved, from logs the operator can see and the caller cannot.

    Built here but rendered by `TraceMiddleware`, because Starlette's own
    `ServerErrorMiddleware` — where an app-level `Exception` handler is installed — sits
    *outside* every user middleware. By the time it runs, the trace context has been reset
    and the id is gone from precisely the response that most needs it.
    """
    return ProblemDetail(
        type=_type_uri("INTERNAL_ERROR"),
        title="Internal server error",
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code="INTERNAL_ERROR",
        detail="The request failed unexpectedly. Quote the trace id when reporting it.",
        instance=instance,
        trace_id=current_trace_id(),
    )


async def _handle_unexpected(request: Request, exc: Exception) -> JSONResponse:
    """Backstop for an exception raised outside `TraceMiddleware`'s reach."""
    return problem_response(unexpected_problem(request.url.path))


def install_error_handlers(app: FastAPI) -> None:
    """Register the handlers that make every error path produce a `ProblemDetail`."""
    app.add_exception_handler(PlatformError, _handle_platform_error)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, _handle_validation_error)  # type: ignore[arg-type]
    app.add_exception_handler(StarletteHTTPException, _handle_http_exception)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, _handle_unexpected)
