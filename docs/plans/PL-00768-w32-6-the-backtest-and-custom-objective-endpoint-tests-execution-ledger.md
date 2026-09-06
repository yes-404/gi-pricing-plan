---
id: PL-768
family: plan
kind: leaf
title: W32-6 — the backtest and custom-objective endpoint tests: execution ledger
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-08-23
owner: planner
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                     # ids only
was: docs/plans/2026-08-23-w32-6-backtest-and-objective-endpoint-tests-ledger.md
---

# W32-6 — the backtest and custom-objective endpoint tests: execution ledger

What executing
[`PL-00769-w32-6-endpoint-tests-for-backtests-and-custom-objectives-implementation-plan.md`](PL-00769-w32-6-endpoint-tests-for-backtests-and-custom-objectives-implementation-plan.md)
actually did, on 2026-08-23, the same day the plan was written.

The plan is **not** edited to agree with this file — [`README.md`](README.md) has that rule.
Where the plan was wrong, this record says so and the correction lives here.

**Executed in an isolated worktree**, as one of six WK-692 slices run concurrently, and against
its own database (`gip_w32_6`) so no other slice's rows could be mistaken for this one's. The
first attempt stopped part-way and left a single `wip:` commit; this run rebased it onto
`main`, finished it, and rewrote the history into three Conventional Commits. `main` moved
**twice while this slice ran** — PRs #144–#146 before it started and #147–#148 during it — so
the branch was rebased twice and the gate re-run against the second base.

---

## Result

| | Before | After |
|---|---|---|
| Endpoint tests over the two backtest routes | 0 | **6** |
| Endpoint tests over the seven custom-objective routes | 2, marooned in a platform-layer file | **16** |
| Locked tables whose trigger is actually fired by a test | 13 | **14** (`backtests` joined) |
| Requirements with real endpoint evidence | — | FR-187, FR-94, FR-166, FR-150 |
| Requirement coverage | 263 / 507 (51.6%) | **263 / 507 (51.6%)** — see below |

No requirement id was allocated. Every marker names one that already existed.

---

## The plan named the wrong requirement, and it was the load-bearing one

The plan's `Spec` block and every task marker called **FR-144** "backtest results". It is
not. FR-144 is the **symbolic derivation of gradient and hessian from an `expression`
objective's loss** — a Phase 2 capability that FR-150 gates off and that nothing in this
repository implements. Marking six backtest tests with it would have moved the coverage count
by one and put a traceability claim on a requirement no line of code satisfies: the exact
"a marker is a claim, not a proof" failure [`CLAUDE.md`](../../CLAUDE.md) §13 rule 1 names.

The backtest requirement is **FR-187**, which `test_backtests.py` already carried. The
markers were corrected to it before the tests were committed.

**Verdict: the plan was wrong, the code is right.** FR-144 keeps a written verdict —
*deferred, owner Phase 2* — on its own spec row rather than a marker.

## Coverage did not move, and that is the finding rather than a shortfall

The plan's Task 4 Step 3 asked for the new total to be filled in from the run, expecting a
rise. **It is 263 of 507 (51.6%), the same figure the branch reports with this slice's two new
test files moved aside** — measured both ways rather than argued. FR-187, FR-94,
FR-166 and FR-150 were each already marked somewhere, so four requirements gained
real endpoint evidence while the count stood still.

The plan's stated starting figure of **258** was stale before this slice finished: W32-2,
W32-3, W32-4 and `07` FR-417 all landed on `main` while it ran, and the branch was rebased
twice. It was 260 against the first base and 263 against the last. **The movement attributable
to W32-6 is zero against either** — which is the only figure this slice can honestly claim, and
the reason the measurement was taken both ways rather than read off one run.

## Enforcement proven on deliberately broken input (§13 rule 4)

Ten mutations, each applied alone, the failure observed, then reverted. Every one is a guard
this slice's tests exist to hold.

| Broken | Observed |
|---|---|
| `load_backtest`'s `workspace_id` predicate dropped | `assert 200 == 404` — the cross-workspace read returned another workspace's artifact; 1 failed, 5 passed |
| `_get_or_404`'s `row.workspace_id != workspace_id` dropped | `assert 200 == 404` **twice** — the get and the usage boundary; 2 failed, 14 passed |
| `refuse_expression_kind` raising `VALIDATION_FAILED` | `assert 'VALIDATION_FAILED' == 'OBJECTIVE_KIND_NOT_ENABLED'` in 3 tests, **status still 409** — so the `["code"]` assertion is what carries them, not the status |
| `backtests_no_modify` trigger disabled in the database | `Failed: DID NOT RAISE DBAPIError` on the `[backtests]` parameter **only** — the new `_APPEND_ONLY_ROWS` entry genuinely fires the trigger |
| The certify route's resolved grid perturbed (`seed=999`) | `{'seed': 999} != {'seed': 20260818}` — the assertion compares against `default_sampling`, not a literal |
| Certify's status guard widened to admit `review` | `assert 202 == 409` |
| `_require_evidence` removed from the submit path | `assert 200 == 422` |
| The submit transition guard's status `409 → 422` | `assert 422 == 409` |
| `GET /models/backtests/{id}` re-gated `ReadModels → FitModels` | **passed** — see the finding below; after the correction, `assert 403 == 200` |
| `GET /custom-objectives/{id}` and `.../usage` re-gated the same way | **passed** — same finding; after the correction, `assert 403 == 200` twice |

`git status --porcelain` after the sweep shows only the two intentional test corrections; every
mutated source file was restored with `git checkout` and the disabled trigger re-enabled, and
the four affected files re-run clean (**56 passed**).

### The finding the mutations produced: three permits proved less than they claimed

Two of the ten mutations **did not fail**. `GET /models/backtests/{id}`,
`GET /custom-objectives/{id}` and `GET /custom-objectives/{id}/usage` could each be re-gated
from `model:read` onto `model:fit` with all 22 new tests staying green, because every permit
read the artifact as the `analyst` — which holds both permissions. The paired refusals used a
principal holding **nothing**, so the pair distinguished *authorised* from *unauthorised* and
never `model:read` from `model:fit`.

This is the same defect Task 3 was written to correct in someone else's test, reproduced in
this slice's own. Corrected: the three permits now read as the **`auditor`** (`model:read`,
not `model:fit`), and both mutations fail them. Recorded as finding 7 in
[`../roadmap.md`](../roadmap.md).

### One test observes a guard that has a twin behind it

`test_submitting_an_objective_twice_conflicts` still passed with the submit transition guard
removed outright: `approvals.submit` raises its own **409 `VALIDATION_FAILED`** for an artifact
already under review. The test does observe the `objectives.py` guard — changing that guard's
status to 422 fails it — but the route is two-deep here, and a future reader should not read
this test as sole evidence for either layer. Left as is: both refusals are correct and the
observed status is the one the route documents.

## Six more places the plan did not match the repository

| Plan said | Repository |
|---|---|
| The stale `n_points=300` docstring is `backend/src/app/platform/backtests.py:18`, `COUNT_GRID` at `:76-78` | Neither is in that file. The stale paragraph is `backend/tests/test_custom_objectives.py:18` and `COUNT_GRID` is at `:80`. Worse than stale: `SamplingSpec` now forbids 300 (`ge=1_000`) |
| Add a workspace-boundary test "for the list route" | **There is no list route.** Seven routes and none of them lists. The boundary is proven on `GET /{id}` and on `/{id}/usage` instead — the latter being the one whose leak is a set of another workspace's models |
| Certifying an already-`certified` objective conflicts | It does not. `certifiable_or_refuse` admits `{draft, certified}` deliberately — re-certification after a library upgrade is how a finding is found. The conflict is `review` and past, and that is what the test drives |
| `_require_evidence` guards `certify` | It guards `submit`. Certification *produces* the evidence; requiring it beforehand would be circular |
| `backend/src/app/jobs/model_handlers.py` | The path is `backend/src/app/worker/model_handlers.py` |
| The refusal code is `FORBIDDEN` | It is `PERMISSION_DENIED`, as W32-2's ledger also recorded |

`02` §5.1's own claim that `/derive` answers **422** was wrong against the code, which answers
**409**; the code is right — the request is well-formed and the *capability* is disabled — and
the spec carries a dated amendment rather than the test being softened.

## Two plan steps deliberately not followed

- **"The frontend half is not needed."** It was run anyway, in full, and passed. The
  reasoning in the plan is sound — nothing here touches `docs/contracts/` — but the cost of
  running it is minutes and the cost of being wrong is a red `main`.
- **"The branch is pushed and a PR is open."** Not done. This slice was executed as one of
  six concurrent branches that the main thread lands itself; the branch is committed and left
  unpushed.

## Verification

Every gate command exit 0, each read from its own exit code, none piped.

`uv run pytest -q`: **1814 passed, 1 xfailed, 0 skipped**, 9m06s at load average 4.8 → 2.9.
**Zero skips is the load-bearing number here** — `conftest_db.py` skips at fixture level when
the database is unreachable, so a slice whose entire deliverable is DB-backed endpoint tests
cannot tell a passing run from an absent one by the summary alone. The suite ran against
`gip_w32_6`, migrated to head (`7c1a9e40b3d2`) before the run.

`generate-contracts.py --check` passed **without a regenerate**, which is the plan's own test
that nothing here touched a shape.

## Carried forward, with owners

- **`uq_backtests_model_version` is not workspace-scoped.** A migration plus a governance
  question about whether model ids may collide across workspaces. **Owner: unassigned; raise
  before the next slice that writes a backtest test or touches this table.** Recorded in
  `02` §4.12.
- **The `derive` route publishes a `200 CustomObjective` it can never return.** A
  `model-schema` change, which a test slice must not make. **Owner: the Phase 2 slice that
  enables `expression_objectives`.** Recorded in `02` §5.1.
- **The custom-objective read routes are single-layer RBAC.** Consistent with the rest of the
  API, so noted rather than proposed. **Owner: the next `06` RBAC slice.**
- **FR-144 remains unevidenced**, with a written verdict of *deferred, owner Phase 2* on
  its spec row.
