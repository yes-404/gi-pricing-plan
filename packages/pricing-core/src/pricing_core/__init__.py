"""Pure Python actuarial engine (ADR-703).

May depend on: Polars, NumPy/SciPy, glum, statsmodels, XGBoost, LightGBM, interpret, the
ZEN Engine bindings, and `model-schema`.

Must not depend on: FastAPI, SQLAlchemy, Celery, Redis, boto3, or any HTTP/DB/queue client.
`.importlinter` enforces this and CI fails the build on a forbidden import — the contract
is checked, not trusted, because ADR-703's whole value is that a reviewer can verify a
number without the platform.
"""

from pricing_core.modelling.ebm import EbmFitError, fit_ebm
from pricing_core.money import ROUNDING_MODES, RoundingMode, apply_factor, reconcile_ladder
from pricing_core.progress import (
    JobCancelled,
    NullProgress,
    ProgressCallback,
    ScaledProgress,
)

__all__ = [
    "ROUNDING_MODES",
    "EbmFitError",
    "JobCancelled",
    "NullProgress",
    "ProgressCallback",
    "RoundingMode",
    "ScaledProgress",
    "apply_factor",
    "fit_ebm",
    "reconcile_ladder",
]
