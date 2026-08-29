# W11 Slice 2 decision-point rulings — DP1 and DP2, the two decisions that block Tasks 2.2 and 2.3 (2026-08-29)

**What this is.** [`.claude/roles/decision-maker.md`](../../.claude/roles/decision-maker.md)
requires every decision point to be pre-resolved *before* its slice starts. DP1 and DP2 are
stated in full in the frozen plan
[`2026-08-29-w11-scoring.md`](2026-08-29-w11-scoring.md) (its "Decision points — unruled"
section) and are the two the plan marks `[BLOCKED]` on Slice 2's Tasks 2.2 and 2.3. A frozen
plan is never edited — this is its dated sibling, the same treatment
[`2026-08-29-w11-prework-rulings.md`](2026-08-29-w11-prework-rulings.md) gave Rulings 1–5 and
[`2026-08-29-w11-slice1-rulings.md`](2026-08-29-w11-slice1-rulings.md) gave Rulings 6–13.

**Numbering continues that record at 14.** Rulings 1–5 and 6–13 are its; nothing here reuses
a number, for the same reason [`CLAUDE.md`](../../CLAUDE.md) §5 gives for requirement ids. A
ruling is cited as "Ruling N" plus the file it lives in, never by bare number.

**Mints no `FR-`/`NFR-`/`OQ-` id.** Every requirement id below is already defined in
`docs/specs/`. One error code is appended to an existing owned-code block — error codes are a
separate namespace from `FR-`/`NFR-`/`OQ-` ids, exactly as Ruling 11 recorded when it appended
`MODEL_CALL_FAILED`, and this paragraph does not cover them.

**Every line number, route, field name, enum member and requirement id below was read against
`origin/main` at `9891be1` — the tree this branch is cut from, and identical to local `HEAD`
at the time of writing.** `gh pr list --state open` at the same moment returned one open pull
request, `#395` (`docs(skills): scope-audit.py's --extra comma list does not inherit a
prefix`), which rules on nothing here. Where a claim inherited from an earlier document turned
out to be wrong against that tree, this record says which claim is wrong in its own first
sentence rather than hedging — [`../process/delivery-process.md`](../process/delivery-process.md)
§15.

**A plan's recommendation is not a ruling, and neither of the plan's two recommendations
survives intact.** DP1's recommendation, **(b)**, is upheld and made precise in three places
it left open. DP2's recommendation, **(a)**, is **refused as constructed**: built the way the
plan describes it, it would make `review` unreachable for every Rating Version and turn two
shipped tests red. What replaces it is neither of the plan's two options.

**One §14 plan review already covers this ground and binds nothing.**
[`../audit/plan-reviews.md`](../audit/plan-reviews.md) review 8 §5 reaches the same
conclusion about the workstream cut and says in terms that the deferral itself "is W11's own
plan's job (its DP1 and DP2), not this review's". Its own acceptance line reads
*"Maintainer acceptance: _pending._"* at `9891be1`, and the consolidated table below it says
*"no recommendation above binds until this line carries a date and a decision."* It is cited
below as corroborating reasoning and never as authority. Its two line citations, `03:160` for
FR-RATE-34 and `03:172` for FR-RATE-40, are each one short of the current tree (`:161` and
`:173`); the frozen plan copied both. The requirements are the ones intended, and this record
uses the `9891be1` numbers.

---

## Ruling 14 — DP1: `POST /api/v1/score` takes an explicit `rating_version_ref` in W11, and refuses rather than guesses when it is absent

**The decision, restated.** DP1 asks how `POST /api/v1/score`'s default path — no explicit
`rating_version_ref` — resolves *"the Rating Version currently live in the target
environment"* (FR-RATE-34, [`../specs/03-rating-engine.md`](../specs/03-rating-engine.md)`:161`)
when FR-RATE-23 (`:134`) makes `live` a property of a **Deployment**, and Deployment
(FR-RATE-50, `03` §3.10 `:193`) together with the Environment entity itself
(FR-PLAT-28, [`../specs/07-platform.md`](../specs/07-platform.md)`:139`) are both W14's
([`../roadmap.md`](../roadmap.md)`:379`). Options as the plan states them: **(a)** pull a
minimal Environment plus live-pointer forward into W11; **(b)** defer — the endpoint requires
an explicit ref until W14, as a named register deferral; **(c)** a throwaway placeholder
pointer.

**Ruled: (b).** With three clauses the plan's (b) does not state, each of which an executor
would otherwise have to guess.

### Why (b), and why (a) is not the cheap option it looks like

- **There is nothing to resolve *to*, and that is a fact about the repository rather than
  about the schedule.** At `9891be1` no `Deployment` type exists anywhere
  (`git grep "class Deployment" -- packages backend` returns nothing), no migration creates a
  `deployments` or `environments` table, and no code path ever assigns
  `RatingVersionStatus.LIVE` — `VALID_RATING_VERSION_TRANSITIONS`
  ([`../../packages/model-schema/src/model_schema/rating.py`](../../packages/model-schema/src/model_schema/rating.py)`:49-59`)
  maps both `LIVE` and `RETIRED` to `frozenset()`, and that file's own comment at `:46-47`
  already says why: *"`live` and `retired` are unreachable here — their transitions are
  W14's, because FR-RATE-23 makes `live` a property of a Deployment."* The half that *does*
  exist is the environment **scope**, not the pointer: a Service Account carries
  `environments: list[str]`
  ([`../../backend/src/app/db/models.py`](../../backend/src/app/db/models.py)`:392`) with the
  comment at `:389-391` citing FR-PLAT-30. So the target environment of a call is already
  derivable; what is missing is which version is live in it, and that is a Deployment record.
- **(a) cannot be cut down to a pointer without becoming (c).** FR-RATE-50 (`03:193`) makes a
  Deployment record who, when, why and the bundle hash; FR-PLAT-29 (`07:140`) enforces
  promotion order against prior deployment history, which
  [`../workflows/wf-04-deploy-and-monitor.md`](../workflows/wf-04-deploy-and-monitor.md)`:48`
  step C2 shows depends on that history existing; FR-RATE-51 requires atomic switchover with
  pre-warming and FR-RATE-55 an audit event. A `(workspace, environment) → rating_version_id`
  row carries none of them. It is not a smaller (a); it is (c) with better manners, and (c) is
  undocumented shadow-modelling of a shape `03` §3.10 already defines precisely.
- **No workflow before `wf-04` exercises the default path.** Both of FR-RATE-34's citations
  outside `03` and the roadmap are in `wf-04` — step A4 (`:30`), where a Consumer System
  scores test quotes *after* step A1 has already created a Deployment, and step C6 (`:52`).
  Deferring the default path to W14 therefore removes nothing any earlier journey needs.
- **Scope, if (a) were taken, would make two closure records wrong.** FR-PLAT-28..31 sit in
  W14's roadmap row (`:379`); `CLAUDE.md` §13 derives closure scope from the specification
  first. Building part of FR-PLAT-28 under W11's name puts a requirement in two workstreams'
  evidence and neither's scope.

### Clause 1 — the deferral lives at the endpoint, never in the shape

**`options.rating_version_ref` stays optional and nullable.** This is the spec's own position
and not merely the contract's: `03` §4.4's `QuoteContext` example (`:395`) is literally
`"options": {"trace": true, "rating_version_ref": null}`, and FR-RATE-35 (`:162`) says
scoring *"accepts"* an explicit ref *"for what-if and testing"* — a field the specified design
treats as an addition to a default cannot be required by the shape that carries it. The
hand-authored contract agrees (`docs/contracts/schemas/scoring.schema.json:20`, inside
`options`, `oneOf` an artifact ref or `null`; `QuoteContext`'s `required` array at `:8` is
`["purpose", "quoted_at", "effective_date", "inputs"]`), but the contract is the corroboration
here, not the authority — Ruling 12 in the Slice 1 record establishes that this exact file can
be the stale side.

There is also a mechanical reason not to put the deferral in the shape, and it is one Slice 1
arms. Ruling 12's obligation 4 binds Task 1.4 to add the scoring shapes to
`scripts/generate-contracts.py`'s `GENERATED_SHAPES` and to lift `"scoring"` from
`backend/tests/test_contracts.py`'s exclusion dict — at `9891be1` that dict still carries
`"scoring": "later-phase — 03 rating"`. From the moment Task 1.4 lands, the generated
`QuoteContext` is compared against the hand-authored one. A `model-schema` shape that made the
ref required would then land as drift, and the tempting repair — editing the authored contract
to match the code — is `CLAUDE.md` §0's forbidden direction.

### Clause 2 — the refusal is a permanent branch with a typed code, not a stub

Omitting the ref means *"this platform has no live Rating Version to score you against."*
That is not a W11 artefact: it is exactly the answer W14's resolver must give when the target
environment holds no Deployment. So W11 ships the real branch with its trigger unconditional,
and W14 narrows the trigger rather than deleting a stub.

**One error code, appended to `03` §5.1's owned block in this ruling's own commit:
`NO_LIVE_RATING_VERSION`, HTTP **409**.** 409 is this backend's established status for *"the
artifact is not in a state that permits this"* — `platform/datasets.py:568`,
`platform/jobs.py:214`, `platform/rating_versions.py:160` and
`platform/approvals.py:427` all refuse state at 409 — and it is the right signal here,
because the caller's operator resolves it by deploying a version and retrying. `03` §5.1's
`/score` row and the Phase-0 OpenAPI stub declare a `default` Problem response, which covers
it; the generated document is the enforced one in any case
([`../../docs/contracts/README.md`](../../docs/contracts/README.md)).

**Task 2.1 owes the code's registration**: `NO_LIVE_RATING_VERSION` must join
`RATING_ERROR_CODES` in [`../../backend/src/app/errors.py`](../../backend/src/app/errors.py)`:275-307`
in the same PR as the route. `PlatformError.__init__` (`:344-348`) raises `ValueError` on an
unregistered code, so the branch cannot be written before the code is registered — which is
the mechanism that stops this ruling being half-applied.

### Clause 3 — FR-RATE-35's two restrictions are scoped to `prod` and W11 imposes neither

The frozen plan's Task 2.1 tells the executor the endpoint *"resolves an explicit
`rating_version_ref` (FR-RATE-35 — `prod` restricts to `approved` versions, records as
`what_if`)"*. Read without the requirement in front of you, that reads as two things to
implement. It is not. FR-RATE-35's full text is: *"Scoring accepts an explicit
`rating_version_ref` for what-if and testing; **in `prod`** this is permitted only for
`approved` versions and is recorded as a `what_if` purpose, never as a quotable price."* Both
restrictions sit inside the `prod` clause. W11 has no environments, therefore no `prod`,
therefore neither restriction applies.

**Ruled:** W11 does **not** restrict the explicit-ref path to `approved` versions and does
**not** rewrite `QuoteContext.purpose` to `what_if`. `purpose` is a required, caller-supplied
field with the five members Ruling 12 fixed, and scoring a `draft` or `review` version by
explicit reference is precisely the *"what-if and testing"* FR-RATE-35 permits. Imposing the
`prod` restrictions unconditionally would forbid the only use the endpoint has before W14.
W14 imposes them when `prod` exists.

### Disposition

- **Task 2.2 ("Default-live resolution") is not built in W11.** It is W14's, with the rest of
  FR-RATE-50 and FR-PLAT-28. Slice 2 loses that task and gains one refusal branch plus its
  test inside Task 2.1.
- **Spec change in this commit:** `NO_LIVE_RATING_VERSION` appended to `03` §5.1's owned
  error-code block with a dated marker. No requirement is amended: FR-RATE-34 and FR-RATE-35
  read exactly as intended, and a deferral is a status fact, which `CLAUDE.md` §9 keeps in the
  roadmap and the register rather than in a spec.
- **Owed at the W11 close, and not this role's to write:** a row in
  [`../audit/register.md`](../audit/register.md) recording FR-RATE-34's default-live path as
  *carry forward with an owner — W14*. `CLAUDE.md` §12 and §13 put the four verdicts and the
  register row with the audit and the lead, not here.

**Acceptance test — the thing that must be true, stated as the violation that must become
expressible.** Before this ruling no test could express *"the platform refused to guess which
version is live"*, because no route existed to refuse anything: `POST /api/v1/score` is absent
from every router at `9891be1` (`backend/src/app/main.py:110-129` lists 19 routers and no
scoring one; `docs/contracts/openapi/generated.json` has no `/api/v1/score` path). After it,
that refusal is an assertion an auditor can run: a `QuoteContext` posted with
`"options": {"rating_version_ref": null}`, or with `options` omitted entirely, must return
**409 `NO_LIVE_RATING_VERSION`**. **The ruling has been overridden if any build answers that
request with a 200** — whichever version it chose, it guessed. And it has been overridden in
the other direction if `model-schema`'s generated `QuoteContext` ever places
`rating_version_ref`, or its parent `options`, in a `required` array: `03` §4.4's own example
carries the null, so a required field puts the code above its own specification. At `9891be1`
`QuoteContext` exists in no Python file in the repository, so both halves start from zero.

---

## Ruling 15 — DP2: FR-RATE-40 splits into four limbs; W11 delivers one, defers two with owners, and does not wire a gate that could only refuse everything

**The decision, restated.** DP2 asks whether W11 builds FR-RATE-40's approval gate
(`03:173`) now — *"vacuously refusing until W12/W13 exist"*, in the plan's own words — or
defers the whole requirement, given that the gate names a passing Regression Suite
(FR-RATE-44, `03:177`, **W12**) and a Dislocation Run (FR-RATE-46, `03:184`, **W13**), neither
built. Options as the plan states them: **(a)** build now, partial, extending
`submit_for_review` with an evidence-presence check and refusing with `EVIDENCE_INCOMPLETE`;
**(b)** defer the whole requirement to whichever of W12/W13 lands last.

**Ruled: neither, as stated.** FR-RATE-40 is a conjunction of four preconditions, and they do
not share a disposition. Splitting it at its own `and`s is what makes the answer visible:

| Limb of FR-RATE-40 | Disposition | Owner |
|---|---|---|
| A change summary (FR-RATE-27) | **Already enforced today.** W11 owes a test that names FR-RATE-40 | W11 |
| A passing Regression Suite (FR-RATE-44) | Deferred — the artifact does not exist | W12 |
| A Dislocation Run over an agreed portfolio (FR-RATE-46) | Deferred — the artifact does not exist | W13 |
| A passing GIPP check, *where the insurer has enabled it* | Not started, conditional — no failing case is constructible until `04` ships | the optimisation workstream |
| *(the wiring: `effective_evidence("rating_version")` at submission)* | **Not W11's.** Lands with the last enabler | W13 |

### Why (b) — "defer the whole requirement" — is wrong

**One of the four limbs is enforced on `main` right now.** `approvals.submit` refuses a blank
change summary before it does anything else:
[`../../backend/src/app/platform/approvals.py`](../../backend/src/app/platform/approvals.py)`:170-177`
raises `PlatformError("VALIDATION_FAILED", "A change summary is required", 422, ...)` with the
detail *"FR-GOV-10: submission requires a change summary."* Every rating-version submission
goes through it — `rating_versions.submit_for_review` calls `approvals.submit` at
[`../../backend/src/app/platform/rating_versions.py`](../../backend/src/app/platform/rating_versions.py)`:166-172`
with `artifact_ref=ArtifactRef(type="rating_version", ...)`. Booking FR-RATE-40 as wholly
deferred would record as absent a control the repository already has, which is the failure
mode `CLAUDE.md` §13 names in the other direction as loudly as a missing one. What it lacks is
attribution: the refusal cites FR-GOV-10 and no test names FR-RATE-40, so `req-coverage.py`
cannot see it.

### Why (a) as the plan constructs it is refused — three independent reasons

**1. Wired today, the gate refuses every submission and turns two shipped tests red.** The
mechanism the other four artifact types use is `policy.effective_evidence(<type>)` — the union
of `EVIDENCE_FLOOR` and the workspace entry (FR-GOV-37, `06:145`) — followed by a fail-closed
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
and it is precisely the harm FR-GOV-37 was written to prevent: *"a default naming
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

**3. An already-adopted register row puts the dislocation limb in W13.** `F-W9-2`
([`../audit/register.md`](../audit/register.md)`:24`), filed at the W9 close, carries
FR-RATE-61 — *"approximation-mode Rating Versions cannot reach `approved` without a Dislocation
Run"* — forward with *"an owner — W13 (FR-RATE-46, the Dislocation Run it needs, is W13's; the
check itself specialises FR-RATE-40's general approval-evidence gate, which W11 builds)"*. The
special case is already W13's on the ground that its artifact is W13's. The general case cannot
be enforced in W11 on a ground the specialisation was excused from.

Note what that row does *and does not* settle: it says W11 builds the general gate, which is
why this ruling does not defer FR-RATE-40 wholesale. It does not say W11 builds it out of
artifacts that do not exist.

### What W11 actually owes

One test, and no production code. `backend/tests/test_rating_versions.py` gains a case marked
`@pytest.mark.req("FR-RATE-40")` — the marker form the file already uses at `:65`, `:111`,
`:133` — asserting that submitting a rating version with a blank or whitespace-only
`change_summary` is refused with **422**, so the change-summary limb becomes visible to
`req-coverage.py` under the requirement that actually demands it rather than only under
FR-GOV-10.

`rating_versions.submit_for_review` gains no evidence check in W11.

### Disposition

- **No spec change.** FR-RATE-40 reads exactly as intended, and where its gate is enforced is
  already fixed by `06` FR-GOV-19 (`:109`, *"enforced at submission"*) and by `03` §5.1's
  submit row (`:515`). Nothing here is a design gap; the limbs' owners are status, which
  `CLAUDE.md` §9 keeps in the roadmap and the register.
- **Owed at the W11 close, and not this role's to write:** register rows for the regression-suite
  limb (owner W12), the dislocation-run limb (owner W13) and the wiring (owner W13), plus a
  `not started, conditional` verdict on the GIPP limb. The four verdicts are the lead's
  (`CLAUDE.md` §12).

**Acceptance test, stated as the violation that must become expressible.** Today no test can
express *"a Rating Version was refused because FR-RATE-40's evidence was incomplete"* — no
test anywhere names FR-RATE-40, and the one refusal that fires cites a different requirement.
After this ruling the expressible violation is: submit a rating version whose `change_summary`
is `"   "`, and a **422** must come back, from a test carrying `FR-RATE-40`. **The ruling has
been overridden in the other direction if any W11 commit makes
`rating_versions.submit_for_review` call `policy.effective_evidence("rating_version")`** — at
`9891be1` that call returns three kinds nothing can verify, so its arrival inside W11 is
observable directly as `backend/tests/test_rating_versions.py:84` and `:264` going red, with no
input change required to detect it.

---

## Findings reported, not ruled — the remedy is scope, and scope is the lead's

Three things were found while establishing the two rulings above. None is W11's to fix and
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
otherwise. But it is the thing W13 must resolve before it can wire the check, and
`structural_diff` has no owner named anywhere. Separately, FR-GOV-37's mechanism (i) requires
the floor to be *"restated in §4.2's own text"*; `06` §4.2's restatement
([`../specs/06-governance.md`](../specs/06-governance.md)`:290-295`) names the floor for
`model`, `validation_rule`, `custom_objective` and `peril_structure`, and omits
`rating_version`, `custom_metric` and `deployment` — three of the six keys `EVIDENCE_FLOOR`
actually holds. Candidate owner: **W17**, which FR-GOV-37 already names as the owner of
FR-GOV-9..19 and evidence enforcement.

**2. `EVIDENCE_FLOOR` has a `deployment` key and `DEFAULT_POLICY` has no `deployment`
entry.** A deployment submission would therefore be refused at `approvals.submit:181-188` with
*"No approval policy for this artifact type"* before any evidence was consulted — the
`peril_structure` defect that `06` §4.2's 2026-08-18 note records ("a correct refusal of an
artifact nobody could ever approve"), in a fourth artifact type. Nothing submits a deployment
today, so it is latent. Candidate owner: **W14**, which builds FR-RATE-50.

**3. `GOLDEN_QUOTE_MISMATCH` is owned by `03` §5.1 (`:533`) and is registered nowhere in
code.** It is absent from `RATING_ERROR_CODES` (`backend/src/app/errors.py:275-307`), so
`PlatformError("GOLDEN_QUOTE_MISMATCH", ...)` would raise `ValueError: unknown error code`.
This is the same spec-versus-code error-code gap the Slice 1 record's third finding describes
as categorical; it bites **W12**, which owns FR-RATE-43.

---

## Sources — read directly at `9891be1`, not inherited

- `docs/specs/03-rating-engine.md` — §2 glossary `:69`, §3.4 `:134`, §3.7 `:161-166`, §3.8
  `:173-177`, §3.9 `:184`, §3.10 `:193`, §4.4 `:385-421`, §5.1 `:505-541`.
- `docs/specs/06-governance.md` — FR-GOV-10/12/14 `:93-97`, §3.3 `:105-149`, FR-GOV-37 `:145`,
  §4.2 `:251-296`, §5.1 `:433-444`.
- `docs/specs/07-platform.md` — FR-PLAT-28..31 `:139-142`.
- `docs/open-questions.md` — OQ-GOV-7 `:158`.
- `docs/workflows/wf-02-model-to-rating-version.md` — Phase D/E `:70-103`;
  `wf-04-deploy-and-monitor.md` — Phases A/B/C `:20-52`.
- `docs/roadmap.md` — the W11–W14 workstream rows `:376-379`.
- `docs/audit/register.md` — the header and every row, F-W9-2 in full.
- `docs/audit/plan-reviews.md` — review 8 §5 and its consolidated table, `:800-895`.
- `docs/plans/2026-08-29-w11-scoring.md` — DP1/DP2/DP3 and Slice 2's tasks;
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
