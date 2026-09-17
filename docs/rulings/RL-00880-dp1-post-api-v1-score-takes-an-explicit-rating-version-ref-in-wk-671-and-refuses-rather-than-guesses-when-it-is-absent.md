---
id: RL-880
family: ruling
title: DP1: `POST /api/v1/score` takes an explicit `rating_version_ref` in WK-671, and refuses rather than guesses when it is absent
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

# WK-671 Slice 2 decision-point rulings — DP1 and DP2, the two decisions that block Tasks 2.2 and 2.3 (2026-08-29)

**What this is.** [`.claude/roles/decision-maker.md`](../../.claude/roles/decision-maker.md)
requires every decision point to be pre-resolved *before* its slice starts. DP1 and DP2 are
stated in full in the frozen plan
[`../plans/PL-00854-wk-671-scoring-sequenced-slice-plan.md`](../plans/PL-00854-wk-671-scoring-sequenced-slice-plan.md) (its "Decision points — unruled"
section) and are the two the plan marks `[BLOCKED]` on Slice 2's Tasks 2.2 and 2.3. A frozen
plan is never edited — this is its dated sibling, the same treatment
[`RL-00868-score-one-s-real-time-path-async-evaluate-not-evaluate-executor-offload-and-whether-5-2-s-sync-convention-is-itself-the-defect.md`](RL-00868-score-one-s-real-time-path-async-evaluate-not-evaluate-executor-offload-and-whether-5-2-s-sync-convention-is-itself-the-defect.md) gave Rulings 1–5 and
[`RL-00879-03-5-2-s-money-block-the-code-is-right-and-the-spec-is-stale-in-more-places-than-f-w11-1-5-reports.md`](RL-00879-03-5-2-s-money-block-the-code-is-right-and-the-spec-is-stale-in-more-places-than-f-w11-1-5-reports.md) gave Rulings 6–13.

**Numbering continues that record at 14.** Rulings 1–5 and 6–13 are its; nothing here reuses
a number, for the same reason [`CLAUDE.md`](../../CLAUDE.md) §5 gives for requirement ids. A
ruling is cited as "Ruling N" plus the file it lives in, never by bare number.

**Mints no `FR-`/`NFR-`/`OQ-` id.** Every requirement id below is already defined in
`docs/specs/`. One error code is appended to an existing owned-code block — error codes are a
separate namespace from `FR-`/`NFR-`/`OQ-` ids, exactly as RL-877 recorded when it appended
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
[`../rfcs/RFC-00839-pending-proposals-for-the-14-review-at-wk-671-s-close.md`](../rfcs/RFC-00839-pending-proposals-for-the-14-review-at-wk-671-s-close.md) review 8 §5 reaches the same
conclusion about the workstream cut and says in terms that the deferral itself "is WK-671's own
plan's job (its DP1 and DP2), not this review's". Its own acceptance line reads
*"Maintainer acceptance: _pending._"* at `9891be1`, and the consolidated table below it says
*"no recommendation above binds until this line carries a date and a decision."* It is cited
below as corroborating reasoning and never as authority. Its two line citations, `03:160` for
FR-250 and `03:172` for FR-257, are each one short of the current tree (`:161` and
`:173`); the frozen plan copied both. The requirements are the ones intended, and this record
uses the `9891be1` numbers.

---

## RL-880 — DP1: `POST /api/v1/score` takes an explicit `rating_version_ref` in WK-671, and refuses rather than guesses when it is absent

**The decision, restated.** DP1 asks how `POST /api/v1/score`'s default path — no explicit
`rating_version_ref` — resolves *"the Rating Version currently live in the target
environment"* (FR-250, [`../specs/03-rating-engine.md`](../specs/03-rating-engine.md)`:161`)
when FR-238 (`:134`) makes `live` a property of a **Deployment**, and Deployment
(FR-267, `03` §3.10 `:193`) together with the Environment entity itself
(FR-428, [`../specs/07-platform.md`](../specs/07-platform.md)`:139`) are both WK-674's
([`../roadmap.md`](../roadmap.md)`:379`). Options as the plan states them: **(a)** pull a
minimal Environment plus live-pointer forward into WK-671; **(b)** defer — the endpoint requires
an explicit ref until WK-674, as a named register deferral; **(c)** a throwaway placeholder
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
  WK-674's, because FR-238 makes `live` a property of a Deployment."* The half that *does*
  exist is the environment **scope**, not the pointer: a Service Account carries
  `environments: list[str]`
  ([`../../backend/src/app/db/models.py`](../../backend/src/app/db/models.py)`:392`) with the
  comment at `:389-391` citing FR-430. So the target environment of a call is already
  derivable; what is missing is which version is live in it, and that is a Deployment record.
- **(a) cannot be cut down to a pointer without becoming (c).** FR-267 (`03:193`) makes a
  Deployment record who, when, why and the bundle hash; FR-429 (`07:140`) enforces
  promotion order against prior deployment history, which
  [`../workflows/WF-00701-deploy-and-monitor.md`](../workflows/WF-00701-deploy-and-monitor.md)`:48`
  step C2 shows depends on that history existing; FR-268 requires atomic switchover with
  pre-warming and FR-272 an audit event. A `(workspace, environment) → rating_version_id`
  row carries none of them. It is not a smaller (a); it is (c) with better manners, and (c) is
  undocumented shadow-modelling of a shape `03` §3.10 already defines precisely.
- **No workflow before `WF-701` exercises the default path.** Both of FR-250's citations
  outside `03` and the roadmap are in `WF-701` — step A4 (`:30`), where a Consumer System
  scores test quotes *after* step A1 has already created a Deployment, and step C6 (`:52`).
  Deferring the default path to WK-674 therefore removes nothing any earlier journey needs.
- **Scope, if (a) were taken, would make two closure records wrong.** FR-428, FR-429, FR-430, FR-431 sit in
  WK-674's roadmap row (`:379`); `CLAUDE.md` §13 derives closure scope from the specification
  first. Building part of FR-428 under WK-671's name puts a requirement in two workstreams'
  evidence and neither's scope.

### Clause 1 — the deferral lives at the endpoint, never in the shape

**`options.rating_version_ref` stays optional and nullable.** This is the spec's own position
and not merely the contract's: `03` §4.4's `QuoteContext` example (`:395`) is literally
`"options": {"trace": true, "rating_version_ref": null}`, and FR-251 (`:162`) says
scoring *"accepts"* an explicit ref *"for what-if and testing"* — a field the specified design
treats as an addition to a default cannot be required by the shape that carries it. The
hand-authored contract agrees (`docs/contracts/schemas/scoring.schema.json:20`, inside
`options`, `oneOf` an artifact ref or `null`; `QuoteContext`'s `required` array at `:8` is
`["purpose", "quoted_at", "effective_date", "inputs"]`), but the contract is the corroboration
here, not the authority — RL-878 in the Slice 1 record establishes that this exact file can
be the stale side.

There is also a mechanical reason not to put the deferral in the shape, and it is one Slice 1
arms. RL-878's obligation 4 binds Task 1.4 to add the scoring shapes to
`scripts/generate-contracts.py`'s `GENERATED_SHAPES` and to lift `"scoring"` from
`backend/tests/test_contracts.py`'s exclusion dict — at `9891be1` that dict still carries
`"scoring": "later-phase — 03 rating"`. From the moment Task 1.4 lands, the generated
`QuoteContext` is compared against the hand-authored one. A `model-schema` shape that made the
ref required would then land as drift, and the tempting repair — editing the authored contract
to match the code — is `CLAUDE.md` §0's forbidden direction.

### Clause 2 — the refusal is a permanent branch with a typed code, not a stub

Omitting the ref means *"this platform has no live Rating Version to score you against."*
That is not a WK-671 artefact: it is exactly the answer WK-674's resolver must give when the target
environment holds no Deployment. So WK-671 ships the real branch with its trigger unconditional,
and WK-674 narrows the trigger rather than deleting a stub.

**One error code, appended to `03` §5.1's owned block in this ruling's own commit:
`NO_LIVE_RATING_VERSION`, HTTP **409**.** 409 is this backend's established status for *"the
artifact is not in a state that permits this"* — `platform/datasets.py:568`,
`platform/jobs.py:214`, `platform/rating_versions.py:160` and
`platform/approvals.py:427` all refuse state at 409 — and it is the right signal here,
because the caller's operator resolves it by deploying a version and retrying. `03` §5.1's
`/score` row and the Phase-0 OpenAPI stub declare a `default` Problem response, which covers
it; the generated document is the enforced one in any case
([`../contracts/README.md`](../contracts/README.md)).

**Task 2.1 owes the code's registration**: `NO_LIVE_RATING_VERSION` must join
`RATING_ERROR_CODES` in [`../../backend/src/app/errors.py`](../../backend/src/app/errors.py)`:275-307`
in the same PR as the route. `PlatformError.__init__` (`:344-348`) raises `ValueError` on an
unregistered code, so the branch cannot be written before the code is registered — which is
the mechanism that stops this ruling being half-applied.

### Clause 3 — FR-251's two restrictions are scoped to `prod` and WK-671 imposes neither

The frozen plan's Task 2.1 tells the executor the endpoint *"resolves an explicit
`rating_version_ref` (FR-251 — `prod` restricts to `approved` versions, records as
`what_if`)"*. Read without the requirement in front of you, that reads as two things to
implement. It is not. FR-251's full text is: *"Scoring accepts an explicit
`rating_version_ref` for what-if and testing; **in `prod`** this is permitted only for
`approved` versions and is recorded as a `what_if` purpose, never as a quotable price."* Both
restrictions sit inside the `prod` clause. WK-671 has no environments, therefore no `prod`,
therefore neither restriction applies.

**Ruled:** WK-671 does **not** restrict the explicit-ref path to `approved` versions and does
**not** rewrite `QuoteContext.purpose` to `what_if`. `purpose` is a required, caller-supplied
field with the five members RL-878 fixed, and scoring a `draft` or `review` version by
explicit reference is precisely the *"what-if and testing"* FR-251 permits. Imposing the
`prod` restrictions unconditionally would forbid the only use the endpoint has before WK-674.
WK-674 imposes them when `prod` exists.

### Disposition

- **Task 2.2 ("Default-live resolution") is not built in WK-671.** It is WK-674's, with the rest of
  FR-267 and FR-428. Slice 2 loses that task and gains one refusal branch plus its
  test inside Task 2.1.
- **Spec change in this commit:** `NO_LIVE_RATING_VERSION` appended to `03` §5.1's owned
  error-code block with a dated marker. No requirement is amended: FR-250 and FR-251
  read exactly as intended, and a deferral is a status fact, which `CLAUDE.md` §9 keeps in the
  roadmap and the register rather than in a spec.
- **Owed at the WK-671 close, and not this role's to write:** a row in
  [`../findings/register.md`](../findings/register.md) recording FR-250's default-live path as
  *carry forward with an owner — WK-674*. `CLAUDE.md` §12 and §13 put the four verdicts and the
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
