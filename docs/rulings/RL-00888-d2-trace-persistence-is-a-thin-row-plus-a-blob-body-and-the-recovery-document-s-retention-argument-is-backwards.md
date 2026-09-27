---
id: RL-888
family: ruling
title: D2: trace persistence is a thin row plus a blob body, and the recovery document's retention argument is backwards
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-08-29
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-08-29-w11-slices-3-4-rulings.md
---

# WK-671 Slices 3 and 4 — trace persistence, the batch abort threshold, and the batch-sampling "silence" (2026-08-29)

**What this is.** The three decision points recovered in
[`../plans/PL-00851-wk-671-five-decision-points-recovered.md`](../plans/PL-00851-wk-671-five-decision-points-recovered.md) that
were left unruled: its **item 2** (trace sampling and retention), the batch-abort-threshold flag
inside its **item 4**, and the spec omission it flagged separately at the end — which
[`../plans/PL-00855-wk-671-slices-2-4-planning-readiness-the-signals-that-release-each-and-what-a-leaf-plan-can-already-take-from-here-2026-08-29.md`](../plans/PL-00855-wk-671-slices-2-4-planning-readiness-the-signals-that-release-each-and-what-a-leaf-plan-can-already-take-from-here-2026-08-29.md)
§9 carries as **D2**, **D3** and **D5**. Recovery items 1, 3 and 5 are already ruled (Rulings 10,
5 and 9 respectively).

**Numbering continues at 23.** Rulings 1–5 are the prework record's, 6–13 the Slice 1 record's,
14–15 the Slice 2 record's, 16–21 the Slices 2–4 record's, 22 the rate-table maturity record's.

**Mints no `FR-`/`NFR-`/`OQ-` id and no error code. `OQ-RATE-8` is deliberately *not* taken** —
RL-890 finds nothing to raise, and the id stays free for whoever needs it next.

**RL-856's lesson was applied to all three, and it changed one answer outright.** The
instruction was to grep the whole suite before calling anything silent. Doing so **dissolves D5**
— the suite answers it in three places, one of them a dated amendment inside a requirement — and
**confirms D3** as genuinely homeless, which is the same discipline reaching the opposite result.
It also inverted the polarity of one of D2's supporting claims.

**Read against `origin/main` at `d614f24`**, with `HEAD` identical.

---

## RL-888 — D2: trace persistence is a thin row plus a blob body, and the recovery document's retention argument is backwards

**The decision, restated.** Recovery item 2 asks where a sampled trace is persisted: **(a)** full
JSON in PostgreSQL; **(b)** a thin PostgreSQL row plus the trace body as a content-addressed blob,
with `GET /api/v1/traces` querying the row table; **(c)** `05-monitoring` owns persistence. It
recommends (b) and calls `07` FR-420's reference-counted blob GC *"a ready-made retention
mechanism"*.

**Ruled: (b)** — with one correction to its reasoning, one deferral it does not name, and two
implementation constraints an executor would otherwise have to guess.

### Why (b), verified rather than adopted

- **The row-plus-blob precedent is real and is in this module.** `03` §4.6's `DislocationRun`
  carries `"largest_movers_blob": "blob:sha256:…"` ([`../specs/03-rating-engine.md`](../specs/03-rating-engine.md)`:472`)
  beside its queryable fields.
- **The blob store supports it today.** FR-418 ([`../specs/07-platform.md`](../specs/07-platform.md)`:112`)
  makes it content-addressed with *"size, media type, and reference count tracked in
  PostgreSQL"*; FR-419 (`:113`) makes blobs immutable and deduplicated.
  `backend/src/app/platform/blobs.py` is the shipped implementation.
- **(c) is refused by the direction of the dependency**, which `05` §7 states from its own side:
  it consumes *"Sampled production traces, deployment events, premium ladders …"* from
  `03-rating-engine`. A consumer does not own its producer's storage.
- **(a) is refused by NFR-500** (`03:795`), which budgets 200 GB/year *"with the sampled-trace
  schema"* — a nested per-step array at that volume in the transactional database.

### Correction — the retention argument is inverted, and the inversion matters

**FR-420's GC is not a retention mechanism; it is a deletion mechanism, and NFR-459 is a
preservation floor.** FR-420 (`07:114`) makes a blob *"deletable only when no artifact
references it and it is older than a configurable grace period (default 30 days)"*. NFR-459
([`../specs/00-overview.md`](../specs/00-overview.md)`:523`) says scoring traces are *"sampled and
retained **≥ 13 months**"* — a minimum, not an expiry. Nothing in the suite obliges anyone to
delete a trace ever.

So the two do not compose the way the recovery document has them. Read correctly:

- A trace blob is unreachable by GC for as long as its row references it, which is what makes
  NFR-459 satisfiable at all.
- The **only** way to breach NFR-459 is to delete the row early — the blob then becomes
  reclaimable one grace period later.
- There is therefore **no expiry job to build**, and the guard Slice 4 owes is on row deletion,
  not on retention scheduling. Building "GC-based retention" as described would have produced
  either nothing or a deleter that breaches the floor it was meant to honour.

**The shipped GC settles this at the code level, not only the requirement's.**
`backend/src/app/platform/blobs.py:301-305` selects candidates with
`BlobRow.ref_count == 0` and `created_at < cutoff`, `retain`/`release` (`:339-350`) move the
count, and the grace period comes from `retention.blob_gc_grace_days` (default 30,
`backend/src/app/platform/settings.py:194-201`). A referenced blob is not a candidate at all —
so GC could not have expired a trace even if Slice 4 asked it to.

### The deferral the recovery document does not name

`00` §4.1's entity-relationship map (`:261`) reads `Deployment ──< ScoringTrace (sampled) ──<
MonitoringAggregate`. **A ScoringTrace's parent is a Deployment**, and Deployment is FR-267 —
WK-674's, as RL-880 established for the same reason on the scoring endpoint. The word *production*
carries the same dependency: FR-259 scopes the sampled stream to *"In production"*, `03`
§5.1's route is *"Sampled **production** traces"* (`:525`), and `05` §7 asks for *"Sampled
**production** traces"* — and there is no Environment or Deployment before WK-674.

**Ruled:** Slice 4 builds the artifact and its storage shape, and the row carries the parent it
can resolve — the rating version reference, the bundle hash, and the environment as a plain
string — gaining the Deployment reference in WK-674. This is the same deferral shape as RL-880 and
is booked the same way: a register row, which is the lead's to write.

### Two constraints an executor would otherwise guess

1. **Deduplication will not help, and the budget must not be planned as though it will.**
   FR-419 dedupes identical content, and `03` §4.5's Trace shape carries `elapsed_us` on every
   step (`:436`, `:441`), so no two traces are byte-identical even for identical inputs.
   NFR-500's 200 GB/year must be met by the schema and the sample rate alone.
2. **The row is a projection of the blob and must be written from the same object.** Three of the
   four fields recovery item 2 proposes for the row — `quote_id`, `rating_version_ref`,
   `bundle_hash` — are already in the trace body at `03` §4.5; only `sample_reason` is new. A
   projection assembled separately from the body it projects will diverge. Serialise once, write
   both in one operation.

### Disposition

No spec change. The row-plus-blob split is an implementation choice inside FR-259 and
NFR-500, and `03` §4.5 already publishes the artifact. If Slice 4 finds the row itself needs a
published contract, that is a `03` §4 change at that point and not before.

**Acceptance test — the violation that must become expressible.** Today nothing can express *"a
sampled trace was lost before its thirteenth month"*, because no trace is persisted at all —
`git grep -ln "ScoringTrace\|scoring_trace\|trace_sampling\|sample_reason" -- packages backend`
returns nothing at `d614f24`. After Slice 4 the expressible violation is a trace row deleted while
NFR-459's floor still covers it, and the test is that deleting a trace row younger than the
retention floor is refused. **The ruling is overridden** if any build reclaims a trace blob whose
row still exists, or ships an expiry job that deletes rows on a schedule shorter than the floor.

---
