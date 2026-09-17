---
id: PL-772
family: plan
kind: leaf
title: W32-8 execution ledger — the artifact library list routes
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-08-23
owner: planner
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                     # ids only
was: docs/plans/2026-08-23-w32-8-artifact-library-list-routes-ledger.md
---

# W32-8 execution ledger — the artifact library list routes

**Plan:** [`PL-00773-artifact-library-list-routes-implementation-plan.md`](PL-00773-artifact-library-list-routes-implementation-plan.md),
frozen at 2026-08-23. **Executed:** 2026-08-24. **Branch:** `w32-8-artifact-library-list-routes`.

This ledger records what execution actually did, including the seven places the plan's
expectations did not survive contact with the repository and the two spec-versus-spec
disagreements the slice found and refused to resolve on its own authority. **The plan is not
edited to agree with any of it** — it is frozen at its date, and a plan quietly rewritten to
match today's repository destroys the record of what was believed when the work was scoped.

## Result

| Task | Outcome |
|---|---|
| 1 — batch the usage count into one aggregate per page | Done. `objectives.usage_counts` and `metrics.usage_counts`, 5 tests |
| 2 — `GET /custom-objectives` | Done. `799ef78`, 7 new tests |
| 3 — `GET /custom-metrics` | Done. `64fe783`, 9 new tests |
| 4 — `GET /peril-structures` | Done. `8c36090`, 7 new tests, **no `usage_count`** |
| 5 — contracts, contract guards, open questions, gate, this ledger | Done. `214ff60`, `2fcb3a5`, `a4a7e50` |

Diff against `main`: **21 files changed, 2625 insertions(+), 81 deletions(-)** across nine
commits. No new requirement id was allocated: every marker names FR-167, FR-166,
FR-162 or FR-192, all of which already existed. Two open questions were raised,
answered upstream before this branch merged, and filed **born-`decided`**: **OQ-602** and
**OQ-603**.

## What was built

Three list routes, one shape, declared at `/custom-objectives`, `/custom-metrics` and
`/peril-structures` and mounted under `API_PREFIX`:

```python
@router.get("/custom-objectives", summary="List the workspace's Custom Objectives",
            responses=problems(400, 401, 403, 422))
async def list_custom_objectives(caller: ReadModels, database: DatabaseDep,
                                 filters: ObjectiveFilterDep) -> Page[CustomObjective]
```

Each filter model is `frozen=True, extra="forbid"` and carries `status`, `slug` (equality,
1..64), `cursor` and `limit` (1..`MAX_LIMIT`). Each platform function takes `limit` and
`count_cap` as **required** keyword arguments rather than defaulting them, because the
defaults live in `app.api.pagination` and `lint-imports` forbids `app/platform/` importing
from `app/api/` — see correction 2 below.

### The budget is measured, not asserted

FR-167 states the budget inside the requirement: *"one aggregate per page, never one
per row."* `backend/tests/test_artifact_usage_counts.py::test_one_page_of_refs_costs_one_query`
counts the queries a page of refs actually issues, and
`test_an_empty_page_asks_the_database_nothing` covers the empty first screen. An N+1
implementation would pass every other test in this slice, which is precisely why the
requirement bothered to state the budget — so it is proven by counting rather than by reading
the code (`CLAUDE.md` §13 rule 4).

## Two spec-versus-spec disagreements, raised here and answered upstream

`CLAUDE.md` §0 forbids a slice silently making either side agree with the other, and both of
these are spec-against-spec, where the slice has no standing to pick. Both were drafted as
open questions for the maintainer. Before this branch merged, the **WK-692 closure proposal's
Part D amendment to FR-167** (#156, merged 2026-08-24) decided both — each the way this
slice had recommended, and reached from the specification side without sight of this analysis.

They are filed **born-`decided`** as OQ-602 and OQ-603, mirrored into
`02-modelling.md` §10. **This reverses a call made earlier in the slice**, and the reversal is
recorded rather than quietly applied. The first instinct was to drop the rows on the ground
that an open question the specification already answers is a register reporting a state the
repository does not have. That is true of a row's **status** and false of its **existence**:
`open-questions.md` declares four status values — `open` · `decided` · `deferred` · `dropped`
— so the register is built to hold answered questions, and most MODEL rows in it are
`decided`. Dropping them would have discarded the alternatives and, more importantly, the
guard rail on OQ-603 — the argument that would reopen it *wrongly*. That reasoning would
then have survived only in this ledger, and a filed plan is frozen at its date rather than
being the register a later session consults before re-asking. Raised by the `w32 decisions`
session; the call is this slice's.

**OQ-602 — does §5.3 render one artifact library or three?** FR-167 opens *"The
three artifact libraries §5.3 renders are listable"*, and this slice built all three
endpoints against it. §5.3 contains **one** library view (`Custom objective library`,
`/objectives`), a Peril structure *detail* view, and no custom-metric view at all. The
requirement's opening sentence cannot be satisfied as written. Recommendation: add the two
missing §5.3 rows. `00-overview.md` §5.6 carries the identical gap and must move with it.
**Outcome:** Part D item 3 added exactly those two rows — `Custom metric library` at `/metrics`
(`02-modelling.md:2576`) and `Peril structure library` at `/peril-structures` (`:2577`) —
against routes §5.1 already declared, so the opening sentence now describes §5.3 as it stands.

**OQ-603 — which artifact rows carry `usage_count`?** FR-167's prose is
unqualified; §5.1 puts the field on objectives (`:1697`) and metrics (`:1705`) and **omits it
from peril structures** (`:1712`). The slice built §5.1's reading and **asserted the absence**
rather than leaving it implicit — `test_the_row_carries_no_usage_count`, with a comment at the
route marking the omission deliberate. Recommendation: qualify the prose, because the quantity
FR-167 defines is *undefinable* on a peril row — `PerilComponent`
(`perils.py:214-228`) holds `frequency_model`, `severity_model` and `burning_cost_model` as
`ArtifactRef`s, so the reference runs PerilStructure → Model, and `modelling.py:832`'s `peril`
is a plain `str` label rather than a ref. "The count of Model Specs referencing that artifact"
is therefore **`0` by construction, forever** — the same defect class W32-9 deleted from
`ShapInteraction.exposure_share` for being `1.0` by construction.

One caveat is written into the question for whoever decides it: this holding does **not** rest
on the peril block having no `/usage` route. `03-rating-engine.md:100` gives `model_call` a
`peril_structure_ref` and FR-237 pins one per call, so a peril structure does have a real
blast radius. Only the specific quantity this requirement defines is vacuous.
**Outcome:** Part D item 4 qualified the prose to the two libraries and adopted that ground
verbatim, including the caveat — *"a Peril Structure does have a blast radius … so the absent
`/usage` route is a separate question and not evidence for this one."* It goes one step
further than this slice asked, withdrawing the requirement's *"all three had create, detail,
certify, submit and usage routes"* clause as to Peril Structures, whose §5.1 block is create,
list, detail, reconcile and submit — the five routes
`test_all_five_routes_are_published` asserts.

## FR-166's observation went false, and is corrected rather than rewritten

FR-166's 2026-08-23 amendment recorded *"(a) there is no list route — seven routes and
none of them lists"*. That went false at `799ef78`, in this slice. A dated **correction is
appended** and the original sentence is left standing (`CLAUDE.md` §5): it records what was
true on 2026-08-23 and is the reason FR-167 exists at all. Deleting it would erase the
evidence for the requirement that cured it.

The evidence that sentence cites is unaffected — the workspace boundary is still proven on
`GET /{id}` and `GET /{id}/usage`, and is now proven a third time on the list route itself,
which is the one whose leak would be a whole page of another workspace's artifacts.

## Where the plan did not match the repository

Seven, none of which changed what the slice delivers. In every case **the repository was the
correct side**.

1. **The route path would have double-prefixed.** The plan declares
   `@router.get("/api/v1/custom-objectives")`. `backend/src/app/main.py:103` includes every
   router with `prefix=API_PREFIX` where `API_PREFIX = "/api/v1"` (`:48`), so the literal
   would have mounted at `/api/v1/api/v1/custom-objectives`. Caught in Task 2 and carried
   forward into Tasks 3 and 4 before it could propagate.
2. **`limit`/`count_cap` defaults would have broken the layering.** The plan gives the
   platform functions `limit: int = DEFAULT_LIMIT`; those constants live in
   `app.api.pagination`, and `lint-imports` forbids `app/platform/` importing `app/api/`.
   Made required keyword arguments supplied by the router.
3. **`usage_count: int = 0`** (plan) versus the implemented `int | None = Field(default=None,
   ge=0)`. `None` means *not asked* — the detail routes need it, and a hard `0` would make
   "nobody references this" indistinguishable from "nobody counted".
4. **`backend/tests/test_peril_structures_api.py` did not exist**; the plan phrases Task 4
   Step 1 as an edit to it. Created.
5. **The plan's Task 4 arithmetic is off by one** — *"six tests, Task 2's seven minus
   `test_each_row_carries_its_usage_count`"* — but the same step then *adds*
   `test_the_row_carries_no_usage_count`. Seven were written.
6. **`_create_peril_structure(client, author)` and the `author` fixture** in the plan's test
   snippet exist nowhere in the repository; `test_peril_structures.py` names its fixture
   `pricing_actuary`. Written to match Tasks 2 and 3's shape instead.
7. **The plan's "two pre-existing tests around `:366-368`"** in `test_custom_objectives.py` do
   not exist; the OpenAPI-presence test is at `:596-609`.

## Every new test was proven to fail first

Each of the 23 new API tests was run against the behaviour it replaces before the
implementation landed, and the failure captured verbatim. Pre-implementation, all seven peril
tests failed with `assert 405 == 200` and a `METHOD_NOT_ALLOWED` body naming
`/api/v1/peril-structures`. Post-implementation each was mutation-proved individually — route
path renamed, `slug ==` changed to a `LIKE` prefix, the status condition deleted,
`usage_count: int = 0` added to `PerilStructure`, the workspace condition emptied, `ReadModels`
downgraded to a bare caller, and the cursor `where` deleted — each mutation failing exactly
one test and then reverted.

**The three contract-presence assertions were proved the same way**, and the mutation chosen
is the failure they exist to catch: `docs/contracts/openapi/generated.json` was reverted to
its pre-regeneration state and all three failed, each naming its own route
(`GET /api/v1/custom-metrics is unpublished`, and the peril and objective equivalents). The
artifact was then restored and verified byte-identical — `git diff docs/contracts/` empty.

**One process note, recorded because it nearly lost work.** Reverting a mutation with
`git checkout -- <file>` discarded the *uncommitted* Task 4 router implementation, because
HEAD had none of it. Caught immediately by a `grep -c` that returned 0, re-applied, and the
remaining mutations were done against `cp` backups instead. A mutation proof on uncommitted
code must not use `git checkout` as its undo.

## Contract regeneration

`generate-contracts.py` rewrote exactly three artifacts, **all three on the generated side**
(`7bbb758`) — `docs/contracts/openapi/generated.json`,
`docs/contracts/schemas/generated/custom-objective.schema.json` and
`docs/contracts/schemas/generated/custom-metric.schema.json`.
`docs/contracts/schemas/generated/peril-structure.schema.json` **was not rewritten**, which is
independent confirmation that Task 4 added no schema field: the absence asserted by
`test_the_row_carries_no_usage_count` is visible in the generated contract too, from a different
direction.

Every path here is written in full deliberately. Two of these slugs have a hand-authored contract
as well — `docs/contracts/schemas/custom-objective.schema.json` and the peril-structure
equivalent — and this slice wrote to the authored custom-objective too, but **by hand, in its own
commit** (`4d92f08`), never by the generator. `custom-metric` has no authored side at all
(`scripts/generate-contracts.py:98` records why). Naming these files by bare basename invites the
reading that `generate-contracts.py` wrote a hand-authored contract, which would be an ADR-704
violation rather than a slice detail: the flow is one-way, `model-schema` → `generated/`, and
nothing generates the authored side. The bare-basename form was in this ledger's first draft and
did mislead a later reader, which is why it is spelled out rather than left to context.

## §13 verdicts

| Requirement | Verdict |
|---|---|
| **FR-167** | **Delivered and tested** for the API half it scopes — three routes, the shared aggregate, the stated per-page budget measured by query count. Its opening sentence about §5.3 and its unqualified `usage_count` prose were **not** deliverable as written and are not made to look delivered: this slice raised both as OQ-602 and OQ-603, and the Part D amendment (#156) corrected the requirement itself on the same date, so the row this slice was built against and the row now in `main` agree. Both open questions are `decided` on arrival. The view half is `WK-664`'s and was never in this slice. |
| **FR-166** | **Delivered and tested**, with its point *(a)* corrected in place and dated. |
| **FR-162** | **Delivered and tested.** The metric library lists, and the module gained the published-contract guard its two sibling modules already had. |
| **FR-192** | **Delivered and tested.** `test_all_four_routes_are_published` became `test_all_five_routes_are_published`. |
