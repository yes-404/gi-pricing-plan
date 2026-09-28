---
id: RL-1172
family: ruling
title: WK-672 opening rulings — F60 and F59 are spec defects, the regression executor lives in pricing-core behind a sync signature, and FR-257 limb (1) is Slice 3's
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-28
owner: decision-maker
tree: df8e5811a151a99c7317690faf9278a6dc3400be
phase: P2
work: WK-672
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~
relates: [PL-930, CR-932, CR-926, FD-1117, FD-1116, FD-1101, RL-858, RL-868, RL-917]
---

# RL-1172 — WK-672 opening rulings: F60 and F59 are spec defects, the regression executor lives in pricing-core behind a sync signature, and FR-257 limb (1) is Slice 3's

## Scope, and what was verified first

This record rules the questions that must be settled before WK-672 (testing: golden quotes,
property assertions, regression runs) opens under its map plan `PL-930`:

1. register row F60 (`FD-1117`), each of its four sub-items;
2. register row F59 (`FD-1116`);
3. three signature questions on `03` §5.2's `testing.py` block that no register row names;
4. which slice owns limb (1) of F44 (`FD-1101`), the FR-257 check;
5. `PL-930` DP1, which is **not** this role's to rule. It is recorded below as the
   deputy's maintainer decision by delegation, quoted verbatim;
6. the slice order after these rulings.

`PL-930` is frozen and is not edited. Per `document-ids.md` §1.7 these are sibling rulings,
and each slice's leaf plan applies them.

**Tree.** Every fact below was read at origin/main
`df8e5811a151a99c7317690faf9278a6dc3400be` (#823), in the decision-maker's worktree on
branch `p2-d-rl`, cut from that commit with a clean status. The planner's report on
`PL-930` is the input. Every factual premise in it that this record relies on was
re-measured, and all of them reproduce except for line drift, which is listed below.

| Premise | Command at `df8e5811` | Reading |
|---|---|---|
| `rating/testing.py` does not exist | `ls packages/pricing-core/src/pricing_core/rating/` | Reproduces: `__init__.py compile.py runtime.py score.py` |
| `to_wire` is public and undeclared (F60 (1)) | `grep -n '^def to_wire\|^__all__' …/rating/runtime.py` | Reproduces: `:343`; `__all__` at `:52` names it |
| the six `operations.py` functions (F60 (2)) | `grep -n '^def ' …/rate_tables/operations.py` | Reproduces at `:113, :142, :168, :269, :383, :395`; the module has no `__all__` |
| `assert_integer_minor_round_trip` (F60 (3)) | `grep -n` in `compile.py`, `backend/src/app/main.py` | Reproduces: defined at `compile.py:67`, in `compile.py`'s `__all__`, called at `main.py:82` |
| `build_scoring_result` (F60 (4)) | `grep -n` in `score.py` | Reproduces: `:707`; `__all__` at `:219` is `["build_scoring_result", "score_batch", "score_one"]` |
| `KeyFilter` is `model-schema`'s (F59) | `grep -n KeyFilter` | Reproduces: defined at `model_schema/rating.py:728`, imported at `operations.py:39` |
| `run_regression` is sync, and `score_one` is async | `sed -n '696,730p' docs/specs/03-rating-engine.md`; `score.py:751` | Reproduces: the spec declares `def run_regression` and `async def score_one`; the code's `score_one` is `async def` |
| `InputContract` does not exist | `grep -rn 'InputContract\b' packages backend/src` | Reproduces: **0** hits. `InputContractField` is at `model_schema/rating.py:201`; `RatingAlgorithm.input_contract: list[InputContractField]` is at `:383` |
| `hypothesis` is not a runtime dependency | `grep -n hypothesis pyproject.toml packages/*/pyproject.toml backend/pyproject.toml` | Reproduces: only the root `pyproject.toml:19`, in the `dev` dependency group |
| FR-257's approval gate has no regression check | read `approvals.submit` and `rating_versions.submit_for_review` | Reproduces. `submit_for_review` is now at `backend/src/app/platform/rating_versions.py:214` (the register row cites an older line) |
| no WK-672 code exists | `grep -rn` over `backend packages frontend/src` for `GOLDEN_QUOTE_MISMATCH`, `RegressionRun`, `GoldenQuote` | Reproduces: 0 hits outside the generated client |

**Line drift, recorded rather than smoothed over.** The F60 and F59 rows cite `03` lines about
seven lower than they are now: `KeyFilter` is at `03:732` (the row says `:725`), and the
`testing.py` block is at `03:720`. The code citations are 0–3 lines stale. No premise failed.

**Two facts that are not in the planner's report, and bear on item 3:**

- A synchronous engine path already exists. `score_batch` evaluates with
  `bundle.decision.evaluate()` (`score.py:936`), which is plain `def` by RL-868, and it
  reaches the same `build_scoring_result` tail as `score_one` (RL-858).
- The worker already runs async work from a sync task with `asyncio.run` per task
  (`backend/src/app/worker/tasks.py:286`).

### A correction to `PL-930`, recorded here because the plan is frozen

**Dated 2026-09-28, on the deputy's E11.** The deputy asked for `PL-930:109`'s stale
citation of `03:597` to be read as `03:603`. At `df8e5811` the citation is on `PL-930:112`,
inside the DP1 paragraph that opens at `:108-109`. It reads
`docs/specs/03-rating-engine.md:597` for `POST /api/v1/score/compare`. That route is at
`03:603`, the §5.1 row *"Score one quote against two versions with a step-level diff
(FR-262)"*. **Read `:603` for `:597` there.**

The same drift appears twice more in `PL-930`, and the same correction is recorded for
both:

- `:375` cites `§5.1:597` for `regression-runs`. Read `03:604`.
- `:383` cites `§5.1:596` for `score/compare`. Read `03:603`.

`PL-930` itself is not edited (`document-ids.md` §1.7). The leaf plans re-derive every `03`
locator at their own tree.

## Ruled

### 1. F60 — `03` §5.2 omits four live exports

**The register's decision cell, verbatim** (`docs/findings/register.md:101`, `FD-1117`):

> carry forward with an owner — the decision-maker, per `CLAUDE.md` §0, to rule each of the four sub-items' correct side before WK-672 opens (proposal 4.2's own stated urgency, since WK-672 builds against these shapes): **(1) and (4)** read as pure spec omissions (the code is right, `03` §5.2 is incomplete) since neither `to_wire` nor `build_scoring_result` conflicts with anything the block does state; **(2)** is the more consequential of the four — six functions are live behind published endpoints and undeclared, so the fenced block understates the module's actual public surface; **(3)** ties to a numbered requirement (FR-273) whose named behaviour has no named function anywhere in §5.2, which a reader implementing from the spec alone would not know to look for. This row does not choose which correction each sub-item takes (spec amendment vs. code change) — that is the ruling's, not the register's

**Options, for each sub-item.** Either amend the spec to declare the function, or change the
code: make it private or remove it.

| Sub-item | Ruling | Why |
|---|---|---|
| (1) `to_wire` | **The spec is wrong.** Declare it in the `runtime.py` block. | It is public, in `runtime.py`'s own `__all__`, and load-bearing (the ZEN wire payload). Making it private would hide a function other modules need. |
| (2) six `operations.py` functions | **The spec is wrong.** Declare all six with their code signatures. | The platform layer calls them from published endpoints. A code change would break those endpoints. |
| (3) `assert_integer_minor_round_trip` | **The spec is wrong.** Declare it in the `compile.py` block. | It is the function FR-273 requires, and the service startup calls it. |
| (4) `build_scoring_result` | **The spec is wrong.** Give it a signature line in the `score.py` block. | It is the FR-254 shared tail that the prose already discusses, and it is in `score.py`'s `__all__`. |

**What it obliges: a spec change, made in this record's own commit.** `03` §5.2 now
declares all nine functions, with signatures copied from the code at `df8e5811`, and a dated
note under the fenced block cites this record. No code changes. F60 is therefore discharged
**before** WK-672 opens, as its row requires, and the Slice 1 leaf plan does **not** carry it.
The register row's `Resolved` annotation is the auditor's to write (rules.md rule 5).

### 2. F59 — `KeyFilter`'s home

**Options.** (a) Correct the spec to say `operations.py` imports `KeyFilter` from
`model_schema.rating`. (b) Move the definition into `operations.py` to match the spec.

**Ruling: (a). The spec is wrong.** Option (b) would define the shape twice, or move it out
of `model-schema`. That is the duplication `CLAUDE.md` §2 forbids, and ADR-704's one-way
seam would be broken to fix a sentence. **What it obliges: a spec change, made in this
commit.** The `operations.py` block now shows the import, dated and citing this record.
No code changes.

### 3. The `testing.py` signatures, and where regression execution lives

#### 3a. Is `run_regression` sync or async?

**Options.**

- **(i) `async def`.** It awaits `score_one` for every case.
- **(ii) Plain `def`, as declared.** It reaches the engine through the synchronous
  `evaluate()` path that `score_batch` already uses.

**Ruling: (ii). The spec is right, and it keeps `def`.**

- `spec-change`'s rule is that a signature is `async def` exactly when it directly awaits a
  native async binding from an async caller. `run_regression` has no async caller:
  `POST …/regression-runs` is a **202**, so the suite runs inside a Job in the worker.
- A synchronous engine path already exists: `score_batch` evaluates with `evaluate()`
  (RL-868). The ruling rests on this ground and the one above.
- **Conditional, amended 2026-09-28 before merge (the deputy's F4):** *if* spike F4
  passes and Slice 3 takes `hypothesis` (item 3c), its shrink loop, which FR-261's shrunk
  counterexample needs, runs through a synchronous property function. That would be a
  third reason for `def`. The ruling does not depend on it.
- The sync path does not weaken the golden-quote guarantee. It reaches the same
  `build_scoring_result` tail as `score_one` (RL-858), over the same compiled graph.

The planner read the async question as a defect, and so did this role's first proposal to
the lead. This record withdraws that proposal before commit. The defect is in `PL-930`'s
Global Constraints instead: they say the executor *"calls
`pricing_core.rating.score_one` exactly as WK-671's evaluator does"*. The leaf plans follow
this ruling, not that sentence.

#### 3b. `generate_contexts(contract: InputContract, …)`

**Ruling: the spec is wrong.** No type named `InputContract` exists. The input contract is
`RatingAlgorithm.input_contract: list[InputContractField]`. The parameter becomes
`contract: Sequence[InputContractField]`. **This is a spec change, made in this commit.**

#### 3c. Placement

**Options.**

- **(i)** Execution goes in `pricing-core` `rating/testing.py`, as `03` §5.2 declares.
- **(ii)** The backend holds a regression executor. `PL-930`'s Global Constraints imply
  this.

**Ruling: (i).** Evaluating a suite against a `CompiledBundle` is pure computation, with no
database, FastAPI or Redis. So it stays in `pricing-core`, and `CLAUDE.md` §2 holds.

- **The backend owns everything that persists or gates:**
  - the `RegressionSuite` / `GoldenQuote` store;
  - the `POST …/regression-runs` route and its Job;
  - the `RegressionRun` row;
  - the promotion hook (FR-260);
  - the approval-evidence check (item 4).

This placement has two consequences, stated so that the slices do not rediscover them:

- **`hypothesis` as a `pricing-core` runtime dependency is CONDITIONAL on spike F4.**
  This condition is the deputy's maintainer decision by delegation, stamped 2026-09-28
  11:35:56 BST, item 3. This record does not settle the dependency ahead of that
  measurement. F4 must show both of the following, with a pinned `hypothesis` version and
  across two processes:
  - a persisted seed reproduces the same generated cases;
  - shrinking yields the same minimal counterexample.
  - **If F4 passes,** Slice 3 takes `hypothesis` as a runtime dependency of `pricing-core`.
    `03` §8 already names it. `docs/skills-map.md` is checked in the same PR
    (`CLAUDE.md` §10). The shrinking ground in item 3a then holds.
  - **If F4 fails,** Slice 3's leaf plan uses a seeded generator of the platform's own.
    FR-261's "shrunk counterexample" clause is then re-read at Slice 3.
  - Either way, the generator reproduces its cases from the persisted `generation.seed`
    and imports none of FastAPI, SQLAlchemy or Redis (`CLAUDE.md` §2).
- **The property-assertion language is ruled: a structured union of FR-261's five classes,**
  as declarative JSON artifacts (`CLAUDE.md` §2), with no free-text expressions. This is the
  deputy's F4 ruling, made by delegation, stamped 2026-09-28 11:33:12 BST. It is the shape
  of `RegressionSuite.properties` when that artifact is built. `03` §4.7's example still
  shows free-text assertions. Correcting it is a spec change owed with the shape, at
  Slice 2 or Slice 3, whichever builds `RegressionSuite` in `model-schema`.
- **`RegressionSuite`, `GoldenQuote` and `RegressionRun` become `model-schema` artifacts**
  in the slice that first builds each one (Slice 2 for the suite and the golden quote,
  Slice 3 for the run).
  - This is not a new decision. ADR-704 and `CLAUDE.md` §2 already make it. These are
    persisted artifacts with a REST surface, unlike `03` §4.8's frame. The hand-authored
    `regression-suite.schema.json` is the Phase 0 draft that `docs/contracts/README.md`
    says stands until then.
  - `backend/tests/test_contracts.py:89` scopes the slug out as
    `"later-phase — 04 optimisation"`. That label is wrong: the shape is `03`'s, and it
    belongs to WK-672. The Slice 1 leaf plan corrects the label, and the slice that builds
    the shape removes the scope-out.

### 4. F44 limb (1) — FR-257's "passing Regression Suite"

**Options.**

- **(a) Slice 2.** It builds the suite store and the promotion hook.
- **(b) Slice 3.** It builds regression runs.
- **(c) A new slice.**

**Ruling: (b), Slice 3.** A "passing Regression Suite" is a `RegressionRun` whose
`overall` is `pass`, and Slice 3 is the first slice that produces one.

- Slice 2's promotion hook is FR-260's separate gate.
- Option (c) would add a slice for one check that Slice 3's own output is the input to.

**What it obliges: code, in Slice 3.**

- `rating_versions.submit_for_review` refuses with `EVIDENCE_INCOMPLETE` (`06`'s code,
  re-raised as `03` §5.1 already lists) unless a `RegressionRun` exists for that Rating
  Version whose `bundle_hash` equals the version's current bundle hash and whose `overall`
  is `pass`.
- It is tested on a failing run, on a run against a stale hash, and on no run at all.
- Its `req("FR-257")` marker names **limb (1) only**, as the register row requires of every
  FR-257 marker.
- The Slice 3 leaf plan lists this in its scope and acceptance.

`PL-930`'s Slice 3 scope never named FR-257. This ruling adds the limb to that slice. It
adds no slice.

### 5. DP1 — who builds FR-262, the Quote Sandbox

**Not this role's ruling.** Its resolver is the maintainer (`document-ids.md` §1.7: a scope
question). The maintainer delegated it to the deputy on 2026-09-28. The lead relayed the
deputy's entry in the team channel. It is quoted here verbatim as **the deputy's maintainer
decision by delegation**:

> **Maintainer decision by delegation (deputy, on the maintainer's instruction of 2026-09-28 11:24 BST), PL-930 DP1**, read at origin/main `df8e5811` against `docs/specs/03-rating-engine.md:178` (FR-262), `:603` (the §5.1 row `POST /api/v1/score/compare`, "Score one quote against two versions with a step-level diff (FR-262)"), and `docs/roadmap.md`'s WK-672 row (FR-260..262 in range) and WK-675 row ("quote sandbox + ladder waterfall"). […]
> - **2026-09-28 11:28:03 BST: DP1 is decided as OPTION A.**
>   - **WK-672 builds the backend limb:** `POST /api/v1/score/compare`, which scores one quote against two Rating Versions through the one shared evaluator (WK-671) and returns the step-level diff. It carries tests that pin the diff's shape and a broken-input proof (versions that differ in one step: exactly that step is reported).
>   - **WK-675 builds the frontend limb:** the Quote Sandbox view on top of that endpoint.
>   - **FR-262 is delivered only when both limbs have landed.** WK-672's closure record types it "backend limb delivered and tested (WK-672); UI limb **reassigned** to WK-675", naming the reassignment's owner and event, not as delivered.
>   - WK-672's Slice 1 (the roadmap-row correction) names the endpoint in WK-672's row, and states in WK-675's row that the sandbox view consumes it.
>
>   **Grounds.** The endpoint is evaluator code and belongs beside the regression runs, which use the same machinery. Option B would put backend evaluator work into a frontend Work and leave the comparison untested by the testing Work. Option C would drop a requirement id from a range with no destination, the silent case §13 forbids.

The quote is verbatim except at one mark, `[…]`, at the end of its first line. There the
source's closing sentence is elided: it tells the lead to quote the block into this ruling,
naming the ruling by its working id. The working id was allocated to another record before
this one merged, so this ruling was minted as **RL-1172**. Keeping that id would cite a
record of another family.

**The reading of one phrase, CONFIRMED by the deputy.** *"The one shared evaluator
(WK-671)"* means WK-671's real-time scoring path. The endpoint makes two `score_one` calls
on the same quote, one against each Rating Version. Each ends in the shared
`build_scoring_result` tail (RL-858), and the two traces (FR-258) are diffed step by step.
**No new step evaluator is built.** This role proposed the reading, and the deputy
confirmed it as the meaning of the DP1 line, by delegation. The confirming line is stamped
2026-09-28 11:35:56 BST, item 1.

**What it obliges.**

- **Slice 1** (spec and roadmap):
  - WK-672's roadmap section names `POST /api/v1/score/compare` as its FR-262 backend
    limb.
  - WK-675's section states that the Quote Sandbox view consumes that endpoint.
- **Slice 4** (code): the endpoint, tests that pin the diff's shape, and the broken-input
  proof. It ships no frontend.
- **The WK-672 Work closure record** types FR-262 exactly as quoted above.

### 6. Slice order after these rulings

The order stays **Slice 1 → 2 → 3 → 4, one at a time** (`delivery-process.md` §8).
`PL-930`'s *"may run in parallel"* for Slices 2 and 3 is superseded by §8 and is not
followed. **No ruling here adds or removes a slice, so no re-plan is needed.** Scope moves
within the existing cut as follows:

- **Slice 1 shrinks.** F60 and F59 are applied here. Slice 1 keeps these tasks:
  - the WK-672 and WK-675 roadmap text, including DP1's two sentences;
  - `03` §4.9 `RegressionRun`;
  - the `GOLDEN_QUOTE_MISMATCH` registration;
  - the `test_contracts.py:89` label correction.
- **Slice 2 is unchanged** except for one addition: its `GoldenQuote`/`RegressionSuite`
  shapes are `model-schema` artifacts (item 3c). NFR-499's access-controlled-artifact clause
  (RL-917) still binds its store.
- **Slice 3 grows** by FR-257 limb (1) (item 4), and its generator is `hypothesis` or its own,
  on spike F4's outcome (item 3c). It builds `run_regression` as a `def` in `pricing-core` (item 3a).
- **Slice 4 is unblocked** by DP1 = A, and its scope is the backend limb only.

## What it obliges

**Made in this record's own commit, and nowhere else.** `docs/specs/03-rating-engine.md`
§5.2 is amended as follows:

- F60 (1)–(4): nine signatures added, copied from the code at `df8e5811`;
- F59: `KeyFilter` shown as imported from `model_schema.rating`;
- item 3b: `generate_contexts`'s parameter type corrected;
- one dated note under the fenced block, citing this record.

The spec keeps all ten sections, mints no requirement id, and raises no open question.

**Owed by the slices, each named in its leaf plan's scope and acceptance:**

| Owner | Obligation | From |
|---|---|---|
| Slice 1 | WK-672's roadmap section names `POST /api/v1/score/compare`; WK-675's states that the Quote Sandbox view consumes it | item 5 |
| Slice 1 | `03` §4.9 `RegressionRun`; `GOLDEN_QUOTE_MISMATCH` registered; the `test_contracts.py:89` label corrected | `PL-930`, item 3c |
| Slice 2 | `RegressionSuite` and `GoldenQuote` as `model-schema` artifacts; the store honours NFR-499 (RL-917) | item 3c |
| Slice 3 | `run_regression` / `generate_contexts` in `pricing-core` `rating/testing.py`, `def`, sync engine path; `hypothesis` at runtime if spike F4 passes, else its own seeded generator, with `skills-map.md` checked if the dependency lands; assertions as the structured union of FR-261's five classes; `RegressionRun` as a `model-schema` artifact | items 3a–3c |
| Slice 3 | FR-257 limb (1) on `submit_for_review`, with a limb-(1)-only marker | item 4 |
| Slice 4 | `POST /api/v1/score/compare`, the diff-shape tests, the broken-input proof; no frontend | item 5 |
| WK-672 closure record | FR-262 typed "backend limb delivered and tested (WK-672); UI limb reassigned to WK-675" | item 5 |
| auditor | the F60 and F59 register rows annotated `Resolved`, and F44 limb (1) re-pointed to Slice 3 | items 1, 2, 4 |

## Acceptance — the violation that must become detectable

- **F60 and F59:** a public `pricing-core` rating function or shape home that `03` §5.2
  misstates. Detected by the next two-direction §5.2 pass (the `spec-reconciler`), which
  must report no disagreement for `compile.py`, `runtime.py`, `score.py` or
  `operations.py` at the merge tree of this record.
- **Item 3a:** an `async def run_regression`. Detected by a Slice 3 test that calls
  `run_regression` from a plain synchronous context. The seed-reproducibility test follows
  spike F4.
- **Item 3c:** `pricing-core` gaining a FastAPI, SQLAlchemy or Redis import. Detected by
  `lint-imports`, which must stay green on Slice 3's tree.
- **Item 4:** a Rating Version reaching `approved` with no passing `RegressionRun` for its
  current bundle hash. Detected by Slice 3's three negative tests: no run, a failing run,
  and a run against a stale hash. Each must be refused with `EVIDENCE_INCOMPLETE`.
- **Item 5:** a `score/compare` diff that misreports. Detected by Slice 4's broken-input
  proof: for two versions that differ in exactly one step, exactly that step is reported.
