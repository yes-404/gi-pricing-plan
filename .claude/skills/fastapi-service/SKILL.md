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

### Async fixtures are function-scoped

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

2026-08-14 — W2 blob slice. 115 tests pass; blob behaviours verified against real MinIO,
and the suite re-run to confirm it is repeatable rather than passing once.

2026-08-14 — W2 persistence slice. 96 tests pass (75 backend, of which 35 run against a
real PostgreSQL 16). Every claim in the append-only table was measured against the running
database before the migration was written, and the migration round-trip was run twice.

2026-08-14 — W2 sprint 1. 40 backend tests pass; the middleware-ordering trap was found by
a failing test asserting `trace_id` on the 500 path, not by reading Starlette's source.
