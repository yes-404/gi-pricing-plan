---
id: LG-1720
family: ledger
title: WK-1178 slice SL-1719 — FD 8049, the score rate-limit test's key expiry cannot outrun the pinned clock and the limiter's key expiry is tested, slice ledger
status: closed                 # active → closed (§1.2a)
created: 2026-10-14
owner: executor
tree: beee5ebedcfebc03c1658728442827960975392a
phase: P2
work: WK-1178
slice: SL-1719
plans: []
corrected_by: []
relates: [SL-1719, FD 8049, FR-452, FR-430, RL-1347]
---

# LG-1720 — WK-1178 slice SL-1719: the score rate-limit test's key expiry

Minted 2026-10-14 as LG-1720 from working id 8052, with SL-1719 from working id 8051, in the FD 8049 fix PR (the maintainer's (by delegation) entry "2026-10-14 17:15:00 BST", (A)).

**GO:** the maintainer's (by delegation) entry "2026-10-14 17:11:47 BST" in `to-lead.md` (the fix is test-only; scope exactly: the fixture makes the limiter's TTL 3600, plus the two expiry tests, each red first on a planted no-expire, no change to `backend/src`), with "2026-10-14 16:43:11 BST" (the accepted test form and the expiry-coverage condition) and "2026-10-14 14:30:54 BST" (the FD). The finding is FD 8049, not on `main` yet (it rides D18).
**CI is the gate:** the maintainer's (by delegation) entry "2026-10-14 17:11:47 BST", ruling (a′): *"FD 8049's fix is TEST-ONLY, so CI's full python run on its PR head IS its gate"*; no gate-1 cycle. ACK: CI python, docs and history green at the head; merge-tree rc 0.
**MERGE-ACK:** not yet given.
**Audit:** written 2026-10-14 17:59:52 BST (see `### Audit`); verdict PROPOSED, the lead's to adopt. ADOPTED by the lead (team-lead, transcript b6860f8f) at from-lead "2026-10-14 18:00:55 BST", conditional on CI python green; the condition was MET at run 38607168256 (b374d1bb, "5858 passed, 6 skipped").

## Tasks

Branch `sl-8051-fd8049-ratelimit-ttl`, worktree `.claude/worktrees/sl-8051`, cut from `origin/main` `beee5ebe`.

- **Fixture:** `_app_client` takes `monkeypatch` and sets `rate_limit._KEY_TTL_SECONDS` to 3600 (`admit` reads the module global at call time); the `client` and `second_client` fixtures pass it through.
- **Expiry test (i):** `test_an_admitted_request_leaves_a_key_with_a_bounded_expiry` — after one admit, `0 < PTTL <= _KEY_TTL_SECONDS * 1000`.
- **Expiry test (ii):** `test_an_expired_key_is_gone_and_the_next_admit_counts_one` — TTL injected as 1 s, a bounded `EXISTS` poll (deadline 3 s, 50 ms interval), then the key is gone and the next admit leaves the count at `b"1"`.
- **`backend/src`:** unchanged; `git diff origin/main --name-only -- backend/src` prints nothing.

### Reds, by their cause

Run by `/home/puzhenhao1989/.claude/jobs/b6860f8f/tmp/sl8051-reds.sh <worktree>` in the lead's DB-prep window: the `pipe.expire` line is removed from `backend/src/app/platform/rate_limit.py` in the working tree only, never committed.

Run in the lead's DB-prep window at head `95e97d84d6f6b2f79e941a3962f217be32524bbe`, tree `ddf10b4fd7e8cd7ff56100a92afadab5f93e8073` (START 2026-10-14T16:52:04+00:00; logs `window.log`, `red.log`, `green.log`). DB `gipricing_sl-8051_18ee3a35`, alembic rc 0. The planted no-expire, working tree only, never committed:

```diff
--- a/backend/src/app/platform/rate_limit.py
+++ b/backend/src/app/platform/rate_limit.py
@@ -96,8 +96,7 @@ class RateLimiter:
         try:
             async with self._client.pipeline(transaction=True) as pipe:
                 pipe.incr(key)
-                pipe.expire(key, _KEY_TTL_SECONDS)
-                count, _ = await pipe.execute()
+                (count,) = await pipe.execute()
         except RedisError as exc:
```

Planted run, `rc=1`: `3 failed, 8 passed, 1 skipped, 1 warning in 50.89s`.

```text
FAILED backend/tests/test_score_rate_limit.py::test_the_environment_default_limits_only_its_environment
FAILED backend/tests/test_score_rate_limit.py::test_an_admitted_request_leaves_a_key_with_a_bounded_expiry
FAILED backend/tests/test_score_rate_limit.py::test_an_expired_key_is_gone_and_the_next_admit_counts_one
```

- **Red (i)**, `test_an_admitted_request_leaves_a_key_with_a_bounded_expiry`: `E   assert 0 < -1` at `test_score_rate_limit.py:317` (`PTTL` is -1, no expiry).
- **Red (ii)**, `test_an_expired_key_is_gone_and_the_next_admit_counts_one`: `E   AssertionError: the key outlived its 1 s expiry by more than 3 s` / `assert not 1` at `test_score_rate_limit.py:344`.
- **Third red**, `test_the_environment_default_limits_only_its_environment`: `assert 409 == 429` at `:166`. It is the Redis-timeout fail-open (FR-452, RL-1347): `rate limit not enforced: TimeoutError` in the captured log, the first `/score` taking 3116.7 ms on a box at load 13. It is not caused by the planted edit; see the Audit section below.
- **Restore:** `git checkout` of `rate_limit.py`; `restore: backend/src diff = 0 line(s)`; the window log rows both new tests "RED on the planted no-expire (as required)".

### Green

Restored run, same window, same head: `rc=1`, `1 failed, 10 passed, 1 skipped, 1 warning in 48.07s`.

```text
FAILED backend/tests/test_score_rate_limit.py::test_the_accounts_own_rate_wins_over_the_environment_default
```

- The one failure is `assert 409 == 429` at `:198`, again with `rate limit not enforced: TimeoutError` in the captured log (the first `/score` 2255.29 ms): the same Redis-timeout fail-open as the third red, a different test of the file. Both new tests passed. See the Audit section below for the explanation of the third red and this restored red.
- Window end: `tree clean | ok`; `END 2026-10-14T16:55:25+00:00 rc=1`.

- **Observation (no finding), dated 2026-10-14**, on the maintainer's (by delegation) entry "2026-10-14 18:01:20 BST" in `to-lead.md`: /score requests of 3116 ms and 2255 ms (`red.log`, `green.log`) against RL-1347's 50 ms Redis client timeout, at load1 ≈ 13 (an external load). It becomes a finding only if a run at load1 < 4 shows the limiter path itself over the bound.

### Audit

Written 2026-10-14 17:59:52 BST by the auditor, against `origin/main...HEAD` of branch `sl-8051-fd8049-ratelimit-ttl` (head `95e97d84`, PR #1308). A proposal; the verdict is the lead's.

**Scope.** `git diff origin/main --name-only` lists exactly `backend/tests/test_score_rate_limit.py`, this ledger, `docs/roadmap.md` and `docs/INDEX.md`. `git diff origin/main --name-only -- backend/src | wc -l` prints 0. Matches the GO ("2026-10-14 17:11:47 BST": test-only, fixture TTL 3600, two expiry tests).

**Fixture.** `_app_client` takes `monkeypatch` and sets `rate_limit._KEY_TTL_SECONDS` to 3600; `client` and `second_client` pass it through. `admit` reads the module global at call time (`rate_limit.py:99`), so the patch takes effect, and the pinned window now has a TTL it cannot outrun (FD 8049 remedy).

**Tests against the 16:43:11 form.**
- (i) `test_an_admitted_request_leaves_a_key_with_a_bounded_expiry`: after one admit, `0 < PTTL <= _KEY_TTL_SECONDS * 1000`. Matches (i).
- (ii) `test_an_expired_key_is_gone_and_the_next_admit_counts_one`: TTL injected as 1, a bounded `EXISTS` poll (deadline 3.0 s, 50 ms step, no fixed sleep), then the key is gone and the next admit leaves `b"1"`. Matches (ii).

**Window runs, from `/home/puzhenhao1989/.claude/jobs/b6860f8f/tmp/sl8051-window/` (`window.log`, `red.log`, `green.log`).**
- *Run 1, 17:51:13–17:51:21 BST: VOID.* No venv: alembic rc 2, pytest rc 4 (`ModuleNotFoundError: fastapi`). Cited as the lead recorded it; its log is not in that directory and was not re-read.
- *Run 2, 17:52:04–17:55:25 BST* (`START 2026-10-14T16:52:04+00:00`, load 13.23/12.69/13.14, head `95e97d84`, tree `ddf10b4f`; `uv sync --all-packages --frozen` rc 0, `createdb gipricing_sl-8051_18ee3a35` rc 0, `alembic upgrade` rc 0). The plant removes `pipe.expire(key, _KEY_TTL_SECONDS)` (and unpacks `(count,) = await pipe.execute()`) in the working tree only.
  - Planted: `| planted run | rc=1 |`; `FAILED …::test_the_environment_default_limits_only_its_environment`, `FAILED …::test_an_admitted_request_leaves_a_key_with_a_bounded_expiry`, `FAILED …::test_an_expired_key_is_gone_and_the_next_admit_counts_one`; **`3 failed, 8 passed, 1 skipped, 1 warning in 50.89s`**. (i) fails `assert 0 < -1` (`:317`); (ii) fails "the key outlived its 1 s expiry by more than 3 s" (`:344`). Both new tests RED on the plant, as required.
  - Restore: `backend/src diff = 0 line(s)`.
  - Restored: `| restored run | rc=1 |`; `FAILED …::test_the_accounts_own_rate_wins_over_the_environment_default`; **`1 failed, 10 passed, 1 skipped, 1 warning in 48.07s`**; `| tree clean | ok |`; `END … rc=1`.

**The third failing test under the plant, named and explained.** `test_the_environment_default_limits_only_its_environment` (`test_score_rate_limit.py:153`; fails `assert 409 == 429` at `:166`, the third request under a limit of 2). **A missing expiry cannot make it fail.** Reading the test and `rate_limit.py:85-109`: every request of the test counts into one key per account (the clock is pinned; the account is created fresh in the test, so the key is new). With or without `expire` the count after requests 1, 2, 3 is 1, 2, 3; expiry only matters after the TTL elapses, and the fixture makes that 3600 s. So request 3 gets `count=3 > 2` and 429 either way. What produced the 409 is in the same failure's captured output in `red.log`: `WARNING app.platform.rate_limit … rate limit not enforced: TimeoutError`, with that `/score` request completing at `duration_ms 3116.7`, status 409. A Redis `TimeoutError` makes `admit` return `True` without a count (`rate_limit.py:101-108`, the fail-open path), so the third request was admitted and reached the handler (409). The first `F` in `..F.....FF.s` is the third test in file order, which is how that output is attributed to it. **Verdict on that red: not caused by the plant; load-induced fail-open (load 13).** It is therefore not evidence for or against the new tests; the two new reds are.

**The restored-run red is the same cause, on a different test.** `test_the_accounts_own_rate_wins_over_the_environment_default` fails `assert 409 == 429` at `:198`, and `green.log` carries `WARNING … rate limit not enforced: TimeoutError` (`rate_limit.py:103`) with `/score` at `duration_ms 2255.29`. It is the limiter failing open on a Redis timeout, not the TTL fix: the fixture change cannot admit a fourth request. A counter is not unavailable in CI (FD 8049 control: 0 such lines in runs 38587011863 and 38568100882). The window therefore has **no clean green of the whole file**; CI's full python run on the PR head is the gate (the 17:11:47 ruling (a′)).

**Findings against the slice (non-blocking, recorded for limb 2 of FD 8049).**
1. Test (i) uses the default TTL of 2 s. A stall of more than 2 s between `admit` and `pttl` returns -2 (key gone) and fails `0 < pttl`; a fail-open admit (no key written) fails it the same way. Both are the load class FD 8049 names. Preferred hardening: patch `_KEY_TTL_SECONDS` to a value the run cannot outrun (the assertion already reads the constant) and assert `metrics.rate_limit_unenforced` did not move. Test (ii) has the same exposure at `assert await redis.get(key) == b"1"`.
2. A fail-open admit is indistinguishable from a correct admit in this file (`status != 429`), so a Redis timeout surfaces as `409 == 429` and reads as a limiter bug. Remedy in FD 8049 limb 2; out of this slice.

**PROPOSED VERDICT: ACCEPT.** Scope is exactly the GO; both new tests are red on the planted no-expire and stated against the accepted form; `backend/src` is untouched; the third red under the plant is explained and unrelated to the expiry; the restored red is the fail-open of limb 2, not the fix. Condition: the PR's CI python job green at the head (it is the gate), with the merge-tree and tree checks of the lead's MERGE-ACK. If CI reds on this file, read the log for `rate limit not enforced` before classifying.

## PRs

- (none opened yet; the lead opens it.)
