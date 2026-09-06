---
id: RL-923
family: ruling
title: the schema is right and is not rebuilt; it is a published data contract two modules read, so it moves out of the docstring into `03` §4 — and it does **not** go into `model-schema`, for a reason, not a deferral
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-08-30
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-08-30-w11-reopen-scope-and-batch-frame-contract-rulings.md
---

## RL-923 — the schema is right and is not rebuilt; it is a published data contract two modules read, so it moves out of the docstring into `03` §4 — and it does **not** go into `model-schema`, for a reason, not a deferral

**Ruled.** In four parts. **No restart, and no rework of the design.** A follow-up commit on
`feat/w11-3a-score-batch` is the disposition.

### 1. Read first, at `7b88d0d`, not from the dispatch

`packages/pricing-core/src/pricing_core/rating/score.py` at `7b88d0d` was read in full for the
added region, together with `packages/pricing-core/tests/test_rating_score_batch.py`,
`packages/model-schema/src/model_schema/scoring.py`, `03` §4.4 and §5.2, FR-253/254/255, and
`docs/plans/PL-00849-wk-671-slice-3-batch-scoring-the-pure-transform-the-checkpointing-handler-and-the-route.md`'s Task 3A and 3B sections. Four premises of the
question were checked rather than accepted:

| Premise | Verdict |
|---|---|
| `03` §5.2 fixes the signature only | **Confirmed** — `docs/specs/03-rating-engine.md:606-608` gives `bundle`, `frame`, `chunk_rows`, `progress` and a `pl.LazyFrame` return, and no row shape |
| no precedent for a chunked frame transform's row schema exists in the repo | **Confirmed, and it is a class of four, not one** — see §2 |
| the executor flagged it rather than letting it pass | **Confirmed** — the commit message and the module docstring both say the schema is *"this task's own design"* |
| the shape is "hand-written where `model-schema` already has one" | **Partly** — six of nine output columns carry `ScoringResult`'s own field names and values; but the frame is a *projection*, not a second definition, which changes the remedy. See §4 |

### 2. The precedent question is bigger than Task 3A, and naming the class is part of the ruling

`03` §5.2 publishes **four** signatures taking or returning a polars frame — `score_batch`'s
`frame`, `dislocate`'s `portfolio`, `attribute`'s `portfolio`, and `score_batch`'s own return.
**No document under `docs/specs/` or `docs/contracts/` states a column schema for any of
them.** Every occurrence of *"portfolio"* in `03` and in `docs/contracts/` treats it as an
opaque Dataset Version reference, never as a declared column list.

`dislocate` and `attribute` are unbuilt — `packages/pricing-core/src/pricing_core/rating/`
holds only `__init__.py`, `compile.py`, `runtime.py` and `score.py`. `score_batch` is simply
the **first member of the class to become real**, which is why it surfaced here and why fixing
only this instance would leave WK-673 to rediscover it. The §4 subsection this ruling requires is
written so it can hold the portfolio frame's schema when WK-673 designs it; this ruling does not
design it, and does not build ahead of WK-673 by attempting to.

### 3. The schema is accepted as designed — there is nothing to re-derive

The input row's four reserved columns are `QuoteContext`'s own fields (`quote_id`, `purpose`,
`effective_date`) plus the `rating_version_ref` that RL-880 already made explicit on this
path; every other input column is a name in `bundle.algorithm.input_contract`, which is already
a `model-schema` shape. The output row is a projection of `ScoringResult` — `outcome`,
`rating_version_ref`, `bundle_hash`, `premium_ladder`, `outputs`, `decline_reasons`, its six
non-diagnostic fields — plus `quote_id` (which FR-253 requires and `ScoringResult` does not
carry) and two error columns. The two deliberate exclusions, `trace` and `timing_ms`, are the
two fields a batch run has no use for.

**That is the right shape**, and the pre-serialisation of the ladder and outputs to JSON text
columns is the right call given a nested `LadderRung` list and an untyped `outputs` dict. **The
design is ratified. §5's defects are about what the code does with that shape, not about the
shape.**

### 4. Where it lives: `docs/specs/03-rating-engine.md` §4, as a new subsection — **not** a docstring, and **not** `model-schema`

**Out of the docstring.** Three independent reasons, any one sufficient:

- **The spec is already partly the authority.** FR-253 states the batch output carries
  *"the quote key, ladder, and selected outputs per row"* — three of the nine output columns are
  already fixed by a numbered requirement. A docstring cannot be the whole record of a shape a
  requirement half-states.
- **It is a cross-module seam, not an implementation detail.** Task 3A produces the frame, Task
  3B writes it to a content-addressed parquet, and `05-monitoring.md` FR-317's 2026-08-26
  amendment (OQ-627) computes A/E from *"a full batch re-score of the exposure dataset
  (`03` FR-253), not from traces"* — verified at `05-monitoring.md:101` and `:433`, both of
  which establish the dependency and name **no columns**. A shape two module specs depend on
  and neither describes is exactly the gap the ten-section standard exists to close.
- **The frozen plan asserts something that is now false.** Task 3A's *"Interfaces — Produces
  (3B relies on this and on nothing else)"* block lists the signature alone. The moment a row
  schema exists, 3B relies on the signature **and** the schema. That is a finding against
  `docs/plans/PL-00849-wk-671-slice-3-batch-scoring-the-pure-transform-the-checkpointing-handler-and-the-route.md`, **recorded here and not repaired** — a filed
  plan is frozen at its date (`CLAUDE.md` §2).

**Not `model-schema`, and this is a refusal with a reason.** The question was put fairly and
the answer is no, for now:

- **There is no columnar contract in this repository to join.** No artifact under
  `docs/contracts/` or `packages/model-schema/src/` defines a tabular row schema. The nearest
  things — `docs/contracts/schemas/rate-table.schema.json`'s per-instance `keys`/`value` block
  and `docs/contracts/schemas/profile.schema.json`'s per-column statistics array — are both
  descriptions of *arbitrary* columns, not a fixed output row.
- **The seam ADR-704 defines does not carry this.** `model-schema` generates JSON Schema and
  OpenAPI, which generate the frontend TypeScript client (`CLAUDE.md` §2). A Polars column
  layout has no generator, no drift check in `scripts/generate-contracts.py --check`, and no
  frontend consumer. Putting it there would not make it generated; it would make it a
  hand-authored file in a directory `CLAUDE.md` §2 says is *"generated and never hand-edited"*.
- **Creating the first columnar contract artifact is an ADR-scale decision about what
  `model-schema` is**, not a Task 3A one. If WK-673's portfolio frame or a second parquet output
  makes the case, that is `.claude/skills/adr-write`'s path. **This ruling does not open it and
  does not pre-judge it.**

**So §2's rule is honoured by a test rather than by a generator.** The rule's target is drift —
*"a shape defined twice will diverge"* — and the drift that can actually happen here is
`ScoringResult` gaining a field that silently never reaches the parquet. Close it directly: a
test asserting that **every field of `ScoringResult` is either a column of the batch output
schema or on a named, commented exclusion list** (`trace`, `timing_ms`). Adding a field to
`ScoringResult` then fails the build. That is `CLAUDE.md` §13's *"enforcement is proven on
deliberately broken input"* in its cheapest honest form, and the proof is a temporary field
added to `ScoringResult` making the test print a failure.

### 5. Three defects in what was built — each of them §2's predicted divergence, in the shape's first commit

**(i) `outputs_json` is asserted nowhere, and its serialiser is silently lossy about money.**
Verified: the substring `outputs` does not occur anywhere in
`packages/pricing-core/tests/test_rating_score_batch.py` at `7b88d0d`. The byte-identity test
compares `outcome`, `rating_version_ref`, `bundle_hash`, `premium_ladder_json`,
`decline_reasons` and `error_code` — every column **except** the one FR-253 names as
*"selected outputs"*. Its serialiser is `json.dumps(outputs, default=str)` over
`ScoringResult.outputs: dict[str, object]`, and `default=str` stringifies whatever JSON cannot
encode. `CLAUDE.md` §7: *"Money is integer pence/cents, or Decimal in the rating path — never
float."* A `Decimal` output is therefore written as a quoted string and an `int` output as a
number, **in the same column**, decided by what the algorithm's output step happened to
produce, with nothing asserting it and `05` FR-317's A/E computation downstream.

**Ruled as a property, not as a shape** (the executor picks the mechanism): the outputs
serialisation must be **total over the value types the rating path can produce**, and must
**fail loudly** on a type it does not name rather than stringify it. `default=str` as a silent
catch-all is refused. At least one `Decimal`-valued and one money-minor output must be asserted
in the byte-identity test, so this column stops being the only unasserted one.

**(ii) The module docstring calls `"error"` a "batch-only sentinel". It is not.**
`packages/model-schema/src/model_schema/scoring.py:69` reads
`ScoringOutcome = Literal["quoted", "declined", "error"]`. It is a contract member, and
`ScoringResult.outcome` is typed with it. The sentence is wrong on its face and it is the
dangerous kind of wrong: a later session reading *"batch-only"* concludes the enum needs
widening for batch, which is precisely the diverged shape §2 calls a mispricing. Correct the
sentence and cite the enum's own location.

**(iii) `rating_version_ref` is taken from user data and never checked against `bundle` — and
this one is not 3A's to close.** `_score_batch_row` builds the context's ref from
`row["rating_version_ref"]`, passes it to `build_scoring_result`, and copies the raw row string
into the output row. `CompiledBundle` carries no ref — its fields are `content_hash`,
`decision`, `algorithm`, `boosters` (`packages/pricing-core/src/pricing_core/rating/runtime.py`,
the `CompiledBundle` dataclass) — so `score_batch` **cannot** derive one, and reading it per row
rather than widening §5.2's signature is correct. The defect is elsewhere: for `score_one` the
caller resolved *that ref* into *that bundle*, so the two agree **by construction**; in
`score_batch` the frame supplies the ref and the caller supplies the bundle independently, and
that construction is gone. A frame whose ref column disagrees with `bundle` produces a parquet
attributing premiums to a Rating Version that did not compute them.

**Ruled: this is a constraint on Task 3B and it is not a 3A change.** 3B resolves the reference
and builds the input frame, so **3B stamps `rating_version_ref` from the reference it
resolved** and never carries it through from the input dataset. The §4 subsection states it,
and 3B's acceptance carries it. Ordering 3A to close a hole it has no information to close
would produce a check that cannot fail.

### 6. Disposition — one follow-up commit, and why this record does not carry the spec edit

| Item | Where |
|---|---|
| §5(i) outputs serialisation property, and its assertions | follow-up commit on `feat/w11-3a-score-batch` |
| §5(ii) docstring correction, citing the enum's definition | same commit |
| §4's drift test against `ScoringResult`'s fields, with its broken-input proof | same commit |
| The new `03` §4 subsection: input reserved columns, the input contract passthrough, the nine output columns with dtypes, the two exclusions, and §5(iii)'s stamping constraint on 3B | **same commit** |
| §5(iii) itself — 3B stamps the ref | Task 3B's plan and acceptance |
| The finding against the frozen plan's *"relies on this and on nothing else"* block | recorded in §4 above; the plan is frozen and is not edited |

**Why the spec edit is in the executor's commit and not in this one.** `CLAUDE.md` §2: *"A
change spanning both lands as one commit — spec, code, tests, any skill update — or the audit
reports a consistency the repository does not have."* The subsection must describe the schema
**after** §5's fixes, so splitting it from those fixes would publish a contract the code does
not yet meet. This role's charter says a `docs/specs/` edit it makes carries its ruling record
in the same commit; it does not require the role to be the one who makes the edit, and where
the two would conflict `CLAUDE.md` §2 governs. **The edit follows
`.claude/skills/spec-change`** — a new subsection number, minted and never reused
(`CLAUDE.md` §5), all ten sections preserved, and `python3 scripts/audit-docs.py` before
commit. It mints **no** requirement id: it documents a shape three existing requirements
already reach (FR-253, FR-254, FR-317), and inventing an id for it would add a
requirement nobody decided to add.

### 7. Override conditions

This ruling is overridden if the frame contract is still only in a docstring when Slice 3
closes; if a columnar schema is added to `packages/model-schema/` or `docs/contracts/` without
an ADR; if `default=str` survives as a silent catch-all in the outputs serialisation; if the
`ScoringResult`-field drift test is written without a proof that it fails on a broken input; if
`03` §5.2's `score_batch` signature is widened; or if 3B accepts `rating_version_ref` from the
input dataset rather than stamping it.

---

## Verification

- **Tree:** `origin/main` at `5c1a6a0`, re-fetched at 2026-08-30T12:20Z in the same command
  that read the clock, immediately before drafting; this record's branch was equal to it at
  that moment. RL-923's subject is commit `7b88d0d` on `feat/w11-3a-score-batch`, which is
  not on `main`; its change set was listed with
  `git diff --stat origin/main...feat/w11-3a-score-batch`, not inferred.
- **RL-921 was established as the highest existing** by enumerating every `## Ruling N`
  heading under `docs/plans/`, not taken from the dispatch's figure.
- **The dispatch's account of RL-921's load-bearing claim was re-verified at source**, as
  the dispatch itself instructed: `content_hash` is written into `row.bundle` by
  `compile_rating_version` in `backend/src/app/platform/rating_versions.py`, `blob_sha256` is
  merged into the same dict by `record_bundle_blob`, and `_fetch_bundle` in
  `backend/src/app/api/score.py` reads `metadata = row.bundle or {}` and keeps only
  `blob_sha256`. Each of the three was read in the file, not accepted from the relay. **Held.**
- **Two constraints the dispatch offered were checked and did not hold** — §0. Both were
  checked before they were weighed, not after a conclusion was reached.
