---
id: FD-1509
family: finding
title: A local class that reuses a published name passes the OpenAPI half of the deployment route-types test
status: active
created: 2026-10-08            # original date 2026-10-05, set at the draft; minted 2026-10-08
owner: auditor
tree: 47d770e8fcbd2410fa101019ed8cf3aae69a1baa
corrected_by: []
relates: [WK-1178, WK-674, PL-1392, SL-1256, LG-1405, FR-428, FD-1335]
---

# FD-1509 — the OpenAPI half of the route-types test compares names, so a same-named local class passes it

**Filed** by auditor-fdc1 on 2026-10-05, from item (3) of `audit-sl1256-2026-10-04.md` and the lead's
routing in `to-lead.md` ("(e3) goes to the next FD batch, owner WK-1178, severity mine at filing"). `tree:` is
`origin/main` = `47d770e8fcbd2410fa101019ed8cf3aae69a1baa`, the tree every figure below was measured on. The id
is a working id until the lead mints it.

*Re-checked 2026-10-05 at main `caa4e411a9c07a389cf47092a923c7761b2b92dc`: `test_deployment_route_types.py` and
`backend/src/app/api/environments.py` are byte-identical to `47d770e8` (`git diff --stat 47d770e8 origin/main` on
both prints nothing), so every line cite below resolves unchanged, and the test still has no `__module__` check.
PL-1392 Acceptance 14 is still at `:508` and LG-1405's run B at `:337-338` of its file.*

**Severity: LOW (the maintainer's (by delegation), `to-lead.md` "2026-10-05 09:44:39 BST — DISPATCH GO: FD-1356 fix …"; the reason corrected in "2026-10-05 09:54:07 BST — FD 9720 NOT filed …", quoted under "Severity (the maintainer's (by delegation))").**

## Finding

`backend/tests/test_deployment_route_types.py` guards PL-1392 Acceptance 14 and 15: every request body and every
2xx of the Environment and Deployment routes is a `model-schema` type. It has two halves. The **AST half**
(`ast_problems`, `:226-270`) reads the handler's source and checks that the `body` annotation is a name imported
from `model_schema`. The **OpenAPI half** (`openapi_problems`, `:109-165`) reads the generated document and
checks that the request body is exactly `{"$ref": "#/components/schemas/<Name>"}` for the table's name, and that
`<Name>` is in `GENERATED_SHAPES`.

The OpenAPI half identifies a type **by its name**. A Pydantic class defined in the API module, with the same
name as the published one and any fields at all, gets the same component name and so the same `$ref`. The half
passes. **When the AST half cannot see the class, nothing else in this file can.**

The ledger of SL-1256 already recorded the observation: `docs/ledgers/LG-01405-wk-674-slice-2-the-environment-and-deployment-record.md`
(broken-input run **B**, near line 337): "the OpenAPI tests still passed, because the class has the same name and
so the same `$ref`: **the plan's prediction that the OpenAPI half also fails does not hold when the local class
reuses the published name**; only the AST half catches it (1 failed, 2 passed)". The slice audit routed it as
"(3) … Non-blocking fix. Either accept with that reason, or harden the test". This essay is the "file an FD"
branch of that routing.

## Requirement

`docs/plans/PL-01392-wk-674-slice-2-the-environment-and-deployment-record-superseding-pl-1306-leaf-plan.md`,
Acceptance 14 (`:508-`), the red-first clause, verbatim: "with the body class defined in the API module as a
local `BaseModel` subclass, the AST assert fails naming it, **and the OpenAPI assert fails because the name is
not a published shape**." The OpenAPI half does not fail when the local class reuses a published name, so the
plan's stated behaviour of the guard is false for that case, and the test file's own header
(`test_deployment_route_types.py:1-9`) says the two halves fail "**separately**".

The rule behind it is `CLAUDE.md` §2: "**Nobody hand-writes a shape that already exists in `model-schema`** —
not the backend, not the frontend, not a test fixture. A shape defined twice will diverge, and in a pricing
platform a diverged shape is a mispricing."

## Evidence

Run on 2026-10-05 in the clean worktree `.claude/worktrees/fd-9723` at `47d770e8`, with the repository venv. No
test was run through pytest; the test module was loaded as a library and its two checkers called. The probe is a
scratch file outside the repository and is not committed.

### 1. OpenAPI half, a local same-named class with a different shape

A minimal app whose `POST /api/v1/environments` takes a **local** `EnvironmentCreate(BaseModel)` with the one
field `anything: str` (the published class has `slug`, `name` and more) and returns a local `Environment`. The
checker is called with the Route table's own row for that route (`ROWS[1]`):

```
local schema : dict_keys(['anything'])
openapi_problems: []
```

The document's `EnvironmentCreate` component has the wrong shape, and the checker reports no problem.

### 2. AST half on the real `environments.py`, two variants

`ast_problems` over the real source with a local class appended, row `ROWS[1]` only:

```
ast, import removed: ['POST /api/v1/environments: environments.py body EnvironmentCreate is not imported from model_schema (a class the API module defines is a second copy of a shape)']
ast, import kept (shadowed): []
```

- **Import removed** is the case the existing test `test_a_body_class_defined_in_the_api_module_is_refused`
  (`:359-360`) covers. The AST half catches it.
- **Import kept** — the module still has `from model_schema import … EnvironmentCreate …` (`environments.py:27`)
  **and** defines `class EnvironmentCreate(BaseModel)` — passes the AST half too. `_imported_from_model_schema`
  (`:193-201`) collects every imported name from the module's top-level `ImportFrom` nodes and never looks for a
  later definition of the same name. So both halves can be satisfied by a shadowing class.
- The repository's ruff selection (`pyproject.toml:83`, which includes `F`) flags the kept-import variant:
  `ruff check --select F811` on the scratch file prints "F811 Redefinition of unused `EnvironmentCreate` from line
  28". So the second variant is stopped by the lint stage of the gate, not by this test. That is a different
  layer, and I did not establish that it fires in every arrangement of the code (for example when the name is
  used before the redefinition).

### 3. What would catch it

Neither half asks where the class **comes from**. The audit's suggestion is the direct one: for each route found
in the live app, take the body and response classes FastAPI resolved and assert `cls.__module__` starts with
`model_schema`. I did not implement or run it. The test file already builds the live app (`document` fixture,
`:279-286`), so the routes are at hand (`app.routes`, each with `body_field` and `response_field`).

## What this finding does NOT claim

- It does not claim any route on `main` uses a local class. The AST half passes on the real source and the
  nine routes are typed from `model_schema` (`ast_problems(_sources()) == []` is a current test).
- It does not claim the guard is useless. The AST half works for the import-removed case; the ledger's run B
  shows it failing as intended.
- It does not claim a diverged shape reaches production. It claims the test's second half gives no
  independent evidence for the case the plan says it covers.
- It does not claim ruff's F811 always fires in the kept-import variant; one arrangement was run.
- It does not survey other route-type tests for the same pattern. Only `test_deployment_route_types.py` was read.

## Disposition

Owner **WK-1178** (the standing maintenance Work; the guard family of FD-1335 and its request-side twin
FD-1366). Proposed remedy, for the plan to decide:

1. In the test, resolve each route's request and response **class** from the live app and assert
   `cls.__module__` starts with `model_schema` (the audit's suggestion), so the OpenAPI half no longer rests on
   the name alone.
2. Prove it on broken input both ways (CLAUDE.md §13): a same-named local class must fail the OpenAPI half and
   the import-kept variant must fail the AST half or the new check; the shipped routes must pass.
3. PL-1392 Acceptance 14's red-first sentence stays as filed: a filed plan is frozen at its date (CLAUDE.md §2), so the
   correction is a record (this finding and LG-1405's run B), not an edit of the plan.

## Severity (the maintainer's (by delegation))

**LOW**, set by the maintainer (by delegation) on 2026-10-05. This essay's earlier provisional MEDIUM is superseded.

**The maintainer's (by delegation) reason, recorded as a dated correction.** Amended 2026-10-05 before mint: the entry
"2026-10-05 09:54:07 BST — FD 9720 NOT filed (its premise is false, verified by me); RL-1401 gets a DATED
CORRECTION LINE (not a note only); e3 LOW stands, with the doubt recorded" in `~/gi-pricing-plan.local/channel/to-lead.md`
(a local file) says of this finding, quoted from it: "**e3 (FD-1509): LOW stands, the reason corrected.** The AST
half does not catch every arrangement (a same-named class with the import kept returns [] from `ast_problems`).
But ruff F811 (redefinition), which runs in the gate's ruff stage, flags that arrangement. So the escape needs
both halves of the route-types check AND ruff to miss. FD-1509 records the doubt, the one arrangement run, and the
ruff dependency." The doubt is the AST half's miss in step 2, "import kept (shadowed): []". The one arrangement run
is the `ruff check --select F811` run on the scratch file in step 2. The ruff dependency is that the kept-import
variant is stopped by the gate's lint stage and not by this test, and that it was not established that F811 fires
in every arrangement. The point that the plan states a guarantee (two independent halves) the test does not
deliver is the reason to harden the test, not a reason for a higher severity.
