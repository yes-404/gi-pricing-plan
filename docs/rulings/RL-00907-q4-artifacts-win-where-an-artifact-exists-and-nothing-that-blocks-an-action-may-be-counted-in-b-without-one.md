---
id: RL-907
family: ruling
title: Q4: artifacts win where an artifact exists — and nothing that blocks an action may be counted in B without one
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-08-30
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-08-30-nt-0014-q1-q3-q4-rulings.md
---

## RL-907 — Q4: artifacts win where an artifact exists — and nothing that blocks an action may be counted in B without one

### 1. Verified first, at `1407e09`

| Claim | Verdict |
|---|---|
| F31 is as described | **Confirmed** — [`../findings/register.md`](../findings/register.md): a heredoc emitting a fixed string with only the timestamp substituted; *"Every substantive field was false and only the freshness timestamp was true, so the file looked healthier the longer it was wrong"* |
| F31's resolution binds a successor | **Confirmed, verbatim** — *"A successor either builds the derivation or the charter drops the claim — the one thing it must not do is inherit a constant with a live timestamp"* |
| B is the same shape | **Confirmed** — same ops area, same writing role (the watcher, matrix row 10), same publication as team state. `runtime_state_schema`'s example in the extract carries **one** file-level `updated_at` over the whole document |
| C2 writes B's counters, and lands after B | **Confirmed** — RL-920 §4 and §6: G is *"still blocked — on slice E"* |
| §7 lists four things to log | **Confirmed** — replan iterations, audit-fix iterations, per-slice re-audit counts, **and gate re-runs**. The caps table covers layers, not gate re-runs |
| §10 places ops state outside the repo | **Confirmed** — and names *"roster state"* among it, the artifact F31 withdrew |

### 2. Ruled — four parts

**(a) Artifacts win, and the answer is bounded by where an artifact exists.** The *capped*
counters — replan iterations at a layer, per-slice re-audit counts — count events that land
in durable committed records: a plan revision, an audit record, a merged PR. For those, B is
a cache and §3's authority rule applies unchanged: on disagreement the artifact is right and
B is wrong by definition. **Gate re-runs are logged and not capped**, so nothing blocks on
them and no authority question arises. The general rule, which is the part worth carrying:
**nothing that blocks an action may be counted in B without a durable artifact behind it.**
Otherwise "artifacts win" is a rule with no artifact, and B is a *record* living outside the
repository, which §10 forbids by its own distinction.

**(b) The watcher re-derives; it does not compare two independently-kept tallies.** "Flags
the mismatch" is not enough, and the reason is the crux of Q4: the failure this file will
actually have is not disagreement, it is **agreement by vacancy**. C2 unwired or silently
broken, B reads `0`, the artifacts read `0`, the flag never fires, the cap never binds, and
every reader is told the process is healthy. **A mismatch detector cannot detect a dead
writer.** So each cycle the watcher recomputes every capped counter from the artifacts and
writes the recomputation. C2's increment stays (RL-920) because the cap must bind at the
moment of the retry, not one watcher cycle later — but a divergence is then a **defect in
C2**, reported as one, not an ambiguity to be adjudicated.

**(c) What makes B different from `roster-state.md`: nothing — unless every field either
re-derives or expires.** F31 binds B, and three conditions discharge it.

- **No file-level freshness token.** A single `updated_at` over the whole document is the F31
  shape exactly: one true field vouching for a document of frozen ones. Every block carries
  its own `written_by` and `written_at`, and the watcher does not touch a block it did not
  write this cycle. `runtime_state_schema` in the extract changes accordingly in slice E.
- **Unwired is absent, never zero.** `retry_counters` may not appear in B until C2 exists.
  **Slice E therefore ships `position` and `in_flight_expensive_verifications` only.** A `0`
  from a counter nothing increments is indistinguishable from a true zero — `RFC-789`'s
  boundary metric in another dress — and this is the concrete reason the note's
  implementation order (B before C2) is a hazard and not merely a sequence.
- **A field with no derivation must expire.** `in_flight_expensive_verifications` is
  genuinely underivable: ephemeral coordination state, announced by a role about itself. It
  is made falsifiable the other way — each entry carries `started_at` and a stated TTL, and
  **a reader treats an expired entry as absent, not as in flight**. This repository already
  knows why one is needed: stopping an agent does not stop the commands it started, so an
  entry outlives its process by default, and a stale entry's failure is silent and
  one-directional — it blocks work that should proceed.
- **`position` fields name the artifact they were read from.** Phase and work read from
  [`../roadmap.md`](../roadmap.md), slice from the filed plan. `flow_step` has no source
  artifact; it is the watcher's belief about what a running agent is doing, which is the
  roster-state claim verbatim. **It is carried only if slice E can name its source, and
  dropped otherwise** — the honest state, and better than one that lies.

**(d) The acceptance test, stated as the violation that must become impossible.** Slice E is
not accepted until a test shows that **a B written by a watcher cycle in which nothing
changed is byte-identical to the previous one.** If any byte moves, a freshness token is
refreshing while its content is frozen, and that is F31 regardless of what the surrounding
prose says. The 108 consecutive identical balance readings are the same failure found live;
this test is the smallest thing that makes it loud.

### 3. What it obliges

Slice E, and the `runtime_state_schema` block of the extract in the same slice — which under
RL-905 also moves the extract's digest, so the two rulings meet in one commit.

**Overridden if** B ships a file-level `updated_at` as its only freshness token, if
`retry_counters` appears before C2, if the watcher's reconciliation is a comparison rather
than a re-derivation, or if any field that blocks an action is counted without a durable
artifact behind it.

---
