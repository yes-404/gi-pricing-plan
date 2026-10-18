---
id: PL-1690
family: plan
kind: map
title: WK-674 — Slice 4 (deployment path) at GO: the FR-452 management limb as RL-1687 rules it, the worker on both queues, and the compose smoke that proves delivery — Work-plan delta
status: active                 # draft → active → superseded | retired (§1.2a)
created: 2026-10-12
owner: planner
tree: 604ea084c96efe93f521fb9ba17738e05241e61a
phase: P2
work: WK-674
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1237, PL-1537, PL-1620, PL-1666, PL-1688, RL-1687, SL-1258, SL-1259, SL-1689, FD-1661, FD-1693]
---

# PL-1690 — WK-674 Slice 4 at GO: Work-plan delta (after PL-1666)

> **For agentic workers:** this is a **Work-plan delta** under Lean P2 L5. It does not replace
> `PL-1237`, `PL-1537`, `PL-1620` or `PL-1666`. It `relates:` them and changes **Slice 4 only**.
> **Read `PL-1237` Task 4, then `PL-1537` row 1 (R4.1 to R4.3), then `PL-1620` (D0.1 to D0.3,
> D4.1 to D4.3), then `PL-1666` (D0.4, D0.5, D4.4 to D4.6), then this file.** Where they differ,
> this file is the later statement. Slice 4 stays one PR under L1 (a'). Its `LG-` quotes E4.1 to
> E4.3 beside the rows it already quotes. REQUIRED SUB-SKILL and bound skills: `PL-1666`'s list,
> unchanged.

Minted 2026-10-12 as PL-1690 from working id 9898, reserved by the lead in its from-lead entry "2026-10-12 05:48:32 BST — RULINGS: …", item (2), which also accepts the T-text timing "before or with the code, never after". Written 2026-10-12 by the planner
(planner-wk674-s4). Evidence was read at `origin/main` `604ea084` and at the authored S4 branch
`origin/sl-1258-wk674-s4` `a04ff676`.

## Authority

- **E4.1 — DP-S4-1:** RL-1687 (minted 2026-10-12 from working id 9876). **At this draft it was the
  decision-maker's draft, branch `rl-9876-fr452-mgmt-2026-10-12` @`d1ee8fbb`, not yet ACKed or
  minted; it was ACKed by the maintainer's (by delegation) entry "2026-10-12 07:44:13 BST" (final
  @`f76ecd7d`) and minted in D14.** Every line of E4.1 that rested on it is re-pointed to RL-1687. Its decision: (1a), (2a), (3a).
- **E4.2 — DP-B1:** the lead's from-lead entry "2026-10-12 05:37:23 BST — PL 9882 + SL 9883 PUSHED
  @3dc58611f25330bdd779257b5222a025cfb9dbd7 (pl-9882-wk674-beat-frontend-2026-10-12; check 31 only;
  doc-index 0; register-lint 0)": "DP-B1 = (a): … S4 MUST consume default,compute (as
  demo.py:210-224 does), with a shape test asserting both queues — an S4 GO CONDITION (FR-415 is
  S4's); not this row's."
- **E4.3 — the functional proof:** the maintainer's (by delegation) entry "2026-10-12 05:37:42
  BST — PL 9882/SL 9883 and DP-B1/B2 noted. DP-B1 is a good catch; add ONE functional proof beside
  the shape test", verbatim: "A shape test asserting `--queues default,compute` proves the
  declaration, not delivery ("declared ≠ reachable"). S4's acceptance adds one functional check in
  its compose smoke: bring up worker + beat, enqueue one outbox Job (any cheap kind), and observe
  it reach a terminal state within a bound, recorded in the LG. If compose smoke cannot run in CI,
  it runs once locally in a build window and the LG quotes the output. Without it, the queue
  defect class (no consumer on a queue) can recur unseen."
- **Beat as a fixture:** the maintainer's (by delegation) entry "2026-10-12 05:39:20 BST — SL-1543
  severity block: …", last paragraph: "S4 (your second message): beat as a one-off test fixture
  from S4's image, with SL 9883 repeating the proof against the real scheduler service. Correct
  reading."

## Goal

Make `SL-1258` GO-able with its last three conditions written into its plan: the FR-452
management limb as ruled, a worker that consumes every queue the platform routes to, and one
functional proof that a Job is delivered through the compose path, not only declared. The Work's
goal is `PL-1237`'s, unchanged.

## Tasks

| Order | Slice | Scope (what the `LG-` quotes) | Requirements, each id | Depends on | Size |
|---|---|---|---|---|---|
| 1 | `SL-1258` — Slice 4: the deployment path | `PL-1666` row 1 as it stands, plus E4.1 to E4.3 below | unchanged from `PL-1666`: `07` §3.6: FR-434, FR-435, FR-437; `07` §3.2: FR-412 (memory half), FR-415 (worker service); `07` §3.9: FR-452 (management-API limb); `07` §9: NFR-531, NFR-534; register FD-1211, FD-1650 | `SL-1257` closed (met); RL-1687 ACKed and minted (E4.1); the build window | 1 + a build window |

FR-448 is touched only by RL-1687's T2, as text. No requirement id is added or removed.

### Slice 4 (`SL-1258`) — changes since `PL-1666`

- **E4.1 — Task C, as RL-1687 rules it.** It replaces `PL-1666` D4.5's "behind DP-S4-1". What
  Task C builds is RL-1687's to state ("What it obliges"), and this delta does not restate it. The
  only additions here are RL-1687's acceptance items, its "Acceptance — the violation that must
  become detectable", items 1 to 4: four tests named `test_management_rate_limit_*`, marked
  `req("FR-452")`, each red by its cause. They are: counted and refused; separate from scoring;
  (3a); no Principal, no count. `PL-1537` Acceptance item 4's floor ("at least 2") becomes 4. The
  T-text timing is "before or with the code, never after" (the lead's from-lead entry
  "2026-10-12 05:48:32 BST", item (2)). Acceptance item 2 checks it.
- **E4.2 — the worker on both queues.** On S4's branch, the `worker` service's command becomes
  `--queues default,compute`. Today it is `--queues compute` (`deploy/docker-compose.yml:145` at
  `a04ff676`), while the outbox relay is sent to `default` (`entrypoint.py:53-58`), `default` is
  the Celery default queue (`celery_app.py:52`), and `RATING_COMPILE`, `MONITOR_RUN` and
  `DOSSIER_GENERATE` route to it (`backend/src/app/platform/jobs.py:72,83,84`).
  - The shape test goes in `backend/tests/test_deploy_stack.py`, in its breaker table. It asserts
    that the queue set equals `{default, compute}`. It is red against `a04ff676`'s compose by that
    cause ("default not consumed"), and its breaker removes `default`.
  - Marked `req("FR-415")`.
- **E4.3 — the compose smoke: delivery, not declaration.** One runtime test in S4's
  `backend/tests/test_deploy_stack_runtime.py`, behind `GIP_DEPLOY_TESTS=1`, with its
  `_compose` helper:
  - **Up:** `--profile app` with `worker`.
  - **Beat as a one-off TEST FIXTURE, not a service:**
    `docker compose … --profile app run --rm -d worker celery -A app.worker.entrypoint beat --schedule <tmp path in the container>`,
    stopped in the test's teardown. S4 adds no `scheduler` service, which stays SL-1689's
    (02:53:52 item 4).
  - **One cheap Job**, submitted through `lb` by its public route. The executor names its kind
    and queue in the `LG-` from `jobs.py:60-84`. Whatever its own queue, the relay that moves it
    rides `default`, so the proof covers both queues.
  - **Terminal within a stated bound.** The bound is stated in the test and in the `LG-`, with
    the elapsed time recorded.
  - **The red, by cause:** the same test against the worker on `--queues compute` only (the
    breaker, or `a04ff676`'s compose). The Job stays `queued` past the bound. The `LG-` quotes
    that red line, and a red that names any other cause is a test defect.
  - **Where it runs:** the gate does not set `GIP_DEPLOY_TESTS` (`PL-1666` D0.5), so it runs once
    locally in S4's build window. The `LG-` quotes the command and its output (E4.3's "if compose
    smoke cannot run in CI").
  - SL-1689's Task 3 repeats this proof against the real `scheduler` service.

## Acceptance Standard

1. **This delta passes the docs checks on its own branch** (check 31's working-id line excepted).
2. **Spec before or with the code.** `git log --format=%s origin/main..<S4 head> -- docs/specs/07-platform.md`
   shows T1 and T2 in a commit before or with Task C's code.
3. **E4.1:** `uv run pytest -q backend/tests -k management_rate_limit` exits 0, collects at least
   4 tests, and the `LG-` quotes each red line.
4. **E4.2:** `uv run pytest -q backend/tests/test_deploy_stack.py -k queue` exits 0, and the `LG-`
   quotes its red line against `a04ff676`.
5. **E4.3:** the build window's `GIP_DEPLOY_TESTS=1` run of the smoke test exits 0, and its red run
   with the worker on `compute` only is quoted.
6. `PL-1666` Acceptance items 3, 4 (as E4.1 raises it), 5, 6 and 7 hold unchanged.

## Decision points

None open. DP-S4-1 is RL-1687's (E4.1), and DP-B1 is the lead's (05:37:23).

## Activation

At this delta's mint: `PL-1666` goes `active` by its status line, citing RL-1687
(RL-1687's "What it does not change", which also says PL-1666 goes active once it is minted).
`SL-1258`'s GO conditions are then: E4.1 to E4.3; `PL-1666` D0.4 (merge main first) and D4.4
(FD-1650's test); the build window; and the lead's GO.
