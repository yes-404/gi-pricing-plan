"""The platform backend: orchestration, persistence, and the HTTP API.

`07 — Platform` is the governing spec. The module path matches its §5.2 (`app.platform.*`);
the `src/` layer is this repo's packaging convention and does not change the import path.

This package may import anything, including both workspace packages. The dependency runs
one way only: `pricing_core` and `model_schema` never import `app` (ADR-703, DEP-3).
"""
