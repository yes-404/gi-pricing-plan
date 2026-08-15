"""Modelling maths: factor resolution and GLM fitting (`02` §5.2).

Importable without the platform, like every other `pricing-core` module — ADR-0001, and
the import-linter contract that enforces it.
"""

from pricing_core.modelling.factors import FactorMatrix, resolve_factors
from pricing_core.modelling.glm import GlmFitError, fit_glm

__all__ = ["FactorMatrix", "GlmFitError", "fit_glm", "resolve_factors"]
