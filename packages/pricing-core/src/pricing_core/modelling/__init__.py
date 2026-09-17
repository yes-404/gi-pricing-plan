"""Modelling maths: factors, bandings, groupings, GLM and GBM fitting (`02` §5.2).

Importable without the platform, like every other `pricing-core` module — ADR-703, and
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
    backtest_model,
    compute_diagnostics,
    compute_gbm_diagnostics,
    deviance,
    unit_deviance,
)
from pricing_core.modelling.ebm import EbmFitError, fit_ebm
from pricing_core.modelling.errors import (
    BandingError,
    FactorResolutionError,
    GroupingError,
    ModellingError,
    NonFiniteDerivativeError,
    ObjectiveError,
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
from pricing_core.modelling.glm import (
    COVARIANCE_MEDIA_TYPE,
    GlmFit,
    GlmFitError,
    decode_covariance,
    encode_covariance,
    fit_glm,
)
from pricing_core.modelling.groupings import (
    apply_grouping,
    grouping_evidence,
    propose_grouping,
)
from pricing_core.modelling.objectives import (
    ObjectiveFns,
    certify_objective,
    compile_objective,
    make_lgb_objective,
    make_xgb_objective,
)
from pricing_core.modelling.predict import (
    PredictionError,
    linear_predictor,
    predict_glm,
)
from pricing_core.modelling.transparency import (
    GlmApproximationFit,
    approximation_spec,
    build_glm_approximation,
    build_shap_summary,
    fidelity_statement,
)

__all__ = [
    "COVARIANCE_MEDIA_TYPE",
    "SUPPORTED_GBM_OBJECTIVES",
    "BandingError",
    "ComparisonCandidate",
    "DiagnosticsResult",
    "EbmFitError",
    "FactorMatrix",
    "FactorResolutionError",
    "GbmFit",
    "GbmFitError",
    "GlmApproximationFit",
    "GlmFit",
    "GlmFitError",
    "GroupingError",
    "ModellingError",
    "NonFiniteDerivativeError",
    "ObjectiveError",
    "ObjectiveFns",
    "PredictionError",
    "apply_banding",
    "apply_grouping",
    "apply_loss_treatment",
    "approximation_spec",
    "backtest_model",
    "band_statistics",
    "build_glm_approximation",
    "build_shap_summary",
    "certify_objective",
    "check_banding",
    "compare_models",
    "compile_objective",
    "compute_diagnostics",
    "compute_gbm_diagnostics",
    "decode_covariance",
    "deviance",
    "encode_covariance",
    "fidelity_statement",
    "fit_ebm",
    "fit_gbm",
    "fit_glm",
    "grouping_evidence",
    "linear_predictor",
    "make_lgb_objective",
    "make_xgb_objective",
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
