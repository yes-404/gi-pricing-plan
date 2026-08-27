# Local stack

Brings up the services Phase 1a needs: PostgreSQL 16, Redis 7 and MinIO. No cloud
dependency (NFR-OVR-9).

```bash
docker compose -f deploy/docker-compose.yml up -d --wait
docker compose -f deploy/docker-compose.yml ps
docker compose -f deploy/docker-compose.yml down          # add -v to drop the volumes
```

`--wait` blocks until every healthcheck passes, so a green exit means the stack is
genuinely usable rather than merely started.

## The local identity provider (FR-PLAT-58)

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
`sslRequired: "none"`, and its passwords are in a file in this repository. `FR-PLAT-59` decides
that no identity provider ships in the production stack and that `deploy/` carries a
*reference* Keycloak deployment the deployer operates and patches — that is a different
artifact, owned by W14, and `deploy/keycloak/` is left free for it. This directory is
`keycloak-local` so the two can never be confused.

**It is an alternative to `dev_auth_enabled`, not a replacement.** Both test suites run with no
container at all, which is why every test covering this provider asserts against the committed
realm file or the database rather than a live one. `scripts/demo.py` now starts the auth profile
(`docker compose --profile auth up`) and sets the `GIP_OIDC_*` variables, so the one-command
demo runs all four containers and the browser signs in through this provider
(*corrected 2026-08-27, W6b: it previously ran no profile and used the dev headers*).

**The browser uses it.** The PKCE flow is `FR-PLAT-55`; the SPA learns the issuer and client id
from `FR-PLAT-66`'s `/api/v1/auth/config` (W6b-10), and the seeded membership answers the
`analyst` / `analyst` login (FR-PLAT-58).

## Verified

**2026-08-14, Debian 13 / Docker 26.1.5 / Compose v5.4.0**

| Measure | Result | Requirement |
|---|---|---|
| Cold start, images pulled | **21 s** | NFR-PLAT-4: < 5 min |
| Warm start, images cached | **6 s** | — |
| Memory, all three services | **117 MB** | — |
| Disk, images + volumes | **~1 GB** | — |

**2026-08-26, Debian 13 / Docker 26.1.5 / Compose v5.4.0** — `--profile auth`, warm images

| Measure | Result | Requirement |
|---|---|---|
| Four-service start (`--profile auth up --wait`) | **80 s** | NFR-PLAT-4: < 5 min |
| Second start (import done, images warm) | **53 s** | — |
| Memory with the provider | **~777 MB** (keycloak 632 MB) | — |

Three specification assumptions were tested against the real services rather than assumed:

- **FR-DATA-29** — reference-table validity intervals must not overlap. A `btree_gist`
  exclusion constraint on `(slug =, key =, validity &&)` **rejected** the overlapping insert
  on PostgreSQL 16.15. The constraint the spec relies on is enforceable as written.
- **FR-OVR-7** — money exactness. `bigint` round-trips minor units exactly, and
  `numeric` addition is exact where binary float is not.
- **ID-4** — content-addressed blobs. Put and get round-tripped through MinIO's S3 API.

## Setup gotchas

Two things cost time on Debian 13 and are worth knowing:

- **`docker-compose-v2` is not a package name here.** Debian ships the legacy v1
  `docker-compose`, which does not understand this file's v2 syntax (the top-level `name:`
  key). Install the v2 plugin binary from the Docker releases instead.
- **A plugin in `~/.docker/cli-plugins` is invisible to `sudo docker`**, because root reads
  `/root/.docker`. Install it to `/usr/local/lib/docker/cli-plugins/` so both see it — or
  add your user to the `docker` group and drop `sudo` altogether (needs a new login).
