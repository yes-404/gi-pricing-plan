"""Modelling maths: factors, bandings, groupings and GLM fitting (`02` §5.2).

Importable without the platform, like every other `pricing-core` module — ADR-0001, and
the import-linter contract that enforces it.
"""

from pricing_core.modelling.bandings import (
    apply_banding,
    band_statistics,
    check_banding,
    propose_banding,
)
from pricing_core.modelling.diagnostics import (
    DiagnosticsResult,
    compute_diagnostics,
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

__all__ = [
    "BandingError",
    "DiagnosticsResult",
    "FactorMatrix",
    "FactorResolutionError",
    "GlmFitError",
    "GroupingError",
    "ModellingError",
    "PredictionError",
    "apply_banding",
    "apply_grouping",
    "band_statistics",
    "check_banding",
    "compute_diagnostics",
    "deviance",
    "fit_glm",
    "grouping_evidence",
    "linear_predictor",
    "predict_glm",
    "propose_banding",
    "propose_grouping",
    "rateable",
    "resolve_factors",
    "unit_deviance",
]
