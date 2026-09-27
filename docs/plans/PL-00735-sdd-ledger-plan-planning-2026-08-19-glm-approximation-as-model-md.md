---
id: PL-735
family: plan
kind: leaf
title: SDD ledger — plan: .planning/PL-00736-the-glm-approximation-as-a-model-implementation-plan.md
status: active                  # draft → active → superseded | retired (§1.2a)
created: 2026-08-19
owner: planner
supersedes: []
superseded_by: ~
corrected_by: []
relates: []                     # ids only
was: docs/plans/2026-08-19-glm-approximation-as-model-ledger.md
---

# SDD ledger — plan: .planning/PL-00736-the-glm-approximation-as-a-model-implementation-plan.md

Spec: `docs/specs/02-modelling.md` — FR-137 (§3.6), §4.4, §4.8, §4.9, §5.1, §5.2. Read, reachable.
Branch: `feat/glm-approximation-model`. BASE at start: ac5382f.
Decision gate answered by the maintainer before execution: **option A — the inline table stays as a legacy era, exclusive with `approximating_model_id`.**

## Pre-flight scan

### Pairs sharing a file or an interface

| Tasks | Produces → consumes | Finding |
|---|---|---|
| T1 → T5 | `MODEL_APPROXIMATION_INVALID` declared in `02` §5.1, registered in `backend/src/app/errors.py` | **DEFECT — see RL-864.** `backend/tests/test_errors.py::test_spec_error_codes_are_all_constructible` reads the spec's code list, so T1's commit reddens it and it stays red until T5. |
| T1 → T2..T5 | FR-141, the id every later `@pytest.mark.req` names | Consistent. `req-coverage.py` fails on a marker naming a requirement that does not exist, so T1 must land first — it does. |
| T2 → T3 | `SURROGATE_RESPONSE_COLUMN`, `GlmSpec.approximates_model_id` | Consistent. T3's `approximation_spec` sets both, satisfying T2's iff-validator. |
| T2 → T3 (regression risk) | `GlmApproximation`'s exclusivity validator vs the **existing** builder | Consistent, and checked: with T2 landed and T3 not yet, `build_glm_approximation` still returns the block with inline coefficients and no id — `inline=True`, `id is not None=False`, so the validator does not fire. T2 alone does not break `pricing-core`. |
| T3 → T4 | `GlmApproximationFit.{spec,result,r_squared,deviance_explained,worst_regions,train,holdout}`, `artifact_block(id)`, `approximation_spec(spec, *, source_model_id)` | Consistent — the names T4 Steps 5 and 6 read are the names T3 Steps 4 and 5 define. |
| T4 → T5 | `backend/tests/test_glm_approximation_model.py`, extended by both | Sequential only. No parallel dispatch of T4 and T5. |
| T4 → T5 | The handler's surrogate spec vs `_refuse_mismatched_approximation` | Consistent by construction: `approximation_spec` copies `dataset_version_id`, `split_ref` and `factors` from the source, which are exactly the three fields the refusal compares. |
| T2 → T6 | `spec_hash` v5 and the regenerated contracts | Consistent. T2 regenerates; T6 re-checks with `--check`. |

### Per-task self-consistency

| Task | Tests specified vs code specified | Finding |
|---|---|---|
| T1 | docs only, no tests; `audit-docs.py` is the check | Agrees with itself. Requirement count 482 → 483 is stated and checkable. |
| T2 | 6 schema prohibitions vs the two validators | Agrees. `Coefficient`'s constructor in the test was checked against `modelling.py:1119` while planning — `term/estimate/std_error/z/p_value/ci_95`, and `-2.4 ∈ [-2.44, -2.39]` satisfies the interval validator. |
| T3 | 2 new tests + 3 amended call sites vs the new return shape | Agrees. `fidelity_statement` was read while planning (`transparency.py:316-355`): it touches only `r_squared`, `deviance_explained`, `worst_regions` and the summary, so its signature is unaffected. |
| T4 | 4 end-to-end tests vs the handler rewrite | Agrees. The helper names imported from `test_model_jobs_gbm.py` are unverified and flagged in the plan's self-review — the implementer confirms them. |
| T5 | 3 refusal tests + 2 validator tests vs the refusal and the carve-out | Agrees. Two test bodies are elided with the file and line range to write them from (`test_paired_quantile_models.py:200-240`), deliberately, so they are written against the real shape rather than this plan's memory of it. |
| T6 | no tests; the gate is the check | Agrees. |

### Rulings made before execution

**RL-864 — the plan's task order is kept, and `test_errors.py::test_spec_error_codes_are_all_constructible` is expected red from T1 until T5.** The alternative was moving T5's one-line code registration into T1, which would put a backend source edit inside a docs-only commit to buy a green intermediate state nothing consumes. This repository has already met the shape and named it: a check that fires on the *contract* goes red at a slice's first commit rather than its last (PR #98). Every implementer dispatch for T2–T5 carries the expected-red test by name so nobody debugs it. *Cost if wrong:* an implementer wastes minutes on a known-red test — bounded by naming it in the dispatch.

**RL-865 — implementers run their task's scoped tests plus `ruff`/`mypy`, not the whole suite.** RL-864 makes a whole-suite run misleading until T5, and the full gate is Task 6's own deliverable. *Cost if wrong:* a cross-task regression surfaces at T6 rather than at the task that caused it; the task reviews and the final whole-branch review are the net.

**RL-866 — the plan's stated counts (482 → 483 requirements, 21 contracts, test tallies) are checkpoints, not acceptance criteria.** Implementers report the number the run prints. The gate is each command's own exit code. *Cost if wrong:* none.

## Task log

Task 1: implementer DONE — commit `1dc6110`, `audit-docs.py` exit 0, **483 requirements** (482 + 1),
66 open questions all mirrored, 128 error codes ownership exclusive. FR-201 confirmed as the
maximum before appending 102.

Task 1: **plan defect reported by the implementer.** The brief's Step 5 said to "replace the module's
old caveat" in `02` §4.9; no such caveat exists there — §4.9's JSON block runs straight into the
`### 4.10` heading. The implementer appended the note rather than inventing a removal, and said so.
**Ruling: the file is right and the brief's wording was wrong.** The caveat it meant is the *Python
module docstring* in `packages/model-schema/src/model_schema/transparency.py`, which Task 2 Step 4
updates — the brief conflated the spec section with the module that implements it. No action beyond
this note: the appended §4.9 text is what that section needed either way, and Task 2 still carries
the docstring edit. *Cost if wrong:* a stale sentence survives in one of the two places; Task 2's
review and the final whole-branch review both look at the same pair of files.

Task 1: review — spec ✅ (every step verbatim, in the named section; `audit-docs` rerun
independently at 483/66), quality **Not approved**, 1 Critical. The reviewer found the sentence the
brief's Step 5 was actually reaching for, one level up from where both I and the implementer looked:
**FR-137's own row** (`02` §3.6, line 172) still ends *"Until it is built,
`approximating_model_id` stays `None` and the artifact carries the coefficients"* and still carries
*"owner Phase 1b"* — contradicting the four "live from 2026-08-19" notes this same commit adds.

Task 1: **Ruling — the finding wins over the brief, and my Ruling above was half right.** The brief's
file list authorised only "a new requirement row" in §3.6, so the implementer's restraint was correct
under instruction-following and it disclosed rather than patched. But the plan is an argument about
the spec and the **spec is the binding authority**: a requirement that contradicts itself, in the one
row five later tasks are written against, is a worse defect than an unauthorised edit. `CLAUDE.md` §5
makes the requirement's *text* permanent, not immune to amendment — FR-171 and FR-187 both
carry dated in-row amendments for exactly this. So the fix **appends** a dated correction and deletes
nothing. My earlier ruling stands only for the second half: the module docstring is still Task 2's.
*Cost if wrong:* one paragraph of amendment prose in a requirement row, visible in the PR diff and
cheap to reword.

Task 1: fix round 1/5 (1 addressed pending re-review, 0 open; commit `1dc6110`..`e73256c`). Append-only
amendment to FR-137's row; `audit-docs` exit 0 with the count **unchanged at 483** — an amendment
adds no requirement, which is the number that proves it. The implementer additionally grepped for
surviving "unbuilt" claims and found 8 more matches, judging all out of scope: they belong to
OQ-582, OQ-639, FR-207, FR-208 and two notes, plus OQ-577's own DECIDED summary
in `open-questions.md` and its `02` §10 mirror — the last two left under the convention OQ-579
set, where a decision record keeps its summary and only the Recommendation column gains the "Built"
note. Sent to the scoped re-review to spot-check that last judgement rather than taking it on trust.

Task 1: re-review round 1 — finding **ADDRESSED**, no new breakage. The re-reviewer compared the `-`
and `+` lines word for word and confirmed the original sentence, the "owner Phase 1b" parenthetical
and the trailing "declared-and-unbuilt" clause all survive inside the appended amendment; all five
ruled points stated; `FR-141` still bolded exactly once; `audit-docs` exit 0 at 483.

Task 1: **the spot-check earned its keep — Ruling: the OQ-579 precedent does not cover
OQ-577's two summaries, and both get a built clause.** OQ-579's summary states only decision
*content*, so it cannot go stale; both of OQ-577's assert "owned by Phase 1b" *inside the
summary*, which is now a false scheduling claim. `02` §10's mirror (~line 2013) has no built
annotation anywhere near it — the identical failure mode as the Critical, relocated to the spec's own
open-questions section. `open-questions.md:55` is self-correcting (its resolution cell two columns
over already says "Built 2026-08-19") but is amended too, because `audit-docs` enforces the mirror and
two records of one decision that differ is the defect this repository names most often. Append-only
again; "owned by Phase 1b" stays, because it was true when the decision was taken. The implementer was
invited to argue back if its reading of OQ-579 survives a re-read. *Cost if wrong:* one redundant
clause in two decision records.

Task 1: fix round 2/5 (1 addressed pending re-review, 0 open; commit `e73256c`..`267ca0b`). Identical
`**Built 2026-08-19 (WK-661).**` clause appended beside the "owned by Phase 1b" claim in both rows,
nothing deleted; `audit-docs` exit 0, 483 requirements, 66 questions mirrored. The implementer agreed
with the ruling on its own reading rather than complying with it, and returned a fact that corrects
mine: **`audit-docs`'s mirror check is presence-only** — the id must appear bolded in both files, and
the surrounding prose is never compared. So the mirror was never at risk from divergent wording, and
my reason for amending `open-questions.md:55` alongside the genuinely misleading `02` §10 row was
wrong. The edit stands on the second reason only: two records of one decision that differ is the
defect this repository names most often, and a self-correcting contradiction is still a contradiction.

Task 1: re-review round 2 — **ADDRESSED**, all six checks pass, `audit-docs` exit 0 (483 / 66).
Task 1: complete (commits `ac5382f`..`267ca0b`, review clean).

Task 2: implementer DONE — commit `4b2db8c`. model-schema + `test_spec_hash.py` **182 passed**, ruff 0,
mypy 0 (125 files), `generate-contracts --check` 0 with **3** files touched.

Task 2: **my pre-flight scan was wrong, and the run found the half I missed.** The scan's
"T2 → T3 (regression risk)" row checked `GlmApproximation`'s exclusivity validator against the old
builder and called the pair consistent. It is — but I never checked the *other* new validator against
the same code. `pricing-core`'s `build_glm_approximation` constructs an internal `GlmSpec` with the
literal `"__gbm_prediction__"` response column and no source model, which FR-141's iff-validator
now refuses: 12 tests red at `transparency.py:95`. **I verified the cause myself** rather than taking
the implementer's word, because "expected red" is exactly where a real break hides —
`ValidationError: response_column is '__gbm_prediction__' and no approximates_model_id names the model
it approximates`. **Ruling: accept it as Task 3's scope.** It is inherent to the ordering, it is the
validator doing precisely its job — the one place in the codebase that built a surrogate spec without
naming its source is the one place it caught — and Task 3 is the next dispatch. *Cost if wrong:*
`pricing-core` is red for one commit; nothing consumes the branch mid-flight. The scan lesson stands:
checking one of two new validators against old callers is not checking the pair.

Task 2: review — spec ✅ (all nine steps verbatim), quality **Approved, zero findings**. The reviewer
re-ran the gate itself rather than trusting the report (ruff 0 · mypy 0, 125 files · `generate-contracts
--check` 0, 21 contracts match · 182 passed), hand-checked **all four combinations** of each validator's
boolean logic, and — the check that mattered most — **constructed a legacy `GlmApproximation` itself**
(inline coefficients, no id) and confirmed it still validates, so artifacts written before this slice
stay readable. It also adjudicated the implementer's three concerns and upheld all three: the brief's
file list was stale against its own Step 1, the brief's predicted 4th contract file was simply wrong
(a cross-field validator is invisible to JSON Schema generation), and the two extra `v4`/`v3` literal
bumps in `test_spec_hash.py` were necessary and weaken nothing.
Task 2: complete (commits `267ca0b`..`4b2db8c`, review clean).

Task 3: implementer DONE — commit `15c2ced`. `test_transparency.py` **12 failed / 7 passed → 23 passed**,
ruff 0, `lint-imports` 0 (ADR-703 intact), model-schema 172 passed as the regression check. `mypy` exits
1 with **4 errors, all in `backend/src/app/worker/model_handlers.py`** — the old call site, which is
Task 4's; nothing inside `packages/`.

Task 3: **third brief defect of the branch, same shape as the first two.** My Step 6 named 3 call sites
of `build_glm_approximation` to amend; the file has **6**, all of them among the 12 red tests. The
implementer amended all six and documented the discrepancy rather than either stopping at three (leaving
the suite red) or silently expanding. Sent to review with an explicit instruction to check whether any
of the six had its *assertions* weakened while its call was updated — going green by loosening a test is
the failure mode a count discrepancy invites.

Task 3: review — spec ✅ (all eight steps), quality **Approved**, no Critical or Important. Verified
independently: `lint-imports` 0 / 3 contracts kept, `mypy` exit 1 with **exactly 4 errors, all at
`model_handlers.py:703,703,733,735`** and none inside `packages/`, `test_transparency.py` **23 passed**,
and no literal `"__gbm_prediction__"` left in `pricing-core/src`. It traced the maths by hand:
`fit_glm`, `predict_glm` (for both R² and deviance) and `_worst_regions` all read the **train** frame;
the holdout is scored, guarded and returned but never fed into any of them.

Task 3: three Minors recorded for the final review's triage — (i) the brief's 3-vs-6 call-site
undercount, correctly handled; (ii) **my reviewing brief was itself wrong**: I told the reviewer
`holdout=data` was scoped to the two new tests, but Step 6 prescribes it for all six, and the reviewer
checked rather than accepted it — none of those six exercises a train/holdout distinction, so the
pattern is right there; (iii) the one assertion removed anywhere was
`assert approximation.target == "gbm_prediction"`, which tested a hardcoded default that could never
fail — its removal is a wash, not a weakening. **No assertion was substantively weakened.**
Task 3: complete (commits `4b2db8c`..`15c2ced`, review clean).

Task 4: implementer DONE — commit `8684327`. **47 passed / 0 failed** (4 new + 43 regression), `mypy`
**exit 0, 125 files** — the four errors at `:703`×2/`:733`/`:735` are gone — ruff 0, `lint-imports` 0.

Task 4: **enforcement proven, including the proof that failed to fail.** Proofs 1 and 3 reddened as
predicted (`MODEL_IMMUTABLE` when `record_fit` is unconditional; the covariance `BlobRef` surviving into
`fit_result`). Proof 2 — feeding the train frame as its own holdout — **reddened nothing**, which the
brief anticipated and asked to be reported honestly rather than papered over. The implementer went one
better and closed the hole: added
`assert diagnostics.universal.holdout.rows != diagnostics.universal.train.rows`, then re-ran it under
the still-broken handler to confirm it now catches it (`assert 313 != 313`; correct 313/311). Sent to
review to judge whether that assertion is a good test or a brittle one — it pins a two-row difference
on one fixture.

Task 4: **plan defect, and the most dangerous one so far — Ruling: my Step 8 restore instruction was
wrong and destructive.** I wrote `git checkout -- <file>` to undo each deliberate break. That reverts to
`HEAD`, not to the working state, so with the task uncommitted it **wiped the entire `_transparency`
rewrite** after the first proof. The implementer re-spliced, kept a known-good copy and restored by
`cp` for the remaining proofs. The fix belongs in a skill, not just here: an enforcement proof must
commit or stash first, or copy the file aside. Flagged to Task 6's skill-update step, and the reviewer
is checking the committed code against the brief especially closely, since a recovery from an
accidental revert is exactly where something silently goes missing. *Cost if wrong:* a lost hunk that
tests still pass over — which is why it is being checked by reading, not by the suite.

Task 4: two deliberate deviations from the brief, both judged sound and sent to review — `artifact_block`
bound once rather than called twice, and `load()` returning `source_slug`/`source_version` instead of a
`ModelRow` whose session is closed by the time `store()` runs. The second is a real lifecycle fix, not a
convenience. Also: `_actuary` lives in `test_model_jobs.py` and is only re-exported by
`test_model_jobs_gbm.py` — the brief guessed the wrong module of the two.

Task 4: review — spec ✅ (nine steps, compared line by line against the brief), quality **Approved**,
2 Important + 2 Minor. All five hard checks pass, each verified at the mechanism rather than the
comment: one `unit_of_work` with every inner call taking the handed session (`grep` over
`platform/` finds no other opener on this path); `should_fit` correct with `block` bound *outside* the
branch so both paths name the surrogate; `compute_diagnostics` fed `approximation.train/holdout` and
`approximation.spec`, so the A/E is against the booster's predictions and neither the original frames
nor the GBM spec reach it; the covariance strip applied to what is persisted; `Diagnostics(model_id=
surrogate.id)` not transposed. Gate re-run by the reviewer: 15 passed **0 skipped** (the DSN took),
mypy 0, ruff 0. It also confirmed the re-splice after the `git checkout` incident **dropped nothing** —
two files touched, tree clean, every element of the brief's snippet present.

Task 4: fix round 1/5 dispatched — 2 Important. **(i)** `MODEL_SPLIT_REQUIRED` and the >64-char slug
refusal are invariants this task introduced with **no test**; `CLAUDE.md` §13 makes a negative test per
invariant a closure condition, so **Ruling: fixed here, not deferred to Task 6** — my brief's omission,
this task's invariants. **(ii)** the assertion added in Step 8 pins an accident: `313 != 311` holds only
because this fixture's split does not divide evenly, so an even split would make it a false red — worse
than the silence it replaced. The reviewer found a strictly better form for free: compare against the
**GBM's own** diagnostics, computed over the same split, which pins the semantics ("the surrogate's
holdout *is* the holdout") and survives any fixture. Required proof that the replacement still catches
the original break before committing — and told it explicitly not to restore with `git checkout --`.

Task 4: fix round 1/5 (2 addressed pending re-review, 0 open; commits `8684327`..`7a925b6`). 6 tests in
the new file, 49 across it plus the regression set; mypy 0, ruff 0, `req-coverage` 0, each read
separately. **The replacement assertion was proven louder than the one it replaced**: re-applying the
proof-2 edit reddens it with `assert 313 == 87` — which names the population that went missing, where
`313 != 311` only said two numbers matched. Restored by `cp`, not `git checkout --`.

Task 4: **deferred minor for the final review's triage — a repository-level hole in testing refusals.**
The implementer reports that a `PlatformError` raised inside a Job handler is stored by the runner as
`JOB_HANDLER_FAILED` with the specific code visible only inside a message string, so **no test going
through `execute_job` can assert on a specific error code**. Both new tests therefore invoke the handler
directly, exactly as `tasks.py` does. If true this is not this slice's defect and not its job to fix —
it is a gap in how every refusal in this repository can be tested. Sent to the re-review to verify the
claim against the runner rather than record it on the implementer's word.

Task 4: re-review round 1 — **both findings ADDRESSED**, no new breakage. `holdout.rows !=` survives
nowhere (grepped across `backend/tests/` and `backend/src/`); the replacement compares against the GBM's
own diagnostics with no fixture integer anywhere in the file; the only production change is a 6-line
comment, placed exactly where a reader meets the reuse path. It judged both new negative tests genuinely
load-bearing rather than passing for the wrong reason: without the split guard the failure is an
`AssertionError` inside `_split_frames` and without the slug guard an asyncpg
`StringDataRightTruncationError`, **both outside `PlatformError`**, so `pytest.raises(PlatformError)`
fails to catch either — a real red. 6 passed / 0 skipped, mypy 0, ruff 0.

Task 4: **deferred minor CONFIRMED against the source, and it is a repository-level gap.**
`backend/src/app/worker/tasks.py`'s generic `except Exception` stores
`JobError(code="JOB_HANDLER_FAILED", message=f"{type(exc).__name__}: {exc}")`, and `PlatformError.
__init__` passes `detail or title` to `super()` — so the handler's own `.code` is **discarded entirely
and is not even a substring** of the stored message. No test going through `execute_job` can assert on
a specific error code from any handler. Not this slice's defect and out of its scope to fix; carried to
the final whole-branch review for triage.
Task 4: complete (commits `15c2ced`..`7a925b6`, review clean).

Task 5: implementer DONE — commit `f0fa0c2`. **51 passed** across `test_glm_approximation_model.py`,
`test_model_specs.py`, `test_errors.py` and `test_paired_quantile_models.py` (the regression check, since
this edits the function next to its refusal); ruff clean. Also corrected a brief defect: `PlatformError`
has no `.status`, it is `.status_code`.

Task 5: Step 8 proof — with the `_refuse_mismatched_approximation` call commented out all three refusal
tests reddened, and **the third reddened differently from the other two**: `FACTOR_RESOLUTION_FAILED`
instead of `MODEL_APPROXIMATION_INVALID`. That is the call-site *ordering* proving itself, not merely its
presence — a surrogate naming the wrong source model also fails factor resolution, and reported in the
wrong order it sends the caller to re-check factors that were never wrong. Restored via a `/tmp` copy.

Task 5: **RULING 1 WAS WRONG — its premise was false, and nothing on this branch was ever red.**
`test_errors.py::test_spec_error_codes_are_all_constructible` checks only `PLATFORM_ERROR_CODES` (`07`'s
codes) and never `MODELLING_ERROR_CODES`, so declaring `MODEL_APPROXIMATION_INVALID` in `02` §5.1 at
Task 1 reddened nothing. I told four implementers to expect a red test that was green. No harm done —
being told to ignore a passing test costs nothing — but the ruling was built on a mechanism I asserted
instead of checking, which is the failure this repository's own memory warns about.

Task 5: **the finding underneath it is worth more than the correction — a real enforcement gap.**
**Nothing in this repository cross-checks `02` §5.1's declared error codes against the registry that
makes them raisable.** A spec can declare a code no code registers, and no test, script or audit
notices — the same shape as the import-linter config that was dead for a day and reported success
throughout (`CLAUDE.md` §13.4). Out of this slice's scope to fix: FR-137 is about the approximating
Model, and `CLAUDE.md` §0 puts an unspecified capability in the spec before the code. **Ruling: record
it, do not build it here.** Carried into Task 6's brief for the roadmap and into the final review's
triage, so the maintainer decides. *Cost if wrong:* a real gap waits one slice; it has waited since
Phase 0.

Task 5: review — spec ✅ (nine steps), quality **Approved**, no Critical or Important. The check that
mattered most passes: the carve-out has a **real counterpart test** — an ordinary spec with
`response_column="claims_kount"` still reports `RESPONSE_MISSING` — so relaxing it for surrogates did not
quietly disable it for everything. Set comparison on `factors` confirmed in the committed code, call site
confirmed between the `interval_for` check and `_refuse_unusable_factors`, and the code registered in
`MODELLING_ERROR_CODES` rather than another module's set. It also read `approximation_spec` in
`pricing-core` and confirmed the **three fields the refusal compares are exactly the three the platform's
own surrogate-builder copies** — so a legitimate surrogate cannot fail the check by construction, while an
inconsistent hand-written one can. 51 passed / **0 skipped**, mypy 0, ruff 0; no expected-red test remains
anywhere on the branch.

Task 5: **the enforcement gap is wider than I recorded it.** The reviewer verified both halves
independently and found the absence is *structural, not `02`-specific*: `audit-docs.py`'s only error-code
check tests ownership exclusivity **between spec documents** and never opens `errors.py`; `scope-audit.py`
has no error-code check at all; `test_spec_hash.py::test_every_code_the_fit_path_can_raise_is_registered`
walks one `pricing-core` file's AST for raise sites, which is code-vs-registry rather than
spec-vs-registry. **Every module has the identical exposure** — `07` looks covered only because one test
names `PLATFORM_ERROR_CODES` specifically. Carried into Task 6 as an open question with options and a
recommendation, per `CLAUDE.md` §10, for the maintainer to decide.
Task 5: complete (commits `7a925b6`..`f0fa0c2`, review clean).

Task 6: implementer DONE — commit `7347d4a`. **Full gate green, both halves, each exit code read
separately.** Python/docs: ruff 0 · mypy 0 (125 files) · lint-imports 0 (1136 deps, 3 contracts kept) ·
**pytest 1360 passed, zero skipped** in 269 s · audit-docs 0 (**483 requirements**, 68 questions all
mirrored) · req-coverage 229/483 · `generate-contracts --check` 0, **21 contracts match** · demo-guide
11 passed. Frontend, from a clean `node_modules`: install / generate:api / lint / type-check / **131
tests, 21 files** / build, all 0.

Task 6: **it improved on my instruction for the measurement.** I offered "separate worktree, or report a
single honest number and say no baseline was taken"; it took the harder option — a detached worktree at
`main`'s tip — and measured the same test by name on both sides:
`test_a_transparency_artifact_is_built_and_read_back` **3.92 s on main vs 4.18 s on branch (+0.26 s,
~7 %)** for the second-frame scoring plus the full GLM diagnostics pass. New file's slowest test 1.85 s,
file total 9.86 s. `type_iii` left at its default rather than pulled as a lever, per the brief. Sent to
review with the question of whether one test's 7 % honestly carries the claim, or whether the measurement
is narrower than what it is being used to support.

Task 6: two open questions raised for the maintainer — **OQ-548** (nothing cross-checks a spec's
declared error codes against the `errors.py` registry; structural, every module) and **OQ-646**
(`PlatformError.code` discarded into `JOB_HANDLER_FAILED`, so no test through `execute_job` can assert a
specific code). Both `open`, both with options and a recommendation, both mirrored into `00-overview.md`
and `07-platform.md` §10. Roadmap: WK-661 "twenty" → "twenty-one" slices plus the FR-137/141 entry; 15
grep hits for stale claims all judged dated historical records the file preserves by convention — sent to
review to spot-check that judgement on three of them rather than accept it.

Task 6: skills — `python-package` gained the `model_copy` rule (it skips cross-field validators, which is
why Task 3 builds the artifact block through a method rather than copying one). For the destructive
`git checkout --` restore the implementer found the rule **already exists** in `python-test` from PR #72
and added a reinforcing entry rather than a duplicate. Sent to review to confirm the existing rule really
covers the failure this branch hit — if it does not, the reinforcing entry is a missed capture.

Task 6: review — spec ✅ (six steps), quality **Approved**, 1 Important + 1 Minor, both in the report's
narrative rather than in any committed artifact. The reviewer **re-ran the entire gate itself** and every
number matched exactly (1360 / 0 skipped; its 288.8 s against the implementer's 269.2 s is machine
variance). It read `tasks.py` and `errors.py` directly and confirmed **both OQ mechanisms are described
exactly right** — `PlatformError.__init__` does pass `detail or title` upward, `tasks.py` has no dedicated
`except PlatformError`, and `audit-docs.py`'s error-code check never opens `errors.py`. It **counted WK-661's
slice list by hand at 21 items**, confirming the corrected count. And it read `python-test`'s existing
rule from #72 — "silently discards the whole feature in that file, the injection *and* everything written
this session" — and judged it genuinely covers this branch's failure, so the reinforcing entry was right
and nothing was missed.

Task 6: fix round 1/5 dispatched — 1 Important. **The measurement is true and its caveat is missing.**
`_fitted_gbm` fits a GBM with **exactly one factor** (`factors=(area,)`), and the cost this slice adds is
type-III diagnostics **refitting the surrogate once per factor**. So "+0.26 s, ~7 %" measures the new code
path running exactly once, and reads as though it bounds the general case — `CLAUDE.md`'s own worked
example is a 40-factor GBM, forty refits. **Ruling: the number stays and gains its limit**, in the roadmap
where the next slice will read it, because §13.5 wants the measurement *and its budget* stated honestly
rather than favourably. *Cost if wrong:* two sentences of caveat on a figure nobody disputes.

Task 6: Minor — the report claimed the stale-claim grep returned 15 hits; the reviewer ran the identical
command on two revisions and got **28**. The *conclusion* survived its independent spot-check (the 7 lines
actually about `OQ-577`/`approximating_model_id` all sit in dated slice records or struck-through
decided rows, none misleading), so only the evidence count was wrong. Correction requested: a count nobody
can reproduce is not evidence, even when what it supports is true.

Task 6: fix round 1/5 (2 addressed pending re-review, 0 open; `7347d4a` amended to **`f2bbc30`** — the
branch is unpushed, so an amend costs nothing and nothing was force-pushed). Caveat now in WK-661's row beside
the number: *"measured at +0.26 s / ~7 % against a **single-factor** fixture; type-III diagnostics refit
the surrogate once per factor, so this does not bound a multi-factor model, and `type_iii=False` is the
lever if that ever bites, not pulled without the maintainer."* Count corrected to **28 hits, 7 of them
about this slice's subject** (roadmap lines 1721, 2075, 2117, 2639, 2735, 2781, 2782), the other 21
incidental matches on two broad search terms; the conclusion is unchanged and was independently
spot-checked. `audit-docs` exit 0, tree clean.

Task 6: **the branch's own table-cell hazard fired once more, and the audit caught it.** The first caveat
edit embedded literal newlines inside a pipe-table cell, splitting the row — `audit-docs.py` failed it
with "3 cells, header has 4" and the implementer rejoined it to one physical line before re-verifying.
That is the third time this repository's markdown-table rule has bitten someone on this branch's work, and
the check caught it every time.

Task 6: re-review round 1 — **ADDRESSED**, all five checks pass. Caveat inline in WK-661's row beside the
number, all three points stated, ~2 sentences, table row one physical line with no pipe inside backticks,
and only `docs/roadmap.md` touched. `audit-docs` exit 0 (483 / 68), tree clean.
Task 6: complete (commits `f0fa0c2`..`f2bbc30`, review clean).

## Final whole-branch review dispatched

9 commits, `ac5382f`..`f2bbc30`, on the most capable model. Scoped to the seams no task review could see —
the end-to-end trace of one transparency build, whether the surrogate concept is now defined twice
anywhere, whether a **pre-branch** artifact still validates and reads, generated contracts against what
`02` §4.4/§4.9 *require* rather than against the Python they came from, and whether every claim the branch
makes about itself in the specs, open questions and roadmap is true of the code as merged. Four deferred
items handed to it for triage: the `should_fit=False` determinism coupling, the twice-computed
`approximation_spec`, **OQ-548** and **OQ-646**.

Final review: **no merge blocker on correctness.** It traced the build end to end and confirmed the claim
the branch rests on **at the mechanism**: `diagnostics.py` reads actuals as `data[spec.response_column]`
(lines 347/473/581/785/961) and that column *is* `__gbm_prediction__`, so the A/E is against the booster
because the spec object says so — not because a comment does. `covariance_blob=None` reaches `record_fit`,
`Diagnostics(model_id=surrogate.id)` is not transposed, no permission regression, nothing defined twice,
contracts agree with what §4.4/§4.9 *require*, FR-141 defined exactly once and nothing renumbered.
All four deferred items judged **correctly deferred**.

Final review: two Important gaps, both cheap; one fix wave dispatched with two Minors folded in.
**(1) The legacy-compatibility guarantee has no positive test** — `GlmApproximation(` appears three times
in the suite and both inline-coefficient cases assert *refusal*, so deleting the legacy fields tomorrow
would leave the gate green. The option-A decision the maintainer took is protected by nothing the suite
can see. **(2) The `-approx` slug convention is in no specification** — the word appears nowhere in `02`
as a naming rule, yet a source slug over 57 characters fails a transparency build against the 64-character
column: a user-visible naming rule and a documented refusal owned by no requirement. Minors folded in: a
sentence saying the three compared fields are deliberate while `offset`/`weight`/`seed` are copied and not
compared, and a new `OQ-MODEL-` recording that a rebuild pays a full fit **plus one type-III refit per
factor** to produce numbers it discards.

Final review: **Low, parked — Ruling.** A stored block with *empty* `coefficients` and no id is now refused
on read. Unreachable in practice: the old builder always emitted at least an intercept, so the only
artifact that could 500 is one that cannot exist. Guarding a state nothing can produce buys a branch nobody
executes. *Cost if wrong:* one 500 on a hand-corrupted row, diagnosable from the validator's own message.

Final fix wave: commits **`e66e179`** (legacy-compatibility positive tests) and **`5c4927f`** (FR-141's
slug convention, the three-vs-six field note, **OQ-589**). Gate green: **pytest 1362 passed, zero
skipped** in 265 s · ruff 0 · mypy 0 (125 files) · audit-docs 0 — **483 requirements, 69 questions** all
mirrored · req-coverage 0 · `generate-contracts --check` 0, 21 contracts match.

Final fix wave: **the agent stalled mid-task and was resumed, not re-dispatched.** It backgrounded the
five-minute suite and stopped with "I'll hold here until the Monitor task notifies me" — a notification
that cannot arrive, because a backgrounded command never wakes a stopped subagent. Its work was intact and
uncommitted (exactly the four expected files), so resuming cost nothing; re-dispatching would have thrown
away a completed fix wave. Told it to poll or re-run in the **foreground** with a generous timeout and to
avoid Monitor entirely. It recorded the same environment note in its own report.
