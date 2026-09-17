---
id: RL-917
family: ruling
title: the clause reaches persistence, and NFR-499 is the defective one
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-08-30
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-08-30-w11-nfr-rate-11-quote-input-stores-ruling.md
---

# WK-671 — NFR-499 against FR-260: which store may hold a quote input in full (2026-08-30)

**What this is.** The ruling on the spec-versus-spec conflict the lead filed: NFR-499 says
quote inputs are *"never logged in full outside sampled traces"*, and FR-260 has a Golden
Quote *"store a Quote Context"* outside any trace. Raised while checking the carrier for
RL-862's off-path re-score, and separated from that ruling because an addendum about a
carrier is the wrong place to settle a requirement conflict.

**Numbering continues at 36.** Rulings 1–30 are catalogued in
[`RL-00858-03-5-2-s-identical-step-evaluator-names-an-artifact-that-does-not-exist-the-spec-is-wrong-the-code-is-right.md`](RL-00858-03-5-2-s-identical-step-evaluator-names-an-artifact-that-does-not-exist-the-spec-is-wrong-the-code-is-right.md);
31–32 there, 33 in
[`RL-00871-no-8-stands-unamended-and-unexcepted-and-the-test-the-question-proposed-is-the-wrong-one.md`](RL-00871-no-8-stands-unamended-and-unexcepted-and-the-test-the-question-proposed-is-the-wrong-one.md),
34 in
[`RL-00863-sampling-cannot-remedy-either-requirement-and-the-reasons-differ.md`](RL-00863-sampling-cannot-remedy-either-requirement-and-the-reasons-differ.md),
35 in
[`RL-00862-serve-untraced-produce-the-trace-off-the-request-path-by-deterministic-re-score.md`](RL-00862-serve-untraced-produce-the-trace-off-the-request-path-by-deterministic-re-score.md).

**Mints no `FR-`/`NFR-`/`OQ-` id.** NFR-499 takes a dated clarification in place — the shape
RL-889 used for FR-255 and RL-890 for FR-259. FR-260 is not edited.

**Read against `origin/main` at `86e2ccf`.**

---

## RL-917 — the clause reaches persistence, and NFR-499 is the defective one

**Ruled in three parts: the clause governs persistence; on that reading it collides with
FR-260; and the defect is NFR-499's, because it states an instance where its own
justification states a class.**

### 1. "Logged" reaches persistence — and the carve-out is what proves it

The reading was open when RL-862's addendum was drafted, and I declined to assert it there.
The lead's argument closes it, and it is worth stating because it is the whole hinge:

**The clause carves out sampled traces. A trace is not a log.** A rule that reached only log
output would have had no need of that exception — nothing would have been at risk of writing a
quote input into a trace *as a log line*. The exception is only meaningful if the rule's domain
is **records of quote inputs**, of which a trace is one. So the domain is persistence, not
log output.

Adopted. NFR-499's second clause governs where a full quote input may be **held**, not
merely what reaches application logs.

### 2. So it collides with FR-260, and only with FR-260

FR-260 (`03`:176): *"A **Golden Quote** stores a Quote Context and the expected outputs."*
A Quote Context is the quote input; a Golden Quote is not a trace. Under §1 that is a breach of
NFR-499 as written.

**The class was swept rather than the reported instance fixed**, because an amendment that
carves out one member and strands its neighbours is the recurring failure here. Every
requirement in `03` §3.8 that puts a quote input anywhere:

| Requirement | Holds a full quote input? | Needs a carve-out? |
|---|---|---|
| FR-259 — sampled traces | Yes, persisted | Already carved |
| **FR-260 — Golden Quote** | **Yes, persisted, outside any trace** | **Yes — the conflict** |
| FR-261 — property assertions | No. *"Generation uses hypothesis-style sampling over the input contract with a **persisted seed**"* — the seed is stored, not the data, and the contexts are synthetic | No |
| FR-262 — Quote Sandbox | No. Scores *"an arbitrary quote"* and shows the trace **inline**; nothing in it persists the context | No |

So the carve-out needs exactly one new member. Stating the sweep is what makes that a finding
rather than an assumption.

### 3. NFR-499 is wrong, not FR-260

**The requirement's own justifying clause gives the test.** It permits sampled traces and says
why: *"**which are access-controlled**"*. The property doing the work is access control, not the
artifact's name. NFR-499 therefore encodes a class — *a full quote input may be held only in
an access-controlled artifact this specification names for the purpose* — and then names a
single instance of it, because a trace was the only such artifact contemplated when it was
written.

FR-260 is a second legitimate one. Deleting or narrowing it is not available: a golden quote
whose stored context may not be a real one is a regression suite that cannot hold the cases that
actually mattered, which is the point of the artifact. **So the text to change is
NFR-499's.**

**But widening a carve-out must carry the property that justified it.** FR-260 says nothing
about access control today. Permitting the store without attaching the obligation would widen
the exception and drop the reason for it — so the clarification attaches to a Golden Quote's
stored Quote Context the same access-control obligation a trace carries, and requires any
*further* store to have its own requirement, so the next one is a visible decision rather than
a third silent collision.

### 4. Nothing is in breach today, and RL-862 is unaffected

- **FR-260 is unimplemented.** `git grep -ln "GoldenQuote\|golden_quote" -- packages/
  backend/ frontend/src` returns nothing at `86e2ccf`. The zero is a true negative, not a dead
  pathspec: the same pathspec returns hits for `ScoringResult`, and a case-insensitive `golden`
  sweep returns only `pricing-core`'s FR-250 *golden test* — a hard-coded unit-test fixture,
  a different artifact from FR-260's stored Golden Quote. **This is settled before WK-672 builds
  it**, not after a violation.
- **RL-862's carrier stays compliant.** Its off-path re-score carries the Quote Context in a
  pending **trace** row, which is inside the carve-out as it already stands and inside it after
  this clarification.

### 5. What this does not decide

Whether a Golden Quote's stored context should be *required* to be synthetic, redacted, or
retained for a bounded period. Those are data-protection choices with a wider blast radius than
this conflict, they belong with `06-governance.md`'s retention surface rather than `03` §9, and
nothing in WK-671 or WK-672 is blocked by leaving them open. **This ruling makes the store lawful and
access-controlled; it does not decide what may go in it.**

**The ruling is overridden** if a reading is found on which a trace *is* a log for this clause's
purpose — which would reopen §1 — or if FR-260's Golden Quote is respecified to hold
something other than a Quote Context.

**Disposition.** NFR-499 takes a dated clarification recording §1's reading, naming the
permitted stores, attaching the access-control obligation to the new one, and requiring a
further store to have its own requirement. FR-260 is unedited: it is not the defective
text, and editing it would move the security obligation away from the security requirement.

---

## Verification

- **Tree:** `86e2ccf`, `origin/main` re-fetched immediately before this was written.
- **NFR-499 (`03`:807), FR-260 (`03`:176), FR-261 (`03`:177) and FR-262
  (`03`:178) were read verbatim at their own lines**, whole rows. None carries a dated
  amendment, so none of the four has been modified since first written — checked because an
  amendment can invert the clause before it.
- **The class sweep in §2 was run over `03` §3.8's requirements rather than over the reported
  instance**, which is what turned FR-261 and FR-262 from assumed carve-outs into
  checked non-members. FR-261's exclusion rests on its own words about a persisted *seed*,
  not on an inference that generated data is synthetic.
- **The unimplemented claim carries its positive control** (§4): the same pathspec that returns
  zero for `GoldenQuote` returns hits for `ScoringResult`, so the zero is a true negative rather
  than a pathspec that stopped matching.
- **The reading in §1 is the lead's argument, adopted rather than relayed** — I had declined to
  assert it in RL-862's addendum and recorded three candidate readings instead; the
  trace-is-not-a-log point is what closes it, and it is reproduced here in full so it can be
  checked rather than taken on the strength of who made it.
- `python3 scripts/audit-docs.py` — run before commit.
- Mints no id and registers no error code, so it owes no
  [`../open-questions.md`](../open-questions.md) mirror row and no
  [`../roadmap.md`](../roadmap.md) §10 gate row.
