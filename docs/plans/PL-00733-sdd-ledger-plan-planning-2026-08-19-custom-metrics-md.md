---
id: PL-733
family: plan
kind: leaf
title: SDD ledger — plan: .planning/PL-00734-custom-metrics-fr-154-implementation-plan.md
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-08-19
owner: planner
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                     # ids only
was: docs/plans/2026-08-19-custom-metrics-ledger.md
---

# SDD ledger — plan: .planning/PL-00734-custom-metrics-fr-154-implementation-plan.md

Spec: `docs/specs/02-modelling.md` — FR-154 (§3.7), §4.4, §4.5, §4.7, §5.1. Read, reachable.
Branch: `worktree-custom-metrics`. BASE at start: 4c85f22.
Decision gate answered by the maintainer before execution: **all three recommendations accepted**
— DG-1 (a) reduced certificate, DG-2 (a) reuse the objective template losses, DG-3 (a) all six endpoints.

## Pre-flight scan

### Pairs sharing a file or an interface

| Tasks | Produces → consumes | Finding |
|---|---|---|
| T1 → T2..T6 | FR-155, FR-156, FR-157, FR-159, FR-160, FR-162, the ids every later `@pytest.mark.req` names | Consistent. `req-coverage.py` fails on a marker naming a requirement that does not exist, so T1 must land first — it does. |
| T1 → T5 | `METRIC_*` codes: T5 declares them in `02` §5.1 **and** registers them in `errors.py` in one commit | Consistent, and **unlike the FR-137 slice there is no deliberately-red window**: `test_spec_error_codes_are_all_constructible` iterates `PLATFORM_ERROR_CODES` only (OQ-548 records exactly this gap), so a modelling code declared in the spec reddens nothing. Noted so nobody expects PR #120's red-test pattern here. |
| T1 → T5 (reporting) | T1 declares 5 new endpoints; T5 publishes them | **Known interim regression, not a gate failure.** Between T1 and T5, `scope-audit.py MODEL --endpoints` reads 34 of 40 rather than 34 of 35. No gate step consumes scope-audit. Ruling below. |
| T2 → T3 | `CustomMetric`, `MetricDirection`, and `template_loss` from objectives | Consistent. T3 Step 4 adds the accessor T3 Step 5 and T3's first test both use. |
| T2 → T4 | `MetricStatus` / `MetricDirection` values as DB check constraints | Consistent — five statuses, two directions, both closed sets. |
| T2 → T5 | `CustomMetric`, `VALID_METRIC_TRANSITIONS` | Consistent. |
| T2 → T6 | `FITTABLE_METRIC_STATUSES` | Consistent — T6's `METRIC_NOT_FITTABLE` test asserts `draft` is excluded, which T2's own test also pins. |
| T3 → T5 | `certify_metric(metric, *, seed)` for the `metric.certify` handler | Consistent. |
| T3 → T6 | `evaluate_metric(metric, y, f, w) -> float` | Consistent. |
| T4 → T5 | `CustomMetricRow`, `MetricCertificateRow` | Consistent. |
| T5 → T6 | `resolve_ref(session, *, workspace_id, ref)` | Consistent **by instruction, not by construction** — T5's Interfaces block requires matching `objectives.resolve_ref`'s real signature rather than the plan's guess at it. |
| T5 → T6 | Both modify `backend/src/app/worker/model_handlers.py` | Sequential only. **No parallel dispatch of T5 and T6.** Different functions (`metric.certify` handler vs the fit handler's `load()`), so no textual conflict expected. |
| T2 → T7 | Contracts regenerated in T2, re-checked with `--check` in T7 | Consistent. |

### Per-task self-consistency

| Task | Tests specified vs code specified | Finding |
|---|---|---|
| T1 | docs only; `audit-docs.py` is the check | Agrees. 483 → 489 is stated and checkable. |
| T2 | 8 tests vs 3 validators, 2 enums, 3 constants | Agrees. `extra="forbid"` is what makes `_metric(hessian_strategy=...)` raise, and the config line is in the plan's code. **`TEMPLATE_PARAMETERS` verified real** (`objectives.py:52` exported, `:332` defined), and `TemplateParameter.check(value)` verified at `:199` — both were flagged as guesses in the plan and are now confirmed. |
| T3 | 6 tests vs 2 functions | Agrees **after RL-865** — the plan's `SamplingSpec(...)` call is wrong as written. |
| T4 | 4 tests vs table, constraints and trigger | Agrees. Fixture names are flagged as unverified in the brief; the implementer reads `conftest.py`. |
| T5 | 6 tests vs service, router, worker handler | Agrees. The bad-transition error code is deliberately unasserted, with instructions to find the real one. |
| T6 | 6 tests vs resolution helper, narrowing, feval wiring | Agrees. Helper/fixture names flagged as unverified; the pre-existing refusal test at `test_gbm.py:984` must stay green and is named. |
| T7 | no tests; the gate is the check | Agrees. |

### Rulings made before execution

**RL-864 — the interim endpoint-count regression between T1 and T5 is accepted, not worked around.** T1 declares five endpoints the code does not serve until T5, so `scope-audit.py MODEL --endpoints` reads worse mid-branch than it did before. The alternative — declaring the endpoints in T5's commit instead — would put the spec change inside the implementation commit and break the rule that the spec is written first (`CLAUDE.md` §0). No gate step reads scope-audit, and T7 Step 3 checks the final number. *Cost if wrong:* a mid-branch audit looks like a regression to anyone running it; bounded by this note.

**RL-865 — `SamplingSpec` takes tuples, and the plan's Task 3 code is wrong.** `objectives.py:592-599` declares `y_range: tuple[float, float]` (likewise `f_range`, `w_range`); the plan writes `y_range=list(_Y_RANGE)`. Pydantic would coerce a 2-list to a tuple in lax mode, but the module's models are strict-ish and relying on coercion where the type is explicit is the kind of thing that changes under a config edit. **The dispatch tells the implementer to pass the tuples directly** — `y_range=_Y_RANGE` — and not the `list(...)` the plan shows. *Cost if wrong:* none; if coercion would have worked, the direct tuple works too.

**RL-866 — implementers run their task's scoped tests plus `ruff`/`mypy`, not the whole suite.** The full gate is Task 7's own deliverable, and the suite is ~5 minutes. *Cost if wrong:* a cross-task regression surfaces at T7 rather than at the task that caused it; the task reviews and the final whole-branch review are the net.

**RL-867 — the plan's stated counts (483 → 489 requirements, 21 → 22 contracts, per-task test tallies) are checkpoints, not acceptance criteria.** Implementers report the number the run prints. The gate is each command's own exit code. *Cost if wrong:* none.

## Task log

Task 1: implementer DONE — commit `d8a8f48`, `audit-docs.py` exit 0, **489 requirements** (483 + 6),
matching the brief's checkpoint exactly. FR-141 confirmed as the maximum before appending 103.

Task 1: **brief defect reported by the implementer, and it is right.** Step 6 said to add the three
`OQ-MODEL-` rows to `docs/open-questions.md` and stopped there; `audit-docs.py` additionally requires
each id to appear bolded in `02-modelling.md`'s own local `## 10. Open questions` mirror table. The
implementer added condensed rows there in the existing OQ-588/589 style rather than inventing one,
and said so instead of quietly patching around a failing audit. **Ruling: the file is right and the
brief was incomplete.** The mirroring rule is `CLAUDE.md` §10's "update `open-questions.md` in the same
PR" read strictly — a spec's own §10 is the module-local half of that mirror, and the audit enforces
both halves. No action beyond this note; the reviewer re-runs the audit independently.
*Cost if wrong:* the added §10 rows diverge in style from their neighbours — visible in the review diff.

Task 1: review — spec ✅, quality **Approved**, 0 Critical, 0 Important. The reviewer verified
FR-159's premise at the mechanism rather than trusting it: `grep -rn 'eval_metrics' --include=*.py .`
returns exactly one hit in the whole codebase, the field's own declaration at `modelling.py:1073`. It also
re-ran `audit-docs.py` independently — 489 requirements, 72 open questions all mirrored — and confirmed the
§10 mirror addition was a real brief gap (check #4 requires every `OQ-` id bolded in some spec file), not
scope creep.

Task 1: minor (deferred): the unstruck tail of `02`'s deferred-endpoint amendment still reads "an endpoint
declared and not built reads as delivered to anyone auditing the table" — true when written, stale framing
now the endpoint is delivered. A brief artifact (Step 5 specified that block verbatim), not an implementer
error. For the final review to triage.

Task 1: minor (deferred): `open-questions.md`'s new rows carry bolded `**FR-MODEL-N**` cross-references.
The reviewer checked whether this trips the define-once rule and proved it cannot — `audit-docs.py` globs
`specs/*.md` only, so `open-questions.md` is outside that check by design, and the rows copy the
pre-existing OQ-588 pattern the brief told them to follow. Noted for whoever owns the convention.

Task 1: ⚠️ resolved by controller — the reviewer could not find the "two verified names"
(`TEMPLATE_PARAMETERS`, `TemplateParameter.check`) in the brief. Correct: they were in my dispatch prompt,
not the brief, and were informational. Nothing in the diff depends on them. Not a gap.

Task 1: complete (commit 4c85f22..d8a8f48, review clean)

Task 2: implementer DONE_WITH_CONCERNS — commit `da8b830`, 8 tests pass, ruff 0, mypy --strict 0
(126 files), contracts 21 → 22 with `--check` clean. Three concerns, two of them real defects in
**my** plan. Corrections handled pre-review, per the skill's DONE_WITH_CONCERNS routing.

Task 2: **RL-868 — `MetricDirection` is a duplicate, not a namesake. Reuse the existing enum.**
The implementer found `model_schema.comparison.MetricDirection` already exists (four members) and is
consumed by `pricing_core.modelling.comparison`; it avoided the collision by omitting the new enum from
the root re-export. That is a workaround, not a resolution — two same-named enums in one package is
exactly the trap `CLAUDE.md` §2 names ("a shape defined twice will diverge, and a diverged shape is a
mispricing"), and `from model_schema import MetricDirection` becomes ambiguous to every later reader.
I read the existing enum before ruling: `HIGHER_IS_BETTER`, `LOWER_IS_BETTER`, `CLOSER_TO_ONE_IS_BETTER`
(for A/E, "1.4 and 0.6 are equally wrong"), `NOT_ORDERED`. Its docstring — *"which way is better,
declared with the metric rather than assumed by the reader"* — is FR-156's concept word for word.
The metric enum's two members are a strict subset. **Reuse it, and refuse the two non-early-stopping
members on `CustomMetric` with a validator naming FR-156:** early stopping compares successive
values, so `NOT_ORDERED` has no "better" and `CLOSER_TO_ONE_IS_BETTER` is not the monotone comparison a
backend's early-stopping loop consumes. **No spec change is needed** — the wire values `lower_is_better`
and `higher_is_better` are unchanged, which is the strongest evidence the two enums were one concept.
Rejected: renaming the new enum (keeps two overlapping definitions of one idea); renaming the existing
one (breaks a live consumer for no gain). *Cost if wrong:* `CustomMetric.direction` accepts a 4-member
type restricted to 2 at the validator rather than at the type — visible, and reversible by splitting the
enum later.

Task 2: **RL-872 — the spec example is wrong and the code is right: `"cap": 250000.0` → `250000`.**
The `money_minor` template parameter's own `check` refuses a float, so the JSON in `02` §4.13 could not
be constructed. Money is integer minor units (`CLAUDE.md` §7, and OQ-547 decided `DecimalStr` refuses a
float). Verified it is the only occurrence in the spec — `grep -n '"cap"'` returns line 1250 alone — so
this is a defect my plan introduced in Task 1, not a pre-existing one. `audit-docs.py`'s money check
missed it because `money_re` matches only keys ending `_minor`; the narrowness is real but widening it is
OQ-548-shaped work, not this slice's. *Cost if wrong:* none — an example that cannot be constructed is
wrong under every reading.

Task 2: brief defects confirmed and accepted as fixed — `YDomain(min=0.0)` names no such field (the real
ones are `min_inclusive`-shaped), and `scripts/generate-contracts.py` needs `CustomMetric` registered in
`GENERATED_SHAPES` rather than discovering it. Both were mine; both fixes stand.

Task 2: corrections landed — commit `d5e8565`. 10 tests (8 + 2 new negatives for the refused direction
members), ruff 0, mypy 0, contracts 22 `--check` clean, audit-docs clean.

Task 2: **RL-873 — the same defect class one line further down, and it gets the same answer.** The
implementer scoped strictly to the `cap` float I named and flagged that `02` §4.13's
`"y_domain": {"min": 0.0}` has the identical field-name mismatch. Correct on both counts: scoping to the
instruction was right, and reporting the rest was right. `YDomain` declares
`min_inclusive`/`min_exclusive`/`max_inclusive`/`max_exclusive` and no `min`
(`objectives.py:222-227`), so the example could not be constructed. I checked what the template itself
declares rather than guessing a plausible value: `TEMPLATE_APPLICABILITY[CAPPED_GAMMA].y_domain` is
`_POSITIVE = YDomain(min_exclusive=0.0)` (`objectives.py:326, 395-397`) — severity is strictly positive.
**Fix to `min_exclusive`, matching the catalogue.** *Cost if wrong:* an example declaring a slightly wrong
bound; bounded by its agreement with `TEMPLATE_APPLICABILITY`, which is the authority a reader would check.

Task 2: review — spec ✅, quality **Approved**, 0 Critical, 1 Important, 2 Minor. The reviewer verified
the corrections at the mechanism rather than trusting the report: `grep -rn 'class MetricDirection'`
returns exactly one definition (`comparison.py:50`), the existing consumer still passes (13/13 comparison
tests), and it re-ran the whole gate itself — ruff 0, mypy 0 (126 files), 183 model-schema tests,
`generate-contracts --check` 22 matching, audit-docs 489/72.

Task 2: **RL-874 — the Important finding is real and is fixed now, not deferred.** `MetricCertificate`
declares `certified_at: str` while the class it is explicitly modelled on, `ObjectiveCertificate`
(`objectives.py:689`), declares `datetime`. The reviewer proposed a fast follow-up; I am folding it into
this task instead, because **Task 5 persists a `MetricCertificateRow` and constructs this object** — a
timestamp typed `str` would reach the database layer before anything caught it, and a certificate's
`certified_at` is the field an auditor reads. It survived because `MetricCertificate` is constructed
nowhere in the suite, so mypy saw a self-consistent `str`. The fix carries a construction test, which is
the actual gap. My defect: the brief's Step 4 code said `str`. *Cost if wrong:* none — the sibling class
is the authority and they now agree.

Task 2: **RL-875 — a Minor upgraded to Important, on the sibling's own reasoning.** The reviewer noted
`CustomMetric` has no analogue of `CustomObjective._applicability_is_within_the_template` and classified
it Minor because `02` §4.13's invariant list does not mention narrowing. But that list is **mine**, and it
was incomplete for the same reason the three JSON defects were. I read the sibling validator before
ruling (`objectives.py:515-524`): its docstring argues *"a Gamma loss declared applicable to `claim_count`
is `y/μ + f` on a response that is zero most of the time, which is `inf`."* That argument transfers to a
metric **verbatim** — `evaluate_metric` computes the same loss — and it is load-bearing for Task 6, whose
`METRIC_NOT_APPLICABLE` check compares the metric's applicability against the *spec*, and so trusts an
applicability nothing has checked against the *template*. A capped-gamma metric declaring `claim_count`
would pass Task 6 and then evaluate a Gamma loss on counts. FR-157's `finiteness` check would not
catch it either: it samples `y` over `[0, 1e7]`, not the response the metric actually meets.
**Add the validator, a negative test, and the missing invariant sentence to §4.13** — resolve, not soften
(`CLAUDE.md` §0). `Applicability.is_within(template)` already exists at `objectives.py:312`.
*Cost if wrong:* a metric author who legitimately wants to widen applicability is refused — but the
sibling refuses it too, so the platform would be inconsistent the other way.

Task 2: minor (deferred): `GENERATED_SHAPES` entry position could not be read from the elided diff
context; `--check` passing is the functional proof. No action.

Task 2: fix round 1/5 (2 addressed, 0 open — `certified_at` now `datetime` with a construction test;
`_applicability_is_within_the_template` analogue with a negative test and the §4.13 invariant sentence;
commits a9aeece..a7113f0). 12 tests, ruff 0, mypy 0, contracts 22 `--check` clean, audit-docs clean.

Task 2: **RL-876 — `MetricCertificate` must be a published contract, because its sibling is.** The
implementer correctly observed that changing `certified_at` altered no generated schema, since
`MetricCertificate` is absent from `GENERATED_SHAPES` — and reported that rather than regenerating
something unchanged, which was right. But the absence is itself the defect: `scripts/generate-contracts.py`
registers `"objective-certificate": "ObjectiveCertificate"` at line 87, and **FR-162 declares
`GET /custom-metrics/{id}/certificate` returning a `MetricCertificate`** — so it crosses the API boundary
exactly as its sibling does. ADR-704 and FR-451 make a boundary-crossing shape a published contract;
one of a matched pair being published and the other not would leave a frontend generating a type for the
objective certificate and hand-writing one for the metric certificate. Register it as
`"metric-certificate"`, mirroring line 87. Task 2 owns this: it already added `"custom-metric"` at line 98.
*Cost if wrong:* one extra generated schema nothing consumes yet — the same state `custom-metric` is in
until Task 5.

Task 2: fix round 2/5 (1 addressed, 0 open — `metric-certificate` registered, schema generated and
committed; commits a7113f0..7f5275f). Contracts 22 → 23, schemas 53 → 54.

Task 2: re-review — **all three findings ADDRESSED, no new breakage.** The re-reviewer verified the
negative test genuinely proves refusal rather than constructing a passing case (it asserts
`ValidationError` matching "wider than" on a `capped_gamma` metric claiming `claim_count`), and confirmed
the generated schema is *committed* rather than merely generated — an uncommitted generated file is a
broken build, and checking that distinction is the difference between a re-review and a rubber stamp.
Independent run: 12 tests, ruff 0, mypy 0 (126 files), 23 contracts match, audit-docs 489/72/54.

Task 2: complete (commits d8a8f48..7f5275f, review clean after 2 fix rounds)

Task 3: **RL-877 — the plan's Task 3 test helper is now refused by Task 2's own validator, and the
helper is what is wrong.** `Applicability.is_within` requires `self.offset_required >= template.offset_required`
(`objectives.py:312-319`), and `TEMPLATE_APPLICABILITY[POISSON]` declares `offset_required=True`
(`objectives.py:384-387`). The plan's `_metric()` helper passes `offset_required=False`, which is a
*widening* — it claims the Poisson loss applies without an exposure offset, and fitting counts without one
models claims per record rather than claims per year. So the validator is right and my helper was wrong.
**Corrected helper for a POISSON metric: `offset_required=True`, `y_domain=YDomain(min_inclusive=0.0)`**
(the template's `_NON_NEGATIVE`), backends narrowed to `("xgboost",)` which `is_within` permits.
Carried into the dispatch. *Cost if wrong:* Task 3's tests fail immediately and visibly at construction.

Task 3: **RL-878 — no `# type: ignore[arg-type]` for the `template` narrowing.** The plan's
`certify_metric` silences mypy twice on `metric.template` being `ObjectiveTemplate | None`. A real
narrowing check that raises is available and is what `evaluate_metric` already does in the same file; a
`type: ignore` where a narrowing works hides the next genuine error at that line. *Cost if wrong:* one
extra guard clause on a branch the validator makes unreachable.

Task 3: implementer DONE — commit `c29554d`, 6/6 tests, ruff 0, mypy 0, lint-imports clean. **Step 7's
mutation proof behaved correctly:** with `_better` forced to `return True`, exactly
`test_certification_catches_a_direction_declared_backwards` failed (1 failed / 5 passed); restored, 6 passed.
All five controller corrections applied.

Task 3: **two further brief defects found by the implementer, both mine, both real.**
(i) `CheckStatus.FAIL` does not exist — the member is `CheckStatus.FAILED`; my brief used the wrong name
throughout the module *and* the test, so it could never have run.
(ii) **`test_weights_are_honoured_not_ignored` was vacuous as written.** The brief set `f=[0.0, 0.0]`, and
the Poisson loss is `exp(f) - y·f`, which at `f=0` is `1` for every row **regardless of `y`** — so the
per-row loss is constant, the weighted and unweighted means are both 1, and the assertion could not fail
whatever the implementation did. Verified independently: this is arithmetic, not opinion. The implementer
changed `f` to `[0.0, 1.0]` and documented why in the docstring. **This is the review rubric's
"test that asserts nothing" defect, and my plan mandated it** — the kind the pre-flight scan is supposed to
catch and did not, because the scan checked that each task's tests matched its code and not whether a test
could discriminate. Worth carrying into how the remaining task briefs are read.

Task 3: review — spec ✅, quality **Approved**, 0 Critical, 0 Important, 1 Minor. The reviewer
independently reproduced the mutation proof (mutated `_better`, got exactly 1 failed / 5 passed, restored
byte-identical, 6 passed, `git status` clean) and **ran the corrected weights test's arithmetic in Python**
rather than accepting the diagnosis: with `y=[0,5], f=[0,1]` a correct weighted mean gives -0.6409 vs
-2.2489 while a weight-ignoring `np.mean` gives -0.6409 for both, so the assertion now genuinely
discriminates. ADR-703 verified at the imports (`metrics.py` pulls only numpy and model-schema — no clock,
no uuid, no id allocation) and `lint-imports` reports 3 contracts kept / 0 broken. No loss arithmetic
reimplemented: every computation routes through `template_loss` into the same `_TEMPLATES[...].loss` that
`compile_objective` binds for fitting.

Task 3: **a real limitation the reviewer surfaced and I am recording rather than fixing.**
`smoke_evaluation` cannot catch "weights ignored", because its fixture uses a constant weight vector
(`3.0` for all 1 000 rows) — so a weighted-mean bug and an unweighted-mean bug return the same number
there. That gap is covered by the unit test instead, which is the right place for it. The check still
catches a wrong reduction, a wrong template, or broken `evaluate_metric` plumbing. Recorded because a
future reader could otherwise take `smoke_evaluation` for broader cover than it has.

Task 3: minor (deferred): `scale_behaviour` is WARN-only by design and its `span < 1e3` threshold is
generous, so it will rarely fire for the shipped catalogue (Poisson's span is ~10). Real but lenient, and
it matches the brief's own design rather than being an implementer defect. For the final review to triage.

Task 3: complete (commits 7f5275f..c29554d, review clean)

Task 4: implementer DONE_WITH_CONCERNS — commit `ee81ca0`, 4/4 new tests plus 13/13 in
`test_artifact_immutability.py`, ruff 0, mypy 0, and the migration reversed cleanly
(`downgrade -1` then `upgrade head`, no "already exists"). It verified **every** negative test by
deliberately breaking the guarded invariant — trigger disabled, constraint dropped, function rewritten —
and restoring. That is the standard `CLAUDE.md` §13.4 asks for and it did it unprompted.

Task 4: **RL-879 — the implementer found a real bug in Task 2's output, and it is load-bearing.**
`CustomMetric._a_status_past_draft_rests_on_a_certificate` (`metrics.py:173-180`) exempts only `DRAFT`.
Its sibling exempts `DEPRECATED` too, and says why (`objectives.py:536-542`): *"an objective abandoned
before it was ever certified is withdrawn, not certified."* Since `VALID_METRIC_TRANSITIONS[DRAFT]`
declares `{CERTIFIED, DEPRECATED}`, the edge `draft → deprecated` is **declared and unconstructable** — a
metric abandoned before certification cannot be represented at all. My defect: the brief's Step 4 code.
Load-bearing because Task 5 builds the lifecycle service over exactly these transitions.
**Reopening Task 2 to fix it**, before Task 4's mirrored CHECK constraint copies the wrong logic into the
database. *Cost if wrong:* a deprecated-without-certificate metric becomes representable when it should
not be — but the sibling's reasoning says it should.

Task 4: **RL-880 — the three omitted constraints get added, and the implementer was right to ask.**
It deliberately left out an undeletable trigger, a phase-1-template CHECK and a certificate-required CHECK,
all present on `custom_objectives`, because the brief named none of them. Correct to scope narrowly and
report. My ruling is to add all three: **artifact immutability is a retrofit-impossible foundation**
(`docs/roadmap.md` §5), so an artifact a Model's spec references by `custom_metric:<slug>@<version>` must
not be deletable; and the other two are the same defence-in-depth argument I already accepted for the
`direction` CHECK — the type refuses it and so does the table. **Ordered after RL-879**, so the
certificate CHECK mirrors corrected logic rather than the bug. *Cost if wrong:* three constraints the
sibling table also carries; the asymmetry would have been the finding either way.

Task 4: accepted without change — GRANT/REVOKE privileges (no table here has default privileges, so
`gip_app` would have had zero access), the two-layer append-only pattern on `metric_certificates`, and the
one out-of-scope edit that forced: adding `"metric_certificates"` to `test_artifact_immutability.py`'s
derived `APPEND_ONLY_TABLES`. All three are necessary and correctly reported.

Task 2 (reopened): RL-879 fixed — commit `30b6388`, 13 tests. The implementer confirmed the new
positive test **fails against the pre-fix validator** before accepting it, which is the discrimination
check this slice learned to demand. Contracts unchanged (23/23).

Task 2 (reopened): hazard noted, no action — the implementer used `git stash` to test the pre-fix state.
This repository shares one stash stack across all worktrees and concurrent sessions, so a bare
`git stash`/`pop` can pop another session's work. It restored correctly and the tree is clean, so nothing
to undo; **future dispatches in this slice carry an explicit instruction not to use bare stash.**

Task 4: fix round 1/5 (3 addressed, 0 open — undeletable trigger, phase-1-template CHECK,
certificate-required CHECK; commits ee81ca0..cd719a1) plus a **TRUNCATE guard added unprompted**, on the
correct reasoning that a row-level BEFORE DELETE trigger does not fire on TRUNCATE in Postgres. Verified
against this repo's own precedent: migration `e1f2a3b4c5d6` states it explicitly and six other tables use
the same row+statement pair. Without it the undeletable guarantee had a hole.

Task 4: review — spec ✅, quality **Approved**, 0 Critical, 0 Important, 1 Minor. The reviewer verified
everything **live against the database** rather than from the diff: `\d custom_metrics` for each
constraint, and it broke two invariants in turn (disabled the immutability trigger; dropped the
certificate CHECK), confirmed the guarding test reported `DID NOT RAISE`, restored, cleaned up the rows the
broken window let through, and re-ran to 20 passed with all triggers back at `tgenabled='O'`.
**The question that mattered came back right:** the CHECK and the Python validator now agree — both exempt
`draft` and `deprecated` — so RL-879's fix did not simply move the bug one layer down. Migration
reverses (`downgrade -1` then `upgrade head`, twice). Tests confirmed **not skipped** (DSN exported).
Shape drift checked field by field: all 12 `CustomMetric` fields present with matching nullability, and the
trigger's frozen-column list accounts for every one.

Task 4: minor (deferred): `metric_certificates` is not in `test_artifact_immutability.py`'s parametrized
owner-connection UPDATE/DELETE/TRUNCATE test, though the structural test does confirm both triggers exist
on it. Low risk — `artifact_append_only()` is shared, unmodified, and behaviourally proven by six other
tables including its structural sibling `objective_certificates`. For the final review to triage.

Task 4: complete (commits c29554d..cd719a1, review clean after 1 fix round)

Task 5: implementer DONE — commit `49bc16d`, 6 tests, ruff 0, mypy 0 (129 files), audit-docs clean. It
found 3 more brief defects (the same three classes as before) and **two real bugs in its own new router
code**, self-reviewed and fixed: `params: dict[str, float]` silently coercing money away from `int`, and a
`SubmitCustomMetric` body FastAPI wrongly required despite all-default fields.

Task 5: **RL-881 — a declared lifecycle edge is unreachable again, and it is the same defect class as
RL-879.** `backend/src/app/api/approvals.py:320,326` dispatches an approval decision to
`modelling_service.apply_approval_decision` and `objectives_service.apply_approval_decision`. There is no
metrics equivalent, and `platform/metrics.py` defines none — so a Custom Metric can be submitted
(`certified → review`) and **can never reach `approved`**, even though `VALID_METRIC_TRANSITIONS[REVIEW]`
declares `{APPROVED, CERTIFIED}` and FR-154 requires the same lifecycle as objectives. Load-bearing:
governance requires an approved artifact for an approved model (R4), so without this every model evaluated
on a custom metric is permanently unapprovable. **Fix in this task**, mirroring `objectives.py:548` and
wiring it at the same call site, with a test driving `certified → review → approved`.
*Cost if wrong:* one more dispatch branch in a file that already has two.

Task 5: **RL-882 — a live bug in shipped code, found by building the parallel path. Fixing it, out of
scope, in its own commit.** `backend/src/app/api/custom_objectives.py:85` declares
`params: dict[str, float]`, so Pydantic coerces an incoming `250000` to `250000.0` before
`TemplateParameter.check` sees it — and that method **raises** for `kind == "money_minor" and not
isinstance(value, int)` (`objectives.py:206-211`). The consequence is not precision loss but total
unreachability: **`capped_gamma` and `spliced_severity` cannot be created through `POST
/api/v1/custom-objectives` at all**, because both carry a money parameter and every value is a float by
the time it is checked. Two of the thirteen shipped templates. The class whose own docstring explains why
money must be integer minor units (*"a cap that arrives as 25000.0 ... is off by a factor of a hundred, and
nothing about the number says so"*) is defeated by an annotation one layer above it. The correct form is
already proven in this branch — `custom_metrics.py:84` uses `dict[str, int | float]`. **I am fixing it
rather than only reporting it**: it is one line, the fix is proven, money discipline is a
retrofit-impossible foundation (`CLAUDE.md` §7, roadmap §5), and a governed pricing platform that silently
refuses its own money templates is the failure that rule exists to prevent. Kept in a **separate commit**
so the record of what this slice changed stays legible. *Cost if wrong:* a one-line widening at an API
boundary where `check()` still enforces the real rule; strictly more permissive than today and covered by a
regression test.

Task 5: deferred to the final review — `EVIDENCE_FLOOR` has no `custom_metric` entry (`06` §4.2 policy
defaults). That is OQ-639-shaped governance policy rather than a code defect, and this slice should not
decide it.

Task 5: fix round 1/5 (2 addressed, 0 open; commits 49bc16d..040e6e8). `deb49e7` — FR-154's
approval lifecycle: `apply_approval_decision` + `_target_status` mirroring objectives, wired into
`approvals._carry_to_the_artifact`, with a positive `certified → review → approved` test and a negative
mirror. `040e6e8` — the out-of-scope money fix, in its own commit, **with the regression test confirmed
failing against the unfixed annotation first** (422, `TemplateParameter.check` rejecting `250000.0`).
70 tests, ruff 0, mypy 0 (129 files), contracts `--check` clean, audit-docs clean.

Task 5: **RL-883 — the `DEFAULT_POLICY` entry is accepted on precedent, not as a fresh governance
decision.** Implementing Finding 1 surfaced a third gap: `DEFAULT_POLICY` had no `custom_metric` entry, so
`certified → review` returned 409 before `apply_approval_decision` could ever be reached — the lifecycle
was blocked two layers deep. I had deferred `EVIDENCE_FLOOR` as OQ-639-shaped and did not want this slice
inventing governance policy. It did not: `backend/src/app/platform/perils.py:288` records that
*"`DEFAULT_POLICY` gained the entry with this slice"* for peril structures, so **a slice adding an
approvable artifact type adding its policy entry is this repository's established pattern**, and the entry
mirrors `custom_objective`'s (evidence: `metric_certificate`). Accepted.

Task 5: **RL-884 — and the spec owes the matching note, which Task 7 must write.** `06` §4.2's JSON
block enumerates these entries by artifact type and carries the exact precedent in a dated note:
*"`peril_structure` added 2026-08-18 (WK-661, the peril-structure slice)."* The code now has a `custom_metric`
entry the spec does not list, which is a spec-vs-code divergence, and `CLAUDE.md` §0 says resolve it rather
than let it sit. **Task 7 adds `custom_metric` to `06` §4.2 with a dated note in the `peril_structure`
style.** Recorded here rather than dispatched now because Task 7 is the documentation task and the branch
merges as one PR, so spec and code still land together. *Cost if wrong:* if Task 7 misses it, the branch
merges with `06` describing a policy default the code has and the spec does not — caught by this ledger
line at the final review.

Task 5: review — spec ✅, quality **Approved**, 0 Critical, 0 Important, 2 Minor. All six §5.1 routes
exist with the declared status codes, and `certify` was confirmed **202-with-a-Job by reading the route
body**, not the decorator. Both retrofit-impossible foundations verified at the mechanism: `metrics.py`
contains **zero** `unit_of_work` calls (every `audit.record` uses the caller's session), and
`record_certificate` only ever `session.add`s a new row — with the live grant checked via `\dp
metric_certificates` showing `INSERT`+`SELECT` and no `UPDATE`. The reviewer independently reverted the
money annotation, watched the regression test fail with *"parameter 'cap' is money and must be integer
minor units, not 250000.0"*, restored, and confirmed a clean tree. It read the lifecycle test's assertions
rather than its name and confirmed it reaches `MetricStatus.APPROVED`. 8 + 37 + 7 tests, none skipped.

Task 5: minor (deferred): the `metric_certificates` append-only trigger has no dedicated negative test —
a **pre-existing gap shared with `objective_certificates`**, not a regression from this task. Pairs with
Task 4's deferred minor about the same table. For the final review to triage together.

Task 5: minor (deferred): `apply_approval_decision`'s "no such row" branch is untested, mirroring the same
untested tolerance in `objectives.py`. Low-risk boilerplate.

Task 5: complete (commits cd719a1..040e6e8, review clean after 1 fix round)

Task 6: **RL-885 — Task 6 extends the derived error-code test to the GBM arm, because it is about to
add three codes nothing checks.** `backend/tests/test_spec_hash.py:108`'s
`test_every_code_the_fit_path_can_raise_is_registered` parses the AST of **`glm.py` only**, collecting
`GlmFitError` raise sites and asserting each code is registered. Its own docstring says it exists so *"a
new named failure is covered on the day it lands"* — but the GBM arm has no equivalent, so Task 6's
`METRIC_REF_UNRESOLVED`, `METRIC_NOT_APPLICABLE` and `METRIC_NOT_FITTABLE` would be raised by `gbm.py` and
derived by nothing. Extending it to walk `gbm.py`/`GbmFitError` is cheap and makes the three new codes
evidenced rather than asserted (`CLAUDE.md` §13.4). Distinct from OQ-548, which is spec-vs-registry; this
is code-vs-registry, and the mechanism to close it already exists one module over.
*Cost if wrong:* the extended test flags a pre-existing unregistered GBM code, which would be a finding
worth having rather than a defect introduced.

Task 6: implementer DONE — commit `35ba563`. `test_gbm.py` 79 passed, `test_model_jobs_gbm.py` 14 passed,
`test_spec_hash.py` 11 passed; ruff/mypy/lint-imports clean project-wide. **The narrowing did not become a
removal:** `test_early_stopping_under_a_custom_objective_is_refused_by_name` still passes on both backends.

Task 6: **two genuine runtime defects found by executing a fit, neither in the brief nor findable by
reading.** (i) XGBoost's eval-log parser splits on `:`, and a custom metric ref *is*
`custom_metric:<slug>@<version>` — so declaring one raised `too many values to unpack`. (ii) XGBoost
silently leaks its own default `rmse` into the eval curve when only custom metrics are declared, so the
curve reported a metric nobody asked for. Fixed narrowly: a sanitize/translate-back helper for the name,
and `disable_default_eval_metric` scoped to exactly that branch. LightGBM needed neither. **These are the
class of defect no amount of spec-reading finds** — the first is a format collision between this
repository's own ref grammar and XGBoost's log format, and the second is a library default asserting
itself. Recorded because they justify the slice's shape: the plan's final task was the one that ran the
thing end to end.

Task 6: **RL-885 discharged, and it came back clean.** The AST-walk extension to
`test_spec_hash.py` now covers `gbm.py`/`GbmFitError` as well as `glm.py`/`GlmFitError`, and found **zero**
unregistered GBM codes — Task 5 had already registered all three. A verification rather than a fix, and the
mechanism now exists for the next slice that adds a GBM failure.

Task 6: to be assessed at review — `test_model_jobs_gbm.py` duplicates a `_certified_objective` helper
locally rather than importing it from `test_custom_objectives.py`, because that file already imports
`_gbm_spec` from this one and the pair would deadlock at module load. Duplication is normally a smell; a
circular import is a real reason. The reviewer decides whether the shape is right.

Task 6: review — spec ✅, quality **Approved**, 0 Critical, **1 Important**, and the verification was the
most thorough of the slice. The reviewer deleted **all three** refusal guards in turn (not the one I asked
for), confirmed each target test failed, restored, and re-ran to baseline after every cycle. It broke the
extended AST walk by injecting a bogus `GbmFitError("NOT_A_REAL_CODE")` into `gbm.py` and confirmed the
`gbm` parametrisation failed while the `glm` one passed — proving the parametrisation walks two modules
rather than one twice, which a passing test alone would not have shown. It proved the colon sanitiser is
**lossless by grammar, not by inspection**: `Slug` admits no underscore or colon and no `ARTIFACT_TYPES`
member contains `:` or `__`, so `replace(":", "__")` is injective over every valid ref. And it confirmed
`disable_default_eval_metric` is scoped exactly — a declared builtin sets `eval_metric` explicitly and the
`elif` never fires, so a metric the user asked for is never dropped. 110 tests, **0 skipped**.

Task 6: **RL-886 — the Important finding is real and gets fixed, not pinned.** `_fit_lightgbm`'s
`stopping_on_custom` branch narrows `feval_entries` to the single stopping target, so a spec declaring two
custom eval metrics and stopping on one reports **only that one** on LightGBM while XGBoost reports both.
The reviewer confirmed this by running a real fit on each backend rather than reasoning about it. Two
reasons to fix rather than document: `gbm.py`'s own module docstring commits to FR-119's *"one
contract, two backends"*, and nothing in FR-159/160 records a backend-specific reduction — so the
asymmetry is undeclared as well as undesirable. The reviewer's mechanism argument is that
`first_metric_only` decides *which metric stops the fit*, not *which metrics are reported*, making the
narrowing unnecessary. **If that turns out to be wrong the fallback is to pin the behaviour by name with a
test and a stated reason** — what must not survive is a divergence nothing records and no test covers.
*Cost if wrong:* LightGBM's early stopping targets the wrong metric, which the existing stopping tests
would catch immediately.

Task 6: fix round 1/5 (1 addressed, 0 open; commits 35ba563..d8859a2). **Widened, and the premise was
verified rather than assumed:** the implementer read LightGBM's `_EarlyStoppingCallback` source and
confirmed `first_metric_only` selects by name-equality against whatever lands at eval-result position 0 —
decided purely by `feval`'s return order, not by which metrics are reported. So it reordered
`feval_entries` with the stopping target first instead of narrowing. Stopping iteration confirmed unchanged
on both backends and invariant to dict insertion order; the new backend-parametrised test was **proven to
fail on the pre-fix code** by deliberate revert-and-rerun, then restored. 81 + 14 + 11 tests, gates clean.

Task 6: accepted omission, stated rather than assumed — no job-level two-metric test. The defect lived
entirely in `gbm.py`; the job level only resolves refs and wires them, which is already covered. The
implementer flagged this rather than quietly skipping it, which is the right call.

Task 6: re-review — **ADDRESSED, no new breakage.** The re-reviewer reproduced the revert-and-rerun itself
(narrowed `feval_entries` back, watched `[lightgbm]` fail with the second metric missing while `[xgboost]`
passed, restored from a file copy rather than `git stash`, confirmed a clean tree) and then **traced the
vendored LightGBM source** to settle the ordering question rather than trusting the implementer's reading:
`_EarlyStoppingCallback._init` takes `evaluation_result_list[0].metric_name`, `Booster.__inner_eval`
appends `feval`'s results in return order, `_lgb_custom_feval` iterates the dict, and dict insertion order
is a **language guarantee** since 3.7 — so with the stopping target placed first structurally the ordering
is guaranteed, not incidental. It also confirmed `params["metric"]="None"` keeps any implicit builtin from
occupying position 0. 81 + 25 tests, 12 early-stopping tests including both protected refusal
parametrisations, nothing skipped.

Task 6: complete (commits 040e6e8..d8859a2, review clean after 1 fix round)

Task 7: **the agent stalled waiting on a Monitor notification that cannot arrive**, despite the dispatch
telling it to run the suite in the foreground. Same failure this repository has hit before: a backgrounded
long command never wakes a stopped subagent. **Resumed, not re-dispatched** — its work was intact and
re-dispatching would have thrown away a completed gate run. Told it to poll or run in the foreground with a
generous timeout and to avoid Monitor entirely.

Task 7: **it reported observing two pytest failures before stalling, and those are now the priority.**
Asked for full node ids, assertions and a diagnosis before any fix, and to distinguish two cases
explicitly: a **real regression from this branch** (six tasks touched the GBM fit path, the approval
lifecycle and the schema — a failure outside this slice's own files would be the most important finding of
the whole slice) versus an **environment or ordering artefact** (shared database state in a full-suite run,
an unmigrated test database, or `libgomp1`), which must be proven by running the test in isolation and
reporting both results. Also asked whether the DSN was exported for that run, since without it ~90 tests
skip silently and some assume a migrated database — which changes what the failures mean.

Task 7: **three real failures, all from this branch, none an environment artefact** — each reproduced in
isolation with the DSN exported. Everything else green: ruff, mypy, lint-imports, audit-docs (489 reqs, 72
OQs), req-coverage 235 of 489 marked, contracts 23 `--check` clean, **frontend fully green** (install,
generate:api, lint, type-check, 131 tests, build), and **`scope-audit MODEL --endpoints` reads 40 of 40**.

Task 7: **RL-887 — failure 1 is a real omission and is fixed.** `JobKind` gained `metric.certify` in
`49bc16d`, so the *generated* `job.schema.json` carries it, but the **hand-authored** Phase-0
`docs/contracts/schemas/job.schema.json` was never updated. `CLAUDE.md` §2 records `docs/contracts/` as
partly generated and partly hand-written, and this is the seam between the two halves. Fix the
hand-authored file. *Cost if wrong:* none — the two files are meant to agree and a test says so.

Task 7: **RL-856 — failure 2 is a real omission, and I misinformed the Task 5 dispatch.** The three
`METRIC_*` codes reached `errors.py` and a prose "Amended 2026-08-19" note, but never the
`**Error codes owned by this module:**` catalogue block that `test_every_error_code_pricing_core_raises_is_registered_and_declared`
actually parses. Every prior addition — `MODEL_APPROXIMATION_INVALID` included — added the code to the list
**and** wrote a note; this one wrote only the note. **My dispatch told the implementer "nothing
cross-checks those two lists (OQ-548), so this is discipline rather than an enforced check." That was too
broad and it is worth correcting:** OQ-548 is about spec-vs-`errors.py` in general, but this repository
*does* check the subset of codes `pricing-core` raises, against both the registry and the spec catalogue —
and that check is what caught this. The implementer followed my framing and I sent it the wrong one.
*Cost if wrong:* none; adding the codes to the catalogue is what every sibling did.

Task 7: **RL-888 — failure 3 is a stale test assumption, and the reason it went stale is a milestone.**
`test_demo_guide.py` hardcodes `{"MODEL","RATE"} <= modules`, where `modules` are those with an endpoint a
spec declares and the contract lacks. **MODEL is now 40 of 40 published**, so it correctly dropped out of
that set — the code is right and the test's assumption is stale. Narrow the expectation to `{"RATE"}`, and
**record the milestone in the slice record**: MODEL is the first module in this repository with every
declared endpoint published, and this slice's Task 1 + Task 5 are what closed the last gap. A test that
encodes "these modules are incomplete" will go stale again by design, which is worth a sentence in its
docstring. *Cost if wrong:* the guide's derivation is unchanged; only the test's expectation moves.

Task 7: **the full-suite gate earned its place.** All three defects were invisible to the per-task scoped
runs — every task was green in isolation. This is the argument for `CLAUDE.md` §11's insistence on running
both halves rather than trusting accumulated per-task greens.

Task 7: complete (commit f3689dd) — Step 0's `06` §4.2 entry, all three gate-found fixes, and the slice
record in one commit. **Full gate green, numbers as printed:** pytest **1412 passed, 0 failed** in 272.7 s ·
ruff 0 · mypy 0 · lint-imports 0 · audit-docs 0 (**489 requirements**, 72 open questions all mirrored,
**131 error codes** — up from 128, the three METRIC_* codes now in the catalogue) · req-coverage
**235 of 489 marked (48.1 %)** · `generate-contracts --check` 0, **23 contracts match** ·
`scope-audit MODEL --endpoints` **40 declared / 40 published (100 %)** · frontend install, generate:api,
lint, type-check, **131 tests**, build all clean.

Task 7: **MODEL is the first module in this repository with every declared endpoint published.** 34 of 35
before this slice; Task 1 declared five more and Task 5 published all six.

Task 7: no push, no PR — correct. The brief's Step 5 calls for one but my live dispatch asked only for
commits, and the agent flagged the discrepancy rather than acting on the wider of the two instructions.
Pushing is the controller's call and belongs after the final whole-branch review.

## Deferred minors, for the final review to triage

- Task 1: the unstruck tail of `02`'s deferred-endpoint amendment is now stale framing.
- Task 1: `open-questions.md` carries bolded `**FR-MODEL-N**` cross-references; proven unable to trip the
  define-once check, which globs `specs/*.md` only.
- Task 3: `scale_behaviour` is WARN-only with a generous `1e3` threshold; real but lenient.
- Task 4 + Task 5 (same table, raised twice): `metric_certificates` has no dedicated negative test for its
  append-only trigger, and is absent from the parametrised owner-connection UPDATE/DELETE/TRUNCATE test.
  A pre-existing gap shared with `objective_certificates`, not a regression.
- Task 5: `apply_approval_decision`'s "no such row" branch is untested, mirroring the same untested
  tolerance in `objectives.py`.

## Final whole-branch review — **DO NOT MERGE**, 2 Critical, 4 Important

The reviewer re-ran the whole gate independently (1412 passed, 0 skipped; audit 489/72/131; 23 contracts;
40/40 endpoints; lint-imports 3 kept) and verified every number the slice record states. It then found what
1412 green tests could not, **by instrumenting the libraries rather than reading the code**.

**C1 (Critical) — `evaluate_metric` never resolves template parameter defaults; 10 of 12 templates raise
`KeyError`.** `metrics.py:57` passes `dict(metric.params)` — the author's raw params — straight into the
loss. `compile_objective` (`objectives.py:641-646`) resolves defaults first, and its docstring says why the
artifact stores only the author's choice: *"a stored artifact that silently gained §4.5's defaults would
make a later change to a default rewrite the meaning of an approved objective."* The metric path inherited
the storage half and not the resolution half. **Compounded by a half-copied validator:**
`CustomMetric._the_parameters_are_the_templates_own` (`metrics.py:125-127`) checks unknown keys and omits
the missing-required branch its sibling has — whose docstring states *"a missing key with no default is a
template that cannot be evaluated at all."* Net effect measured: `POST /custom-metrics` returns **201** for
`capped_gamma` with no `cap`, and certification then dies on a bare `KeyError` instead of a governed error.
Falsifies §4.13's own stated invariant, which this branch wrote.

**C2 (Critical) — early stopping binds to the wrong metric, with a *guessed* direction.** `gbm.py:878-897`
applies the explicit metric-binding remedy only on the `stopping_on_custom` branch; line 897's `else` uses
the shorthand the code's own comment calls *"exactly ambiguous once a custom metric is also being
reported."* The reviewer instrumented `xgb.callback.EarlyStopping._update_rounds`: with a spec naming a
**builtin** stopping metric and a custom metric also declared, XGBoost bound
`custom_metric__poisson-nll@1` with `maximize=False` against a metric declaring `higher_is_better`. That is
FR-156's stated failure verbatim — *"stops the fit at the wrong round in exactly half of cases, and
produces a fitted model rather than an error."* **LightGBM Case A is a regression this branch introduced
with no custom metric involved**: honouring `eval_metrics` registered reporting metrics as stopping
metrics, and `first_metric_only=False` halts when any of them stalls.

**Why the suite missed both:** every fixture supplies a complete param set for a zero- or one-parameter
template. `test_gbm.py`'s `_metric()`, `test_custom_metrics_api.py:28` and `test_metrics.py:55` all encode
the one input shape that works.

**Important:** I3 LightGBM drops declared *builtin* eval metrics (RL-886's defect, second instance);
I4 `EVIDENCE_FLOOR` has no `custom_metric` entry **and `metrics.py:643-647` claims a control the code does
not have**; I5 `MetricUsage` defined in `backend/` rather than `model-schema` (RL-876's argument not
extended to the usage pair); I6 the roadmap's own `WK-661 — outstanding work` table still says 34/35 and lists
custom metrics as unbuilt, **contradicting the new slice record 30 lines below it**.

**Ruling audit — two of mine judged wrong, and both criticisms are accepted.**
*RL-886 was incomplete and its own fallback was not applied:* it generalised from the custom-vs-custom
asymmetry to "fixed" while `params["metric"]="None"` produces the identical one for builtins and the `else`
branch a worse one. Its own words were *"what must not survive is a divergence nothing records and no test
covers"* — two survived. *RL-883 was over-extended:* the `perils.py` precedent covers `DEFAULT_POLICY`
and establishes nothing about `EVIDENCE_FLOOR`, and FR-364's empty-floor rule is scoped to artifacts
§3.3 **predates** — which `custom_metric` does not, since this slice created it. I deferred a gap this
slice made as though it were a pre-existing governance question, and it then fell out of the record
entirely. **RL-882 (the out-of-scope money fix) was judged right**, on the grounds that the rule is
retrofit-impossible, the fix was already proven in-branch, and it stayed in its own commit — with the fair
caution that it made the reviewer's job harder and would not survive that defence at 200 lines.

**Process finding worth keeping:** all four structural defects live *at the seam between a task and the
sibling it claims to mirror* — half a validator copied, half a remedy applied, one shape in the wrong
package, one floor entry not mirrored. Every per-task review compared the task to its brief and found it
correct. None could ask whether the sibling's contract was inherited whole. **"Diff the new artifact
against the one it says it mirrors, field by field and validator by validator"** would have caught C1, I3
and I5 mechanically.

Final fix wave: commits `c59a283` (C1 + C2) and `9d33539` (I4 + I6). **Gate green: pytest 1449 passed,
0 skipped** (was 1412) in 276 s · ruff 0 · mypy 0 (129 files) · lint-imports 3 kept · audit-docs 0
(489 requirements, 72 OQs, 131 error codes) · req-coverage 235/489 (48.1 %) · contracts 23 `--check` ·
**scope-audit MODEL 40/40**.

Final fix wave: **LightGBM took explicit binding, not a pinned limitation** — verified empirically that
LightGBM preserves `params["metric"]` order in `evaluation_result_list`, so the builtin branch moves the
stopping metric to the front and `first_metric_only` is now `True` whenever stopping is configured. One
genuine limitation *is* pinned with a test and a stated reason: LightGBM evaluates builtins before `feval`,
so a spec stopping on a Custom Metric while also declaring a builtin gets the builtin suppressed rather
than stopped on, where XGBoost reports both. That is RL-886's fallback applied properly this time —
declared and covered rather than silent.

Final fix wave: **enforcement proven on broken input for every fix** — `dict(metric.params)` restored → 6
catalogue `KeyError`s; the validator half removed → 5 `DID NOT RAISE`; LightGBM's reorder reverted →
`assert 25 == 66`; XGBoost's shorthand restored → `assert 27 == 95` and `assert 6 == 22`.

Final fix wave: **two test-design notes that are the best evidence this slice learned its own lesson.**
`rmse` was rejected as the second builtin because it stalls at the same round as `poisson-nloglik` on
LightGBM — *the test would have passed against the bug*; `mae` was chosen because it diverges (95/22,
66/25). The custom-capture test uses `quantile@alpha=0.9` because a near-copy of `poisson-nloglik` agrees
by coincidence. Both are the discrimination check that my own vacuous weights test failed at Task 3.

Final fix wave: still open and **now recorded rather than lost** — `06` §3.3's `custom_metric` evidence row
and its `EVIDENCE_FLOOR` entry, owner WK-661, in that order. This is the gap RL-883 mis-deferred; it is in
the slice record's "Not delivered" list now.

## Scoped re-review of the final fix wave — all four ADDRESSED, **safe to merge**

Verified by reproduction, not reading. It reverted `evaluate_metric` to `dict(metric.params)` (6 of 12
catalogue `KeyError`s, exactly as reported), restored XGBoost's shorthand (2 failures — and `[last-xgboost]`
passed, which is *why* parametrising over both declaration orders is load-bearing rather than decorative),
and additionally broke LightGBM's reorder and `first_metric_only` on its own initiative. Tree clean at
`9d33539` after every cycle. **C1's fix was better than briefed:** `resolve_template_params` was *extracted*
from `compile_objective` and both now call it — one mechanism, not two — and it found **three** unresolved
call sites where I had named one.

**The load-bearing LightGBM claim survives a discriminating probe.** Rather than confirm the ordering held
for the metrics tested, the re-reviewer ran **all 24 permutations** of four metrics and got 24 distinct
outputs matching 24 distinct inputs — an unordered container returns the *same* order for every input, so
24-for-24 means output order is the identity of input order. Backed structurally by `basic.py:5350-5413`
(builtins before `feval`, by code rather than observation). Explicit binding was right, not lucky.

**The tests discriminate, and the fixer's rejection reason was measured.** `mae` vs `poisson-nloglik`
diverge 95/22 (XGB) and 66/25 (LGB); `rmse` stalls at **25 on LightGBM, identical to `poisson-nloglik`** —
so an `rmse`-based test would have passed against the broken binding, exactly as claimed. One honest limit
the re-reviewer volunteered: the LightGBM half of the custom-capture test does not discriminate (that path
already had the builtin alone), and its docstring says so — a consistency assertion, not a regression guard.

**RL-889 — the residual is parked, and raised as an open question rather than decided.** LightGBM
evaluates builtins before `feval`, so a spec stopping on a Custom Metric while also declaring a builtin
gets the builtin **silently dropped**: accepted, never evaluated, and nothing on the returned `GbmFit` says
so. That is a narrower instance of the exact defect FR-159 was raised against. It is **pre-existing
on this branch** (`params["metric"]="None"` predates the fix wave and appears as unchanged context), and it
is now tested and named in `02` FR-160's 2026-08-20 amendment — so it is a *documented* asymmetry,
not a silent one. But whether a documented silent drop satisfies FR-159's "honoured", or whether the
combination should be refused outright, is a **design choice the spec leaves open** — and `CLAUDE.md` §0
says record it with options and a recommendation rather than pick one. The re-reviewer's own analysis rules
out the obvious third path: reimplementing LightGBM's builtin as an `feval` entry would emit a curve
labelled `rmse` that is not LightGBM's `rmse`, which is worse and violates FR-159's "passed to the
backend's own metric vocabulary". *Cost if wrong:* a caller declaring that combination gets one fewer
metric than asked for, with the fit itself unaffected.

Gate confirmed independently: **1449 passed, nothing skipped** (run with `-rs`, DB-backed tests visible in
the warnings summary so they executed rather than skipped) · ruff 0 · mypy 0 · lint-imports 3 kept ·
audit-docs 0 · req-coverage 235/489 · contracts 23 · MODEL 40/40. `scope-audit` exits 1 by design while
unevidenced requirements remain (19, all pre-existing, all with verdicts on file).
