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
plans: [PL-1544, PL-1577]
corrected_by: []
relates: [PL-1544, PL-1577, RL-1521, RL-1524, FD-1209, FD-1244, FD-1245, FD-1494, LG-1641]
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
