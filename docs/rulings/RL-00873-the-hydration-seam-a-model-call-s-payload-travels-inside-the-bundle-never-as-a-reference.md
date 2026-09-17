---
id: RL-873
family: ruling
title: the hydration seam: a `model_call`'s payload travels **inside** the `Bundle`, never as a reference
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

## RL-873 — the hydration seam: a `model_call`'s payload travels **inside** the `Bundle`, never as a reference

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
  (`../specs/07-platform.md` FR-418/419) that something dereferences at hydration time.
  `Bundle` gets small; `load_bundle` gets I/O.
- **(c) Split by artifact kind** — coefficients inline, boosters by reference.

**Ruled: (a), inline, for every artifact kind including boosters.**

Rationale:

- **`NFR-492` (`../specs/03-rating-engine.md:780`) settles it in the requirement's own
  words:** *"bundle size stays under 500 MB **including booster artifacts**."* A size budget
  is only stated over what is inside the thing being sized. Under (b) or (c) a `Bundle`
  carrying a reference is a few kilobytes and the clause has nothing to bound. Two
  independent corroborations: `03` §8's Redis row calls the cached thing the
  `` `Bundle` `` cache *"keyed by content hash"* (`:757`), and `../skills-map.md:94`'s
  Redis row names the sizing problem as *"memory sizing for 500 MB bundles"* — a 500 MB
  value in Redis is a bundle with its boosters in it, not a pointer to one.
- **It is what `FR-239` (`:135`) and `compile.py`'s own DP1 comment already say**, and
  the only reading that needs no requirement amended. `FR-239`: the Bundle *"is
  sufficient to score with no database access."* `compile.py:280-283`: *"The Bundle is
  self-contained: sufficient to score with no database access."* Under (b) the Bundle stops
  being self-contained and both would need amending. `CLAUDE.md` §0 says a code/spec
  disagreement is resolved rather than made to match quietly — here the reading that
  requires no amendment is also the one three separate artifacts already state.
- **This ruling deliberately does *not* lean on `NFR-491` (`:779`),** and says so because
  the temptation is obvious. `NFR-491` reads *"A compiled bundle scores with **zero**
  database or network access; everything it needs is inside it,"* and its subject is now
  ambiguous: since `FR-243` (`:139`) "Compiled Bundle" is the glossary's name for the
  loaded runtime type (`:67`), so `NFR-491` may be constraining `CompiledBundle`, under
  which a blob fetch during hydration — before any scoring — would satisfy it. RL-867's
  own addendum flagged exactly this imprecision and deliberately left it
  (`2026-08-29-w11-prework-rulings.md:399-404`). It is still open, it is **not** reopened
  here, and it is not load-bearing for this ruling: `NFR-492` names `Bundle` explicitly
  and needs no disambiguation.
- **(b) also collides with `ADR-703` in a way (a) does not.** `pricing-core` may not import
  `redis`, `httpx`, `requests`, `boto3` or `botocore` — `.importlinter:16-34`, contract
  `core-has-no-infrastructure`, `allow_indirect_imports = false`. A dereferencing
  `load_bundle` therefore needs an injected reader Protocol, mirroring
  `ArtifactResolver` (`compile.py:298`). That is buildable, so it is not an argument that
  (b) is impossible — it is an argument that (b) costs a new injected dependency, a new
  async signature, and two amended requirements to buy a smaller Redis value that
  `NFR-492` and `skills-map.md:94` both already budget for at full size.

**Disposition — two parts, one of them a spec change applied in this commit.**

1. **`load_bundle` takes no resolver and performs no I/O**, and its signature is added to
   `../specs/03-rating-engine.md` §5.2, which today lists every other `pricing-core` rating
   module and has no `rating/runtime.py` block at all — `git grep -n load_bundle` over
   `docs/specs/` and `docs/workflows/` returns zero hits at `7b8473a`, while `FR-243`
   requires *"a hydration step"* and names no function for it. Appended as
   `def load_bundle(bundle: Bundle) -> CompiledBundle`, plain `def` per
   `.claude/skills/spec-change`'s rule: it awaits no injected async dependency and no native
   async binding. This completes RL-867's disposition, which named `load_bundle` in prose
   and never landed it in an interfaces section.
2. **The payload must survive a JSON round trip**, because `Bundle` is persisted and cached
   as JSON and `resolved_payloads` is typed `dict[str, Any]` (`compile.py:361`). Raw
   `bytes` do not. This is not a new constraint on the executor so much as a fact about the
   existing type, and the existing GBM path already produces a JSON-shaped artifact —
   `../../packages/pricing-core/src/pricing_core/modelling/gbm.py:975` persists a booster as
   `bytes(booster.save_raw(raw_format="json"))`. **`NFR-492`'s 500 MB is measured on the
   serialised form**, so Task 1.3's `NFR-492` exit criterion measures the persisted
   `Bundle`, not an in-memory estimate.

**Flagged, not ruled — a headroom risk this ruling creates and does not close.** A `Bundle`
approaching `NFR-492`'s 500 MB is at the edge of what a Redis string value can hold
(Redis's own limit is 512 MB), and text-encoding a booster spends headroom to get there.
`skills-map.md:94` already lists *"memory sizing for 500 MB bundles"* and *"eviction policy
that must never evict the live bundle"* as open research against `FR-268` / `NFR-494`
— this ruling adds the encoding-overhead term to that existing question rather than opening
a new one. It becomes real only when a bundle with a large booster is measured, which is
Task 1.3's own `NFR-492` criterion; if that measurement lands near the cap, it is a
finding against `NFR-492`, not against this ruling.

---
