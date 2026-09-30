---
id: PL-9920
family: plan
kind: leaf
title: WK-674 Slice 2 — The Environment and Deployment record (FR-267, FR-428, FR-429, FR-272 audit and NFR-498 for deploy): leaf plan
status: draft                  # draft → active → superseded | retired (§1.2a)
created: 2026-09-30
owner: planner
tree: 9f63d0feee524815e7e0c68c99a53ac3f80e6c37
phase: P2
work: WK-674
slice: SL-1256
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1237, RL-1296, RL-1232, RL-1236, RL-1263, RL-880, RL-886, RL-888, RL-916, CR-1212, FD-1197, FD-1281]
---

# WK-674 Slice 2 — The Environment and Deployment record: leaf plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. The executor also binds `spec-change` (Task 1), `contract-schema` and `contract-guard` (Task 2), `python-package` (Tasks 2–6), `python-test` (every task), `fastapi-service` (Tasks 4–6) and `dev-commands` (the gate and the migration), and reads [`README.md`](README.md)'s five unchecked conventions before its first step.

## Goal

Make an **Environment** a real object and a **Deployment** a recorded, audited act: a
Deployer binds an `approved` Rating Version to an Environment, the platform refuses the act
when promotion order, approval, permission or reference type says no, and `/score` then
serves the version that is live in the caller's environment instead of refusing.

**Architecture.** `model-schema` gains the `Environment` and `Deployment` shapes, a skip
field on `ApprovalPolicyEntry`, and one pure promotion-order predicate beside `entry_for`.
The backend gains an `environments` table (seeded `dev → uat → prod`), an append-only
`deployments` table, an environments router and a deployments router, and a nullable
Deployment reference on `scoring_traces`. The deploy route and the `prod` approval
submission both call the one predicate. The route writes its Audit Event in its own
transaction. The switch itself is **not** built here: a Deployment takes effect through
the existing per-request resolution, which Slice 5 replaces (`PL-1237` Task 2).

**Tech Stack:** Pydantic v2, FastAPI, SQLAlchemy 2.x async, Alembic, pytest. **No new
dependency**: this slice touches neither `uv.lock` nor any `pyproject.toml` (see **Write set**).

**Spec:**
- [`../specs/03-rating-engine.md`](../specs/03-rating-engine.md) §3.10 — **FR-267** (`03:195`
  at the tree above), **FR-272** (`03:200`, its Audit Event limb only, as `RL-1252` leaves it);
  §9 **NFR-498** (`03:1154`, the deploy limb only); §5.1 (`03:740`, deployment rows `:766-768`);
  **FR-238** (`03:135`) and **FR-250** (`03:162`), read for the default-live path.
- [`../specs/07-platform.md`](../specs/07-platform.md) §3.5 — **FR-428** (`07:139`), **FR-429**
  (`07:140`, as amended by `RL-1232` DP-7 and by RL-1296); §4.2 `Environment`
  (`07:245-259`); §5.1 (`07:297`, environment rows `:306-307`).
- [`../specs/06-governance.md`](../specs/06-governance.md) — §3.3's "Deployment to `prod`" row
  (`06:121`); **FR-364**'s floor (`06:344-350`); §4.1 (`06:188`); §4.2 (`06:305`, JSON
  `:307-333`, the `deployment` entry `:325-327`); **FR-347** (`06:83`); **FR-357** (`06:98`);
  **FR-368** (`06:154`, read-only: WK-679's).
- [`../specs/00-overview.md`](../specs/00-overview.md) §2 (Deployment, Environment) and §4's ER
  line `Deployment ──< ScoringTrace` (`00:263`).

**What this plan implements.** WK-674's map plan, **PL-1237**, **Task 2 — "Slice 2: the
Environment and Deployment record"** (`PL-1237:768-826` at the tree above), with its carried
obligations (`:362-444`) and the Slice 2 rows of its permission table (`:481-484`). The
slice row is **SL-1256** in `docs/roadmap.md`.

## Status

**Draft**, filed 2026-09-30 against the tree above, under **working id 9920** (the number is
not minted; `doc-id.py next --ref origin/main` is run at this PR's merge turn). The slice row
already exists (**SL-1256**), so this PR cuts no `SL-` row.

**Activation needs, in order:**
1. **OQ-1234 decided** — done by **`RL-1296`** (#935, working id 9901; read at its head
   `75f6ca2ef22f29f95528c6f197345588bbd3803d`, merged to `main` as `65b33479`). *(Revised
   2026-09-30 after the merge: the PR-number citations are replaced by the id throughout, and
   the id is added to `relates:`. #971 C amends its item 3; that pair is the lead's to set at
   #971's mint.)*
2. **DP-S2-1, DP-S2-2, DP-S2-3 and DP-S2-5 below resolved** — all four are, as of this
   revision: DP-S2-1 by #974, DP-S2-2 and DP-S2-3 by #971 A–B, DP-S2-5 disposed by #971 A.6 (head `327e1179`).
   **DP-S2-4 does not block this slice** (the maintainer's entry headed
   `2026-09-30 11:17:35 BST — DATED CORRECTION to my A1 entries (12:0x "pin each route's permission against the spec's declared permission (06/03 §5.1 permission column, or the contract)"); DP-S2-4 routing`).
   *(2026-09-30: DP-S2-2 and DP-S2-3 are ruled by #971, working id 9906, read at its head
   `5fb440fb9b29c335eddb714fa5cea51705e8e0af`, dm-effort-high. #971 was ruled from the lead's
   relay before this plan was pushed; this revision aligns the plan to it at every site class,
   each marked *(#971)*. A later revision applies #971's A.6 at head
   `324ea1659ca1542db4b1e362dc3864da6a476bbb` and #974.)*
3. **The lead's go.**

**Dispatch needs** (the lead's, not activation conditions — listed so the dispatch record
can cite them):
- **#960 (the OQ-1234 roadmap strike) merged before dispatch**, and the dispatch record cites
  it. Set by the maintainer's entry headed
  `2026-09-30 10:07:37 BST — #935 CLEAN noted; DECISION: roadmap strike goes in a follow-up PR`
  (`~/gi-pricing-plan.local/channel/to-lead.md`), first bullet.
- **The RL-1263 write-set check** against every build slice in flight at dispatch (see
  **Write set**), and the contention measurement if this is the first overlap (see **Global
  Constraints**).

## Acceptance Standard

Every command runs in the executor's worktree, over `origin/main...HEAD`. "Red first" means
the failing run is quoted in the ledger with its failing assert line **and the cause the
step predicts**; a failure for any other cause is a plan defect, reported, not worked around.
"Red on broken input" means the guard is green, then deliberately disabled (the named line
deleted or the named call patched to a no-op), the test is shown red with the predicted
cause, and the guard is restored; the ledger quotes both runs.

1. **Spec.** Task 1's edits are made through `spec-change`, before any code that implements
   them, and `python3 scripts/audit-docs.py` exits 0 on the commit. `03` §3.10's FR-267..FR-272
   rows are **not** reworded; each spec change is a dated note or an appended row, section or
   contract. If the executor believes an existing requirement needs rewording, it stops and
   reports.
2. **Contract.** `uv run python scripts/generate-contracts.py --check` exits 0 after
   regeneration. The regenerated schemas under `docs/contracts/schemas/generated/` include
   `environment` and `deployment`, and `approval-policy`'s schema carries the skip field. Each
   new shape is declared once, in `model-schema`, checked by count:
   `git grep -n -E '^class (Environment|Deployment)\b' -- packages backend/src frontend/src`
   prints **exactly three** lines: two in `packages/model-schema/src/model_schema/deployments.py`,
   and the runtime-mode enum `backend/src/app/config.py:32` (`class Environment(enum.StrEnum)`),
   which the pattern also matches. `EnvironmentRow` and `DeploymentRow` do not match (`\b`).
   Any other count fails this item. The contract guard
   (`contract-guard`) passes, quoted.
3. **Migration (FR-417).** One new Alembic revision, whose `down_revision` is the head at
   the executor's tree (`d7e2a9b5c418` at the tree above; re-pointed at merge per RL-1263).
   `uv run alembic upgrade head`, `downgrade -1`, `upgrade head` all exit 0 against a scratch
   database, and `uv run pytest tests/test_repository_invariants.py -q` passes. A migration
   test asserts: the `environments` table holds `dev`, `uat`, `prod` with promotion orders 1,
   2, 3 and `requires_prior_environment` null, `dev`, `uat`; **pre-existing `scoring_traces`
   rows keep their `environment` string and get a null Deployment reference** (there was no
   Deployment to serve them; see DP-S2-1's premise), tested on rows inserted before the
   upgrade (`PL-1237` Task 2 gate: "tested on existing rows").
4. **The refusals, each by its cause, each red first or red on broken input.** In
   `backend/tests/test_deployments.py` and `backend/tests/test_environments.py`, each test
   marked with its requirement:
   - **(FR-267)** a `prod` deployment with no complete approval record → 409
     `DEPLOY_REQUIRES_APPROVAL`;
   - **(FR-267, FR-238)** a Rating Version in `draft` or `review` → refused, naming its
     status; only `approved` deploys;
   - **(G3)** a deploy request naming a `sub_graph` reference, and one naming each other
     non-`rating_version` type in `ARTIFACT_TYPES` (`refs.py:21-31`, parametrised over the
     set minus `rating_version`), is refused with 422 `VALIDATION_FAILED` naming the type,
     **before** any row is read. Red on broken input: with the type check deleted, the
     `sub_graph` case is shown to reach the Rating Version loader;
   - **(FR-429, the one predicate)** a `prod` deployment with no successful `uat` deployment
     and no permitted skip → refused at the route with 409 `PROMOTION_ORDER_VIOLATION`
     **and** at the `prod` approval submission with 422 `EVIDENCE_INCOMPLETE`. A test flips
     the policy's skip field and shows **both** refusals flip together;
   - **(FR-429)** a permitted skip whose reason is empty or whitespace → refused by both;
   - **(FR-429, the blanket skip — condition 1)** the skip field on an **unqualified**
     `deployment` entry (`environment` null), and on a **non-`deployment`** entry, is
     refused by `ApprovalPolicy` validation, so `set_policy` cannot store it. **The fallback
     path**: with a policy holding only an unqualified `deployment` entry, `entry_for("deployment",
     "prod")` falls back to it (`approvals.py:146-162`) and the predicate grants **no** skip,
     so the `prod` deployment without `uat` is refused. Each red on broken input, with the
     validator's check deleted;
   - **(FR-428)** the route enforces order for a configured fourth environment, which the
     `prod`-only floor does not cover (`07:140`, last amended clause);
   - **(FR-267)** a caller without `deployment:promote` → 403 `PERMISSION_DENIED`;
   - **(`CR-1212` item 4; #971 B.5, each red first)** a Deployer assigned only to `uat`
     deploys in `uat` and is refused on `prod` with 403; a workspace-wide Deployer deploys to
     both; **with the handler's `resource=` argument removed**, the `uat`-only Deployer is
     refused in `uat` as well, and the test fails; a Service Account is still refused (FR-347);
   - **(#971 A.4, the FD-1200 class, each red first on broken input)** a deployment request
     whose row lacks either floor item (`rating_version_approval`, or the `uat_deployment`
     predecessor item), or is stripped of it by a fixture, is refused at submission with 422
     `EVIDENCE_INCOMPLETE`, **and** a decision on such a row is refused; with the check
     removed, the fixture is approved and the test fails. An attempted update of a submitted
     request's evidence or pins through the module's functions is refused;
   - **(#971 audit advisory A2; auditor-plans F3, red first)** a generic
     `POST /api/v1/approval-requests` naming `deployment:…` is refused when no row exists,
     when the row is not in `review`, and when a fixture has stripped a floor item from its
     `evidence`; so no approvable deployment request exists without pinned evidence (Task 5
     step 6 gives the reason);
   - **(auditor-plans F4, red first)** a decision on a deployment request that is not in
     `review` is refused by `require_in_review` in the deployment module's
     `apply_approval_decision`, not only by the route;
   - **(auditor-plans F5, red first)** two concurrent deploys naming one approved Deployment
     Request produce **exactly one** Deployment row and one `deployment.created` event; the
     other is refused with 409 `DEPLOY_REQUIRES_APPROVAL`. Red on broken input: with the
     `WHERE status = 'approved'` condition removed, two Deployments are written;
   - **(A3; #971 A.6, each red first)** changing `prod`'s display `name` leaves it gated: a
     deploy to it still requires its approved Deployment Request (with resolution keyed on
     the display name, this test fails); a request to change `prod`'s **slug** is refused
     with 422 `VALIDATION_FAILED` naming the slug as immutable; `set_policy` refuses a
     `deployment` entry naming `prd`, a slug no Environment has, with 422
     `VALIDATION_FAILED`; **retiring an Environment that a policy entry names is refused**
     with 409 naming the entry (this plan's choice, below), until the entry is removed;
   - **(auditor-plans N1–N3, each red first)** `POST /api/v1/environments` refuses a slug
     that does not match `_SLUG` (`refs.py:33`) — a one-character slug and an upper-case
     slug — with 422 `VALIDATION_FAILED` (N2); creating an Environment with the slug of a
     **retired** one is refused, because a slug is never reissued (N1: otherwise an old
     `deployment:<slug>@n` reference would come to mean a different Environment); after
     `uat` is retired, `set_policy` refuses a `deployment` entry naming `uat`, and a Service
     Account key naming `uat` is refused (N3: "an existing Environment slug" means a
     **non-retired** one);
   - **(#971 A.6 at `327e1179`, credentials, each red first)** creating or rotating a Service
     Account key whose `environments` names `prd`, a slug no Environment has, is refused with
     422 `VALIDATION_FAILED` naming it; retiring `uat` while an unrevoked key names it is
     refused with 409, until the key is revoked or its environments are narrowed;
   - **(#971 A.5)** a deploy to an approval-gated target naming no **approved** Deployment
     Request is refused with 409 `DEPLOY_REQUIRES_APPROVAL`; a request whose **pinned**
     predecessor item no longer satisfies FR-429's predicate is refused at the route with 409
     `PROMOTION_ORDER_VIOLATION`;
   - **(FR-347)** a Service Account caller (API key) is refused on the deploy route;
   - **(RL-886)** with a policy that has no `deployment` entry, the `prod` approval submission
     is refused with 422 "No approval policy for this artifact type"
     (`backend/src/app/platform/approvals.py:227-234`), **before** any evidence is read;
   - **(FR-272, NFR-498, `RL-1232` DP-4)** every Deployment row has exactly one Audit Event
     with before/after state, written in the same transaction. Red on broken input: with the
     `audit.record` call patched to a no-op, the test is red because the Deployment committed
     with no event;
   - **(FR-428, `RL-1236` DP-B)** a caller without `admin:manage_environments` creating,
     renaming or retiring an Environment → 403 `PERMISSION_DENIED`;
   - **(FR-357)** withdrawing the approval of a Rating Version that has a Deployment →
     409 `WITHDRAW_AFTER_DEPLOY_FORBIDDEN`, **with liveness derived by the server** (Task 6),
     not taken from the request body;
   - positive controls: a Deployer deploys an approved version to `dev`, then `uat`, then
     (with the `prod` approval) `prod`; a permitted, reasoned skip deploys to `prod`.
5. **The dependency direction (DEP-1, RL-1296 item 4).** The predicate lives in
   `packages/model-schema/src/model_schema/approvals.py`, reads only its arguments, and loads
   nothing. `git grep -n -E 'from app\.(platform|api)\.(deployments|rating)' --
   backend/src/app/platform/approvals.py` prints nothing. (Environments are `07`'s, so PLAT,
   left of GOV in DEP-1's order: `set_policy`'s existence check of #971 A.6 may read them.) (No `lint-imports` contract covers
   modules inside `app`, so this command and the review are the check.)
6. **Default-live scoring (RL-880, register F43 L1).** In `backend/tests/test_score.py`:
   an API-key caller scoped to an environment with a Deployment, posting no
   `rating_version_ref`, is scored against that Deployment's Rating Version; an environment
   with no Deployment still gets 409 `NO_LIVE_RATING_VERSION`; a bearer caller (no
   environment) with no ref gets the same 409. Each red first: before Task 6, the first case
   gets the 409.
7. **The trace link (RL-888, RL-916; DP-S2-1 ruled (a) by #974, working id 9986, head
   `849dce653e2cbb4123d3546d3f8e72bf3dbb155a`).** In `backend/tests/test_traces.py`, each
   red first: a default-live score's sampled trace carries the serving Deployment's id; an
   explicit ref **equal** (type, slug and version) to the live Deployment's Rating Version
   carries that Deployment's id; an explicit ref to a non-live version, or another version of
   the same slug, carries null; an explicit ref in an environment with no live Deployment
   carries null; **the switchover case**: a Deployment recorded between the bundle's
   resolution and the trace write does not relink the trace (the id resolved with the bundle
   is the one written, `03` FR-268); **the completion case** (#974 F1): after
   `complete_pending_trace` deletes and re-inserts the row, the Deployment id is still
   there. The `environment` string is written exactly as today.
8. **The `STALE_OWNER` obligation (the ruling of #942, working id 9856, D1 item 4), on
   whichever branch holds at Task 4's and Task 5's check commits:**
   - **Branch A — #942 has merged:** `06` §4.1's `Check owner` cells for
     `deployment:promote` and `admin:manage_environments` are emptied **in the commit that
     adds their checks** (Task 4 for `admin:manage_environments`, Task 5 for
     `deployment:promote`), and WK-1178's parity test, if merged, passes on that commit.
   - **Branch B — #942 has not merged:** the slice does not touch those cells, and the
     ledger records that #942's mint turn clears them in its own PR. Set by the
     maintainer's entry headed
     `2026-09-30 10:59:49 BST — DECISION: WK-674 S2 vs #942's STALE_OWNER: option (a), placed after the fix pair, with (b) as automatic fallback`.
   The ledger names the branch taken and the `origin/main` SHA it read.
9. **Coverage.** `uv run python scripts/req-coverage.py` lists tests against FR-267, FR-428,
   FR-429, FR-272, NFR-498, FR-347 and FR-357. FR-272's notification limb is recorded as
   *deferred with an owner — WK-688* (`RL-1252`), not claimed.
10. **The gate.** The full two-half gate (`CLAUDE.md` §11) exits 0 on the committed tree,
    with every command's rc, the `N passed` line and `HEAD` quoted in the ledger, against
    main's `N passed`.
11. **Item 11** (`PL-1237` Tasks preamble): before the lead merges, the maintainer's
    **MERGE-ACK**, naming the PR's full head SHA, is recorded in the lead's channel file
    (`~/gi-pricing-plan.local/channel/to-lead.md`), given by the maintainer or on the
    maintainer's behalf, **never posted on the PR**; and the slice's clean audit is filed. A
    Slice closes on a clean audit and the lead's merge (`CLAUDE.md` §13).
12. **The authorisation sweep sees every route (Task 0A — the first build task, before any
    new route).** Source: auditor-922's A1 finding, **MEDIUM**, owner this task (cited as
    prose until it is filed), and the maintainer's entries headed
    `2026-09-30 11:01:50 BST — DECISION: candidate A1 (vacuous authorisation sweep): evidence, severity rule, owner WK-674 S2`,
    `2026-09-30 11:06:50 BST — A1 reproduced: decisions pending switch_workspace; the fix's shape`,
    `2026-09-30 11:08:22 BST — A1 = MEDIUM, conditional on the behavioural switch_workspace confirmation`
    and `2026-09-30 11:09:37 BST — A1 MEDIUM confirmed behaviourally; the condition is met`.
    In `backend/tests/test_api_authorisation_sweep.py`, each red first:
    - **(a) flattened:** the static sweep walks included routers (FastAPI's
      `_IncludedRouter.original_router.routes`, as the finding records it for 0.141.1),
      and asserts the number of `(method, path)` operations it iterated **equals** the number
      of operations in `app.openapi()["paths"]` (137 at the finding's tree). Red first: at the
      tree above it iterates the 2 open routes, so the equality fails naming both counts;
    - **(b) a guard removed is seen:** with `requires()` removed from one real guarded route
      in the test's setup, the static sweep fails naming that route;
    - **(c) moved out of this slice** (the 11:17:35 entry): pinning each route's permission
      against a spec declaration goes to the WK-1178 slice #977 (DP-S2-4 (a), a Permission
      column on every §5.1 row) names, with its red first
      on the `AUDIT_READ → JOB_READ` swap (`backend/src/app/api/audit.py:52`). **This slice's
      new routes** (the environments, deployment-request and deploy routes) get their
      permission declared in that mechanism by **whichever of this slice and that one lands
      second**, and the later one checks the earlier's routes;
    - **(d) the no-roles behavioural sweep asserts 401 or 403, with a valid body per route.**
      A 422 is not a refusal. Red first on `POST /api/v1/me/workspace`, which passes today
      only because an empty body is refused with 422;
    - **(e) a named allow-list, with file:line, of the handler-guarded routes**, each checked
      by the test to still contain its `require_permission(` (or membership refusal) at the
      named site, so the list cannot rot silently: `POST /api/v1/validation-rules`
      (`backend/src/app/platform/validation_rules.py:192` and `:199`); `POST /api/v1/me/workspace`
      (`backend/src/app/api/me.py`, three `WORKSPACE_SCOPE_DENIED` refusals, each cited at
      its code line: `:241`, the malformed `Workspace-Id` header (`UUID(workspace_id)` at
      `:238`, raised at `:240-241`); `:251`, the membership check of the workspace entered
      (`if` at `:249`); `:260`, the membership check of the workspace left (`if` at `:258`) —
      the last two being `00` FR-396 and FR-397's membership check; not the decorator at
      `:215`; **no permission needed**, per the 11:08:22 entry); and, as Task 5
      adds each, **both new handler-guarded routes** — `POST /api/v1/environments/{env}/deployments`
      and `POST /api/v1/environments/{env}/deployment-requests` — each at the line of its
      handler's `require_permission(` (#971 B.2: `deployment:promote` with the Environment as
      the resource, so neither carries `PERMISSION_ATTRIBUTE`; #971 audit advisory A4);
    - **(f) siblings:** every other test iterating `app.routes` the same way is fixed in the
      same task. At the tree above `git grep -n 'app.routes' -- backend/tests` names only
      `test_api_authorisation_sweep.py:189`; the executor re-runs it and fixes each hit;
    - **(g) all routes accounted for:** each of the operations is guarded by a declared
      permission, by a named allow-list entry, or is in `OPEN_BY_DESIGN` /
      `NO_PERMISSION_REQUIRED` (`:28`, `:43`), and the three sets plus the guarded set
      partition the operation count exactly.
13. **Exactly one writer of `approved`, on every approval-capable table** — #971 A.4 as
    restated at head `327e117942c81fe75a07c8eed597af9ce14beaa9` (superseding its versions at
    `fa49e06c` and `324ea165`), on the maintainer's entries headed
    `2026-09-30 11:21:51 BST — status 11:25 noted; three rulings` and
    `2026-09-30 11:22:45 BST — A.4 residual (record_certificate conditionals): steer WIDEN, not baseline`.
    A structural test in `backend/tests/`:
    - **vocabulary declared, population derived:** every mapped class under
      `app.db.models.Base` with a `status` column declares that column's vocabulary as column
      metadata (`info={"status_vocabulary": <the StrEnum>}`); a `status` column with no
      declared vocabulary **fails**. The population is every class whose vocabulary has an
      `APPROVED` member (at the tree above: `ApprovalStatus`, `MetricStatus`, `ModelStatus`,
      `ObjectiveStatus`, `PerilStructureStatus`, `RatingVersionStatus`, and the Deployment
      Request's own). **This slice declares a `StrEnum` for `validation_rules` and
      `validation_rule_sets`**, whose vocabulary is only string constants today
      (`backend/src/app/platform/validation_rules.py:65`), so both join the population rather
      than dropping out. `jobs`, `dataset_versions` and `scoring_traces` have no `APPROVED`
      member, so `jobs.py:226`, `datasets.py:581` and `traces.py:252` are outside it by
      construction;
    - **attribution, or fail closed:** an AST walk over `backend/src` ties each status write
      to a mapped class by a constructor `XRow(..., status=…)`, or by `<name>.status = …`
      where `<name>` is annotated with a mapped class or was bound in the same function from
      `session.get(XRow, …)` or a `select(XRow)` result. A write tied to no class fails. A
      column `default=`/`server_default=` of `"approved"` is a write on its own class;
    - **possible values, evaluated statically:** a string literal; an enum member or its
      `.value`; a module-level name bound to a literal; a conditional (the union of its
      branches); a name annotated with an enum type (all its members); a lookup in a
      module-level dict literal (its values). A write is ignored **iff every value it can
      produce is a non-approved member** of its table's vocabulary — which covers
      `record_certificate` at `platform/metrics.py:459` and `platform/objectives.py:532`.
      Anything else, an unknown value included, is "possibly approved";
    - **the rule:** on a population table every possibly-approved write sits in that table's
      `apply_approval_decision` reached from `_carry_to_the_artifact`
      (`backend/src/app/api/approvals.py:488`, carrying at `:499-517`), or, for
      `approval_requests`, in `_resolve_status` (`platform/approvals.py:547-554`);
    - **red first, five plants, each failing the check:** a second writer of `approved` on the
      deployment-request table; a conditional with an `APPROVED` branch; an unattributable
      status write; a `default="approved"`; a `status` column with no declared vocabulary;
    - **zero writers passes and is reported as a note** (`peril_structures` today);
    - **the baseline: exactly three validation writers**, named, dated 2026-09-30, temporary
      and shrink-only, pinned as a literal citing the validation-rule finding (HIGH, the
      maintainer's entry headed
      `2026-09-30 11:23:26 BST — DECISION: validation-rule approval bypass: HIGH (not CRITICAL); owner and order; two follow-ons`;
      cited as prose until it mints): `approve_rule` (`validation_rules.py:395`, writing at
      `:423`); `seed_builtin_rules` (`:89`, constructing at `:132` with `status=APPROVED` at
      `:154`); `replace_rule_set` (`:538`, constructing at `:621` with `status=APPROVED` at
      `:643`, and the column default `backend/src/app/db/models.py:1195` on the same class).
      That finding's WK-1178 fix slice removes each entry red first, and it is **serialised
      after this slice** (it edits `_carry_to_the_artifact` too). `deployment_requests` has no
      entry.

## Global Constraints

- **Money is integer minor units, or `Decimal` in the rating path** (`CLAUDE.md` §7). This
  slice adds no money field.
- **Nobody hand-writes a shape that exists in `model-schema`** (`CLAUDE.md` §2):
  `Environment`, `Deployment` and the skip record are declared once, there.
- **The Audit Event is written in the same transaction as the change** (`06` FR-368;
  `audit.record` joins the caller's transaction, `backend/src/app/platform/audit.py:52-70`).
- **A Deployment row is never updated in place** (`06` FR-382 needs what was live over a
  date range; `PL-1237:521-523`). A later Deployment supersedes an earlier one by being later.
- **The skip reason is always required when a skip is used, and is not configurable** (RL-1296, item 3).
- **The skip field, `06` §4.2 and the regenerated contract land in one commit** (RL-1296, item 5), never the §4.2 text before the model.
- **Governance imports nothing from the rating module** (`00` DEP-1, `00:469`; DEP-537
  `:471-476`). Deployment facts reach the approval submission through a caller-supplied
  resolver, as `ArtifactResolver` (`backend/src/app/platform/approvals.py:110-127`) and
  `EvidenceAuthorResolver` (`:283-296`) already do.
- **The migration chain has exactly one head** (`07` FR-417).
- **`NO_LIVE_RATING_VERSION` is permanent** (RL-880; `backend/src/app/api/score.py:128-151`):
  the slice narrows its trigger to "no Deployment in this environment, or no environment",
  and does not delete it.
- **Build ahead of the phase is forbidden** (`CLAUDE.md` §9): no Monitor creation (`05`
  FR-310), no notification (FR-272's second limb), no switch (Slice 5), no routing or shadow
  (Slice 6). The deploy transaction leaves the boundary where WK-687's Job submission can be
  added (FR-413's outbox rule; `PL-1237:538-541`).
- **FD 9881 (FR-447) is Slice 3's, not this slice's** — the maintainer's entry headed
  `2026-09-30 10:56:21 BST — #942 (ruling 7 of 7): auditor approved; D3 = RL; dm-effort-high kept through the fix rounds; WK-674 S2 plan`,
  last bullet.
- **RL-1263 concurrency.** This slice runs beside WK-690 Slice 1 (lane B), each holding a
  gate slot. The maintainer's entry headed
  `2026-09-30 10:05:40 BST — ETA read (maintainer "check ETA"); two dispatch reminders`
  sets two conditions: **if this slice's diff touches `uv.lock` or any `pyproject.toml`, it
  serialises behind WK-690 Slice 1's dependency change**, and the dispatch record states the
  `uv.lock` check; and **the first overlap of this slice's gate with WK-690 Slice 1's
  triggers the three-pair contention measurement**, run alone first.

## Scope

### Requirement coverage, each id individually

| Spec section | Id | This slice |
|---|---|---|
| `03` §3.10 | FR-267 | Whole: Deployment binds an `approved` RV to an Environment; who, when, why, bundle hash; Deployer only; `prod` needs the complete approval record |
| `03` §3.10 | FR-272 | The Audit Event limb for **deploy**. Rollback's is Slice 5's; routing and shadow configuration's are Slice 6's (`PL-1237:293`). The notification limb is WK-688's (`RL-1252`) |
| `03` §9 | NFR-498 | The **deploy** limb, riding with FR-272 (`PL-1237:298`) |
| `07` §3.5 | FR-428 | Whole: Environment as a first-class object, seeded `dev → uat → prod`, more configurable, create / rename / retire |
| `07` §3.5 | FR-429 | Whole: both checks on one predicate, with the skip's home as RL-1296 gives it |
| `06` §3.1 | FR-347 | The negative test only (`PL-1237:529-531`); the rest is WK-676's |
| `06` §3.2 | FR-357 | The deployment state it needs, and the server-derived liveness of Task 6; the rest is WK-677's |

**Carried obligations placed here** (`PL-1237:362-444`, each re-read at the tree above):
RL-880 and register F43 limb L1 (Task 6); RL-886 (Task 2); RL-888 and RL-916 (Task 6,
DP-S2-1); `CR-1212` item 4 (Task 1 and Task 2, DP-S2-3); OQ-1234 as RL-1296
decides it (Tasks 1, 2 and 5); **G3** of the ruling of #938 (working id 9851, "WK-674
Slice 2: G3", its §What it obliges) — set on this slice by the maintainer's entry headed
`2026-09-30 10:02:08 BST — DECISION: section-disjoint spec edits under RL-1263; #938 must-checks`,
Must-check A ("Name one owner"); **`STALE_OWNER`** of the ruling of #942 (Acceptance 8).

**Not in this slice**, each with where it goes: FR-268 and FR-269 (and rollback's audit limb)
→ Slice 5. FR-270 and FR-271 → Slice 6. FR-430, FR-431, register F48 and F54 → Slice 3.
FR-453 / FR-272's notification → WK-688. FR-368's general obligation → WK-679. FR-382 and
FR-384 read what this slice writes, and are not built. The Environment's `settings` object
(`07:245-259`, the `settings` key) → Slice 3, gated by `OQ-1235`; this slice's `Environment`
shape omits it, with a dated `07` §4.2 note saying so (Task 1).

**One map-plan deviation, dated 2026-09-30, stated rather than folded in.** `PL-1237` Task 2 says the slice
"declares the `Environment` data contract alongside" the new `03` Deployment contract. At the
tree above `07` §4.2 **already declares `Environment`** (`07:245-259`). Declaring it a
second time in `03` would be a shape defined twice (`CLAUDE.md` §2), so this slice declares
only `Deployment` in `03` and aligns `07` §4.2 by a dated note.
**Recorded as a dated delta to the map plan, in this leaf plan** *(2026-09-30)*. `PL-1237` is
`active` and frozen, so it takes only `status:`, `superseded_by:` and `corrected_by:`
(`document-ids.md` §1.5); a delta note here is the planner's form, as `PL-1239` recorded its
own map-plan deviation. No separate map-plan record is filed. **Agreed** by the maintainer's
entry headed `2026-09-30 11:12:45 BST — #973 (WK-674 S2 plan): (a) agreed; (b) its own FD, plus a class sweep`,
item (a).

### Premises re-derived at the tree above

| # | Premise | Evidence | Status |
|---|---|---|---|
| a | No Environment or Deployment object exists | `git grep -n 'class .*Environment' -- backend/src packages` prints only `backend/src/app/config.py:32` (the runtime-mode enum); `git grep -n -i live_deployments -- packages backend/src docs/specs` prints only `docs/specs/07-platform.md:253` | greenfield |
| b | `DEFAULT_POLICY` has no `deployment` entry; the floor has one | `packages/model-schema/src/model_schema/approvals.py:107` (`"deployment": ("rating_version_approval", "uat_deployment")`); `DEFAULT_POLICY` `:202-261` holds `validation_rule`, `custom_objective`, `custom_metric`, `model`, `peril_structure`, `rating_version` | reproduces RL-886 |
| c | `ApprovalPolicyEntry` is keyed per artifact type and environment, with fallback | `approvals.py:111-122` (`environment: str \| None`, `:119-121`); `entry_for` `:146-162` returns the exact match, then the `environment is None` entry; the only validator is `_separation_of_duties_is_not_configurable` (`:137-144`) | reproduces |
| d | Nothing checks `uat_deployment` | `git grep -n -i uat_deployment -- backend packages` prints only `approvals.py:107` | reproduces |
| e | Neither Slice 2 permission is checked | `git grep -n -E "(Perm\|Permission)\.(DEPLOYMENT_PROMOTE\|ADMIN_MANAGE_ENVIRONMENTS)\b" -- backend/src` exits 1. Declared at `permissions.py:54` and `:69`; `deployer` holds `DEPLOYMENT_PROMOTE` (`:140`), `admin` holds `ADMIN_MANAGE_ENVIRONMENTS` (`:146`) | reproduces (the ruling of #942's evidence 5) |
| f | A grant's scope is one resource, or the workspace | `RoleAssignmentRow.scope_type` / `scope_id` (`backend/src/app/db/models.py:558-608`, constraint `scope_id_iff_scoped` `:599-602`); `rbac._covers` (`backend/src/app/platform/rbac.py:205-217`): a workspace-wide assignment covers every resource; `ScopeType` (`permissions.py:91`) has no `environment` member | the base for DP-S2-3 |
| g | `sub_graph` is a valid reference type, and nothing names a deployment | `ARTIFACT_TYPES` (`packages/model-schema/src/model_schema/refs.py:21-31`) includes `sub_graph` and `rating_version`, and has **no** `deployment`; `REF_PATTERN` is built from it (`:51-53`) | the base for G3 and DP-S2-2 |
| h | An approval request holds no evidence; the owning module's row does | `ApprovalRequestRow` (`models.py:611-655`) has `artifact_ref`, `artifact_type`, `environment` and no evidence column; `rating_versions.submit_for_review` writes `row.evidence` then calls `approvals.submit` (`backend/src/app/platform/rating_versions.py:250-305`); `submit` (`platform/approvals.py:192-280`) checks no evidence, and `EVIDENCE_INCOMPLETE` is raised by owning modules (`rating_versions.py:658-661`) | the base for DP-S2-2 |
| i | `DEPLOY_REQUIRES_APPROVAL` is not registered; `PROMOTION_ORDER_VIOLATION` is | `git grep -n DEPLOY_REQUIRES_APPROVAL -- backend` exits 1; `PROMOTION_ORDER_VIOLATION` at `backend/src/app/errors.py:62`, raised nowhere; `03`'s catalogue names both (`03:771-786`, `:778`) | Task 5 registers the first |
| j | `/score` resolves only an explicit ref | `backend/src/app/api/score.py:128-151` (`_required_ref`, 409 `NO_LIVE_RATING_VERSION`); the ref reaches `resolve_rating_version_ref` in `_fetch_bundle` (`:182`) | reproduces RL-880 |
| k | A trace's environment is a plain string | `ScoringTraceRow` (`models.py:2140`, table `scoring_traces` `:2186`, `environment` `:2199`; docstring `:2151-2152`: "a plain string, not a Deployment FK … Deployment does not exist before WK-674"); the value is `Caller.environment` (`backend/src/app/api/deps.py:66-69`, RL-916), `None` for a bearer caller | reproduces RL-888 / RL-916 |
| l | Withdrawal liveness is supplied by the HTTP client | `Withdraw.artifact_is_live` (`backend/src/app/api/approvals.py:94-98`), passed through at `:288`; `service.withdraw` raises at `platform/approvals.py:452-460` | **a defect Slice 2 closes** (Task 6): a client can assert "not live" |
| m | No environments or deployments router | `ls backend/src/app/api/` has neither; routers are registered at `backend/src/app/main.py:125-147`, `API_PREFIX = "/api/v1"` (`:60`); `requires` at `backend/src/app/api/authz.py:54` | greenfield |
| n | The OpenAPI stub has the deploy path, no `/environments` path | `docs/contracts/openapi/gi-pricing.yaml:284-293`; `grep -c '"/api/v1/environments' docs/contracts/openapi/generated.json` prints 0 | reproduces |
| o | The Alembic head | `d7e2a9b5c418` (`backend/migrations/versions/d7e2a9b5c418_tenant_marker.py`, Slice 1), the one revision no `down_revision` names | reproduces |
| p | `03` §4 ends at §4.10 | `03` §4.1 (`:231`) … §4.10 `ScoreComparison` (`:696`); no Deployment contract | the new contract takes the next free number (see **Write set**) |
| q | `06` §4.1 has no `Check owner` column on main | `grep -c 'Check owner' docs/specs/06-governance.md` prints 0; the column arrives with #942 (head `2df91c8e415284d10999a2e0756d554f8cdd1faf`, its D4) | the base for Acceptance 8's two branches |
| r | Slice 1 is closed | `docs/roadmap.md`, `#### SL-1255`, `status: closed` (#933, #934) | the dependency holds |

The executor re-reads each at its own tree and stops on any that no longer holds
([`README.md`](README.md) convention 4).

### Write set, for the RL-1263 dispatch check

Registry-exempt paths are RL-1263's list as corrected by the maintainer's dated line of
2026-09-29 23:20:11 BST (`RL-1263`, "Registry list, as corrected"). Every other path is
named with the slices that may also touch it.

| Path | What this slice does | Also touched by | RL-1263 |
|---|---|---|---|
| `uv.lock`, any `pyproject.toml` | **nothing** | WK-690 S1 (the sympy pin) | not shared; the dispatch record states `git diff --stat origin/main...HEAD -- uv.lock '*pyproject.toml'` prints nothing |
| `docs/specs/03-rating-engine.md` §3.10 | dated notes under FR-267/FR-272 only | none found | section-disjoint from WK-690 S1 (§3.5 FR-244 only) |
| `docs/specs/03-rating-engine.md` §4 | **a new subsection** (`Deployment`) after the last one | WK-1250 S1 (`PL-1278` Task 1 takes §4.11), WK-674 S6 | **serialises with WK-1250 S1**: two slices taking the next §4 number collide (`PL-1278:175`). The executor takes the next free number **at its merge**, never a number read earlier |
| `docs/specs/03-rating-engine.md` §5.1 | one row appended to the REST table (the deployment-history `GET`, `PL-1237:773-774`) | WK-1250 S1 (four rows), WK-1178 fix slice (**amends the error-code catalogue line**, `03:771-786`) | this slice **does not edit the catalogue lines** (`03:771-786`); a route-table append against a catalogue amendment is not the same definition, decided at dispatch against both diffs (the maintainer's entry headed `2026-09-30 10:24:00 BST — DATED CORRECTION to my 10:15:07 entry (the unpinned-step FD: "It covers the `coalesce(` path as well as `??`")`, last bullet). If the executor finds it must add a code to the catalogue, it stops and reports |
| `docs/specs/06-governance.md` §4.1, §4.2, and the §4.1 scope example | the skip field (§4.2), RL-886's note (§4.2), the environment scope (FR-345, #971 B.4), `Check owner` cells (branch A) | #942 (§4.1, D4), WK-690 S3 (a §4.1 row), WK-1250 S1 (§3.3 under its DP-1) | §4.1 **serialises with #942** unless #942 has merged (then branch A edits two cells of the merged table) |
| `docs/specs/07-platform.md` §4.2, §5.1 | a dated note on `Environment`; rename / retire rows appended | none found | not shared |
| `docs/contracts/schemas/*.json` (hand-authored) | none: #971 A.2 keeps evidence off `ApprovalRequestRow`, so `approval-request.schema.json`'s `evidence_bundle` (`:25-35`) is not touched | none found | **not exempt**; serialises if touched by another slice |
| `packages/model-schema/src/model_schema/approvals.py` | the `deployment` `DEFAULT_POLICY` entry, the skip field and validator, the predicate | WK-673, WK-1250 (if its DP-1 is (a)) — named in RL-1263 item 4 | **serialises** with any in-flight slice editing `EVIDENCE_FLOOR`/`DEFAULT_POLICY` |
| `packages/model-schema/src/model_schema/permissions.py` | `ScopeType.ENVIRONMENT` (#971 B.1) | WK-690 S3 (`custom_objective:author`) | an added enum member is an edit to an existing class: serialises unless the dispatch record shows no shared member |
| `packages/model-schema/src/model_schema/refs.py` | `"deployment"` in `ARTIFACT_TYPES` (#971 A.1) | WK-1250 (`sub_graph` already present) | serialises if another slice edits the set |
| `packages/model-schema/src/model_schema/__init__.py`, `scripts/generate-contracts.py` | exports and slug-map entries for the new shapes | WK-1250 S1, WK-673 S4 (`PL-1278:178-179`) | not on the registry list; serialises unless the dispatch record names the path |
| `backend/src/app/errors.py` | `DEPLOY_REQUIRES_APPROVAL` registered in the rating set | WK-1178 fix slice (new codes, likely) | an added member of an existing frozenset: serialises unless the dispatch record shows the two diffs add different members only |
| `backend/src/app/db/models.py` | `EnvironmentRow`, `DeploymentRow` appended (exempt); **`ScoringTraceRow` gains a column** (an edit to an existing class) | WK-1250 S1 (appends) | the appends are exempt; the `ScoringTraceRow` edit serialises with any slice editing that class |
| `backend/src/app/main.py` | two router registrations | WK-1250 S1 | exempt (append only) |
| `backend/migrations/versions/` | one new revision | WK-1250 S1, WK-690 S1 (none planned) | exempt; re-point `down_revision` at the second merge |
| `backend/src/app/api/score.py` (`_required_ref`, `_fetch_bundle`), `backend/src/app/platform/traces.py` | default-live resolution; the trace's Deployment reference | WK-1250, WK-673, WK-675 S7b (RL-1263 item 4 names `score.py`) | **serialises** with any in-flight slice editing `score.py` |
| `backend/src/app/api/service_accounts.py` (`:63`, `:180`, `:246`) | the Environment-slug check at creation and rotation (#971 A.6) | WK-674 S3 (per-environment keys, register F54: the same lines) | an edit to existing functions: serialises with any in-flight slice editing them; S3 follows this slice anyway |
| `backend/src/app/db/models.py`, every mapped class with a `status` column | `info={"status_vocabulary": …}` on each `status` column (#971 A.4) — **an edit to existing classes** | any slice editing one of those classes | not registry-exempt (only appended classes are); serialises unless the dispatch record shows no other in-flight slice edits those columns |
| `backend/src/app/platform/validation_rules.py` (`:65`) | a `StrEnum` of the validation vocabulary (#971 A.4) | the validation-rule WK-1178 fix slice (serialised after this slice, the 11:23:26 entry) | serialised by that order |
| `backend/src/app/platform/approvals.py` (`set_policy`, `:137-190`) | the existence check of #971 A.6: an entry naming no Environment slug is refused | any slice editing `set_policy` | an edit to an existing function: serialises unless the dispatch record shows no other in-flight slice edits it |
| `backend/src/app/api/approvals.py` (`Withdraw`, `withdraw_request`) | server-derived liveness | none found | not shared |
| `backend/tests/test_api_authorisation_sweep.py` (and any sibling Acceptance 12 (f) finds) | Task 0A: flattening, the count equality, the spec pin, the valid-body sweep, the named allow-list | none found | test-only; **no RL-1263 overlap with WK-690 S1 and no third slot** (the 11:01:50 entry) |
| the five modules' §5.1 REST tables (`01`, `02`, `03`, `06`, `07`) | **nothing in this slice**: Task 0A (c) moved out (the 11:17:35 entry); #977 (a) puts the column in a WK-1178 slice. **If that slice lands first**, this slice fills the column for its own new rows (`03` and `07` §5.1) | WK-1250 S1 (`03` §5.1 rows), WK-1178 fix slice (`03:771-786`), any slice appending §5.1 rows | **serialises** with each: a new column edits every existing row of the table |
| `backend/src/app/api/approvals.py` (`_carry_to_the_artifact`) | one call added, to the deployment module's `apply_approval_decision` (#971 A.4) | any slice adding an approvable type | an edit to an existing function: serialises unless the dispatch record shows the two diffs add different calls only |
| `docs/contracts/schemas/common/artifact-ref.schema.json` | regenerated with `deployment` in the type list (#971 A.1); if the guard shows it is hand-authored, edited to match | WK-1250 | **not exempt** if hand-authored (`RL-1263`, "Registry list, as corrected") |
| new: `backend/src/app/api/environments.py`, `backend/src/app/api/deployments.py`, `backend/src/app/platform/environments.py`, `backend/src/app/platform/deployments.py`, their tests | created | — | not shared |

### Decision points

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-S2-1 | When a quote is scored with an **explicit** `rating_version_ref`, which Deployment does its sampled trace reference? `00`'s ER line makes every trace a child of a Deployment (`00:263`); RL-916 made the environment string reconcilable to "the Deployment that actually served the quote"; an explicit ref may name a version that is not live anywhere | (a) The environment's live Deployment if its Rating Version equals the ref, else null; (b) always null for an explicit ref; (c) refuse an explicit ref outside `local`, so every served quote has a Deployment | **(a).** It records the truth in both cases: a quote served by the live version is attributable to its Deployment, and a what-if quote against another version is not pretended to be. (c) breaks every caller that pins a version today (RL-880 made the explicit ref the only path until now). Pre-existing rows get null under every option: no Deployment existed to serve them | decision point | yes — Task 6 | **#974 (working id 9986, head `849dce65`, the decision-maker at medium effort) — (a)**: the live Deployment only if it serves exactly the ref's Rating Version (type, slug, version), else null; resolved once with the bundle and never re-read; the `environment` string unchanged, the link additive |
| DP-S2-2 | **What does a `deployment` approval request name, and where is its evidence pinned?** The policy and the floor are keyed `deployment` (premise b) and `submit` looks up `entry_for(artifact_ref.type, environment)` (`platform/approvals.py:227`), but no `ArtifactRef` can name a deployment (premise g), and an approval request holds no evidence (premise h). RL-1296 (item 3) puts the skip reason in "the predecessor-deployment evidence item of that request", which therefore has no home yet | (a) Add `deployment` to `ARTIFACT_TYPES`; the rating module creates a **deployment request** row (Rating Version, target environment, the pinned evidence: the RV's approval request id, and the `uat` Deployment id **or** the skip record), and submits it through the unchanged `approvals.submit`, as every other owning module does; the Deployment row that the route writes references the approved request; (b) the request names the **Rating Version** ref with `environment="prod"`, and `approvals.submit` gains a policy-key override (`"deployment"`); evidence is held in a new table keyed by request id; (c) give `ApprovalRequestRow` an evidence column (the `06` §4.3 `evidence_bundle` made real) for every artifact type | **(a).** It is the existing pattern (premise h): the owning module holds and pins the evidence, governance reads the policy by the reference's type, and `submit`'s signature does not change. (b) makes governance's lookup key differ from the thing approved, and the open-request uniqueness constraint (`uq_approval_requests_open_artifact`, `models.py:645`) would then collide an RV's own review with its deployment review. (c) changes every module's evidence path, which is wider than this slice | decision point | yes — Tasks 1, 2, 3 and 5 | **#971 (working id 9906) A — (a)**: a Deployment Request row owned by the deployment module, `deployment` in `ARTIFACT_TYPES`, evidence pinned on the row at submission, the deploy route executing only an approved request and re-evaluating FR-429 from the pinned evidence. #971 C amends the OQ-1234 ruling's item 3: the skip record is pinned on the Deployment Request row |
| DP-S2-3 | **The shape of `CR-1212` item 4's environment scope on `deployment:promote`.** The test is fixed ("a Deployer whose grant names only `uat` is refused on `prod`", `PL-1237:810-811`); the mechanism is not. A grant's scope today is one resource or the workspace (premise f) | (a) Add `ScopeType.ENVIRONMENT`, with `scope_id` the Environment's id; the deploy route checks `deployment:promote` against `ResourceRef(ENVIRONMENT, env.id)`, so `_covers` is reused unchanged and a workspace-wide Deployer still covers every environment; (b) as (a), but `deployment:promote` is honoured **only** through an environment-scoped grant, so a workspace-wide Deployer deploys nowhere; (c) a list of environment names on the assignment | **(a).** It reuses the one scope mechanism and its one check (`rbac.py:205-217`), keeps today's workspace-wide Deployer working, and satisfies the test. (b) is stricter and makes every existing grant useless at once. (c) adds a second scope mechanism beside `scope_type` | decision point | yes — Tasks 1, 2 and 5 | **#971 (working id 9906) B — (a)**: `ScopeType.ENVIRONMENT`, checked **in the handler** with `resource=ResourceRef(ScopeType.ENVIRONMENT, <environment id>)`, never by a bare `requires(Permission.DEPLOYMENT_PROMOTE)`; `06` FR-345 gains "or Environments" in the spec-first commit |
| DP-S2-4 | **Where is "the spec's declared permission" for a route?** Acceptance 12 (c) must pin each route's permission against the spec, never a hand-written map (the 11:06:50 entry). At the tree above **no spec declares one per route**: every module's §5.1 REST table has the columns `Method \| Path \| Purpose` only (`01`, `02`, `03`, `06`, `07`), and `docs/contracts/openapi/generated.json` carries no `x-` extension at all (`grep -o '"x-[a-z-]*"' docs/contracts/openapi/generated.json` prints nothing) | (a) A `Permission` column on each module spec's §5.1 REST table, filled for every route (the spec is where a route is declared), and a parser in the test; (b) a routes cell on each Built row of `06` §4.1's permission table (#942's D4), one place beside the catalogue WK-1178 checks; (c) an `x-permission` extension emitted into the generated OpenAPI from `requires()` | **(a).** The route's row is the one place a reader looks for what a route requires, and a missing cell is visible there. (b) puts routes into a permission catalogue whose rows are keyed by permission, so a route guarded by two permissions or none has no natural row, and it couples this task to #942's table. (c) is circular: the "spec" would be generated from the code under test, so the `AUDIT_READ → JOB_READ` swap would change both sides and stay green. **Cost of (a):** a spec edit to five modules' §5.1 tables, which serialises with every in-flight slice appending §5.1 rows (**Write set**) | decision point | **no** — Task 0A (c) moved out of this slice (the 11:17:35 entry) | **#977 (working id 9907, head `070a83fe`, dm-effort-high) — (a)**: a Permission column on all 152 §5.1 rows, carried by a WK-1178 slice **serialised with this one**; this slice's new routes are declared by whichever of the two lands second, and the later checks the earlier's |
| DP-S2-5 | **The policy is keyed by environment *name*, and FR-428 lets an Environment be renamed** (#971 audit advisory A3). `ApprovalPolicy.entry_for(artifact_type, environment)` matches a string (`packages/model-schema/src/model_schema/approvals.py:146-162`) and `ApprovalRequestRow.environment` is `String(32)` (`backend/src/app/db/models.py:627`). #971 A.1 pins the Environment's identity on the request row but not on the policy key, so renaming `prod` would leave the `prod` entry matching nothing, and by #971 A.5 a target with no entry needs no request: a rename makes a gated target look ungated | (a) Key the policy by Environment identity, and refuse a rename that would change any entry's resolution; (b) refuse any rename of an Environment named by a policy entry; (c) re-key the policy's entries in the rename's transaction | **(a)**, the maintainer's steer (the 11:14:48 entry, last bullet). It closes the hole at its cause, since the key stops being renamable. (b) leaves the key renamable and relies on every rename path remembering the check. (c) edits governance's policy from `07`'s rename route, a second writer of the policy beside `set_policy` | decision point | yes — Tasks 2, 4 and 5 | **Disposed by #971 A.6 (head `327e1179`: "This item disposes of the leaf plan's DP-S2-5") — an immutable Environment slug**: policy, `ApprovalRequestRow.environment`, `{env}` and every reference key on the slug; FR-428's rename changes the display name only; a slug change is refused; `set_policy` refuses an entry naming no existing slug. Retiring a policy-named Environment is left to this plan (refused, **Decided in this plan**; #971 A.6 at `327e1179` confirms both this and the request slug) |

**Decided in this plan, as slice design, not decision points** (RL-1296 leaves
them to "Slice 2", its "Not ruled here"):
- **The skip field's name**: `skippable_predecessors: tuple[str, ...] = ()` on
  `ApprovalPolicyEntry` — the environment names whose deployment a deployment into this
  entry's environment may skip.
- **The skip record's shape**: `PromotionSkip(skipped_environment: str, reason: str)`, frozen,
  `extra="forbid"`, `reason` refused when empty after `strip()`. It is pinned on the
  Deployment Request row (#971 A.2, and #971 C's amendment of the OQ-1234 ruling's item 3).
- **Environment scope**: an Environment is a **deployment-wide** (tenant) object, not a
  workspace one — **confirmed by #971 A.6 at `327e1179`** ("Environments are
  deployment-wide, not per workspace"; its earlier "the workspace's Environments" was loose
  wording, not a design difference). `07` §4.2 has no workspace field (`07:245-259`), API keys carry environment
  names with no workspace (`models.py:430`), and ADR-710 makes the deployment the tenant
  boundary. A Deployment row carries the `workspace_id` of its Rating Version, so "live in
  environment E" is read per workspace.
- **Predecessor**: the Environment's `requires_prior_environment` (`07:252`), as the §4.2
  contract already declares it, seeded `null`, `dev`, `uat`.
- **Environment slug and display name** (#971 A.6): every Environment has an **immutable
  `slug`** (`_SLUG`'s grammar, `refs.py:33`) and a mutable display `name`. The seeds are slugs
  `dev`, `uat`, `prod`. The policy's `environment`, `ApprovalRequestRow.environment`, every
  `{env}` path parameter and every Environment reference name the slug; FR-428's rename
  changes the `name` only. **A slug is never reissued**: a retired Environment keeps its
  row and its slug (auditor-plans N1), and "an existing Environment" means a non-retired one
  wherever it is checked (N3).
- **The Deployment Request slug scheme** (#971 A.1 leaves it to this plan, "the slug must not
  be a renamable name"): **the target Environment's slug**, e.g. `deployment:prod@3` — the
  third request into `prod`. *(Revised 2026-09-30: the first draft used the Environment's id
  in hex because the name was renamable; #971 A.6 makes the slug immutable, so the readable
  form now meets the same constraint.)* ID-2's "monotone per parent" reads as per
  Environment. The Environment is pinned on the row by its id as well, and the Rating Version
  is pinned on the row, not in the slug.
- **Retiring an Environment that a policy entry names** (#971 A.6 leaves it to this plan):
  **refused**, with 409 naming the entry, until `set_policy` removes it. Otherwise the policy
  would hold an entry for an Environment that no longer resolves, which is the silent
  ungating #971 A.6 exists to prevent.
- **Who may submit a deployment request**: the same handler check as the deploy itself,
  `deployment:promote` with the target Environment as the resource (#971 B.2). Submitting is
  the Deployer's act of asking to deploy.

---

## Tasks

### Task 0: Preconditions

- [ ] `pwd` is the executor's worktree; `git branch --show-current` is the slice branch.
- [ ] `uv sync --all-packages` (a fresh worktree without it reports hundreds of phantom mypy
  errors — `dev-commands`).
- [ ] Confirm, naming the `origin/main` SHA read: `RL-1296` is on `main`; #960 is merged; #971 is merged and minted; #974 is merged and minted. **Stop if any does not hold.**
- [ ] Record whether #942 has merged (`grep -c 'Check owner' docs/specs/06-governance.md` at
  `origin/main`), which fixes Acceptance 8's branch **for now**; re-check at Tasks 4 and 5.
- [ ] Re-derive premises a–r; record the tree and each result in the ledger.
- [ ] Run the **Write set** check against every build slice in flight (`gh pr list --state
  open`, and the lead's `eta.md` "In flight"), and read anything that rules on FR-267,
  FR-428, FR-429, the approval policy, `ScopeType` or `score.py`. Name the SHA read.
- [ ] Create the slice ledger (`LG-`, the executor's; `document-ids.md` §1.6), with a working
  id.

### Task 0A: The authorisation sweep sees every route — first, before any new route

**Files:** Modify `backend/tests/test_api_authorisation_sweep.py` (`_operations` `:68-76`,
`test_every_operation_refuses_a_caller_holding_no_roles` `:103`,
`test_every_operation_declares_the_permission_it_enforces` `:175-202`,
`test_the_sweep_covers_the_whole_published_surface` `:205-211`); each sibling Acceptance 12 (f)
finds. **Step (c) is not in this slice** (the 11:17:35 entry); nothing here waits on DP-S2-4.

**Interfaces — Produces** (a test-module helper; later tasks' routes are checked by it):
```python
def _flattened_routes(routes: Sequence[BaseRoute]) -> Iterator[APIRoute]:
    # Every APIRoute, descending into included routers (the A1 finding's shape).
    ...

HANDLER_GUARDED: Final[dict[tuple[str, str], tuple[str, int]]]
    # (METHOD, path) -> (file, line) of the handler's require_permission( / membership check
```

- [ ] **Red first, (a):** replace the `api_client.app.routes` loop at `:189` with
  `_flattened_routes(...)` **only after** adding the equality assert between the iterated
  operation count and `len(_operations(...))` without `OPEN_BY_DESIGN` filtering — first run
  the equality against the unchanged loop and quote the red (2 iterated against the OpenAPI
  count). Predicted cause: the loop does not descend into `_IncludedRouter`. A red for any
  other cause is a plan defect. Before relying on `original_router`, confirm the attribute
  name at the installed FastAPI (`uv run python -c "import fastapi; print(fastapi.__version__)"`
  and a one-line probe), and name what the probe printed in the ledger.
- [ ] **Red first, (b):** in the test's setup, build the app with `requires()` removed from
  one real guarded route (monkeypatch its `dependant`), and show the static sweep fails naming
  it. Restore.
- [ ] **(e):** the named allow-list `HANDLER_GUARDED`, with the two routes and their file:line
  from Acceptance 12 (e). A companion assert reads each named file and line and fails if it no
  longer holds `require_permission(` (or, for `me.py`, the `WORKSPACE_SCOPE_DENIED` refusal).
  The static sweep treats an allow-listed route as guarded; nothing else is skipped.
- [ ] **Red first, (d):** the no-roles behavioural sweep builds a **valid** body for each
  operation from its schema in `app.openapi()`, and fills **every required path and query
  parameter** from that parameter's own schema (not `_concrete`'s blanket UUID, `:78-90`,
  which a slug-typed parameter would refuse with 422). The builder covers, for required
  properties only: `$ref` resolved; enums → the first member; **`format`** → `uuid` a fresh
  UUID7, `date` `2026-01-01`, `date-time` `2026-01-01T00:00:00Z`; **`anyOf`/`oneOf`** → the
  first branch it can satisfy; **`allOf`** → the branches merged; `pattern` → a value from
  the schema's `examples` when present; strings → a `minLength`-long filler; numbers →
  `minimum` or 1. (auditor-plans counted, at the tree above, 38 `format: uuid` nodes, 116
  `anyOf`/`oneOf`/`allOf` nodes and 59 UUID path parameters; without these the unsatisfiable
  list would hold most routes.) The sweep asserts 401 or 403 exactly. An operation whose schema the builder cannot satisfy is
  named in a constant with its reason, and that constant's size is asserted, so it cannot
  grow silently. Red first: `POST /api/v1/me/workspace` with a valid body — its
  `workspace_id` is `format: uuid`, filled with a workspace the caller is not a member of —
  where the current sweep passes it only on 422.
- [ ] **(f), (g):** fix each sibling; assert the partition of Acceptance 12 (g).
- [ ] Green; quote the iterated count and the OpenAPI count in the ledger. Commit:
  `test(api): the authorisation sweep flattens included routers and pins every route (A1, WK-674 S2)`.

### Task 1: Spec — `03`, `07`, `06`

**Files:** Modify `docs/specs/03-rating-engine.md` (§3.10 notes, a new §4 subsection, one
§5.1 row), `docs/specs/07-platform.md` (§4.2 note, §5.1 rows), `docs/specs/06-governance.md`
(FR-345 and the §4.1 scope example, #971 B.4; §4.2 RL-886 note). **Not** the skip field — it lands in
Task 2's commit (RL-1296, item 5).

- [ ] `03` §4: a new subsection **`Deployment`**, numbered the next free §4 number at the
  executor's tree, after the last. It gives the shape (id, workspace, environment, Rating
  Version ref, bundle hash, deployed by, deployed at, reason, the approval request it rests
  on: the executed Deployment Request, #971 A.5), the invariants (append-only, never updated in place; `approved` versions
  only, FR-238; a `sub_graph` or any non-`rating_version` reference is refused, G3), an
  example, and the audit actions this Work emits: `deployment.created` (this slice),
  `deployment.rolled_back` (Slice 5), `deployment.routing_changed` and
  `deployment.shadow_configured` (Slice 6), each named here once so Slices 5 and 6 append
  nothing to the catalogue.
- [ ] `03` §5.1: append `| GET | /api/v1/environments/{env}/deployments | Deployment history for an environment (FR-267; read by `06` FR-382) |`. Do not touch `03:771-786`.
- [ ] `03` §3.10: a dated note after FR-267 naming the new contract and this slice, and after
  FR-272 naming the Audit Event limb's delivery for deploy.
- [ ] `07` §4.2: a dated note after the `Environment` example: `live_deployments` is derived
  from Deployment rows (never stored twice), `settings` lands in Slice 3 (`OQ-1235`), and
  `requires_prior_environment` is FR-429's predecessor.
- [ ] `07` §5.1: append `| PATCH | /api/v1/environments/{slug} | Change an environment's display name or description; the slug is immutable (`admin:manage_environments`) |` and `| POST | /api/v1/environments/{slug}/retire | Retire an environment that has no live Deployment and that no policy entry names |`. `07` §4.2's `Environment` gains `slug` beside `name`, in a dated note citing #971 A.6.
- [ ] `06` FR-345: its list of scopes gains "or Environments", dated, citing #971 (by id
  once minted) and `CR-1212` item 4 (#971 B.4); the scope kind is the `ScopeType` value
  `environment`, which Task 2 adds to the enum (so the contract regenerates there). `06` §4.1's assignment example may show an
  `environments` scope, with a dated note citing `RL-1232` DP-6 as amended.
- [ ] Wherever `ARTIFACT_TYPES`' list is stated as a spec (`refs.py:18-19` names it a spec
  change, #971 A.1): `deployment` joins it, with the Deployment Request's meaning and its slug
  scheme (**Decided in this plan**).
- [ ] `06` §4.2: a dated note after the JSON: the `deployment` entry is now in
  `DEFAULT_POLICY` (RL-886).
- [ ] `03`'s new §4 subsection also declares the **Deployment Request** (#971 A.1–A.2): its
  reference form `deployment:<environment slug>@<n>`, the pinned Rating Version and
  Environment identity, the two pinned evidence items (`rating_version_approval`: the
  decided approval request of the pinned version; `uat_deployment`: the predecessor
  Deployment's id **or** a `PromotionSkip`), written once at submission and never updated
  (FR-356, `00` FR-4). `03` §5.1 also gains
  `| POST | /api/v1/environments/{env}/deployment-requests | Submit a deployment request for approval (FR-267, FR-429) |`.
- [ ] `python3 scripts/audit-docs.py`; quote the rc. Commit:
  `docs(specs): 03 Deployment contract, 07 Environment note and routes, 06 scope and RL-886 note (WK-674 S2)`.

### Task 2: `model-schema` — shapes, the policy entry, the skip field and the predicate

**Files:** Create `packages/model-schema/src/model_schema/deployments.py` (`Environment`,
`Deployment`); modify `approvals.py` (`ApprovalPolicyEntry`, `DEFAULT_POLICY`, the predicate),
`permissions.py` (`ScopeType.ENVIRONMENT`, #971 B.1), `refs.py` (`"deployment"` in
`ARTIFACT_TYPES`, #971 A.1), `__init__.py`;
`scripts/generate-contracts.py` (slug map); `docs/specs/06-governance.md` §4.2 (the skip
field — **this commit**); regenerate `docs/contracts/`; tests under
`packages/model-schema/tests/`.

**Interfaces — Produces:**
```python
class PromotionSkip(BaseModel):          # frozen, extra="forbid"
    skipped_environment: str
    reason: str                           # refused when reason.strip() == ""

class ApprovalPolicyEntry(BaseModel):     # existing; one field added
    skippable_predecessors: tuple[str, ...] = ()

def promotion_order_refusal(
    entry: ApprovalPolicyEntry | None,
    *,
    target: str,
    predecessor: str | None,
    predecessor_deployed: bool,
    skip: PromotionSkip | None,
) -> str | None:
    """None when the order is satisfied; otherwise why not. Reads only its arguments."""
```

- [ ] **First commit — the `deployment` `DEFAULT_POLICY` entry (RL-886).** Red first: a test
  that `DEFAULT_POLICY.entry_for("deployment", "prod")` is not `None`. Predicted failure: it
  returns `None` (premise b). Add the entry exactly as `06:325-327` shows it (`prod`, 1
  approver, role `deployer`, evidence the two floor kinds). Commit.
- [ ] **Second commit — the skip field, its validator, `06` §4.2 and the contract, together
  (RL-1296, item 5).**
  - Red first, in `packages/model-schema/tests/test_approvals.py` (append; mirror its
    existing tests): an `ApprovalPolicy` whose entry sets `skippable_predecessors` with
    `environment=None`, and one with `artifact_type="rating_version"`, each raise
    `ValidationError` naming the field. Predicted failure: `extra="forbid"` rejects the
    unknown field — a different error is a plan defect. After adding the field, the
    predicted red becomes "no error raised"; quote both.
  - Add the field and an `@model_validator(mode="after")` on `ApprovalPolicyEntry` refusing
    a non-empty value unless `artifact_type == "deployment"` and `environment is not None`.
  - `06` §4.2: add `"skippable_predecessors": []` to the `prod` `deployment` entry and a
    dated note citing `RL-1296`.
  - Regenerate contracts; `generate-contracts.py --check` exits 0; commit all of it at once.
- [ ] **The predicate**, red first over a table of cases (the one predicate every caller
  uses: the route, the request's submission, and the route's re-evaluation from pinned
  evidence, #971 A.5): satisfied when the target has no
  predecessor, or the predecessor is deployed; otherwise satisfied only when `skip` names
  the predecessor, `skip.reason.strip()` is non-empty, and `entry` is not `None`, **names the
  target (`entry.environment == target`)**, and lists the predecessor in
  `skippable_predecessors`. The target check is hardening (auditor-plans F8): the fallback's
  no-skip then rests on the predicate as well as on the validator, so an unqualified entry
  that somehow carried the field still grants nothing. Red first: an unqualified entry
  constructed with `model_construct` (bypassing the validator) and carrying the field grants
  no skip. Every other case returns a reason naming the
  target and the predecessor. Add `PromotionSkip` and the function to `approvals.py`.
- [ ] `Environment`, `Deployment` and `DeploymentRequest` shapes in `deployments.py`,
  matching Task 1's contract and `07` §4.2 (without `settings`). `ScopeType.ENVIRONMENT`
  (#971 B.1); `"deployment"` in `ARTIFACT_TYPES` (#971 A.1), with
  `docs/contracts/schemas/common/artifact-ref.schema.json` regenerated. Export, register the slugs, regenerate, run the
  contract guard, quote its result. Commit.

### Task 3: The migration

**Files:** Create one revision under `backend/migrations/versions/`; modify
`backend/src/app/db/models.py` (append `EnvironmentRow`, `DeploymentRequestRow`,
`DeploymentRow`; add the nullable `deployment_id` to `ScoringTraceRow`); test
`backend/tests/test_migration_deployments.py`.

- [ ] Red first: the Acceptance 3 migration test, on a scratch database upgraded to
  `d7e2a9b5c418` (mirror `scratch_database` and `_upgrade(cfg, revision)` in
  `backend/tests/test_migration_dataset_owner.py`; do not invent new fixtures), with two
  `scoring_traces` rows inserted before the upgrade. Predicted failure: the `environments`
  table does not exist.
- [ ] The revision: `environments` (UUID id, immutable `slug` unique across **all** rows, retired included (N1), display `name`, description, `promotion_order`,
  `requires_prior_environment` nullable, `retired_at` nullable), seeded `dev`/`uat`/`prod`;
  `deployments` (UUID id, `workspace_id`, `environment_id` FK, `rating_version_ref`, `bundle_hash`,
  `deployed_by`, `deployed_at`, `reason`, and the Deployment Request id it executed, nullable
  for a target with no `deployment` policy entry, #971 A.5), with no update path in the
  application; `deployment_requests` (UUID id, `workspace_id`, `slug`, `version`, unique
  `(workspace_id, slug, version)`, `environment_id` FK, `rating_version_ref`, `status`
  (`draft`/`review`/`approved`/`rejected`/`withdrawn`/`executed`), `approval_request_id`,
  `evidence` JSONB written once — #971 A.4 permits a database trigger to refuse an update;
  if the executor adds one, its test is red first too); `scoring_traces.deployment_id` nullable FK. Downgrade drops
  all three in reverse.
- [ ] **Declare every `status` column's vocabulary (#971 A.4 at `327e1179`)**: add
  `info={"status_vocabulary": <StrEnum>}` to each mapped class's `status` column in
  `backend/src/app/db/models.py` (metadata only, no schema change, so no migration), and a
  `StrEnum` for the validation vocabulary beside `validation_rules.py:65`'s constants, used by
  `validation_rules` and `validation_rule_sets`. Acceptance 13's test lands in Task 5 with the
  Deployment Request's writer, and its "no declared vocabulary" plant is red first here.
- [ ] Round trip (`upgrade`, `downgrade -1`, `upgrade`) and `tests/test_repository_invariants.py`;
  quote each rc. Commit.

### Task 4: Environments — the entity and its routes (FR-428)

**Files:** Create `backend/src/app/platform/environments.py`, `backend/src/app/api/environments.py`;
modify `backend/src/app/main.py` (one registration); test `backend/tests/test_environments.py`.

- [ ] Red first: the Acceptance 4 `admin:manage_environments` refusals and a positive
  create / rename / retire by an Admin. Predicted failure: 404 on `/api/v1/environments`
  (no router) — the ledger quotes it; after the router exists without the check, the
  predicted red is "the non-Admin call succeeds".
- [ ] **The slug and the rename (#971 A.6)**, red first on Acceptance 4's A3 cases: `PATCH
  /api/v1/environments/{slug}` changes `name` and `description` only, and a body naming a
  different `slug` is refused; `POST /api/v1/environments/{slug}/retire` is refused while a
  policy entry names the slug. `set_policy` (`backend/src/app/platform/approvals.py:137-190`)
  refuses a `deployment` entry whose `environment` is not an existing Environment slug,
  reading the environments platform module (permitted by DEP-1, Acceptance 5).
- [ ] **Slug validity and permanence (auditor-plans N1, N2).** `POST /api/v1/environments`
  validates the new `slug` with `model-schema`'s `Slug` type (`refs.py:41`, built from
  `_SLUG` at `:33`), never a second copy of the pattern. A retired Environment keeps its row
  (`retired_at` set) and its slug, and the `environments` table's unique constraint on `slug`
  covers retired rows, so a slug is never reissued. Red first: Acceptance 4's N1 and N2 cases.
- [ ] **"Existing" means non-retired (N3).** The existence checks of `set_policy` and of the
  credential step below both read `retired_at IS NULL`. Red first: Acceptance 4's N3 cases.
- [ ] **Credentials name only existing Environments (#971 A.6 at `327e1179`).** In
  `backend/src/app/api/service_accounts.py`, each name in `environments` (`:63`, a free
  `list[str]` today) is checked against the Environment slugs at creation and at rotation —
  the two places a key is minted from `environments[0]` (`:180`, `:246`) — and refused with
  422 `VALIDATION_FAILED` naming it. Red first: a key for `prd` is refused.
- [ ] `GET`/`POST /api/v1/environments`, `PATCH /api/v1/environments/{slug}`,
  `POST /api/v1/environments/{slug}/retire` (refused while any Deployment in it is live, while
  a policy entry names it, or while an unrevoked Service Account key names it),
  each writing its Audit Event; the three writes use
  `Depends(requires(Permission.ADMIN_MANAGE_ENVIRONMENTS))`.
- [ ] **Acceptance 8, this permission:** re-check `origin/main` for #942. Branch A: empty the
  `admin:manage_environments` `Check owner` cell in `06` §4.1 **in this commit**. Branch B:
  do not touch it; note it in the ledger.
- [ ] Green; commit.

### Task 5: The deploy route and the `prod` approval (FR-267, FR-429, FR-272, NFR-498, G3, FR-347)

**Files:** Create `backend/src/app/platform/deployments.py`, `backend/src/app/api/deployments.py`;
modify `backend/src/app/main.py` (one registration), `backend/src/app/errors.py`
(`DEPLOY_REQUIRES_APPROVAL` in the rating module's set); test `backend/tests/test_deployments.py`.

- [ ] Red first: every Acceptance 4 case not covered by Task 4, each with its predicted
  cause written in the test's docstring before the code exists.
- [ ] **The Deployment Request (#971 A)**, `POST /api/v1/environments/{env}/deployment-requests`,
  body `{rating_version_ref, change_summary, skip?: PromotionSkip}`:
  1. G3 as below; `deployment:promote` checked in the handler with the Environment as the
     resource (#971 B.2); add the route to `HANDLER_GUARDED` with its file:line in this commit.
  2. Load the Rating Version (must be `approved`) and its decided approval request; find the
     predecessor's successful Deployment of that version, or take the `skip`.
  3. Call `promotion_order_refusal` with the target's environment-qualified entry; a reason
     → 422 `EVIDENCE_INCOMPLETE`. A missing floor item → the same.
  4. Write the row with its `evidence` **once**, then call the unchanged `approvals.submit`
     with `artifact_ref=deployment:<environment slug>@<n>` and `environment=<slug>`, as
     `rating_versions.submit_for_review` does (`backend/src/app/platform/rating_versions.py:293-305`).
     `backend/src/app/platform/approvals.py` imports nothing from the rating or deployment
     modules (Acceptance 5).
  5. `apply_approval_decision` in the deployment module loads the row **locked**
     (`with_for_update()`, as `rating_versions.py:337` does), calls
     `approvals.require_in_review(ref, row.status)` on it (`backend/src/app/platform/approvals.py:85`),
     as `rating_versions.py:357` does, and only then moves the row to `approved` (or back),
     called from a **new deployment branch of `_carry_to_the_artifact`**
     (`backend/src/app/api/approvals.py:488`, beside the four at `:499-517`; #971 audit
     advisory A5) — the **only** writer of `approved` (Acceptance 13). It refuses a row whose
     evidence lacks a floor item.
  6. **The generic route (#971 audit advisory A2).** Once `deployment` is in
     `ARTIFACT_TYPES`, `POST /api/v1/approval-requests` (authenticated only, `06` §5) must not
     become a way around the owning module. `_resolve_the_artifact`
     (`backend/src/app/api/approvals.py:425-484`) fails closed today with
     `ARTIFACT_TYPE_NOT_RESOLVABLE`; it gains a deployment branch that accepts **only** a
     Deployment Request row in `review` whose `evidence` holds both floor items, and refuses
     every other deployment reference (auditor-plans F3). **Why this cannot create an
     approvable request without pinned evidence (the FD-1200 class):** a Deployment Request
     row exists only through the owning module's submission (step 4), which writes the
     evidence and the approval request in one transaction; the generic route cannot create a
     row, and a row it could name in `review` already holds its open request, so a second
     one is refused by `uq_approval_requests_open_artifact` (`backend/src/app/db/models.py:645`).
     Red first (Acceptance 4): the generic route naming a reference with no row, a row not in
     `review`, and a row stripped of a floor item by a fixture, each refused.
- [ ] `POST /api/v1/environments/{env}/deployments`, body `{rating_version_ref, reason,
  deployment_request_ref?}` (`extra="forbid"`):
  1. **G3 first**: parse the ref; refuse any type other than `rating_version` with 422
     `VALIDATION_FAILED` naming the type, before reading any row.
  2. `rbac.require_permission(..., permission=Permission.DEPLOYMENT_PROMOTE,
     resource=ResourceRef(ScopeType.ENVIRONMENT, env.id))` **in the handler**, never a bare
     `requires(...)` (#971 B.2). Add this route to Task 0A's `HANDLER_GUARDED` with its
     file:line **in this commit**, so the sweep stays green by knowing it, not by skipping it.
  3. Load the Rating Version; refuse unless `approved`.
  4. **Approval-gated target** (it has a `deployment` policy entry; `prod` by default):
     require `deployment_request_ref` naming an **approved** request for this version and this
     Environment's identity, else 409 `DEPLOY_REQUIRES_APPROVAL`; re-evaluate
     `promotion_order_refusal` from the request's **pinned** evidence, never a re-read source;
     a reason → 409 `PROMOTION_ORDER_VIOLATION`. **The skip, if any, is the one pinned on the
     approved request; the deploy body takes no `skip`** (#971 A.5). **Mark the request
     `executed` exactly once** (auditor-plans F5): a conditional `UPDATE deployment_requests
     SET status = 'executed' WHERE id = :id AND status = 'approved' RETURNING id` in the
     deploy's transaction; no row returned → 409 `DEPLOY_REQUIRES_APPROVAL` ("the request is
     not approved, or has been executed"), and no Deployment is written.
     **Ungated target:** no request; the predicate reads the predecessor's successful
     Deployment directly, and no skip is possible (#971 A.5); a reason → 409
     `PROMOTION_ORDER_VIOLATION`.
  5. Insert the Deployment row and `audit.record(... action="deployment.created",
     before=<the previous live Deployment or None>, after=<this one>)` in **one**
     transaction.
- [ ] `GET /api/v1/environments/{env}/deployments`: history, newest first, cursor-paginated
  as the neighbouring list routes are.
- [ ] **Acceptance 8, this permission:** re-check `origin/main` for #942; branch A empties the
  `deployment:promote` `Check owner` cell **in this commit**; branch B notes it.
- [ ] The red-on-broken-input runs: G3 type check, blanket-skip validator, audit call, the
  handler's `resource=` argument (#971 B.5), the floor-item check (#971 A.4), and the planted
  second writer of `approved` (Acceptance 13).
- [ ] Green; commit.

### Task 6: Default-live scoring, the trace link, and server-derived liveness (RL-880, RL-888, RL-916, FR-357)

**Files:** Modify `backend/src/app/api/score.py` (`_required_ref`, `_fetch_bundle`),
`backend/src/app/platform/traces.py`, `backend/src/app/api/approvals.py` (`Withdraw`,
`withdraw_request`); tests `backend/tests/test_score.py`, `backend/tests/test_traces.py`,
`backend/tests/test_api_approvals.py`.

- [ ] Red first: Acceptance 6's three cases and Acceptance 7's trace cases.
- [ ] `_required_ref`: with no ref and a caller environment, resolve that environment's live
  Deployment for the caller's workspace; with none, or with no caller environment, keep the
  409. Update its docstring's "until then" sentence with a dated note, not by deletion.
- [ ] **Trace (#974):** resolve the Deployment **once**, together with the ref and the bundle
  in `_fetch_bundle` (`backend/src/app/api/score.py:153`, its ref resolution at `:182`), before scoring: for a
  default-live quote, the Deployment that served it; for an explicit ref, the caller
  environment's live Deployment if its Rating Version equals the ref exactly, else null.
  Pass that value to the trace write in `backend/src/app/platform/traces.py`; never re-read
  it at write time. Written with the pending row, never back-filled (`UPDATE` is revoked on
  `scoring_traces`, #974).
- [ ] **Carry the link across completion (#974 F1).** `complete_pending_trace`
  (`backend/src/app/platform/traces.py:198-272`) deletes the pending row (`:266`) and
  inserts the finished one at the same id; the insert copies `deployment_id` from the
  pending row. Red first (Acceptance 7): a sampled default-live trace, completed, still
  carries its Deployment id. Predicted red: the completed row's `deployment_id` is null
  because the re-insert does not copy it.
- [ ] `withdraw_request` — **the owner of auditor-928's client-supplied-liveness finding**
  (cited as prose until it is filed; the maintainer's entry headed
  `2026-09-30 11:12:45 BST — #973 (WK-674 S2 plan): (a) agreed; (b) its own FD, plus a class sweep`,
  item (b)). If that finding's class sweep places further instances here, the lead adds them
  by a dated delta. Derive liveness from Deployment rows for a `rating_version` ref.
  Remove `Withdraw.artifact_is_live`; update `test_api_approvals.py:500` to plant a real
  Deployment instead of sending the flag. **Red first:** a client sending
  `artifact_is_live: false` (or omitting it) for a version with a Deployment is refused with
  409 `WITHDRAW_AFTER_DEPLOY_FORBIDDEN`. Predicted red before the change: the withdrawal
  **succeeds**, because the route trusts the body.
- [ ] Green; commit.

### Task 7: The gate and the ledger

- [ ] `tests/test_repository_invariants.py`, the migration round trip, then the full two-half
  gate on the committed tree. Quote every rc, the `N passed` line and `HEAD` against main's
  `N passed` (a total that did not move means the new tests were never collected).
- [ ] The ledger records: the tree; premises a–r; the red-first and broken-input quotes; DP
  resolutions with their record ids; Acceptance 8's branch and the SHA it read; the Write set
  check as run at dispatch; FR-272's notification carried to WK-688.
- [ ] Item 11 (Acceptance 11).

## Hand-off

Slice 3 (environment isolation) starts after this slice closes and is gated by `OQ-1235`. It
reads this slice's `EnvironmentRow` for per-environment keys and settings. Slice 5 replaces
Task 6's per-request resolution with the switch, and reuses Task 5's route shape for rollback.

## Self-review

- **Scope against the map plan and the spec.** FR-267, FR-428, FR-429, FR-272 (deploy audit
  limb), NFR-498 (deploy limb), FR-347 (negative test), FR-357 (the state it needs) are each
  listed individually. `PL-1237` Task 2's gate outline maps to Acceptance 4 item by item:
  missing approval, skipping `uat` on one predicate, non-Deployer, `uat`-only Deployer, no
  Audit Event on broken input, non-Admin environment lifecycle, Service Account, absent
  policy entry; `generate-contracts.py --check` (Acceptance 2); the trace relationship on
  existing rows (Acceptance 3); the full gate (10); item 11 (11).
- **The five conditions the lead relayed**, each at every site class (narrative, Files,
  Steps, Acceptance):
  1. blanket skip and fallback — Global Constraints, Task 2 second commit, Task 5, Acceptance 4;
  2. `STALE_OWNER`, both branches — Scope, Tasks 0, 4 and 5, Acceptance 8;
  3. G3 — Scope, Task 1, Task 5 step 1, Acceptance 4;
  4. RL-1263 write set, `uv.lock`, `03` §5.1, contention — Global Constraints, Write set, Task 0;
  5. #960 before dispatch — Status.
  6. A1, the authorisation sweep, first — Task 0A, Write set, Acceptance 12; and the
     single writer of `approved` over every approvable table — Acceptance 13, Task 5.
- **auditor-plans' audit of `fdde72a2`, F1–F9**, each closed at its sites: F1 by #971 A.6
  (Task 4, Acceptance 4); F2 Acceptance 13; F3 Task 5 step 6 and Acceptance 4; F4 Task 5
  step 5 and Acceptance 4; F5 Task 5 deploy step 4 and Acceptance 4; F6 Task 0A (d); F7
  Acceptance 12 (e); F8 the predicate (Task 2); F9 the dated deviation paragraph and `RL-1296`.
- **#971 at `327e1179` and #977**, applied at their sites: A.4 restated (Acceptance 13, Task 3
  vocabulary step, Write set); A.6's credentials (Task 4, Acceptance 4, Write set); the
  deployment-wide confirmation (Decided in this plan); DP-S2-5 closed; DP-S2-4 ruled (a) by
  #977 (DP table, Acceptance 12 (c), Write set).
- **auditor-plans N1–N3** (its audit of `a79fc6b4`): N1 and N2 Task 4 and Acceptance 4, with
  the Task 3 constraint; N3 Task 4 and Acceptance 4. Its G1 is Acceptance 13's declared
  vocabulary (#971 A.4 at `327e1179`, `models.py:635`, `:1195`, `:1898` among the `String`
  status columns it covers).
- **Each ruling applied where it operates.** RL-1296 items 1 (Task 2 validator), 3
  (`PromotionSkip`, pinned on the Deployment Request as #971 C amends it), 4 (the predicate's place, Acceptance 5), 5 (one commit, Task 2),
  6 (no new permission: `set_policy` stays the grant path, nothing added); its Acceptance
  bullets are Acceptance 4's FR-429 cases and Acceptance 5.
- **Literals** were checked against the tree above (premises); names the executor adds
  (`skippable_predecessors`, `PromotionSkip`, `promotion_order_refusal`, the modules and
  tables) are proposals, named once.
- **#971 applied at every site class** (the 2026-09-30 revision): A.1 (Task 1 spec, Task 2
  `refs.py`, Task 3 table, Decided-in-plan slug), A.2 (Task 1, Task 3 `evidence`, Task 5
  submission), A.4 (Acceptance 4 and 13, Task 5), A.5 (Acceptance 4, Task 5 deploy step 4),
  B.1–B.5 (Task 2, Task 1 FR-345, Task 5 step 2, Task 0A allow-list, Acceptance 4), C
  (`PromotionSkip`'s home). The DM's check-back on this revision ("consistent" or a dated
  delta) is the 11:11:25 entry's condition; its answer on `22cb24b3` was "consistent", with
  four wording gaps (the pinned skip at the route, the request row's slug and identity, the
  model-derived one-writer check with its baseline, and Task 1's FR-345 amendment), each
  closed in the revision after it, with #971's audit advisories A2–A5.
- **Open: none that blocks this slice.** DP-S2-1 (#974), DP-S2-2 and DP-S2-3 (#971 A–B) and
  DP-S2-5 (disposed by #971 A.6 at `327e1179`) are settled; DP-S2-4 is ruled by #977 (working id 9907) and, by the 11:17:35
  entry, does not block this slice. The plan goes `active` on the lead's go once
  #971 and #974 are minted.
- **Placeholder scan**: no step says "per DP-S2-n" any more; nothing is deferred except
  Task 0A (c), which is another slice's.
