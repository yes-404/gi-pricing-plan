---
id: PL-790
family: plan
kind: leaf
title: W6b-10: Browser Authentication — Implementation Plan
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-08-25
owner: planner
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                     # ids only
was: docs/plans/2026-08-25-w6b-10-browser-auth.md
---

# W6b-10: Browser Authentication — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give the SPA real authentication — an authorization-code-with-PKCE login against the platform's OIDC provider, a bearer token held in memory only, silent renewal that logs out rather than pretending, and, last of all, the `x-dev-principal-id` dev pin removed — removal never precedes replacement.

**Architecture:** The channel is `FR-394`'s: one unauthenticated `GET /api/v1/auth/config` publishes the issuer and `client_id` the flow cannot start without, shaped in `model-schema` and generated onto both sides. The browser half is `oidc-client-ts` (the library `OQ-644`'s decision names as the default candidate), wrapped in a thin in-memory session module — no Pinia store, so the filed W6b-11 plan's claim of "the app's first Pinia store" stays true. The API side is unchanged: it already verifies a bearer token (`FR-393`).

**Tech Stack:** FastAPI + Pydantic v2 · `model-schema` (the shape, per `FR-394`) · Vue 3 + Vite + `oidc-client-ts` (new frontend dependency — a tech-dependency change, `skills-map.md` updates in the same PR) · vitest (happy-dom) + `@testing-library/vue`.

**Spec:** [`../specs/07-platform.md`](../specs/07-platform.md) — `FR-393`, `FR-394`, `FR-398`, `FR-437`; [`../specs/00-overview.md`](../specs/00-overview.md) — `FR-388`'s in-memory rule. The decisions this plan executes are [`../open-questions.md`](../open-questions.md) `OQ-644` (PKCE, 2026-08-15) and `OQ-656` (the channel, decided 2026-08-25 as `FR-394`).

**Anchor:** this plan describes the tree at `11cadbd7` — the tip of `origin/main` when its citations were verified. Nothing this plan cites changed since: the two later commits (`6776d5f`, `d5c5424`) touch only `docs/roadmap.md`. Line numbers are exact at the anchor.

## Global Constraints

- **`FR-393`** — the browser authenticates by OIDC **authorization code with PKCE** against the same provider and discovery document the API verifies against. The SPA is a *public* client: no client secret exists in it, the code verifier never leaves the browser, and **the access token is held in memory only** (`FR-388` — load-bearing per `OQ-644`, not advisory). **Renewal is silent and failure to renew logs the session out rather than retrying indefinitely** — an expired session that looks logged in is how a user comes to believe the platform lost their work. The API side is unchanged: it verifies a bearer token and knows nothing about how the browser obtained it. The development identity headers (`x-dev-principal-id`, `x-dev-workspace-id`, injected by the frontend dev proxy) are not part of this flow and never authenticate anything outside `local`/`dev` — they hang off `dev_auth_enabled`, which is `False` by default and refuses to start in a deployed environment.
- **`FR-394`** (decides `OQ-656`) — the browser learns the issuer and its `client_id` at runtime, from an unauthenticated `GET /api/v1/auth/config`, shaped in `model-schema` and generated onto both sides. Build-time injection is **not** the channel (`FR-437` forecloses it); extending `/version` would hand-write the shape; nothing in the response is a credential. The response also carries `dev_auth_enabled`.
- **`OQ-644`, decided: the client library is WK-664's to choose — `oidc-client-ts` is the default candidate**, and hand-rolling PKCE is defensible only if silent renewal comes with it. This plan takes the default candidate.
- **`FR-398`** — the local provider (W6b-14's) is an **alternative** to `dev_auth_enabled`, never a replacement: both test suites keep running with no container. It ships behind a compose profile and imports a checked-in realm.
- **`FR-437`** — no provider ships in production; a `prod` deployment refuses to start with no configured issuer. The SPA must never assume a provider exists outside `local`/`dev`.
- **The disposition (manager, 2026-08-25, verbatim):** *"Pin removal splits: `x-dev-principal-id` goes when W6b-10 lands real auth; `x-dev-workspace-id` goes when W6b-11 lands the switcher. Removal never precedes replacement."* This slice removes the principal pin; the workspace pin is W6b-11's (already planned there).

## Scope, dependencies, and what this slice deliberately does not do

**In scope (this slice):**

1. `oidc_client_id` in `Settings` — the field `FR-394` presupposes and no artifact has (env `GIP_OIDC_CLIENT_ID`, default `""`, matching the existing `oidc_*` trio).
2. `GET /api/v1/auth/config` — the unauthenticated endpoint, shaped in `model-schema`, on the `/version` precedent; its §5.1 declaration row; contract regeneration.
3. The browser flow — `oidc-client-ts` behind a thin in-memory session module: login, logout, silent renewal via `prompt=none`, boot bootstrap, router guard, and a minimal sign-in/sign-out control in the shell.
4. The `Authorization: Bearer` wiring in `client.ts`, from the in-memory session.
5. Removal of the `x-dev-principal-id` pin — the Vite proxy injection and the seed's export print — **last**, after the real flow works; plus the dated spec notes the removal forces.

**Out of scope (by disposition and by the boundary W6b-14 drew):**

- The provider, the realm, the seeded users, the seed membership rows — **W6b-14's** (its plan commits `deploy/keycloak-local/` and `ensure_member`).
- The workspace pin `x-dev-workspace-id` — **W6b-11's** Task 8 (its plan is filed; this slice leaves the proxy's workspace injection alone — with a real bearer token, `deps.py`'s credential order ignores the dev headers anyway).
- The backend's dev path (`_development_caller`, `deps.py:185-220`) — backend tests and local backend dev authenticate through it, `FR-393` confines it to `local`/`dev`, and nothing in the browser uses it after this slice. It stays.
- A BFF / session cookie — `OQ-644` parked that until Phase 3.
- The W6b-11 workspace selector and its store — W6b-11 **waits on** this slice, not the reverse.

**Dependency record.** `W6b-10` depends on **`W6b-14`**: end-to-end, the flow exercises only against a running provider with the checked-in realm, and the seeded membership is what makes the login land in a workspace. The tasks below are nevertheless self-contained: backend tests assert the config endpoint against `Settings`; frontend tests stub `fetch` and mock the `UserManager` (both test suites keep running with no container — `FR-398`). Build order: **W6b-14 → W6b-10 → W6b-11**. The demo consequence: local browser development after Task 7 requires the auth profile (`docker compose --profile auth up`) and the `GIP_OIDC_*` environment — which is exactly `FR-398`'s designed world ("a contributor working on the browser login starts four").

## Findings

**Finding 1 — the SPA had no route to the issuer or the client id; ruled, and this plan builds the ruling.** `FR-393` specifies the flow but not its bootstrap: a discovery document resolves the provider's endpoints only once the issuer is known and never carries a `client_id`. W6b-14's Finding 3 raised it and routed it; `OQ-656` was decided 2026-08-25 as `FR-394` — the unauthenticated `GET /api/v1/auth/config`, with the census that settled it: *"no `oidc_client_id` exists anywhere — `config.py` has `oidc_issuer`, `oidc_audience`, `oidc_jwks_url`, `oidc_jwks_ttl_s`, `dev_auth_enabled` and no other"*. Tasks 1–2 build the channel; the §5.1 row the requirement implies is Task 2's.

**Finding 2 — the `Settings` object the response draws from is missing the field the response publishes.** `FR-394` says "the value the browser is told and the value the API verifies against come from one `Settings` object" — but that object has no `client_id` (Finding 1's census). Task 1 adds it; the deployed value must match the realm's client id `gi-pricing-frontend` (W6b-14's Task 2). In `local`, W6b-14's compose profile supplies the other three `GIP_OIDC_*` variables; the client id joins them. Task 1 also records why the field stays out of `oidc_configured` (`config.py:209-211`) — that property gates the API's own verification, which needs no client id.

**Finding 3 — this slice's own pin removal supersedes half of `FR-394`'s sentence.** "…so one bundle can tell whether to start a login or trust the dev proxy" presupposes the principal pin this slice removes. After Task 7 there is no dev proxy to trust: the SPA always logs in, and `dev_auth_enabled` in the response remains for backend dev mode and because `FR-394`'s shape publishes it. Task 7's dated note records this; the shape does not change.

**Finding 4 — the realm plan is silent on refresh tokens; silent renewal holds either way.** W6b-14's Task 2 Produces block declares the client's grants: PKCE `S256`, `http://localhost:5173/*` redirect URIs, `aud: gi-pricing-api` — and says nothing about refresh tokens (a full-plan sweep finds no `refresh` or `offline` mention). The mechanism here does not depend on that silence: `signinSilent` renews silently whether or not the session carries a refresh token — via the stored token when one exists (Keycloak's default grants one), via `prompt=none` in a hidden iframe against a `silent_redirect_uri` route in the same SPA otherwise. Failure to renew → logout, exactly `FR-393`'s sentence.

**Finding 5 — the filed W6b-11 plan claims its store will be the app's first Pinia store; this plan must not falsify it.** Pinia is registered in `main.ts` but no store exists. W6b-11's Task 6 files `workspace.ts` as "the app's **first** Pinia store". The session state here is deliberately a module singleton (in-memory by requirement anyway, framework-independent, and `oidc-client-ts` is not Vue-bound) — recorded so the executor does not "improve" the plan into a Pinia store and strand a filed claim.

---

### Task 1: `oidc_client_id` in Settings

**Files:**
- Modify: `backend/src/app/config.py` (add the field after the `oidc_*` trio at `:140-142`)
- Test: `backend/tests/test_config.py` (extend — the `load_settings`-style tests at `:70-85`)

**Interfaces:**
- Consumes: the existing `oidc_*` field pattern (`config.py:140-142`) and the `env_prefix="GIP_"` binding (`config.py:91-92`)
- Produces: `Settings.oidc_client_id: str` (default `""`, env `GIP_OIDC_CLIENT_ID`) — consumed by Task 2's endpoint.

- [ ] **Step 1: Write the failing tests**

In `backend/tests/test_config.py`, beside the `FR-391` startup tests (`:70-85`), which build `Settings` through `load_settings` with explicit kwargs:

```python
def test_the_oidc_client_id_is_configured_like_its_siblings() -> None:
    settings = load_settings(
        environment=Environment.LOCAL,
        oidc_client_id="gi-pricing-frontend",
    )
    assert settings.oidc_client_id == "gi-pricing-frontend"


def test_the_oidc_client_id_defaults_empty_like_the_rest_of_the_trio() -> None:
    assert load_settings(environment=Environment.LOCAL).oidc_client_id == ""
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run pytest backend/tests/test_config.py -v`
Expected: FAIL — pydantic refuses the unknown `oidc_client_id` kwarg, so the first test errors on construction.

- [ ] **Step 3: Implement the field**

In `config.py`, after `oidc_jwks_url` (`:142`), the same pattern as its siblings — a plain `str` with default `""`; the `GIP_OIDC_CLIENT_ID` env var binds automatically through the `model_config` at `:91-92`, no alias needed:

```python
    # The browser flow's client id (FR-394). The API's own verification does not
    # need it, so it is not part of `oidc_configured` — joining it there would refuse
    # an API-only deployment over a value only the SPA uses.
    oidc_client_id: str = ""
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `uv run pytest backend/tests/test_config.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/src/app/config.py backend/tests/test_config.py
git commit -m "feat(w6b-10): the oidc client id setting"
```

---

### Task 2: `GET /api/v1/auth/config` — the shape in `model-schema`, the endpoint beside `/version`

**Files:**
- Create: `packages/model-schema/src/model_schema/auth.py` (the shape — `model-schema` is the single source of truth, `CLAUDE.md` §2)
- Modify: `packages/model-schema/src/model_schema/__init__.py` (re-export, beside `ActorKind` — the import list at `:90`, `__all__` at `:318`)
- Modify: `scripts/generate-contracts.py` (register the shape in `GENERATED_SHAPES`, `:38` — an unregistered model gets no committed contract, and `build_schemas` (`:164-186`) only iterates that map)
- Create: `backend/src/app/api/auth_config.py` (the route builder — `health.version_route`'s pattern, `health.py:123-133`)
- Modify: `backend/src/app/main.py` (import at `:18-34`, mount beside `/version` at `:124-131`)
- Create: `backend/tests/test_api_auth.py`
- Test: `packages/model-schema/tests/test_auth.py` (create — every `model-schema` shape carries its tests there)
- Modify: `docs/specs/07-platform.md` (§5.1, after the health row at `:300`)
- Regenerate: `docs/contracts/openapi/generated.json` and `docs/contracts/schemas/generated/oidc-auth-config.schema.json` (generated, never hand-edited)

**Interfaces:**
- Consumes: `Settings.oidc_issuer` (`config.py:140`), `Settings.oidc_client_id` (Task 1), `Settings.dev_auth_enabled` (`config.py:153`); the `/version` unauthenticated pattern
- Produces: `GET /api/v1/auth/config` → `200` `{issuer: str, client_id: str, dev_auth_enabled: bool}` — consumed by Task 3's bootstrap.

- [ ] **Step 1: Write the failing tests**

`backend/tests/test_api_auth.py` — the plain `client` fixture (`conftest.py:31-34`) builds a DB-free app with `Settings(environment=Environment.LOCAL, version="test")`, which is exactly what an unauthenticated test needs (the `/version` test at `test_health.py:87-89` proves no credential is required on such a route):

```python
"""FR-394 — the unauthenticated values the browser login needs to start.

The channel exists because the flow cannot start with an auth gate: the issuer and the
client_id are what a *public* client publishes, and nothing here is a credential.
"""

from fastapi.testclient import TestClient

from app.config import Environment, Settings
from app.main import create_app


def test_the_auth_config_publishes_the_flow_s_bootstrap_values() -> None:
    app = create_app(
        Settings(
            environment=Environment.LOCAL,
            version="test",
            oidc_issuer="https://idp.example/realms/gip",
            oidc_client_id="gi-pricing-frontend",
            dev_auth_enabled=True,
        )
    )
    with TestClient(app, raise_server_exceptions=False) as client:
        body = client.get("/api/v1/auth/config").json()
    assert body == {
        "issuer": "https://idp.example/realms/gip",
        "client_id": "gi-pricing-frontend",
        "dev_auth_enabled": True,
    }


def test_the_auth_config_answers_with_no_credential_at_all(client: TestClient) -> None:
    """The flow cannot start with an auth gate — no dependency, so no 401, no dev header."""
    body = client.get("/api/v1/auth/config").json()
    assert body == {"issuer": "", "client_id": "", "dev_auth_enabled": False}
```

A publication test, mirroring `test_the_header_is_published_on_an_operation` (`test_workspace_selection.py:117-130`) — the generated client is the reason a route must be declared rather than assumed:

```python
def test_the_auth_config_is_published_in_the_contract(api_client: TestClient) -> None:
    document = api_client.get("/openapi.json").json()
    schema = document["paths"]["/api/v1/auth/config"]["get"]["responses"]["200"]["content"][
        "application/json"
    ]["schema"]
    assert schema["$ref"] == "#/components/schemas/OidcAuthConfig"
```

`packages/model-schema/tests/test_auth.py`:

```python
"""`OidcAuthConfig` — the shape `07` FR-394 publishes (`07` §5.1)."""

import pytest
from pydantic import ValidationError

from model_schema import OidcAuthConfig


def test_every_value_the_flow_needs_is_required() -> None:
    with pytest.raises(ValidationError):
        OidcAuthConfig.model_validate({"issuer": "https://idp.example/realms/gip"})


def test_a_full_config_round_trips() -> None:
    model = OidcAuthConfig.model_validate(
        {
            "issuer": "https://idp.example/realms/gip",
            "client_id": "gi-pricing-frontend",
            "dev_auth_enabled": True,
        }
    )
    assert model.model_dump() == {
        "issuer": "https://idp.example/realms/gip",
        "client_id": "gi-pricing-frontend",
        "dev_auth_enabled": True,
    }
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run pytest backend/tests/test_api_auth.py packages/model-schema/tests/test_auth.py -v`
Expected: FAIL — `404` on the route, and `OidcAuthConfig` is not exported by `model_schema`.

- [ ] **Step 3: Declare the shape in `model-schema`**

`packages/model-schema/src/model_schema/auth.py` — a frozen pydantic model in the house style (`perils.py`'s models use the same `model_config`):

```python
"""The values the browser OIDC login needs before it can start (`07` FR-394).

Public by design: the issuer and the client_id are what a *public* client publishes
(FR-393, OQ-644), and nothing here is a credential.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

__all__ = ["OidcAuthConfig"]


class OidcAuthConfig(BaseModel):
    """The unauthenticated `/api/v1/auth/config` payload — `07` §5.1."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    issuer: str
    client_id: str
    dev_auth_enabled: bool
```

In `__init__.py`, add `from model_schema.auth import OidcAuthConfig` beside the `ActorKind` import (`:90`) and `"OidcAuthConfig"` to the `__all__` list (`:318`).

In `scripts/generate-contracts.py`, register it at the end of `GENERATED_SHAPES` (`:38`):

```python
    # Added 2026-08-25 (W6b-10, browser auth). No hand-authored Phase-0 counterpart —
    # FR-394 names the shape's contents, so this is its first written form.
    "oidc-auth-config": "OidcAuthConfig",
```

- [ ] **Step 4: Implement the endpoint**

`backend/src/app/api/auth_config.py` — the `version_route` closure pattern (`health.py:123-133`), bound to the loaded settings and mounted in `main.py`:

```python
"""The unauthenticated OIDC bootstrap values the browser login needs (FR-394).

One route, built the way `/version` is (`health.version_route`, `main.py:124-131`): a
closure bound to the loaded settings, mounted in `main.py`. Deliberately **no** auth
dependency — the channel exists because the flow cannot start with an auth gate, and
nothing here is a credential.
"""

from __future__ import annotations

from collections.abc import Callable

from app.config import Settings
from model_schema import OidcAuthConfig

__all__ = ["auth_config_route"]


def auth_config_route(settings: Settings) -> Callable[[], OidcAuthConfig]:
    """Build the `/api/v1/auth/config` handler bound to the loaded settings."""

    def auth_config() -> OidcAuthConfig:
        return OidcAuthConfig(
            issuer=settings.oidc_issuer,
            client_id=settings.oidc_client_id,
            dev_auth_enabled=settings.dev_auth_enabled,
        )

    return auth_config
```

In `main.py`: add `auth_config` to the `from app.api import (...)` list (`:18-34`, after `audit` — the list is alphabetical), `from model_schema import OidcAuthConfig` beside the other imports (the `me.py:29` import is the precedent for importing `model_schema` classes), and mount the route directly after the `/version` block (`:124-131`):

```python
    app.add_api_route(
        f"{API_PREFIX}/auth/config",
        auth_config.auth_config_route(settings),
        methods=["GET"],
        tags=["platform"],
        summary="The OIDC values the browser login needs",
        response_model=OidcAuthConfig,
    )
```

`/version` is mounted without the prefix; this route is **not** — `FR-394` declares `/api/v1/auth/config`, so the `f"{API_PREFIX}/..."` form is the one that publishes the declared path.

- [ ] **Step 5: Declare the §5.1 row**

In `07-platform.md`'s §5.1 table, after the health row (`:300`):

| `GET` | `/api/v1/auth/config` | The OIDC issuer and client id the browser login needs, unauthenticated (FR-394) |

- [ ] **Step 6: Regenerate the contract and run the tests**

Run: `uv run python scripts/generate-contracts.py && uv run python scripts/generate-contracts.py --check && uv run pytest backend/tests/test_api_auth.py packages/model-schema/tests/test_auth.py -v`
Expected: PASS — including the publication test. Commit the regenerated `openapi/generated.json` and `schemas/generated/oidc-auth-config.schema.json` with the code (CI's `--check` fails on drift, and the conformance test at `test_contracts.py:102` compares the committed schema against the model).

- [ ] **Step 7: Commit**

```bash
git add packages/model-schema/src/model_schema/auth.py packages/model-schema/src/model_schema/__init__.py packages/model-schema/tests/test_auth.py scripts/generate-contracts.py backend/src/app/api/auth_config.py backend/src/app/main.py backend/tests/test_api_auth.py docs/specs/07-platform.md docs/contracts/openapi/generated.json docs/contracts/schemas/generated/oidc-auth-config.schema.json
git commit -m "feat(w6b-10): the unauthenticated auth config channel"
```

---

### Task 3: `oidc-client-ts`, the generated type, and the config bootstrap

**Files:**
- Modify: `frontend/package.json` (`pnpm --dir frontend add oidc-client-ts`)
- Modify: `docs/skills-map.md` (two edits — the §1 OIDC row at `:40`, and a new §5 row after `:120`)
- Create: `frontend/src/auth/config.ts`
- Test: `frontend/src/auth/__tests__/config.test.ts` (create)

**Interfaces:**
- Consumes: the generated `components["schemas"]["OidcAuthConfig"]` (in the contract after Task 2) and `request` (`client.ts:30`)
- Produces: `loadAuthConfig(): Promise<OidcAuthConfig>` — memoized, one fetch per page load — consumed by Task 4.

- [ ] **Step 1: Add the dependency and generate the client**

Run: `pnpm --dir frontend add oidc-client-ts && pnpm --dir frontend generate:api`
The first installs the library `OQ-644` names; the second makes the generated `OidcAuthConfig` type exist for the type gate.

- [ ] **Step 2: Write the failing test**

`frontend/src/auth/__tests__/config.test.ts` — the `respond`/`vi.stubGlobal("fetch")` style of `client.test.ts` (its `respond` helper is at `:6`):

```ts
import { afterEach, describe, expect, it, vi } from "vitest";

import { loadAuthConfig } from "../config";

function respond(status: number, body: unknown): void {
  vi.stubGlobal(
    "fetch",
    vi.fn(async () =>
      new Response(JSON.stringify(body), {
        status,
        headers: { "Content-Type": "application/json" },
      }),
    ),
  );
}

afterEach(() => vi.unstubAllGlobals());

describe("the auth config bootstrap", () => {
  it("fetches the config once and memoizes it", async () => {
    const cfg = {
      issuer: "http://localhost:8080/realms/gi-pricing",
      client_id: "gi-pricing-frontend",
      dev_auth_enabled: true,
    };
    respond(200, cfg);
    expect(await loadAuthConfig()).toEqual(cfg);
    expect(await loadAuthConfig()).toEqual(cfg);
    expect(vi.mocked(fetch)).toHaveBeenCalledTimes(1);
  });

  it("surfaces a failed fetch as a ProblemError", async () => {
    respond(503, { title: "Service Unavailable", status: 503, detail: "…", errors: [] });
    await expect(loadAuthConfig()).rejects.toThrow();
  });
});
```

The issuer literal is the W6b-14 realm's published issuer (`docs/plans/PL-00793-w6b-14-the-local-oidc-provider-implementation-plan.md:243`) — a fixture taken from the repo's own plans, not invented.

- [ ] **Step 3: Run the test to verify it fails**

Run: `pnpm --dir frontend test -- config.test.ts`
Expected: FAIL — `../config` does not exist.

- [ ] **Step 4: Implement the bootstrap**

```ts
import { request } from "../api/client";
import type { components } from "../api/generated/schema";

export type OidcAuthConfig = components["schemas"]["OidcAuthConfig"];

let cached: OidcAuthConfig | null = null;

/** The issuer and client_id the PKCE flow cannot start without (07 FR-394).
 *  Fetched once per page load; the values are public by design. */
export async function loadAuthConfig(): Promise<OidcAuthConfig> {
  cached ??= await request<OidcAuthConfig>("/auth/config");
  return cached;
}
```

`request` prefixes `BASE` (`/api/v1`, `client.ts:18`), so the unprefixed path is the correct one.

- [ ] **Step 5: Update `docs/skills-map.md` and run the gates**

`docs/skills-map.md` — a tech-dependency change rides with the slice (`CLAUDE.md` §10), two edits:

1. In the §1 OIDC row (`:40`), the Skills cell's closing sentences — *"**Library choice is WK-664's** — `oidc-client-ts` is the default candidate, and hand-rolling PKCE is defensible only if silent renewal comes with it. Until WK-664 ships, only the frontend dev proxy reaches the API from a browser"* — are false the moment this slice lands. Replace them with: *"**Chosen by W6b-10 (2026-08-25): `oidc-client-ts`**, the default candidate `OQ-644` named — behind `frontend/src/auth/`, with `FR-394`'s config channel as the bootstrap. Until then only the frontend dev proxy reached the API from a browser; its principal pin goes with W6b-10, the workspace pin with W6b-11."*
2. Append a row to §5's table (after `openapi-typescript`, `:120`):

| oidc-client-ts | 07 FR-393, `frontend/src/auth/` | ★★ | `UserManager` settings, silent renewal by `prompt=none` iframe (the realm plan is silent on refresh tokens — Finding 4), `InMemoryWebStorage` (the `FR-388` load-bearing rule), the expiring/renew-error events | [oidc-client-ts docs](https://github.com/authts/oidc-client-ts) |

Then:

Run: `pnpm --dir frontend test -- config.test.ts && pnpm --dir frontend type-check`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add frontend/package.json frontend/pnpm-lock.yaml frontend/src/auth/config.ts frontend/src/auth/__tests__/config.test.ts docs/skills-map.md
git commit -m "feat(w6b-10): the oidc client dependency and the auth config bootstrap"
```

---

### Task 4: The session module — `UserManager` behind an in-memory singleton

**Files:**
- Create: `frontend/src/auth/oidc.ts` (the `UserManager` factory + redirect completion)
- Create: `frontend/src/auth/session.ts` (the in-memory session singleton — **not** a Pinia store; Finding 5)
- Test: `frontend/src/auth/__tests__/session.test.ts` (create)

**Interfaces:**
- Consumes: `loadAuthConfig` (Task 3), `oidc-client-ts` (`UserManager`, `User`, `InMemoryWebStorage`), `setAccessToken`/`clearAccessToken` (Task 5 — the call sites are textual; the functions land in the next task's commit, so this task's tests stub `client.ts`)
- Produces: `initSession(): Promise<User | null>`, `signIn(): Promise<void>`, `signOut(): Promise<void>`, `completeRedirectIfPresent(): Promise<User | null>`, `completeSilentRenew(): Promise<void>`, `currentUser: User | null`, `useSessionUser()` (reactive, for rendering), `isSignedIn(): boolean` — consumed by Tasks 5–7.

- [ ] **Step 1: Write the failing tests**

`frontend/src/auth/__tests__/session.test.ts` — `vi.mock("oidc-client-ts", ...)` with a stub `UserManager` whose methods are `vi.fn()`s, and `vi.mock("../../api/client", ...)` for the token setters (the mock's relative path resolves to `src/api/client`, the module the real code imports):

```ts
import { beforeEach, describe, expect, it, vi } from "vitest";

const managerStub = {
  getUser: vi.fn(),
  signinRedirect: vi.fn(),
  signinRedirectCallback: vi.fn(),
  signinSilent: vi.fn(),
  signinSilentCallback: vi.fn(),
  signoutRedirect: vi.fn(),
  events: {
    addUserLoaded: vi.fn(),
    addAccessTokenExpiring: vi.fn(),
    addSilentRenewError: vi.fn(),
    addUserSignedOut: vi.fn(),
  },
};
vi.mock("oidc-client-ts", () => ({
  UserManager: vi.fn(() => managerStub),
  InMemoryWebStorage: vi.fn(),
  Log: { setLevel: vi.fn() },
}));
vi.mock("../../api/client", () => ({ setAccessToken: vi.fn(), clearAccessToken: vi.fn() }));
vi.mock("../config", () => ({
  loadAuthConfig: vi.fn(async () => ({
    issuer: "http://localhost:8080/realms/gi-pricing",
    client_id: "gi-pricing-frontend",
    dev_auth_enabled: true,
  })),
}));

import { initSession, signIn, signOut, completeSilentRenew, currentUser } from "../session";
import { setAccessToken, clearAccessToken } from "../../api/client";
import { UserManager, InMemoryWebStorage } from "oidc-client-ts";

beforeEach(() => {
  vi.clearAllMocks();
});

describe("the auth session", () => {
  it("builds the manager from the config with memory-only storage", async () => {
    await initSession();
    const settings = vi.mocked(UserManager).mock.calls[0][0];
    expect(settings).toMatchObject({
      authority: "http://localhost:8080/realms/gi-pricing",
      client_id: "gi-pricing-frontend",
      response_type: "code",
      automaticSilentRenew: true,
    });
    expect(settings.userStore).toBeInstanceOf(InMemoryWebStorage);
  });

  it("pushes the bearer token into the api client on user load, clears on unload", async () => {
    await initSession();
    const onLoaded = vi.mocked(managerStub.events.addUserLoaded).mock.calls[0][0];
    const onSignedOut = vi.mocked(managerStub.events.addUserSignedOut).mock.calls[0][0];
    onLoaded({ access_token: "t" });
    expect(setAccessToken).toHaveBeenCalledWith("t");
    onSignedOut();
    expect(clearAccessToken).toHaveBeenCalled();
  });

  it("renews silently when the token approaches expiry, and logs out when renewal fails", async () => {
    await initSession();
    const onExpiring = vi.mocked(managerStub.events.addAccessTokenExpiring).mock.calls[0][0];
    const onRenewError = vi.mocked(managerStub.events.addSilentRenewError).mock.calls[0][0];
    onExpiring();
    expect(managerStub.signinSilent).toHaveBeenCalled();
    onRenewError();
    // FR-393's sentence: failure to renew logs the session out rather than
    // retrying indefinitely — an expired session that looks logged in is worse.
    expect(managerStub.signoutRedirect).toHaveBeenCalled();
  });

  it("signIn redirects, signOut redirects through the provider", async () => {
    await initSession();
    await signIn();
    expect(managerStub.signinRedirect).toHaveBeenCalled();
    await signOut();
    expect(managerStub.signoutRedirect).toHaveBeenCalled();
  });
});
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `pnpm --dir frontend test -- session.test.ts`
Expected: FAIL — `../session` does not exist.

- [ ] **Step 3: Implement `oidc.ts`**

```ts
import { InMemoryWebStorage, Log, UserManager, type User } from "oidc-client-ts";

import type { OidcAuthConfig } from "./config";

/** The UserManager settings FR-393's clauses imply: code+PKCE, memory-only storage,
 *  silent renewal by prompt=none iframe (the realm plan is silent on refresh tokens — Finding 4). */
export function buildManager(config: OidcAuthConfig): UserManager {
  Log.setLevel(Log.INFO);
  return new UserManager({
    authority: config.issuer,
    client_id: config.client_id,
    redirect_uri: `${window.location.origin}/callback`,
    silent_redirect_uri: `${window.location.origin}/silent-renew`,
    response_type: "code",
    scope: "openid profile email",
    userStore: new InMemoryWebStorage(),
    automaticSilentRenew: true,
    accessTokenExpiringNotificationTimeInSeconds: 60,
  });
}

/** Process a redirect callback; no-op when the URL carries no code/state. */
export async function completeSignin(manager: UserManager): Promise<User | null> {
  if (!new URLSearchParams(window.location.search).has("code")) return null;
  const user = await manager.signinRedirectCallback();
  window.history.replaceState({}, "", window.location.pathname);
  return user;
}
```

The `redirect_uri` path `/callback` and `silent_redirect_uri` path `/silent-renew` are SPA routes (Task 6) and fall under the realm's `http://localhost:5173/*` wildcard — the realm needs no change.

- [ ] **Step 4: Implement `session.ts`**

```ts
import { readonly, ref } from "vue";
import type { User, UserManager } from "oidc-client-ts";

import { clearAccessToken, setAccessToken } from "../api/client";
import { loadAuthConfig } from "./config";
import { buildManager, completeSignin } from "./oidc";

/** The session is in memory only (FR-388, load-bearing per OQ-644): a hard reload
 *  clears it, and the boot sequence (Task 6) restores it through a silent provider check —
 *  an act of the provider session, not of storage. A module singleton, not a Pinia store:
 *  the filed W6b-11 plan owns the app's first store (Finding 5). */
export let currentUser: User | null = null;

const userRef = ref<User | null>(null);

/** Reactive view of the session for rendering; `currentUser` is the guard's plain read. */
export function useSessionUser() {
  return readonly(userRef);
}

export const isSignedIn = (): boolean => currentUser !== null;

let manager: UserManager | null = null;

function adopt(user: User | null): void {
  currentUser = user;
  userRef.value = user;
  if (user) setAccessToken(user.access_token);
  else clearAccessToken();
}

export async function initSession(): Promise<User | null> {
  manager = buildManager(await loadAuthConfig());
  manager.events.addUserLoaded((user) => adopt(user));
  manager.events.addUserSignedOut(() => adopt(null));
  manager.events.addAccessTokenExpiring(() => {
    // FR-393: renewal is silent; a hard reload alone would look logged-out.
    void manager?.signinSilent();
  });
  manager.events.addSilentRenewError(() => {
    // An expired session that looks logged in is how a user comes to believe the
    // platform lost their work — so failure logs out (FR-393's sentence).
    void manager?.signoutRedirect();
  });
  const user = await manager.getUser();
  if (user) adopt(user);
  return user;
}

export async function signIn(): Promise<void> {
  await manager?.signinRedirect();
}

export async function signOut(): Promise<void> {
  await manager?.signoutRedirect();
}

export async function completeRedirectIfPresent(): Promise<User | null> {
  return manager ? completeSignin(manager) : null;
}

export async function completeSilentRenew(): Promise<void> {
  if (!manager) return;
  await manager.signinSilentCallback();
}
```

`initSession` is called once from the boot sequence (Task 6); `signIn` is the guard's and the shell's action. Tests invoke the registered event handlers through the stub's `events` map.

- [ ] **Step 5: Run the tests and the type gate**

Run: `pnpm --dir frontend test -- session.test.ts && pnpm --dir frontend type-check`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/auth/oidc.ts frontend/src/auth/session.ts frontend/src/auth/__tests__/session.test.ts
git commit -m "feat(w6b-10): the in-memory auth session"
```

---

### Task 5: The `Authorization` header in `client.ts`

**Files:**
- Modify: `frontend/src/api/client.ts` (module-level token + header — the headers block is at `:38-40`, `request` at `:30`)
- Test: `frontend/src/api/__tests__/client.test.ts` (extend — its `respond` helper at `:6` builds the fetch stub the assertions read)

**Interfaces:**
- Consumes: nothing new (the session calls into this, never the reverse — no import cycle)
- Produces: `setAccessToken(token: string | null): void`, `clearAccessToken(): void` — the exact names Task 4's stub mocks.

- [ ] **Step 1: Write the failing tests**

In `client.test.ts`, resetting the token in `afterEach`:

```ts
import { request, setAccessToken, clearAccessToken } from "../client";

it("sends Authorization: Bearer once a session token exists", async () => {
  setAccessToken("some-token");
  respond(200, {});
  await request("/anything");
  const headers = new Headers(vi.mocked(fetch).mock.calls[0][1]?.headers);
  expect(headers.get("Authorization")).toBe("Bearer some-token");
});

it("sends no Authorization header with no token, and clearAccessToken removes it", async () => {
  respond(200, {});
  await request("/anything");
  expect(new Headers(vi.mocked(fetch).mock.calls[0][1]?.headers).has("Authorization")).toBe(false);
  setAccessToken("t");
  clearAccessToken();
  respond(200, {});
  await request("/anything");
  expect(new Headers(vi.mocked(fetch).mock.calls[1][1]?.headers).has("Authorization")).toBe(false);
});
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `pnpm --dir frontend test -- client.test.ts`
Expected: FAIL — `setAccessToken` is not exported.

- [ ] **Step 3: Implement**

Module level, above `request` (`:30`):

```ts
let currentAccessToken: string | null = null;

/** The bearer token subsequent requests carry (07 FR-393). Set by the auth session;
 *  null sends no Authorization header and lets the platform refuse (07 §3.7). */
export function setAccessToken(token: string | null): void {
  currentAccessToken = token;
}

export function clearAccessToken(): void {
  currentAccessToken = null;
}
```

And in the headers block (`:38-40`), after the `Idempotency-Key` line:

```ts
  if (currentAccessToken) headers["Authorization"] = `Bearer ${currentAccessToken}`;
```

The client still knows no data shapes and no auth *flow* — it carries a token it was handed, which is the same hand-off shape W6b-11's plan gives the workspace header.

- [ ] **Step 4: Run the tests and the type gate**

Run: `pnpm --dir frontend test -- client.test.ts && pnpm --dir frontend type-check`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/api/client.ts frontend/src/api/__tests__/client.test.ts
git commit -m "feat(w6b-10): the bearer token in the api client"
```

---

### Task 6: The boot sequence, the guard, and the shell control

**Files:**
- Modify: `frontend/src/main.ts` (await the bootstrap before the mount at `:8`)
- Create: `frontend/src/auth/bootstrap.ts`
- Modify: `frontend/src/router/index.ts` (guard + `meta.requiresAuth`; two routes before the `createRouter` export at the tail)
- Create: `frontend/src/views/SigninCallback.vue`, `frontend/src/views/SilentRenew.vue`, `frontend/src/components/AuthControl.vue`
- Modify: `frontend/src/App.vue` (embed the control in the header nav, after the Reference `RouterLink`)
- Test: `frontend/src/auth/__tests__/bootstrap.test.ts`, `frontend/src/router/__tests__/guard.test.ts`, `frontend/src/components/__tests__/AuthControl.test.ts` (create)

**Interfaces:**
- Consumes: `initSession`, `signIn`, `signOut`, `isSignedIn`, `completeRedirectIfPresent`, `completeSilentRenew`, `useSessionUser` (Tasks 4–5)
- Produces: the app boots into a session; guarded routes redirect to the provider; the shell shows the signed-in state.

- [ ] **Step 1: Write the failing tests**

`frontend/src/auth/__tests__/bootstrap.test.ts` — mock the session module (`vi.mock("../session", ...)` resolves to the same module `bootstrap.ts` imports) and assert the boot order and the failure behaviour:

```ts
import { beforeEach, describe, expect, it, vi } from "vitest";

const mocks = {
  completeRedirectIfPresent: vi.fn(async () => null),
  initSession: vi.fn(async () => null),
};
vi.mock("../session", () => mocks);

import { bootstrap } from "../bootstrap";

describe("the auth bootstrap", () => {
  beforeEach(() => vi.clearAllMocks());

  it("processes a redirect callback, then initializes", async () => {
    await bootstrap();
    expect(mocks.completeRedirectIfPresent).toHaveBeenCalled();
    expect(mocks.initSession).toHaveBeenCalled();
  });

  it("continues to boot anonymous when the bootstrap fails", async () => {
    mocks.initSession.mockRejectedValueOnce(new Error("config refused"));
    await expect(bootstrap()).resolves.toBeUndefined();
  });
});
```

`frontend/src/router/__tests__/guard.test.ts` — the real `router` from `index.ts` (the guard registers at module load), the session module mocked (from this file the specifier is `../../auth/session`):

```ts
import { beforeEach, describe, expect, it, vi } from "vitest";

const mocks = { isSignedIn: vi.fn(), signIn: vi.fn(async () => {}) };
vi.mock("../../auth/session", () => mocks);

import { router } from "../index";

beforeEach(() => {
  vi.clearAllMocks();
});

describe("the auth guard", () => {
  it("lets a signed-in user through", async () => {
    mocks.isSignedIn.mockReturnValue(true);
    await router.push("/data");
    expect(mocks.signIn).not.toHaveBeenCalled();
    expect(router.currentRoute.value.path).toBe("/data");
  });

  it("redirects an anonymous visitor to the provider via signIn", async () => {
    mocks.isSignedIn.mockReturnValue(false);
    await router.push("/data");
    expect(mocks.signIn).toHaveBeenCalled();
  });
});
```

`frontend/src/components/__tests__/AuthControl.test.ts` — `render`/`screen` from `@testing-library/vue`, the session mocked (from this file, `../../auth/session`):

```ts
import { readonly, ref } from "vue";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/vue";
import userEvent from "@testing-library/user-event";

const user = ref<{ profile?: { name?: string } } | null>(null);
const mocks = {
  useSessionUser: () => readonly(user),
  signIn: vi.fn(async () => {}),
  signOut: vi.fn(async () => {}),
};
vi.mock("../../auth/session", () => mocks);

import AuthControl from "../AuthControl.vue";

describe("the auth control", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    user.value = null;
  });

  it("shows Sign in when anonymous and calls signIn on click", async () => {
    render(AuthControl);
    await userEvent.click(screen.getByRole("button", { name: "Sign in" }));
    expect(mocks.signIn).toHaveBeenCalled();
  });

  it("shows the user's name and Sign out when signed in, calling signOut on click", async () => {
    user.value = { profile: { name: "A. Analyst" } };
    render(AuthControl);
    expect(screen.getByText("A. Analyst")).toBeTruthy();
    await userEvent.click(screen.getByRole("button", { name: "Sign out" }));
    expect(mocks.signOut).toHaveBeenCalled();
  });
});
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `pnpm --dir frontend test -- bootstrap.test.ts guard.test.ts AuthControl.test.ts`
Expected: FAIL — the modules and components do not exist.

- [ ] **Step 3: Implement the bootstrap and the two views**

`frontend/src/auth/bootstrap.ts`:

```ts
import { completeRedirectIfPresent, initSession } from "./session";

/** Runs once before the app mounts: finish a redirect the provider just sent us,
 *  then establish the session (memory-only; the silent provider check restores it). */
export async function bootstrap(): Promise<void> {
  try {
    await completeRedirectIfPresent();
    await initSession();
  } catch (error) {
    // A failed bootstrap (the platform is down, the config fetch refused) must not leave
    // a blank page: mount anonymous, and the guard's sign-in attempt fails loudly at the
    // provider rather than silently here.
    console.error("auth bootstrap failed; continuing without a session", error);
  }
}
```

`frontend/src/views/SigninCallback.vue` — the `/callback` route (Task 4's `redirect_uri`):

```vue
<script setup lang="ts">
import { onMounted } from "vue";
import { useRouter } from "vue-router";

import { completeRedirectIfPresent } from "../auth/session";

const router = useRouter();

onMounted(async () => {
  await completeRedirectIfPresent();
  await router.push({ name: "datasets" });
});
</script>

<template>
  <p class="text-sm text-slate-600">Signing in…</p>
</template>
```

`frontend/src/views/SilentRenew.vue` — the `/silent-renew` route (Task 4's `silent_redirect_uri`):

```vue
<script setup lang="ts">
import { onMounted } from "vue";

import { completeSilentRenew } from "../auth/session";

onMounted(async () => {
  await completeSilentRenew();
});
</script>

<template>
  <div />
</template>
```

In `frontend/src/main.ts` (the mount is at `:8`; adapt to the file's actual import order):

```ts
import { bootstrap } from "./auth/bootstrap";

// The session is memory-only (FR-388): every hard reload boots anonymous and the
// provider check inside initSession restores the sign-in — a provider act, not storage,
// and exactly why the token must never reach localStorage.
await bootstrap();
```

- [ ] **Step 4: Implement the guard and the shell control**

In `router/index.ts`, register the guard after the `router` export:

```ts
router.beforeEach((to) => {
  if (to.meta.requiresAuth && !isSignedIn()) {
    void signIn(); // redirects the whole page to the provider
    return false;
  }
  return true;
});
```

With the imports `import { isSignedIn, signIn } from "../auth/session";`.

Add `meta: { requiresAuth: true }` to every route in the array **except**:

- `/demo` — `FR-408`'s entrance is routed unconditionally; the view reads the API's answer as a state (the comment already on that entry says exactly this),
- the two new auth routes below.

And append the two routes before the `createRouter` export:

```ts
  {
    // The OIDC redirect target (Task 4's `redirect_uri`). Never guarded — the guard's
    // refusal is what sent the browser out, and a guarded callback is an unclosable loop.
    path: "/callback",
    name: "auth-callback",
    component: () => import("@/views/SigninCallback.vue"),
  },
  {
    // The silent-renewal iframe target (Task 4's `silent_redirect_uri`). Never guarded —
    // the iframe's `prompt=none` request must land on a page that only completes it.
    path: "/silent-renew",
    name: "silent-renew",
    component: () => import("@/views/SilentRenew.vue"),
  },
```

`frontend/src/components/AuthControl.vue` — the sign-in/sign-out control the header embeds:

```vue
<script setup lang="ts">
import { computed } from "vue";

import { signIn, signOut, useSessionUser } from "../auth/session";

const user = useSessionUser();
const name = computed(() => user.value?.profile.name ?? "Signed in");
</script>

<template>
  <button
    v-if="!user"
    type="button"
    class="text-sm text-slate-600 hover:text-slate-900"
    @click="signIn"
  >
    Sign in
  </button>
  <span v-else class="flex items-center gap-4">
    <span class="text-sm text-slate-600">{{ name }}</span>
    <button
      type="button"
      class="text-sm text-slate-600 hover:text-slate-900"
      @click="signOut"
    >
      Sign out
    </button>
  </span>
</template>
```

In `App.vue`: add `import AuthControl from "./components/AuthControl.vue";` to the `<script setup>` block, and after the Reference `RouterLink` inside the header `<nav>`:

```vue
        <AuthControl class="ml-auto" />
```

- [ ] **Step 5: Run the tests and the type gate**

Run: `pnpm --dir frontend test -- bootstrap.test.ts guard.test.ts AuthControl.test.ts && pnpm --dir frontend type-check`
Expected: PASS. No test imports `main.ts` (views and components render standalone), so the top-level `await bootstrap()` fires only in the real boot.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/main.ts frontend/src/auth/bootstrap.ts frontend/src/auth/__tests__/bootstrap.test.ts frontend/src/router/index.ts frontend/src/router/__tests__/guard.test.ts frontend/src/views/SigninCallback.vue frontend/src/views/SilentRenew.vue frontend/src/components/AuthControl.vue frontend/src/components/__tests__/AuthControl.test.ts frontend/src/App.vue
git commit -m "feat(w6b-10): the sign-in boot sequence and shell control"
```

---

### Task 7: The principal pin goes — last, never before the replacement works

**Files:**
- Modify: `frontend/vite.config.ts` (drop the `x-dev-principal-id` injection — the proxy block at `:53-69`)
- Modify: `examples/fremtpl2/seed.py` (drop the dead `GIP_DEV_PRINCIPAL_ID` export from the print, `:347`)
- Modify: `docs/specs/07-platform.md` (dated notes on `FR-393` (`:77`) and `FR-394` (`:78`))

**Interfaces:**
- Consumes: nothing new — the real flow (Tasks 3–6) is the replacement this task requires to exist first
- Produces: the dev proxy no longer asserts an identity on the browser's behalf; local browser dev authenticates through the real flow against W6b-14's provider (`docker compose --profile auth up` + the `GIP_OIDC_*` variables), which is `FR-398`'s designed world. The backend dev path (`deps.py:185-220`) is untouched — backend tests and local backend dev still authenticate through `x-dev-principal-id`, which stays honoured there.

**Why there is no failing test first.** This task deletes, and the suites assert nothing about the deleted lines — verified at the anchor: no test in either `backend/tests/` or `frontend/src/` reads `vite.config.ts`, and the proxy headers appear in no fixture (the backend tests that exercise the dev path import `DEV_PRINCIPAL_HEADER` from `deps.py`, which this task does not touch). The filed W6b-11 plan's Task 8 removes the sibling pin the same way — no invariant test, the gate is the untouched dev-path suite. The removal's verification is the Tasks 3–6 flow itself plus Step 4's gates; a test that greps a config file would be the only one of its shape in either suite.

- [ ] **Step 1: Remove the principal pin from the proxy**

In `frontend/vite.config.ts` (`:53-69`): delete the `principal` env read (`:54`) and the `request.setHeader("x-dev-principal-id", …)` line (`:65`). The workspace lines stay — W6b-11's Task 8 removes them, and this slice must not collide with a filed plan. Update the warning (`:57-59`) to check `GIP_DEV_WORKSPACE_ID` alone, and replace the comment's closing sentence — *"Real OIDC in the SPA is a later workstream's work."* — with: *"Real OIDC in the SPA landed with W6b-10 — the browser authenticates through the real flow; this proxy injects only the workspace pin, which goes when W6b-11 lands the selector (removal never precedes replacement)."*

- [ ] **Step 2: Drop the dead export from the seed print**

In `examples/fremtpl2/seed.py` (`:347`): delete the `export GIP_DEV_PRINCIPAL_ID=…` line. The `export GIP_DEV_WORKSPACE_ID=…` line stays — W6b-11's Task 8 removes it. A printed instruction pointing at a dead variable misleads the next operator; that is why the line goes with the pin, not later.

- [ ] **Step 3: The dated spec notes**

On `FR-393` (`07-platform.md:77`), after the existing dev-header sentence, append:

> *Amended 2026-08-25 (W6b-10): `x-dev-principal-id` was removed when the browser's real authorization-code-with-PKCE flow landed — removal never precedes replacement. The proxy injects no principal any more; the backend dev path the header served stays, confined to `local`/`dev` exactly as the row says. `x-dev-workspace-id` goes when `W6b-11` lands the workspace selector.*

On `FR-394` (`07-platform.md:78`), append:

> *Amended 2026-08-25 (W6b-10): the "trust the dev proxy" half of the sentence above died with this slice's own pin removal — there is no dev proxy identity to trust any more, and the SPA always logs in. `dev_auth_enabled` stays in the response: `FR-394`'s shape publishes it and backend dev mode is its consumer.*

- [ ] **Step 4: Run the gates**

Run: `uv run pytest backend/tests/test_api_me.py backend/tests/test_api_authorisation_sweep.py backend/tests/test_demo_guide.py backend/tests/test_config.py -v && python3 scripts/audit-docs.py && pnpm --dir frontend type-check`
Expected: PASS — the dev-path tests prove the backend still honours `x-dev-principal-id` where it is legitimate, and the audit covers the spec edits.

- [ ] **Step 5: Commit**

```bash
git add frontend/vite.config.ts examples/fremtpl2/seed.py docs/specs/07-platform.md
git commit -m "feat(w6b-10): the principal pin goes; the browser logs in"
```

---

## Self-Review

**1. Spec coverage.** `FR-394` — Tasks 1, 2 (the channel, the shape, the §5.1 row, the contract), 3 (the bootstrap), 7 (the dated note). `FR-393` — Tasks 3–6 (PKCE, in-memory token, silent renewal, logout-on-failure), 7 (the pin). `FR-388` — Task 4's memory-only store and its comment. `FR-398` — recorded in the dependency section and Task 7's world. `FR-437` — Global Constraints; nothing bakes an issuer into the bundle (Task 3 fetches it). The disposition — Task 7, last. `OQ-644` — Task 3's library choice is its named default. `OQ-656` — decided as `FR-394`; Finding 1 records it. **Gaps:** none — Finding 1 was ruled before filing, and the remaining findings each own a task.

**2. Placeholder scan.** The only `…` literals are the test fixture's `detail: "…"` (the neighbouring tests' exact shape) and the ellipses inside cited text ("`request.setHeader("x-dev-principal-id", …)`", "…so one bundle can tell…") which are prose elisions in this document, not instructions to the executor. No "TBD", no step without its code or its command.

**3. Type consistency.** `OidcAuthConfig` is defined in `model-schema` (Task 2), registered in `GENERATED_SHAPES` (Task 2), re-exported from the generated client (Task 3), consumed by `buildManager` (Task 4); `setAccessToken`/`clearAccessToken` are defined in Task 5 and are the exact names Task 4's tests mock; `initSession`/`signIn`/`signOut`/`isSignedIn`/`completeRedirectIfPresent`/`completeSilentRenew`/`useSessionUser` are the exact names Tasks 6's tests mock; the `/callback` and `/silent-renew` routes Task 6 registers are the exact URIs Task 4's manager settings point at. The issuer fixture is W6b-14's published realm issuer, not an invented URL.

## Verification

`python3 scripts/audit-docs.py` passes at filing (run against this file's own prose — check 2 reads plans). The Python and frontend gates are the executor's per-task steps, not this PR's: this PR adds no code, only a plan.

## Open questions

- **Demo guide treatment** — once W6b-10 and W6b-11 land, the one-command demo (`examples/`, `FR-439`) must say when the auth profile and the `GIP_OIDC_*` variables are needed. Which slice owns that sentence is the next slice-map revision's to make; recorded here so the demo limitation is visible.
- **`Log.setLevel`** — `oidc-client-ts` logs at INFO by default; if the team wants quieter logs, one line in `oidc.ts` changes it. Not a decision this plan needs.
