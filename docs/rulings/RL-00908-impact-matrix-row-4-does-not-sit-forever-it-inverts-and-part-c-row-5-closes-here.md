---
id: RL-908
family: ruling
title: impact-matrix row 4 does not sit forever; it inverts, and Part C row 5 closes here
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

## RL-908 — impact-matrix row 4 does not sit forever; it inverts, and Part C row 5 closes here

### 1. Verified first, at `1407e09`

| Claim | Verdict |
|---|---|
| §6 step 4's sentence, verbatim | **Confirmed** at `docs/process/delivery-process.md:110-113`: *"the full local gate must be green. **Not yet built as a blocking hook** — today this is an instruction the executor follows, not an enforcement mechanism (rulings record Part C row 5; an implementation gap, not a document conflict)."* |
| Part C row 5 says what row 4 says it says | **Confirmed** — [`../plans/PL-00845-rfc-840-rfc-841-adoption-reconciliation-and-rulings-2026-08-29.md`](../plans/PL-00845-rfc-840-rfc-841-adoption-reconciliation-and-rulings-2026-08-29.md) Part C, RFC-840 §5: *"**note, not rule**: the hook is an implementation gap for §15 step 4, not a document conflict"* |
| RL-920 dissolved C3 | **Confirmed** — §3: *"it is not built, in either form, and the row is closed as discharged rather than deferred"* |

### 2. Ruled

**The sentence does not stand — and not because it is false.** "Not yet built as a blocking
hook" is still literally true and will stay true. The defect is the clause after it:
**"an implementation gap"** is an instruction to a future session to close the gap, and
RL-920 forbids exactly that. A reader who finds it will build the thing that was ruled
out, having never seen the ruling — which is how a decision travels while its reasons do not.

**A matrix row whose trigger is dissolved does not wait forever; it inverts.** Row 4's
trigger becomes RL-920 rather than C3's completion, and its replacement text names the
ruling instead of the hook. **Ruled replacement**, for §6 step 4:

> **Deliberately not built as a blocking hook** (RL-920) — CI runs the full gate on every
> pushed branch on a clean runner, which is the stronger check; a local or git hook would
> check a weaker thing at higher cost and can be bypassed without trace. Today this is an
> instruction the executor follows, and the enforcement sits at CI and at the merge. The
> residual gap is named rather than implied: a commit that is never pushed runs under no
> gate, and nothing depends on one, because a Slice closes on a clean audit and the lead's
> merge and both act on a PR.

**Part C row 5 closes here, in this record, and the 2026-08-29 record is not touched.** It is
a filed plan and frozen ([`../plans/README.md`](../plans/README.md)); row 4's own wording anticipated this —
*"record the closure in the rulings record **or its successor**"* — and this record is the
successor. The row is closed as **discharged by ruling**, not as implemented: the enforcement
it wanted exists, at CI, and the mechanism it named was ruled against.

### 3. What it obliges

The §6 step 4 edit lands in the adoption's next slice, written by the executor under the
lead — not by this role, whose write scope does not reach `docs/process/`. RFC-895's
impact-matrix row 4 reads "Amend on C3 completion" and is now wrong; the note is amended
where its `Status` row is settled (below), in one pass, rather than in two.

**Overridden if** §6 step 4 is edited to say the hook is planned, deferred, or owned by
anyone.

---

## Part E — not a ruling: RFC-895's own `Status` row

**This is not this role's, and it is handed back.** It is not a decision point in the
adoption's slice plan, not a spec-and-code conflict, and not a technical choice — it is a
question about which record owns a correction, which the decision-maker charter's last clause
leaves with the planner or the lead. What follows is a view with its evidence, offered
because the lead asked for one, and it binds nothing.

**The row is not merely awaiting correction; it is false now, on both halves of its own
definition.** [`../rfcs/README.md`](../rfcs/README.md) defines `open`
as *"Raised, assessed, not agreed"*, obliging *"Nothing is built"*. It **was** agreed — the
maintainer's delegation, quoted and dated 2026-08-30 in the adoption plan §1.1 — and four
slices are built and merged. On the same file's vocabulary the correct value today is
`accepted` (*"Maintainer agreed, with a date"*), becoming `landed` when E, F and G land or
are dropped, with `landed`'s obligation to record where.

**On ownership the lead's inclination is right, and for a stronger reason than "the close
owns it".** That same README's check 1 requires a status be *verified* against the roadmap
and the git log, never remembered. Only the party that changed the facts can verify the new
value, and that party is the adoption. [`../roadmap.md`](../roadmap.md)'s line — *"the note's
own `Status` row still reads `open`, which the reconciliation should correct"* — is a second
record claiming one fix, which is `RFC-756`'s mechanism precisely, and the cheaper half to
move is the roadmap's: it becomes a pointer (the adoption corrects the row; the
reconciliation covers only the unadopted remainder) rather than a claim.

**One thing that should not wait for either record.** A false status row is live today, and
both candidate owners are scheduled for later. Whoever the lead assigns it to, the correction
is available now and costs one line.
