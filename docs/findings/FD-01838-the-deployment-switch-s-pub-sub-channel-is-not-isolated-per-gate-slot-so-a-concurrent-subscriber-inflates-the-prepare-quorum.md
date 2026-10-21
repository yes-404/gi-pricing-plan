---
id: FD-1838
family: finding
title: The deployment switch's pub/sub channel is not isolated per gate slot, so a concurrent subscriber inflates the PREPARE quorum
status: active
created: 2026-10-21
owner: auditor
tree: c35113b2052877fc779eddd44229b607aef162a9
corrected_by: []
relates: [WK-1178, WK-674, SL-1711, FD-1823]
---

# FD-1838 — The deployment switch's pub/sub channel is not isolated per gate slot, so a concurrent subscriber inflates the PREPARE quorum

## Finding

**MEDIUM; owner WK-1178; Lean P2 limb (ii)** (work was blocked: SL-1711 run 2, 2026-10-21). Filed on the
maintainer's (by delegation) entry "2026-10-21 21:13:34 BST" (`to-lead.md`), option (iii)-b, on lead 25's
report "2026-10-21 21:12:58 BST" (`channel/from-lead-2026-10-09.md`). Filed under working id 8150; minted as FD-1838 on 2026-10-21.

The deployment switch's Redis channel name does not depend on the gate slot, and the PREPARE quorum is
Redis PUBLISH's receiver count, which counts subscribers server-wide. Any process on the box subscribed to
the same channel is therefore counted as a receiver that will never acknowledge, and a switch run beside it
ends `DEPLOY_SWITCH_INCOMPLETE`. A per-slot Redis db does not isolate it: pub/sub ignores the db number.

## Evidence

At `origin/main` c35113b2, `backend/src/app/platform/deployment_switch.py`:

- :346-350, `RedisSwitchTransport.__init__(self, client, namespace)`: `self.channel = f"gip:switch:{namespace}"`
  (:348); the roster and ack keys use the same namespace (:349, :353).
- :355-356, `publish` returns `int(await _awaited(self._client.publish(self.channel, ...)))`: the receiver count.
- :250-253, `receivers = await transport.publish(message)`, then `transport.acks(..., receivers, timeout)`, then
  `if len(acked) >= receivers`: the count is the quorum.
- :406-407, `RedisSwitch.for_environment` builds the namespace as `f"{self._stack}:{environment}"`; `backend/src/app/main.py:131`
  passes `f"{settings.environment.value}:{settings.tenant_id}"` as the stack, so on this box every process
  that uses the defaults shares `gip:switch:local:local:{dev,uat,prod}`.

**The occurrence:** SL-1711 run 2 (`origin/sl-1711-wk674-wf701-demo` @135c0b89, LG 8136): rc 1, 40 passed,
1 failed; A5 and A6 passed; the journey stopped at DEP with `DEPLOY_SWITCH_INCOMPLETE` 503 "1 of 2 subscribed
processes acknowledged PREPARE", while the SL-1275 gate's pytest was subscribed to the same channel. The
maintainer's (by delegation) entry "2026-10-21 21:13:34 BST" verified the three code lines above and found
lead 25's reading holds. It also corrected the maintainer's (by delegation) earlier ruling "2026-10-21
16:23:35 BST": RL-1626's small-run allowance does not cover a test that exercises the switch.

Not measured here: no test that exercises the switch was run for this record (the 21:13:34 rule). That the
two concurrent gate slots (gate-1 + gate-1b) can collide the same way is the maintainer's reading from the
code, not a reproduction.

## Interim control

The rule in force from "2026-10-21 21:13:34 BST" item (iii)-a: no test that exercises the deployment switch
(the WF-701 journey, `test_deploy_switch*`, `test_deploy_stack_runtime`, anything publishing on
`gip:switch:*`) runs beside a gate or another such test. It runs only with gate-1/1b free and
`PUBSUB NUMSUB gip:switch:local:local:{dev,uat,prod}` = 0, checked and quoted immediately before the run. Until
the fix lands, two code gates are not paired when either runs switch tests.

## Remedy (not made here)

Gate scripts and `run-small.sh` set a per-slot switch namespace derived from `GIP_GATE_SLOT`, passed through the
existing constructor parameter (the stack argument of `RedisSwitch`, or `RedisSwitchTransport`'s `namespace`),
red-first against a concurrent subscriber on the unsuffixed channel. This record chooses no further design.

## Disposition

Open, owner WK-1178. **Deferred with an owner: WK-1178**; the event that next discharges it: a merged
per-slot namespace with a red-first test against a concurrent subscriber, or a dated ruling accepting the
absence. Filed under working id 8150; minted as FD-1838 on 2026-10-21.
