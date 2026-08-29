# W11 Slices 2–4 — D4, F1, M4 ruled, and the three findings Rulings 14–15 filed unruled (2026-08-29)

**What this is.** The second batch of decision-point rulings for W11's later slices. D4, F1 and
M4 are raised in
[`2026-08-29-w11-slices-2-4-planning-readiness.md`](2026-08-29-w11-slices-2-4-planning-readiness.md)
— D4 in its §9, F1 in its §3.4, M4 in its §10 — which states in its own §11 that it decides
nothing and that F1 and M4 are raised *"with **no** recommendation, because neither is a taste
call"*. The three findings are the ones
[`2026-08-29-w11-slice2-rulings.md`](2026-08-29-w11-slice2-rulings.md) reported and explicitly
did not rule. A frozen plan and a filed readiness document are never edited; this is their
dated sibling.

**Numbering continues at 16.** Rulings 1–5 are
[`2026-08-29-w11-prework-rulings.md`](2026-08-29-w11-prework-rulings.md)'s, 6–13
[`2026-08-29-w11-slice1-rulings.md`](2026-08-29-w11-slice1-rulings.md)'s, 14–15
[`2026-08-29-w11-slice2-rulings.md`](2026-08-29-w11-slice2-rulings.md)'s. Nothing here reuses a
number ([`CLAUDE.md`](../../CLAUDE.md) §5). **Ruling 4 lives in the prework record, not the
Slice 1 one** — a citation this record gets right because the sweep that gathered it checked.

**Mints no `FR-`/`NFR-`/`OQ-` id and no error code.** Three requirements gain dated amendments
or clarifications; no id is created, renumbered or retired.

**Read against `origin/main` at `c049159`** — the tree this branch is cut from, with `HEAD`
identical. Where a measurement was taken, it says on what and with what limit. Where this
record corrects something an earlier record of mine got wrong, the correction leads
(Ruling 21).

**Two things this batch does that the readiness document asked for and could not do itself:**
it answers F1's explicitly-deferred sub-question — *"whether FastAPI's `ORJSONResponse` fails at
import or at first render without `orjson`"* — by running it, and it dissolves M4's open half by
checking the premise rather than reasoning from it.

---

## Ruling 16 — D4: Slice 2 builds a per-worker in-process slot, and it is the first cache of its kind in this backend

**The decision, restated.** D4 asks whether Task 2.1 builds a per-worker holding tier for loaded
bundles, and how much of one. Options: **(a)** none — fetch the `Bundle` and `load_bundle` per
request; **(b)** a per-worker in-process slot in `backend/` keyed by `content_hash`, bounded,
populated on first use, with no refresh trigger; **(c)** a Redis tier holding serialised `Bundle`
bytes, deserialised and loaded per request.

**Ruled: (b)**, with five clauses.

### Why not (a) or (c)

- **(c) cannot hold the thing that costs anything to make.** FR-RATE-65
  ([`../specs/03-rating-engine.md`](../specs/03-rating-engine.md)`:139`) defines `CompiledBundle`
  as *"never itself serialised"*, and Ruling 4 (`2026-08-29-w11-prework-rulings.md:277-282`)
  already ruled that `CompiledBundle` is *"never round-tripped through Redis itself"*, with the
  lead's addendum (`:341-343`) upholding it against the two spec locations that said otherwise.
  So (c) caches the `Bundle` and still pays deserialise **plus** hydration on every request. It
  is the hidden cache Ruling 4 rejected, one level down, and Ruling 8 says so in terms.
- **(a) puts a booster deserialise inside a 50 ms budget.** `predict_gbm` constructs a fresh
  handle and deserialises into it on every call —
  [`../../packages/pricing-core/src/pricing_core/modelling/gbm.py`](../../packages/pricing-core/src/pricing_core/modelling/gbm.py)`:1249-1250`
  on the XGBoost branch and `:1269` on the LightGBM branch, both verified against `c049159`
  rather than taken from Ruling 8's citation. NFR-RATE-1 (`03:784`) allows 50 ms p99 for a
  ~200-step structure with one `exact` GBM call. (a) also leaves NFR-RATE-9's *"last-known-good
  cached bundle"* naming nothing at all.

### Clause 1 — where it lives, and that it is a precedent

The slot lives in `backend/`, above `pricing_core`. This is not a preference:
[`../../.importlinter`](../../.importlinter)`:16-34` forbids `pricing_core` from importing
`redis` **and** `app`, with `allow_indirect_imports = false`, so the structural half is already
enforced by `lint-imports`.

**It is the first in-process cache in this backend, and must be shaped as one rather than
appear as a module-level dict.** Swept at `c049159`: `lru_cache`, `cached_property`, `@cache`
and any import of `functools` are all **absent** from `backend/src/app/`; there is no
module-level dict cache and no singleton; the only cross-request state is FastAPI `app.state`,
set once at startup (`backend/src/app/main.py:150-153`) and read per request. The shape to
follow is the one W10-3D established for the diff cache
([`../../backend/src/app/platform/diff_cache.py`](../../backend/src/app/platform/diff_cache.py)):
a dedicated module, a `Protocol`-typed client so a fake satisfies it without a broker, identity
keys and no TTL, and a documented failure posture. What must **not** be copied from it is its
backing store — `DiffCache` is Redis (`diff_cache.py:70-75`) and constructed per request
(`backend/src/app/api/rate_tables.py:355`); this slot is in-process and per worker.

### Clause 2 — indexed by the source `Bundle`'s `content_hash`, and the glossary clause that appears to forbid it

`Bundle` is frozen and carries `content_hash: str`
([`../../packages/pricing-core/src/pricing_core/rating/compile.py`](../../packages/pricing-core/src/pricing_core/rating/compile.py)`:363`),
reproducible from the graph and pins (`:366-379`). Ruling 10's first property requires
`CompiledBundle` to expose it.

`03` §2's glossary (`:67`) says a Compiled Bundle is *"Not itself cached in Redis or
content-hash-keyed — only `Bundle` is."* Read literally, that forbids this clause. **Ruled: it
denies the distribution role, not an in-process index.** Under the literal reading Ruling 10's
first property is pointless — a hash exposed that nothing may key on answers no question — and
FR-RATE-51's *"either the old or the new bundle, never a mix"* becomes unverifiable at runtime,
which is the exact consequence Ruling 10 gives for a `CompiledBundle` that has forgotten its
provenance. The glossary row gains a dated clarification in this commit, because the same row
was already wrong once (`ddb0c6f`, #340) and a reader who finds it a second time will file the
slot as a spec violation.

### Clause 3 — bounded by count, never by bytes; default 1

Capacity is a **count**, held as a typed setting alongside the others in
`backend/src/app/config.py`, defaulting to **1**. Reasons: NFR-RATE-4 permits a bundle of up to
500 MB *including booster artifacts* (Ruling 7's reading of it), nothing in this repository
measures a hydrated `CompiledBundle`'s footprint, so a byte bound would be an estimate wearing a
number's clothes; and 1 is the only default that cannot regress a worker's memory against
option (a), which holds none. **A default above 1 cites a measurement** from Task 1.5's harness,
in the `docs/research/` note that harness already owes. Eviction is least-recently-used, which
at capacity 1 is replacement.

### Clause 4 — no refresh, no poll, no pub/sub, no environment pointer

All four are W14's, per Ruling 10, and this ruling adds nothing to them. Note for whoever rules
the refresh trigger later: `07` FR-PLAT-61 ([`../specs/07-platform.md`](../specs/07-platform.md)`:102`)
already rules against a sensor watching for something the platform knows, so W14 starts from a
deploy-time push and argues its way to poll, not the reverse.

### Clause 5 — the degraded read is in scope; the availability target is not

NFR-RATE-9 (`03:792`) reads *"degrading to the last-known-good cached bundle if metadata storage
is unavailable."* **A slot indexed only by `content_hash` cannot be reached under that
failure**, and the readiness document's claim that (b) *"satisfies NFR-RATE-9 by construction"*
does not hold: the request carries a `rating_version_ref` (Ruling 14), and ref → `Bundle` →
hash is a metadata read. With metadata storage down there is no hash to look up.

So the slot also records, for each ref it has served, the hash it resolved to. That is a memo of
a resolution this worker itself performed — **not** the `environment → current hash` pointer
Ruling 10 keeps for W14, which does not exist in W11 because environments do not select
anything yet.

**The 99.95 % monthly availability figure is not discharged by W11** and must not be booked as
though it were: it is measured against a deployed service, and nothing is deployed until W14.
What W11 owes is the mechanism, which is the half that is retrofit-expensive.

### Disposition

- Task 2.1 builds the slot. Spec change in this commit: the `03` §2 glossary clarification
  above. Nothing else; no requirement is amended.
- **Owed at the W11 close and not this role's to write:** a register row booking NFR-RATE-9 as
  *carried forward with an owner — W14* for its availability target, with the degradation
  mechanism recorded as delivered.

**Acceptance test — two violations that must become expressible.**

1. **Ruling 10's purity property, which currently lives in a ruling and in no acceptance block
   anywhere.** The structural half is already enforced (`lint-imports`, `.importlinter:33`). The
   behavioural half becomes expressible for the first time: `load_bundle` called twice with the
   same `Bundle` must return two **distinct** objects. A build in which they are identical has
   put a cache inside `pricing_core`, and the ruling is overridden.
2. **The degraded read.** With the rating-version load patched to raise, a second request for a
   ref this worker has already served must return **200** from the slot, and a first request for
   an unseen ref must be refused. Before this ruling neither could be written, because no slot
   existed to be reached. **Overridden if any build serves a ref it has never resolved while
   metadata storage is down** — that is not degradation, it is invention.

---

## Ruling 17 — F1: `NFR-RATE-13` is amended to the property it was always about; `orjson` is not added

**The decision, restated.** NFR-RATE-13 (`03:797`) requires the scoring endpoint to skip
`response_model` validation and serialise *"directly with a C-speed encoder
(`ORJSONResponse`)"*, and its 2026-08-27 amendment closes *"The design rule is unchanged:
validate inbound, never outbound; encode with `ORJSONResponse`."* `orjson` is not a dependency:
`grep -c orjson uv.lock` returns **0**, and no `.toml` in the tree names it. F1 asks whether the
requirement is satisfied by adding `orjson`, by a different encoder, or by re-reading it.

**Ruled: by amending it to state the property, and satisfying that property with the compiled
serialiser Pydantic v2 already ships. `orjson` is not added, so no `docs/skills-map.md` row and
no `03` §8 row is owed for a dependency — but the skills-map row that quotes the retired clause
is corrected in this commit.**

Four findings, all measured this session against
`/home/puzhenhao1989/gi-pricing-plan/.venv` (FastAPI **0.141.1**, Starlette 1.6.0,
pydantic-core **2.46.4**) rather than reasoned about:

1. **`ORJSONResponse` is deprecated in the pinned FastAPI**, and the deprecation names its
   replacement: *"ORJSONResponse is deprecated, FastAPI now serializes data directly to JSON
   bytes via Pydantic when a return type or response model is set, which is faster and doesn't
   need a custom response class"* (`fastapi/responses.py:69-77`, `FastAPIDeprecationWarning`).
   The requirement names a class the framework has retired.
2. **That replacement is precisely what NFR-RATE-13's first sentence forbids.** Probed with
   three routes over the same payload: a route annotated `-> Out` returning a shape that
   violates `Out` gives **500**; the identical return from an unannotated route gives **200**;
   and an annotated route returning a valid model plus an extra key emits `{"n":7}` — the extra
   key filtered out. The "modern path" validates and filters outbound. So the deprecation notice
   offers this endpoint nothing: taking its advice would reintroduce the outbound validation the
   requirement exists to remove.
3. **A missing `orjson` fails at render, not at import** — the question the readiness document
   declined to assert. `from fastapi.responses import ORJSONResponse` succeeds; constructing one
   and rendering raises `AssertionError: orjson must be installed to use ORJSONResponse`
   (`fastapi/responses.py:95`). An `orjson`-based route that ever lost its dependency would boot
   clean and 500 on the first quote. That is the expensive discovery mode, and it is the one on
   offer.
4. **The property is already available with no new dependency.**
   `Response(content=result.model_dump_json(), media_type="application/json")` returns the exact
   bytes with no outbound validation — probed: `200`, `application/json`, `{"n":7,"label":"x"}`.
   And `model_dump_json` **serialises without validating**: given a `model_construct`-built
   instance holding a `str` where an `int` is declared, it emits `{"n":"not-an-int","label":3}`
   verbatim and only warns. The serialiser is pydantic-core 2.46.4 — compiled, and already a
   hard dependency of everything here. Precedent for the shape exists:
   `backend/src/app/api/rate_tables.py:213` returns a raw `Response`, and `model_dump_json()` is
   used at four sites including `platform/diff_cache.py:105`.

**Measured, with its limit stated.** `model_dump_json()` over a `ScoringResult`-shaped model
(20 ladder rungs, 60 outputs, refs and hash) ran at **0.0168 ms/call over 20 000 calls** on the
shared verification machine — 0.034 % of NFR-RATE-1's 50 ms budget. **That figure is
serialise-only, over an already-constructed model, in a tight loop, and is not a request-path
measurement.** It is also **not** a comparison against `orjson`, which cannot be installed in
this environment. It establishes that the compiled path is not a cost problem; it does not
establish that it beats `orjson`, and this ruling does not claim it does. The argument against
`orjson` is the deprecated class and the render-time failure, not speed.

**One thing checked and found not to help, so it is not offered as a reason:** the deprecation
is **not** gate-visible today. There is no `filterwarnings = ["error"]` in any `pyproject.toml`,
so using the deprecated class would not turn a test red. Which is the argument for deciding it
now rather than at the FastAPI upgrade that removes it.

### Disposition

- Spec change in this commit: NFR-RATE-13 gains a dated amendment restating the design rule as
  *validate inbound, never outbound; serialise the trusted result directly with a compiled
  encoder*, recording that `ORJSONResponse` was named when it was the way to get one, that it is
  deprecated in the pinned FastAPI, and that the framework's stated replacement is outbound
  validation — which this requirement forbids.
- [`../skills-map.md`](../skills-map.md)'s low-latency-serving row quotes the retired clause
  verbatim and is corrected in the same commit, per `CLAUDE.md` §10.
- **No tech-dependency change**, so no `03` §8 row is owed. F1's documentation obligation
  dissolves rather than being discharged.

**Acceptance test — the violation that must become expressible.** A `ScoringResult` whose
contents violate its own declared types must be returned by the scoring endpoint **verbatim**,
not 500. That assertion is impossible under the annotated/`response_model` path — probe 2 above
returns 500 — and passes under a raw `Response`, so the test discriminates the two
implementations rather than merely observing a green endpoint. **The ruling is overridden** if
`orjson` appears in any `pyproject.toml` or in `uv.lock`, or if the scoring route declares a
`response_model=` or a Pydantic-model return annotation.

---

## Ruling 18 — M4: the grant is a Service Account, and M4's open half is not open

**The decision, restated.** M4 records that the frozen map's Task 2.1 instruction to *"grant
`Permission.SCORE_EXECUTE` to the Service Account role (currently granted to none)"* describes a
mechanism that does not exist and would turn a passing test red. It leaves one half unresolved:
whether Slice 2's RBAC test can express *"a scoped Service Account may call it"* before W14,
*"and it may prove to be DP1-shaped rather than independent of it."*

**Ruled on both halves. M4's diagnosis is correct; its open half is not open.**

**The diagnosis, verified.** `SCORE_EXECUTE` and `SCORE_BATCH` are `Permission` members
(`packages/model-schema/src/model_schema/permissions.py:58-59`) under a comment that already
says what they are — *"Scoring (`03`, `07`) — the only permissions a Service Account may hold
(FR-GOV-6)"* (`:57`). `BUILTIN_ROLES` (`:131`) grants neither, and
`backend/tests/test_rbac.py:101-107`, marked `@pytest.mark.req("FR-GOV-6")`, asserts it for
every role slug. FR-GOV-6 ([`../specs/06-governance.md`](../specs/06-governance.md)`:83`) is the
requirement. **Task 2.1 grants nothing; it checks `Permission.SCORE_EXECUTE` on the caller.**

**The open half, dissolved by checking the premise.** M4 reasons that FR-GOV-6's *"scoped to
named environments"* may make the RBAC test DP1-shaped, because the Environment entity is
FR-PLAT-28 and W14's. It does not, because a Service Account's environment scope is not that
entity and already ships end to end:

- `environments` is a caller-supplied list of strings stored on the row —
  `backend/src/app/api/service_accounts.py:173`, `environments=body.environments`;
- the API key is minted bound to one of them — `:180`,
  `generated = generate_key(body.environments[0])`;
- the key's environment is **enforced at authentication** —
  `backend/src/app/auth/service.py:212`,
  `if parsed.environment not in set(account.environments):`;
- and the authenticated `Caller` carries both scopes — `backend/src/app/api/deps.py:65-66`
  (`environments: frozenset[str]`, `permissions: frozenset[str]`), populated at `:296`.

DP1 turns on **which Rating Version is live in an environment** — a Deployment fact, absent
until W14. FR-GOV-6 turns on **whether this credential may act in this environment** — an
authorisation fact that has shipped. They share a word and nothing else.

**So Slice 2's RBAC test is writable in full today**, in three cases: a Service Account scoped
to `uat` holding `score:execute` may call the endpoint; the same account without the permission
is refused; and a key for an environment outside the account's list is refused at
authentication, before the route is reached.

**Disposition.** No spec change and no code change beyond Task 2.1's own. The correction is to
the frozen map, which is never edited — this record is its sibling.

**Acceptance test — stated as the violation, and as the predicted failure by cause.** The
violation that must become expressible is the middle case: a Service Account scoped to the right
environment but **without** `score:execute` must be refused by the endpoint. And the standing
guard already exists: **if any commit adds `SCORE_EXECUTE` or `SCORE_BATCH` to a `BUILTIN_ROLES`
entry, `test_rbac.py:101-107` fails naming the offending role slug.** That named assertion is
the expected red for anyone who follows the frozen map's wording. **A different RBAC failure, or
a 403 from an integration test, is not this** — it means something else is wrong, and is a plan
defect rather than the predicted one.

---

## Ruling 19 — Finding 1: the `rating_version` evidence floor stands; the specification is the side that moves

**The finding, restated.** `EVIDENCE_FLOOR["rating_version"]`
([`../../packages/model-schema/src/model_schema/approvals.py`](../../packages/model-schema/src/model_schema/approvals.py)`:106`)
names `structural_diff`, `regression_run` and `dislocation_run` — three kinds nothing can
verify — while the docstring 27 lines above it (`:79-100`) states that the floor is §3.3's
*"**checkable projection**, not the whole table"*. And `06` §4.2's restatement of the floor —
the blockquote opening *"These defaults sit on top of §3.3's floor"* — named it for `model`,
`validation_rule`, `custom_objective` and `peril_structure`, omitting `rating_version`,
`custom_metric` and `deployment`: three of the six keys the constant actually holds. (Cited by
its opening words rather than a line range, because the correction below moves the range.)

**Ruled: the code stands; the specification moves.**

- **Not lowering the constant.** Its only live effect for `rating_version` is `below_floor()` →
  `POLICY_BELOW_EVIDENCE_FLOOR` at policy-save (`backend/src/app/platform/approvals.py:113`,
  proven at `backend/tests/test_approvals.py:503` and `:582`). FR-GOV-37's stated harm is a
  **submission** refusing on an unverifiable kind, and Ruling 15 keeps that wiring out of W11,
  so the harm cannot occur. Lowering the entry now and restoring it at W12/W13 is the same edit
  twice, with a window in between during which a workspace can save a policy below the floor.
- **What is actually missing is FR-GOV-37's own second half.** It requires that *"the remainder
  is named with an owner rather than asserted"*, and does that for `model` and for
  `peril_structure`. For `rating_version` it names nothing at all. That is the defect, and it is
  in the requirement.

**Spec changes in this commit, both to `06`:**

1. **FR-GOV-37 gains a dated amendment** naming the `rating_version` floor and the owner of each
   kind's verifiability: `regression_run` becomes verifiable in **W12**, `dislocation_run` in
   **W13**. `structural_diff` gets a **trigger rather than an owner** — no workstream row names a
   persisted structural-diff artifact, and inventing an owner would be the "phrase rather than a
   workstream" that FR-GOV-37 itself rejects; the precedent for a triggered, deliberately
   unowned row is `docs/audit/register.md`'s F7.
2. The amendment also states the invariant that was implicit and is now load-bearing: **a floor
   entry that no submission path can yet verify is permissible only while no submission path
   consults it, and the path that will consult it carries the owner.** That is the rule under
   which `rating_version`'s entry is legitimate and `model_comparison_if_predecessor`'s exclusion
   is legitimate at the same time — without it the two look contradictory.
3. **§4.2's floor restatement gains the three artifact types it omits.** Mechanism (i) of
   FR-GOV-37 is that the floor *"is restated in §4.2's own text"*; it has been restating four
   sixths of it since `custom_metric` was added on 2026-08-22.

**Scope note.** FR-GOV-9..19 and evidence enforcement are **W17's** by FR-GOV-37's own words.
What lands here is the naming FR-GOV-37 requires of itself, not a change to what is enforced;
anything beyond that is W17's.

**Acceptance test — the violation that must become expressible.** Until this amendment, "a key
exists in `EVIDENCE_FLOOR` that FR-GOV-37 does not name" was not a statement a reader could
evaluate, because three of six keys were unnamed and the comparison had no second list. After
it, the two lists exist and the comparison is one read of each. **The ruling is overridden** if
`EVIDENCE_FLOOR` gains a key that FR-GOV-37 does not name, or if a submission path begins
consulting `effective_evidence("rating_version")` while any of its kinds is still unverifiable —
Ruling 15 already makes the second observable as two named tests going red.

---

## Ruling 20 — Finding 2: `deployment` has a floor and no policy entry; the spec is right and the code is short one entry

`EVIDENCE_FLOOR` holds `"deployment": ("rating_version_approval", "uat_deployment")`
(`approvals.py:107`) and `DEFAULT_POLICY` has **no** `deployment` entry (`:202-261`), while `06`
§4.2's document does (`:271-273`). A deployment submission therefore never reaches an evidence
check: `approvals.submit` refuses at `backend/src/app/platform/approvals.py:181-188` with
*"No approval policy for this artifact type"*.

**Ruled: no spec change. `06` §4.2 is right; the code is short one entry, and it is W14's** —
the workstream that owns FR-RATE-50 and is the first to submit a deployment for approval. This is
the third instance of a defect class `06` §4.2 already documents twice, for `peril_structure`
(2026-08-18) and `custom_metric` (2026-08-20); the dated note recording it belongs in §4.2 with
the entry that fixes it, which is how both predecessors were handled, so it is not written now.

**Stated as the predicted failure by cause, not by status.** The refusal is a **422** whose title
is *"No approval policy for this artifact type"* — it fires **before** any evidence is consulted,
so both the status and the message point away from the actual gap. An executor who reads only the
status will look at the evidence machinery, which is working.

**Acceptance test — the violation that must become expressible.** A `deployment` submission
reaching the evidence check at all. Today it cannot, so no test can distinguish "evidence
incomplete" from "no policy"; once the entry exists, the two are separable refusals and each is
assertable.

---

## Ruling 21 — Finding 3: the framing was wrong, and the class is bigger and mostly benign

**The correction leads, per `docs/process/delivery-process.md` §15: my own filing of this finding
in `2026-08-29-w11-slice2-rulings.md` was wrong in its framing.** It reported
`GOLDEN_QUOTE_MISMATCH` being owned by `03` §5.1 and registered nowhere as a defect. It is not
one. `PlatformError.__init__` (`backend/src/app/errors.py:335-348`) refuses an unknown code with
the message *"Codes are enumerated in the owning spec's Interfaces section; **add it there before
raising it**"* — the registry is deliberately populated at the point of first **raise**,
spec-first. A declared-but-unregistered code is the designed state until something raises it.
`GOLDEN_QUOTE_MISMATCH` is W12's to register when W12 raises it, and nothing is wrong today.

**Measured rather than exemplified.** Across the seven module specs' owned-code blocks, **32 of
161 declared codes are unregistered**: `01` 0/17, `02` 5/58, `03` 11/36, `04` 9/9, `05` 7/7,
`06` 0/15, `07` 0/19. `04` and `05` are 9/9 and 7/7 because neither module is built — which is
the mechanism working, not a backlog. The enumerating command, so this number is re-derivable
rather than quoted: extract `` `UPPER_SNAKE` `` tokens from each spec's
`**Error codes owned by this module:**` block and diff against the string literals in
`backend/src/app/errors.py`. The subset that would matter is codes whose owning workstream has
**closed**, and the sweep finds exactly one — see the finding below.

**Ruled: no spec change, no register row, and no defect.** The two codes this record's own work
adds to the unregistered count — `MODEL_CALL_FAILED` (Ruling 11) and `NO_LIVE_RATING_VERSION`
(Ruling 14) — are pending their raise in Slice 1 and Task 2.1 respectively, which is the
mechanism behaving as designed.

**Acceptance test.** The ruling is "no change", so the test is the standing one it establishes:
**an audit that books an unregistered spec-declared code as a defect without first checking
whether the workstream that owes its raise has shipped has mis-applied this ruling.** What the
measurement makes newly expressible is the sharper statement — *"a module spec declares an error
code that its own **closed** workstream never raises"* — which is now countable rather than
anecdotal, and which returns exactly one hit today.

---

## Findings reported, not ruled

**1. `FR-RATE-25`'s control-factor clause appears to be enforced nowhere, and W9 closed.**
FR-RATE-25 (`03:136`) requires bundle compilation to validate, among other things, *"no
`control`-intent factor in a rateable path (`02` FR-MODEL-3)"*, and `03` §5.1 owns
`CONTROL_FACTOR_IN_RATEABLE_PATH` for it. At `c049159` that code appears in no Python file, and
`git grep -in "intent" -- packages/pricing-core/src/pricing_core/rating/` returns **zero** — a
true negative, positive-controlled by `git grep -c "def " -- .../rating/compile.py` returning
`15` over the same pathspec. The only `FactorIntent.CONTROL` hits in the repository are `02`
modelling tests. FR-RATE-25 is W9's (`../roadmap.md:374`) and **W9 closed 2026-08-27**. Whether
this reopens the W9 close, becomes a register row with an owner, or is absorbed by W11's compile
path is a scope question, and `CLAUDE.md` §12 puts scope outside this role.

**2. Checked and clear, recorded so nobody re-raises it.** `07` FR-PLAT-22 (`07:116`) cites
FR-RATE-65 beside FR-RATE-51 for *"the rating `Bundle` cache"*, which reads like a stranded
list-mate of the Redis-caching glossary error that `ddb0c6f` (#340) fixed. It is not:
`git log -S` shows that commit **added** the cross-reference in the same edit as the fix, and
the cached thing FR-PLAT-22 names is the `Bundle`. No finding.

---

## Sources — read at `c049159`, and measured where a measurement is claimed

- `docs/specs/03-rating-engine.md` — §2 glossary `:67`, FR-RATE-24/25 `:135-136`, FR-RATE-65
  `:139`, §8 `:756-777`, §9 `:780-800`, §5.2 `:601-616`.
- `docs/specs/06-governance.md` — FR-GOV-6 `:83`, §3.3 `:105-149`, §4.2 `:251-348`.
- `docs/specs/07-platform.md` — FR-PLAT-22 `:116`, FR-PLAT-61 `:102`.
- `docs/plans/2026-08-29-w11-prework-rulings.md` Ruling 4 and its addendum;
  `2026-08-29-w11-slice1-rulings.md` Rulings 8 and 10;
  `2026-08-29-w11-slice2-rulings.md` Rulings 14 and 15;
  `2026-08-29-w11-slices-2-4-planning-readiness.md` §3.3, §3.4, §4, §9, §10, §11.
- `.importlinter` in full; `docs/adr/0001-pricing-core-is-dependency-free.md`.
- Code: `packages/model-schema/src/model_schema/approvals.py`, `.../permissions.py`,
  `packages/pricing-core/src/pricing_core/rating/compile.py`,
  `.../modelling/gbm.py`, `backend/src/app/errors.py`, `.../platform/approvals.py`,
  `.../platform/diff_cache.py`, `.../api/service_accounts.py`, `.../api/deps.py`,
  `.../auth/service.py`, `.../main.py`, `.../config.py`, `backend/tests/test_rbac.py`,
  `backend/tests/test_approvals.py`.
- Measured this session against `/home/puzhenhao1989/gi-pricing-plan/.venv` (FastAPI 0.141.1,
  pydantic-core 2.46.4): the `ORJSONResponse` deprecation and its render-time assertion; the
  annotated-route outbound-validation probe; the raw-`Response` and `model_dump_json` probes;
  and the 0.0168 ms/call serialisation figure, whose limits are stated in Ruling 17.
