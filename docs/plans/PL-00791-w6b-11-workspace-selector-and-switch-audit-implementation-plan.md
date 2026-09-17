---
id: PL-791
family: plan
kind: leaf
title: W6b-11: Workspace Selector and Switch Audit — Implementation Plan
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-08-25
owner: planner
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                     # ids only
was: docs/plans/2026-08-25-w6b-11-workspace-selector.md
---

# W6b-11: Workspace Selector and Switch Audit — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give a principal with more than one workspace membership the shell control to choose which workspace it acts in — and audit that act into both audit chains, so the record of *who was acting where, and when did they stop* is complete.

**Architecture:** The backend half of the selection already exists — `require_caller` verifies a `Workspace-Id` header against the principal's memberships on every request, and refuses rather than defaults (`FR-397`, delivered by WK-692). This slice adds the one thing the delivered mechanism deliberately left out: the **call site**. A principal-only dependency authenticates without a selection; two `me.py` endpoints make the memberships readable before a selection exists and turn the switch into an explicit, audited act (`POST /api/v1/me/workspace` running `record_switch`, per `OQ-652` option (c)); the SPA gets its first Pinia store, sends the chosen workspace as the `Workspace-Id` header on every request, and renders the selector in the app shell. Last of all, the development pin `x-dev-workspace-id` is removed — removal never precedes replacement.

**Tech Stack:** FastAPI + Pydantic v2 (shapes in `me.py`, which is where the `/me` shapes already live) · Vue 3 `<script setup lang="ts">` + Pinia + `@testing-library/vue` · vitest (happy-dom) · the generated OpenAPI contract (`docs/contracts/openapi/generated.json`) and the generated frontend client (`pnpm generate:api`).

**Spec:** [`../specs/07-platform.md`](../specs/07-platform.md) — `FR-395`, `FR-396`, `FR-397`, `FR-394`; [`../specs/06-governance.md`](../specs/06-governance.md) — `FR-372`. The decision this plan executes is [`../open-questions.md`](../open-questions.md) `OQ-652` (decided 2026-08-25, Reading 1, option (c)).

**Anchor:** this plan describes the tree at `6776d5f` (tip of `origin/main` at filing — PR #237, the ruling this plan builds on, merged 2026-08-25). Line numbers are exact there.

## Global Constraints

- **`FR-390`** — access is explicit, never default: an authenticated user with no membership row can reach no workspace.
- **`FR-396`** — the selection is checked against the principal's own memberships on every request, never trusted; a switch is audited into **both** chains (the workspace left and the workspace entered); the first selection after login has no chain to leave and writes one event. Four obligations; obligations 1–3 are delivered (WK-692).
- **`FR-397`** — the chosen workspace travels as a verified `Workspace-Id` request header: declared on the route, optional in the published contract, required in the handler; unprefixed (`X-` is retired by RFC 6648); a principal with several memberships and no header is refused `WORKSPACE_SELECTION_REQUIRED`, never defaulted.
- **`OQ-652`, decided: a switch is a human act.** Only the explicit `POST /api/v1/me/workspace` audits (`record_switch`); `require_caller` audits nothing; a client that changes its header without the act switches unrecorded — which under Reading 1 is not a gap, because such a caller has not switched.
- **Never hand-write an API type in the frontend** — it comes from the generated client (`CLAUDE.md` §2). The backend response shapes this slice adds live beside the existing `/me` shapes in `me.py` (no `model-schema` Workspace shape exists to duplicate — `model-schema` declares shapes only, no endpoints).
- **`FR-394`** (decides `OQ-656`) — the browser learns the OIDC issuer and `client_id` from an unauthenticated `GET /api/v1/auth/config`. That endpoint is **`W6b-10`'s** build work, not this slice's.

## Scope, dependencies, and the disposition this plan is filed under

**In scope (this slice):**

1. `require_identity` — authenticate without a workspace selection (the seam both switch endpoints need).
2. `GET /api/v1/me/workspaces` — the memberships list, unscoped, so a first selection can be made.
3. `POST /api/v1/me/workspace` — the switch: validates against memberships, audits through `record_switch`, returns the entered workspace.
4. The spec amendment these endpoints need (`FR-396`, `FR-397`, §5.1 rows).
5. The frontend: a `me.ts` client, the workspace store (the app's first Pinia store), `Workspace-Id` wiring in `client.ts`, the shell selector in `App.vue`.
6. Removal of the `x-dev-workspace-id` pin — the backend dev path adopts the real selection semantics, then the Vite proxy injection and every stale mention of the pin go. **Last, after the switcher lands; removal never precedes replacement.**

**Out of scope (by disposition, manager 2026-08-25, verbatim):** *"seed membership is already W6b-14's (its plan commits `workspace_members` rows in `seed.py`). Pin removal splits: `x-dev-principal-id` goes when W6b-10 lands real auth; `x-dev-workspace-id` goes when W6b-11 lands the switcher. Removal never precedes replacement."* — So: **no seed changes for membership** (W6b-14's Task 3, [`PL-00793-w6b-14-the-local-oidc-provider-implementation-plan.md`](PL-00793-w6b-14-the-local-oidc-provider-implementation-plan.md) file table row `examples/fremtpl2/seed.py`), **no `x-dev-principal-id` removal** (W6b-10's), no browser authentication (W6b-10's), no membership provisioning API (deliberately absent until WK-659, `models.py:472-476`), no §5.3 view row (the selector is shell chrome, not a view — stated in Task 4).

**`W6b-11b` vacated; obligation 4 folded in here.** The revised slice map's P8 split cut obligation 4 into `W6b-11b` gated on `OQ-652`. The decision's own text vacates it — *"P8's own criterion is met — the audit work is not browser work; the browser contributes one call in a switcher W6b-11 already owns"* — leaving *"the endpoint and the switcher's call"* as obligation 4's remaining work. The manager's disposition assigns that remainder to this slice ("`x-dev-workspace-id` goes when W6b-11 lands the switcher" — the switcher is this slice's). The ruling's amendment text leaves the formal slice assignment to the next slice-map revision — this plan is filed under the manager's disposition, and the revision will formalise what this plan already records.

**Dependency record.** `W6b-11` waits on its own dependency **`W6b-10`** (browser authentication) — `FR-397`'s 2026-08-25 amendment says so in as many words. `W6b-10` is unblocked: `OQ-656` was decided 2026-08-25 as `FR-394`, and `W6b-10`'s own dependency `W6b-14` has its plan filed. **Build-order consequence for Task 8:** by the time this slice builds, W6b-14's seeded `workspace_members` rows exist, so the dev path has memberships to check. The tasks here are nevertheless self-contained: every backend test seeds its own memberships through fixtures (the pattern `test_workspace_selection.py:45-71` already establishes).

## Findings

**Finding 1 — the first selection was impossible from the SPA as specified; ruled and closed before this plan was filed.** `FR-396` names the identity endpoint (`GET /api/v1/me`) as the memberships source — *"the memberships are readable from the identity endpoint `06` §5.1 declares"* — and `/me` is scoped: `require_caller` refuses a multi-membership principal with no selection (`WORKSPACE_SELECTION_REQUIRED`, `deps.py:166-171`) **before it can read the list it would choose from**; the memberships come from the platform database (`authenticate_bearer`, `backend/src/app/auth/service.py:103-113`), so no client-side channel exists. The list the choice would come from was unreadable until the choice existed. **Ruled 2026-08-25 by the decision-maker, merged as PR #237** (the second amendment on `FR-396`): this plan's recommendation was adopted verbatim — an **unscoped `GET /api/v1/me/workspaces`** (authenticated, list-only, the principal's own memberships) and the switch `POST /api/v1/me/workspace` **accepts an absent `Workspace-Id` as `left=None`**, the first selection writing one event. The refused alternatives and their reasons are recorded in the amendment: a scope-exemption on `/me` itself (one endpoint with two auth regimes, and it amends the delivered `FR-397` refusals) and a client-side persisted selection (dead on first-ever login). Both routes are already declared in `06` §5.1. Tasks 2–4 build against the ruling.

**Finding 2 — the dev path bypasses membership entirely today, and that is a decision, not an oversight.** `_development_caller` (`deps.py:185-220`) builds a `Caller` from the two dev headers with **no** membership check — the comment at `deps.py:124-126` says the omission is deliberate ("a different header for a different purpose, and FR-397 says so in as many words"). The consequence: under dev headers, `/me`'s `workspaces` list is empty until W6b-14's seed rows exist, and the selector has nothing to render. Task 8 is where this changes — the dev path adopts the real selection semantics against the seeded memberships, which is also what makes the switcher exercisable in `local`/`dev`.

**Finding 3 — the demo seed writes no `workspaces` row and no `workspace_members` rows today** (`grep` for `WorkspaceRow|ensure_workspace|workspace_members|WorkspaceMember` in `examples/fremtpl2/seed.py` returns nothing; only role assignments at `:306-326`). W6b-14's Task 3 fixes this and is deliberately not duplicated here. Until it lands, the dev principal has no memberships and the selector shows an empty list — which is also the correct, by-design state for a Service Account (`me.py:114-117`), so an empty list is a normal state, never an error.

---

### Task 1: `require_identity` — authenticate without a workspace selection

**Files:**
- Modify: `backend/src/app/api/deps.py` (add beside `require_caller`, after the `_development_caller` helper)
- Test: `backend/tests/test_workspace_identity.py` (create)

**Interfaces:**
- Produces: `IdentityDep = Annotated[Identity, Depends(require_identity)]` — used by Tasks 2 and 3. `Identity` is a frozen dataclass with `principal: Principal` and `workspaces: frozenset[UUID]`.

- [ ] **Step 1: Write the failing test**

`backend/tests/test_workspace_identity.py` — mirror the fixture pattern of `test_workspace_selection.py:18-71` (its `StubVerifier`, `_claims`, `_memberships` helpers are the established way to make an authenticated principal with N memberships):

```python
"""`require_identity` authenticates without resolving a workspace selection.

It exists for the one surface a principal must reach before it has a selection: the switch
endpoints in `me.py`. `require_caller` refuses a multi-membership principal with no header
(`WORKSPACE_SELECTION_REQUIRED`), which is exactly the state a first selection starts from.
"""

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.req("FR-396")


async def test_a_multi_membership_principal_without_a_header_is_authenticated(
    client: AsyncClient, database
):
    # A principal with several memberships and NO Workspace-Id header must still reach
    # a route using IdentityDep — the refusal belongs to require_caller, not to auth.
    ...
```

The test route: declare a throwaway endpoint in the test (or call the dependency directly with a `Request` built via `httpx` against a temporary FastAPI app) that echoes `identity.principal.id` and `sorted(str(w) for w in identity.workspaces)`. Assert: (1) a multi-membership principal with no header gets `200`, not `WORKSPACE_SELECTION_REQUIRED`; (2) the returned membership set matches the seeded rows; (3) no credential and `dev_auth_enabled=False` → `401 UNAUTHENTICATED`.

- [ ] **Step 2: Run the test to verify it fails**

Run: `uv run pytest backend/tests/test_workspace_identity.py -v`
Expected: FAIL — `IdentityDep` is not defined (`NameError` / `ImportError` from `deps.py`).

- [ ] **Step 3: Implement `require_identity`**

In `deps.py`, beside `require_caller`:

```python
@dataclass(frozen=True)
class Identity:
    """An authenticated principal with no workspace selection made.

    `require_caller` resolves a selection and refuses rather than defaulting
    (`FR-397`); this does neither. It exists for the one surface a principal must
    reach before it has a selection — the switch endpoints in `me.py`.
    """

    principal: Principal
    workspaces: frozenset[UUID]


async def require_identity(
    request: Request,
    database: DatabaseDep,
    settings: SettingsDep,
) -> Identity:
    """Authenticate the caller without resolving a workspace selection."""
    # The same credential order `require_caller` uses (:112-127): bearer → apikey → dev.
    # Bearer branch: return the identity `authenticate_bearer` already built — its
    # `workspaces` attribute was read at authentication time; pass it through as-is
    # (frozenset it if it is not one already; do not re-query).
    # Apikey branch: a Service Account has exactly one workspace by construction — that
    # single id is its membership set.
    # Dev branch: build the dev principal exactly as `_development_caller` does today
    # (:185-220, the `x-dev-principal-id` half only — no workspace resolution here), then
    # query `WorkspaceMemberRow.user_id == <dev principal id>` for the membership set.
```

The bearer branch is the only one that must not re-query: `identity.workspaces` is read at authentication time — `authenticate_bearer` loads the memberships from the database (`backend/src/app/auth/service.py:103-113`), and `test_workspace_selection.py:46-50` re-authenticates for exactly this reason — so pass it through as-is rather than inventing a second source.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `uv run pytest backend/tests/test_workspace_identity.py backend/tests/test_workspace_selection.py -v`
Expected: PASS — the new file green, the existing selection tests untouched (they exercise `require_caller`; this adds a sibling, not a change).

- [ ] **Step 5: Commit**

```bash
git add backend/src/app/api/deps.py backend/tests/test_workspace_identity.py
git commit -m "feat(w6b-11): authenticate without a workspace selection"
```

---

### Task 2: `GET /api/v1/me/workspaces` — the memberships list, unscoped

**Files:**
- Modify: `backend/src/app/api/me.py` (add a route beside `get_me`)
- Test: `backend/tests/test_workspace_switch.py` (create — Task 3 adds to it)
- Regenerate: `docs/contracts/openapi/generated.json` (never hand-edited — run the generator, commit its output)

**Interfaces:**
- Consumes: `IdentityDep` (Task 1), `WorkspaceMembership` (`me.py:56-63`)
- Produces: `GET /api/v1/me/workspaces` → `200`, `tuple[WorkspaceMembership, ...]` — consumed by the frontend in Task 5.

- [ ] **Step 1: Write the failing test**

`backend/tests/test_workspace_switch.py`:

```python
"""The switcher's endpoints: the unscoped membership list, and the audited switch."""

import pytest

pytestmark = pytest.mark.req("FR-396")


async def test_the_list_is_readable_without_a_selection(client: AsyncClient, database):
    # A multi-membership principal, NO Workspace-Id header: 200, every membership listed,
    # each carrying its slug and name (FR-395), ordered by name.
    ...
```

Assertions: (1) multi-membership principal, no header → `200` with both memberships, each entry exactly `{workspace_id, slug, name}`; (2) list ordered by `name` (mirror the `ORDER BY WorkspaceRow.name` the existing `/me` query uses, `me.py:118-132`); (3) a Service Account → `200` with `[]` — empty is the designed state, not an error; (4) no credential, `dev_auth_enabled=False` → `401`.

- [ ] **Step 2: Run the test to verify it fails**

Run: `uv run pytest backend/tests/test_workspace_switch.py -v`
Expected: FAIL — `404` (no such route).

- [ ] **Step 3: Implement the route**

In `me.py`, beside `get_me`:

```python
@router.get(
    "/me/workspaces",
    summary="The workspaces this principal may act in",
    responses=problems(401),
)
async def list_workspaces(
    identity: IdentityDep, database: DatabaseDep
) -> tuple[WorkspaceMembership, ...]:
    # The same join the /me memberships query already runs (me.py:118-132), keyed on
    # identity.principal.id, ordered by WorkspaceRow.name — but deliberately NOT scoped:
    # this is the list a first selection is made from, and there is no selection yet.
    ...
```

This route declares **no** `Workspace-Id` header parameter: it is the one surface that must work before a selection exists — the ruling's shape exactly (PR #237, `FR-396`'s second amendment: unscoped, authenticated, list-only).

- [ ] **Step 4: Regenerate the contract and run the tests**

Run: `uv run python scripts/generate-contracts.py && uv run pytest backend/tests/test_workspace_switch.py backend/tests/test_workspace_selection.py -v`
Expected: PASS — and `docs/contracts/openapi/generated.json` now carries `/api/v1/me/workspaces`. Commit the regenerated file with the code (the contract is a published artifact; `generate-contracts.py --check` in CI fails on drift).

- [ ] **Step 5: Commit**

```bash
git add backend/src/app/api/me.py backend/tests/test_workspace_switch.py docs/contracts/openapi/generated.json
git commit -m "feat(w6b-11): the unscoped workspace membership list"
```

---

### Task 3: `POST /api/v1/me/workspace` — the audited switch

**Files:**
- Modify: `backend/src/app/api/me.py` (request shape + route)
- Test: `backend/tests/test_workspace_switch.py` (extend)
- Regenerate: `docs/contracts/openapi/generated.json`

**Interfaces:**
- Consumes: `IdentityDep` (Task 1), `record_switch` (`platform/workspace_switch.py:16-18`, built and tested by W32-7 — **no call site exists anywhere in production code**; this task adds the first one)
- Produces: `POST /api/v1/me/workspace` → `200` `WorkspaceMembership` (the workspace entered); body `{"workspace_id": "<uuid>"}`.

- [ ] **Step 1: Write the failing tests**

Extend `backend/tests/test_workspace_switch.py`. Mirror the `_switch_events` helper of `test_workspace_selection.py:127-144` (selects `AuditEventRow` where `action LIKE 'workspace.%'` ordered by `sequence`):

```python
async def test_a_switch_is_recorded_in_both_chains(client: AsyncClient, database):
    # Principal with memberships A and B; request carries Workspace-Id: A; body names B.
    # Response: 200, B's slug and name. Events: ["workspace.entered", "workspace.left"]
    # in B's and A's chains respectively (the existing record_switch tests at
    # test_workspace_selection.py:148, :168 prove the mechanism; this proves the call site).

async def test_the_first_selection_writes_one_event(client: AsyncClient, database):
    # No Workspace-Id header, body names A → 200, events: ["workspace.entered"] only.
    # FR-396: the first selection after login has no chain to leave.

async def test_a_switch_to_a_non_membership_is_denied(client: AsyncClient, database):
    # Body names a workspace the principal is not a member of → 403 WORKSPACE_SCOPE_DENIED,
    # no audit events.

async def test_a_malformed_header_is_a_platform_refusal_not_a_422(
    client: AsyncClient, database
):
    # Header "Workspace-Id: not-a-uuid" → 403 WORKSPACE_SCOPE_DENIED. Mirror deps.py:94-104:
    # the header parses as str then UUID(), so the refusal stays in the error catalogue.

async def test_reselecting_the_current_workspace_writes_one_event(
    client: AsyncClient, database
):
    # Header names A, body names A → 200, events: ["workspace.entered"] only
    # (record_switch skips the left event when left == entered).

async def test_the_header_is_published_on_the_switch_operation(
    client: AsyncClient, database
):
    # Mirror test_workspace_selection.py:115-:145 — read /openapi.json, assert
    # "/api/v1/me/workspace" exists and its parameters include "Workspace-Id" (optional).
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run pytest backend/tests/test_workspace_switch.py -v`
Expected: FAIL — `404` on the POST (no route yet); the mechanism-only tests keep passing elsewhere.

- [ ] **Step 3: Implement the request shape and the route**

In `me.py`, beside `WorkspaceMembership` (mirror its `frozen=True, extra="forbid"` config):

```python
class SwitchWorkspaceRequest(BaseModel):
    """The workspace a principal chooses to act in (FR-396's fourth obligation)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    workspace_id: UUID
```

Then the route:

```python
@router.post(
    "/me/workspace",
    summary="Choose the workspace to act in",
    responses=problems(401, 403, 422),
)
async def switch_workspace(
    body: SwitchWorkspaceRequest,
    identity: IdentityDep,
    database: DatabaseDep,
    workspace_id: Annotated[
        str | None,
        Header(alias="Workspace-Id", description=WORKSPACE_ID_DESCRIPTION),
    ] = None,
) -> WorkspaceMembership:
    # left: the workspace this request is scoped to, or None — the first selection after
    # login has no chain to leave (FR-396) and record_switch takes left=None for it.
    # 1. Parse the header as UUID (str-then-UUID, mirroring deps.py:94-104, so a malformed
    #    value is WORKSPACE_SCOPE_DENIED, never a bare 422).
    # 2. Refuse unless body.workspace_id is in identity.workspaces → WORKSPACE_SCOPE_DENIED
    #    (mirror deps.py:157-164's message). Refuse a non-None left that is not a
    #    membership the same way.
    # 3. await platform.workspace_switch.record_switch(
    #       database.session?, principal=identity.principal, left=left, entered=body.workspace_id)
    #    — pass the session the handler's own database dependency exposes, the same object
    #    the existing /me query uses.
    # 4. Query the entered WorkspaceRow and return WorkspaceMembership(workspace_id, slug, name).
```

A malformed **body** `workspace_id` is a Pydantic `422` ProblemDetail — that is the platform's standard channel for invalid bodies (the header's str-then-parse exists only to keep *header* refusals in the error catalogue; `FR-397` says nothing about bodies).

- [ ] **Step 4: Regenerate the contract and run the tests**

Run: `uv run python scripts/generate-contracts.py && uv run pytest backend/tests/test_workspace_switch.py backend/tests/test_workspace_selection.py -v`
Expected: PASS — including the publication test, now that the regenerated contract declares `Workspace-Id` on the switch operation. Commit the regenerated `docs/contracts/openapi/generated.json` with the code.

- [ ] **Step 5: Commit**

```bash
git add backend/src/app/api/me.py backend/tests/test_workspace_switch.py docs/contracts/openapi/generated.json
git commit -m "feat(w6b-11): the audited workspace switch"
```

---

### Task 4: The one spec amendment the ruling left — the `FR-397` carve-out

**Files:**
- Modify: `docs/specs/07-platform.md` (append a dated note to `FR-397`, `:81`)

**The ruling already did the rest of the spec work (PR #237, merged):** `FR-396` carries its second decision-maker amendment — the deadlock finding, the ruling, and the refused alternatives — and `06` §5.1 declares both routes. This task adds only the one sentence the ruling did not: `FR-397`'s universal "required in the handler" now has a named exception, and a reader of that row alone would read the switch endpoint as violating it.

- [ ] **Step 1: Append the dated note**

After `FR-397`'s existing amendment (`07-platform.md:81`), append — keeping every prior clause verbatim:

> *Amended 2026-08-25 (W6b-11): the one surface exempt from "required in the handler" is the switch endpoint `POST /api/v1/me/workspace` — there, an absent header **is** the first selection `FR-396`'s fourth obligation names (ruled 2026-08-25, `FR-396`'s amendment of that date), not a forgotten one. Every scoped route keeps the rule.*

- [ ] **Step 2: Run the doc gate**

Run: `python3 scripts/audit-docs.py`
Expected: PASS — the amendment cites only ids already defined (`FR-396`, `FR-397`).

- [ ] **Step 3: Commit**

```bash
git add docs/specs/07-platform.md
git commit -m "docs(w6b-11): name the switch endpoint as the header rule's exception"
```

`07` §5.3 gets **no** row for the selector: the table lists views, and the selector is shell chrome in `App.vue`'s header — stated here so the absence is a decision, not an omission. (The two endpoints are already declared where identity endpoints live, `06` §5.1 — PR #237 filed both rows there; no `07` §5.1 row is added.)

---

### Task 5: `frontend/src/api/me.ts` — the client for the switcher's endpoints

**Files:**
- Create: `frontend/src/api/me.ts`
- Test: `frontend/src/api/__tests__/me.test.ts` (create)

**Interfaces:**
- Consumes: the generated types (`components["schemas"]["WorkspaceMembership"]` — present in the contract after Task 2's regeneration) and `request` (`client.ts:30`)
- Produces: `listWorkspaces(): Promise<WorkspaceMembership[]>` and `switchWorkspace(workspaceId: string): Promise<WorkspaceMembership>` — consumed by Task 6's store.

- [ ] **Step 1: Generate the client and write the failing test**

Run `pnpm --dir frontend generate:api` first — the generated `WorkspaceMembership` type must exist before type-checking. Then `frontend/src/api/__tests__/me.test.ts`, mirroring `client.test.ts`'s `respond`/`vi.stubGlobal("fetch")` style:

```ts
import { afterEach, describe, expect, it, vi } from "vitest";

import { listWorkspaces, switchWorkspace } from "../me";
import { isProblem, ProblemError } from "../problem";

function respond(status: number, body: unknown): void {
  vi.stubGlobal(
    "fetch",
    vi.fn(async () =>
      new Response(body === undefined ? null : JSON.stringify(body), {
        status,
        headers: { "Content-Type": "application/json" },
      }),
    ),
  );
}

afterEach(() => vi.unstubAllGlobals());

describe("the workspace client", () => {
  it("lists the memberships without a selection", async () => {
    respond(200, [{ workspace_id: "…", slug: "ws-…", name: "…" }]);
    expect(await listWorkspaces()).toHaveLength(1);
  });

  it("posts the switch and returns the entered workspace", async () => {
    const entered = { workspace_id: "…", slug: "ws-…", name: "…" };
    respond(200, entered);
    await expect(switchWorkspace(entered.workspace_id)).resolves.toEqual(entered);
    const [, init] = vi.mocked(fetch).mock.calls[0];
    expect(JSON.parse(String(init?.body))).toEqual({ workspace_id: entered.workspace_id });
  });

  it("surfaces a platform refusal as a ProblemError", async () => {
    respond(403, {
      type: "about:blank", title: "Forbidden", status: 403,
      code: "WORKSPACE_SCOPE_DENIED", detail: "…", errors: [],
    });
    await expect(listWorkspaces()).rejects.toSatisfy(
      (e: unknown) => e instanceof ProblemError && isProblem(e) && e.code === "WORKSPACE_SCOPE_DENIED",
    );
  });
});
```

Fill the `…` literals from real UUID shapes in the neighbouring tests — never invent one (a sample uuid is a fixture, and fixtures come from the repo's own tests).

- [ ] **Step 2: Run the test to verify it fails**

Run: `pnpm --dir frontend test -- me.test.ts`
Expected: FAIL — `../me` does not exist.

- [ ] **Step 3: Implement `me.ts`**

```ts
import { request } from "./client";
import type { components } from "./generated/schema";

export type WorkspaceMembership = components["schemas"]["WorkspaceMembership"];

/** Every workspace this principal is a member of, each named. Unscoped, so a first
 *  selection can be made (07 FR-396). */
export function listWorkspaces(): Promise<WorkspaceMembership[]> {
  return request<WorkspaceMembership[]>("/me/workspaces");
}

/** Choose the workspace to act in; the platform audits the switch (07 FR-396). */
export function switchWorkspace(workspaceId: string): Promise<WorkspaceMembership> {
  return request<WorkspaceMembership>("/me/workspace", {
    method: "POST",
    body: { workspace_id: workspaceId },
  });
}
```

- [ ] **Step 4: Run the tests and the type gate**

Run: `pnpm --dir frontend test -- me.test.ts && pnpm --dir frontend type-check`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/api/me.ts frontend/src/api/__tests__/me.test.ts
git commit -m "feat(w6b-11): the workspace switch client"
```

---

### Task 6: The workspace store and the `Workspace-Id` header wiring

**Files:**
- Create: `frontend/src/stores/workspace.ts` (the app's **first** Pinia store — pinia is registered in `main.ts:1,:8` and `grep defineStore` returns nothing today)
- Modify: `frontend/src/api/client.ts` (module-level selection + header)
- Test: `frontend/src/stores/__tests__/workspace.test.ts` (create); `frontend/src/api/__tests__/client.test.ts` (extend)

**Interfaces:**
- Consumes: `listWorkspaces`, `switchWorkspace` (Task 5); `setWorkspaceId` (defined here)
- Produces: `useWorkspaceStore` — `state.workspaces: WorkspaceMembership[]`, `state.current: WorkspaceMembership | null`, `getters.needsSelection`, `actions.load()`, `actions.select(workspaceId)` — consumed by Task 7.

- [ ] **Step 1: Write the failing tests**

`frontend/src/api/__tests__/client.test.ts` — extend, resetting the selection in `afterEach`:

```ts
import { request, setWorkspaceId } from "../client";
// in afterEach: setWorkspaceId(null);

it("sends the Workspace-Id header once a selection exists", async () => {
  setWorkspaceId("ws-uuid");
  respond(200, {});
  await request("/anything");
  const headers = new Headers(vi.mocked(fetch).mock.calls[0][1]?.headers);
  expect(headers.get("Workspace-Id")).toBe("ws-uuid");
});

it("sends no Workspace-Id header with no selection", async () => {
  respond(200, {});
  await request("/anything");
  const headers = new Headers(vi.mocked(fetch).mock.calls[0][1]?.headers);
  expect(headers.has("Workspace-Id")).toBe(false);
});
```

`frontend/src/stores/__tests__/workspace.test.ts` — fresh pinia per test (`createPinia(); setActivePinia(...)`), stubbed `fetch`, `sessionStorage` cleared in `beforeEach` (the vitest environment is happy-dom, which provides it):

```ts
describe("the workspace store", () => {
  it("restores a remembered selection on load and skips it when stale", ...);
  // load() with sessionStorage holding an id that IS in the list → current is it;
  // holding an id that is NOT (membership revoked) → current falls back: the single
  // member if exactly one, else null. A stale remembered id is never sent.

  it("defaults a single membership to the only member", ...);
  // one membership, nothing remembered → current = the member; setWorkspaceId called.

  it("select() posts the switch, remembers it, and reloads", ...);
  // select(id) → fetch called with POST /api/v1/me/workspace and body {workspace_id: id};
  // current = returned membership; sessionStorage written; setWorkspaceId called;
  // window.location.reload() called (spy on it).
});
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `pnpm --dir frontend test -- client.test.ts workspace.test.ts`
Expected: FAIL — `setWorkspaceId` is not exported; the store module does not exist.

- [ ] **Step 3: Add the selection to `client.ts`**

Module level, above `request`:

```ts
let currentWorkspaceId: string | null = null;

/** The workspace subsequent requests act in (07 FR-397). Set by the workspace store;
 *  null sends no header and lets the platform refuse or default (07 FR-396). */
export function setWorkspaceId(id: string | null): void {
  currentWorkspaceId = id;
}
```

In `request()`, after the existing `Idempotency-Key` line:

```ts
  if (currentWorkspaceId) headers["Workspace-Id"] = currentWorkspaceId;
```

The header name is unprefixed, per `FR-397` — deliberately not `x-dev-workspace-id`, which `FR-393` confines to `local`/`dev`.

- [ ] **Step 4: Implement the store**

`frontend/src/stores/workspace.ts`:

```ts
import { defineStore } from "pinia";

import { setWorkspaceId } from "../api/client";
import { listWorkspaces, switchWorkspace, type WorkspaceMembership } from "../api/me";

/** Per-tab, survives a reload, never shared across tabs (sessionStorage): two tabs may
 *  hold two workspaces — the case FR-397's per-request transport exists for — and a
 *  reload restores the selection without a new POST, which is correct under OQ-652:
 *  a switch is a human act, and a reload is not one. */
const STORAGE_KEY = "gi.workspaceId";

export const useWorkspaceStore = defineStore("workspace", {
  state: () => ({
    workspaces: [] as WorkspaceMembership[],
    current: null as WorkspaceMembership | null,
  }),
  getters: {
    needsSelection: (state) => state.workspaces.length > 1,
  },
  actions: {
    async load() {
      this.workspaces = await listWorkspaces();
      const remembered = sessionStorage.getItem(STORAGE_KEY);
      const match = remembered
        ? this.workspaces.find((w) => w.workspace_id === remembered)
        : undefined;
      this.current = match ?? (this.workspaces.length === 1 ? this.workspaces[0] : null);
      setWorkspaceId(this.current?.workspace_id ?? null);
    },
    async select(workspaceId: string) {
      const entered = await switchWorkspace(workspaceId);
      this.current = entered;
      sessionStorage.setItem(STORAGE_KEY, entered.workspace_id);
      setWorkspaceId(entered.workspace_id);
      // Views hold workspace-scoped data; a reload re-fetches under the new header.
      window.location.reload();
    },
  },
});
```

A multi-membership principal with nothing remembered starts with `current = null` and sends no header — the platform refuses scoped requests with `WORKSPACE_SELECTION_REQUIRED` until the user picks, which is the designed safety, never someone else's data (`FR-397`).

- [ ] **Step 5: Run the tests and the type gate**

Run: `pnpm --dir frontend test -- client.test.ts workspace.test.ts && pnpm --dir frontend type-check`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/stores/workspace.ts frontend/src/stores/__tests__/workspace.test.ts frontend/src/api/client.ts frontend/src/api/__tests__/client.test.ts
git commit -m "feat(w6b-11): the workspace store and the Workspace-Id header"
```

---

### Task 7: The shell selector in `App.vue`

**Files:**
- Create: `frontend/src/components/WorkspaceSelector.vue`
- Modify: `frontend/src/App.vue` (mount it in the header)
- Test: `frontend/src/components/__tests__/WorkspaceSelector.test.ts` (create)

**Interfaces:**
- Consumes: `useWorkspaceStore` (Task 6). The selector calls `store.load()` on mount and `store.select(id)` on change; it renders `store.workspaces` and highlights `store.current`.

- [ ] **Step 1: Write the failing test**

`frontend/src/components/__tests__/WorkspaceSelector.test.ts` — `render`/`screen` from `@testing-library/vue` (the style of `SpecProblemList.test.ts`), fresh pinia per test, stubbed `fetch`:

```ts
import { render, screen } from "@testing-library/vue";
import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { useWorkspaceStore } from "@/stores/workspace";
import WorkspaceSelector from "../WorkspaceSelector.vue";

describe("the workspace selector", () => {
  it("loads the memberships on mount and shows the current workspace name", ...);
  // list of two → both names present; current's name shown alongside.

  it("renders nothing when the list is empty", ...);
  // a Service Account has no memberships (me.py:114-117) — an empty list is normal.

  it("calls store.select on change", async () => {
    // fireEvent.change the <select> → the store's select was called with the value;
    // fetch was called with POST /api/v1/me/workspace.
  });
});
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pnpm --dir frontend test -- WorkspaceSelector.test.ts`
Expected: FAIL — the component does not exist.

- [ ] **Step 3: Implement the selector**

`frontend/src/components/WorkspaceSelector.vue`:

```vue
<script setup lang="ts">
import { onMounted } from "vue";

import { useWorkspaceStore } from "@/stores/workspace";

const store = useWorkspaceStore();
onMounted(() => store.load());
</script>

<template>
  <div v-if="store.workspaces.length" class="flex items-center gap-2 text-sm" data-test="workspace-selector">
    <span v-if="store.current" class="text-slate-500">{{ store.current.name }}</span>
    <select
      v-if="store.needsSelection"
      :value="store.current?.workspace_id ?? ''"
      aria-label="Workspace"
      class="rounded border border-slate-300 bg-white px-2 py-1"
      data-test="workspace-select"
      @change="store.select(($event.target as HTMLSelectElement).value)"
    >
      <option v-if="!store.current" value="" disabled>Choose a workspace…</option>
      <option v-for="w in store.workspaces" :key="w.workspace_id" :value="w.workspace_id">
        {{ w.name }}
      </option>
    </select>
  </div>
</template>
```

A native `<select>` is deliberate: it is keyboard-navigable and screen-reader-announced for free, and the prompt option ("Choose a workspace…") is the honest state of a multi-membership principal before its first selection. A single membership shows the name and no control — no selection is needed (`FR-396`).

- [ ] **Step 4: Mount it in the shell**

In `frontend/src/App.vue`'s header `<nav>`, import `WorkspaceSelector` and place it after the existing `RouterLink`s (the header is the natural shell mount — `App.vue` is 42 lines, static today, and holds nothing dynamic yet).

- [ ] **Step 5: Run the tests and the type gate**

Run: `pnpm --dir frontend test -- WorkspaceSelector.test.ts && pnpm --dir frontend type-check`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/components/WorkspaceSelector.vue frontend/src/components/__tests__/WorkspaceSelector.test.ts frontend/src/App.vue
git commit -m "feat(w6b-11): the workspace selector in the shell"
```

---

### Task 8: The dev path adopts the selection, and the pin goes — last

**Files:**
- Modify: `backend/src/app/api/deps.py` (`_development_caller` and the dev-header constants)
- Modify: `frontend/vite.config.ts` (drop the `x-dev-workspace-id` injection)
- Modify: `examples/fremtpl2/seed.py` (drop the now-dead `GIP_DEV_WORKSPACE_ID` export from the print)
- Modify: `docs/specs/07-platform.md` (dated note on the dev-header sentence in `FR-393`)
- Test: `backend/tests/test_workspace_identity.py` (extend — the dev-path cases)

**Interfaces:**
- Consumes: the seeded `workspace_members` rows (W6b-14 Task 3 — built before this slice in the pipeline; the tests here seed their own via fixtures, so this task is self-contained regardless)
- Produces: the dev flow resolves the workspace exactly as the bearer flow does — from the `Workspace-Id` header, checked against memberships.

- [ ] **Step 1: Write the failing tests**

Extend `backend/tests/test_workspace_identity.py` (dev-mode client fixture — mirror how the existing tests flip `dev_auth_enabled`; the dev principal is `x-dev-principal-id` with seeded `WorkspaceMemberRow`s):

```python
async def test_dev_principal_workspace_is_checked_against_memberships(...):
    # dev_auth_enabled=True, x-dev-principal-id set, NO x-dev-workspace-id, Workspace-Id
    # names a membership → the caller's workspace_id is it (the header, not any pin).

async def test_dev_principal_with_several_memberships_and_no_header_is_refused(...):
    # several memberships, no Workspace-Id, no pin → WORKSPACE_SELECTION_REQUIRED (403).
    # Today this request would 401 "both dev headers required"; that refusal goes.

async def test_dev_principal_naming_a_non_membership_is_denied(...):
    # Workspace-Id names a workspace the dev principal is not a member of →
    # WORKSPACE_SCOPE_DENIED (403). The pin must NOT be honoured: a request carrying
    # x-dev-workspace-id naming a non-membership is refused the same way — the pin is
    # gone, not merely unused.
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run pytest backend/tests/test_workspace_identity.py -v`
Expected: FAIL — the dev path still requires both dev headers and ignores `Workspace-Id`.

- [ ] **Step 3: Adopt the selection in `_development_caller`**

In `deps.py`:

- Delete `DEV_WORKSPACE_HEADER` (`:52`) — its last consumer goes in Step 4.
- In `_development_caller` (`:185-220`): keep the `dev_auth_enabled` gate and the `x-dev-principal-id` requirement; **drop** the `x-dev-workspace-id` requirement. Resolve the workspace by querying `WorkspaceMemberRow.user_id == <dev principal id>` and applying the same logic `_select_workspace` (`:130-182`) applies: no memberships → the existing "No workspace access" refusal; header absent + several memberships → `WORKSPACE_SELECTION_REQUIRED`; header naming a non-membership → `WORKSPACE_SCOPE_DENIED`; header absent + exactly one → the single membership; else the header's value.
- Rewrite the comment at `:124-126`: the dev path **now** consumes the same `Workspace-Id` header with the same check — the "different header for a different purpose" sentence describes the code before this task and no longer does. The comment must say so rather than stay stale (`CLAUDE.md` §0: quietly making one match the other destroys the record — a dated sentence keeps it).

The two dev modes now differ only in *authentication*, never in *selection*: a dev request is checked against memberships exactly like a bearer request, which is what makes the switcher exercisable in `local`/`dev` against W6b-14's seeded rows.

- [ ] **Step 4: Remove the pin from the proxy and the seed print**

In `frontend/vite.config.ts` (`:39-69`): delete the `workspace` env read and the `request.setHeader("x-dev-workspace-id", …)` line; update the warning to check `GIP_DEV_PRINCIPAL_ID` alone; update the comment block (it says "putting **these headers** in `client.ts`…" — now one header, injected here because a browser must never choose its own principal; the workspace is chosen in the UI and travels as the verified `Workspace-Id` header, `FR-397`).

In `examples/fremtpl2/seed.py` (`:346-348`): drop the `export GIP_DEV_WORKSPACE_ID=…` line from the printed instructions — the variable is dead once the pin is gone, and a printed instruction pointing at a dead variable misleads the next operator. The `export GIP_DEV_PRINCIPAL_ID=…` line stays: `x-dev-principal-id` goes only when W6b-10 lands real auth, which is not this slice.

- [ ] **Step 5: Amend the dev-header sentence in `FR-393`**

In `07-platform.md`'s `FR-393` row (the sentence naming *"the development identity headers (`x-dev-principal-id`, `x-dev-workspace-id`, injected by the frontend dev proxy)"*), append a dated note:

> *Amended 2026-08-25 (W6b-11): `x-dev-workspace-id` was removed when the workspace selector landed — removal never precedes replacement; the dev path now resolves the workspace from the same verified `Workspace-Id` header as every other request, checked against the seeded memberships. `x-dev-principal-id` remains until `W6b-10` lands real authentication.*

- [ ] **Step 6: Run the backend tests and the doc gate**

Run: `uv run pytest backend/tests/test_workspace_identity.py backend/tests/test_workspace_selection.py -v && python3 scripts/audit-docs.py`
Expected: PASS — the new dev-path tests green, the bearer-path selection tests untouched, the audit clean.

- [ ] **Step 7: Commit**

```bash
git add backend/src/app/api/deps.py backend/tests/test_workspace_identity.py frontend/vite.config.ts examples/fremtpl2/seed.py docs/specs/07-platform.md
git commit -m "feat(w6b-11): the dev path adopts the selection; the workspace pin goes"
```

---

## Self-Review

**1. Spec coverage.** `FR-396` obligation 4 — Tasks 1, 3, 6, 7 (the endpoint, the call, the act); obligations 1–3 and `FR-397` are delivered (WK-692) and consumed — Tasks 6, 8. `FR-395`'s name — rendered by Task 7, carried by Task 2. `OQ-652` option (c) — Task 3's route and Task 6's "a reload is not an act" comment. The pin disposition — Task 8, last. `FR-372`'s per-workspace chains — Task 3's `record_switch` call (mechanism delivered). `FR-394` — recorded as W6b-10's, not built here. **Gaps:** none — Finding 1 was ruled and merged before filing (PR #237), and Tasks 2–4 build against the ruling's exact shape.

**2. Placeholder scan.** The only `…` literals are in Task 5's test sample, with the instruction to take real UUID shapes from neighbouring fixtures rather than inventing them — deliberate, since a sample fixture written from memory is the exact defect the plan conventions call out. No "TBD", no "add appropriate error handling", no step without its code or its command.

**3. Type consistency.** `IdentityDep`/`Identity(principal, workspaces: frozenset[UUID])` defined in Task 1, consumed in Tasks 2–3; `WorkspaceMembership` backend (`me.py:56-63`) and frontend (generated) carry the same three fields (`workspace_id`, `slug`, `name`) and are never re-declared by hand (§2); `listWorkspaces`/`switchWorkspace` (Task 5) are the exact names the store calls (Task 6); `setWorkspaceId` (Task 6) is the exact name `client.ts` exports; the store's `load`/`select`/`needsSelection` are the exact names `WorkspaceSelector.vue` binds (Task 7). The header literal `Workspace-Id` appears once per side and matches `deps.py:86-87` verbatim.

## Verification

`python3 scripts/audit-docs.py` passes at filing (run against this file's own prose — check 2 reads plans). The Python and frontend gates are the executor's per-task step, not this PR's: this PR adds no code, only a plan.

## Open questions

- **Finding 1's ruling** — closed before filing: adopted verbatim, merged as PR #237 (see Finding 1). Nothing here is open.
- **The demo seed's membership count** — W6b-14's Task 3 seeds one workspace; the selector then shows one entry and no selection is needed. A second seeded workspace would exercise the switch end-to-end in the demo. That is W6b-14's seed shape to decide, not this slice's — recorded here so the demo limitation is visible.
