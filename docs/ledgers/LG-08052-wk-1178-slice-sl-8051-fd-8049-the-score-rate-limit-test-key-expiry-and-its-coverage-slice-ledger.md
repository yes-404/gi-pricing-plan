---
id: LG-8052
family: ledger
title: WK-1178 slice SL-8051 — FD 8049, the score rate-limit test's key expiry cannot outrun the pinned clock and the limiter's key expiry is tested, slice ledger
status: active                 # active → closed (§1.2a)
created: 2026-10-14
owner: executor
tree: beee5ebedcfebc03c1658728442827960975392a
phase: P2
work: WK-1178
slice: SL-8051
plans: []
corrected_by: []
relates: [SL-8051, FD-8049, FR-452, FR-430, RL-1347]
---

# LG-8052 — WK-1178 slice SL-8051: the score rate-limit test's key expiry

Working ids 8051 (slice) and 8052 (this ledger), reserved by the lead; not yet minted.

**GO:** the maintainer's (by delegation) entry "2026-10-14 17:11:47 BST" in `to-lead.md` (the fix is test-only; scope exactly: the fixture makes the limiter's TTL 3600, plus the two expiry tests, each red first on a planted no-expire, no change to `backend/src`), with "2026-10-14 16:43:11 BST" (the accepted test form and the expiry-coverage condition) and "2026-10-14 14:30:54 BST" (the FD). The finding is FD 8049, not on `main` yet (it rides D18).
**CI is the gate:** the maintainer's (by delegation) entry "2026-10-14 17:11:47 BST", ruling (a′): *"FD 8049's fix is TEST-ONLY, so CI's full python run on its PR head IS its gate"*; no gate-1 cycle. ACK: CI python, docs and history green at the head; merge-tree rc 0.
**MERGE-ACK:** not yet given.
**Audit:** not yet.

## Tasks

Branch `sl-8051-fd8049-ratelimit-ttl`, worktree `.claude/worktrees/sl-8051`, cut from `origin/main` `beee5ebe`.

- **Fixture:** `_app_client` takes `monkeypatch` and sets `rate_limit._KEY_TTL_SECONDS` to 3600 (`admit` reads the module global at call time); the `client` and `second_client` fixtures pass it through.
- **Expiry test (i):** `test_an_admitted_request_leaves_a_key_with_a_bounded_expiry` — after one admit, `0 < PTTL <= _KEY_TTL_SECONDS * 1000`.
- **Expiry test (ii):** `test_an_expired_key_is_gone_and_the_next_admit_counts_one` — TTL injected as 1 s, a bounded `EXISTS` poll (deadline 3 s, 50 ms interval), then the key is gone and the next admit leaves the count at `b"1"`.
- **`backend/src`:** unchanged; `git diff origin/main --name-only -- backend/src` prints nothing.

### Reds, by their cause

Run by `/home/puzhenhao1989/.claude/jobs/b6860f8f/tmp/sl8051-reds.sh <worktree>` in the lead's DB-prep window: the `pipe.expire` line is removed from `backend/src/app/platform/rate_limit.py` in the working tree only, never committed.

- (output owed: the failing lines of tests (i) and (ii) on the planted no-expire.)

### Green

- (output owed: `test_score_rate_limit.py` after `git checkout` of the file; `git status --porcelain` empty; `git diff --stat backend/src` empty.)

## PRs

- (none opened yet; the lead opens it.)
