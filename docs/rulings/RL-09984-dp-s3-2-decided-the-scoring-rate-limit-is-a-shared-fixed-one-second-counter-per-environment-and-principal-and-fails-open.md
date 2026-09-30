---
id: RL-9984
family: ruling
title: PL-1342 DP-S3-2 decided — the scoring rate limit is a shared fixed one-second counter per Environment and Principal, limited by the account's own rate or an Environment default, and it fails open
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-30
owner: decision-maker
tree: 36b2a121662b9d69a309fee0e8023fbfff3a71ea
phase: P2
work: WK-674
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [PL-1342, SL-1257, FR-452, FR-430, FR-431, FR-446, NFR-499, NFR-497, NFR-489, RL-1184, RL-1311, ADR-710]
---

# RL-9984 — PL-1342 DP-S3-2 decided: the scoring rate limit is a shared fixed one-second counter per Environment and Principal, limited by the account's own rate or an Environment default, and it fails open

## How this was ruled

**Ruled at effort `high`**, by the decision-maker session `dm-s3dp`. Its first command,
`echo "CLAUDE_EFFORT=$CLAUDE_EFFORT"`, printed `CLAUDE_EFFORT=high`. The lead spawned it on the
maintainer's spawn order (`to-lead.md`, a local channel file outside the repository, the entry
"2026-09-30 22:31:50 BST", as the lead's brief relays it; this session did not read that entry).
PL-1342's row asks for "the decision-maker at medium effort". The charter's Model / effort line
(`.claude/roles/decision-maker.md:13`) allows high "for a decision-maker ruling … on the
maintainer's raise". The lead has flagged the difference to the maintainer.

**Working id 9984**, hand-assigned by the lead, who is the only allocator (`FD-1338`). Not minted.

**The question, as filed.** `PL-1342:406`, DP-S3-2, *"The rate-limit counter's key and limit"*,
blocking Task 5. The row names three options, recommends (b), and asks for two more rulings:
*"the window and the Redis-outage behaviour"* (auditor-close1255 L3). The WK-674 Slice 3 dispatch
record (`~/gi-pricing-plan.local/handover/DISPATCH-WK-674-S3-2026-09-30.md`, a local file) holds
Task 5 until this ruling mints (its "Delta 1", 2026-09-30 23:38:06 BST).

## Verified first, at 36b2a121662b9d69a309fee0e8023fbfff3a71ea

`origin/main` was `36b2a121` when this session fetched it (2026-09-30, about 23:30 BST). PL-1342
was written at `11c76b6c`, so its line numbers into `03` are older. Every citation below was
re-read at `36b2a121` with `git show origin/main:<path>`.

**The requirements.**
- **`07` FR-452** (`07:183`): *"Rate limiting is applied per Principal and per environment, with
  scoring limits configured separately from management-API limits, and `429` responses carrying
  `Retry-After`."* **PL-1342 does not cite FR-452.** It is the one requirement that states the
  limit's key and its response, so this ruling is written against it.
  `git grep -n 'FR-452' origin/main -- docs backend packages` finds it only in `07`,
  `docs/INDEX.md` and `docs/REDIRECTS.csv`. No plan, roadmap row or test names it, so it has no
  owner.
- **`07` FR-430** (`07:141`): Environments have *"independent Service Account scopes, rate limits,
  and monitoring configuration"*.
- **`07` FR-431** (`07:142`): *"Environment configuration (rate limits, sampling rates, feature
  flags) is a Setting resolved by the precedence in §3.8 and is audited on change."*
- **`03` NFR-499** (`03:1168`, not `03:1160` as PL-1342 cites it at its older tree): *"the scoring
  API authenticates per Consumer System with scoped credentials and per-client rate limits"*.
  A Consumer System is *"an external system … calling the scoring API"* (`00-overview.md:75`).
- **`03` NFR-497** (`03:1166`): the scoring endpoint *"targets 99.95 % monthly"*.
- **`03` NFR-489** (`03:1158`): p99 < 50 ms at 200 rps per replica, and < 15 ms without a GBM call.
- **Register row F48** (`docs/findings/register.md:89`) records the mechanism, decided
  2026-09-28: *"a shared Redis counter, per tenant. ADR-710 makes Redis per-tenant, and an
  in-process limiter 'is not a limit'"*. `RL-1184:217-218` (E6) carries the same words.
  `07` FR-17 makes the cache and broker per tenant, so the Redis instance is already the
  tenant's. No tenant id is needed in a key.

**The code.**
- **No limiter exists.** `git grep -n -E 'rate_limit_rps|RATE_LIMITED|Retry-After|retry_after' origin/main -- backend/src packages`
  prints six lines: `api/service_accounts.py:65`, `:90`, `:113`, `:175`, `db/models.py:432` and
  `errors.py:66`. None of them reads a limit. This reproduces F48.
- **`rate_limit_rps` is optional** on an account (`api/service_accounts.py:65`,
  `int | None`, `gt=0`). It is stored on the account row (`db/models.py:432`).
- **The account row is already read on every API-key request.** `authenticate_api_key` (`auth/service.py:163`) reads it at
  `auth/service.py:186` (`session.get(ServiceAccountRow, …)`) and builds the identity at `:229`.
  The identity carries the Principal (`kind=service_account`, `id=account.id`) and the
  Environment the key was presented for (`:238`, RL-916). It does not carry `rate_limit_rps`.
  `Caller` (`api/deps.py:60-70`) is the same: a Principal, a workspace, and `environment`, which
  is `None` for a bearer or development caller.
- **Which routes a Service Account can reach.** `ALLOWED_PERMISSIONS` is
  `{"score:execute", "score:batch"}` (`api/service_accounts.py:44`). `POST /api/v1/score` needs
  `score:execute` (`api/score.py:124`, `:290`). `POST /api/v1/score/batch` needs `score:batch`
  (`:125`, `:483`) and answers 202 with a Job. `POST /api/v1/score/compare` needs `rating:read`
  (`:338`), which no Service Account can hold.
- **The scoring path uses no Redis today.**
  `git grep -n -i redis origin/main -- backend/src/app/api/score.py backend/src/app/platform/traces.py backend/src/app/api/deps.py`
  prints nothing (exit 1). The bundle slot is in-process (`platform/bundle_slot.py:77`,
  "Failure posture: there is none to degrade to"). So a limiter adds the first network call
  outside the database to `/score`.
- **The precedent for a Redis outage** is `DiffCache`: *"Fail-open on purpose: Redis is an
  optimisation, not the correctness path. A cache outage degrades to a plain compute-on-read,
  never to a 500."* (`platform/diff_cache.py:16-17`; `except RedisError` at `:93`, `:106`).
- **`PlatformError` carries no response headers** (`errors.py:399-425`: `code`, `title`,
  `status_code`, `detail`, `errors`). FR-452's `Retry-After` needs one.
- **Metrics** exist (`observability/metrics.py`, Prometheus). Its docstring (`:3-9`) forbids a
  label with an unbounded value, such as a UUID.
- **A setting may be unset by default.** `modelling.max_factor_count` has `default=None`, and its
  description says "**Unset by default, and that is the decision**"
  (`platform/settings.py:148-152`).
- **Redis in CI and locally is Redis 7**: `redis:7-alpine` (`deploy/docker-compose.yml:25`;
  `.github/workflows/python.yml:132-133`, with `GIP_REDIS_URL` at `:307`).

## Options, weighed

- **Key: (a) and (b) share it.** One counter per (Environment, Principal). FR-452 says "per
  Principal and per environment", which is this key. FR-430's "independent … rate limits" follows
  from it: a burst in `uat` uses no part of `prod`'s count.
- **(a), the account's own rate or no limit: not adopted.** An account created without
  `rate_limit_rps` is never limited, and nothing an operator sets for an Environment changes that.
  FR-431 names rate limits as Environment configuration that is a Setting. Under (a) there is no
  such Setting.
- **(b), (a) plus an Environment setting as the default: adopted.** It gives FR-431 its Setting,
  resolved by FR-446's precedence with the Environment layer that this slice builds (`RL-1311`).
- **(c), a per-Environment aggregate cap as well: not adopted.** No requirement asks for a cap on
  the sum of all clients. It protects capacity, which is sizing, not NFR-499's per-client limit.
  It would be a second counter on every request.
- **The default's value.** A platform-wide number would limit a tenant's largest client on the day
  it upgrades, and the platform does not know a tenant's capacity. So the setting is unset by
  default, as `modelling.max_factor_count` is. The operator sets it for each Environment.
- **The window.** A fixed window is one `INCR` and one `EXPIRE`. At a boundary it admits up to
  twice the limit in one second, which is acceptable for a capacity control. A sliding log needs a
  sorted set per key. A token bucket needs a server-side script. Neither is asked for.
- **A Redis outage: fail open.** `/score` has no Redis dependency today. Fail-closed would make a
  cache outage a pricing outage, against NFR-497. The limit is a capacity control, and it is not
  the security boundary: authentication and the Environment check (`auth/service.py:214-224`)
  still run on every request. `DiffCache` is the same choice for the same reason.
- **Which routes.** NFR-499 is about the scoring API that Consumer Systems call. A Service Account
  reaches two routes. `/score` is the real-time path that NFR-489 budgets by requests per second.
  `/score/batch` submits a Job (202), and the worker pool bounds its load, not a request rate.
  `/score/compare` needs `rating:read`, so no Consumer System can call it.

## Ruled

### 1. The key

**One counter per (Environment, Principal) per one-second window, on `POST /api/v1/score`.**
- The Environment is `Caller.environment`: the Environment the presented key was verified for
  (RL-916). For a bearer or development caller it is `None`, and the key's Environment field is
  empty.
- The Principal is `Caller.principal`: its `kind` and its `id`. So FR-452's "per Principal" holds
  for every caller of `/score`, not only Service Accounts.
- The Redis key is `gip:ratelimit:score:{environment}:{principal_kind}:{principal_id}:{window}`.
  `{window}` is the integer Unix second of the request, read from a clock the module takes as a
  parameter (so that a test can fix it).
- No tenant id and no workspace id are in the key. The Redis instance is the tenant's (`07` FR-17,
  ADR-710), and a Principal id is a UUID.

### 2. The limit

The limit for a request is the first of these that is set:
1. **The account's own `rate_limit_rps`**, for a Service Account caller. The value comes from the
   account row that `authenticate_api_key` already reads (`auth/service.py:186`). It is carried on the
   authenticated identity and on `Caller` as `rate_limit_rps: int | None`, and it is `None` for
   every other kind of Principal. The limiter makes no second database read for it.
2. **The setting `scoring.default_client_rate_limit_rps`**, resolved through the Settings resolver
   with the caller's Environment (FR-446, `RL-1311`). Its definition:
   - type `int`, `default=None`, `constraints={"min": 1}`;
   - scope **workspace or Environment** (the scope that Task 4 builds), so a value set for `uat`
     changes no other Environment;
   - a description that says it is unset by default and why (the reason in "Options, weighed").
3. **Otherwise, no limit.** The request is admitted and **Redis is not called**.

An Environment setting does not lower an account's own rate. The account's value is more
specific, so it wins.

### 3. The window and the count

- **Fixed, one second.** In one transaction (`MULTI`/`EXEC`, a redis-py pipeline with
  `transaction=True`): `INCR` the key, then `EXPIRE` it for 2 seconds. The expiry only removes old
  keys, because the window is in the key. So a crash between the two commands cannot lock a
  client out.
- **The request is admitted if the count after `INCR` is at most the limit.** Otherwise it is
  refused. A refused request is also counted, and that is correct: it arrived in that second.
- **Clock skew between replicas** moves the window edge by the skew. With NTP that is
  milliseconds. It is accepted, and it is not corrected.

### 4. The refusal

- **429 `RATE_LIMITED`** (`errors.py:66`, a `07` code, `07:343`). The problem's `detail` names the
  limit and the window ("more than N requests in one second") and nothing from the request body.
- **The response carries `Retry-After: 1`** (FR-452). A fixed one-second window always ends within
  one second. `PlatformError` carries no headers (`errors.py:399-425`). The executor adds a way for
  it to carry response headers that the problem handler writes. That is the simplest carrier. The
  exact spelling is the executor's.
- **Order.** The limit runs after authentication and after the `score:execute` check, so a 401 or a
  403 is never counted. It runs before the Quote Context is scored, so a refused request scores
  nothing and persists nothing.
- `/score`'s OpenAPI entry (`responses=problems(…)`, `api/score.py`) adds 429, and the contract is
  regenerated (FR-451).

### 5. A Redis outage: fail open, logged and counted

- **Any `RedisError` from the counter** (a refused connection, a timeout, a reset) admits the
  request. The request is scored as if no limit applied.
- **Each such request is logged** at `WARNING`, once, with the error type and the Environment. The
  log line carries no quote input (NFR-499) and no credential. It **is counted** on a new Prometheus
  counter, `gip_rate_limit_unenforced_total`, with one label, `environment` (an empty string for a
  bearer caller). The label set is bounded (`observability/metrics.py:3-9`). No Principal id is a
  label.
- **The client has a bounded timeout.** One `redis.asyncio` client per process is built in the
  application's lifespan from `settings.redis_url` (`config.py:124`), with a socket connect timeout
  and a socket read timeout of **50 ms** each, and it is closed at shutdown. A hung Redis then costs
  a request at most about 100 ms, and only during the outage. The client is not created for each
  request (`DiffCache.from_url` does that on the rate-table route, and it is not copied here).
- **No circuit breaker.** Nothing requires one, and a refused connection fails at once.

### 6. The other routes, and FR-452's other limbs

- **`/score/batch` and `/score/compare` are not counted.** The reasons are in "Options, weighed".
- **Not delivered by this ruling: FR-452's management-API limits.** FR-452 says scoring limits are
  "configured separately from management-API limits". This ruling configures the scoring limit
  separately (its own setting, on `/score` only). It builds no management-API limit. FR-452 has no
  owner (see "Verified first"). **Which Work owns its management-API limb is scope, so it is the
  lead's, not this role's** (`CLAUDE.md` §12, "A question in no charter is the lead's"). It is
  raised to the lead below.

## What it obliges

WK-674 Slice 3, Task 5 (`PL-1342:452-456`), beside Acceptance 4:

- A rate-limit module under `backend/src/app/platform/` (PL-1342's write set names "a rate-limit
  module"), with rules 1–5.
- `scoring.default_client_rate_limit_rps` added to `REGISTRY` (`platform/settings.py`), with the
  scope of rule 2.
- `rate_limit_rps` carried on the authenticated identity (`auth/service.py:229-240`) and on
  `Caller` (`api/deps.py:60-70`), and set from the account row already read.
  **`auth/service.py` and `api/deps.py` are not in PL-1342's write set** (`auth/service.py` is
  listed as "none planned"). The lead adds both to the dispatch record's write set and runs the
  RL-1263 check against lane A before Task 5 starts.
- The `/score` dependency, after the `score:execute` check; 429 in its OpenAPI responses; the
  contract regenerated.
- The response-header carrier on `PlatformError` and the problem handler (`errors.py` is already
  in the dispatch record's write set; the handler's module is added if it is not `errors.py`).
- The process-wide Redis client, in the lifespan, with the timeouts of rule 5.
- The counter `gip_rate_limit_unenforced_total` in `observability/metrics.py`.
- `07` FR-452 is **not** reworded by the slice. This ruling adds its dated clause.

## Acceptance — the violation that must become detectable

These add to PL-1342 Acceptance 8. Each runs against the real Redis of the test environment (CI's
Redis 7 service; the local compose Redis). **A single-process test proves nothing here** (F48),
so cases 1 and 2 use two applications.
1. **Shared across replicas** (Acceptance 8 as written). Two applications (two `create_app` calls,
   two `TestClient`s, one Redis), with an account whose `rate_limit_rps` is 3 and the clock fixed
   to one second. Together they admit 3 `/score` requests. The 4th, from either application, is
   429 `RATE_LIMITED`. **The window is fixed by the injected clock**, so the test cannot straddle a
   second boundary and flake. Red on broken input: with the counter made per-process (an
   in-memory dict), the pair admits 6.
2. **`Retry-After`.** The 429 in case 1 carries `Retry-After: 1`, and its body is an RFC 9457
   problem with code `RATE_LIMITED`. Red first: no header.
3. **Independent per Environment (FR-430).** The same account holds a `dev` key and a `uat` key
   (Acceptance 4). With `dev`'s count at the limit, a `uat` request is admitted.
4. **The Environment default.** An account with no `rate_limit_rps`, with
   `scoring.default_client_rate_limit_rps` set to 2 for `uat` only: its 3rd `uat` request in a
   second is refused, and its `dev` requests are not limited. The same key set at workspace level
   limits both.
5. **The account's own rate wins.** With the account at 5 and the `uat` default at 2, the 3rd, 4th
   and 5th `uat` requests are admitted and the 6th is refused.
6. **No limit, no call.** With neither set, 20 requests in one second are admitted, and a Redis
   client that fails on any call is never called.
7. **Fail open.** With the Redis URL pointed at a closed port, a limited account's requests are
   all admitted (200), `gip_rate_limit_unenforced_total{environment="uat"}` rises by the number of
   requests, and one `WARNING` is logged per request, with no quote input in it. Red on broken
   input: with the `except RedisError` removed, the request fails (500).
8. **Not counted before authorisation.** A request refused with 401 or 403 leaves the count
   unchanged.
9. **Measured, not asserted (`CLAUDE.md` §13, NFR-489).** The limiter's own cost: p50 and p99 of
   the limiter call over 10,000 calls against the local Redis, quoted in the ledger with `uptime`,
   in the gate slot that Acceptance 11 names. This records what the new call adds to `/score`. It is
   not a pass/fail gate, because NFR-489 is measured on the whole path.

## Spec changes in this commit

- **`07` FR-452** gains a dated clause with rules 1–6.
- **`07` §8**, the `Celery + Redis` row: its "Used for" cell adds the scoring rate-limit counter
  (FR-452). This is a new use of a dependency that is already there. No dependency is added, and
  `uv.lock` and `pyproject.toml` do not change.
- **`docs/skills-map.md`**, the `Redis (cache semantics)` row: "Used in" adds `07 FR-452`, and its
  skills note adds the fixed-window counter and the fail-open rule.
- **Not edited here:** FR-430, FR-431 and NFR-499. Each already says what this ruling implements.
  PL-1342 is frozen and is not edited (`document-ids.md` §1.5).

## Raised to the lead (not ruled here)

- **FR-452's management-API limb has no owner.** Scope, so the lead's or the maintainer's.
- **The write set.** `auth/service.py` and `api/deps.py` join Task 5's write set (above).
- **PL-1342 cites NFR-499 at `03:1160` and NFR-496 at `03:1157`.** At `36b2a121` they are at
  `03:1168` and `03:1165`. The plan is frozen. The executor re-derives line numbers at its own tree,
  as the plan tells it to (`PL-1342:371`).
