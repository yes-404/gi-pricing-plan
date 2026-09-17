---
id: RL-881
family: ruling
title: DP2: FR-257 splits into four limbs; WK-671 delivers one, defers two with owners, and does not wire a gate that could only refuse everything
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-08-29
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-08-29-w11-slice2-rulings.md
---

## RL-881 — DP2: FR-257 splits into four limbs; WK-671 delivers one, defers two with owners, and does not wire a gate that could only refuse everything

**The decision, restated.** DP2 asks whether WK-671 builds FR-257's approval gate
(`03:173`) now — *"vacuously refusing until WK-672/WK-673 exist"*, in the plan's own words — or
defers the whole requirement, given that the gate names a passing Regression Suite
(FR-261, `03:177`, **WK-672**) and a Dislocation Run (FR-263, `03:184`, **WK-673**), neither
built. Options as the plan states them: **(a)** build now, partial, extending
`submit_for_review` with an evidence-presence check and refusing with `EVIDENCE_INCOMPLETE`;
**(b)** defer the whole requirement to whichever of WK-672/WK-673 lands last.

**Ruled: neither, as stated.** FR-257 is a conjunction of four preconditions, and they do
not share a disposition. Splitting it at its own `and`s is what makes the answer visible:

| Limb of FR-257 | Disposition | Owner |
|---|---|---|
| A change summary (FR-242) | **Already enforced today.** WK-671 owes a test that names FR-257 | WK-671 |
| A passing Regression Suite (FR-261) | Deferred — the artifact does not exist | WK-672 |
| A Dislocation Run over an agreed portfolio (FR-263) | Deferred — the artifact does not exist | WK-673 |
| A passing GIPP check, *where the insurer has enabled it* | Not started, conditional — no failing case is constructible until `04` ships | the optimisation workstream |
| *(the wiring: `effective_evidence("rating_version")` at submission)* | **Not WK-671's.** Lands with the last enabler | WK-673 |

### Why (b) — "defer the whole requirement" — is wrong

**One of the four limbs is enforced on `main` right now.** `approvals.submit` refuses a blank
change summary before it does anything else:
[`../../backend/src/app/platform/approvals.py`](../../backend/src/app/platform/approvals.py)`:170-177`
raises `PlatformError("VALIDATION_FAILED", "A change summary is required", 422, ...)` with the
detail *"FR-352: submission requires a change summary."* Every rating-version submission
goes through it — `rating_versions.submit_for_review` calls `approvals.submit` at
[`../../backend/src/app/platform/rating_versions.py`](../../backend/src/app/platform/rating_versions.py)`:166-172`
with `artifact_ref=ArtifactRef(type="rating_version", ...)`. Booking FR-257 as wholly
deferred would record as absent a control the repository already has, which is the failure
mode `CLAUDE.md` §13 names in the other direction as loudly as a missing one. What it lacks is
attribution: the refusal cites FR-352 and no test names FR-257, so `req-coverage.py`
cannot see it.

### Why (a) as the plan constructs it is refused — three independent reasons

**1. Wired today, the gate refuses every submission and turns two shipped tests red.** The
mechanism the other four artifact types use is `policy.effective_evidence(<type>)` — the union
of `EVIDENCE_FLOOR` and the workspace entry (FR-364, `06:145`) — followed by a fail-closed
loop over a `verifiable` map, the canonical instance being
[`../../backend/src/app/platform/modelling.py`](../../backend/src/app/platform/modelling.py)`:1238-1261`.
At `9891be1`, `effective_evidence("rating_version")` returns three kinds:
`EVIDENCE_FLOOR["rating_version"]` is
`("structural_diff", "regression_run", "dislocation_run")`
([`../../packages/model-schema/src/model_schema/approvals.py`](../../packages/model-schema/src/model_schema/approvals.py)`:106`)
and `DEFAULT_POLICY`'s `rating_version` entry ships the same three (`:254-259`). Nothing in the
repository can verify any of them, so `missing` would be all three and the raise would be
unconditional. Two shipped tests assert the opposite —
`backend/tests/test_rating_versions.py:84` (service level, and it goes on to drive the same
version to `approved` through `approval_service.decide`) and `:259-264` (HTTP level, asserting
`200` and `status == "review"`). `review` and `approved` would become unreachable for every
Rating Version in every workspace. That is not a strict gate; it is a lifecycle with no edges,
and it is precisely the harm FR-364 was written to prevent: *"a default naming
`model_comparison_if_predecessor` would have refused every model submission"* rather than
raise the standard.

**2. The plan's own literals would build the check in the wrong namespace.** Option (a) says to
check *"`evidence.regression_suite_run_id`/`evidence.dislocation_run_id` presence"*. Those
field names are correct — `RatingVersionEvidence`
([`../../packages/model-schema/src/model_schema/rating.py`](../../packages/model-schema/src/model_schema/rating.py)`:88-96`)
declares `regression_suite_run_id`, `dislocation_run_id`, `gipp_check_id` and
`structural_diff_blob`, all `| None = None` — and they are **not** the names the approval
policy uses. The policy catalogue's kind strings are `structural_diff`, `regression_run`,
`dislocation_run` (`approvals.py:106`, `:258`), and nothing maps one vocabulary to the other. A
check keyed on the model's field names bypasses `effective_evidence` entirely, so a workspace
policy could neither tighten it nor see it — the `transparency_artifact` versus
`transparency_artifact_if_non_glm` spelling defect that `06` §4.2's 2026-08-18 note records, a
second time. There is a second, independent reason such a check would refuse everything:
`RatingVersionEvidence` is **never written**. `row.evidence` is a nullable JSONB column
(`backend/src/app/db/models.py:1912`) and the only mention of it in any code path is a read
guarded by `if row.evidence else None` (`rating_versions.py:73`); a repository-wide grep for an
assignment to `.evidence` returns nothing.

**3. An already-adopted register row puts the dislocation limb in WK-673.** `F-W9-2`
([`../findings/register.md`](../findings/register.md)`:24`), filed at the WK-669 close, carries
FR-224 — *"approximation-mode Rating Versions cannot reach `approved` without a Dislocation
Run"* — forward with *"an owner — WK-673 (FR-263, the Dislocation Run it needs, is WK-673's; the
check itself specialises FR-257's general approval-evidence gate, which WK-671 builds)"*. The
special case is already WK-673's on the ground that its artifact is WK-673's. The general case cannot
be enforced in WK-671 on a ground the specialisation was excused from.

Note what that row does *and does not* settle: it says WK-671 builds the general gate, which is
why this ruling does not defer FR-257 wholesale. It does not say WK-671 builds it out of
artifacts that do not exist.

### What WK-671 actually owes

One test, and no production code. `backend/tests/test_rating_versions.py` gains a case marked
`@pytest.mark.req("FR-257")` — the marker form the file already uses at `:65`, `:111`,
`:133` — asserting that submitting a rating version with a blank or whitespace-only
`change_summary` is refused with **422**, so the change-summary limb becomes visible to
`req-coverage.py` under the requirement that actually demands it rather than only under
FR-352.

`rating_versions.submit_for_review` gains no evidence check in WK-671.

### Disposition

- **No spec change.** FR-257 reads exactly as intended, and where its gate is enforced is
  already fixed by `06` FR-363 (`:109`, *"enforced at submission"*) and by `03` §5.1's
  submit row (`:515`). Nothing here is a design gap; the limbs' owners are status, which
  `CLAUDE.md` §9 keeps in the roadmap and the register.
- **Owed at the WK-671 close, and not this role's to write:** register rows for the regression-suite
  limb (owner WK-672), the dislocation-run limb (owner WK-673) and the wiring (owner WK-673), plus a
  `not started, conditional` verdict on the GIPP limb. The four verdicts are the lead's
  (`CLAUDE.md` §12).

**Acceptance test, stated as the violation that must become expressible.** Today no test can
express *"a Rating Version was refused because FR-257's evidence was incomplete"* — no
test anywhere names FR-257, and the one refusal that fires cites a different requirement.
After this ruling the expressible violation is: submit a rating version whose `change_summary`
is `"   "`, and a **422** must come back, from a test carrying `FR-257`. **The ruling has
been overridden in the other direction if any WK-671 commit makes
`rating_versions.submit_for_review` call `policy.effective_evidence("rating_version")`** — at
`9891be1` that call returns three kinds nothing can verify, so its arrival inside WK-671 is
observable directly as `backend/tests/test_rating_versions.py:84` and `:264` going red, with no
input change required to detect it.

---

## Findings reported, not ruled — the remedy is scope, and scope is the lead's

Three things were found while establishing the two rulings above. None is WK-671's to fix and
none changes either disposition; each is filed here so the decision to act or not is
deliberate.

**1. `EVIDENCE_FLOOR["rating_version"]` contradicts the rule stated in its own docstring, and
`06` §4.2 does not restate it at all.** The constant's docstring
(`packages/model-schema/src/model_schema/approvals.py:79-100`) says the floor is §3.3's
*"**checkable projection**, not the whole table"*, because *"submission fails closed on an
evidence kind it cannot verify"*. Eight lines later the `rating_version` key names three kinds
nothing can verify. It is **inert and not exploitable** — `effective_evidence("rating_version")`
has no caller anywhere in `backend/src` (the only three production callers are
`modelling.py:1246`, `objectives.py:845`, `metrics.py:797`) — and this record must not imply
otherwise. But it is the thing WK-673 must resolve before it can wire the check, and
`structural_diff` has no owner named anywhere. Separately, FR-364's mechanism (i) requires
the floor to be *"restated in §4.2's own text"*; `06` §4.2's restatement
([`../specs/06-governance.md`](../specs/06-governance.md)`:290-295`) names the floor for
`model`, `validation_rule`, `custom_objective` and `peril_structure`, and omits
`rating_version`, `custom_metric` and `deployment` — three of the six keys `EVIDENCE_FLOOR`
actually holds. Candidate owner: **WK-677**, which FR-364 already names as the owner of
FR-351, FR-352, FR-353, FR-354, FR-355, FR-356, FR-357, FR-358, FR-359, FR-361, FR-363 and evidence enforcement.

**2. `EVIDENCE_FLOOR` has a `deployment` key and `DEFAULT_POLICY` has no `deployment`
entry.** A deployment submission would therefore be refused at `approvals.submit:181-188` with
*"No approval policy for this artifact type"* before any evidence was consulted — the
`peril_structure` defect that `06` §4.2's 2026-08-18 note records ("a correct refusal of an
artifact nobody could ever approve"), in a fourth artifact type. Nothing submits a deployment
today, so it is latent. Candidate owner: **WK-674**, which builds FR-267.

**3. `GOLDEN_QUOTE_MISMATCH` is owned by `03` §5.1 (`:533`) and is registered nowhere in
code.** It is absent from `RATING_ERROR_CODES` (`backend/src/app/errors.py:275-307`), so
`PlatformError("GOLDEN_QUOTE_MISMATCH", ...)` would raise `ValueError: unknown error code`.
This is the same spec-versus-code error-code gap the Slice 1 record's third finding describes
as categorical; it bites **WK-672**, which owns FR-260.

---

## Sources — read directly at `9891be1`, not inherited

- `docs/specs/03-rating-engine.md` — §2 glossary `:69`, §3.4 `:134`, §3.7 `:161-166`, §3.8
  `:173-177`, §3.9 `:184`, §3.10 `:193`, §4.4 `:385-421`, §5.1 `:505-541`.
- `docs/specs/06-governance.md` — FR-352/354/356 `:93-97`, §3.3 `:105-149`, FR-364 `:145`,
  §4.2 `:251-296`, §5.1 `:433-444`.
- `docs/specs/07-platform.md` — FR-428, FR-429, FR-430, FR-431 `:139-142`.
- `docs/open-questions.md` — OQ-639 `:158`.
- `docs/workflows/WF-00699-approved-models-to-approved-rating-version.md` — Phase D/E `:70-103`;
  `WF-701-deploy-and-monitor.md` — Phases A/B/C `:20-52`.
- `docs/roadmap.md` — the WK-671–WK-674 workstream rows `:376-379`.
- `docs/findings/register.md` — the header and every row, F-W9-2 in full.
- `docs/closures/INDEX.md#plan-reviewsmd` — review 8 §5 and its consolidated table, `:800-895`.
- `docs/plans/PL-00854-wk-671-scoring-sequenced-slice-plan.md` — DP1/DP2/DP3 and Slice 2's tasks;
  `2026-08-29-w11-slice1-rulings.md` Rulings 11 and 12 including the addendum and its three
  findings.
- `docs/contracts/README.md` (the authored-versus-generated table),
  `docs/contracts/schemas/scoring.schema.json`, `docs/contracts/openapi/gi-pricing.yaml`,
  `docs/contracts/openapi/generated.json`.
- Code: `packages/model-schema/src/model_schema/approvals.py`, `.../rating.py`,
  `backend/src/app/platform/approvals.py`, `.../rating_versions.py`, `.../modelling.py`,
  `backend/src/app/errors.py`, `backend/src/app/api/models.py`, `backend/src/app/main.py`,
  `backend/src/app/db/models.py`, `backend/src/app/config.py`,
  `backend/tests/test_rating_versions.py`, `backend/tests/test_contracts.py`, `.importlinter`.
