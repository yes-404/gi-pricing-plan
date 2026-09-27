---
id: RL-883
family: ruling
title: F1: `NFR-502` is amended to the property it was always about; `orjson` is not added
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-08-29
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-08-29-w11-slices-2-4-rulings.md
---

## RL-883 — F1: `NFR-502` is amended to the property it was always about; `orjson` is not added

**The decision, restated.** NFR-502 (`03:797`) requires the scoring endpoint to skip
`response_model` validation and serialise *"directly with a C-speed encoder
(`ORJSONResponse`)"*, and its 2026-08-27 amendment closes *"The design rule is unchanged:
validate inbound, never outbound; encode with `ORJSONResponse`."* `orjson` is not a dependency:
`grep -c orjson uv.lock` returns **0**, and no `.toml` in the tree names it. F1 asks whether the
requirement is satisfied by adding `orjson`, by a different encoder, or by re-reading it.

**Ruled: by amending it to state the property, and satisfying that property with the compiled
serialiser Pydantic v2 already ships. `orjson` is not added, so no `docs/skills-map.md` row and
no `03` §8 row is owed for a dependency — but the skills-map row that quotes the retired clause
is corrected in this commit.**

Four findings, all measured this session against
`/home/puzhenhao1989/gi-pricing-plan/.venv` (FastAPI **0.141.1**, Starlette 1.6.0,
pydantic-core **2.46.4**) rather than reasoned about:

1. **`ORJSONResponse` is deprecated in the pinned FastAPI**, and the deprecation names its
   replacement: *"ORJSONResponse is deprecated, FastAPI now serializes data directly to JSON
   bytes via Pydantic when a return type or response model is set, which is faster and doesn't
   need a custom response class"* (`fastapi/responses.py:69-77`, `FastAPIDeprecationWarning`).
   The requirement names a class the framework has retired.
2. **That replacement is precisely what NFR-502's first sentence forbids.** Probed with
   three routes over the same payload: a route annotated `-> Out` returning a shape that
   violates `Out` gives **500**; the identical return from an unannotated route gives **200**;
   and an annotated route returning a valid model plus an extra key emits `{"n":7}` — the extra
   key filtered out. The "modern path" validates and filters outbound. So the deprecation notice
   offers this endpoint nothing: taking its advice would reintroduce the outbound validation the
   requirement exists to remove.
3. **A missing `orjson` fails at render, not at import** — the question the readiness document
   declined to assert. `from fastapi.responses import ORJSONResponse` succeeds; constructing one
   and rendering raises `AssertionError: orjson must be installed to use ORJSONResponse`
   (`fastapi/responses.py:95`). An `orjson`-based route that ever lost its dependency would boot
   clean and 500 on the first quote. That is the expensive discovery mode, and it is the one on
   offer.
4. **The property is already available with no new dependency.**
   `Response(content=result.model_dump_json(), media_type="application/json")` returns the exact
   bytes with no outbound validation — probed: `200`, `application/json`, `{"n":7,"label":"x"}`.
   And `model_dump_json` **serialises without validating**: given a `model_construct`-built
   instance holding a `str` where an `int` is declared, it emits `{"n":"not-an-int","label":3}`
   verbatim and only warns. The serialiser is pydantic-core 2.46.4 — compiled, and already a
   hard dependency of everything here. Precedent for the shape exists:
   `backend/src/app/api/rate_tables.py:213` returns a raw `Response`, and `model_dump_json()` is
   used at four sites including `platform/diff_cache.py:105`.

**Measured, with its limit stated.** `model_dump_json()` over a `ScoringResult`-shaped model
(20 ladder rungs, 60 outputs, refs and hash) ran at **0.0168 ms/call over 20 000 calls** on the
shared verification machine — 0.034 % of NFR-489's 50 ms budget. **That figure is
serialise-only, over an already-constructed model, in a tight loop, and is not a request-path
measurement.** It is also **not** a comparison against `orjson`, which cannot be installed in
this environment. It establishes that the compiled path is not a cost problem; it does not
establish that it beats `orjson`, and this ruling does not claim it does. The argument against
`orjson` is the deprecated class and the render-time failure, not speed.

**One thing checked and found not to help, so it is not offered as a reason:** the deprecation
is **not** gate-visible today. There is no `filterwarnings = ["error"]` in any `pyproject.toml`,
so using the deprecated class would not turn a test red. Which is the argument for deciding it
now rather than at the FastAPI upgrade that removes it.

### Disposition

- Spec change in this commit: NFR-502 gains a dated amendment restating the design rule as
  *validate inbound, never outbound; serialise the trusted result directly with a compiled
  encoder*, recording that `ORJSONResponse` was named when it was the way to get one, that it is
  deprecated in the pinned FastAPI, and that the framework's stated replacement is outbound
  validation — which this requirement forbids.
- [`../skills-map.md`](../skills-map.md)'s low-latency-serving row quotes the retired clause
  verbatim and is corrected in the same commit, per `CLAUDE.md` §10.
- **No tech-dependency change**, so no `03` §8 row is owed. F1's documentation obligation
  dissolves rather than being discharged.

**Acceptance test — the violation that must become expressible.** A `ScoringResult` whose
contents violate its own declared types must be returned by the scoring endpoint **verbatim**,
not 500. That assertion is impossible under the annotated/`response_model` path — probe 2 above
returns 500 — and passes under a raw `Response`, so the test discriminates the two
implementations rather than merely observing a green endpoint. **The ruling is overridden** if
`orjson` appears in any `pyproject.toml` or in `uv.lock`, or if the scoring route declares a
`response_model=` or a Pydantic-model return annotation.

---
