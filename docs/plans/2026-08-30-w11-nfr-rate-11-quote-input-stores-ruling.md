# W11 — NFR-RATE-11 against FR-RATE-43: which store may hold a quote input in full (2026-08-30)

**What this is.** The ruling on the spec-versus-spec conflict the lead filed: NFR-RATE-11 says
quote inputs are *"never logged in full outside sampled traces"*, and FR-RATE-43 has a Golden
Quote *"store a Quote Context"* outside any trace. Raised while checking the carrier for
Ruling 35's off-path re-score, and separated from that ruling because an addendum about a
carrier is the wrong place to settle a requirement conflict.

**Numbering continues at 36.** Rulings 1–30 are catalogued in
[`2026-08-29-w11-3-d6-batch-resumability-ruling.md`](2026-08-29-w11-3-d6-batch-resumability-ruling.md);
31–32 there, 33 in
[`2026-08-29-w11-slice-parallelism-ruling.md`](2026-08-29-w11-slice-parallelism-ruling.md),
34 in
[`2026-08-29-w11-nfr-rate-2-sampling-structural-ruling.md`](2026-08-29-w11-nfr-rate-2-sampling-structural-ruling.md),
35 in
[`2026-08-29-w11-nfr-rate-1-trace-capture-remedy-ruling.md`](2026-08-29-w11-nfr-rate-1-trace-capture-remedy-ruling.md).

**Mints no `FR-`/`NFR-`/`OQ-` id.** NFR-RATE-11 takes a dated clarification in place — the shape
Ruling 24 used for FR-RATE-38 and Ruling 25 for FR-RATE-42. FR-RATE-43 is not edited.

**Read against `origin/main` at `86e2ccf`.**

---

## Ruling 36 — the clause reaches persistence, and NFR-RATE-11 is the defective one

**Ruled in three parts: the clause governs persistence; on that reading it collides with
FR-RATE-43; and the defect is NFR-RATE-11's, because it states an instance where its own
justification states a class.**

### 1. "Logged" reaches persistence — and the carve-out is what proves it

The reading was open when Ruling 35's addendum was drafted, and I declined to assert it there.
The lead's argument closes it, and it is worth stating because it is the whole hinge:

**The clause carves out sampled traces. A trace is not a log.** A rule that reached only log
output would have had no need of that exception — nothing would have been at risk of writing a
quote input into a trace *as a log line*. The exception is only meaningful if the rule's domain
is **records of quote inputs**, of which a trace is one. So the domain is persistence, not
log output.

Adopted. NFR-RATE-11's second clause governs where a full quote input may be **held**, not
merely what reaches application logs.

### 2. So it collides with FR-RATE-43, and only with FR-RATE-43

FR-RATE-43 (`03`:176): *"A **Golden Quote** stores a Quote Context and the expected outputs."*
A Quote Context is the quote input; a Golden Quote is not a trace. Under §1 that is a breach of
NFR-RATE-11 as written.

**The class was swept rather than the reported instance fixed**, because an amendment that
carves out one member and strands its neighbours is the recurring failure here. Every
requirement in `03` §3.8 that puts a quote input anywhere:

| Requirement | Holds a full quote input? | Needs a carve-out? |
|---|---|---|
| FR-RATE-42 — sampled traces | Yes, persisted | Already carved |
| **FR-RATE-43 — Golden Quote** | **Yes, persisted, outside any trace** | **Yes — the conflict** |
| FR-RATE-44 — property assertions | No. *"Generation uses hypothesis-style sampling over the input contract with a **persisted seed**"* — the seed is stored, not the data, and the contexts are synthetic | No |
| FR-RATE-45 — Quote Sandbox | No. Scores *"an arbitrary quote"* and shows the trace **inline**; nothing in it persists the context | No |

So the carve-out needs exactly one new member. Stating the sweep is what makes that a finding
rather than an assumption.

### 3. NFR-RATE-11 is wrong, not FR-RATE-43

**The requirement's own justifying clause gives the test.** It permits sampled traces and says
why: *"**which are access-controlled**"*. The property doing the work is access control, not the
artifact's name. NFR-RATE-11 therefore encodes a class — *a full quote input may be held only in
an access-controlled artifact this specification names for the purpose* — and then names a
single instance of it, because a trace was the only such artifact contemplated when it was
written.

FR-RATE-43 is a second legitimate one. Deleting or narrowing it is not available: a golden quote
whose stored context may not be a real one is a regression suite that cannot hold the cases that
actually mattered, which is the point of the artifact. **So the text to change is
NFR-RATE-11's.**

**But widening a carve-out must carry the property that justified it.** FR-RATE-43 says nothing
about access control today. Permitting the store without attaching the obligation would widen
the exception and drop the reason for it — so the clarification attaches to a Golden Quote's
stored Quote Context the same access-control obligation a trace carries, and requires any
*further* store to have its own requirement, so the next one is a visible decision rather than
a third silent collision.

### 4. Nothing is in breach today, and Ruling 35 is unaffected

- **FR-RATE-43 is unimplemented.** `git grep -ln "GoldenQuote\|golden_quote" -- packages/
  backend/ frontend/src` returns nothing at `86e2ccf`. The zero is a true negative, not a dead
  pathspec: the same pathspec returns hits for `ScoringResult`, and a case-insensitive `golden`
  sweep returns only `pricing-core`'s FR-RATE-34 *golden test* — a hard-coded unit-test fixture,
  a different artifact from FR-RATE-43's stored Golden Quote. **This is settled before W12 builds
  it**, not after a violation.
- **Ruling 35's carrier stays compliant.** Its off-path re-score carries the Quote Context in a
  pending **trace** row, which is inside the carve-out as it already stands and inside it after
  this clarification.

### 5. What this does not decide

Whether a Golden Quote's stored context should be *required* to be synthetic, redacted, or
retained for a bounded period. Those are data-protection choices with a wider blast radius than
this conflict, they belong with `06-governance.md`'s retention surface rather than `03` §9, and
nothing in W11 or W12 is blocked by leaving them open. **This ruling makes the store lawful and
access-controlled; it does not decide what may go in it.**

**The ruling is overridden** if a reading is found on which a trace *is* a log for this clause's
purpose — which would reopen §1 — or if FR-RATE-43's Golden Quote is respecified to hold
something other than a Quote Context.

**Disposition.** NFR-RATE-11 takes a dated clarification recording §1's reading, naming the
permitted stores, attaching the access-control obligation to the new one, and requiring a
further store to have its own requirement. FR-RATE-43 is unedited: it is not the defective
text, and editing it would move the security obligation away from the security requirement.

---

## Verification

- **Tree:** `86e2ccf`, `origin/main` re-fetched immediately before this was written.
- **NFR-RATE-11 (`03`:807), FR-RATE-43 (`03`:176), FR-RATE-44 (`03`:177) and FR-RATE-45
  (`03`:178) were read verbatim at their own lines**, whole rows. None carries a dated
  amendment, so none of the four has been modified since first written — checked because an
  amendment can invert the clause before it.
- **The class sweep in §2 was run over `03` §3.8's requirements rather than over the reported
  instance**, which is what turned FR-RATE-44 and FR-RATE-45 from assumed carve-outs into
  checked non-members. FR-RATE-44's exclusion rests on its own words about a persisted *seed*,
  not on an inference that generated data is synthetic.
- **The unimplemented claim carries its positive control** (§4): the same pathspec that returns
  zero for `GoldenQuote` returns hits for `ScoringResult`, so the zero is a true negative rather
  than a pathspec that stopped matching.
- **The reading in §1 is the lead's argument, adopted rather than relayed** — I had declined to
  assert it in Ruling 35's addendum and recorded three candidate readings instead; the
  trace-is-not-a-log point is what closes it, and it is reproduced here in full so it can be
  checked rather than taken on the strength of who made it.
- `python3 scripts/audit-docs.py` — run before commit.
- Mints no id and registers no error code, so it owes no
  [`../open-questions.md`](../open-questions.md) mirror row and no
  [`../roadmap.md`](../roadmap.md) §10 gate row.
