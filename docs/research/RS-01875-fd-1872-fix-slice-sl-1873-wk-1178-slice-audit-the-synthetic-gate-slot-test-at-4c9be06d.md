---
id: RS-1875
family: research
kind: audit
title: FD-1872 fix slice SL-1873 (WK-1178) slice audit, the synthetic gate slot test at 4c9be06d
status: draft
created: 2026-10-23   # drafted 2026-10-23 under working id 8202; minted 2026-10-23 as RS-1875
owner: auditor
tree: dcab76fc048045aef57ca1959f4e87b5750115d4
phase: P2
work: WK-1178
corrected_by: []
relates: [SL-1873, LG-1874, FD-1872, FD-1838]
---

# RS-1875 — FD-1872 fix slice SL-1873, slice audit

Disclosure: drafted under working id 8202; minted as RS-1875 on 2026-10-23, in the fix slice's PR (SL-1873), folded from `aud-8199-2026-10-23` @0208ad11.

*(Working id 8202, written by `aud-8199`, 2026-10-23, from the brief `brief-aud-8199-2026-10-23.md` (lead 26). Check 31/32 on this id and on FD-1872, SL-1873, LG-1874 are expected until the mint.)*

## Question

Does the slice remedy FD-1872 as the maintainer's entry "2026-10-22 23:42:23 BST" item 1 (`to-lead.md`) ruled: test only, a synthetic per-run slot at each real-slot site, red-first proof, green by import closure, a sweep for other real-slot literals?

## Method

Range `origin/main...4c9be06d` (base `1fe82ee6`; branch `fix/fd-8199-synthetic-gate-slot`). Read by `git show`, `git diff` and `git grep` only; no test, DB, redis or gate was run by this seat, and the slice branch was not edited.

## Checks

1. **Only the test file changes outside `docs/`.** `git diff --stat origin/main...4c9be06d`: `backend/tests/test_deployment_switch_slot_namespace.py`, `docs/INDEX.md`, `docs/roadmap.md`, the LG. `git diff --name-only origin/main...4c9be06d -- '*.py'` lists the one test file. No product code is touched. **Met.**
2. **Each former real-slot site is synthetic.** The three sites at `origin/main` (:40 `gate-1`, :42 `gate-1b`, :52 `gate-1`) now call `_synthetic_slot()` = `/tmp/slots/test-{uuid4().hex[:8]}`; `uuid4` was already imported. **Met.**
3. **The two-slot test compares two different slots.** `test_two_gate_slots_get_two_stacks` calls the helper twice and keeps `assert first != second`. **Met.**
4. **The `other-slot` case.** Parametrized `[False, True]`, ids `plain` and `other-slot`. For `other-slot` the foreign channel is computed under a second synthetic slot inside `monkeypatch.context()`; the env is restored on exit, so the switch under test uses the first slot. A stack that ignored the slot would put the foreign subscriber on the same channel and fail the `receivers == 1` assertion, so the case has teeth. The `plain` case is unchanged apart from the synthetic slot. **Met.**
5. **The sweep.** `git grep -n '/tmp/slots/gate-' 4c9be06d -- backend packages tests frontend scripts` returns the LG's list plus the new docstring prose at slot_namespace:37. The three classifications, each read at its file:line:
   - `backend/tests/test_run_small_script.py:134`: the script is run with a caller-set `GIP_GATE_SLOT` and must refuse (SLOT_SET); no Redis.
   - `tests/test_root_conftest.py:211,217`: `monkeypatch.setenv` with `_acquire_pytest_gate_slot` stubbed; no Redis.
   - `tests/test_root_conftest.py:312,316`: a regex over the dev-commands skill text; no env set.
   Other `GIP_GATE_SLOT` mentions (`scripts/run-small.sh`, `scripts/_docverify.py:4231`) are not test literals. **Met.**
6. **RED/GREEN/closure lines in LG-1874 equal the logs** (`scratch/fix-8199/431c430a…-*.log`, verbatim): RED `1 failed, 2 passed in 4.05s` with `SwitchIncompleteError: 1 of 2 subscribed processes acknowledged PREPARE`; GREEN with the injected subscriber `4 passed, 1 warning in 1.10s`; GREEN without `4 passed, 1 warning in 1.08s`; closure `69 passed, 3 warnings in 69.90s`. Log header times are 00:19-00:21 BST 2026-10-23. **Met.**
7. **The closure derivation reruns to the same list.** `git grep -n -E "^(from|import) .*deployment_switch|^from app.platform import .*deployment_switch" 4c9be06d -- backend/tests packages tests` lists test_deployment_switch.py:16, test_deployment_switch_http.py:32, test_deployment_switch_slot_namespace.py:20, test_score.py:47, the four files the closure run covered. **Met.**

## Notes (not blocking)

- The LG's ruff, mypy and cleanup claims (ruff rc 0, `Success: no issues found in 246 source files`, db 11 flushed, db 0 untouched) were not re-verified: that would mean running tools. They rest on the executor's record.
- LG-1874's Audit section reads "(not yet)"; it is written from this record at the mint, in the slice PR.
- LG-1874's `created: 2026-10-22` is the draft date; the gate runs are 2026-10-23 BST. Cosmetic.
- The maintainer's text names the channel `gip:switch:gate-1:dev`; the real one is `gip:switch:local:local:gate-1:dev` (`deployment_switch.py` :400-410), which the LG uses.
- audit-docs on the slice head is owed when gate slots are free.

## Verdict (PROPOSED)

**CLEAN**, no blocking items. The verdict is the lead's; the lead adopted it on 2026-10-23.
