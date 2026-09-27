---
id: RL-882
family: ruling
title: D4: Slice 2 builds a per-worker in-process slot, and it is the first cache of its kind in this backend
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-08-29
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-08-29-w11-slices-2-4-rulings.md
---

# WK-671 Slices 2–4 — D4, F1, M4 ruled, and the three findings Rulings 14–15 filed unruled (2026-08-29)

**What this is.** The second batch of decision-point rulings for WK-671's later slices. D4, F1 and
M4 are raised in
[`../plans/PL-00855-wk-671-slices-2-4-planning-readiness-the-signals-that-release-each-and-what-a-leaf-plan-can-already-take-from-here-2026-08-29.md`](../plans/PL-00855-wk-671-slices-2-4-planning-readiness-the-signals-that-release-each-and-what-a-leaf-plan-can-already-take-from-here-2026-08-29.md)
— D4 in its §9, F1 in its §3.4, M4 in its §10 — which states in its own §11 that it decides
nothing and that F1 and M4 are raised *"with **no** recommendation, because neither is a taste
call"*. The three findings are the ones
[`RL-00881-dp2-fr-257-splits-into-four-limbs-wk-671-delivers-one-defers-two-with-owners-and-does-not-wire-a-gate-that-could-only-refuse-everything.md`](RL-00881-dp2-fr-257-splits-into-four-limbs-wk-671-delivers-one-defers-two-with-owners-and-does-not-wire-a-gate-that-could-only-refuse-everything.md) reported and explicitly
did not rule. A frozen plan and a filed readiness document are never edited; this is their
dated sibling.

**Numbering continues at 16.** Rulings 1–5 are
[`RL-00868-score-one-s-real-time-path-async-evaluate-not-evaluate-executor-offload-and-whether-5-2-s-sync-convention-is-itself-the-defect.md`](RL-00868-score-one-s-real-time-path-async-evaluate-not-evaluate-executor-offload-and-whether-5-2-s-sync-convention-is-itself-the-defect.md)'s, 6–13
[`RL-00879-03-5-2-s-money-block-the-code-is-right-and-the-spec-is-stale-in-more-places-than-f-w11-1-5-reports.md`](RL-00879-03-5-2-s-money-block-the-code-is-right-and-the-spec-is-stale-in-more-places-than-f-w11-1-5-reports.md)'s, 14–15
[`RL-00881-dp2-fr-257-splits-into-four-limbs-wk-671-delivers-one-defers-two-with-owners-and-does-not-wire-a-gate-that-could-only-refuse-everything.md`](RL-00881-dp2-fr-257-splits-into-four-limbs-wk-671-delivers-one-defers-two-with-owners-and-does-not-wire-a-gate-that-could-only-refuse-everything.md)'s. Nothing here reuses a
number ([`CLAUDE.md`](../../CLAUDE.md) §5). **RL-867 lives in the prework record, not the
Slice 1 one** — a citation this record gets right because the sweep that gathered it checked.

**Mints no `FR-`/`NFR-`/`OQ-` id and no error code.** Three requirements gain dated amendments
or clarifications; no id is created, renumbered or retired.

**Read against `origin/main` at `c049159`** — the tree this branch is cut from, with `HEAD`
identical. Where a measurement was taken, it says on what and with what limit. Where this
record corrects something an earlier record of mine got wrong, the correction leads
(RL-887).

**Two things this batch does that the readiness document asked for and could not do itself:**
it answers F1's explicitly-deferred sub-question — *"whether FastAPI's `ORJSONResponse` fails at
import or at first render without `orjson`"* — by running it, and it dissolves M4's open half by
checking the premise rather than reasoning from it.

---

## RL-882 — D4: Slice 2 builds a per-worker in-process slot, and it is the first cache of its kind in this backend

**The decision, restated.** D4 asks whether Task 2.1 builds a per-worker holding tier for loaded
bundles, and how much of one. Options: **(a)** none — fetch the `Bundle` and `load_bundle` per
request; **(b)** a per-worker in-process slot in `backend/` keyed by `content_hash`, bounded,
populated on first use, with no refresh trigger; **(c)** a Redis tier holding serialised `Bundle`
bytes, deserialised and loaded per request.

**Ruled: (b)**, with five clauses.

### Why not (a) or (c)

- **(c) cannot hold the thing that costs anything to make.** FR-243
  ([`../specs/03-rating-engine.md`](../specs/03-rating-engine.md)`:139`) defines `CompiledBundle`
  as *"never itself serialised"*, and RL-867 (`2026-08-29-w11-prework-rulings.md:277-282`)
  already ruled that `CompiledBundle` is *"never round-tripped through Redis itself"*, with the
  lead's addendum (`:341-343`) upholding it against the two spec locations that said otherwise.
  So (c) caches the `Bundle` and still pays deserialise **plus** hydration on every request. It
  is the hidden cache RL-867 rejected, one level down, and RL-874 says so in terms.
- **(a) puts a booster deserialise inside a 50 ms budget.** `predict_gbm` constructs a fresh
  handle and deserialises into it on every call —
  [`../../packages/pricing-core/src/pricing_core/modelling/gbm.py`](../../packages/pricing-core/src/pricing_core/modelling/gbm.py)`:1249-1250`
  on the XGBoost branch and `:1269` on the LightGBM branch, both verified against `c049159`
  rather than taken from RL-874's citation. NFR-489 (`03:784`) allows 50 ms p99 for a
  ~200-step structure with one `exact` GBM call. (a) also leaves NFR-497's *"last-known-good
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
reproducible from the graph and pins (`:366-379`). RL-876's first property requires
`CompiledBundle` to expose it.

`03` §2's glossary (`:67`) says a Compiled Bundle is *"Not itself cached in Redis or
content-hash-keyed — only `Bundle` is."* Read literally, that forbids this clause. **Ruled: it
denies the distribution role, not an in-process index.** Under the literal reading RL-876's
first property is pointless — a hash exposed that nothing may key on answers no question — and
FR-268's *"either the old or the new bundle, never a mix"* becomes unverifiable at runtime,
which is the exact consequence RL-876 gives for a `CompiledBundle` that has forgotten its
provenance. The glossary row gains a dated clarification in this commit, because the same row
was already wrong once (`ddb0c6f`, #340) and a reader who finds it a second time will file the
slot as a spec violation.

### Clause 3 — bounded by count, never by bytes; default 1

Capacity is a **count**, held as a typed setting alongside the others in
`backend/src/app/config.py`, defaulting to **1**. Reasons: NFR-492 permits a bundle of up to
500 MB *including booster artifacts* (RL-873's reading of it), nothing in this repository
measures a hydrated `CompiledBundle`'s footprint, so a byte bound would be an estimate wearing a
number's clothes; and 1 is the only default that cannot regress a worker's memory against
option (a), which holds none. **A default above 1 cites a measurement** from Task 1.5's harness,
in the `docs/research/` note that harness already owes. Eviction is least-recently-used, which
at capacity 1 is replacement.

### Clause 4 — no refresh, no poll, no pub/sub, no environment pointer

All four are WK-674's, per RL-876, and this ruling adds nothing to them. Note for whoever rules
the refresh trigger later: `07` FR-413 ([`../specs/07-platform.md`](../specs/07-platform.md)`:102`)
already rules against a sensor watching for something the platform knows, so WK-674 starts from a
deploy-time push and argues its way to poll, not the reverse.

### Clause 5 — the degraded read is in scope; the availability target is not

NFR-497 (`03:792`) reads *"degrading to the last-known-good cached bundle if metadata storage
is unavailable."* **A slot indexed only by `content_hash` cannot be reached under that
failure**, and the readiness document's claim that (b) *"satisfies NFR-497 by construction"*
does not hold: the request carries a `rating_version_ref` (RL-880), and ref → `Bundle` →
hash is a metadata read. With metadata storage down there is no hash to look up.

So the slot also records, for each ref it has served, the hash it resolved to. That is a memo of
a resolution this worker itself performed — **not** the `environment → current hash` pointer
RL-876 keeps for WK-674, which does not exist in WK-671 because environments do not select
anything yet.

**The 99.95 % monthly availability figure is not discharged by WK-671** and must not be booked as
though it were: it is measured against a deployed service, and nothing is deployed until WK-674.
What WK-671 owes is the mechanism, which is the half that is retrofit-expensive.

### Disposition

- Task 2.1 builds the slot. Spec change in this commit: the `03` §2 glossary clarification
  above. Nothing else; no requirement is amended.
- **Owed at the WK-671 close and not this role's to write:** a register row booking NFR-497 as
  *carried forward with an owner — WK-674* for its availability target, with the degradation
  mechanism recorded as delivered.

**Acceptance test — two violations that must become expressible.**

1. **RL-876's purity property, which currently lives in a ruling and in no acceptance block
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
