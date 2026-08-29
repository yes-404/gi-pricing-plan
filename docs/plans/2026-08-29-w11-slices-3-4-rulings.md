# W11 Slices 3 and 4 — trace persistence, the batch abort threshold, and the batch-sampling "silence" (2026-08-29)

**What this is.** The three decision points recovered in
[`2026-08-29-w11-decision-points-recovery.md`](2026-08-29-w11-decision-points-recovery.md) that
were left unruled: its **item 2** (trace sampling and retention), the batch-abort-threshold flag
inside its **item 4**, and the spec omission it flagged separately at the end — which
[`2026-08-29-w11-slices-2-4-planning-readiness.md`](2026-08-29-w11-slices-2-4-planning-readiness.md)
§9 carries as **D2**, **D3** and **D5**. Recovery items 1, 3 and 5 are already ruled (Rulings 10,
5 and 9 respectively).

**Numbering continues at 23.** Rulings 1–5 are the prework record's, 6–13 the Slice 1 record's,
14–15 the Slice 2 record's, 16–21 the Slices 2–4 record's, 22 the rate-table maturity record's.

**Mints no `FR-`/`NFR-`/`OQ-` id and no error code. `OQ-RATE-8` is deliberately *not* taken** —
Ruling 25 finds nothing to raise, and the id stays free for whoever needs it next.

**Ruling 22's lesson was applied to all three, and it changed one answer outright.** The
instruction was to grep the whole suite before calling anything silent. Doing so **dissolves D5**
— the suite answers it in three places, one of them a dated amendment inside a requirement — and
**confirms D3** as genuinely homeless, which is the same discipline reaching the opposite result.
It also inverted the polarity of one of D2's supporting claims.

**Read against `origin/main` at `d614f24`**, with `HEAD` identical.

---

## Ruling 23 — D2: trace persistence is a thin row plus a blob body, and the recovery document's retention argument is backwards

**The decision, restated.** Recovery item 2 asks where a sampled trace is persisted: **(a)** full
JSON in PostgreSQL; **(b)** a thin PostgreSQL row plus the trace body as a content-addressed blob,
with `GET /api/v1/traces` querying the row table; **(c)** `05-monitoring` owns persistence. It
recommends (b) and calls `07` FR-PLAT-20's reference-counted blob GC *"a ready-made retention
mechanism"*.

**Ruled: (b)** — with one correction to its reasoning, one deferral it does not name, and two
implementation constraints an executor would otherwise have to guess.

### Why (b), verified rather than adopted

- **The row-plus-blob precedent is real and is in this module.** `03` §4.6's `DislocationRun`
  carries `"largest_movers_blob": "blob:sha256:…"` ([`../specs/03-rating-engine.md`](../specs/03-rating-engine.md)`:472`)
  beside its queryable fields.
- **The blob store supports it today.** FR-PLAT-18 ([`../specs/07-platform.md`](../specs/07-platform.md)`:112`)
  makes it content-addressed with *"size, media type, and reference count tracked in
  PostgreSQL"*; FR-PLAT-19 (`:113`) makes blobs immutable and deduplicated.
  `backend/src/app/platform/blobs.py` is the shipped implementation.
- **(c) is refused by the direction of the dependency**, which `05` §7 states from its own side:
  it consumes *"Sampled production traces, deployment events, premium ladders …"* from
  `03-rating-engine`. A consumer does not own its producer's storage.
- **(a) is refused by NFR-RATE-12** (`03:795`), which budgets 200 GB/year *"with the sampled-trace
  schema"* — a nested per-step array at that volume in the transactional database.

### Correction — the retention argument is inverted, and the inversion matters

**FR-PLAT-20's GC is not a retention mechanism; it is a deletion mechanism, and NFR-OVR-6 is a
preservation floor.** FR-PLAT-20 (`07:114`) makes a blob *"deletable only when no artifact
references it and it is older than a configurable grace period (default 30 days)"*. NFR-OVR-6
([`../specs/00-overview.md`](../specs/00-overview.md)`:523`) says scoring traces are *"sampled and
retained **≥ 13 months**"* — a minimum, not an expiry. Nothing in the suite obliges anyone to
delete a trace ever.

So the two do not compose the way the recovery document has them. Read correctly:

- A trace blob is unreachable by GC for as long as its row references it, which is what makes
  NFR-OVR-6 satisfiable at all.
- The **only** way to breach NFR-OVR-6 is to delete the row early — the blob then becomes
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
MonitoringAggregate`. **A ScoringTrace's parent is a Deployment**, and Deployment is FR-RATE-50 —
W14's, as Ruling 14 established for the same reason on the scoring endpoint. The word *production*
carries the same dependency: FR-RATE-42 scopes the sampled stream to *"In production"*, `03`
§5.1's route is *"Sampled **production** traces"* (`:525`), and `05` §7 asks for *"Sampled
**production** traces"* — and there is no Environment or Deployment before W14.

**Ruled:** Slice 4 builds the artifact and its storage shape, and the row carries the parent it
can resolve — the rating version reference, the bundle hash, and the environment as a plain
string — gaining the Deployment reference in W14. This is the same deferral shape as Ruling 14 and
is booked the same way: a register row, which is the lead's to write.

### Two constraints an executor would otherwise guess

1. **Deduplication will not help, and the budget must not be planned as though it will.**
   FR-PLAT-19 dedupes identical content, and `03` §4.5's Trace shape carries `elapsed_us` on every
   step (`:436`, `:441`), so no two traces are byte-identical even for identical inputs.
   NFR-RATE-12's 200 GB/year must be met by the schema and the sample rate alone.
2. **The row is a projection of the blob and must be written from the same object.** Three of the
   four fields recovery item 2 proposes for the row — `quote_id`, `rating_version_ref`,
   `bundle_hash` — are already in the trace body at `03` §4.5; only `sample_reason` is new. A
   projection assembled separately from the body it projects will diverge. Serialise once, write
   both in one operation.

### Disposition

No spec change. The row-plus-blob split is an implementation choice inside FR-RATE-42 and
NFR-RATE-12, and `03` §4.5 already publishes the artifact. If Slice 4 finds the row itself needs a
published contract, that is a `03` §4 change at that point and not before.

**Acceptance test — the violation that must become expressible.** Today nothing can express *"a
sampled trace was lost before its thirteenth month"*, because no trace is persisted at all —
`git grep -ln "ScoringTrace\|scoring_trace\|trace_sampling\|sample_reason" -- packages backend`
returns nothing at `d614f24`. After Slice 4 the expressible violation is a trace row deleted while
NFR-OVR-6's floor still covers it, and the test is that deleting a trace row younger than the
retention floor is refused. **The ruling is overridden** if any build reclaims a trace blob whose
row still exists, or ships an expiry job that deletes rows on a schedule shorter than the floor.

---

## Ruling 24 — D3: the batch abort threshold is a workspace setting with a one-directional per-run argument

**The decision, restated.** FR-RATE-38 (`03:166`) says a batch run *"does not abort on individual
failures unless the failure rate exceeds a **declared threshold**"* and does not say where the
declaration lives. Recovery item 4 recommends a workspace setting on `07` FR-PLAT-45's precedent
*"with an optional per-batch-request override"*.

**Ruled: a workspace setting, unset by default, plus a per-run argument that may only lower the
effective threshold — never raise it.** Three parts, and the third is a correction.

### It is genuinely homeless, and that was checked rather than assumed

Ruling 22's lesson cuts both ways. Swept:
`grep -rn "failure rate\|failure_rate\|abort" docs/specs/*.md docs/workflows/*.md` returns
FR-RATE-38 itself and, otherwise, only `02` FR-MODEL-48's per-round fit abort and its two workflow
rows — a different mechanism in a different module. FR-PLAT-45's enumerated workspace settings
(`07:174`) list currency, locale, default validation thresholds, trace sampling rate, approval
policy reference, retention windows, the two model-complexity thresholds and feature flags, and
**no batch failure threshold**. So unlike D5 below, this one really is unhoused.

### Part 1 — the home, and the default

The setting joins FR-PLAT-45's list and is **unset by default**. Two reasons, both from text
already on the page: FR-RATE-38's own construction — *"does not abort … **unless** the failure rate
exceeds a declared threshold"* — makes an undeclared threshold mean *no rate-based abort*, with the
requirement's first half (counts and samples per error type) still doing its work; and FR-PLAT-45's
own list already carries two thresholds *"both unset by default"* (`modelling.max_factor_count`,
`modelling.min_exposure_per_parameter`), so the pattern needs no invention.

**Mirror the shipped neighbour rather than inventing a second mechanism.** Both of those
settings are read at `backend/src/app/platform/model_specs.py:62` and `:65` through one
resolver taking a dotted key, typed `int | None` / `float | None` and guarded with
`if … is not None` (`:109`, `:125`) — unset-by-default in the code, not only on the page. The
key ruled here, `rating.batch_abort_failure_rate`, follows that `<module>.<name>` form
exactly. No per-request override exists anywhere on that path today, which is the other half
of why the run's value must be a Job argument rather than a fourth resolution tier.

### Part 2 — it is a Job input, not a fourth precedence tier

FR-PLAT-43 (`07:172`) resolves settings by *"environment variable → workspace setting → platform
default"* — three tiers, and *"the effective value and its source are inspectable by an Admin."*
An unqualified "per-request override" would silently add a fourth tier to that chain and make the
inspector's answer incomplete. That chain is not only specified but implemented as exactly three:
`settings.resolve` (`backend/src/app/platform/settings.py:261-279`) reads an environment candidate
and a `workspace_settings` row and hands both to `_resolution` (`:328-345`), which reports the
source as `ENV`, `WORKSPACE` or `DEFAULT` and has no fourth branch to add one to.

**Ruled:** the run's value is an **argument to the Job**, not a Setting. FR-PLAT-43's chain
resolves the workspace default; the run's argument is recorded on the Job — where FR-PLAT-14
(`07:99`) already retains *"its parameters and result reference"* for ≥ 13 months — and never
enters settings resolution. FR-PLAT-43 is untouched and stays true as written.

### Part 3 — the correction: the argument is one-directional

The recovery document's *"optional per-batch-request override"* is unqualified. `01` has already
decided this exact question for thresholds, and decided it the other way:

- **FR-DATA-54** ([`../specs/01-data-management.md`](../specs/01-data-management.md)`:118`):
  *"Changing a validation rule's threshold authors a new rule version. A threshold is part of what
  a rule *is*."*
- `01:355`: *"A rule's thresholds are **not overridable** at set level either, and for a stronger
  reason than severity's: **no threshold has a safe direction to move in** (FR-DATA-54)."*
- And where `01` does permit an override at all, it is one-directional: `severity_override` *"may
  only *raise* severity (`warn → fail`), never lower"* (`01:352`).

Applied here, the safe direction is unambiguous and the two cases are not symmetric: **lowering**
the threshold aborts a failing batch sooner, **raising** it lets a run push through more failures
than the workspace agreed to tolerate. So the argument may only lower the effective threshold. That
keeps the workspace setting a genuine floor on caution — the same shape as `severity_override`,
whose precedent is what makes this a derivation rather than a preference.

### Disposition

Two spec changes in this commit: FR-PLAT-45's list gains the setting, and FR-RATE-38 gains a dated
clarification naming where *"declared"* lives, the unset default, the one-directional argument, and
the requirement that the Job records both the threshold in force and the observed failure rate when
it aborts — an abort nobody can reconstruct is not auditable.

**Acceptance test — the violation that must become expressible.** Today *"this batch aborted at a
threshold nobody agreed to"* cannot be said, because no threshold exists anywhere to disagree with.
After this ruling the expressible violation is a run that completes past its workspace threshold,
or a run whose argument raises it: a batch request carrying a threshold **above** the workspace
setting must be refused, and a run whose failure rate crosses the effective threshold must abort
with both numbers on the Job. **The ruling is overridden** if a build accepts a per-run value
higher than the resolved setting, or aborts without recording the threshold it used.

---

## Ruling 25 — D5: FR-RATE-41/42 are not silent about batch, and no open question is raised

**The decision, restated.** The recovery document flags, and the readiness document carries as D5,
that *"FR-RATE-41/42 state no batch sampling default"* — recommending batch inherit the 1 % policy
*"or a 10M-row batch Job blows the annual storage budget in one run"* — and says it *"needs an
`OQ-` or a spec change from the decision-maker"*.

**Ruled: no `OQ-`, no gap. The suite answers it in three independent places, and the answer is not
the one the recommendation reaches for.** `OQ-RATE-8` is not taken.

### What the sweep found

1. **FR-RATE-42 scopes itself.** *"**In production**, traces are sampled (default 1 %, configurable,
   plus 100 % of declines and errors) and persisted for ≥ 13 months"* (`03:175`). The sampled
   stream is the production quoting path, not every code path that can produce a trace.
2. **Two more locations say *production* independently.** `03` §5.1's route is *"Sampled
   **production** traces (FR-RATE-42)"* (`:525`), and `05` §7 lists what it consumes from `03` as
   *"Sampled **production** traces, deployment events, premium ladders …"*.
3. **A dated amendment inside a requirement already divides the labour.** FR-MON-11
   ([`../specs/05-monitoring.md`](../specs/05-monitoring.md)`:101`) carries: *"(Recorded 2026-08-26,
   OQ-MON-1: A/E is computed from a full batch re-score of the exposure dataset (`03` FR-RATE-36),
   **not from traces**; trace sampling stays for quote-level metrics — conversion, declines,
   latency, constraint activation.)"* OQ-MON-1 is **decided**, maintainer-accepted, and its
   reasoning is exactly D5's subject: full coverage comes from the batch re-score's own output; the
   trace stream is for the quote-level metrics where full coverage is unaffordable.
4. **NFR-RATE-12's budget is over quotes, not batch rows** — *"1 % sampling of 50 M annual
   **quotes**"* (`03:795`).

So the feared failure mode — a multi-million-row batch Job consuming the annual trace budget — is
of something the suite never asked for. **This is the same class as Ruling 22's finding and the
opposite result to D3's:** a claim of silence that a suite-wide grep dissolves, where the answer
was sitting in a sibling module's dated amendment that an id-based search never reaches.

### What follows for Slice 3 and Slice 4

- **Batch scoring contributes nothing to the sampled production trace stream, and `score_batch`
  takes no sampling policy.** Slice 3 builds none, and Slice 4's sampling applies to the real-time
  path only.
- **A batch run may still produce traces**, because FR-RATE-41 says *"Traces are the same structure
  in real-time and batch"* — but on request, per FR-RATE-41's own *"on request"*, and they are
  written with that Job's output under Ruling 23's row-plus-blob shape with the **Job** as their
  parent. They never enter `GET /api/v1/traces`, which `03` §5.1 scopes to production.

### Disposition

One spec change: FR-RATE-42 gains a dated clarification recording the scope its first two words
already carry and pointing at FR-MON-11's amendment — because two independent readers, the recovery
document and the readiness document, both read the pair as silent, which is evidence the text
invites the misreading even though it does not contain it. No requirement's meaning changes.

**Acceptance test — the violation that must become expressible.** The violation is a batch run
whose traces land in the production stream: after Slice 3, `GET /api/v1/traces` must return nothing
attributable to a `score/batch` Job, and a batch run must not consume sample budget. Before this
ruling that could not even be asserted, because an implementer following the recovery document's
recommendation would have made batch traces *part* of that stream at 1 %. **The ruling is
overridden** if `score_batch` acquires a sampling rate parameter, or if a trace row written by a
batch Job is returned by the production traces route.

---

## Findings reported, not ruled

1. **The trace sampling rate is specified in three places and nothing reconciles them.**
   FR-PLAT-45 (`07:174`) makes it a **workspace** setting; FR-PLAT-31 (`07:142`) makes *"sampling
   rates"* part of **environment** configuration resolved by §3.8's precedence; and `05`'s Monitor
   shape carries `"trace_sample_rate": 0.01` inside a Monitor's own **population** block
   (`05:164`), which is a third declaration that a Monitor asserts rather than reads. A Monitor
   whose declared rate disagrees with the environment's actual rate computes A/E against a
   population that does not exist. Not W11's — the Monitor shape is `05`'s and the precedence is
   `07` §3.8's — and not urgent, since OQ-MON-1 moved A/E off traces. Owner: the lead to place.
2. **`00` §4.1's ERD parents `ScoringTrace` on `Deployment`, which is the third W11 surface to hit
   the W14 dependency** after FR-RATE-34's default-live path (Ruling 14) and NFR-RATE-9's degraded
   read (Ruling 16). Three instances is a pattern rather than three coincidences, and it may be
   worth one register row naming the class instead of three naming the cases. A §14 plan-review
   question, which `CLAUDE.md` §12 puts outside this role.

---

## Sources — read at `d614f24`

- `docs/specs/03-rating-engine.md` — FR-RATE-37/38 `:165-166`, FR-RATE-41/42 `:174-175`, §4.5
  `Trace`, §4.6 `DislocationRun` `:447-472`, §5.1 `:525`, NFR-RATE-12 `:795`.
- `docs/specs/07-platform.md` — FR-PLAT-14 `:99`, FR-PLAT-18/19/20 `:112-114`, FR-PLAT-31 `:142`,
  §3.8 FR-PLAT-43/44/45 `:172-174`.
- `docs/specs/05-monitoring.md` — FR-MON-11 `:101` including its 2026-08-26 amendment, the Monitor
  shape `:158-168`, §7's dependency table.
- `docs/specs/01-data-management.md` — FR-DATA-54 `:118`, `:352`, `:355`.
- `docs/specs/00-overview.md` — §4.1's ERD `:261`, NFR-OVR-6 `:523`.
- `docs/open-questions.md` — OQ-MON-1 `:143`, decided 2026-08-26.
- `docs/plans/2026-08-29-w11-decision-points-recovery.md` items 2, 4 and the flagged omission;
  `2026-08-29-w11-slices-2-4-planning-readiness.md` §9's queued table;
  `2026-08-29-w11-scoring.md` Slice 4.
- Code: `backend/src/app/platform/blobs.py:301-350`, `backend/src/app/platform/settings.py:194-201`
  and `:261-345`, `backend/src/app/platform/model_specs.py:53-140`; and the absence sweep
  `git grep -ln "ScoringTrace\|scoring_trace\|trace_sampling\|sample_reason" -- packages backend`,
  which returns nothing.
