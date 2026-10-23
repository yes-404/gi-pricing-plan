---
id: FD-8199
family: finding
title: The switch slot-namespace test names real gate slots, so a paired gate's subscriber is counted in its PREPARE quorum
status: active
created: 2026-10-23
owner: auditor
tree: 4e399fd01e8de2fe55d2f128b0e09ee2b2735c6a
corrected_by: []
relates: [WK-1178, FD-1838, SL-1551, SL-8200, LG-8201]
---

# FD-8199 — The switch slot-namespace test names real gate slots, so a paired gate's subscriber is counted in its PREPARE quorum

## Finding

**LOW-MEDIUM; owner WK-1178. A test-isolation defect; product code is unaffected.** Authority: the maintainer's entry
"2026-10-22 23:42:23 BST" item 1 (`to-lead.md`): new FD, remedy test-only, a synthetic per-run slot. Filed under working id 8199.

`backend/tests/test_deployment_switch_slot_namespace.py` sets `GIP_GATE_SLOT` to REAL gate slot names. `switch_stack`
appends the slot's basename to the channel prefix, and Redis pub/sub is server-wide whatever the db, so a paired gate that
holds `gate-1` has a subscriber on `gip:switch:local:local:gate-1:dev`. The test publishes PREPARE on that same channel and
the subscriber is counted in the quorum but never acknowledges: "1 of 2 subscribed processes acknowledged PREPARE".

## Evidence

At `origin/main` 1fe82ee6, `backend/tests/test_deployment_switch_slot_namespace.py`:

- :40 `monkeypatch.setenv("GIP_GATE_SLOT", "/tmp/slots/gate-1")` and :42 `"/tmp/slots/gate-1b"` (`test_two_gate_slots_get_two_stacks`);
  :52 `"/tmp/slots/gate-1"` (`test_a_subscriber_on_the_unsuffixed_channel_is_not_counted_in_the_quorum`).
- `backend/src/app/platform/deployment_switch.py` :400-410, `switch_stack`: `os.path.basename(slot)` appended when `GIP_GATE_SLOT` is set.

**The occurrence:** SL-1551's gate, `~/gi-pricing-plan.local/scratch/sl1551-gate/pytest.log` :10310, `FAILED
backend/tests/test_deployment_switch_slot_namespace.py::test_a_subscriber_on_the_unsuffixed_channel_is_not_counted_in_the_quorum`,
with `SwitchIncompleteError: 1 of 2 subscribed processes acknowledged PREPARE` (:167).

**Reproduced red:** LG-8201's RED run (log `431c430a…-red-old-with-injected.log`): `origin/main`'s test file with a subscriber
injected on the real `gip:switch:local:local:gate-1:dev` channel, `1 failed, 2 passed in 4.05s`, the same `SwitchIncompleteError`.

**Not measured:** that the unfixed test also disturbs the live gate it shares a channel with (it PUBLISHES a PREPARE for a
random deployment onto that gate's channel). That is read from the mechanism; no run observed a gate affected.

**Sweep:** `git grep -n '/tmp/slots/gate-' -- backend packages tests frontend scripts` at the fix head `4c9be06d` lists three other
files, all legitimate (LG-8201 Task list, re-read by the auditor): `backend/tests/test_run_small_script.py:134` (the script
refuses a caller-set slot; no Redis), `tests/test_root_conftest.py:211,217` (monkeypatched env, acquisition stubbed),
`tests/test_root_conftest.py:312,316` (a regex over the dev-commands skill text).

## Remedy

SL-8200 / LG-8201, branch `fix/fd-8199-synthetic-gate-slot`: a per-run `/tmp/slots/test-<8 hex>` at each hit; the
parametrized `other-slot` case is the permanent stand-in for a paired gate. Test only.

## Disposition

Open, owner WK-1178; **fix before close**: SL-8200 (LG-8201). Closed in place citing the PR when that slice merges.
Filed under working id 8199.
