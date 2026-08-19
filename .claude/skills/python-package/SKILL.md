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

## uv workspace wiring that bites

Two settings whose absence fails `uv sync` before any check runs:

- **The root is not a package.** It is a workspace container, so `[tool.uv] package = false`.
  Otherwise uv tries to build it, finds no `[build-system]`, and stops.
- **A member's dependency on another member needs its own source mapping.** In
  `packages/pricing-core/pyproject.toml`:
  ```toml
  dependencies = ["model-schema"]
  [tool.uv.sources]
  model-schema = { workspace = true }
  ```
  A root-level `[tool.uv.sources]` does **not** cover a member's dependencies — uv resolves
  `model-schema` from PyPI, where it does not exist.

- **`uv sync` alone installs almost nothing you need.** Because the root sets
  `package = false` and declares no dependency on any member, a plain `uv sync` gives you
  the dev tools and neither workspace package. The venv looks healthy; then mypy and pytest
  fail with `No module named 'pydantic'` on files that import it correctly, which reads
  like a broken install rather than an incomplete sync. Always:
  ```bash
  uv sync --all-packages --dev
  ```
  This is what `.github/workflows/python.yml` runs, which is why CI stayed green while the
  local gate reported ten mypy errors and four collection failures on the same commit.

## Getting `uv` itself

`uv` is not preinstalled and is not a Debian package here. If a session unpacked it into a
scratchpad directory, **that directory is ephemeral** — the binary vanishes and the next
session finds no `uv` at all. Put it somewhere durable:

```bash
cp <unpacked>/uv <unpacked>/uvx ~/.local/bin/ && chmod +x ~/.local/bin/uv*
```

`~/.profile` already prepends `~/.local/bin` when that directory exists, so a login shell
picks it up — but only from the next shell, so `export PATH="$HOME/.local/bin:$PATH"` for
the current one.

## Adding a dependency

Add it to the *package's* `pyproject.toml`, not the root. Then check it against
`.importlinter` — if `pricing-core` needs something the contract forbids, the answer is
almost always that the code belongs in `backend/`.

Every runtime dependency must be **Apache-2.0 compatible** (OQ-OVR-2 decided; NFR-OVR-11).
AGPL and SSPL are out, transitively.

**A wheel that installs is not a wheel that imports.** `uv sync` resolves and unpacks; it
says nothing about the shared libraries the extension modules need at load time. LightGBM's
Linux wheel links the OpenMP runtime and does not vendor it, so on a machine without
`libgomp1` the install succeeds and `import lightgbm` fails with

```
OSError: libgomp.so.1: cannot open shared object file: No such file or directory
```

XGBoost's wheel *does* vendor one, which makes this worse rather than better: the primary
backend works, the secondary does not, and a test suite that only exercised the primary
would report the pair healthy. Fixed with `sudo apt-get install -y libgomp1`, and declared
as a step in `.github/workflows/python.yml` rather than left to the runner image.

**A compiled dependency can `abort()` instead of raising.** LightGBM refuses a monotone
constraint on a feature it was told is categorical by calling `Fatal`, which on 4.7.0 kills
the interpreter:

```
[LightGBM] [Fatal] The output cannot be monotone with respect to categorical features
Fatal Python error: Aborted
```

`pytest.raises` cannot catch it and the worker simply dies, so the *first* thing to try with
an unexplained hard exit from a native library is the combination on its own, in a throwaway
script — the message is printed before the abort, and it is the only place it appears. XGBoost
accepts the same pair and silently grows a categorical split under a constraint that then does
not hold, which is the more dangerous half.

**After adding a compiled dependency, import it before writing anything against it.**
`uv run python -c "import <pkg>; print(<pkg>.__version__)"` costs a second and is the whole
check.

Watch the *coercion* a Pydantic field applies to values you pass through to a library.
`dict[str, float]` turned `max_depth: 5` into `5.0`, and both GBM backends reject a float
where they want an integer — a contract that silently retypes a caller's value fails at the
backend, one layer past where the mistake was made. `dict[str, int | float]` keeps it.

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

**A `computed_field` and `extra="forbid"` break the artifact's own round trip.** A computed
field **is** serialised, so `model_validate(x.model_dump(mode="json"))` hands the model a
key it has no field for, and `extra="forbid"` rejects it. Nothing warns; the first symptom
is a `ValidationError` from the *read* path of whatever persists the artifact, naming a
field the writer never set.

Three answers, and which to pick depends on whether the value belongs on the wire:

| | Use |
|---|---|
| Nothing outside the process needs it | a plain `@property` — `TransparencyArtifact.kinds` |
| A caller would otherwise reimplement the rule | `computed_field` **plus** a `model_validator(mode="before")` that drops the key — `Reconciliation.ratio` / `.status` |
| It is genuinely stored | an ordinary field, and accept that two statements of one fact can disagree |

Drop rather than compare in the second case. A stored or hand-edited value then has no way
to be believed, which is the guarantee "derived, not stored" exists for — and comparing
would turn a tampered row into a validation error at read time rather than a corrected one.

**`model_copy(update=...)` does not re-run validators.** It is a shallow copy with a dict
merge, not `model_validate`, so a cross-field `model_validator(mode="after")` never sees the
updated object. `GlmSpec._a_surrogate_says_so_in_both_places` (FR-MODEL-102) refuses a spec
where `approximates_model_id` is set without `response_column == SURROGATE_RESPONSE_COLUMN`,
or the reverse — an **iff** across two fields. Building a surrogate's spec by copying the
source GBM's spec and patching both fields with `model_copy(update={...})` would produce an
object that violates its own invariant and never notices, because the validator that would
have caught it only runs on construction or `model_validate`. `pricing_core.modelling.
transparency.approximation_spec()` builds the surrogate's `GlmSpec` through `GlmSpec(...)` —
an ordinary constructor call naming every field — for exactly this reason: a method, not a
copy, so the iff-validator runs. The rule generalises to any model with a cross-field
invariant: **`model_copy` is safe only for fields the invariant does not touch.**

## Typing

`mypy --strict` over `packages/`. Prefer `Protocol` over ABCs for injected collaborators —
`ProgressCallback` is defined in `pricing-core` and *implemented* by the backend, so the
dependency points inward and ADR-0001 holds while FR-PLAT-8/9 are still satisfied.

`from __future__ import annotations` at the top of every module.

## Style

Ruff, line length 100. Match the surrounding code. Comments explain *why* — the what is in
the spec, and a comment restating the code is noise that rots.

## Verified

2026-08-19 — W5, the GLM approximation as a Model. The `model_copy(update=...)` rule above,
found while writing `approximation_spec()`: an earlier draft built the surrogate's `GlmSpec`
by copying the GBM's spec and patching `approximates_model_id` and `response_column` with
`model_copy(update={...})`, which produced an object satisfying neither iff-branch of
`_a_surrogate_says_so_in_both_places` and raised nothing, because the validator never re-ran.
Rewritten as a plain constructor call.

2026-08-18 — W5, peril structures. The `computed_field` round-trip rule, found when
`load_structure` re-validated a stored `Reconciliation` and `extra="forbid"` rejected the
artifact's own `ratio` and `status`. The round-trip test that would have caught it is now
in `packages/model-schema/tests/test_perils.py`.

2026-08-17 — W5's `wf-01` journey slice: the LightGBM abort above, found when a monotone
constraint on a banded factor met `categorical_handling: "native"` for the first time. The
procedure that found it is the one written above — the pair alone, in a throwaway script.

2026-08-14 — re-verified on the rebuilt instance. Full gate green after
`uv sync --all-packages --dev`: ruff clean, mypy 7 files clean, import-linter 3 kept /
0 broken, 21 tests pass. The ADR-0001 contract was re-proven non-trivial by injecting
`import fastapi` into `pricing_core.money` (2 kept, 1 broken) and reverting.

2026-08-14 — W1. `MoneyMinor` strictness, `DecimalStr` schema pinning, and envelope
freezing are all covered by passing tests, including negative ones asserting a float is
refused and that the generated schema carries no `anyOf`. The `DecimalStr` rule exists
because research F7 measured the permissive union on a bare `Decimal`; without it the
contract would have admitted exactly what FR-OVR-7 forbids.

2026-08-17 — W5, the GBM arm. The `libgomp1` rule and the `int | float` coercion rule are
both from building `fit_gbm`: the first stopped `import lightgbm` outright on this machine,
the second failed inside both backends with two different error messages for one cause.
