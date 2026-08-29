# FR-RATE-65's attribution, and the mechanism this is not an instance of (2026-08-29)

**What this is.** A scope question the W11 close cannot be silent on: FR-RATE-65 sits in `03`
§3.4 — W9's section — outside W9's row range and outside W11's, while W11's Task 1.3 built its
subject. **Ruling 30.** Read against `origin/main` at `b6daaa8`, with `HEAD` identical. Mints no
id, edits no specification.

---

## Correction first: two of the premises the question arrived with are false

**FR-RATE-65 is evidenced, and `req-coverage` can see it.** The question was put as *"`git grep
FR-RATE-65 -- packages backend` returns nothing, so no marker, so `req-coverage` cannot see it"*.
At `b6daaa8` that grep returns **two files** — `packages/pricing-core/src/pricing_core/rating/runtime.py`
(3 occurrences) and `packages/pricing-core/tests/test_rating_runtime.py` (11) — and the test file
carries **nine** `@pytest.mark.req("FR-RATE-65")` markers. All of them landed in `24b537d`, W11
Slice 1 Task 1.3 (#406), the same commit that built the type. Positive control: the same grep form
returns nothing for `FR-RATE-64`, so it discriminates.

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

## Ruling 30 — W11's, and it is forced rather than chosen

**Ruled: FR-RATE-65 is W11's**, taking that row to eleven `FR-` ids (FR-RATE-34..42, 64, 65)
beside its three NFRs.

**The alternative is not merely unattractive, it is impossible.** W9 **closed 2026-08-27**
(`docs/roadmap.md`'s W9 row). FR-RATE-65 was created **2026-08-29** by `ddb0c6f` (#340), the
disposition of prework Ruling 4. A workstream cannot own a requirement that did not exist at its
close: booking it to W9 would insert an obligation retroactively into a closed record, and
reopening a Work close is the maintainer's alone (`CLAUDE.md` §13). So *"a closed W9's unevidenced
requirement that W11 discharged"* fails twice over — W9 never saw it, and it is not unevidenced.

**And W11's claim is positive, not residual.** FR-RATE-65 exists *because* of a W11 ruling:
prework Ruling 4 minted it to settle a question blocking W11 Slice 1. W11 specified it, built it,
tested it and marked it. There is no sense in which any other workstream has a claim.

---

## This is **not** the mechanism review 8's 4.2 addresses, and 4.2 as accepted would misfile it

4.2 — *"workstream rows cite the spec section as the row of record, range as gloss only"* — was
**accepted 2026-08-29** and is unowned. Its mechanism is a row stating a numeric range while a
requirement is added to that section and the range does not stretch. FR-RATE-60 and FR-RATE-64 are
that: both landed into sections whose workstream row already existed and was **still open**.

**FR-RATE-65 is a different shape.** It was minted *after* its section's workstream had closed,
into that closed workstream's section, by a different workstream's ruling. Under 4.2's convention
read literally, §3.4 is the row of record and §3.4 is W9's — which yields W9, the answer this
ruling has just shown to be impossible.

**So 4.2 needs a temporal qualifier before its check is built**, and this is the useful part of
the question: *the section is the row of record **as of the owning workstream's close**; a
requirement appended to a section after that workstream closed belongs to whoever builds it, and
is assigned when it is minted.* Without that clause, a check implementing 4.2 faithfully would
report FR-RATE-65 as W9's and be wrong in a way that looks authoritative. Recorded for 4.2's
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
mints it, exactly as a new `OQ-` names its gate. Had that existed, Ruling 4 would have placed
FR-RATE-65 on W11's row on 2026-08-29 and this question would not exist.

**Proposed, not written.** `.claude/skills/spec-change` is in this role's grant (`CLAUDE.md` §12
permits a skill update), but `docs/roadmap.md`'s workstream rows are not, and a rule that obliges
a roadmap edit should not be filed by the role that cannot make one. It also overlaps 4.2's
unowned check, and two mechanisms for one gap should be designed together. **Owner: the same §14
review that owns 4.2**, which is where Ruling 29 already routed the gate-coverage cluster.

---

## Disposition

- **Attribution ruled: W11's.** The `docs/roadmap.md` W11-row edit adding FR-RATE-65 is the lead's
  — the same edit review 8's 4.1 already made for FR-RATE-64 (PR #314), and the fifth instance of
  this role's charter-grant finding if it were taken here instead.
- **No §13 verdict is owed** for FR-RATE-65 at the W11 close: nine markers, `req-coverage`-visible,
  delivered and tested. The close records it as delivered, not as an exception.
- **No spec change.** FR-RATE-65 reads correctly; only the roadmap is short a citation.

**Acceptance test — the violation that must become expressible.** Today "a requirement exists that
no workstream row claims" is checkable only by reading every row against every id by hand, which is
how three of these survived. After the row edit, the specific violation — FR-RATE-65 absent from
`docs/roadmap.md` — is one grep. **This ruling is overridden** if FR-RATE-65 is ever booked to W9,
or if a §13 verdict is recorded against it as unevidenced.

## Sources — read at `b6daaa8`

- `docs/roadmap.md` W9 and W11 rows; `docs/specs/03-rating-engine.md` FR-RATE-65 `:139`, §3.4.
- `docs/audit/plan-reviews.md` review 8's 4.2 per-item line `:858-873` and its acceptance `:1020-1030`.
- `git log -S` on `docs/specs/03-rating-engine.md` for `FR-RATE-65` → `ddb0c6f` (#340), 2026-08-29;
  and on `packages/pricing-core/tests/test_rating_runtime.py` for the marker → `24b537d` (#406).
- `packages/pricing-core/tests/test_rating_runtime.py` (9 markers), `.../rating/runtime.py`.
- `.claude/skills/spec-change/SKILL.md:84`, its only `roadmap` mention.
