---
id: PL-8022
family: plan
kind: map
title: WK-674 — Slice 4 consumes every routed pool and handles every routed kind: E4.2 amended to a derived consumer set, the io and scoring reds on compose asserting succeeded, the trace handler and its derived guard, demo.py on the same set, and the FR-405 pool split for the maintainer's ruling — Work-plan delta
status: draft                  # draft → active → superseded | retired (§1.2a)
created: 2026-10-14
owner: planner
tree: ba68a6daf3cfb7634258915a6e542bc658ae3f62
phase: P2
work: WK-674
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1237, PL-1537, PL-1666, PL-1688, PL-1690, SL-1258, SL-1689]
---

# PL-8022 — WK-674 Slice 4: every routed pool consumed (Work-plan delta, amends PL-1690 E4.2)

> **For agentic workers:** this is a **dated Work-plan delta** under Lean P2 L5. It does not replace
> `PL-1237`, `PL-1537`, `PL-1620`, `PL-1666` or `PL-1690`, and it leaves all their bodies unedited.
> It `relates:` them and changes **Slice 4 (`SL-1258`) only**, plus one activation line of
> `SL-1689` (§"Effect on SL-1689"). **Read `PL-1666`, then `PL-1690`, then this file.** Where they
> differ, this file is the later statement: **E4.2 below replaces `PL-1690` E4.2 whole**; `PL-1690`
> E4.1 and E4.3 stand, and E4.4 to E4.6 here add to them. Slice 4 stays one PR under L1 (a'). Its
> `LG-` quotes E4.2 and E4.4 to E4.6 beside the rows it already quotes, and carries the dated line
> the maintainer's (by delegation) entry names (§Authority). REQUIRED SUB-SKILL and bound skills:
> `PL-1666`'s list, unchanged.

Working id PL 8022, reserved by the lead in `eta.md`, "2026-10-14 10:32:05 BST lead: RESERVED
working id PL 8022". Written 2026-10-14 by the planner (planner-s4queues). Evidence was read at
`origin/main` `ba68a6da` and at the authored S4 branch `origin/sl-1258-wk674-s4` `e1555803`.

## Authority

- **The amendment:** the maintainer's (by delegation) entry in `to-lead.md`, "2026-10-14 10:13:50
  BST — Unconsumed worker queues: the finding is WIDER (io too); (a) AMENDED to a DERIVED consumer
  set; (b) one finding for the class", item (a), verbatim: "S4 at its GO makes the compose
  worker(s) consume EVERY pool in the routing table, and E4.2's shape test asserts **consumed
  queues ⊇ `set(DEFAULT_QUEUE_FOR_KIND.values())`**, DERIVED from the table, never a hard-coded
  {default, compute, scoring}. A hard-coded set is how this gap got blessed, and the next new pool
  would repeat it. This amends PL-1690's ruled E4.2 set (dated line in S4's LG and the next delta).
  Pool → worker split (one worker for all, or per-pool workers as FR-405 intends: compute few and
  fat, scoring many and thin) is S4's planner's to recommend, and I rule it. Reds by cause on
  compose: one `dataset.ingest` job AND one `score.batch` job (or `trace_produce`) each reach a
  terminal state through a REAL worker (no inline execute_job); both are red on main's compose by
  "never consumed"." Its `scripts/demo.py` paragraph, verbatim: "its worker command gets the same
  derived set (the demo is not exempt). Whether that is S4's write set or the WF-701 demo slice's
  is the planner's call, but it must land before the G2 rehearsal is re-run on the merged tree."
- **The correction and DP-Q3:** the maintainer's (by delegation) entry in `to-lead.md`, "2026-10-14
  10:36:42 BST — Unregistered trace handler: DP-Q3 → S4; inside FD 8021; my 10:13:50 "terminal
  state" CORRECTED to `succeeded`". Its correction, verbatim: "**My error, corrected:** my 10:13:50
  red asserted the jobs "reach a terminal state". `failed` is terminal, so the red would have passed
  on this very defect. **The compose reds assert `status == succeeded`** (and, for trace_produce, a
  listed trace row with a body), via PL 8022." Its ruling, verbatim: "**DP-Q3 → S4 owns it,**
  together with the derived-consumer rule: (a) the production entrypoint registers
  `register_trace_handlers`; (b) a GUARD test, derived and not hand-listed: for every JobKind in
  `DEFAULT_QUEUE_FOR_KIND`, the production entrypoint's registry has a handler, EXCEPT an explicit
  allow-list of later-phase kinds. Each allow-list entry carries its phase and spec reference (e.g.
  OPTIMISATION_RUN → P3/04, MONITOR_RUN → P4/05, and so on, verified by the planner against roadmap
  §6, not assumed). A P2 kind may never be allow-listed. (c) the red: the guard fails on main naming
  SCORE_TRACE_PRODUCE. Also decide in PL 8022 whether `jobs.submit` should REFUSE a kind with no
  production handler rather than queue a Job that can only fail. Recommend; I rule." The lead
  relayed it in its message to this seat at 2026-10-14 (after 10:36:42 BST). E4.7 and DP-Q4 apply
  it; the verification of each allow-list entry is E4.7's table, and it does **not** confirm the
  entry's example "OPTIMISATION_RUN → P3/04" (the roadmap places WK-684 in P4).
- **The finding as first raised:** the lead's from-lead entry "2026-10-14 10:13:05 BST", its
  "QUEUE FINDING (planner-wf701plan, lead-verified at main 1e260c15)": `score.trace_produce` and
  `score.batch` route to `scoring`, and no worker consumes it.
- **The finding record:** FD 8021 (working id), one class as the 10:36:42 entry words it: "a
  routed job never completes on a real worker: no consumer for io/scoring; no handler for
  trace_produce". Owner WK-674, reserved in `eta.md` "2026-10-14 10:14:33 BST"; auditor-queues is verifying it by
  a run, and proposes the severity over the whole class. **S4 discharges it.** This delta does not restate its severity.
- **The reservation:** the lead's `eta.md` line "2026-10-14 10:32:05 BST", which names this
  delta's contents.

## Goal

Slice 4's compose stack consumes **every queue the routing table names**, proven by a shape test
whose expected set is **derived from `DEFAULT_QUEUE_FOR_KIND`** and by three delivery proofs on the
pools that had no consumer, each asserting `succeeded`. Every routed kind has a handler in the
production worker, or is an allow-listed later-phase kind, proven by a derived guard. The local demo consumes the same derived set. The Work's goal is
`PL-1237`'s, unchanged.

## Premises (read at `ba68a6da` and `e1555803`)

- **P1 — the routing table names four pools.** `backend/src/app/platform/jobs.py:58-87`,
  `DEFAULT_QUEUE_FOR_KIND`: `default` (`RATING_COMPILE`, `MONITOR_RUN`, `DOSSIER_GENERATE`, `:72,83,84`),
  `compute` (14 kinds), `scoring` (`SCORE_BATCH`, `SCORE_TRACE_PRODUCE`, `:76,79`) and `io`
  (`DATASET_INGEST`, `EXPORT_REGULATORY`, `BLOB_GC`, `:59,85,86`). `JobQueue` has exactly these four
  members (`packages/model-schema/src/model_schema/jobs.py:85-91`). `submit` stamps the queue
  from the table (`jobs.py:122`) and the outbox row carries it (`:156-162`).
- **P2 — the consumers today.** On `main`, `deploy/docker-compose.yml` has no worker service at all
  (services `postgres`, `redis`, `minio`, `keycloak`). On S4's branch it is one `worker` service on
  `--queues compute` (`deploy/docker-compose.yml:145` at `e1555803`). `scripts/demo.py:208-224`
  runs `--queues default,compute`. `backend/src/app/worker/entrypoint.py:3`'s docstring says
  `--queues compute`. No path consumes `scoring` or `io`. The one statement of all four is
  `.claude/skills/dev-commands/SKILL.md:964` (`--queues compute,default,io,scoring`).
- **P3 — the relay rides `default`, by a literal.** The outbox relay's beat entry sends to
  `"default"` (`entrypoint.py:53-58`), and `task_default_queue="default"` (`celery_app.py:52`).
  Neither reads `JobQueue` or the table. `default` is in `set(DEFAULT_QUEUE_FOR_KIND.values())`
  today only because three kinds route to it (P1). DP-Q2 is about this.
- **P4 — S4's prepared tests encode the old set.** At `e1555803`, `backend/tests/test_deploy_stack.py:87`
  is `ROUTED_QUEUES = {"default", "compute"}`, and `worker_consumes_every_routed_queue` (`:90-104`)
  reports both a missing and an "extra" queue (an equality check). Its breaker
  `_break_worker_drops_default_queue` (`:178-180`) is in the table at `:193`. The runtime test
  `test_a_submitted_job_reaches_a_terminal_state_through_the_compose_worker`
  (`backend/tests/test_deploy_stack_runtime.py:229-266`) proves `rating.compile` on `default`, with
  `JOB_TERMINAL_BOUND_SECONDS = 60` (`:188`) and the beat fixture (`:200-215`).
  `backend/tests/test_demo_command.py:310` asserts `"default,compute" in demo_script.worker_command()`.
- **P5 — a terminal state does not prove the work ran.** `backend/src/app/worker/tasks.py:126-139`:
  a Job whose kind has no registered handler goes to `failed` with `JOB_HANDLER_NOT_REGISTERED`.
  `entrypoint.py:64-76` registers the data, model, rate-table, rating, scoring and dislocation
  handlers and **never calls `register_trace_handlers`** (`backend/src/app/worker/trace_handlers.py:120`);
  `git grep -n register_trace_handlers origin/main -- backend/src` finds only its definition. So a
  `score.trace_produce` Job on a real worker that consumes `scoring` still ends `failed`: terminal,
  through a real worker, and the trace never produced. This was read, not run; the 10:36:42 entry
  verified the same lines at `origin/main`, placed it inside FD 8021 (working id), and gave it to S4
  (E4.7). Kinds with no handler module at all on `main`: `OPTIMISATION_RUN`, `GIPP_CHECK`,
  `MONITOR_RUN`, `DOSSIER_GENERATE`, `EXPORT_REGULATORY` and `BLOB_GC` (the `JobKind` references in
  `backend/src/app/worker/*_handlers.py`, read per module); and no route on `main` submits any of
  them: `git grep -n -E "JobKind\.(OPTIMISATION_RUN|GIPP_CHECK|MONITOR_RUN|DOSSIER_GENERATE|EXPORT_REGULATORY|BLOB_GC)" origin/main -- backend/src packages`
  prints only `backend/src/app/platform/jobs.py`'s table rows.
- **P6 — the ingest and batch routes.** `dataset.ingest` is submitted by `start_ingestion`,
  `POST /datasets/{slug}/versions` (`backend/src/app/api/datasets.py:515-549`), the only enqueuer
  (`backend/tests/test_ingest_enqueuers.py`). `score.batch` is submitted by `POST /score/batch`
  (`backend/src/app/api/score.py:608-649`). Both handlers are registered by the entrypoint
  (`data_handlers.py:447`, `scoring_handlers.py:388`).

## Tasks

| Order | Slice | Scope (what the `LG-` quotes) | Requirements, each id | Depends on | Size |
|---|---|---|---|---|---|
| 1 | `SL-1258` — Slice 4: the deployment path | `PL-1666` row 1, `PL-1690` E4.1 and E4.3, and E4.2 and E4.4 to E4.6 below | `PL-1690`'s set, unchanged: `07` §3.6: FR-434, FR-435, FR-437; `07` §3.2: FR-412 (memory half), FR-415 (worker service); `07` §3.9: FR-452 (management-API limb); `07` §9: NFR-531, NFR-534; register FD-1211, FD-1650. **Cited, not added:** `07` §3.2: FR-405 (the per-queue pools the split reads), FR-406 (the relay); FD 8021 (working id), discharged at merge | `PL-1690`'s, plus: DP-Q1 ruled by the maintainer; DP-Q5 resolved (E4.7's green); FD 8021 minted | 1 + a build window |

No requirement id is added or removed. FR-405 and FR-406 are cited because E4.2 and E4.4 read them;
the markers below are `req("FR-415")` as `PL-1690` set them, plus `req("FR-405")` on the split check
(E4.2) and `req("FR-406")` where `PL-1690` E4.3 already uses it.

### Slice 4 (`SL-1258`) — changes since `PL-1690`

- **E4.2 — every routed pool consumed: the derived consumer set.** Replaces `PL-1690` E4.2 whole.
  - **The rule.** The set of queues the compose stack consumes is a **superset** of
    `{q.value for q in DEFAULT_QUEUE_FOR_KIND.values()}`, read from the table at test time. No test,
    compose file or script names the expected set as literals. The relation is `⊇`, not `=`: a
    consumer of a queue no kind routes to is not a defect (the relay's queue, P3).
  - **Consumed** is the union, over every compose service whose `command` runs
    `celery -A app.worker.entrypoint worker`, of the comma-split argument after `--queues`. A worker
    service with no `--queues` is a defect the check reports (Celery would consume only
    `task_default_queue`).
  - **The shape test**, in `backend/tests/test_deploy_stack.py`, replacing `ROUTED_QUEUES` and the
    equality check (P4). The check function returns problems, as the file's other checks do; the
    test's assert is exactly:

    ```python
    from app.platform.jobs import DEFAULT_QUEUE_FOR_KIND

    def routed_queues() -> set[str]:
        return {q.value for q in DEFAULT_QUEUE_FOR_KIND.values()}

    def consumed_queues(compose: dict[str, Any]) -> set[str]:
        ...  # the union defined above

    def every_routed_queue_is_consumed(compose: dict[str, Any]) -> list[str]:
        return [f"queue {q} is routed to and never consumed"
                for q in sorted(routed_queues() - consumed_queues(compose))]

    @pytest.mark.req("FR-415")
    def test_every_routed_queue_is_consumed() -> None:
        assert consumed_queues(_load()) >= routed_queues(), every_routed_queue_is_consumed(_load())
    ```

    DP-Q2 (a), if ruled, adds the relay queue to the right-hand side (E4.4).
  - **Red, by cause, before the compose edit:** against `e1555803`'s compose the test fails naming
    `queue default is routed to and never consumed`, `queue io …` and `queue scoring …`. The `LG-`
    quotes that line.
  - **The breakers**, in the existing table (`test_each_check_goes_red_on_the_break_it_exists_for`):
    `_break_drop_io_consumer` and `_break_drop_scoring_consumer`, each removing that queue from
    every consuming service (under DP-Q1 (b), deleting the service). They replace
    `_break_worker_drops_default_queue`. Each is red by its named queue only.
  - **A guard that the rule is derived, not copied:** one test replaces the name the test module
    reads (`monkeypatch.setattr(<test module>, "DEFAULT_QUEUE_FOR_KIND", ...)`) with a copy of the
    table plus one stand-in entry whose value has `.value == "phantom"` (the check reads `.value`
    only), and asserts `every_routed_queue_is_consumed(_load())` names `phantom`. A hard-coded
    expected set cannot pass it.
  - **Under DP-Q1 (b) only:** `worker_has_a_memory_backstop` (`:75-84` at `e1555803`) applies to every
    worker service, not to `services["worker"]`; and a second check, marked `req("FR-405")`, asserts
    no worker service consumes more than one queue (that is what makes each pool sized
    independently). Each joins the breaker table with one breaker.
  - **The compose edit** is DP-Q1's ruled shape.
  - Acceptance item 3.

- **E4.3, extended — the io and scoring reds on compose, through a real worker.** Three runtime tests
  in `backend/tests/test_deploy_stack_runtime.py`, beside `PL-1690` E4.3's `rating.compile` test, on
  its helpers (`_compose`, `built_n`, `beat_fixture`, `down`, `_api`, `_seeded_scoring_request`),
  behind `GIP_DEPLOY_TESTS=1`:
  - `test_a_dataset_ingest_job_succeeds_through_the_compose_io_worker`, marked `req("FR-415")` and
    `req("FR-406")`: start one ingestion through `lb` by `POST /api/v1/datasets/{slug}/versions`
    (P6), the smallest source the existing ingest tests use; assert `job["queue"] == "io"`.
  - `test_a_score_batch_job_succeeds_through_the_compose_scoring_worker`, same markers: submit one
    `POST /api/v1/score/batch` over the seeded rating version (P6); assert `job["queue"] == "scoring"`.
  - `test_a_sampled_trace_is_produced_through_the_compose_scoring_worker`, same markers: score one
    quote through `lb` (`POST /api/v1/score`) that is sampled with certainty (a declined quote, the
    100 % floor of `platform/traces.py:94-97`, or the seeded version's `rating.trace_sample_rate`
    raised to 1; the executor names which in the `LG-`); the `score.trace_produce` Job it submits
    (`backend/src/app/api/score.py:570`) is read and asserted on as below; then
    `GET /api/v1/traces` (`backend/src/app/api/traces.py:167`) must list a row whose `quote_id` is
    that quote's, with `status == "complete"` and a non-empty `trace` body:

    ```python
    rows = [r for r in _api("GET", "/api/v1/traces", headers)["items"] if r["quote_id"] == quote_id]
    assert rows and rows[0]["status"] == "complete" and rows[0]["trace"], (
        f"no complete trace with a body for quote {quote_id}: {rows!r}"
    )
    ```

    (The listing's envelope key is whatever `list_traces` returns; the executor reads it there.)
    It is the delivery proof of E4.7 (a), and the one PL 8014 (working id)'s C7 rests on.
  - **Up:** every worker service DP-Q1 rules, plus `lb`; beat as `PL-1690` E4.3's one-off fixture.
    No inline `execute_job`: the Job is moved by the relay and run by the worker container.
  - **The assert in each, exactly:** poll `GET /api/v1/jobs/{id}` until a terminal status or the
    bound, then

    ```python
    assert status == "succeeded", (
        f"job {job['id']} ({job['kind']}, queue {job['queue']}) is {status!r} after "
        f"{bound}s: " + ("never consumed" if status == "queued" else f"error {error_code}")
    )
    ```

    `succeeded`, not only terminal: the 10:36:42 entry's correction (§Authority). P5 is why: a
    terminal `failed` is reached through a real worker by a Job that never ran its handler. If the
    executor finds a `succeeded` run of any of the three cannot be set up on compose, it stops and
    reports to the lead; it does not relax the assert.
  - **The bound:** stated in each test as a constant beside `JOB_TERMINAL_BOUND_SECONDS`, and the
    elapsed time printed; the `LG-` quotes both.
  - **Red, by cause ("never consumed"):** each test run against `e1555803`'s compose (the worker on
    `--queues compute`) ends `queued` past its bound, and the message says `never consumed`. The
    `LG-` quotes each red line. A red naming any other cause is a test defect. **The trace test has
    a second red, by its own cause:** against S4's head with only E4.7 (a)'s registration line
    reverted, its Job ends `failed` with `error JOB_HANDLER_NOT_REGISTERED` and no trace row is
    listed; the `LG-` quotes it. **Reading of "red on
    main's compose":** `main`'s compose has no worker service (P2), so a run there would be red by
    "no worker", a different cause. The red base is therefore `e1555803`: the worker `main` would
    receive without this delta. The lead may rule another reading.
  - **Where it runs:** `PL-1666` D0.5 and `PL-1690` E4.3, unchanged: the gate does not set
    `GIP_DEPLOY_TESTS`, so all three run once in S4's build window, in the same session as the
    `rating.compile` proof, and the `LG-` quotes the command and output.
  - Acceptance item 4.

- **E4.4 — the relay queue, named once (DP-Q2, recommended (a)).** If DP-Q2 is ruled (a):
  `backend/src/app/worker/celery_app.py` gains `RELAY_QUEUE: Final = JobQueue.DEFAULT` beside
  `TASK_RELAY_OUTBOX`; `task_default_queue` and the beat entry's `"queue"` option
  (`entrypoint.py:57`) read it; and E4.2's assert becomes
  `consumed_queues(_load()) >= routed_queues() | {RELAY_QUEUE.value}`. One breaker: with the three
  `default` kinds moved to `compute` in a substituted table (as E4.2's guard substitutes it) and
  `default` removed from every consuming service, the check names `default`; the (b) form of the
  assert passes on the same input, which is the gap (a) closes. If
  ruled (b), nothing here is built and the `LG-` records the ruling.

- **E4.5 — `scripts/demo.py` on the same derived set: in S4's write set.** `worker_command()`
  (`scripts/demo.py:208-224`) builds its `--queues` argument from the table:
  `",".join(sorted(routed))`, with `routed` read as E4.2 reads it (and `RELAY_QUEUE` under DP-Q2 (a)),
  imported inside the function. The step label at `:392`, `"Celery worker (default, compute)"`,
  is derived from the same set. The demo stays **one** worker process whatever DP-Q1 rules: it is
  the local demo, not the deployed topology, and FR-405's sizing is the deployed stack's.
  `backend/tests/test_demo_command.py:310` changes to assert the queue argument's split set
  `>=` the derived set, red first against today's `"default,compute"`.
  - **Why S4 and not the WF-701 demo slice (SL 8015, working id):** SL 8015 runs after Slice 5
    (PL 8014, working id), and the maintainer's condition is "before the G2 rehearsal is re-run
    on the merged tree"; S4 lands first. It also keeps the derived set and its two consumers in one
    PR. SL 8015's T6 then reads the merged `worker_command()` rather than changing it.
  - Acceptance item 5.

- **E4.6 — the stale docstring.** `backend/src/app/worker/entrypoint.py:3`'s usage line is updated
  to the derived form (P2), so it no longer states `--queues compute`.

- **E4.7 — every routed kind has a production handler (DP-Q3, ruled to S4 at 10:36:42).**
  - **(a) The registration.** `backend/src/app/worker/entrypoint.py` calls
    `register_trace_handlers()` (from `app.worker.trace_handlers`) beside the six calls at `:71-76`.
  - **(b) The guard, derived.** In a new `backend/tests/test_worker_handler_coverage.py`, marked
    `req("FR-405")` and `req("FR-406")`. The production entrypoint cannot be imported in a test (it
    reads settings, checks the tenant binding with `asyncio.run` and builds the Celery app at import,
    `entrypoint.py:27-46`), so the guard reads **which** registrars it calls from its source, and
    runs them:
    1. parse `backend/src/app/worker/entrypoint.py` with `ast`; collect every module-level call
       whose function name matches `register_*_handlers`, and the module each is imported from (the
       `from app.worker.<m> import register_*_handlers` statements in the same file);
    2. `monkeypatch.setattr(app.worker.handlers, "HANDLERS", {})`, so registrations other tests made
       do not count (`backend/tests/test_score.py` calls `register_trace_handlers` itself);
    3. import each module and call each collected registrar once;
    4. assert, exactly:

    ```python
    registered = set(app.worker.handlers.HANDLERS)
    missing = sorted(k.value for k in DEFAULT_QUEUE_FOR_KIND
                     if k not in registered and k not in LATER_PHASE_KINDS)
    assert missing == [], f"routed kinds with no handler in the production entrypoint: {missing}"
    ```

    No kind is named in the assert. The only kinds the file names are the allow-list's.
  - **The allow-list, `LATER_PHASE_KINDS`**, in the guard's file: a mapping from `JobKind` to a
    `(phase, work, spec reference)` triple. Two more asserts hold it honest: every entry's phase is
    not `P1a`, `P1b` or `P2`; and every entry is **absent** from `registered` (an entry whose
    handler has landed is stale and fails, so the kind moves under the main assert). The entries,
    each verified at `ba68a6da` against the roadmap's phase sections (`docs/roadmap.md`
    `## P3 — Governance` `works:` line and `## P4 — Optimisation & Monitoring` `works:` line, and
    each Work row's "From "Workstreams"" requirement list) and the spec row:

    | Kind | Phase | Work (its roadmap row) | Spec reference | Allow-listed? |
    |---|---|---|---|---|
    | `OPTIMISATION_RUN` | P4 | WK-684 (FR-284 to FR-293, each listed on the row) | `04` FR-284 (the Optimisation Run) | yes |
    | `GIPP_CHECK` | P4 | WK-685 (FR-294, FR-297 to FR-302) | `04` FR-294 (the GIPP check) | yes |
    | `MONITOR_RUN` | P4 | WK-687 (`05` FR-307 onwards) | `05` FR-307 (the Monitor) | yes |
    | `DOSSIER_GENERATE` | P3 | WK-680 (FR-376, FR-377, FR-379, FR-380, FR-381) | `06` FR-376 (the Model Dossier) | yes |
    | `EXPORT_REGULATORY` | P3 | WK-681 (FR-382) | `06` FR-382 (the regulatory response export) | yes |
    | `BLOB_GC` | **none found** | **none**: `git show origin/main:docs/roadmap.md \| grep -c "FR-420"` prints `0`; WK-658 (P1a, closed, "~35 of 61 `PLAT` requirements") names blobs but lists no FR ids | `07` FR-420 (reference-counted blob GC) | **no** — not verifiable as later-phase, so not allow-listed by this plan; DP-Q5 |

    The 10:36:42 entry's example "OPTIMISATION_RUN → P3/04" is not what the roadmap says: WK-684 is
    in `## P4`'s `works:` line. The table uses the roadmap.
  - **(c) The red on `main`:** the guard file run against `ba68a6da`'s `entrypoint.py` (before (a))
    fails with `missing == ['blob.gc', 'score.trace_produce']` while DP-Q5 is open, or
    `['score.trace_produce']` once DP-Q5 places `BLOB_GC` in a later phase; either names
    `SCORE_TRACE_PRODUCE` (`score.trace_produce`). The `LG-` quotes the line. After (a), it is green
    only when DP-Q5 is resolved; **the guard is never made green by allow-listing a kind this table
    did not verify.**
  - **Breakers** (the guard's own, in its file): drop one registrar call from a copy of the parsed
    call list, and the guard names that registrar's kinds; add an allow-list entry with phase `P2`,
    and the phase assert fails.
  - Acceptance item 9.

### SL-1258's write set, widened

`PL-1537` §"Write sets and shared paths" named S4's expected set. This delta adds, at path level:

| Path | Why | Under |
|---|---|---|
| `deploy/docker-compose.yml` — every worker service, not only `worker` | DP-Q1's shape | E4.2 |
| `scripts/demo.py` | the derived `--queues` | E4.5 |
| `backend/tests/test_demo_command.py` | its `:310` assert | E4.5 |
| `backend/src/app/worker/entrypoint.py` | the docstring (E4.6); the beat entry's queue (E4.4); `register_trace_handlers()` (E4.7 (a)) | E4.4, E4.6, E4.7 |
| `backend/tests/test_worker_handler_coverage.py` (new) | the derived handler guard | E4.7 (b) |
| `backend/src/app/worker/celery_app.py` | `RELAY_QUEUE` | E4.4, DP-Q2 (a) only |
| `backend/tests/test_deploy_stack.py`, `backend/tests/test_deploy_stack_runtime.py` | already in `backend/tests/`; named for the reviewer | E4.2, E4.3 |

Under DP-Q4 (a) only, add `backend/src/app/platform/jobs.py`, `backend/src/app/errors.py` and
`docs/specs/07-platform.md` (a spec line before the code). The executor states the actual set in its `LG-`, as `PL-1537` requires.

## Effect on SL-1689 (the scheduler and frontend row)

`SL-1689` is serialised on `deploy/docker-compose.yml` after S4 (`PL-1688` Global Constraints;
the maintainer's (by delegation) entry "2026-10-12 02:53:52 BST" item 4), so it builds on whatever
S4 merges. Three of its premises change; its scope does not:

- **Its activation need** "`SL-1258`'s worker consuming `default,compute`" (`docs/roadmap.md` SL-1689
  row; `PL-1688` Tasks row) is read as "`SL-1258` merged with every routed pool consumed, per PL-8022
  E4.2". A dated line under the row records it (this delta's commit); `PL-1688` stays unedited.
- **Its Task 0** quotes "`deploy/docker-compose.yml`'s `worker` command"; under DP-Q1 (b) that is
  every worker service's command.
- **Its Task 1 breaker table** is S4's file. Its new checks join the table E4.2 leaves, with the
  derived check in it. Its **Task 3** runtime proof brings up every worker service DP-Q1 rules; the
  cheapest kind it names at Task 0 still has its queue consumed.

FR-432 names container **images** (`api`, `worker`, `scheduler`, `frontend`), so per-pool worker
**services** from the one image do not move its `worker` limb. `PL-1688`'s Goal line, "`api`,
`worker`, `scheduler` and `frontend`" in `config --services`, would read `worker-*` under DP-Q1 (b):
SL-1689's `LG-` records that reading at Task 0, or the lead rules it.

## Decision points

| DP | Question | Options | Recommendation | Kind | Blocking? | Resolved by |
|---|---|---|---|---|---|---|
| **DP-Q1** | How the compose stack maps pools to worker services (FR-405) | **(a) One worker for all pools.** The existing `worker` service, `--queues` = the derived set, one `--concurrency` (2 today) and one `mem_limit`. One service. A fit occupies a slot that a `score.batch` or an ingest then waits behind; the pools cannot be sized apart. **(b) One worker service per pool**, from the one image through a YAML anchor: `worker-compute` (`--concurrency 2`, `mem_limit` 4g: few and fat), `worker-scoring` (`--concurrency 4`: many and thin), `worker-io` (`--concurrency 4`: network-bound), `worker-default` (`--concurrency 2`: the relay, compile, monitor and dossier). Four services; each `--concurrency` and `mem_limit` an env-overridable default (`${GIP_WORKER_<POOL>_CONCURRENCY:-n}`), each a starting value, not a measured one. A new pool adds a service, which E4.2 forces. **(c) Three services:** `compute`, `scoring`, and one for `io` and `default` together. Fewer containers; `io` and `default` share a pool, so they are not sized apart. | **(b).** FR-405 says the pools are "sized independently", and FR-415 relies on "each queue's worker pool is sized independently (FR-405)" as the boundary that replaces a quota. (a) states both and builds neither; it also puts a model fit and a batch score in one slot pool, which `jobs.py:55-57`'s own comment names as the starvation case. (c) breaks the same promise for `io` and `default`. (b) costs three more compose services from one anchor and lets FR-434's "scoring without compute" be shown by stopping one service. The concurrency figures are defaults to be measured, not a claim. | scope (the maintainer, by the 10:13:50 entry: "I rule it") | **yes** — the compose edit, the E4.2 checks and both runtime tests depend on it | the maintainer's dated line |
| **DP-Q2** | Is the relay's queue part of the asserted set? It is `default` by two literals (P3), outside the table | **(a)** Name it once, `RELAY_QUEUE` (E4.4), and assert `⊇ routed ∪ {RELAY_QUEUE}`. Two more files in the write set. **(b)** Assert `⊇ routed` only, as the 10:13:50 entry words it. `default` is covered today only while a kind routes to it. | **(a).** It is the same defect class one step earlier: if `RATING_COMPILE`, `MONITOR_RUN` and `DOSSIER_GENERATE` ever moved off `default`, (b) would pass while no Job left the outbox. It adds, never removes, from the ruled `⊇`. | decision point | no — default (b) until ruled, so E4.2 is built as the entry words it; (a) adds at E4.4 | the decision-maker's `RL-`, or the maintainer's line with DP-Q1 |
| **DP-Q3** | Does S4 also register the trace handler (P5)? | (a) yes, with a derived guard; (b) no, a separate owner | (a), as recommended | scope | — | **RULED (a)** by the maintainer's (by delegation) entry "2026-10-14 10:36:42 BST"; applied as E4.7 |
| **DP-Q4** | Should `jobs.submit` **refuse** a kind with no production handler, rather than queue a Job that can only fail? | **(a) Refuse the allow-listed kinds.** `LATER_PHASE_KINDS` moves from the guard's file to `backend/src/app/platform/jobs.py`, beside `DEFAULT_QUEUE_FOR_KIND`, as the one declaration; `submit` raises a typed `PlatformError` for a kind in it, before any row, audit event or outbox write. The API process cannot read the worker's registry (the registrars run in the worker process only), so the declaration is the only thing `submit` can check. Costs: one error code (a `07` spec line first, then `errors.py`), one red test, and a slice already at GO grows a spec edit. **(b) No runtime refusal.** E4.7's guard is the control: a P2 kind cannot lack a handler, and no route on `main` submits an allow-listed kind (P5). The gap that remains: a later phase adds a route for its kind before its handler, and the guard still allows the kind until its entry is removed. **(c) Refuse any kind with no handler, read at submit** — not buildable as stated, for the process reason in (a). | **(a).** It makes "a queued Job that can only fail" unrepresentable for the declared kinds instead of tested for, which is the class FD 8021 (working id) records, at the cost of one set lookup. The allow-list becomes a contract both sides read, and E4.7's stale-entry assert forces its removal when the handler lands, so the refusal cannot outlive the gap. If the maintainer prefers S4 not to grow a spec edit at GO, (b) now and (a) as the first slice of whichever phase adds the first route for an allow-listed kind. | scope (the maintainer: "Recommend; I rule") | no — default (b) until ruled; (a) adds a task after E4.7 | the maintainer's dated line |
| **DP-Q5** | `BLOB_GC` is routed (`io`), has no handler, and FR-420 is on no roadmap row (E4.7's table). Where is it placed? | **(a)** The maintainer places FR-420 in a later phase by a dated roadmap line (a Work in P3, for example WK-1251's production packaging, or another); `BLOB_GC` is then allow-listed with that phase. **(b)** FR-420 is P2's: S4 or a new WK-674 row builds the `blob.gc` handler (conservative, dry-runnable, audited, per FR-420). **(c)** `BLOB_GC` leaves the routing table until its phase; the guard then does not see it. | **(a).** Nothing submits `blob.gc` (P5), and FR-420's GC is a deletion mechanism (`PL-850:189`'s reading), not part of P2's rating path. (b) adds unplanned scope to a slice at GO. (c) edits a shared routing table to make a test pass. | scope (the maintainer) | **yes, for E4.7's green only**: the guard is red on `blob.gc` until resolved; E4.2, E4.3 and E4.7 (a) proceed | the maintainer's dated line |

## Acceptance Standard

1. **This delta passes the docs checks on its own branch**, check 31's working-id lines excepted:
   `python3 scripts/audit-docs.py` exits 0 apart from them.
2. **No hard-coded expected set:** `git grep -n -E "ROUTED_QUEUES|default,compute|\{\"default\", \"compute\"" <S4 head> -- backend/tests scripts deploy`
   prints nothing, and the derived-guard test of E4.2 (the `phantom` table entry) exits 0.
3. **E4.2:** `uv run pytest -q backend/tests/test_deploy_stack.py` exits 0; the `LG-` quotes the red
   line of `test_every_routed_queue_is_consumed` against `e1555803`'s compose, naming `default`, `io`
   and `scoring`, and the red of each new breaker.
4. **E4.3, extended:** in the build window,
   `GIP_DEPLOY_TESTS=1 GIP_N_SHA=<S4 head> uv run pytest -q backend/tests/test_deploy_stack_runtime.py -k "dataset_ingest or score_batch or sampled_trace or terminal_state"`
   exits 0 with each test's bound and elapsed time printed; the three new tests against
   `e1555803`'s compose are red with `never consumed`, the trace test is red with
   `JOB_HANDLER_NOT_REGISTERED` with E4.7 (a) reverted, and the `LG-` quotes every red line.
5. **E4.5:** `uv run pytest -q backend/tests/test_demo_command.py` exits 0, and its changed assert is
   seen red against `ba68a6da`'s `scripts/demo.py` (`default,compute`).
6. **DP-Q1** carries the maintainer's dated line before S4's compose edit is committed; the `LG-`
   quotes it. DP-Q2 carries a ruling or records the default applied; DP-Q3 is ruled (E4.7).
7. **The amendment's dated lines:** S4's `LG-` carries a dated line naming the 10:13:50 entry as the
   amendment of `PL-1690` E4.2, the 10:36:42 entry as the correction to `succeeded` and DP-Q3's
   ruling, and this delta as their plan.
8. `PL-1690` Acceptance items 2, 3, 5 and 6 hold unchanged; its item 4 is replaced by item 3 here.
9. **E4.7:** `uv run pytest -q backend/tests/test_worker_handler_coverage.py` exits 0; the `LG-`
   quotes its red against `ba68a6da`'s `entrypoint.py`, naming `score.trace_produce`, and each
   breaker's red. `git grep -n register_trace_handlers <S4 head> -- backend/src/app/worker/entrypoint.py`
   prints the call. `LATER_PHASE_KINDS` holds exactly the entries E4.7's table marks "yes", plus
   `BLOB_GC` only if DP-Q5 is ruled (a).
10. **DP-Q4 and DP-Q5** each carry a ruling, or the `LG-` records the default applied.

## Activation

At this delta's mint, and once DP-Q1 is ruled: `SL-1258`'s GO conditions are `PL-1690`'s Activation
list with **E4.2 read as this file's E4.2**, plus E4.3 extended, E4.4 (as DP-Q2 rules), E4.5 and E4.6;
E4.7 (with DP-Q5 resolved for its green); FD 8021 (working id) minted, so the `LG-` can name what
the merge discharges; and the lead's GO.
`PL-1690` stays as its own status line says; this delta does not change it.
