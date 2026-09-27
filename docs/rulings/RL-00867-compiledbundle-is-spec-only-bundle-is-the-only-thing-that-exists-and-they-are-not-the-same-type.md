---
id: RL-867
family: ruling
title: `CompiledBundle` is spec-only; `Bundle` is the only thing that exists, and they are not the same type
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-08-29
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-08-29-w11-prework-rulings.md
---

## RL-867 — `CompiledBundle` is spec-only; `Bundle` is the only thing that exists, and they are not the same type

**The finding, restated precisely.** Every `03` §5.2 scoring-adjacent signature —
`score_one`, `score_batch`, `dislocate` (twice: `baseline`, `candidate`), `run_regression`
(`03-rating-engine.md:598,600,605,610`) — takes a `CompiledBundle`. `git grep -n
CompiledBundle` across `packages/`, `backend/` and the spec returns **only** those four
spec lines; zero code definitions, zero imports, zero references anywhere. The only real
class is `Bundle` (`packages/pricing-core/src/pricing_core/rating/compile.py:350`), defined
by the already-ruled `DP1` (`compile.py:280-283`, 2026-08-27): "the JDM graph plus the
pinned artifacts' resolved payloads, wrapped by the pricing-core facade... self-contained:
sufficient to score with no database access." This ruling does not reopen DP1 — `Bundle`
stays exactly what DP1 said. The question DP1 never had to answer is whether the thing
`score_one` actually executes against is the same object.

**Options:**

- **(a) Rename-only: `CompiledBundle` *is* `Bundle`.** The spec's four signatures are
  corrected to say `Bundle`, and scoring takes the plain, JSON-shaped, persisted object
  directly.
- **(b) `CompiledBundle` is a distinct, new runtime type — a loaded wrapper around a
  `Bundle`** — holding whatever the ZEN engine binding needs to actually execute the graph
  (an initialised decision/engine handle built from `graph`) plus any GBM boosters loaded
  from `resolved_payloads` into live `Booster` objects, produced by a new hydration function
  (e.g. `load_bundle(bundle: Bundle) -> CompiledBundle`) that is never itself serialised.
  `Bundle` stays exactly DP1's self-contained, cacheable, distributable data form;
  `CompiledBundle` is what a warm worker process holds and what `score_one`/`score_batch`/
  `dislocate`/`run_regression` actually take.
- **(c) One mutable type**: keep only `Bundle`, but let it lazily populate and memoise an
  engine handle / loaded boosters on first use as instance state.

**Ruled: (b).** Grow the code to match the spec's existing name; do not rename the spec to
match today's code.

Rationale:

- **(a) reintroduces, per request, exactly the cost this session's own WK-671 orientation
  report already flagged as the central real-time-evaluator risk.** If `score_one` receives
  the plain `Bundle` — a Pydantic model whose `graph` field is a JSON-shaped `dict[str,
  dict[str, Any]]` — something has to turn that into whatever the `zen-engine` Python
  binding needs to actually walk the DAG, and something has to turn any resolved booster
  bytes into a live, `nthread=1`-pinned `Booster` object, on **every call**, unless a second,
  hidden cache is invented inside `score_one` itself. That hidden cache would just be option
  (b) again, minus the type system saying so — worse for testability (nothing distinguishes
  "freshly deserialised" from "already loaded" at the type level) and worse for the exact
  latency budget `NFR-489` sets (repeating graph-parse and booster-load work per request
  that a warm process should only do once per deployment switch).
- **(b) is what `FR-268` and `NFR-494` already describe, just without a name for the
  loaded half.** `FR-268`: "Bundles are **pre-warmed into cache** before the switch."
  `NFR-494`: switchover "completes within 30 s of the deploy command **including cache
  warming**." Pre-warming is a *load* step — it only makes sense as a description of turning
  a distributable `Bundle` into something already resident and ready to execute in a
  process's memory. `Bundle` (DP1) is the thing that gets distributed and cached in Redis;
  `CompiledBundle` is the thing pre-warming produces, held per-worker, never round-tripped
  through Redis itself. This is the same two-tier shape this session's own WK-671 orientation
  report recommended for the caching decision point, arrived at independently from the
  executor's and planner's side and now given the concrete names the spec already committed
  to.
- **(c) blurs a distinction this codebase is otherwise careful to keep sharp.** `Bundle` is
  a `BaseModel` — data, meant to be hashed (`content_hash`), serialised
  (`bundle.model_dump_json()`, used for exactly that in
  `rating_versions.py:285`), and compared for equality. Attaching mutable, unserialisable
  runtime state (an engine handle, loaded boosters) to instances of that same class means a
  `Bundle` can no longer be freely copied, diffed, or round-tripped through JSON without
  first checking whether the loaded fields happen to be populated — exactly the kind of
  boundary confusion `03` §3.11 already spent a spike (S1) correcting once for money at the
  ZEN engine's Python binding. Keeping "the record" and "the loaded resource" as two named
  types is the same discipline applied one layer up.
- **Growing the spec's name rather than renaming the spec matches every ruling in this file
  so far.** Rulings 1, 2 and 3 all found the spec's declared shape correct and the code
  incomplete or mis-specified relative to it (a missing route, a wrong status code, an
  under-specified signature) — not the reverse. `CompiledBundle` already exists in the one
  place that gets to mint the name first; the code has not caught up yet, which is a
  different situation from the code being wrong.

**Disposition.** No spec change — `03` §5.2 already says `CompiledBundle` correctly.
**Code, WK-671 slice 1**: add a `CompiledBundle` type to `pricing_core.rating` (or a sibling
module, e.g. `pricing_core.rating.runtime`) and a hydration function from `Bundle` to it;
retarget `score_one`/`score_batch` (and, when built, `dislocate`/`run_regression`) to take
`CompiledBundle`; the in-process cache RL-865 and this session's own orientation report
both anticipate holds `CompiledBundle` instances, loaded once per deployment-switch, not
`Bundle` bytes re-parsed per request. Exact field shape and the engine-handle type are the
executor's to design against this ruling, not fixed here.

**Related, not re-ruled (already flagged in this record's own RL-865, now independently
confirmed by the executor and planner too).** `CompiledBundle`'s hydration step is only as
good as what `Bundle.resolved_payloads` actually contains, and today's resolver
(`rating_versions.py:240-271`) puts a placeholder (`payload={"status": model.status}`) in
the `model` branch and raises `NOT_FOUND` unconditionally for `rate_table` refs on a stale
Phase-2 comment. No realistic Rating Version compiles today regardless of sync/async or
`CompiledBundle`. Same WK-671 slice-1 prerequisite named in RL-865; not a separate ruling.

**Addendum, filed later the same day: RL-867's own disposition undersold itself, and its
evidence search had a hole in it.** Found while checking, ahead of this team's stand-down,
where a fresh session would actually find each ruling — the trigger and the standard are
`CLAUDE.md` §13's "a reference that resolves only for the writer"
(`.claude/rfcs/RFC-00777-a-reference-that-resolves-only-in-the-writer-s-context.md`).

*The disposition gap.* "No spec change" (above) was correct about the bare name — `03` §5.2
already said `CompiledBundle` before this ruling — but the bare name pre-existing is not the
same as the *contract* pre-existing, and the contract (a distinct type, a hydration step,
never itself serialised) existed only in this record. Corrected: **`FR-243`**, filed in
`03-rating-engine.md` §3.4 alongside `Bundle`'s own `FR-239`/`FR-240`, not as a new
§4 data contract — `Bundle` has no §4 entry either, so a `CompiledBundle` one would be a new
pattern, not a fix.

*The evidence-search gap.* This ruling's own search was `git grep -n CompiledBundle` — one
word. `03-rating-engine.md:67`'s glossary spells the concept "Compiled Bundle" — two words —
and could not have matched. That entry, and `:756`'s §8 tech-dependency row, both said the
*loaded, execution* form is what Redis caches, keyed by content hash — the opposite of what
this ruling concluded (Redis caches plain `Bundle`; the loaded form is per-worker only,
never Redis-round-tripped, because a native engine handle does not usefully survive a
round-trip into a different process). Both predate this ruling by two weeks
(`f8704bb9`, 2026-08-14, the original spec-authoring commit) — read as "compiled" used as a
plain adjective on "bundle," from before the two-tier split existed to need two names.

**Ruled (lead, on the decision-maker's proposed reading): the glossary and §8 are wrong,
RL-867 stands.** The engineering settles it independent of the dating evidence: serialising
a loaded engine handle and boosters into Redis and reconstructing them in another process is
precisely what `Bundle` already is for, so a spec describing Redis holding the loaded form
describes a round trip with no purpose.

**Condition on the fix, attached to the ruling and not optional: search the concept, not the
identifier, before touching any one location.** A single fresh grep for the one-word
identifier is exactly the search that missed this the first time. Swept `"compiled bundle"`
(case-insensitive), `"execution form"`, `"cached in redis"`, and `"bundle cache"` across
`docs/`. Found and fixed, both carrying the same claim as `:67`/`:756`:

- `03-rating-engine.md:67` (glossary) — retargeted to the per-worker, not-Redis-cached
  reading, citing `FR-243`.
- `03-rating-engine.md:756` (§8) — "Compiled bundle cache" → `` `Bundle` cache ``.
- `07-platform.md:116` (`FR-422`) — a location outside `03-rating-engine.md` entirely,
  which no version of the pre-swept location list named: "the compiled rating bundle cache"
  → "the rating `` `Bundle` `` cache", citing `FR-243` alongside the existing
  `FR-268`. Crosses into a second spec module because `07`'s own text had independently
  picked up the same imprecision by citing `03`'s Redis row, not because this ruling reopens
  anything about the platform module itself.

Checked and left alone, because the claim they carry does not assert a caching location and
so is not the contradiction being corrected: `FR-268`, `NFR-494` (`03`, both already
say plain "bundle"), `03-rating-engine.md:722` and `07-platform.md:432` (both "bundle cache",
not "compiled bundle"), `docs/skills-map.md:94`'s Redis row (names "500 MB bundles" —
plain "bundle" throughout, already consistent with this ruling despite being the row the
sweep was specifically asked to check). Also noticed and deliberately **not** fixed here,
flagged rather than silently expanded into: `FR-239`/`NFR-491` say a `Bundle` "is
sufficient to score with no database access," which conflates "contains everything scoring
needs" (true) with "is itself what executes" (imprecise — `score_one` takes `CompiledBundle`,
`FR-243`) — a real but softer, different imprecision than the Redis-caching claim this
addendum corrects, and out of the scope the sweep was asked to close. Also left alone as
either generated (`docs/contracts/**`, never hand-edited) or historical/frozen
(`docs/closures/INDEX.md#plan-reviewsmd`, `docs/plans/PL-00818-wk-669-implementation-plan-rating-algorithm-contract-validation-bundle-compilation.md`, this record's
own earlier text) — every remaining "compiled bundle" hit in `04-optimisation.md`,
`07-platform.md:165/432` and `WF-701-deploy-and-monitor.md` uses the phrase as loose prose for
plain `Bundle`, consistent with `FR-239`'s framing, not a Redis-location claim.

`python3 scripts/audit-docs.py` re-run clean on this delta (below).

**Addendum, filed later the same day: the citation itself resolved nowhere.** RL-867's
rationale and disposition (above, at three points — the `(a)` bullet, the `(b)` bullet, and
the disposition's own last sentence) cite "this session's own WK-671 orientation report" as
though it were an existing, committed document. It was not: the report was sent as a
teammate message during WK-671 setup and never promoted into a filed file — a citation that
resolved only for the writer, `RFC-777`'s own defect, inside the record that exists to
avoid exactly that. Found by the lead sweeping the handover for content with no committed
home, the same sweep that produced `RFC-842` and `RFC-843`.

**Now resolves to `docs/plans/PL-00851-wk-671-five-decision-points-recovered.md` (#362,
merged).** That document recovers all five of the session's original decision-point
scopings verbatim, quotes this ruling's own citing sentence back for cross-reference, and
states plainly why it quotes rather than links: "session transcripts are local to the
machine and session that produced them, not a durable citation." The original wording above
is left exactly as written, per this record's own header precedent for a citation later
found to need redirecting rather than rewriting — a reader hitting "this session's own WK-671
orientation report" now has this paragraph to resolve it, which is the fix; the phrase
itself is not worth three separate edits to reword.
