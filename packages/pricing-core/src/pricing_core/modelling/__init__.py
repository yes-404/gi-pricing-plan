"""Modelling maths: factors, bandings, groupings, GLM and GBM fitting (`02` §5.2).

Importable without the platform, like every other `pricing-core` module — ADR-0001, and
the import-linter contract that enforces it.
"""

from pricing_core.modelling.bandings import (
    apply_banding,
    band_statistics,
    check_banding,
    propose_banding,
)
from pricing_core.modelling.comparison import ComparisonCandidate, compare_models
from pricing_core.modelling.diagnostics import (
    DiagnosticsResult,
    compute_diagnostics,
    compute_gbm_diagnostics,
    deviance,
    unit_deviance,
)
from pricing_core.modelling.errors import (
    BandingError,
    FactorResolutionError,
    GroupingError,
    ModellingError,
)
from pricing_core.modelling.factors import FactorMatrix, rateable, resolve_factors
from pricing_core.modelling.gbm import (
    SUPPORTED_GBM_OBJECTIVES,
    GbmFit,
    GbmFitError,
    apply_loss_treatment,
    fit_gbm,
    objective_family,
    predict_gbm,
    tree_summary,
)
from pricing_core.modelling.glm import GlmFitError, fit_glm
from pricing_core.modelling.groupings import (
    apply_grouping,
    grouping_evidence,
    propose_grouping,
)
from pricing_core.modelling.predict import (
    PredictionError,
    linear_predictor,
    predict_glm,
)
from pricing_core.modelling.transparency import (
    build_glm_approximation,
    build_shap_summary,
    fidelity_statement,
)

__all__ = [
    "SUPPORTED_GBM_OBJECTIVES",
    "BandingError",
    "ComparisonCandidate",
    "DiagnosticsResult",
    "FactorMatrix",
    "FactorResolutionError",
    "GbmFit",
    "GbmFitError",
    "GlmFitError",
    "GroupingError",
    "ModellingError",
    "PredictionError",
    "apply_banding",
    "apply_grouping",
    "apply_loss_treatment",
    "band_statistics",
    "build_glm_approximation",
    "build_shap_summary",
    "check_banding",
    "compare_models",
    "compute_diagnostics",
    "compute_gbm_diagnostics",
    "deviance",
    "fidelity_statement",
    "fit_gbm",
    "fit_glm",
    "grouping_evidence",
    "linear_predictor",
    "objective_family",
    "predict_gbm",
    "predict_glm",
    "propose_banding",
    "propose_grouping",
    "rateable",
    "resolve_factors",
    "tree_summary",
    "unit_deviance",
]
