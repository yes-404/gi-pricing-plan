# W11 — sampling is not a remedy for NFR-RATE-1 or NFR-RATE-2, and FR-RATE-42's declines limb is why (2026-08-29)

**What this is.** The **structural half** of the NFR-RATE-2 remedy question, ruled at the lead's
express authorisation while **remedy selection stays gated on PR #416's audit**. The question
came from a lead analysis note held outside the repository
(`~/w11-handover-2026-08-29/nfr-rate-2-interaction.md`, dated 2026-08-30, self-labelled
*"derived — not measured"*), which argues that sampling is the wrong remedy.

**Why this half can be ruled while the measurement is still under audit.** Everything below is
either arithmetic or a reading of requirement text. The only empirical input is the *ordering*
— a traced request is much slower than an untraced one — which the measurements put at roughly
9 ms against 75 ms mean and which no plausible audit correction inverts. **No absolute figure,
and not the 88 %/12 % attribution split, is load-bearing here.** Those are #416's and are
untouched.

**Numbering continues at 34.** Rulings 1–30 are catalogued in
[`2026-08-29-w11-3-d6-batch-resumability-ruling.md`](2026-08-29-w11-3-d6-batch-resumability-ruling.md),
which added 31 and 32; 33 is
[`2026-08-29-w11-slice-parallelism-ruling.md`](2026-08-29-w11-slice-parallelism-ruling.md).

**Mints no `FR-`/`NFR-`/`OQ-` id and no error code, and amends no requirement.** A remedy would
amend one; remedy selection is gated, so nothing is amended here.

**Read against `origin/main` at `9942800`.** The research note the figures come from is in
**PR #416 and is not on `main`**, so it is named rather than linked.

---

## Ruling 34 — sampling cannot remedy either requirement, and the reasons differ

**Ruled: "lower the sampling rate" is eliminated as a remedy for NFR-RATE-2 and for
NFR-RATE-1.** The two eliminations are independent, and the first is stronger than the analysis
note claimed.

### 1. For NFR-RATE-2, the sampling rate does not appear in the requirement at all

NFR-RATE-2 (`03`:798), verbatim:

> **NFR-RATE-2** | Tracing adds ≤ 20 % to scoring latency and never changes the result (R3).

**This is a per-request ratio between a traced and an untraced execution of the same work.** The
fraction of traffic traced is not a term in it. No value of the sampling knob — 1 %, 0.1 %,
zero — changes what tracing adds to a request that *is* traced.

So for NFR-RATE-2, sampling is not a weak remedy or a partial one. **It is definitionally
inert.** The requirement is violated per request or it is not, and the measurements put it
violated by a wide margin (untraced mean 9.235 ms against traced 75.511 ms — an addition of
roughly 700 % against a 20 % ceiling). Only the *margin* depends on #416.

This limb needs no mixture arithmetic and no assumption about decline rates. It is the simpler
and the more decisive of the two.

### 2. For NFR-RATE-1, the arithmetic leaves a window of exactly 1 %, and it is already spent

NFR-RATE-1 (`03`:797), verbatim:

> **NFR-RATE-1** | Real-time scoring p99 < 50 ms server-side at 200 rps per replica for a
> ~200-step motor structure with one `exact` GBM call (NFR-OVR-1). Without a GBM call,
> p99 < 15 ms.

**Read for its own scope clause, because that is what would dissolve the question: it has
none.** The population is "real-time scoring" — the requirement does not exclude traced
requests, does not say "untraced", and does not name a sampled subset. Traced requests are
inside the population it is measured over. Nothing in the suite carves them out.

Let *p* be the fraction of real-time requests traced. The mixture's 99th percentile falls
inside the untraced population iff the untraced share is at least 99 %:

- 1 − *p* ≥ 0.99 **iff** *p* ≤ 1 %.

That is the whole of the aggregate argument, and it is arithmetic on the definition of a
percentile.

### 3. The answer to the question asked: yes, FR-RATE-42's design is implicated — and it is the declines limb

FR-RATE-42 (`03`:175) states the policy as *"sampled (default 1 %, configurable, plus 100 % of
declines and errors)"*.

Let *d* be the fraction of requests that decline or error. Every one of them is traced, and
1 % of what remains is traced:

- ***p* = *d* + 0.01(1 − *d*) = 0.01 + 0.99*d***

Apply §2's condition, *p* ≤ 0.01:

- 0.01 + 0.99*d* ≤ 0.01 **iff** *d* ≤ 0 **iff** ***d* = 0**.

**So the design admits a compliant p99 only when the decline-and-error rate is exactly zero.**
The 1 % knob alone consumes the entire 1 % window; the declines limb has no headroom left to
draw on. The lead's reading is confirmed: it is the *"100 % of declines and errors"* limb, not
the configurable knob, that carries the traced fraction past the threshold — and it does so at
**any** nonzero decline rate, not merely a large one.

**This corrects the analysis note in the direction of its own conclusion.** The note names its
load-bearing assumption as *"if the decline rate exceeds ~1 % of traffic"* and flags that nobody
has measured it. That threshold is the one at which declines come to *dominate* the traced
population — a different claim from the one the argument needs. The knob is exhausted at
*d* > 0. **The structural conclusion therefore does not rest on the unmeasured decline rate at
all**, only on its being nonzero, which FR-RATE-42's existence presupposes: a tracing policy
written to capture declines is answering a case that occurs.

Two supporting readings, both verified rather than assumed:

- **Declines are inside NFR-RATE-1's population by construction.** FR-RATE-39 (`03`:167) makes a
  `decline` outcome *"a **successful** scoring response with `outcome: declined` and reason codes
  — not an HTTP error."* A declined quote is ordinary served traffic, so it cannot be argued out
  of a latency population as an error case.
- **The knob is configurable upward, never downward past the limb.** FR-RATE-42 makes the rate
  configurable, so an operator raising it moves *p* further past the threshold; and lowering it
  to zero still leaves *p* = *d*, because the declines limb is not governed by the rate.

### 4. What this eliminates, and what it does not

**Eliminated:** any remedy of the form *"tune the sampling rate"*. For NFR-RATE-2 it is inert
(§1). For NFR-RATE-1 the only setting that satisfies the condition is *p* ≤ 1 %, which is
unreachable while FR-RATE-42's declines limb stands (§3) — and which, even if reached, satisfies
the requirement by making the violation rarer than the metric can see rather than by removing
it. **A remedy that works only by pushing the failure below the resolution of the metric that
measures it is hiding the failure.** That is the same shape as
[`NT-0007`](../../.claude/notes/0007-context-bound-measures-cap-not-discipline.md)'s boundary
metric reading zero by construction — cited as the analogous failure of measurement design, not
as a rule about context.

**Not eliminated, and explicitly still open** — this is #416's and the lead's:

- Cutting the per-request traced cost, which would dissolve both limbs at once and is the only
  candidate that satisfies the requirements as written rather than trading one against another.
- Amending a budget. If NFR-RATE-1's population is ever narrowed to exclude traced requests,
  **the narrowing must be written into the requirement**, with the traced population given its
  own stated budget. A budget silently measured over a filtered population is the §4 trap above.
- Amending FR-RATE-42's declines limb. Recorded as available and flagged as the option to weigh
  most carefully: a declined quote is the single case an actuary or regulator most needs to
  reconstruct, which is presumably why the limb was written at 100 %.

### 5. What is not established, stated rather than smoothed over

- **How far past 50 ms the mixture p99 actually goes, for a given *d*, is not established
  here.** At *p* just above 1 % the mixture's p99 is a *low* quantile of the traced distribution
  — at *d* ≈ 0.1 % it is roughly the traced 9th percentile — and the harness reported the traced
  mean and p99 but neither its minimum nor its median. At *d* ≈ 1 % (*p* ≈ 2 %) it is the traced
  median, which the measured mean of 75.5 ms suggests is well past 50 ms, but that step uses the
  mean as a proxy for the median and is the one inference here that is not arithmetic on
  measured values.
- **The magnitude of *d* has never been measured in this project.** §3 removes the dependence on
  its magnitude but not the fact that it is unmeasured; a remedy that trades on *how far* the
  budget is missed will need it.
- **Every absolute figure, and the ~88 %/12 % attribution split, is under audit in PR #416** and
  is not relied on above beyond the traced-slower-than-untraced ordering.

**The ruling is overridden** if the audit inverts that ordering, if NFR-RATE-1 is amended to
state a population that excludes traced requests, or if FR-RATE-42's declines limb is withdrawn
— any of which changes the premises rather than the conclusion.

---

## Carried forward — a constraint on Slice 4's Task 4D

Not part of the ruling; recorded because it is the same mechanism and it lands on work that is
about to be planned. The analysis note observes that if a traced payload carries a per-node copy
of a growing context, serialised trace **size** is super-linear in step count as well as time.
Slice 4's Task 4D projects NFR-RATE-12 from measured serialised size. **It must measure at the
~200-step scale NFR-RATE-1 names, or it projects from the flat part of a curve.** Ruling 33 §3
separately requires that measurement not be taken under contention. Both belong in Slice 4's
leaf plan.

---

## Verification

- **Tree:** `9942800`, `origin/main` re-fetched before this was written.
- **NFR-RATE-1, NFR-RATE-2 and FR-RATE-42 were read verbatim at their own lines** in
  `docs/specs/03-rating-engine.md` (`:797`, `:798`, `:175`), whole rows including dated
  amendments. **NFR-RATE-1 was read specifically for a scope clause that would have dissolved
  the question — it has none**, which is the check that made the rest necessary.
- **FR-RATE-39 was read** (`03`:167) to confirm a decline is a successful response rather than an
  error, since the argument depends on declines sitting inside the latency population.
- **The mixture arithmetic is derived here, not taken from the note**, which is how the note's
  stated threshold (*"decline rate exceeds ~1 %"*) was found to be the wrong one for the claim it
  supports.
- **The measurements are cited from the note and from PR #416's research file, which is not on
  `main`** — named, not linked, and used only for the traced-slower-than-untraced ordering.
- `python3 scripts/audit-docs.py` — run before commit.
- Amends no requirement and mints no id, so it owes no
  [`../open-questions.md`](../open-questions.md) mirror row and no
  [`../roadmap.md`](../roadmap.md) §10 gate row.
