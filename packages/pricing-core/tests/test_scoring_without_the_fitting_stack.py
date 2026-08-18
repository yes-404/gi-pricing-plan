"""Scoring works with the fitting stack absent (`07` NFR-PLAT-11, ADR-0003, FR-MODEL-62).

OQ-PLAT-3 decided that the scoring service is the same image with a role flag through Phases
1-2 and a separate image from Phase 3. The only thing that makes the later split cheap is
that the scoring path never grows a dependency on the libraries that *fit* models — and the
only way to know it has not is to score with those libraries made unimportable.

**An import-linter contract was tried first and is the wrong instrument.** `glum` and
`sklearn` are already imported at *call sites* rather than at module scope — inside
`fit_glm`, `propose_banding` and `propose_grouping` — which is the discipline this
requirement wants. import-linter reads the AST and counts a function-scope import exactly
like a module-scope one, so a contract over `pricing_core.modelling.predict` reports four
violations against code that is already correct, and the only ways to make it pass are to
weaken it or to restructure modules that have no other reason to move. What matters is the
**runtime** property, so the test creates the runtime: a subprocess where importing the
fitting stack raises.

`xgboost` and `lightgbm` are deliberately not blocked. `02` FR-MODEL-62 scores a GBM by
loading its JSON booster, so a boosting library is a scoring dependency by design; what the
split sheds is the libraries that fit.
"""

from __future__ import annotations

import json
import subprocess
import sys
from uuid import uuid4

import numpy as np
import polars as pl
import pytest

from model_schema import Factor, FactorType, GlmSpec, OffsetSpec
from pricing_core.modelling.glm import fit_glm

#: Run in the child, where the fitting stack must not be reachable. Everything it needs
#: arrives as JSON on argv — which is also the point: a scoring process receives artifacts,
#: never a live fitting session (ADR-0003).
CHILD = r'''
import json, sys

BLOCKED = {"glum", "sklearn", "celery", "dagster"}


class Blocker:
    """Refuses the fitting stack, however deep the import is attempted."""

    def find_spec(self, name, path=None, target=None):
        if name.split(".")[0] in BLOCKED:
            raise ImportError(
                f"{name} was imported while scoring — `07` NFR-PLAT-11 forbids it"
            )
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

mu = predict_glm(fit, frame, factors, spec)

for blocked in BLOCKED:
    assert blocked not in sys.modules, f"{blocked} reached sys.modules while scoring"

print(json.dumps({"total": float(mu.sum()), "rows": int(mu.shape[0])}))
'''


def _book(n: int = 400) -> pl.DataFrame:
    rng = np.random.default_rng(20260818)
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


@pytest.mark.req("NFR-PLAT-11")
@pytest.mark.req("FR-MODEL-62")
def test_a_glm_scores_in_a_process_where_the_fitting_stack_cannot_be_imported() -> None:
    """Fit here, score there — which is what a separate scoring image would do.

    The assertion is the Poisson identity the in-process test uses: with a log link, an
    intercept and an exposure offset the fitted totals reproduce the observed total. A child
    that merely imported the module would prove much less — this one reconstructs the design,
    the base level and the offset with `glum` unimportable.
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
    fit = fit_glm(frame, spec, factors, seed=1).result

    payload = json.dumps(
        {
            "fit": fit.model_dump_json(),
            "spec": spec.model_dump_json(),
            "factors": [f.model_dump_json() for f in factors],
            "rows": frame.to_dict(as_series=False),
        }
    )
    completed = subprocess.run(
        [sys.executable, "-c", CHILD, payload],
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr

    scored = json.loads(completed.stdout)
    assert scored["rows"] == frame.height
    assert scored["total"] == pytest.approx(float(frame["claim_count"].sum()), rel=1e-6)


@pytest.mark.req("NFR-PLAT-11")
def test_the_blocker_would_notice_a_fitting_import() -> None:
    """The guard above is only worth its runtime if the block actually blocks.

    Without this, a `Blocker` that silently returned `None` for everything would let the
    test above pass by importing `glum` freely — a green test proving nothing, which is the
    failure mode a check like this is most prone to.
    """
    child = CHILD.split("payload = json.loads")[0] + "import glum\n"
    completed = subprocess.run(
        [sys.executable, "-c", child], capture_output=True, text=True, check=False
    )
    assert completed.returncode != 0
    assert "NFR-PLAT-11 forbids it" in completed.stderr
