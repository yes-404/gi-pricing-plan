---
id: PL-793
family: plan
kind: leaf
title: W6b-14 — The Local OIDC Provider Implementation Plan
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-08-25
owner: planner
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                     # ids only
was: docs/plans/2026-08-25-w6b-14-local-oidc-provider.md
---

# W6b-14 — The Local OIDC Provider Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a local OIDC provider behind an opt-in compose profile, with a checked-in
realm whose demo user resolves into the seeded freMTPL2 workspace — so that `FR-393`'s
browser login has something real to authenticate against.

**Architecture:** A fourth compose service (Keycloak) that starts only under
`--profile auth`, importing a realm committed to `deploy/keycloak-local/`. The realm declares
one public PKCE client for the SPA and puts the API in the token's `aud`. A new
`ensure_member` beside `ensure_workspace` in `app/platform/workspaces.py` writes the `users`
and `workspace_members` rows a bearer login needs, and `examples/fremtpl2/seed.py` calls it —
so a real login resolves to the *same principal id* the dev-header path already uses and
inherits its role assignments rather than needing its own.

**Tech Stack:** Docker Compose v2 · Keycloak · PostgreSQL 16 (existing) · SQLAlchemy 2.x async ·
pytest. **No Vue and no frontend change at all** — see §Out of scope.

**Spec:** [`../specs/07-platform.md`](../specs/07-platform.md) — `FR-398` is the whole of
this slice; `FR-387`, `FR-388`, `FR-390`, `FR-393`, `FR-437` and `NFR-529`
bound it.

---

## Global Constraints

Copied verbatim from `FR-398` (`docs/specs/07-platform.md:81`), which is this slice's
entire requirement:

- **"A local OIDC provider ships with the compose stack, behind an opt-in profile."**
- **"A contributor running the test suites starts the same three containers as today, and a
  contributor working on the browser login starts four."**
- **"It imports a checked-in realm — a public client with PKCE and no secret, the dev-server
  redirect URIs, and an API audience equal to the configured `oidc_audience`."**
- **"Its demo users must resolve into the seeded workspace, and today they cannot … so the
  seed grants membership keyed on the realm's issuer and subject."**
- **"This is an alternative to `dev_auth_enabled`, never a replacement: both test suites keep
  running with no container, because a test suite that needs an identity provider running is
  one that stops being run."**

Two consequences that bind every task:

- **Every test this slice adds asserts against a checked-in file or against the database,
  never against a running provider.** The container is verified by hand, once, in the steps
  that say so — never by the suite.
- **`deploy/docker-compose.yml` carries its own rule** (lines 3-5): *"Services arrive as the
  workstreams that use them do — an unused container in the compose file is a claim the
  platform does not yet support, and it makes `docker compose up` slower for no benefit."*
  `FR-398` quotes that rule as the reason for the profile. The profile is what makes a
  fourth container honest.

This slice adds no schema, no endpoint and no `model-schema` shape, so §2's generated-contract
rules are not engaged.

---

## Preconditions and dependencies

**W6b-14 has no unmet dependency.** The revised slice map lists it among the slices that can
start today and its dependency column is empty. What depends on *it* is `W6b-10`, the PKCE
flow.

Verified against the repository while writing, all four:

| Claim | Verified by |
|---|---|
| No provider in the stack | `deploy/docker-compose.yml` declares `postgres`, `redis`, `minio` and nothing else |
| No OIDC configuration | `backend/src/app/config.py:140-142` — `oidc_issuer`, `oidc_audience`, `oidc_jwks_url` all default to `""` |
| The verification half is built | `backend/src/app/auth/oidc.py` — asymmetric algorithms only |
| The demo would authenticate into zero workspaces | `backend/src/app/auth/service.py:105-110` reads memberships; `examples/fremtpl2/seed.py:302-326` writes role assignments and no membership |

---

## Out of scope, and why

- **The browser flow.** `FR-393` is `W6b-10`. This slice makes it possible; it does not
  start it. Nothing under `frontend/` changes.
- **How the SPA learns the issuer and client id.** Finding 3. A real `§0` gap, **routed to
  `w6b-decision-maker`** and not decided here — a compose profile and a realm publish nothing
  to a browser, so W6b-14 does not close it and must not appear to.
- **The reference production deployment.** `FR-437` (`07-platform.md:145`) decides
  `OQ-645`'s production half: no identity provider ships in the production stack, and
  `deploy/` carries a **reference** Keycloak deployment the deployer operates, patches and is
  accountable for — **owned by WK-674**, *"with the rest of `deploy/` beyond compose."* See
  Finding 7 for the directory-name consequence.
- **Group-to-role mapping.** `FR-350` (`06-governance.md:86`) decided it and marked it
  **Phase 3**. The realm this slice commits carries a user and a client; it maps no groups.
- **An API to create memberships.** Deliberately absent, and recorded as such — Finding 2.

---

## Findings

### Finding 1 — the seeded workspace has no `workspaces` row, and `ensure_workspace` has zero production callers

`backend/src/app/platform/workspaces.py` describes itself as *"the idempotent ensure the seeds
and the test suite need."* Swept repository-wide: **every call site is under `backend/tests/`**.
`examples/fremtpl2/seed.py` does not call it, and no other production path does. So the seeded
freMTPL2 workspace has a `workspace_id` and no row.

**Why that has been invisible.** `RoleRow.workspace_id` is a plain column with **no foreign
key** (`backend/src/app/db/models.py:538`), so `rbac.seed_builtin_roles` and the seed's role
assignments insert happily against a workspace that does not exist.
`WorkspaceMemberRow.workspace_id` **is** a foreign key to `workspaces.id`
(`models.py:481-483`) — `test_workspace_selection.py:63` carries the comment *"A membership
names a workspace that exists (FR-395's foreign key)"* — so the very first membership row
is what makes the missing parent fatal. Task 3 must create the workspace before the
membership, and would fail on the FK if it did not.

A second consequence: `GET /api/v1/me` joins `WorkspaceRow` to render the list
(`backend/src/app/api/me.py:121-127`), so that endpoint would return an **empty** list for the
demo workspace even once a membership existed. Task 3 fixes it as a side effect, which is
worth saying out loud because it is `W6b-11`'s precondition arriving in a slice that does not
name it.

**Verdict: delivered by this slice** (Task 3), for the demo path only. The general question —
what calls `ensure_workspace` when a workspace is created by something other than a seed — is
answered by the module's own docstring: *"A Workspace is created by provisioning, which `06`
owns and which does not exist yet."* That is **not started, owner `06`**, and correctly
outside this phase.

### Finding 2 — the absence of a membership writer is a recorded decision, not a gap

`WorkspaceMemberRow` is constructed in test modules and nowhere else. The obvious reading is
that membership granting was forgotten. It was not: `models.py:472-476` states it as a
decision — *"There is deliberately **no API to create these in WK-658**. Self-service membership
would make authentication sufficient for access, which is precisely what FR-390 forbids.
Provisioning arrives with the governance write path (WK-659, FR-345)."*

Recorded because the sweep that finds it looks exactly like a defect discovery, and filing it
as one would have proposed re-opening a settled decision. **Verdict: not started, owner WK-659 /
`FR-345`.** Untouched by this slice, which writes the demo's membership from a seed rather
than from an API — the shape that decision permits.

### Finding 3 — the SPA still has no route to the issuer or the client id, and this slice does not change that

`FR-393` requires the browser to authenticate *"against the same provider and discovery
document the API verifies against"* and says nothing about how the browser learns which one
that is. Measured:

- `docs/specs/07-platform.md` §5.1 publishes no configuration or discovery endpoint.
- `frontend/src/` contains **one** `import.meta.env` reference — `ChartFigure.vue:61`, a `DEV`
  guard — and **no** `.env` file at any level.
- It cannot be a build-time constant: `FR-437` puts production on a deployer's own
  provider, so a value baked into the bundle would be wrong for every deployment but this one.

W6b-14 supplies the *values*; nothing supplies the *channel*. **Routed to
`w6b-decision-maker` as a `§0` gap** — a capability `FR-393` needs and no requirement
specifies — and deliberately **not given an OQ number here**, because minting one in a plan
would put an id in the suite that `open-questions.md` does not carry. **Verdict: deferred,
owner maintainer via `w6b-decision-maker`**; it blocks `W6b-10`, not this slice.

### Finding 4 — Keycloak's management port collides with MinIO's published port

MinIO publishes `9000:9000` (`deploy/docker-compose.yml:42`). Recent Keycloak serves health
and metrics on a separate **management** interface on port 9000 inside the container. Nothing
breaks while that port is **not published to the host**, and this plan does not publish it —
the healthcheck runs *inside* the container. Stated because the natural debugging move when a
healthcheck misbehaves is to publish the port and look at it, and on this stack that move
takes MinIO down.

### Finding 5 — the API is not containerised, so there is exactly one provider URL

The classic local-OIDC failure is an issuer mismatch: the browser reaches the provider at
`localhost` and the backend reaches it at a service name, so the `iss` claim the backend
verifies never matches the one the token carries. **It cannot arise here.** The API is not in
the compose file; `scripts/demo.py:189` starts the three containers and then runs the API as a
host process on `API_PORT = 8000` (`scripts/demo.py:48`). Browser and backend reach Keycloak at
the same `localhost` URL, and one issuer value is correct for both.

Recorded rather than left implicit because it is why this plan can put a single issuer in
`deploy/README.md`, and because it **stops being true** the moment the API is containerised —
at which point the realm and the backend settings need the two-URL treatment, and whoever
containerises the API needs to know that.

### Finding 6 — the seeded user id must be reused, not defaulted

`authenticate_bearer` resolves the principal through `_upsert_user`
(`backend/src/app/auth/service.py:103`, defined at `:124`), which keys on `(issuer, subject)`;
`UserRow.id` defaults to a fresh UUIDv7 (`models.py:361`). The seed's role assignments are
written against `analyst.id` (`examples/fremtpl2/seed.py:303`, granted at `:325`).

So if Task 3 inserts a `UserRow` and lets the id default, an OIDC login produces a principal
with a **different id** from the one holding the role assignments: authenticated, a member of
the workspace, and authorised for nothing. `ensure_member` therefore takes the principal id as
an argument and passes it as `UserRow.id`.

`FR-398` gestures at this — *"mints principals with fresh identifiers and grants them role
assignments, while `authenticate_bearer` keys a user on `(issuer, subject)`"* — but states the
remedy only as *"the seed grants membership keyed on the realm's issuer and subject."*
Membership alone yields a demo user who can open the workspace and do nothing in it. The id
reuse is the part that makes the demo work, and Task 3 Step 1 tests it by that predicate.

### Finding 7 — `deploy/keycloak/` is a name WK-674 will want, so this slice does not take it

`FR-437` gives WK-674 a **reference** Keycloak deployment under `deploy/`, *"with the rest of
`deploy/` beyond compose"* — and its whole decision is the distinction between a local provider
this project ships and a production one it explicitly does not secure on a deployer's behalf. A
directory called `deploy/keycloak/` holding a `sslRequired: "none"` realm with a password in it
is exactly the artifact that distinction exists to prevent being confused, and
`deploy/keycloak/` is the name WK-674's reference deployment will reach for first.

This slice therefore uses **`deploy/keycloak-local/`**, leaving `deploy/keycloak/` free.
**Verdict: not started, owner WK-674** for the reference deployment itself. The cost of the
choice is one hyphen; the cost of the collision is a local dev realm read as a production
example.

---

## File structure

| File | Change | Task |
|---|---|---|
| `deploy/docker-compose.yml` | Add the `keycloak` service under `profiles: ["auth"]` | 1 |
| `tests/test_repository_invariants.py` | Add the two `FR-398` artifact invariants | 1, 2 |
| `deploy/keycloak-local/realm-gi-pricing.json` | Create — the checked-in realm | 2 |
| `backend/src/app/platform/workspaces.py` | Add `ensure_member` beside `ensure_workspace` | 3 |
| `backend/tests/test_workspace_members.py` | Create — the rows a bearer login needs | 3 |
| `examples/fremtpl2/seed.py` | Call `ensure_workspace` then `ensure_member` | 3 |
| `deploy/README.md` | Document the profile, the settings and the login | 4 |
| `docs/specs/07-platform.md` | Amend `FR-387`; `FR-398` discharged | 5 |

**Why the helper lives in `workspaces.py` and not in the seed.** `ensure_workspace`'s module
docstring already claims this exact job — *"the idempotent ensure the seeds and the test suite
need"* — and the seed cannot host a testable function: `examples/` has no `__init__.py`, and
`examples/fremtpl2/test_seed.py:15-17` reaches its subject through `sys.path.insert(...)` plus
`from seed import …`, a pattern that gets no database fixture because `conftest_db.py` is under
`backend/tests/`. Putting it where `ensure_workspace` already is makes it importable, testable
with the normal fixtures, and adjacent to the FK ordering it depends on.

---

## The names this slice fixes

Chosen once, here, because four files must agree and a mismatch surfaces as an authentication
failure with no useful message. Derived from `name: gi-pricing`
(`deploy/docker-compose.yml:7`) so nothing is arbitrary:

| Name | Value | Used by |
|---|---|---|
| Realm | `gi-pricing` | realm JSON, issuer URL |
| Issuer | `http://localhost:8080/realms/gi-pricing` | `GIP_OIDC_ISSUER`, `REALM_ISSUER` |
| JWKS | `http://localhost:8080/realms/gi-pricing/protocol/openid-connect/certs` | `GIP_OIDC_JWKS_URL` |
| SPA client id | `gi-pricing-frontend` | realm JSON; `W6b-10` needs it |
| API audience | `gi-pricing-api` | `GIP_OIDC_AUDIENCE`, and the realm's audience mapper |
| Demo user | `analyst@example.fr` | matches `seed.py:303`'s display |
| Host port | `8080` | free: 5432, 6379, 9000, 9001 are compose's, 8000 the API's, 5173 the frontend's (`scripts/demo.py:48-49`) |

The env prefix is `GIP_` (`backend/src/app/config.py:92`), so the three settings at
`config.py:140-142` are `GIP_OIDC_ISSUER`, `GIP_OIDC_AUDIENCE` and `GIP_OIDC_JWKS_URL`.

---

## Task 1: The compose profile

**Files:**
- Modify: `deploy/docker-compose.yml` (insert before the `volumes:` block at line 50)
- Test: `tests/test_repository_invariants.py`

**Interfaces:**
- Consumes: nothing.
- Produces: a service `keycloak` at `http://localhost:8080`, started only by
  `docker compose --profile auth up`. Task 2 mounts a realm into it; Task 4 documents it.

- [ ] **Step 1: Pin the image tag from the registry rather than from memory**

Do not write a tag from recall. Ask the registry and record the answer:

```bash
curl -s "https://quay.io/api/v1/repository/keycloak/keycloak/tag/?limit=20&onlyActiveTags=true" | python3 -c "import json,sys; [print(t['name']) for t in json.load(sys.stdin)['tags']]"
```

Pick the highest stable major and pin `quay.io/keycloak/keycloak:<major>`, matching the
loose-major house style of `postgres:16-alpine` and `redis:7-alpine`. **Write the tag you
actually saw into the compose file and into the commit message.** If the registry is
unreachable, stop and say so — a guessed tag is the failure this step exists to prevent.

- [ ] **Step 2: Write the failing test**

Add to `tests/test_repository_invariants.py`, beside the existing
`test_the_full_stack_is_declared_for_local_use` (`:61-77`). Mirror that test's style
deliberately: it reads the compose file as **text** via the module's `ROOT` constant (`:23`)
and asserts substrings, because PyYAML is not a dependency of this repository. Do not add one
for a test. The module already uses `@pytest.mark.req` throughout (eleven markers) and
`--strict-markers` is on (`pyproject.toml:109`), so the marker must be spelled exactly.

```python
@pytest.mark.req("FR-398")
def test_the_local_provider_is_declared_behind_an_opt_in_profile() -> None:
    """FR-398: a local OIDC provider ships with the stack, behind an opt-in profile.

    The profile is the requirement, not a detail of it -- FR-398 says a contributor
    running the test suites starts the same three containers as today. A `keycloak` service
    with no `profiles:` key satisfies the first half of the requirement and breaks the
    second, and the two are one line apart in the file.
    """
    compose = (ROOT / "deploy" / "docker-compose.yml").read_text(encoding="utf-8")
    assert "keycloak:" in compose
    assert "profiles:" in compose, "the provider must not start by default"
    # The realm is imported, not hand-configured -- FR-398's reproducibility half.
    assert "--import-realm" in compose
    # deploy/keycloak/ is left free for WK-674's reference deployment (FR-437).
    assert (ROOT / "deploy" / "keycloak-local" / "realm-gi-pricing.json").is_file()
```

- [ ] **Step 3: Run it and watch it fail**

```bash
uv run pytest tests/test_repository_invariants.py::test_the_local_provider_is_declared_behind_an_opt_in_profile -q
```

Expected: **FAIL** on the first assertion, `assert "keycloak:" in compose` — no such service is
declared. **Record the assertion that fired.** If it fails anywhere else the working tree is
not what this plan was written against; stop and report that rather than proceeding. A pass
here means the test is not testing anything.

- [ ] **Step 4: Add the service**

Insert before `volumes:` (line 50). Inline-flow `ports:` and `volumes:` match the file's
existing style (`:42-43`). Substitute the tag from Step 1:

```yaml
  # The local identity provider (FR-398), behind an opt-in profile.
  #
  # Not in the default `up`: this file's own rule is that an unused container is a claim the
  # platform does not support, and three of the four services are needed by every
  # contributor while this one is needed only by someone working on the browser login.
  # `--profile auth` is the difference between three containers and four.
  #
  # `start-dev` is deliberate. It runs HTTP-only against a dev-mode database, which is right
  # for a provider whose entire purpose is local, and refuses to be mistaken for the
  # production deployment FR-437 says this project does not ship.
  keycloak:
    profiles: ["auth"]
    image: quay.io/keycloak/keycloak:<TAG FROM STEP 1>
    command: ["start-dev", "--import-realm"]
    environment:
      KC_BOOTSTRAP_ADMIN_USERNAME: admin
      KC_BOOTSTRAP_ADMIN_PASSWORD: admin      # local only, as with postgres above
      KC_HEALTH_ENABLED: "true"
    ports: ["8080:8080"]
    # Port 9000 is Keycloak's management interface and is deliberately NOT published:
    # minio above already publishes 9000 to the host.
    volumes: ["./keycloak-local:/opt/keycloak/data/import:ro"]
    healthcheck:
      test: ["CMD-SHELL", "exec 3<>/dev/tcp/127.0.0.1/9000 && printf 'GET /health/ready HTTP/1.1\\r\\nHost: localhost\\r\\nConnection: close\\r\\n\\r\\n' >&3 && grep -q UP <&3"]
      interval: 5s
      timeout: 5s
      retries: 40
```

`retries: 40` at `interval: 5s` is a 200 s ceiling, inside `NFR-529`'s budget — the
README's own table reads it as *"< 5 min"*. Keycloak's first start imports a realm and is far
slower than the other three services, whose cold start was measured at 21 s.

- [ ] **Step 5: Verify the healthcheck against the real image, and fix it if it is wrong**

The healthcheck uses bash's `/dev/tcp` because the Keycloak image ships **no** `curl` and no
`wget` — that is the trap this step exists for. The exact health path and management port are
properties of the image, **not facts about this repository**, so verify rather than trusting
the block above:

```bash
docker compose -f deploy/docker-compose.yml --profile auth up -d
docker compose -f deploy/docker-compose.yml ps
docker compose -f deploy/docker-compose.yml exec keycloak sh -c 'exec 3<>/dev/tcp/127.0.0.1/9000 && printf "GET /health/ready HTTP/1.1\r\nHost: x\r\nConnection: close\r\n\r\n" >&3 && cat <&3'
```

Expected: `keycloak` reaches `(healthy)`, and the exec prints a body containing `UP`. **If the
path or the port differ for the tag you pinned, change the compose block to what you observed
and say so in the commit message** — a healthcheck that never goes green makes `--wait` hang
forever, which reads as a broken stack rather than a wrong URL.

- [ ] **Step 6: Prove the default stack is unchanged**

This is the half of `FR-398` a passing suite will not notice:

```bash
docker compose -f deploy/docker-compose.yml down
docker compose -f deploy/docker-compose.yml config --services | sort
docker compose -f deploy/docker-compose.yml --profile auth config --services | sort
```

Expected: the first prints exactly `minio`, `postgres`, `redis`; the second those three **and**
`keycloak`. If `keycloak` appears in the first, the profile key is misplaced and every
contributor now starts a container they did not ask for.

- [ ] **Step 7: Run the invariants module**

```bash
uv run pytest tests/test_repository_invariants.py -q
```

Expected: **PASS**, including the pre-existing `NFR-462` test — it asserts
`compose.count("healthcheck:") >= 3` (`:75`) and a fourth healthcheck keeps that true, but
confirm it rather than assuming.

- [ ] **Step 8: Commit**

```bash
git add deploy/docker-compose.yml tests/test_repository_invariants.py
git commit -m "feat(w6b-14): the local OIDC provider, behind an opt-in compose profile"
```

---

## Task 2: The checked-in realm

**Files:**
- Create: `deploy/keycloak-local/realm-gi-pricing.json`
- Test: `tests/test_repository_invariants.py`

**Interfaces:**
- Consumes: the mount path from Task 1 (`/opt/keycloak/data/import`).
- Produces: issuer `http://localhost:8080/realms/gi-pricing`; a public client
  `gi-pricing-frontend` with PKCE `S256` and `http://localhost:5173/*` redirect URIs; tokens
  carrying `aud: gi-pricing-api`; a user `analyst@example.fr` whose `sub` is a **fixed** UUID
  Task 3 reuses.

- [ ] **Step 1: Write the failing test**

Four properties, each one clause of `FR-398`: *"a public client with PKCE and no secret,
the dev-server redirect URIs, and an API audience equal to the configured `oidc_audience`."*
**Add `import json` to the module's imports** — it currently imports `pathlib`, `shutil`,
`subprocess` and `pytest` only (`:15-21`).

```python
@pytest.mark.req("FR-398")
def test_the_checked_in_realm_declares_a_public_pkce_client() -> None:
    """FR-398's realm, asserted as a file rather than against a running provider.

    A test needing the container would be one nobody runs -- FR-398 says exactly that --
    so this reads the artifact that is committed. What it cannot check is that Keycloak
    agrees with it; Step 6 does that once, by round-tripping an export.
    """
    realm = json.loads(
        (ROOT / "deploy" / "keycloak-local" / "realm-gi-pricing.json").read_text(
            encoding="utf-8"
        )
    )
    assert realm["realm"] == "gi-pricing"

    spa = {c["clientId"]: c for c in realm["clients"]}["gi-pricing-frontend"]

    # Public client, no secret: FR-393 -- "no client secret exists in it".
    assert spa["publicClient"] is True
    assert "secret" not in spa
    # PKCE, and S256 specifically: `plain` is a code challenge that protects nothing.
    assert spa["attributes"]["pkce.code.challenge.method"] == "S256"
    # The dev server, which scripts/demo.py:49 fixes at 5173.
    assert any("localhost:5173" in uri for uri in spa["redirectUris"])
    # The audience the API verifies (config.py:141). Keycloak does not put a resource server
    # in `aud` unless a mapper says so -- this assertion catches its absence, because every
    # other part of the flow works without it.
    audiences = [
        m["config"]["included.client.audience"]
        for m in spa.get("protocolMappers", [])
        if m["protocolMapper"] == "oidc-audience-mapper"
    ]
    assert "gi-pricing-api" in audiences
```

- [ ] **Step 2: Run it and watch it fail**

```bash
uv run pytest tests/test_repository_invariants.py::test_the_checked_in_realm_declares_a_public_pkce_client -q
```

Expected: **FAIL** with `FileNotFoundError` on `realm-gi-pricing.json`. Record it. A different
failure means Task 1 left a stub behind.

- [ ] **Step 3: Choose the demo user's subject, and write it down once**

The `sub` claim must be **stable across a realm re-import**, because Task 3 stores it in the
`users` table. Keycloak uses the imported `users[].id` as the `sub`, so pin it:

```bash
uv run python -c "import uuid; print(uuid.uuid4())"
```

Record the value. It appears in exactly two places — the realm's `users[0].id` and the seed's
`REALM_SUBJECT` — and they must be identical. Generating it here rather than writing one from
memory is the same rule as Task 1 Step 1.

- [ ] **Step 4: Write the realm**

Create `deploy/keycloak-local/realm-gi-pricing.json`, substituting Step 3's UUID for
`<SUBJECT>`:

```json
{
  "realm": "gi-pricing",
  "enabled": true,
  "displayName": "GI Pricing (local development)",
  "sslRequired": "none",
  "registrationAllowed": false,
  "clients": [
    {
      "clientId": "gi-pricing-frontend",
      "name": "GI Pricing SPA",
      "enabled": true,
      "publicClient": true,
      "standardFlowEnabled": true,
      "directAccessGrantsEnabled": false,
      "serviceAccountsEnabled": false,
      "redirectUris": ["http://localhost:5173/*"],
      "webOrigins": ["http://localhost:5173"],
      "attributes": {
        "pkce.code.challenge.method": "S256",
        "post.logout.redirect.uris": "http://localhost:5173/*"
      },
      "protocolMappers": [
        {
          "name": "gi-pricing-api-audience",
          "protocol": "openid-connect",
          "protocolMapper": "oidc-audience-mapper",
          "config": {
            "included.client.audience": "gi-pricing-api",
            "access.token.claim": "true",
            "id.token.claim": "false"
          }
        }
      ]
    }
  ],
  "users": [
    {
      "id": "<SUBJECT>",
      "username": "analyst",
      "email": "analyst@example.fr",
      "firstName": "Demo",
      "lastName": "Analyst",
      "enabled": true,
      "emailVerified": true,
      "credentials": [{ "type": "password", "value": "analyst", "temporary": false }]
    }
  ]
}
```

`directAccessGrantsEnabled: false` is deliberate: the resource-owner password grant mints a
token from a username and password with no browser flow at all, and `FR-393` specifies
**authorization code with PKCE** — *"the code verifier never leaves the browser"*. Leaving the
direct grant enabled would offer a second, weaker route to a token that the requirement does
not describe. `sslRequired: "none"` is what permits `http://localhost`, and is the line that
would be wrong in any deployment — `FR-437` says this file is never the production one.

- [ ] **Step 5: Run the test**

```bash
uv run pytest tests/test_repository_invariants.py -q
```

Expected: **PASS**.

- [ ] **Step 6: Verify the schema against Keycloak, not against this plan**

The field names above are Keycloak's realm-export schema. **They are not facts about this
repository and this plan cannot verify them** — a key Keycloak ignores is silently dropped on
import, and the realm would come up looking correct while the client is confidential, the
audience mapper absent, or PKCE unenforced. Round-trip it once:

```bash
docker compose -f deploy/docker-compose.yml --profile auth up -d --wait
curl -s http://localhost:8080/realms/gi-pricing/.well-known/openid-configuration | python3 -m json.tool | head -20
docker compose -f deploy/docker-compose.yml exec keycloak /opt/keycloak/bin/kc.sh export --dir /tmp/export --realm gi-pricing
docker compose -f deploy/docker-compose.yml exec keycloak cat /tmp/export/gi-pricing-realm.json > "$TMPDIR_EXPORT"
```

Set `TMPDIR_EXPORT` to a scratch path first. Then inspect it — write this to a file and run it
with `python3`, rather than pasting a heredoc:

```python
import json, os
r = json.load(open(os.environ["TMPDIR_EXPORT"]))
spa = {c["clientId"]: c for c in r["clients"]}["gi-pricing-frontend"]
print("publicClient    :", spa.get("publicClient"))
print("pkce            :", spa.get("attributes", {}).get("pkce.code.challenge.method"))
print("redirectUris    :", spa.get("redirectUris"))
print("audience mappers:", [
    m["config"].get("included.client.audience")
    for m in spa.get("protocolMappers", [])
    if m.get("protocolMapper") == "oidc-audience-mapper"
])
print("user subject    :", [u["id"] for u in r.get("users", [])])
```

Expected: the discovery document's `issuer` is exactly
`http://localhost:8080/realms/gi-pricing`; `publicClient` is `True`; `pkce` is `S256`; the
redirect list contains the 5173 entry; the audience list contains `gi-pricing-api`; and the
user subject equals Step 3's UUID.

**Any mismatch means the committed file is wrong, not the export.** Amend
`realm-gi-pricing.json` to the shape Keycloak accepts, re-import (`down` then `up` — the import
runs at first start only), and repeat until the five lines agree. Record what you changed: a
corrected field name here is the most useful sentence in the commit message, because the next
person will write the same wrong one.

- [ ] **Step 7: Commit**

```bash
git add deploy/keycloak-local/realm-gi-pricing.json tests/test_repository_invariants.py
git commit -m "feat(w6b-14): the checked-in realm — public PKCE client, and the API in aud"
```

---

## Task 3: The identity rows the seeded workspace needs

**Files:**
- Modify: `backend/src/app/platform/workspaces.py`
- Test: `backend/tests/test_workspace_members.py` (create)
- Modify: `examples/fremtpl2/seed.py`

**Interfaces:**
- Consumes: the realm issuer and the `<SUBJECT>` UUID from Task 2 Step 3.
- Produces:

```python
async def ensure_member(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    user_id: UUID,
    issuer: str,
    subject: str,
    email: str | None = None,
    display_name: str | None = None,
) -> UserRow
```

After this, `authenticate_bearer` resolves a realm login to the **same principal id** the
dev-header path uses, holding the role assignments the seed already grants.

- [ ] **Step 1: Write the failing tests**

Create `backend/tests/test_workspace_members.py`. **Mirror
`backend/tests/test_workspace_selection.py` throughout** — module-level imports, the `database`
fixture with `async with database.unit_of_work() as session`, `new_uuid7` from `model_schema`,
and a local `StubVerifier`. Do not invent fixtures: `asyncio_mode = "auto"`
(`pyproject.toml:110`), so a plain `async def test_` is the house style and
`@pytest.mark.asyncio` is not used here.

The first test asserts the predicate `FR-398` actually states — that a login *resolves into
the seeded workspace*, as that principal — by driving `authenticate_bearer`, rather than by
reading rows back.

```python
"""FR-398: a realm login resolves into the seeded workspace, as that principal."""

from __future__ import annotations

import pytest
from sqlalchemy import select

from app.auth.oidc import TokenClaims
from app.auth.service import authenticate_bearer
from app.db.models import WorkspaceMemberRow
from app.db.session import Database
from app.platform import workspaces
from model_schema import new_uuid7

ISSUER = "http://localhost:8080/realms/gi-pricing"


class StubVerifier:
    """Returns fixed claims.

    Copied from `test_workspace_selection.py` rather than imported, for the reason that
    module gives: a test module is not an import target for another one.
    """

    def __init__(self, claims: TokenClaims) -> None:
        self._claims = claims

    @property
    def issuer(self) -> str:
        return ISSUER

    def verify(self, token: str) -> TokenClaims:
        return self._claims


def _claims(subject: str) -> TokenClaims:
    """Copy this from `test_workspace_selection.py:39` verbatim.

    It takes a subject and nothing else -- the email and name it carries are fixed in that
    definition. Whatever `TokenClaims` currently requires is a fact about `app/auth/oidc.py`,
    so copy rather than reconstruct.
    """


@pytest.mark.req("FR-398")
async def test_a_realm_login_resolves_to_the_seeded_principal(database: Database) -> None:
    """The seeded user's id IS the principal id, not a fresh one.

    Membership alone is not enough. `authenticate_bearer` returns `UserRow.id` as the
    principal, and the seed's role assignments are written against the principal it minted
    -- so a defaulted id authenticates successfully, joins the workspace, and is authorised
    for nothing. That failure surfaces three layers from its cause, which is why this is
    asserted through `authenticate_bearer` rather than by reading the row back.
    """
    workspace_id, principal_id = new_uuid7(), new_uuid7()
    subject = f"sub-{new_uuid7().hex[-12:]}"

    async with database.unit_of_work() as session:
        await workspaces.ensure_workspace(
            session, workspace_id=workspace_id, name="freMTPL2 demo"
        )
        await workspaces.ensure_member(
            session,
            workspace_id=workspace_id,
            user_id=principal_id,
            issuer=ISSUER,
            subject=subject,
            email="analyst@example.fr",
        )

    async with database.unit_of_work() as session:
        identity = await authenticate_bearer(
            session, StubVerifier(_claims(subject)), "t"
        )

    assert identity.principal.id == principal_id
    assert workspace_id in identity.workspaces


@pytest.mark.req("FR-398")
async def test_ensuring_a_member_twice_does_not_raise(database: Database) -> None:
    """The seed is re-run against an existing database more often than not.

    `workspace_members` carries `uq_workspace_members_user_workspace`
    (`db/models.py:489`), so a second blind insert raises rather than being ignored. `users`
    carries `uq_users_issuer_subject` for the same reason.
    """
    workspace_id, principal_id = new_uuid7(), new_uuid7()
    subject = f"sub-{new_uuid7().hex[-12:]}"

    for _ in range(2):
        async with database.unit_of_work() as session:
            await workspaces.ensure_workspace(session, workspace_id=workspace_id)
            await workspaces.ensure_member(
                session,
                workspace_id=workspace_id,
                user_id=principal_id,
                issuer=ISSUER,
                subject=subject,
            )

    async with database.unit_of_work() as session:
        rows = (
            await session.execute(
                select(WorkspaceMemberRow).where(
                    WorkspaceMemberRow.user_id == principal_id
                )
            )
        ).scalars().all()
    assert len(rows) == 1
```

- [ ] **Step 2: Run them and watch them fail**

```bash
uv run pytest backend/tests/test_workspace_members.py -q
```

Expected: **FAIL** with `AttributeError: module 'app.platform.workspaces' has no attribute
'ensure_member'`. Record the message. If it fails on a fixture or an import instead, Step 1's
mirroring was incomplete — fix the test against `test_workspace_selection.py` before touching
the implementation, because a test that fails for the wrong reason will look confirmed by a
status alone.

- [ ] **Step 3: Add `ensure_member`**

In `backend/src/app/platform/workspaces.py`. Extend the imports to
`from app.db.models import UserRow, WorkspaceMemberRow, WorkspaceRow`, add
`from sqlalchemy import select`, and set
`__all__ = ["ensure_member", "ensure_workspace"]`.

```python
async def ensure_member(
    session: AsyncSession,
    *,
    workspace_id: UUID,
    user_id: UUID,
    issuer: str,
    subject: str,
    email: str | None = None,
    display_name: str | None = None,
) -> UserRow:
    """Make an OIDC identity a member of a workspace, as a given principal (FR-398).

    Two rows, and each is load-bearing for a different reason:

    * the `users` row **with `id=user_id`**, because `authenticate_bearer` returns
      `UserRow.id` as the principal and a caller's role assignments are written against the
      principal id it already uses -- a defaulted id yields a member of the workspace who
      may do nothing in it;
    * the `workspace_members` row, because `FR-390` grants no access by default and
      `authenticate_bearer` reads workspaces from that table alone.

    **The workspace must already exist**: `workspace_members.workspace_id` is a foreign key
    to `workspaces.id`, so call `ensure_workspace` first. It is not called from here because
    the caller owns the workspace's name, and `ensure_workspace` returns an existing row
    untouched -- naming it afterwards silently does nothing.

    Idempotent, like `ensure_workspace` and `seed_builtin_roles`: a seed is re-run against an
    existing database routinely, and both `uq_workspace_members_user_workspace` and
    `uq_users_issuer_subject` make a second blind insert an error rather than a no-op.
    """
    user = await session.get(UserRow, user_id)
    if user is None:
        user = UserRow(id=user_id, issuer=issuer, subject=subject)
        session.add(user)
    # Only overwrite what the caller actually supplied: a re-run passing no email must not
    # blank one an earlier run set.
    if email is not None:
        user.email = email
    if display_name is not None:
        user.display_name = display_name

    existing = (
        await session.execute(
            select(WorkspaceMemberRow).where(
                WorkspaceMemberRow.user_id == user_id,
                WorkspaceMemberRow.workspace_id == workspace_id,
            )
        )
    ).scalar_one_or_none()
    if existing is None:
        session.add(WorkspaceMemberRow(user_id=user_id, workspace_id=workspace_id))

    await session.flush()
    return user
```

- [ ] **Step 4: Run the tests**

```bash
uv run pytest backend/tests/test_workspace_members.py -q
```

Expected: **PASS**, both tests.

- [ ] **Step 5: Call it from the seed**

In `examples/fremtpl2/seed.py`. The `app.*` imports live **inside `run()`** at `:261-279`, not
at module top level — add `from app.platform import workspaces` alongside the existing
`from app.platform import rbac` at `:274`.

Add the two constants beside the module's other constants near the top of the file. **Do not
annotate them `Final`** — `seed.py`'s `typing` import at `:27` is `from typing import Any`
only, and this slice should not widen it:

```python
#: The realm `deploy/keycloak-local/realm-gi-pricing.json` imports, and the subject it pins
#: for the demo analyst. These two strings are the join between a browser login and this
#: seed: `authenticate_bearer` keys a user on `(issuer, subject)`, so a realm re-import that
#: changed either would authenticate a *different* user into nothing.
REALM_ISSUER = "http://localhost:8080/realms/gi-pricing"
REALM_SUBJECT = "<SUBJECT FROM TASK 2 STEP 3>"
```

Then, immediately after the two `grant(...)` calls at `:325-326`:

```python
    # A real login through the local provider (FR-398) resolves to `analyst`, so it
    # inherits the role assignments granted just above rather than needing its own. The
    # workspace row comes first: `workspace_members.workspace_id` is a foreign key, and
    # nothing has created that row until now -- `RoleRow.workspace_id` has no foreign key,
    # which is why the seed has worked without one. The actuary has no realm user; one demo
    # login is what FR-398 asks for.
    async with database.unit_of_work() as session:
        await workspaces.ensure_workspace(
            session, workspace_id=workspace_id, name="freMTPL2 demo"
        )
        await workspaces.ensure_member(
            session,
            workspace_id=workspace_id,
            user_id=analyst.id,
            issuer=REALM_ISSUER,
            subject=REALM_SUBJECT,
            email=analyst.display,
            display_name="Demo Analyst",
        )
```

Check the surrounding block's own names before pasting: `database`, `workspace_id` and
`analyst` must be the identifiers in scope at `:325`. If `run()` opens its sessions by another
name, follow that rather than this sample.

- [ ] **Step 6: Check the seed still imports and its own tests pass**

The seed cannot be run end to end in CI — it fetches 36 MB (`pyproject.toml:101` says so) — so
check what can be checked:

```bash
uv run pytest examples/fremtpl2 -q
uv run python -c "import sys; sys.path.insert(0, 'examples/fremtpl2'); import seed; print(seed.REALM_ISSUER)"
```

Expected: the existing seed tests pass, and the import prints the issuer. The second command
mirrors `examples/fremtpl2/test_seed.py:15-17`'s `sys.path` approach, which is how anything
reaches this module.

- [ ] **Step 7: Run the whole suite with no provider container**

This is `FR-398`'s *"both test suites keep running with no container"*:

```bash
docker compose -f deploy/docker-compose.yml down
docker compose -f deploy/docker-compose.yml up -d --wait
uv run pytest -q
```

The three default services come back up because the database-backed tests need postgres; what
must be **absent** is `keycloak`. Expected: **PASS**, with the previous total plus the two new
tests. A difference of more than two means something was collected or skipped that was not
before — find out which before continuing.

- [ ] **Step 8: Commit**

```bash
git add backend/src/app/platform/workspaces.py backend/tests/test_workspace_members.py examples/fremtpl2/seed.py
git commit -m "feat(w6b-14): seed the workspace, user and membership a realm login resolves to"
```

---

## Task 4: The documented path in

**Files:**
- Modify: `deploy/README.md`

**Interfaces:**
- Consumes: everything the previous three tasks produced.
- Produces: the four commands `W6b-10` starts from.

- [ ] **Step 1: Extend the README**

Append after the existing local-stack command block, before the `## Verified` section:

````markdown
## The local identity provider (FR-398)

Off by default. Three containers start as before; the provider is a fourth, behind a profile:

```bash
docker compose -f deploy/docker-compose.yml --profile auth up -d --wait
```

It imports `deploy/keycloak-local/realm-gi-pricing.json` on first start — a public PKCE client
for the SPA, an audience mapper putting the API in the token, and one demo user. Point the API
at it (the prefix is `GIP_`, `backend/src/app/config.py:92`):

```bash
export GIP_OIDC_ISSUER=http://localhost:8080/realms/gi-pricing
export GIP_OIDC_AUDIENCE=gi-pricing-api
export GIP_OIDC_JWKS_URL=http://localhost:8080/realms/gi-pricing/protocol/openid-connect/certs
```

| What | Value |
|---|---|
| Realm | `gi-pricing` |
| SPA client | `gi-pricing-frontend` — public, PKCE `S256`, no secret |
| Demo login | `analyst` / `analyst` |
| Keycloak admin | `admin` / `admin` at `http://localhost:8080/admin` |

**This is a local provider and never a production one.** It serves plain HTTP, its realm sets
`sslRequired: "none"`, and its passwords are in a file in this repository. `FR-437` decides
that no identity provider ships in the production stack and that `deploy/` carries a
*reference* Keycloak deployment the deployer operates and patches — that is a different
artifact, owned by WK-674, and `deploy/keycloak/` is left free for it. This directory is
`keycloak-local` so the two can never be confused.

**It is an alternative to `dev_auth_enabled`, not a replacement.** Both test suites run with no
container at all, which is why every test covering this provider asserts against the committed
realm file or the database rather than a live one. `scripts/demo.py` is unchanged and still
uses the dev headers: it runs `docker compose up` with no profile (`scripts/demo.py:189`), so
the one-command demo starts the same three containers it always did.

**The browser cannot use this yet.** The PKCE flow is `FR-393`, owned by `W6b-10`, and how
the SPA learns the issuer and client id is an open question with the maintainer — nothing in
the frontend reads either value today.
````

- [ ] **Step 2: Record the start cost**

The README's `## Verified` block carries measured start times against `NFR-529: < 5 min`,
and a fourth container changes the number that requirement is read against. Measure rather than
estimate:

```bash
docker compose -f deploy/docker-compose.yml --profile auth down -v
time docker compose -f deploy/docker-compose.yml --profile auth up -d --wait
docker stats --no-stream --format "{{.Name}} {{.MemUsage}}"
```

Add a row for the four-service start with the number you observed, dated today and labelled as
the `--profile auth` start. **Leave the existing 2026-08-14 rows untouched** — they record what
was measured on that date on that machine, not a claim about today, and the cold-start 21 s and
117 MB figures stay as they are. **If the four-service start exceeds 5 min that is a finding,
not a number to write down quietly:** report it, because `NFR-529` would then be breached by
this slice.

- [ ] **Step 3: Commit**

```bash
git add deploy/README.md
git commit -m "docs(w6b-14): the documented way in to the local provider, and its measured start"
```

---

## Task 5: The spec amendment, the gate, and the hand-off

**Files:**
- Modify: `docs/specs/07-platform.md`

- [ ] **Step 1: Amend `FR-387`**

`FR-387`'s 2026-08-23 amendment ends *"what is outstanding is the local container"*
(`docs/specs/07-platform.md:71`). That becomes false when this branch lands, and `CLAUDE.md` §0
forbids leaving spec and code disagreeing. **Append a dated note; do not rewrite the clause** —
an amendment records what was believed on its date, and overwriting it destroys that. Something
of the form:

> *Amended 2026-08-25 (W6b-14): the local container landed. `deploy/docker-compose.yml`
> carries a `keycloak` service behind the `auth` profile importing
> `deploy/keycloak-local/realm-gi-pricing.json`, and `examples/fremtpl2/seed.py` seeds the
> workspace, user and membership rows a realm login resolves to. `FR-398` is discharged;
> the browser half (`FR-393`) is not, and remains `W6b-10`.*

Keep the whole amendment on one line — `audit-docs.py` parses a wrapped line beginning with
`|` as a table row.

- [ ] **Step 2: Run the docs half**

```bash
python3 scripts/audit-docs.py && uv run python scripts/req-coverage.py
```

Both must pass. A spec edit is what `audit-docs.py` exists for.

- [ ] **Step 3: Run the Python half**

```bash
uv run ruff check . && uv run mypy && uv run lint-imports && uv run pytest -q
uv run python scripts/generate-contracts.py --check
```

`generate-contracts.py --check` should report **no drift** — this slice adds no `model-schema`
shape, so a change there means something was edited that should not have been.

- [ ] **Step 4: Run the frontend half anyway**

```bash
pnpm --dir frontend install --frozen-lockfile && pnpm --dir frontend generate:api
pnpm --dir frontend lint && pnpm --dir frontend type-check
pnpm --dir frontend test && pnpm --dir frontend build
```

This slice changes nothing under `frontend/`, and the gate is still both halves (`CLAUDE.md`
§11: *"a Python-only 'gate' has been green here while the frontend was red"*). A failure here
is a pre-existing break on `main`, not this branch's — say which when reporting.

- [ ] **Step 5: Confirm `FR-398` is evidenced**

```bash
uv run python scripts/req-coverage.py | grep -n "FR-398"
```

Expected: evidenced by the `@pytest.mark.req("FR-398")` tests in
`tests/test_repository_invariants.py` and `backend/tests/test_workspace_members.py`. If it is
unmarked, check the marker spelling before concluding anything — an unmarked id is not the same
as an unevidenced requirement, and `--strict-markers` catches only unregistered markers, not a
correctly-registered marker carrying the wrong id.

- [ ] **Step 6: Prove the default stack one final time, from clean**

The single regression this slice could cause is starting a fourth container for everyone:

```bash
docker compose -f deploy/docker-compose.yml down -v
docker compose -f deploy/docker-compose.yml up -d --wait
docker compose -f deploy/docker-compose.yml ps --format "{{.Service}}"
```

Expected: exactly three service names. **If `keycloak` is among them the slice has failed its
main constraint**, whatever the tests say.

- [ ] **Step 7: Hand off what W6b-10 needs**

State in the PR body, because these are values `W6b-10`'s plan cannot derive from the spec: the
issuer, the client id, the audience, the redirect URI, and the demo credentials. Add the thing
that is *not* delivered — **the SPA has no channel to the issuer or the client id** (Finding 3,
with `w6b-decision-maker`). A PR handing over the values without that sentence reads as though
`W6b-10` is unblocked.

---

## Self-review

Run against `docs/plans/README.md`'s three unenforced conventions.

**Rule 1 — every repository literal verified against shipped source.** Every path, line number
and default was read from the file it names. The pass caught **six** defects in this plan's own
first draft, all of them the class that reaches an executor as a confident wrong instruction:

| Draft claimed | Source says |
|---|---|
| `from examples.fremtpl2.seed import seed_identity`, with a `db_session` fixture and `@pytest.mark.asyncio` | `examples/` has no `__init__.py`; `examples/fremtpl2/test_seed.py:15-17` reaches the module by `sys.path.insert`; the fixture is `database: Database` (`backend/tests/conftest_db.py:42-43`); `asyncio_mode = "auto"` (`pyproject.toml:110`) |
| The helper belongs in `seed.py` | It cannot be tested there — no fixtures reach `examples/`. `workspaces.py`'s docstring already claims the job |
| `service.py:139-152` keys the user on `(issuer, subject)` | `_upsert_user` is defined at `:124` and called from `authenticate_bearer` at `:103`; memberships are read at `:105-110` |
| Seed imports at `:284`; `grant(...)` at `:326-327` | Imports at `:261-279`; the calls at `:325-326` |
| `REALM_ISSUER: Final = …` | `seed.py:27` imports `Any` only; `Final` is not in scope |
| `directAccessGrantsEnabled: false` is "the flow `OQ-644` decided against" | `OQ-644` (`07-platform.md:465`) decided **PKCE-in-the-SPA over a BFF session cookie**. It says nothing about the password grant. The correct authority is `FR-393`, which specifies authorization code with PKCE |

The last of those is the worst kind: a citation that is real, adjacent, and points somewhere
else. It would have survived review by anyone who checked that `OQ-644` exists and concerns
browser authentication.

Two design defects were fixed in the same pass. `ensure_member` assigned `user.email = email`
unconditionally, so a re-run passing no email would blank one an earlier run set — it now
writes only what the caller supplied. And the plan asserted `NFR-529` as "300 s" where
`deploy/README.md`'s own table reads it as *"< 5 min"*; the budget is quoted from the table now.

Three literals are **not** from this repository and are marked as such where they are used:
Keycloak's image tag (Task 1 Step 1 derives it from the registry), its health path and
management port (Task 1 Step 5 verifies them against the running image), and the realm-export
schema (Task 2 Step 6 round-trips an export and says in terms that the plan cannot verify it).
That is the "name the authority rather than supply a sample" form, and Task 3 Step 1 applies it
to `_claims` — the plan gives its signature and tells the executor to copy the body from
`test_workspace_selection.py:39` rather than reconstructing what `TokenClaims` requires.

**Rule 2 — a predicted failure stated by cause, not status.** Each watch-it-fail step names the
expected assertion or exception — `assert "keycloak:" in compose`, `FileNotFoundError`,
`AttributeError: … has no attribute 'ensure_member'` — and each says what a *different* failure
means. Task 3 Step 2 makes the discriminator explicit, because the fixture names are the part
of that test most likely to be wrong and a bare "it failed" would confirm the prediction while
hiding a second fault.

**Rule 3 — run rule 1 against shipped source, not the plan's own prose.** Doing so produced two
of the seven findings and corrected a third. It stopped an early draft from reporting *"nothing
writes `workspace_members` outside tests"* as a defect — `models.py:472-476` records it as a
decision, so it became Finding 2 with a `not started, owner WK-659` verdict rather than a proposal
to re-open a settled question. It also sharpened Finding 1: the reason the missing `workspaces`
row has gone unnoticed is that `RoleRow.workspace_id` carries **no** foreign key
(`models.py:538`) while `WorkspaceMemberRow.workspace_id` does — a fact no amount of reading
the seed would have produced. And it produced Finding 7, from `FR-437`'s own wording about
what WK-674 owns under `deploy/`.

**Spec coverage.** `FR-398`'s clauses map to tasks as: the opt-in profile → Task 1; the
checked-in realm, public PKCE client, dev redirect URIs and API audience → Task 2; demo users
resolving into the seeded workspace → Task 3; alternative-not-replacement and both suites
running with no container → the Global Constraints, Task 1 Step 6 and Task 3 Step 7. No clause
is unclaimed. `FR-387`'s stale sentence → Task 5 Step 1.

**Type consistency.** `ensure_member`'s signature is written once in the Interfaces block and
used identically in Task 3's tests, its implementation and its seed call site:
`(session, *, workspace_id, user_id, issuer, subject, email=None, display_name=None) -> UserRow`.
`REALM_ISSUER` and `REALM_SUBJECT` appear in `seed.py` and the realm JSON and nowhere else, and
Task 2 Step 3 makes the subject a single generated value rather than two literals that must
match.
