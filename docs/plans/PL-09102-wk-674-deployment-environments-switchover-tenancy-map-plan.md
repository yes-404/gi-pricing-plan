---
id: PL-9102
family: plan
kind: map
title: WK-674 — Deployment, environments, atomic switchover, rollback, shadow and tenancy: map plan
status: draft                   # draft → active → superseded | retired (§1.2a)
created: 2026-09-28
owner: planner
tree: 6c6f4532c7d0ec65646225108f8cf9f8f570c746
phase: P2
work: WK-674
supersedes: []
superseded_by: ~
corrected_by: []
relates: [ADR-710, RL-876, RL-880, RL-882, RL-886, RL-888, RL-916, RL-921, RL-922, CR-927, PL-930, PL-1070, PL-1177]
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
  each listed below), §5.1 (the three deployment routes at `03:607-609`), §9 (NFR-489,
  NFR-494, NFR-497, NFR-502).
- [`../specs/07-platform.md`](../specs/07-platform.md): §3.5 (FR-428 to FR-431), §3.6
  (FR-436, FR-437), and §3.2 (Jobs): FR-412 and FR-415 (the clauses at `07:101` and `07:104`).
- [`../specs/00-overview.md`](../specs/00-overview.md): FR-18 (`00:221`), and the §2
  entities Deployment and Environment (`00:165-166`).
- [`../specs/06-governance.md`](../specs/06-governance.md): §3.3's deployment evidence row
  (`06:121`), FR-364's floor, the §4.2 `deployment` policy entry (`06:290-297`), and FR-368.
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
   that DP's resolver id.
2. **Every `07` requirement has a verdict.** Run
   `python3 scripts/scope-audit.py PLAT --sections 3.5 --extra FR-436,FR-437,FR-412,FR-415`.
   The same rule applies. **A pre-existing marker is not delivery.** FR-412's marker covers
   only the wall-clock half (`backend/tests/test_worker.py:288`). FR-430's marker exercises
   the refusal branch only on a hand-crafted key (register row F54). FR-437's marker covers
   only the local profile (`tests/test_repository_invariants.py:81`). Each of these ids gets
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
6. **NFR-489 and NFR-502 each carry a measured verdict.** Both are measured on the
   deployment path, on a dedicated host, in more than one pass (RL-922's table row for
   NFR-489). Each result is recorded in WK-674's closure record with the shape measured and
   the load at the start. If NFR-489 still fails, DP-3's resolution governs what the record
   says.
7. **The register rows owed to WK-674 are resolved.** `python3 scripts/register-owed.py WK-674`
   prints no row without a resolution. At this tree it lists F41, F43 and F48. F54 is added
   once #830's register pass lands, and must be resolved too.
8. **Every Decision point has its resolver before the slice it blocks starts.** Each
   blocking row in the Decision points table below has a resolver id in its `Resolved by`
   cell before that slice's leaf plan moves to `active`.
9. **The roadmap row names what the spec assigns to WK-674.** Inside the `### WK-674`
   section of `docs/roadmap.md`, `grep -n -E 'FR-437|FR-412|FR-415'` prints at least one
   line for each id. The activation commit makes this true (see **Activation**).
10. **Every slice closes on its own clean audit.** Each of Slices 1 to 6 has its own leaf
    plan filed under `docs/plans/`, with `work: WK-674`. Each slice closes on its own
    item 11, defined in **Tasks** below.
11. **The full gate passes, both halves, on the merged tree of the last slice.** These are
    the `CLAUDE.md` §11 commands, each exiting 0:
    - `uv run ruff check . && uv run mypy && uv run lint-imports && uv run pytest -q`
    - `python3 scripts/audit-docs.py && uv run python scripts/req-coverage.py`
    - `uv run python scripts/generate-contracts.py --check`
    - the five `pnpm --dir frontend` commands, each prefixed with `env -C <worktree>`

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
| `03` §3.10 | FR-270 | Optional date-based routing by the quote's effective date; overlapping ranges are refused (`DEPLOY_DATE_RANGE_OVERLAP`) | 6 (DP-2) |
| `03` §3.10 | FR-271 | Optional shadow scoring: a proportion of live traffic is also scored against a candidate; the results are recorded and never returned | 6 (DP-2) |
| `03` §3.10 | FR-272 | Every deployment, rollback and routing change emits an Audit Event and a notification | 2 (audit), DP-4 (notification) |
| `03` §9 | NFR-494 | Atomic switchover, no dropped or mixed requests, 30 s or less including warm-up | 5 (the F1 test) |
| `03` §9 | NFR-489 | Scoring p99 < 50 ms at 200 rps per replica (< 15 ms without GBM); re-measured on a dedicated host, more than one pass (RL-922) | 5 (DP-3) |
| `03` §9 | NFR-502 | No outbound validation on `/score`; owed a measurement since `CR-927` §6 | 5 |
| `03` §9 | NFR-497 | 99.95 % monthly availability; the degraded read is delivered (register F41) | DP-5 |
| `07` §3.5 | FR-428 | Environment is a first-class object: name, description, promotion order, its own live deployments; `dev → uat → prod` shipped, more configurable | 2 |
| `07` §3.5 | FR-429 | Promotion order enforced: no `prod` without a prior successful `uat`, unless policy permits a recorded skip | 2 (DP-7) |
| `07` §3.5 | FR-430 | Independent SA scopes, rate limits and monitoring configuration per environment; a `uat` key never scores `prod`; one key per granted environment (amended by #830, item E7) | 3 |
| `07` §3.5 | FR-431 | Environment configuration is a Setting, resolved by the §3.8 precedence and audited on change | 3 |
| `07` §3.6 | FR-436 | One tenant per deployment; tenant marker in the database; refuse to start on a mismatch; the same for object storage and the broker | 1 |
| `07` §3.6 | FR-437 | No IdP in the production stack; `deploy/` carries a **reference** Keycloak deployment (the local half is already evidenced) | 4 |
| `07` §3.2 | FR-412 | Resource budget: the **memory** half is armed against a worker the deployed stack runs (FR-415's WK-674 clause) | 4 |
| `07` §3.2 | FR-415 | The Job and the queue are the resource boundary; "arming the memory half and shipping that worker service is WK-674's" | 4 |
| `00` §3 | FR-18 | Every Job records the platform build it ran on; the dossier states it | 1 |

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
  predicts the failure by its cause. The dated §4.2 note goes in with the entry. → Slice 2.
- **RL-888 and RL-916.** A sampled trace carries the environment string as a stand-in for
  its Deployment parent. WK-674's migration reconciles that string to the Deployment that
  actually served the quote. → Slice 2.
- **RL-921 and RL-922.** The architectural question behind NFR-489 is discharged. The
  re-measurement of the requirement stays WK-674's. → Slice 5, and DP-3.
- **`CR-927` §6.** NFR-502 is owed a measurement, with the same owner as NFR-489. → Slice 5.
- **Register F48 (NFR-499 per-client rate limits).** The decision is #830 item E6, quoted
  there as the deputy's words: "a shared Redis counter, per tenant". `rate_limit_rps` is
  persisted today and read by nothing, and `RATE_LIMITED` is raised nowhere. → Slice 3.
- **Register F54.** Key issuance mints a key only for `environments[0]`
  (`backend/src/app/api/service_accounts.py:180` and `:246`). The shape of the fix is `07`
  FR-430's 2026-09-28 amendment (#830 item E7). → Slice 3.
- **Register F41 (NFR-497).** The availability target is carried. → DP-5.

### Cross-module dependencies — `06`, `05`, `00` (swept at this tree)

**`06` — governance.** WK-674 must satisfy:

- the §3.3 evidence row "Deployment to `prod`" (`06:121`);
- FR-364's floor: `deployment` requires `rating_version_approval` and `uat_deployment`
  (`06:290-297`);
- the §4.2 default `deployment` entry: `prod`, 1 approver, role `deployer`;
- FR-368: the Audit Event is written in the same transaction;
- FR-357: withdrawal is refused after the artifact is live, with
  `WITHDRAW_AFTER_DEPLOY_FORBIDDEN`. This needs the deployment state to be queryable;
- FR-382: what was live in each environment over a date range;
- FR-384: blast radius, where the `deployments` field is empty today;
- FR-347: a Service Account never holds a deploy permission (a negative test).

These all attach to Slice 2. FR-382 constrains the Deployment table's shape: it keeps
history rows and is never updated in place.

**`05` — monitoring (WK-687, Phase 3).** WK-674 **feeds** these and builds none of them:

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

| # | Premise | At `6c6f4532` | Status |
|---|---|---|---|
| a | The WK-674 roadmap row lists the whole scope | The `From "Workstreams"` line under `### WK-674` (`docs/roadmap.md:666`) lists FR-267, FR-268, FR-269, FR-270, FR-271, FR-272, FR-428, FR-429, FR-430, FR-431, FR-436, FR-18. It omits FR-437 (`07:153`, "Owned by WK-674"), and FR-412 and FR-415 (`07:104`, "Arming the memory half and shipping that worker service is WK-674's"; again at `07:491`) | **does not reproduce.** Scope follows the spec; the row is corrected at activation |
| b | Deployment and Environment exist in some form | `grep -rlE 'class Deployment' backend/src packages` prints nothing. `class Environment` exists only as the settings enum `backend/src/app/config.py:31` (`local`, `dev`, `uat`, `prod`), not as the FR-428 entity | greenfield |
| c | A tenant marker and a build column exist | `grep -rlE 'tenant_id\|TENANT_ID\|tenant_marker\|platform_version\|build_version' backend/src packages` prints nothing | greenfield |
| d | A deployment path exists for the F1 test | `deploy/docker-compose.yml` runs `postgres`, `redis`, `minio` and `keycloak` (profile-gated) — no `api`, `worker` or `scheduler` service | **does not reproduce**, which is why Slice 4 precedes Slice 5 |
| e | FR-272's "configured channel" is specified somewhere | `05:380` and `06:568` both list notification channels as provided by `07`. No `07` requirement defines one (a grep of `07` for notification, channel and webhook finds only the dependency row `07:433`), and no code sends one (`grep -rliE 'notification\|webhook' backend/src` prints nothing) | **does not reproduce** → DP-4 |
| f | The deploy permission has one name | `06:62` and `06:219` say `rating_version:deploy_prod` and `rating_version:deploy_*`. The code has `deployment:promote` (`packages/model-schema/src/model_schema/permissions.py:54`) | **conflict** → DP-6 |
| g | Promotion order has one home | `07` FR-429 and the OpenAPI stub (`docs/contracts/openapi/gi-pricing.yaml:284-293`, 409 `DEPLOY_REQUIRES_APPROVAL \| PROMOTION_ORDER_VIOLATION`) put it at the deploy route. `06` FR-364's floor puts `uat_deployment` in the evidence check (`EVIDENCE_INCOMPLETE`) | **conflict** → DP-7 |
| h | `03` FR-241's date-routing cross-reference | `03:137` says "unless the deployment explicitly uses date-based routing (FR-247)". FR-247 (`03:153`) is the Premium Ladder, and date routing is FR-270 | stale reference; Slice 6's spec task corrects it, and the Slice 6 leaf plan re-verifies it first |
| i | The F1 RS record and #830's E6/E7 are on main | PR #837 and PR #830 are open drafts (#830 head `3319b34f`) | cited by PR number and item, not by record id; a leaf plan re-reads them at its own tree (`docs/plans/README.md` rule 4) |
| j | A sweep claim that `00` makes the environment set "exactly" `dev`, `uat`, `prod` | `00:166` lists the three and says nothing about exclusivity, so it does not conflict with FR-428's "additional environments are configurable" | not reproduced; no conflict |
| k | Owed register rows | `python3 scripts/register-owed.py WK-674` lists 3: F41, F43, F48. F54's owner moves to WK-674 in #830's register pass | reproduces (3), F54 pending |

### Noted, not WK-674's

The following `07` §3.6 requirements are held by no roadmap row at this tree (`grep` of
`docs/roadmap.md` for each prints nothing): FR-432 (the image set), FR-433 (Helm), FR-434
and NFR-534 (scoring without the compute pool), FR-435 and NFR-531 (migrations and rolling
deploys), FR-438 and NFR-533 (signed images and the SBOM). Slice 4 needs part of FR-432's
compose set (`api`, `worker`) as its deployment path. Which of the rest are WK-674's is a
scope question, and it is **DP-1**.

---

## Decision points

These rows follow the form in `docs/process/document-ids.md` §1.7. Rows of kind *scope* are
the maintainer's, resolved by the deputy under the maintainer's delegation. Rows of kind
*decision point* are the decision-maker's. The planner rules none of them.

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-1 | Which `07` §3.6 packaging requirements are WK-674's? FR-437 says "with the rest of `deploy/` beyond compose", but no roadmap row holds FR-432, FR-433, FR-434, FR-435 or FR-438 | (a) All of §3.6 beyond compose, including the FR-433 Helm chart; (b) the compose `api` and `worker` services (FR-432's part), FR-434 with NFR-534, and FR-437's reference Keycloak in WK-674, with FR-433 Helm, FR-438 and NFR-533 moved to Phase 3; (c) the deployment path only, with every other §3.6 id reassigned | **(b).** The F1 test needs a real multi-replica `api` plus Redis path, and FR-434 is the property that path must have anyway. Helm and signing add no evidence for any Phase 2 requirement, and a chart nobody deploys is an artifact nothing tests | scope | yes — Slice 4 | |
| DP-2 | FR-270 and FR-271 are marked "Optional". Are they built in WK-674 or deferred? | (a) Build both, as Slice 6; (b) build FR-271 (shadow feeds `05`) and defer FR-270 with an owner; (c) defer both, with WK-687 as owner | **(a).** Both are in the roadmap row's id list. "Optional" is a per-environment runtime option, not an optional deliverable. FR-271 is "the pre-deployment safety net feeding 05", and WK-687 cannot compare shadow results that were never recorded | scope | yes — Slice 6 | |
| DP-3 | If NFR-489 still fails on the deployment path, what does the Work record? | (a) The measured verdict FAIL, with the Work closing on a reduced scope as WK-671 did; (b) the verdict plus a proposed NFR-489 amendment, filed as its own spec change with the measurement; (c) hold the close until it passes | **(b).** The requirement has failed at two closes (`CR-927` §4 and §10). A third failure with no proposal repeats a verdict and changes nothing. Never a silent pass | scope | no — resolved at Slice 5's close. Until then, the default is the measured verdict, recorded as is | |
| DP-4 | FR-272's notification "to a configured channel": no `07` requirement specifies a channel (premise e) | (a) A spec change in `07` defining a minimal channel (a webhook through a secret reference), built in Slice 2; (b) WK-674 writes a durable deployment event through the outbox with the Audit Event, and delivery belongs to WK-688 (alerting and routing, Phase 3), with FR-272 amended to say so; (c) WK-674 builds delivery with no spec | **(b).** The retry and failure-surfacing obligations sit in `05` FR-336, which is WK-688's. A channel built now would be the "later phase built ahead" that `CLAUDE.md` §0 forbids. (c) is excluded by `CLAUDE.md` §0 | scope | yes — Slice 2's close (not its start) | |
| DP-5 | NFR-497's 99.95 % monthly availability (register F41): what verdict can WK-674 give before any production month exists? | (a) "Deferred with an owner — WK-687 (operational monitoring)", with the degraded read already delivered; (b) measure a synthetic month on the compose path; (c) keep WK-674 as owner until production | **(a).** A monthly availability target can only be measured by the monitoring that WK-687 builds. A synthetic month measures the harness, not the target | scope | no — resolved at Slice 5's close. Until then the default is (a) | |
| DP-6 | The deploy permission's name: `06:62` and `06:219` say `rating_version:deploy_prod` and `rating_version:deploy_*`, per environment; the code says `deployment:promote` | (a) The spec is right: rename to a per-environment family; (b) the code is right: amend `06` to `deployment:promote`, scoped by the environment of the grant; (c) keep both | Decision-maker's call. Planner's input: FR-430 already scopes credentials per environment, so (b) keeps one permission and one scoping mechanism | decision point | yes — Slice 2 | |
| DP-7 | Promotion order: a route check (`PROMOTION_ORDER_VIOLATION`, FR-429) or an evidence floor (`uat_deployment`, FR-364, `EVIDENCE_INCOMPLETE`)? | (a) Both: the route refuses a `prod` deploy with no successful `uat`, and the approval submission's floor also requires it; (b) the floor only, with the code removed from the stub; (c) the route only, with the floor kind removed | Decision-maker's call. Planner's input: (a) is what the two specs say read together, since the floor gates submission and the route gates the act | decision point | yes — Slice 2 | |

**Slice design, decided here and not a DP.** Slice 4 (the deployment path) runs **before**
Slice 5 (switchover). The deputy's F1 decision measures the acceptance test "on the
deployment path WK-674 builds, not a loopback mirror", and at this tree no such path
exists (premise d). Running Slice 5 first would reproduce F1's own limitation, which the
decision calls inconclusive for exactly that reason. Slice 3 (environment isolation) runs
before Slice 4. The deployment path is then measured with the per-environment keys and the
shared rate-limit counter already in place. A path measured without them would change
shape when they land, and the NFR-489 figure would describe a path that is never shipped.

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

---

## Tasks

At this level, each slice is one task: its scope, its dependency, and an outline of its
gate. The steps are written in its leaf plan. **Item 11 of every slice** is the close
condition in `PL-1070` item 11's form:

> **The deputy's merge acknowledgement is recorded** on the PR before the lead merges, and
> the slice's clean audit is filed. Per `CLAUDE.md` §13 a Slice closes on a clean audit and
> the lead's merge — no maintainer acceptance line is required for this slice, and none is
> to be waited on.

### Task 1 — Slice 1: tenancy and provenance (FR-436, FR-18)

- **Scope.**
  - A tenant identifier in deployment configuration.
  - A single-row marker table, written at first migration and carrying the same
    identifier.
  - A startup check that refuses to start on a mismatch. It is a startup failure, not a
    warning. It covers the database, object storage and the broker wherever their
    configuration is per tenant (FR-436).
  - A platform-build column on the Job row, set at submission, and the dossier's statement
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

### Task 2 — Slice 2: the Environment and Deployment record (FR-267, FR-428, FR-429, FR-272 audit, the carried rulings)

- **Scope.**
  - **The spec change comes first.** It declares the `Deployment` and `Environment` data
    contracts in `03` §4. It adds a `GET` for deployment history, which FR-382 and the
    view at `03:847` need and `03` §5.1 lacks. It adds the audit-action catalogue for
    deployment, rollback, routing change and shadow configuration change (FR-368, NFR-498).
    It applies DP-6 and DP-7. It adds RL-886's `06` §4.2 policy entry with its dated note.
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
- **Depends on:** Slice 1. It is blocked on DP-6 and DP-7, and its close is blocked on DP-4.
- **Gate outline.**
  - Each refusal is tested by its cause:
    - a missing approval gives `DEPLOY_REQUIRES_APPROVAL`;
    - skipping `uat` gives whatever code DP-7 decides;
    - a non-Deployer is refused;
    - a Service Account holding a deploy permission is refused (FR-347);
    - a policy entry that is absent fails as RL-886 describes, by its cause.
  - `generate-contracts.py --check` passes.
  - The ER relationship `Deployment ──< ScoringTrace` holds, and the migration reconciling
    it is tested on existing rows.
  - The full gate.
  - Item 11.

### Task 3 — Slice 3: environment isolation (FR-430, FR-431, register F54, register F48)

- **Scope.**
  - One key per granted environment: creation mints one key per environment, and rotation
    and revocation act on one named environment's key (FR-430 as amended by #830 item E7;
    register F54).
  - A test in which a legitimately issued `dev` key is refused against `uat`. Today the
    refusal branch cannot be reached by a key the platform issued.
  - Environment configuration as a Setting, audited on change (FR-431).
  - NFR-499's per-client limit as a **shared Redis counter, per tenant** (#830 item E6;
    register F48). It reads `rate_limit_rps` and raises `RATE_LIMITED`.
- **Depends on:** Slice 2.
- **Gate outline.**
  - A two-replica test showing that the limit holds across replicas. A limiter kept in one
    process "is not a limit" (register F48), so a single-process test proves nothing here.
  - A negative test showing that the old one-key behaviour fails the new assertion.
  - The full gate.
  - Item 11.

### Task 4 — Slice 4: the deployment path (FR-437 reference, FR-412 memory half, FR-415 worker service, DP-1's packaging set)

- **Scope.**
  - The compose `api` service, runnable as n replicas behind a stated load-balancing
    topology.
  - A `worker` service, to which FR-412's **memory** budget is applied and enforced
    (FR-415's WK-674 clause).
  - `api` serving with the compute pool absent (FR-434 and NFR-534, if DP-1 resolves (b)).
  - The reference Keycloak deployment under `deploy/`, with a README saying the deployer
    operates, patches and is accountable for it (FR-437).
  - A load harness that drives `/score` at 200 rps against n ∈ {2, 4, 8} replicas and
    records the load at the start of each run. Slice 5 reuses it.
- **Depends on:** Slice 3. It is blocked on DP-1.
- **Gate outline.**
  - A test that brings the stack up.
  - A Job over its memory budget terminates with a typed error naming the budget (FR-412),
    proven on a deliberately oversized Job.
  - The harness's dry run on this path, with its output quoted.
  - The full gate.
  - Item 11.

### Task 5 — Slice 5: atomic switchover, rollback and the measurements (FR-268, FR-269, NFR-494, NFR-489, NFR-502)

- **Scope.**
  - The PREPARE/COMMIT push over a Redis channel, per the F1 decision. It is triggered by
    Slice 2's deploy transaction. Each worker hydrates off the event loop and acknowledges,
    then swaps its one `live` reference and acknowledges.
  - `/score` reads `live` once at request start, and every response carries the bundle
    hash.
  - `bundle_slot_capacity` is set, and any value above 1 cites the measurement (RL-882).
  - Rollback is the same operation aimed at a previously deployed version, with no
    re-approval (FR-269).
  - The measurements:
    - the F1 acceptance test, unchanged (Acceptance Standard item 5), filed as a research
      record;
    - NFR-489 and NFR-502 on the dedicated host, more than one pass (item 6);
    - DP-3 and DP-5 are applied at the close.
- **Depends on:** Slice 4's path and harness, and Slice 2's deploy transaction.
- **Gate outline.**
  - The F1 test's 9 or more runs, with loads recorded.
  - The 3 m-n4 drops are explained, or 0 drops are shown at n=4 and n=8.
  - A broken-input proof that a response whose bundle hash differs from `live` fails the
    mixed-bundle assertion.
  - The rollback tested under load.
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
  - Routing and shadow-configuration changes emit Audit Events (FR-272).
- **Depends on:** Slice 5. It is blocked on DP-2.
- **Gate outline.**
  - The overlap refusal tested by its cause.
  - A test showing a shadow result never appears in the caller's response.
  - A latency check showing shadow scoring adds no time to the caller's p99, measured on
    Slice 4's harness.
  - The full gate.
  - Item 11.

---

## Activation

When the deputy accepts this plan by delegation, the activation commit:

1. Sets `status: active` in the front matter. This is permitted only when every blocking
   Decision point row has a resolver id (`document-ids.md` §1.7). Otherwise the plan stays
   `draft`, and the rows still open are named in the acceptance line.
2. Corrects the `From "Workstreams"` line under `### WK-674` in `docs/roadmap.md` (premise
   a), in the same way `PL-1177`'s Task 1 corrected WK-672's. It appends, after the FR-18
   clause: "; and, owned by WK-674 in `07` itself: **FR-437** (the reference identity
   provider, `07:153`), **FR-412**'s memory half and **FR-415**'s worker service (`07:104`)
   — added 2026-09-28 by the map plan `PL-9102`". It also appends the F1 obligation, which
   the F1 decision says is written into the row when the first slice is planned.
3. Adds the six `SL-` rows under `### WK-674`, with ids the lead issues, each `draft`.
4. Regenerates `docs/INDEX.md` in the final commit only.

## Status

- **Acceptance line:** _pending — the deputy's dated line by delegation_

## Self-review

1. **Spec coverage.** Every id in the roadmap row, and every id `07` assigns to WK-674, is
   in the coverage table with a slice or a DP: FR-267, FR-268, FR-269, FR-270, FR-271,
   FR-272, FR-428, FR-429, FR-430, FR-431, FR-436, FR-437, FR-412, FR-415, FR-18, NFR-489,
   NFR-494, NFR-497, NFR-502. The 06 and 05 obligations from the sweep attach to Slice 2,
   Slice 5 or Slice 6, or are named as fed and not built.
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
