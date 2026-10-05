---
id: FD-1335
family: finding
title: The /api/v1/score 200 response has no schema in the generated OpenAPI, so the one-way contract cannot type it
status: active
created: 2026-09-30
owner: auditor
tree: 8d5c67a56c27a9dcbba8d4e4ad28a1895e1dd862
corrected_by: []
relates: [WK-671, WK-672, WK-675, WK-1178, FR-250, FR-262, FR-451, NFR-502]
---

# FD-1335 — The `/api/v1/score` 200 response has no schema in the generated OpenAPI

## Finding

**Severity: medium.** Proposed by the auditor, and **accepted MEDIUM, 2026-09-30, by the maintainer (by delegation)** in `~/gi-pricing-plan.local/channel/to-lead.md`, a local channel file outside the repository, entry "2026-09-30 17:13:45 BST — FD 9969 severity LOW CONFIRMED; FD 9971 (/score untyped) MEDIUM accepted, with timing and a regression guard" (its FD 9971 clauses are quoted in the Disposition below).
Filed 2026-09-30 under working id 9971; minted as FD-1335. **Working ids in the maintainer's entry headers quoted below are as
written then:** FD 9971 is this record, and FD 9969 is FD-1333.

**Scope, as the maintainer states it** (entry "2026-09-30 17:24:46 BST — FD 9971: FOLD the 12 open-object 2xx responses in, in
two parts, so /score isn't delayed", `to-lead.md`): **"`{}` or a JSON object with no properties"**. The sweep below finds **6 + 12
= 18** such 2xx responses in the generated OpenAPI: 6 whose schema is `{}` (two are the `/score` bodies this record began with,
four are streams and files) and 12 that are objects with no `properties`. Same defect in practice: no usable shape, so a
hand-written one is invited. Same fix: a response model on the route.

`CLAUDE.md` §2 says one contract joins backend and frontend and that it flows one way:
`model-schema` generates `docs/contracts/`, which generates `frontend/src/api/generated`, and
*"Nobody hand-writes a shape that already exists in `model-schema`"*. At `origin/main`
`8d5c67a56c27a9dcbba8d4e4ad28a1895e1dd862` the generated OpenAPI describes the 200 response of
`POST /api/v1/score`, the platform's real-time scoring endpoint (FR-250), with the **empty
schema `{}`**. The generated client therefore types that body as `unknown`, and a consumer that
needs to read a premium has no generated type to read it with. The shape exists, as
`ScoringResult` in `packages/model-schema/src/model_schema/scoring.py:171`, and the route does
not reference it. `POST /api/v1/score/compare` (FR-262) has the same gap for `ScoreComparison`
(`scoring.py:249`).

Nothing is priced wrongly, and no request misbehaves. The gap is in the **contract**: the one
mechanism that keeps a backend shape and a frontend shape from diverging has no shape to carry
for the endpoint whose output is a premium. A consumer's only way forward is the hand-written
type that §2 forbids, and `CLAUDE.md` §2 says why: "a diverged shape is a mispricing."

**Not a defect in the route's behaviour.** The route omits a response model on purpose
(`NFR-502`, below). The finding is that the omission also removed the documentation.

## Evidence

All of it at `origin/main` `8d5c67a56c27a9dcbba8d4e4ad28a1895e1dd862`, in a worktree of that
commit after `uv sync --all-packages`. `uv run python scripts/generate-contracts.py --check`
exits 0 there ("31 generated contracts match the models"), so the committed
`docs/contracts/openapi/generated.json` is what the models generate.

### 1. The sweep: every 2xx response whose schema is `{}` or an object with no `properties`

**Predicate, verbatim.** For each path, each HTTP method, each response whose status key starts with `2`, each media type under
its `content`, the response is **untyped** when its schema is either:
- **form 1:** `{}` (an empty mapping; an absent `schema` key counts as empty); or
- **form 2:** `"type": "object"` with **no `properties` key and none of `$ref`, `allOf`, `anyOf` or `oneOf`**
  (the generated client gets `{ [key: string]: unknown }`).

A 2xx response with no `content` at all (a 204) is reported apart and counted in neither. The whole script is the fenced block
below. **Bytes hashed:** exactly the text between the opening and closing fences, 2313 bytes including its final newline;
sha256 prefix `4574b64f1293849b`.

```python
import json, sys

HTTP_METHODS = ("get", "put", "post", "delete", "options", "head", "patch", "trace")


def _json_2xx_schemas(doc):
    """Yield (METHOD, path, status, media, schema) for every 2xx response media type; a 2xx
    response with no content at all (a 204) is yielded as media None, schema None."""
    for path, item in doc["paths"].items():
        for method in HTTP_METHODS:
            op = item.get(method)
            if op is None:
                continue
            for status, resp in op.get("responses", {}).items():
                if not str(status).startswith("2"):
                    continue
                content = resp.get("content")
                if not content:
                    yield method.upper(), path, status, None, None
                    continue
                for media, body in content.items():
                    yield method.upper(), path, status, media, body.get("schema", {})


def is_empty(schema):
    """Form 1: the schema is `{}`."""
    return schema == {}


def is_open_object(schema):
    """Form 2: a JSON object with no `properties`, and no `$ref`, `allOf`, `anyOf` or `oneOf`."""
    return (isinstance(schema, dict) and schema.get("type") == "object" and "properties" not in schema
            and not any(k in schema for k in ("$ref", "allOf", "anyOf", "oneOf")))


def sweep(doc):
    empty, open_obj, no_content, total = [], [], [], 0
    for method, path, status, media, schema in _json_2xx_schemas(doc):
        total += 1
        if media is None:
            no_content.append((method, path, status))
        elif is_empty(schema):
            empty.append((method, path, status, media))
        elif is_open_object(schema):
            open_obj.append((method, path, status, media))
    return total, empty, open_obj, no_content


if __name__ == "__main__":
    doc = json.load(open(sys.argv[1]))
    total, empty, open_obj, no_content = sweep(doc)
    print(f"paths={len(doc['paths'])} responses_2xx={total}")
    print(f"form1_empty_schema={len(empty)}")
    for h in sorted(empty):
        print("  ", *h)
    print(f"form2_object_without_properties={len(open_obj)}")
    for h in sorted(open_obj):
        print("  ", *h)
    print(f"2xx_without_content={len(no_content)}")
    print(f"total_untyped={len(empty) + len(open_obj)}")
```

**Command, verbatim**, from the repository root: `python3 sweep_untyped_2xx.py docs/contracts/openapi/generated.json`.
The document's own sha256 prefix is `26684eab9510cc6c`. Output, verbatim:

```text
paths=117 responses_2xx=137
form1_empty_schema=6
   GET /api/v1/audit/export 200 application/json
   GET /api/v1/jobs/{job_id}/events 200 application/json
   GET /api/v1/rate-tables/{slug}@{version}/export/csv 200 application/json
   GET /api/v1/rate-tables/{slug}@{version}/export/xlsx 200 application/json
   POST /api/v1/score 200 application/json
   POST /api/v1/score/compare 200 application/json
form2_object_without_properties=12
   GET /api/v1/approval-requests/{request_id} 200 application/json
   GET /api/v1/dataset-versions/{version_id}/rejected 200 application/json
   GET /api/v1/rating-algorithms/{slug}@{version}/diff 200 application/json
   POST /api/v1/approval-requests 201 application/json
   POST /api/v1/approval-requests/{request_id}/decide 200 application/json
   POST /api/v1/approval-requests/{request_id}/withdraw 200 application/json
   POST /api/v1/rate-tables/{slug}/seed-from-model 201 application/json
   POST /api/v1/rate-tables/{slug}@{version}/bulk-operation 201 application/json
   POST /api/v1/rate-tables/{slug}@{version}/import 200 application/json
   POST /api/v1/rating-algorithms 201 application/json
   POST /api/v1/sources/{source_id}/preview 200 application/json
   POST /api/v1/validation-reports/{report_id}/results/{rule_id}/acknowledge 201 application/json
2xx_without_content=0
total_untyped=18
```

**Count: 6 + 12 = 18 untyped 2xx responses, of 137 over 117 paths.**

- **Form 1, 6 responses.** Two are **JSON bodies whose shape already exists in `model-schema`**: `POST /api/v1/score` and
  `POST /api/v1/score/compare`. The other four return a **stream or a file**, so there is no JSON shape to type:
  `GET /audit/export` returns `StreamingResponse` as `application/x-ndjson` or `text/csv`
  (`backend/src/app/api/audit.py:278-281`, `:306-309`); `GET /jobs/{job_id}/events` returns `text/event-stream`
  (`backend/src/app/api/jobs.py:308-310`); the two rate-table exports return `text/csv` and the `spreadsheetml` type
  (`backend/src/app/api/rate_tables.py:213`, `:235-236`). Those four carry the same `{}` and are a **different case** (the
  OpenAPI names `application/json` for a body that is not JSON), handled as a LOW sub-item (Disposition, Part A exclusions).
- **Form 2, 12 responses**, all with `additionalProperties: true`, listed above by method, path and status. Measured in the
  generated client after `pnpm --dir frontend generate:api`: `create_rating_algorithm_api_v1_rating_algorithms_post` 201 is
  `"application/json": { [key: string]: unknown; }`.

**Controls**, run against the same document with the predicates above (`controls`, the same import of the script):

```text
real document:                                                  form1=6 form2=12
negative control, /score/batch 202 ($ref Job), flagged in either form: False
planted form 1, /score/batch 202 blanked to {}:                 form1=7 form2=12; flagged=True
planted form 2, /score/batch 202 an open object:                form1=6 form2=13; flagged=True
negative form 2, /score/batch 202 an object WITH properties:    form1=6 form2=12; flagged=False
fix control, /rating-algorithms 201 given a $ref:               form1=6 form2=11; flagged=False
fix control, /score 200 given a $ref:                           form1=5 form2=12
```

The positive controls are the finding itself (`/score` is form 1, the twelve are form 2) and a typed route made untyped in each
form (`/score/batch` blanked, then made an open object: both flagged). The negative controls are the typed `/score/batch` 202 (a
`$ref` to `Job`, flagged in neither form) and an object **with** `properties` (not flagged in form 2). The fix controls give
`/score` and then `/rating-algorithms` a `$ref` and the count falls.

### 2. Why the route does not reference `ScoringResult`

The route is declared with **no response model and no return annotation, on purpose**.
`backend/src/app/api/score.py:276-295` (the decorator, the `def` and its return annotation; the middle lines elided):

```python
@router.post(
    "/score",
    summary="Score one Quote Context against an explicit Rating Version",
    status_code=200,
    ...
    responses=problems(401, 403, 404, 409, 422),
)
async def score(
    ctx: QuoteContext,
    ...
) -> Response:
```

and it returns a raw `Response` (`score.py:321`, `return Response(content=result.model_dump_json(),
media_type="application/json")`). The module docstring gives the reason
(`score.py:21-26`): **"No `response_model=`, and no Pydantic return annotation** (NFR-502 as
amended by RL-883). The requirement is *validate inbound, never outbound* … `ScoringResult` is
built by `pricing-core` and is already trusted, so it is serialised with Pydantic v2's compiled
encoder and returned in a raw `Response`." `NFR-502` (`docs/specs/03-rating-engine.md:1163`)
says the endpoint "does **not** apply `response_model` validation to its response". `/score/compare`
does the same (`score.py:330-342`, and `return Response(content=comparison.model_dump_json(), …)` at `:376`, where `comparison` is a `ScoreComparison`, `:371`).

FastAPI builds a route's documented response from `response_model` or the return annotation. A
route that has neither documents nothing for its 200, which is the `{}` measured above.
`scripts/generate-contracts.py` adds nothing to it: `build_openapi()` (`:163-175`) builds the
app with fixed settings and returns `app.openapi()` unchanged, so the document is exactly what
FastAPI documents. Nothing else in the repository declares the shape for the route. `ScoringResult`
is defined once in `packages/model-schema/src/model_schema/scoring.py:171`. It appears in
`docs/contracts/schemas/scoring.schema.json` (`$defs`, authored) and in
`docs/contracts/schemas/generated/score-comparison.schema.json` (`$defs`, generated). It appears
**0 times** in the generated client (`grep -c ScoringResult frontend/src/api/generated/schema.d.ts`
prints `0`, after `pnpm --dir frontend install --frozen-lockfile && pnpm --dir frontend generate:api`).
The authored `scoring.schema.json:54` has `"outputs": {"type": "object"}`, which is an open
object, so the `outputs` field is untyped inside the shape too. **That is a second, smaller point,
and this record does not claim it as a defect**: the ladder's output names are the rating
algorithm's, so an open object may be right.

**The two requirements do not conflict.** A route can document a body without validating it.
Measured in a scratch app with the repository's FastAPI:

```python
@app.post("/s", status_code=200, responses={200: {"model": ScoringResult}})
async def s() -> Response:
    return Response(content='{"not":"a ScoringResult"}', media_type="application/json")
```

`app.openapi()` gives the 200 schema `{'$ref': '#/components/schemas/ScoringResult'}`, and a
request returns `200 {"not":"a ScoringResult"}`. So `responses={200: {"model": …}}` types the
contract and runs **no outbound validation**, which is what `NFR-502` requires. This is the fix
direction, offered as evidence and not as a decision (below).

### 3. Who owns the route

The route table is `03` §5.1: `POST /api/v1/score` (FR-250), `POST /api/v1/score/batch` (FR-253)
and `POST /api/v1/score/compare` (FR-262) at `docs/specs/03-rating-engine.md:758-760`. By
construction:
- `/score` and `/score/batch` are **WK-671's** (`docs/roadmap.md` `### WK-671`, "Scoring:
  real-time, batch, trace, one shared evaluator"; `score.py:1` names "WK-671 Task 2B"). WK-671
  is `status: closed`.
- `/score/compare` is **WK-672's** (`docs/roadmap.md`: "the Quote Sandbox's backend is WK-672's
  … `POST /api/v1/score/compare`, which WK-672 builds and tests"). WK-672 is `status: closed`.
- The **consumer** is WK-675's Quote Sandbox and ladder waterfall (`### WK-675`, "Frontend: DAG
  designer, rate table editor, quote sandbox + ladder waterfall, dislocation views"; the
  roadmap says "the quote sandbox view in this Work consumes `POST /api/v1/score/compare`").
  WK-675 is `status: active`.

Both owning Works are closed, so a fix cannot be carried by its owner. **WK-1178**, P2 standing
maintenance ("hotfixes, dependency bumps and security findings", `status: active`), is the
active Work that carries fix slices to code whose Work is closed (for example SL-1300, the
`compile_bundle` pin-membership fix). That is the auditor's proposal for the carrying Work, and
the maintainer decides it.

### 4. The frontend has no hand-written `/score` type today

`git grep -n -i -E "api/v1/score|/score\b|ScoringResult|ScoreComparison|premium_ladder|payable_premium|decline_reasons|bundle_hash" -- frontend/src ':!frontend/src/api/generated'`
prints **3 lines, none a type**: `frontend/src/views/__tests__/PredictionView.test.ts:101`, `:135`
and `:152`, each `screen.getByRole("button", { name: /score/i })`, a UI button label in a test
of the model prediction view. There is **no hand-written response type for `/score`** in
`frontend/`. The gap is therefore latent: nothing has diverged yet. It becomes live when WK-675
builds the Quote Sandbox, which consumes exactly these two responses, and finds `unknown` where a
premium ladder should be.

The generated client for the same routes, measured after `pnpm --dir frontend generate:api`
(`frontend/src/api/generated/schema.d.ts`, VCS-ignored):
- `score_api_v1_score_post` 200: `"application/json": unknown;`
- `score_compare_api_v1_score_compare_post` 200: `"application/json": unknown;`
- `score_batch_api_v1_score_batch_post` 202 (the typed control): `"application/json": components["schemas"]["Job"];`

## Disposition

**Accepted MEDIUM, 2026-09-30, by the maintainer (by delegation),** in the entry "2026-09-30 17:13:45 BST — FD 9969 severity
LOW CONFIRMED; FD 9971 (/score untyped) MEDIUM accepted, with timing and a regression guard" (`to-lead.md`, a local channel
file outside the repository, so it is cited by its header and its operative content is stated here). **Carrier: WK-1178.**
**carry forward with an owner.** The decision on the register row is the lead's.

**The maintainer's reason, and the auditor's.** The entry: "A missing contract for the premium endpoint, with WK-675 about
to consume it, is exactly the gap the one-way contract (CLAUDE.md §2) exists to prevent." The auditor's proposed reasoning,
kept: not low, because the gap is in the contract for the endpoint that returns the premium and the consumer that will trip
over it is already scheduled (WK-675); not high, because nothing is wrong at runtime, the frontend holds no hand-written
shape today (measured, above), and the fix is a small change to two route declarations. It would rise if a hand-written
`/score` type were found in a consumer or a copy elsewhere.

**The conditions and the fix, as the maintainer states them** (entries "2026-09-30 17:13:45 BST", above, and
"2026-09-30 17:24:46 BST — FD 9971: FOLD the 12 open-object 2xx responses in, in two parts, so /score isn't delayed"), with what
each needs. **The fix is split so the WK-675 hold stays narrow.**

**Part A: blocks the WK-675 `/score` slice.**

1. **Timing, which is the point of the severity.** Part A lands **before WK-675 dispatches any slice that consumes `/score` or
   `/score/compare`.** Carrier WK-1178. The dependency **is to be recorded** in `PL-1286`'s (WK-675's map plan) next dispatch
   record, which does not exist yet (that plan is frozen, so the record is a dispatch record, not an edit), and the lead holds
   that WK-675 dispatch on it.
2. **The two response models.** `responses={200: {"model": ScoringResult}}` on `/score` and
   `responses={200: {"model": ScoreComparison}}` on `/score/compare`, keeping the raw `Response` and the absence of
   `response_model`, so the `$ref` is documented and **no outbound validation runs** (`NFR-502`). Regenerate the contracts
   (`FR-451`). **Evidence required: `NFR-502` is re-read after the change, not assumed unchanged.** Its own figure is the one to
   re-check: the amended text cites p99 0.070 ms, 0.14 % of the 50 ms budget, from `docs/research/w8-spike-resolution.md`.
   The slice measures again with the route as changed and quotes the result.
3. **The guard, in the same fix, over BOTH forms now, each proven red first** (`CLAUDE.md` §13). A contract check that fails
   when a JSON 2xx response is form 1 (`{}`) or form 2 (an object with no `properties`), using the predicates in Evidence §1.
   Each form is shown red on broken input before the guard is written, and the two `{}` `/score` responses are form 1's red on
   the real document. **New instances fail from day one.** Its exclusion list has two parts:
   - **permanent, cited: the four stream and file routes** (the list below, with the lines that make each a non-JSON body);
   - **temporary, each carrying the exclusion marker `pending FD-1335 part B`** (the maintainer's entry wrote it as "pending FD 9971 part B";
     it carries the minted id): **the 12 open-object routes** listed in Evidence §1.

   The four permanent exclusions, by method and path:
   - `GET /api/v1/audit/export`: `StreamingResponse`, `application/x-ndjson` or `text/csv` (`backend/src/app/api/audit.py:278-281`,
     `:306-309`);
   - `GET /api/v1/jobs/{job_id}/events`: `text/event-stream` (`backend/src/app/api/jobs.py:308-310`);
   - `GET /api/v1/rate-tables/{slug}@{version}/export/csv`: `text/csv` (`backend/src/app/api/rate_tables.py:213`);
   - `GET /api/v1/rate-tables/{slug}@{version}/export/xlsx`: the `spreadsheetml` type (`backend/src/app/api/rate_tables.py:235-236`).

   **Proof, red first:** on the real document the guard fails on `/score` and `/score/compare` before Part A and passes after,
   and it fails on a planted form-2 route not on the list.

**Part B: carrier WK-1178.**

4. **The 12 routes get response models**, and each is removed from the temporary exclusion list as it is fixed. **The FD closes
   when the temporary list is empty.**
5. **The hold is per route.** Any of the 12 that a WK-675 slice consumes (for example `POST /rating-algorithms` for the
   designer, or the approval-request routes) is fixed **before that slice dispatches.** The lead checks this at each `PL-1286`
   dispatch record.

**A separate LOW sub-item in the same finding: document the four stream and file routes' media types** rather than leaving
`{}`. Same carrier, and **it does not block WK-675.** The maintainer's entry "2026-09-30 17:18:21 BST — FD 9971 media types: the
author's reading is CONFIRMED" says the media types in his 17:13:45 entry were illustrative, that the sub-item **documents what
each route's code already declares** and changes no route's behaviour, and that if a route declares nothing the FD notes it
rather than choosing a type. What the code declares, each set on the response the route returns (none is set at the route
decorator, which is why the OpenAPI shows `application/json`):
- `GET /api/v1/audit/export`: `application/x-ndjson` (`backend/src/app/api/audit.py:280`) or `text/csv` (`:308`);
- `GET /api/v1/jobs/{job_id}/events`: `text/event-stream` (`backend/src/app/api/jobs.py:310`);
- `GET /api/v1/rate-tables/{slug}@{version}/export/csv`: `text/csv` (`backend/src/app/api/rate_tables.py:213`);
- `GET /api/v1/rate-tables/{slug}@{version}/export/xlsx`:
  `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` (`backend/src/app/api/rate_tables.py:235-236`).

**None of the four declares nothing**, so the slice picks no type. It documents these.

**Event.** Part A merges (the two response declarations, the regenerated contracts, `NFR-502` re-measured, and the guard proven
red on both forms) before WK-675 dispatches a slice that consumes `/score` or `/score/compare`. Part B follows, route by route
(each of the 12 before any WK-675 slice that consumes it), and **the finding closes when the guard's temporary exclusion list is
empty.** The LOW sub-item follows in Part A or later and gates nothing. Ownership shape: event.

*Disclosure: this record was filed under working id 9971 and minted as FD-1335 at its merge turn. The number 9971 was earlier the working id of a ruling that has since been minted under its own id; this record is unrelated to it.*
