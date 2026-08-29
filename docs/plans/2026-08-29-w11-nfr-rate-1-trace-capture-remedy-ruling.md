# W11 — the NFR-RATE-1 remedy: trace production moves off the serving request (2026-08-29)

**What this is.** The remedy ruling the lead released, on the ground they identified: Slice 4's
leaf plan pins the traced *fraction* at **1**, so NFR-RATE-1 fails on 100 % of traffic
unconditionally in the decline rate. That ground is confirmed, and it changes the remedy rather
than only the severity.

**This supersedes nothing in Ruling 34 and corrects one of its premises.** Ruling 34's
conclusion — sampling is not a remedy — stands and is strengthened. But its §2–§3 computed a
traced fraction *p* from FR-RATE-42's persistence policy, which silently assumed that the
population **paying** the traced cost is the population whose traces are **kept**. Under
always-capture those are different populations, and *p* = 1 regardless of the sampling knob.
The arithmetic was right about the knob and wrong about what the knob governs.

**Numbering continues at 35.** Rulings 1–30 are catalogued in
[`2026-08-29-w11-3-d6-batch-resumability-ruling.md`](2026-08-29-w11-3-d6-batch-resumability-ruling.md);
31–32 there, 33 in
[`2026-08-29-w11-slice-parallelism-ruling.md`](2026-08-29-w11-slice-parallelism-ruling.md),
34 in
[`2026-08-29-w11-nfr-rate-2-sampling-structural-ruling.md`](2026-08-29-w11-nfr-rate-2-sampling-structural-ruling.md).

**Mints no `FR-`/`NFR-`/`OQ-` id and amends no requirement.** The remedy is satisfied by the
requirements as written; §5 explains why no amendment is needed, which is the part that would
otherwise be assumed.

**Read against `origin/main` at `fb56dc6`.**

---

## Ruling 35 — serve untraced; produce the trace off the request path by deterministic re-score

**Ruled: trace *production* is decoupled from the serving request.** The quoting path scores
untraced and responds. Where FR-RATE-42 requires a trace — every decline, every error, and the
sampled fraction — the trace is produced by re-scoring the same Quote Context against the same
pinned bundle, off the request path, and persisted. **FR-RATE-42's 100 % rule is not weakened,
and no requirement is amended.**

### 1. The ground is confirmed, and it is stronger than a decline-rate argument

Slice 4's plan (`2026-08-29-w11-4-trace-sampling-persistence.md`:317–331), verbatim at
`fb56dc6`:

> **A declined or errored quote is sampled at 100 %, which means `trace=True` must be decided
> *before* the outcome is known** — the request either always requests a trace and discards it
> when not sampled, or re-scores, and re-scoring is not acceptable on a 50 ms budget. Take the
> first; note the cost in 4D's measurement, because always-tracing changes the latency figure
> Slice 2 measured.

So every request runs `trace=True`. **The traced fraction is 1**, and NFR-RATE-1's p99 is the
traced p99 — 103.2 ms against a 50 ms budget, a breach on **every** request, with no dependence
on *d* at all.

The plan also routed this here in advance, and the trigger has now fired: *"If measurement in
4D shows always-capturing breaches NFR-RATE-1, that is a finding for the decision-maker, not a
licence to drop the 100 % rule — the rule is FR-RATE-42's text."* **That instruction is correct
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

The comparison that was never made is the third row. **NFR-RATE-1 bounds what the serving
request costs, and a trace produced after the response has been sent is not part of it.** The
dismissal treated "re-score" as necessarily synchronous; nothing requires that.

### 3. Neither requirement is strained, because each was read for its own scope

- **FR-RATE-42** (`03`:175) requires that traces are *"**sampled** … and **persisted** for
  ≥ 13 months …, feeding `05-monitoring.md`"*. It is a **persistence and monitoring**
  requirement. It says nothing about *when* a trace is produced, and nothing that requires it to
  come from the serving execution. Every decline still yields a persisted trace under this
  ruling.
- **FR-RATE-41** (`03`:174) governs the *caller-requested* trace — *"**on request**, scoring
  returns every step's id, label, …"*. That path is **unchanged**: a caller who asks for a trace
  gets one inline and knowingly pays for it. It is not the 200 rps production quoting population
  NFR-RATE-1 sizes, and this ruling does not touch it.
- **NFR-RATE-1** (`03`:797) bounds *"real-time scoring p99 … **server-side**"*. Serving untraced
  puts the quoting path at the untraced distribution — p99 12.5 ms against a 50 ms budget,
  roughly 4× headroom — where always-capture puts it at 2.06× over.

### 4. The mechanism is already specified platform behaviour, not new capability

This is the part that makes the remedy cheap rather than speculative. **Both things an off-path
re-score needs are already required elsewhere in this same spec:**

- **Storing a Quote Context and re-scoring it is FR-RATE-43** (`03`:176): *"A **Golden Quote**
  stores a Quote Context and the expected outputs. Promotion **re-scores** every golden quote
  and refuses promotion on any mismatch beyond a declared tolerance (**default: exact for
  money**)."* So storing the input and re-running it is established, and **exact reproduction is
  already an obligation the platform holds itself to.**
- **Re-scoring off the request path is already the platform's idiom for coverage.** `05`
  FR-MON-11's 2026-08-26 amendment, quoted inside FR-RATE-42 itself, puts full-coverage A/E on
  *"a batch re-score of the exposure dataset"* and, in its own words, *not from traces*.

Determinism is likewise not an assumption being introduced: FR-RATE-37 requires real-time and
batch to produce byte-identical results through the identical code path, and Ruling 31 makes
that byte-identity Slice 3's acceptance test.

### 5. Two conditions, because without them the remedy is unsafe

**(a) The re-score must address the *pinned* bundle, never the live one.** `ScoringResult`
already carries `rating_version_ref` and `bundle_hash`; the re-score must use both. A trace
produced against a later bundle would document a quote that was never served — the failure mode
is silent and it is an audit failure, not a performance one.

**(b) The re-score must verify it reproduced the served quote, and say so when it did not.** The
persisted trace must be checked against the premium actually served, and a mismatch recorded
rather than swallowed. FR-RATE-43's *"exact for money"* is the available standard. **A trace
that silently does not match the quote it purports to explain is worse than no trace**, because
it will be relied on by an actuary or a regulator precisely when it matters.

### 6. What this does not fix, stated so the limb is not booked as satisfied

**NFR-RATE-2 is untouched and remains failing.** It is a per-request ratio — *"tracing adds
≤ 20 % to scoring latency"* — so it is violated whenever a trace is produced at all, wherever
that happens. Moving the cost off the request path removes it from NFR-RATE-1's population; it
does not make tracing cheaper. Under this ruling roughly *d* + 1 % of requests still pay a
~8.2× traced cost, off-path.

**So the remedy discharges the NFR-RATE-1 limb and leaves the NFR-RATE-2 limb open**, still
gated on PR #416's owner question (whether the dominant cost is ours to cut). Ruling 34 §4's
remaining candidates apply to that limb alone. Naming which limb is satisfied is deliberate: a
remedy that fixes one and is reported as fixing "the interaction" would leave NFR-RATE-2 booked
as delivered.

### 7. Costs, stated rather than discovered later

- **Compute.** A traced request now costs an untraced serve *plus* a traced re-score, so the
  work is roughly doubled for the *(d + 1 %)* population — against always-capture, which pays
  ~8.2× on **all** traffic. Always-capture is also a capacity multiplier, not only a latency
  one: at ~8.2× CPU per request, sustaining NFR-RATE-1's 200 rps per replica needs roughly eight
  times the fleet. That cost has not been costed anywhere and is removed by this ruling.
- **The Quote Context must reach the re-score.** A Job payload is the natural carrier and
  `rating.compile` is the shape. This persists a Quote Context in `JobRow.parameters`;
  FR-RATE-43 already persists Quote Contexts, and traces themselves persist quote data for
  ≥ 13 months, so it is not a new class of exposure — **but it is a governance question and it
  is the lead's, not ruled here.**
- **Traces arrive after the response**, by the queue's latency. Acceptable for monitoring and
  audit, which is what FR-RATE-42 feeds. If any consumer needs a trace synchronously, that is
  FR-RATE-41's on-request path, which is unchanged.

**The ruling is overridden** if a consumer of FR-RATE-42's stream is found that requires the
trace to be produced by the serving execution itself, if re-scoring is shown not to reproduce
exactly under the pinned bundle, or if #416's audit shows traced cost can be brought inside
NFR-RATE-2's ceiling — in which case always-capture becomes affordable and the simpler design
returns.

---

## Verification

- **Tree:** `fb56dc6`, `origin/main` re-fetched immediately before this was written.
- **Slice 4's plan was read verbatim at `origin/main`**, not from the escalation — which is how
  the rejected alternative was found to have been *considered and dismissed*, rather than
  overlooked. The dismissal's ground is quoted in full in §2 so it can be checked against the
  comparison it omitted.
- **FR-RATE-41, FR-RATE-42, FR-RATE-43 and NFR-RATE-1 were each read for their own scope
  clause** (`03`:174, :175, :176, :797), whole rows including dated amendments. FR-RATE-42's
  scope is persistence and monitoring; FR-RATE-41's is the on-request return. That division is
  what makes the remedy available without an amendment, and it would have been invisible from a
  paraphrase.
- **FR-RATE-43 was not sought as support for a conclusion already reached** — it was found while
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
