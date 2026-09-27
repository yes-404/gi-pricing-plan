---
id: PL-770
family: plan
kind: leaf
title: W32-7 — Workspace Identity and Selection: execution ledger
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-08-23
owner: planner
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                     # ids only
was: docs/plans/2026-08-23-w32-7-workspace-identity-and-selection-ledger.md
---

# W32-7 — Workspace Identity and Selection: execution ledger

**Slice:** `W32-7` · **Plan:**
[`PL-00771-workspace-identity-and-selection-implementation-plan.md`](PL-00771-workspace-identity-and-selection-implementation-plan.md),
frozen at its date and **not edited** by this execution (`CLAUDE.md` §2). Where the plan turned
out to be wrong, the correction is here and in the commit message, so the record of what was
believed on 2026-08-23 survives.

**Executed:** 2026-08-24 · **Branch:** `w32-7-workspace-identity` · **Requirements:**
FR-396, FR-397, and FR-451 by collision (§4).

---

## 1. What shipped

| Task | Landed in | Substance |
|---|---|---|
| 1 | branch commit 1 | `WorkspaceRow`, the two foreign keys (`workspace_members`, `workspace_settings`), migration `57547846f0a3` with its 35-table backfill, and `platform.workspaces.ensure_workspace`. |
| 2 | branch commit 2 | `GET /api/v1/me` returns every membership with FR-395's name, ordered by name. |
| 3 + 4 | branch commit 3 | The verified `Workspace-Id` header and `_select_workspace`; `platform.workspace_switch.record_switch`; OQ-652 and OQ-653; the injected-`422` strip. |
| 5 | branch commit 4 — *this one* | This ledger and the W32-7 roadmap record. |

The four are named by ordinal rather than by hash because this branch is **squash-merged**:
the commits above do not survive onto `main`, so a hash written here would resolve for
nobody. The durable citation is the pull request.

**Tasks 3 and 4 landed as one commit, against the plan's one-commit-per-task shape.**
`test_workspace_selection.py` holds both sets of tests. Splitting them would have produced
either a commit with a behaviour change and no test covering it, or a revision that does not
pass its own suite — and a bisect landing on either is worse than a wider commit.

## 2. The four obligations of FR-396, with verdicts

`CLAUDE.md` §13 admits four verdicts and silence is not one of them.

| # | Obligation (FR-396) | Verdict | Evidence |
|---|---|---|---|
| 1 | The selection is **checked against the principal's own memberships on every request**, never trusted; a workspace the principal does not belong to is refused `WORKSPACE_SCOPE_DENIED`. | **Delivered and tested** | `test_a_selection_outside_the_memberships_is_denied` (code *and* status asserted), plus the breakage proof in §3. |
| 2 | Several memberships and **no** selection is refused `WORKSPACE_SELECTION_REQUIRED`, **never defaulted** into one. | **Delivered and tested** | `test_several_memberships_and_no_selection_is_refused`; `test_membership_of_several_workspaces_requires_a_choice` now asserts the *code*, not only the status — it previously passed against `UNAUTHENTICATED` and would have gone on passing through a regression. |
| 3 | Exactly **one** membership needs no selection; a Service Account never sends one. | **Delivered and tested** | `test_a_single_membership_needs_no_selection`. |
| 4 | **A switch is audited into both chains**; the first selection after login writes one event. | **Deferred with an owner — `W6b-11`** | Mechanism delivered and tested (`test_a_switch_is_recorded_in_both_chains`, `test_the_first_selection_after_login_writes_one_event`, plus §3's breakage proof). **The call site is not built**, and OQ-652 says why. |

**Why obligation 4 is deferred and not delivered.** `require_caller` runs once per request and
holds no memory of the previous one, so *"the selection changed"* is not a fact it can observe:
a switch is a difference between two requests and the platform stores nothing spanning two
requests. Auditing every selection instead would need no schema change — which is exactly why
it is the option a later reader reaches for — and would take a per-workspace advisory lock and
write an audit event on **every authenticated request a multi-membership principal makes**,
turning the FR-372 chain into a request log and burying the record of what was actually
done. OQ-652 records all three options and recommends storing the previous selection,
reached through an explicit endpoint. **A green suite here must not be read as this obligation
being met.**

### FR-397's own claims

| Claim | Verdict | Evidence |
|---|---|---|
| The header is **declared on the route** and appears in the published contract. | **Delivered and tested** | `test_the_header_is_published_on_an_operation`; **108 of 112 operations** carry it, the four without being `/healthz`, `/readyz`, `/version`, `/metrics` — exactly the unauthenticated surface. The plan estimated "~40 operations"; declaring it on the shared dependency reached every authenticated route, so no per-route fallback was needed. |
| **Optional in the contract, required in the handler**, so the refusal is a typed platform error and not a `422` outside the error catalogue. | **Delivered and tested** | The parameter is `str \| None = None` and parsed by hand; annotated `UUID \| None`, FastAPI would answer a malformed value with a bare `422`. A malformed header yields `403 WORKSPACE_SCOPE_DENIED`. |
| Named `Workspace-Id`, **not** `x-dev-workspace-id`, and unprefixed. | **Delivered** | `Header(alias="Workspace-Id")`. `_development_caller` still reads `x-dev-workspace-id`, a different header for a different purpose, and the omission is commented as a decision rather than left to look like an oversight. |

## 3. Enforcement proven on deliberately broken input

`CLAUDE.md` §13 rule 4: a check that has never printed a failure has not been tested. Each
breakage was applied, run, and reverted by re-patching — **not** by `git checkout --`, for the
reason in §5.

| Breakage | Result |
|---|---|
| `_select_workspace`: `if selected not in identity.workspaces` → `if False` | **1 failed**, 4 passed — `test_a_selection_outside_the_memberships_is_denied … Failed: DID NOT RAISE PlatformError` |
| `responses._is_injected_validation_error` → `return False` | **2 failed**, 120 passed — `test_committed_contracts_match_the_models` and `test_the_injected_validation_error_is_stripped_and_ours_is_kept` |
| `record_switch`: write only the entered chain | **1 failed**, 6 passed — `test_a_switch_is_recorded_in_both_chains` |

## 4. FR-451: declaring one header re-opened a defect a module exists to prevent

Not in the plan, and the most useful thing this slice found.

FastAPI injects a `422` typed as its own `HTTPValidationError` into every operation that has a
parameter and does not already declare one. Declaring `Workspace-Id` on `require_caller` gave
**112 operations a parameter in a single edit**, and the five that had never had one —
`GET /api/v1/me`, `/settings`, `/sources`, `/approval-policy`, `/demo/guide` — began publishing
a second error shape. That is the exact finding `api/responses.py` was written to remove,
arriving through a **dependency** rather than through a route, which is a path no per-route
convention can cover.

`without_fastapi_validation_error` strips the injected response and the two schemas it drags
in, applied in `create_app` so the served document and the committed contract are the same
bytes. The five routes are **not** given `problems(422)` instead: they cannot return one, and
`responses.py` exists to stop a route advertising an error it never produces. The 103 routes
that genuinely can fail validation declare their own `422` and are untouched — verified after
the change: **0 injected, 103 `ProblemDetail`, both schemas absent.**

**`generate-contracts.py --check` passed throughout.** The drift check compares the contract to
the code, and here both were wrong together — the same asymmetry W32-8 hit from the authored
side. It was the full suite that caught it.

## 5. Where the plan was wrong

The plan is frozen and unedited. Three corrections:

1. **Task 3 Step 9 restores `deps.py` with `git checkout --` after the breakage proof.** That
   is safe only if Step 8's commit already ran. Executed in the written order on an uncommitted
   tree, it discards the entire task — which is what happened here; the work was rebuilt from
   the patch script. A breakage proof must be reverted by re-patching unless the tree is clean.
2. **Task 5 Step 1 recommends adding `workspace` to `ARTIFACT_TYPES`** so the switch event's
   `entity_ref` parses, on the ground that "an audit chain whose refs do not all parse is a
   chain a reader must special-case". Measured before diverging: of the **39 `entity_ref`
   spellings the backend writes, only 19 parse.** Thirteen types besides `workspace` are already
   absent from the frozenset — `actor`, `approval_policy`, `backtest`, `blob`, `job`,
   `model_comparison`, `model_family`, `principal`, `profile`, `role`, `service_account`,
   `setting`, `validation_report` — and five more name a listed type with **no `@version`**
   (`dataset:{slug}`, `dataset:{row.slug}`, `dataset_version:{version_id}`, `model:{model_id}`,
   `reference_table:{slug}`). The premise was false: the chain never held only `ArtifactRef`s,
   so admitting one more type fixes 1 case in 20 and redefines the frozenset as "things that
   appear in `entity_ref`". **OQ-653** records the measurement and recommends declaring what
   the column actually is. The five unversioned refs are flagged there as a plain bug under any
   option: `dataset:{slug}` records which dataset was touched but not which version, which is
   the fact an auditor came for.
3. **The plan does not mention the injected `422`** (§4). Its estimate of "~40 operations"
   carrying the header was also low by a factor of nearly three, for the same reason the `422`
   spread: a dependency reaches further than a route.

## 6. Gate

Both halves, judged by **exit code** and never by output text. All thirteen exit `0`.

| Command | Exit |
|---|---|
| `uv run ruff check .` | 0 |
| `uv run mypy` | 0 |
| `uv run lint-imports` | 0 |
| `uv run pytest -q` | 0 |
| `python3 scripts/audit-docs.py` | 0 |
| `uv run python scripts/req-coverage.py` | 0 |
| `uv run python scripts/generate-contracts.py --check` | 0 |
| `pnpm --dir frontend install --frozen-lockfile` | 0 |
| `pnpm --dir frontend generate:api` | 0 |
| `pnpm --dir frontend lint` | 0 |
| `pnpm --dir frontend type-check` | 0 |
| `pnpm --dir frontend test` | 0 |
| `pnpm --dir frontend build` | 0 |

**`pytest` reconciled rather than read.** `1923 passed, 1 skipped, 1 xfailed` against
`--collect-only`'s **1925 collected** — the three accounted for, so the summary describes the
whole tree and not a subset of it. Frontend: **21 files, 131 tests**, all passing.

**One failure on the first run, which did not reproduce and is recorded rather than
suppressed.** `test_peril_structures.py::test_versioning_is_by_slug` failed once with a
dataset-validation job reaching `FAILED` instead of `SUCCEEDED`; the module passes standalone
(`17 passed`) and the full suite passed on a second run. It is not this slice's: the only
insert into either newly-foreign-keyed table anywhere in `backend/src` is
`platform/settings.py:371`, reachable solely from the settings endpoint and never from a job,
and a foreign-key violation would fail deterministically rather than once under a nine-minute
run. The argument and the measurement are kept apart deliberately — the reasoning above is why
it is *implausible*, the second green run is the evidence that it *did not happen again*, and
neither substitutes for the other.

### FR-397 in the generated client, checked rather than assumed

The reason for declaring the header on the dependency instead of reading the raw request is
that a generated client should carry it, so that is what was verified — in
`frontend/src/api/generated/schema.d.ts`, which is regenerated and VCS-ignored:

```
"Workspace-Id"?: string | null;          # on the authenticated operations
$ grep -c HTTPValidationError frontend/src/api/generated
0
```

The second is the §4 strip observed from the far end of the contract flow: the shape is absent
from the client because it is absent from the document, not because anything filters it there.

**`ruff format` is not part of this gate and was not run.** CI runs `uv run ruff check .` only
(`.github/workflows/python.yml:109`), and the repository is not formatted to `ruff format`'s
style — it reports **230 files would be reformatted** against a green `main`. Running it here
rewrote pre-existing code in five files, including a deliberately aligned comment table in
`test_contracts.py`'s `ArtifactRef` cases, and turned a pure addition into 91 changed lines
against 55 deleted. That churn was reverted hunk by hunk before this commit; the file is now
**+53/−0**. A formatter the repository does not use is a diff generator, and the churn it makes
is indistinguishable from the change under review.

## 7. Open questions filed

| Id | Question | Recommendation |
|---|---|---|
| **OQ-652** | What tells the API that a workspace selection *changed*? | Store the previous selection, reached through an explicit endpoint; **refuse** auditing every selection. Consumed by `W6b-11`. |
| **OQ-653** | 20 of 39 `entity_ref` spellings do not parse as an `ArtifactRef`, and nothing notices. | Declare and validate that `entity_ref` names the *subject* of the event; **never** widen `ARTIFACT_TYPES` to make an existing string parse. |

Both are mirrored into `docs/specs/07-platform.md` §10, and `audit-docs.py` checks the mirror
in both directions.
