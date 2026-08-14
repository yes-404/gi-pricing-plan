---
name: python-package
description: Write Python in this repo's uv workspace — where code belongs, the package dependency boundaries enforced by import-linter, and the Pydantic v2 and typing idioms the contracts depend on. Use when adding a module or package, adding a dependency, defining an artifact shape, or touching anything under packages/.
---

# Writing Python here

## Where code goes

| Package | Holds | May import |
|---|---|---|
| `packages/model-schema` | Every shape crossing a module boundary or persisted as an artifact | **Pydantic only** |
| `packages/pricing-core` | All actuarial computation | Polars, NumPy/SciPy, glum, XGBoost, LightGBM, ZEN bindings, `model_schema` — **no** web/DB/queue client |
| `backend/` *(from W2)* | Orchestration, persistence, API | Anything, including both packages |

`.importlinter` enforces the boundaries and CI runs `lint-imports`. **Do not work around a
contract failure by adding the module to the allow-list** — the failure means the code is
in the wrong package. ADR-0001's value is that a reviewer can reproduce a number without
the platform, and one convenience import ends that.

`src/` layout throughout; `uv` workspace with **one lockfile at the root**.

```bash
uv sync --all-packages --dev
uv run ruff check . && uv run mypy && uv run lint-imports && uv run pytest -q
```

## Adding a dependency

Add it to the *package's* `pyproject.toml`, not the root. Then check it against
`.importlinter` — if `pricing-core` needs something the contract forbids, the answer is
almost always that the code belongs in `backend/`.

Every runtime dependency must be **Apache-2.0 compatible** (OQ-OVR-2 decided; NFR-OVR-11).
AGPL and SSPL are out, transitively.

## Pydantic v2 idioms this project depends on

**Money is a type, not a convention.** `MoneyMinor` is `Annotated[int, Strict()]`, so a
float is a validation error. `250.0` is refused as firmly as `361.20` — it is a whole
number of pence, so accepting it would teach callers that floats are fine here.

**`Decimal` needs help to be safe.** A bare `Decimal` field generates
`anyOf: [{"type":"number"}, {"type":"string"}]`, and the number branch admits the lossy
binary form FR-OVR-7 forbids — a payload could satisfy the generated contract while
violating the spec. Use `DecimalStr`, which pins a `PlainSerializer` to `str` **and**
overrides `__get_pydantic_json_schema__` to declare `type: string`. Verified: research F7.

**Artifacts are frozen.** `model_config = ConfigDict(frozen=True, extra="forbid")` is
FR-OVR-1 as a type. `extra="forbid"` matters just as much — ADR-0002 makes this package the
single source of truth, so an undeclared field does not exist.

**Discriminated unions** survive to JSON Schema as `oneOf` + `discriminator`, and a
`Literal` covering two tags maps both onto one branch. Verified: research F6.

## Typing

`mypy --strict` over `packages/`. Prefer `Protocol` over ABCs for injected collaborators —
`ProgressCallback` is defined in `pricing-core` and *implemented* by the backend, so the
dependency points inward and ADR-0001 holds while FR-PLAT-8/9 are still satisfied.

`from __future__ import annotations` at the top of every module.

## Style

Ruff, line length 100. Match the surrounding code. Comments explain *why* — the what is in
the spec, and a comment restating the code is noise that rots.

## Verified

2026-08-14 — W1. `MoneyMinor` strictness, `DecimalStr` schema pinning, and envelope
freezing are all covered by passing tests, including negative ones asserting a float is
refused and that the generated schema carries no `anyOf`. The `DecimalStr` rule exists
because research F7 measured the permissive union on a bare `Decimal`; without it the
contract would have admitted exactly what FR-OVR-7 forbids.
