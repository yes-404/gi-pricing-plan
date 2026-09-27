---
id: RL-921
family: ruling
title: a `ref` may not be served from the memo without a metadata read, and it does not need to be: the content hash is already in hand after the first read, and is discarded
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-08-30
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-08-30-w11-reopen-hooks-and-bundle-resolution-rulings.md
---

## RL-921 — a `ref` may not be served from the memo without a metadata read, and it does not need to be: the content hash is already in hand after the first read, and is discarded

**Ruled.** **No staleness window is admitted, because none is needed.** The question as posed
rests on a premise the code refutes, and with that premise removed the correctness/latency
trade the question assumes does not exist. **NFR-489 is not amended, and it is not the
defective artifact on the evidence now in hand** — but neither is it shown reachable, and §4
below says exactly what is still open rather than smoothing it.

### 1. Every relayed measurement re-read at source, and each held

Read in `docs/research/w11-task-2d-nfr-rate-1-full-path.md` at `daa6fbe`, not accepted from
the dispatch:

| Relayed | Verdict |
|---|---|
| `_fetch_bundle` alone p99 66.294 ms | **Confirmed**, `:81`, with-GBM, 200 sequential calls, warm slot |
| against a 50 ms whole-request budget | **Confirmed** — `03` §9 `:797`, and NFR-489 carries **no amendment and no scoping clause**: no "excluding I/O", no warm-cache carve-out |
| over budget at every rung from 10 rps | **Confirmed**, `:128` — *"Every rung is over budget in both conditions"* |
| queue wait p99 7.179 / 4.191 ms at 10 rps | **Confirmed**, `:112` and `:122`; the attribution resolves to fetch, not saturation |
| payload 2,039,114 B | **Confirmed**, `:46` and `:81` |
| the memo is wired to the NFR-497 branch only | **Confirmed in code** — `slot.hash_for` has exactly one call site in the backend, `backend/src/app/api/score.py:175`, inside `except Exception:` (`:174`). On the happy path the memo is **written** (`:184`) and never read |
| a re-pointed ref would serve a stale bundle | **Confirmed, and it is worse than stated** — see §3 |

Two limits from the measurement's own record, carried forward rather than dropped: **one
pass**, and a **shared 4-core box** with 1-minute load rising to 10.76 during the run. The 200
rps rungs are void by the record's own statement (the generator issued 149.5 and 142.1).

### 2. The premise that does not survive, and what it dissolves

The research note argues the memo cannot move to the happy path because *"the slot is keyed on
`content_hash`, and **the only way to learn a ref's content hash is to fetch the bundle**"*
(`:74-75`). **That universal is false at `daa6fbe`.**

`compile_rating_version` writes the content hash into the version's own row —
`backend/src/app/platform/rating_versions.py:440-444`, `row.bundle = {"content_hash":
bundle.content_hash, "bytes": …, "compiled_at": …}` — and `record_bundle_blob` merges the blob
key into the same dict (`:163`). `_fetch_bundle` reads that dict at
`backend/src/app/api/score.py:126` (`metadata = row.bundle or {}`), takes **only**
`blob_sha256` from it, and **discards `content_hash`**.

So after `_fetch_bundle`'s **first** statement — one indexed `SELECT` on
`(workspace_id, slug, version)`, covered by `uq_rating_versions_slug_version`, deliberately
without `FOR UPDATE` (`rating_versions.py:111-117`) — the content hash is already in hand.
Everything the measurement attributes the cost to happens *after* it: the blob primary-key
lookup (`score.py:135`), the whole-object store read of 2,039,114 B (`:143`), and
`Bundle.model_validate_json` over that payload including the inlined booster text (`:144`).

**Ruled: the authoritative read stays on the hot path and the three dominant terms leave it.**
The version row is read on every request, as now; on a hit against the hash it already
returned, the compiled bundle is served from the slot and the blob read and the 2 MB parse are
skipped. On a miss — which is what a recompiled version produces — the full path runs and
re-hydrates. **Correct by construction, with zero staleness window**, because every request
re-reads the authoritative binding.

This is not a fix instruction and the shape is not mandated beyond the property: *the
resolution's result is used where it is already available, rather than re-derived from the
blob.* How it is arranged, including keeping the ref→hash memo written for §3's benefit, is
the executor's.

### 3. Why the memo route is refused, and a finding that must not land silently

Serving from `hash_for(ref)` without any read is refused, and **not merely because a read is
cheap**. `backend/src/app/platform/bundle_slot.py:28-31` justifies the ref→hash memo on
artifact immutability — *"a given `rating_version` ref names one immutable version and
compiles to one `Bundle` content hash. The mapping cannot change under the memo."*

**That argument is wrong as stated, and the repository already knows it.** `row.bundle` is
mutable: `POST /api/v1/rating-versions/{id}/compile`
(`backend/src/app/api/models.py:1215-1244`) carries no already-compiled refusal, and
`_rating_compile` (`backend/src/app/worker/rating_handlers.py:41-48`) captures `prior_hash`
**precisely because the recompile overwrites it**, then audits `before`/`after` bundle hashes.
The system therefore already models *a changed content hash under an unchanged pinned ref* as
a normal, audited event. A memo-first happy path would serve the pre-recompile bundle under a
window that is not 30 s and not bounded by anything — it lasts until that worker evicts.

It is safe **today** only because `hash_for` is read solely in the degradation branch, where
serving a last-known-good bundle is what NFR-497 asks for. **The docstring's staleness
argument at `bundle_slot.py:28-31` is a defect in the reasoning, not in the behaviour**, and it
is the sentence a later session would build the happy-path shortcut on. Filing it as a
register row is the auditor's; it is named here so the next reader of that docstring does not
take it as licence.

**A TTL is refused for a second, independent reason.** Workers expire at independent times, so
a TTL produces exactly the *"mixed-bundle requests"* NFR-494 forbids and the *"never a
mix"* FR-268 forbids. It is also unprovable under `CLAUDE.md` §13: nothing observes a
window closing, so there is no deliberately broken input that makes a TTL print a failure. A
per-request read is provable — recompile, then assert the next request scores against the new
hash.

**An invalidation signal is refused as premature, and it is already ruled.** Refresh, poll,
pub/sub and an environment pointer are WK-674's under RL-882 clause 4, recorded in
`bundle_slot.py:33-35` — *"A slot that acquires any of them has overridden the ruling."* This
ruling introduces none of them. The push switchover FR-268 and NFR-494 describe
(pre-warm, then flip, ≤ 30 s including warming) remains the specified end state and remains
WK-674's; §2's shape does not conflict with it and does not anticipate it.

### 4. What this does **not** decide — stated plainly, not softened

- **It does not establish that NFR-489 passes.** It removes the measured dominant term —
  `_fetch_bundle` is 36.574 ms of a 60.959 ms mean handler at the cleanest rung, about 60 %.
  What remains is one `SELECT` plus connection acquisition, `score_one`, and the ~12 ms
  residual of framework, auth, DI and serialisation that NFR-502 is recorded **owed, not
  delivered** for failing to isolate.
- **The 15 ms limb is the one still in the dock, and it is the requirement's own half.** The
  component re-measure reads p99 **23.027 ms** without GBM against a **15 ms** budget — over,
  *with the fetch already excluded*. The with-GBM component p99 is 33.468 ms, inside 50 ms but
  only 1.49× inside. **If a re-measurement with the blob read removed still fails the 15 ms
  limb, that is the trigger that puts NFR-489 itself in question**, and answering it from
  today's numbers would be the guess `CLAUDE.md` §0 forbids. The requirement is not amended
  here and the trigger is named so the next decision is a decision rather than a discovery.
- **It does not establish 200 rps.** NFR-489's budget is *at 200 rps per replica*; the
  measurement never reached it, on a shared box. A re-run needs a dedicated host, and one pass
  will not establish a verdict near a bound.
- **It does not decide the slot's capacity.** `backend/src/app/config.py:172` defaults
  `bundle_slot_capacity` to 1, and its own comment says raising it *"cites a measurement from
  the latency harness"*. With capacity 1 and more than one ref in play the slot thrashes and
  every request pays the full path, so §2's benefit is conditional on a capacity that comment
  requires evidence for. Not set here.
- **A consequence for NFR-497 that is deferred, not ignored.** Under §2 the metadata read
  stays, so NFR-497's degradation clause keeps its meaning intact — which is a further
  argument for §2 over the memo route, where the clause would have described the normal path
  and stopped distinguishing anything.

### 5. Disposition — which of code and spec is wrong, and where the change lands

`CLAUDE.md` §0 asks the question and the answer is **the code**, with a narrower defect than
the record it comes from claims. The closure record §5 and the research note both read this as
*"a deliberate correctness choice with an unmeasured cost"* — correctness traded for latency.
**There is no trade.** The value that would buy the latency is read and thrown away four lines
before the expensive work starts. The specification is not overstated and needs no scoping
clause: FR-239's *"compiled once, distributed, and cached"*, FR-243's `CompiledBundle`
*"held per worker process"*, and `03` §8's Redis row (*"`Bundle` cache keyed by content hash;
hot-path lookup"*) already describe a hot path that is a cache lookup rather than an
object-store read.

**No `docs/specs/` edit is made or authorised by this ruling**, so `.claude/skills/spec-change`
does not fire and no requirement id moves. The code change is `CLAUDE.md` §0's **first** row —
code inside the current phase — and belongs to the reopened WK-671 or to whichever slice next
touches the scoring path; the re-measurement belongs with it, since a change made for latency
that is not re-measured is an assertion.

**The WK-671 closure record §6's carry-forward row** — *"NFR-489 fails at the full path …
owner: an architectural ruling before WK-674 deployment. The question is whether a `ref` may be
served from a memo without a metadata read, and what staleness window that admits"* — **is
discharged by this ruling**: the answer is that it may not, and that it does not need to.
RL-919 §3 has that recorded in the reopen section.

**The ruling is overridden** if `hash_for(ref)` is read before the version row is read, if a
TTL or an invalidation channel is added to `BundleSlot` before WK-674, if NFR-489 is amended
without the re-measurement §4 names, or if the latency change lands without a re-measurement
naming its tree and its host.

---

## Verification

- **Tree:** `daa6fbe`, `origin/main`, re-fetched at 2026-08-30T11:22Z in the same command that
  read the clock, immediately before drafting. Branch head equal to it at that moment.
- **RL-924 was established as the highest existing** by enumerating every `## Ruling N`
  heading under `docs/plans/`, not by trusting the dispatch's figure.
- **The absence claims in RL-920 §1 were checked two ways each** — on disk and in
  `git ls-files` — because an untracked file on disk and a tracked file absent from disk fail
  differently, and `ls` alone distinguishes neither.
- **RL-921's premise refutation was found by reading `compile_rating_version`'s write, not
  by reading `_fetch_bundle` alone.** Reading only the consumer reproduces the research note's
  conclusion; the discarded field is visible only from the producer's side.
- **Every measurement in RL-921 §1 was re-read in
  `docs/research/w11-task-2d-nfr-rate-1-full-path.md`**, with its own stated limits (one pass,
  shared box, void 200 rps rungs) carried forward rather than dropped.
- **RL-919's charter attributions were read in the role files**, not inferred: closure
  records are the auditor's (`.claude/roles/auditor.md`, Owns) and `docs/roadmap.md` is the
  lead's (`.claude/roles/lead.md`, Tools).
- **§0 records what could not be verified.** The maintainer's reopen direction is a relay with
  no artifact behind it at this tree, and RL-919 §1 makes recording it a precondition rather
  than assuming it.
- `python3 scripts/audit-docs.py` — run before commit.
- **Mints no id and registers no error code**, so it owes no [`../open-questions.md`](../open-questions.md)
  mirror row and no [`../roadmap.md`](../roadmap.md) §10 gate row. Makes no `docs/specs/` or
  `docs/contracts/` edit, so it opens no window in which declarations disagree.
