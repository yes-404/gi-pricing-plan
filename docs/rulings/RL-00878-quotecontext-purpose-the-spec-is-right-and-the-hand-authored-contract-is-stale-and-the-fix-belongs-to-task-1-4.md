---
id: RL-878
family: ruling
title: `QuoteContext.purpose`: the spec is right and the hand-authored contract is stale, and the fix belongs to Task 1.4
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-08-29
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-08-29-w11-slice1-rulings.md
---

## RL-878 — `QuoteContext.purpose`: the spec is right and the hand-authored contract is stale, and the fix belongs to Task 1.4

**Raised by the planner during Slice 1 execution**, after Rulings 6–11 were filed — the case
this record's own pre-resolution standard exists for, arriving late rather than not at all.

**Correction to the report as received, first sentence per `docs/process/delivery-process.md`
§15:** the enum is `docs/contracts/schemas/scoring.schema.json` **line 12**, not line 13.
Everything else in the report holds.

**The finding, verified independently rather than adopted.**
`docs/contracts/schemas/scoring.schema.json:12` types the field with four members —
`"purpose": {"enum": ["new_business", "renewal", "mid_term_adjustment", "what_if"]}` —
omitting `cancellation`. `../specs/03-rating-engine.md` gives **five** in two separate
places: §2's glossary row (`:63`) and §4's own `InputContract` example (`:240-241`,
`"domain": ["new_business", "renewal", "mid_term_adjustment", "cancellation", "what_if"]`).

**Ruled: the contract is the wrong side.** This is a `CLAUDE.md` §0 code-versus-spec
question, and the answer is not close:

- **Three spec locations say five, and the third is the dated record of the edit itself.**
  `OQ-617` (`:807`): *"**DECIDED 2026-08-18**: the same algorithm for the risk price, with
  pro-rata/refund/charge logic in a separately-versioned sub-graph mounted on `purpose` —
  FR-218. §2's `purpose` gained `cancellation` in the same edit, because the answer keys
  on a value that did not exist."* Dropping `cancellation` to match the contract would
  silently reverse a maintainer decision, which is the outcome `CLAUDE.md` §0 forbids by
  name.
- **`FR-218` (`:87`) cannot be satisfied under the four-member enum.** It mounts the
  sub-graph *"only when `purpose ∈ {mid_term_adjustment, cancellation}`"* and requires that
  *"a version that mounts no such sub-graph **refuses** an MTA or cancellation quote rather
  than pricing it as new business — pricing it as new business is the failure this
  requirement exists to prevent, and it is silent."* A `QuoteContext` that cannot carry
  `cancellation` cannot be built to be refused, so half the guard is unexpressible, not
  merely untested.
- **Provenance checked, not inferred.** `scoring.schema.json` has exactly two commits in its
  whole history — `b452c78` (the Phase 0 draft) and `cb9dd78` (the remaining ten artifact
  schemas) — and neither is `eb43022`, the 2026-08-18 commit that decided `OQ-617`. That
  commit's own message records the gap as a CI-scope observation rather than a coverage one:
  *"No file under `frontend/` or `docs/contracts/` changed, so the frontend workflow does not
  run on this branch."* The contract was never disagreed with; it was never revisited.

**The real decision here is who fixes it and when**, since which side is wrong was settled by
the paragraph above.

- **(a) Fix the contract in this ruling's own commit.**
- **(b) Fix it in the PR that builds `QuoteContext` — Task 1.4.**
- **(c) Amend the spec down to four.** Refused above.

**Ruled: (b).**

- **There is no authoritative shape to keep it consistent with yet.** `git grep -n
  mid_term_adjustment` over `packages/`, `backend/`, `frontend/src` and `docs/contracts/`
  returns **exactly one hit at `7b8473a`**: the stale schema line itself. `model-schema`
  defines no purpose enum at all, which matches the frozen plan's own statement that
  `QuoteContext`, `ScoringResult` and `Trace` have *"zero code exists for any of the three
  today"*. Per `ADR-704` and `CLAUDE.md` §2, `model-schema` is the single source of truth
  and Task 1.4 is what creates it. Correcting the hand-authored contract now would fix the
  only *existing* copy while the *authoritative* one is still unwritten — and open a second
  window for the two to diverge again, which is the failure being fixed.
- **`CLAUDE.md` §2 wants them in one commit**: a change spanning spec and code *"lands as
  **one commit** — spec, code, tests, any skill update — or the audit reports a consistency
  the repository does not have."* The `model-schema` enum, the contract line and
  `FR-218`'s refusal test are one change.
- **Charter boundary, named rather than routed around.**
  `.claude/roles/decision-maker.md`'s Tools line grants writes to ruling records, the
  open-questions log and `docs/specs/`. It does **not** name `docs/contracts/`. Ruling which
  side is wrong is §0 and is this role's; editing a hand-authored contract file is not
  granted to it. (b) is the disposition the charter permits *and* the better engineering, so
  nothing is lost here — but see the finding below, because that will not always be true.

**Binding on Task 1.4 — three obligations, all in one PR** (a fourth is added by the
addendum below):

1. `QuoteContext.purpose` carries **five** members including `cancellation`, defined once in
   `model-schema` (`ADR-704`, `CLAUDE.md` §2 — nobody hand-writes a shape `model-schema`
   owns).
2. `docs/contracts/schemas/scoring.schema.json:12` is corrected to those five in the same
   commit.
3. **`FR-218`'s refusal test covers both members, not one.** The frozen plan's exit
   criterion (`2026-08-29-w11-scoring.md:401-404`) specifies only *"a `QuoteContext` with
   `purpose: mid_term_adjustment`"*. That is the half the stale contract can already express
   — so the test as written would have gone green with this defect fully in place. The
   contract gap and the test gap are **the same gap**: `cancellation` is
   `mid_term_adjustment`'s stranded list-mate in the requirement, in the contract and in the
   test, and fixing any one of the three alone leaves the guard half-proven.

**Finding against this role's own charter file, reported per the lead's standing invitation
and not worked around.** `.claude/roles/decision-maker.md` grants `docs/specs/` writes for
"the spec changes its charter already owns", but a `CLAUDE.md` §0 ruling decides between
*spec* and *code*, and one of the artifacts that can be the wrong side —
`docs/contracts/schemas/` — is hand-authored (`docs/contracts/README.md`'s own table:
`schemas/` is authored, `schemas/generated/` is not) and outside the grant. It did not bite
here, because (b) is independently correct. It bites the first time a hand-authored contract
is the wrong side and no code PR is in flight to carry the correction — at which point the
answer must be to widen the charter or route the edit to a role that has the grant, never to
edit it anyway. Not urgent; filed so the decision is made deliberately rather than under
time pressure.

**Addendum to RL-878, filed the same day, after `b826790` merged.** Raised by the lead
asking the one question this ruling had answered by inference rather than head-on — *"check
whether `QuoteContext` also exists under `schemas/generated/` first — that changes the
disposition entirely."* It was the right question to insist on. The answer confirms the
disposition and, in confirming it, exposes something larger that Task 1.4 must not walk into.

**The check, run head-on rather than inferred.** `docs/contracts/schemas/generated/` holds
27 schemas and **no scoring or quote-context schema among them**. `git grep -n QuoteContext`
over `docs/contracts/`, `packages/`, `backend/` and `frontend/src` returns three hits, and
all three resolve to the one hand-authored definition:

- `docs/contracts/schemas/scoring.schema.json:7` — the definition itself;
- `docs/contracts/schemas/regression-suite.schema.json:19` —
  `"context": {"$ref": "scoring.schema.json#/$defs/QuoteContext"}`;
- `docs/contracts/openapi/gi-pricing.yaml:256` — the Phase 0 design stub, `$ref`-ing the same.

The last two are `$ref`s, so correcting line 12 fixes all three at once. The lead's *"one
hand-authored line"* is therefore exactly right, and for a better reason than either of us
first had: not that the other references do not exist, but that they inherit.

**The ruling's disposition stands unchanged.** No generated tier owns `QuoteContext`, so
`FR-451`'s drift gate has nothing to fire on and `scripts/generate-contracts.py --check`
cannot see this file at all.

## The larger thing, and a fourth obligation on Task 1.4

**Corrected before merge — the first filing of this paragraph overstated the guard, and the
wrong half is named rather than quietly rewritten.** It claimed that fixing the enum without
lifting the exclusion "would disarm the only mechanism that could have caught the defect."
**That is false.** `backend/tests/test_contracts.py`'s own docstring scopes it to two claims —
*"**Freshness.** The committed files match what the models produce right now"* and
*"**Conformance.** Where a shape has both a hand-authored Phase 0 contract and a generated
one, they agree"* — and it reads no file under `docs/specs/` at all. It could never have
caught the `purpose` divergence, which is spec-versus-hand-authored-contract, not
contract-versus-generated. Found by a sweep run after this addendum was first pushed, and
corrected on the same branch before merge.

**What is true, and why obligation 4 still stands.** `test_contracts.py` excludes
`"scoring"` with the reason `"later-phase — 03 rating"`. That reason is true *today* —
`QuoteContext` exists nowhere in `model-schema`. **Task 1.4 is what makes it false**, by
creating `QuoteContext`, `ScoringResult` and `Trace` there. From that moment the
hand-authored contract and the generated shape can diverge, and the exclusion is what would
let that happen silently. Obligation 4 is therefore a **forward** guard on a gap Task 1.4
itself opens — not, as first written, a recovery of the guard that missed this one. The
distinction matters, because a reader who believes the drift guard covers spec-to-contract
drift will not ask for the check that actually does.

**Obligation 4, therefore, in the same PR:** add the new shapes to
`scripts/generate-contracts.py`'s `GENERATED_SHAPES`, and lift `"scoring"` from
`test_contracts.py`'s exclusion dict. The precedent is in that dict's own neighbours and is
explicit about why — `GENERATED_SHAPES`' comment for the 2026-08-15 entries reads: *"Both had
hand-authored Phase-0 contracts and no generated counterpart, so nothing compared the shape
the code produces against the shape the contract promises — **and three divergences went
unnoticed until `main` moved**."* This is that lesson's fourth instance, and the first where
it was seen coming.

## Finding: three shipped rating types are already in the state this obligation prevents

Reported, not ruled — the remedy is scope, and scope is the lead's.

Checked while establishing the precedent above, and it is a class rather than one case.
`model-schema` **already defines** `RatingVersion` (`packages/model-schema/src/model_schema/
rating.py:104`), `RatingAlgorithm` (`:341`), `RateTable` (`:651`), plus `RateTableVersion`
(`:818`) and `RateTableDiff` (`:684`) — all shipped by WK-669 and WK-670. Each has a hand-authored
contract on disk (`docs/contracts/schemas/rating-algorithm.schema.json`,
`rating-version.schema.json`, `rate-table.schema.json`). And:

- `grep -n "RatingVersion\|RatingAlgorithm\|RateTable" scripts/generate-contracts.py` returns
  **zero**. A true negative, not a pattern miss: `GENERATED_SHAPES` is a `dict[str, str]` of
  slug → class name whose values are literally `"Job"`, `"Banding"`, `"ModelComparison"` and
  so on, so a class name would appear verbatim if it were there.
- `test_contracts.py` still excludes all three as `"later-phase — 03 rating"` — a reason that
  expired when WK-669 and WK-670 built the types.

So three shipped `model-schema` types have hand-authored contracts that **nothing has ever
compared them against**, and the exclusion that permits it now misdescribes why. `scoring`
becomes the fourth the moment Task 1.4 lands without obligation 4.

**Corrected with the paragraph above, and for the same reason:** the first filing of this
finding called it *"the identical mechanism that produced the `purpose` divergence, already
in place three more times."* It is not identical. This is the **contract-versus-code** gap;
`purpose` is the **spec-versus-contract** gap. They are siblings — the third finding below is
the parent both belong to — and running them together is what made the overstated claim above
sound reasonable when it was written.

Not proposed for fixing here: whether WK-669's and WK-670's closes should be reopened for it, or
whether it becomes a register row with an owner, is a scope question for the lead and the
§14 plan review — `CLAUDE.md` §12 and `docs/process/delivery-process.md` §5 step 7 both put
that call outside this role. What is ruled is only that **WK-671 does not add a fourth.**

## Second finding: `purpose` was not the only shape `eb43022` left behind, and the second is worse

A sweep of every enum `03-rating-engine.md` declares in §2 and §4 against its hand-authored
schema found **two** disagreements, not one, and both were landed by the same 2026-08-18
commit:

| # | Shape | Spec | Hand-authored contract | Gap |
|---|---|---|---|---|
| 1 | `QuoteContext.purpose` | `:63`, `:240-241` | `scoring.schema.json:12` | enum member `cancellation` missing |
| 2 | `RateTableVersion.storage` | FR-232 `:123`, `:289`, `:310-316` | `rate-table.schema.json` | **the whole field is absent** |

**The second is the worse one**, and it is `03`'s, not WK-671's: `FR-232` added `storage`
(`rows \| parquet`, "fixed when the version is written and immutable with it") on 2026-08-18,
and `grep -n storage docs/contracts/schemas/rate-table.schema.json` returns **nothing** — not
in `properties`, not in `required`. That schema has exactly one commit in its history
(`b452c78`, 2026-08-14), so it has never been touched since it was drafted, including not for
the requirement that added a field to it. WK-670 shipped `RateTable`/`RateTableVersion` into
`model-schema` against a contract missing that field.

Every other enum in §2 and §4 agrees — `RatingVersion.status`, `model_reference_mode`,
`ScoringResult.outcome`, `LadderRung.rung`, `operation.kind`, `input_contract[].type` and the
step `type` set were all checked and all match. So the class is two, bounded, and named.

## Third finding: nothing compares a spec's declared shape against its hand-authored contract

This is the gap that let both of the above survive, and it is the one worth fixing.

- **`scripts/audit-docs.py` does not do it.** Its only two checks touching
  `docs/contracts/schemas/` are *"Every JSON Schema parses and has no duplicate keys"* and
  *"Every JSON Schema `$ref` resolves"* — structural, not semantic. Grepped case-insensitively
  for `enum` across the whole script: every hit is Python's `enumerate()` builtin, never the
  JSON Schema keyword.
- **`backend/tests/test_contracts.py` does not do it either**, and says so in its own
  docstring — freshness and hand-authored-versus-generated conformance, with no file under
  `docs/specs/` read anywhere in it.

So a requirement can add a field or an enum member to a shape, and both the document gate and
the contract gate stay green while the committed contract goes on describing the old shape.
Two instances are on `main` today. **This is the same shape as the first finding in this
record** — error codes are unchecked across the spec/code boundary in both directions — and
the two together suggest the real gap is categorical: the gate checks documents against
documents and code against code, and nothing checks a document against the artifact it
specifies. Reported, not ruled: the remedy is a new check, which is scope.

---

---
