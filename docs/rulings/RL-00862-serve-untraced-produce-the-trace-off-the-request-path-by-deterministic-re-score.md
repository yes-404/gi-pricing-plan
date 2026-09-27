---
id: RL-862
family: ruling
title: serve untraced; produce the trace off the request path by deterministic re-score
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-08-29
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-08-29-w11-nfr-rate-1-trace-capture-remedy-ruling.md
---

# WK-671 — the NFR-489 remedy: trace production moves off the serving request (2026-08-29)

**What this is.** The remedy ruling the lead released, on the ground they identified: Slice 4's
leaf plan pins the traced *fraction* at **1**, so NFR-489 fails on 100 % of traffic
unconditionally in the decline rate. That ground is confirmed, and it changes the remedy rather
than only the severity.

**This supersedes nothing in RL-863 and corrects one of its premises.** RL-863's
conclusion — sampling is not a remedy — stands and is strengthened. But its §2–§3 computed a
traced fraction *p* from FR-259's persistence policy, which silently assumed that the
population **paying** the traced cost is the population whose traces are **kept**. Under
always-capture those are different populations, and *p* = 1 regardless of the sampling knob.
The arithmetic was right about the knob and wrong about what the knob governs.

**Numbering continues at 35.** Rulings 1–30 are catalogued in
[`RL-00858-03-5-2-s-identical-step-evaluator-names-an-artifact-that-does-not-exist-the-spec-is-wrong-the-code-is-right.md`](RL-00858-03-5-2-s-identical-step-evaluator-names-an-artifact-that-does-not-exist-the-spec-is-wrong-the-code-is-right.md);
31–32 there, 33 in
[`RL-00871-no-8-stands-unamended-and-unexcepted-and-the-test-the-question-proposed-is-the-wrong-one.md`](RL-00871-no-8-stands-unamended-and-unexcepted-and-the-test-the-question-proposed-is-the-wrong-one.md),
34 in
[`RL-00863-sampling-cannot-remedy-either-requirement-and-the-reasons-differ.md`](RL-00863-sampling-cannot-remedy-either-requirement-and-the-reasons-differ.md).

**Mints no `FR-`/`NFR-`/`OQ-` id and amends no requirement.** The remedy is satisfied by the
requirements as written; §5 explains why no amendment is needed, which is the part that would
otherwise be assumed.

**Read against `origin/main` at `fb56dc6`.**

---

## RL-862 — serve untraced; produce the trace off the request path by deterministic re-score

**Ruled: trace *production* is decoupled from the serving request.** The quoting path scores
untraced and responds. Where FR-259 requires a trace — every decline, every error, and the
sampled fraction — the trace is produced by re-scoring the same Quote Context against the same
pinned bundle, off the request path, and persisted. **FR-259's 100 % rule is not weakened,
and no requirement is amended.**

### 1. The ground is confirmed, and it is stronger than a decline-rate argument

Slice 4's plan (`2026-08-29-w11-4-trace-sampling-persistence.md`:317–331), verbatim at
`fb56dc6`:

> **A declined or errored quote is sampled at 100 %, which means `trace=True` must be decided
> *before* the outcome is known** — the request either always requests a trace and discards it
> when not sampled, or re-scores, and re-scoring is not acceptable on a 50 ms budget. Take the
> first; note the cost in 4D's measurement, because always-tracing changes the latency figure
> Slice 2 measured.

So every request runs `trace=True`. **The traced fraction is 1**, and NFR-489's p99 is the
traced p99 — 103.2 ms against a 50 ms budget, a breach on **every** request, with no dependence
on *d* at all.

The plan also routed this here in advance, and the trigger has now fired: *"If measurement in
4D shows always-capturing breaches NFR-489, that is a finding for the decision-maker, not a
licence to drop the 100 % rule — the rule is FR-259's text."* **That instruction is correct
and is honoured below: the 100 % rule is untouched.**

### 2. The rejected alternative was measured against the wrong baseline

The plan dismissed re-scoring because *"re-scoring is not acceptable on a 50 ms budget"*. That
is true of a re-score performed **inside** the request — and the option it chose instead is
worse on the same metric, for every request rather than a fraction:

| | request-path cost | share of traffic breaching 50 ms |
|---|---|---|
| Always capture and discard (chosen) | traced, p99 103.2 ms | **100 %** |
| Synchronous re-score on decline | untraced, plus traced for declines | *d* + sample |
| **Off-path re-score (this ruling)** | **untraced, p99 12.5 ms** | **0 %** |

The comparison that was never made is the third row. **NFR-489 bounds what the serving
request costs, and a trace produced after the response has been sent is not part of it.** The
dismissal treated "re-score" as necessarily synchronous; nothing requires that.

### 3. Neither requirement is strained, because each was read for its own scope

- **FR-259** (`03`:175) requires that traces are *"**sampled** … and **persisted** for
  ≥ 13 months …, feeding `05-monitoring.md`"*. It is a **persistence and monitoring**
  requirement. It says nothing about *when* a trace is produced, and nothing that requires it to
  come from the serving execution. Every decline still yields a persisted trace under this
  ruling.
- **FR-258** (`03`:174) governs the *caller-requested* trace — *"**on request**, scoring
  returns every step's id, label, …"*. That path is **unchanged**: a caller who asks for a trace
  gets one inline and knowingly pays for it. It is not the 200 rps production quoting population
  NFR-489 sizes, and this ruling does not touch it.
- **NFR-489** (`03`:797) bounds *"real-time scoring p99 … **server-side**"*. Serving untraced
  puts the quoting path at the untraced distribution — p99 12.5 ms against a 50 ms budget,
  roughly 4× headroom — where always-capture puts it at 2.06× over.

### 4. The mechanism is already specified platform behaviour, not new capability

This is the part that makes the remedy cheap rather than speculative. **Both things an off-path
re-score needs are already required elsewhere in this same spec:**

- **Storing a Quote Context and re-scoring it is FR-260** (`03`:176): *"A **Golden Quote**
  stores a Quote Context and the expected outputs. Promotion **re-scores** every golden quote
  and refuses promotion on any mismatch beyond a declared tolerance (**default: exact for
  money**)."* So storing the input and re-running it is established, and **exact reproduction is
  already an obligation the platform holds itself to.**
- **Re-scoring off the request path is already the platform's idiom for coverage.** `05`
  FR-317's 2026-08-26 amendment, quoted inside FR-259 itself, puts full-coverage A/E on
  *"a batch re-score of the exposure dataset"* and, in its own words, *not from traces*.

Determinism is likewise not an assumption being introduced: FR-254 requires real-time and
batch to produce byte-identical results through the identical code path, and RL-857 makes
that byte-identity Slice 3's acceptance test.

### 5. Two conditions, because without them the remedy is unsafe

**(a) The re-score must address the *pinned* bundle, never the live one.** `ScoringResult`
already carries `rating_version_ref` and `bundle_hash`; the re-score must use both. A trace
produced against a later bundle would document a quote that was never served — the failure mode
is silent and it is an audit failure, not a performance one.

**(b) The re-score must verify it reproduced the served quote, and say so when it did not.** The
persisted trace must be checked against the premium actually served, and a mismatch recorded
rather than swallowed. FR-260's *"exact for money"* is the available standard. **A trace
that silently does not match the quote it purports to explain is worse than no trace**, because
it will be relied on by an actuary or a regulator precisely when it matters.

### 6. What this does not fix, stated so the limb is not booked as satisfied

**NFR-490 is untouched and remains failing.** It is a per-request ratio — *"tracing adds
≤ 20 % to scoring latency"* — so it is violated whenever a trace is produced at all, wherever
that happens. Moving the cost off the request path removes it from NFR-489's population; it
does not make tracing cheaper. Under this ruling roughly *d* + 1 % of requests still pay a
~8.2× traced cost, off-path.

**So the remedy discharges the NFR-489 limb and leaves the NFR-490 limb open**, still
gated on PR #416's owner question (whether the dominant cost is ours to cut). RL-863 §4's
remaining candidates apply to that limb alone. Naming which limb is satisfied is deliberate: a
remedy that fixes one and is reported as fixing "the interaction" would leave NFR-490 booked
as delivered.

### 7. Costs, stated rather than discovered later

- **Compute.** A traced request now costs an untraced serve *plus* a traced re-score, so the
  work is roughly doubled for the *(d + 1 %)* population — against always-capture, which pays
  ~8.2× on **all** traffic. Always-capture is also a capacity multiplier, not only a latency
  one: at ~8.2× CPU per request, sustaining NFR-489's 200 rps per replica needs roughly eight
  times the fleet. That cost has not been costed anywhere and is removed by this ruling.
- **The Quote Context must reach the re-score.** A Job payload is the natural carrier and
  `rating.compile` is the shape. This persists a Quote Context in `JobRow.parameters`;
  FR-260 already persists Quote Contexts, and traces themselves persist quote data for
  ≥ 13 months, so it is not a new class of exposure — **but it is a governance question and it
  is the lead's, not ruled here.**
- **Traces arrive after the response**, by the queue's latency. Acceptable for monitoring and
  audit, which is what FR-259 feeds. If any consumer needs a trace synchronously, that is
  FR-258's on-request path, which is unchanged.

**The ruling is overridden** if a consumer of FR-259's stream is found that requires the
trace to be produced by the serving execution itself, if re-scoring is shown not to reproduce
exactly under the pinned bundle, or if #416's audit shows traced cost can be brought inside
NFR-490's ceiling — in which case always-capture becomes affordable and the simpler design
returns.

---

## Verification

- **Tree:** `fb56dc6`, `origin/main` re-fetched immediately before this was written.
- **Slice 4's plan was read verbatim at `origin/main`**, not from the escalation — which is how
  the rejected alternative was found to have been *considered and dismissed*, rather than
  overlooked. The dismissal's ground is quoted in full in §2 so it can be checked against the
  comparison it omitted.
- **FR-258, FR-259, FR-260 and NFR-489 were each read for their own scope
  clause** (`03`:174, :175, :176, :797), whole rows including dated amendments. FR-259's
  scope is persistence and monitoring; FR-258's is the on-request return. That division is
  what makes the remedy available without an amendment, and it would have been invisible from a
  paraphrase.
- **FR-260 was not sought as support for a conclusion already reached** — it was found while
  checking whether storing a Quote Context and re-scoring it were new capabilities. They are
  not, and that check is what moved this from a proposal to a ruling.
- **The latency figures are the Task 1.5 measurements in PR #416**, still under audit and used
  here only for the ordering and the direction of the comparison in §2. **The ruling does not
  depend on their exact values**: always-capture puts the traced distribution on the request
  path and off-path re-score puts the untraced one there, whatever the numbers turn out to be.
- `python3 scripts/audit-docs.py` — run before commit.
- Amends no requirement and mints no id, so it owes no
  [`../open-questions.md`](../open-questions.md) mirror row and no
  [`../roadmap.md`](../roadmap.md) §10 gate row.

---

## Addendum, filed 2026-08-29 after `fdbcb90` — §7's suggested carrier is withdrawn

**§7 suggested the wrong carrier and an implementer would have built it.** That section reads
*"A Job payload is the natural carrier and `rating.compile` is the shape. This persists a Quote
Context in `JobRow.parameters`"*, and flags the governance question as the lead's. The lead
answered it, and the answer is that **the Quote Context must not go in `JobRow.parameters` at
all.** A **pending trace row** carries it instead. The ruling itself is unchanged; only §7's
mechanism suggestion is withdrawn.

**The ground, verified here rather than taken on report.** Two facts at `fdbcb90`:

- `Job.parameters` is a **returned API field** —
  `packages/model-schema/src/model_schema/jobs.py:220`, `parameters: dict[str, Any] =
  Field(default_factory=dict)` on the `Job` schema the jobs routes return.
- **Job reads scope by workspace and nothing else.**
  `backend/src/app/api/jobs.py:91`'s `_load_scoped` raises 404 only when
  `row is None or row.workspace_id != caller.workspace_id`. There is no per-resource or
  role check beyond workspace membership.

So a Quote Context in a Job's parameters is readable by any caller in the workspace who can
read jobs. NFR-499 (`03`:807) requires that *"quote inputs are never logged in full outside
sampled traces, **which are access-controlled**"*. Routing the input through a Job would give
quote inputs a read path that the trace access control does not govern — **the control would be
bypassed by a field nobody thought of as a trace.**

**A second ground was drafted here and is withdrawn before it landed.** The same requirement
says quote inputs *"are never logged in full outside sampled traces"*, and the draft argued
that on the reading where this governs *where a quote input may exist in full* — not merely
what reaches application logs — a trace row is **the only permitted carrier** rather than the
better one.

**That reading cannot be asserted, because FR-260 stores a Quote Context.** If *"logged"*
reached persisted state, every Golden Quote would breach NFR-499, and this ruling relies on
FR-260 (§4) as settled behaviour. So one of three holds, and the suite does not say which:

- **NFR-499 is scoped to its own subject, the scoring API.** Its sentence opens *"the
  scoring API authenticates…"*, and the second clause plausibly inherits that subject — in
  which case FR-260's deliberately authored test artifact is simply out of scope, and the
  clause still binds the **live scoring-path** input this remedy carries. On this reading the
  withdrawn ground survives *for the data this ruling actually moves*.
- ***"logged"* means written to logs.** FR-260 is untroubled and the ground falls entirely.
- **The two requirements conflict** and one is wrong.

**The access-control ground above depends on none of them and is sufficient on its own**, which
is why the ruling does not rest on this. **Recorded rather than resolved**: the disposition
belongs with the lead's separately filed finding on the NFR-499 / FR-260 tension, not
to an addendum whose subject is a carrier.

**A pattern worth the §14 review rather than two nits.** This is the second requirement in the
same `03` §9 table whose predicate cannot be applied without an interpretive step:
NFR-490 names no statistic (filed separately by the lead), and NFR-499's *"logged"* is
ambiguous between *written to logs* and *persisted anywhere*. Both are governed requirements
that an implementer must guess at, and in both cases the guess decides whether an
implementation conforms.

**How the error was made.** §7 reasoned from an existing shape — `rating.compile` passes its
inputs as Job parameters — without checking whether *this* payload was one the field may
legally hold. **A precedent establishes that a mechanism works, never that it is permitted for
new content.** The check that was missing is a one-line read of what the Job schema returns.
