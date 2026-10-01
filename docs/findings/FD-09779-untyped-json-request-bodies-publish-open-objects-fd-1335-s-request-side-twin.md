---
id: FD-9779
family: finding
title: Untyped JSON request bodies publish open objects, so the one-way contract cannot type them (FD-1335's request-side twin)
status: active
created: 2026-10-01
owner: auditor
tree: 446b55aa2d47fade85974b07eeb94046e62481dc
corrected_by: []
relates: [FD-1335, FD-1357, WK-1178, FR-451]
---

# FD-9779 — Untyped JSON request bodies publish open objects

## Finding

**Severity: medium (proposed by the auditor; the lead gives the verdict).** Reasoning: a contract gap, not a mispricing. Every route validates its body at run time (service-side), so no request is priced wrongly; but the generated client types each body as `{ [key: string]: unknown }`, so a caller must hand-write the shape, which `CLAUDE.md` §2 forbids ("a shape defined twice will diverge"). Same class and same severity as FD-1335, the response-side finding.

Ordered by the maintainer 2026-10-01; filed under working id 9779 (allocated by the lead). **Five** routes take `body: dict[str, Any]`, so the generated OpenAPI publishes `{"additionalProperties": true, "type": "object"}` as their JSON request body. Four of five have a shape already defined in `model-schema` (or named in the spec); the route does not reference it.

## Evidence

All at `origin/main` 65fc6129 (tree `446b55aa2d47fade85974b07eeb94046e62481dc`), in a worktree of that commit. Two differently built predicates; both give 5 and the same five routes.

### Predicate 1 (source): AST walk over `backend/src/app/api/*.py`

A function is a route when a decorator is `@<x>.get|put|post|delete|patch(...)`. It is flagged when a parameter annotation (positional or keyword-only) matches `\b(dict|Dict|Any|Mapping|MutableMapping|object)\b` and does not contain `BaseModel`, when a parameter is annotated exactly `Request`, or when the body calls `request.json()` or `request.body()`. Script (`ast.parse` per file, `ast.walk` per function) kept in the auditor's scratch as `src.py`; output, verbatim:

```text
POST '/rate-tables/{slug}/seed-from-model' rate_tables.py:118 ['body: dict[str, Any]']
POST '/rate-tables/{slug}@{version}/bulk-operation' rate_tables.py:154 ['body: dict[str, Any]']
POST '/rating-algorithms' rating_algorithms.py:34 ['body: dict[str, Any]']
POST '' sub_graphs.py:45 ['body: dict[str, Any]']
POST '/{slug}/versions' sub_graphs.py:60 ['body: dict[str, Any]']
(+ 6 'Request param' hits: datasets.py:756, health.py:142, jobs.py:259, settings.py:63, :78, validation.py:267)
COUNT 11
```

The six `Request` hits are false positives of the predicate's own breadth: each handler takes `request: Request` for `request.app.state` or the trace context, and `grep -nE "\.json\(\)|\.body\(\)|\.stream\(\)|add_api_route|api_route\(|Body\(" backend/src/app/api/*.py` returns **no hit**, so no handler reads a raw body; their bodies are typed (`SchemaCorrection`, `UpdateSettings`, `RuleCreate`). **Source count after that triage: 5.**

### Predicate 2 (contract): `docs/contracts/openapi/generated.json`

For each path, each HTTP method with a `requestBody`, each media type containing `json`: **open** when the schema is `{}`/absent, or `"type": "object"` with no `properties` and none of `$ref`, `allOf`, `anyOf`, `oneOf` (this includes additionalProperties-only). Script kept as `contract.py`; output, verbatim:

```text
POST /api/v1/rate-tables/{slug}/seed-from-model application/json {"additionalProperties": true, "title": "Body", "type": "object"}
POST /api/v1/rate-tables/{slug}@{version}/bulk-operation application/json {"additionalProperties": true, "title": "Body", "type": "object"}
POST /api/v1/rating-algorithms application/json {"additionalProperties": true, "title": "Body", "type": "object"}
POST /api/v1/sub-graphs application/json {"additionalProperties": true, "title": "Body", "type": "object"}
POST /api/v1/sub-graphs/{slug}/versions application/json {"additionalProperties": true, "title": "Body", "type": "object"}
COUNT 5
```

### Reconciliation

| Method, path | Handler | Source | Contract | Body shape that exists |
|---|---|---|---|---|
| POST `/rate-tables/{slug}/seed-from-model` | `rate_tables.py:118` (`_seed_body`, :57) | yes | yes | none: `03` §4.2 body `{model_ref, change_note}` is validated by hand in `_seed_body` |
| POST `/rate-tables/{slug}@{version}/bulk-operation` | `rate_tables.py:154` | yes | yes | `BulkOperationBase` (`rating.py:745`) |
| POST `/rating-algorithms` | `rating_algorithms.py:34` | yes | yes | `RatingAlgorithm` (`rating.py:374`) |
| POST `/sub-graphs` | `sub_graphs.py:45` | yes | yes | `SubGraphCreate` (`sub_graphs.py:155`) |
| POST `/sub-graphs/{slug}/versions` | `sub_graphs.py:60` | yes | yes | `SubGraphBody` (`sub_graphs.py:40`) |

**In one list, not the other: none.** The source predicate's six extra raw hits are the `Request`-param false positives above. Contract-side, two more request bodies are not JSON and are outside the predicate by design: `POST /rate-tables/{slug}@{version}/import` and `POST /sources/{source_id}/preview` (`multipart/form-data`). The generated routes' *responses* are FD-1335's. Not swept: open objects **nested inside** a typed body (e.g. `UpdateSettings.values`); that is a different, narrower question.

### Limits of the two instruments

Both predicates see only handler signatures / published schemas. A route whose body is typed by a model that itself is an empty `BaseModel` would pass the source predicate and fail neither (it has `$ref`): neither instrument catches that. Not found by either, so not claimed absent.

## Disposition

**Proposed (the lead's verdict):** *fix before close with an owner: WK-1178*, extend FD-1335's guard to request bodies. Part A: give each of the five routes a typed body (the four shapes above exist; `seed-from-model` needs a new `model-schema` request model for `{model_ref, change_note}`, which FD-1357's fix-plan touches the same route for, so land them together), regenerate `docs/contracts/`. Part B: the contract guard fails on a JSON `requestBody` that is `{}` or an open object, shown red on broken input before it is written (`CLAUDE.md` §13), with no exclusion for the multipart routes (they are not JSON). **Event:** the guard lands in the same PR as FD-1335's Part B, or the finding does not close.
