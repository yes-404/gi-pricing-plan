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

## Verified

2026-08-14 — W2 sprint 1. 40 backend tests pass; the middleware-ordering trap was found by
a failing test asserting `trace_id` on the 500 path, not by reading Starlette's source.
