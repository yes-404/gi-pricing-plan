---
family: reference
title: Packages
status: active                  # active → retired (§1.2a)
created: 2026-08-14
owner: lead
corrected_by: []
relates: []                      # ids only
---

# Packages

| Package | Purpose | May depend on |
|---|---|---|
| [`model-schema`](model-schema) | Every shape crossing a module boundary or persisted as an artifact (ADR-704) | Pydantic, and nothing else |
| [`pricing-core`](pricing-core) | All actuarial computation (ADR-703) | Polars, NumPy/SciPy, glum, XGBoost, LightGBM, ZEN bindings, `model-schema` — **no** web, database or queue client |

Both contracts are enforced by `.importlinter` and checked in CI. They are not style
preferences: ADR-703 exists so a reviewer can reproduce a number without the platform, and
that is only true if nothing has reached for a database client.

## Running the checks

```bash
uv sync --all-packages --dev
uv run ruff check . && uv run mypy && uv run lint-imports && uv run pytest -q
uv run python scripts/req-coverage.py     # which requirements the suite claims
```

## Requirement traceability

Tests are marked with the requirement they satisfy:

```python
@pytest.mark.req("FR-10")
def test_money_minor_refuses_floats(): ...
```

`scripts/req-coverage.py` turns those marks into a report and **fails if a test claims a
requirement that does not exist** — which catches both typos and any renumbering that
violates the append-only rule (`CLAUDE.md` §5).

## A note on the tests

Most of the money tests are **negative**. For a governed system the suite has to prove the
wrong thing *cannot* happen, not merely that the right thing can — so the tests that earn
their keep assert that a float is refused, that an envelope cannot be mutated, and that the
generated JSON Schema does not admit a payload the specification forbids.
