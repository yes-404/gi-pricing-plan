---
name: fastapi-service
description: Conventions and traps for the backend/ FastAPI service in this GI pricing platform — the app factory, RFC 9457 problem responses, trace propagation and where Starlette's middleware ordering breaks it, liveness vs readiness, and typed settings. Use when adding a route, middleware, error code, health probe or setting under backend/.
---

# The backend service

`07 — Platform` governs it; `00` §5 fixes the API conventions every module obeys. Package
is `app` (spec §5.2 names `app.platform.*`), under `backend/src/` per the repo's layout.

## The app factory takes its settings

```python
def create_app(settings: Settings | None = None) -> FastAPI
```

Not module-level globals. A test builds an app in `prod` to check the TLS refusal without
mutating the process, and two apps with different configs can coexist in one test session.

## Problem responses: four handlers, not one

Every non-2xx must be a `ProblemDetail` (`00` §5.3). That needs handlers for **all four**
paths, and missing any one leaks a second error shape:

| Raised by | Handler | Without it |
|---|---|---|
| Our code | `PlatformError` | — |
| FastAPI request parsing | `RequestValidationError` | `{"detail": [...]}`, no code |
| The router (404/405) | `StarletteHTTPException` | `{"detail": "Not Found"}`, no code, no trace |
| Anything unhandled | see the trap below | plain-text 500 |

`ProblemDetail` lives in `model-schema`, not here — every module returns it and the
frontend generates its type from it (ADR-0002).

`PlatformError` validates its `code` against the set enumerated in `07` §5.1. Adding a code
means adding it to the owning spec *first*; the constructor refuses an unknown one, which
is deliberate — an unenumerated code reaches a client as something it cannot branch on.

## The trap: `ServerErrorMiddleware` sits outside your middleware

An app-level `Exception` handler (`app.add_exception_handler(Exception, ...)`) is installed
on Starlette's `ServerErrorMiddleware`, which `build_middleware_stack` puts **outermost** —
outside every middleware you add.

So a `BaseHTTPMiddleware` that binds a context variable and clears it in `finally` has
already cleared it by the time that handler runs. The 500 response comes back with
`trace_id` **absent**, on precisely the path where R4 matters most:

```json
{"code": "INTERNAL_ERROR", "status": 500, "instance": "/boom"}   ← no trace_id
```

**Fix:** render the unexpected-error problem *inside* the trace middleware, where the
context is still live, and keep the app-level handler only as a backstop for exceptions
raised outside its reach. `backend/src/app/observability/middleware.py` does this.

Test it with `TestClient(app, raise_server_exceptions=False)` — the default re-raises into
the test, so the handler that exists for the unexpected is never exercised.

## Liveness and readiness are different questions

- `/healthz` — is the process alive? **Touches no dependency.** A failure restarts the
  container, so wiring the database into it turns a brief blip into a restart storm across
  every replica simultaneously.
- `/readyz` — can it serve? Probes database, Redis, blob store; failure removes the pod
  from the load balancer without restarting it.

Probes register themselves (`register_probe`), run concurrently, and are individually
timed out — an unanswered probe is indistinguishable to the orchestrator from a hung
process and gets the wrong remedy. A probe that raises is a *down component*, not a 500.
Probes are process-global, so tests need an autouse fixture clearing them.

## trace_id is 32 lowercase hex, not a ULID

W3C/OpenTelemetry `trace-id` (`00` §5.3). The point of the value is to join a problem
response to a span in a trace backend; a ULID reads like an identifier and correlates with
nothing. Inbound `traceparent` is **joined, not replaced**, so a request crossing a service
boundary stays one trace; a malformed header starts a new trace rather than failing the
request. All-zero is the W3C "no trace" sentinel and must be rejected.

*The four spec examples showed `01J…` until W2 implemented this and the mismatch surfaced.*

## Settings are typed, frozen, and validated at startup

FR-PLAT-44: an invalid setting prevents startup with a message naming the environment
variable — not an exception halfway through a job. `extra="forbid"` so a typo'd variable
fails loudly instead of being ignored. `frozen=True` so configuration cannot drift at
runtime. `resolve()` returns the value *and its source*, because "why is this setting what
it is?" is a support question with three layers of precedence behind it.

`database_url` is validated to the `postgresql+asyncpg://` scheme: a sync driver does not
error, it blocks the event loop, and the symptom is latency under concurrency.

## Persistence: the traps that cost real time

**`uv sync` is not enough** — see `python-package`. Everything below assumes the workspace
is synced with `--all-packages --dev` and `alembic upgrade head` has been run.

### Append-only needs three layers, and each covers what the one below cannot

Measured against PostgreSQL 16, not assumed:

| Layer | Stops | Bypassed by |
|---|---|---|
| Privileges — app connects as a **non-owner** role with `SELECT, INSERT` | the application | the table owner |
| Row trigger on `UPDATE`/`DELETE` | owner, stray `psql` | `session_replication_role = replica` |
| **Statement** trigger on `TRUNCATE` | `TRUNCATE` | same |
| Hash chain (FR-GOV-24) | nothing — it *detects* | nothing |

Two findings behind that table:

- **`REVOKE ... FROM <owner>` does nothing.** After revoking `UPDATE, DELETE` from the
  table owner, an owner `UPDATE` still reported `UPDATE 1`. Ownership carries implicit
  privileges. FR-GOV-22 is only real if the application connects as a role that does not
  own the table.
- **Row triggers do not fire on `TRUNCATE`.** A `BEFORE UPDATE OR DELETE ... FOR EACH ROW`
  trigger leaves `TRUNCATE audit_events` working perfectly, emptying the log in one
  statement. A second `BEFORE TRUNCATE ... FOR EACH STATEMENT` trigger is required.

### Tests cannot clean up an append-only table

There is no `DELETE FROM audit_events` between tests — by design. Isolation comes from a
**fresh `workspace_id` per test**, not from truncation.

### One canonical serialisation, or the chain lies

The hash must be computed from a *single* model (`AuditEventCore`), used by the writer and
the verifier alike. Writing the hashed payload as a hand-built dict in one place and
`model_dump(mode="json")` in another produced a chain that verified against itself and
failed against the exported record — the datetime format differed. A chain that verifies
in one code path and not another is worse than none, because it is believed.

### Alembic drops tables but not ENUM types

Autogenerated `downgrade()` leaves `job_kind`, `job_status`, … behind, so
`downgrade` → `upgrade` fails with `DuplicateObjectError: type "job_source" already
exists`. Add explicit `DROP TYPE IF EXISTS` to `downgrade()` and **prove the round-trip
twice** — a rollback that cannot be re-applied is a one-way door (FR-PLAT-35).

Also: reuse an existing type with `create_type=False` on the second and later tables, or
the migration tries to create it again within a single upgrade.

### Blob store: write order is not symmetric

    upload to S3  →  then insert the row

A crash between them leaves an object with no row — an orphan, which GC reclaims. The
reverse leaves a row with no object: a reference that resolves to nothing, which no sweep
repairs and which surfaces months later when someone opens a dataset. Orphaned bytes are
cheap; dangling references are not.

Content addressing makes the upload safely repeatable, so the retry is free.

### Content addressing makes fixed test payloads stateful

`put(b"counted content")` returns the *existing* row on the second run, reference count and
all. A test asserting `ref_count == 1` passes once and fails for ever after. Deduplication
working correctly is precisely what causes this. Generate unique payloads per run.

The same reasoning as audit: with a persistent database, isolation comes from unique data,
not from cleanup.

### MinIO needs path-style addressing and a bucket

`BotoConfig(s3={"addressing_style": "path"})` — MinIO does not serve virtual-host style
buckets by default and the failure is a DNS error that looks nothing like configuration.
`ensure_bucket()` is idempotent and runs at startup: a missing bucket fails every write
with an error that reads as a credentials problem.

### Credentials are `SecretStr`, and GC dry-runs by default

`SecretStr` redacts in every `repr` and `model_dump`, so an accidental
`log.info(..., extra={"settings": settings})` cannot leak them (R3) — the protection is in
the type, not in remembering. And `collect_garbage(dry_run=True)` by default: a destructive
sweep whose default is to destroy is one that gets run by accident.

### Authentication

Three credential paths, all fail-closed: OIDC bearer, service-account API key, and
local-only development headers that `require_startable` refuses in `uat`/`prod`.

**The workspace is never taken from the request.** It is derived from membership (users) or
from the account's own row (service accounts). A header-supplied workspace makes tenancy a
claim rather than a fact.

### Token verification: five things, and the allow-list is the important one

Signature, algorithm, issuer, audience, expiry. **Restrict algorithms to asymmetric
families.** Accepting `HS256` beside an RSA key set is algorithm confusion: the *public*
key becomes the HMAC secret, so anyone who can read the JWKS can mint tokens for any user.

Testing that attack needs a **hand-assembled** token — `jwt.encode` refuses to sign HS256
with a PEM public key. That guard protects the signer; an attacker is not using PyJWT, so
testing through it proves nothing about the verifier.

Never return the rejection reason. "Expired" versus "bad signature" tells an attacker what
to fix next and tells a legitimate caller nothing the trace id does not.

### API keys: hash the secret, store the prefix

Prefix in clear so a leaked key is identifiable and revocable without anyone holding the
secret; SHA-256 of the secret because these are 256 random bits — a slow KDF protects
*low-entropy* secrets and here only adds latency to every scoring request. Constant-time
compare. An unknown prefix and a wrong secret must fail **identically**, or the prefix
becomes an oracle for which keys exist.

**No field may contain the separator.** `secrets.token_urlsafe` includes `_`, which is the
character separating key fields — `parse_key` handled it with `maxsplit=3`, but the format
invited a `rsplit` mistake that landed within the hour. `token_hex` has no such character.

The environment inside a key is a **label, not an authorisation**: it is attacker-supplied
and not covered by the hash. Check it against the account's grant.

## Collection endpoints

**Cursor, never offset** (`00` §5.2). With `OFFSET`, a row inserted while a client pages
shifts everything after it — the client sees one row twice and misses another. On a jobs
list refreshed while jobs are submitted, that is the normal case.

Fetch `limit + 1` rows and return `limit`: the extra row answers "is there another page?"
without a second query. The cursor is opaque so clients cannot come to depend on the sort
key.

**`total_estimate` is capped, not exact.** FR-PLAT-14 keeps 13 months of job history; an
unbounded `COUNT(*)` scans the year to render one page.

### UUIDv7's leading bits are a timestamp, so `hex[:8]` is not unique

`f"user-{new_uuid7().hex[:8]}"` collides for anything created in the same millisecond —
two tests shared a user, and one inherited the other's workspace memberships. Take the
**tail** when you want randomness, or the whole thing.

This is the same property as the ordering trap below, seen from the other side: the head is
time and the tail is entropy.

### UUIDv7 does not order within a millisecond

It is a fine cursor for "newest first" and a poor one for "in the order these happened".
Three log lines written in one transaction came back scrambled, because ids in the same
millisecond have no defined order — and `at` ties too, since every row in a transaction
shares its transaction timestamp.

For anything where **insertion order is the meaning** (log lines), use a database-assigned
`Identity()` column and order by it. This is the same rule the audit chain already
follows with its per-workspace `sequence`; it just has to be applied everywhere order
matters, not only where tamper-evidence does.

## `pytest.raises(match=...)` on a `PlatformError` tests the *detail*

`PlatformError.__str__` is `detail or title`, so `match="requires a reason"` compares
against the long explanatory sentence, not the short title. It has produced a confusing
failure twice. Assert the field you mean:

```python
with pytest.raises(PlatformError) as exc:
    ...
assert exc.value.code == "BREAK_GLASS_REASON_REQUIRED"
assert exc.value.title == "Withdrawal requires a reason"
```

The `code` is the contract anyway — it is what a client branches on — so asserting it is
both more correct and more stable than any substring of prose.

## Routes must fail closed

`require_caller` returns **401** when no identity provider is configured, and
`Settings.require_startable` refuses to boot with development identity enabled in `uat` or
`prod`. A route added later inherits the refusal by depending on it, rather than having to
remember to ask for authentication.

**Cross-tenant reads are 404, not 403.** A 403 confirms the id exists, which is a
disclosure in a multi-tenant system even when the body says nothing else.

## SSE: poll, do not subscribe

`LISTEN`/`NOTIFY` holds a database connection per viewer; a jobs page open in three
browsers exhausts the pool. Poll one row on an interval, emit only on change, and **close
the stream when the job is terminal** — otherwise a client that forgets to unsubscribe
holds the connection for ever. Send `X-Accel-Buffering: no`, or a proxy buffers the stream
and the client sees nothing until the job ends, which looks exactly like a hung job.

## Test fixtures must take the test DSN explicitly

An app fixture built from a bare `Settings()` falls back to the packaged default DSN
whenever `GIP_DATABASE_URL` is unset — true locally, false in CI. The tests then pass on
the runner and fail on a developer machine. Source it from the same helper the database
fixture uses.

## Worker: a sync protocol over an async data layer

`pricing_core.progress.ProgressCallback` is **synchronous** — a fitting loop calls
`update()` between rounds — while the data layer is async. Three options, only one works:

| Approach | Outcome |
|---|---|
| `asyncio.run()` inside the callback | New loop per tick; the engine's connections detach from it |
| A second, synchronous SQLAlchemy stack | Two implementations of the audit write — the split that produced a self-consistent, externally-invalid hash chain |
| **Run the handler in a thread; marshal writes back with `run_coroutine_threadsafe`** | One data layer, one audit path |

So: `await asyncio.to_thread(handler, params, progress)`, and the callback does
`asyncio.run_coroutine_threadsafe(coro, loop).result(timeout=...)`. Throttle both the
progress write and the cancellation poll — a tight loop otherwise turns a fit into a
database benchmark.

### The Celery app is a factory, not a module global

Constructing it reads settings and opens a broker connection. Every test and tooling script
imports worker code without wanting either. `entrypoint.py` holds the one module-level app,
imported only when a worker is actually started.

### `asyncio.run()` per task is correct here

A long-lived loop shared across tasks binds the engine's connections to it, and a prefork
child inherits a loop it must not use. Jobs are long-running by definition, so a connection
per Job is not the cost that matters.

### At-least-once means the consumer must be idempotent

`task_acks_late` plus outbox redelivery means a Job can arrive twice. `execute_job` returns
early unless the row is still `queued`. Test it by calling the task twice and asserting the
handler ran once.

### Never `pkill -f` a pattern your own command line contains

`pkill -f "celery -A app.worker.entrypoint"` matches the shell running it and kills the
session. The same trap makes `ps | grep -c 'entrypoint worker'` report phantom processes.
Use `pgrep -x <name>`, or `awk '/pattern/ && !/awk/'`.

## Async fixtures are function-scoped

A `scope="session"` async engine binds connections to the loop that created it, while
pytest-asyncio gives each test a fresh loop. The symptom is
`got Future attached to a different loop`, which reads like a driver bug. Create the engine
per test.

### The unit of work owns the transaction boundary

`audit.record()` and `outbox.enqueue()` **raise** when there is no open transaction, and
`outbox.publish_directly()` raises when there *is* one (FR-PLAT-51). Services take a
session; only `Database.unit_of_work()` commits. If a service needs its own transaction,
that is the bug — not the guard.

## Verified

2026-08-14 — W2 OIDC slice. 218 tests pass, the suite run five times to confirm it after
three genuine flakes were found and fixed — two of them real defects in the code and test
data rather than in the harness.

2026-08-14 — W2 jobs-routes slice. 173 tests pass; the full suite was run seven times to
confirm it is repeatable, after one run failed two tests that did not reproduce. The
likeliest cause — process-global readiness probes cleared only on fixture entry — was made
order-independent rather than left to chance.

2026-08-14 — W2 Celery slice. 154 tests pass. The full seam was verified with a real
worker process against the compose stack: submit in a transaction, relay after commit,
broker hop, worker dispatch, typed failure, audit chain verified. No handlers are
registered yet (they arrive with W4/W5), so the correct end state was
`JOB_HANDLER_NOT_REGISTERED` — which still exercises every hop.

2026-08-14 — W2 blob slice. 115 tests pass; blob behaviours verified against real MinIO,
and the suite re-run to confirm it is repeatable rather than passing once.

2026-08-14 — W2 persistence slice. 96 tests pass (75 backend, of which 35 run against a
real PostgreSQL 16). Every claim in the append-only table was measured against the running
database before the migration was written, and the migration round-trip was run twice.

2026-08-14 — W2 sprint 1. 40 backend tests pass; the middleware-ordering trap was found by
a failing test asserting `trace_id` on the 500 path, not by reading Starlette's source.
