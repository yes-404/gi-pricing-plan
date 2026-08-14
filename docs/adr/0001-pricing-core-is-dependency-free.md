# ADR-0001 — pricing-core is dependency-free and owns all actuarial maths

- **Status:** accepted
- **Date:** 2026-08-14
- **Deciders:** maintainer
- **Related:** FR-OVR-5, DEP-3, ADR-0002

## Context

Actuarial computation must be reproducible outside the platform: by a reviewer checking a
filing, by a maintainer debugging a production quote, by a user in a notebook, and by CI
with property-based tests. Commercial pricing suites fail this — their maths is only
reachable through their own UI and runtime, which makes independent verification and
regression testing hard.

There is constant pressure to let a fitting routine "just read the dataset from S3" or
"just log to the request logger", which would drag web and storage dependencies into the
computational core.

## Decision

`packages/pricing-core` contains **all** actuarial computation and **no** infrastructure.

- It may depend on: Polars, NumPy/SciPy, glum, statsmodels, XGBoost, LightGBM, interpret,
  the ZEN Engine bindings, and `packages/model-schema`.
- It must not depend on: FastAPI, SQLAlchemy, Celery, Redis, boto3, or any HTTP/DB/queue
  client.
- Its functions are pure with respect to I/O: data arrives as Polars DataFrames or
  `model-schema` models and leaves the same way. Progress is reported through an injected
  callback, never a logger or a database write.
- Stochastic functions take an explicit `seed: int` (FR-OVR-8).
- The backend orchestrates and persists; it contains no actuarial formulae. A reviewer
  must be able to answer "how is this number computed?" by reading `pricing-core` alone.

CI enforces this with an import-linter contract that fails the build on a forbidden
import, and by running the `pricing-core` test suite in an environment where the backend
packages are not installed.

## Consequences

**Positive** — independent verification and notebook use; fast unit tests with no
fixtures; the option to publish `pricing-core` to PyPI (OQ-OVR-4); a clean seam for
swapping fitting backends.

**Negative** — the backend must materialise data before calling the core, so worker
memory is sized for the dataset rather than streamed from storage inside the fit;
some duplication of small helpers between core and backend; progress reporting is more
ceremony than a logger call.

**Neutral** — the core is where performance work concentrates, since it is the only place
that touches full datasets.
