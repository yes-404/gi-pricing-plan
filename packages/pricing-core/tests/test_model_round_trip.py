"""A stored Model round-trips: export, import into a clean instance, score identically
(NFR-482, verdict reversed 2026-08-27 by WK-665).

The requirement asks for export → import into a clean instance → predictions identical to
the last representable digit. The model's artifact is the `GlmFitResult` (plus the spec and
the factors it was fitted with); the clean instance is a subprocess where the fitting stack
cannot be imported — the `test_scoring_without_the_fitting_stack.py` mechanism. Scoring the
same serialised artifact in the parent and in two clean children must produce byte-identical
totals, which is what "identical to the last representable digit" means: float64 JSON
round-trips exactly, and a lossless export/import preserves the prediction.
"""

from __future__ import annotations

import json
import subprocess
import sys
from uuid import uuid4

import numpy as np
import polars as pl
import pytest

from model_schema import (
    Factor,
    FactorType,
    GlmSpec,
    OffsetSpec,
)
from pricing_core.modelling.glm import fit_glm
from pricing_core.modelling.predict import predict_glm

#: Run in the clean instance, where the fitting stack must not be reachable. Everything it
#: needs arrives as JSON on argv — a scoring process receives artifacts, never a live
#: fitting session (ADR-705).
CHILD = r'''
import json, sys

BLOCKED = {"glum", "sklearn", "celery", "dagster", "interpret"}


class Blocker:
    def find_spec(self, name, path=None, target=None):
        if name.split(".")[0] in BLOCKED:
            raise ImportError(f"{name} was imported while scoring — NFR-482 forbids it")
        return None


sys.meta_path.insert(0, Blocker())

import polars as pl  # noqa: E402
from model_schema import Factor, GlmFitResult, GlmSpec  # noqa: E402

from pricing_core.modelling.predict import predict_glm  # noqa: E402

payload = json.loads(sys.argv[1])
fit = GlmFitResult.model_validate_json(payload["fit"])
spec = GlmSpec.model_validate_json(payload["spec"])
factors = [Factor.model_validate_json(f) for f in payload["factors"]]
frame = pl.DataFrame(payload["rows"])

for blocked in BLOCKED:
    assert blocked not in sys.modules, f"{blocked} reached sys.modules while scoring"

mu = predict_glm(fit, frame, factors, spec)
print(json.dumps({"total": float(mu.sum()), "rows": int(mu.shape[0])}))
'''


def _book(n: int = 400) -> pl.DataFrame:
    rng = np.random.default_rng(20260827)
    area = rng.choice(["A", "B", "C"], size=n)
    exposure = rng.uniform(0.5, 1.0, size=n)
    lam = exposure * np.where(area == "A", 0.10, np.where(area == "B", 0.16, 0.24))
    return pl.DataFrame(
        {
            "area": area,
            "exposure_years": exposure,
            "claim_count": rng.poisson(lam).astype(float),
        }
    )


@pytest.mark.req("NFR-482")
def test_a_stored_glm_scores_identically_in_a_clean_instance() -> None:
    """Export → import → score reproduces the prediction to the last representable digit.

    The parent scores the fitted model in-process; two clean children reload the exported
    artifact and score it with the fitting stack unimportable. All three totals are the
    same `float64` value — bit-identical, which is a stronger statement than an
    `approx` and exactly what "the last representable digit" means.
    """
    frame = _book()
    factors = [
        Factor(
            id=uuid4(), slug="area", dataset_id=uuid4(), version=1,
            type=FactorType.IDENTITY, source_columns=("area",),
        )
    ]
    spec = GlmSpec(
        model_family_slug="freq",
        dataset_version_id=uuid4(),
        response_column="claim_count",
        offset=OffsetSpec(kind="log_column", column="exposure_years"),
        factors=tuple(f.id for f in factors),
        family="poisson",
    )
    fit = fit_glm(frame, spec, factors).result

    parent_total = float(predict_glm(fit, frame, factors, spec).sum())

    payload = json.dumps(
        {
            "fit": fit.model_dump_json(),
            "spec": spec.model_dump_json(),
            "factors": [f.model_dump_json() for f in factors],
            "rows": frame.to_dict(as_series=False),
        }
    )
    child_totals = []
    for _ in range(2):
        completed = subprocess.run(
            [sys.executable, "-c", CHILD, payload],
            capture_output=True, text=True, check=False,
        )
        assert completed.returncode == 0, completed.stderr
        child_totals.append(json.loads(completed.stdout)["total"])

    # Two clean instances agree with each other and with the parent — bit-exact.
    assert child_totals[0] == child_totals[1]
    assert child_totals[0] == parent_total
    # And the total is the Poisson identity: the round-trip did not perturb the model.
    assert child_totals[0] == pytest.approx(float(frame["claim_count"].sum()), rel=1e-6)


@pytest.mark.req("NFR-482")
def test_the_clean_instance_cannot_import_the_fitting_stack() -> None:
    """The block above is only worth its runtime if the block actually blocks.

    Without this, a `Blocker` that silently returned `None` would let the round-trip pass
    by importing `glum` freely — a green test proving nothing.
    """
    child = CHILD.split("payload = json.loads")[0] + "import glum\n"
    completed = subprocess.run(
        [sys.executable, "-c", child], capture_output=True, text=True, check=False
    )
    assert completed.returncode != 0
    assert "NFR-482 forbids it" in completed.stderr
