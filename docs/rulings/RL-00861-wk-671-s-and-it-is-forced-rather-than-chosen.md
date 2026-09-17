---
id: RL-861
family: ruling
title: WK-671's, and it is forced rather than chosen
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-08-29
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-08-29-w11-fr-rate-65-attribution.md
---

# FR-243's attribution, and the mechanism this is not an instance of (2026-08-29)

**What this is.** A scope question the WK-671 close cannot be silent on: FR-243 sits in `03`
§3.4 — WK-669's section — outside WK-669's row range and outside WK-671's, while WK-671's Task 1.3 built its
subject. **RL-861.** Read against `origin/main` at `b6daaa8`, with `HEAD` identical. Mints no
id, edits no specification.

---

## Correction first: two of the premises the question arrived with are false

**FR-243 is evidenced, and `req-coverage` can see it.** The question was put as *"`git grep
FR-243 -- packages backend` returns nothing, so no marker, so `req-coverage` cannot see it"*.
At `b6daaa8` that grep returns **two files** — `packages/pricing-core/src/pricing_core/rating/runtime.py`
(3 occurrences) and `packages/pricing-core/tests/test_rating_runtime.py` (11) — and the test file
carries **nine** `@pytest.mark.req("FR-243")` markers. All of them landed in `24b537d`, WK-671
Slice 1 Task 1.3 (#406), the same commit that built the type. Positive control: the same grep form
returns nothing for `FR-252`, so it discriminates.

**This makes the finding smaller and changes the verdict it needs.** It is not an unevidenced
requirement; it is a fully evidenced one that **no workstream row claims**. A bookkeeping gap in
`docs/roadmap.md`, not a gap in the work — and at the close it takes no §13 verdict at all once
the row names it, where an unevidenced requirement would have needed one of the four.

**A second, smaller discrepancy, noted without adjudicating it.** The question calls this the
fourth firing; the maintainer's own acceptance line for review 8's 4.2, dated 2026-08-29, calls it
*"the third"*. Counts in this area have aged repeatedly — F27's row records its own count ageing
four times in one day — so the number is not load-bearing here and I have not tried to settle it.
What matters is that the class is real and recurring.

---

## RL-861 — WK-671's, and it is forced rather than chosen

**Ruled: FR-243 is WK-671's**, taking that row to eleven `FR-` ids (FR-RATE-34..42, 64, 65)
beside its three NFRs.

**The alternative is not merely unattractive, it is impossible.** WK-669 **closed 2026-08-27**
(`docs/roadmap.md`'s WK-669 row). FR-243 was created **2026-08-29** by `ddb0c6f` (#340), the
disposition of prework RL-867. A workstream cannot own a requirement that did not exist at its
close: booking it to WK-669 would insert an obligation retroactively into a closed record, and
reopening a Work close is the maintainer's alone (`CLAUDE.md` §13). So *"a closed WK-669's unevidenced
requirement that WK-671 discharged"* fails twice over — WK-669 never saw it, and it is not unevidenced.

**And WK-671's claim is positive, not residual.** FR-243 exists *because* of a WK-671 ruling:
prework RL-867 minted it to settle a question blocking WK-671 Slice 1. WK-671 specified it, built it,
tested it and marked it. There is no sense in which any other workstream has a claim.

---

## This is **not** the mechanism review 8's 4.2 addresses, and 4.2 as accepted would misfile it

4.2 — *"workstream rows cite the spec section as the row of record, range as gloss only"* — was
**accepted 2026-08-29** and is unowned. Its mechanism is a row stating a numeric range while a
requirement is added to that section and the range does not stretch. FR-223 and FR-252 are
that: both landed into sections whose workstream row already existed and was **still open**.

**FR-243 is a different shape.** It was minted *after* its section's workstream had closed,
into that closed workstream's section, by a different workstream's ruling. Under 4.2's convention
read literally, §3.4 is the row of record and §3.4 is WK-669's — which yields WK-669, the answer this
ruling has just shown to be impossible.

**So 4.2 needs a temporal qualifier before its check is built**, and this is the useful part of
the question: *the section is the row of record **as of the owning workstream's close**; a
requirement appended to a section after that workstream closed belongs to whoever builds it, and
is assigned when it is minted.* Without that clause, a check implementing 4.2 faithfully would
report FR-243 as WK-669's and be wrong in a way that looks authoritative. Recorded for 4.2's
eventual owner; 4.2's acceptance line says explicitly that where the check lives *"is not decided
by this acceptance"*, so nothing here disturbs it.

---

## The root cause, which neither 4.2 nor this ruling fixes

**`.claude/skills/spec-change` requires a new `OQ-` to reach `docs/roadmap.md` in the same commit
and requires nothing at all of a new `FR-` or `NFR-`.** Grepped: `roadmap` appears **once** in that
skill, on the decision-gate line for open questions. Positive control — the grep found that line,
so it would have found an equivalent one for requirements.

That asymmetry is why this keeps happening. Every firing of the mechanism is a requirement that
reached `docs/specs/` without anything asking which workstream would build it, and a post-hoc
check — 4.2's — detects the omission after it has already been made. **The preventive form is one
sentence in the same skill**: a new `FR-`/`NFR-` names its workstream row in the same commit that
mints it, exactly as a new `OQ-` names its gate. Had that existed, RL-867 would have placed
FR-243 on WK-671's row on 2026-08-29 and this question would not exist.

**Proposed, not written.** `.claude/skills/spec-change` is in this role's grant (`CLAUDE.md` §12
permits a skill update), but `docs/roadmap.md`'s workstream rows are not, and a rule that obliges
a roadmap edit should not be filed by the role that cannot make one. It also overlaps 4.2's
unowned check, and two mechanisms for one gap should be designed together. **Owner: the same §14
review that owns 4.2**, which is where RL-860 already routed the gate-coverage cluster.

---

## Disposition

- **Attribution ruled: WK-671's.** The `docs/roadmap.md` WK-671-row edit adding FR-243 is the lead's
  — the same edit review 8's 4.1 already made for FR-252 (PR #314), and the fifth instance of
  this role's charter-grant finding if it were taken here instead.
- **No §13 verdict is owed** for FR-243 at the WK-671 close: nine markers, `req-coverage`-visible,
  delivered and tested. The close records it as delivered, not as an exception.
- **No spec change.** FR-243 reads correctly; only the roadmap is short a citation.

**Acceptance test — the violation that must become expressible.** Today "a requirement exists that
no workstream row claims" is checkable only by reading every row against every id by hand, which is
how three of these survived. After the row edit, the specific violation — FR-243 absent from
`docs/roadmap.md` — is one grep. **This ruling is overridden** if FR-243 is ever booked to WK-669,
or if a §13 verdict is recorded against it as unevidenced.

## Sources — read at `b6daaa8`

- `docs/roadmap.md` WK-669 and WK-671 rows; `docs/specs/03-rating-engine.md` FR-243 `:139`, §3.4.
- `docs/closures/INDEX.md#plan-reviewsmd` review 8's 4.2 per-item line `:858-873` and its acceptance `:1020-1030`.
- `git log -S` on `docs/specs/03-rating-engine.md` for `FR-243` → `ddb0c6f` (#340), 2026-08-29;
  and on `packages/pricing-core/tests/test_rating_runtime.py` for the marker → `24b537d` (#406).
- `packages/pricing-core/tests/test_rating_runtime.py` (9 markers), `.../rating/runtime.py`.
- `.claude/skills/spec-change/SKILL.md:84`, its only `roadmap` mention.
