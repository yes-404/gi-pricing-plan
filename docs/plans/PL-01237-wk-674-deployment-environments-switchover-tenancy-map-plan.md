---
id: PL-1237
family: plan
kind: map
title: WK-674 — Deployment, environments, atomic switchover, rollback, shadow and tenancy: map plan
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-09-29
owner: planner
tree: 9cd179cbcc2ab55c6bcf44d956c73c74a24d4144
phase: P2
work: WK-674
supersedes: []
superseded_by: ~
corrected_by: []
relates: [ADR-710, RL-876, RL-880, RL-882, RL-886, RL-888, RL-916, RL-921, RL-922, CR-927, PL-930, PL-1070, PL-1177, CR-1212, RL-1184, RL-1232, RL-1236, FD-1197, FD-1211, OQ-1233, OQ-1234, OQ-1235]
---

# WK-674 — Deployment, environments, atomic switchover, rollback, shadow and tenancy: map plan

> **For agentic workers:** this is a **map plan**. It cuts WK-674 into six slices and fixes their scope, order, dependencies and gates. It carries no code steps. Each slice gets its own leaf plan (`kind: leaf`) before it starts, and the executor works from that leaf plan. REQUIRED SUB-SKILL for each leaf plan's executor: subagent-driven-development (recommended) or executing-plans. Each executor also binds `python-test` (requirement markers, negative tests), `dev-commands` (the gate and its traps), `fastapi-service` (routes, RFC 9457 problems) and `contract-schema` (the new shapes), and reads `docs/plans/README.md`'s five unchecked conventions before its first step.

## Goal

Build the Deployment half of the rating path. An `approved` Rating Version is deployed to a
first-class Environment. Every worker switches to the new bundle atomically. The switch can
be rolled back, routed by date or shadowed. Each deployment is bound to exactly one tenant,
as ADR-710 requires. The Work is done when every id in **Scope** below has a verdict, and
when the switchover meets the F1 acceptance test on the deployment path this Work builds,
not on a loopback mirror.

**Architecture.** This is a map plan, per `docs/process/delivery-process.md` §5 step 2. The
precedent is `PL-930` (WK-672's map plan) and its leaf plan `PL-1177`. The switchover design
direction is fixed by the deputy's F1 decision (2026-09-28, by the maintainer's delegation).
It is filed whole as the Decision section of the F1 research record in PR #837 (unmerged at
this tree; salvage ref `refs/salvage/2026-09-28/spike-f1` at `73a6d3fd`). The direction is a
two-phase push over a channel:

- **PREPARE:** each worker fetches and hydrates the new bundle off the event loop, then
  acknowledges.
- **COMMIT:** each worker swaps its one `live` reference, then acknowledges.

`/score` reads `live` once at request start. Every response carries the engine-stamped
bundle hash. The decision **does not** treat NFR-494's 30 s bound or its zero-drop clause as
met; Slice 5 must show both.

**Tech Stack.** FastAPI + Pydantic v2; SQLAlchemy 2.x async + Alembic; PostgreSQL 16; Redis
(the switch channel and the per-tenant rate-limit counter); Celery (the worker service);
`model-schema` for every new shape (ADR-704); Docker Compose for the deployment path. **No
new dependency is planned.** A leaf plan that finds it needs one updates `docs/skills-map.md`
in the same PR (`CLAUDE.md` §10).

**Spec.** These are the sections the executors read with their leaf plan:

- [`../specs/03-rating-engine.md`](../specs/03-rating-engine.md): §3.10 (FR-267 to FR-272,
  each listed below), §5.1 (the three deployment routes at `03:765-767`), §9 (NFR-489,
  NFR-490, NFR-493's linearity limb, NFR-494, NFR-496's prod-sampling limb, NFR-497,
  NFR-498's deployment limb, NFR-502).
- [`../specs/07-platform.md`](../specs/07-platform.md): §3.5 (FR-428 to FR-431), §3.6
  (FR-434, FR-435, FR-436, FR-437), §3.2 (Jobs): FR-412 and FR-415 (the clauses at `07:101`
  and `07:104`), and §9 (NFR-531, NFR-534).
- [`../specs/00-overview.md`](../specs/00-overview.md): FR-18 (`00:222`), and the §2
  entities Deployment and Environment (`00:165-166`).
- [`../specs/06-governance.md`](../specs/06-governance.md): §3.3's deployment evidence row
  (`06:121`), FR-364's floor, the §4.2 `deployment` policy entry (`06:325-327`), and FR-368.

*(Amended 2026-09-29: the cites above were re-read at the tree in the front matter,
`9cd179cb`. Three moved from `ed123cb0` — `03:607-609` → `03:765-767`, `00:221` → `00:222`,
`06:290-297` → `06:325-327` — and the ids CR-1212 assigns to WK-674 were added.)*
- ADR-710 (`docs/adrs/ADR-00710-tenant-isolation-is-a-deployment-boundary.md`).

## Acceptance Standard

These conditions are for the Work as a whole. Each leaf plan states its own conditions for
its slice, and this list does not replace them. Every command runs in the executor's own
worktree (`env -C <worktree> …`), against the range `origin/main...HEAD`, never a tip SHA
alone.

1. **Every §3.10 requirement has a verdict.** Run
   `python3 scripts/scope-audit.py RATE --sections 3.10`. It must report every one of
   FR-267, FR-268, FR-269, FR-270, FR-271 and FR-272 as evidenced. Any id it lists under
   "NO EVIDENCE" must carry one of `CLAUDE.md` §13's four verdicts in WK-674's closure
   record. If DP-2 defers FR-270 or FR-271, the verdict is "deferred with an owner", naming
   that DP's resolver id. *(Amended 2026-09-29: DP-2 is resolved (a) by `RL-1232`, so both
   are built. FR-272's notification limb is not a WK-674 delivery unless `OQ-1233` names
   WK-674. Until then its verdict at the close is "deferred with an owner", the owner being
   `OQ-1233`'s answer.)*
2. **Every `07` requirement has a verdict.** Run
   `python3 scripts/scope-audit.py PLAT --sections 3.5 --extra FR-434,FR-435,FR-436,FR-437,FR-412,FR-415`
   *(FR-434 and FR-435 added 2026-09-29, `CR-1212` item 12)*.
   The same rule applies. **A pre-existing marker is not delivery.** FR-412's marker covers
   only the wall-clock half (`backend/tests/test_worker.py:288`). FR-430's marker exercises
   the refusal branch only on a hand-crafted key (register row F54). FR-437's marker covers
   only the local profile (`tests/test_repository_invariants.py:83`; *`:81` at `ed123cb0`,
   corrected 2026-09-29*). Each of these ids gets
   its verdict from the limb this Work adds, read in the test body, not from the marker
   count.
3. **FR-18 is delivered and tested.** `grep -rn 'req("FR-18")' backend/tests` prints at
   least one line. The test it marks asserts that a Job row carries the platform build it
   ran on.
4. **FR-436 is proven on broken input.** A test starts the application with a tenant
   identifier that differs from the database's marker, and asserts a startup failure whose
   message names the mismatch. The same holds for object storage and for the broker. The
   closure record cites each test by node id, and quotes the failing output from one run
   against a deliberately mismatched configuration.
5. **The F1 acceptance test passes, unchanged, on the deployment path Slice 4 builds.** A
   research record reports at least 3 runs for each n ∈ {2, 4, 8} workers, at 200 rps, and
   each run shows all of the following:
   - 0 mixed responses and 0 dropped responses, with the bundle hash asserted on every
     response;
   - a switch in 30 s or less, warm-up included;
   - load below 12 at the start of the run, recorded beside it;
   - the worker affinity and the load-balancing topology stated.

   **The 3 drops F1 saw in m-n4-r1 are carried.** The record either reproduces the m-n4
   conditions and names their cause, or shows 0 drops at N ≥ 3 at n=4 and at n=8. Until
   one of those is true, "dropped" is an open question on WK-674's row, not a pass.

   *(Amended 2026-09-29, the maintainer's answer QDP-3 of the entry `2026-09-29 14:20:41 BST ·
   maintainer (acting on the maintainer's behalf) · QDP-1/2/3 (WK-674 DP mechanisms)`.)* The
   runs that carry this item's verdict are made on a **dedicated host, a dependency owned by
   the maintainer**. No repo record names one at `9cd179cb`. A run on the shared VM may be
   filed as a diagnostic, but it **claims no verdict near a bound**: not the 30 s switch and
   not the zero-drop clause.

   *(Amended 2026-09-29, in the commit that sets this plan `active`: the maintainer's host
   fallback, entry `2026-09-29 16:08:24 BST · maintainer (acting on the maintainer's behalf) ·
   HOST FALLBACK accepted; DEPENDABOT plan approved (the maintainer)`, §1, quoted verbatim in
   item 6, applies to this item.)* If no dedicated host exists at Slice 5's close, the F1
   acceptance test's verdict is **measured, diagnostic** on the shared VM and **carried**,
   owner the maintainer, discharge event **a dedicated host available**. No near-bound pass
   or fail is claimed.
6. **NFR-489 and NFR-502 each carry a measured verdict.** Both are measured on the
   deployment path, on a dedicated host, in more than one pass (RL-921 §4: "A re-run needs a
   dedicated host, and one pass will not establish a verdict near a bound"). Each result is recorded in WK-674's closure record with the shape measured and
   the load at the start. If NFR-489 still fails, DP-3's resolution governs what the record
   says. *(Amended 2026-09-29.)* **NFR-490** (tracing adds ≤ 20 % and never changes the
   result) and **NFR-493's linearity limb** (batch throughput linear in workers) are measured
   the same way, on the same host, and recorded the same way (`CR-1212` G4 (a) and (b)). The
   host is the maintainer-owned dependency of item 5. Until it exists, DP-3 (b) reads
   "verdict recorded; the re-measurement trigger cannot validly fire without a dedicated host
   (RL-921)", and nothing claims a measured verdict near a bound from the shared VM.

   *(Added 2026-09-29, on auditor-843's LOW items.)* Two verdict forms are fixed here in
   advance, so that a red or unstable figure is recorded and never argued after it:
   - **NFR-489's without-GBM limb (register F38).** F38's record is "measured, verdict
     unstable across runs, not established": two of five runs breached 15 ms, and load
     widened the spread about fivefold. So this limb's verdict **may be recorded as
     "measured, unstable"**. That applies when repeated passes on the dedicated host both
     pass and breach the bound, and it must carry each pass's p99, stdev and the load at its
     start. "Measured, unstable" is not a pass. It feeds DP-3 as a failure would, and it is
     named here rather than left under the NFR-489 row, because F38 is a distinct register row
     (`CR-1212` L80 proposes WK-674 as its owner). The register's owner cell is the auditor's
     to move.
   - **NFR-490 measured red.** Its latency limb fails today (+497 % to +723 % across five runs,
     register F35), and its remedy, shrinking the ~1.1 MB `to_wire(passThrough: True)` payload
     in `packages/pricing-core/src/pricing_core/rating/runtime.py`, has no Work (`CR-1212` G4
     table). Slice 5 schedules the **measurement only**. If it is red, the closure record
     states the measured verdict **FAIL** with the figures. ~~It records the remedy's ownership
     as an **open scope question for the maintainer**, and WK-674 closes with NFR-490 carried
     with that question named, never on a silent pass. **Whether WK-674 builds the F35 remedy
     is not decided by this plan.** It is a scope question the lead has put to the
     maintainer. If the answer assigns it here, the planner places it in a named slice by a
     dated amendment while this plan is `draft`, or by a replan once it is `active`.~~
     *(Amended 2026-09-29: the scope question is decided in the maintainer's entry
     `2026-09-29 15:36:43 BST · maintainer (acting on the maintainer's behalf) · SCOPE:
     NFR-490 / F35 in WK-674, option (b)`.)* **Slice 5 measures NFR-490 and, if it is red,
     records it red with the figure, the tree and the log. WK-674 does not build F35's
     remedy**, because it is a scoring-path change outside WK-674's deployment scope. F35's
     remedy is **carried forward, with its owner named at plan review 16**. WK-674 closes with
     NFR-490 recorded as measured (red if red) and F35 carried under that owner event, never on
     a silent pass. Whether P2 can exit with NFR-490 red is plan review 16's to state, not this
     plan's.

   **Host fallback (amended 2026-09-29, in the commit that sets this plan `active`).** The
   maintainer's entry `2026-09-29 16:08:24 BST · maintainer (acting on the maintainer's
   behalf) · HOST FALLBACK accepted; DEPENDABOT plan approved (the maintainer)`, §1, gives
   this wording for every near-bound measured verdict that needs the host. It is quoted
   verbatim:

   > "*(Amended 2026-09-29 by the maintainer: no dedicated host is committed. These verdicts are **measured, diagnostic** on the shared VM; the verdict is **carried**, owner the maintainer, discharge event **a dedicated host available**. No near-bound pass or fail is claimed from the shared VM.)*"

   In this item it applies to **NFR-489** (both limbs, F38's included), **NFR-502**, **NFR-493's
   linearity limb** and **NFR-494**. Item 5 applies it to the F1 acceptance test. **NFR-490 is
   unaffected**: it is far from its bound, and the SCOPE entry of 15:36:43 BST stands for it.
   Where no dedicated host exists at Slice 5's close, each of those verdicts is recorded as
   "measured, diagnostic on the shared VM; the verdict is carried, owner the maintainer,
   discharge event a dedicated host available".
7. **The register rows owed to WK-674 are resolved.** `python3 scripts/register-owed.py WK-674`
   prints no row without a resolution. ~~At this tree it lists F41, F43 and F48. F54 is added
   once the register-and-records pass (auditor-b's PR) moves its owner to WK-674, and it must
   be resolved too.~~ *(Amended 2026-09-29, re-run at `63e4a7f0`, which is `9cd179cb` merged
   into this branch.)* It prints 8 owed rows. Six are WK-674's, and each is placed below: F-W9-1
   (NFR-502 and NFR-501, Slice 5), F41 (NFR-497, the close), F43 (FR-250 L1, Slice 2), F48
   (NFR-499's rate limit, Slice 3), F54 (one key per environment, Slice 3) and FD-1211 (the
   FD-1199 teardown-abort extensions in production processes, Slice 4). The other two, FD-1197
   and FD-1209, name WK-674 in their text but are **the lead's**; they are not this Work's to
   resolve.
8. **Every Decision point has its resolver before the slice it blocks starts.** Each
   blocking row in the Decision points table below has a resolver id in its `Resolved by`
   cell before that slice's leaf plan moves to `active`.
9. **The roadmap row names what the spec assigns to WK-674.** Inside the `### WK-674`
   section of `docs/roadmap.md`, `grep -n -E 'FR-437|FR-412|FR-415'` prints at least one
   line for each id. ~~The activation commit makes this true (see **Activation**).~~
   *(Amended 2026-09-29, the maintainer's answer Q843-2: "The roadmap WK-674 row edit is the
   lead's, after the map is accepted.")* The lead's edit makes this true, and it also names
   FR-434, FR-435, NFR-531, NFR-534, NFR-490, NFR-493's linearity limb and NFR-496's
   prod-sampling limb, so the same grep extended to those ids prints a line for each.
10. **Every slice closes on its own clean audit.** Each of Slices 1 to 6 has its own leaf
    plan filed under `docs/plans/`, with `work: WK-674`. Each slice closes on its own
    item 11, defined in **Tasks** below.
11. **The full gate passes, both halves, on the merged tree of the last slice.** These are
    the `CLAUDE.md` §11 commands, each exiting 0:
    - `uv run ruff check . && uv run mypy && uv run lint-imports && uv run pytest -q`
    - `python3 scripts/audit-docs.py && uv run python scripts/req-coverage.py`
    - `uv run python scripts/generate-contracts.py --check`
    - the five `pnpm --dir frontend` commands, each prefixed with `env -C <worktree>`
12. *(Added 2026-09-29, `CR-1212` item 12.)* **FR-434 with NFR-534, and FR-435 with NFR-531,
    are proven on the Slice 4 path.** A test brings up the compose `api` service with no
    `worker` service and scores through it (NFR-534, "runs and serves with the compute worker
    pool entirely absent"). A second test runs the migration as its own step, then serves the
    **previous** application version against the migrated schema, and rolls `api` replicas
    forward under load with 0 failed requests (NFR-531). A broken-input proof shows each red:
    an `api` that imports the worker stack at start, and a migration run from application
    start.

    *(Added 2026-09-29, on auditor-843's LOW item: how the "previous application version"
    exists while FR-432's image set is carried to Phase 3.)* The two versions are **two
    `api` images built locally by compose from two commits**. **N-1** is built from the
    commit before the slice's migration, and **N** from the slice head. Each is tagged by its
    commit SHA, and both SHAs are recorded in the evidence. The run:
    1. Serve N-1 against the old schema.
    2. Run N's migration as its own step.
    3. Show N-1 still serves against the migrated schema.
    4. Roll the `api` replicas from N-1 to N under the Slice 4 harness's load, counting
       failed requests.

    **The test proves nothing unless N-1 and N differ in schema.** So the migration between
    them must change a table N-1 reads. The broken-input proof is a planted migration that is
    **not** forward-compatible (e.g. it drops or renames a column N-1 selects), and it must
    turn the run red with failed requests.

    **Sufficient, and for what.** This is sufficient evidence for NFR-531 **on the compose
    deployment path WK-674 ships**: its clause is about the migration discipline and the
    rolling behaviour, and two real builds from two commits exercise both. It is **not**
    evidence for FR-432 (published, versioned images: Phase 3), and it makes no claim about a
    Kubernetes rolling update, which goes with FR-433 in Phase 3. The closure record states
    both limits beside the verdict.

## Global Constraints

- **Money** is integer minor units, or `Decimal` in the rating path, never float
  (`CLAUDE.md` §7). A deployment moves no money. The shadow-scoring record (FR-271) stores
  premiums, and holds them in the same form as `ScoringResult`.
- **`pricing-core` stays importable standalone**, with zero FastAPI, SQLAlchemy or Redis
  dependencies (`CLAUDE.md` §2; `.importlinter`).
  - The switch channel, the `live` reference and the per-tenant counter all live in
    `backend/`.
  - `load_bundle` stays pure with respect to the cache (RL-876, property 2).
  - `CompiledBundle` keeps exposing its `content_hash` (RL-876, property 1).
- **No hand-written shape that `model-schema` owns** (`CLAUDE.md` §2). `Deployment`,
  `Environment`, the routing rule and the shadow configuration are `model-schema` artifacts.
  `docs/contracts/` is regenerated, never edited by hand.
- **Spec first** (`CLAUDE.md` §0). 03 §4 declares no `Deployment` or `Environment` contract,
  and `docs/contracts/schemas/` holds no such file (sweep at this tree). The slice that
  builds a shape amends the spec in the same PR, before the code.
- **Push before poll.** WK-674 starts from a deploy-time push and argues its way to poll,
  never the reverse (RL-876; RL-882 clause 4; `07` FR-413's rule against sensors). The F1
  decision's PREPARE/COMMIT is that push.
- **Validate inbound, never outbound** on `/score` (NFR-502 as amended 2026-08-29, RL-883).
  The bundle hash stamped on each response is written by the engine, not re-validated.
- **Ids are listed individually.** Every plan cites FR- and NFR- ids one by one, never as a
  bare numeric range (`.claude/roles/planner.md`). This plan does so. Where it writes "FR-267
  to FR-272" in prose, the six ids are listed individually beside it.
- **Measurement discipline** (`delivery-process.md` §8):
  - No NFR measurement runs while another slice's suite or load test runs.
  - Every expensive verification is announced to the team before it starts.
  - Every process runs with its cwd set to the executor's own worktree (the team's
    process-cwd rule).

---

## Scope

### Requirement coverage, by spec section, each id individually

| Section | Id | What it demands (short) | Slice |
|---|---|---|---|
| `03` §3.10 | FR-267 | Deployment binds an `approved` RV to an Environment; who, when, why, bundle hash; Deployer only; `prod` needs the complete approval record | 2 |
| `03` §3.10 | FR-268 | Atomic per environment, never a mix; bundles pre-warmed before the switch | 5 |
| `03` §3.10 | FR-269 | Rollback to any previously deployed RV is one audited operation with the same guarantees, and needs no re-approval | 5 |
| `03` §3.10 | FR-270 | Optional date-based routing by the quote's effective date; overlapping ranges are refused (`DEPLOY_DATE_RANGE_OVERLAP`) | 6 (DP-2 (a), `RL-1232`) |
| `03` §3.10 | FR-271 | Optional shadow scoring: a proportion of live traffic is also scored against a candidate; the results are recorded and never returned | 6 (DP-2 (a), `RL-1232`) |
| `03` §3.10 | FR-272 | Every deployment, rollback and routing change emits an Audit Event and a notification | ~~2 (audit, with NFR-498), DP-4 (notification)~~ *(amended 2026-09-29)* **Audit limb, with NFR-498: 2 (deploy), 5 (rollback), 6 (routing and shadow configuration).** Notification limb: the channel is `07` FR-453 (`RL-1232` DP-4 as amended), and which Work delivers it is `OQ-1233`'s (open) |
| `03` §9 | NFR-494 | Atomic switchover, no dropped or mixed requests, 30 s or less including warm-up | 5 (the F1 test) |
| `03` §9 | NFR-489 | Scoring p99 < 50 ms at 200 rps per replica (< 15 ms without GBM). A **failing measurement** carried to WK-674, not a ruling (premise l); re-measured on a dedicated host, more than one pass (RL-921 §4) | 5 (DP-3) |
| `03` §9 | NFR-502 | No outbound validation on `/score`; owed a measurement since `CR-927:172` | 5 |
| `03` §9 | NFR-497 | 99.95 % monthly availability; the degraded read is delivered (register F41). Slice 5 keeps it reachable against the `live` reference; the availability verdict is the lead's at the close (see **Verdicts the plan does not give**) | 5 (mechanism) |
| `03` §9 | NFR-498 | Audit with before/after state — **this Work's limb only:** deployments, rollbacks and routing changes (the other limbs are other Works'). It rides with FR-272's audit limb | ~~2 (deploy, rollback), 6 (routing, shadow config)~~ *(amended 2026-09-29)* 2 (deploy), 5 (rollback: Slice 5 builds it), 6 (routing, shadow configuration) |
| `07` §3.5 | FR-428 | Environment is a first-class object: name, description, promotion order, its own live deployments; `dev → uat → prod` shipped, more configurable | 2 |
| `07` §3.5 | FR-429 | Promotion order enforced: no `prod` without a prior successful `uat`, unless policy permits a recorded skip | 2 (DP-7 (a), `RL-1232`; the skip's home is `OQ-1234`, owner WK-674, placed in Slice 2 — *added 2026-09-29*) |
| `07` §3.5 | FR-430 | Independent SA scopes, rate limits and monitoring configuration per environment; a `uat` key never scores `prod`; one key per granted environment (amended by ~~#830, item E7~~ `RL-1184`, E7). `07` §4.3's contract still shows one `key` per account, so Slice 3 opens with its own spec change (premise m) | 3 — all three limbs: keys, rate limits and **monitoring configuration** *(the last named 2026-09-29; see Task 3)* |
| `07` §3.5 | FR-431 | Environment configuration is a Setting, resolved by the §3.8 precedence and audited on change | 3 (gated by `OQ-1235`: roadmap gate "Before WK-674 Slice 3" — *added 2026-09-29*) |
| `07` §3.6 | FR-436 | One tenant per deployment; tenant marker in the database; refuse to start on a mismatch; the same for object storage and the broker | 1 |
| `07` §3.6 | FR-437 | No IdP in the production stack; `deploy/` carries a **reference** Keycloak deployment (the local half is already evidenced) | 4 (the reference deployment). Its dated amendment moving FR-433 to Phase 3 is **done by `RL-1232`** (DP-1 (b), QDP-1) — *2026-09-29* |
| `07` §3.2 | FR-412 | Resource budget: the **memory** half is armed against a worker the deployed stack runs (FR-415's WK-674 clause) | 4 |
| `07` §3.2 | FR-415 | The Job and the queue are the resource boundary; "arming the memory half and shipping that worker service is WK-674's" | 4 |
| `00` §3 | FR-18 | Every Job records the platform build it ran on; the dossier states it | 1 |
| `07` §3.6 | FR-434 | The scoring API is independently deployable and horizontally scalable, and runs without the compute workers present | 4 — *added 2026-09-29, `CR-1212` item 12* |
| `07` §3.6 | FR-435 | Migrations run as an explicit pre-deploy step, never on application start, and are forward-compatible with the previous application version | 4 — *added 2026-09-29, `CR-1212` item 12* |
| `07` §9 | NFR-534 | The scoring service runs and serves with the compute worker pool entirely absent (FR-434) | 4 — *added 2026-09-29, `CR-1212` item 12* |
| `07` §9 | NFR-531 | Rolling deploys cause no failed requests; the previous application version runs against the migrated schema (FR-435) | 4 — *added 2026-09-29, `CR-1212` item 12* |
| `03` §9 | NFR-490 | Tracing adds ≤ 20 % to scoring latency and never changes the result. Latency limb **failing** (+723 %, `CR-1212` G4 table) | 5 — *added 2026-09-29, `CR-1212` G4 (b)* |
| `03` §9 | NFR-493 | Batch scoring ≥ 1 M risks/hour per worker, **linear in workers** — the linearity limb only; throughput passes (`CR-1212` G4 table, F52) | 5 — *added 2026-09-29, `CR-1212` G4 (a)* |
| `03` §9 | NFR-496 | Ladder reconciles to the penny, asserted continuously in non-prod and **sampled in prod** — the prod-sampling limb only | 3 (gated by `OQ-1235`) — *added 2026-09-29, `CR-1212` G4 (a)* |

### Placement of `CR-1212`'s WK-674 assignments (added 2026-09-29)

The maintainer's answer Q843-2, in the entry headed verbatim (fenced, because the heading
carries a padded id):

```text
## 2026-09-29 14:17:56 BST · maintainer (acting on the maintainer's behalf) · Q843-1/2/3: CR-01212 item 4 stands; DP-6 amended
```

says the default is to **fold** each into the slice whose subject it matches, with a seventh
slice only for a group that matches none. **Every one folds, so there is no seventh slice.** One line each:

*(Noted 2026-09-29, on the maintainer's entry `2026-09-29 15:26:00 BST · maintainer (acting on
the maintainer's behalf) · STRUCTURE: routing per document-ids §1.6 and the charters; today's
technical answers re-homed`.)* Under `document-ids.md` §1.6, placing requirements into slices is
**the planner's decision**, and Q843-2 is re-homed as a **recommendation**. **The placements
below, and the other placements this amendment makes, are the planner's decisions, each with
its reason.** They agree with the recommendation at every point, so there is no departure to
report:
- fold every assignment, with no seventh slice;
- `CR-1212` item 4's environment-scoping spec change and `OQ-1234` go in Slice 2, which
  creates Environment and Deployment (the spec change lands "with its environment record",
  and DP-7's predicate reads the skip);
- `OQ-1235` gates Slice 3, matching its roadmap gate, because Slice 3 is the first slice that
  resolves per-environment configuration;
- the dedicated host is a dependency of Slice 5 and of the F1 test. It is owned by the
  maintainer, because the STRUCTURE entry keeps the host question with the maintainer.

- **FR-434 → Slice 4.** Slice 4 builds the compose `api` service, and "runs without the
  compute workers" is a property of how that service is packaged and started.
- **NFR-534 → Slice 4.** It is FR-434's measurement, taken on the same stack: `api` up, no
  `worker` service.
- **FR-435 → Slice 4.** The explicit migration step is part of the deployment path Slice 4
  builds. Slice 1's tenant-marker migration already runs as a migration, never at start.
- **NFR-531 → Slice 4.** Rolling `api` replicas needs the n-replica path and the load
  harness Slice 4 builds. It is an **application-version** roll, distinct from Slice 5's
  **Rating-Version** switch.
- **NFR-490 → Slice 5.** It is a scoring-latency measurement on the deployment path,
  taken with NFR-489 and NFR-502 on the dedicated host. Its failing latency limb is F35's.
- **NFR-493's linearity limb → Slice 5.** Linearity needs n workers on the deployed stack
  and a quiet host. It is measured with Slice 5's other measurements, on the dedicated host.
- **NFR-496's prod-sampling limb → Slice 3.** "Continuously in non-prod, sampled in prod" is
  per-environment behaviour driven by per-environment configuration, which is Slice 3's
  subject. It shares Slice 3's `OQ-1235` gate.
- **NFR-489 and NFR-502** were already Slice 5's (`CR-1212` G4 (b) confirms WK-674).

### Carried obligations — rulings and register rows that name WK-674

- **RL-880, and register F43 limb L1.** FR-250's default path resolves the Rating Version
  that is `live` in the target environment. At this tree, `POST /api/v1/score` without a
  `rating_version_ref` returns 409 `NO_LIVE_RATING_VERSION`. That branch is permanent:
  WK-674 narrows its trigger to "no Deployment in this environment" and does not delete it.
  RL-880 also says `prod` restrictions arrive with `prod`. → Slice 2.
- **RL-876 and RL-882 clause 4.** The refresh trigger, the switch channel and the
  environment pointer are WK-674's. So are `bundle_slot_capacity` and any TTL, and any
  capacity above 1 must cite a measurement (RL-882). → Slice 5.
- **RL-886.** `06` §4.2 is right, and the code is short one `deployment` policy entry.
  Without it, `approvals.submit` refuses with a 422 whose title is "No approval policy for
  this artifact type". That refusal fires **before** any evidence is read, so the plan
  predicts the failure by its cause. The dated §4.2 note goes in with the entry. The code
  moved after RL-886 cited `backend/…/approvals.py:107`. At this tree the floor is
  `packages/model-schema/src/model_schema/approvals.py:107`
  (`"deployment": ("rating_version_approval", "uat_deployment")`), and `DEFAULT_POLICY` at
  `:202` of the same file holds entries for `validation_rule`, `custom_objective`,
  `custom_metric`, `model`, `peril_structure` and `rating_version`, and **none for
  `deployment`** (premise p). → Slice 2.
- **RL-888 and RL-916.** A sampled trace carries the environment string as a stand-in for
  its Deployment parent. WK-674's migration reconciles that string to the Deployment that
  actually served the quote. → Slice 2.
- **RL-921 and RL-922: NFR-489 is a failing measurement, not a ruling.** `CR-927:171`
  carried NFR-489 to "an architectural ruling before WK-674 deployment". That ruling exists:
  RL-921 §5 discharges the carry row. `CR-926:249` and the WK-671 roadmap row
  (`docs/roadmap.md:620`, "NFR-489's verdict is unchanged — still measured and FAILING;
  RL-921 discharged the architectural question, not the requirement") carry the **failing
  measurement** to WK-674. So WK-674 owes a re-measurement, not a ruling. RL-921 §4 names
  the trigger that DP-3 depends on: "If a re-measurement with the blob read removed still
  fails the 15 ms limb, that is the trigger that puts NFR-489 itself in question". It also
  names the conditions: a dedicated host, and more than one pass near a bound. → Slice 5,
  and DP-3.
- **`CR-927:172`.** "NFR-502 owed, not delivered | carry forward with the same owner —
  isolating it needs the same instrumentation an NFR-489 remedy would add". The locator
  reproduces at this tree. → Slice 5.
- **Register F48 (NFR-499 per-client rate limits).** The decision is the deputy's E6
  (to-lead channel, 2026-09-28, the OQ-stream entry): "a shared Redis counter, per tenant".
  It is **not** a spec change in #830: #830's diff touches `07` only at FR-430 (E7). #830's
  RL record routes E6 to the register pass, as the F48 row's decision (premise o). So the
  leaf plan cites the F48 row as that pass leaves it, and re-reads it at its own tree.
  `rate_limit_rps` is persisted today and read by nothing, and `RATE_LIMITED` is raised
  nowhere. → Slice 3.
- **Register F54.** Key issuance mints a key only for `environments[0]`
  (`backend/src/app/api/service_accounts.py:180` and `:246`). The shape of the fix is `07`
  FR-430's 2026-09-28 amendment (#830 item E7). → Slice 3.
- **Register F41 (NFR-497).** The availability target is carried. Its verdict is the lead's
  at the close. → **Verdicts the plan does not give**.

*Added 2026-09-29, at `9cd179cb`.* **#830 has merged as `RL-1184`**, so "#830 item E6" and
"#830 item E7" above are `RL-1184`'s E6 and E7, and the F48 and F54 rows read as that record
and the register leave them. Six more obligations now name WK-674:

- **`CR-1212` item 4: the environment-scoping spec change.** *"A `06`/`07` spec change that
  scopes `deployment:promote` to named environments, owned by WK-674 and landed with its
  environment record."* `RL-1232` DP-6 is amended to match: "no environment-scoped grant" is
  the Phase 2 state only, until that slice lands. → **Slice 2**, which creates Environment.
- **`OQ-1234`: the home of FR-429's skip permission** (owner WK-674; `RL-1232` DP-7's premise
  note: no schema holds it). → **Slice 2**, which creates Deployment and Environment. Its
  leaf plan does not go `active` until `OQ-1234` is decided, because DP-7's one predicate
  reads the skip.
- **`OQ-1235`: how per-environment configuration resolves** when `07` FR-446's precedence has
  no Environment level. Its roadmap gate is "Before WK-674 Slice 3". → **gates Slice 3**,
  and with it FR-431, FR-430's monitoring-configuration limb, NFR-496's prod-sampling limb,
  and Slice 6's per-environment default-off switches (DP-2).
- **`OQ-1233`: which Work delivers FR-453's deployment-notification limb.** It is FR-272's
  notification channel (`RL-1232` DP-4 as amended). → No slice until it is decided. If it names
  WK-674, the planner places delivery in a named slice: by a dated amendment here while this
  plan is `draft`, or by a replan once it is `active`.
- **FD-1211: the FD-1199 teardown-abort extensions are reachable in production processes.**
  Its event is "WK-674's shutdown and recycling design, with a test of a process that loads
  the extensions and exits". → **Slice 4**, which builds the worker service and its process
  lifecycle.
- **F-W9-1 (NFR-502 and NFR-501).** `CR-1212` G4 (b) moves the owner from "a ruling before
  WK-674" to WK-674. → **Slice 5**, with NFR-489.
- *Added 2026-09-29 (auditor-843's LOW items).* **Register F38 (NFR-489's without-GBM limb,
  "verdict unstable across runs").** `CR-1212` L80 proposes WK-674. → **Slice 5**, under the
  verdict form fixed in Acceptance item 6.
- *Added 2026-09-29.* **Register F35 (NFR-490's latency limb failing; the remedy has no
  Work).** → **Slice 5 measures it**, under Acceptance item 6's red-verdict form. ~~Building the
  remedy is a scope question with the maintainer, and it is not placed.~~ *(Amended
  2026-09-29, the maintainer's SCOPE entry of 15:36:43 BST, option (b).)* WK-674 does not build
  the remedy. It is carried forward, with its owner named at plan review 16.

### Permission names — each name with its `RL-1236` verdict

**Status, amended 2026-09-29 at `9cd179cb`.** The catalogue ruling has merged as **`RL-1236`**
(#856), and #855's permission-catalogue finding is **FD-1197**. The rule (b) below is
therefore discharged: every row now states `RL-1236`'s verdict, and Slice 2's leaf plan is no
longer waiting on it. The text of rule (b) is kept as the record of what bound this plan
before the ruling merged. ~~**Status at this commit.** #856's DP-B and DP-D are decided (the
deputy's 15:01:11 and 15:03:38 BST entries), and the rows they govern say so; #856 has not
minted, so it is cited by PR number. The rows marked "pending" still wait for the rest of the
catalogue ruling.~~

**Why this section exists.** The permission-catalogue finding filed in #855 (unmerged at
this tree, so it is cited here by PR number, as #830 and #837 are) finds that `06`
names 24 permissions and the code names 24, and **only 7 names are shared**. This is a
`CLAUDE.md` §0 disagreement at scale. The deputy's resolution (to-lead channel,
2026-09-28 14:52:49 BST, item 4) is binding on this plan in two ways:

1. **Slice 2's leaf plan is not written until the decision-maker's permission-catalogue ruling (pending) merges.** That
   RL has no minted id at this tree. It is named here as "the decision-maker's
   permission-catalogue ruling (pending)", shortened below to "the catalogue ruling". It gives each of the 34
   unshared names a verdict: *map*, *spec-only* or *code-only*.
2. **Until then, every slice that adds or checks a permission states which name it uses
   and why, and cites #855's finding.** It never silently picks the `06` name or the code name.

The table below is that statement for every slice. The code names are read from
`packages/model-schema/src/model_schema/permissions.py` at this tree. The `06` column
counts hits of the literal name in `docs/specs/06-governance.md`. **Slices 1 and 4 add and
check no permission.**

*The `In 06?` column is as read at `ed123cb0`. At `9cd179cb`, `RL-1232` and `RL-1236` have
amended `06` (e.g. `06:220` now names `deployment:promote`); each leaf plan re-reads it. The
reason cells were brought up to the merged rulings on 2026-09-29.*

| Slice | Act | Name the slice uses | In `06`? | Why this name (`RL-1236` verdict; amended 2026-09-29) |
|---|---|---|---|---|
| 2 | Deploy (`POST /api/v1/environments/{env}/deployments`) | `deployment:promote` (`permissions.py:54`) | No; `06:62` and `06:219` say `rating_version:deploy_prod` and `rating_version:deploy_*` | **Ruled, not picked.** `RL-1232` DP-6 (b): the code's name is right and `06` is amended to it. `RL-1236` rows 3, 4 and 24 map both `06` names to it and cite `RL-1232`, not re-ruling it. ~~and there is no environment-scoped grant~~ *(2026-09-29: that is the Phase 2 state only. Slice 2 lands `CR-1212` item 4's spec change scoping this permission to named environments, per `RL-1232` DP-6 as amended.)* |
| 2 | Decide the `deployment` approval request | `approval:decide` (`permissions.py:53`) | Yes (2 hits) | One of the 7 shared names, so there is no disagreement to resolve |
| 2 | The Environment record's lifecycle: create, rename, retire (`07`'s `/api/v1/environments`) | `admin:manage_environments` (`permissions.py:69`) | No (0 hits); `06` names no permission for this act | **`RL-1236` DP-B (a), row 34: add to `06`, owned by WK-674 Slice 2.** Slice 2 adds its first route check, with a negative test that a non-Admin is refused. Its scope is the record's lifecycle only; it guards **no** setting value (`RL-1236` DP-D) |
| 2 | A Service Account never holds a deploy permission (FR-347, negative test) | `deployment:promote` | As in the first row | The negative test checks the permission `RL-1232` rules; it follows that ruling |
| 3 | Mint, rotate and revoke per-environment keys (FR-430, register F54) | `admin:manage_service_accounts` (`permissions.py:70`) | No (0 hits) | **`RL-1236` row 32: add to `06`.** It is already checked (`backend/src/app/api/service_accounts.py:40`), and Slice 3's per-environment key routes extend that router under the same name |
| 3 | A Service Account scores (the scope a key carries) | `score:execute` (`permissions.py:58`) | No (0 hits); `07` §4.3's example names `score:execute` | **`RL-1236` row 26: add to `06`.** `07` §4.3 already names it |
| 3 | Update environment configuration (FR-431, `PUT /api/v1/environments/{name}/settings`) | `admin:manage_settings` (`permissions.py:68`) | No (0 hits) | **`RL-1236` DP-D (b), row 31 (add to `06`).** Every per-environment setting value is guarded by `admin:manage_settings`, which already guards the settings route. Every settings change writes an Audit Event naming the environment, the key, the old value and the new value |
| 5 | Roll back (FR-269, `…/deployments/rollback`) | `deployment:promote` | As in Slice 2's first row | Rollback is the same operation aimed at an earlier version (Task 5), so it checks the same permission |
| 6 | Deploy a version carrying a date range (FR-270) | `deployment:promote` | As in Slice 2's first row | **Confirmed by the deputy (15:05:53 BST): a deploy act.** A date range belongs to a deployment, and overlaps are "rejected at deployment time" (FR-270). It carries DP-7's approval floor for `prod`. **Turning date routing on or off for an environment is a setting**, in the next row |
| 6 | Turn date routing or shadow scoring on or off, and configure shadow (FR-270, FR-271, `PUT /api/v1/environments/{env}/shadow`) | `admin:manage_settings` | No (0 hits) | **`RL-1236` DP-D (b)**, scoped by the deputy at 15:05:53 BST (quoted in `RL-1236`) to the switches and the shadow configuration only. It writes the same Audit Event as Slice 3's settings row. **The rule: nothing guarded by `admin:manage_settings` may change which Rating Version prices a live quote.** So routing on selects only among versions deployed into that environment through `deployment:promote`. The shadow switch needs only the audit, because shadow results are recorded and never served |

**What each leaf plan does with this table.** ~~It re-reads the catalogue ruling (if merged) and #855's finding at
its own tree, then quotes the row it relies on. If the catalogue ruling has merged, it states the ruling's
verdict for each name instead of the "pending" reason above. If the catalogue ruling has not merged, it
cites #855's finding (by its minted id, once merged) beside every permission it adds or checks. Slice 2's leaf plan cannot take the
second path: it waits for the catalogue ruling.~~ *(Amended 2026-09-29: `RL-1236` has
merged.)* It re-reads `RL-1236` and FD-1197 at its own tree, quotes the row it relies on, and
states that row's verdict beside every permission it adds or checks.

### Cross-module dependencies — `06`, `05`, `00` (swept at this tree)

**`06` — governance.** Two kinds of obligation, kept apart because only the first is
WK-674's scope.

*What WK-674 builds, in Slice 2:*

- the §3.3 evidence row "Deployment to `prod`" (`06:121`);
- FR-364's floor: `deployment` requires `rating_version_approval` and `uat_deployment`
  (`06:325-327` at `9cd179cb`; `06:290-297` at `ed123cb0`);
- the §4.2 default `deployment` entry: `prod`, 1 approver, role `deployer`. It is missing
  from the code (RL-886; premise p).

*Other Works' requirements that read what WK-674 writes.* WK-674 builds none of these. Its
Deployment record must not make any of them harder:

- FR-368 (WK-679, Phase 3): the Audit Event is written in the same transaction. WK-674
  emits its own events that way (FR-272, NFR-498);
- FR-357 (WK-677, Phase 3): withdrawal is refused after the artifact is live. The refusal
  already exists at `backend/src/app/platform/approvals.py:435-460` (`withdraw`, raising
  `WITHDRAW_AFTER_DEPLOY_FORBIDDEN` at `:454`; it was `:337-348` at `ed123cb0`). It needs the
  deployment state to be queryable, which Slice 2 provides;
- FR-382 (WK-681, Phase 3): what was live in each environment over a date range. This
  constrains the Deployment table's shape: it keeps history rows and is never updated in
  place;
- FR-384 (held by no roadmap row at this tree): blast radius, where the `deployments` field is empty today;
- FR-347 (WK-676, Phase 3): a Service Account never holds a deploy permission. Slice 2
  adds a negative test, because WK-674 is the first Work with a deploy permission to
  withhold.

**`05` — monitoring (WK-687, Phase 4).** WK-674 **feeds** these and builds none of them:

- FR-310: the first `prod` deployment creates template Monitors;
- FR-331: a deployment timeline;
- FR-333: which bundle hash is serving, per environment and per replica;
- FR-330 and the FR-307 `shadow` family: shadow results.

What WK-674 owes 05 is durable, queryable records: Deployment rows, Audit Events, the
per-response bundle hash, and persisted shadow results. It does not build the monitors
themselves. Building ahead of the phase is forbidden (`CLAUDE.md` §9). Following FR-413's
outbox rule, the deploy transaction is where a later Monitor-creating Job gets submitted.
WK-687 adds that submission, and Slice 2 leaves the transaction boundary where the Job can
be added.

**`00` — overview.**

- §2 defines Deployment ("recorded, reversible, audited") and Environment.
- §4's ER model has `Deployment ──▸ Environment` and `Deployment ──< ScoringTrace`. The
  trace foreign key is Slice 2's (RL-916).
- §1.4 makes Deployer its own permission.

### Premises re-derived at this tree

| # | Premise | At `ed123cb0` | Status |
|---|---|---|---|
| a | The WK-674 roadmap row lists the whole scope | The `From "Workstreams"` line under `### WK-674` (`docs/roadmap.md:665`) lists FR-267, FR-268, FR-269, FR-270, FR-271, FR-272, FR-428, FR-429, FR-430, FR-431, FR-436, FR-18. It omits FR-437 (`07:153`, "Owned by WK-674"), and FR-412 and FR-415 (`07:104`, "Arming the memory half and shipping that worker service is WK-674's"; again at `07:491`) | **does not reproduce.** Scope follows the spec; the row is corrected at activation |
| b | Deployment and Environment exist in some form | `grep -rlE 'class Deployment' backend/src packages` prints nothing. `class Environment` exists only as the settings enum `backend/src/app/config.py:31` (`local`, `dev`, `uat`, `prod`), not as the FR-428 entity | greenfield |
| c | A tenant marker and a build column exist | `grep -rlE 'tenant_id\|TENANT_ID\|tenant_marker\|platform_version\|build_version' backend/src packages` prints nothing | greenfield |
| d | A deployment path exists for the F1 test | `deploy/docker-compose.yml` runs `postgres`, `redis`, `minio` and `keycloak` (profile-gated) — no `api`, `worker` or `scheduler` service | **does not reproduce**, which is why Slice 4 precedes Slice 5 |
| e | FR-272's "configured channel" is specified somewhere | `05:380` and `06:568` both list notification channels as provided by `07`. No `07` requirement defines one (a grep of `07` for notification, channel and webhook finds only the dependency row `07:433`), and no code sends one (`grep -rliE 'notification\|webhook' backend/src` prints nothing) | **does not reproduce** → DP-4 |
| f | The deploy permission has one name | `06:62` and `06:219` say `rating_version:deploy_prod` and `rating_version:deploy_*`. The code has `deployment:promote` (`packages/model-schema/src/model_schema/permissions.py:54`) | **conflict** → DP-6 |
| g | Promotion order has one home | `07` FR-429 and the OpenAPI stub (`docs/contracts/openapi/gi-pricing.yaml:284-293`, 409 `DEPLOY_REQUIRES_APPROVAL \| PROMOTION_ORDER_VIOLATION`) put it at the deploy route. `06` FR-364's floor puts `uat_deployment` in the evidence check (`EVIDENCE_INCOMPLETE`) | **conflict** → DP-7 |
| h | `03` FR-241's date-routing cross-reference | `03:137` says "unless the deployment explicitly uses date-based routing (FR-247)". FR-247 (`03:153`) is the Premium Ladder, and date routing is FR-270 | stale reference; Slice 6's spec task corrects it, and the Slice 6 leaf plan re-verifies it first |
| i | The F1 RS record and #830's E6/E7 are on main | PR #837 and PR #830 are open drafts (#830 head `3319b34f`) | cited by PR number and item, not by record id; a leaf plan re-reads them at its own tree (`docs/plans/README.md` rule 4) |
| j | A sweep claim that `00` makes the environment set "exactly" `dev`, `uat`, `prod` | `00:166` lists the three and says nothing about exclusivity, so it does not conflict with FR-428's "additional environments are configurable" | not reproduced; no conflict |
| k | Owed register rows | `python3 scripts/register-owed.py WK-674` lists 3: F41, F43, F48. F54's owner moves to WK-674 in the register-and-records pass (auditor-b's PR, not #830). F54's row reads "not started … unowned" at this tree (`docs/findings/register.md:95`) | reproduces (3), F54 pending |
| l | NFR-489 comes to WK-674 as "the architectural ruling before WK-674 deployment" (the brief's input) | `CR-927:171` says so. But RL-921 §5 discharges that carry row, and `CR-926:249` and `docs/roadmap.md:620` both record NFR-489 as still **measured and FAILING**, carried to WK-674 | **does not reproduce as stated.** WK-674 carries a failing measurement, not a ruling. RL-921 §4's 15 ms-limb trigger feeds DP-3 |
| m | FR-430's amendment (#830 item E7) is the whole spec change for one key per environment | #830's diff changes `07` at FR-430 only. `07` §4.3 (`07:255-268`) still shows one `key` object per ServiceAccount | **does not reproduce.** Slice 3 opens with a `07` §4.3 spec change (the key set, per environment) |
| n | `03` declares a `Deployment` contract | `03` §4 runs from §4.1 to §4.8 (`RatingAlgorithm` … `score_batch`'s frame contract), with no `Deployment`. The only deployment shape in the suite is `live_deployments` inside `07` §4.2's `Environment` (`07:239-253`) | **does not reproduce.** Slice 2 opens with a spec change that declares it |
| o | #830 carries the F48 decision (E6) as a spec change | `07`'s only change in #830 is FR-430. The RL record in #830 routes E6 to the register pass, as the F48 row's decision | **does not reproduce.** The F48 row, as that pass leaves it, is the citation |
| p | The approval policy for `deployment` exists | `EVIDENCE_FLOOR` has `deployment` (`packages/model-schema/src/model_schema/approvals.py:107`). `DEFAULT_POLICY` (`:202`) has six entries and no `deployment` entry | reproduces RL-886's finding, with the code moved from `backend/` to `model-schema` |
| q | `CR-927:172` names NFR-502 as owed | The line reads "NFR-502 owed, not delivered · carry forward with the same owner" | reproduces |

**Re-read 2026-09-29 at `9cd179cb`.** The table above stays as derived at `ed123cb0`. What
has changed since:
- **a:** the roadmap line is now `docs/roadmap.md:676` (was `:665`), and still omits FR-437,
  FR-412 and FR-415. It now also omits `CR-1212`'s assignments. The edit is the lead's, after
  acceptance (Acceptance item 9).
- **b, c, d:** reproduce. There is still no `class Deployment`, no tenant marker or build
  column, and no `api`, `worker` or `scheduler` service in compose. The maintainer confirmed
  the last at `c9f50232` (QDP entry).
- **e:** superseded. `07` FR-453 (`07-platform.md:184`) is the channel (`RL-1232` DP-4 as
  amended, on Q848-1), and the delivering Work is `OQ-1233`'s.
- **f, g:** resolved by `RL-1232` DP-6 (b) and DP-7 (a).
- **i:** #830 has merged as `RL-1184`. #837 (the F1 record) is still open, so it is still
  cited by PR number.
- **k:** superseded by Acceptance item 7's re-run: 8 rows, six of them WK-674's.
- **m, o:** #830's E7 and E6 are `RL-1184`'s. The substance of each premise is unchanged.
- Line cites that moved, found by comparing each cited line at the two trees: `03:137` →
  `03:138` (FR-241), `03:153` → `03:154` (FR-247), `03:847` → `03:1050` (the Deployments
  view), `06:219` → `06:220` (amended), `06:568` → `06:625`, `docs/roadmap.md:620` → `:629`,
  and `tests/test_repository_invariants.py:81` → `:83`. The register's F54 row is still
  `docs/findings/register.md:95`, with its cell rewritten by the register-and-records pass.

### Noted, not WK-674's

**A premise, recorded and not planned here.** The following `07` §3.6 requirements are held
by no roadmap row at this tree (`grep -n '<id>\b' docs/roadmap.md` prints nothing for each):

- FR-432, the image set;
- FR-433, Helm;
- FR-434 and NFR-534, scoring without the compute pool;
- FR-435 and NFR-531, migrations and rolling deploys;
- FR-438 and NFR-533, signed images and the SBOM.

`deploy/docker-compose.yml` ships only `postgres`, `redis`, `minio` and `keycloak`, and no
application service (premise d). Assigning an owner to an id on no row is re-planning, so
this plan proposes it to **plan review 15** and does not take it. There are two exceptions:

- **FR-433 (Helm) is DP-1.** FR-437 says "Owned by WK-674, with the rest of `deploy/`
  beyond compose", which puts a chart in WK-674's reach by the spec's own words.
- **Slice 4 builds compose `api` and `worker` services.** This is **slice design**,
  decided in the slice-design note below, because the F1 acceptance test needs a real
  deployment path. Building them is not a claim on FR-432's or FR-434's verdict. The
  closure record gives those ids no verdict unless plan review 15 assigns them here.

**Resolved 2026-09-29.** Plan review 15 has assigned them (`CR-1212` item 12, and G4 (d) for
NFR-533):
- **FR-434 with NFR-534, and FR-435 with NFR-531, are WK-674's.** They are placed in Slice 4
  (see **Placement of `CR-1212`'s WK-674 assignments**), so Slice 4's `api` and `worker`
  services *are* evidence for FR-434 and NFR-534.
- **FR-432, FR-433 and FR-438 are carried to Phase 3**, and so is NFR-533 (G4 (d)). Slice 4's
  services remain no claim on FR-432's verdict.
- **FR-433 is DP-1 (b), resolved by `RL-1232`.** `07` FR-437's amendment recording the move
  is in `RL-1232`'s commit, not in any slice.

This section's heading is kept, and only FR-432, FR-433, FR-438 and NFR-533 now fit it.

---

## Decision points

These rows follow the form in `docs/process/document-ids.md` §1.7. **Three rows are the
maintainer's**, resolved by the deputy under the maintainer's delegation: DP-1, DP-2 and
DP-3, all of kind *scope*. **DP-4, DP-6 and DP-7 are the decision-maker's**, all of kind
*decision point*. Each of those is a spec-versus-spec or spec-versus-code question
(`delivery-process.md` §3). The planner rules none of them. Slice design is decided in this
plan and is not in this table.

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-1 | Does WK-674 build FR-433's Helm chart / Kubernetes manifests? FR-437 says "Owned by WK-674, with the rest of `deploy/` beyond compose", yet FR-433 is on no roadmap row | (a) Build the chart in WK-674, as a seventh slice after Slice 5; (b) move FR-433 to Phase 3, with its owner named at plan review 15, and WK-674's `deploy/` work stops at compose plus FR-437's reference Keycloak; (c) leave it unowned, recorded as a premise only | **(b).** The F1 acceptance test is measured on the compose path Slice 4 builds, and no Phase 2 requirement is evidenced by a chart. A chart nobody deploys is an artifact nothing tests. (c) leaves the one id the spec itself routes towards WK-674 without an owner | scope | yes — Slice 4 (its `deploy/` scope) | `RL-1232` Part A — **(b)**, as filed 2026-09-28 14:08:59 and standing (QDP entry, 2026-09-29). FR-437's amendment is in `RL-1232`'s commit (QDP-1) |
| DP-2 | FR-270 and FR-271 are marked "Optional". Are they built in WK-674 or deferred? | (a) Build both, as Slice 6; (b) build FR-271 (shadow feeds `05`) and defer FR-270 with an owner; (c) defer both, with WK-687 as owner | **(a).** Both are in the roadmap row's id list. "Optional" is a per-environment runtime option, not an optional deliverable. FR-271 is "the pre-deployment safety net feeding 05", and WK-687 cannot compare shadow results that were never recorded | scope | yes — Slice 6 | `RL-1232` Part A — **(a)**, standing: both built, default off per environment, enabling one is an environment setting with its own audit event |
| DP-3 | NFR-489's failure path. It is a failing measurement carried to WK-674 (premise l). If the Slice 5 re-measurement on the deployment path still fails, what does the Work do? | (a) Record the measured verdict FAIL and close on a reduced scope, as WK-671 did; (b) record the verdict, and if RL-921 §4's trigger fires (the 15 ms without-GBM limb still fails with the blob read removed) file a proposed NFR-489 amendment as its own spec change with the measurement; (c) hold the close until it passes | **(b).** The requirement has failed at two closes (`CR-927` §4 and §10). RL-921 §4 already names the condition under which NFR-489 "itself" is in question. A third failure with no proposal repeats a verdict and changes nothing. Never a silent pass | scope | no — resolved at Slice 5's close. Until then, the default is the measured verdict, recorded as is | `RL-1232` Part A — **(b)**, standing, with the limit that a performance target changes only by the maintainer's decision. *QDP-3 note (2026-09-29): "verdict recorded; the re-measurement trigger cannot validly fire without a dedicated host (RL-921)". The host is a maintainer-owned dependency of Slice 5* |
| DP-4 | FR-272's notification "to a configured channel": no `07` requirement specifies a channel (premise e) | (a) A spec change in `07` defining a minimal channel (a webhook through a secret reference), built in Slice 2; (b) WK-674 writes a durable deployment event through the outbox with the Audit Event, and delivery belongs to WK-688 (alerting lifecycle and routing, Phase 4), with FR-272 amended to say so; (c) WK-674 builds delivery with no spec | Decision-maker's call. Planner's input: (b). The retry and failure-surfacing obligations sit in `05` FR-336, which is WK-688's. A channel built now would be the "later phase built ahead" that `CLAUDE.md` §0 forbids. (c) is excluded by `CLAUDE.md` §0 | decision point | yes — Slice 2's close (not its start) | `RL-1232` Part B — **(b), narrowed to the Audit Event**, as amended 2026-09-29 (Q848-1): the channel is `07` FR-453, and its delivering Work is `OQ-1233`'s (open) |
| DP-6 | The deploy permission's name: `06:62` and `06:219` say `rating_version:deploy_prod` and `rating_version:deploy_*`, per environment; the code says `deployment:promote` | (a) The spec is right: rename to a per-environment family; (b) the code is right: amend `06` to `deployment:promote`, scoped by the environment of the grant; (c) keep both | Decision-maker's call. Planner's input: FR-430 already scopes credentials per environment, so (b) keeps one permission and one scoping mechanism | decision point | yes — Slice 2 | `RL-1232` Part B — **(b)**, the code's name `deployment:promote`, as amended 2026-09-29 (Q843-1): "no environment-scoped grant" is the Phase 2 state only; `CR-1212` item 4's spec change scoping it to named environments lands in Slice 2. *(This row's planner input rested on FR-430, which `RL-1232` shows does not carry over to human grants.)* |
| DP-7 | Promotion order: a route check (`PROMOTION_ORDER_VIOLATION`, FR-429) or an evidence floor (`uat_deployment`, FR-364, `EVIDENCE_INCOMPLETE`)? | (a) Both: the route refuses a `prod` deploy with no successful `uat`, and the approval submission's floor also requires it; (b) the floor only, with the code removed from the stub; (c) the route only, with the floor kind removed | Decision-maker's call. Planner's input: (a) is what the two specs say read together, since the floor gates submission and the route gates the act | decision point | yes — Slice 2 | `RL-1232` Part B — **(a), both checks on one predicate**, standing as a requirement-level ruling (premise note 2026-09-29, Q848-2). The skip's home is `OQ-1234`, owner WK-674, placed in Slice 2 |

**DP-5 is withdrawn, and its number is not reused.** It asked what verdict NFR-497's monthly
availability target gets. A verdict on an unevidenced requirement is the lead's, not a
decision point (`CLAUDE.md` §12 and §13). The question moves to **Verdicts the plan does not
give** below.

### Verdicts the plan does not give

The lead gives these verdicts at the close. The planner's input is stated here so that it
is on the record before the close, not argued after it.

- **NFR-497, the 99.95 % monthly target (register F41).** Planner's input: *deferred with
  an owner — WK-687* (operational monitoring, Phase 4). The degraded read is delivered, and
  Slice 5 keeps it working against the `live` reference. A monthly availability figure can
  only be measured by the monitoring WK-687 builds. A synthetic month measures the harness,
  not the target.
- ~~**FR-432 and FR-434, if plan review 15 assigns them to WK-674.** Slice 4's compose `api`
  and `worker` services are then evidence for them. They are not evidence for any id plan
  review 15 does not assign.~~ *(Struck 2026-09-29: plan review 15 has decided. FR-434 and
  NFR-534 are WK-674's and are placed in Slice 4, and FR-432 is carried to Phase 3
  (`CR-1212` item 12). These are no longer verdicts the plan does not give.)*

**Slice design, decided here and not a DP.** Slice 4 (the deployment path) runs **before**
Slice 5 (switchover). The deputy's F1 decision measures the acceptance test "on the
deployment path WK-674 builds, not a loopback mirror", and at this tree no such path
exists (premise d). Running Slice 5 first would reproduce F1's own limitation, which the
decision calls inconclusive for exactly that reason. Slice 3 (environment isolation) runs
before Slice 4. The deployment path is then measured with the per-environment keys and the
shared rate-limit counter already in place. A path measured without them would change
shape when they land, and the NFR-489 figure would describe a path that is never shipped.
Slice 4 also builds compose `api` and `worker` services, as the path itself. There are no
application services in `deploy/docker-compose.yml` at this tree, and the F1 test cannot
run on n replicas without them. This is how the slice is built, not a scope claim on
FR-432 or FR-434 (see **Noted, not WK-674's**). *(Amended 2026-09-29: `CR-1212` item 12 has
since assigned FR-434 to WK-674, so the services are FR-434's evidence. They remain no claim
on FR-432, which is carried to Phase 3.)*

**Slice ids.** No `SL-` row exists in `docs/roadmap.md` (`grep -c 'id: SL-'
docs/roadmap.md` prints 0), which follows the `PL-930` and `PL-1177` precedent. Slices are
named here by number. The six `SL-` rows are minted with ids the lead issues, as `draft`,
when this plan is activated.

## Sequencing

```
Slice 1  tenancy + provenance ─→ Slice 2  Environment + Deployment record
                                   ─→ Slice 3  environment isolation (keys, rate limit)
                                   ─→ Slice 4  deployment path (compose api/worker, Keycloak ref, memory budget)
                                   ─→ Slice 5  atomic switchover + rollback + measurements (F1 test)
                                   ─→ Slice 6  date routing + shadow   [DP-2]
```

Strictly one slice at a time (`delivery-process.md` §8). Each slice depends on the one
before it:

- **Slice 2 needs Slice 1**, because the Deployment row is written in a database whose
  tenant marker Slice 1 establishes.
- **Slice 3 needs Slice 2's Environment entity**, because the keys and the counter are per
  environment.
- **Slice 4 needs Slice 3**, for the reason in the slice-design note above.
- **Slice 5 needs Slice 4's path and Slice 2's record**, because a switch is triggered by a
  deployment.
- **Slice 6 needs Slice 5's `live` reference**, because routing and shadow both select
  among bundles that are already warm.

The mapping to the proposal the lead adopted is: its S1, S2, S4, S5, S3 and S6 are Slices
1 to 6 here.

**Open-question gates, added 2026-09-29.** Two slices wait on open questions WK-674 owns, as
well as on the slice before:
- **Slice 2's leaf plan does not go `active` until `OQ-1234` is decided** (the skip's home,
  which DP-7's one predicate reads).
- **Slice 3 does not start until `OQ-1235` is decided** (roadmap gate "Before WK-674 Slice
  3"). The same answer governs Slice 6's per-environment default-off switches.
- **Slice 5's measurements wait on the dedicated host**, a maintainer-owned dependency
  (QDP-3). Slice 5's code can land before the host exists, but its measured verdicts cannot.

---

## Tasks

At this level, each slice is one task: its scope, its dependency, and an outline of its
gate. The steps are written in its leaf plan. **Item 11 of every slice** is the close
condition in `PL-1070` item 11's form:

> ~~**The deputy's merge acknowledgement is recorded** on the PR before the lead merges, and~~
> **The maintainer's MERGE-ACK, naming the PR's full head SHA, is recorded in the lead's
> channel file (`~/gi-pricing-plan.local/channel/to-lead.md`), given by the maintainer or on
> the maintainer's behalf, before the lead merges. It is never posted on the PR.** And
> the slice's clean audit is filed. Per `CLAUDE.md` §13 a Slice closes on a clean audit and
> the lead's merge — no maintainer acceptance line is required for this slice, and none is
> to be waited on.

*(Amended 2026-09-29: the ACK's place is step 6 of the maintainer's 2026-09-29 10:41:05 BST
merge plan and `lead.md` rule 4 as amended by PR #893. It is the same correction the
auditor made to the Slice 1 leaf plan.)*

### Task 1 — Slice 1: tenancy and provenance (FR-436, FR-18)

- **Scope.**
  - A tenant identifier in deployment configuration.
  - A single-row marker table, written at first migration and carrying the same
    identifier.
  - A startup check that refuses to start on a mismatch. It is a startup failure, not a
    warning. It covers the database, object storage and the broker wherever their
    configuration is per tenant (FR-436).
  - A platform-build column on the Job row, ~~set at submission~~ **set when the worker moves
    the Job to `running`** *(amended 2026-09-29: FR-18 reads "the platform version it ran on",
    so this map adopts the Slice 1 leaf plan's (#892) recording point; a Job reaches
    `running` once, so it records one build)*, and the dossier's statement
    of it (FR-18). The dossier generator is WK-680's, so this slice exposes the value, and
    records that the dossier half is carried with an owner if WK-680 has not landed.
- **Depends on:** nothing in WK-674.
- **Gate outline.**
  - Negative tests on deliberately mismatched configuration, one per store, each naming the
    mismatch in its predicted failure.
  - The migration is reversible, and has exactly one head (`07` FR-417).
  - A `req("FR-18")` test.
  - The full gate, both halves.
  - Item 11.

### Task 2 — Slice 2: the Environment and Deployment record (FR-267, FR-428, FR-429, FR-272 audit, NFR-498, the carried rulings)

- **Scope.**
  - **The slice opens with a spec change, before any code.** `03` declares no `Deployment`
    contract (premise n). The change appends one to `03` §4, after §4.8, and declares the
    `Environment` data contract alongside it. It adds a `GET` for deployment history, which FR-382 and the
    view at `03:847` (`03:1050` at `9cd179cb`) need and `03` §5.1 lacks. It adds the audit-action catalogue for
    deployment, rollback, routing change and shadow configuration change (FR-368, NFR-498).
    It applies DP-6 and DP-7. It adds RL-886's `06` §4.2 policy entry with its dated note, and
    the matching `deployment` entry in `DEFAULT_POLICY`
    (`packages/model-schema/src/model_schema/approvals.py:202`; premise p).
  - Then the `model-schema` shapes and the regenerated contracts.
  - Then Environment as an entity (FR-428), seeded `dev → uat → prod`, including
    promotion order (FR-429).
  - Then `POST /api/v1/environments/{env}/deployments`, which records who, when, why and the
    bundle hash, requires Deployer, and applies the `prod` approval (FR-267). It writes the
    Audit Event in the same transaction (FR-368, FR-272 audit limb).
  - Then default-live resolution on `/score` (RL-880; register F43 L1). The 409 branch
    remains for an environment with no Deployment.
  - Then the reconciliation of each trace's environment string to its Deployment (RL-888,
    RL-916), and `WITHDRAW_AFTER_DEPLOY_FORBIDDEN` (FR-357).
  - The switch itself is **not** in this slice. A deployment recorded here takes effect by
    the existing per-request resolution. Slice 5 replaces that resolution with the push.
  - *Added 2026-09-29.* **`CR-1212` item 4's environment-scoping spec change**, landed with
    the Environment record it scopes: a `06`/`07` spec change that scopes
    `deployment:promote` to named environments (`RL-1232` DP-6 as amended, Q843-1). It goes
    in through `spec-change`, before the code that enforces it.
  - *Added 2026-09-29.* **`OQ-1234`'s answer** (the home of FR-429's skip permission) is
    applied here, in the shape the decision gives. DP-7's one predicate reads it, so the
    route check and the `uat_deployment` floor are built against the decided home, not a
    guessed one.
- **Depends on:** Slice 1. ~~It is blocked on DP-6 and DP-7, and its close is blocked on DP-4.~~
  ~~**Its leaf plan is not written until the decision-maker's permission-catalogue ruling (pending)
  merges** (#855's finding; the deputy's 14:52:49 BST entry, item 4(a)). Until then, the names it
  would use are those stated in **Permission names** above, each with #855's finding cited.~~
  *(Amended 2026-09-29.)* DP-4, DP-6 and DP-7 are resolved by `RL-1232`, and the catalogue
  ruling has merged as `RL-1236` (FD-1197 is #855's finding), so neither block remains. **Its
  leaf plan does not go `active` until `OQ-1234` is decided.**
- **Gate outline.**
  - Each refusal is tested by its cause:
    - a missing approval gives `DEPLOY_REQUIRES_APPROVAL`;
    - skipping `uat` gives ~~whatever code DP-7 decides~~ `PROMOTION_ORDER_VIOLATION` at the
      route and `EVIDENCE_INCOMPLETE` at the `prod` approval submission, both reading one
      predicate, and a test shows the two cannot disagree on one Rating Version (`RL-1232`
      DP-7; amended 2026-09-29);
    - a non-Deployer is refused;
    - *added 2026-09-29:* a Deployer whose grant names only `uat` is refused on `prod`
      (`CR-1212` item 4);
    - *added 2026-09-29:* a deployment whose transaction commits with no Audit Event is
      shown red on deliberately broken input (`RL-1232` DP-4);
    - a non-Admin creating, renaming or retiring an Environment is refused for lack of
      `admin:manage_environments` (~~#856's~~ `RL-1236` DP-B);
    - a Service Account holding a deploy permission is refused (FR-347);
    - a policy entry that is absent fails as RL-886 describes, by its cause.
  - `generate-contracts.py --check` passes.
  - The ER relationship `Deployment ──< ScoringTrace` holds, and the migration reconciling
    it is tested on existing rows.
  - The full gate.
  - Item 11.

### Task 3 — Slice 3: environment isolation (FR-430, FR-431, register F54, register F48; NFR-496's prod-sampling limb, added 2026-09-29)

- **Scope.**
  - **The slice opens with a spec change, before any code.** `07` §4.3's `ServiceAccount`
    contract shows one `key` object (premise m). FR-430's amendment (~~#830 item E7~~ `RL-1184` E7) says
    the account holds one key per granted environment. §4.3 is amended to the key set,
    keyed by environment, with each key's rotation state, through `spec-change`.
  - One key per granted environment: creation mints one key per environment, and rotation
    and revocation act on one named environment's key (FR-430 as amended by ~~#830 item E7~~
    `RL-1184` E7; register F54).
  - A test in which a legitimately issued `dev` key is refused against `uat`. Today the
    refusal branch cannot be reached by a key the platform issued.
  - Environment configuration as a Setting, audited on change (FR-431). It is guarded by
    `admin:manage_settings` (~~#856's~~ `RL-1236` DP-D), and each change's Audit Event names the
    environment, the key, the old value and the new value. *(Amended 2026-09-29: it resolves
    per `OQ-1235`'s answer, which decides where the Environment level sits relative to
    `07` FR-446's precedence.)*
  - NFR-499's per-client limit as a **shared Redis counter, per tenant** (~~#830 item E6~~
    `RL-1184` E6; register F48). It reads `rate_limit_rps` and raises `RATE_LIMITED`.
  - *Added 2026-09-29.* **FR-430's monitoring-configuration limb.** Each environment holds
    its own monitoring configuration, as environment configuration in `OQ-1235`'s shape, so a
    change in one environment never changes another's. The limb is the per-environment
    *configuration* only. The monitors that read it are WK-687's (Phase 4), and this slice
    builds none of them (`CLAUDE.md` §0).
  - *Added 2026-09-29.* **NFR-496's prod-sampling limb** (`CR-1212` G4 (a)). The ladder
    reconciliation (FR-248) is asserted on every scored quote in non-`prod` environments,
    and on a configured sample in `prod`. The sampling rate is per-environment
    configuration, guarded by `admin:manage_settings` like every other environment setting.
- **Depends on:** Slice 2. *(Amended 2026-09-29.)* **And on `OQ-1235` being decided**: its
  roadmap gate is "Before WK-674 Slice 3".
- **Gate outline.**
  - A two-replica test showing that the limit holds across replicas. A limiter kept in one
    process "is not a limit" (register F48), so a single-process test proves nothing here.
  - A negative test showing that the old one-key behaviour fails the new assertion.
  - *Added 2026-09-29:* a test that setting a monitoring-configuration value in `uat` leaves
    `prod`'s resolved value unchanged, with a broken-input proof: a shared, unscoped key
    makes it go red (FR-430's monitoring limb).
  - *Added 2026-09-29:* a test that non-`prod` asserts the reconciliation on every quote and
    `prod` on the configured sample, with a broken-input proof: an off-by-one-penny ladder is
    caught in `uat` on the first quote (NFR-496).
  - The full gate.
  - Item 11.

### Task 4 — Slice 4: the deployment path (FR-437 reference, FR-412 memory half, FR-415 worker service; FR-434, FR-435, NFR-531, NFR-534 and FD-1211, added 2026-09-29)

- **Scope.**
  - The compose `api` service, runnable as n replicas behind a stated load-balancing
    topology.
  - A `worker` service, to which FR-412's **memory** budget is applied and enforced
    (FR-415's WK-674 clause).
  - `api` runs with no compute pool present. ~~This is how the path is built (slice design),
    not a verdict on FR-434 or NFR-534, which plan review 15 assigns or does not.~~
    *(Amended 2026-09-29: `CR-1212` item 12 assigns FR-434 and NFR-534 to WK-674.)* This is
    **FR-434's delivery and NFR-534's measurement**: the scoring API is deployed and scaled on
    its own, and serves with the `worker` service absent.
  - *Added 2026-09-29.* **FR-435: migrations as an explicit pre-deploy step**, a one-shot
    step the deployment path runs before `api` starts, never at application start, with each
    migration forward-compatible with the previous application version. **NFR-531** is
    measured on it: the previous `api` version serves against the migrated schema while
    replicas roll forward, with 0 failed requests.
  - *Added 2026-09-29.* **FD-1211: the process lifecycle.** The `worker` and `api` services'
    shutdown and recycling design covers a process that loads the FD-1199 teardown-abort
    extensions and exits, which is FD-1211's event.
  - The reference Keycloak deployment under `deploy/`, with a README saying the deployer
    operates, patches and is accountable for it (FR-437). *(2026-09-29: FR-437's dated
    amendment moving FR-433 to Phase 3 is already **done by `RL-1232`** (DP-1 (b), QDP-1).
    This slice builds the reference deployment only.)*
  - A load harness that drives `/score` at 200 rps against n ∈ {2, 4, 8} replicas and
    records the load at the start of each run. Slice 5 reuses it.
- **Depends on:** Slice 3. ~~Its `deploy/` scope beyond compose is blocked on DP-1 (Helm).~~
  *(2026-09-29: DP-1 is resolved (b) by `RL-1232`. WK-674's `deploy/` work stops at compose
  plus FR-437's reference Keycloak, and Helm is Phase 3.)*
- **Gate outline.**
  - A test that brings the stack up.
  - A Job over its memory budget terminates with a typed error naming the budget (FR-412),
    proven on a deliberately oversized Job.
  - The harness's dry run on this path, with its output quoted.
  - *Added 2026-09-29:* Acceptance Standard item 12's two tests (FR-434 with NFR-534; FR-435
    with NFR-531), each with its broken-input proof.
  - *Added 2026-09-29:* a test of a process that loads the FD-1199 extensions and exits
    cleanly under the designed shutdown path (FD-1211's event), repeated enough times to meet
    an intermittent abort, with the count stated.
  - The full gate.
  - Item 11.

### Task 5 — Slice 5: atomic switchover, rollback and the measurements (FR-268, FR-269, NFR-494, NFR-489, NFR-502; NFR-490, NFR-493's linearity limb, and FR-272's and NFR-498's rollback limb, added 2026-09-29)

- **Scope.**
  - The PREPARE/COMMIT push over a Redis channel, per the F1 decision. It is triggered by
    Slice 2's deploy transaction. Each worker hydrates off the event loop and acknowledges,
    then swaps its one `live` reference and acknowledges.
  - `/score` reads `live` once at request start, and every response carries the bundle
    hash.
  - `bundle_slot_capacity` is set, and any value above 1 cites the measurement (RL-882).
  - Rollback is the same operation aimed at a previously deployed version, with no
    re-approval (FR-269). *(Added 2026-09-29.)* It emits its Audit Event, with before and
    after state, in the rollback's own transaction (FR-272's and NFR-498's rollback limb;
    `RL-1232` DP-4).
  - The measurements:
    - the F1 acceptance test, unchanged (Acceptance Standard item 5), filed as a research
      record;
    - NFR-489 and NFR-502 on the dedicated host, more than one pass (item 6), which also
      discharges F-W9-1's owner row *(noted 2026-09-29)*;
    - *added 2026-09-29:* NFR-490 (tracing ≤ 20 %, result unchanged) and NFR-493's
      linearity limb (batch throughput at 1, 2 and 4 workers), on the same host, the same
      way (item 6);
    - *added 2026-09-29, the maintainer's entry `2026-09-29 15:36:43 BST · maintainer
      (acting on the maintainer's behalf) · SCOPE: NFR-490 / F35 in WK-674, option (b)`:*
      **NFR-490 is measured and, if red, recorded red with the figure, the tree and the log.
      This slice does not build F35's remedy** (the ~1.1 MB `to_wire(passThrough: True)`
      payload). The remedy is carried forward, with its owner named at plan review 16;
    - DP-3 is applied at the close;
    - NFR-497's degraded read is re-tested against the `live` reference with metadata
      storage stopped, and its availability verdict is left to the lead (**Verdicts the
      plan does not give**).
  - *Added 2026-09-29, the maintainer's answer QDP-3.* **The dedicated host is a dependency
    owned by the maintainer**, not by this slice. No repo record names one at `9cd179cb`.
    Until it exists, DP-3 (b) reads "verdict recorded; the re-measurement trigger cannot
    validly fire without a dedicated host (RL-921)", and no measurement from the shared VM is
    reported as a verdict near a bound.
  - *Added 2026-09-29, in the commit that sets this plan `active`: the maintainer's host
    fallback* (entry `2026-09-29 16:08:24 BST · maintainer (acting on the maintainer's behalf)
    · HOST FALLBACK accepted; DEPENDABOT plan approved (the maintainer)`, §1, quoted verbatim
    in Acceptance item 6). No dedicated host is committed. Where none exists at this slice's
    close, **the F1 test, NFR-489, NFR-502, NFR-493's linearity limb and NFR-494** are
    recorded as "**measured, diagnostic** on the shared VM; the verdict is **carried**, owner
    the maintainer, discharge event **a dedicated host available**". **NFR-490 is unchanged** (the SCOPE
    entry of 15:36:43 BST).
- **Depends on:** Slice 4's path and harness, and Slice 2's deploy transaction. *(Added
  2026-09-29.)* Its measured verdicts also depend on the maintainer-owned dedicated host.
- **Gate outline.**
  - The F1 test's 9 or more runs, with loads recorded. *(2026-09-29: on the dedicated host;
    shared-VM runs are diagnostics only.)*
  - The 3 m-n4 drops are explained, or 0 drops are shown at n=4 and n=8.
  - A broken-input proof that a response whose bundle hash differs from `live` fails the
    mixed-bundle assertion.
  - The rollback tested under load.
  - *Added 2026-09-29:* a rollback whose transaction commits with no Audit Event is shown red
    on deliberately broken input.
  - *Added 2026-09-29:* NFR-490's "never changes the result" limb, tested by scoring one quote
    with tracing on and off and comparing results byte for byte; the latency limb is item 6's
    measurement.
  - The full gate.
  - Item 11.

### Task 6 — Slice 6: date-based routing and shadow scoring (FR-270, FR-271), subject to DP-2

- **Scope.**
  - The spec task comes first: correct FR-241's stale cross-reference to FR-270 (premise h).
  - Declare the routing-rule and shadow-configuration contracts in `03` §4, and add a route
    for configuring date routing. `03` §5.1 has `PUT /api/v1/environments/{env}/shadow`
    but no routing route.
  - Build date routing: several deployed versions per environment, selected by the quote's
    effective date. Overlapping ranges are refused at deploy time with
    `DEPLOY_DATE_RANGE_OVERLAP`.
  - Build shadow scoring: a proportion of live traffic is scored against a candidate
    **after** the caller's response and never returned to the caller. Results are
    persisted, with premiums held exactly as in `ScoringResult`, where `05` FR-330 can
    read them.
  - Routing and shadow-configuration changes emit Audit Events (FR-272), each with before
    and after state in the change's own transaction (NFR-498's routing limb; *made explicit
    2026-09-29*). Turning routing
    or shadow on or off, and the shadow configuration, are per-environment settings guarded
    by `admin:manage_settings` (~~#856's~~ `RL-1236` DP-D), resolved as `OQ-1235` decides. A deployment carrying a date range is guarded
    by `deployment:promote` (the deputy, 15:05:53 BST).
  - **The rule: nothing guarded by `admin:manage_settings` may change which Rating Version
    prices a live quote** (the deputy, 15:05:53 BST). With routing on, selection is only among
    versions promoted into that environment through `deployment:promote`. Turning routing
    on never makes a version live that was not promoted there.
- **Depends on:** Slice 5. ~~It is blocked on DP-2.~~ *(2026-09-29: DP-2 is resolved (a) by
  `RL-1232`, so both are built, default off per environment.)*
- **Gate outline.**
  - The overlap refusal tested by its cause.
  - A test showing a shadow result never appears in the caller's response.
  - A negative test for the safeguard, stated by its cause (selection, not permission): with
    routing on, a version present in the environment but not promoted into it is never
    selected (the deputy, 15:05:53 BST).
  - A negative test: a user without `admin:manage_settings` is refused enabling shadow on
    `prod` (~~#856's~~ `RL-1236` DP-D). A companion test shows an allowed change writes the Audit Event
    with the environment, the key, the old value and the new value.
  - *Added 2026-09-29:* a routing change whose transaction commits with no Audit Event is
    shown red on deliberately broken input (FR-272; NFR-498).
  - A latency check showing shadow scoring adds no time to the caller's p99, measured on
    Slice 4's harness.
  - The full gate.
  - Item 11.

---

## Activation

When ~~the deputy accepts this plan by delegation~~ the maintainer (or the session acting on
the maintainer's behalf) accepts this plan *(amended 2026-09-29)*, the activation commit:

1. Sets `status: active` in the front matter. This is permitted only when every blocking
   Decision point row has a resolver id (`document-ids.md` §1.7). Otherwise the plan stays
   `draft`, and the rows still open are named in the acceptance line. *(2026-09-29: every
   row now has one, `RL-1232`.)*
2. ~~Corrects the `From "Workstreams"` line under `### WK-674` in `docs/roadmap.md` (premise
   a), in the same way `PL-1177`'s Task 1 corrected WK-672's. It appends, after the FR-18
   clause: "; and, owned by WK-674 in `07` itself: **FR-437** (the reference identity
   provider, `07:153`), **FR-412**'s memory half and **FR-415**'s worker service (`07:104`)
   — added 2026-09-28 by the map plan". It also appends the F1 obligation, which
   the F1 decision says is written into the row when the first slice is planned.~~
   *(Amended 2026-09-29, the maintainer's answer Q843-2: "The roadmap WK-674 row edit is
   the lead's, after the map is accepted.")* **The lead** corrects the `From "Workstreams"`
   line under `### WK-674` (premise a; now `docs/roadmap.md:676`). The ids it should add
   are: FR-437 (`07:153`), FR-412's memory half and FR-415's worker service (`07:104`), and
   `CR-1212`'s FR-434, FR-435, NFR-531, NFR-534, NFR-489, NFR-490, NFR-502, NFR-493's
   linearity limb and NFR-496's prod-sampling limb, with the F1 obligation. This plan
   proposes that list and does not write the row.
3. Adds the six `SL-` rows under `### WK-674`, with ids the lead issues, each `draft`.
4. Regenerates `docs/INDEX.md` in the final commit only.

**Maintainer acceptance, quoted verbatim** from the entry headed `2026-09-29 16:04:02 BST ·
maintainer (acting on the maintainer's behalf) · PL-1237 ACCEPTANCE LINE (the WK-674 map
plan)` (to-lead.md). The copy of that entry which follows it in the channel file, with its
timestamp missing, is voided and is not the source:

> **Maintainer acceptance:** accepted 2026-09-29 16:04:02 BST by the maintainer's delegation (to-lead.md). PL-1237 is `active`. Slice 1 may start. Slice 2 waits on OQ-1234 and Slice 3 on OQ-1235 (both resolved by the decision-maker by `RL-`). Slice 5's measured verdicts wait on a dedicated host (maintainer-owned). F35's remedy is carried per SCOPE 2026-09-29 15:36:43.

**Activated 2026-09-29** in PR #892, the Slice 1 leaf plan's PR, which is next in the WK-674
chain: `status: active` is set in the same commit as this quotation and as the host
fallback (Acceptance items 5 and 6; Task 5). Step 1's condition holds: every Decision point
row has its resolver, `RL-1232`. Steps 2 and 3 are the lead's.

## Status

- **Acceptance line:** ~~_pending — the maintainer's dated line, or one given on the
  maintainer's behalf_ *(amended 2026-09-29; it was "the deputy's dated line by delegation")*~~
  **Given 2026-09-29 16:04:02 BST by the maintainer's delegation**, and quoted verbatim under
  **Activation**.
- **Status note, dated 2026-09-29, at activation.** Which slices can start:
  - **Slice 1 may start.** Its leaf plan is PL-1239 (`draft`, with its own DP-S1-1 to
    DP-S1-3 open).
  - **Slice 2 waits on `OQ-1234`** (the home of FR-429's skip permission). The decision-maker
    resolves it by an `RL-`.
  - **Slice 3 waits on `OQ-1235`** (per-environment configuration against FR-446's
    precedence), resolved the same way. That is its roadmap gate "Before WK-674 Slice 3".
  - **Slice 5's measured verdicts wait on a dedicated host**, owned by the maintainer. Under
    the host fallback (Acceptance item 6), the near-bound verdicts are recorded as measured,
    diagnostic and carried if no host exists at its close.
  - **F35's remedy is carried** per the maintainer's entry `2026-09-29 15:36:43 BST ·
    maintainer (acting on the maintainer's behalf) · SCOPE: NFR-490 / F35 in WK-674, option
    (b)`. WK-674 measures NFR-490 and does not build the remedy, whose owner is named at plan
    review 16.
  - Slices 4 and 6 follow in sequence, with no gate beyond the slice before (Slice 6 inherits
    `OQ-1235` through Slice 3).
- **2026-09-29: working id 9102, minted 1237** at #843's turn in the merge queue, from
  `doc-id.py next --ref origin/main` at `9cd179cb`. `created:` moved from 2026-09-28 to the
  mint date, because `audit-docs.py` check 31 requires `created` to be non-decreasing with
  the number. The only surviving mention of the working id is inside `RL-1232`'s fenced,
  verbatim quotation of the deputy's 2026-09-28 14:08:59 entry, which is a dated record and
  is not rewritten.

## Self-review

1. **Spec coverage.** Every id in the roadmap row, and every id `07` assigns to WK-674, is
   in the coverage table with a slice or a DP: FR-267, FR-268, FR-269, FR-270, FR-271,
   FR-272, FR-428, FR-429, FR-430, FR-431, FR-436, FR-437, FR-412, FR-415, FR-18, NFR-489,
   NFR-494, NFR-497, NFR-498 (its deployment, rollback and routing limb, added in the
   2026-09-28 amendment), NFR-502. The 06 obligations are split into the three WK-674 builds
   (Slice 2) and the other Works' requirements it feeds. The 05 obligations are named as fed
   and not built. The `07` §3.6 ids on no roadmap row are a premise for plan review 15,
   except FR-433, which is DP-1.
2. **Placeholders.** None in the scope, the premises or the DPs. The empty `Resolved by`
   cells are the §1.7 form for open rows, not placeholders. Code steps are deliberately
   absent: this is a map plan.
3. **Consistency.** The slice numbers used in the coverage table, the carried obligations,
   the DP `Blocking` cells, the Sequencing and the Tasks agree, and were checked by
   grepping each "Slice N" across the file. The F1 test is stated once, in item 5, and is
   referred to elsewhere.
4. **Rulings between the sweep and the PR.** `gh pr list --state open` was read before
   filing (`docs/plans/README.md` rule 4). #830 (items E6 and E7) and #837 (F1) are the
   open PRs that rule on this plan's subject, and both are cited by PR and item because
   neither is merged.
5. **Amendment, 2026-09-28 (the respawned planner, on the lead's adoption of `96af4958`).**
   This file was first committed at `96af4958`, and this commit amends it at tree
   `ed123cb0`. It adds premises l to q (NFR-489 as a failing measurement, `07` §4.3's single
   key, `03`'s missing `Deployment` contract, E6's route through the register pass, the
   missing `DEFAULT_POLICY` entry, `CR-927:172`). It adds NFR-498's limb. It narrows DP-1 to
   Helm. It re-kinds DP-4 as the decision-maker's. It withdraws DP-5 as a verdict. It corrects
   WK-687's and WK-688's phase from P3 to P4 (`docs/roadmap.md`'s `phase:` field under each).
   It splits the `06` sweep into what WK-674 builds and what it feeds, and records the
   `07` §3.6 ids on no row as a premise.
6. **Amendment, 2026-09-28 (the permission-catalogue rule (b), on the deputy's 14:52:49 BST entry).** It adds
   **Permission names**, a per-slice statement of every permission name a slice adds or
   checks, with its `06` status and reason, and #855's finding cited. It also records in Slice 2
   that its leaf plan waits for the catalogue ruling. The names
   were read at this tree from `permissions.py`, and each `06` count is a literal-string
   count (`git show origin/main:docs/specs/06-governance.md | grep -c -- '<name>'`).
7. **Amendment, 2026-09-28 (#856's DP-B and DP-D, the deputy's 15:01:11 and 15:03:38 BST
   entries).** The Slice 2, 3 and 6 permission rows now state decided names:
   `admin:manage_environments` for the Environment record's lifecycle only, and
   `admin:manage_settings` for every per-environment setting value, each with an Audit
   Event naming the environment, the key, the old value and the new value. Slice 2 gains the
   non-Admin negative test, and Slice 6 gains the `prod` shadow-enable negative test. The
   deputy's 15:05:53 BST entry confirms Slice 6's split: the date-range deploy is
   `deployment:promote`, and only the switches and the shadow configuration are
   `admin:manage_settings`. It adds the rule that nothing under `admin:manage_settings`
   changes which version prices a live quote, and the not-promoted-never-selected negative
   test.
8. **Amendment, 2026-09-29 (the WK-674 planner, at #843's merge turn, after `RL-1232` and
   `RL-1236` merged).** This branch merged `origin/main` at `9cd179cb`, and the front
   matter's `tree` moved to it. Sources: auditor-843's findings as the maintainer accepted
   them, and two maintainer entries, headed verbatim (fenced, because the first heading
   carries a padded id):

   ```text
   ## 2026-09-29 14:17:56 BST · maintainer (acting on the maintainer's behalf) · Q843-1/2/3: CR-01212 item 4 stands; DP-6 amended
   ## 2026-09-29 14:20:41 BST · maintainer (acting on the maintainer's behalf) · QDP-1/2/3 (WK-674 DP mechanisms)
   ```

   The change, item by item:
   - **`CR-1212`'s assignments placed (the blocker).** FR-434, FR-435, NFR-531 and NFR-534 go
     to Slice 4. NFR-490 and NFR-493's linearity limb go to Slice 5. NFR-496's prod-sampling
     limb goes to Slice 3. NFR-489 and NFR-502 stay in Slice 5. Every one folds, so there is
     no seventh slice; the one-line rationales are under **Placement of `CR-1212`'s WK-674
     assignments**. The phrase "plan review 15 assigns or does not" is struck at every site.
   - **The slice that creates Environment (Slice 2)** carries `CR-1212` item 4's
     environment-scoping spec change and `OQ-1234`. Its leaf plan waits for `OQ-1234`.
   - **`OQ-1235` gates Slice 3**, per its roadmap gate "Before WK-674 Slice 3".
   - **DP-3's dedicated host** is a maintainer-owned dependency of Slice 5 and of the F1
     acceptance test (Acceptance items 5 and 6). Nothing claims a near-bound verdict from
     the shared VM.
   - **Every DP's `Resolved by` cell is `RL-1232`.** DP-1 (b), DP-2 (a) and DP-3 (b) stand as
     filed; DP-4, DP-6 and DP-7 stand as amended. FR-437's amendment is recorded as done by
     `RL-1232`, so Slice 4 builds only the reference Keycloak. `RL-1236` replaces every
     "#856" citation, `RL-1184` every "#830 item E6/E7", and FD-1197 every "#855's finding".
     Struck text is kept.
   - **The five accepted fixes.** (1) FR-272 and NFR-498 are placed in Slices 2, 5 and 6, with
     a broken-input audit test in each. (2) FR-430's monitoring-configuration limb has a Slice
     3 bullet and a gate. (3) Stale cites were re-read at `9cd179cb`: each cited line was
     compared between the two trees, and the moves are annotated where they sit and listed
     under the premises. (4) `register-owed.py WK-674` was re-run and lists F54 and FD-1211,
     with FD-1211 placed in Slice 4 (Acceptance item 7). (5) Slice 1's build column is
     recorded at `running`, adopting the Slice 1 leaf plan's reading of FR-18's "ran on".
   - **Also corrected, the same defect the auditor found in the Slice 1 leaf plan:** item 11's
     "deputy's merge acknowledgement … on the PR" is now the maintainer's MERGE-ACK in the
     lead's channel file, never on the PR. The Activation and acceptance lines name the
     maintainer, not "the deputy". The roadmap row edit is the lead's (Q843-2), and this plan
     proposes the ids for it.
   - **Authority, noted later the same day** (the maintainer's 15:26:00 BST STRUCTURE entry):
     the placements are the planner's decisions, and Q843-2 is a recommendation they agree
     with at every point. See the note under **Placement of `CR-1212`'s WK-674 assignments**.
     The DP cells cite `RL-1232` unchanged. The decision-maker's dated re-adoption of the
     maintainer's technical answers in `RL-1232` belongs to the next records PR, not to this
     plan.
   - **Consistency checked by grep:** every id in the coverage table appears in its slice's
     Task, and no `Resolved by` cell is empty
     (`grep -E '^\| DP-[0-9]' <this file> | grep -c '| |$'` prints 0).
