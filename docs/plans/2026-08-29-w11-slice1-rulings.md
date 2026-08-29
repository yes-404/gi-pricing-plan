# W11 Slice 1 decision-point rulings — the eight decisions that block Tasks 1.2 to 1.5 (2026-08-29)

**What this is.** `.claude/roles/decision-maker.md` requires every decision point to be
pre-resolved *before* its slice starts. W11 Slice 1 is the pilot for the NT-0010/0011
process adoption (`docs/process/delivery-process.md` §14, step 6), so this is the record
that clears it. The frozen plan is
[`2026-08-29-w11-scoring.md`](2026-08-29-w11-scoring.md); the recovered options and
recommendations behind three of the decisions below are
[`2026-08-29-w11-decision-points-recovery.md`](2026-08-29-w11-decision-points-recovery.md).
A frozen plan is never edited — this is its dated sibling, the same treatment
[`2026-08-29-w11-prework-rulings.md`](2026-08-29-w11-prework-rulings.md) gave Rulings 1–5.

**Numbering continues that record at 6.** Rulings 1–5 are its; nothing here reuses a
number, for the same reason `CLAUDE.md` §5 gives for requirement ids. A ruling is cited as
"Ruling N" plus the file it lives in, never by bare number.

**Mints no `FR-`/`NFR-`/`OQ-` id.** Every requirement id below is already defined in
`docs/specs/`. One error code is appended to an existing owned-code block — error codes are
a separate namespace from `FR-`/`NFR-`/`OQ-` and this paragraph does not cover them.

**Every literal, line number, route, signature and requirement id below was grepped or read
against `origin/main` at `7b8473a`** before being written down. Where a claim recovered from
an earlier document turned out to be wrong against that tree, this record says which claim
is wrong in its own first sentence rather than hedging — `docs/process/delivery-process.md`
§15.

**Three of the first six were on no list, and a seventh arrived after they were filed.**
Ruling 12 was raised by the planner during execution, which is the honest shape of
pre-resolution: it catches most of them early and not all of them. Rulings 7, 8 and 10's *subject* was named in
the recovery document; Rulings 7 and 8 as filed are new decisions found by reading the
shipped source that Tasks 1.2, 1.3 and 1.4 will actually build against. That is what
pre-resolution is for, and it is also the honest state of the frozen plan: it carries an
unresolved "or" (Task 1.2) and one factual claim about an existing function that does not
hold (Task 1.3).

---

## Ruling 6 — DP3: load-generation tooling for the sustained-200 rps test

**The decision, restated.** DP3 (`2026-08-29-w11-scoring.md:199-206`) asks which tool
generates load for the sustained-200 rps measurement `NFR-RATE-1`
(`../specs/03-rating-engine.md:777`) and `NFR-OVR-1` (`../specs/00-overview.md:518`) both
state, and which `../roadmap.md:146` schedules as a Phase 2 W11 test. Options as the plan
states them: **(a)** add `locust`; **(b)** hand-roll `asyncio` + `httpx` following the
`scripts/bench-model.py` / `scripts/bench-data.py` convention; **(c)** shell out to an
external CLI (`hey` / `wrk` / `k6`).

**Ruled: (b).**

Rationale, and two corrections to the plan's own framing of it:

- **(b) adds no dependency, and the plan's "(no new dependency)" gloss is right for a
  reason it does not give.** `httpx` is already a root dependency
  (`../../pyproject.toml:24`, present because FastAPI's `TestClient` is an `httpx`
  transport) and a backend one (`../../backend/pyproject.toml:18`). `asyncio` is stdlib.
  So (b) triggers neither of `.claude/skills/spec-change`'s coupled obligations — no `03`
  §8 row, no `../skills-map.md` row. **(a) triggers both**, and (c) trades a Python
  dependency for an unpinned system one that CI does not install, which is worse for a
  measurement that has to be reproducible to be worth taking.
- **Correction: `bench-model.py` and `bench-data.py` use no `asyncio` and no `httpx`.**
  Both are stdlib-only — `time.perf_counter` for timing and a daemon `threading.Thread`
  sampler for CPU occupancy (`../../scripts/bench-model.py`, 785 lines;
  `../../scripts/bench-data.py`, 307 lines). What (b) inherits from them is their
  **governance** convention, stated verbatim in `bench-data.py`'s docstring and quoted back
  by `bench-model.py:4-9`: *"Not a CI gate. A timing assertion on a shared runner fails for
  reasons that have nothing to do with the code, and a check that fails randomly teaches
  everyone to re-run it. This produces numbers for a workstream closure record instead,
  where a human reads them once against the budget."* That convention binds: the load
  generator is **not** a CI gate, and its result is a dated note under `docs/research/`.
  It does not follow that their library set binds, and stating the convention as
  "asyncio + httpx following bench-model.py" conflates the two.
- **Correction: Task 1.5 needs no load generator at all, and this ruling does not give it
  one.** The plan tags Task 1.5 `[depends on DP3]` and the sequencing table repeats it, but
  Task 1.5's own exit criteria measure `score_one` directly — *"no HTTP, no FastAPI"*
  (`2026-08-29-w11-scoring.md:452`). A single-process p99 over a loop needs `perf_counter`,
  not a load generator. **DP3 binds Task 2.1**, which is where the plan itself puts the
  sustained-200 rps measurement (`:439-442`, `:479`). Task 1.5 is unblocked either way; what it
  takes from this ruling is the governance convention above, which it was already told to
  follow.

**Disposition.** No spec change. `scripts/bench-rating.py` (Task 1.5) is stdlib-only and
follows `bench-model.py`'s shape. The sustained-load driver (Task 2.1) is `asyncio` +
`httpx` in the same `scripts/` convention, not a CI gate, its result a dated
`docs/research/` note. No `03` §8 row and no `../skills-map.md` row is owed by either.

**Acceptance test — the thing that must be true, stated as the violation.** If a later PR
adds `locust`, `k6`, `hey` or `wrk` to any `pyproject.toml`, `uv.lock`, CI workflow or
setup instruction for this measurement, this ruling has been overridden and needs a
successor record. As of `7b8473a` none of the four appears anywhere in the repository
except in DP3's own two option lines.

---

## Ruling 7 — the hydration seam: a `model_call`'s payload travels **inside** the `Bundle`, never as a reference

**The decision, and where it is currently left open.** Task 1.2 tells the executor to
*"fetch real model content (coefficients **or** a booster blob reference) for the `model`
branch"* (`2026-08-29-w11-scoring.md:277-280`, emphasis added). That "or" is not a type
split the executor can resolve locally: it decides what `Bundle.resolved_payloads`
(`../../packages/pricing-core/src/pricing_core/rating/compile.py:350-364`) holds, and
therefore whether Task 1.3's `load_bundle` performs I/O — which decides its signature, its
`def` / `async def`, and whether `pricing-core` needs an injected reader protocol at all.
`_Resolver.resolve`'s `model` branch today returns `payload={"status": model.status}`
(`../../backend/src/app/platform/rating_versions.py:253-265`), a placeholder that answers
neither.

**Options:**

- **(a) Inline.** The resolved payload carries the artifact itself — GLM coefficients as
  data, a GBM booster as its serialised form — inside `Bundle.resolved_payloads`. `Bundle`
  stays exactly what its own docstring and DP1 say it is.
- **(b) By reference.** `resolved_payloads` carries a content-addressed blob reference
  (`../specs/07-platform.md` FR-PLAT-18/19) that something dereferences at hydration time.
  `Bundle` gets small; `load_bundle` gets I/O.
- **(c) Split by artifact kind** — coefficients inline, boosters by reference.

**Ruled: (a), inline, for every artifact kind including boosters.**

Rationale:

- **`NFR-RATE-4` (`../specs/03-rating-engine.md:780`) settles it in the requirement's own
  words:** *"bundle size stays under 500 MB **including booster artifacts**."* A size budget
  is only stated over what is inside the thing being sized. Under (b) or (c) a `Bundle`
  carrying a reference is a few kilobytes and the clause has nothing to bound. Two
  independent corroborations: `03` §8's Redis row calls the cached thing the
  `` `Bundle` `` cache *"keyed by content hash"* (`:757`), and `../skills-map.md:94`'s
  Redis row names the sizing problem as *"memory sizing for 500 MB bundles"* — a 500 MB
  value in Redis is a bundle with its boosters in it, not a pointer to one.
- **It is what `FR-RATE-24` (`:135`) and `compile.py`'s own DP1 comment already say**, and
  the only reading that needs no requirement amended. `FR-RATE-24`: the Bundle *"is
  sufficient to score with no database access."* `compile.py:280-283`: *"The Bundle is
  self-contained: sufficient to score with no database access."* Under (b) the Bundle stops
  being self-contained and both would need amending. `CLAUDE.md` §0 says a code/spec
  disagreement is resolved rather than made to match quietly — here the reading that
  requires no amendment is also the one three separate artifacts already state.
- **This ruling deliberately does *not* lean on `NFR-RATE-3` (`:779`),** and says so because
  the temptation is obvious. `NFR-RATE-3` reads *"A compiled bundle scores with **zero**
  database or network access; everything it needs is inside it,"* and its subject is now
  ambiguous: since `FR-RATE-65` (`:139`) "Compiled Bundle" is the glossary's name for the
  loaded runtime type (`:67`), so `NFR-RATE-3` may be constraining `CompiledBundle`, under
  which a blob fetch during hydration — before any scoring — would satisfy it. Ruling 4's
  own addendum flagged exactly this imprecision and deliberately left it
  (`2026-08-29-w11-prework-rulings.md:399-404`). It is still open, it is **not** reopened
  here, and it is not load-bearing for this ruling: `NFR-RATE-4` names `Bundle` explicitly
  and needs no disambiguation.
- **(b) also collides with `ADR-0001` in a way (a) does not.** `pricing-core` may not import
  `redis`, `httpx`, `requests`, `boto3` or `botocore` — `.importlinter:16-34`, contract
  `core-has-no-infrastructure`, `allow_indirect_imports = false`. A dereferencing
  `load_bundle` therefore needs an injected reader Protocol, mirroring
  `ArtifactResolver` (`compile.py:298`). That is buildable, so it is not an argument that
  (b) is impossible — it is an argument that (b) costs a new injected dependency, a new
  async signature, and two amended requirements to buy a smaller Redis value that
  `NFR-RATE-4` and `skills-map.md:94` both already budget for at full size.

**Disposition — two parts, one of them a spec change applied in this commit.**

1. **`load_bundle` takes no resolver and performs no I/O**, and its signature is added to
   `../specs/03-rating-engine.md` §5.2, which today lists every other `pricing-core` rating
   module and has no `rating/runtime.py` block at all — `git grep -n load_bundle` over
   `docs/specs/` and `docs/workflows/` returns zero hits at `7b8473a`, while `FR-RATE-65`
   requires *"a hydration step"* and names no function for it. Appended as
   `def load_bundle(bundle: Bundle) -> CompiledBundle`, plain `def` per
   `.claude/skills/spec-change`'s rule: it awaits no injected async dependency and no native
   async binding. This completes Ruling 4's disposition, which named `load_bundle` in prose
   and never landed it in an interfaces section.
2. **The payload must survive a JSON round trip**, because `Bundle` is persisted and cached
   as JSON and `resolved_payloads` is typed `dict[str, Any]` (`compile.py:361`). Raw
   `bytes` do not. This is not a new constraint on the executor so much as a fact about the
   existing type, and the existing GBM path already produces a JSON-shaped artifact —
   `../../packages/pricing-core/src/pricing_core/modelling/gbm.py:975` persists a booster as
   `bytes(booster.save_raw(raw_format="json"))`. **`NFR-RATE-4`'s 500 MB is measured on the
   serialised form**, so Task 1.3's `NFR-RATE-4` exit criterion measures the persisted
   `Bundle`, not an in-memory estimate.

**Flagged, not ruled — a headroom risk this ruling creates and does not close.** A `Bundle`
approaching `NFR-RATE-4`'s 500 MB is at the edge of what a Redis string value can hold
(Redis's own limit is 512 MB), and text-encoding a booster spends headroom to get there.
`skills-map.md:94` already lists *"memory sizing for 500 MB bundles"* and *"eviction policy
that must never evict the live bundle"* as open research against `FR-RATE-51` / `NFR-RATE-6`
— this ruling adds the encoding-overhead term to that existing question rather than opening
a new one. It becomes real only when a bundle with a large booster is measured, which is
Task 1.3's own `NFR-RATE-4` criterion; if that measurement lands near the cap, it is a
finding against `NFR-RATE-4`, not against this ruling.

---

## Ruling 8 — the loaded-booster seam does not exist: `predict_gbm` re-loads the booster on every call

**The claim in the frozen plan that does not hold, named first.** Task 1.3 instructs the
executor to build `CompiledBundle` holding *"any GBM boosters loaded from
`Bundle.resolved_payloads` into live `Booster` objects **via the existing
`predict_gbm`/`predict_glm` loaders**"* (`2026-08-29-w11-scoring.md:322-326`, emphasis
added). **There are no such loaders.** `predict_gbm` is a predictor, not a loader:
`def predict_gbm(result: GbmFitResult, booster: bytes, data: pl.DataFrame, ...) -> pl.Series`
(`../../packages/pricing-core/src/pricing_core/modelling/gbm.py:1185-1192`; the same
signature in `../specs/02-modelling.md:2345-2348`). It takes **bytes**, and on the XGBoost
branch constructs a fresh handle and deserialises into it on every invocation —

```python
loaded = xgb.Booster()
loaded.load_model(bytearray(booster))
```

(`gbm.py:1248-1250`) — and on the LightGBM branch does the same with
`lgb.Booster(model_str=booster.decode())` (`gbm.py:1269`). It returns predictions and never
the handle, so there is nothing for a `CompiledBundle` to hold. `predict_glm` takes a
`GlmFitResult` and no bytes (`../../packages/pricing-core/src/pricing_core/modelling/predict.py:230-239`), so the GLM half needs
nothing; the gap is the GBM half only.

**Why this is a decision and not an executor detail.** Following the instruction as written
puts a full booster deserialisation on the per-quote hot path, which is the exact cost
`FR-RATE-65` exists to remove — it requires boosters *"loaded from `resolved_payloads` into
**live objects**"* (`../specs/03-rating-engine.md:139`) — and the exact cost Ruling 4's
rationale rejected option (a) for. `NFR-RATE-1` is p99 < 50 ms with one `exact` GBM call;
`NFR-RATE-14` (`:789`) measures the `nthread=1` prediction itself at p99 1.626 ms on this
machine, so a per-call `load_model` is not a rounding error against that budget, it is the
budget. Resolving it changes a shipped `pricing-core` public signature and therefore
`02-modelling.md` §5.2, which is a spec change, not a local refactor.

**Options:**

- **(a) As the plan says** — `score_one`'s `model_call` calls `predict_gbm(result,
  booster_bytes, ...)` per quote. Zero new surface; defeats `FR-RATE-65` and spends the
  latency budget on work `CompiledBundle` exists to have already done.
- **(b) Split the seam** — a loader that returns the live booster object, and a prediction
  entry point that accepts one. `predict_gbm` keeps its present signature as a thin
  `load + predict` wrapper over the two, so **no existing caller changes** and no test moves.
- **(c) Memoise inside `predict_gbm`**, keyed on the bytes or their hash.

**Ruled: (b).**

Rationale:

- **(c) is the hidden cache Ruling 4 already rejected**, one level down. Its words:
  *"That hidden cache would just be option (b) again, minus the type system saying so —
  worse for testability (nothing distinguishes 'freshly deserialised' from 'already loaded'
  at the type level)"* (`2026-08-29-w11-prework-rulings.md:297-300`). The argument transfers
  intact from `Bundle`/`CompiledBundle` to `bytes`/`Booster`; ruling it differently here
  would make the same platform hold two contradictory positions on the same question.
- **(b) is the only option under which `FR-RATE-65`'s "live objects" clause has a
  referent.** Under (a) `CompiledBundle` holds bytes it re-parses per call, which is what
  `Bundle` already holds.
- **`predict_gbm`'s signature is preserved deliberately.** It has been corrected twice
  already (`../specs/02-modelling.md:2481` and `:2516`, 2026-08-16 and 2026-08-17), each time by a slice
  that found its behaviour wrong; a third change to its shape while W11 is mid-flight would
  put every existing caller and diagnostic in the blast radius of a rating-engine slice.
  Wrapping is strictly cheaper than changing.

**Disposition — the executor's, and *not* pre-written here.** The seam's function names,
the loaded type's name, and whether the loader lives in
`pricing_core/modelling/gbm.py` beside `predict_gbm` or in `pricing_core/rating/runtime.py`
beside `CompiledBundle` are Task 1.3's design, constrained only by the two clauses above.
This ruling deliberately writes no signature into `02-modelling.md` §5.2, because naming a
function before it is designed is how a spec acquires a signature nothing implements —
`FR-RATE-65` and `CompiledBundle` were that exact failure, and Ruling 4 exists because of
it. **The obligation instead: the PR that adds the loader appends its signature to
`../specs/02-modelling.md` §5.2 in the same commit**, per `CLAUDE.md` §2 (spec and code land
together) and §5's ten-section standard, where §5.2 is the `pricing-core` interface list.

**Acceptance test, stated as the violation that must become impossible.** A test asserting
that scoring N quotes against one `CompiledBundle` performs exactly **one** booster
deserialisation, not N. Written to fail against the plan-as-written implementation (a)
first — a probe that has never gone red has not been tested (`CLAUDE.md` §13).

---

## Ruling 9 — how a decline is represented: the whole DAG evaluates, and every firing constraint's code is collected

**The decision.** Recovery item 5 (`2026-08-29-w11-decision-points-recovery.md`, §5): does a
`constraint` step's decline short-circuit DAG evaluation, leaving downstream ladder rungs
null or absent **(a)**, or does the full DAG always evaluate with `outcome` flipping to
`declined` and `decline_reasons` collecting every firing step's code **(b)**? Task 1.4 says
only *"constraint decline is `outcome: declined`, never an error"*
(`2026-08-29-w11-scoring.md:388-390`) and is silent on which.

**Ruled: (b) — full evaluation, collect all.** Not a taste call: it is what a committed
contract already requires.

**Correction to the recovery document's stated grounds, before the grounds this ruling
actually rests on.** Recovery item 5 argues (b) because *"§4.4 example shows
`decline_reasons` as a **list** alongside a fully-populated `premium_ladder`."* **The
"alongside" half is wrong.** `../specs/03-rating-engine.md:399-420` shows exactly one
`ScoringResult`, and it is not a declined one: `outcome` is the literal placeholder
`"quoted | declined | error"` (`:401` — the enum written out, not a value) and
`decline_reasons` is `[]` (`:417`). The ladder is fully populated, but beside an **empty**
reason list, so the example is evidence about the *schema* — one shape, `decline_reasons`
an array — and no evidence at all about ladder population under a decline. Nothing in §4.4
shows a worked declined quote. The recommendation survives; that particular argument for it
does not, and repeating it would put a checkable falsehood into a filed record.

Grounds this ruling does rest on, strongest first:

- **`docs/contracts/schemas/scoring.schema.json:48` makes `premium_ladder` required for
  every outcome**, `declined` included:
  `"required": ["outcome", "rating_version_ref", "bundle_hash", "premium_ladder", "outputs"]`,
  with `"outcome": {"enum": ["quoted", "declined", "error"]}` (`:50`). Option (a) produces a
  result that violates its own contract. **Cite this contract by its tier**: it is
  hand-authored Phase 0 (`docs/contracts/README.md`'s table — `schemas/` is authored,
  `schemas/generated/` is not), and it is explicitly *not* yet covered by the drift guard —
  `../../backend/tests/test_contracts.py:89` carries `"scoring": "later-phase — 03 rating"`.
  So it is **specified and not enforced**: authoritative as specification, and nothing today
  would catch a violation of it. That is a reason to hold Task 1.4 to it deliberately, not
  a reason to discount it.
- **The contract's own invariant requires a ladder that reaches the end**, not a truncated
  one: *"applying every rung's recorded operation to risk_premium reproduces payable_premium
  exactly (FR-RATE-32)"* (`scoring.schema.json:60`), which `NFR-RATE-8` re-states as a
  measured property. A ladder short-circuited at the `constraints` rung cannot satisfy it.
- **`FR-RATE-11` (`../specs/03-rating-engine.md:111`) is written in the plural, over
  steps:** *"**Each** carries a `reason_code` that appears in the Trace **and in any decline
  response**."* Under (a), only the first firing step's code can appear, because the others
  never evaluate — so (a) makes `FR-RATE-11` false for every constraint after the first.
- **`FR-RATE-5` (`:85`) specifies topological-order evaluation and no early-exit
  primitive**, and a sweep of §3 and §4.3 for `short-circuit`, `early exit`, `halt`,
  `stop evaluating` and `skip remaining` returns a clean zero. `FR-RATE-39` (`:167`) says a
  decline is *"a **successful** scoring response with `outcome: declined` and reason
  codes"* — plural, and successful, which is the shape of a completed evaluation.
- **One row schema for batch.** Under (b), quoted and declined rows share
  `outcome: string` + `decline_reasons: list[str]` with no nullable-ladder variant, which is
  what Slice 3's parquet output and `05`'s trace consumption both want.

**Already settled, so not ruled here: the element type of `decline_reasons`.** It is
`array<string>` — bare reason codes — in three committed places:
`../specs/03-rating-engine.md:247` (`{"name": "decline_reasons", "type": "array<string>",
"required": false}`), `docs/contracts/schemas/scoring.schema.json:55`, and
`docs/contracts/schemas/regression-suite.schema.json:26`. Per-step detail lives in the
Trace, which already carries `{"applied": ..., "reason_code": ...}` per constraint step
(`../specs/03-rating-engine.md:437-441`); duplicating it into `decline_reasons` would
duplicate the Trace. This was on the list to rule and dissolved on being looked up — it is
recorded as settled rather than silently dropped.

**Disposition — a spec change applied in this commit.** `FR-RATE-39` gains a dated
amendment in place, per `CLAUDE.md` §5 (ids permanent; amend in place, never renumber). It
appends no new `FR-` because it adds no obligation the requirement did not already carry —
it makes precise which of two readings of "reason codes" was meant, and names the contract
that already decided it.

**Acceptance test, stated as the violation.** A `QuoteContext` firing **two** constraint
declines returns `outcome: declined`, `len(decline_reasons) == 2`, and a `premium_ladder`
that reconciles to `payable_premium_minor` under `NFR-RATE-8`'s check. Two, not one: a
single-decline test passes under (a) and (b) alike and would prove nothing.

---

## Ruling 10 — the warm-worker refresh trigger is W14's, and Slice 1 owes it exactly two properties

**The decision.** Recovery item 1 carries forward, from the unfiled W11 orientation report,
a refresh mechanism Ruling 4 never restated: each worker *"refreshed by a short background
poll against 'current hash for env X'"*, recommending *"poll over pub/sub … NFR-RATE-6's 30
s switchover budget has plenty of room for a ~1-2 s poll."* The recovery document asks a
decision-maker to *"confirm this mechanism (or rule a different one) when Task 1.3's refresh
behaviour is built."*

**Ruled: neither. The refresh trigger is not W11's to build, and Task 1.3 builds no refresh
behaviour.** The recommendation is declined as premature rather than wrong.

Rationale:

- **Nothing in Slice 1 or Slice 2 builds a cache tier for it to sit in.** A grep of the
  frozen plan for `redis`, `cache`, `warm`, `refresh`, `poll` and `slot` returns four hits
  in total, none of them a task: two in the tech-stack preamble (`:31`, `:33`), one that is
  Job-status polling for a 202 (`:292`), and Task 1.3's description of `CompiledBundle` as
  *"what a warm worker process holds after loading one"* (`:310`). `load_bundle` appears
  five times and is never described as called repeatedly or on a timer. Slice 2 has zero
  hits for all six terms. There is no in-process slot to refresh and no Redis tier to
  refresh it from.
- **The refresh trigger belongs to Deployment, and Deployment is W14.** A warm worker learns
  a new bundle exists *because a deployment switched* — `FR-RATE-51` (`:194`), `FR-RATE-50`,
  `03` §3.10, with `NFR-RATE-6`'s 30 s budget (`:782`) measured from the deploy command.
  DP1 already establishes Deployment and the Environment entity (`FR-PLAT-28`) as W14's,
  three workstreams out. Ruling a refresh mechanism now is building ahead of the phase,
  which `CLAUDE.md` §9 forbids and §0's table routes to a spec change instead.
- **When it is ruled, "poll" starts behind, not ahead.** Two facts the orientation report
  did not have. First, the only mechanism `docs/specs/` actually specifies is a **push**:
  `FR-RATE-51` — *"Bundles are pre-warmed into cache before the switch"* — and `03` §6 step
  11, *"Backend Pre-warms the bundle, switches atomically, emits Audit Event +
  notification"* (`:706`). A sweep of all of `docs/specs/` for `poll`, `pub/sub`, `pubsub`,
  `subscribe`, `invalidate`, `refresh` and `warm` finds no refresh mechanism of any kind for
  the bundle cache. Second, `07` has already ruled against polling as a platform pattern,
  in a clause that names this exact situation: `FR-PLAT-61`
  (`../specs/07-platform.md:102`) — *"**Event-triggered runs are not polled**: where a
  platform event should start a Job — a deployment creating its monitors (`wf-04`) — the
  transaction recording the event submits the Job in the same outbox write, so there is no
  sensor watching the database for something the platform already knows."* A deploy-time
  push is the platform's stated shape; a 1–2 s per-worker poll is the sensor it names. That
  is not a ruling against poll — `FR-PLAT-61` scopes itself to Job submission, and a
  cross-process cache handoff is a different problem — but it means W14 starts from push and
  argues its way to poll, rather than the reverse.

**Disposition — no spec change; two properties Slice 1 must have so W14 has a choice left.**
Both are already implied by Ruling 4 and are stated here so Task 1.3 cannot quietly close
the option:

1. **`CompiledBundle` exposes the `content_hash` of the `Bundle` it was loaded from.** Every
   candidate switch mechanism — push, poll, or pub/sub — compares a held hash against a
   current one. A `CompiledBundle` that has forgotten its provenance cannot participate in
   any of them, and `FR-RATE-51`'s *"either the old or the new bundle, never a mix"* becomes
   unverifiable at runtime.
2. **`load_bundle` is pure with respect to the cache**: it consults no cache, registers
   itself in no global, and starts no background task. It takes a `Bundle` and returns a
   `CompiledBundle`. This is not merely tidy — `.importlinter:16-34` forbids `pricing_core`
   from importing `redis` at all, so any cache tier must live above it in `backend/`, and a
   `load_bundle` that owned a slot would put the seam on the wrong side of `ADR-0001`.

---

## Ruling 11 — `MODEL_CALL_FAILED`

**The decision.** `FR-RATE-38` (`../specs/03-rating-engine.md:166`) names five per-quote
error categories: *"contract violation, reference miss, table miss, constraint decline,
model failure."* §5.1's owned-code block (`:527-540`) covers three
(`INPUT_CONTRACT_VIOLATION`, `REFERENCE_LOOKUP_MISS`, `RATE_TABLE_MISS`); constraint decline
is `FR-RATE-39`'s successful-response path and correctly has no code; **model failure has
none.** Recovery item 4 recommends declaring `MODEL_CALL_FAILED`, matching the existing
`_FAILED` suffix family, and says the decision-maker will *"rule this formally (as a spec
change appending to §5.1's owned-code list) once the plan reaches the slice."* The slice has
been reached.

**Ruled: confirmed. `MODEL_CALL_FAILED`,** appended to `03`'s owned-code block in this
commit, dated in the same style as the block's two existing `*(added …)*` annotations.
Re-verified at `7b8473a`: `git grep -n MODEL_CALL_FAILED` returns five hits, all in
`docs/plans/`, none in `docs/specs/` or `backend/` — so the code is unowned and check 10 of
`../../scripts/audit-docs.py` (cross-spec ownership exclusivity, `:574-598`) cannot
conflict on it. The alternative, reusing `BUNDLE_COMPILE_FAILED`, is refused for the reason
recovery item 4 gives: it names a compile-time failure and would blur the audit trail
between a bundle that would not build and a booster that would not answer.

**No `FR-` is appended.** `FR-RATE-38` already states the obligation ("model failure" is one
of its five categories); this names the code that discharges it. Error codes are a separate
namespace, and `../../backend/src/app/errors.py`'s own `PlatformError.__init__` names the
spec as the authority — *"Codes are enumerated in the owning spec's Interfaces section; add
it there before raising it"* (`errors.py:344-348`). Spec first is therefore the enforced
order, and this commit is that first half.

**For the executor, verified and not assumed.** Adding the code to the spec does not make it
raisable. `PlatformError` refuses any code outside `_KNOWN_CODES` (`errors.py:314-321`,
`:335-349`), and `RATING_ERROR_CODES` (`:275-307`) does not currently contain
`MODEL_CALL_FAILED` — nor, checked at the same tree, `INPUT_CONTRACT_VIOLATION`,
`REFERENCE_LOOKUP_MISS` or `LADDER_RECONCILIATION_FAILED`, all three of which §5.1 already
lists as owned and all three of which Task 1.4's error-typing work names. **Four codes, not
one**, must reach `RATING_ERROR_CODES` before anything raises them as a `PlatformError`.
Their absence today is a not-yet-built path rather than a defect — none has a caller — but
an executor reading Task 1.4 and expecting three of the four to already exist will find they
do not. Separately: inside `pricing-core`, which cannot import `app`, the established
convention is a code-named `ValueError` — `compile.py`'s `_raise_named` produces
`ValueError(f"{code}: {message}")` — so `score_one`'s own refusals follow that, and the
mapping to `PlatformError` happens at the backend boundary in Slice 2.

---

---

## Ruling 12 — `QuoteContext.purpose`: the spec is right and the hand-authored contract is stale, and the fix belongs to Task 1.4

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
  `OQ-RATE-4` (`:807`): *"**DECIDED 2026-08-18**: the same algorithm for the risk price, with
  pro-rata/refund/charge logic in a separately-versioned sub-graph mounted on `purpose` —
  FR-RATE-63. §2's `purpose` gained `cancellation` in the same edit, because the answer keys
  on a value that did not exist."* Dropping `cancellation` to match the contract would
  silently reverse a maintainer decision, which is the outcome `CLAUDE.md` §0 forbids by
  name.
- **`FR-RATE-63` (`:87`) cannot be satisfied under the four-member enum.** It mounts the
  sub-graph *"only when `purpose ∈ {mid_term_adjustment, cancellation}`"* and requires that
  *"a version that mounts no such sub-graph **refuses** an MTA or cancellation quote rather
  than pricing it as new business — pricing it as new business is the failure this
  requirement exists to prevent, and it is silent."* A `QuoteContext` that cannot carry
  `cancellation` cannot be built to be refused, so half the guard is unexpressible, not
  merely untested.
- **Provenance checked, not inferred.** `scoring.schema.json` has exactly two commits in its
  whole history — `b452c78` (the Phase 0 draft) and `cb9dd78` (the remaining ten artifact
  schemas) — and neither is `eb43022`, the 2026-08-18 commit that decided `OQ-RATE-4`. That
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
  today"*. Per `ADR-0002` and `CLAUDE.md` §2, `model-schema` is the single source of truth
  and Task 1.4 is what creates it. Correcting the hand-authored contract now would fix the
  only *existing* copy while the *authoritative* one is still unwritten — and open a second
  window for the two to diverge again, which is the failure being fixed.
- **`CLAUDE.md` §2 wants them in one commit**: a change spanning spec and code *"lands as
  **one commit** — spec, code, tests, any skill update — or the audit reports a consistency
  the repository does not have."* The `model-schema` enum, the contract line and
  `FR-RATE-63`'s refusal test are one change.
- **Charter boundary, named rather than routed around.**
  `.claude/roles/decision-maker.md`'s Tools line grants writes to ruling records, the
  open-questions log and `docs/specs/`. It does **not** name `docs/contracts/`. Ruling which
  side is wrong is §0 and is this role's; editing a hand-authored contract file is not
  granted to it. (b) is the disposition the charter permits *and* the better engineering, so
  nothing is lost here — but see the finding below, because that will not always be true.

**Binding on Task 1.4 — three obligations, all in one PR** (a fourth is added by the
addendum below):

1. `QuoteContext.purpose` carries **five** members including `cancellation`, defined once in
   `model-schema` (`ADR-0002`, `CLAUDE.md` §2 — nobody hand-writes a shape `model-schema`
   owns).
2. `docs/contracts/schemas/scoring.schema.json:12` is corrected to those five in the same
   commit.
3. **`FR-RATE-63`'s refusal test covers both members, not one.** The frozen plan's exit
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

**Addendum to Ruling 12, filed the same day, after `b826790` merged.** Raised by the lead
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
`FR-PLAT-48`'s drift gate has nothing to fire on and `scripts/generate-contracts.py --check`
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
(`:818`) and `RateTableDiff` (`:684`) — all shipped by W9 and W10. Each has a hand-authored
contract on disk (`docs/contracts/schemas/rating-algorithm.schema.json`,
`rating-version.schema.json`, `rate-table.schema.json`). And:

- `grep -n "RatingVersion\|RatingAlgorithm\|RateTable" scripts/generate-contracts.py` returns
  **zero**. A true negative, not a pattern miss: `GENERATED_SHAPES` is a `dict[str, str]` of
  slug → class name whose values are literally `"Job"`, `"Banding"`, `"ModelComparison"` and
  so on, so a class name would appear verbatim if it were there.
- `test_contracts.py` still excludes all three as `"later-phase — 03 rating"` — a reason that
  expired when W9 and W10 built the types.

So three shipped `model-schema` types have hand-authored contracts that **nothing has ever
compared them against**, and the exclusion that permits it now misdescribes why. `scoring`
becomes the fourth the moment Task 1.4 lands without obligation 4.

**Corrected with the paragraph above, and for the same reason:** the first filing of this
finding called it *"the identical mechanism that produced the `purpose` divergence, already
in place three more times."* It is not identical. This is the **contract-versus-code** gap;
`purpose` is the **spec-versus-contract** gap. They are siblings — the third finding below is
the parent both belong to — and running them together is what made the overstated claim above
sound reasonable when it was written.

Not proposed for fixing here: whether W9's and W10's closes should be reopened for it, or
whether it becomes a register row with an owner, is a scope question for the lead and the
§14 plan review — `CLAUDE.md` §12 and `docs/process/delivery-process.md` §5 step 7 both put
that call outside this role. What is ruled is only that **W11 does not add a fourth.**

## Second finding: `purpose` was not the only shape `eb43022` left behind, and the second is worse

A sweep of every enum `03-rating-engine.md` declares in §2 and §4 against its hand-authored
schema found **two** disagreements, not one, and both were landed by the same 2026-08-18
commit:

| # | Shape | Spec | Hand-authored contract | Gap |
|---|---|---|---|---|
| 1 | `QuoteContext.purpose` | `:63`, `:240-241` | `scoring.schema.json:12` | enum member `cancellation` missing |
| 2 | `RateTableVersion.storage` | FR-RATE-62 `:123`, `:289`, `:310-316` | `rate-table.schema.json` | **the whole field is absent** |

**The second is the worse one**, and it is `03`'s, not W11's: `FR-RATE-62` added `storage`
(`rows \| parquet`, "fixed when the version is written and immutable with it") on 2026-08-18,
and `grep -n storage docs/contracts/schemas/rate-table.schema.json` returns **nothing** — not
in `properties`, not in `required`. That schema has exactly one commit in its history
(`b452c78`, 2026-08-14), so it has never been touched since it was drafted, including not for
the requirement that added a field to it. W10 shipped `RateTable`/`RateTableVersion` into
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

## Ruling 13 — `03` §5.2's money block: the code is right, the spec is stale in four ways, not the two reported

**Raised as `F-W11-1-5`** in the Slice 1 plan (`2026-08-29-w11-1-evaluator-core.md`, PR #370),
which routed it here correctly: *"it is a spec-vs-code conflict, which `delivery-process.md`
§3 makes theirs."* It is `CLAUDE.md` §0's question — which of spec and code is wrong — and
this record answers it.

**The finding as reported understates its own scope, and the count is the part worth
correcting first.** `F-W11-1-5` says *"Both the module path and the third parameter's name
differ."* Checked against `002f4d8`, **four** things differ, and two of them are not in the
report:

| # | Spec, `../specs/03-rating-engine.md` §5.2 | Shipped code | Reported? |
|---|---|---|---|
| 1 | module `pricing_core/rating/money.py` (`:619`) | `packages/pricing-core/src/pricing_core/money.py`; **no `rating/money.py` exists** | yes |
| 2 | `apply_factor(..., rounding: Rounding)` (`:621`) | `apply_factor(..., mode: RoundingMode)` (`money.py:33`) | the name, yes |
| 3 | the type `Rounding` | `RoundingMode = Literal["half_even", "half_up", "ceiling", "floor", "down"]` (`money.py:20`); **`Rounding` exists nowhere in the codebase** | **no** |
| 4 | declares `to_minor(value: Decimal, currency: str) -> int` (`:620`); does **not** declare `reconcile_ladder` | `to_minor` is not in `pricing-core` at all — it is `model_schema/money.py:105`, `to_minor(value: Decimal, *, places: int = 2) -> int`; `reconcile_ladder(risk_premium_minor: int, steps: list[tuple[str, int]]) -> bool` **does** exist (`money.py:55`) and the spec never declares it | **no** |

Row 4 is two errors in opposite directions in one block — a declared function that is in a
different *package* with a different signature, and an undeclared one that ships. The second
half matters for this slice: `reconcile_ladder` is what `NFR-RATE-8`'s ladder-reconciliation
test exercises, and Task 1.4's Step 12 is that test, so the plan depends on a function §5.2
does not list.

**Ruled: the code is right; §5.2 is stale.** Grounds:

- **`pricing_core.money` is public surface, not an internal path.**
  `packages/pricing-core/src/pricing_core/__init__.py:13` re-exports
  `ROUNDING_MODES, RoundingMode, apply_factor, reconcile_ladder` from it. Moving the module
  to match the spec would break `pricing-core`'s published API for a naming preference,
  which is the tail wagging the dog.
- **The parameter name is deliberate and requirement-grounded**, not incidental.
  `money.py:36-37`: *"`mode` has no default. FR-RATE-12 requires rounding to be declared per
  step; a default here would silently satisfy the type checker while defeating the
  requirement."* A spec correction costs nothing; a rename to `rounding` would gain nothing
  and lose that reasoning's anchor.
- **`Rounding` never existed.** This is not a rename that drifted — the spec names a type the
  repository has never had, so there is no code side to prefer.

**Disposition — applied to `../specs/03-rating-engine.md` §5.2 in this commit**, following
the correction convention that block already uses (`bundle_hash` carries *"corrected
2026-08-27 (F-W9-3-2)"*, `compile_bundle` was corrected to `async def` by Ruling 3):

- the module comment becomes `pricing_core/money.py`;
- `apply_factor`'s third parameter becomes `mode: RoundingMode`;
- `reconcile_ladder` is added, because it ships and `NFR-RATE-8` depends on it;
- `to_minor`'s line is replaced by a pointer comment naming where it actually lives.

**Deliberately not decided here, and flagged rather than folded in: which spec should declare
`model_schema.money.to_minor`.** It is declared in exactly one place in the whole suite today
— `03` §5.2, wrongly — and removing it from there without a home elsewhere loses the reader's
path, which is why a pointer comment replaces it rather than a deletion. But `to_minor` is
`model-schema`'s, so its §5.2 home is `00`'s or `02`'s surface, not `03`'s, and choosing
between them is a different module's interface question rather than this conflict's
resolution. Queued below.

**`F-W11-1-5`'s "not a blocker" assessment is confirmed**, and it was the planner's to make
rather than mine to accept on trust: Task 1.4 imports from the real path either way, and the
plan states the real path in its Global Constraints, so no executor reads §5.2 for it. The
correction is filed because a stale interface list is a trap for the *next* reader, not
because it blocks this one.

---

## Dispositions applied to `../specs/03-rating-engine.md`

*("this commit" in the first filing; the record has since grown across three PRs — #368, #373 and
the one carrying Ruling 13 — so each row names its own.)*

| Ruling | Edit | Section |
|---|---|---|
| 7 | Add the `rating/runtime.py` block with `def load_bundle(bundle: Bundle) -> CompiledBundle` | §5.2 |
| 9 | Dated amendment to `FR-RATE-39` — full evaluation, all firing codes collected, ladder always populated | §3 |
| 11 | Append `MODEL_CALL_FAILED` to the owned-code block | §5.1 |
| 13 | Money block corrected: module path, `apply_factor`'s third parameter, `reconcile_ladder` added, `to_minor` repointed | §5.2 |

Rulings 6, 8, 10 and 12 apply no spec edit. Ruling 8's spec change is owed by the PR that
builds the seam, and Ruling 12's contract correction by the PR that builds `QuoteContext`,
each for the reason its own disposition gives.

## Queued, not ruled — decision points whose slices have not started

Listed so that nothing here reads as overlooked. Each is ruled before its own slice, per the
same standard this record follows.

| Item | Slice | Why not now |
|---|---|---|
| **DP1** — default-live resolution for `POST /api/v1/score` | 2 | Plan recommends (b), defer to W14 as a named register deferral. Task 2.1 is not blocked by it |
| **DP2** — `FR-RATE-40`'s approval gate ahead of W12/W13 | 2 | Plan recommends (a), build the mechanism now. Blocks Task 2.3 only |
| **`FR-RATE-38`'s batch abort threshold — where it is configured** | 3 | The requirement says *"unless the failure rate exceeds a declared threshold"* and names no home. Recovery item 4 recommends a workspace setting on `FR-PLAT-45`'s precedent with a per-request override. It reaches into `07`, and Slice 3's exit criteria are where it becomes real |
| **Trace persistence — thin Postgres row + blob body, GC-based retention** | 4 | Recovery item 2's recommendation (b). Slice 4's own scope |
| **Which spec declares `model_schema.money.to_minor`** | — | Ruling 13 removed it from `03` §5.2, where it was wrong on package and signature alike, and left a pointer comment. Its correct §5.2 home is `00`'s or `02`'s surface, not `03`'s. Not urgent; it is declared nowhere correct today |
| **`FR-RATE-41`/`42` state no **batch** sampling default** | 4 | A spec silence, not a choice inside an existing requirement — recovery item 2 flags it as needing an `OQ-` or a spec change. Raised properly it is an `OQ-RATE`, which per `.claude/skills/spec-change` also takes a `../roadmap.md` §10 decision-gate row and a recount of that row's `N (M open)` count. Owed before Slice 4 |

## Findings reported, not ruled

Neither is a decision; both are reported to the lead rather than acted on here.

1. **Nothing checks error codes across the spec/code boundary, in either direction.** Check
   10 of `../../scripts/audit-docs.py` (`:574-598`) reads only `docs/specs/*.md` and only
   tests that no code is claimed as owned by two modules. It never opens
   `backend/src/app/errors.py`. So a code can be listed as owned and exist nowhere (three do
   today — see Ruling 11), and a code could exist in `errors.py` owned by no spec, and the
   gate stays green either way. `PlatformError.__init__` catches the second direction at
   runtime, on the first raise; nothing catches the first.
2. **The frozen plan's Task 1.5 dependency tag is over-broad**, and its Task 1.3 instruction
   contains one claim about shipped code that does not hold (Rulings 6 and 8 respectively).
   Recorded as a finding against the plan, **not** as a request to edit it — a frozen plan
   is frozen (`docs/plans/README.md`), and this record is where its corrections live. Both
   belong in the §14 plan review at this workstream's close, as evidence about how a plan's
   literals age, alongside `docs/plans/README.md`'s own "conventions the audit cannot check".

## Verification

- Tree: `origin/main` at `7b8473a`, fetched and confirmed equal to local `HEAD` before this
  record was started. Every line number cited above was read at that tree; a line number is
  only as good as its revision.
- `python3 scripts/audit-docs.py` — clean after the three `03-rating-engine.md` edits.
- **The `MODEL_CALL_FAILED` edit was proven to register, not assumed to.** Two controls, both
  run in the worktree that produced this commit. *Positive:* the audit's own summary line
  goes `157 error codes, ownership exclusive` on the stashed tree to `158 error codes,
  ownership exclusive` with the edit applied — so check 10's regex genuinely parsed the new
  code out of §5.1's block rather than skipping over it. *Broken input:* the same code was
  temporarily also claimed in `02-modelling.md`'s owned block, and the audit printed
  `158 error codes, **1 conflicts**` with `error code MODEL_CALL_FAILED claimed by both
  02-modelling.md and 03-rating-engine.md`, then went clean again on revert (`git checkout --
  docs/specs/02-modelling.md`, working tree confirmed back to the two intended files). A
  check that has only ever printed a pass has not been tested — `CLAUDE.md` §13. Note the
  limit of what this proves: that check 10 sees this code and rejects a double claim. It
  proves nothing about whether the code is ever raised, because nothing in the gate reads
  `backend/src/app/errors.py` at all — finding 1 below.
- The three edits touch one spec and mint no `FR-`/`NFR-`/`OQ-` id, so no
  `docs/open-questions.md` mirror row and no `../roadmap.md` §10 gate row is owed by this
  commit. The one item that *will* owe both is the `FR-RATE-41`/`42` batch-sampling gap,
  queued above.
