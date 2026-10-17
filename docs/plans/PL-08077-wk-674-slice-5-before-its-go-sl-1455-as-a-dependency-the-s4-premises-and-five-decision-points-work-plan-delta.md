---
id: PL-8077
family: plan
kind: map
title: WK-674 — Slice 5 (SL-1259) before its GO, with SL-1455 merged as a formal dependency, the premises Slice 4 and SL-1455 changed, and five decision points — a dated Work-plan delta
status: draft                   # draft → active → superseded | retired (§1.2a)
created: 2026-10-17
owner: planner
tree: 055b5e6b74f9d4b10f6df54570e33ed2805ae9a8
phase: P2
work: WK-674
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1237, PL-1537, PL-1620, PL-1710, PL-1735, PL-1454, PL-1714, RL-1614, RL-1685, RL-1687, SL-1258, SL-1259, SL-1455, SL-1711, SL-1736, SL-1722]
---

# PL 8077 — WK-674 Slice 5 before its GO: SL-1455 as a dependency, the changed premises, five decision points (Work-plan delta)

> **For agentic workers:** this is a **dated Work-plan delta** under Lean P2 L5
> (`document-ids.md` §1.6, the PL `map`/`leaf` row: *"a change is one dated Work-plan delta, a
> new `PL-` that `relates:` the Work's plan"*). It does not replace
> [`PL-1237`](PL-01237-wk-674-deployment-environments-switchover-tenancy-map-plan.md) Task 5,
> [`PL-1537`](PL-01537-wk-674-slices-4-to-6-work-plan-delta.md) row 2,
> [`PL-1620`](PL-01620-wk-674-slices-4-and-5-after-sl-1455-returned-to-p2-work-plan-delta.md)
> D5.1 to D5.5, or
> [`PL-1710`](PL-01710-wk-674-the-wf-701-deployment-steps-demo-slice-after-s5-and-s5-s-commit-acknowledgement-line-work-plan-delta.md)
> D5.6, and it edits none of their bodies. **Read them in that order, then this file.** Where
> they differ, this file is the later statement. It changes **Slice 5 (`SL-1259`) only**: one
> added "Depends on" (D5.7), a re-derived write set (D5.8), the transaction order and the
> rollback's FR-452 pair (D5.9, D5.10), the seed rule for S5's tests (D5.11), and five decision
> points (DP-S5-Q1, Q2, Q4, Q5, Q7) that the maintainer asked to see with this draft.
> REQUIRED SUB-SKILL for S5's executor: subagent-driven-development (recommended) or
> executing-plans. Bound skills, unchanged from `PL-1620`: `python-test`,
> `test-driven-development` (every red seen red **by its cause**), `dev-commands`,
> `fastapi-service`, `contract-guard` (D5.6's `model-schema` field), `git-hygiene`.

Filed under **working id 8077**, reserved by the lead in `~/gi-pricing-plan.local/handover/eta.md`,
entry "2026-10-17 11:13:00 BST — Lead: ids allocated / reserved", verbatim: *"Working id reserved:
**8077 PL** (WK-674 S5 Work-plan delta draft; planner-1259, branch
pl-1259-s5-delta-2026-10-17)."* Written 2026-10-17 (started 11:12:59 BST) by the planner
(seat `planner-1259`). The starting point is the planner's readiness note
`~/gi-pricing-plan.local/scratch/sl1259-readiness-2026-10-16.md` (not a governed record); every
claim of it that this file uses was re-read at the trees below, and the ones that moved are
marked.

**Trees read.** `origin/main` @`055b5e6b` (#1317) for every spec, plan, ruling and roadmap
citation. S4's authored branch `origin/sl-1258-wk674-s4` @`de92620a` (tree `1de91e9c`,
merge-base with main `055b5e6b`). SL-1455's branch `origin/sl-1455-wk1178-nfr489-http`
@`2f4243bb` (tree `d8b8315a`, merge-base `0877e6e7`). `PL 8061` (unminted, the `PL-1714` delta
that carries E4.8) on `origin/pl-8061-pl1714-delta-2026-10-16` @`33446114`. **Neither S4 nor
SL-1455 is merged** (roadmap `SL-1258` and `SL-1455` are `status: draft` at `055b5e6b`); every
line cite into their branches moves until they merge, and S5's `LG-` re-derives each at S5's
base.

## Authority

Every entry is quoted from `~/gi-pricing-plan.local/channel/to-lead.md` unless it names another
file. Each names its author.

- **The owed delta and the questions — the lead:** `from-lead-2026-10-09.md`, entry
  "2026-10-16 10:29:33 BST — Lead: planner-1259 DONE — SL-1259 (WK-674 S5) NOT READY; a plan
  delta is owed before its GO; questions for the maintainer; SL-1722 re-merged". Its questions,
  verbatim: *"(Q1) must the NFR-489 exit reading go through `live` (then the bench needs a
  governed deploy, and S5 writes into S4's harness)? (Q2) one process per container, or S5 adds
  `--workers`; does D5.6's identifier name a process or a container? (Q4) the S5 delta vehicle: a
  new PL delta (PL-1710 is on main, frozen)? (Q5) the 12:07:40 DP-4 line amending S5's
  dedicated-VM run list — on a branch or owed? (Q6) SL-1455 merged as a formal "Depends on" for
  S5? (Q7) under DP-E1 (b), E4.8's slice vs S5 on test_deploy_stack_runtime.py — which first?"*
- **Q6 answered, the rest to come with this draft — the maintainer (by delegation):** entry
  "2026-10-16 10:29:56 BST — Maintainer: RL-1687's 429-declaration question (around :306-309):
  the LEAD rules it; my view: it lands in S4", verbatim: *"SL-1259 (S5) NOT ready: noted. The
  plan delta is owed before its GO. Q6: YES. SL-1455 becomes a formal Depends-on of S5 in the
  delta, because S5's NFR-489 exit reading builds on SL-1455's measured path. Q1, Q2, Q4, Q5,
  Q7: answered with S5's delta draft, ideally at the Mon 19 12:00 checkpoint. The planner brings
  each as a DP with options and citations, and Q5 (the 12:07:40 DP-4 line: branch or owed) is
  answered by a grep first. None blocks today's work."*
- **Q3, ruled — the lead:** `from-lead-2026-10-09.md`, entry "2026-10-16 10:30:18 BST — LEAD
  RULING (RL-1687's 429-declaration question …)", verbatim in part: *"in SL-1258 (WK-674 S4),
  every /api/v1 operation the management rate limit counts declares a 429 problem response,
  through ONE router-level mechanism on the included routers (not per-route `problems(...)`
  edits), and `generate-contracts` is re-run so `docs/contracts/openapi/generated.json` carries
  it — in the same commit as the limiter change"*. Concurred by the maintainer (by delegation),
  entry "2026-10-16 10:30:57 BST". Applied in P4 below.
- **Today's lane — the maintainer (by delegation):** entry "2026-10-17 11:08:04 BST —
  Maintainer: TODAY'S MODE …", lane E, verbatim: *"SL-1259 S5: the plan delta (planner) and the
  Mon 19 DPs Q1–Q7."* "The 16 Oct cut checkpoint stays Mon 19 Oct 12:00."
- **The vehicle:** Lean P2 L5 (`document-ids.md` §1.6, quoted in the header above). `PL-1710`
  is on `main` and frozen by family (`document-ids.md:49`, the Plan row: `frozen`), and check
  34 (`document-ids.md:230`) reds any body edit to it; see DP-S5-Q4.

## Goal

Make Slice 5 GO-ready on paper before Mon 19 Oct 12:00: name every dependency it actually has,
re-derive the premises Slice 4 and SL-1455 changed under it, and put the five open questions to
the maintainer as decision points with options, citations and a recommendation. The Work's goal
is `PL-1237`'s, unchanged; Slice 5's scope and requirement ids are `PL-1620`'s, unchanged.

## Acceptance Standard

Each item is checked by a command a fresh reviewer can run from the repository root on the named
tree.

1. **This delta passes the docs checks on its own branch.** `python3 scripts/audit-docs.py`,
   `python3 scripts/doc-index.py --check` and `python3 scripts/register-lint.py` each exit 0 at
   the branch head, except the lines naming this file's working id 8077, which clear at the mint.
2. **No requirement range.** `grep -nE '(N?FR)-[0-9]+ *(-|to|–) *(N?FR-)?[0-9]+' <this file>`
   prints no line that stands for a set of requirement ids.
3. **SL-1455 is a formal dependency.** At S5's GO, `git grep -n 'D5.7' -- <S5's LG>` prints the
   quoted D5.7 line, and `SL-1259`'s roadmap row carries a dated line naming this delta's minted
   id (Hand-off).
4. **Every decision point has a resolver's dated line before S5's GO.** For each of DP-S5-Q1,
   Q2, Q5 and Q7 (Q4 is answered by this file's existence once ruled), S5's `LG-` quotes the
   ruling entry by its header, verbatim, before its first code commit.
5. **Slice 5's own acceptance** is `PL-1537` Acceptance item 5 as changed by `PL-1620` D5.1 to
   D5.5, `PL-1710` D5.6 and this file's D5.7 to D5.11, item by item, at S5's merge tree.
6. **The gate is green on S5's merge tree**: the `CLAUDE.md` §11 commands, both halves, each exit
   0, named against `origin/main...<S5's branch>`.

## Global Constraints

`PL-1237`'s, `PL-1537`'s, `PL-1620`'s and `PL-1710`'s Global Constraints apply unchanged. In
addition:

- **No direct DB or status write in an S5 test** (to-lead "2026-10-14 11:43:57 BST" item 1, as
  applied by "2026-10-16 10:08:52 BST" items 1 to 4 and "2026-10-16 10:19:57 BST"); D5.11.
- **A verdict states N** (`00` §2.3 **Replica**, `docs/specs/00-overview.md:170`; `03` NFR-489's
  dated clarification, `docs/specs/03-rating-engine.md:1507`: *"every reading states N"*).
- **Never `cd`**, as every role charter says.

## Premises re-derived

Each premise names the tree it was read at. "S4" is `de92620a`; "SL-1455" is `2f4243bb`.

- **P1 — S4's deploy routes count after the permission check.** `CountDep =
  Annotated[CountAfterCheck, Depends(management_counter)]` (`backend/src/app/api/deployments.py:38`
  at S4), taken by both POST routes (`:53`, `:83`) and passed as `count_management=` (`:68`,
  `:96`); the service awaits it inside `_authorised_environment` (`platform/deployments.py:100-101`
  at S4). *(Readiness note I1; unchanged in substance, lines moved.)*
- **P2 — the order inside `deploy`.** `deploy` is `platform/deployments.py:455` at S4; the
  count runs through `_authorised_environment` (`:478`), then `_approved_compiled_version`
  (`:480`), and the `deployment.created` audit `after=` is `:573`. `PL-1710` P5's cites
  (`:524-554` at `1e260c15`) are stale at S4's tree. *(I2.)*
- **P3 — S4's bench never reads `live`.** `scripts/bench-deploy-path.py:131` at S4 seeds through
  `bench._seed`, and `:134` sends `bench._ctx()`, which sets
  `options.rating_version_ref=_RATING_VERSION_REF` (`scripts/bench-rating.py:484` at S4); an
  explicit ref is used before `live`. `_seed` writes the Rating Version `status="draft"`
  (`bench-rating.py:771` at SL-1455), and `deploy` refuses anything not approved and compiled
  (`_approved_compiled_version`, `platform/deployments.py:106` at S4). *(I3, confirmed.)*
- **P4 — `429` is declared router-wide in S4.** `app.include_router(router, prefix=API_PREFIX,
  responses=problems(429))` (`backend/src/app/main.py:149` at S4), the lead's 10:30:18 ruling. A
  rollback route added to the deployments router inherits `429`; S5 does not write it per route.
  *(I7: resolved.)*
- **P5 — one uvicorn process per `api` container.** `deploy/Dockerfile:43` at S4: `CMD
  ["uvicorn", "app.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]`, no
  `--workers`; `deploy/docker-compose.yml` sets no `WEB_CONCURRENCY` (`git grep -n -E
  'workers|WEB_CONCURRENCY|uvicorn' origin/sl-1258-wk674-s4 -- deploy/docker-compose.yml` prints
  comment lines `:133`, `:135` only). The bench's `--workers` (default 1,
  `bench-deploy-path.py:107`) is recorded as `workers_per_replica` (`:92`), not applied or
  observed. uvicorn 0.52.3 (this tree's lock) reads `WEB_CONCURRENCY` when `--workers` is not
  given (`uvicorn/config.py:352-353`). RL-1685's **Replica** row: *"N `uvicorn` worker processes,
  one per dedicated vCPU, behind one listening address"*; its NFR-454 clarification: *"on the
  shared VM N = 4, a diagnostic reading only, and the reference N is fixed with G4's dedicated
  host"* (`docs/rulings/RL-01685-…:436`). *(I4, confirmed.)*
- **P6 — SL-1455's bench already has a default-live arm, by a direct row.** `_seed` adds a
  `DeploymentRow` for `uat` with `reason="bench: default-live arm"` (`scripts/bench-rating.py:793-808`
  at SL-1455), and the sweep drives a body with `rating_version_ref` popped (`:1341-1352`). That
  arm reads `live` through `_serving_ref` (`backend/src/app/api/score.py:169-191` at SL-1455) but
  no governed deploy runs, so no PREPARE/COMMIT push would run on S5's tree. *(New since the
  readiness note.)*
- **P7 — the dedicated-host verdict wording.** The maintainer's (by delegation) entry "2026-10-16
  22:22:44 BST — DATED LINE on PL-1454 Acceptance 2 / Task 4 — the sweep moves to the dedicated
  host, and its reading is the G4 VERDICT", item 2, verbatim: *"On nfr-bench-1 the reading is
  labelled "measured, dedicated host (G4 discharge)". It IS the NFR-489 verdict (and NFR-454's
  limb in the same invocations)"*; reserved as RL 8076 (unminted). `RL-1614` (minted) records
  the 2026-10-11 11:02:35 ruling, item 1: *"(c) is rejected: two competing verdicts"*, and item
  2: *"The P2 exit's "meeting NFR-489" is SL-1259's verdict on the exit tree, with replicas per
  DP-3"*. **How the two read together decides what S5's NFR-489 run is for**; it is put to the
  maintainer inside DP-S5-Q1, not resolved here.
- **P8 — S5's write set against the in-flight branches.** Predicate: `git diff --name-only
  origin/main...<branch> | sort`, intersected by `comm -12` with the 15-path S5 set of D5.8.
  S5 ∩ S4 (42 paths) = **9**: `api/deployments.py`, `api/score.py`, `main.py`,
  `platform/deployments.py`, `backend/tests/test_deploy_stack_runtime.py`, `deploy/Dockerfile`,
  `deploy/docker-compose.yml`, `scripts/bench-deploy-path.py`, `scripts/bench-rating.py`. S5 ∩
  SL-1455 (17 paths) = **3**: `api/score.py`, `main.py`, `bench-rating.py`. S4 ∩ SL-1455 = 5:
  `api/authz.py`, `api/score.py`, `main.py`, `platform/rate_limit.py`, `bench-rating.py`. All S5
  overlaps are serial by D5.7; they are rebase work, not parallel conflicts. *(Readiness note §3
  counted 8 for S4; S4's `main.py` is new since, from P4.)*
- **P9 — the re-checks the frozen plans keep.** `03` NFR-502 names `/score` only:
  `git grep -n -E '^\| \*\*NFR-502\*\*' origin/main -- docs/specs/03-rating-engine.md | grep -c
  'score/compare'` → 0 at `055b5e6b` (`PL-1620` D5.4 holds). `PL-1620` D5.5's window clash has
  lapsed: `SL-1367` is `status: closed` (`docs/roadmap.md:1976` at `055b5e6b`); S5's `LG-` cites
  its ledger when it books its window.
- **P10 — the compose worker set.** S4 runs one service per pool: `worker-compute`,
  `worker-scoring`, `worker-io`, `worker-default` (`deploy/docker-compose.yml:147-170` at S4).
  `PL-1237` Task 5 puts the switch on a Redis channel, which adds no Job kind and no queue; S5
  adds neither, so S4's derived-consumer guard stays green. If S5 finds it needs one, that is a
  stop (`CLAUDE.md` §0), not a widening.

## Tasks

| Order | Slice | Scope (what the `LG-` quotes) | Requirements, each id | Depends on | Size |
|---|---|---|---|---|---|
| 1 | `SL-1259` — Slice 5 (changed) | `PL-1537` row 2, `PL-1620` D5.1 to D5.5, `PL-1710` D5.6, **plus D5.7 to D5.11 below** | unchanged from `PL-1620`: `03` FR-268, FR-269, FR-272 (audit limb for rollback), NFR-489, NFR-490, NFR-493 (linearity limb), NFR-494, NFR-497 (mechanism), NFR-498 (rollback limb), NFR-502; `07` FR-452 (the rollback route's count, D5.10; cited, not added) | `SL-1258` merged; **`SL-1455` merged (D5.7)**; DP-S5-Q1, Q2 and Q7 ruled; `PL-1710` DP-3's pre-build statement written | + one dependency, + four acceptance lines, write set + up to 5 paths |

### Slice 5 (`SL-1259`) — changes since `PL-1710`

**Dated line, 2026-10-17, on `PL-1620` and `PL-1710` (not edited).**

- **D5.7 — SL-1455 merged is a "Depends on" of Slice 5** (Q6, the maintainer's 10:29:56 entry:
  *"SL-1455 becomes a formal Depends-on of S5 in the delta, because S5's NFR-489 exit reading
  builds on SL-1455's measured path"*). It was an order only: `RL-1614`, recording the 11:02:35
  ruling, item 1, *"SL-1455 precedes SL-1259's bundle-path edits"*; `PL-1454:268`. S5 branches
  from a `main` that carries both `SL-1258` and `SL-1455`, and every S5 cite into
  `api/score.py`, `main.py` and `bench-rating.py` is re-derived there (P8).
- **D5.8 — the write set, re-derived.** `PL-1537`'s S5 set (`PL-01537-…:148`:
  `api/deployments.py`, `platform/deployments.py`, `errors.py`, `03-rating-engine.md`,
  `openapi/generated.json`, `backend/tests/`) **plus**: `api/score.py`, `main.py` and
  `platform/bundle_slot.py`, `config.py` (`PL-1237` Task 5's `live` read, lifespan subscriber and
  `bundle_slot_capacity`); `packages/model-schema/src/model_schema/deployments.py` and the
  regenerated contract (`PL-1710` DP-3 (a)); and, by the rulings of DP-S5-Q1 and Q2,
  `scripts/bench-deploy-path.py`, possibly `scripts/bench-rating.py`, and `deploy/Dockerfile` or
  `deploy/docker-compose.yml`. Fifteen paths in all (P8's predicate set). Any path outside it
  is a stop to the lead, not a widening.
- **D5.9 — the order in the deploy transaction**, part of `PL-1710` DP-3's pre-build statement
  (ruled (a), CONDITIONAL, the maintainer's (by delegation) entry "2026-10-14 10:14:13 BST" item
  3): permission check → management count (P1) → approved-and-compiled check (P2) → PREPARE →
  COMMIT → `deployment.created` audit with the D5.6 set → commit. A `429` from the count raises
  before PREPARE, so a refused deploy never makes a replica hydrate. The statement S5 writes in
  its `LG-` before the code also says, as DP-3 requires, what is recorded when the transaction
  fails after replicas switched. Red-first: a deploy refused `429` leaves every replica's `live`
  unchanged and sends no PREPARE.
- **D5.10 — the rollback route under FR-452.** The rollback route (`03:1069`, `POST
  /environments/{env}/deployments/rollback`) takes `CountDep` and passes `count_management=`
  through `_authorised_environment`, as S4's two POST routes do (P1). Red-first, by the pattern
  of the maintainer's (by delegation) entry "2026-10-16 10:14:17 BST" item (2): a `403` rollback
  leaves the management counter unchanged; a permitted rollback adds exactly 1. Its `429` is
  inherited (P4); the regenerated `generated.json` shows it on the new operation. The
  rollback-under-load test (`PL-1237` gate outline) states the management limit it runs under
  (`platform.default_management_rate_limit_rps`, `platform/settings.py:244` at S4, default
  `None`).
- **D5.11 — S5's tests seed through the governed path.** Every S5 runtime test creates its
  Rating Version through the services or the API (`examples/fremtpl2/model.py:723`,
  `create_approved_rating_version`, or submit/decide by two principals) and deploys it through
  the deploy route. The only accepted direct write is the upstream Model through
  `approved_rows.add_approved`, citing "2026-10-16 10:19:57 BST" item 3. `bench-rating.py::_seed`
  is never imported by a test (10:08:52 item 4); S5's `LG-` carries that grep. How S5 reaches
  S4's private `_governed_workspace` (`backend/tests/test_deploy_stack_runtime.py:129` at S4) is
  DP-S5-Q7.

Nothing else in Slice 5 changes. `SL-1711` (`PL-1710`) is unchanged; it still follows S5.

## Decision points

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-S5-Q1 | Must S5's NFR-489 exit reading go through `live` (requests with no `rating_version_ref`, served from a version deployed by the governed deploy route), and so through S4's bench? S4's bench sends an explicit ref and seeds a `draft` that `deploy` refuses (P3); SL-1455's default-live arm reads `live` from a directly written `DeploymentRow`, with no PREPARE/COMMIT (P6). Sub-question for the maintainer: how 22:22:44 item 2 (*"It IS the NFR-489 verdict"*) reads beside `RL-1614` (*"(c) is rejected: two competing verdicts"*; P7). | (a) **Default-live through the governed deploy**: `bench-deploy-path.py` creates and approves its version through the services (`create_approved_rating_version`), deploys it by `POST /environments/uat/deployments`, and drives requests with the ref removed; the explicit-ref arm stays as a labelled diagnostic. S5 writes `bench-deploy-path.py` (S4's, merged by then). (b) **Default-live from a direct `DeploymentRow`**, as SL-1455's arm does (P6); no governed deploy in the bench. (c) **Explicit ref as the exit reading**, as S4's bench is built; default-live not measured by S5. | **(a).** NFR-489 is a budget "for a single quote against a live Rating Version" (`00` NFR-454, which NFR-489 cites, `docs/specs/03-rating-engine.md:1507`), and S5 is the slice that changes how `live` is served; (c) skips that read (`score.py:169-191` at SL-1455), and (b) skips the PREPARE/COMMIT push S5 builds, so a replica's `live` could be unset or stale on the measured path. (a) also keeps the seed on the services (the 10:08:52 basis: *"a compile green on such a seed can be green on a version the platform would never have accepted"*). On P7, the planner's reading for the maintainer to confirm or correct: 22:22:44 makes SL-1455's dedicated-host sweep the G4 discharge of the remedy proof (per replica, one listening address), and `RL-1614` keeps the exit-tree verdict on S4's replicated path with S5; if 22:22:44 instead moves the exit verdict to SL-1455, `RL-1614` needs a superseding ruling and S5's NFR-489 limb shrinks to "no regression from SL-1455's reading". | scope / measurement | **yes**: it fixes S5's write set and the meaning of its NFR-489 run | the maintainer |
| DP-S5-Q2 | One `uvicorn` process per `api` container (P5), or does S5 make N > 1? And does `PL-1710` D5.6's "stable replica identifier" name a process or a container? | (a) **N from `WEB_CONCURRENCY`, observed**: the compose `api` service sets `WEB_CONCURRENCY` (uvicorn reads it, P5; no `CMD` change), and the bench observes N per container (as it already observes `replicas_running`) and voids a reading whose observed N differs from the claimed one. D5.6's identifier names the **replica** (the container's hostname), and the after-state records, per replica, the worker processes that acknowledged COMMIT out of those subscribed; "every replica switched" means every process of every replica. (b) **N = 1 per container, stated**: no compose change; every S4-path reading is N = 1. D5.6 names the container, which is then one process. (c) **"Replica" read as N containers behind `lb`**: N = number of `api` containers. | **(a).** RL-1685 defines a replica as *"N `uvicorn` worker processes … behind one listening address"* and records that one event loop cannot carry 200 rps (*"2.8 and 1.7 s of evaluator time per second at 200 rps"*, `RL-01685-…:436`), so (b) makes NFR-489 at 200 rps fail by construction; (c) contradicts the `00` §2.3 definition and would need a spec change. Under (a), each uvicorn worker runs the lifespan and so subscribes on its own; acknowledging per process and grouping by replica keeps D5.6's test meaningful (the suppressed-COMMIT red drops one process of one replica and names both). The compose edit is one `environment:` key in S4's file, after S4 merges. N on the shared VM is 4 (RL-1685); the reference N is fixed with the dedicated host (G4). | mechanism / measurement | **yes**: it fixes D5.6's record shape and the compose write | the maintainer; the decision-maker if D5.6's shape needs `PL-1710` DP-3 re-ruled |
| DP-S5-Q4 | The vehicle for S5's changes: `PL-1710` is on `main` (`status: draft`), and S5's premises moved. | (a) **This new dated Work-plan delta** (`PL 8077`), relating `PL-1237`, under Lean P2 L5. (b) Fold the items into `PL-1710` before its activation line. (c) S5's `LG-` states them as executor premises at the GO. | **(a).** (b) is refused mechanically: a plan is `frozen` by family (`document-ids.md:49`) and check 34 (`:230`) passes only `status:`, `superseded_by:` and `corrected_by:` changes against the merge-base. (c) puts a write-set and scope change (D5.8, DP-S5-Q1, Q2) in an executor's record, which is the planner's and the decision-maker's to state (`delivery-process.md` §3, as `planner.md` cites it). `PL-1710`'s activation line stays the lead's; this delta does not need it, but S5's GO needs D5.6 binding, so it needs that line. | process | no (this file is the answer if ruled (a)) | the maintainer |
| DP-S5-Q5 | Is the dated line from the maintainer's (by delegation) entry "2026-10-14 12:07:40 BST" DP-4 (*"Record it as a dated line amending S5's run list (RL-1614)"*) written on a branch, or owed? **Grep first**, verbatim: `git grep -n -i -e '12:07:40' -e 'session 2' origin/main -- docs/rulings docs/plans docs/roadmap.md docs/ledgers docs/findings` at `055b5e6b` (44 lines). Result: no line under `SL-1259`'s row (its one dated line is `docs/roadmap.md:1192`); the hits are `PL-1735` (minted from `PL 8034`), which **plans** the line: Task 4 Step 4 (`PL-01735-…:738-740`), text pre-written, placed *"under `SL-1259`'s row in `docs/roadmap.md`"*, owned by `SL-1736`, confirmed by the maintainer's (by delegation) entry "2026-10-14 12:31:22 BST" (`PL-01735-…:742-744`). `SL-1736` is `status: draft` (its row, `docs/roadmap.md:2603`). The same predicate over every `origin` branch head is the owed second half (Hand-off item 1). | (a) **Owed by `SL-1736`, as `PL-1735` plans it**: the line lands with SL-1736's PR, and S5's `LG-` quotes it, or quotes `PL-1735`'s pre-written text and the 12:07:40 entry if SL-1736 has not merged by S5's GO. (b) **Write it now** in this delta's batch, under `SL-1259`'s row, and strike it from SL-1736's write set by a dated line. (c) Leave it to S5's `LG-` only. | **(a).** It is planned, owned and confirmed; moving it would make two records own one line. The run list S5 books on nfr-bench-1 session 2 is then `RL-1614` item 3, `PL-1620` D5.3, plus `PL-1735` DP-4's two NFR-485 5 M × 60 runs (≈ +30 min per arm) and any named NEAR-BOUND extras (`PL-1735:521-533`: session 2 *"3.9 h committed, at most 5.15 h"*). S5's `LG-` lists them when it books the window. | record keeping | no | the maintainer |
| DP-S5-Q7 | Under DP-E1 (b) (the maintainer's (by delegation) entry "2026-10-16 09:55:22 BST" item (3): *"S4 merges seeded, and E4.8 becomes its OWN slice id (minted in the next batch, owner WK-674)"*), E4.8's slice and S5 both edit `backend/tests/test_deploy_stack_runtime.py`. Which goes first? DP-E1's (a)/(b) is the lead's, at S4's PR time, and is not yet picked. Under (a) the question does not arise (E4.8 lands inside S4). | (a) **No ordering constraint; S5 writes its runtime tests in a new module** (for example `backend/tests/test_deploy_switch_runtime.py`) and touches the shared file only to move `_governed_workspace`, `_Workspace` and `_scoring_request` (`test_deploy_stack_runtime.py:118-246` at S4) into a shared test-helper module; whichever of E4.8's slice and S5 merges second re-merges and re-runs the other's named tests, as `PL 8061` E4.9 does for the shared entrypoint. (b) **E4.8's slice first**, then S5 (E4.8 needs only `SL-1722`; S5 needs S4 and SL-1455, so this is the likely order anyway). (c) **S5 first**; E4.8's slice rebases onto it. | **(a), with (b)'s order expected.** It removes the conflict instead of scheduling it: S5's tests are about the switch, not the stack, and need the helper, not the file; importing a private name across test modules (the other way out) leaves the helper owned by one file and edited by two slices. Under (a) the only shared edit is a move, red-checked by both slices' named tests at the second merge. | sequencing | **yes**, under DP-E1 (b) only | the lead (sequencing); the maintainer if contested |

A plan is "`draft` while decision points are open, `active` on freeze" (`document-ids.md` §1.6,
the PL `map`/`leaf` row). DP-S5-Q1, Q2 and Q7 are open and blocking, so this delta stays
`draft` until each is ruled and the rulings are cited here by a dated activation line, at or
before its mint.

## Hand-off (not this plan's writes)

1. **DP-S5-Q5's second half** — the same predicate over every `origin` branch head: the lead or
   an auditor, outside any held gate slot (the sweep-pause rule). This draft ran it on `main`
   only.
2. **`SL-1259`'s roadmap row** gets a dated line naming this delta's minted id, as the planner's
   earlier dated line on that row does (`docs/roadmap.md:1192`): the planner, in the mint batch,
   with the minted id (a working id there would red check 31).
3. **`PL-1710`'s activation line** (D5.6 binding for S5): the lead.
4. **DP-E1's (a)/(b)**: the lead, at S4's PR time.
5. **The P7 reading** (22:22:44 item 2 beside `RL-1614`): the maintainer, inside DP-S5-Q1; RL
   8076's minting (the next D batch) should carry whichever reading is ruled.

## Self-review

- **Spec coverage.** No requirement id is added or removed; the Tasks row lists `PL-1620`'s ids
  individually and cites `07` FR-452 for D5.10 without adding it.
- **Rulings at every site**, re-checked against `to-lead.md` and `from-lead-2026-10-09.md` from 2026-10-16 10:29:33 to 2026-10-17 11:13:00 BST (`docs/plans/README.md` convention 4). Q6: D5.7, the Tasks row,
  Acceptance item 3. The 10:30:18 `429` ruling: P4, D5.10. DP-3 of `PL-1710` (10:14:13 item 3):
  D5.9. The seed rulings (11:43:57, 10:08:52, 10:19:57): Global Constraints, D5.11, DP-S5-Q1.
  12:07:40 DP-4: DP-S5-Q5. 09:55:22 item (3): DP-S5-Q7. 22:22:44: P7, DP-S5-Q1.
- **Placeholders.** "<S5's LG>" and "<S5's branch>" are read at the slice. The example module
  name in DP-S5-Q7 (a) is illustrative, not a commitment. No other.
- **Literals** were read at the trees named in the header, by path and line: every route,
  setting key, function, file line and count.
- **Not done here:** no code, no ruling, no edit to a frozen plan or to the roadmap.
