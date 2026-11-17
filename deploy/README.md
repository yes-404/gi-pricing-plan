---
family: reference
title: Local stack
status: active                  # active → retired (§1.2a)
created: 2026-08-14
owner: lead
corrected_by: []
relates: []                      # ids only
---

# Local stack

Brings up the services Phase 1a needs: PostgreSQL 16, Redis 7 and MinIO. No cloud
dependency (NFR-462).

```bash
docker compose -f deploy/docker-compose.yml up -d --wait
docker compose -f deploy/docker-compose.yml ps
docker compose -f deploy/docker-compose.yml down          # add -v to drop the volumes
```

`--wait` blocks until every healthcheck passes, so a green exit means the stack is
genuinely usable rather than merely started.

*(Dated 2026-10-25, on the maintainer's (by delegation) entry "2026-10-25 11:53:23 GMT".)*
Every published port of this stack (PostgreSQL 5432, Redis 6379, MinIO 9000 and 9001, Keycloak
8080 and the `lb` port, `GIP_LB_PORT`, default 8000) is bound to `127.0.0.1`. A host outside this
machine reaches none of them. To use one from another machine, forward it over SSH
(`ssh -L 8080:127.0.0.1:8080 <host>`). `backend/tests/test_compose_binds.py` fails if a
service is published without the bind. A running container keeps its old binding until it is
recreated from a checkout that has this change.

*(Dated 2026-11-15, #1510 slice S6b.)* On a fresh volume PostgreSQL runs
`deploy/postgres/app-login-role.sql` once, at first start, through its `initdb` entry
(`docker-entrypoint-initdb.d`); that run is not wrapped in one transaction. The provisioner
`scripts/provision-app-role.py` runs the same file in one transaction, and that is the form to
use on an existing volume.

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
realm file or the database rather than a live one. `scripts/demo.py` now starts the auth profile
(`docker compose --profile auth up`) and sets the `GIP_OIDC_*` variables, so the one-command
demo runs all four containers and the browser signs in through this provider
(*corrected 2026-08-27, WK-664: it previously ran no profile and used the dev headers*).

**The browser uses it.** The PKCE flow is `FR-393`; the SPA learns the issuer and client id
from `FR-394`'s `/api/v1/auth/config` (W6b-10), and the seeded membership answers the
`analyst` / `analyst` login (FR-398).

## Verified

**2026-08-14, Debian 13 / Docker 26.1.5 / Compose v5.4.0**

| Measure | Result | Requirement |
|---|---|---|
| Cold start, images pulled | **21 s** | NFR-529: < 5 min |
| Warm start, images cached | **6 s** | — |
| Memory, all three services | **117 MB** | — |
| Disk, images + volumes | **~1 GB** | — |

**2026-08-26, Debian 13 / Docker 26.1.5 / Compose v5.4.0** — `--profile auth`, warm images

| Measure | Result | Requirement |
|---|---|---|
| Four-service start (`--profile auth up --wait`) | **80 s** | NFR-529: < 5 min |
| Second start (import done, images warm) | **53 s** | — |
| Memory with the provider | **~777 MB** (keycloak 632 MB) | — |

Three specification assumptions were tested against the real services rather than assumed:

- **FR-69** — reference-table validity intervals must not overlap. A `btree_gist`
  exclusion constraint on `(slug =, key =, validity &&)` **rejected** the overlapping insert
  on PostgreSQL 16.15. The constraint the spec relies on is enforceable as written.
- **FR-10** — money exactness. `bigint` round-trips minor units exactly, and
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

## The deployment path (WK-674 Slice 4)

`api`, `worker` and `migrate` are one image run under three commands, behind the `app` profile,
so the default `up` is still the three backing services. Build from the repository root and give
the image the commit it was built from (FR-18):

```bash
export GIP_BUILD=$(git rev-parse HEAD)
docker compose -f deploy/docker-compose.yml --profile app build api
docker build -f deploy/frontend.Dockerfile -t gi-pricing-frontend:$GIP_BUILD .
docker compose -f deploy/docker-compose.yml --profile app up -d --wait --scale api=2 lb
```

  `frontend` is built with `docker build`, not `compose build`: the buildx on this box is below the
  0.17.0 that `compose build` needs. A bare `--profile app up` starts `frontend`, so build its image
  first.

- **Upgrading to the build that applies a Factor's `unseen_level_behaviour`** (`02` FR-2143): a
  GLM `model_call` refuses a quote carrying a level of a categorical Factor that its fit never
  saw, unless the Factor declares `map_to_base`. **Before upgrading, run the sweep**, a read-only
  script that lists the stored versions that can refuse such quotes:
  `uv run python scripts/sweep-unseen-levels.py [--dsn <read-only URL>] [--workspace <id>]`. It
  prints its denominators first, then one line per version and class (reference only, never a
  level or a hash), and exits 0 (none reachable), 1 (a version is reachable), 2 (a bundle could
  not be read), 3 (no version with a bundle was found, so nothing was checked), 64 (an argument
  error) or 70 (the sweep itself failed: it prints the exception's type only; never read 70 as
  clean or as reachable). A version whose GLM has an indicator term for a level its numeric input
  can never produce refuses EVERY quote on that path, not only the affected values; the sweep
  lists such versions as `NOTEXAMINED-NUMERIC-TERMS` until their models are refitted (the line
  lists every identity label that starts like a number, so it is a floor on what the tool
  examined, not a count of faults). The NOTEXAMINED lines are information: they never change the
  exit code. A version whose every undeclared identity Factor cannot be reached by a quote, and that
  carries no other class and no line the sweep did not examine (a NOTEXAMINED line, or a model of another family), is listed as `NOTREACHABLE`, never `PLAIN`,
  with a reason word on its line: `closed-input` (the Factor is fed only by an input that is a
  closed enum over the fit's own levels, on every GLM that input feeds, and no interaction Factor
  of that fit takes it as an operand) or `not-scored` (nothing the runtime scores reads the GLM:
  no `model_call` names it, directly or through a Peril Structure, and no scored GLM reads it as
  its offset model). An `expression` Factor with no Banding and with relativities is `PLAIN`. A version the runtime
  cannot load (a GLM whose Factor the bundle does not carry, or whose fit names a level its Factor
  cannot produce) is `UNREADABLE` with the exception's type, and exit 2 now also means that the
  runtime could not load a version's bundle: the sweep takes what is scored from the runtime's
  own loader. `PLAIN` is what the sweep
  cannot classify, an upper bound. The sweep classifies each model in a bundle by its model type: a GLM is examined; a
  model of another family (a GBM or an EBM) keeps the `02` FR-131 refusal whatever a Factor
  declares, is not examined, and is counted on the `not-examined-other-family` line; a model with
  no fit result, no model type or an unknown one makes its version unreadable (exit 2). Every
  unreadable line names the version and either a fixed reason word or the exception's type, never
  its text. A version it
  lists will refuse the quotes it names until a new model is approved: a declaration changes only
  by a new Factor version, a refit and a new Rating Version. A batch carrying many such rows can
  abort above `rating.batch_abort_failure_rate`.
- **Upgrading to the build that refuses a stored bundle on a `control` operand** (WK-2113 S3,
  FD-1495): a stored Rating Version compiled before the `control`-intent guards existed is now
  refused wherever it is hydrated, and a deploy, a rollback or a deployment request for it is
  refused too (`CONTROL_FACTOR_IN_RATEABLE_PATH`, a 409 problem; one Audit Event
  `rating_version.load_refused` per process per bundle). **Before upgrading, run the sweep**, a
  read-only script that lists every stored version the new build will refuse:
  `uv run python scripts/sweep-stored-bundles.py [--dsn <read-only URL>] [--workspace <id>]`.
  It prints its denominators first (`versions`, `with a bundle`, `checked`), one `OFFENDER` line
  per version (reference, hash, which half found it, the Factor and the interaction), and exits
  0 (clean), 1 (an offender) or 2 (a bundle could not be read, so it is not shown clean). The
  remedy for an offender is a **new version** (a compiled version is never mutated: compile is
  draft-only), not an edit. **Do not enable blob garbage collection (FR-420, OQ-1943) before every existing bundle blob is retained**: versions compiled before this build hold their bundle blob at `ref_count` 0, and the compile Job now retains the blob only for new compiles. **Restart every `api` replica and every `worker` after the upgrade:**
  a running process holds the bundles it already hydrated and re-validates nothing it holds
  (`roll-api.sh` keeps the old replicas serving until the new ones pass their healthcheck, so an
  old process serves until it is removed).
- **Rolling `api` to a new image is health-gated** (NFR-531). A plain `up --scale api=2`
  recreates every replica at once, so none is healthy until the new ones pass their healthcheck.
  Run `GIP_BUILD=<new> deploy/roll-api.sh [-t <seconds>] <project> <compose-file>...`. `lb`
  re-resolves `api` every second and retries the next upstream, so it needs no change.
  `roll-api.sh` fails loud, and a failed roll before the old replicas are stopped returns to the
  pre-roll replicas, removing the new ones. A pre-roll replica that is already stopped counts as
  an old one: a failed roll leaves it in place, and a successful roll removes it with the others
  (FD-1816).
- **`migrate`** is a one-shot step (FR-435). `api` and `worker` wait for it to exit 0; nothing
  migrates at application start.
  Take a database backup before you run `migrate` against a database that holds production
  artifacts (`07` FR-416, as amended): a conditionally irreversible migration can be undone only by
  restoring that backup.
- **`api`** has no dependency on `worker` (FR-434): `up api lb` starts the scoring API with no
  compute worker present (NFR-534). `lb` is the stated topology: one nginx, round-robin over the
  `api` replicas through Docker DNS (`deploy/lb.conf`).
- **Upload body limit** (FR-450): the API refuses a request body past `GIP_MAX_UPLOAD_BODY_MIB`
  (default 64) on the two upload routes with an RFC 9457 `413`. `client_max_body_size` in
  `deploy/lb.conf` and in `deploy/frontend.nginx.conf` is that limit plus 1 MiB (`65m`), so the
  proxy never answers first: nginx's default of 1 MiB would return its own HTML `413`. A tested
  default is held to both files; **a deployer who raises `GIP_MAX_UPLOAD_BODY_MIB` raises both
  nginx values to the new limit plus 1 MiB**, and nothing in the stack does it for them.
- **`worker`** runs Celery with a container `mem_limit`; a Job's own `resource_budget.memory_gb`
  is checked inside the process and fails the Job naming the budget (FR-412, FR-415).
- **`scheduler`** is the Celery beat process (FR-432, FR-413, FR-406): the outbox relay is a beat
  schedule entry, so without it a committed Job stays `queued`. It is one process and never
  scaled; its schedule file is under `/tmp`, because the image's working directory is not writable.
- **`frontend`** is the built SPA on nginx (FR-432), built from `deploy/frontend.Dockerfile` with
  the repository root as the context. It serves `/` with a history fallback and proxies `/api/`
  to `lb`, so the browser stays same-origin. It publishes `127.0.0.1:${GIP_WEB_PORT:-5173}`, the
  port the local realm admits; stop the Vite dev server first, or set `GIP_WEB_PORT`.
- **Shutdown** (FD-1211): each process finalizes the interpreter on SIGTERM, then the container is
  replaced.
- **Production identity provider:** `deploy/keycloak/` is a reference you operate (FR-437).

`deploy/docker-compose.isolated.yml` is for the runtime tests: it publishes the backing services
on ephemeral ports so a test project cannot collide with the dev stack.

## The audit anchor signing key (FR-373)

The audit anchor (`POST /api/v1/audit/anchor`) is the customer's ritual: it is offered, never on by
default. It signs the chain head with an Ed25519 key you hold.

- **The key** is the setting `GIP_AUDIT_ANCHOR_SIGNING_KEY`: an unencrypted PKCS#8 PEM Ed25519
  private key, for example the output of `openssl genpkey -algorithm ed25519`. It is a secret
  setting until `07` FR-424's secret backend exists, so keep it out of the compose file you commit.
  A value that is set and is not an Ed25519 key refuses start-up. With no value the platform starts
  and the anchor route answers `503` `AUDIT_ANCHOR_KEY_UNCONFIGURED`.
- **Rotation** is: generate a new key, set the setting, restart. The platform keeps no retired key
  and needs none: an anchor carries the public key that verifies it, and the first anchor under a
  new key carries the `previous_key_id` of the one before it, so the rotation is visible in the
  chain and in what the customer stored. **Rotation does not revoke.** A signature made with a key
  that later leaked stays valid; what the customer relies on is the time it stored the anchor, in a
  store you do not control.
- **How a customer verifies an anchor** (it needs no platform access except steps 1 and 5):
  1. Call `POST /api/v1/audit/anchor` with an `audit:read` credential and store the whole response,
     unchanged, in a store the operator does not control.
  2. Pin the key: check that `key_id` equals `sha256:` plus the hex SHA-256 of the base64-decoded
     `public_key`, and that this key is one the customer pinned out of band (at onboarding, or
     announced by the operator at a rotation and matched by `previous_key_id`). A public key taken
     only from the response proves nothing against the operator.
  3. Rebuild the signed bytes from `statement`: `json.dumps(statement, sort_keys=True,
     separators=(",", ":"), ensure_ascii=False).encode()`.
  4. Verify the Ed25519 signature over those bytes with that public key, using any RFC 8032
     implementation. A failure means the stored anchor was altered or was not issued by the pinned key.
  5. Later, to detect a rewrite of history, export the log (`GET /api/v1/audit/export?format=json`)
     and check that the event at `head_sequence` has an `event_hash` equal to `head_event_hash`, and
     that `GET /api/v1/audit/verify` is intact over the range.
