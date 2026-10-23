---
id: LG-1874
family: ledger
title: WK-1178 slice SL-1873 — FD-1872, the switch slot-namespace test names a synthetic slot (slice ledger)
status: closed                 # active → closed (§1.2a)
created: 2026-10-22   # drafted 2026-10-22 under working id 8201; minted 2026-10-23 as LG-1874
owner: executor
tree: 1fe82ee673cc8aef2bd3e70b81b8304059fccbc1
phase: P2
work: WK-1178
slice: SL-1873
plans: []
corrected_by: []
relates: [SL-1873, FD-1872, FD-1838]
---

# LG-1874 — WK-1178 slice SL-1873: the switch slot-namespace test names a synthetic slot

Disclosure: drafted under working id 8201; minted as LG-1874 on 2026-10-23, in this slice's PR, with the slice SL-1873 (from 8200), the finding FD-1872 (from 8199) and the audit RS-1875 (from 8202).

**GO:** the maintainer's entry "2026-10-22 23:42:23 BST" item 1 (`to-lead.md`), via the lead's brief `brief-exec-8200-2026-10-22.md`. Test only; product code untouched.
**MERGE-ACK:** (added at merge) — pending

## Tasks

### Scope

FD-1872 (LOW-MEDIUM, owner WK-1178): `backend/tests/test_deployment_switch_slot_namespace.py` set `GIP_GATE_SLOT` to REAL slot names (`/tmp/slots/gate-1`, `/tmp/slots/gate-1b`). Redis pub/sub channels are server-wide, so a paired gate holding that slot adds a subscriber that the test counts in its PREPARE quorum: SL-1551's gate failed `test_a_subscriber_on_the_unsuffixed_channel_is_not_counted_in_the_quorum` with "1 of 2 subscribed processes acknowledged PREPARE". Product code (`switch_stack`) is unaffected. No requirement changes.

### Task list

1. Sweep (`git grep -n '/tmp/slots/gate-' -- backend packages tests frontend scripts`, tree only). In scope: `backend/tests/test_deployment_switch_slot_namespace.py:40,42,52`. Legitimate, not touched: `backend/tests/test_run_small_script.py:134` (proves run-small refusal 65; no Redis); `tests/test_root_conftest.py:211,217` (monkeypatched env, `_acquire_pytest_gate_slot` stubbed); `tests/test_root_conftest.py:312,316` (a regex over the dev-commands skill text).
2. RED: today's test with a subscriber injected on the real `gip:switch:local:local:gate-1:dev` channel, run in a no-gate gap.
3. Fix: a per-run synthetic slot `/tmp/slots/test-<8 hex>` at each hit; two different ones where the test compares two slots. The parametrized `other-slot` case is the permanent stand-in for a paired gate's subscriber, because a permanent test must not subscribe to a real gate channel.
4. GREEN by import closure (common brief item 29).
5. ruff and mypy on the changed file.

### Gate

Run on tree `fix-8199` @ `431c430a23b08e27d9dfd21c6c2072b2a99f5fd1` (tree `7bf0efb4befd96902995805107eb03f1841522ca`), in a no-gate gap opened by the lead (no gate running, all slots free), through `scripts/run-small.sh` of tools-main (read-only use). Per-worktree database `gipricing_fix-8199_a8d78b9c` made with `createdb -T` plus `alembic upgrade head` (rc 0). `GIP_REDIS_URL=redis://localhost:6379/11` (never db 0). Before: `PUBSUB CHANNELS 'gip:switch:*'` empty; `PUBSUB NUMSUB gip:switch:local:local:gate-1:dev` 0. Logs `scratch/fix-8199/431c430a23b08e27d9dfd21c6c2072b2a99f5fd1-*.log`, each named by its head. The injector (`scratch/fix-8199/inject.py`) subscribes to the REAL channel `gip:switch:local:local:gate-1:dev` for 300 s; NUMSUB showed 1 while it ran.

| Run | File | Injected subscriber | rc | Summary |
|---|---|---|---|---|
| RED (log `red-old-with-injected`) | `origin/main`'s test file, copied to an untracked `backend/tests/test_zz_red8199_old.py` and removed after | yes, on `gate-1:dev` | 1 | `1 failed, 2 passed in 4.05s`; `FAILED …::test_a_subscriber_on_the_unsuffixed_channel_is_not_counted_in_the_quorum`; `SwitchIncompleteError: 1 of 2 subscribed processes acknowledged PREPARE` |
| GREEN with (log `green-fixed-with-injected`) | `backend/tests/test_deployment_switch_slot_namespace.py` (fixed) | yes | 0 | `4 passed, 1 warning in 1.10s` |
| GREEN without (log `green-fixed-without-injected`) | same | no | 0 | `4 passed, 1 warning in 1.08s` |
| Closure (log `closure-a`) | `test_deployment_switch.py`, `test_deployment_switch_http.py`, `test_score.py` | no | 0 | `69 passed, 3 warnings in 69.90s (0:01:09)` |

**Closure derivation.** The slice changes one test file and no `src` module: `git diff --name-only origin/main...HEAD -- '*.py'` lists only `backend/tests/test_deployment_switch_slot_namespace.py`. Nothing imports a test file, so the closure is that file plus the other tests that import what it imports from `app.platform.deployment_switch`: `git grep -n -E "^(from|import) .*deployment_switch|^from app.platform import .*deployment_switch" -- backend/tests packages tests` lists `test_deployment_switch.py:16`, `test_deployment_switch_http.py:32`, `test_deployment_switch_slot_namespace.py:20` and `test_score.py:47`. The other four files that mention the name (`test_deployment_route_types.py`, `test_deployments.py`, `test_error_sinks.py`, plus three `src` modules) do not import it and do not import any changed file.

**Static checks.** `ruff check` and `ruff format --check` on the changed file: rc 0 and rc 0. `uv run mypy`: `Success: no issues found in 246 source files`.

**Cleanup.** `dropdb` rc 0; `select count(*) from pg_database where datname='gipricing_fix-8199_a8d78b9c'` 0. The runs left 18 ack keys in redis db 11 (switch acks of the `small-test` and `test-…` slots); `FLUSHDB` on db 11, then `redis-cli -n 11 dbsize` 0. `PUBSUB CHANNELS 'gip:switch:*'` empty and NUMSUB on `gate-1:dev` 0 after. Db 0 was not touched (dbsize 56 before and after the flush).

### Gate of record (full local code gate, gate-1)

Head `ca4bf5c1bab9b547afaefcde81be4765f7aca8a6` (tree `7d23aa37ee4778feffdf4aa75395413f272c9a9d`), branch `fix/fd-8199-synthetic-gate-slot`, the 4e399fd0 re-merge of `origin/main`. Seat `exec-8199g`; logs `~/gi-pricing-plan.local/scratch/fd8199-gate/` (`gate.log`, `pytest.log`, `load.log`). Read from those files at the mint, 2026-10-23.

- **START:** lead's log "GATE START ca4bf5c1bab9b547afaefcde81be4765f7aca8a6 gate-1 Fri Oct 23 10:14:17 BST 2026" (`gate.log` line 1: `START head: ca4bf5c1… tree: 7d23aa37… load(date l1 l5 l15): 2026-10-23T09:14:20+00:00 2.90 1.40 0.68`).
- **END:** `END 2026-10-23T10:33:11+00:00 3.77 3.08 3.43 (date l1 l5 l15)`. `head guard | ok`; `tree after gate: 0 changed path(s)`.
- **Python half:** ruff rc 0; mypy rc 0; import_linter rc 0; req_coverage rc 0; contracts rc 0; **audit_docs rc 1**; **pytest rc 1**. `pytest summary: 13 failed, 6738 passed, 21 skipped, 147 warnings in 3126.69s (0:52:06)`.
- **The 13 failures by file** (`pytest.log` FAILED lines): `test_audit_docs_finding_citations.py` 1, `test_audit_docs_ids.py` 2, `test_audit_docs_process_core_digest.py` 2, `test_audit_docs_w37_11_ceiling.py` 1, `test_doc_index.py` 1, `test_register_lint.py` 3, `test_register_owed.py` 1, `test_repository_invariants.py` 2. That is exactly the eight-file docs-audit set of the maintainer's standing 1(f).
- **audit-docs:** `FAILED (1): - check 31: gap in the full allocation between 1859 and 8199` (`audit_docs.log` :882-883): the slice's own working id, nothing else.
- **Frontend half:** `pnpm install --frozen-lockfile`, `generate:api`, `lint`, `type-check`, `test --maxWorkers=2`, `build` all rc 0; `Test Files  129 passed (129)`, `Tests  817 passed (817)`, `Type Errors  no errors`, `✓ built in 1.65s`.
- **Demo:** `demo.py --journey wf-699 | rc=0`; keycloak restored from tools-main, bind source `…/worktrees/tools-main/deploy/keycloak-local`.
- **Zeros:** `own-DB count=0 redis RT db 1 dbsize=0 redis RD db 3 dbsize=0`.
- **Load windows** (the maintainer's entry "2026-10-23 11:33:52 BST", `to-lead.md`): the excursion windows 10:22–10:25 and ~10:52–10:57 BST are recorded against the gate. The lead's log at 10:25:42 BST records a load1 reading of 7.48 (read by another seat before its run) overlapping the pytest stage. `load.log` holds only the phase-boundary samples (`START` 2.90, `after-python` 2.03, `after-frontend` 2.90, `END` 3.77 load1), not that reading. No timing test is among the 13 failures, so under the 23 Oct rule a clean pass stands.
- **Verdict:** the gate STANDS for the code under 1(f) (the maintainer, "2026-10-23 11:33:52 BST"). Conditions before the ACK, per the standing rule: the mint at its turn, audit-docs rc 0, the 13 re-run through run-small on the minted head, and PR CI including the python run. This ledger records the true pytest line ("13 failed"), never "0 failed" (the maintainer's record correction in the same entry).

### Audit

`RS-1875` (`aud-8199`, range `origin/main...4c9be06d`, base `1fe82ee6`): PROPOSED CLEAN, seven checks met, no blocking items. The lead's verdict, `from-lead` log "2026-10-23 00:27:17 BST Lead 26: aud-8199 PROPOSED CLEAN … VERDICT (lead): CLEAN". The audited head `4c9be06d` is the slice head before the 4e399fd0 re-merge; the re-merge brought main only (the diff vs `origin/main` stays the one test file plus docs). Not re-verified by the audit: the ruff, mypy and cleanup claims above (RS-1875 Notes).

### Build log

- 2026-10-22 — branch `fix/fd-8199-synthetic-gate-slot` from `origin/main` @ `1fe82ee6`; test edit, SL-1873 row and this ledger written; nothing run.
- 2026-10-22 — head `431c430a`: RED, GREEN and the closure set run in the lead's no-gate gap; lines in Gate above.

- 2026-10-23 — head `ca4bf5c1`: re-merge of `origin/main` 4e399fd0 (INDEX-only conflict, taken from main and regenerated); full gate-1 run above.
- 2026-10-23 — mint at its id turn: FD 8199 → FD-1872, SL 8200 → SL-1873, LG 8201 → LG-1874, RS 8202 → RS-1875 (eta.md "2026-10-23 10:43:59 BST"); FD essay, RS-1875 and the register row folded from `aud-8199-2026-10-23` @0208ad11 (item 34); SL-1873 closed with the closing acts below; every prefixed cite re-pointed.

## PRs

(opened at its id turn — after FD 8169's merge)
