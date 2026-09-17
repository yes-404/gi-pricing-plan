---
id: LG-730
family: ledger
title: WK-661 — `WF-698` driven end to end
status: closed                 # active → closed (§1.2a) — set `closed` only at slice close
created: 2026-08-17
owner: executor
phase: P1b
work: WK-661
plans: [PL-NNNNN]              # every plan this ledger has executed; append, never remove
corrected_by: []
relates: []
was: docs/audit/closure-records.md
---

### WK-661 — `WF-698` driven end to end, 2026-08-17 *(in progress, not closed)*

The tenth slice: FR-19(ii) for `WF-698`, the requirement the citation-audit slice left
outstanding and the GBM slice made writable. One test, `backend/tests/test_wf01_journey.py`,
walking the journey's own phases in order through the same Jobs and services a caller reaches
— not a marker on an existing test, which FR-19 refuses by name.

| Delivered | Evidence |
|---|---|
| A→E2 and E6→E10 in one test | Ingest, **the failure loop** (a version that fails validation, is corrected, and passes), profiling, a materialised train/test split, a banding, a grouping, a GLM fit, an XGBoost fit on the same factors and split, diagnostics on both, the transparency artifact, the comparison, submission, the self-approval refusal, and approval — each block naming the step it executes |
| The split is **materialised**, not asserted | `dataset.derive` produces both parts as real versions. A faked split gives every fit a holdout identical to its training set, and every diagnostic downstream reports the model's own memory |
| E9 walks the refusal, not the happy path | `SUBMITTER_CANNOT_APPROVE` (`06` R1) is asserted inside the journey, because a journey test that only walked the happy path would not reach the one step that has to fail |
| E1 compares **both** candidates | The artifact is read back through `load_comparison` and its `holdout_deviance` asserted to carry a number for each model ref — the job succeeding proves nothing, since a comparison that silently dropped the GBM would also succeed |
| The three steps the platform cannot drive are **pinned, not skipped** | D7 (an `interaction` Factor) and E4/E5 (the Peril Structure, FR-188, FR-189, FR-190, FR-191) are inverted assertions: each passes while the capability is absent and **fails the day it lands**, so the slice that builds either must come back and extend the journey. A comment would have said the same and gone stale |

**Model comparison gained its GBM arm here, because the journey asked for it.** `WF-698` E1
compares "the GLM and GBM candidates" and FR-186 is type-agnostic, so a comparison that
could only read a `GlmSpec` was code failing the spec rather than a capability nobody had
specified — the comparison slice's own verdict said as much, deferring it to "the GBM slice".
Three sites: `ComparisonCandidate` takes a `GlmFitResult | GbmFitResult` and requires the
booster bytes alongside a GBM fit (ADR-703 — this package is handed artifacts, never ids),
`_score` dispatches to `predict_gbm`, and the backend's `_resolve_candidate` validates through
the union adapters and fetches the booster. `relativity_differences` is computed for the GLM
candidates alone and returns empty below two, because a relativity is a ratio between level
effects and a booster has none — `02` §3.6's transparency artifact is where a GBM's factor
story lives.

**The defect the journey found is in the encoding, and it is the kind only an end-to-end run
produces.** D5's banding and D8's monotone constraint met for the first time here. A banded
Factor was being handed to both backends as an **unordered categorical**, with its levels coded
in *lexicographic* order — so `"10-49"` sorted between `"0-1"` and `"2-4"`, and a declared
`decreasing` constraint would have held over the alphabet rather than over age. On LightGBM it
was worse than wrong: a monotone constraint on a categorical feature **aborts the process**
(`[LightGBM] [Fatal] The output cannot be monotone with respect to categorical features`, 4.7.0)
rather than raising, so the failure arrives as a dead worker with no error to map. Resolved in
`02` §4.4 (amended, dated) rather than diverged from: a banding is **ordinal** — coded in the
artifact's own label order and declared to the backend as ordered integers — while identity
categoricals and groupings stay unordered, since the platform has no order to assert for them.
FR-122 refuses a direction on those two and only those two. The dtype vocabulary is now
named: `f64`, `ord`, `cat`. Proven behaviourally on both backends: band-midpoint predictions
never rise under a `decreasing` constraint, and the encoding map's order is asserted to equal
the banding's labels.

**Two stale tests, corrected against the spec rather than against the code.** Both pinned
`OverallOutcome.FAIL` for an unacknowledged warning; `01` §4.6 was amended on 2026-08-14 so
that `overall` derives from rule results alone and acknowledgement is checked at promotion
(FR-46). The code was right, the tests were the survivors — and the property they
asserted deadlocked promotion, since a report that can never leave `fail` can never be
acknowledged into `validated`. The test now names what it asserts:
`test_an_unacknowledged_warning_is_pass_with_warnings_and_still_blocks_promotion`.

**Numbers.** Suite: **961 Python tests**, 105 frontend. `req-coverage` reads 182 of 443
marked (41.1 %). `scope-audit MODEL --sections 3.5,3.6` is unchanged at **17 of 19** — a
journey test evidences the seams between requirements rather than adding to their count, which
is the point of having both measures.

**Not delivered, with verdicts:**

| Item | Verdict |
|---|---|
| **D7** — an `annual_mileage x driver_age` interaction factor | **Not started.** `resolve_factors` implements `identity`, `banding` and `grouping` and refuses `interaction` by name. Owner: the interaction-factor slice, which must extend this journey test |
| **E4/E5** — the Peril Structure and its reconciliation (FR-188, FR-189, FR-190, FR-191) | **Not started** — no contract, no table, no code. Owner: the peril-structure slice, which also owns FR-128 |
| FR-19(ii) for `WF-699…05` | **Outstanding**, each owned by the phase whose exit criterion names it (`§12`) — unchanged by this slice |
| `WF-698` as a **Phase 1b exit** claim | **Not yet.** The exit is the journey end to end *on freMTPL2* through the UI; this test drives the platform on a synthetic frame, which is what makes it a test rather than the demo. WK-665's modelling half is the other half |

#### WK-661 slice — peril structures and the risk-premium reconciliation, 2026-08-18

`02` §3.9 built end to end: FR-MODEL-58, 59, 60, 61 and **FR-128**, which the GBM slice
reassigned here. `scope-audit MODEL --sections 3.9` moves from **0 of 4** to **5 of 5** — the fifth is
FR-192, appended by this slice — and §3.5 completes at **12 of 12**, FR-128 having
been the one requirement the GBM arm reassigned rather than evidenced. Declared endpoints go
from **20 of 30** to **24 of 32**: two of the four new routes were declared and unbuilt, and
two the spec did not declare at all.

**The inverted assertion did what it was built to do.** `WF-698`'s
`test_wf01_names_the_steps_it_cannot_yet_drive` went red the moment `PerilStructure` landed,
which was this slice's cue to drive E4/E5 for real rather than to delete the assertion. The
journey now composes a structure over the selected model, reconciles it through the real
worker, and submits and approves it beside the model. FR-19(ii) for `WF-698` stays
**partial** with **one** step named instead of three.

**Five spec defects found by building, all resolved in the spec rather than absorbed:**

1. **`02` §5.2's two signatures were unwritable** — the *fifth* instance of the
   Model-parameter defect, and the two `TODO.local.md` predicted by name. A `PerilStructure`
   carries model refs, and resolving one needs the database ADR-703 forbids `pricing-core`.
2. **§5.1 declared a create and a reconcile and no read** — a `POST` whose artifact nothing
   can fetch, plus an approvable artifact with no way to submit it. FR-192 appended.
   Invisible to the endpoint audit for the third time now, for the structural reason it will
   stay invisible: the audit compares the spec against the contract, and an endpoint in
   neither is in neither.
3. **FR-191 was unreachable.** `approvals.submit` is fully generic and `peril_structure`
   has been a valid artifact type since Phase 0 — but `06` §4.2's `DEFAULT_POLICY` had no
   entry, so submission was refused with "no approval policy for this artifact type". A
   correct refusal, which is exactly what made it invisible.
4. **§4.10's example was not a contract**, and building one settled six things it left open
   — derived `ratio`/`status`, the per-peril breakdown FR-128 needs, required
   calibration evidence, `BlobRef` as an object rather than a string, exact-decimal money,
   and a lifecycle whose `draft → review` edge does not exist.
5. **FR-190 does not say where observed burning cost comes from**, and it cannot be
   derived. The caller declares the column, with no default.

**Three things the tests found rather than confirmed:**

- **`job_kind` is a Postgres ENUM.** This is the first slice ever to add a `JobKind`, so the
  Job insert was refused by the database from inside `job_service.submit` — after the route
  had validated everything it could see. The migration carries the `ALTER TYPE`; a downgrade
  cannot remove the value and says so.
- **A `computed_field` breaks its own artifact's round trip.** `ratio` and `status`
  serialise, and `extra="forbid"` then rejects the payload coming back — which
  `load_structure` hit on its first run. They are dropped and recomputed on input, so a
  stored or hand-edited ratio has no way to be believed.
- **A punitive tolerance does not produce a failing reconciliation** on this book: the fit
  reconciles to the penny. The failing test doubles a restoration loading instead, which
  drives FR-128 through the platform path and is a better test than the one intended.

**Enforcement proven against deliberately broken input** (§13.4), not assumed: with the
restoration loading removed, the same capped peril fails the reconciliation it passes with
it; with the total rounded independently instead of summed from the rounded parts, the
penny-drift test reports 99 against 100.

**Not delivered, with verdicts:**

| Item | Verdict |
|---|---|
| **`separate_model`** large-loss treatment (FR-189) | **Deferred**, refused by name with `LOSS_TREATMENT_UNIMPLEMENTED` in `pricing-core` *and* before the Job is queued. It needs an excess-layer model, which nothing fits. Contract-level from the start, because FR-189 names all four kinds. Owner: the slice that fits an excess-layer model  **Owner named 2026-08-22 (audit-remediation slice): Phase 1b, and if no Phase 1b slice claims it, it is a Phase 2 spec change rather than an implicit debt.** "The slice that fits an excess-layer model" is an event nothing schedules, which §13 rule 1 counts as silence rather than as one of its four verdicts. The refusal by name (`LOSS_TREATMENT_UNIMPLEMENTED`) is correct and stays; what changes is that the requirement is now **not started with a phase** instead of not started with a sentence. |
| **`/peril-structures/{id}`** view (`02` §5.3) | **Not started.** Owner: WK-664, unchanged |
| **`03-rating-engine`'s consumption** of an approved structure (FR-191's second half) | **Not started, and correctly so** — Phase 2. A later phase is a spec change, not code (`CLAUDE.md` §0) |
| `WF-698` **D7**, the interaction factor | **Not started**, unchanged. Still pinned as the one inverted assertion |
| `WF-698` E4 as **frequency × severity** | **Driven as burning cost**, a fixture limit rather than a platform one — severity responds to cost *per claim* and every claim-free row in the fixture book carries a zero a Gamma refuses. The arithmetic is covered directly in `packages/pricing-core/tests/test_perils.py`. Recorded in the journey test and in FR-19 |

#### WK-661 slice — interaction factors, and `WF-698` complete, 2026-08-18

FR-83 has listed `interaction` as a Factor type since Phase 0 and the contract had no
field to express one, so the type was selectable and unresolvable. `operand_factor_ids` is
that field and FR-92 is the rule. §3.1 moves **6/8 → 7/9**; FR-208's list of
unimplemented arms drops from **five to four**.

**`WF-698` is now driven end to end, and the pinned test is deleted.** It held three inverted
assertions — D7, E4, E5 — each passing while its capability was absent and failing the day it
landed. Every one fired as designed and was driven by the slice that broke it. **FR-19(ii)
for `WF-698` is delivered**, the first of the five journeys to get there.

**The design decision, and why it was not silently taken.** An interaction crosses **Factors,
not columns**: every other place the spec names one names factors, and an operand is usually
itself a banding or a grouping — crossing raw `driver_age` with raw `region` gives one cell
per policy, crossing `driver_age_banded` with `vehicle_group_rated` gives a table. What an
interaction may cross is the genuinely open half, and it is **OQ-584** rather than a
choice buried in a commit: a continuous operand is refused by name with its remedy, because
refusing is additive to undo and a product term shipped today is a model someone has fitted
by the time `03` finds no rate-table cell for it.

**Three consequences the build forced, each a defect if left implicit:**

1. **Only observed combinations become levels.** A full Cartesian product puts a coefficient
   on cells with no exposure, and on any real cross most cells have none.
2. **An operand contributes no design column of its own.** A full cross spans every cell, so
   its operands' main effects are collinear with it. This was not a preference: with the rule
   removed the fit test fails with `the design matrix is singular`, which is the broken-input
   run saying it.
3. **Type III now compares an interaction against the *main-effects* model.** It falls out of
   (2) — drop the cross and its operands become terms again — and it is the better question:
   "does this interaction earn its place over the main effects" is what an actuary means.

**Found by the tests rather than confirmed by them:** `diagnostics._term_count` resolved each
factor **alone** to count its degrees of freedom, which an interaction cannot survive, and
`_type_iii` would have dropped an operand out of the list and left the cross unresolvable.
Both are seams no unit test reaches — the fit and the diagnostics run in one handler — and
the end-to-end backend test is what surfaced them.

**Not delivered, with verdicts:**

| Item | Verdict |
|---|---|
| A **continuous** operand (a varying slope) | **Refused by name**, OQ-584, with the recommendation and its reasoning on file. Owner: the maintainer, revisited when `03`'s rate-table shape is built rather than specified |
| `spline`, `polynomial`, `offset`, `expression` | **Not started**, unchanged. FR-208 now names four rather than five; each needs its own contract field and its own argument |
| The factor workbench's interaction UI (`02` §5.3, FR-135's suggestions with exposure share and holdout lift) | **Not started.** Owner: WK-664, unchanged |
| `WF-698` as a **Phase 1b exit** claim | **Still not yet**, and unchanged by this slice: the exit is the journey on freMTPL2 through the UI. What is delivered is FR-19(ii)'s *test* |

#### WK-661 slice — backtests, and a `Diagnostics` field nothing could ever fill, 2026-08-18

FR-187 has named the backtest since Phase 0 and **no section defined what it produces**.
`02` §4.12 is that definition, `FR-94` is the read endpoint the table omitted, and
`MODEL` moves **24/32 → 26/33** endpoints — the denominator rises because the read route the table omitted is now declared in it.

**`Diagnostics.backtest` is removed rather than populated.** It was declared from Phase 0 and
typed `null`, and nothing could ever have filled it: FR-170 computes diagnostics once at
fit time, while a backtest runs later — and again for every period after that, which one field
on one immutable artifact has no room for. It is the same defect FR-171's `double_lift`
had, found the same way and resolved the same way. `cross_validation` stays, because
FR-182 computes it at fit time and `Diagnostics` is where it will land.

| Delivered | Evidence |
|---|---|
| `pricing_core.modelling.backtest_model` | Reuses `_partition`, so "the same diagnostic shapes" is the same arithmetic and not two implementations that agree today. Proved by the degenerate case: backtest against the training frame and every figure equals the fit's train partition |
| Both model types, one path | `score_fitted`'s dispatch; parametrised over XGBoost **and** LightGBM, for FR-129's reason — the scoring-side offset is per backend, and dropping it would report the offset as deterioration |
| `POST /models/{id}/backtest` → 202 Job, `GET /models/backtests/{id}` | FR-187 and **FR-94**. Four refusals, all before the queue hop |
| `backtests` table, migration `c9d0e1f2a3b4` | Unique on `(model_id, dataset_version_id)` — a model has many backtests, one per period, and re-running one pair would be a second answer to one question |
| The **first test in this repository to exercise an artifact trigger** | `backend/tests/test_backtests.py` runs an `UPDATE` as the owner and asserts it is refused. Every other artifact table's test checks the grants only |
| `SCOREABLE_MODEL_STATUSES` consolidated into `model-schema` | Two private copies already existed (comparison, peril structures) and this slice needed a third. `CLAUDE.md` §2's rule, applied at the point it became visible |

**Two things the tests found rather than confirmed.**

**The refusal order is load-bearing.** A split's `train` and `test` parts are derived Dataset
Versions that stay `draft`, so `01` §1.3's validated gate answered a request to backtest the
model's own holdout with *"that version is not validated"* — true, unhelpful, and an
instruction to go and validate the holdout, after which the request would have been allowed.
The definitional refusal now runs first. `datasets.load_version` was made public for it, which
is the gate-free half `fittable_or_refuse` was already built from.

**A GBM test asserting calibration must first assert it converged.** At 30 boosting rounds the
booster's own train A/E was 0.53, and the backtest on a book with 30 % more claims read 0.65 —
a number that is entirely shrinkage. A test that checked only the later figure would have
calibrated its bound against an unconverged fit. It now runs 300 rounds and asserts train
A/E ≈ 1.000 before reading the backtest.

**`01` FR-44 appended, from a gap this slice measured.** FR-43's trigger exists
because revoking `UPDATE` from the *owner* does nothing. `diagnostics`, `model_comparisons`
and `transparency_artifacts` were each created with the grants and **no trigger at all** —
verified on a migrated database: two triggers each on the FR-43 tables and on
`backtests`, zero on those three. Each is evidence something is approved against. Recorded
with an owner rather than fixed here, because it is a different requirement's scope.

**Not delivered, with verdicts:**

| Item | Verdict |
|---|---|
| A **list** of a model's backtests (`GET /models/{id}/backtests`) | **Not built, deliberately.** It is what `05-monitoring.md` reads and nothing consumes it yet; `CLAUDE.md` §0 puts a later phase's capability in the spec rather than the code. Named in FR-94. Owner: the monitoring workstream |
| `POST /models/{id}/predict` (FR-MODEL-63, 77, 78) | **Not started.** The other of the two shortest remaining endpoints; 63 still needs the covariance blob `predict_glm`'s signature deliberately does not take |
| `01` FR-44's three tables | **Not started, and not this slice's.** Owner: WK-661's next slice or WK-673, whichever reaches it first. The migration is three tables through the loop `a1b2c3d4e5f6` already writes, plus a negative test each. **Taken up 2026-08-18** by the FR-44 slice below, which found six tables rather than three |
| A backtest view (`02` §5.3) | **WK-664**, a Vue view. No frontend work in this slice.  **Corrected 2026-08-23:** this cell cited a `02` §5.3 row that did not exist — the record owed a view the spec did not register. The row was added on 2026-08-23, addressed by backtest id (FR-94), together with the prediction view its slice is paired with. The citation is now true; the obligation is unchanged |
| A backtest cited as approval evidence (`06` §3.3) | **Not started.** `06` §3.3's evidence table has no `backtest` kind, and adding one is a governance decision rather than a modelling one — the shape OQ-639 is already about |


#### WK-661 slice — custom objectives, and the tolerance that stopped checking, 2026-08-18

`02` §3.7 was the largest unbuilt block in the spec — **1 of 16 requirements evidenced**, and
five of `MODEL`'s six unpublished endpoints. It is now **16/17**, and `MODEL` moves
**27/33 → 34/35** endpoints (97%); the denominator rises because FR-166 declares the two
read routes the §5.1 table omitted, and the one still unpublished is `POST /custom-metrics`.

**Templates only, per the 2026-08-15 decision — and that is what made the certification
machinery cheap rather than what made it unnecessary.** The twelve templates are the
platform's own analytic derivatives, so §4.7's checks are not verifying a user's arithmetic;
they are verifying a *parameterisation*, at the values this objective was actually given —
and two of the three findings below come from running them.

| Delivered | Evidence |
|---|---|
| `pricing_core.modelling.objectives` — the twelve-template catalogue, `compile_objective`, `certify_objective` | 23 tests, parametrised over the catalogue, so a thirteenth template inherits every one of them |
| The nine §4.7 checks, **all emitted for every objective, always** | Richardson-extrapolated central differences at `h = 1e-4`, with the agreement tolerance floored *and* offset by each point's own finite-difference noise. `certified_with_findings` is the ordinary outcome for a pricing loss; only `failed` blocks |
| `ObjectiveCertificate` wrapping `CertificateResult` | ADR-703, made concrete: `pricing-core` cannot allocate an id, read a clock or know about a Job, so identity sits outside and findings inside. `CertificateResult.outcome_of` is the single place the verdict rule lives, enforced by a `model_validator` |
| `custom_objectives`, `objective_certificates`, migration `d0e1f2a3b4c5` | The definition is immutable while the lifecycle columns move — a certificate certifies the parameters it ran against, so an `UPDATE ... SET params` on a `certified` row is refused by trigger and proved so by test. Certificates are append-only |
| Seven endpoints (FR-146/163/164/**95**, and `derive` refusing) | `POST /derive` exists **in order to refuse**, with `OBJECTIVE_KIND_NOT_ENABLED`: a declared endpoint that 404s says "wrong URL" where the truth is "not in this phase" |
| `fit_gbm`'s custom branch, both backends | Seven refusals by name, every one before the fit: not supplied, ref mismatch, not approved, response undeclared, not applicable, offset required, early stopping unsupported |
| FR-355 extended: a Custom Objective returns to **`certified`**, not `draft` | The certificate is pinned to the objective version (FR-146) and the version did not change when an approver asked a question. Returning it to `draft` would discard evidence that is still valid |

**Three things the tests found rather than confirmed.**

**A defect in `predict_gbm`, in code this slice only had to read.** The LightGBM branch applied
`np.exp` to the raw score unconditionally, though `_OBJECTIVES` had carried the inverse link
as its third element all along. Correct for three of the four builtin objectives and wrong for
`binary:logistic`, which returned `exp(f)` where the model means `1 / (1 + exp(-f))` — a
"probability" above 1 for every row the model thought likely, and the two agree to within 1 %
at `f = 0`, so a weak-signal book would not have shown it. Nothing had yet asked a LightGBM
binomial model for a prediction. The custom path needed the link recorded anyway
(FR-130), and the defect was visible the moment it was. Fixed, with a regression test
parametrised over both backends and over builtin/custom; artifacts predating the field keep
the old behaviour deliberately, because silently changing what a stored model predicts is the
worse failure. `02` §4.3 carries the note.

**Certification caught the platform's own arithmetic.** `minimum_at_truth` failed for
`asymmetric_poisson`: the implemented loss was not minimised at `f = log(y)`, and the spec was
right about what the objective meant. The code was fixed and the spec left alone — the one
direction of `CLAUDE.md` §0's rule that is easy to get backwards when the code is newer than
the words.

**The tolerance stopped checking, and nothing would have said so.** Raising the sampling floor
from 600 to 1 000 points made three of twelve templates warn on derivatives that were exactly
correct — the extra points reach where the true derivative is near zero and the difference
quotient is all noise. The fix was to subtract each point's own noise floor from the tolerance,
which is right, and which also loosens the check that exists to catch a wrong derivative. So
the loosening is now pinned from the other side: a 1 % relative error in either derivative
reaches `failed`, and an absolute error of `1e-08` in the Gamma hessian — two hundred times the
noise where that hessian is smallest — still reaches `failed`. The general rule went into
`.claude/skills/python-test`, because this will not be the last tolerance that gets loosened.

**Not delivered, with verdicts:**

| Item | Verdict |
|---|---|
| **FR-144/145's `expression` kind** — the grammar, the SymPy derivation, `POST /derive` | **Phase 2**, behind `expression_objectives_enabled`, and refused by name rather than absent. FR-145 is evidenced only for the half that binds a template — the definition cannot be rewritten — not for the parser. Owner: the maintainer, with OQ-632 |
| **FR-154 custom metrics**, and `POST /custom-metrics` — `MODEL`'s last unpublished endpoint | **Deferred to Phase 1b.** Evidenced only as the shape of its absence: under a callable objective both backends hand a builtin metric the raw score, so the metric early stopping names is not the metric it stops on. Refused with `OBJECTIVE_EARLY_STOPPING_UNSUPPORTED` and FR-154 named in the message, because a wrongly-stopped fit produces a model that is merely worse and never one that errors |
| The sandbox question (`CLAUDE.md` §3's "arbitrary-code objective is a governance risk") | **Not answered, and deliberately not.** Templates execute no user text at all, so Phase 1 buys the capability without owing the answer. It comes due with the `expression` kind, not before |
| `02` §5.3's two views — `/objectives`, `/objectives/{id}/certificate` | **Not started.** Owner: WK-664. The §5.3 note records two things the views will need that the spec has wrong: "pass/warn/fail" is four statuses, and the expression editor has nothing to parse in Phase 1 |
| `06` §4.1's `custom_objective:author` / `custom_objective:submit` | **Superseded 2026-08-18.** The permissions do not exist and the spec was the wrong side; the built surface checks `model:read` / `model:fit` / `model:submit`, and separation of duty is bought by FR-353 and FR-163 instead. Whether authoring an objective deserves its own permission is **OQ-632**, to be decided *with* the `expression` kind |
| `WF-702` Route B, and Phase C's compiled expression tree | **Phase 2**, unchanged. Route A is now real end to end except A3, and the journey carries a dated note saying which of its steps read differently |


#### WK-661 slice — FR-44, and a comment that had been wrong for three days, 2026-08-18

The backtest slice (#99) found three artifact tables carrying FR-43's grants and no
trigger, and raised FR-44 with an owner. This slice is that owner. It found **six**.

The difference is how the second measurement was taken. The first read the three tables it
already suspected; the second asked the database which tables the *schema* declares
append-only — grants of exactly `SELECT, INSERT` and nothing else — and then asked which of
those carry both triggers:

| Table | Layer 1 | Layer 2, before | After |
|---|---|---|---|
| `diagnostics`, `model_comparisons`, `transparency_artifacts` | grants | **nothing** | both |
| `objective_certificates` | grants | `TRUNCATE` only | both |
| `bandings`, `groupings` | grants | `TRUNCATE` only | both |

`objective_certificates` is mine, from the slice merged two hours earlier. `bandings` and
`groupings` are the ones worth recording: `c3d4e5f6a7b8` states the protection in a comment
— *"Insert-only at the privilege layer, so the rule survives a direct `UPDATE` from a psql
session"* — and then creates the `TRUNCATE` trigger alone. The sentence had been in the tree,
false, since #72 on 2026-08-15, and `test_transformations.py`'s test of it passes
because it does `SET LOCAL ROLE gip_app` first, which is the one connection the claim was not
about.

| Delivered | Evidence |
|---|---|
| `e1f2a3b4c5d6` attaches `artifact_append_only()` to all six | six `_no_modify` triggers, three `_no_truncate` |
| A negative test per table, run as the **owner** | `test_an_artifact_cannot_be_rewritten_from_the_owner_connection`, parametrised over the six: `UPDATE`, `DELETE` and `TRUNCATE` each refused, and the row still there |
| The invariant, checked as an invariant | `test_every_table_the_grants_call_append_only_carries_both_triggers` derives its table list from the grants, so a seventh table built with layer 1 alone fails on the day it is added |
| The derived test's own blind spot, closed | `test_the_application_role_holds_only_select_and_insert` now pins all eleven tables explicitly: a table regranted `UPDATE` would otherwise drop out of the derived set and be checked by nobody |
| `01` FR-44 and `02` §4.12 amended | The requirement is now stated as the invariant rather than as a list of three, with the corrected count and the date |

**Enforcement proven against broken input**, both layers: dropping `groupings_no_modify`
fails two tests (`DID NOT RAISE DBAPIError`, and `missing a trigger: [('groupings', 0, 1)]`);
granting `UPDATE` back on `diagnostics` fails two others, including the set-equality guard
that keeps the derived test from passing vacuously.

**Not delivered, with verdicts:**

| Item | Verdict |
|---|---|
| The false comment in `c3d4e5f6a7b8` | **Left as written.** A merged migration is a dated record; `e1f2a3b4c5d6`'s docstring and this entry record that the claim was untrue and when it stopped being so. Editing the old file would remove the only evidence of how long it stood |
| `test_transformations.py`'s `SET LOCAL ROLE gip_app` test | **Left as written, and now honest.** It tests layer 1, which is what it does; the owner path it overstates is covered by the new test rather than by rewriting it |
| An artifact table checked at the ORM layer as well | **Not started, and probably never.** `DiagnosticsRow` and its siblings carry the claim in a docstring only. The database is the layer that cannot be bypassed, which is the whole argument of FR-43 |

#### WK-661 slice — five decisions, and §3.3 as an evidence floor, 2026-08-18

Five open questions decided in one pass, and the plan's own gate table repaired while doing
it. Four of the five appended a requirement and stopped there, which is the correct
deliverable for a later phase (`CLAUDE.md` §0); the fifth was buildable today and was built.

| Question | Decision | Requirement | Built? |
|---|---|---|---|
| **OQ-577** | The GLM approximation of a GBM is a **Model** in its own right | `02` FR-137 | No — **Phase 1b**, before anything references a transparency artifact by identifier. After that it is a migration rather than a decision |
| **OQ-576** | An `approximation`-mode Rating Version must show a dislocation run against itself in `exact` mode, inside a workspace-declared threshold | `03` FR-224 | No — **Phase 2**, with the deployment path it gates |
| **OQ-584** | An `interaction` operand must resolve to levels; no product term at any intent | `02` FR-93 | Already built — the requirement ratifies the interaction slice's refusal and names the `diagnostic`-intent variant as the likely eventual answer |
| **OQ-585** | One interval kind until a **named consumer** asks for a second | `02` FR-196 | Already built — the requirement supplies the trigger the row could not, so "revisit when there is a consumer" stops depending on memory |
| **OQ-639** | `06` §3.3 is a **floor**; §4.2 may add and never remove | `06` FR-364 | **Yes** — its precondition had fired twice over |

**The floor, in three mechanisms.** The objection to a floor was never that it is wrong, it
is that a submission refused for evidence the policy does not mention is an error nobody can
act on. So the floor is restated in §4.2's own text; `PUT /approval-policy` refuses a policy
that drops below it with `POLICY_BELOW_EVIDENCE_FLOOR` naming the artifact type and the
kinds; and submission checks the **union** of floor and policy, so a policy stored before the
floor existed cannot sit below it either. `EVIDENCE_FLOOR` lives in `model-schema` beside
`DEFAULT_POLICY` — one shape, one place (`CLAUDE.md` §2).

**The enforced floor is §3.3's *checkable projection*, and the rest is named with an owner.**
Submission fails closed on a kind it cannot verify (`06` R4), so a floor naming
`model_comparison_if_predecessor` — which lives inside a comparison's `payload` and cannot be
queried — would have refused every model submission rather than raising the standard.
FR-364 says which kinds are enforced, which are not, and who owns each remainder.

**Two divergences found while building it, resolved rather than aligned.** `06` §4.2's `model`
entry lists three evidence kinds and `DEFAULT_POLICY` shipped one; §4.2's `rating_version`
entry lists six against three. The code was right for the day it was written and the page was
right about the destination, and §4.2 now carries a dated note saying so. The sharper one:
the submission check answered a kind it spelled `transparency_artifact` while the spec spells
it `transparency_artifact_if_non_glm` — so a workspace that copied the kind off the page got
a **fail-closed refusal for evidence it had**. Both spellings are accepted now and the spec's
is canonical.

**The gate table was missing four questions and double-counting a fifth.** `OQ-584`,
`OQ-585`, `OQ-586` and `OQ-632` had been raised, mirrored and invisible to the
plan; `OQ-639` was counted at both 1b and Phase 3 because the Phase 3 row carried a
parenthetical naming it. That parenthetical is now prose beneath the table, where it cannot
be counted. This is the fourth time this exact defect has been recorded — `audit-docs.py`
checks the spec ↔ register mirror and cannot see this table at all, which is the argument for
the `docs-audit` skill's snippet being run at every raise *and* every decision, not only at a
raise.

**Not delivered, with verdicts:**

| Item | Verdict |
|---|---|
| `02` FR-137 — the approximating Model | ~~**Deferred, Phase 1b**, with the deadline stated in the requirement.~~ **Delivered 2026-08-19** (PR #120), and the deadline was the reason it landed when it did: before anything referenced a transparency artifact by identifier, so it stayed a decision instead of becoming a migration. See the GLM-approximation slice record below. *(Original verdict, kept:)* `approximating_model_id` stays `None` meanwhile, which is FR-207's declared-and-unbuilt state with a trigger attached |
| `03` FR-224 — the approximation deployment gate | **Deferred, Phase 2.** Needs FR-263 built; nothing in Phase 1 deploys a Rating Version. Building it now would be building ahead of the phase |
| `model_comparison_if_predecessor` in the enforced floor | **Deferred**, owner: the slice that gives `model_comparisons` a queryable model reference. Named in FR-364 rather than left to be noticed  **Owner named 2026-08-22: WK-677**, which owns FR-351, FR-352, FR-353, FR-354, FR-355, FR-356, FR-357, FR-358, FR-359, FR-361, FR-363 and evidence enforcement, and is therefore where a queryable model reference on a comparison belongs. The same workstream took `06` §3.3's per-peril-model-approvals remainder on the same day, for the same reason — both are evidence kinds the floor cannot name while they live inside a JSONB payload, and both are WK-677's subject rather than a passing slice's. |
| §3.3's factor/banding/grouping **rationale** evidence | **Not started** — unmodelled, no artifact holds it. Owner: Phase 1b |
| §4.2's `rating_version` and `deployment` entries in `DEFAULT_POLICY` | **Left as they are.** Their floors are declared in `EVIDENCE_FLOOR` and enforced on any workspace that adds an entry; adding entries for artifacts nothing can submit yet would be shipping a policy for a Phase 2 capability |

#### WK-661 slice — what a penalised fit may claim, 2026-08-18

`glum` warns on every penalised fit that its covariance matrix *"will be incorrect"*, and the
suite has been printing that warning since the prediction slice. It is right: the matrix is
the information matrix of the **unpenalised** problem, and it knows nothing about the
shrinkage that produced the coefficients beside it. OQ-586 asked what such a fit may
report. **`02` FR-197 is the answer: report both numbers, and state the basis.**

**The recommendation on file was a rule about how to decide, not an answer** — *decide
FR-113 and FR-194 together, not for the interval alone* — and honouring it is what
settled the choice. The interval inherits the matrix from the standard errors rather than
introducing it, so refusing the interval would have had to take the standard errors with it,
leaving a penalised fit reporting **no uncertainty at all**. That is what ruled the honest-
looking option out: not that it was wrong about the matrix, but what it would have cost the
half of the question nobody was asking about.

| Delivered | Evidence |
|---|---|
| `UncertaintyBasis` — `information_matrix` \| `unpenalised_information_matrix` | One vocabulary for both halves, in `model-schema` beside `UncertaintyKind`. `02` R5 is about what the platform *claims*, and this is the claim |
| `GlmSpec.uncertainty_basis`, the **single** derivation | Derived from `alpha`, never stored on the fit result: the spec is pinned by `spec_hash` and immutable, so a stored copy could only agree or be wrong (`CLAUDE.md` §2). No migration, no nullable, no fallback |
| `Model.uncertainty_basis` | The reader for FR-113's half — a coefficient surface asks the Model rather than deriving `alpha > 0` for itself. `None` for a GBM, where FR-198 refuses an interval outright and there is no matrix to describe |
| `Uncertainty.basis` on every prediction | Populated from the spec in `_score_glm`. The validator **refuses an interval with no basis**, so the qualification cannot be dropped by the next caller rather than merely being present in this one |
| Both directions tested end to end | A penalised fit through the real Job reports `unpenalised_information_matrix`; an unpenalised one reports `information_matrix`. Without the second, a field hard-coded to the first would pass |

**Two things the build decided that the question had left open.** The basis is read from
`alpha`, **not** from `glum`'s warning text — the fit swallows that warning inside
`catch_warnings`, and a library's prose is not a mechanism; it can be reworded in a patch
release without anything failing. And `l1_ratio` alone does not make a fit penalised: at
`alpha = 0` there is no penalty to mix, so reading the basis off the mix would have labelled
every elastic-net default approximate. Both are pinned by tests rather than left in a comment.

**Not delivered, with verdicts:**

| Item | Verdict |
|---|---|
| The **correct** penalised covariance — bootstrap or a penalty-aware sandwich | **Deferred with a named trigger**, which is the half of this decision that stops it decaying: built when the first consumer needs valid penalised inference — a surface that renders coefficient intervals on a penalised fit, or an approval that cites them. ~200 refits is a different cost class from a fit, so it is a Job and not a fit-time step. Owner: the slice that builds the first such consumer  **Owner named 2026-08-22: Phase 1b, gated on a consumer existing.** "The slice that builds the first such consumer" describes a trigger, not an owner — but unlike the other four this one is *genuinely* conditional, because the work is ~200 refits as a Job and nothing today renders or cites a coefficient interval on a penalised fit. The honest verdict is therefore **not started, Phase 1b, with the trigger stated**: the first view or export that shows an interval for a `select_by == "cv"` fit. Recording the trigger *and* a phase is the difference between a deferral and a silence. |
| A coefficient surface that renders the basis | **Not started, and nothing to start on.** Regularisation has no UI and nothing in `02` §4.11's comparison reads the intervals — which is why FR-113's half ships as a property with a stated reader rather than as a rendered label |
| Suppressing `glum`'s warning now that the platform states the same fact | **Rejected.** The warning is the library telling the truth about its own return value, and a repository that silences it keeps the fact only where its own code remembers to look |

#### WK-661 slice — the boundary that keeps a scoring image cheap, 2026-08-18

OQ-642 decided that scoring ships in the same image through Phases 1–2 and gets its own
from Phase 3. The image is Phase 3 and stays there. What cannot wait is the property that
makes it a repackaging rather than a rewrite: **the scoring path must never grow a dependency
on the libraries that fit models**, and two phases of modelling work sit between the decision
and the split.

`07` **NFR-535** is that property, and it is enforced by scoring a real Model in a
subprocess where `glum`, `scikit-learn`, `celery` and `dagster` cannot be imported — asserting
the Poisson identity, so the design reconstructs, the base level resolves and the offset
applies with the fitting stack absent. ADR-705 is what makes that possible at all; this is
the first check that it is *still* true.

**An import-linter contract is the wrong instrument, learnt by writing one.** The obvious
mechanism was a fourth contract in `.importlinter`, and it reported four violations on its
first run — `predict → glm → glum`, `predict → factors → bandings → sklearn`, and two more.
Every one of those imports is **already at its call site**, inside `fit_glm`,
`propose_banding` and `propose_grouping`, which is exactly the discipline the requirement
wants. import-linter reads the AST and cannot tell a function-scope import from a module-scope
one, so the only ways to green the contract were to weaken it or to move modules that have no
other reason to move. The requirement records this, because the next person to reach for
import-linter here should not have to rediscover it.

| Delivered | Evidence |
|---|---|
| `test_scoring_without_the_fitting_stack.py` | Fit in the parent, score in a child with a `MetaPathFinder` refusing the fitting stack. Artifacts cross as JSON, which is also the shape a scoring service receives them in (ADR-705) |
| A test that the blocker blocks | Without it a `Blocker` returning `None` for everything would let the first test pass while importing `glum` freely — a green check proving nothing, which is what this kind of test is most prone to |
| `xgboost` / `lightgbm` deliberately **not** blocked | `02` FR-193 scores a GBM by loading its JSON booster. Found by checking the requirement against FR-193 rather than by reasoning about what a scoring service obviously needs — the first draft had both on the forbidden side |

**Not delivered, with verdicts:**

| Item | Verdict |
|---|---|
| The separate scoring image | **Phase 3**, unchanged by this. Building it now would be building ahead of the phase; the point of the slice is that it will be a repackaging |
| The scoring API entry point in the test's scope | **Not started — there is no scoring API.** `03` is Phase 2. The requirement names the extension explicitly: the slice that builds it adds that path to this test rather than adding a second mechanism |
| `03` FR-232/218/252 | **Spec only, Phase 2**, which is the rule and not a shortfall (`CLAUDE.md` §0) |

#### WK-661 slice — the profile contract, and a divergence that had been recorded for four days, 2026-08-19

`docs/roadmap.md` had carried a row since 2026-08-15 saying that `ColumnProfile` has no
`histogram` while `01` §4.7's example **and** `docs/contracts/schemas/profile.schema.json`
both declare one. It was recorded and then built around — the state `CLAUDE.md` §0 exists to
prevent, since a divergence written down and left alone is indistinguishable, from the next
slice's point of view, from one nobody noticed.

**The contract was right and the requirement was incomplete.** FR-60 enumerates the
statistics profiling produces and never named this one, so `01` gains **FR-65** rather
than the schema losing a field. Bins are equal-width over the observed `[min, max]` with
edges chosen in Python, not by either engine's own histogram function: FR-62 requires
one answer regardless of engine, and every divergence `test_the_two_profiling_paths_agree`
has ever caught came from an engine default.

| Delivered | Evidence |
|---|---|
| **FR-65** — `Histogram` on `ColumnProfile` | One frozen shape in `model-schema` with three invariants: one more edge than bins, strictly increasing edges, one exposure weight per bin when exposure is present |
| Both profiling engines compute it | `profile_frame` (Polars) and `profile_parquet` (DuckDB), sharing `_histogram_edges` so the bin boundaries cannot drift. `test_the_two_profiling_paths_agree` carries the histogram free and **agreed on the first attempt, with no tolerance added** |
| **FR-64** delivered | `severity_minor` → `mean_severity`, `burning_cost_minor` → `mean_burning_cost`. Both are ratios, not amounts; `_minor` is reserved for integer minor units (FR-10). The hand-written money-scan exclusion in `backend/tests/test_contracts.py` is **deleted, not grown** — the new names do not match the scan's pattern |
| `profile.schema.json` generated for the first time | 21 generated contracts, up from 20. The hand-written Phase-0 schema and the model were compared against each other for the first time and **six divergences** were reconciled, each with a written verdict for which side was wrong |
| `Profile.job_id` and `Profile.weight_column` | The contract declared both and the model carried neither. Both are now wired from the real profiling path: `store_profile` had always taken a `job_id` that `_profile_version` never passed, so `ProfileRow.job_id` and the `profile.created` audit event had been persisting `NULL` for **every** profiling Job since the handler was written |
| The Profile view renders histograms | `HistogramChart.vue`, ECharts, exposure plotted beside counts on a second axis when the profile carries it. `01` §5.3's Contents item, one of the six the WK-663 record listed as missing |
| The dtype label uncoloured | It was tinted by `psiBand(null)`, which returns `"stable"` before any threshold — so it was never showing a PSI band, only the colour of one, on a view with no comparison in it |

**What it found, beyond the histogram:**

- **`ColumnProfile.row_count`** — the one of the six nobody had predicted. Verdict: model
  right, and load-bearing: it is `VR-DST-6`'s standard-error divisor and gates the check.
- **The `job_id`/`weight_column` wiring shipped with zero assertions.** Deleting it left the
  whole suite green. Closed in `fe3e020`, and the obvious assertion was the wrong one — the
  model's default for `weight_column` and the fixture's exposure column are both
  `exposure_years`, so a backend assertion passes whether or not anything records the
  argument. The real proof profiles a frame whose exposure column is named `earned_years`.
- **`scope-audit.py DATA --catalogue VR` reads 1 / 38, not 38 / 38** — found by running the
  audit rather than quoting it. Not a regression; see the corrected WK-663 row above.
- **Five scalar-type divergences between the hand-authored contracts and the models**,
  found in this slice's closing review by reading the branch diff file by file rather than
  by any check. `mean_severity` and `mean_burning_cost` declared `MoneyMinor` —
  `{"type": "integer"}` — in both `profile.schema.json` and `banding.schema.json`, against
  `float` in `OneWayRow`; and `profile.schema.json` typed `severity_ci`'s two bounds as
  integers where `banding.schema.json`'s copy of the identical shape typed them as numbers.
  The published contract therefore asserted exactly the rounding **FR-64** exists to
  forbid, three commits after the rename that requirement asked for. **All five predate the
  slice** — `severity_minor: MoneyMinor` against `float | None` at the branch base — so the
  rename moved a divergence under new names without looking beneath them. Fixed here, with
  the record in `01` §4.7's note of 2026-08-19.

  The useful half is why nothing caught it: **every conformance test compared field names.**
  `test_the_column_profile_shape_matches_its_contract` was written specifically to look one
  level deeper than the flat tests and still compared only the property names it found
  there — the same claim the four earlier `Banding`/`Grouping` divergences also satisfied.
  `test_generated_and_authored_agree_on_scalar_types` now compares admitted JSON types
  across all six shapes carrying both a generated and a hand-authored contract, following
  `$ref`s between files and unwrapping `anyOf`. It deliberately ignores `null` (the two
  sides differ on nullability uniformly, which is its own reconciliation) and compares only
  paths present on both sides, so `top_levels` — a *structural* disagreement — stays
  FR-66's with an owner rather than becoming an exemption entry here.

**Not delivered, with verdicts:**

| Item | Verdict |
|---|---|
| **FR-66** — `top_levels` carrying `exposure_years` per level | **Deferred, owned, and appended rather than negotiated away.** The contract declares `{level, count, exposure_years}`; the model carries a two-element `(str, int)`. Closing it means per-level exposure in both engines plus every reader that treats the item as `(str, int)` — 22 call sites across 7 non-generated files, including the distributional validation layer. That is a feature the size of this slice, not a reconciliation. The contract is **not** edited down to what was built (`CLAUDE.md` §14). Owner: WK-661's next slice, or whoever picks up FR-66 |
| **OQ-565** — `Dataset` has no status, validated-at or owner | **Raised open and deliberately not decided by this slice; decided by the maintainer 2026-08-19.** `01` §5.3's dataset list asks to display all three and §4.1 never defined them. There are two defensible answers — `Dataset` gains the three fields, or §5.3 means the *latest version's* status and validated-at plus a workspace-level owner — so it is recorded with options and a recommendation (read them off the latest version, but give `Dataset` an explicit `owner_id`, because no version carries ownership and `06`'s RBAC will need a subject) rather than being silently picked. **The recommendation was accepted 2026-08-19** and applied as `FR-55` (`latest_version_status` and `last_validated_at` derived per request, never stored — and the date scoped to the most recently *validated* version, not the latest, so a fresh draft above a validated version does not read as never validated) and `FR-82` (`Dataset.owner_id`, explicit). **Still not delivered: WK-664's, with the trigger in each requirement** |
| **`01` §5.3's PSI comparison selector** | **Built 2026-08-19.** `compareProfiles()` has its caller; the reference-version picker lives in the route query (**OQ-556**), versions with no stored profile are disabled rather than offered, and each column card carries a `ColumnDrift` block banded against `VR-DST-1`. The Contents claim is now met rather than annotated. |
| The other four of the WK-663 record's six §5.3 Contents items | **Unchanged, still WK-664's** — dataset status/validated/owner (**unblocked 2026-08-19** — OQ-565 decided, `FR-55`/`FR-82` say what to build), the lineage graph, and threshold editing in the rule set editor. Threshold editing of these is **delivered 2026-08-25 (W6b-13)** as rule versioning under `FR-56` — see [the W6b-13 plan](../plans/PL-00792-w6b-13-rule-set-rule-versioning-screen-implementation-plan.md); the other two remain. **All six delivered 2026-08-26, the lineage graph last (W6b-12)** — the arithmetic, because a bare count has been the stale thing twice: status badge, last validated and owner (**W6b-3**, fields via `FR-55`/`FR-82`), histograms (**WK-661**), PSI selector (**WK-661**), lineage graph (**W6b-12**), plus threshold editing (**W6b-13**). |
| `NFR-465` / `NFR-466` | **Unchanged** — measured, not tested; WK-660's verdict stands |

**Retrofit list (§5):** untouched. No new money field, no new artifact type, no schema
migration; `mean_severity` and `mean_burning_cost` were floats before the rename and are
floats after it, which is the whole point of FR-64. **In the model.** The published
contract had been calling both of them integers since before this slice began, which is the
one place a money-discipline claim actually reaches an external consumer — worth stating
plainly, because "the retrofit list is untouched" was true of the code and not of the
contract, and the two are the same promise.

**Gate (local, 2026-08-19, both halves, each exit code read on its own):** ruff clean ·
mypy --strict on 125 source files · import-linter 3 kept / 0 broken · **1264 python tests**,
zero skipped, with compose up so the Postgres-backed job tests actually ran ·
docs audit, 476 requirements across 8 specs · req-coverage 223 of 476 marked (46.8 %) ·
**21 generated contracts match** · `pnpm install --frozen-lockfile` · `generate:api` ·
eslint · `vue-tsc --build` · **109 frontend tests** · `pnpm build`.

**Enforcement proven against deliberately broken input** (§13 step 4): the nested contract
conformance test bit on all four mutations, in both directions; `job_id=None` in the worker
failed the artifact assertion with `assert None == UUID('01a018f2-…')` and, after this
slice added the assertion on the persisted column, fails there too; and passing
`weight_column="exposure_years"` in place of the recorded argument failed with
`assert 'exposure_years' == 'earned_years'`.

The type comparison added in the closing review was broken three ways before being trusted.
Restoring `MoneyMinor` on `banding`'s `mean_severity` failed with *"the model and the
contract disagree on the type of `band_stats.[].mean_severity` (model ['number'], contract
['integer'])"*. Retyping `profile`'s `severity_ci` bounds as integers failed the same way at
`one_ways.[].rows.[].severity_ci.[]` — **but only after a second fix**: the first walker read
`items` and not `prefixItems`, and Pydantic emits a fixed-length tuple as `prefixItems`, so
the deliberately broken interval passed. Every tuple field in every contract was invisible
and nothing said so. Removing the `prefixItems` line again fails
`test_the_type_comparison_reaches_the_one_way_row` on both shapes, naming the path it can no
longer see. That test names its three paths rather than counting them, because the first
attempt at a control — comparing aligned paths against a fraction of the walker's own output
— did **not** fire when the walker was crippled: a walker that stops descending shrinks the
numerator and denominator together, so the threshold moves out of the way of the defect it
exists to catch. An exemption entry for `top_levels` was written and then deleted for the
adjacent reason: with the walker fixed, that divergence is a path mismatch rather than a
type mismatch, so the entry suppressed nothing and only made the list look load-bearing.

#### WK-661 slice — `top_levels` carries exposure per level, 2026-08-19

**FR-66 delivered.** `ColumnProfile.top_levels` moves from an unnamed
`tuple[tuple[str, int], ...]` to `tuple[LevelCount, ...]` — `{level: str | None, count: int,
exposure_years: DecimalStr | None}` — computed by both profiling engines and read under
those names everywhere `top_levels` is read. **The authored contract needed no edit**:
`docs/contracts/schemas/profile.schema.json` had declared `{level, count, exposure_years}`
since Phase 0, so this slice moved the model to the document rather than the other way
round — the same direction the profile-contract slice moved a day earlier.

| Delivered | Evidence |
|---|---|
| `LevelCount` in `model-schema` | `{level, count, exposure_years}`, `frozen`, `extra="forbid"`. `exposure_years` carried its own `field_validator` refusing a `float` outright — the one strict `DecimalStr` field in the repository. **Superseded 2026-08-19** when `OQ-547` was decided: the rule moved onto `DecimalStr` itself and the field-scoped validator was deleted (FR-21) |
| Both profiling engines compute per-level exposure | `profile_frame` and `profile_parquet` share `_stored_exposure`, so the two cannot compute it two different ways |
| Every reader moved off positional access | `compare_profiles` and `_psi` in `pricing_core.data.profile`; `validate.py`'s `_level_counts`, `_psi_column` (`VR-DST-1`), `_new_level` (`VR-DST-2`) and `_vanished_level` (`VR-DST-3`) |
| `VR-DST-3`'s fallback corrected | Where no `one_ways` summary exists, the fallback now reads `exposure_years` and drops to `count` only when the version carried no exposure column — it previously used count *as if* it were exposure, contradicting the rule's own definition ("levels with material reference exposure") |
| Nulls excluded from three checks | `str(level)` no longer coerces a null to the literal `"None"`. `VR-DST-1`'s PSI, `VR-DST-2` and `VR-DST-3` now exclude nulls from both sides — **this moves published PSI numbers on columns carrying nulls**, and a column that had nulls in the reference and none now no longer reports a phantom vanished level. `VR-DST-4` null-rate-shift retains the signal; both changed checks were previously double-counting it under an accidental level name |
| The nested conformance test deepened | `test_the_column_profile_shape_matches_its_contract` now descends into `top_levels`' item and compares its property names, closing the exact blind spot that let the shape divergence hide behind a matching container name. **Proven against deliberately broken input**: an invented property added to the authored contract was confirmed named by the test, then reverted (`57a0cc0`) |
| The Vue chip list shows exposure per level | `ProfileView.vue`'s `top_levels` chips render `exposure_years` beside `count`; no new §5.3 Contents item — this corrected one that already existed |

**Both questions decided 2026-08-19** (they were raised by this slice and answered in the
next one; the slice record is below):

- **`OQ-566`** — **decided: defer both halves, together, until a consumer needs an
  exposure-ordered view.** Selection stays by count and `VR-DST-1`'s PSI stays
  count-weighted. FR-60 is amended to say so — the spec asked for two selections and
  the platform produces one, and the spec was the side that was wrong. The deferral, its
  trigger (a named reader: `02`'s factor workbench or a monitoring view) and its
  deliberately **unowned** status are **FR-67**.
- **`OQ-547`** — **decided: `DecimalStr` refuses a `float` at validation** (FR-21),
  delivered the same day, `Relativity` included. `LevelCount.exposure_years`'s field-scoped
  validator is deleted rather than duplicated.

**Gate (local, 2026-08-19, both halves, each exit code read on its own):** ruff clean ·
mypy --strict on 125 source files · import-linter 3 kept / 0 broken · **1281 python tests**,
zero skipped · docs audit, 478 requirements across 8 specs, 63 open questions all mirrored ·
req-coverage 224 of 478 marked (46.9 %) · **21 generated contracts match** ·
`pnpm install --frozen-lockfile` · `generate:api` · eslint · `vue-tsc --build` ·
**113 frontend tests** · `pnpm build`. `backend/tests/test_demo_guide.py` — 11 passed; the
guide is derived (FR-409) and needed no hand edit.

#### Slice — the exact-decimal types refuse a float, and the audit that decided it (2026-08-19)

`OQ-547` and `OQ-566`, both raised by the `top_levels` slice the day before, decided
and applied. `OQ-566` is a deferral with a trigger (FR-67); `OQ-547` is a code
change (FR-21). **The audit the recommendation called "the real work" is what this
record is mostly about**, because it changed three things the decision had assumed.

| Delivered | Evidence |
|---|---|
| `DecimalStr` and `Relativity` reject a `float` | A shared `BeforeValidator` in `model_schema.money`. Refusal proven on a Python float, a float nested in a `tuple[DecimalStr, ...]`, `model_validate` of a dict, and `model_validate_json` of a JSON *number*; `str`, `int` and `Decimal` still accepted and the wire form still a string (`test_money.py`, five new `FR-10` tests) |
| `LevelCount.exposure_years`'s validator deleted | The inconsistency `OQ-547` recorded is resolved by generalising the strict field, not by leaving ten lax ones beside it |
| **The caller audit came back clean** | Every existing caller passes a `str`, an `int` or a `Decimal`. The paths that compute in float — both profiling engines, the numpy lift/AE bins, the double-lift bins — already quantised at the boundary, so `_stored_exposure` is now named in FR-21 as the pattern to copy. **No caller needed rerouting and the full suite passed unchanged**, which is the opposite of what the recommendation expected |
| **The affected-field count was wrong** | The question said "26 `DecimalStr` fields across 7 modules". There are **11, across 6** — the 26 was a count of every *line mentioning* `DecimalStr`, imports and `money.py`'s own definition included. Corrected in `docs/open-questions.md`, `00` §7 and here. A figure nobody had recomputed since it was written down, which is why `CLAUDE.md` §0 keeps counts out of prose |
| **A published contract was declaring three exact decimals as JSON numbers** | `docs/contracts/schemas/peril-structure.schema.json` typed `restoration_loading`, `ratio` and `tolerance` as `{"type": "number"}` while all three are `DecimalStr` the model has always serialised as strings — verified by dumping a real `Reconciliation` (`"1.010000"`, `"0.02"`). Wrong since Phase 0; strict input is what made it *reachable*, since a client following the contract now gets a 422 instead of a silent coercion. All three moved to the `Decimal` `$ref` every other schema in the suite already used, and the undeclared `loading_factor` added |
| The check that should have caught it, widened | `test_generated_and_authored_agree_on_scalar_types` compared **6** slugs while **12** schemas have both sides — and the six were never chosen, merely never added. Now 11, with `COMPARED_SLUGS` a named constant and `test_every_eligible_schema_is_compared` failing the day an eligible schema is neither compared nor pinned. **The check would have caught this contract on the day it was written** |
| The one divergence it surfaced is pinned, not fixed | Widening found `diagnostics`: `GlmDiagnostic.aliasing` is `tuple[str, ...]` against a contract declaring an array of untyped `object`. Neither side is obviously wrong — an object entry could carry `{term, aliased_with, reason}` — so it is **`OQ-587`**, and `test_the_diagnostics_divergence_is_exactly_the_known_one` pins it at exactly that path. A *new* divergence in `diagnostics` still fails; the day `OQ-587` is decided the pin fails and is deleted *(it was, 2026-08-21 — FR-173: the names kept, the authored contract corrected to strings, the pin deleted)* |

**Enforcement proven against deliberately broken input**, all three, each reverted after:
the widened comparison fails on the pre-fix `peril-structure` contract; the coverage guard
fails when a slug is removed from `COMPARED_SLUGS`; the pin fails when a second divergence
is injected into `diagnostics.schema.json`.

**Not delivered, stated rather than left silent:** `ReconcileRequest.tolerance`
(`backend/src/app/api/peril_structures.py`) is a bare `Decimal`, so a JSON number is still
coerced there and stringified into the job parameters — the same hole one layer earlier,
and outside this change because it is an API request shape rather than an artifact field.
`ReconciliationResult` in `pricing-core` is a frozen dataclass and therefore unvalidated;
that is true of every `pricing-core` dataclass and singling one out would be arbitrary.
Both are recorded in `OQ-587`'s neighbourhood rather than fixed here.

**Gate (local, 2026-08-19, both halves, each exit code read on its own):** ruff clean ·
mypy --strict on 125 source files · import-linter 3 kept / 0 broken · **1300 python tests**,
zero skipped · docs audit, 480 requirements across 8 specs, 64 open questions all mirrored ·
req-coverage 224 of 480 marked (46.7 %) · **21 generated contracts match** ·
`pnpm install --frozen-lockfile` · `generate:api` · eslint · `vue-tsc --build` ·
**113 frontend tests** · `pnpm build`. The docs audit failed once on the way, correctly: a
bolded `**FR-67**` used as a *cross-reference* reads as a second definition of it —
the trap `.claude/skills/spec-change` already documents, paid for again by not reading the
skill first.


#### WK-661 slice — paired quantile models, and the name a quantile pair had no right to (2026-08-19)

The twentieth slice, and the one that makes FR-199 real: a GBM can now carry a
prediction interval, from two Models fitted with the `quantile` template and linked to the
model they bound. Two requirements appended, one open question raised and decided the same
day, and all four of `UnavailableReason`'s values reachable for the first time.

| Delivered | Evidence |
|---|---|
| `interval_for` on `GbmSpec`, joining `spec_hash` | `IntervalFor(model_id, model_version, alpha)`; `SPEC_HASH_VERSION` `v3 → v4` in the same commit as the field (FR-206). Tests pin that two bounds against different central models, the two sides of one pair, and a bound versus an ordinary GBM all hash apart — the three collisions that would have let FR-204 hand a caller somebody else's model |
| A bound must match the model it bounds | `_refuse_mismatched_interval_model` in `reserve_model`, before a Job exists: family, dataset version, split and **factor set** — the last compared as a *set*, since two specs listing the same factors in a different order describe the same design matrix |
| A bound must actually be a quantile fit | The rule the plan did not have and FR-199's text does: the objective must resolve to the `quantile` template, at the same alpha `interval_for` declares. A bound fitted with `count:poisson` passes every structural rule and estimates the **mean** |
| One bound per side | FR-200(iv). A second lower bound satisfies every other rule, and the response carries a single `level` with nothing to say which pair produced it |
| Bounds are findable | `load_interval_models`, ordered lower-first so no second caller sorts them another way, plus a **partial** functional index on `(spec -> 'interval_for' ->> 'model_id')` — partial because almost no model is a bound, and the common answer (none) is the one that must stay cheap |
| Crossing detected at fit time | `detect_quantile_crossing` in `pricing-core`, and `QuantileCrossing` on the **second** bound's `GbmDiagnostics`. The first has no counterpart when it is fitted and FR-170 computes diagnostics once, so there is no later pass in which to fill it in |
| Crossing refused at predict time | 409 `MODEL_INTERVAL_UNAVAILABLE` naming the rows and the worst gap. Without it the honest finding reached `PredictedRow`'s ordering validator and became a 500 with the reason in a traceback |
| All four `UnavailableReason` values reachable | `_score_gbm`'s four arms, most-specific-first, and a test that pins the order |

**The requirement named a thing the contract had no word for, and that is the finding.**
FR-196 (decided the day before, OQ-585) fixed the platform at **exactly one**
interval kind, `confidence_interval_mean`, and reserved `prediction_interval` for a `φ·V(μ)`
computation over aggregates. FR-199's deliverable is neither: a quantile pair covers
`Y`, not `E[Y|x]`, and it is produced per row by a different estimator entirely. Raised as
**OQ-588** rather than picked (`CLAUDE.md` §0) and **decided by the maintainer the same
day** at the recommendation — a third member, `quantile_pair_interval`, specified as
**FR-201**. Neither existing value is widened and the reserved name is left waiting for
the consumer that triggers it, so **FR-196 is amended by addendum rather than edited**
(`CLAUDE.md` §14). The argument that admits it is FR-196's own: it refused a second kind
shipped *before a consumer existed*, and FR-199's pair is opt-in at 2–3× the fit cost,
so nobody receives one without having asked.

**FR-198 named two reasons and did not say what they meant.** `interval_models_not_approved`
and `interval_models_stale` had been declared and unreachable since the prediction slice, and
each had two defensible readings. Making them reachable forced the choice, so it is recorded
as a requirement rather than made in code: **FR-200(ii)** reads "not approved" as *less
reviewed than the model it bounds* — the strict reading would make the feature unusable at
exactly the point an actuary is deciding whether the bounds are any good — and **(iii)** reads
"stale" as *the central Model is `superseded`*, the literal reading of FR-198's own
parenthetical, reachable because `SCOREABLE_MODEL_STATUSES` admits `superseded`. Both
alternatives are named in the requirement, so a later reader can see they were decided.

**Two orderings are load-bearing, and both are pinned by tests.** The pairing check runs
**before** the factor check: a bound naming the wrong dataset version also fails factor
resolution, and reported the other way round the caller re-checks factors that were never
wrong. And `_score_gbm`'s staleness arm runs before its approval arm, so a superseded model
with unapproved bounds is told the family has moved on rather than told to go and get bounds
approved for a version nobody should quote.

**Three fixtures were corrected by the platform rather than the other way round**, which is
the shape worth recording: a `custom_objectives` CHECK refused an objective stamped
`approved` without a certificate, so the fixture now certifies through the real Job; a factor
must name a column the dataset actually has; and FR-153 requires a spec naming a custom
objective to declare its `response`. A fourth was mine alone — a `unit_of_work` opened inside
another takes a second connection and **deadlocks against the pool rather than failing**, so
the run hung with no output at all.

**Enforcement proven against broken input**, each neutralised in turn and restored:
the structural mismatch check reddens 3 tests; the quantile-template check 2; the
one-bound-per-side check 1; the fit-time crossing attachment reddens the pair test with
`assert None is not None`. The `Uncertainty` validator additionally refuses a `level` that
disagrees with the alphas it came from — a 0.05/0.95 pair covers 0.90, and a response
claiming 0.95 overstates its coverage by exactly the amount a reader cannot check.

**Not delivered, with owners.** **No frontend**: nothing renders a GBM interval or a
crossing figure, so both are reachable only over the API — `02` §5.3's model-detail view is
**WK-664**'s and building it here would be building ahead of the row that owns it. The
`alpha != 0.5` refusal is a validator and **has no JSON Schema form**, so the published
contract carries the range and not the median rule; the type is its only enforcement.
FR-200(ii) is implemented as the single case that matters — an `approved` central model
with a not-`approved` bound — rather than as a general lifecycle ordering, because `02`
declares no such ordering and inventing one would be specifying a comparison nothing needs.

**Bookkeeping corrected while here:** WK-661's row said "eighteen slices in" and the
exact-decimal slice (PR #116, 2026-08-19) had already landed without being added to it. The
row now reads twenty and names both.

**Gate, both halves, run locally.** ruff 0 · mypy --strict 0 (125 source files) ·
import-linter 3 kept / 0 broken · **1339 python tests, zero skipped** in 315 s (was 1300) ·
audit-docs 0 — **482 requirements** across 8 specs (was 480), **65 open questions** all
mirrored (was 64) · req-coverage **227 of 482 marked, 47.1 %** (was 224 of 480) ·
`generate-contracts.py --check` 0, **21 generated contracts match** ·
`pnpm install --frozen-lockfile` · `generate:api` · eslint · `vue-tsc --build` no errors ·
**113 frontend tests** · `pnpm build`. `scope-audit.py MODEL --endpoints`: **FR-199
leaves the unevidenced list**, which falls 21 → 20, and FR-200/201 land evidenced —
113 in scope, 93 with evidence (82 %).

#### WK-661 slice — the GLM approximation as a Model, 2026-08-19

The twenty-first slice, and the one that discharged a deadline rather than answered a need:
FR-137 had to land before anything referenced a transparency artifact by identifier,
after which it would have been a migration instead of a decision. **OQ-577 was decided
by the maintainer as option A before execution began** — the inline coefficient table stays
as a legacy era, exclusive with `approximating_model_id`, rather than being migrated away.

| Delivered | Evidence |
|---|---|
| The approximation is a Model in its own right | `GlmSpec.approximates_model_id`, and `approximation_spec(spec, *, source_model_id)` deriving the surrogate's spec from the GBM's — `dataset_version_id`, `split_ref` and `factors` copied, `SURROGATE_RESPONSE_COLUMN` (`__gbm_prediction__`) as the response |
| The fidelity is measured against the booster **by mechanism** | `diagnostics.py` reads actuals as `data[spec.response_column]`, and that column *is* `__gbm_prediction__` — so the A/E is against the booster because the spec object says so, not because a comment does. Traced end to end in the final review rather than asserted |
| Two eras, mutually exclusive | A validator refusing a block that carries both inline coefficients and an `approximating_model_id`, and refusing one that carries neither |
| The legacy era cannot be deleted silently | Positive tests, added in the fix wave. Before them all three `GlmApproximation(` uses asserted *refusal*, so deleting the legacy fields would have left the gate green — the maintainer's option-A decision was protected by nothing the suite could see |
| A hand-written surrogate spec is refused | `_refuse_mismatched_approximation`, comparing exactly the three fields `approximation_spec` copies; `MODEL_APPROXIMATION_INVALID` declared in `02` §5.1 and registered in `errors.py` |
| `spec_hash` moved with the field | v4 → v5 in the same commit as `approximates_model_id`, contracts regenerated |
| FR-141 appended | The maximum was 101, not the last id read. It carries the `-approx` slug convention the code needed and no spec stated: a source slug over 57 characters fails against the 64-character column |

**Three open questions raised, none decided here.** **OQ-589** — a rebuild
(`should_fit=False`) pays a full GLM fit plus one type-III refit per factor for numbers it
then discards, because `store()` only persists them when `should_fit` is `True`.
**OQ-548** — nothing in this repository compares a spec's §5.1 error-code table against
`errors.py`; verified twice on this branch, and structural, applying to every module rather
than to `02` alone. **OQ-646** — a `PlatformError` raised inside a Job handler loses its
`.code` to `JOB_HANDLER_FAILED`, which is why this slice's two refusal tests had to call the
handler directly instead of going through `execute_job`. *(OQ-589 and OQ-548 decided
2026-08-21 — see §10; OQ-646 remains open, placed on the any-time row.)*

**A check went red on purpose, from the first commit to the fifth.**
`test_errors.py::test_spec_error_codes_are_all_constructible` reads the spec's code list, so
declaring `MODEL_APPROXIMATION_INVALID` in `02` reddened it until the registration landed
four tasks later. Ruled deliberately rather than worked around: moving the registration into
the docs commit would have put a backend source edit inside a docs-only commit to buy a green
intermediate state nothing consumes. Same shape as PR #98 — a check that fires on the
*contract* goes red at a slice's first commit rather than its last.

**Measured, not asserted.** +0.26 s / ~7 % on the transparency Job, against a
**single-factor** fixture. That does not bound a multi-factor model — type-III diagnostics
refit the surrogate once per factor, which is exactly what OQ-589 is about.
`type_iii=False` is the lever if it ever bites, and is not pulled without the maintainer.

**Not delivered, with owners.** No frontend renders the surrogate link or the approximation's
own model page — `02` §5.3's model-detail view is **WK-664**'s. A stored block with *empty*
coefficients and no id is now refused on read; unreachable in practice, since the old builder
always emitted at least an intercept, so it is parked rather than guarded.

**Gate, both halves, run locally.** ruff 0 · mypy --strict 0 (125 source files) ·
**1362 python tests, zero skipped** in 265 s (was 1339) · audit-docs 0 — **483 requirements**
(was 482), **69 open questions** all mirrored (was 66) · req-coverage **229 of 483 marked,
47.4 %** (was 227 of 482) · `generate-contracts.py --check` 0, **21 generated contracts
match**.

**Recorded late, and that is the process finding.** PR #120 updated WK-661's row in §6 and wrote
no slice record; this one was written 2026-08-19 from the branch's ledger and the merged
diff. It is the second such omission in WK-661 — the prediction slice (PR #102) is the first, and
is noted in the same row. A row's prose says a slice happened; only a record says what it
found.

#### WK-661 — outstanding work, derived 2026-08-19

**Derived from the specification first, then evidenced** (`CLAUDE.md` §13 rule 1):
`scope-audit.py MODEL`, then `--endpoints`. `02` declares no `XX-YYY-N` catalogue, so unlike
`01` there is no catalogue axis to check.

> **Superseded in part, 2026-08-20 — the custom-metrics slice landed.** The counts and the
> slice list below were true on 2026-08-19 and are no longer. Re-derived on 2026-08-20 by
> re-running the same two commands, with the current figures beside the originals; the
> 2026-08-19 column is kept rather than overwritten, because what was believed on the day a
> plan was made is the thing a governed record cannot lose. The requirement total rose by
> six because the slice appended FR-155…108, all six of them evidenced; the
> unevidenced 19 are unchanged, and their verdicts below still stand.

| | Derived 2026-08-19 | Re-derived 2026-08-20 |
|---|---|---|
| Requirements in scope | **114** | **120** |
| With evidence | **95 (83 %)** | **101 (84 %)** |
| Without evidence | **19** | **19** |
| Endpoints declared in §5.1 | **35** | **40** |
| Endpoints published | **34 (97 %)** | **40 (100 %)** |

*(`uv run python scripts/scope-audit.py MODEL --endpoints` prints "declared: 40 · published:
40 (100%) · every declared endpoint is published in the contract";
`uv run python scripts/req-coverage.py` prints "requirements specified : 489 · requirements
marked : 235 (48.1%)" repository-wide.)*

~~**Five buildable slices remain**~~ — ~~**four**, corrected 2026-08-20: slice 1 below
is delivered~~ ~~**three**, corrected 2026-08-21: slices 1 and 2 below are delivered~~
~~**one**, corrected 2026-08-21: slices 3 and 4 below are delivered.~~ **None**, corrected
2026-08-22 by the audit-remediation slice: slice 5 — EBM — was delivered on 2026-08-21 by
the pass that struck its row below and left this counter at one. **Every row in this table
is now struck as delivered**, which is the state it was built to reach and the one thing it
never said. Four corrections in three days, each of them this counter lagging a strike made
in the same edit — the table below is the record and this line is a hand-maintained summary
sitting beside it, which is the arrangement §0 warns about.
Smallest first:

| Slice | Requirements | State, and what is actually missing |
|---|---|---|
| ~~**1. Custom metrics**~~ **— DELIVERED 2026-08-20** | ~~FR-154's endpoint~~ FR-MODEL-45, 103–108 | ~~`POST /api/v1/custom-metrics` is the one unpublished endpoint of the 35. Deferred to Phase 1b by a dated amendment in `02` §5.1~~ **Built in the custom-metrics slice recorded below, not deferred to Phase 1b**: six routes rather than one, the artifact, table, certification Job and approval path, `eval_metrics` honoured (FR-159) and early stopping on a Custom Metric (FR-160). The deferral's reasoning — that a custom metric is `feval` and changes what early stopping optimises rather than what the model fits — turned out to be the argument *for* building it inside WK-661: FR-160 made a Custom Metric the only way to early-stop under a callable objective at all |
| ~~**2. Regularisation and cross-validation**~~ **— DELIVERED 2026-08-21** | FR-112, FR-182 | ~~Already paired by a verdict on file — `select_by: cv` lives in the penalty path. The schema is ahead of the code: `GlmSpec` carries `alpha` and `l1_ratio`, and `cv_folds` exists. Missing are the documented penalty path, the CV selection option, declared fold construction (`random`, `temporal`, `grouped_by_key`) with a persisted seed, and per-fold metrics **and their dispersion** persisted as diagnostics rather than the mean alone~~ **DELIVERED 2026-08-21**: `GlmSpec.select_by`/`GlmSpec.cv` (FR-112), `GlmCvSpec`'s three fold-construction methods via `pricing_core.data.splits.assign_folds` (FR-182), `_fit_cv_path` in `pricing_core.modelling.glm`, and `Diagnostics.cross_validation` (`CrossValidationDiagnostics`/`CvPathPoint`/`CvFoldMetric`) persisting the full path and the selected alpha's per-fold dispersion. No new HTTP endpoint (the existing `GET /api/v1/models/{id}/diagnostics` surfaces it) and no frontend work (the Diagnostics view's CV screen remains WK-664's). Two spec interactions found and resolved by dated amendment in `02-modelling.md`: K-fold `temporal` semantics (undefined by FR-73/FR-182; resolved as contiguous time-ordered blocks) and FR-197's `uncertainty_basis` under CV selection (resolved as unconditionally naive/penalised) |
| ~~**3. Tweedie power by profile likelihood**~~ **— DELIVERED 2026-08-21** | ~~FR-114~~ | ~~Today `GlmSpec` only *validates* that a supplied power lies between the two families it spans. Missing: the grid, the persisted profile curve, and recording an estimated `p` as an estimate with its own uncertainty rather than silently baking it in as a constant~~ **DELIVERED 2026-08-21**: `GlmSpec.tweedie` carries the grid; `fit_glm` estimates p by profile likelihood (refit at each point, profile log-likelihood argmax scored with the Tweedie series density at the mean-deviance dispersion estimate), persists the curve on `GlmFitResult.tweedie`, and records the estimate with its 95% profile-likelihood CI — never a constant; a maximum at a scan edge is refused (`GLM_TWEEDIE_POWER_GRID_EDGE`); estimation × CV selection refused by name (FR-207). |
| ~~**4. Offset from another model**~~ **— DELIVERED 2026-08-21** | FR-116 | ~~`offset_model_ref` appears nowhere…~~ **— DELIVERED 2026-08-21:** `OffsetSpec.offset_model_ref` (renamed from the dead `model_ref` scaffold), GLM-to-GLM, resolved at fit/predict/backtest time, refused by name elsewhere. |
| ~~**5. EBM**~~ **— DELIVERED 2026-08-21** | FR-140 | ~~Verdict on file: not started, owner is "the slice that first fits an `ebm` model" — and `ebm` is one of the four Model types in `CLAUDE.md` §7's vocabulary, so WK-661 owns it unless reassigned. The stated cost is `interpret` as a third heavy dependency serving one requirement~~ **DELIVERED 2026-08-21**: term shape functions exported verbatim as additive lookup tables; transparency artifact built from the export with no approximation; universal diagnostics through the shared partition; scoring from the tables alone (ADR-705). The third heavy dependency is now installed, so the 'one requirement for a model type nothing fits' objection is discharged *(2026-08-21: delivered by the EBM slice — see the slice record below.)* |

**The NFR gap — 11 of 12 unevidenced**, and it is not one problem:

| NFRs | Verdict |
|---|---|
| NFR-477, NFR-478 | **Measured 2026-08-15 and recorded in `02` §9**, met for three of the four proposal methods. Unevidenced only because a measurement is not a marker — `CLAUDE.md` §13 rule 1's "evidence is not only markers" case. They need the measurement recognised as the evidence, not a test invented to stand in for it |
| NFR-482, NFR-483, NFR-484 | **Testable today, no fixture needed.** Export/import round-trip with identical predictions; that user expressions never reach `eval`/`exec` and out-of-grammar input fails with a position-accurate error; that every named creation, fit and status transition emits an Audit Event with before/after state  ~~**Testable today**~~ **— two of the three were not, corrected 2026-08-22 by the audit-remediation slice, and each now has its own verdict in `02` §9.** **NFR-484 was**, and is now evidenced (`backend/tests/test_model_nfrs.py`) for every act that has a before; five create events carry none, left as they are and pinned by a test, because a versioned artifact's create has no prior state. **NFR-483 is half testable** — the `eval`/`exec` clause is now evidenced by removing both builtins and watching a legitimate expression still evaluate; the position-accurate error is **not met** (`ExpressionError` carries no `lineno`/`col_offset`) and the per-round time budget is implemented nowhere. **NFR-482 has nothing to test**: a six-way search found **zero** Model export paths and zero import paths — no route, no CLI (`[project.scripts]` is empty), no bundle schema — and its parent FR-5 carries **zero markers**. Owner: **unassigned**, because it is a capability nobody has been asked to build |
| NFR-479, NFR-480, NFR-486 | **Measurable today** against existing fixtures, because none of the three names a data scale: diagnostics adding no more than 30 % to fit wall-clock is a *ratio*, certification completes under 3 minutes, and a diagnostics artifact stays under 50 MB  **Measured 2026-08-22 and recorded in `02` §9.** NFR-480 (0.42–3.56 s of 180 s) and NFR-486 (0.13 MB of 50 MB, GBM path included) are **met with two orders of magnitude of headroom**. **NFR-479 was not met as written** *(re-read 2026-08-22, OQ-572 decided: re-scoped to exclude the per-factor block and re-set to 50 % at a named scale, it is now **met** at every measured arm; the type-III block moved to NFR-487, which is **breached at 678 013 × 60**, and the GBM path to NFR-488, which is met)*, and the cause is a sibling requirement rather than a slow function: FR-172's type-III tests drop each factor and refit, so diagnostics cost one extra fit *per factor* — **510 %** of fit wall-clock at 12 factors, **1 388 %** at 24, **3 002 %** on the GBM path. Everything else `compute_diagnostics` does fits the budget at 9.0–9.5 %. The two requirements cannot both hold as written, so it is raised as **OQ-572** with three options rather than tuned quietly |
| NFR-475, NFR-476, NFR-485 | **Blocked on a fixture that does not exist.** All three name 5 M rows × 60 factors; freMTPL2 is 678 013 rows. Either a synthetic fixture is built, or they are measured at a stated smaller scale with the extrapolation written down. NFR-476's second clause — a custom `expression` objective adding no more than 25 % — is **Phase 2** regardless, since expression objectives do not exist |
| NFR-481 | **Evidenced.** The only one of the twelve carrying a marker today  ~~**Evidenced.**~~ **Half evidenced, corrected 2026-08-22.** The requirement asks for identical GLM coefficients to 1e-10 **and** an identical booster hash; the one marker it carries is the **booster** half, and nothing anywhere refits a GLM on the same `spec_hash` and seed to compare coefficients. Counted as evidenced because a marker existed — the same defect FR-185 was caught by on 2026-08-16, applied to an NFR this time. **Owner: the GLM slice**, a two-fit determinism test beside the code it is about |

**Not WK-661, with the reason:**

| Requirement | Owner |
|---|---|
| FR-144 — `expression` objectives | **Phase 2, WK-690**, behind `expression_objectives_enabled`. The route exists and answers `422` with that code rather than `404`, so a caller learns the capability is off rather than absent |
| FR-95 — `expression` factors | **Phase 2, WK-690**, by OQ-573's decision — its verdict on file reads "owned by that slice", and that slice is WK-690. **WK-690's carry-over list named FR-144/145/150 and not FR-95**; corrected 2026-08-19, **accepted by the maintainer 2026-08-22** — so WK-661 disowns it on a recorded decision rather than on a correction nobody signed. |
| FR-91 — proxy detection | **Phase 3** by OQ-581 (decided 2026-08-15), and by the requirement's own text. Through Phases 1–2 the platform's only treatment is FR-90's `prohibited` flag, which refuses direct use and audits the attempt |
| `02` §5.3's model spec builder, model detail and diagnostics views | **WK-664**, stated in the gradient-boosting and paired-quantile slice records |

**Three requirements had no verdict anywhere until this pass** — **FR-112**,
**FR-114** and **FR-116** were unevidenced and unspoken for in every slice record,
which is the one option `CLAUDE.md` §13 rule 1 does not allow. They are recorded above as not
started, owner WK-661, by WK-661's own scope definition ("every `MODEL` requirement") rather than by
a new assignment. FR-114's verdict is delivered by the 2026-08-21 Tweedie slice and
FR-116's by the offset-from-another-model slice; FR-115 is delivered: markers at `test_glm.py:134,:429` and `test_spec_hash.py:99,:114`, `GLM_SEPARATION_DETECTED` registered and declared — the 'remains unbuilt' lines were stale. The remainder — a bare non-`LinAlgError` `ValueError` from glum still reaches the job unwrapped — is recorded 2026-08-21 as unbuilt, owner WK-661.

#### WK-661 slice — custom metrics, and a field that was read by nothing, 2026-08-20

The twenty-second slice, spanning 2026-08-19 → 08-20. FR-154 gives a Custom Metric
the same lifecycle and grammar as a Custom Objective, declared separately so it can be
reused across objectives — and the slice exists around a single finding: `GbmSpec.eval_metrics`
had been declared since Phase 0 and read by nothing. A caller could name a metric, builtin
or custom, and be told nothing was wrong while none were ever evaluated. FR-159 now
requires it honoured.

| Delivered | Evidence |
|---|---|
| A Custom Metric artifact and table, declared separately from any objective | `custom_metrics` table keyed on `(workspace_id, slug, version)`, undeletable, definition frozen after creation (FR-154/155) — nothing ties a metric to one objective, so the same metric ref resolves under any spec that names it |
| Six HTTP routes, mirroring `custom_objectives` | `POST /custom-metrics` (create/version), `GET /{id}`, `POST /{id}/certify` (202 + Job), `GET /{id}/certificate`, `POST /{id}/submit`, `GET /{id}/usage` (FR-162) |
| `eval_metrics` honoured, not merely declared | `GbmSpec.eval_metrics` now drives `feval`/`custom_metric` wiring on both XGBoost and LightGBM, builtin and custom metrics alike (FR-159) |
| `OBJECTIVE_EARLY_STOPPING_UNSUPPORTED` narrowed, not retired | Early stopping on a **builtin** metric under a callable objective is still refused — both backends hand it the raw score, not the transformed prediction. Only the availability of an alternative changed: declare a Custom Metric in `eval_metrics` and stop on that (FR-160) |
| Two lifecycle edges that were declared and unreachable, now reachable | `draft → deprecated` (the certificate validator exempted only `draft`, so an uncertified metric could not be withdrawn — fixed in `30b6388`, verified to fail against the pre-fix validator); `review → approved` (no `apply_approval_decision` for metrics and no `DEFAULT_POLICY` entry, so `submit` 409'd before the edge was ever reached — fixed in `deb49e7`) |
| `06` §4.2's `custom_metric` approval-policy entry | Added in this slice's Step 0, resolving the spec-vs-code divergence `deb49e7` created — `certified → review` 409'd in every workspace without it. Dated note follows `peril_structure`'s precedent |
| A pre-existing bug, fixed out of scope, in its own commit | `custom_objectives.py` declared `params: dict[str, float]`, coercing money to float, and `TemplateParameter.check` **raises** for a non-int money value — so `capped_gamma` and `spliced_severity` could not be created through their own endpoint at all. Fixed in `040e6e8`. **Pre-existing, not part of FR-154** |

**Two runtime defects found by running a fit, not by reading (`35ba563`).** XGBoost's
eval-log parser (`xgb.callback.EarlyStopping.after_iteration`) re-parses a formatted string
by splitting each `"name:value"` entry on a single `:`. A Custom Metric ref is
`custom_metric:<slug>@<version>` — already `kind:slug@version` — so declaring one raised
`too many values to unpack` the moment the name reached XGBoost's own log line; fixed by
`_xgb_safe_metric_name`, sanitising only the string handed to XGBoost and translating it
back in `_curve`. Separately, XGBoost was found to leak its own implicit default (`rmse`,
picked for a callable objective it cannot introspect) into the curve when only custom
`eval_metrics` were declared and `eval_metric` was therefore never set; fixed by setting
`disable_default_eval_metric` in that case. LightGBM needed neither fix.

**A backend asymmetry, found and fixed (`d8859a2`).** LightGBM's `_fit_lightgbm` reported
only the stopping target when several custom metrics were declared — `first_metric_only`
decides which metric drives early stopping, not which metrics get reported, and the
`stopping_on_custom` branch had narrowed `feval` to the stopping target alone, silently
dropping every other declared custom metric from the curve. XGBoost was unaffected. Fixed
by ordering the stopping target first in `feval`'s return rather than narrowing it, verified
against LightGBM's own `_EarlyStoppingCallback._init` — `first_metric` is
`evaluation_result_list[0].metric_name`, and that list's ordering is builtin `params["metric"]`
entries followed by `feval`'s in return order — so the fix is read against the mechanism it
depends on, not asserted.

**A milestone.** MODEL is now the first module in this repository with **every declared
endpoint published** — 40 of 40, up from 34 of 35 before this slice. Task 1 declared five
more endpoint rows in `02` §5.1 and Task 5 published all six of the Custom Metric routes,
closing the axis.

**Three failures, invisible to every per-task scoped test run, found only by the full gate.**
Each of the seven tasks in this slice ran green against its own test files. Only
`uv run pytest -q` across the whole suite surfaced these — the evidence for `CLAUDE.md`
§11's insistence on running both halves of the gate rather than trusting accumulated
per-task greens:

1. **`backend/tests/test_contracts.py::test_job_status_and_kind_enums_agree_with_the_contract`.**
   `JobKind` gained `metric.certify` in `49bc16d`, regenerating the *generated* schema, but
   the hand-authored `docs/contracts/schemas/job.schema.json` — `CLAUDE.md` §2's "partly
   generated, partly hand-written" seam — was never updated. Fixed by adding `metric.certify`
   to the authored file in the same position the generated one carries it.
2. **`tests/test_repository_invariants.py::test_every_error_code_pricing_core_raises_is_registered_and_declared`.**
   `METRIC_REF_UNRESOLVED`, `METRIC_NOT_APPLICABLE` and `METRIC_NOT_FITTABLE` were registered
   in `errors.py` and named in a prose "Amended 2026-08-19" note in `02` §5.1, but never added
   to the backtick-delimited catalogue list the test actually parses — every prior addition
   (e.g. `MODEL_APPROXIMATION_INVALID`) added the code to that list *and* a note; `49bc16d`
   wrote only the note. The dispatch that caused it said "nothing cross-checks those two
   lists (OQ-548)" — too broad: this repository checks the subset `pricing-core` raises
   against both `errors.py` and the spec catalogue, and that check is what caught this.
   Fixed by adding the three codes to the list; the existing note stands, now complete rather
   than replaced.
3. **`backend/tests/test_demo_guide.py::test_the_guide_names_the_endpoints_a_spec_declares_and_the_contract_lacks`.**
   Hardcoded `{"MODEL", "RATE"} <= modules` (modules with a declared-but-unpublished
   endpoint). MODEL correctly dropped out of that set once this slice closed its endpoint
   axis to 40 of 40 — the code was right, the test's assumption was stale. Narrowed to
   `{"RATE"}`, with a docstring sentence added: the set is *expected* to shrink as modules
   complete, so a future failure here most likely means a module finished, not that
   something broke.

All three were confirmed as genuine (not full-suite-only ordering or environment artefacts)
by re-running each failing test in isolation with the DSN exported — each reproduced
identically alone. After the three fixes, the full suite is green.

**Enforcement proven against broken input (`CLAUDE.md` §13.4).** The `draft → deprecated`
fix (`30b6388`) shipped with a positive test verified to fail against the pre-fix validator.
The `review → approved` fix (`deb49e7`) shipped with the full `certified → review → approved`
lifecycle test and a negative case mirroring `custom_objectives`' own — a decision about
another artifact type leaves the metric untouched. `test_repository_invariants.py`'s
error-code check is itself the proof for finding 2 above: it went red against `49bc16d`'s
incomplete catalogue entry, which is exactly the broken input it exists to catch.

**Gate, both halves, run locally.** ruff 0 · mypy --strict 0 (129 source files) ·
`lint-imports` 0 (3 contracts kept) · **1412 python tests, zero skipped**, in 273 s ·
audit-docs 0 — **489 requirements** across 8 specs, **72 open questions** all mirrored,
**131 error codes** ownership-exclusive (was 128) · req-coverage **235 of 489 marked,
48.1 %** · `generate-contracts.py --check` 0, **23 generated contracts match** · frontend:
`pnpm install --frozen-lockfile`, `generate:api`, `lint`, `type-check`, **131 tests passed**,
`build` — all green, confirming the two new generated contracts (`custom-metric`,
`metric-certificate`) round-trip cleanly through the TypeScript client · `scope-audit.py
MODEL --endpoints`: **40 declared, 40 published (100%)**.

**Not delivered, with owners.** No frontend view renders a Custom Metric — `02` §5.3's
model spec builder is **WK-664**'s, unchanged by this slice. `expression`-kind metrics remain
Phase 2 behind `expression_objectives_enabled`, per FR-154's own template-only scope
for Phase 1. The four other buildable slices this workstream's outstanding-work table named
on 2026-08-19 (regularisation/CV, Tweedie power, offset-from-model, EBM) are untouched by
this slice.

**`custom_metric` has no evidence floor — deferred, then dropped from this record until the
whole-branch review found it (2026-08-20).** `06` §3.3 has no evidence row for
`custom_metric`, so `model_schema.approvals.EVIDENCE_FLOOR` has no entry for it and
`ApprovalPolicy.below_floor()` returns nothing: a workspace that edits `metric_certificate`
out of its own `06` §4.2 entry is accepted, and `metrics._require_evidence` then has nothing
to require. `custom_objective` **is** in the floor and is protected; the parallel this slice
claimed everywhere else does not hold here. What protects a metric today is the lifecycle,
not the policy — submission requires `certified`, only `record_certificate` sets it, it sets
it beside a `certificate_id`, and the `certified_metric_has_a_certificate` CHECK refuses the
pair coming apart. The gap is that the *policy reader* is told a floor exists where none
does. ~~**Owner: WK-661**, as a `06` §3.3 spec change plus the matching `EVIDENCE_FLOOR` entry,
in that order — adding the entry alone would put the code above its own specification. Not
folded into the fix wave that found it, because a new §3.3 evidence row is a governance
change rather than a defect fix.~~ **Closed 2026-08-22 by the audit-remediation slice, in
exactly that order.** `06` §3.3 gained the Custom Metric row — "Metric Certificate with
`overall ≠ failed`" (`02` FR-154/157/162) — with a dated note recording that **§3.3 was
the side that was wrong**: the evidence was decided on 2026-08-20 when §4.2's
`DEFAULT_POLICY` gained the entry, and the floor that entry sits on was never written down.
Then `EVIDENCE_FLOOR` gained `"custom_metric": ("metric_certificate",)`, and FR-364 was
amended for the floor it now carries. Proved by `test_the_metric_floor_is_exactly_what_is_checkable`
— the entry is a *complete* projection of the §3.3 row, leaving none of the uncheckable
remainder `model_comparison_if_predecessor` is — and by the negative case this entry
described but nothing tested: an edited policy dropping `metric_certificate` now reports
`below_floor() == {"custom_metric": ("metric_certificate",)}` instead of nothing, and
`set_policy` refuses it. **The same pass found a second false premise and corrected it
rather than leaving it standing**: FR-364's `peril_structure` sentence rested on "an
artifact type with no §3.3 row", and §3.3 has carried a Peril Structure row since
2026-08-14 — four days *before* FR-364 was written. The empty floor survives on a reason
the original did not give, with **owner WK-677**. `metrics._require_evidence`'s docstring
asserted the protection existed until 2026-08-20, named the gap from then until 2026-08-22,
and now records the closure with both earlier states kept.

**LightGBM silently drops a declared builtin `eval_metric` when early stopping targets a
Custom Metric — raised as `OQ-593`, not resolved.** Found in the same final review,
immediately before merge. Tested and named in FR-160's 2026-08-20 amendment, but
whether a documented drop satisfies FR-159's "honoured" is undecided. **Owner: WK-661**,
alongside the `06` §3.3 / `EVIDENCE_FLOOR` gap above. *(Decided 2026-08-21: the drop is
recorded on the fit — FR-161; owner WK-661 stands.)*

#### WK-661 slice — regularisation and cross-validation, 2026-08-21

The twenty-third slice, 2026-08-21 (PR #124). FR-112 and FR-182 were two of the
three requirements the 2026-08-19 outstanding-work pass found with **no verdict anywhere** —
unevidenced and unspoken for in every slice record, the one option `CLAUDE.md` §13 rule 1
does not allow. They were paired before they were built, by a verdict on file rather than by
convenience: `select_by: cv` lives inside the penalty path, so cross-validation without
regularisation would have had nothing to select over. **The schema was ahead of the code** —
`GlmSpec` had carried `alpha` and `l1_ratio` since Phase 0 and `cv_folds` was declared and
read by nothing — which is the state FR-207's staged contract exists to make visible
rather than to permit indefinitely.

| Delivered | Evidence |
|---|---|
| The documented penalty path (FR-112) | `GlmSpec.select_by` (`fixed` default, or `cv`) and `GlmSpec.cv`; `_fit_cv_path` scans the elastic-net path into `glum` with `l1_ratio` held fixed across every point |
| Declared fold construction, not an implicit split (FR-182) | `pricing_core.data.splits.assign_folds` generalises `01` FR-73's two-part cutoff to K folds: `random` reuses the same seeded draw, `temporal` cuts the sorted order into contiguous equal-count blocks, `grouped_by_key` keeps a key's groups whole across folds |
| One seed, not two | Fold assignment is reproducible from `ModelSpecCommon.seed` — the seed the spec already versions into `spec_hash`. `GlmCvSpec` carries none of its own, deliberately: a second field is a second thing that can disagree with the first |
| Per-fold metrics **and their dispersion**, not the mean alone | `Diagnostics.cross_validation` persists the whole scanned path and the selected alpha's per-fold spread. A CV mean with no dispersion beside it says a model was selected and not how close the race was |
| The empty fold is refused by name | `GLM_CV_FOLD_EMPTY`, registered and declared in `02` §5.1 in the same commit — the skew a fold count chosen against the whole book does not guarantee against, per fold. A fold cannot be scored, or trained, on nothing |
| `spec_hash` moved with the fields | `SPEC_HASH_VERSION` 5 → 6 (FR-206); every `v5:` digest is stale and findable |
| Evidenced, not asserted | **39 new tests** — FR-182 ×27, FR-112 ×11, FR-170 ×1, FR-197 ×1, across three new test files, plus a CV-selected model fitted **through the real Job** recording its fold dispersion |
| Contracts regenerated | `openapi/generated.json` and three schemas (FR-451) |

**Two spec interactions the code found, both resolved by dated amendment in `02` rather
than decided in the code and left unwritten** (§0). **K-fold `temporal` was undefined** —
neither FR-182 nor `01` FR-73 said what it means, FR-73 defining only a
two-part cutoff; resolved as contiguous time-ordered blocks. **FR-197's
`uncertainty_basis` predates `select_by == "cv"`**: under CV selection `GlmSpec.alpha` is
pinned to `0.0` and the effective penalty comes from `cv.alphas`, so the basis cannot be
read off the spec's alpha at all; resolved as unconditionally naive/penalised for every
`select_by == "cv"` fit. Conservative rather than exact, for a stated reason — the grid
starts at zero and moves away from it, so a fit landing back on exactly zero is the rare
point and the cautious label costs a display caveat rather than a wrong number.

**FR-207's staged contract, eighth entry.** `select_by` and `cv` go live under a
**nested** `cv: GlmCvSpec` block rather than the flat `select_by`/`cv_folds` fields the
2026-08-17 decision named, mirroring `GbmSpec`'s nested `early_stopping`. FR-207's row
and §4.4's note were amended to say the shape that was **built**, not the shape that was
predicted, and the fields leave the absent-entirely list by amendment rather than by being
quietly dropped from it.

**Three defects the slice's own final review found, all in validators that looked
complete.** `GlmCvSpec.alphas` let **NaN** through — `nan < 0` is `False` and `nan != nan`
defeats a distinctness check, so a path `glum` could never fit was storable.
`CrossValidationDiagnostics` checked fold coverage with **set equality**, so metrics for
folds `0,0,1,2` under `folds=3` passed and double-counted fold 0 in the dispersion. And
three `SplitError` branches had no negative test; they do now, with a note that Polars'
`arg_sort` puts null `time_column` rows in fold 0 — deliberate and deterministic, written
down so the next reader does not rediscover it as a bug.

**A §5.2 interface comment lagged the field it describes**, and was corrected in the slice:
`fit_glm`'s documented return read `.result, .covariance_bytes` after `GlmFit` gained `cv`,
so a caller copying the signature off the page would have missed the cross-validation
diagnostics the fit carries. The same shape as every §5.1 divergence this workstream has
found — the code moved and the page a caller copies from did not.

**Not delivered, with owners.** **No new HTTP endpoint** — the existing diagnostics route
surfaces `cross_validation`, and a second route for a field on an artifact already served
would have nothing of its own to say. **No frontend**: the CV screen is **WK-664**'s.
FR-197's exact answer for penalised inference — a bootstrap or penalty-aware sandwich
over ~200 refits, a Job rather than a fit-time step — remains owned by the first consumer
that renders or cites a coefficient interval on a penalised fit; CV selection does not
create one.

**Gate: not reconstructable, and deliberately not invented.** This record was written on
2026-08-22 from the merged commit, and the branch's ruff / mypy / test-count figures were
never written down at merge time. What is verifiable from the merged diff is stated above.
§13 rule 5 asks for a measurement or the reason a measurement is the wrong instrument; a
gate figure recalled four days later is neither.

**Recorded late, and that is the process finding.** PR #124 struck its row in the
outstanding-work table above and wrote no slice record; this one was written 2026-08-22 from
the merged diff. **It is the third such omission in WK-661** — the prediction slice (PR #102) is
the first, the GLM approximation (PR #120) the second, and the Tweedie slice below is the
fourth, from the same day and the same cause. The cause is now visible enough to name: a
slice whose entry in this file is a row it can *strike* treats the strike as the
bookkeeping and stops, while a slice with no such row writes a record. A row's strike says a
slice happened; only a record says what it found — and this one found three validator
defects and two undefined spec semantics the strike does not mention.

#### WK-661 slice — Tweedie power by profile likelihood, 2026-08-21

The twenty-fourth slice, 2026-08-21 (PR #125), and the one where the design on file turned
out to be wrong and building it is what proved so. FR-114 is the last of the three
requirements the 2026-08-19 pass found with no verdict anywhere. Before this slice `GlmSpec`
only **validated** that a supplied Tweedie power lay between the two families it spans: `p`
was a constant an actuary typed, defaulting to 1.5, with no uncertainty attached and nothing
recording where it came from — `CLAUDE.md` §7's rule about surfacing uncertainty with every
estimate, broken by an estimate never presented as one.

| Delivered | Evidence |
|---|---|
| The grid, opt-in | `GlmSpec.tweedie` carrying `p_grid`; `null` under a fixed-power spec, so existing specs are unchanged. Default is a ten-point scan strictly inside `(1, 2)`; at least two points, strictly increasing. One point would be a fixed fit wearing a scan's clothes |
| A **true** profile likelihood, not a deviance argmin | `estimated_power` is the argmax of the Tweedie log-likelihood over `p_grid` — `μ̂(p)` the GLM refit at each scanned power, `φ̂(p)` the mean-deviance dispersion, and the Tweedie series density of Dunn and Smyth (2005) |
| The density is its own module, with its own tests | `pricing_core.modelling.tweedie_density` — the series density in log space, matching the R `tweedie` package's `dtweedie_series` |
| The estimate carries its own uncertainty | 95 % profile-likelihood interval, linearly interpolated between scanned points, persisted with the profile curve itself |
| It lives on the fit, not on Diagnostics | `TweediePowerFit` rides on `GlmFitResult` because the estimate feeds every downstream deviance recomputation, and all of those receive the fit as their first argument. On Diagnostics it would be a number beside the fit rather than a number the fit is made of |
| Never silently baked in as a constant — the defect the row named | `_power_of`: diagnostics, the type-III sweep and `backtest_model` all read `p` from the fit result instead of the spec's 1.5 default, and the type-III refits hold it fixed at the estimate |
| A maximum at a scan edge is refused, never reported | `GLM_TWEEDIE_POWER_GRID_EDGE`, registered and declared in the same commit. An argmax at either boundary reports the scan's edge as the answer, which is a statement about the grid dressed as a statement about the book |
| Three mutual exclusions refused by name | A non-Tweedie family; a fixed `family_params.power` supplied beside the grid; and estimation together with `select_by == "cv"`, since the profile is penalty-dependent and the two selections would each be conditioning on the other's answer |
| `spec_hash` moved with the field | `SPEC_HASH_VERSION` 6 → 7 (FR-206): two specs differing only in `tweedie.p_grid` sharing a digest would hand the second caller the first caller's model under FR-204 |
| Evidenced, not asserted | **25 new tests, every one marked FR-114**, across three files, plus an estimated-`p` model fitted **through the unchanged fit Job**, its persisted result carrying the estimate, the interval and the curve |

**The design on file was wrong, and the code is what found it — §0 in its literal case.**
The planning-time design, written into this file's outstanding-work row and into the slice's
own opening tasks, was **deviance argmin**: scan `p`, refit, take the power minimising the
deviance. It is not a likelihood profile for Tweedie — the deviance carries a saturated term
and a `p`-dependent normaliser, and neither cancels out of the argmin. **Measured, not
argued**: at the slice's pinned seeds the deviance-argmin estimator came in at roughly
*truth + 0.25* and hit the grid edge at every seed. The estimator was replaced by the true
profile log-likelihood, and `02` §4.4's FR-114 amendment records **which side was wrong
and why**, naming the replaced design rather than editing it away. Had the code been quietly
bent to the deviance design instead, the platform would have shipped a biased power estimate
with a confident-looking interval around it.

**A fixture defect the same measurement exposed.** The recovery test's data generator drew
the compound representation with claim shape 1, which is exact **only at p = 1.5** — so the
data was not Tweedie at the other scanned powers and the test was measuring the generator as
much as the estimator. It now draws the shape implied by the stated power, so the data is
Tweedie at every one, with bit-identical draws at the pinned seed. The test asserts the
profile curve is finite, that the argmax **is** the reported estimate, and that the interval
brackets the truth — three properties, where a single point estimate compared to a target
would have passed under the biased estimator too.

**Not delivered, with owners.** **No new HTTP endpoint** — `tweedie` rides on the fit result
the existing model read already serves. **No frontend**: nothing renders the profile curve
or the interval, and those views are **WK-664**'s. **Estimation × CV selection is refused, not
built** — recorded on FR-207's staged contract as a named refusal rather than a gap,
and owned by whoever first needs a penalised Tweedie fit with an estimated power, which
nothing does today.

**Gate: not reconstructable, and deliberately not invented** — as with the record above.
Verifiable from the merged diff and stated here: 25 tests all marked FR-114, three
regenerated contracts, `SPEC_HASH_VERSION` 7, and `GLM_TWEEDIE_POWER_GRID_EDGE` registered
and declared. The one number this slice *did* measure is in the record where it belongs —
the deviance-argmin bias, which is the finding.

**Recorded late, and that is the process finding.** PR #125 struck its row in the
outstanding-work table above and wrote no slice record; this one was written 2026-08-22 from
the merged diff. **It is the fourth such omission in WK-661** — after PRs #102, #120 and #124,
the last of which merged three hours before this one and failed the same way for the same
reason. **This is the omission that costs the most**, and it is why the pattern is worth
naming rather than re-apologising for: the struck row says "DELIVERED 2026-08-21" and
nothing more, while the thing this slice actually found — that the design on file produced a
measurably biased estimator, and that the fixture built to check it was wrong in the same
direction — existed for four days only inside `02`'s amendment and a squashed commit
message.

#### WK-661 slice — offset from another model, and a scaffold field that was read by nothing, 2026-08-21

The twenty-fifth slice, spanning 2026-08-21. FR-116 gives a GLM spec an
offset from another model — the referenced fitted GLM's linear predictor on the training
data, enabling residual modelling and "fit on top of the current rating structure" — and
the slice exists around a finding with the custom-metrics shape: `OffsetSpec`'s Phase-0
scaffold `model_ref: str` had been declared and read by nothing, while `fit_glm` passed
`kind="model"` silently with no offset at all. A caller could declare an offset from
another model and be told nothing was wrong while none was ever applied. FR-116 as
amended 2026-08-21 now requires it honoured — the field live, the ref resolved, the fit
offset.

| Delivered | Evidence |
|---|---|
| `offset_model_ref` on `OffsetSpec`, and the named refusals | `OffsetSpec.offset_model_ref: ModelRef \| None` — the canonical `model:slug@version` string (ID-3), the pattern admitting `model:` refs and nothing else; validators require `kind == "model"` ⟺ ref set; `GbmSpec` refuses `kind="model"` by name (GLM specs only, FR-116 as amended); `GlmFitResult.offset_model_ref` records the resolved pinned ref — what was actually constructed is recorded on the fit result (FR-126's rule, applied to GLM) |
| `SPEC_HASH_VERSION` 7 → 8 in the same commit | `backend/src/app/platform/modelling.py` — the ref joins the canonicalised spec payload, so FR-204's dedup must not match a fit offset against another model's structure to one with no offset (FR-206) |
| pricing-core takes the resolved array — required, never silent | `model_offset` threaded through `fit_glm`, `linear_predictor`, `predict_glm`, `predict_glm_interval`, `score_fitted`, `compute_diagnostics` and `backtest_model`; every entry point that reaches a `kind="model"` spec without the array raises `MODEL_OFFSET_MISSING`, with length and finiteness validated — pricing-core never resolves the ref (ADR-703), so the backend supplies η and pricing-core refuses to fit without it |
| The type-III reduced fit keeps the offset | The drop-one-term refits inside `_type_iii` pass the same `train` array; before the fix the pre-existing `except GlmFitError: continue` swallowed `MODEL_OFFSET_MISSING` and a model-offset fit with ≥ 2 factors got a **silently empty** type-III table — `test_type_iii_reduced_fits_keep_the_offset` pins presence for both terms and the insignificance of the factor whose effect lives inside the offset |
| The backend resolves the ref | `OffsetModelSource` + `resolve_offset_model` in `platform/modelling.py` (modelled on `_quantile_crossing` and `_refuse_mismatched_approximation`): the pinned row's spec, fit result, factors, bandings and groupings; refusals by name — not a model, not fitted, not a GLM, or link-mismatched (`MODEL_OFFSET_REF_INVALID`), missing row (`NOT_FOUND`) |
| Fit, prediction and backtest wired | `_fit` and `_backtest` in `model_handlers.py` resolve in `load()`, compute η on the worker thread and pass it to `fit_glm`/`compute_diagnostics`/`backtest_model`; `_score_glm` resolves per request and honours the offset in both `predict_glm` and `predict_glm_interval` |
| Spec validation resolves the ref before a Job is queued | `SpecProblemKind.MODEL_OFFSET_UNRESOLVABLE`, raised by `validate_spec` for a ref that names nothing, an unfitted model, a non-GLM or a link mismatch (WF-698 D2's rule applied to offsets-from-model) |
| The code registered and catalogued in one commit | `MODEL_OFFSET_REF_INVALID` added to `errors.py`'s `MODELLING_ERROR_CODES` and `02` §5.1's backtick catalogue in the same commit as its first raise, with the dated blockquote note; `MODEL_OFFSET_MISSING`'s note gained a dated addendum for its fit-side uses |
| The spec amendment and the question it raised | FR-116 amended 2026-08-21 (the ref is `model:slug@version`, GLM-to-GLM v1, what is refused by name); §4.4's `offset_model_ref` block declared; OQ-594 recorded in `open-questions.md` and mirrored in `02` §10; this closure moves the field live on FR-207's staged contract as the ninth live entry |

**The §0 divergence, resolved.** The code scaffold's `model_ref` was the outlier — the
spec's FR-116 text and the hand-authored `docs/contracts/schemas/model-spec.schema.json`
have always named and typed the field `offset_model_ref` as an artifact-ref string, and the
scaffold field was read by nothing. Spec and contract agreed, and the code followed them: a
rename with the artifact-ref pattern, not a new field. And today's behaviour was a defect,
not an absence: `fit_glm` passed `kind="model"` silently with `offset = None`, fitting as
though no offset were declared — the silent-ignore defect is replaced by the implemented
path plus named refusals, `MODEL_OFFSET_MISSING` at every unwired pricing-core entry point,
`MODEL_OFFSET_REF_INVALID` at resolution, `MODEL_OFFSET_UNRESOLVABLE` at validation, and
GBM's accidental column-refusal replaced by the schema's deliberate one.

**Delivered on `worktree-offset-model` in nine commits** — `e3f6610` (the FR-116
amendment and OQ-594), `c37c717` (the schema field, refusals and `SPEC_HASH_VERSION`
8), `ab17018`, `af8f5c8` and `e781d8b` (pricing-core fit, scoring, diagnostics, backtest
and the type-III fix), `cd805e2` (the fit job), `6f9c740` (prediction), `c136440`
(backtest), `5b6ef87` (spec validation) — each tagged FR-116.

**Not delivered, with owners.** GBM/EBM referenced models and `GbmSpec`-declared offsets
stay refused by name — OQ-594 records the widening options, recommendation (a) then
(c) *(decided 2026-08-21: (a) then (c) — FR-117)*; the peril-reconciliation scoring
path is declared-and-refused (`MODEL_OFFSET_MISSING`)
until WK-661 wires the resolver there; EBM as a model type is FR-140's separate slice;
FR-115's fit-error surfacing is delivered: markers at `test_glm.py:134,:429` and `test_spec_hash.py:99,:114`, `GLM_SEPARATION_DETECTED` registered and declared — the 'remains unbuilt' lines were stale. The remainder — a bare non-`LinAlgError` `ValueError` from glum still reaches the job unwrapped — is recorded 2026-08-21 as unbuilt, owner WK-661; `02` §5.3's model spec builder
is **WK-664**'s, unchanged by this slice.

**Gate, both halves, run locally.** ruff 0 · mypy --strict 0 (130 source files) ·
`lint-imports` 0 (3 contracts kept) · **1547 python tests** · audit-docs 0 —
**489 requirements** across 8 specs, **74 open questions** all mirrored, **134 error
codes** ownership-exclusive (was 133) · req-coverage **239 of 489 marked, 48.9 %** ·
`generate-contracts.py --check` 0, **23 generated contracts match** · frontend:
`install --frozen-lockfile` 0, `generate:api` 0, lint 0, type-check 0,
**131 vitest tests**, build 0.

#### WK-661 slice — EBM models via interpret-core, 2026-08-21

The twenty-sixth slice, spanning 2026-08-21 → 08-22. FR-140 gives the platform its
fourth Model type: `ebm`, fitted by `interpret-core==0.7.8` and transparent by
construction — the term shape functions ARE the model, so they are exported verbatim as
additive lookup tables (ADR-705: fit results are data, never pickles), and the
transparency artifact is built from that export with no approximation, no surrogate and
no booster blob. One requirement, one model type, pin exact: the `interpret` metapackage
would pull notebooks and visualisation extras, so only `interpret-core` is installed
(~115 MB incremental; the workspace's sklearn 1.9.0 satisfies its requirement).

| Delivered | Evidence |
|---|---|
| `EbmSpec`/`EbmFitResult`, and the verbatim export | `EbmSpec` (`objective` `rmse`/`mae`, `interactions` 0–1, `max_bins` a power of two in [16, 32768], `max_rounds` 50000, `monotone_constraints` map); `fit_ebm` exports interpret's additive lookups verbatim — term scores and bin weights in the library's own slot layout (numeric `len(cuts)+3`, categorical `len(levels)+2`, the 1-based level dict), `feature_order` and the index rule scoring uses; `fit_ebm` honours `spec.weight.kind == "column"` via `sample_weight` and draws `random_state=spec.seed` |
| The transparency artifact from the export, no approximation | `build_ebm_shape_functions` serialises the fit's own tables verbatim into `terms_blob`; `fidelity_statement` exact-by-construction prose; `monotonicity_verified` read from the exported tables in the declared directions; no surrogate reserved — FR-132/136/139 |
| Universal diagnostics through the shared partition | `compute_ebm_diagnostics` reuses `_partition` with `family="gaussian"` (FR-171's "all model types" taken literally); complexity is the total real bins across terms; no eval curve or importances — an EBM's dependence structure IS the exported tables, and duplicating it as a diagnostic would be a second statement of one fact (FR-170/171/183/184/185) |
| Scoring from the tables alone | `predict_ebm` scores `intercept + Σ term scores` from the exported lookups — no estimator and no fitting-stack import, and `test_scoring_without_the_fitting_stack.py` gains `interpret` to its blocked set (FR-140, ADR-705, NFR-535) |
| `spec_hash` v9 | `SPEC_HASH_VERSION` moves `8 → 9` in the same commit as the EBM fields joining the payload (FR-206); the stale-digest LIKE clause names the stale version (`v8`), corrected from the plan's incoherent `'v9:%'` — every historical entry names the version it finds |
| Four plan-defect corrections, each with a dated note (2026-08-21) | The plan's interpret-internals facts were spike-unverified; the backstop caught each as prescribed, never a weakened test: (1) `feature_types` is `"nominal"`, not `"categorical"` — the banding `levels` are passed verbatim; (2) `monotone_constraints` is a positional int list, not the plan's `f"feature {i}"` keyed-dict convention (the plan's own Self-Review flagged it unverified); (3) `best_iteration_` is a 2-D `[stage, bag]` array — read via `np.ravel(...)[0]`; (4) the plan's own test direction was backwards (`<= 1e-9` asserted non-increasing for a +1 constraint) → `>= -1e-9`, tolerance untouched |
| The spec note the code disproved, amended in the same commit | The §5.1 blockquote claimed `interpret` raises a bare `ValueError` on a nominal constraint; pinned 0.7.8 silently zeroes the term — the pre-check is the whole refusal and the message says the true mechanism (amended 2026-08-21, the fit task; CLAUDE.md §0) |
| A second error code the plan never foresaw | `EBM_MONOTONE_CONSTRAINT_UNKNOWN`: a transparency-time refusal — a constraint naming a feature the fitted tables do not contain cannot be checked, and reporting `True`/`False` would fabricate a verdict. Registered in `MODELLING_ERROR_CODES` and declared in §5.1's catalogue with a dated blockquote (2026-08-22) in the same commit; the plan's "only one new code" premise is superseded by the design its own transparency task chose |
| Backend boundary refusals — the plan's new task 2b | Widening the `ModelSpec`/`FitResult` union broke the whole-repo mypy gate at three backend sites the plan's Task 2 verification form could not see (it never runs whole-repo mypy). Two became named refusals that double as the mypy narrowing: `prediction.py` refuses an EBM predict request with `MODEL_TYPE_UNSUPPORTED` (dated note, the real arm was attributed to WK-664 here and is **W32-4's**; built 2026-08-23 (W32-4, the EBM predict arm), which narrows this refusal to a spec/fit-result mismatch rather than deleting it), and `_resolve_candidate` refuses an EBM row with `MODELS_NOT_COMPARABLE` — WF-698 E1 is GLM-vs-GBM surrogate validation, and an EBM has no surrogate. The third site was fixed by Task 11's planned dispatch restructure |
| The early `EbmSpec`/`EbmFitResult` exports | The model-schema package-root exports landed ahead of Task 5 — `EbmSpec` with Task 2b and `EbmFitResult` with Task 3, one alphabetical import line each, because the boundary refusals' imports needed them; Task 5 completed the remaining names |
| Objectives refused by name, not extended | EBM's vocabulary is `rmse`/`mae` only (identity link); §7's families and binomial `log_loss` are **declared-and-refused by name** as `objective` values under FR-207, with the dated note in §4.4; `interactions=2` (triples) is **declared-and-unbuilt** (a triple grid at even 64 bins is 262k cells — the JSONB envelope cannot bound cubic growth); custom objectives do not apply to EBM — `ObjectiveBackend` has no EBM member by design |
| The one authored-vs-generated divergence, hand-aligned | The comparison test compares type names and enum values only — constraint-level drift (`minLength`/`required`/`additionalProperties`) has **no mechanical guard** (Task 13's open item, owner WK-661). The slice found and hand-aligned exactly one divergence: `transparency-artifact.schema.json`'s hand-authored `ebm_shape_functions` block declared `terms_blob` with no `minLength` against the type's `min_length=1` — amended to `minLength: 1` with a dated note (a hand edit to a hand-authored file; regeneration never touches it) |
| Spec-hash counter coherence (Task 1's deferred minor) | §4.4's blockquotes show `spec_hash` moving `v4 → v5` (the approximation) beside `8 → 9` (the EBM fields); the vN lineage between v5 and v8 — v6 with regularisation/CV (FR-112/182) and v7 with Tweedie power (FR-114) — went unrecorded in the spec. Recorded here as a coherence follow-up, owner WK-661 |

**Recorded, not built, with owners.** `fit_gbm` ignores `spec.weight` — verified, no
reference in `gbm.py`; dated note 2026-08-21, owner WK-661. *(Corrected 2026-08-22: the note
was never written. `git log -S "dated note 2026-08-21"` shows the phrase entering the
repository only in `c2c54a6`, and only in this file — so FR-207's obligation was
recorded as discharged while nothing in `02-modelling.md` said the field was unbuilt. The
gap is closed by building it rather than by writing the note; FR-111 carries the
amendment.)* **FR-161** (a declared eval
metric a backend could not evaluate is recorded on the fit) — the verdict is recorded here:
owned by WK-661, due before WK-661 closes; explicitly NOT this (EBM) slice. *(Delivered 2026-08-22
by the slice below, as this record scheduled it.)* **NFR-482**
recorded as-is — the export/import round-trip NFR remains unevidenced for the suite; this
slice's EBM round-trip tests are evidence for the EBM artifact only, and the record says
exactly that rather than claiming closure. The `06` §3.3 custom-metric evidence-row gap and
OQ-639 remain as they were — unchanged by this slice. No frontend view renders an EBM
(WK-664 owns any that will); no alembic revision — `ModelRow.spec`/`fit_result` and
`TransparencyArtifactRow.payload` are JSONB columns, unchanged; the slice is API-only.

**Gate, both halves, run locally.** ruff 0 · mypy --strict 0 (131 source files) ·
`lint-imports` 0 (3 contracts kept) · **1609 python tests** · audit-docs 0 —
**494 requirements** across 8 specs, **74 open questions** all mirrored, **136 error
codes** ownership-exclusive (was 134) · req-coverage **241 of 494 marked, 48.8 %** —
FR-173 joins the marked set with the marker backfill that closes this record ·
`generate-contracts.py --check` 0, **23 generated contracts match** · frontend untouched
(WK-664 owns any view that renders an EBM — the slice is API-only).

#### WK-661 slice — GBM declared weights and the dropped eval metric record, 2026-08-22

The twenty-seventh slice, 2026-08-22. Two defects sharing one shape — FR-159's own
words for the class: *a spec accepted, silently ignored, and reported to the caller as
configured*. `spec.weight` was declared on `ModelSpecCommon`, honoured by `fit_glm`,
`fit_ebm` and `compute_diagnostics`, and read by neither GBM backend; and a builtin eval
metric suppressed so it could not hijack a custom stopping target was dropped with nothing
on the artifact to say so. Both are closed in the fit path; no backend handler changed.

| Delivered | Evidence |
|---|---|
| `spec.weight` reaches both GBM backends | `_weights(data, weight)` mirrors `_offset`; `fit_gbm` resolves it once for the training frame and once for the holdout, and the `valid` tuple widens to carry it — a curve whose train half is weighted and whose holdout half is not would plot two quantities on one axis. `xgb.DMatrix(weight=)` via the `matrix()` closure, `lgb.Dataset(weight=)` on both sets. A missing column raises Polars' own `ColumnNotFoundError`, exactly as `fit_glm` has always done — no new error code, because one malformed spec must not be answered differently by model type (FR-111/184) |
| The actuarial measurement that names the defect | `test_a_gamma_severity_fit_weighted_by_claim_count_predicts_the_weighted_mean` — a closed-form severity book whose unweighted mean is **5.0** and whose claim-count-weighted mean is **1.8**. Both backends fitted **5.0000** before and predict **1.8004** after. `test_non_uniform_weights_change_the_fit` pins that a non-uniform column moves the booster at all; `test_a_weight_column_of_ones_fits_identically_to_no_weight` is the control proving the plumbing is inert when the spec asks for nothing |
| The custom objective and custom metric receive the declared weights | `make_xgb_objective`/`make_lgb_objective` and both `_custom_feval` helpers already read `get_weight()` and fell back to `np.ones_like(y)`; nothing had ever set it, so **every custom objective and custom eval metric fitted before this date was uniform-weighted**. `test_a_custom_objective_receives_the_declared_weights` and `test_a_custom_eval_metric_receives_the_declared_weights` record the array the backend hands in and compare it to the column. `make_lgb_objective`'s docstring asserted "nothing is dropped", false from the day it was written; corrected with a dated note (FR-111/146/155) |
| `GbmFitResult.dropped_eval_metrics` (FR-161) | `DroppedEvalMetric` — `name` as `eval_metrics` spelled it, `reason` a closed set whose one member is `builtin_evaluated_before_custom_stopping_metric`. `_fit_lightgbm` populates it from the same `_builtin_eval_metric_names` list the non-stopping arm passes to `params["metric"]`; `_fit_xgboost` returns empty because it evaluates both lists. Negative tests first: a free-text reason and a twice-named metric are both refused. `test_lightgbm_records_the_builtin_eval_metric_it_dropped` pins the record, `test_a_fit_that_evaluated_everything_drops_nothing` the control, and the pre-existing `test_lightgbm_drops_a_builtin_eval_metric_rather_than_stop_on_it` is byte-unchanged — the drop behaviour did not move, only its visibility |
| `spec_hash` `v9` to `v10`, and the lineage it completes | **The first bump for an interpretation change rather than a payload one.** `weight` was always in the digest; what changed is that `fit_gbm` began honouring it, so a `v9:` digest over a weighted GBM spec names a fit this build produces differently and FR-204's dedup would hand the next caller the unweighted one. Every `v9:` digest is stale and findable with `LIKE 'v9:%'` — including an unweighted GLM's, which the change cannot have affected; that over-invalidation is accepted because a targeted one has no mechanism here. `02` §4.4's lineage also catches up on `v5 → v6`, `v6 → v7` and `v7 → v8`, which it had skipped while the backend comment block carried them (FR-206) |
| No new shape hand-written, no handler edit | `model_handlers.py` reads `fit.result` by attribute and `record_fit` persists the whole result, so the field rides along — 22 backend gbm/handler tests pass untouched. Contracts regenerated: `DroppedEvalMetric` with a single-member `const` reason, `dropped_eval_metrics` defaulting to `[]` so every artifact written before this date still validates (FR-451) |

**Recorded, not built, with owners.** The **eleven unevidenced `NFR-MODEL` requirements**
(NFR-475/476/477/479/480/482/483/484/485/486/478 — performance budgets, the export/import round-trip,
and determinism at suite scale) are unowned by this slice and remain the largest single
block of MODEL scope without evidence; NFR is 1 of 12 evidenced. **FR-115's
remainder** — a bare non-`LinAlgError` `ValueError` from glum still reaches the job
unwrapped — owner WK-661, unchanged. The **`06` §3.3 custom-metric `EVIDENCE_FLOOR` gap** is
a spec change first and then code, in that order, owner WK-661. **FR-386** unchanged.
**FR-117(c)** stays sequenced behind (a), per the 2026-08-21 decision. The EBM
**`interactions=2` triples** remain declared-and-unbuilt and ~~**no workstream has ever been
named for them** — itself an FR-207 defect rather than merely a deferral, and stated
here as one.~~ **Owner named 2026-08-22 (audit-remediation slice): Phase 1b.** This entry was
right that an unowned residual is a defect and not a deferral, and it is the one item on the
2026-08-22 list that named the problem without applying the same judgment to the four
sibling owners phrased as events nothing schedules — all five now carry a phase or a
workstream. The **constraint-level contract-drift guard** (`minLength`/`required`/
`additionalProperties`) ~~still has no mechanical guard, owner WK-661.~~ **Partly built
2026-08-22.** The audit-remediation slice made the existence test resolve `allOf` and
`if`/`then`, made the type test compare **nullability** across the six MODEL-owned slugs,
taught `_scalar_types` to read `const`, and added a nested-path test — after finding that
the existing checks compared **top-level names only**, which is precisely how
`gbm.quantile_crossing` (FR-199) and `gbm.tree_count` sat absent from the published
contract for months with every test green. Three defects in the checking machinery itself
were fixed on the way, including a `properties.update()` that **deleted** a conditional
branch's real field definitions. What remains uncovered is `minLength`/`additionalProperties`
and `required`-set drift, and **arm-level attribution** — the flattened union cannot tell
which `if`/`then` arm declares a field, so a GLM-only field declared on the GBM arm still
passes. **Owner for the remainder: WK-664**, the first workstream to consume these contracts
from the frontend and therefore the first to be hurt by drift in them. **New finding, recorded
rather than fixed:** `02` §4.8 carries `fit_result` examples for GLM and EBM and **has
never carried one for a GBM**, so there was no example for `dropped_eval_metrics` to join;
FR-161's amendment points readers at the generated contract instead. Writing one is
a spec change larger than this slice and is owned by WK-661. No frontend view renders either
field; no alembic revision — `ModelRow.fit_result` is JSONB and unchanged. *(Fixed 2026-08-22 by the audit-remediation slice: §4.8 now carries a GBM `fit_result` example, validated against `GbmFitResult` rather than hand-written, and naming every field the type declares.)*

**Gate, both halves, run locally.** ruff 0 · mypy --strict 0 (131 source files) ·
`lint-imports` 0 (3 contracts kept) · **1625 python tests** (was 1609) · audit-docs 0 —
**494 requirements** across 8 specs, **74 open questions** all mirrored, **136 error
codes** ownership-exclusive and unchanged, this slice adding none by design ·
req-coverage **242 of 494 marked, 49.0 %** — FR-161 joins the marked set ·
`generate-contracts.py --check` 0, **23 generated contracts match** · frontend:
`install --frozen-lockfile` 0, `generate:api` 0, lint 0, type-check 0,
**131 vitest tests**, build 0. MODEL scope-audit: **108 of 124 evidenced (87 %)**, up from
107 — the five unevidenced `FR`-MODEL requirements that remain are all gated
(FR-MODEL-6, 40, 82, 110, 112).

**Delivered on `worktree-ebm-slice` in fifteen commits** — `1bae625` (the `02`
amendment declaring the EBM arm and its fit/transparency shapes), `328f102` (`EbmSpec`
with the refused-by-name vocabulary), `0a0e83b` (the predict and comparison boundary
refusals), `cc75829` (`EbmFitResult` with the additive tables), `46a2a1e` (the
transparency artifact's EBM block), `bd80fdf` (the package-root exports), `157468e`
(`fit_ebm` via interpret-core, tables exported verbatim), `7acde30` (the shape-functions
blob and `EBM_MONOTONE_CONSTRAINT_UNKNOWN`), `1771254` (scoring from the tables alone),
`e9307c2` (universal diagnostics through the shared partition), `a94b4eb`
(`SPEC_HASH_VERSION` 9 with the EBM fields), `39e19f0` (the backend fit dispatch with
the named constraint refusal), `c2482c5` (the backend transparency artifact through
`model.transparency`), `e45d564` (contracts regenerated with the EBM arm) — each tagged
FR-140; this record and the FR-173 marker backfill close the slice.


#### WK-661 slice — the audit-remediation slice, 2026-08-22

The twenty-eighth slice, and the one that answers a closure audit rather than building a
capability. Six slices, four of them clearing defects the audit found and two clearing the
record itself. **It is not a closure record** — `CLAUDE.md` §13's verdicts are below, but WK-661
closes only when the maintainer accepts them and OQ-572 is decided. **OQ-572 was decided 2026-08-22** — option (a), denominator settled as fit wall-clock — so that half of the condition is discharged; the maintainer's acceptance of the verdicts below is the half that remains.

**The audit's own numbers moved while it was being answered, twice**, which is the first
finding: the requirement count was re-derived at 124 by the verification pass and was **125**
by the time the correction was applied, because this slice had appended FR-118 an hour
earlier. Every number below is re-derived at the moment of writing and carries the command
that produced it.

##### What was built

| Delivered | Evidence |
|---|---|
| `models.diagnostics_id` joins the immutability trigger (`02` R2, `00` FR-4) | Migration `9e4c7b21fa08`. `record_fit` writes the fit result, the pointer and the status in **one `UPDATE`**, checked in the handler rather than assumed, so the guard freezes from the statement that sets it. Proven three ways: the negative test fails at the pre-fix revision; a deliberately *naive* unconditional guard is caught by the positive control; `downgrade -1` restores the exact prior function body |
| Submission resolves the artifact it pins (FR-386) | The suite's **first five FR-386 markers**. Fan-out in the route, mirroring `_carry_to_the_artifact` — DEP-1 satisfied with no registry, because a registry would be a second mechanism for a seam that already had one. Six of twenty types resolve; **an unresolvable type fails closed** with the new `06`-owned `ARTIFACT_TYPE_NOT_RESOLVABLE`, on `07`'s `JOB_HANDLER_NOT_REGISTERED` reasoning. Enforcement proven: removing the resolver gives 8 failures |
| `custom_metric`'s evidence floor (`06` §3.3, FR-363) | The §3.3 row **first**, then `EVIDENCE_FLOOR` — the order the code's own docstring demanded, since the entry alone would put the code above its specification. Three negative tests, each proven to fail without the entry |
| `GLM_FIT_FAILED` (FR-115's remainder) | glum's `ValueError` refusals were escaping raw. Measured against glum 3.4.1 rather than assumed — a response outside the family's domain, a negative or all-zero weight vector, an all-zero response, non-finite input. **Not folded into `GLM_RANK_DEFICIENT`**, whose message names collinear terms — a lie for a non-positive response |
| A handler's `PlatformError` keeps its code (OQ-646, decided (a)) | Marked **FR-403**: this is platform job machinery, not modelling. The `RuntimeError` control **passed before the change too**, which is what makes it a control rather than a second copy of the same assertion |
| Bühlmann–Straub (FR-106) | Built, per OQ-579's 2026-08-15 decision that WK-661 builds *two* methods. The Poisson process-variance identity is what makes it estimable from a one-way summary at all. Degenerate cases **refused by name, never clamped** — FR-118. The refusal test is **inverted, not deleted**, so the record of what was once refused survives |
| The contract half (FR-9, FR-451, FR-206/207) | Six MODEL-owned schemas reconciled, and the **guard tests fixed first** — see below |
| Twelve NFRs measured or given a verdict (`02` §9) | Five measurement blockquotes, each with machine, load average, budget and a met/not-met table |
| `GET /api/v1/models`, and the silent-ignore closed | Three list routes gain `extra="forbid"` query models |

##### The guard tests were the defect, not only the schemas

Fixing the existence test surfaced three defects **in the checking machinery**, none of which
was in the work order:

- `_type_map` did `properties.update(...)`, so the *last* variant naming a field replaced
  every earlier definition — and a conditional refinement is exactly that shape. Following
  `then` therefore **deleted** the real definitions and took the walker from 36 paths to 28.
- `const` was invisible to `_scalar_types`, so a `{"const": …}` branch was typeless.
- `ENVELOPE_FIELDS` was wrong **in both directions**: the literal
  `{id, slug, version, dataset_id}` — three real envelope fields out of fourteen, plus one
  that is not an envelope field at all. It had been hiding `TransparencyArtifact.id`,
  `created_at` and `Diagnostics.id` from a check they should always have failed.

**The broken-input proof earned its keep by finding two dead checks**, including the exact
mechanism by which `gbm.quantile_crossing` (FR-199) and `gbm.tree_count` sat absent from
the published contract for months with every test green: the existence test compared
**top-level names only**, and the type test narrows only when a path stops being shared.

The sharpest single finding: `model.schema.json`'s `fit_result` was one flat block requiring
`converged`, which neither `GbmFitResult` nor `EbmFitResult` has — so **no GBM or EBM fit
could ever have validated against the published contract.**

##### `CLAUDE.md` §13, rule by rule

1. **Scope derived from the specification first.** `scope-audit.py MODEL`: **125 in scope,
   111 evidenced (89 %), 14 without** — and the roadmap's own claim of "seventy-eight
   requirements" was not stale but **never a count of `02`** (it is §6's Phase-1b planning
   estimate, borrowed from a table two pages away; the derived count on the day it was
   written was 85). Endpoints **41 of 41** after `GET /models`; catalogues clean.
2. **Deliverables audited against the definition.** The §5.1 endpoint table matched on all
   40 rows, which is *how the parameters went unexamined* — `--endpoints` compares method and
   path, so a wrong parameter is invisible to it. Checked by hand: `?dataset={slug}` returned
   **200 with every factor in the workspace**, one `{id}` row of 23 was wrong, and §5.2 had
   drifted on nine functions.
3. **Gates green locally, both halves, each exit code read.** ruff 0 · mypy 131 files ·
   lint-imports 3 kept 0 broken · `pytest backend/tests` **774 passed** ·
   `pytest tests/ packages/` **917 passed** · audit-docs all checks · req-coverage 495/248 ·
   `generate-contracts.py --check` 23 match · frontend install, generate:api, type-check,
   lint, **131 tests**, build — all 0.
4. **Enforcement proven on broken input**, every time: the trigger at the pre-fix revision and
   against a deliberately naive guard; the floor entry removed; the resolver removed; nine
   mutated schemas; `tasks.py` reverted to capture the before-output.
5. **NFRs measured, not asserted** — five blockquotes in `02` §9, each with the machine, the
   **load average** (the same proposal measured 8.58 s at load 1.6 and 20.01 s at load 8.4),
   the budget and the shortfall as a percentage.
6. **What was *not* delivered** — the three numbers, below.
7. **Documents updated in the same commit** as the code, including two skills and their index.
8. **Repository clean**: one branch, no tracked build artifacts, the generated frontend client
   still git-ignored.

##### The headline, as three numbers rather than one

`scope-audit.py` counts a requirement as evidenced when *any* test carries its marker, so
"111 of 125" means **declared-or-refused**, not built. The roadmap caught this once on
FR-185 (2026-08-16) and never applied it to the headline. Stated properly:

- **108 built** — implemented and evidenced by a test of the behaviour.
- **3 declared-and-refused-by-name** — FR-189 (`separate_model`, `LOSS_TREATMENT_UNIMPLEMENTED`),
  FR-208 (`spline`/`polynomial`/`offset`/`expression` refused at resolution), and
  FR-207, whose subject *is* the staged contract. **This was five before this slice**:
  FR-115 and FR-106 are now genuinely built.
- **14 unevidenced, each with a verdict** — every one below.

| Requirement | Verdict | Owner |
|---|---|---|
| FR-95 — `expression` factors | Not started | **WK-690**, accepted by the maintainer 2026-08-22 |
| FR-144 — `expression` objectives | Not started | **WK-690** (OQ-573) |
| FR-91 — proxy detection | Not started | **Phase 3 / WK-691** (OQ-581) |
| FR-138 — rebuild reuses stored numbers | **Built 2026-08-22** (WK-661, the closure slice), and the verdict this row carried was false. *(Original verdict, struck rather than overwritten:)* ~~**Delivered but untested** (OQ-589, 2026-08-21)~~ — **it was neither.** The branch FR-138 describes runs *before* `build_glm_approximation` and `compute_diagnostics`; in the handler both ran unconditionally and `should_fit` first appeared after them. A call-counting test on the pre-change code shows **both** running on a rebuild, so the marker this row said was owed would have been a false claim rather than a missing one. The requirement is amended in one clause by building it: the branch **skips** the surrogate's `Diagnostics` compute rather than **loading** it, because the result is consumed only inside the `should_fit` arm and loading it would be a query whose result is discarded — `02` FR-138(ii) | ~~WK-661 — a marker is owed, not a feature~~ **Discharged by WK-661.** Three marks, and the audit found it rather than the Phase-1b measurement its owner clause named |
| FR-117 — offsets-from-model widening | Not started, sequenced | **Phase 1b**, (a) then (c) |
| NFR-475, -10 | **Measured by extrapolation** — 173 s of 600 s, 16.0 GB of 32 GB | The slice with a 16-core worker |
| NFR-476 | **Measured once, growth unmeasured** — 963 s of 1 200 s on an *assumed* linearity | Same |
| NFR-477 | **Measured and breached by all three grouping methods**; the cause is the one-way summary, not Ward | The factor-workbench slice |
| NFR-479 | **Measured and met** since OQ-572 was decided 2026-08-22 — re-scoped off FR-172's block and re-set to 50 % at a named scale; 32.1 % at the worst measured arm | None required |
| NFR-487 — the type-III block | **Measured and breached** at 678 013 × 60: more than 1.61× per tested factor against a 1.0× bound, and the observation is *censored* | **Phase 1b**, with the warm-denominator run the corrected multiples rest on |
| NFR-488 — the GBM block | **Measured and met** — 0.0480 fits per scoring pass against 0.06, 1.25× headroom | None required. The sweep it prices is **no longer uncapped**: OQ-596 decided 2026-08-22, FR-175 bounds the categorical grid to the 20 most-exposed levels — 0.96 of one fit at this measured rate |
| NFR-480, -11 | **Measured and met**, 50× and 380× headroom | None required |
| NFR-482 | **Out of Phase 1 scope — maintainer verdict 2026-08-22**, on plan review 3's question 2(a). Zero export and import paths exist, no row ever named one, and its parent FR-5 carries zero markers. *(Original verdict, kept:)* **Nothing to test** — zero export and import paths exist | **None in Phase 1.** *(Original owner cell, kept:)* **Unassigned**, needs a verdict before it can have a test — which is the absence this verdict removes |
| NFR-478 | **Measured and held** — 0.22 s against 5.22 s | None required |

Nine of the fourteen carry a **recorded measurement** rather than a marker, which §13 rule 1
admits as evidence where a test is the wrong instrument — and says so with the number.

##### Not delivered, and honestly so

- **OQ-572 is decided** (2026-08-22, option (a)). NFR-479 is re-scoped off
  FR-172's block, given the wall-clock denominator in its own text, and re-set to 50 %
  at a named scale; the type-III block is NFR-487 and the GBM block NFR-488.
  **What the decision did not fix is stated rather than closed over**: NFR-487 is
  breached at 678 013 × 60 on a *censored* observation, owned by Phase 1b, and the
  partial-dependence sweep NFR-488 prices is uncapped — OQ-596, **since
  decided** (2026-08-22, FR-175).
- **OQ-571 is decided** (2026-08-22). `offset` is superseded as a Factor type
  (FR-209), the arm kept in the published contract because artifacts are immutable and
  a stored row must stay loadable. `spline` and `polynomial` are **not scheduled and not
  deferred into silence**: both stay declared and refused, gated on FR-210, owned by
  WK-690. The blocker turned out to be neither of them — **no continuous Factor can be rated or
  reviewed today**, including the `identity`-over-numeric one that already resolves, because
  FR-113's relativity table is categorical-only and FR-230 seeds from it. That gap
  appeared in none of the question's four options.
- ~~**`FactorIntent.OFFSET` is a live silent mis-fit**~~ — **decided 2026-08-22 as OQ-595.**
  It was declarable through the API and read by neither fit path, so the factor was fitted
  with a free coefficient. FR-84 supersedes the arm — on a **layer** argument, not the
  duplication one the question recommended, because `OffsetSpec` turns out to be strictly
  *less* expressive than a per-factor intent. Two things the question did not say: `intent` is read in
  exactly **two** places — `rateable()`, which nothing in production calls, and the
  `factor.created` audit event, which **records** the declared intent without gating on it,
  so the platform attested to a property the fit never had — and **`diagnostic` carried the identical
  defect** — refused by FR-85 pending OQ-597 rather than left live beside a
  fixed twin, and **since superseded with it** (2026-08-22, OQ-597, FR-86).
- ~~**`FactorIntent.DIAGNOSTIC` has no stated meaning**~~ — **decided 2026-08-22 as OQ-597**,
  superseded by FR-86 **without the missing meaning ever being supplied**, because both
  readings of it fail: the distinct one — resolved and reported, held out of the linear
  predictor — is a property of *one fit* mis-sited on a Factor reused by every spec that names
  it, and the redundant one is `control` already. The capability is real and is re-sited on the
  Model Spec, where `ModelSpecCommon.factors` is a flat `tuple[UUID, ...]` with no per-factor
  attribute to carry it; gated, owner WK-690. **FR-85's ground for holding the question
  open was wrong against the decision that wrote it** — it measured `diagnostic` against the
  *duplication* argument, which OQ-595 had refuted, rather than the *layer* argument it
  actually decided on. Corrected in place rather than quietly dropped.

- **No GBM could fit an `interaction` Factor at all**, from FR-92 on 2026-08-18 until
  2026-08-22 — **found and fixed here** (FR-176), not merely recorded. `resolve_factors`
  requires a cross's operands to be supplied and gives them no term of their own; `fit_glm`
  builds its design from the resolved *terms* and never sees them, while the GBM encoder
  iterated the *factor list* and raised `KeyError` on the first operand. One line of
  difference between two sibling paths. Behind it sat two more `IndexError` sites in the
  per-factor diagnostics blocks, masked by the first. All three went unseen because **only
  the GLM suite ever fitted a cross** — the GBM suite covers `interaction_constraints`, a
  backend parameter of a similar name and no relation. Found while deciding OQ-596, by
  writing the test the requirement implied rather than by reading the code.
- **A GBM declaring a *sparse* interaction still could not produce diagnostics** — found
  2026-08-22 while deciding OQ-598 (FR-178), one day after FR-176 was believed
  to have cleared that path, and **recorded rather than fixed**: the remedy is WK-690's slice.
  FR-176 skipped the cross and left its **operands** in the list, and both per-factor
  blocks permute and sweep an operand's raw column *alone* — which recombines the operands into
  cells the fit never saw. Measured on a book carrying 3 of 9 cells, which FR-92 says is
  what a real cross looks like: the fit succeeds, the booster's whole feature order is
  `('area_x_fuel',)`, and `compute_gbm_diagnostics` then raises
  `UNSEEN_LEVEL_BEHAVIOUR_REQUIRED` naming all six absent cells. It reaches production —
  `load_factors` returns `ordered + operands` — and dies **uncoded**, the raise landing outside
  the block that maps a `GbmFitError` to a platform error code, which is the same reader-facing
  failure FR-176 recorded for the bare `KeyError` and believed it had removed. **A dense
  fixture hid both defects**: the suite's only cross draws its two sides independently, so every
  cell is populated and no shuffle there can produce an unseen pair. The lesson is a fixture
  one — a cross whose cells are all full is not a cross, and FR-92 said so in writing
  before either defect was built.
- **Two of OQ-598's four options turned out to be one option**, on the half the question
  believed separated them — recorded because the lesson is general to this codebase. "Permute
  the cross's combined column" is not reachable at all: `predict_gbm` re-resolves the cross from
  the operands' **raw** columns on every call, so **every per-factor GBM diagnostic is bounded by
  what can be expressed as a raw-column edit**. A shuffle applied to both operands under one
  shared order permutes the *pairs*, which is exactly a permutation of the resolved cross column
  — measured, the observed cell set is identical before and after and 67.8 % of holdout
  predictions move. The options differ only on the sweep grid, where the cross's observed cells
  score and the Cartesian product of operand levels does not: FR-131 again, the wall that
  killed FR-175's pooled `other` bar four requirements earlier.
- **Two defects in `_sweep` found and deliberately *not* fixed**, recorded rather than
  tuned away because neither is what OQ-596 asked and both change numbers already
  persisted on fitted artifacts. First, `PartialDependencePoint.exposure_share` reports a
  **row-count** share while its name and its docstring say exposure — equal only on a book
  where every row carries the same exposure, which freMTPL2 is not. Second, on a *numeric*
  factor the share is `1/len(points)`, which the ten-quantile grid makes roughly true by
  construction and the grid's own de-duplication can make badly false: a low-cardinality
  numeric column collapses to a few points and each is then reported at an equal share it
  does not hold. The field exists to stop a reader taking a spike over thin exposure for a
  rating signal (`02` §4), so both are worth an owner. Owner: WK-664, with the frontend that
  first plots the curve. Fixed 2026-08-23 (W32-5), under FR-181 — all four sites
  moved together, the level ranking and the omission record's share included, because the
  requirement makes the ranking and the emitted share the same quantity. NFR-488
  re-measured after the fix: 0.0356 fits per scoring pass against the 0.06 budget, at load
  average 0.85, on the 75 000 x 60 x 500 arm the 0.0480 reading was taken on.
- **The sweep runs over a factor's *source column*, not its resolved levels** — found while
  deciding OQ-596, recorded not fixed. `_sweep` holds `source_columns[0]`, so a `grouping`
  factor collapsing a 10 000-code column to eight groups still costs 10 000 scoring passes and
  emits 10 000 points that take eight distinct values, and a `banding` factor gets a curve over
  raw ages rather than over its bands. FR-175's cap bounds this — it is the pathological
  case the cap was written for — but the cap counts *source* levels, so the requirement says so
  rather than implying it counts the factor's own. Owner: WK-664. Fixed 2026-08-23 (W32-5),
  under FR-181 — a banding or grouping factor is now gridded over its resolved levels
  and the source column held at a representative raw value drawn from the frame, so
  `predict_gbm` runs `resolve_factors` exactly as it does in production. Cross factors are
  *not* covered: they still grid over their first source column, because a representative
  value for a cross level is a tuple across several columns. Owner: WK-664, with the frontend
  that first plots a cross factor's curve.
- **Two §14 question-4 spec-accuracy findings against `02`**, both surfaced by OQ-595 and
  neither fixed here, because §14's output is a proposal rather than an edit. §5.3's factor
  workbench Contents column claims "monotonic-direction and intent controls", and the built
  view contains the string `intent` **zero times** — so no actuary can declare a non-`risk`
  intent through the UI at all, which is also why the supersession's blast radius is as small as
  FR-84 states. And `rateable()` is exported from `pricing-core` and absent from §5.2's
  signature table, in the code→spec direction. Owner: WK-664.
- **`02` §5.3's Prediction Contents cell claims a batch input the built view will not have**, a
  §14 question-4 finding, not fixed here because §14's output is a proposal rather than an edit.
  The cell (registered 2026-08-23) reads "input row **or uploaded batch**", and "batch"/"upload"
  appear **once** in all of `02` — in that cell — so no FR carries the capability. The divergence
  is in the UI only: `PredictRows.rows` is required with no default, so the wire shape is always
  a batch, capped at `MAX_PREDICT_ROWS`, and the schema's own description sends a portfolio
  re-rate to `03`'s batch scoring. What is absent is a surface that uploads one. W6b-6b ships the
  single-row generated form ruled 2026-08-25, which is the whole of what the requirement set
  binds — and FR-24 makes a §5.3 Contents cell prose that binds nothing outside its seven
  named carve-outs, of which Prediction is not one. Closing this is therefore a **spec change
  first** (`CLAUDE.md` §0's table), not a slice pickup: either an FR states batch scoring on this
  endpoint, or §5.3 drops the clause. **Owner: maintainer**, as the spec decision — WK-664 closes
  without building it.
- **FR-197's bootstrap owner clause cannot be executed as written**, a §14 question-4
  finding, not fixed here because §14's output is a proposal rather than an edit. The clause
  reads *"Owner: the slice that builds the first of them"* — "them" being the two trigger
  conditions, a surface rendering coefficient intervals on a penalised fit, or an approval
  citing them. `ModelDetailView.vue` was added **2026-08-15** (WK-661, `#71`, `ed3a733`), three days
  *before* the FR was written on 2026-08-18 (`f97bdaf`), and it renders `std_error` and `ci_95`
  for every coefficient with no branch on `alpha`. **Two readings, and the clause fails under
  both.** Read literally — the surface exists, so the trigger has fired — the owner is a slice
  shipped inside **WK-661, closed 2026-08-22**: an owner that can never act, the orphan shape of
  W32-7 and of the batch finding above. Read as reachability — the FR's own ground is
  a conjunction — *"Neither exists today: regularisation has no UI and nothing in §4.11's
  comparison reads the intervals"* — and nothing under `frontend/src` authors `alpha` or `select_by`
  today, so the trigger is unfired — the clause still names a condition that was **already
  satisfied when it was written**, so it cannot be read literally at all. Neither reading is
  adopted here. The finding is that the trigger does not distinguish a surface that *would*
  render a penalised fit's intervals from one that *does*, and a penalised fit at `alpha = 25.0`
  is exercised deliberately (`backend/tests/test_prediction.py:810`,
  `packages/model-schema/tests/test_uncertainty_basis.py:59,112`), so the distinction is not
  academic. Deciding it is a spec change (`CLAUDE.md` §0's table). **Owner: maintainer.**
  *(The `alpha = 25.0` fact is often attributed to `02` §4.8. It is not there — §4.8 is the
  `Model` data contract and carries no fit. That attribution is OQ-586's own wording at
  `open-questions.md:70`, and re-deriving it from §4.8 will return nothing.)*
  - **Addendum, from the WK-661 slice record at `docs/roadmap.md`'s "regularisation and
    cross-validation, 2026-08-21" heading.** That slice (`#124`, `7d4d1b9`) landed after the FR
    and did **not** falsify its ground: it is backend-only — `GlmSpec.select_by`, `_fit_cv_path`,
    `assign_folds`, `Diagnostics.cross_validation` — and touches no file under `frontend/`. It
    did two other things that bear on this finding. It **widened what "penalised" means**,
    pinning `alpha` to `0.0` under `select_by == "cv"` so the basis cannot be read off alpha at
    all, resolved by a dated amendment to FR-197 itself — the blockquote directly below
    that FR's row in `02`'s requirements table. (`02` records decisions as dated prose *below* a
    row, not inside it, so a row-scoped search reports the amendment absent; the same slice's
    other amendment, below FR-187's row, has the identical shape.) And it made that amendment **without
    re-deriving the trigger's ground**, one day before WK-661 closed on 2026-08-22 — so the last
    slice positioned to notice the stale *"Neither exists today"* was the one editing the
    requirement containing it. Then on **2026-08-25**, W6b-1b (`#194`, `dbb4ea0`) mounted
    `CrossValidationPanel` in `DiagnosticsView.vue`. **The ground is a conjunction, and only its
    first limb falls.** Under a display reading, *"regularisation has no UI"* is now **false**,
    and falsified by an open WK-664 slice rather than a closed WK-661 one; the second limb — *"nothing
    in §4.11's comparison reads the intervals"* — is untouched by that panel and not assessed
    here. This does **not** fire the trigger — the panel renders the alpha path, the selected
    alpha and its dispersion, and carries no `std_error` or `ci_95` — but it removes half the
    FR's stated ground from use as evidence that the trigger is unfired, and a conjunction with
    one false limb is false. The reachability reading above survives only by narrowing
    *"no UI"* to *"no **authoring** UI"*, which the FR does not say.
- **`02` §4.6 diverges from the parser in three ways**, the third being that the implemented
  grammar is *wider* in operators and *narrower* in functions, and `where` — the one construct
  §4.6 singles out by name — **does not exist**. Recorded, not resolved: WK-690 owns that grammar.
- **FR-107 is partly unmet** — `source_level_stats` is in the contract and not in the
  Python, so the marker on its test overstates it. Owner: WK-664.
- **NFR-481 is half evidenced** and the roadmap called it evidenced.
- **Five constraint-level contract-drift classes remain unguarded**, plus arm-level
  attribution. Owner: WK-664.

##### Findings the audit did not name

- **FR-364's `peril_structure` justification was false when written** — it says the type
  "has no §3.3 row at all", and §3.3 has carried one since 2026-08-14, *four days earlier*.
  The conclusion survives on a different reason; the unenforced half is WK-677's.
- **`CLAUDE.md` §11's `alembic upgrade head` could never have worked** — the app defaults to
  `gip:gip`, compose provisions `gipricing`. Invisible because the tests carry their own DSN
  and CI sets the variable explicitly: **a defaults mismatch that every automated path routes
  around is invisible to every automated path.**
- **`ReconcileRequest.tolerance` published `anyOf: [number, string]`** — FR-21's audit
  swept fields that *were* `DecimalStr`, so one that should have been was invisible to it.
- **`transparency_artifact_id` is superseded, not owed.** `ix_transparency_model` is not
  unique, so a Model accumulates artifacts and a single back-pointer would be wrong the first
  time a second was written.
- **`00` §5.2 illustrated pagination with `GET /api/v1/models`** — an example route nothing
  implemented, which is why "40 of 40 endpoints" measured the spec against itself.

##### Three process findings

1. **A slice updates the row that describes itself, and every other place counting or judging
   slices is unowned.** That single mechanism produced the stale slice count, the
   buildable-slice counter left at one when every row beneath was struck, and six stale
   verdicts in the diagnostics table. #116 did it; #124 and #125 did it again.
2. **PRs #124 and #125 landed with no slice records** — the 3rd and 4th such omission. Both
   are now written from the merged diffs, each saying in the record that it was written late.
   The Tweedie one is the costliest: its struck row says "DELIVERED" while what it actually
   found — that the design on file produced a *measurably biased* estimator, and that the
   fixture built to check it was wrong in the same direction — lived only in a squashed
   commit message.
3. **This slice committed the defect it was fixing.** FR-118 was appended and left
   unevidenced for two hours, exactly the marker-misattribution that had let Bühlmann–Straub
   read as covered while refused at runtime. Caught by re-deriving with `scope-audit.py`
   *after* editing — not by review, and not by care.

**Gate:** both halves, run locally, each exit code read. Recorded in rule 3 above.

#### WK-692 — the closure proposal's decisions, 2026-08-24

`plans/PL-00776-wk-692-what-closure-needs-and-why-it-cannot-happen-yet.md` raised twelve items across Parts B, C and D and
left every one of them *pending*. They are decided here, by the maintainer on 2026-08-24, and
the proposal's acceptance table is signed to match. **This is a decision record, not a slice
record** — no code was written for it. Where a decision changed a spec, the spec carries its
own dated amendment and this block only says which.

**Part B — the three structural blockers. All three accepted as recommended.** B1: the
Phase 1b table now carries a **WK-692** row. B2: §3's slice boundaries are accepted as executed
for W32-1 … W32-6 and accepted as scoped for W32-7 … W32-10; the five new ids stand. B3: the
five missing slice records are back-filled below.

**Part C — the three §13 verdicts.** Two are settled here; the third is settled at close
because it turns on a fact that does not exist yet.

| Requirement | Verdict | Owner, and why this one |
|---|---|---|
| **FR-158** — the escalated constraint disagreements | **Reassigned** | To **W32-11**, below. The proposal's cell did not discharge the verdict: OQ-600 already names the owner as **WK-692**, so "reassigned" is only meaningful if a *different* owner is named — reassigning it to the workstream that is closing is the same as leaving it. OQ-600's own pairing points at W6b-7, and that is **refused**: W6b-7 is a frontend slice and this is a `model-schema` narrowing, an authored-contract `minItems` 8 → 9, a regeneration and a carve-out removal, with no browser in it. Nothing of FR-158 is built — the three sides still disagree exactly as OQ-600 described |
| `dataset-version` and `validation-report` having no generated side | **Not started**, owner **W32-11** | *Not started* is straightforwardly right — neither slug is generated, neither is in `COMPARED_SLUGS`, and no commit claims otherwise. What the proposal's cell omitted is that it was also **unowned**: the slice map handed these to "W32-1's successor", and that successor — W32-1b — declines them in writing, so the ownership chain terminated. A closure record saying *not started* without naming a new owner would reproduce the exact gap §13 rule 2 exists to close, which is why the verdict carries one. *(Discharged 2026-08-24: **W32-11 delivered both** — `9ab14d6` (#158) gives each slug a generated side and `COMPARED_SLUGS` goes 13 → 15. This verdict was accurate when taken, hours before that merge, and is left standing rather than restated: the closure record takes **delivered**, while this row keeps the record of what was believed at the moment the owner was assigned. Routed by `w6b-executor` via `w6b-lead`, which is the two-independent-readers check working.)* |
| **FR-396**, the fourth obligation — the request-path *trigger* that records a switch | **Settled at close, not here** | The proposal offers *deferred with an owner*, and that is defensible **only** once W32-7 has shipped `record_switch` and the both-chains audit, so that the mechanism exists and only the trigger is missing. On the repository as it stands, `record_switch` appears nowhere outside a plan file, there is no `workspaces` table, and `deps.py`'s `_single_workspace` still refuses a multi-membership caller outright — so **all four** obligations are *not started*, not just the fourth. Writing *deferred* today would report a mechanism the repository does not have. **The rule is decided here and the verdict is instantiated against fact at close**: if W32-7 ships the mechanism *and* files the trigger question as **a new `OQ-PLAT` question, whatever its number**, the fourth obligation is *deferred with an owner*, owner **W6b-11**. *(The number is deliberately not named. `OQ-648` is the highest in use, so the next free is 10, but ids are allocated sequentially at execution and W32-7's plan specifies the question as behaviour without numbering it — a rule pinned to `10` would fail a correct W32-7 on a numbering accident if any other slice files an `OQ-PLAT` first. The verdict is taken against the merged tree.)* — the switcher is the first caller that knows a switch occurred. If either half is missing, all four are *not started*, owner **W32-7** *(**Discharged 2026-08-24 at `60f6e46`, when WK-692 closed. The first branch fired.** W32-7 shipped `record_switch` and the both-chains audit in `platform/workspace_switch.py`, and filed the trigger question as **`OQ-652`** — so obligation 4 is **deferred with an owner, owner W6b-11**, and the other three are **delivered**. **The second branch is spent, and is recorded as spent rather than deleted**: it would have left an owner clause naming **W32-7**, and no owner clause may name a slice of a closed workstream, so it is discharged here instead of being left to point at nothing. **The rule above is not rewritten** — §0 keeps the record of what was believed when the owner was assigned, and the rule's refusal to name an OQ number is why a numbering accident did not fail a correct W32-7.)* |

**W32-11 — the contract guard's two remaining gaps.** An eleventh slice is allocated here
rather than the two items being scattered, because they are the same work: both are backend
`FR-451` guard work, both were left by W32-1b in writing, and both were unowned. Its
scope is *(i)* the nine-check and four-check narrowings on `ObjectiveCertificate` and
`MetricCertificate`, `objective-certificate.result.checks` `minItems` 8 → 9, and removal of
the `UNRESOLVED_CONSTRAINT_DISAGREEMENTS` carve-out — **in one commit**, which OQ-600 is
directive about; and *(ii)* generated sides for `dataset-version` and
`validation-report`, which need no new model — both Pydantic models and both ORM rows exist —
only two `GENERATED_SHAPES` entries, two `COMPARED_SLUGS` additions, and reconciliation of the
drift the first comparison exposes. **The reconciliation is where the work is**: the
`validation-rule` precedent of 2026-08-23 found three divergences on first comparison. **WK-692
does not close until W32-11 lands.** Closing while the guard is blind at a pair the project
has already decided is precisely the roadmap-reporting-progress-it-does-not-have failure §13
names.

**Two corrections to the paragraph above, both made the same day it was written.**
*(First, the mechanism was stated backwards, and W32-11's own measurement of the guard
corrects it — the original wording is superseded here rather than overwritten, per §5. It is **not** the `minItems` bump that turns the policing test red:
bumping the authored floor alone leaves the pair disagreeing, generated `1` against authored `9`,
and `test_the_escalated_constraint_disagreements_are_still_unresolved` keeps passing. It is the
**narrowings** that do it — unbinding the shared `CertificateResult` makes the generated side emit
no `minItems` at all, so the pair stops disagreeing and the test asserting that it still does goes
red unless the carve-out leaves in the same commit. The directive holds; the reason is the other
way round.)* **Second, the agreement the commit produces is by non-comparison, and saying so is
the point**:
the guard intersects paths and then keywords, so a constraint present on one side only is skipped in
**both** directions by deliberate design — "a constraint on one side alone is a difference of
intent". After the narrowing the floor is published on the **authored** contract only; the generated
schema and `openapi/generated.json` carry none, and enforcement is server-side in the validators.
That satisfies FR-158 as written, and it is **not** the same thing as the two sides having
been reconciled. W32-10 exists because a green suite was once reporting delivery on evidence that
did not bear on the requirement, so this record does not repeat the shape.

**W32-11 had no executor when it was allocated, and it has one now — recorded in both states
because the gap is the point.** As allocated, its plan was not filed and the five-slice run
that closes the rest of WK-692 — W32-10, -9, -8, -1b, -7 — was scoped before it existed and did
not include it, so the standing consequence was that when those five merged WK-692 would sit
un-closeable with every other slice done. That was recorded in the form that forces the
question rather than in a footnote, and the question was then answered: the closure-execution
session picked the slice up on 2026-08-24 as an inference from "execute the remaining work to
close WK-692", **surfaced the inference explicitly rather than acting on it silently**, and the
maintainer confirmed it the same day, in a second and separate message, quoted here exactly as
sent rather than tidied — *"plz mind slice 11 should be the last slice before closure, any new
findings cannot resolved should be booked in a later work or phase, not stop w32 closing; close
if all the goals achieved."* *(Relayed to this session by the executing session, which received
it firsthand; this session did not. The chain is stated so a reader can check it rather than
take it on trust, and the wording is left uncorrected so the check is against the instruction
and not against someone's rendering of it.)*

**That instruction changes WK-692's close condition, and this record follows it rather than the
stricter one written above.** Two effects. **W32-11 is terminal** — it is the last slice, and
no twelfth is allocated to absorb what it turns up. **A finding W32-11 cannot resolve is booked
forward with an owner, not held against the close**: closure requires every unevidenced
requirement to carry a §13 disposition, never for every disposition to be *done*. And the
clause that authorises the close is the last one — **"close if all the goals achieved"** — so
what WK-692's closure record must demonstrate is the goals met, not the ledger empty. The rule this
does **not** relax is the one §13 exists for — a booked-forward finding must be booked, with an
owner, in `open-questions.md` or a roadmap row where the next planner will meet it. Booking
forward into prose in a slice ledger is the silence §13 forbids wearing a different hat. Three
findings from W32-11's own measurement are already travelling that route, and they are the test
of whether the rule was applied or merely invoked.

**Part D — five spec-versus-code disagreements.** Item 2 needs no decision: W32-9 merged as
`faff060` and settled it in code. Of the remaining four, **every one was resolved against the
spec** — the code was right in all four, which is itself the finding and is why none of them
was fixed by widening behaviour. The amendments are dated 2026-08-24 on the rows and blocks
they correct, not summarised here: `02` FR-167 (items 3 and 4), `02` §5.3 and `00` §5.6
(item 3), `02` §4.9 and §5.2 (item 1), and `.claude/skills/contract-guard` (item 5, landing
with W32-1b). **Item 4 is the one worth flagging**, because a plausible wrong resolution was
rejected: a Peril Structure list carries **no** usage count, and not because the count is
merely unimplemented — FR-167 defines the quantity as Model Specs referencing the
artifact, and the reference runs the other way, a Peril Structure pinning models per §4.10, so
the count is *undefinable* on a peril row. An implementation must not invent one to make the
three shapes symmetric.

#### W32-1 … W32-5 — five slice records, back-filled 2026-08-24

**These five records were written after the fact**, from each slice's ledger under
`docs/plans/` and its merge commit, not from the diffs and not from recollection. They are
marked as late for the same reason the WK-661 table marks its own: the omission is the record.
W32-1 through W32-5 were built and merged between 2026-08-22 and 2026-08-23 with ledgers
filed and **no roadmap record**, so for two days the plan could not answer *what did WK-692
deliver* without opening six plan files — and this is the first time all such omissions in a
run happened inside one workstream. Decided as
`plans/PL-00776-wk-692-what-closure-needs-and-why-it-cannot-happen-yet.md` Part B3, accepted by the maintainer 2026-08-24.
**They are shorter than W32-6's record and deliberately so**: a back-filled record states what
merged and what it left with a §13 verdict, and does not reconstruct reasoning nobody wrote
down at the time.

#### W32-1 slice — contracts and the drift guard, 2026-08-23

Merged as `8ac102c` (#141), executed 2026-08-22, the day its plan was written.

| Delivered | Evidence |
|---|---|
| `GroupingEvidence.source_level_stats` added to the Python model — the field its contract had declared since Phase 0, at a construction site that already computed the value (FR-107, `00` FR-9) | `packages/pricing-core/tests/test_groupings.py`, 29 → **30 passed** |
| Three new constraint-level comparisons in the drift guard — `required`-set drift, `additionalProperties` closure, scalar constraints — built on the four existing walkers (`07` FR-451) | `backend/tests/test_contracts.py`, 55 → **99 passed**; 7 new test functions, 8 new `@pytest.mark.req` markers |

**Requirements evidenced:** FR-451, FR-107, FR-9. **None allocated.**

**Left with a §13 verdict.** *(i)* **OQ-600** — the objective-certificate check floor,
`minItems: 8` in the contract against `1` in the model, where neither published number is
right: `02` §4.7's 2026-08-18 amendment makes it nine, and `CertificateResult` is shared with
`MetricCertificate`, which FR-157 gives four. **Escalated to the maintainer as a design
decision**, and scoped out of the guard by (path, keyword) pair with a test that fails the
moment either side moves — the exclusion is falsifiable rather than silent. *(ii)*
**Arm-level attribution** — a GLM-only field declared on the GBM arm still passes, because
`_type_map` unions every arm onto one dotted path. **Deferred**, with the limit written into
the guard's own record rather than left for the next reader to rediscover.

**The finding worth keeping.** Task 2's new test failed unconditionally and said nothing
about the contract: it rebuilt dotted paths as `f"{block}.{name}"` from
`path.rsplit('.', 1)[-1]`, which `prefixItems` — Pydantic's tuple encoding — breaks. **The
contract half was correct throughout; only the test was broken**, and the plan's own
measurement section had named `prefixItems` as the trap before writing it again. The rule now
lives in `.claude/skills/contract-guard`: never rebuild a path from a segment, compare whole
paths as sets.

#### W32-1b slice — arm-level attribution in the drift guard, 2026-08-24

Merged as `7e09eb4` (#159). **This slice discharges the arm-level attribution deferral
recorded immediately above**, which W32-1 left with a §13 verdict rather than a fix.

| Delivered | Evidence |
|---|---|
| All three drift-guard walkers re-keyed from `dotted.path` to `(arm, path)` — `_type_map`, `_closure_map`, `_constraint_map` — so a field moved between tagged-union arms is no longer invisible (`07` FR-451, `00` FR-9) | `backend/tests/test_contracts.py`, **121 passed, 1 skipped**, unchanged across every edit — the re-keying is a reach change, not a behaviour change |
| A shared arm coordinate system: `_complete_arms` builds the arm set from **both** walked maps, `_expand` re-keys both sides onto it, `_admits` decides which arms a constraint reaches, `_arm_name` puts the arm in the failure message | Compared type paths **556 → 606**; constraint keys **189 → 196**, expanded **760 → 767**, `(arm, path, keyword)` triples **839 → 846**; closure flat **17 → 19**, keys **115 → 117** |
| `_conjoin` replaces `.update` at the constraint expansion, refusing a within-arm keyword collision rather than dropping one last-writer-wins | 0 collisions at the walk and 0 at the expansion on this corpus, so the refusal is proven reachable rather than assumed unreachable |

**Requirements evidenced:** FR-451, FR-9. **None allocated.**

**The enforcement proof, run on deliberately broken input** (§13 rule 3). Before the change,
moving `family` from the `glm` arm to the gbm arm left `_type_map` equal dict-for-dict — 64
paths before and after, no disagreement against the generated side either way; moving
`family_params` from `glm` to `ebm` left `_closure_map` returning the identical three paths
with identical values. **Both are caught now.** The merge also made
`spec.monotone_constraints` report `{null, object, string}` — the union of `GbmSpec`'s
`string` and `EbmSpec`'s `object | null`, a shape no arm admits.

**Left with a §13 verdict.** **OQ-649** — arm-level *existence* is still open: the
comparison intersects twice, keys then keywords, so a bound declared on one side only is
reported by neither walker nor comparison. Measured at **70** one-sided constrained paths
across the corpus, **18** of them where the field exists on both sides and only the bound is
one-sided, which the field-name comparison cannot see either. Whether a one-sided bound is
drift is a design decision this slice deliberately does not take. **W32-1b files no new open
question** — the case is subsumed by `OQ-649`, which already names the double
intersection.

**The finding worth keeping — a guard can be narrowed to silence by the coordinate system it
is measured in.** The filed plan's Step 5 built the arm set with `_arms` over the document
root. Measured against this tree that is wrong twice: `model.schema.json`'s root declares no
union at all, so expanding onto its arm set takes `model` from **125 compared paths to 11
while still passing** — a guard that goes quiet without going red — and the "both sides
declare the same arms" pre-assertion fails outright on `custom-objective` and
`validation-rule`, whose generated sides carry no discriminator. Building arms from one side
rather than both is the same defect at larger scale: constraint keys **760 → 177**, `model`
**584 → 1**. The plan is frozen at its date and was not edited to agree; the correction lives
in the code, and three reach controls now pin the numbers so the narrowing cannot recur
silently.

**Three false statements in live prose were corrected rather than carried.** `_arms`'
docstring claimed the arm set is the same whether built from a `discriminator.mapping` or
from four `if`s — the authored `model-spec` has **three** `allOf` `if`s carrying four values
against the generated side's four `mapping` entries, and four-versus-three is the point
rather than an erratum in it. `_constraint_map`'s docstring claimed a one-sided path was
"reported by the comparison rather than by this walker"; it is reported by nothing, and the
prose was corrected rather than the intersection widened. The **same false claim** had
propagated into `.claude/skills/contract-guard` step 3, which named a field-*name* comparison
as the arbiter of one-sided bounds; that skill's walkers table, its "arm-level attribution is
not built" line — written while it was being built — and its `Verified` date were all fixed in
the same session per `CLAUDE.md` §12.

**One finding unrelated to arm attribution, booked because it is a data-loss hazard.** Step 5
of `contract-guard` recommended `git stash` when a proof breaks the walker rather than the
contract. **The stash stack is shared across every worktree of this repository and concurrent
sessions push and pop it**, so a bare `stash` / `stash pop` there can restore another
session's work over yours. Replaced with a private backup file, which is what this slice's
own enforcement proof actually used. The general rule now lives in
`.claude/skills/git-hygiene`.

#### W32-2 slice — the built-in validation-rule catalogue, 2026-08-23

Merged as `a23e16b` (#146).

| Delivered | Evidence |
|---|---|
| `01` §4.4's 38 named rules as a catalogue constant in `model-schema`, following `BUILTIN_ROLES`' precedent, seeded into every workspace as approved built-ins beside `seed_builtin_roles` (FR-68, newly allocated) | `packages/model-schema/tests/test_validation_catalogue.py` — 8 new tests |
| `GET /api/v1/validation-rules` — the workspace's rules, cursor-paginated, filterable by `builtin`, ordering pinned to `id ASC` (FR-68) | `backend/tests/test_api_validation_rules.py` — 6 new tests; the refusal code is `PERMISSION_DENIED` |
| Built-in rule check bindings in `pricing-core` | `packages/pricing-core/tests` |

**Requirements evidenced:** FR-68. **Allocated:** FR-68.

**Left with a §13 verdict.** *(i)* FR-67, NFR-465 and NFR-466 — out of scope;
their verdicts are already written elsewhere in this file. *(ii)*
`examples/fremtpl2/seed.py` still fabricates a `dry_run_report_id` for its nine workspace
rules, and removing it needs a real dry-run report the seed does not produce. **Deferred,
unowned.** *(iii)* `frontend/src/api/profiles.ts` still hard-codes VR-DST-1's PSI bands.
**Deferred, owner W6b-13.**

**The finding worth keeping.** **The plan's acceptance instrument was wrong and the code was
right.** It demanded `38/38` *and* exit 0 from the same `scope-audit.py` run, but the script
exits 1 as soon as any in-scope requirement lacks evidence — before the catalogue result is
consulted — so a slice leaving FR-67 and the two DATA NFRs untouched can never produce
exit 0 however complete its catalogue. The two numbers answer different questions: catalogue
completeness, and whether the whole module is closed, which is a §13 question no single slice
can settle. Recorded rather than fixed; `scope-audit.py` was left alone.

#### W32-3 slice — the dataset list's derived fields, and dataset ownership, 2026-08-23

Merged as `225a8b9` (#148).

| Delivered | Evidence |
|---|---|
| The dataset list's derived fields — `latest_version_status`, `last_validated_at`, `last_validated_version` — computed per request and stored nowhere, governed by a paired-field validator so the pair cannot be half-populated (FR-55) | `packages/model-schema/tests/test_dataset_derived_fields.py` — 6 new tests; `backend/tests/test_api_datasets.py` — 8 new tests; 9 FR-55 markers |
| `Dataset.owner_id`, non-null, set from the creating principal and changed only through the new `PATCH /api/v1/datasets/{dataset_id}` by an Admin (`admin:manage_roles`) or the current owner, audited (FR-82) | `backend/tests/test_api_datasets.py` |

**Requirements evidenced:** FR-55, FR-82. **None allocated.**

**Left with a §13 verdict.** *(i)* `scripts/demo.py` was **not** run end to end — it
unconditionally runs `docker compose up` and binds ports 8000/5173, forbidden while sibling
slices were executing. The seed half was exercised through the real Job path (exit 0) and
`backend/tests/test_demo_guide.py` passes, but the browser walk-through at `/demo` is
unverified. **Delivered but untested**, worth a manual check in a quiet window. *(ii)*
FR-67, NFR-465, NFR-466 — out of scope, verdicts elsewhere in this file.

**Two findings worth keeping.** **First**, promoting `owner_id` to `NOT NULL` made 26 tests
in `backend/tests/test_api_approvals.py` raise `NotNullViolationError`, and the tempting
repair — a column default — **was refused deliberately**: it would have satisfied all 26
while making the new constraint impossible to falsify, and a constraint that cannot fail is
not enforcement (§13 rule 3). The helpers now pass an explicit owner. **Second, the landing
hazard, which is a property of any fan-out and not of this slice**: this slice's migration and
W32-2's both parented on `9e4c7b21fa08`, and `git rebase origin/main` succeeded with **no
conflict** — git sees two new files in a directory — leaving two Alembic heads that only
`alembic upgrade head` reports.

#### W32-4 slice — the EBM predict arm, 2026-08-23

Merged as `54624c7` (#147).

| Delivered | Evidence |
|---|---|
| `POST /api/v1/models/{model_id}/predict` scores an EBM instead of refusing it, routing the EBM arm to the `predict_ebm` `pricing-core` has had since 2026-08-21 (FR-140) | `backend/tests/test_prediction.py` — 2 FR-140 markers |
| A new `UnavailableReason` member giving the response a typed reason for having no interval — an EBM has no covariance matrix and no quantile pair — and a narrowed refusal: an EBM spec carrying a GLM fit result is refused by name (FR-180, newly allocated) | `packages/model-schema/tests/test_ebm_prediction.py` — 5 new tests |

**Requirements evidenced:** FR-140, FR-180, FR-207. **Allocated:** FR-180.

**Left with a §13 verdict.** *(i)* The plan's closing step asked for its own checkboxes to be
ticked; **they were left unticked deliberately** — `docs/plans/README.md` freezes a filed plan
as a record of what was believed at its date, and that rule outranks an instruction inside the
frozen file. The ledger is the execution record instead. *(ii)* Two of the four roadmap sites
the plan named were left alone: they correctly attribute the frontend EBM views to WK-664. **No
in-scope requirement was left without evidence.**

**Two findings worth keeping.** **First, this one slice resolved a spec-vs-code disagreement
in each direction.** The blanket EBM refusal existed only in a docstring with the spec silent
on it — there the **code** was wrong, and the obligation was written down as FR-180
rather than the behaviour quietly widened; the reciprocal case, `02` §5.2's incomplete
`predict.py` block, was a **spec** defect fixed with a dated note. **Second, no timing from
that session is quotable**: the same suite took 12:09 at load 5.8 and 2:36:57 at load 16–31
earlier the same day — a contention factor of roughly 13 on a machine shared by five
concurrent slices. This is why a duration measured during a fan-out is not a regression
signal.

#### W32-5 slice — the two partial-dependence defects, 2026-08-23

Merged as `ae4cdc1` (#150).

| Delivered | Evidence |
|---|---|
| `exposure_share` is summed exposure over total exposure at both categorical points (was a row count) and numeric grid points (was the constant `1.0 / len(labels)`); the omission record's share is dropped exposure over total exposure (FR-174, FR-175) | `packages/pricing-core/tests/test_gbm.py` — 4 new tests, 5 new markers |
| FR-175's cap ranks levels by exposure rather than row count (FR-175) | as above |
| A banded or grouped factor's curve gives one point per band or group rather than one per raw source value (FR-181, newly allocated) | two new tests |

**Requirements evidenced:** FR-174, FR-175, FR-181, NFR-488.
**Allocated:** FR-181.

**Left with a §13 verdict.** *(i)*
`packages/pricing-core/src/pricing_core/modelling/transparency.py` still computes
`exposure_share` as a row count at `:268` and hardcodes `1.0` at `:398`, in the SHAP fidelity
path. **Deliberately untouched** — `02` §5.2 describes *that* site as a percentage of rows, so
changing it is a separate resolution needing its own requirement. **Deferred, unowned.**
*(ii)* Cross factors still grid over their first source column, where a representative value
for a cross level is a tuple across several columns. **Deferred, owner WK-664**, with the
frontend that first plots such a curve.

**The finding worth keeping, because it is a property of the rules and not of this slice.**
**The id-allocation rule and `audit-docs.py`'s gap check cannot both hold for two concurrent
slices.** Defining FR-181 while W32-4's 124 lived on an unlanded branch failed the gate
with a numbering-gap error naming 124, and the failure was **measured** — a placeholder row
for 124 gave exit 0, then was removed — rather than argued. The id was left at 125 because
renumbering would collide and ids are permanent (§5); the instance cleared itself when W32-4
merged. **The consequence a fan-out has to plan for is a merge-order dependency**, and it is
the second one this workstream found after W32-3's two-heads hazard.

#### W32-6 slice — the backtest and custom-objective endpoint tests, 2026-08-23

One of six concurrent test-hardening slices. **Nine routes that had two OpenAPI-presence
assertions between them now carry endpoint tests** — six over the backtest routes, sixteen
over the custom-objective ones. **No requirement id was allocated**: every marker names one
that already existed, which is also why the coverage total did not move (below).

##### What was built

| Delivered | Evidence |
|---|---|
| The backtest routes over HTTP (FR-187, FR-94) | `backend/tests/test_api_backtests.py` — **6 passed, 0 skipped**. 202-and-a-job on request, the stored summary on read, a 404 that names the id asked for, cross-workspace absence, and both refusals (`model:fit` to request, `model:read` to read) |
| The custom-objective routes over HTTP (FR-166, FR-150) | `backend/tests/test_custom_objectives_api.py` — **16 passed, 0 skipped**. Create, read, usage, certify and submit; two cross-workspace 404s; four RBAC refusals **each with a passing case beside it**; three conflicts (certify while under review, submit twice, evidence incomplete); and the `expression` kind refused by name |
| `backtests` joins the append-only row list (`00` FR-4) | `test_artifact_immutability.py`, 13 tests → **14**. The table carried both layers already — the narrowed grant and the `artifact_append_only` row and statement triggers — but was **absent from `_APPEND_ONLY_ROWS`**, the one list that makes the test fire against it |
| The derive refusal split in two (FR-150) | `test_custom_objectives.py` — finding 1 below |

##### The findings, and which side was wrong in each

1. **The derive refusal proved something other than what it claimed — the test was wrong.**
   It granted the caller nothing and asserted `status_code in (403, 409)`. `FitModels` is a
   *route* dependency, resolved before the handler body, so the 409 arm was unreachable and
   the test could never observe the kind gate it was named for. Split in two: an ungranted
   caller must get **403 `PERMISSION_DENIED`**, and a caller holding `analyst` must get
   **409 `OBJECTIVE_KIND_NOT_ENABLED`**. Proven load-bearing by mutating the raised code to
   `VALIDATION_FAILED` — exactly one of the two fails, while the status stays 409, so the
   `["code"]` assertion and not merely the status is what carries the test.
2. **`backtests` was locked in the database and missing from the test's list — the test list
   was wrong.** Entry added, and the trigger shown to fire against a deliberate `INSERT`.
3. **The plan named FR-144 as "backtest results" — the plan was wrong.** FR-144 is
   the **symbolic derivation of gradient and hessian from an `expression` objective's loss**,
   a Phase 2 capability gated off by FR-150 and implemented by nothing. Marking backtest
   tests with it would have put a traceability claim on a requirement no line of this
   repository satisfies — precisely the "a marker is a claim, not a proof" failure
   `CLAUDE.md` §13 rule 1 warns about. The backtest requirement is **FR-187**, which
   `test_backtests.py` already carried; the new markers were corrected to it before commit.
   **Verdict on FR-144: deferred, owner Phase 2**, recorded on its spec row.
4. **A docstring documented `n_points=300` — the comment was wrong**, and by more than
   staleness: `SamplingSpec` now forbids that value (`ge=1_000`). Corrected to name
   `COUNT_GRID`, which is where the real grid lives.
5. **`02` §5.1 said `/derive` answers 422; the code answers 409 — the spec was wrong.** The
   code is right: the kind gate fires before the request body is looked at, so there is
   nothing to report as a validation failure. Corrected by a dated §5.1 amendment.
6. **Three shape findings recorded rather than fixed**, each with an owner, below.
7. **Three read permits were granted by a principal holding both permissions — the
   tests were wrong.** Found by mutation while proving the suite load-bearing (§13
   rule 4): swapping `ReadModels` for `FitModels` on `GET /models/backtests/{id}`,
   `GET /custom-objectives/{id}` and `.../usage` left all 22 new tests green, because
   every permit read as the `analyst`, which holds `model:read` *and* `model:fit`. A
   route re-gated on `model:fit` would have kept them green while every read-only
   principal lost the artifact. Corrected: the three permits now read as the
   `auditor`, and the same mutation fails them.

##### Recorded, not fixed

- **`uq_backtests_model_version` is not workspace-scoped.** Every other uniqueness constraint
  on a workspace-owned table is. Whether that is a defect or a deliberate global identity is
  a governance question and a migration, not a test change. **Owner: unassigned — raise
  before the next slice that touches this table.** Recorded in `02` §4.12.
- **The `derive` route publishes a `200 CustomObjective` it can never return** — the only
  reachable outcome is the 409. A `model-schema` change. **Owner: the Phase 2 slice that
  lands `expression` objectives.** Recorded in `02` §5.1.
- **The custom-objective read routes are single-layer RBAC.** Consistent with the rest of the
  API, so this is noted rather than proposed as a change. **Owner: the next `06` RBAC slice.**

##### What did not move, and why that is the point

**This slice moved requirement coverage by zero** — measured on the branch with its two new
test files present and again with them moved aside, and identical both times (**263 of 507,
51.6%**, on the base it landed against). The plan predicted a rise on the strength of
FR-144 gaining its first marker; finding 3 is why it did not. *(The plan's stated
starting figure of 258 was stale before this slice finished — W32-2, W32-3, W32-4 and `07`
FR-417 all landed on `main` while it ran. The absolute figure is whichever of them landed
last; the movement attributable to W32-6 is zero against any of them.)* FR-187, FR-94, FR-166 and FR-150 were each
already marked somewhere, so **four requirements gained real endpoint evidence while the
count stood still** — the clearest demonstration to hand that the coverage number counts
markers, not proof, and that §13 rule 1's "a marker is a claim" is the load-bearing half.

`scope-audit.py MODEL --endpoints` is unchanged at **41 of 41 declared endpoints published**;
this slice added tests, not routes.

#### W32-11 slice — certificate floors and two generated sides, 2026-08-24

The **terminal** slice of WK-692 — allocated 2026-08-24 by the
[WK-692 closure proposal](../plans/PL-00776-wk-692-what-closure-needs-and-why-it-cannot-happen-yet.md)'s Part C decisions and appended
to, **not one of**, the five slices that proposal filed. It decides `OQ-600` as
FR-158, and gives the last two Phase-1a shapes that had never been compared against code a
generated side. The ledger is
[beside the plan](../plans/PL-00780-w32-11-ledger-certificate-floors-and-two-generated-sides.md).

*(Corrected 2026-08-24. This paragraph opened "The last of the five slices the WK-692 closure
proposal filed", which is false on **membership**, not on order. The proposal's table files
exactly W32-7, W32-8, W32-9, W32-1b and W32-10, and at `plans/PL-00776-wk-692-what-closure-needs-and-why-it-cannot-happen-yet.md`
it **considered this id and declined it** — "`W32-1b` rather than `W32-11`, because §3 of the
slice map already uses that name for this work". W32-11 was allocated afterwards, in Part C's
acceptance; the last of the filed five is **W32-7**, which is unstarted. The **predicate** was
true — W32-11 is the terminal slice, and the proposal's own Part C says WK-692 does not close until
it lands — so every check of the claim passed and only opening the proposal's table caught the
**source** it was attributed to. Corrected in place rather than appended: a reader who reaches
only the opening sentence would otherwise take W32-11 for one of the filed five and read the
proposal's slate as complete. Kept because this is not the stale count §5 already guards, nor a
positional index; see plan review 4.)*

##### What was built

| Delivered | Evidence |
|---|---|
| The certificate battery is enforced **by name, not by a count floor** (FR-158, OQ-600 option (a)) | `battery_is_exactly` computes missing / unexpected / duplicated names, called from `ObjectiveCertificate` (nine names, `02` §4.7) and `MetricCertificate` (four, FR-157). `Field(min_length=1)` is off the shared `CertificateResult`. A nine-long battery missing `branch_discontinuity` and carrying `finiteness` twice is what the old floor waved through, and it read as complete to an approver |
| `dataset-version` gains a generated side (FR-451) | `docs/contracts/schemas/generated/dataset-version.schema.json` |
| `validation-report` gains a generated side, and its authored contract gains the `id` it always required (FR-451) | `docs/contracts/schemas/generated/validation-report.schema.json`; `id` added to the authored contract's `required` and `properties` |
| The Phase-1a gap in `contract-guard`'s reach is **closed** | That skill named `dataset-version`, `validation-report` and `validation-rule` as shapes describing artifacts Phase 1a built that nothing compared. **W32-2 closed `validation-rule`** (`a23e16b`, #146); **this slice closed `dataset-version` and `validation-report`** (`9ab14d6`, #158). The set is empty and the sentence naming it is retired. *(Corrected 2026-08-24: this cell first read "W32-2 closed the first, this slice the other two", which inverts the attribution — `validation-rule` is third in that list, not first. The closed set was right and nothing derived from it was wrong; the per-slice attribution was not. Found because `.claude/skills/contract-guard/SKILL.md` states it correctly and disagreed, and settled by the file-addition history of each generated schema rather than by re-reading either prose. The fix is to name the shapes instead of counting into a list.)* |

`COMPARED_SLUGS` **13 → 15**; authored-without-generated **14 → 11**. Measured on `946725f` plus
this slice: 26 authored, 25 generated, 15 both-sided, 11 authored-only, 10 generated-only, 36
distinct. `COMPARED_SLUGS` equals the both-sided set exactly. **All 11 authored-only slugs describe
Phase 2+ artifacts**, so the residual is bounded by the phase rule rather than by oversight.

##### The finding this slice existed to produce

**Every layer of the contract guard is scoped to the intersection of its two sides.** The type
comparison intersects paths; the constraint comparison intersects paths and then keywords; and
`test_every_eligible_schema_is_compared` — the completeness check — defines an *eligible* schema as
one having both sides, so it is defined over the complement of the problem. Nothing is wrong today.
What is missing is any way to keep knowing that: **the guard is silent in exactly the same way
whether a shape is one-sided on purpose or by accident**, and no reader or test can tell the two
apart.

The two new slugs demonstrate it the day they were added. `dataset-version` passes every
comparison — 26 shared paths, **zero** disagreements — while **22 of its paths are one-sided**: 17
the contract promises and the model does not carry, 5 the reverse, and three of those are the same
concept as a scalar on one side and an object on the other. `validation-report` has 24 shared
paths, 8 one-sided, and one real disagreement.

Corroborating it: `generate-contracts.py`'s comment beside `peril-structure` still read "No
hand-authored Phase-0 counterpart" six days after #133 gave it one. The only place a shape's
one-sidedness was ever declared had gone stale silently, which is the argument for deriving the
declaration rather than narrating it.

**Any count published from here must say which frame it means.** Both are true of the same tree:
the guard compares 15 of 15 shapes it defines as in scope, none unaccounted for; and 21 of the 36
distinct shapes are out of scope by construction.

##### Dispositioned, not delivered

Five open questions were filed rather than answered, each with an owner, and each naming the WK-692
goal it bears on so a closure record can quote rather than paraphrase it. None holds WK-692 open.

| Row | What it books |
|---|---|
| `OQ-649` | The intersection scope above. Subsumes plan finding F2, the missing authored-keyword completeness check |
| `OQ-650` | Nothing revalidates artifacts stored under a looser shape when a shape is tightened; the failure surfaces on the read path, to a user who did nothing |
| `OQ-651` | `metric-certificate` has no authored contract at all — model-side floor enforced, comparison and publication outstanding |
| `OQ-567` | Is an Offending Sample entry an opaque string or a keyed object? The model and the contract disagree and no specification chooses |
| `OQ-568` | `DatasetVersion` diverges from its contract on 22 of 48 paths with every comparison green |

**`OQ-567` was not decided rather than decided quietly.** The model emits a `|`-joined string
with no escaping, `None` rendered as the empty string, and column names dropped; the contract
declares a bare `{"type": "object"}` that constrains nothing. FR-49 says "primary keys of
rows" and chooses no encoding. `CLAUDE.md` §0 forbids a silent pick, so the type comparison is
pinned at that one path with a companion test that goes red the day the pin stops earning its
place — the shape `diagnostics.aliasing` held until `OQ-587` was decided and its pin deleted.

##### Two plan errors, corrected in execution rather than in the plan

The plan predicted that leaving the `UNRESOLVED_CONSTRAINT_DISAGREEMENTS` entry in place would turn
its companion test red. **It did not.** That companion reads both sides through `.get(...)`, so once
`minItems` left the model side it compared `None` against the contract's `9`, found them unequal,
and reported the pair as still disagreeing — an entry could have outlived its question indefinitely
with nothing saying so. The accurate statement is that the pair stopped being **comparable**, not
that it stopped disagreeing. The successor pin's companion tests membership before value, and that
is proven on four deliberately broken pins: a path where both sides agree, a path on neither side,
a path on the model side only, and the real one.

The plan also predicted the merged `contract-guard` would read "13 and two" and said to stop and
reconcile otherwise. It read *twelve* and *14 authored* — the 13/two figures describe W32-1b, which
had not landed. Reconciled by measurement rather than assumption.

#### W32-10 slice — the untested behaviour, 2026-08-24

The first of the five slices the [WK-692 closure proposal](../plans/PL-00776-wk-692-what-closure-needs-and-why-it-cannot-happen-yet.md)
filed, and run first because it touches nothing the other four touch. **It adds no capability.**
What it adds is the ability for three shipped behaviours to fail: a migration's backfill, the EBM
prediction route over HTTP, and the partial-dependence exposure share. **No requirement id was
allocated** — every marker names one that already existed.

##### What was built

| Delivered | Evidence |
|---|---|
| The `82edffbe1dce` dataset-owner backfill is exercised (FR-82) | `backend/tests/test_migration_dataset_owner.py` — **8 passed**. **The first test in this repository that exercises a migration.** Five resolution and negative cases over a `pg_temp` shadow table running `_BACKFILL` verbatim, plus the `nullable=False` refusal through real alembic against a per-test scratch database. Five mutation proofs: the `@%` boundary widened *and* narrowed, the `dataset.created` filter removed, `ORDER BY sequence` swapped for `ORDER BY at`, and the broken input withdrawn to prove the refusal is caused by it |
| The EBM prediction route over HTTP (FR-180, FR-140, FR-193) | `backend/tests/test_prediction.py` — **18 passed** over the file, two tests added. The route was previously asserted over HTTP only by *it is published* and one 403; it now carries per-row numbers, `model_type == "ebm"` and the named interval refusal to the wire |
| The partial-dependence share is exposure, not rows (FR-175, FR-181) | `packages/pricing-core/tests/test_gbm.py` — a fixture whose exposure ranking and row-count ranking disagree, asserting `4.0/404.0` and rejecting `2/404`, parametrised over both backends. **FR-181's first evidence that bears on the requirement** |

##### The finding this slice existed to produce

W32-5 changed `OmittedLevels.exposure_share` from a row-count share to an exposure share, and the
test written to prove it asserted `0.0 < share < 0.5` — which passes identically under the
definition it replaced. Reverting `diagnostics.py` to row counts fails the new test
(`0.00495 != 0.00990`) while **the pre-existing assertion stays green**. The suite had been
reporting W32-5 as delivered on evidence that does not bear on the requirement, and that is now
demonstrated rather than argued.

##### Two plan errors, corrected in execution rather than in the plan

Both are recorded in
[the ledger](../plans/PL-00757-w32-10-untested-behaviour-execution-ledger.md); the plan is frozen at its date.

1. **A blocker that did not exist.** The plan required a `blob_bucket` fixture edit before Task 2
   could start. The EBM arm takes no `blob_store` at all — an EBM's fit result *is* its model
   (ADR-705) — so the buckets never meet. The edit was made, disproved by removing it, and
   reverted; a fixture shared by 16 test modules was left untouched. **Premise disproved, edit not
   made.**
2. **A drafted test that could not catch the failure its own docstring named.** It compared the
   HTTP body against `service.predict_rows` called in the test body — both sides through the same
   service, so a mutation moves expected and actual together and `approx` still passes. Proven by
   mutating the EBM to return the intercept for every row. Closed with an assertion that two rows
   must differ. The same shape as the `0.0 < share < 0.5` problem, found in the slice written to
   fix it.

Task 1 also found that the plan's Step 3 claimed a proof it does not have: the two inconsistent
`entity_ref` shapes are each excluded by the `LIKE` independently, so removing the action filter
leaves that test green. The action filter was given its own seeding, which is what makes the
mutation bite.

##### Verdicts

- **FR-82, FR-180** — already marked before this slice; their coverage line does not
  move. This slice deepens their evidence rather than creating it.
- **FR-181** — **first evidence**, moved off zero.
- The migration's refusal branch — **tested**, not deferred. The plan permitted dropping the
  scratch-database shape as too costly; it was built, so no §13 verdict is owed against it.
- The three stale `datasets.py` anchors in the migration's comment (`:191` → `:205`, `:868` →
  `:951`, `:271` → `:293`) — **deferred with an owner.** The behaviour described is unchanged and
  only the line numbers rotted; a tests-only slice does not edit a merged migration. Owner: the
  next slice that touches that file for a behavioural reason.

**Gate:** the Python/docs half only, run locally, each exit code read — `1842 passed, 1 xfailed`,
all seven commands 0. **The frontend half was not run and is not required**: this slice is tests
only and changes no contract. Requirement coverage **264 marked (50.5%)**.

**One operational finding.** Three tasks ran concurrently against the **shared** compose database,
and it cost: a teardown `DeadlockDetectedError` in `conftest_db`'s session-end cleanup, and
intermittent failures across runs in `test_audit.py`, `test_celery_broker.py` and
`test_model_comparison.py` that did not reproduce on the clean final run. W32-6 gave each
concurrent slice its own database (`gip_w32_6`) and saw none of this. **Concurrent slices should
take a database each**, and this record is the second observation of the same cost.


#### W32-9 slice — the transparency exposure share, 2026-08-24

The second of the five slices the [WK-692 closure proposal](../plans/PL-00776-wk-692-what-closure-needs-and-why-it-cannot-happen-yet.md)
filed. It closes in `transparency.py` the gap W32-5 closed one module away in `diagnostics.py`:
a share called *exposure* that counted rows. **No requirement id was allocated** — every marker
names one that already existed.

##### What was built

| Delivered | Evidence |
|---|---|
| The worst-region share is a share of exposure (FR-136) | `packages/pricing-core/tests/test_transparency.py` — **30 passed**. A fixture whose exposure ranking and row-count ranking disagree (`area = rare` is 4 rows × 50.0 exposure years, `area = common` is 200 rows × 0.02), asserting `200/204` and `4/204`. `_worst_regions` reuses `diagnostics.py`'s `_weights` and `_share` rather than growing a second pair |
| The fidelity statement says what it reports (FR-136) | The rendered sentence moved from `% of rows` to `% of exposure`, so the noun and the number agree for the first time. `docs/specs/02-modelling.md:1354`'s worked example already read *"0.8% of exposure"* — **the spec was right and the code was wrong** |
| `ShapInteraction.exposure_share` is withdrawn (FR-135) | **31 passed** transparency, **103 passed** contracts, `generate-contracts.py --check` **0**. Deleted from the Pydantic shape, its producer, the hand-authored contract, both generated artifacts and `test_contracts.py`'s `REACHED_NESTED_PATHS` |

##### Which of the three FR-136 sites moved

Two. The computation in `_worst_regions` (`mask.sum() / rows` → weighted) and the prose in
`fidelity_statement`. The third — `WorstRegion.exposure_share` in `model-schema` — was already
*named* for exposure and only its value was wrong, so **the published shape is unchanged** and no
consumer of the worst-region half sees a contract change. The one contract change in this slice is
FR-135's deletion.

##### FR-135 was withdrawn, not computed

The field was the literal `1.0` at its only construction site, so there was nothing to make
correct. OQ-601 decided on 2026-08-23 that the honest fix is deletion, and this slice performs
it. **FR-168 — the holdout strength ratio that is meant to replace it — is left unbuilt**,
with OQ-601 as its origin and commit `b019070` as the place it was appended. Until it is
built, an interaction candidate carries `strength` alone: a smaller artifact than the spec's
eventual target, and a truthful one, which the constant was not.

##### The spec line this changed

`docs/specs/02-modelling.md:194` — FR-135's 2026-08-23 amendment stated that *"Removing the
constant field from `ShapInteraction` is **WK-692**'s, and until it lands the artifact publishes a
number that means nothing."* It has now landed, so that clause would have gone stale on merge. Per
`CLAUDE.md` §0 it is resolved rather than left, and per §5 by **appending a dated note to the same
row** — the record of what was believed on 2026-08-23 is preserved intact rather than rewritten.

##### Verdicts

- **FR-136** — already marked; its coverage line does not move. This slice makes the number
  behind the marker mean what the requirement says.
- **FR-135** — **delivered by withdrawal.** The requirement's exposure-share clause is
  satisfied by the field's removal, not by a computation.
- **FR-168** — **not started.** Owner: a later slice or workstream; origin OQ-601.
  Named here so the gap between the withdrawal and its replacement is on the record rather than
  discovered by the next audit.
- The `02` §5.2 `holdout` keyword on `build_shap_summary` (`:2355-2359`) — **not a finding.**
  `git log -L` attributes those lines to `b019070`, the commit that appended FR-168; it is a
  dated, owned forward declaration of a function this slice does not build. Recorded in
  [the ledger](../plans/PL-00774-w32-9-execution-ledger-the-transparency-exposure-share.md) so the next audit does
  not re-derive it.

**The frame is the train frame, deliberately.** `_worst_regions` weights over the train frame, not
the holdout — `02` §3.6 approximates the population the model was fitted on, so unlike a
partial-dependence curve this must not report the holdout's exposure profile. This is the one place
the slice differs from the FR-181 precedent it otherwise mirrors, and the reasoning is in the
function's docstring so the next reader does not "fix" it.

**Gate:** both halves, run locally **in the worktree**, each exit code read — all thirteen
commands 0. `1856 passed, 1 xfailed`; requirement coverage **264 marked (50.5%)**, unchanged and
correctly so, since both markers name requirements already marked; 24 contracts match; frontend
**21 files / 131 tests**, `generate:api` leaving no tracked change and the regenerated
`ShapInteraction` carrying `pair` and `strength` only.

##### One operational finding: the delegated gate ran against the wrong tree

The first gate run was delegated to a `gate-runner` subagent, which reported all thirteen commands
green — having prefixed its pytest with `cd /home/puzhenhao1989/gi-pricing-plan`, the **shared
checkout, which is on `main`**. Every number it reported was `main`'s, and its
`grep exposure_share frontend/src` "found no results" only because the generated client there had
never been regenerated.

It was caught by arithmetic: the agent reported 1843 executed while the worktree collects **1857**,
and a 14-test gap with no `skipped` or `deselected` is not a gap a passing run can have. **A
wrong-tree gate agrees with a right-tree gate on every slice that does not move the counts**, which
is what makes it hard to see. The rule: a delegated gate must be told to run in the worktree, must
report the `pwd` it ran in, and its pytest total must be reconciled against `--collect-only` before
it is believed.

#### W32-8 slice — the artifact library list routes, 2026-08-24

**Merged.** `GET /custom-objectives`, `GET /custom-metrics` and `GET /peril-structures`, each
cursor-paginated and filterable by `status` and `slug`, behind one shared per-page usage
aggregate. FR-167's own budget — *one aggregate per page, never one per row* — is
**measured rather than asserted**: `test_one_page_of_refs_costs_one_query` counts the queries a
page issues, because an N+1 implementation passes every other test in the slice. Nine commits,
21 files, +2625/−81. Full record in
[the ledger](../plans/PL-00772-w32-8-execution-ledger-the-artifact-library-list-routes.md); the plan is frozen
at its date.

**Two spec-versus-spec disagreements were raised, and both were answered upstream on the
same date.** `CLAUDE.md` §0 forbids a slice picking a side when both sides are specification,
so the slice raised them rather than editing either side. Before the branch merged, the WK-692
closure proposal's Part D amendment to FR-167 (#156) decided both — each the way the
slice had recommended, and reached from the specification side without sight of that analysis.
Both are filed **born-`decided`**, because the register's four status values exist so that an
answered question keeps its alternatives and its guard rails where the next reader will look.

* **OQ-602 — does §5.3 render one artifact library or three?** FR-167 opens *"the three artifact
  libraries §5.3 renders are listable"*, and when the slice was built §5.3 rendered **one**
  (`Custom objective library`, `/objectives`), plus a peril structure *detail* view and no
  custom-metric view at all. Part D item 3 added the two missing §5.3 rows — `Custom metric
  library` at `/metrics` and `Peril structure library` at `/peril-structures` — against routes
  §5.1 already declared, so the opening sentence now describes §5.3 as it stands.
* **OQ-603 — which artifact rows carry `usage_count`?** The same requirement's prose was unqualified,
  while §5.1 puts the field on objectives and metrics and **omits it from peril structures**.
  The slice built §5.1's reading and **asserted the absence** rather than leaving it implicit.
  Part D item 4 qualified the prose to the two libraries, on the ground the slice had given:
  the quantity is undefinable on a peril row, because `PerilComponent` holds model
  `ArtifactRef`s so the reference runs PerilStructure → Model, and `ModelSpec.peril` is a plain
  `str` label — *"the count of Model Specs referencing that artifact"* is **`0` by construction,
  forever**, the same defect class W32-9 deleted from `ShapInteraction.exposure_share`. The
  holding deliberately does **not** rest on perils having no `/usage` route: FR-237 pins a
  peril structure per `model_call`, so it has a real blast radius.

**FR-166's point *(a)* went false in this slice** — *"there is no list route — seven routes
and none of them lists"* — and carries a dated correction rather than a rewrite (§5). The
sentence records what was true on 2026-08-23 and is the reason FR-167 exists; deleting it
would erase the evidence for the requirement that cured it.

**The gate caught a gap three test runs had not.** Twelve of thirteen commands were green and
`generate-contracts.py --check` passed, but `test_contracts.py` failed on `custom-objective`:
the model produced `usage_count` while the **authored** contract did not declare it. The
generated side agreeing with the model proves nothing about the authored side, which is the
half a human maintains — the asymmetry `CLAUDE.md` §13 rule 4 is pointing at. Fixed in
`8c72c38`. `custom-metric` did not fail because it has no authored counterpart at all, which is
one of the uncompared shapes W32-1b's skill count tracks.


#### W32-7 slice — workspace identity and selection, 2026-08-24

**Merged.** FR-396 and FR-397: a principal who belongs to several workspaces can now
say which one it is acting in, and the platform **verifies the answer instead of trusting it**.
`require_caller` declares a `Workspace-Id` header and `_select_workspace` checks it against the
memberships the platform already holds — a workspace the principal does not belong to is
`403 WORKSPACE_SCOPE_DENIED`, and several memberships with no selection remain refused with
`403 WORKSPACE_SELECTION_REQUIRED`. The refusal is the permanent rule and the header is a way to
satisfy it, never a claim that widens scope; **nothing defaults a multi-membership principal
into one workspace.** The header is published on **108 of the 112 operations** — the four
without it are `/healthz`, `/readyz`, `/version` and `/metrics`, exactly the unauthenticated
surface — and that count is asserted by a test rather than assumed, because the reason for
declaring the header on the dependency instead of reading the raw request is that a generated
client should carry it. Full record in
[the ledger](../plans/PL-00770-w32-7-workspace-identity-and-selection-execution-ledger.md); the plan is
frozen at its date. Four commits, of which three carry the code — the workspace row and
its backfill migration, `GET /me`, then the header check with the switch recorder — for
21 files and +2883/−77, or 20 files and +819/−49 once the regenerated
`openapi/generated.json` is set aside, that one file being most of the total.

**FR-396 has four obligations and this slice delivered three.** The fourth — auditing a
switch — got its **mechanism** but not its trigger. `platform.workspace_switch.record_switch`
writes one event in the workspace left and one in the workspace entered, because `06` FR-372
chains audit events *per workspace* and a single event is invisible from the chain an auditor is
usually reading; the two writes are ordered by id so two principals switching in opposite
directions cannot take the same pair of advisory locks in opposite orders. What is missing is
the call site, and not for want of effort: **`require_caller` runs once per request and holds no
memory of the previous one, so "the selection changed" is not a fact it can observe.** The
§13 verdict is therefore *deferred with an owner* rather than delivered — a green suite here
would otherwise imply an obligation that is not met. **Owner: `W6b-11`**, the workstream with
the workspace switcher in front of it. Options are OQ-652, which recommends storing the
previous selection reached through an explicit endpoint and names *auditing every selection*
as the option to refuse out loud: it needs no schema change, so it is the one a later reader
reaches for, and it turns the FR-372 chain into a request log.

**A measurement replaced the question the plan asked.** The plan's Task 5 recommended adding
`workspace` to `ARTIFACT_TYPES` so a switch event's `entity_ref` would parse. Checked before
diverging: of the **39 `entity_ref` spellings the backend writes, only 19 parse** — 13 types
besides `workspace` are already absent from the frozenset (`actor`, `job`, `principal`, `role`,
`service_account` and eight more), and 5 more name a listed type with **no `@version`**, so
`dataset:{slug}` records which dataset was touched but not which version of it. "The audit
chain holds `ArtifactRef`s" was never true, and admitting one more type would fix 1 case in 20
while redefining the frozenset as "things that appear in `entity_ref`" rather than "things that
are artifacts". OQ-653 records the measurement and recommends declaring what the column
actually is — *the subject of the event* — with a validator that admits both shapes. The plan
is left unedited (§2: a filed plan is frozen at its date); the correction is in `38d2c22`'s
message and the ledger.

**Declaring one header re-broke a defect a whole module exists to prevent.** FastAPI injects a
`422` typed as its own `HTTPValidationError` into every operation that has a parameter and does
not already declare one. Giving `require_caller` a header handed **112 operations a parameter in
a single edit**, and the five that had never had one began publishing a second error shape — the
exact FR-451 finding `api/responses.py` was written to remove, arriving through a dependency
rather than through a route. A per-route convention cannot catch a change made in a dependency,
so `without_fastapi_validation_error` now strips it from the assembled document, applied in
`create_app` so the served document and the committed contract stay the same bytes. The five
are **not** given `problems(422)` instead: they cannot return one — the header is optional and
`api.deps` answers a malformed value with `403`, not `422` — and advertising an error a route
never produces is precisely what `problems` exists to stop. The 103 routes that genuinely can
fail validation declare their own `422` and are untouched. Caught by the full suite, not by
`generate-contracts.py --check`, which passed throughout: the contract faithfully described the
code and both were wrong together, which is the asymmetry `CLAUDE.md` §13 rule 4 points at.
