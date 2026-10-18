"""FR-127's large-loss treatment, in one place (SL-1734, 2026-10-17).

It lived in `gbm.py` while only the boosters applied it. The GLM and EBM arms fit the
same declared `loss_treatment` and read it nowhere, so a capped spec fitted uncapped under
a recorded treatment (FD-1723). Every fit arm now applies this one function at its response
read, passing its own fit-error class as `weights.require_usable_weights` does.
"""

from __future__ import annotations

from collections.abc import Callable

import numpy as np

from model_schema import LossTreatment

__all__ = ["apply_loss_treatment"]


def apply_loss_treatment(
    response: np.ndarray, treatment: LossTreatment, error: Callable[..., Exception]
) -> np.ndarray:
    """FR-127: large-loss treatment is applied to the **response**, at fit time.

    Not to the dataset. `01` VR-ACT-10 flags large losses and never removes them, so one
    validated Dataset Version serves many capping assumptions without re-ingestion — which
    is only true while the assumption is applied here.

    `spliced` and `excess` are declared by FR-127 and implemented by nothing. They are
    refused by name rather than treated as `none`: fitting an uncapped model under a spec
    that says otherwise would be wrong in the one direction nobody checks, since the spec
    is what `spec_hash` and the model document both report. `error` is the calling arm's own
    fit-error class (`GlmFitError`, `GbmFitError`, `EbmFitError`), taking `(code, message,
    terms=…)`, so the platform's handler maps the one code whichever arm raised it.
    """
    if treatment.kind == "none":
        return response
    if treatment.kind == "capped":
        capped = np.minimum(response, float(treatment.cap_minor or 0))
        return np.asarray(capped, dtype=np.float64)
    raise error(
        "LOSS_TREATMENT_UNIMPLEMENTED",
        f"loss treatment {treatment.kind!r} is declared by FR-127 and built by no "
        "slice yet. Refused rather than applied as 'none', which would fit an uncapped "
        "model under a spec that records a treatment.",
        terms=[treatment.kind],
    )
