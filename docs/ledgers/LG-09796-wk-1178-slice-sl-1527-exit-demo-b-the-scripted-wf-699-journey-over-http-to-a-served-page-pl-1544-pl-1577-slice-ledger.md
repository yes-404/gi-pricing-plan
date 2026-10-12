---
id: LG-9796
family: ledger
title: WK-1178 slice SL-1527 — exit demo (b): the scripted WF-699 journey over HTTP to a served page (PL-1544 + PL-1577 slice ledger)
status: active                 # active → closed (§1.2a) — set `closed` only at slice close
created: 2026-10-11
owner: executor
tree: 1b04cb05a72e2329d35f57dd87cb3be600096177
phase: P2
work: WK-1178
slice: SL-1527
plans: [PL-1544, PL-1577, PL-1644]
corrected_by: []
relates: [PL-1544, PL-1577, PL-1644, RL-1645, RL-1521, RL-1524, FD-1209, FD-1244, FD-1245, FD-1494, LG-1641]
---

# LG-9796 — WK-1178 slice SL-1527: exit demo (b)

*(Filed under working id 9796, reserved by the lead.)* Executed by `executor-sl1527` from PL-1544
and its deltas PL-1577 and working id 9799, base `origin/main`
`1b04cb05a72e2329d35f57dd87cb3be600096177` (#1285, SL-1503). Times are BST
(`TZ=Europe/London date`) unless marked.

**GO:** `to-lead.md` "2026-10-11 23:18:17 BST" (PL-1544 re-check ACCEPTED; DP-D4 = (a), `bonus_malus`
increasing on [50, 230] over the NCD ladder, spacing 45; GO (need 17) CONDITIONAL: SL-1527 AUTHORS
NOW; activation and gate wait for working id 9799 and the WF-699 D4 T-text (working id RL 9701) to
mint; merge order docs, then SL-1527). Quoted from the lead's brief; the entry itself is a local
channel file (RFC-777) and was not re-read by the executor.
**MERGE-ACK:** added at merge.

## Tasks

### Scope

The slice's row is `#### SL-1527 — WK-1178 exit-demo slice (b) — the scripted WF-699 journey over
HTTP, ending in a served page` in `docs/roadmap.md`, under PL-1544 as amended by PL-1577 and working
id 9799. Write set (the lead's brief, item 3): PL-1544 §Write set, PL-1577 Task 3, and working id
9799 only; any other path is a STOP to the lead. PL-1544 and SL-1527 stay `draft` until the
activation commit, which comes on the lead's word after the docs mint.

### Task list

- Task 0 — preconditions and drift (below). No code.
- Task 1 — the journey test, red first.
- Task 2 — phases A and B over HTTP.
- Task 3 — phases C and D (D4 and D5 per working id 9799 (a)).
- Task 4 — phase E, the deploy step, the served quote.
- Task 5 — the one command, the pre-flight, the served page, FD-1494's three limbs.
- Task 6 — rehearsal, the gate, this ledger (owed after the docs mint and the lead's grant).

### Gate

Not run. No gate starts before the docs mint and the lead's "gate slot granted" for the head
(executor charter S-13).

### Audit

Not yet.

### Build log

#### Task 0 — drift between PL-1544 (as amended) and `origin/main` `1b04cb05`

Base recorded: `git rev-parse origin/main` = `1b04cb05a72e2329d35f57dd87cb3be600096177`; the worktree
branch `sl-1527-wk1178-exit-demo-b` tracks it. `uv sync --all-packages` and
`pnpm --dir frontend install --frozen-lockfile` ran clean. `df /` 63% used.

1. **Marker form (Acceptance 1 and 9).** PL-1544 says the journey test carries
   `pytestmark = pytest.mark.req("WF-699")` and that `req-coverage.py` lists it. Both are false at
   this tree. `scripts/req-coverage.py` collects only the decorator form
   `@pytest.mark.req("<id>")` (its regex, `scripts/req-coverage.py:58`) and fails with "tests claim
   requirements that do not exist" for any id not defined as `**FR-n**` or `**NFR-n**` in
   `docs/specs/`. `WF-699` is a workflow id, so a decorator `req("WF-699")` reds `req-coverage`, and a
   module-level `pytestmark` is invisible to it. There is no house marker for a workflow id: the
   precedent, `backend/tests/test_wf01_journey.py:262`, marks `@pytest.mark.req("FR-19")` (the FR that
   requires the journey test) and names `WF-698` in the docstring and the test name. This slice
   follows that form: decorators with the FR ids the journey exercises (PL-1544 §Requirement
   coverage), the docstring naming `docs/workflows/WF-00699-approved-models-to-approved-rating-version.md`,
   and test names `test_wf699_*`. Acceptance 1's `git grep -n -E 'WF-(00)?699'` still prints the file;
   the "req-coverage lists the WF-699 test" clause of Acceptance 9 cannot hold as worded and is
   reported to the lead.
2. **PL-1577 Task 3 and Acceptance 4** (the "20,000-policy sample" text in `journey.py` and
   `README.md`, naming `PL-1574` and `FD-1576`) is this slice's and PL-1544's Acceptance does not list
   it. Added to Task 6's checks.
3. **README machine-requirement sentence** (`to-lead.md` "2026-10-11 16:37:21 BST" item 3, via
   LG-1641): the host + container sum (2.70 GiB for stage a, 1.27 GiB provisional for stage d) is this
   slice's, measured on the real journey run.
4. **Seed size of the journey test.** PL-1544 Task 1 Step 1 leaves it unstated. A 2,000-row seed is a
   degenerate fit and the seed now refuses it (`DegenerateFitError`, `RELATIVITY_FLOOR = 0.01`,
   `examples/fremtpl2/model.py`, LG-1641). The in-process journey test therefore does not seed from
   the ARFF: it builds its own synthetic approved GLM and tables the way
   `backend/tests/test_demo_rating_evidence.py` does. The one-command rehearsal uses the full seed.
5. **Global Constraint 2** (the approvals HOLD): stale. `e3a98c97` (SL-1529, #1276) types every
   approval route from the `model-schema` `ApprovalRequest`, and RL-1522 rules the decision values. The
   journey reads approval responses through that shape.
6. **Goldens** are not constants: the journey reads them from the seeded suite over HTTP.
7. **B7 contingency** (`SKIPPED B7: SL-1340`): moot, need 18 is MET (`SL-1340` merged `a3572d1a`).
   The skip table has no B7 entry.
8. **Missing ladder.** The seed creates no `ncd-ladder` sub-graph (`git grep ncd-ladder -- backend
   packages examples scripts` hits tests and the comment at `examples/fremtpl2/algorithm.py:37` only).
   The journey creates and saves it over HTTP (`POST /api/v1/sub-graphs`) and mounts it; "@4" has no
   meaning here and the mount names the version the journey saved.
9. **Dispatch steps not run at authoring:** Task 0 Step 3 (PL-1408's containment query,
   `TOTAL route_approved=0`) and Step 2's re-derivation of needs run at dispatch, on the lead's word,
   because a gate slot is held on the box.

#### Rulings on the Task 0 gaps (quoted by header; the entries are local channel files, RFC-777)

- **Worker (gap 1): Option A.** The lead's ruling, `from-lead` "2026-10-11 23:25:00 BST", confirmed
  by the maintainer (by delegation), `to-lead.md` "2026-10-11 23:25:46 BST", item (a). `scripts/demo.py
  --journey` starts `celery -A app.worker.entrypoint worker --queues default,compute --concurrency 2`
  and `beat` as background children through `background()`, before the journey and stopped with it.
  The red-first wiring test shows that with no worker the first 202 Job never completes. The
  compose file's missing worker service is not this slice's (it becomes an FD in D13).
- **Marker (gap 2): the `test_wf01_journey.py` precedent, as a disclosed deviation** (23:25:46, item
  (b)). The journey test is marked with the FRs it exercises (decorator form) and names `WF-699` in
  its docstring and test names. **Disclosed deviation:** PL-1544 Acceptance 1 and 9 say the test
  carries a `WF-699` marker and that `req-coverage` lists it; `scripts/req-coverage.py:58` reads
  only decorator `FR-`/`NFR-` ids, so that clause cannot hold.
- **B7's "@4"** is illustrative (23:25:46, item (c)): the journey asserts the exact version it
  saved and pinned, read from its own create response, never a literal 4.
- **WRITE-SET WIDENING (gap 3), disclosed.** `from-lead` "2026-10-11 23:27:08 BST": Option A.
  `examples/fremtpl2/seed.py` for principal role grants, workspace membership and recording every id
  in `last-seed.json`, **nothing else in `seed.py`**; its test in `examples/fremtpl2/test_seed.py`;
  one README line. The maintainer let it stand with four conditions, `to-lead.md` "2026-10-11
  23:27:48 BST": (1) idempotent, existing role slugs only (no new role, permission or migration);
  (2) ONE definition of the principal set, the journey's fixture CALLS the seed's provisioning
  function and never writes rows; (3) the LG records the widening (this entry); (4) the grep of
  specs 06 and 07 for a role-grant or membership FR is the auditor's. **RL-1521 binds the journey's
  steps, not its setup.** Built: `seed.py` `DEMO_PRINCIPALS` and `grant_demo_principals()` (seed
  and journey test both call it); `analyst` and `actuary` also hold `approver` so
  `SUBMITTER_CANNOT_APPROVE` and `AUTHOR_CANNOT_APPROVE` fire past the role gate.
- **SKIPPED lines:** the lead's correction (23:27:48 forward): print BOTH, B4's `model_call` clause
  and C1′, per PL-1542 :110 and Hand-off 6. `SKIPS` has `SKIPPED B4 model_call: FD-1456; SL-1543`
  and `SKIPPED C1′: FD-1456; SL-1543`; the B4 line's exact text is the executor's, pending the
  planner's correction of Acceptance 2.

#### Notes recorded at the lead's instruction (from-lead 23:27:08)

- D4's regression Job carries no run id: a failed Job has `result = null` and `error.detail = {}`;
  the run id is only inside `error.message` ("regression run <uuid> is recorded") and no route
  lists runs. The journey parses it from the message (`regression()` in `journey.py`).
- E3 is staged as "submit before any Dislocation Run exists for the candidate"
  (`EVIDENCE_INCOMPLETE`). The gate keys staleness on the bundle hash, not on a rate-table edit time
  (`rating_versions.py:_dislocation_gate`), and a created Rating Version's pins are immutable, so
  WF-699 E3's "predates the last rate table edit" cannot be staged over HTTP. D6 to D8 therefore run
  between E3 and E4 (the resubmission), as WF-699 E4 words it.
- The ladder is an expression-only sub-graph. There is no route that creates a rate table from
  scratch (only seed-from-model, which needs a model Factor, and versions of an existing table), so
  working id 9799's "the rate table behind the ncd-ladder" cannot be built over HTTP; the maintainer's
  23:18:17 wording is "the hand-written NCD-ladder sub-graph". `POST /sub-graphs` creates it with the
  bands as one ternary chain (`ladder_body()`); the defect and its fix are new sub-graph versions
  (D4 and D5 each build a new algorithm version and Rating Version, because pins cannot be edited).
- The journey forks the **seeded** `fremtpl2-rate@1` (WF-699 B1: "forks to @n") rather than calling
  `build_fremtpl2_algorithm`, which needs `Banding` objects and the base premium that are not
  readable over HTTP. It is still the one definition: the seed saved what the builder returned.
- **B3 (the reference-table `lookup`) is not walked in this cut.** It is not in `SKIPS` and no owner
  exists for it, so it prints nothing and is not claimed `ok`; the lead rules whether to build it
  (a reference table, `admin` principal, a pinned `lookup` step consumed by the premium) or to give
  it an owner.
- Fixed-seed fixture: the in-process journey test uses the synthetic fit of
  `test_demo_rating_evidence.py` (the 2,000-row seed is refused as a degenerate fit); the delta's
  "the journey test seeds 20,000 rows and needs the ARFF" is not what the test does, and the real
  full-seed fit is exercised by the one-command rehearsal. Disclosed deviation from the delta, item
  "Task 1 Step 1".

#### The lead's verdicts on the disclosed deviations (`from-lead` "2026-10-11 23:45:51 BST")

Accepted as disclosed deviations: the expression-sub-graph ladder; the HTTP fork of
`fremtpl2-rate@1`; E3's staging and the D4 run id taken from `error.message`; the README
machine-requirement sentence after the Acceptance 5 run. B4's SKIPPED text: aligned to minted
PL-1644's Acceptance 2 row, which requires a line for B4's `model_call` clause and one for C1′,
each naming `FD-1456` and `SL-1543` (no exact string is given; the executor's line matches).
Held for the maintainer's ruling, as written: B3 (the lead recommends SKIPPED plus an FD) and
the Acceptance 5 fit (the lead recommends the real-seed rehearsal in the ledger plus a synthetic CI
test). DB-test slots (`STAGE=reds`) are granted by head after the ALONE window.

#### The maintainer's rulings on B3 and Acceptance 5 (`to-lead.md` "2026-10-11 23:46:22 BST", relayed by the lead)

- **B3 is BUILT in this slice, not carried.** The widening is accepted for exactly: the reference
  table is created over HTTP through the existing `/reference-tables` routes by the seeded admin
  principal; a pinned `lookup` step as at `effective_date` is consumed by the premium; a red-first
  test shows a quote dated BEFORE the row's `effective_from` does NOT use it. No new route, no DB
  writes (RL-1521). If the route cannot create or pin what B3 needs: STOP and send the gap.
  Authored (not yet run): `journey.py` `reference_table()` (admin creates `wf699-region-loading`,
  keyed on `region`, payload `expense_loading` 1.00, effective from 2020-01-01, published and pinned
  in `pins.reference_tables`); `fork()` inserts `s_loading` (`lookup`, `as_at: effective_date`,
  `on_miss: error`) and `number(expense_loading)` into `s_premium`; S1 scores a quote dated
  2019-06-01 and asserts 422 `REFERENCE_LOOKUP_MISS`. Honest reading, not a silent pick: the
  freMTPL2 contract has no outcode input (the WF's "outcode → rating area" key), so the key is
  `region`, the nearest existing geography input, and the loading is 1.00 so goldens are unaffected.
  Pure test `test_b3_the_fork_puts_a_pinned_as_at_lookup_in_the_premium`; B3 added to the end-to-end
  test's required steps.
- **B3's geography key is `region` (the maintainer accepted it, `to-lead.md` "2026-10-11 23:48:51 BST").
  Deviation recorded: WF-699 B3's "outcode → rating area" is walked on freMTPL2's `region`.** The
  maintainer added one assertion, because a 1.00 loading makes consumption unobservable (the 2019 422
  proves the step is consulted, not that `s_premium` multiplies by it). Authored: the base region has
  a second reference row, 1.05 effective from 2027-01-01 (after every golden and demo quote date, so
  no golden moves); the first row ends there. S1 scores the same region on 2027-06-01 and asserts the
  premium is exactly the earlier premium × 1.05 in Decimal, half-even to whole minor units, else
  `LOADING_NOT_MULTIPLIED_INTO_THE_PREMIUM`. A possible ±1 from double rounding (the earlier premium
  is itself rounded) is not accepted as a tolerance; if the slot shows it, it is reported, not
  absorbed. RED on a wiring that drops the multiply: the slot script's `red_b3_multiply` stage
  scratch-reverts the multiply in `journey.py`, runs the end-to-end test and restores the file; its
  line is recorded here at the slot, or this test is recorded as a GUARD if it cannot be shown.
- **Acceptance 5, split (accepted):** CI stays synthetic (the in-process journey test); Acceptance 5
  is met by the real full-seed one-command rehearsal in an ALONE window, and this ledger will quote
  its command, tree, the "20,000 rows ran" line and exit code verbatim. The lead books the window.

#### Reds (each by its cause), authoring

| Task | Test | Red line as printed |
|---|---|---|
| 1 | `backend/tests/test_wf699_journey.py` (collection) | `ERROR backend/tests/test_wf699_journey.py - FileNotFoundError: [Errno 2] No s…` (`examples/fremtpl2/journey.py` absent) |
| principals | `examples/fremtpl2/test_seed.py::test_the_demo_principals_use_existing_roles_and_cover_the_journey` | `ImportError: cannot import name 'DEMO_PRINCIPALS' from 'seed'` |
| D4 | `test_the_d4_property_does_not_depend_on_the_fit` | `AttributeError: module 'demo_journey' has no attribute 'declared_d4_property'` |
| 5 | `test_the_seed_record_pre_flight_runs_before_the_rule_set_pre_flight` | `ValueError: substring not found` (no `check-seed-record.py` in `demo`) |
| 5 | `test_postcondition_http_error_is_a_refusal` | `urllib.error.HTTPError: HTTP Error 403: Forbidden` escaping `_verify_journey_postconditions` |
| 5 | `test_the_journey_flag_names_one_journey_and_defaults_to_none` | `AttributeError: module 'demo_script' has no attribute 'JOURNEYS'` |
| 5 | `test_the_journey_runs_with_a_worker_after_the_postconditions_and_before_the_frontend` | `ValueError: substring not found` (no worker in `demo`) |
| 5 | `test_a_journey_failure_exits_non_zero_with_the_step_line` | `SystemExit: 2` (`--journey` unrecognised) |

DB-backed reds (`test_the_seed_record_pre_flight_refuses_*`, `test_an_id_that_contradicts_the_stored_identity_is_refused_where_it_arises`,
`test_wf699_journey_runs_end_to_end`) are written and wait for the lead's slot; their red-by-cause
lines are recorded at the slot, against the parent source.

#### Commits (authoring, pushed to `origin/sl-1527-wk1178-exit-demo-b`)

| Task | What | Commit |
|---|---|---|
| 1 | the journey test, red | `9b041b42` |
| principals | `grant_demo_principals`, `DEMO_PRINCIPALS`, ids recorded | `9352b424` |
| 1-2 | journey core, skip table, step-naming client | `fbd418ce` |
| 2-4 | phases A to E, deploy, served quote; the D4 declaration; the ladder body | `d918c534` |
| 4 | the end-to-end journey test, authored | `e328556c` |

## PRs

The slice's PR is opened at the lead's word, after the full gate and the Acceptance 5 rehearsal;
its number and merge commit are recorded here at merge.
