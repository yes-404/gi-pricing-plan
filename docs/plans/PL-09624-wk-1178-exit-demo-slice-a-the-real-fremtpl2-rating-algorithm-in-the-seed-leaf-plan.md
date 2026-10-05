---
id: PL-9624
family: plan
kind: leaf
title: WK-1178 — exit-demo slice (a), the real freMTPL2 rating algorithm in the seed, priced from the approved GLM through its seeded rate tables (FR-230, FR-237, FR-246, FR-257, FR-260): leaf plan
status: draft                  # draft → active → superseded | retired (§1.2a)
created: 2026-10-05
owner: planner
tree: 809a3794af6d3a6ba688663b0d9b59f951190680
phase: P2
work: WK-1178
supersedes: []
superseded_by: ~
corrected_by: []
relates: [PL-1371, FD-1209, FD-1357, RL-1361, PL-1376, SL-1377, FD-1374, RL-1343, RL-1263, SL-1409, PL-1408]
---

# PL-9624 (working id) — WK-1178: exit-demo slice (a), the real freMTPL2 rating algorithm in the seed, leaf plan

Filed under working id 9624 (this plan) and slice working id 9626 (its `SL-` row under
WK-1178 in [`../roadmap.md`](../roadmap.md), `draft`), both reserved by the lead. It is the
first of the two leaf plans `PL-1371` Task 3 orders: *"Task 3 (the planner, on the lead's
order): cut the exit-demo SL rows under DP-1's Work, `draft`, in `docs/roadmap.md`, and write
their leaf plans in §5's preparation order"* (`PL-1371` §Tasks). The lead's order is dated
2026-10-05 15:06 BST. The second leaf, exit-demo slice (b), is PL 9629 (working id), filed
in its own PR, which depends on this one for the two `SL-` rows.

**Why (a) comes first.** `PL-1371` §5's preparation order puts "(11) the exit-demo leaves,
under WK-1178 (DP-1 (a))" as one item, so the order within it comes from the dependency
graph: Appendix A gives DEMO-a the single dependency `["1178-FD1357"]` and DEMO-b the
dependency list `["673-S6", "674-S2", "DEMO-a", "1178-FD1356", "1178-FD9752"]`, and its G2
list orders `"DEMO-a"` before `"DEMO-b"` (`PL-1371` Appendix A, the `DEMO-a`, `DEMO-b` and
`G2 = [` lines). §3.8 lists (a) as row 6 and (b) as row 7. (b) depends on (a), so (a) is
written first.

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended)
> or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`)
> syntax for tracking. The executor also binds `python-test` (the `req` marker, negative
> tests), `test-driven-development` (every acceptance item is seen red, by its cause, before
> the code that turns it green), `python-package` (where the shared algorithm module lives),
> `dev-commands` (the two-half gate, the alembic DSN, `uv sync --all-packages`) and
> `git-hygiene`. Read [`README.md`](README.md)'s five unchecked conventions before the first
> step. The executor is spawned from `.claude/roles/executor.md`, model sonnet.

## Goal

The freMTPL2 demo seed's Rating Version is priced from the approved freMTPL2 GLM. Its tables
are seeded from that model with `seed_from_model`, one table per rateable Factor (`03`
FR-230, `RL-1361` section A). Its algorithm multiplies a base premium by the seeded
relativities and rounds once to the penny (FR-226). The base premium is **a simplification
(a frequency GLM × mean severity; no severity model)**, DP-a2's ruled label, so nobody reads
it as a modelled pure premium. The Rating Version pins that algorithm
version and every seeded Rate Table Version (FR-237). It replaces the demo fixture
`demo-fixture-motor`, whose docstring says *"`payable = premium_in * 2`. **Not priced from the
GLM**"* (`examples/fremtpl2/model.py:_demo_algorithm`, `:327-330`). One builder module
defines the algorithm, and the seed and exit-demo slice (b)'s journey both use it, so the
demo never carries two freMTPL2 algorithms that disagree.

It discharges the algorithm half of `FD-1209`. Its register row's event reads: *"the real
freMTPL2 algorithm exists in the seed and `WF-699` runs end to end on it"*
(`docs/findings/register.md`, the FD-1209 row). The `WF-699` half is slice (b)'s.

**Architecture:** a pure builder, `examples/fremtpl2/algorithm.py:build_fremtpl2_algorithm`,
takes the approved model's Factor slugs, the seeded table refs, the Bandings of the banded
factors and the base premium, and returns a `RatingAlgorithm` payload. The seed calls it
after `compare_and_approve` has approved the GLM, because `seed_from_model` refuses an
unapproved model (`platform/rate_tables.py:seed_from_model`, `check_model_approved`). The
engine has no banding step and matches table keys exactly
(`pricing_core/rating/runtime.py:221-227`, `:235-245`). So each banded factor's raw value
becomes its band label through one `expression` step, a chain of ZEN ternaries that the
builder generates from the Banding's boundaries and labels. ZEN's ternary is verified live:
*"ternary operator, **not** an `if(cond, a, b)` function"* (`runtime.py:298-301`).

**Tech Stack:** Python 3.12, Pydantic v2 (`model_schema.rating.RatingAlgorithm`), Polars, the
GoRules ZEN engine through `pricing_core.rating`, SQLAlchemy 2 async (the seed's service
calls), pytest.

**Spec, map plan and rulings:**
- [`../specs/03-rating-engine.md`](../specs/03-rating-engine.md): FR-212, FR-213, FR-226,
  FR-230 (with its 2026-10-03 clarification from `RL-1361` section A), FR-237, FR-240,
  FR-246, FR-257, FR-260, FR-261;
- [`../specs/02-modelling.md`](../specs/02-modelling.md): FR-97 and FR-101 (Bandings), under
  DP-a1 (a) only;
- [`../specs/07-platform.md`](../specs/07-platform.md): FR-440 (the demo seed's Rating
  Version);
- `docs/plans/PL-01371-p2-scope-freeze-lane-loading-plan-every-remaining-slice-against-the-code-freeze-map-plan.md`,
  §3.8 row 6 and §7 ("Exit demo (a)");
- `docs/rulings/RL-01361-*.md` sections A and D (one table per Factor; a continuous factor is
  refused);
- `docs/findings/FD-01374-fr-246-s-declared-inputs-rule-is-unenforced-for-names-and-03-s-own-example-declares-no-inputs.md`,
  §"Disposition" item 4 (the interim guard this slice carries);
- `docs/rulings/RL-01343-*.md` (decimal outputs; why this slice declares none).

## The decisions this plan rests on, quoted

`PL-1371` §7, accepted by the maintainer with four amendments on 2026-10-03 (`PL-1371` §9):

> "**Exit demo (a): the real freMTPL2 rating algorithm in the seed.** Depends on the FD-1357
> fix only. It needs neither WK-673 nor WK-674, so it takes the first free slot after item 1.
> Acceptance, as the maintainer set it in `holds-2026-10-01.md` ("Saturday lane-loading plan
> — items to include"): PL 9776's Spike S1 harness re-run on the new algorithm, and "every
> step's reads ⊆ its declared consumes", shown by running FD 9773's P5 sweep script on it (0
> undeclared reads). Its dispatch record also states "declares no decimal output" until the
> RL-1343 fix merges (the maintainer's guard). It discharges FD-1209's algorithm half."

FD 9773 is minted as `FD-1374`. Its Disposition item 4 reads: *"**Interim guard.** G2's
Exit-demo slice (a) acceptance line, "every step's reads ⊆ its declared consumes", checked by
running the sweep on the new algorithm with 0 undeclared reads. Until enforcement lands, that
line is the only guard."*

**DP-a0 to DP-a3 and activation need 3, ruled by the maintainer (by delegation)**, entry
headed *"2026-10-05 15:28:26 BST — Wave results: D1 = (c); D2 PL 9624 DPs; D3 PL 9629 DP-6 +
plan the 2 missing G2 items; C1′ is FD 9995 (no new finding); FD 9619 noted"*, item D2,
verbatim:

> D2 (leaf (a) PL 9624):
>  - DP-a0: do NOT adopt S3's model_call fixture (a GLM cannot be scored via model_call on main). AGREED.
>  - DP-a1: band the 3 continuous factors (driv_age, veh_age, veh_power) and refit, keeping SEVEN factors, so G2's "7-factor freMTPL2 GLM" (the maintainer's 2026-10-01 08:01:45 entry, roadmap :603) still holds. Condition: the plan records the band edges and their source, and the refit's fit statistics beside the current model's (deviance, AIC, the factor list), so the change is visible, not silent. AGREED.
>  - DP-a2: the base rate = exp(intercept) × the mean freMTPL2sev claim cost. AGREED, labelled in the plan and the demo script as a simplification (a frequency GLM × mean severity; no severity model), so nobody reads it as a modelled pure premium.
>  - DP-a3: FD-1374's lost sweep rebuilt as a committed test from FD-1374's verbatim predicate. AGREED.
>  - Activation need 3 (PL 9776's Spike S1 is NOT filed, yet leaf (a)'s acceptance re-runs its harness): an acceptance criterion must not depend on an unfiled instrument. The planner either drops that clause, replacing it with DP-a3's committed test where that covers the same claim, or files the spike as a research record (RS) first. The planner proposes which; I rule at the plan's ACK.

The entry is a local channel entry, which a repository reader cannot resolve (RFC-777). It is
quoted here so the plan carries it; the ruling's governed home, if one is needed beyond this
plan, is the lead's to route at the mint. The roadmap anchor `:603` is the Exit demo row at
`809a3794` (`docs/roadmap.md`, the row whose first cell is `**Exit demo**`).

**Activation need 3, ruled by the maintainer (by delegation)**, entry headed *"2026-10-05
15:42:02 BST — Mint 1 (RL-1418) noted; need 3 conditional; WK-674 S3 prep accepted; G2 vs
WF-699's PERIL PATH: a scope question for the maintainer, SIZE it first"* (`RL-1418` merged
as `137bc817`, #1128), its paragraph on need 3, verbatim:

> NEED 3 (PL 9624): option (i) is ACCEPTED ONLY IF a3's committed test also does S1 step 1's extractor-vs-engine cross-check (the extractor's static reads against the engine's actual reads on the seed algorithm, both computed, compared, red on a planted mismatch). That cross-check is the instrument FD-1374's guard rests on, and the plan's own note admits (i) drops it. With it added, no RS is needed; PL-1371 §7's wording difference goes as a dispatch delta (PL-1371 is frozen). a1's band edges from the seed run, as an acceptance item: OK.

The same entry's closing line bounds this plan while the G2 peril-path scope question is open:
*"Until then, PL 9629 and PL 9624 continue for the shared parts (A1–A2, C–E with seeded
tables)."* This slice is A1–A2's seeded tables and the algorithm over them, so it continues.
The same local-entry caveat as above applies (RFC-777).

**The scope question is now decided: Option A.** The maintainer's entry headed *"2026-10-05
16:43:31 BST — THE MAINTAINER'S DECISION (asked live): G2 takes OPTION A, WF-699's literal
Peril Structure path is BUILT IN P2; and the FD 9605 approval, now on the record"*, item 1,
verbatim:

> 1. Four serial build slices under WK-1178, as sized: A-1 FD 9995 in full (the peril approval carry plus the _Resolver peril branch; it flips PL 9683's Acceptance 7); A-2 GLM via model_call (FD 9605); A-3 Peril Structure scoring (compile resolves and maturity-checks the component models; the runtime calls assemble_risk_premium, fixing the bare KeyError on payload["fit_result"] at runtime.py:540); A-4 the demo scope on PL 9624/PL 9629 (a severity GLM, the peril structure, reconcile, approve, the B4 model_call, the C1 pin). About 5 executor-days likely (3.5–8), a chain after PL 9683 and PL 9649.

**This slice's scope does not change.** A-4 is cut as its own slice, SL 9594 / PL 9593
(working ids, reserved), which follows this slice and slice (b). It is not an edit to this
plan. A-4 needs A-1 to A-3 merged and the double-count ruling (item 4 of the same entry), and
this slice needs neither. DP-a0 (no `model_call`) and DP-a2 (the base rate, labelled a
simplification) still hold for this slice. A-4 adds the severity GLM and B4's `model_call` on
top, in the form the double-count ruling decides. The same local-entry caveat applies
(RFC-777).

## Status

`draft`. **DP-a0 to DP-a3 are ruled** (above): DP-a0 (a), DP-a1 (a) with its condition
(Acceptance 11), DP-a2 (i) + (x) with its label (Acceptance 8, Task 1), DP-a3 (a).
**Activation need 3 is ruled (i), on a condition** (15:42:02 BST, quoted above): Acceptance 4's
committed test also performs Spike S1 step 1's extractor-vs-engine cross-check. That
condition is written into Acceptance 7 and Task 1 Step 1; whether the text meets it is the
maintainer's (by delegation) check at the plan's ACK. The tasks below are written for the
ruled options. The plan moves to `active` only
through a separate activation PR, after every activation need below holds. That PR carries
the `SL-` row's status flip and this plan's.

### Activation needs, in order

1. **The FD-1357 fix merged.** `SL-1377` is `closed` (`docs/roadmap.md`, the `SL-1377` yaml
   block) and its code merged as `8252741c` (#1087). **Met.** This is the only *build*
   dependency `PL-1371` §7 names ("Depends on the FD-1357 fix only"). §3.8 row 6 lists two
   more, "Spike S1 of PL 9776 filed; FD 9773 minted". FD 9773 is minted (`FD-1374`). Spike S1
   is need 3.
2. **DP-a0 to DP-a3 ruled.** **Met**: the maintainer (by delegation), entry 2026-10-05
   15:28:26 BST, item D2 (quoted above).
3. **Activation need 3 ruled**: (i) or (ii) of §"Activation need 3: the proposal".
   **Ruled (i), on the condition that the committed test also performs S1 step 1's
   extractor-vs-engine cross-check** (15:42:02 BST, quoted above; Acceptance 7). **Met when
   the maintainer (by delegation) confirms at the ACK that Acceptance 7 meets the condition.**
   The need as first written was *"PL 9776's Spike S1 filed"*. At `809a3794` none is filed:
   `git grep -n -E '9776|Spike S1' origin/main -- docs/research` finds no F35 spike, and PL
   9776 is draft #1051 @`ecbb82ab`. The ruling's rule is *"an acceptance criterion must not
   depend on an unfiled instrument"*. Under (i) this slice needs no spike at all (*"With it
   added, no RS is needed"*). (ii), filing S1 as an `RS-` first, is the fallback only if the
   cross-check proves impossible in a committed test; §"Activation need 3: the proposal" says
   why it is not.
4. **Serialisation on shared files** (§"Write set"): `SL-1409` (the FD-1356 fix, `active` on
   lane B) merged, because it edits `examples/fremtpl2/seed.py`. **That half is met:** `SL-1409`
   is `closed`, merged as `cdaaa573` (#1157). The FD 9708 fix (PL 9683,
   working id, #1140) merged first if it is active first, because it edits the same two
   functions of `examples/fremtpl2/model.py`. Under the maintainer's (by delegation) priority rule, entry
   "2026-10-05 13:12:56 BST — DECISIONS 15 and 16; CORRECTION to my 13:03:23 item 11; a priority
   rule for HIGH G2 blockers", *"a HIGH finding that blocks G2 (FD 9707, FD 9708) takes the first
   build lane that frees once its plan is active"*.
5. **The lead's go**, in a separate activation PR, with a dispatch record that states
   *"declares no decimal output"* while the `RL-1343` fix is unmerged (`PL-1371` §7).

### Activation need 3: the proposal (the maintainer (by delegation) rules at the ACK)

**What Acceptance 7 claimed.** PL 9776 §"Spike S1" step 5 (#1051 @`ecbb82ab`) says the re-run
on G2's algorithm *"includes steps 1 and 6 (reference sets, added edges and cycles), not only
step 3's equality"*. Step 1 lists *"every step whose set is not a subset of its declared
`consumes`, with the extra names"*. Step 6 lists *"every step whose reference set adds an edge
beyond its declared `consumes`"* and *"every added edge that closes a cycle"*. So this slice's
claim is: the built algorithm has (1) no read outside `consumes`, and (6) no added edge and so
no added cycle.

| Option | What it does | For | Against |
|---|---|---|---|
| **(i)** | **Drop Acceptance 7's harness re-run.** Acceptance 4 (DP-a3's committed test, FD-1374's predicate verbatim) carries both claims. Claim (1) is Acceptance 4's assertion. Claim (6) follows from it: step 6's added edges are exactly the reads outside `consumes`, so 0 undeclared reads means 0 added edges, and with no added edge the graph is the declared one, which compiles as a DAG (FR-212; Acceptance 2's `rating.compile` Job). Acceptance 7 is rewritten to state that derivation and to assert it in the test (below) | No dependency on a draft plan's executor; the check is committed, runs on every gate and cannot vanish with a job dir (the reason DP-a3 (a) was ruled). PL 9776's own corpus rule (step 5: *"every multi-step algorithm that exists when S1 runs"*) takes this algorithm in automatically if S1 runs after this slice merges, so F35 loses nothing | Two parts of S1 step 1 are not reproduced: the cross-check of the extractor against the engine (*"with the reference set alone in the context must succeed, and with one name removed must fail"*), and Task 1A's `referenced_names` as the extractor. Acceptance 4 uses FD-1374's predicate, not Task 1A's code, which does not exist on `main` (P6). Step 3's equality (the M1 wire) is not part of this slice's claim, before or after |
| (ii) | **File Spike S1 first** as an `RS-` of `kind: spike` (PL 9776 §"Spike S1"), then re-run its harness here, as Acceptance 7 first said | Keeps `PL-1371` §7's accepted wording, including the engine cross-check | Puts F35's spike, unscheduled and owned by another plan's executor, on G2's critical path. `PL-1371` §7 itself refused that chain the other way (*"S1 does **not** wait for G2"*, PL 9776 step 5) |

**Recommendation, as first proposed: (i).** It holds every claim this slice makes about its
own algorithm with a committed test, and leaves the engine cross-check where it belongs, in
F35's spike, which re-reads this algorithm when it runs. **The departure from `PL-1371` §7's
accepted acceptance wording** (*"PL 9776's Spike S1 harness re-run on the new algorithm"*) is
stated here and is the maintainer's to accept at the ACK. `PL-1371` is frozen and is not edited.

**Ruled (15:42:02 BST): (i), only with the cross-check added.** The table and recommendation
above are kept as written, so the ruling's reason stays readable: the "Against" cell of (i)
is what the condition removes. Under the ruling, Acceptance 4's test module also performs S1
step 1's extractor-vs-engine cross-check (Acceptance 7, Task 1 Step 1). The second gap in that
cell stays: the extractor is FD-1374's predicate, not Task 1A's `referenced_names`, which does
not exist on `main` (P6). `PL-1371` §7's wording difference goes to the dispatch record as a
delta (Hand-off 5).

**Why the cross-check fits a committed test** (the condition for (i); (ii) is the fallback only
if it does not). S1 step 1's method is *"`zen.evaluate_expression` (or
`zen.compile_expression`, whichever the binding exposes) with the reference set alone in the
context must succeed, and with one name removed must fail"* (PL 9776 §"Spike S1" step 1,
#1051 @`ecbb82ab`). Three facts, read at `cdaaa573`:

- **The engine is in-process and already a dependency.** `zen-engine==0.53.0` is pinned in
  `packages/pricing-core/pyproject.toml`, and `pricing_core/rating/compile.py` imports `zen`
  and calls `zen.compile_expression`. The binding's stub (`zen/__init__.pyi`, 0.53.0)
  declares `evaluate_expression(expression: str, context: Optional[ZenContext] = None) -> Any`.
  No server, database or runtime beyond the test process is needed.
- **The fields the engine evaluates are enumerated in code.** `pricing_core.rating.authored`
  `EXPRESSION_FIELDS` names them (`key_expr` of `lookup` and `table`, `expr`, `condition`,
  `clamp_bounds`), and `authored_expression_fields(algorithm)` returns every such string of
  an algorithm with its step and field. A `lookup`'s `as_at` is in `NON_EXPRESSION_FIELDS`
  (*"nothing evaluates it"*), so it has no engine side: the cross-check covers it by
  FD-1374's predicate only, and says so. The `feature_map` keys belong to `model_call`,
  which this algorithm has none of (DP-a0).
- **"Must fail" needs one adjustment, measured, not assumed.** Probed on 2026-10-05 against
  `zen-engine` 0.53.0 (a one-off `python -c` in an existing worktree venv; no test run):
  `a + b` with `{"a": 1}` raises `RuntimeError` (`vmError`, *"Opcode Add: Unsupported
  type"*), but the bare `a` with `{}` returns `None`, and `a > 1 ? x : y` with `{"a": 2,
  "y": 1}` returns `None`. A missing name can evaluate to `null` without an error. So the
  committed test reads "succeeds" as **"returns the same value as with the full context"** and
  "fails" as **"raises, or returns a different value"**, and it chooses its contexts so that
  every name is on the evaluated branch at least once (below). Otherwise a name read only in
  an untaken branch, or returned bare, would pass the extractor unchecked.

## Acceptance Standard

Each item is checked by a command run from the repository root on the merge tree. "Red
first" means the named test was run and failed **for the stated cause** before the code that
turns it green. A failure with the right status and a different cause is a plan defect
([`README.md`](README.md) rule 2). Each red is recorded in the slice's ledger, with the
failure line as printed.

1. **Every rateable factor is seeded from the approved GLM** (FR-230). The seed calls
   `seed_from_model` once per Factor in the model's relativities, one slug per Factor
   (`fremtpl2-<factor slug>`). Under DP-a1 (a) that is all seven; under (b) or (c) it is the
   four categorical ones. Test: `test_the_seed_seeds_one_table_per_rateable_factor` in
   `backend/tests/test_demo_rating_evidence.py`. Each table's `seeded_from` names the
   approved GLM's ref, and each key's `factor_ref` names the model's Factor version.
   Red first on the base tree (the seed seeds no table: `_EMPTY_PINS`, `model.py:322-324`).
2. **The Rating Version pins the algorithm and every seeded table** (FR-237). Its `pins.rate_tables`
   lists exactly the Acceptance 1 refs at their seeded versions, and its `pins.models` lists
   the approved GLM. It compiles through the `rating.compile` Job. Test:
   `test_the_demo_rating_version_pins_every_seeded_table`. Red first: on the base tree,
   `pins.rate_tables == []`.
3. **The premium is the GLM's, to the penny** (the "real" in "real algorithm"). For three
   fixed quote contexts (named in the test, chosen to cover the base level, a non-base level
   of every factor, and a band edge of every banded factor), the scored
   `payable_premium_minor` equals the premium computed independently from the fitted model:
   `base_premium × Π exp(β_level)`, computed with `Decimal` from `GlmFitResult.coefficients`
   (not from the seeded tables), then rounded `half_even` to 0 dp in minor units. Test:
   `test_the_demo_premium_is_the_glm_premium`. Red first: on the base tree the scored premium
   is `premium_in * 2`.
4. **Every step's reads ⊆ its declared consumes** (FD-1374's interim guard; FR-246). Under
   DP-a3 (a), `test_the_demo_algorithm_reads_only_what_it_declares` in
   `backend/tests/test_fremtpl2_algorithm.py` applies FD-1374's predicate, verbatim from its
   §"The sweep", to every step of the built algorithm. It asserts 0 undeclared reads and
   prints the per-step read sets. **Broken-input proof:** the same test module holds
   `test_the_reads_check_refuses_an_undeclared_read`, which removes one name from one table
   step's `consumes` and expects exactly one undeclared read naming that step. Both are
   recorded red-then-green in the ledger. If PL 9776's Task 1A (FR-246 enforced at save) has
   merged before dispatch, its save-time refusal also guards this, and the ledger says so.
5. **No decimal output** (`PL-1371` §7; `RL-1343` §4). Every entry of the algorithm's
   `outputs` has `type == "money_minor"`. Test:
   `test_the_demo_algorithm_declares_no_decimal_output`. It is removed only by the slice that
   merges the `RL-1343` fix.
6. **The regression evidence is real** (FR-257 limb (1), FR-260, FR-261). The seed's
   Regression Suite holds the three Acceptance 3 contexts as golden quotes. Their expected
   values come from Acceptance 3's independent computation, never from `score_one` on the
   bundle under test, which is what makes today's golden quote circular (`model.py:413`). It
   also holds the properties `no_null_output`, `premium_bounded`, and one monotone property
   on a banded factor whose fitted relativities are monotone (named by the executor from the
   fit, with the fit's relativities quoted in the ledger). The `rating.regression` Job ends
   `succeeded`. Test: the existing `test_demo_rating_evidence.py` assertions, rewritten.
   Red first: `expected_minor == DEMO_PREMIUM_IN * 2` (`test_demo_rating_evidence.py:73`)
   fails once the fixture is gone.
7. **Spike S1's claims on this algorithm: no read outside `consumes`, no added edge, no
   added cycle, and the extractor agrees with the engine** (`PL-1371` §7; PL 9776 §"Spike S1"
   steps 1 and 6). **Under activation need 3 (i), ruled with its condition (15:42:02 BST):**
   held by committed tests in `backend/tests/test_fremtpl2_algorithm.py`, with no harness
   re-run and no `RS-`.
   - **(a) Edges.** `test_the_demo_algorithm_reads_only_what_it_declares` also asserts that
     the graph built from each step's read set has the same edges as the graph built from its
     `consumes` (0 added edges), which with Acceptance 2's compile is 0 added cycles. The
     ledger records the derivation in one line beside Acceptance 4's output.
   - **(b) The extractor-vs-engine cross-check (S1 step 1; the ruling's condition).**
     `test_the_reads_extractor_agrees_with_the_engine` computes **both sides** for every
     string `pricing_core.rating.authored.authored_expression_fields` returns for the built
     algorithm. **Extractor side:** the string's reference set by Acceptance 4's helper
     (FD-1374's predicate). **Engine side:** `zen.evaluate_expression(text, ctx)` on (1) the
     full context, (2) the context cut to the reference set alone, and (3) for each name in
     the set, the cut context with that name removed. It asserts (2) equals (1): the engine
     reads nothing outside the set. For each name it asserts (3) raises or differs from (1):
     the engine reads every name the extractor claims. **Contexts:** every raw input takes its
     value from each of Acceptance 3's three contexts, and each band ternary is also run once
     per band, with a value inside it (the band values `test_band_expression_maps_each_edge`
     uses). Every produced name takes one fixed non-null value of the type its producing step
     declares. A (string, name) pair counts as checked if (3) holds under at least one
     context. **A pair checked under no context is a failure** that names the string and the
     name: ZEN returns `null` for a missing name in some positions (§"Activation need 3: the
     proposal"), so "no error" alone is not "not read". A lookup's `as_at` is not evaluated
     by the engine (`NON_EXPRESSION_FIELDS`), so it has no engine side; the test lists it as
     "predicate only" and does not count it as checked. The test prints, per string, its
     reference set and the engine verdict for each name. The ledger records that output.
   - **(c) Red on a planted mismatch.** `test_the_cross_check_refuses_a_planted_mismatch` runs
     the same comparison function on one real step's string from the built algorithm, twice.
     Under-reported: a reference set with one real name removed must give exactly one
     "engine reads outside the set" failure that names it. Over-reported: a reference set with
     one name added that the string does not contain must give exactly one "extractor claims
     a read the engine does not make" failure that names it. Both tests are recorded
     red-then-green in the ledger, beside Acceptance 4's broken-input proof.

   **Under (ii)** (the fallback, only if (b) proves impossible in a committed test): the
   harness is run verbatim from Spike S1's `RS-` (sha256 prefix checked) on the built
   algorithm. Step 1 must list 0 names outside `consumes` (agreeing with Acceptance 4), and
   step 6 must list 0 new edges and 0 cycles. Output in the ledger with the `RS-` id. If the
   executor finds (b) cannot be built (for example, an evaluated field whose text
   `zen.evaluate_expression` cannot take alone), that is a STOP to the lead with the failing
   string, not a quiet fall-back to (ii).
8. **The demo still runs.** `uv run python scripts/demo.py --rows 20000` exits 0 on the slice
   head and prints its `/demo` URL. This is run once by the executor, alone on the box with no
   gate slot held, with the elapsed time recorded. The seed's printed line names the
   algorithm slug and "priced from the GLM", not "demo fixture", and labels the base premium
   *"a simplification (frequency GLM × mean severity; no severity model)"* (DP-a2's ruled
   label), as the base step's `note` and the algorithm's change note also do.
9. **The gate.** Both halves green on the slice head (`dev-commands`), through the
   gate-runner holding a slot (`RL-1263`). `generate-contracts.py --check` rc 0 (no contract
   changes are expected). `audit-docs.py` red only on check 31 before the mint and clean
   after.
10. **Scope held.** `git diff --stat origin/main...HEAD` touches only §"Write set"'s paths.
11. **The refit is visible, not silent** (DP-a1's ruled condition). The slice records, in
    its ledger and its PR body, both of the following.
    - (a) **The band edges and their source**, per banded factor (`driv_age`, `veh_age`,
      `veh_power`). The source is fixed by this plan: `transform_service.propose_banding_for_version`
      (`backend/src/app/platform/transformations.py`), method quantile, 5 bands, on the seed's
      validated freMTPL2 dataset version (Task 2 Step 1). The edges and labels are the saved
      Banding's own, read back from its artifact with its id and version. They cannot be
      written into this plan before the build, because they are an output of that call on the
      seeded data, and no code is run in a preparation wave.
    - (b) **The refit's fit statistics beside the current model's**, as one table with two
      columns (base tree, slice head): deviance and AIC
      (`model_schema.diagnostics.GlmDiagnostics` fields `deviance` and `aic`; Poisson has a
      closed-form likelihood, so `aic` is not `None`), and the factor list with each factor's
      `FactorType`. Both columns are computed by the same code on the same seeded rows (the
      `--rows` value is recorded), the base-tree column on `809a3794` or the dispatch tree.
    Check: the ledger table exists with both columns non-empty and seven factors in each; the
    seed's printed model line names the seven factors. No test asserts the figures (they are
    data, not behaviour), so this item has no red-first step.

## Global Constraints

- **Money is integer minor units, or Decimal in the rating path, never float** (`CLAUDE.md`
  §7). The base premium is computed with `Decimal` and enters the algorithm as an integer
  literal in minor units. Relativities enter as the seeded tables' decimal strings
  (`operations.py:159`). Acceptance 3's independent computation uses `Decimal` throughout,
  including `Decimal.exp()`.
- **No pandas** (`CLAUDE.md` §3). The seed already uses Polars.
- **Nobody hand-writes a shape that already exists in `model-schema`** (`CLAUDE.md` §2). The
  builder returns a dict validated by `RatingAlgorithm.model_validate` before it is saved.
- **Model and rating definitions are declarative JSON artifacts, never pickles** (`CLAUDE.md`
  §2). The algorithm is saved through `algorithm_service.create_algorithm`. If DP-a0 (b) is
  ruled, it is loaded from `examples/fremtpl2/rating/`'s JSON.
- **No decimal output** until the `RL-1343` fix merges (`PL-1371` §7).
- **Enforcement is proven on deliberately broken input** (`CLAUDE.md` §13): Acceptance 1–6
  are each red first, and Acceptance 4 has its own broken-input test.
- **Shared files** (`RL-1263` option (c)): two concurrent build slices may not both change the
  same existing function, class, spec section or policy table. `docs/INDEX.md` is a
  registry: regenerate, never hand-merge.
- **No spec text is written by this slice** unless a ruling carries it verbatim. FR-440's
  "minimal Rating Version" is a floor, and this slice exceeds it without changing it.

## Scope

### Requirement coverage, each id individually

| Spec | Id | What this slice holds | Marker |
|---|---|---|---|
| `03` | FR-230 | Each rateable Factor's table is seeded from the approved GLM, `seeded_from` recorded | `req("FR-230")` on Acceptance 1 |
| `03` | FR-237 | The Rating Version pins the algorithm version and every seeded table version | `req("FR-237")` on Acceptance 2 |
| `03` | FR-212 | The algorithm is a valid DAG and compiles | existing compile tests; Acceptance 2 |
| `03` | FR-213 | The input contract declares each of the seven raw rating inputs with type and domain | `req("FR-213")` on the builder test |
| `03` | FR-226 | One `output` step, `half_even`, 0 dp, in minor units | `req("FR-226")` on Acceptance 3 |
| `03` | FR-240 | The bundle compiles with every pin resolved and approved | Acceptance 2 (regression only) |
| `03` | FR-246 | Every step's reads ⊆ its consumes (the interim guard) | `req("FR-246")` on Acceptance 4 |
| `03` | FR-257 | The submission carries a passing Regression Suite whose golden quotes are not circular | `req("FR-257")` on Acceptance 6 |
| `03` | FR-260 | Golden quotes with independently computed expected values | `req("FR-260")` on Acceptance 6 |
| `03` | FR-261 | One monotone property on a banded factor | `req("FR-261")` on Acceptance 6 |
| `02` | FR-97 | *(DP-a1 (a) only)* the three continuous columns become Bandings | `req("FR-97")` on the seed test |
| `02` | FR-101 | *(DP-a1 (a) only)* the Bandings are versioned artifacts saved through the service | existing tests; no new marker |
| `07` | FR-440 | The seed's Rating Version is still created and approved; it now pins tables too | existing `test_demo_rating_evidence.py` |

### Premises, read at `809a3794` (verified against the source)

- **P1. Only categorical factors can be seeded.** RL-1361 §A: *"A continuous factor is one
  [refused], because it has no relativity table"*. The pure op refuses with *"factor {factor!r}
  names no relativity entry of model ..."* (`pricing_core/rate_tables/operations.py:194-198`),
  returned as 422 `VALIDATION_FAILED`, and `test_api_rate_tables.py:1232`
  (`test_a_factor_that_names_no_relativity_entry_is_a_422`) pins it. The demo's GLM has
  seven `FactorType.IDENTITY` factors (`examples/fremtpl2/model.py:_create_factor`,
  `:143-166`): three continuous (`driv_age`, `veh_age`, `veh_power`, `:60-64`) and four
  categorical (`veh_brand`, `veh_gas`, `area`, `region`, `:65-70`). So **four** tables can be
  seeded today, not seven. `WF-699` A2 reads *"Repeats for every rateable factor across
  perils"* (`docs/workflows/WF-00699-approved-models-to-approved-rating-version.md:42`), so
  four is not a spec breach. It is the reason for DP-a1.
- **P2. A banded factor is categorical and seedable.** `apply_banding` returns a
  `pl.String` series of band labels (`pricing_core/modelling/bandings.py:apply_banding`), and
  the design matrix treats a `String` column as categorical (`modelling/factors.py:223-224`).
  So a `FactorType.BANDING` factor gets relativity levels and a seedable table. Bandings are
  saved through `transform_service.create_banding(session, workspace_id=, actor=, banding=)`
  (`backend/src/app/api/models.py:create_banding`, `:395-411`).
- **P3. The engine has no banding, and `model_call` cannot price a GLM.** A `table` step
  becomes an exact-match ZEN decision table (`runtime.py:235-245`, `"hitPolicy": "first"` at
  `:264`). `interpolation != "none"` raises (`:221-227`). A `model_call` on a non-GBM model
  returns `_model_call_failure` (`runtime.py:568-579`), pinned by
  `test_rating_score.py:test_a_model_call_failure_is_refused_with_the_real_message`.
- **P4. No table carries the intercept, and the model is frequency only.** The seed reads only
  `fit.relativities` (`operations.py:139`). The intercept is `GlmFitResult.coefficients` term
  `"intercept"` (`model_schema/modelling.py:1616-1617`). The GLM is Poisson/log on
  `claim_count` with offset `log(exposure_years)` (`model.py:219-228`; family and link are the
  defaults, `modelling.py:1040-1045`). The seed already joins freMTPL2sev's claim amounts in
  integer minor units (`seed.py:108-125`).
- **P5. There is no route or service that creates a hand-authored rate table.** The
  rate-table routes are seed, bulk-operation, import and diff
  (`backend/src/app/api/rate_tables.py`, the `@router` decorators at `:70`, `:112`, `:159`,
  `:180`, `:205`, `:268`). The import's `import_confirmed` appends a version to an existing
  slug (`platform/rate_tables.py:419-430`). This decides DP-a2's options.
- **P6. FD-1374's sweep script is gone.** It is cited as
  `/home/puzhenhao1989/.claude/jobs/6fa41099/tmp/p5/sweep.py` and `p5b/sweep2.py`
  (FD-1374 §"The sweep"). Neither exists (`ls` at 2026-10-05 15:1x BST: "No such file or
  directory"), because a job's tmp dir is deleted with the job. No `def referenced_names`
  exists on `main`. The predicate survives verbatim in FD-1374 §"The sweep", which is what
  DP-a3 builds on.
- **P7. A measurement-only freMTPL2 algorithm is planned elsewhere.** PL 9689 (working id,
  WK-673 S3, #1138 @`e810b785`), DP-S3-6, decided (a): *"a measurement-only ZEN algorithm as
  a **declarative JSON fixture** (never code, never a pickle), named so the exit-demo slice
  can adopt it; no `seed.py` edit"*. Its fixture is
  `examples/fremtpl2/rating/fremtpl2-rate.rating-algorithm.json`, reproducing RS-1201's
  `rate()` with *"a `model_call` on a declarative GLM artifact, severity, an age table,
  expense load, min premium, cap"*. P3 says a GLM `model_call` cannot score on `main`. That
  decides DP-a0's options.
- **P8. The seed writes the Rating Version's `algorithm_ref` and `pins` directly**
  (`model.py:396-397`). PL 9683 (working id, the FD 9708 fix, #1140 @`78bfc54f`) moves that
  write behind the typed create route, editing `author_demo_rating_evidence` and
  `create_approved_rating_version` and adding `save_demo_algorithm` (its §"Write set").

### Write set, and its contention (`RL-1263`)

"Edited" means an existing definition changes; "added" means a new definition. Rows marked
*(DP-x y)* exist only under that option.

| Path | Change | Other slices touching it | Consequence |
|---|---|---|---|
| `examples/fremtpl2/algorithm.py` | added (new module): `build_fremtpl2_algorithm`, `band_expression`, `base_premium_minor`, `FREMTPL2_ALGORITHM_SLUG` | none | none. Slice (b)'s journey imports it |
| `examples/fremtpl2/model.py` | edited: `_create_factor` (`:143-166`, takes a `FactorType` and an optional `banding_id`) *(DP-a1 a)*, `fit_demo_models` (`:194-`, creates the three Bandings first) *(DP-a1 a)*, `author_demo_rating_evidence` (`:366-`), `create_approved_rating_version` (`:490-`); removed: `_demo_algorithm` (`:327-348`), `DEMO_PREMIUM_IN`, `_EMPTY_PINS`; added: `seed_demo_rate_tables` | **PL 9683** (FD 9708 fix) edits `author_demo_rating_evidence` and `create_approved_rating_version` and adds `save_demo_algorithm`; **PL 9688** (FD 9707 fix) and **PL 9728** (NFR-489) read `:323`, `:334-343` and `:413`; PL 9776 reads `:327-330` | **serial with PL 9683**: whichever merges second rebases on it and re-reads both functions. This slice keeps PL 9683's route-based create if PL 9683 has merged. Reads by PL 9688, 9728 and 9776: none |
| `examples/fremtpl2/seed.py` | edited: `run`'s order (`:609-623` at `809a3794`; `:651-665` at `cdaaa573`, after `SL-1409`): `seed_demo_rate_tables` after `compare_and_approve`, before `create_approved_rating_version` | **SL-1409** (`active`) edits `run`'s rule write (`:437-455`) and the order before the first `ingest` (`:536`) | **serial: SL-1409 first** (activation need 4), **met**: `SL-1409` merged as `cdaaa573` (#1157), so this slice re-reads `run` at its dispatch tree |
| `backend/tests/test_demo_rating_evidence.py` | edited: `:37-39` (the made-up `model_ref`), `:51`, `:68-73` (fixture assertions); added: Acceptance 1, 2, 3, 5 and 6 tests | **PL 9683** edits it; **PL 9688** and PL 9776 name it in their acceptance runs | serial with PL 9683, as above |
| `backend/tests/test_fremtpl2_algorithm.py` | added: the builder tests, Acceptance 4 (both tests), Acceptance 7 (b) and (c) (the cross-check and its planted mismatch) and the band-expression tests | none | none |
| `examples/fremtpl2/README.md` | edited: the seed's rating paragraph (the fixture becomes the real algorithm) | none found | none |
| the slice's ledger `docs/ledgers/LG-<n>`; `docs/INDEX.md` | added; regenerated | every PR | registry |

**Not written:** `backend/src/` (no route, service or schema changes), `packages/`,
`frontend/`, `docs/specs/`, `scripts/demo.py`, and `examples/fremtpl2/rating/` (PL 9689's
fixture directory) unless DP-a0 (b) is ruled.

**Open PRs read at `809a3794`** (`gh pr list --state open`, 2026-10-05 15:1x BST). These rule
on, or touch, this slice's subject: #1140 (PL 9683, above), #1138 (PL 9689, P7), #1145
(PL 9688, `lookup` only; this algorithm has no `lookup` step), #1113 (PL 9728, reads the
golden quote's in-process scoring), #1051 (PL 9776, Spike S1 and Task 1A), #1125 (FD 9717,
the seed record's pre-flight; slice (b)'s), and #1152 (PL 9649: a model with a
`control`-intent Factor or an unapproved custom objective is refused at approval and
compile; this GLM has neither, as every Factor is `FactorIntent.RISK` at `model.py:162`).

### Size

Small to medium: about one executor day. Four tasks after the preconditions. One refit of
the demo GLM under DP-a1 (a) (the seed's own fit path, already timed by `scripts/demo.py`).
One full two-half gate (a gate slot under `RL-1263`). No NFR is measured.

## Decision points

| DP | Question | Options | Recommendation | Owner | Blocks |
|---|---|---|---|---|---|
| **DP-a0** | Which freMTPL2 algorithm is "the real" one in the seed (P7)? | (a) built from the **seeded tables**, as this plan describes, so `WF-699` A1–A2's tables are the ones the Rating Version pins; PL 9689's fixture stays measurement-only. (b) adopt PL 9689's `fremtpl2-rate.rating-algorithm.json`. (c) both, with a test that they price identically | **(a).** G2's journey seeds the tables in A1–A2 and pins them in C1. A `model_call` algorithm (b) bypasses those tables, and on `main` a GLM `model_call` fails (P3). (c) is two definitions of one thing, which `CLAUDE.md` §2's rule exists to prevent | decision-maker (it settles how this plan relates to PL 9689's DP-S3-6 ruling, which named its fixture "so the exit-demo slice can adopt it") | Tasks 1–3 |
| **DP-a1** | How are the three continuous factors (`driv_age`, `veh_age`, `veh_power`) rated (P1, P3)? | (a) **banded**: each becomes a `FactorType.BANDING` Factor on a Banding (FR-97) proposed by `transform_service.propose_banding_for_version`, the service behind `POST /bandings/propose` (`api/models.py:332-352`), on the seed's dataset version. The GLM is refit with seven categorical factors, all seven are seeded, and the algorithm maps each raw value to its band label with one generated ternary `expression` step. (b) **linear**: they stay identity terms and enter the algorithm as `exp(β·x)` expression steps on literal coefficients. (c) **omitted**: the algorithm prices on the four categorical tables and the base only, and says so | **(a).** It is the rateable form RL-1361 names (*"through its bound Factor, its declared Banding"*), it makes A1–A2 seed all seven, and it is the UK rating-table form `WF-699` A3 assumes (*"softens `17-20` from 1.92 to 1.84"*, a driver-age band). (b) puts `exp` of a float coefficient on the rating path, which the money rule forbids unless it is Decimal, and ZEN's `exp` is unverified. (c) is not "priced from the GLM". **Cost of (a):** the demo GLM changes (seven categorical terms), so `fit_demo_models`, `compare_and_approve`'s figures and any test pinning the fitted coefficients change. The executor lists every such test in Task 0 | the maintainer (by delegation): it changes the demo's model, which G2's journey shows | Tasks 1, 2 |
| **DP-a2** | Where does the base premium come from, and where is it held (P4, P5)? | Source: (i) `exp(intercept)` × the mean claim cost from freMTPL2sev (Σ `claim_amount_minor` ÷ Σ `claim_count` over the seed's dataset version), in `Decimal`, rounded to whole minor units; (ii) a stated constant. Holding: (x) an integer literal in one `expression` step (`base_premium_minor = <n>`), versioned and approved with the algorithm, with the derivation written in the step's `note` and the change note; (y) a rate table, which needs a create route that does not exist (P5), so a spec change and a route | **(i) + (x).** (i) is derived from the same data as the fit, and is reproducible from the seed's inputs. (x) needs no new surface. A literal is not a global: FR-246 forbids *"globals, no environment, no time-of-day"*, not constants. (y) is scope growth into `03` §5.1 for a demo | decision-maker | Task 1 |
| **DP-a3** | How is "every step's reads ⊆ its declared consumes" shown, now the sweep script is gone (P6)? | (a) a **committed test** (Acceptance 4) implementing FD-1374's predicate verbatim, with its own broken-input test. (b) wait for PL 9776 Task 1A's save-time check and rely on it. (c) re-create the sweep script locally and record its output | **(a).** A committed test cannot vanish with a job dir, runs on every gate, and is the "running the sweep" `PL-1371` §7 asks for in a form a reader can re-run. (b) ties G2 to F35's timing. (c) repeats the loss | decision-maker | Task 3 |

**Ruled** (the maintainer (by delegation), 2026-10-05 15:28:26 BST, item D2, quoted in
§"The decisions this plan rests on"): **DP-a0 (a)**; **DP-a1 (a)**, on the condition that
the band edges and their source and the refit's fit statistics beside the current model's are
recorded (Acceptance 11); **DP-a2 (i) + (x)**, labelled a simplification (Goal, Acceptance 8,
Task 1); **DP-a3 (a)**. The table above is kept as written, so the options the ruling chose
between stay readable.

## Tasks

### Task 0: Preconditions (no code)

- [ ] **Step 1:** `pwd` is the slice worktree; `git branch --show-current` is the slice
  branch; `uv sync --all-packages`. `alembic current` equals `alembic heads` before any
  pytest (`dev-commands`).
- [ ] **Step 2:** Re-read §"Activation needs" at dispatch: the DP rulings (quote each
  verbatim in the ledger), whether `SL-1409` and PL 9683 have merged, and whether PL 9776's
  S1 `RS-` is filed (its id and the harness's sha256 prefix).
- [ ] **Step 3:** Re-verify each premise P1–P8 at the dispatch tree with the command shown
  in the premise, and record any change. A premise that has moved is a STOP to the lead,
  not a silent adjustment.
- [ ] **Step 4 (DP-a1 (a) only):** list every test that pins the demo GLM's fitted figures
  or factor set:
  `git grep -n -E 'FACTOR_SET|CONTINUOUS_FACTORS|CATEGORICAL_FACTORS|fit_demo_models|compare_and_approve' -- backend/tests examples scripts`.
  Each hit is in this slice's write set or is recorded as unaffected, with the reason.

### Task 1: The builder, red first (Acceptance 3, 4, 5, 7; DP-a0, DP-a1, DP-a2)

**Files:** create `examples/fremtpl2/algorithm.py`, `backend/tests/test_fremtpl2_algorithm.py`.

**Interfaces (produces):**
- `FREMTPL2_ALGORITHM_SLUG: Final = "fremtpl2-rate"`
- `band_expression(column: str, banding: Banding) -> str`: the ZEN ternary chain mapping
  `column`'s raw value to the Banding's label. It honours `closed` (`"left"` → `x < upper`),
  and the label order of `banding.labels`. Out-of-range values follow the Banding's
  `below_range`/`above_range` policies; under `ERROR` the input contract's `min`/`max` refuse
  them first.
- `base_premium_minor(intercept: Decimal, mean_claim_minor: Decimal) -> int`:
  `(intercept.exp() * mean_claim_minor).quantize(Decimal(1), rounding=ROUND_HALF_EVEN)`.
- `build_fremtpl2_algorithm(*, tables: Mapping[str, ArtifactRef], bandings: Mapping[str, Banding], base_minor: int, domains: Mapping[str, Sequence[str]], version: int = 1) -> dict[str, Any]`,
  where `tables` maps each Factor slug to its seeded table ref, and `bandings` maps each
  banded Factor slug to its Banding (empty under DP-a1 (c)).

The algorithm's steps, in order:
1. One `input` step per raw column (seven), `on_missing: "error"`. The input contract
   declares the continuous ones `int` with `min`/`max` from the Banding's boundaries, and the
   categorical ones `string` with `domain` = the seeded levels.
2. One `expression` step per banded factor, `expr = band_expression(...)`, `result_type:
   "string"`, `consumes: [<column>]`, `produces: <factor slug>`.
3. One `expression` step, `base`, `expr = "<base_minor>"`, `result_type: "money_minor"`,
   `consumes: []`, `produces: "base_premium_minor"`, `note` = DP-a2's derivation, opening
   with its ruled label, "a simplification (frequency GLM × mean severity; no severity
   model)".
4. One `table` step per seeded Factor, `rate_table_ref` = its ref, `key_expr: [<factor slug>]`,
   `on_miss: "error"`, `consumes: [<factor slug>]`, `produces: "rel_<factor slug>"`.
5. One `expression` step, `premium`,
   `expr = "base_premium_minor * rel_<f1> * … * rel_<f7>"`, `result_type: "decimal"`,
   `consumes` = every name in `expr`, `produces: "premium_unrounded"`.
6. One `output` step, `output_name: "payable_premium_minor"`, `rounding: {"mode":
   "half_even", "dp": 0}`, `consumes: ["premium_unrounded"]`. `outputs: [{"name":
   "payable_premium_minor", "type": "money_minor", "required": true}]`.

- [ ] **Step 1: Write the failing tests.** In `test_fremtpl2_algorithm.py`:
  `test_the_built_algorithm_validates` (`RatingAlgorithm.model_validate` on the builder's
  output for a two-table, one-banding fixture); `test_band_expression_maps_each_edge`
  (evaluate the generated ternary through `pricing_core.rating`'s expression evaluation for
  the value just below, at and just above every boundary, against `apply_banding` on the same
  values); `test_the_demo_algorithm_declares_no_decimal_output` (Acceptance 5);
  `test_the_demo_algorithm_reads_only_what_it_declares` and
  `test_the_reads_check_refuses_an_undeclared_read` (Acceptance 4, DP-a3 (a)). The reads
  helper implements FD-1374 §"The sweep" verbatim: string literals stripped, then
  `[A-Za-z_]\w*` not preceded by `.`, `$` or a word character and not followed by `(`, minus
  `true false null and or not in`, over `expr`, `condition`, each `clamp_bounds` value, each
  `key_expr` entry, a `lookup`'s `as_at`, and the `feature_map` keys. Cite FD-1374 by id and
  section in the helper's docstring. Under activation need 3 (i), the first test also asserts
  Acceptance 7 (a)'s edge claim: the producer-to-step edges built from each step's read set
  equal those built from its `consumes`. **The ruling's condition (Acceptance 7 (b), (c)):**
  `test_the_reads_extractor_agrees_with_the_engine` and
  `test_the_cross_check_refuses_a_planted_mismatch`. Both call one comparison function,
  `_extractor_vs_engine(text, reference_set, contexts)`, which returns its failures as
  (string, name, kind) records. It iterates
  `pricing_core.rating.authored.authored_expression_fields`, never a hand-kept field list, and
  calls `zen.evaluate_expression` directly. Cite PL 9776 §"Spike S1" step 1 (by its minted id
  if minted at dispatch) and this plan's Acceptance 7 in its docstring, with the engine fact
  that a missing name can evaluate to `null`.
- [ ] **Step 2: Run them and see each fail by its cause** (`ModuleNotFoundError:
  examples.fremtpl2.algorithm` is the cause for all seven on the base tree). Record the line.
- [ ] **Step 3: Implement `algorithm.py`** as specified above.
- [ ] **Step 4: Run the tests green.** `uv run pytest -q backend/tests/test_fremtpl2_algorithm.py`.
- [ ] **Step 5: Commit** `feat(examples): the freMTPL2 rating algorithm builder (exit-demo (a), WK-1178)`.

### Task 2: The seed seeds the tables and pins them (Acceptance 1, 2; DP-a1)

**Files:** modify `examples/fremtpl2/model.py`, `examples/fremtpl2/seed.py`,
`backend/tests/test_demo_rating_evidence.py`.

**Interfaces:** consumes Task 1's builder. Produces
`seed_demo_rate_tables(database, settings, blob_store, workspace_id, actor, model_id) -> dict[str, ArtifactRef]`,
which calls `platform.rate_tables.seed_from_model(..., slug=f"fremtpl2-{factor}", model_ref=..., factor=factor, change_note=...)`
once per Factor in the approved GLM's relativities, in `FACTOR_SET` order.

- [ ] **Step 1 (DP-a1 (a)):** `fit_demo_models` creates three Bandings, one per continuous
  column, through `transform_service.create_banding`. Their boundaries come from
  `transform_service.propose_banding_for_version` on the seed's validated dataset version, quantile with 5 bands
  (the method and band count are recorded in the ledger; the labels are the Banding's own).
  `_create_factor` takes `type` and `banding_id`, so the three are `FactorType.BANDING`.
- [ ] **Step 2: Write the failing tests** `test_the_seed_seeds_one_table_per_rateable_factor`
  and `test_the_demo_rating_version_pins_every_seeded_table` against a seeded test database
  (the existing `test_demo_rating_evidence.py` fixtures, extended to fit on a small row slice).
  Run them, and see them fail for "no rate table seeded" and `pins.rate_tables == []`.
- [ ] **Step 3: Implement** `seed_demo_rate_tables`, call it in `seed.py:run` after
  `compare_and_approve` and before `create_approved_rating_version`, and pass its refs into
  `create_approved_rating_version`. That function builds the algorithm (Task 1), saves it,
  and sets `pins.rate_tables` to the refs and `pins.models` to the approved GLM. If PL 9683
  has merged, this goes through its typed create route; otherwise through the row as today
  (`model.py:396-397`). Remove `_demo_algorithm`, `DEMO_PREMIUM_IN` and `_EMPTY_PINS`.
- [ ] **Step 4: Run green**, then commit
  `feat(examples): the freMTPL2 seed seeds its rate tables and pins them (exit-demo (a))`.

### Task 3: The premium is the GLM's, and the evidence is not circular (Acceptance 3, 6; DP-a2)

- [ ] **Step 1: Write the failing test** `test_the_demo_premium_is_the_glm_premium`. For
  each of three contexts it computes the expected premium from `GlmFitResult.coefficients`
  (intercept and each level's β) and the seed's mean claim cost, in `Decimal`, and compares
  it with `payable_premium_minor` from `score_one` on the compiled bundle. Run it red: the
  base tree scores `premium_in * 2`.
- [ ] **Step 2:** `author_demo_rating_evidence` builds the Regression Suite from those three
  contexts and the independently computed expected values. Remove the `score_one` circular
  expectation (`model.py:413`). Add the three properties of Acceptance 6. The suite slug and
  change note drop "demo fixture" and say "priced from the approved GLM".
- [ ] **Step 3: Run green** (`test_demo_rating_evidence.py` and
  `test_fremtpl2_algorithm.py`), then commit
  `feat(examples): golden quotes priced independently from the GLM (exit-demo (a))`.

### Task 4: Spike S1's claims, the demo run, the gate and the ledger (Acceptance 7–11)

- [ ] **Step 1:** Record activation need 3's ruling verbatim. Under (i): record Acceptance 4's
  output with Acceptance 7 (a)'s one-line derivation (0 undeclared reads, so 0 added edges and
  0 added cycles), and Acceptance 7 (b)'s per-string output with (c)'s red-then-green lines.
  Under (ii): run Spike S1's harness from its `RS-`, verbatim, on the built
  algorithm (steps 1 and 6), checking its sha256 prefix first, and record the output.
- [ ] **Step 2:** Check `pgrep -af 'pytest|vitest|flock'` and both gate slots
  (`flock -n /tmp/slots/gate-1 true`, the same for `gate-2`). Run nothing heavy beside a
  held slot. Then run `uv run python scripts/demo.py --rows 20000` once (Acceptance 8) and
  record the exit code, the elapsed time and the seed's rating line.
- [ ] **Step 3:** The full two-half gate through the gate-runner, which holds a gate slot
  under `RL-1263` (Acceptance 9). Record each rc and the tree.
- [ ] **Step 4:** In the slice's `LG-` ledger: every red with its printed line; the DP
  rulings quoted; the Bandings' boundaries and labels with their source (Acceptance 11 (a));
  the fit-statistics table, base tree beside slice head (Acceptance 11 (b)); the base premium's
  derivation with its inputs and its label; Acceptance 7's record; `git diff --stat
  origin/main...HEAD` against §"Write set" (Acceptance 10).

## Hand-off

1. The lead mints PL 9624 and SL 9626 at the merge turn, and dispatches only after
   §"Activation needs" hold, in a separate activation PR. **Post-mint working-id sweep:**
   every working id this plan cites (PL 9629, PL 9683, PL 9688, PL 9689, PL 9649, PL 9728,
   PL 9776, FD 9717, SL 9625, SL 9626, PL 9624) is re-pointed to its minted id where one
   exists at the mint tree. Ids not yet minted are listed as such in the mint PR body.
2. **Slice (b) consumes** `examples/fremtpl2/algorithm.py:build_fremtpl2_algorithm` and
   `FREMTPL2_ALGORITHM_SLUG` (PL 9629, working id). A change to their signatures after this
   slice merges is a replan trigger for slice (b).
3. When this slice merges, `FD-1209`'s algorithm half is discharged. Its `WF-699` half
   stays with slice (b), and the auditor records the split.
4. The `RL-1343` fix slice removes Acceptance 5's guard test in its own commit when it
   merges, or keeps it if the algorithm still declares no decimal output.
5. **Dispatch delta for `PL-1371` §7's wording** (activation need 3, ruled (i) with its
   condition, 15:42:02 BST: *"PL-1371 §7's wording difference goes as a dispatch delta
   (PL-1371 is frozen)"*). The lead writes it into this slice's dispatch record, not into
   `PL-1371`. Proposed text: *"Delta to `PL-1371` §7, exit demo (a), acceptance. Where §7
   reads 'PL 9776's Spike S1 harness re-run on the new algorithm', this slice instead holds
   Spike S1 steps 1 and 6's claims on its algorithm with committed tests (PL 9624 Acceptance 4
   and 7): FD-1374's predicate as the extractor, 0 undeclared reads, 0 added edges and so 0
   added cycles, and S1 step 1's extractor-vs-engine cross-check computed against
   `zen.evaluate_expression`, red on a planted mismatch. No `RS-` is filed and no harness is
   re-run. Not reproduced: Task 1A's `referenced_names` as the extractor (not on `main`), and
   S1 step 3's equality, which was never this slice's claim. Ruled by the maintainer (by
   delegation), 2026-10-05 15:42:02 BST."* Each working id in it is re-pointed at the mint
   (Hand-off 1).

## Self-review

1. **Coverage of `PL-1371` §7's (a) paragraph, clause by clause.** "the real freMTPL2 rating
   algorithm in the seed": Goal, Tasks 1–3, Acceptance 1–3. "Depends on the FD-1357 fix
   only": activation need 1, met; §3.8's two extra items are needs 2 and 3. "PL 9776's Spike
   S1 harness re-run": Acceptance 7 (a)–(c), Task 1 Step 1, Task 4 Step 1, with the departure
   ruled under activation need 3 (i) on its condition, and Hand-off 5's dispatch delta. "every step's reads ⊆ its declared
   consumes … 0 undeclared reads": Acceptance 4, DP-a3. "declares no decimal output":
   Acceptance 5, activation need 5. "discharges FD-1209's algorithm half": Hand-off 3.
2. **Every design choice the sources leave open is a DP with an owner** (DP-a0 to DP-a3),
   each with options and a recommendation. None is picked silently. The tasks follow the
   recommendations and name each alternative's effect.
3. **Repository literals checked at `809a3794`:** the `model.py` line ranges (`:60-70`,
   `:143-166`, `:194`, `:322-324`, `:327-348`, `:366`, `:396-397`, `:413`, `:490`);
   `seed.py:108-125` and `:609-623` (`:651-665` at `cdaaa573`); `operations.py:139`, `:159`, `:194-198`;
   `runtime.py:221-227`, `:235-245`, `:264`, `:298-301`, `:568-579`; `test_api_rate_tables.py:1232`;
   `api/models.py:395-411`; `api/rate_tables.py`'s six route decorators;
   `platform/rate_tables.py:419-430`; `modelling.py:1040-1045` and `:1616-1617`;
   `test_demo_rating_evidence.py:37-39`, `:51`, `:68-73`. The draft exit-demo script's cites
   were re-checked at this tree by a read-only sweep. One was wrong at both trees:
   `model_schema/approvals.py:282` opens `DEFAULT_POLICY`, and the Rating Version quorum is
   at `:335-338` (`:292` and `:345-348` at `cdaaa573`). This plan does not use it.
4. **What was not executed.** No test was run (docs-only preparation wave). The one thing
   executed is the `zen-engine` 0.53.0 probe behind Acceptance 7 (b)'s reading of "must fail"
   (§"Activation need 3: the proposal"), a one-off `evaluate_expression` call, no test suite. The
   ternary-banding approach rests on the ternary being verified live (`runtime.py:298-301`)
   and is proven in Task 1 Step 1 (`test_band_expression_maps_each_edge`) before anything
   depends on it. If ZEN returns a non-string for a string-valued ternary, that test fails
   by its cause and the executor reports a replan trigger.
5. **Type consistency.** `build_fremtpl2_algorithm`'s keyword arguments are produced by
   `seed_demo_rate_tables` (tables), Task 2 Step 1 (bandings), `base_premium_minor` (base)
   and the seeded levels (domains), and are consumed with those names in Task 2 Step 3 and in
   slice (b).

## Pre-mint note, 2026-10-05

*Dated 2026-10-05 (`TZ=Europe/London date`: 2026-10-05 15:32:20 BST), before the mint of PL
9624 (working id).* Edited in place on the unmerged draft #1161, on the lead's order (prep
wave, section S), to record the maintainer's (by delegation) ruling of 2026-10-05 15:28:26 BST,
item D2, and nothing else. What changed: the ruling quoted verbatim (§"The decisions this plan
rests on"); §"Status" and activation needs 2 and 3; §"Activation need 3: the proposal"
(new: options (i) and (ii), recommendation (i), for the ruling at the ACK); Acceptance 7
(rewritten for (i), with (ii) kept); Acceptance 8 and Task 1's base step (DP-a2's label);
Acceptance 11 (new: DP-a1's condition); the Goal (the label); a **Ruled** line after the
decision-point table; Task 4 Steps 1 and 4; Self-review item 1. No scope, task cut, write set
or other decision point changed. Verified at `origin/main` `809a3794`; then, after merging
`origin/main` `cdaaa573` (#1157, `SL-1409`), re-verified there at 15:38:18 BST: activation
need 4's `SL-1409` half is met, and the `seed.py` and `approvals.py` line cites that moved are
re-anchored beside their `809a3794` values.

## Pre-mint note 2, 2026-10-05

*Dated 2026-10-05 (`TZ=Europe/London date`: 2026-10-05 15:46:19 BST), before the mint of PL 9624 (working
id).* Edited in place on the unmerged draft #1161, on the lead's order (prep wave, section
AB), to record the maintainer's (by delegation) ruling on activation need 3, entry 2026-10-05
15:42:02 BST, and nothing else. What changed: the ruling quoted verbatim (§"The decisions
this plan rests on"); §"Status" and activation need 3 (ruled (i) on its condition); §"Activation
need 3: the proposal" (the ruling, and why the cross-check fits a committed test, with the
`zen-engine` probe that changes "must fail" to "raises or returns a different value");
Acceptance 7 (rewritten: (a) edges, (b) the extractor-vs-engine cross-check, (c) red on a
planted mismatch; (ii) kept as the fallback, with a STOP if (b) cannot be built); Task 1's
heading and Step 1 (two tests and one comparison function) and Step 2 (seven tests, not
five); Task 4 Step 1; Hand-off 5 (new: the dispatch delta for `PL-1371` §7's wording); Self-review
items 1 and 4; the `test_fremtpl2_algorithm.py` row of §"Write set" (names the two added tests; same file). No scope, write set, owner, other decision point or other acceptance item
changed; the new tests live in `backend/tests/test_fremtpl2_algorithm.py`, already in the write
set. Cites re-verified at `origin/main` `cdaaa573`: `authored.py` `EXPRESSION_FIELDS`,
`NON_EXPRESSION_FIELDS` and `authored_expression_fields` (by symbol); `zen-engine==0.53.0` in
`packages/pricing-core/pyproject.toml`; `compile.py`'s `import zen`; PL 9776 §"Spike S1" step 1
at #1051 @`ecbb82ab`.

## Pre-mint note 3, 2026-10-05

*Dated 2026-10-05 (`TZ=Europe/London date`: 2026-10-05 16:50:24 BST), before the mint of PL
9624 (working id).* Edited in place on the unmerged draft #1161, on the lead's order (prep
wave, section AM), to record the maintainer's Option A decision, entry 2026-10-05 16:43:31
BST, item 1, and nothing else. What changed: in §"The decisions this plan rests on", the item
quoted verbatim and one paragraph saying that A-4 is its own slice (SL 9594 / PL 9593,
working ids), so this plan's scope does not change; the 15:42:02 BST entry's header now names
`RL-1418` in place of the `RL-[…]` elision, because `RL-1418` merged as `137bc817` (#1128),
which the maintainer (by delegation) cleared at 16:43:57 BST ("The RL-[…] elision restored at
the mint: fine"). No scope, task, acceptance item, write set, owner or decision point changed.
`origin/main` `137bc817` merged in. Between `cdaaa573` and `137bc817`, main changed only
`docs/INDEX.md`, `RL-1361` (its `corrected_by` field) and the new `RL-1418`, so no line cite
in this plan moved.
