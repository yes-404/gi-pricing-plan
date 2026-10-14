---
id: FD-8049
family: finding
title: The score rate-limit test pins the limiter's clock beside a real-time 2-second Redis expiry, so a stall of more than 2 seconds between requests resets the counter and the 4th request is admitted
status: active
created: 2026-10-14
owner: auditor
tree: beee5ebedcfebc03c1658728442827960975392a
corrected_by: []
relates: [WK-1178, FR-452, FR-430, RL-1347, P2]
---

# FD-8049 — the rate-limit flake: a pinned window key beside a real 2-second TTL

*(Filed under working id 8049, reserved by the lead; a minter folds it into the docs batch.
Authority: the maintainer's (by delegation) entry "2026-10-14 14:30:54 BST" in
`channel/to-lead.md`: *"FD: YES, in D18, owner WK-1178 … Proposed MEDIUM … Fix in P2 (small),
red first. Until fixed, a gate red on exactly this test, with this assert, may be re-run once."*
Citations read at `origin/main` `beee5ebedcfebc03c1658728442827960975392a`, written 2026-10-14 16:11:40 BST.)*

## Finding

**Severity: MEDIUM, proposed by the auditor (confirming the maintainer's proposal). Owner WK-1178.**

CI run 38568100882 (D16 #1304 at `5e03ced9`, python job) failed
`backend/tests/test_score_rate_limit.py::test_the_counter_is_shared_across_replicas_and_the_refusal_carries_retry_after`
with `assert 409 == 429` at `:128` (the refused request). 409 is `NO_LIVE_RATING_VERSION`, the handler's
refusal after the limiter *admitted* the request (module docstring, `:6-11`). The re-run of the
failed job passed (5847 passed); D16 is docs and `.claude` only.

### Mechanism (hypothesis; the by-run reproduction is OWED, see below)

- The test pins the limiter clock: `_app_client` sets `client.app.state.rate_limiter.clock = lambda:
  FIXED_SECOND` (`test_score_rate_limit.py:54`; `FIXED_SECOND = 1_800_000_000.0`, `:42`). Every request
  of the test therefore counts into **one** key: `RateLimiter.key(...)` ends in `int(self.clock())`
  (`rate_limit.py:85-87`).
- `RateLimiter.admit` runs `pipe.incr(key)` then `pipe.expire(key, _KEY_TTL_SECONDS)` in one
  transaction (`rate_limit.py:97-99`), `_KEY_TTL_SECONDS = 2` (`:39`). Redis evaluates that TTL in
  **real** time and each request refreshes it.
- So the key lives only while consecutive requests arrive within 2 real seconds. A gap of more than 2
  s between two requests of the test (a loaded CI runner, a GC pause, a slow request on a gate box)
  lets Redis delete the key; the next `INCR` returns 1, and the request is admitted (`count <= limit`,
  `:105`). In the failing test the limit is 3 (`:122`); a reset before the 4th request gives `count=1`
  and a 409 where 429 is asserted.

### §0 classification — which side is wrong

**The test is wrong; the limiter is correct.** In production the clock is the real clock throughout.
A request in window `w` (real second) writes key `...:w` with a 2 s TTL. That key is read only while
real time is in `[w, w+1)`, so at most 1 s remains of the window; a 2 s TTL set at or after `w`'s
start cannot lapse inside the window, whatever the gaps between requests. The module's own
rationale (`:36-38`) says the TTL "only removes old windows". The premise "TTL outlives the window"
holds only when the key's window and Redis's clock are the same clock. The test breaks that premise by
stopping one clock (the window) and not the other (the TTL): the window never ends, but the key
does. The module comment at `rate_limit.py:77-78` says the pin exists "so a run cannot straddle a
second boundary and flake"; it removed one flake and introduced a second, of a different kind.

**No production change is warranted.** The fix is in the test's coupling, never a sleep or a retry:

1. Preferred: the test fixture `monkeypatch.setattr(rate_limit, "_KEY_TTL_SECONDS", 3600)` in
   `_app_client`. `admit` reads the module global at call time, so this needs no new seam, and a
   pinned window with a TTL the run cannot outrun is the same relation production has (TTL >= window
   remaining). The file's `test_a_request_refused_at_authentication...` reads the key directly
   (`:277`) and is unaffected.
2. Alternative, heavier: make the TTL a `RateLimiter` constructor argument. A new public seam for a
   test; not recommended unless WK-1178 needs the TTL configurable anyway.

A red-first regression test belongs with the fix: a test that deletes the key between two requests
(`redis.delete`, no sleep) is red on today's tree only if it asserts the TTL-independence; the cheaper
red is asserting `await redis.ttl(key) > 60` after one request, red at 2.

### Condition on the fix — expiry must stay tested (2026-10-14 16:42:26 BST; the maintainer's (by delegation) ruling accepting FD-8049, in `to-lead.md`, entry "2026-10-14 16:43:11 BST — FD 8049 accepted + the expiry-coverage condition", which restates the ruling first sent after 16:41:40)

Patching `_KEY_TTL_SECONDS` to 3600 in the fixture is the allowed "TTL the pinned clock cannot
outrun", **on condition it leaves the limiter's key expiry covered.** Checked by reading
`git grep -nEi '\bttl\b|expire|_KEY_TTL|pexpire' -- backend/tests` at the D18 tree: **no test covers it.**
Every hit is a different subject (API-key `expires_at`, SQLAlchemy `expire_on_commit`, token expiry);
none touches `gip:ratelimit:*` TTL, and `test_score_rate_limit.py` has no hit. Today nothing would fail
if `pipe.expire` were deleted, which is the second defect the fix must close: with the line gone the
counter keys never leave Redis.

**So the fix MUST ADD an expiry test**, red first on a planted no-expire (`pipe.expire` removed in a
scratch copy: red, printed in its ledger, reverted). The 16:43:11 entry accepts this form, verbatim:
*"(i) after one admit, `PTTL key` in (0, ttl·1000]; (ii) with an injected TTL of 1 s, a BOUNDED poll
(max 3 s, polling `EXISTS`, not a fixed sleep) sees the key gone, and the next admit counts 1. …
A real-time bounded poll against Redis is the only honest way to test a real TTL; it is not a retry."*
Its finding that no expiry test exists today is the one recorded above.

**Land early: struck twice today (D16 `5e03ced9`, D17 `3012748a`).**

## Sweep (item 3)

Predicates, run with `git grep` at `beee5ebedcfebc03c1658728442827960975392a` (the D18 worktree, which carries no change under `backend/`
or `packages/`):

- **P-clock** (a pinned or injected clock): `git grep -nE '(rate_limiter|limiter)\.clock *=|clock *= *lambda|RateLimiter\(.*clock|clock=' -- backend packages`
- **P-ttl** (a Redis expiry or TTL): `git grep -nE '\.(expire|pexpire|setex|psetex|expireat)\(|ex=[0-9A-Za-z_]|px=[0-9A-Za-z_]|_TTL|\bttl\b' -- 'backend/src' 'backend/tests' 'packages/*/src' 'packages/*/tests'`

The pattern needs both: a pinned clock and a real-time expiry on the same key.

| Hit | Predicate | Verdict |
|---|---|---|
| `backend/src/app/platform/rate_limit.py:39`, `:99` | P-ttl (the only two) | the real-time expiry; correct in production |
| `backend/tests/test_score_rate_limit.py:54` | P-clock | **the pin; the defect.** Applies to every test using `client`/`second_client` |
| `:229`, `:259` | P-clock | pin on a limiter whose Redis is a closed port (`redis://127.0.0.1:1/0`): no key is ever written, **not exposed** |

No other `expire`/`setex`/`ex=` call exists under `backend/` or `packages/*`, and no other pinned
clock (a search for `freezegun`, `time_machine`, `monkeypatch` of `time.time`/`monotonic` found none).
So the pattern occurs **once**, in this module and its one test file. Within that file the exposed
tests are those sending 2 or more requests under one account on real Redis through the pinned
`client`: `:117` (the failing one, 5 requests), `:137` (2 on `dev`), `:149` (2, then 1, then 5), `:181`
(6); the loop at `:172-177` is the same shape. They share the fix; the failing test is the longest
exposure, which is why it was the one that failed. `:203` (no limit, no counter) is not exposed.

## Reproduction (item 1): OWED, a gate-1 window (needs the DB + Redis fixtures)

Not run: an ALONE gate held the box when this was filed, and the test needs Postgres and Redis.
The plan, with no sleep in production code and no committed change: a throwaway copy of the test in
the job's scratch directory (not under the repo) whose only difference is a helper that, before the 4th
request, sleeps `GAP` real seconds (the injected stall; a sleep in a *repro harness*, not a fix):

```
GIP_FD8049_GAP=2.5 uv run --directory <worktree> pytest <scratch>/repro_fd8049.py -q   # expect RED: assert 409 == 429
GIP_FD8049_GAP=0   uv run --directory <worktree> pytest <scratch>/repro_fd8049.py -q   # expect GREEN
```

and the same pair with the fix of the preferred option applied (`_KEY_TTL_SECONDS` patched to 3600),
where `GAP=2.5` must turn **green**, proving the cause and the fix. Both outputs are to be printed
into this essay before it is set `closed`. Until then the mechanism above is a hypothesis that
fits the symptom (409 in place of 429, passes on re-run) and does not yet exclude another cause.

## Evidence

- CI run 38568100882 (python job, D16 #1304 at `5e03ced9`): `assert 409 == 429` at `test_score_rate_limit.py:128`;
  the re-run of the failed job passed (5847). The maintainer's entry "2026-10-14 14:30:54 BST" records both.
- Re-readable at the stated tree: `git show origin/main:backend/src/app/platform/rate_limit.py | sed -n 36,40p` (the TTL),
  `| sed -n 94,106p` (the pipeline and the `count <= limit` test); `git show origin/main:backend/tests/test_score_rate_limit.py | sed -n 50,55p` (the pin).
- By-run reproduction: OWED (see above); until it is printed here the mechanism is a hypothesis.

## Why MEDIUM, proposed

- Against HIGH: no wrong price or wrong refusal ships; the limiter is correct in production.
- Against LOW: it is a flake in the full suite, and each occurrence costs a CI or gate cycle (the
  maintainer's entry: gate cycles are the scarce resource, 6-8 a day). It already cost one re-run.
- Re-rate trigger: HIGH if the by-run reproduction shows the production limiter, not the test, can
  reset (a real-clock case this analysis missed).

## Disposition

Standing, until fixed (the maintainer's (by delegation) entry "2026-10-14 14:30:54 BST"): a gate red
on exactly this test with exactly this assert may be re-run **once**; any other failure may not.
The event that next discharges it: the WK-1178 slice in P2 that lands the red-first test and the
fixture change, with the by-run reproduction printed here.
