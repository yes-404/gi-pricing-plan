---
id: PL-8014
family: plan
kind: map
title: WK-674 — the scripted WF-701 deployment-steps demo, cut as one slice after Slice 5 (SL-8015), and Slice 5's one added acceptance line (the COMMIT acknowledgement set in the deployment Audit Event's after-state) — Work-plan delta
status: draft                   # draft → active → superseded | retired (§1.2a)
created: 2026-10-14
owner: planner
tree: 1e260c1553acf39844939fe12da685ccfb835e54
phase: P2
work: WK-674
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1237, PL-1537, PL-1620, PL-1666, PL-1544, RL-1614, SL-1258, SL-1259, SL-1260]
---

# PL-8014 — WK-674: the WF-701 deployment-steps demo slice after S5, and S5's acknowledgement line (Work-plan delta)

> **For agentic workers:** this is a **dated Work-plan delta** under Lean P2 L5
> (`document-ids.md` §1.6, PL row: *"one plan per Work, slices as rows, no per-slice `leaf`; a
> change is one dated Work-plan delta, a new `PL-` that `relates:` the Work's plan"*). It does
> not replace [`PL-1237`](PL-01237-wk-674-deployment-environments-switchover-tenancy-map-plan.md)
> (the map plan), [`PL-1537`](PL-01537-wk-674-slices-4-to-6-work-plan-delta.md),
> [`PL-1620`](PL-01620-wk-674-slices-4-and-5-after-sl-1455-returned-to-p2-work-plan-delta.md) or
> [`PL-1666`](PL-01666-wk-674-slice-4-fd-9704-round-trip-fr-452-management-limb-and-activation-work-plan-delta.md),
> and it leaves every one of their bodies unedited. It does two things at once, as one delta:
> (1) it adds **one slice row**, SL-8015 (working id), under `### WK-674` in
> [`../roadmap.md`](../roadmap.md): the scripted, rehearsable walk of WF-701's deployment steps;
> (2) it adds **one dated acceptance line to Slice 5** (`SL-1259`), D5.6 below.
> **Read `PL-1237` Task 5, then `PL-1537` row 2 (R5.1 to R5.10), then `PL-1620` (D0.1 to D0.3,
> D5.1 to D5.5), then this file.** For S4's compose, read `PL-1666` and then `PL 1690` (on
> `origin/docs-d14-2026-10-12`, #1298, not yet on `main`; see activation need 3).
> REQUIRED SUB-SKILL for SL-8015's executor: subagent-driven-development (recommended) or
> executing-plans, task by task; steps use checkbox (`- [ ]`) syntax. Bound skills:
> `test-driven-development` (every red seen red **by its cause** before the code that turns it
> green), `python-test` (the `req` marker; negative tests), `dev-commands` (`uv sync
> --all-packages`; both gate halves; the compose commands), `fastapi-service` (reading the
> routes it calls; it adds none), `git-hygiene`. Not bound: `spec-change` and `contract-schema`,
> because SL-8015 changes no spec and no contract (if Task 0 finds it must, that is a stop, not
> a widening). Spawned from `.claude/roles/executor.md`; reads [`README.md`](README.md)'s five
> unchecked conventions before the first step.

Filed under **working id 8014**; its slice row is **SL-8015** (`draft`, working id 8015). Both
were reserved by the lead in `~/gi-pricing-plan.local/handover/eta.md`, line "2026-10-14 10:01:15
BST lead: RESERVED working ids (free-check own calls: 8011, 8014, 8015 all 0 on
id-form/eta/INDEX/branches/git grep; 8012, 8013 skipped for bare hits)", which assigns "PL 8014 =
the WK-674 dated plan delta: the WF-701 deploy-steps demo slice after S5 (W0 (b)) + S5's one
acceptance line (W1 (a): the COMMIT acknowledgement set in the deployment audit after-state).
SL 8015 = that demo slice. Seat planner-wf701plan." Written 2026-10-14 (started 10:07:09 BST) by
the planner (planner-wf701plan).

**Trees read.** `origin/main` @`1e260c15` (#1297) for every code and spec citation unless a line
says otherwise; `PL 1690` and `PL 1688` (written with a space throughout: each is minted only on the D14 branch, #1298, and does not resolve on `main` until D14 merges, so check 32 would read the hyphenated form as a broken citation) on `origin/docs-d14-2026-10-12` @`a49c6bc8`; S4's authored
branch `origin/sl-1258-wk674-s4` @`e1555803` for `deploy/docker-compose.yml`. **No S5 branch exists
on `origin` at this writing** (`git branch -r` lists no `sl-1259` ref). The starting point is the
design memo `~/gi-pricing-plan.local/handover/memo-wf701-deploy-demo-2026-10-14.md` (planner seat
`planner-wf701demo`, not a governed record); every claim of it this file uses was re-read at
`1e260c15`, and three were found to need more than the memo said (Premises P3, P5 and P6).

## Authority

Every entry below is quoted from `~/gi-pricing-plan.local/channel/to-lead.md` unless it names
another file. Each names its author.

- **The user's decision, recorded by the maintainer (by delegation):** entry "2026-10-14 09:50:37
  BST — USER DECISION: §12 row 2's "WF-701 phases A–D" = the DEPLOYMENT steps only; monitoring
  steps → P4 row 4. G2 restatement ADOPTED (re lead 09:49:20)", verbatim: *"P2 is judged on
  WF-701's deployment steps, A1–A6 and C1–C4, C6, C7 (B1/B2 shadow optional, as WF-701 says). C5
  (05 FR-310) and D1–D4 (05 FR-331, FR-333, FR-329, FR-332) are checked in P4, where roadmap :2859
  already puts "the monitoring half of WF-701". A3's deployment notification (FR-453, WK-688/P4)
  goes with them."*
- **The demo must exist — the maintainer (by delegation):** entry "2026-10-14 09:50:52 BST —
  addendum to 09:50:37 (re lead 09:50:18): the WF-701 deployment-half demo must exist; SL-[…] audit
  noted" (the elided id is a slice id the header names, elided so check 32 does not read a
  quoted header as a citation), item 2, verbatim: *"the exit demo must walk the deployment steps (A1–A6, C1–C4, C6, C7)
  scripted and rehearsable, the same standard as WF-699's journey (no faked step; 12 Oct rulings).
  A planner seat (non-building) now drafts its plan: EITHER as part of S5's acceptance (if S5's
  plan can absorb it without a re-plan) OR as one WK-674 demo slice after S5. Which one is the
  planner's recommendation; I rule on it. Its activation needs are S5 merged. Include it in the
  row-2 ETA."*
- **The memo's six decision points, ruled — the maintainer (by delegation):** entry "2026-10-14
  10:00:17 BST — RULED: WF-701 demo DP-W0..W5 (memo-wf701-deploy-demo-2026-10-14.md); PL 8002/SL
  8003 DP-1, 2, 4, 5 (re lead 09:59:09)", part (A), verbatim:
  - *"DP-W0 (b): ONE WK-674 demo slice after S5. It keeps RL-1614's separation of S5's NFR verdict
    from demo defects. Cost on row 2: +0.5 d likely, +1 d worst. Add it to eta.md's row-2 block."*
  - *"DP-W1 (a): S5 records the COMMIT acknowledgement set in the deployment Audit Event's
    after-state. This is ONE acceptance line, added to S5 by a dated plan-delta line (S5's plan is
    frozen; no body edit), so "every replica switched" is observable without P4's FR-333."*
  - *"DP-W2 (a): dev auth, demo profile only, CONDITIONAL. Task 0 shows (red first if it is
    missing) that dev-principal auth is REFUSED at startup for environment `prod`, or whatever
    existing guard covers it, cited by file:line. If no guard exists, that is a finding filed
    before the GO, not a demo workaround. The output prints that the demo runs with dev auth."*
  - *"DP-W3 (a): author now on a branch stacked on S5's head; GO and merge after S5 merges. At S5's
    merged tree, every S5-dependent red (A2, C4, replica C6) is re-shown red by its cause before
    green."*
  - *"DP-W4 (a): the declining candidate goes through the GOVERNED path only (an API-created
    version, validated, approved by two principals, deployed): no DB write, no status write. It
    must not change WF-699's journey goldens; it is its own version, with its own golden."*
  - *"DP-W5 (a): FD now (FD 8007 in D15), limb shown `KNOWN GAP C7-errors: FD-<id>`. … The FD must
    state the §0 question in full … Proposed severity MEDIUM, owner WK-1178. Its resolution (a spec
    clarification or code) must land BEFORE the 12 Nov exit demo: C7 is inside row 2, so the exit
    demo cannot carry a KNOWN GAP on it."* (The elision drops the code check and the §0 question's
    text, which are the FD's to carry, not this plan's.)
- **The id correction — the maintainer (by delegation):** entry "2026-10-14 10:00:28 BST — id
  correction to my 10:00:17 (A) DP-W5", verbatim: *"The C7-errors FD takes the NEXT free working
  id, after a free-check in its own call, never 8007. Everything else in 10:00:17 stands."* The lead
  reserved **FD 8011** for it (eta line above). FD 8011 is filed by an auditor
  (`~/gi-pricing-plan.local/channel/from-lead-2026-10-09.md`, the lead's entry "2026-10-14 10:01:48
  BST": *"seat auditor-fds to file FD 8007 AND FD 8011 (C7 errors, MEDIUM, owner WK-1178, the §0
  question) on one branch for D15/D16"*), never by this plan.
- **The lead's receipt and the id reservation:** the lead's entry "2026-10-14 10:01:15 BST — Lead:
  RECEIVED the maintainer's (by delegation) 10:00:17 + 10:00:28 rulings." in
  `~/gi-pricing-plan.local/channel/from-lead-2026-10-09.md`, verbatim in part: *"IDs: FD 8011 (C7
  errors), PL 8014 + SL 8015 (demo delta + slice) reserved → planner-wf701plan."*
- **RL-1614** (on `main`): Slice 5 holds P2's NFR-489 exit verdict on the exit tree. **PL-1620
  D0.3:** the temporary dedicated VM serves only the solo measurement runs and is deleted after
  S5's verdict. SL-8015 needs no VM.
- **Lean P2 L5** (`docs/plans/README.md`, the "One plan per Work" paragraph): a new slice is one
  dated Work-plan delta that `relates:` the Work's plan.

## Goal

Make P2's exit demo walk WF-701's deployment steps — A1–A6, C1–C4, C6 and C7 — as a scripted,
rehearsable journey to WF-699's journey's standard (no faked step), in a WK-674 slice of its own
that merges after Slice 5, and make Slice 5 leave behind the one server-side record the demo needs
to show that every replica switched. The Work's goal is `PL-1237`'s, unchanged.

## Acceptance Standard

Each item is checked by a command a fresh reviewer can run from the repository root on the named
tree.

1. **This delta passes the docs checks on its own branch.** `python3 scripts/audit-docs.py`,
   `python3 scripts/doc-index.py --check` and `python3 scripts/register-lint.py` each exit 0 at the
   branch head, except check 31's lines naming this file's working ids 8014 and 8015, which clear
   at the mint.
2. **No requirement range.** `grep -nE '(N?FR)-[0-9]+ *(-|to|–) *(N?FR-)?[0-9]+' <this file>`
   prints no line that stands for a set of ids; every id is listed individually in the Tasks table.
3. **Slice 5 carries D5.6.** `SL-1259`'s `LG-` quotes D5.6 beside the `PL-1537` and `PL-1620` rows
   it already quotes, and `git grep -n 'COMMIT acknowledgement' -- <S5's LG>` prints D5.6's quoted
   line and the line recording its red (D5.6's red, by its cause).
4. **SL-8015 closes on its own L1 (a') ledger** whose scope section quotes the SL-8015 row of this
   file's Tasks table and the slice section below verbatim, and cites this delta by its minted id:
   `git grep -l 'SL-<minted 8015>' -- docs/ledgers` prints one file by the Work's close.
5. **SL-8015's own acceptance standard** (the section "SL-8015 — acceptance standard" below) holds
   at its merge tree, item by item.
6. **The gate is green on each slice's merge tree**: the `CLAUDE.md` §11 commands, both halves,
   each exit 0, named against `origin/main...<slice branch>`.

## Global Constraints

`PL-1237`'s, `PL-1537`'s and `PL-1620`'s Global Constraints apply unchanged. In addition, for
SL-8015:

- **No faked step.** No step is replaced by a direct DB write, a status write or a fixture. The
  in-process test's `run_job` is the only in-process substitute, and the compose run removes it
  (09:50:52 item 2; 10:00:17 W4).
- **No assertion on a status code alone.** Every step reads its server-side effect back through a
  route other than the one that caused it.
- **WF-699's journey and goldens are untouched** (10:00:17 W4). `run_wf699_journey`
  (`examples/fremtpl2/journey.py:1194`) is called, never edited.
- **No new route, no spec change, no contract change.** FR-333's bundle-health surface is P4's
  (09:50:37); the quote sandbox **view** is WK-675's and is not needed.
- **Not a measurement.** The journey's < 30 s check on C4 is labelled "functional bound, not the
  NFR verdict". NFR-494's and NFR-489's verdicts are S5's on the dedicated VM (RL-1614; `PL-1620`
  D5.3), quoted by tree, never re-measured.
- **Money is integer minor units**; a golden premium is compared as an integer, never a float.
- **Never `cd`**, as every role charter says; `git -C`, `uv run --directory`, absolute paths.

## Premises re-derived at `1e260c15`

- **P1 — the dev-auth guard exists (W2's condition is met).** `Settings.require_startable`,
  `backend/src/app/config.py:204-213`: *"if self.dev_auth_enabled and self.environment in {
  Environment.UAT, Environment.PROD, }: raise ConfigInvalidError( f"dev_auth_enabled must not be set
  in {self.environment.value}. …"*. It runs at every settings load (`config.py:287`,
  `settings.require_startable()`). Its test: `backend/tests/test_api_jobs.py:120-127`,
  `test_development_identity_is_refused_outside_local`, marked `req("FR-391")`, parametrised over
  `Environment.UAT` and `Environment.PROD`. **No finding is owed before the GO on this ground.**
  Task 0 still proves it on broken input (step 0.1).
- **P2 — "environment" has two scopes here, and the demo uses both.** The guard reads
  `Settings.environment` — the **process** environment (`config.py:32-38`: `local`, `dev`, `uat`,
  `prod`). WF-701's steps act on the **Environment resource** (`/api/v1/environments/{slug}/…`,
  `backend/src/app/api/deployments.py:36`), whose slugs are also `dev`, `uat` and `prod`. S4's
  compose runs the process as `GIP_ENVIRONMENT: dev` with `GIP_DEV_AUTH_ENABLED:
  ${GIP_DEV_AUTH_ENABLED:-true}` (`deploy/docker-compose.yml:13,19` at `e1555803`), and the guard
  admits that. The demo therefore deploys to the Environment resource `prod` inside a process whose
  own environment is `dev`. The output says both, in one line (Task 4). DP-1 puts this reading to
  the maintainer, because 10:00:17 W2's "refused at startup for environment `prod`" is the process
  scope and may have been meant as the other.
- **P3 — `score.trace_produce` rides a queue no planned worker consumes.**
  `DEFAULT_QUEUE_FOR_KIND[JobKind.SCORE_TRACE_PRODUCE] = JobQueue.SCORING`
  (`backend/src/app/platform/jobs.py:79`), and `submit` uses that map
  (`jobs.py:122`, `queue=queue or DEFAULT_QUEUE_FOR_KIND[kind]`). S4's worker is
  `--queues compute` at `e1555803` (`deploy/docker-compose.yml:145`), and `PL 1690` E4.2 makes it
  `--queues default,compute` with a shape test asserting the queue set **equals** `{default,
  compute}`. `scripts/demo.py`'s `worker_command()` also consumes `default,compute` only. So on
  both run modes outside the in-process test, a sampled trace stays pending and `GET
  /api/v1/traces` (complete traces only, `backend/src/app/api/traces.py:167`) never returns it:
  C7 cannot pass. This is the defect class `PL 1690` E4.3 was ruled to catch ("no consumer on a
  queue"). The memo's fresh-stack need (d) assumed E4.2 covered it; it does not. **DP-2.** The same
  holds for `JobQueue.IO` (`DATASET_INGEST`, `EXPORT_REGULATORY`, `BLOB_GC`, `jobs.py:59,85,86`),
  which no WF-701 step needs; it is named for the lead, not taken here.
- **P4 — the `/score` rate limit admits C7's volume by default.** `ScoreRateLimitDep`
  (`backend/src/app/api/score.py:161`, applied at `:393`) reads
  `scoring.default_client_rate_limit_rps`, whose default is `None` (`backend/src/app/platform/
  settings.py:233-241`: *"Unset by default: with no limit the request is admitted without a counter
  call (`RL-1347` rule 2)"*), or the Service Account's own `rate_limit_rps`. The journey creates
  its Service Accounts without `rate_limit_rps`. Task 0 re-reads both at S5's merged tree (S4
  changes the limiter for the management API, `PL 1690` E4.1), and the journey paces under any
  limit it finds; it never raises one.
- **P5 — D5.6's record has an ordering and a shape question S5 must answer.** Today the deploy's
  Audit Event is written **inside** the deploy transaction, with `after=` the `Deployment` model's
  dump (`backend/src/app/platform/deployments.py:524-554`). S5's switch (`PL-1237` Task 5: "Each
  worker hydrates off the event loop and acknowledges, then swaps its one `live` reference and
  acknowledges") produces COMMIT acknowledgements during the switch. For the COMMIT set to be in
  `deployment.created`'s after-state, the COMMIT round must complete before that transaction
  commits, and the set needs a place in the `Deployment` shape, which `model-schema` owns
  (`CLAUDE.md` §2: nobody hand-writes a shape that exists there). **DP-3.**
- **P6 — the declining candidate is buildable from the shipped grammar.** A `constraint` step with
  `on_violation: Literal["clamp", "decline", "error"]` and a `reason_code`
  (`packages/model-schema/src/model_schema/rating.py:415-420`); `ScoringOutcome = Literal["quoted",
  "declined", "error"]` (`model_schema/scoring.py:75`). `git grep -n -i decline origin/main --
  examples/fremtpl2` prints nothing, so no seeded version declines today.
- **P7 — C7's errors limb is FD 8011's.** On `POST /api/v1/score`, a `ValueError` from `score_one`
  is re-raised as a problem (`score.py:421-427`) before `_maybe_sample_trace` runs (`:429`), so
  an errored quote is never sampled from this route. 10:00:17 W5 rules the limb `KNOWN GAP` until
  FD 8011 is resolved, and requires that resolution before the 12 Nov exit demo.
  *Amended 2026-10-14 (docs batch D16, in place, the plan being pre-merge):* FD 8011 is resolved by
  RL 8019, confirmed by the maintainer (by delegation) in the entry "2026-10-14 10:26:21 BST" in
  `to-lead.md`: the limb is walked, not a `KNOWN GAP`. A refused quote is not traced, so the
  slice asserts the 422 refusal, the absence of that `quote_id` from `GET /traces`, and the ruled
  line `C7-errors: refused, not traced (FR-259, RL 8019)`. The sentence above is kept as the
  premise it was.
- **P8 — the band for C7's 1 % limb, computed exactly.** For N = 2,000 quoted quotes at p = 0.01
  (the default, `settings.py:217-219`), the count X of persisted quoted traces is Binomial(2000,
  0.01), mean 20. The pre-registered band is **[3, 45]**. Computed with exact rational arithmetic
  (`fractions.Fraction`, `math.comb`): P(X ≤ 2) = 4.196e-07, P(X ≥ 46) = 3.833e-07, P(outside) =
  8.030e-07. At p = 0.0 the count is 0, outside the band, so the band is not vacuous (R6).

## Tasks

| Order | Slice | Scope (what the `LG-` quotes) | Requirements, each id | Depends on | Size |
|---|---|---|---|---|---|
| 1 | `SL-1259` — Slice 5 (changed) | `PL-1537` row 2 and `PL-1620` D5.1 to D5.5 as they stand, **plus D5.6 below** | unchanged from `PL-1620`; D5.6 adds no id (it serves `03` §3.10: FR-268's "every replica" observability for SL-8015) | unchanged | + one acceptance line |
| 2 | SL-8015 — the WF-701 deployment-steps demo | the section "SL-8015 — the slice" below | `03` §3.7: FR-250; `03` §3.8: FR-258, FR-259, FR-262; `03` §3.10: FR-267, FR-268, FR-272 (audit limb only); `03` §9: NFR-494 (functional bound only; the verdict is S5's); `07` §3.5: FR-429; `06` §3.2: FR-354 | activation needs 1 to 6 below | 1 + a compose build window, no VM |

Requirements **not** taken, each named: `03` FR-269 (rollback, WF-701 Phase H), `03` FR-271
(shadow, Phase B, optional with `SL-1260`), `05` FR-310 (C5), `05` FR-329, FR-331, FR-332 and FR-333
(D1–D4), and `07` FR-453 (A3's notification) — all P4 or optional (09:50:37).

### Slice 5 (`SL-1259`) — changes since `PL-1620`

**Dated line, 2026-10-14, on `PL-1620` (frozen; not edited), on the maintainer's (by delegation)
entry "2026-10-14 10:00:17 BST", (A) DP-W1 (a):**

- **D5.6 — the COMMIT acknowledgement set is recorded server-side.** S5 records, in the
  deployment Audit Event's after-state (`deployment.created`, and `deployment.rolled_back` for a
  rollback, `PL-1537` R5.7), the set of replicas that acknowledged COMMIT for that switch, each
  named by a stable replica identifier, so "every replica switched" is observable without P4's
  FR-333. Acceptance: one test reads the Audit Event back through `GET /api/v1/audit` and asserts
  the set equals the replicas subscribed to the switch; **its red, by its cause:** the same switch
  with one replica's COMMIT acknowledgement suppressed records a set short by that replica, and the
  test fails naming it. `PL-1620` Acceptance item 5 holds unchanged; this line is added beside it.
  How the set reaches the after-state (P5) is DP-3's; S5 states its answer in its `LG-` before
  the code, and if DP-3's recommendation cannot hold, S5 stops and raises it (`CLAUDE.md` §0)
  rather than recording something else under this line.

Nothing else in Slice 5 changes. SL-8015 edits no S5 file.

### SL-8015 — the slice

**Scope in one sentence.** After Slice 5 merges, a scripted journey walks WF-701's A1–A6, C1–C4, C6
and C7, in order, on the state WF-699's journey leaves, in two run modes, each step asserting its
status code and a server-side effect read back through another route.

**The frame (Task 0 confirms it; DP-4).** Live: WF-699's `rv3`, which `deploy_and_score`
(`examples/fremtpl2/journey.py:1084`) makes live in `dev`, `uat` and `prod`. Candidate **K1**: a
second approved Rating Version carrying the `min_premium 150 -> 180` change
(`examples/fremtpl2/rating/fremtpl2-rate.changes.json:39`), built through the same API calls as
WF-699's version builds. Both shipped algorithms carry a `MIN_PREMIUM_APPLIED` reason code
(`fremtpl2-rate.rating-algorithm.v1.json:403`, `v2.json:465`). Candidate **K2** (C7's declines
limb, W4): its own version, adding one `constraint` step with `on_violation: "decline"` (P6),
created, validated, approved by two distinct principals and deployed through the API, with its own
golden quote; WF-699's goldens are untouched.

**Per step: the call, the assert, the served capability.** Routes are under `/api/v1`. "Read back"
names the second route.

| # | The call | The assert (status **and** read-back effect) | Served by | Needs S4/S5 |
|---|---|---|---|---|
| C2 (first) | Before A1: the prod request-and-deploy path for K1, which has no `uat` deployment | 409, problem `code == "PROMOTION_ORDER_VIOLATION"`; Task 0 records which call refuses (request or deploy). Read back: `GET /environments/prod/deployments` still lists `rv3` first | `platform/deployments.py:474-496` (the code at `:495`); `model_schema/approvals.py:342` | no |
| C3 (i) | Deploy a compiled, unapproved version to `uat` | 409 `DEPLOY_REQUIRES_APPROVAL`; read back: `uat`'s list unchanged | `platform/deployments.py:557-607` (the code at `:559`) | no |
| A1 | `POST /environments/uat/deployments` `{rating_version_ref: K1, reason}` | 201; read back: `GET /environments/uat/deployments` lists K1 first, its `bundle_hash` equal to K1's compiled `content_hash` | `api/deployments.py:67-87`; list `:90-113` | no |
| A2 | The same deploy, with a concurrent `POST /score` stream through `lb` on a `uat` key across the switch | (i) every response's `bundle_hash` is old or new; (ii) after the deploy returns, none carries the old hash; (iii) D5.6's COMMIT set, read through `GET /audit`, equals the `api` containers `docker compose ps` reports | S5's switch and D5.6; S4's `lb` and `api` replicas | **yes** |
| A3 | `GET /audit` filtered to the deployment | one `deployment.created` event, before and after state, the deploy `reason` as justification, the deployer as actor | `platform/deployments.py:537-554`; `api/audit.py:156` | no |
| A4 | `POST /score`, `uat`-bound `X-API-Key`, no `rating_version_ref` | 200, `outcome == "quoted"`, `bundle_hash` is K1's, a `premium_ladder` and `outputs` present | `api/score.py:378-431`, `_serving_ref` `:195`; the key from `POST /service-accounts` with `score:execute` | no |
| A5 | `POST /score/compare` `{base: rv3, comparison: K1}`, once per quote, over K = 200 real freMTPL2 policies from the seed's dataset | each 200 with a step-level `TraceDiff`; at least one premium differs; totals and the changed count printed | `api/score.py:460-506` (FR-262 is one quote per call) | no |
| A6 | From A5, the quote with the largest relative move whose K1 trace applies `MIN_PREMIUM_APPLIED` and whose `rv3` trace does not; re-score it with `options.trace=true` | K1's trace shows the min-premium step applied with that reason, `rv3`'s does not; step id and % move printed; **WF-701's "14 %" is not asserted** (example text) | `options.trace`, `api/score.py:410-419`; `TraceStep`, `model_schema/scoring.py:168-186` | no |
| C3 (ii), (iii) | (ii) Deploy K1 to prod against an undecided request; (iii) read K1's approval request | (ii) 409 `DEPLOY_REQUIRES_APPROVAL`; (iii) two **distinct** approvers | default policy `approvers_required=2` (`model_schema/approvals.py:429-430`); distinct approvers `platform/approvals.py:464-469` | no |
| C1 | `POST /environments/prod/deployment-requests`, decision `approve` by a prod approver, `POST /environments/prod/deployments` with `deployment_request_ref` | 201; read back: `GET /environments/prod/deployments` lists K1 first | `api/deployments.py:42-87` | no |
| C4 | C1's deploy with the stream running on a prod key across the switch; the deploy call's wall time recorded | A2's (i) to (iii) on prod, plus the `deployment.created` event; elapsed printed and checked **< 30 s as a functional bound, not the NFR-494 verdict** | as A2 | **yes** |
| C6 | About 50 `POST /score` on a prod key, no ref, through `lb` | 200, every `bundle_hash` K1's, `outcome == "quoted"`, one golden quote's `payable_premium` equal to its integer expected value | `api/score.py:195-230` | replicas: **yes** |
| C7 (i), (ii) | Prod `rating.trace_sample_rate` left at its default 0.01; N = 2,000 quoted quotes on the prod key; then `GET /traces?rating_version=…&from=…&to=…` as an analyst bearer, polled until the count is stable | (i) the count is inside [3, 45] (P8), with N, p and the band printed; (ii) every persisted trace's `bundle_hash` is K1's | `api/score.py:509-580`; `platform/traces.py:78-99`; completion by `score.trace_produce` (a worker on `scoring`, DP-2); `api/traces.py:167` | the worker queue (DP-2) |
| C7 (iii) declines | K2 deployed `uat` then prod through the governed path; M = 20 quotes that K2 declines, on the prod key, rate unchanged | exactly M persisted traces with `outcome == "declined"` for K2 (the 100 % floor), read through `GET /traces` | `traces.decide_sampling` floor, `platform/traces.py:94-97` | the worker queue (DP-2) |
| C7 (iv) errors | With the prod key, `POST /api/v1/score` one quote that omits a declared non-nullable input; after C7's trace poll is stable, `GET /traces` | 422 with problem `code` `INPUT_CONTRACT_VIOLATION`; no listed trace carries that quote's `quote_id`; the one printed line, asserted, is exactly `C7-errors: refused, not traced (FR-259, RL 8019)`. The no-row proof is a backend test that reads `scoring_traces` directly, and the demo cites it by name. No fault is caused in `prod`; nothing about errors at 100 % is asserted | P7 as amended; RL 8019 §3 and its "What it obliges" section | — |

**The two run modes** (the memo's §2, kept):

1. **In-process test** `backend/tests/test_wf701_journey.py`, the harness of
   `backend/tests/test_wf699_journey.py` (Starlette `TestClient`, the seeded world, `run_job` running
   Jobs in process). It walks every in-scope step, in order, after `run_wf699_journey`, and runs in
   the normal gate as a regression guard on the sequence and the refusals. It has one process and no
   replicas, so A2 (iii), C4 (iii) and C6's replica limb are each printed and asserted as exactly one
   line, `COMPOSE-ONLY A2/C4/C6 replica limb`, never as `ok`. No step is absent.
2. **The rehearsable demo run** against S4's compose stack: `docker compose -f deploy/docker-compose.yml
   --profile app up --scale api=2` (S4's comment at `deploy/docker-compose.yml:116` at `e1555803`), with `lb`,
   `api`×2, `worker` (on the queues DP-2 settles), `postgres`, `redis`, `minio`; then
   `uv run python scripts/demo.py --journey wf-701 --target compose`. It seeds through
   `examples/fremtpl2/seed.py`, runs WF-699's journey and then WF-701's over real HTTP to `lb`.
   Behind `GIP_DEPLOY_TESTS=1` in the test suite, in the form of `PL 1690` E4.3's compose smoke; it
   cannot run in CI, so the `LG-` quotes the build window's run by command, tree and output.

**Task 0 — readiness, at S5's merged tree, before any red** (each result in the `LG-`, by command
and output):

- [ ] **0.1 — W2's guard, on broken input.** Run `uv run pytest -q
  backend/tests/test_api_jobs.py -k development_identity_is_refused` and quote its pass. Then, in a
  scratch copy only (never committed), delete `Environment.PROD` from the set at
  `backend/src/app/config.py:206-209`, re-run, and quote the red line naming `prod`; restore. Cite
  `config.py:204-213` and `:287` by line at that tree. If the guard is gone at that tree, stop: a
  finding is filed before the GO (W2), never a demo workaround.
- [ ] **0.2 — compose auth.** Quote `GIP_ENVIRONMENT` and `GIP_DEV_AUTH_ENABLED` from the merged
  `deploy/docker-compose.yml` (P2), and record DP-1's ruling.
- [ ] **0.3 — the `/score` rate limit.** Quote `scoring.default_client_rate_limit_rps`'s default
  and the Service Account `rate_limit_rps` the journey sets (P4). If a limit applies, state the
  pacing that fits C7's 2,000 quotes and the two streams under it; if none fits, that is a finding
  against the default, not an override.
- [ ] **0.4 — the `trace_produce` queue.** Quote `jobs.py`'s entry for `SCORE_TRACE_PRODUCE` and
  the merged compose worker's `--queues`, and record DP-2's ruling and the change it makes.
- [ ] **0.5 — the frame.** Confirm `rv3` is live in `prod` after `run_wf699_journey`, that K1 is
  buildable through the API, and that A5's K = 200 sample holds a quote where K1 binds the minimum
  premium and `rv3` does not; if none does, grow K and record the value (never fabricate the quote).
  Confirm K1 and K2 are not in the dislocation baseline pair WF-699 uses
  (`journey.py:1038`, baseline `fremtpl2-demo@1`).
- [ ] **0.6 — S5's surface.** Quote the D5.6 field path in the merged after-state, the replica
  identifier's form, and how the in-process harness sees S5's switch (one replica).
- [ ] **0.7 — how the seed reaches the compose stack** (database and blob endpoints from the host),
  by the command used.

**Tasks** (each ends with a testable deliverable; reds before greens):

- [ ] **T1 — the journey skeleton and its line rules.** Create `examples/fremtpl2/journey_wf701.py`
  with `run_wf701_journey(client, record, *, log)`, reusing `JourneyStepFailed` and `Skip` from
  `examples/fremtpl2/journey.py:44,76` by import (no second definition). Its ruled lines are exactly
  `COMPOSE-ONLY A2/C4/C6 replica limb` (in-process only) and the walked limb line `C7-errors: refused, not traced (FR-259, RL 8019)`.
  Test first: R1, then a test that an unruled skip fails the journey (the form of
  `test_wf699_journey.py:57`).
- [ ] **T2 — the deliberate refusals** C2 and C3 (i), (ii): R2, R3 first.
- [ ] **T3 — A1, A3 to A6, C1, C3 (iii), C6 (one process)** in order, each with its read-back.
- [ ] **T4 — C7 (i) and (ii)**, the band test with R6 first; **C7 (iii)** with K2 through the
  governed path, R7 first; **C7 (iv)** as the walked limb of RL 8019 §3 (the 422 refusal, the
  trace-list absence, the ruled line; no `KNOWN GAP C7-errors` line exists). The journey's first output line is
  *"WF-701 demo: process environment dev with development identity (dev auth); deployments target
  the Environment resources uat and prod"* (W2's "the output prints that the demo runs with dev
  auth", and P2).
- [ ] **T5 — A2 and C4 (and C6 through replicas)** against S5's switch: the stream, the
  old-or-new assertion, D5.6's set against `docker compose ps`. R4 in-process (an injected
  response), R5 on compose. **At S5's merged tree, each S5-dependent red (A2, C4, replica C6) is
  re-shown red by its cause before green** (W3).
- [ ] **T6 — `scripts/demo.py --journey wf-701 [--target compose]`.** `JOURNEYS`
  (`scripts/demo.py:56`) gains `"wf-701"`; `--target compose` points the journey at the running
  stack's `lb` and refuses (R9) when it is not up, naming the missing services; the local mode's
  `worker_command()` consumes the queues DP-2 settles. `backend/tests/test_demo_command.py` covers
  the new choices. R8 first.
- [ ] **T7 — the rehearsal.** One compose run, alone on the box, no gate slot held, elapsed
  recorded against the pre-registered target **WF-701's part ≤ 10 min wall** (a miss is recorded,
  not tuned away); the rehearsal checklist in `PL-1544`'s form, run once in full on the slice head,
  quoting S5's `LG-` NFR-494 and NFR-489 lines by tree.

**Reds, each seen red by its cause before the code that turns it green** (each quoted in the `LG-`
with its failure line as printed; a matching status with a different cause is a plan defect,
`README.md` convention 2):

- **R1.** `uv run pytest -q backend/tests/test_wf701_journey.py` fails at collection because
  `run_wf701_journey` does not exist.
- **R2.** C2: first written expecting 201, it fails with 409 and problem `code
  PROMOTION_ORDER_VIOLATION`: the refusal is the server's, not the test's.
- **R3.** C3 (i) and (ii): R2's method, for `DEPLOY_REQUIRES_APPROVAL`.
- **R4.** A2 (i) / C4 (i): an injected response carrying a third hash fails the old-or-new
  assertion (the proof `PL-1237` Task 5's gate outline asks of S5, repeated on the journey).
- **R5.** A2 (iii) / C4 (iii) on compose: the set read against 3 with `api`×2 (or one replica's
  COMMIT suppressed) fails, naming the missing replica.
- **R6.** C7 (i): prod `rating.trace_sample_rate` set to 0.0 through the settings API: the count
  is 0, outside [3, 45], and the step fails naming the band.
- **R7.** C7 (iii): before K2 exists the step fails because no declined trace is found; and with the
  floor's branch in `traces.decide_sampling` (`platform/traces.py:94-97`) removed in a scratch copy
  (never committed), M declined quotes persist fewer than M traces and the step fails.
- **R8.** With the A1 body refused, `scripts/demo.py --journey wf-701` exits non-zero with a line
  starting `A1:` (the form of `PL-1544` Acceptance 6).
- **R9.** `--journey wf-701 --target compose` with S4's services down refuses, naming them.

**SL-8015 — acceptance standard**

1. `backend/tests/test_wf701_journey.py` has a module docstring naming
   `docs/workflows/WF-00701-deploy-and-monitor.md`, and `req` markers for FR-250, FR-258, FR-259,
   FR-262, FR-267, FR-268, FR-272, FR-354, FR-429 and NFR-494, each listed separately.
   `uv run pytest -q backend/tests/test_wf701_journey.py` exits 0. R1, R2, R3, R4, R6 and R8 are
   quoted in the `LG-`.
2. Every in-scope step (A1–A6, C1–C4, C6, C7) is walked in order, each asserting its status and its
   read-back effect (the step table). The only ruled lines are `COMPOSE-ONLY A2/C4/C6 replica limb`
   (in-process) and `C7-errors: refused, not traced (FR-259, RL 8019)`, and the test asserts them;
   no step is absent and no other skip line exists, and no line contains `KNOWN GAP C7-errors`.
   If the RL 8019 T1 text (the FR-259 clarification in `03`) is absent from `main` at the GO, the
   slice keeps a `KNOWN GAP` line, and the exit demo cannot pass C7 (RL 8019's last violation).
3. The refusals match on problem `code`: C2 `PROMOTION_ORDER_VIOLATION`; C3 (i) and (ii)
   `DEPLOY_REQUIRES_APPROVAL`.
4. **On compose** (`GIP_DEPLOY_TESTS=1`, S4's stack, `api`×2), `uv run python scripts/demo.py
   --journey wf-701 --target compose` exits 0 and prints one line per step: A2 and C4 show (i), (ii)
   and (iii) with a set of 2; C6 about 50 prod quotes on K1's hash; C7 the count inside [3, 45]
   with N, p and the band, and exactly M declined traces. R5, R7 and R9 are quoted. The run is alone
   on the box, no gate slot held, elapsed recorded against ≤ 10 min.
5. **The NFR verdicts are not this slice's.** The rehearsal quotes S5's `LG-` NFR-494 and NFR-489
   lines by tree; the journey's < 30 s line reads "functional bound, not the NFR verdict".
6. The rehearsal checklist (`PL-1544`'s form) is run once in full on the slice head and recorded by
   command and tree.
7. The gate is green on the merge tree: `CLAUDE.md` §11, both halves, each exit 0, named against
   `origin/main...<slice branch>`.
8. **The write set**, `git diff --stat origin/main...HEAD`, lies inside: `examples/fremtpl2/
   journey_wf701.py`; K2's and K1's demo-data files under `examples/fremtpl2/rating/` (new files
   only; no shipped file edited); `scripts/demo.py`; `backend/tests/test_wf701_journey.py`;
   `backend/tests/test_demo_command.py`; the compose runtime test under `backend/tests/` beside
   `PL 1690` E4.3's; the change DP-2 rules, if it rules it into this slice; and the slice's `LG-`.
   It touches no S5 file, no spec, no contract, and not `examples/fremtpl2/journey.py`.

**Activation needs** (each quoted in the GO request):

1. `SL-1259` (S5) **merged** (09:50:52 item 2), with D5.6 met in its `LG-`.
2. `SL-1258` (S4) merged (implied by 1; named because the compose mode rests on it).
3. `PL 1690` minted on `main` (D14, #1298), so E4.2's worker and E4.3's smoke are on the tree.
4. DP-1 to DP-3 ruled (DP-4 to DP-6 are non-blocking; each has a recommendation that stands
   unless ruled otherwise).
5. RL 8019 minted (its minted id fills the walked limb's line), and its T1 text on `main`.
6. This delta ACKed and minted; a build slot and the single gate; one compose build window booked
   in `eta`.

**Authoring before activation (W3).** Authoring may start before need 1 on a branch that is
re-stacked onto S5's head (DP-5 for the base while no S5 branch exists). GO and merge follow S5's
merge; every S5-dependent red (A2, C4, replica C6) is re-shown red at S5's merged tree before
green.

## Decision points

| # | Question | Options | Recommendation | Kind | Blocking | Resolved by |
|---|---|---|---|---|---|---|
| DP-1 | W2 reads "dev-principal auth is REFUSED at startup for environment `prod`". The guard (P1) reads the **process** environment; the demo deploys to the **Environment resource** `prod` in a process whose environment is `dev` (P2). Is that the demo W2 permits? | (a) Yes: process `dev` with dev auth, Environment resources `uat`/`prod` inside it, both printed in the output's first line (T4). (b) No: the process runs `prod`, which needs OIDC through the reference Keycloak, TLS termination and an issuer (`config.py:215-226`) — the memo's DP-W2 (b), which W2 did not choose. | **(a).** It is the only form the shipped guard allows with dev auth, and Keycloak login is not a WF-701 step. | reading of a ruling | **yes** | the maintainer |
| DP-2 | `score.trace_produce` routes to `scoring` (P3), and neither S4's worker (`PL 1690` E4.2: the set equals `{default, compute}`) nor `demo.py`'s consumes it, so C7 cannot pass outside the in-process test. Who adds the consumer? | (a) **S4**, at its GO (still open): the worker consumes `default,compute,scoring`, E4.2's shape test asserts that set, and E4.3's smoke stands; `demo.py`'s local worker gets `scoring` in SL-8015 (T6). (b) A separate compose `worker-scoring` service (FR-405's pools), added by SL-8015, which then edits S4's compose file after S4 merges. (c) SL-8015 runs a one-off `scoring` worker as a test fixture, as E4.3 runs beat; the demo command starts it too. | **(a).** It is the defect class E4.3 was ruled to catch ("no consumer on a queue"), found before S4's GO, and S4 owns FR-415's worker; (b) widens a demo slice into S4's file, (c) makes the demo pass on a stack the product does not ship. Whether it is also an `FD-` or a backlog row is the lead's (Lean P2 L3). | scope / finding | **yes** (C7 cannot pass otherwise) | the lead at S4's GO; the maintainer if contested |
| DP-3 | D5.6 (W1) records the COMMIT set in `deployment.created`'s after-state. Today that event is written inside the deploy transaction with `after=` the `Deployment` model (P5). How does the set get there? | (a) S5's switch completes its COMMIT round before the deploy transaction commits, and the set is a field added to `Deployment` in `model-schema` (so S5's write set adds `packages/model-schema/` and the regenerated contract). (b) The after-state carries the PREPARE set (known before commit), and the COMMIT set goes on a second, catalogued Audit Event after the switch (a `06` catalogue append, a spec change in S5). (c) The set is a column on the Deployment row, filled after COMMIT, read back through `GET /environments/{env}/deployments`; the after-state names the PREPARE set. | **(a)**, as W1 is worded, **on one condition**: S5's `LG-` states, before the code, what happens if the transaction fails after replicas have switched. If S5 cannot make that safe, it stops and the decision-maker rules (b) or (c) (`CLAUDE.md` §0); no S5 code records a different set under D5.6 without that ruling. | mechanism of a ruling | **yes**, for S5's D5.6 | the decision-maker, at S5's GO |
| DP-4 | The frame: which version is live and which is the candidate? | (a) `rv3` live, K1 (`min_premium 150 -> 180`) candidate; (b) `fremtpl2-demo@1` live, `rv3` candidate; (c) `rv3` live, another new candidate | **(a)**, subject to Task 0.5; (b) re-deploys a version WF-699 already deployed, which A2 needs to be new | demo design | no | the recommendation stands unless ruled |
| DP-5 | W3 says "author now on a branch stacked on S5's head", but no S5 branch exists at `1e260c15`, and S4 (`origin/sl-1258-wk674-s4` @`e1555803`) is not GO'd. What is the authoring base? | (a) Branch from `main` now; author T1 to T4 and T6 (no S4 or S5 dependency); re-stack onto S5's head when S5 pushes, then author T5. (b) Stack on S4's authored head now. (c) Wait for S5's branch. | **(a).** It keeps W3's intent (authoring early, GO after S5) without stacking on a branch that is itself unGO'd. | sequencing | no | the lead |
| DP-6 | The pre-registered volumes | K = 200 (A5), about 50 (C6), N = 2,000 with band [3, 45] (C7 (i), P8), M = 20 (C7 (iii)) | **As listed**; K grows only by Task 0.5's rule, recorded | demo design | no | the recommendation stands unless ruled |

A plan is "`draft` while decision points are open, `active` on freeze" (`document-ids.md` §1.6,
the PL `map`/`leaf` row). DP-1, DP-2 and DP-3 are open and blocking, so this delta stays `draft`
until each is ruled and the rulings are cited here by a dated activation line.

## Rulings recorded (2026-10-14, docs batch D16)

This delta is pre-merge, so it is edited in place. These are the rulings given by the maintainer
(by delegation) in `to-lead.md`, recorded here at the sites the decision-point table names. The
table above keeps its recommendations as written, and each ruling below is read with its row.

- **DP-1: ruled (a).** Entry "2026-10-14 10:14:13 BST", item 2. The guard exists
  (`config.py:204-213`, called at `:287`, `test_api_jobs.py:120-127`) and refuses dev auth when the
  PROCESS environment is `prod`. The demo is a dev process that deploys to the Environment
  RESOURCE `prod`, which is a legitimate demo. The first output line prints BOTH facts verbatim:
  the process environment (`dev`, dev auth ON) and the target Environment (`prod`). Nobody can then
  read the demo as a production-auth run. Task 4's first line is written to that ruling.
- **DP-2: ruled (a), amended to a DERIVED consumer set.** Entry "2026-10-14 10:13:50 BST", item (a)
  AMENDED. S4, at its GO, makes the compose worker(s) consume EVERY queue in the routing table. E4.2's
  shape test asserts that the consumed queues are a superset of
  `set(DEFAULT_QUEUE_FOR_KIND.values())`, derived from the table in
  `backend/src/app/platform/jobs.py` and never a hard-coded `{default, compute, scoring}`. This
  amends the E4.2 set that `PL 1690` ruled (`{default, compute}`), by a dated line in S4's `LG-`
  and the next delta. The same entry widens the gap: `DATASET_INGEST` routes to the `io` queue, which
  no worker consumes either. `scripts/demo.py` takes the same derived set, so T6 below consumes
  that set and not `default,compute,scoring` as the DP-2 row's option (a) says. Whether the
  `demo.py` change is S4's write set or this slice's is the planner's call, and it must land before
  the G2 rehearsal is re-run on the merged tree. One finding covers the class (the lead's, with an id
  in 8000 to 8299), and S4 discharges it.
- **DP-3: ruled (a), CONDITIONAL, at S5's GO.** Entry "2026-10-14 10:14:13 BST", item 3.
  `deployment.created` is written inside the deploy transaction (`platform/deployments.py:524-554`).
  So recording the COMMIT acknowledgement set needs a write after COMMIT or a second event, plus a
  `model-schema` field. S5's write set widens by that field: it goes through contract-guard, and
  `generated.json` is checked at the ACK. **The condition:** S5's plan states, BEFORE the build, what
  is recorded when the transaction fails AFTER the switch. There is no silent "all switched". If
  that cannot be stated, STOP, and a decision-maker (effort high, separate CLI) rules it at S5's GO.
- **DP-5: not ruled here.** The same entry notes it as the lead's. The recommendation (a) stands as a
  recommendation until the lead rules.

DP-1 and DP-3 are therefore ruled (DP-3 conditionally) and DP-2 is ruled, so the "open and blocking"
sentence above holds only for what is not yet cited by a dated activation line. This delta stays
`draft` until the lead gives that line.

## Hand-off (not this plan's writes)

- **FD 8011** (C7 errors, MEDIUM, owner WK-1178, the §0 question): filed by an auditor (the lead's
  10:01:48 entry), never by this plan.
- **D5.6 into S5's `LG-`:** S5's executor, at S5's GO.
- **DP-2 into S4:** the lead, at S4's GO, if ruled (a); `PL 1690` is frozen once minted, so the
  change is a dated line in S4's `LG-` or a further delta, the lead's choice.
- **WK-674's roadmap row** lists this delta's minted id (L5): the lead.
- **eta.md's row-2 block** already carries W0's +0.5 d / +1 d (the lead's eta line "2026-10-14
  10:01:15 BST lead:
  §12 ROW 2 ETA amended").

## Self-review

- **Spec coverage.** Each in-scope WF-701 step has a row in the step table and a task: A1 (T3), A2
  (T5), A3 (T3), A4 (T3), A5 (T3), A6 (T3), C1 (T3), C2 (T2), C3 (T2, T3), C4 (T5), C6 (T3, T5), C7
  (T4). Its requirement, by `docs/workflows/WF-00701-deploy-and-monitor.md` §2: A1 and C1 FR-267;
  A2 FR-268 and NFR-494; A3 FR-272; A4 and C6 FR-250; A5 FR-262; A6 FR-258; C2 FR-429; C3 FR-354;
  C4 NFR-494; C7 FR-259. Each id is defined (`03` §3.7, §3.8, §3.10, §9; `07` §3.5; `06` §3.2) and
  listed individually in the Tasks table and acceptance item 1.
- **Rulings at every site** (`README.md` convention 5). W0: the Tasks table and activation need 1.
  W1: D5.6, acceptance item 3, DP-3. W2: P1, Task 0.1 and 0.2, T4's first line, DP-1. W3: authoring
  paragraph, T5, DP-5. W4: frame, step C7 (iii), T4, write set, Global Constraints. W5: P7, step C7
  (iv), T1, acceptance item 2, Hand-off.
- **Placeholders.** "RL 8019" in the C7-errors line is a working id, replaced at the mint by the
  ruling's minted id; "<S5's LG>" and "<slice branch>" are read at the slice. No other.
- **Literals** were read at `1e260c15` (or the named branch) by path and line: every route, code,
  enum member, setting key and default in the step table and premises.
- **Not done here:** the memo's §3 shape argument and ETA figures, which W0 has ruled.
