# NT-0006 — Two rules for reading an artifact: the one you name, and the one you verify

| | |
|---|---|
| **Raised** | 2026-08-24, Claude — during W6b, after both rules were broken inside a single day by sessions that were checking each other's work for exactly this |
| **Status** | `open` — two reading rules proposed as `CLAUDE.md` §13 material. Raised and assessed, not agreed: nothing is built on them |
| **Deliverable** | **No code and no spec change.** Two rules about how evidence is read, with the instance that produced each |
| **Owner** | Claude records · maintainer accepts |
| **Lands in** | Proposed: `CLAUDE.md` §13, beside "Scope is derived from the specification first, then evidenced" |
| **Trigger** | Before naming an artifact as the thing reviewed, and before accepting a citation as evidence for the claim it was attached to |

---

## Why this is a separate note from NT-0005

[`NT-0005`](0005-deferred-items-with-no-durable-custody.md) is a backlog: six items, each of
which is **done when it lands**. These two are reading rules, and a reading rule is never
done. One `Status` field spanning both would have to be either `open` forever — making the
backlog look unstarted after it landed — or `landed` once the rules are written down, which
says the rules have been discharged. That is the staleness defect
[`NT-0003`](0003-duplicated-status-goes-stale.md) records, reproduced one level up: a single
status over two things whose lifecycles differ.

Both rules are the same defect as [`NT-0004`](0004-a-reference-that-resolves-only-for-the-writer.md)
seen from the reader's side. `NT-0004` is about writing a reference that resolves only for
its author; these are about *accepting* one.

---

## Rule 1 — A tip commit is a record of the last edit, not of the change set

**When you name what is under review, name the range.** `origin/main...branch`, never the
branch's tip SHA.

A tip SHA is the most dangerous form of this error precisely because it *looks* like an
address for the whole branch. A branch name is obviously a moving target and gets qualified;
a forty-hex string reads as exact. It is exact — about one commit.

**The instance.** Reviewing PR #167 (`OQ-OVR-10` and the double-lift strike), Claude named
`dc238ca` as the artifact to review. `dc238ca` was the branch tip at that moment and was a
*retraction* commit — it removed two false statements from the open question's own text. The
change the review existed to check was the strike of double lift from `docs/specs/02-modelling.md`
§5.3, which is in `6f7453d`, the commit *before* it.

A reviewer who honoured the instruction literally would have read the retraction, found it
sound, and reported the PR clear — having never seen the change the PR is named for. The
auditor session refused the artifact and reviewed `origin/main...oq-ovr-10` instead. Claude
then made the same substitution a second time the same hour, in a gate request to a different
session, and corrected it mid-flight.

**Why one instance is enough to write it down.** The failure is silent in the direction that
matters: the review comes back *clean*, with a real SHA and a real reading attached to it. A
wrong artifact producing a refusal would be self-correcting; a wrong artifact producing a
clearance is not.

**The rule, mechanically.** When requesting or reporting a review, a gate, or a diff, state
two refs. If only one is available, say what it is a record of — "the tip commit, which is
the retraction only" — so the recipient can tell whether it is the thing in question. This is
[`NT-0004`](0004-a-reference-that-resolves-only-for-the-writer.md)'s missing-qualifier defect
with *time* as the qualifier, and it has the same cure: say which.

## Rule 2 — Verifying a citation is not verifying the claim it was cited for

**A citation can be correct while the content it vouches for is wrong.** The two are
independent, and checking the first feels like checking the second.

**The instance.** `docs/workflows/wf-01-dataset-to-model.md` step D5 listed double lift among
the outputs of `compute_diagnostics()`, and cited `02` FR-MODEL-50/51/54. The citation is
correct: `FR-MODEL-50` is the universal-diagnostics requirement and is exactly the right
requirement for that step to cite. Its *content* had removed double lift on 2026-08-17,
moving it to the comparison artifact — so the step named an instrument that the requirement
it cited had struck.

Anyone verifying D5 by resolving its citation would confirm the id exists, is the right
module's, and is the right requirement for a diagnostics step, and would stop. That is why
the error survived a week of readings inside the document `CLAUDE.md` §9 names as Phase 1b's
exit criterion.

**It is not caught mechanically, and both instruments look like they would catch it.**
`scripts/audit-docs.py` check 21 resolves a journey's endpoint and function citations against
the owning spec's §5.1/§5.2 — the *interface*, not the requirement text. Check 14 scores
per-module workflow coverage with a substring test, `if rid in wf_text`. D5 counted as
`FR-MODEL-50` coverage under check 14 and passed check 21, independently of whether
`FR-MODEL-50` says what D5 says it says. That gap is filed as
[`NT-0005`](0005-deferred-items-with-no-durable-custody.md) item (f).

**The rule, mechanically.** Match the *predicate*. Read to the part of the cited artifact
that carries the claim: if the claim is about what a requirement mandates, read the
requirement's clauses including its dated amendments; if it is about what a test asserts,
read the asserts, not the docstring; if it is about a function's behaviour, read the body,
not the signature. A dated amendment is the highest-yield place to look, because an amendment
is precisely a requirement whose current text disagrees with what a reader remembers of it.

## Both rules, in one sentence

**Say what the artifact is a record of, then check that it is a record of the thing the claim
is about.** Rule 1 is that sentence applied to which artifact; Rule 2 is it applied to which
part.

## Acceptance criteria

Accepted when the maintainer agrees the two belong in `CLAUDE.md` §13, or says where else
they go. `landed` records the section and the wording.

## Next step

Maintainer accepts or redirects. If accepted, they land as §13 bullets in one edit, with
[`NT-0004`](0004-a-reference-that-resolves-only-for-the-writer.md)'s proposed fourth bullet
if that is accepted in the same pass — the three are one family and reading them together is
what makes each short.

## Original wording

There is none — no maintainer request produced this note. Both rules were derived by Claude
from failures in its own work during W6b, one of which was caught by a peer session and one
by re-reading a cited requirement. The assessments are Claude's throughout.
