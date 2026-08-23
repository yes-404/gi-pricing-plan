# NT-0003 — Duplicated status in `CLAUDE.md` goes stale

| | |
|---|---|
| **Raised** | 2026-08-23, Claude — during the `CLAUDE.md` restructure that cut the file from 41 KB to under 15 KB |
| **Status** | `landed` 2026-08-23 — the surviving rules are `CLAUDE.md` §0, §2 and §9; this note is the incident record they cite |
| **Deliverable** | **No code and no spec change.** A record of four measured incidents, so the rules that cite it are not re-litigated from memory |
| **Owner** | Claude records · maintainer accepts |
| **Lands in** | `CLAUDE.md` §0 (counts are not written here), §2 (the tree carries no status marks), §9 (the roadmap is the only place) |
| **Trigger** | Already fired four times. Re-read before adding any status, count or progress mark to `CLAUDE.md` |

---

## The rule these incidents produced

**Status lives in `docs/roadmap.md` and only there. Counts that change are not written in
`CLAUDE.md`; they are printed by a script.** Status duplicated in two places disagrees, and
the copy nobody updates is the one that gets read first.

## The four incidents

1. **The phase line sat at `1a` for eight days.** Phase 1a's exit demo was accepted on
   2026-08-15; §0's heading still announced Phase 1a on 2026-08-23. Every session in that
   window read the wrong phase out of the file whose first section exists to state it, and
   §0's own table then answered the deliverable question against it.

2. **Two of the three totals §0 used to state were stale within a fortnight.** The file
   carried requirement and coverage counts as prose. `uv run python scripts/req-coverage.py`
   prints both, and prints them true. This is the same argument that makes the demo guide
   derived rather than written.

3. **§9 restated the roadmap and went stale within a fortnight.** The phase list, workstream
   rows, closure records and decision gates were written in two places. §9 now names the
   phase and its exit criterion and defers everything else to `docs/roadmap.md`.

4. **§12 kept a second list of the installed skills.** It went stale and then disagreed with
   `.claude/skills/README.md`, which it pointed at. The section now carries the pointer and
   no list.

## What the 2026-08-23 restructure did with this

Deleted the status marks (`✔ ◐ …`) and the workstream tags (`[W2✔ …]`) from §2's repository
tree. This is a genuine deletion rather than a relocation, and it is the one in the
restructure: the data already exists in `docs/roadmap.md` §6, which §9 declares the sole
authority, and a second copy inside a tree diagram is incident 1 waiting to happen at
component granularity. §2 now carries one line saying where component status lives.

## Where the old references survive, and why they stay

Six places still name "`CLAUDE.md` §2's layout marks". **None is a defect and none was
edited**, because each is a record of what was true or intended when it was written:

- `docs/roadmap.md:580` — a **closure record**, past tense: the marks *were* updated in that
  PR. The sentence is true as written; changing it would make the record false.
- `docs/plans/2026-08-18-profile-contract.md:1152`,
  `2026-08-19-glm-approximation-as-model.md:1529`, `2026-08-22-w5-closure.md:641`,
  `2026-08-22-w5-audit-remediation.md:417` — filed plans, frozen at their dates.
  [`docs/plans/README.md`](../../docs/plans/README.md) is explicit: *do not edit a filed plan
  to agree with today's repository*, and the correction belongs in whatever document is still
  authoritative. For this change that document is this note.
- [`NT-0001`](0001-phase-boundary-plan-review.md) §The request, question 4 — the proposal as
  raised on 2026-08-15, `landed` since. Its body keeps the voice it was written in.

**The live procedures were the things that needed fixing, and were fixed** in the same
commit: `.claude/skills/close-workstream` step 6 and `.claude/skills/phase-review`
question 4 both told a future reader to check marks that no longer exist. A reader who greps
the phrase and lands in a plan or a closure record should read it as history and come here.

## Retention

`CLAUDE.md` cites this note by id. The `landed` verdict's usual obligation — delete at the
end of the phase, keeping the index line — is deferred while that citation stands, or the
rule loses the evidence it rests on.

## Original wording

None. This note was raised by Claude from measurements taken during the restructure, not
from a maintainer request, and it says so in the **Raised** field rather than borrowing a
voice it does not have.
