# NFR-RATE-1's remediation, and `score_batch`'s frame contract (2026-08-30)

**What this is.** Two rulings. The first was assigned to the decision-maker by the maintainer
by name, after the lead put three scope shapes to them and was told *"let decision maker to
make decision"*: does NFR-RATE-1's remediation belong inside the W11 reopen. The second is a
decision point the executor hit inside W11 Task 3A and flagged rather than let pass: it
designed `score_batch`'s input/output row schema itself, because `03` §5.2 fixes the
function's signature and nothing anywhere fixes a row shape, and it recorded that schema in a
module docstring.

**Numbering continues at 42, 43.** Rulings 1–30 are catalogued in
[`2026-08-29-w11-3-d6-batch-resumability-ruling.md`](2026-08-29-w11-3-d6-batch-resumability-ruling.md);
31–32 there, 33 in
[`2026-08-29-w11-slice-parallelism-ruling.md`](2026-08-29-w11-slice-parallelism-ruling.md),
34 in
[`2026-08-29-w11-nfr-rate-2-sampling-structural-ruling.md`](2026-08-29-w11-nfr-rate-2-sampling-structural-ruling.md),
35 in
[`2026-08-29-w11-nfr-rate-1-trace-capture-remedy-ruling.md`](2026-08-29-w11-nfr-rate-1-trace-capture-remedy-ruling.md),
36 in
[`2026-08-30-w11-nfr-rate-11-quote-input-stores-ruling.md`](2026-08-30-w11-nfr-rate-11-quote-input-stores-ruling.md),
37 in
[`2026-08-30-w11-2b-bundle-resolution-ruling.md`](2026-08-30-w11-2b-bundle-resolution-ruling.md),
38 in
[`2026-08-30-w11-service-account-permissions-ruling.md`](2026-08-30-w11-service-account-permissions-ruling.md),
39–41 in
[`2026-08-30-w11-reopen-hooks-and-bundle-resolution-rulings.md`](2026-08-30-w11-reopen-hooks-and-bundle-resolution-rulings.md).
**Ruling 41 was verified as the highest existing** by enumerating every `## Ruling N` heading
under `docs/plans/`, not taken from the dispatch.

**Read against `origin/main` at `5c1a6a0`** for docs and backend code, re-fetched at
2026-08-30T12:20Z in the same command that read the clock; and against commit `7b88d0d` on
branch `feat/w11-3a-score-batch` for Ruling 43's subject, which is not on `main`. The branch
is one commit ahead of `8fd48b7` and its change set is
`packages/pricing-core/src/pricing_core/rating/score.py` (+279/−15) and
`packages/pricing-core/tests/test_rating_score_batch.py` (+250), listed with
`git diff --stat origin/main...feat/w11-3a-score-batch` rather than inferred from the message.

**Mints no `FR-`/`NFR-`/`OQ-` id.** Ruling 43 *requires* one `docs/specs/` edit and says
explicitly why this record does not carry it.

**Nothing here was taken from the lead's relay.** The dispatch's account of Ruling 41's
load-bearing claim was re-verified at source before either ruling was drafted — see
§Verification.

---

## 0. Two constraints the dispatch offered that do not hold, checked before they were weighed

**`CLAUDE.md` §0's "do not build ahead of the phase" does not bear on Ruling 42.** The
dispatch named it as a constraint. **W14 is in Phase 2, the same phase as W11** —
`docs/roadmap.md` §7's workstream table lists W8 through W15 and W30 under *"Phase 2 — Rating
Engine"*, with W14 as *"Deployment: environments, atomic switchover, rollback, shadow"*. Moving
work between W11 and W14 is therefore a **workstream-scope** question, not a phase-boundary
one, and §0's later-phase row is not engaged in either direction. Recorded because a rule
cited on the wrong side of a decision is worse than no rule: it makes the cautious answer look
compelled when it is only cautious.

**Shape (c) — remediate but defer the re-measurement — is not open, and is not refused here
either.** It was already foreclosed by a standing ruling. Ruling 41 §5: *"the re-measurement
belongs with it, since a change made for latency that is not re-measured is an assertion."*
The lead reached the same answer by a different route (`CLAUDE.md` §13 forbids booking an
unmeasured optimisation) and both are right, but the point is that (c) required no new
decision. Ruling 42 treats the live question as the one Ruling 41 §5 actually left open:
whether the change belongs *"to the reopened W11 or to whichever slice next touches the
scoring path"*.

---

## Ruling 42 — the remediation is ruled **into** the reopen, and NFR-RATE-1's verdict is ruled **out** of it: they are two different things and the record must not merge them

**Ruled.** Neither (a) nor (b) as put. The **code change** of Ruling 41 §2 lands inside the
reopen, carried by Slice 3's Task 3B. The **NFR-RATE-1 re-measurement** that would settle the
requirement does **not** land inside the reopen, is not attempted, and stays owned by W14.
NFR-RATE-1's verdict does not move: it remains *measured and FAILING*.

This widens the scope Ruling 39 §1 fixed. **Said plainly, as the dispatch asked: yes, this
adds work your predecessor's ruling did not include.** §5 below states exactly what it adds
and what it does not, because the difference is the whole ruling.

### 1. Why (b) as posed is not buildable, on the record's own numbers

(b) was *"remediate and re-measure inside the reopen"*. The re-measurement it means cannot be
performed here. Ruling 41 §4, verified at source: *"It does not establish 200 rps.
NFR-RATE-1's budget is at 200 rps per replica; the measurement never reached it, on a shared
box. **A re-run needs a dedicated host**, and one pass will not establish a verdict near a
bound."* The original measurement's own record carries the same two limits — one pass, and a
shared 4-core box with 1-minute load rising to 10.76 during the run — and voids its own 200 rps
rungs because the generator issued 149.5 and 142.1.

Nothing about the host has changed. A re-measurement run inside the reopen would reproduce the
void condition and hand the re-close a number that reads like a verdict and is not one. That is
the failure `CLAUDE.md` §13 names — *"NFRs are measured, not asserted"* — arriving through a
measurement rather than through an assertion, which is harder to spot.

### 2. Why (a) is not the honest answer either

Deferring the whole thing leaves four things standing at the re-close, and they compound:

- **A hard target failing, with a known, cheap, correct-by-construction removal of about 60 %
  of its measured cost, deliberately not taken.** Ruling 41 §4: `_fetch_bundle` is 36.574 ms of
  a 60.959 ms mean handler at the cleanest rung.
- **Two register rows carried forward *unowned*.** `docs/audit/register.md` gives both F50 and
  F51 the resolution *"carry forward, unowned"*. `CLAUDE.md` §14 admits three resolutions for
  an open finding — the close fixes it, it is carried forward **with a named owner**, or it is
  accepted. *Unowned* is none of them. Two W11 findings therefore currently lack a
  §14-conforming resolution, and the reopen is the last moment at which W11 can give them one.
- **F50's own filed disposition says the consequence out loud**: *"NFR-RATE-1 remediation
  (Ruling 41 §2, which would touch this same module) is explicitly not part of the W11 reopen
  … so **nobody is currently positioned to fix it as a side effect of other work**."* That
  sentence was written as a description of a state. It is also an argument, and (a) makes it
  permanent.
- **The next author of that module reads the false sentence while writing against it.** F50 is
  a docstring at `backend/src/app/platform/bundle_slot.py:28-31` arguing that a ref's mapping
  *"cannot change under the memo"*. Ruling 41 §3 established it is false and safe only because
  `hash_for` is read solely on the degradation branch. Task 3B is being written now and must
  resolve a `rating_version_ref` to a `CompiledBundle`; the only implementation of that in the
  repository is `_compiled_for`/`_fetch_bundle` in `backend/src/app/api/score.py`, whose
  neighbour is that docstring.

### 3. The positive reason: the reopen already has to touch this seam

`docs/plans/2026-08-29-w11-3-batch-scoring.md` describes Task 3B's *"Interfaces — Consumes"*
as *"3A's `score_batch`; `BlobStore.put` for the final output; `ProgressCallback` plumbing per
FR-PLAT-8."* **It names no bundle-resolution interface at all**, and grepping that plan for
`load_bundle`, `_compiled_for`, `_fetch_bundle` and `resolve_rating_version_ref` returns
nothing — the only `CompiledBundle` hits are the three copies of `score_batch`'s signature.

That is a gap in the plan, not evidence of separation. A batch handler receives a Rating
Version reference and must end up holding a `CompiledBundle`; `CompiledBundle` is not
serialisable (FR-RATE-65) and cannot arrive as a Job argument. So 3B will either **reuse**
`api/score.py`'s resolution — touching the module Ruling 41 §2 changes — or **write a second
resolver**, which is the shape `CLAUDE.md` §2 forbids in its own words: *"A shape defined twice
will diverge, and in a pricing platform a diverged shape is a mispricing."*

**Ruled: 3B reuses it, and reuses it in the form Ruling 41 §2 specifies.** That is why the
remediation belongs to this slice rather than to a later one: the slice has to arrive at this
code regardless, and the only choice is whether it arrives before or after the fix.

### 4. What is measured, and what that measurement may and may not be called

The change lands with a **component-level delta measurement of its own predicate**, not with an
NFR verdict. Concretely:

- `_compiled_for` p99 on a slot **hit** against `_compiled_for` p99 on the **current** full
  path, same tree, same host, same harness, both conditions in the same run.
- The report **names its tree, its host, its pass count and its ref cardinality**
  (`CLAUDE.md` §13: *"A reference carries its scope and its measurement"*). Ref cardinality is
  not optional detail: Ruling 41 §4 records that `backend/src/app/config.py:172` defaults
  `bundle_slot_capacity` to 1, so *"with capacity 1 and more than one ref in play the slot
  thrashes and every request pays the full path"*. A delta measured over one ref is a
  measurement of a single-ref workload and must say so.
- **`bundle_slot_capacity` is not raised.** Ruling 41 §4 left it unset and its own code comment
  requires a latency-harness measurement to raise it. Raising it here would be the guess §0
  forbids.

**What this measurement is not.** It is not a re-measurement of NFR-RATE-1, it is not run at
200 rps, it is not run on a dedicated host, and it does **not** fire Ruling 41 §4's trigger —
*"if a re-measurement with the blob read removed still fails the 15 ms limb, that is the
trigger that puts NFR-RATE-1 itself in question"*. That trigger is armed by a **requirement**
re-measurement on a host that can carry one, and a component delta on a shared 4-core box is
not it. Reading the trigger as fired by this delta would answer the requirement's own question
from numbers that cannot support it.

### 5. The boundary that keeps this from being a scope widening in the sense that matters

**The reopen's requirement scope is unchanged.** It stays FR-RATE-36, FR-RATE-37, FR-RATE-42
and NFR-RATE-12 — Ruling 39 §1's list, restated in the closure record §9. **NFR-RATE-1 is not
added to it.** No `FR-`/`NFR-` id moves, no requirement gains an owner, and the §13 closure
audit's scope is the same set it was before this ruling.

What is added is a **code change that discharges a carried-forward finding**, plus owners for
two register rows. That is `CLAUDE.md` §14's own machinery for open findings, not a new
deliverable. The distinction is load-bearing at the re-close: the acceptance condition this
work joins is *"the code change and its delta measurement are complete"*, and it is **never**
*"NFR-RATE-1 passes"*.

**The 2026-08-30 amendment to `docs/plans/2026-08-30-w11-reopen-direction.md` §4 anticipated
this ruling and is engaged by it.** It records that *"if a further slice is ruled into the
reopen it joins this condition automatically … the condition is not met until it too is
complete."* Read against §5's boundary: what joins Condition 1 is the code change and its delta
measurement. Nothing in this ruling makes NFR-RATE-1's *passing* a precondition of the
re-close, and reading it that way would make W11 unclosable on the hardware available.

### 6. The sentence the record must not be able to produce

**Removing the blob read does not make NFR-RATE-1 pass, and no artifact produced under this
ruling may imply that it does.** The evidence, unchanged by anything here: the without-GBM limb
reads component p99 **23.027 ms against a 15 ms budget with the fetch already excluded**, and
the with-GBM component p99 is 33.468 ms, inside 50 ms by only 1.49×. Ruling 41 neither amended
NFR-RATE-1 nor showed it reachable, and this ruling does neither.

Three concrete prohibitions follow, so this is testable rather than hortatory:

- **`docs/audit/work/W11/README.md` §4's NFR-RATE-1 row and §6's carry-forward row are not
  edited.** They are the record as at the close (Ruling 39 §2). The remediation is reported in
  the appended reopen section, under the finding it discharges.
- **The re-close's NFR-RATE-1 verdict is the same verdict**: measured and failing. A close
  reporting it any other way has broken this ruling.
- **The delta measurement is published with its host and pass count attached**, so a later
  reader cannot lift the number out of its condition.

### 7. Disposition and owners

| Item | Owner | Applied where |
|---|---|---|
| Ruling 41 §2's code change (version-row read stays; blob PK lookup, ~2,039,114 B object read and full `model_validate_json` leave the hot path) | W11 Slice 3, Task 3B | `backend/src/app/api/score.py` `_compiled_for`/`_fetch_bundle` |
| The component delta measurement of §4, with tree, host, pass count and ref cardinality | W11 Slice 3, Task 3B | filed with the change |
| **F50** — the `bundle_slot.py:28-31` docstring correction | W11 Slice 3, Task 3B | the register row's *unowned* is superseded by this line |
| **F51** — the research note's false premise at `docs/research/w11-task-2d-nfr-rate-1-full-path.md:74-75` | W11 Slice 3, Task 3B, as a dated correcting annotation quoting what it supersedes | the register row's *unowned* is superseded by this line |
| NFR-RATE-1's requirement re-measurement, on a dedicated host, more than one pass | **W14** — unchanged | not W11 |
| `bundle_slot_capacity`, a TTL, a refresh/poll/pub-sub channel | **W14** — unchanged, Ruling 16 clause 4 | not W11 |

**F51's correction is an annotation, not an edit.** The register row already reasons that a
merged research note *"needs the same ruling-then-file path Ruling 41 itself came from, not a
register row alone"*. This ruling is that path. The note's **measurements are not in question**
and are not to be touched — Ruling 41 §1 re-read every one of them and each held; only the
premise sentence at `:74-75` is wrong.

### 8. Override conditions

This ruling is overridden if the delta measurement is reported without its host and pass
count; if any artifact describes NFR-RATE-1 as passing, improved to passing, or re-measured; if
Ruling 41 §4's 15 ms trigger is treated as fired; if `bundle_slot_capacity` is raised, or a TTL
or invalidation channel added, under cover of this work; or if the closure record's §§1–8 are
edited rather than appended to.

---

## Ruling 43 — the schema is right and is not rebuilt; it is a published data contract two modules read, so it moves out of the docstring into `03` §4 — and it does **not** go into `model-schema`, for a reason, not a deferral

**Ruled.** In four parts. **No restart, and no rework of the design.** A follow-up commit on
`feat/w11-3a-score-batch` is the disposition.

### 1. Read first, at `7b88d0d`, not from the dispatch

`packages/pricing-core/src/pricing_core/rating/score.py` at `7b88d0d` was read in full for the
added region, together with `packages/pricing-core/tests/test_rating_score_batch.py`,
`packages/model-schema/src/model_schema/scoring.py`, `03` §4.4 and §5.2, FR-RATE-36/37/38, and
`docs/plans/2026-08-29-w11-3-batch-scoring.md`'s Task 3A and 3B sections. Four premises of the
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
only this instance would leave W13 to rediscover it. The §4 subsection this ruling requires is
written so it can hold the portfolio frame's schema when W13 designs it; this ruling does not
design it, and does not build ahead of W13 by attempting to.

### 3. The schema is accepted as designed — there is nothing to re-derive

The input row's four reserved columns are `QuoteContext`'s own fields (`quote_id`, `purpose`,
`effective_date`) plus the `rating_version_ref` that Ruling 14 already made explicit on this
path; every other input column is a name in `bundle.algorithm.input_contract`, which is already
a `model-schema` shape. The output row is a projection of `ScoringResult` — `outcome`,
`rating_version_ref`, `bundle_hash`, `premium_ladder`, `outputs`, `decline_reasons`, its six
non-diagnostic fields — plus `quote_id` (which FR-RATE-36 requires and `ScoringResult` does not
carry) and two error columns. The two deliberate exclusions, `trace` and `timing_ms`, are the
two fields a batch run has no use for.

**That is the right shape**, and the pre-serialisation of the ladder and outputs to JSON text
columns is the right call given a nested `LadderRung` list and an untyped `outputs` dict. **The
design is ratified. §5's defects are about what the code does with that shape, not about the
shape.**

### 4. Where it lives: `docs/specs/03-rating-engine.md` §4, as a new subsection — **not** a docstring, and **not** `model-schema`

**Out of the docstring.** Three independent reasons, any one sufficient:

- **The spec is already partly the authority.** FR-RATE-36 states the batch output carries
  *"the quote key, ladder, and selected outputs per row"* — three of the nine output columns are
  already fixed by a numbered requirement. A docstring cannot be the whole record of a shape a
  requirement half-states.
- **It is a cross-module seam, not an implementation detail.** Task 3A produces the frame, Task
  3B writes it to a content-addressed parquet, and `05-monitoring.md` FR-MON-11's 2026-08-26
  amendment (OQ-MON-1) computes A/E from *"a full batch re-score of the exposure dataset
  (`03` FR-RATE-36), not from traces"* — verified at `05-monitoring.md:101` and `:433`, both of
  which establish the dependency and name **no columns**. A shape two module specs depend on
  and neither describes is exactly the gap the ten-section standard exists to close.
- **The frozen plan asserts something that is now false.** Task 3A's *"Interfaces — Produces
  (3B relies on this and on nothing else)"* block lists the signature alone. The moment a row
  schema exists, 3B relies on the signature **and** the schema. That is a finding against
  `docs/plans/2026-08-29-w11-3-batch-scoring.md`, **recorded here and not repaired** — a filed
  plan is frozen at its date (`CLAUDE.md` §2).

**Not `model-schema`, and this is a refusal with a reason.** The question was put fairly and
the answer is no, for now:

- **There is no columnar contract in this repository to join.** No artifact under
  `docs/contracts/` or `packages/model-schema/src/` defines a tabular row schema. The nearest
  things — `docs/contracts/schemas/rate-table.schema.json`'s per-instance `keys`/`value` block
  and `docs/contracts/schemas/profile.schema.json`'s per-column statistics array — are both
  descriptions of *arbitrary* columns, not a fixed output row.
- **The seam ADR-0002 defines does not carry this.** `model-schema` generates JSON Schema and
  OpenAPI, which generate the frontend TypeScript client (`CLAUDE.md` §2). A Polars column
  layout has no generator, no drift check in `scripts/generate-contracts.py --check`, and no
  frontend consumer. Putting it there would not make it generated; it would make it a
  hand-authored file in a directory `CLAUDE.md` §2 says is *"generated and never hand-edited"*.
- **Creating the first columnar contract artifact is an ADR-scale decision about what
  `model-schema` is**, not a Task 3A one. If W13's portfolio frame or a second parquet output
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
`decline_reasons` and `error_code` — every column **except** the one FR-RATE-36 names as
*"selected outputs"*. Its serialiser is `json.dumps(outputs, default=str)` over
`ScoringResult.outputs: dict[str, object]`, and `default=str` stringifies whatever JSON cannot
encode. `CLAUDE.md` §7: *"Money is integer pence/cents, or Decimal in the rating path — never
float."* A `Decimal` output is therefore written as a quoted string and an `int` output as a
number, **in the same column**, decided by what the algorithm's output step happened to
produce, with nothing asserting it and `05` FR-MON-11's A/E computation downstream.

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
already reach (FR-RATE-36, FR-RATE-37, FR-MON-11), and inventing an id for it would add a
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
  that moment. Ruling 43's subject is commit `7b88d0d` on `feat/w11-3a-score-batch`, which is
  not on `main`; its change set was listed with
  `git diff --stat origin/main...feat/w11-3a-score-batch`, not inferred.
- **Ruling 41 was established as the highest existing** by enumerating every `## Ruling N`
  heading under `docs/plans/`, not taken from the dispatch's figure.
- **The dispatch's account of Ruling 41's load-bearing claim was re-verified at source**, as
  the dispatch itself instructed: `content_hash` is written into `row.bundle` by
  `compile_rating_version` in `backend/src/app/platform/rating_versions.py`, `blob_sha256` is
  merged into the same dict by `record_bundle_blob`, and `_fetch_bundle` in
  `backend/src/app/api/score.py` reads `metadata = row.bundle or {}` and keeps only
  `blob_sha256`. Each of the three was read in the file, not accepted from the relay. **Held.**
- **Two constraints the dispatch offered were checked and did not hold** — §0. Both were
  checked before they were weighed, not after a conclusion was reached.
