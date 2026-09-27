---
id: RL-875
family: ruling
title: how a decline is represented: the whole DAG evaluates, and every firing constraint's code is collected
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-08-29
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-08-29-w11-slice1-rulings.md
---

## RL-875 — how a decline is represented: the whole DAG evaluates, and every firing constraint's code is collected

**The decision.** Recovery item 5 (`2026-08-29-w11-decision-points-recovery.md`, §5): does a
`constraint` step's decline short-circuit DAG evaluation, leaving downstream ladder rungs
null or absent **(a)**, or does the full DAG always evaluate with `outcome` flipping to
`declined` and `decline_reasons` collecting every firing step's code **(b)**? Task 1.4 says
only *"constraint decline is `outcome: declined`, never an error"*
(`2026-08-29-w11-scoring.md:388-390`) and is silent on which.

**Ruled: (b) — full evaluation, collect all.** Not a taste call: it is what a committed
contract already requires.

**Correction to the recovery document's stated grounds, before the grounds this ruling
actually rests on.** Recovery item 5 argues (b) because *"§4.4 example shows
`decline_reasons` as a **list** alongside a fully-populated `premium_ladder`."* **The
"alongside" half is wrong.** `../specs/03-rating-engine.md:399-420` shows exactly one
`ScoringResult`, and it is not a declined one: `outcome` is the literal placeholder
`"quoted | declined | error"` (`:401` — the enum written out, not a value) and
`decline_reasons` is `[]` (`:417`). The ladder is fully populated, but beside an **empty**
reason list, so the example is evidence about the *schema* — one shape, `decline_reasons`
an array — and no evidence at all about ladder population under a decline. Nothing in §4.4
shows a worked declined quote. The recommendation survives; that particular argument for it
does not, and repeating it would put a checkable falsehood into a filed record.

Grounds this ruling does rest on, strongest first:

- **`docs/contracts/schemas/scoring.schema.json:48` makes `premium_ladder` required for
  every outcome**, `declined` included:
  `"required": ["outcome", "rating_version_ref", "bundle_hash", "premium_ladder", "outputs"]`,
  with `"outcome": {"enum": ["quoted", "declined", "error"]}` (`:50`). Option (a) produces a
  result that violates its own contract. **Cite this contract by its tier**: it is
  hand-authored Phase 0 (`docs/contracts/README.md`'s table — `schemas/` is authored,
  `schemas/generated/` is not), and it is explicitly *not* yet covered by the drift guard —
  `../../backend/tests/test_contracts.py:89` carries `"scoring": "later-phase — 03 rating"`.
  So it is **specified and not enforced**: authoritative as specification, and nothing today
  would catch a violation of it. That is a reason to hold Task 1.4 to it deliberately, not
  a reason to discount it.
- **The contract's own invariant requires a ladder that reaches the end**, not a truncated
  one: *"applying every rung's recorded operation to risk_premium reproduces payable_premium
  exactly (FR-248)"* (`scoring.schema.json:60`), which `NFR-496` re-states as a
  measured property. A ladder short-circuited at the `constraints` rung cannot satisfy it.
- **`FR-225` (`../specs/03-rating-engine.md:111`) is written in the plural, over
  steps:** *"**Each** carries a `reason_code` that appears in the Trace **and in any decline
  response**."* Under (a), only the first firing step's code can appear, because the others
  never evaluate — so (a) makes `FR-225` false for every constraint after the first.
- **`FR-216` (`:85`) specifies topological-order evaluation and no early-exit
  primitive**, and a sweep of §3 and §4.3 for `short-circuit`, `early exit`, `halt`,
  `stop evaluating` and `skip remaining` returns a clean zero. `FR-256` (`:167`) says a
  decline is *"a **successful** scoring response with `outcome: declined` and reason
  codes"* — plural, and successful, which is the shape of a completed evaluation.
- **One row schema for batch.** Under (b), quoted and declined rows share
  `outcome: string` + `decline_reasons: list[str]` with no nullable-ladder variant, which is
  what Slice 3's parquet output and `05`'s trace consumption both want.

**Already settled, so not ruled here: the element type of `decline_reasons`.** It is
`array<string>` — bare reason codes — in three committed places:
`../specs/03-rating-engine.md:247` (`{"name": "decline_reasons", "type": "array<string>",
"required": false}`), `docs/contracts/schemas/scoring.schema.json:55`, and
`docs/contracts/schemas/regression-suite.schema.json:26`. Per-step detail lives in the
Trace, which already carries `{"applied": ..., "reason_code": ...}` per constraint step
(`../specs/03-rating-engine.md:437-441`); duplicating it into `decline_reasons` would
duplicate the Trace. This was on the list to rule and dissolved on being looked up — it is
recorded as settled rather than silently dropped.

**Disposition — a spec change applied in this commit.** `FR-256` gains a dated
amendment in place, per `CLAUDE.md` §5 (ids permanent; amend in place, never renumber). It
appends no new `FR-` because it adds no obligation the requirement did not already carry —
it makes precise which of two readings of "reason codes" was meant, and names the contract
that already decided it.

**Acceptance test, stated as the violation.** A `QuoteContext` firing **two** constraint
declines returns `outcome: declined`, `len(decline_reasons) == 2`, and a `premium_ladder`
that reconciles to `payable_premium_minor` under `NFR-496`'s check. Two, not one: a
single-decline test passes under (a) and (b) alike and would prove nothing.

---
