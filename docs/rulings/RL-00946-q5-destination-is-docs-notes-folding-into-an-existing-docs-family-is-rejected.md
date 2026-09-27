---
id: RL-946
family: ruling
title: Q5: destination is `docs/notes/`; folding into an existing `docs/` family is rejected
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-09-01
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-09-01-nt-0016-q4-q5-q6-q7-notes-rulings.md
---

## RL-946 — Q5: destination is `docs/notes/`; folding into an existing `docs/` family is rejected

### 1. Verified first, at `b2fb122`

| Claim | Verdict |
|---|---|
| `README.md` is 48 lines and contains no occurrence of `.claude` | **Confirmed, unchanged from `b551060`** — `git diff --stat b551060 HEAD -- README.md` is empty; read in full, 48 lines, zero `.claude` matches |
| its *Explore the project* tour lists five destinations, all under `docs/` | **Confirmed** — `docs/specs/`, `docs/adr/`, `docs/workflows/`, `docs/findings/register.md`, `docs/roadmap.md`; no notes entry |
| `CONTRIBUTING.md` and `SECURITY.md` likewise contain no `.claude` occurrence | **Confirmed, unchanged** |
| the RFC-897/RFC-898 dependency — "the landed README carries a `.claude/notes/` citation for a later slice to update" — does not exist | **Confirmed absent, as the plan states** — there is nothing to update; the front door already points into `docs/` only |
| C5 — "home is determined by consumer... notes are consumed by readers and citations, never by the runtime, so they belong under `docs/`" | **Confirmed as stated** — `.claude/rfcs/0016-…md:64-67` |
| the alternative limb (fold into `docs/adr/`) imports supersede semantics notes lack | **Confirmed as the note's own stated reason** — `.claude/rfcs/0016-…md:232-234`; ADRs supersede one another explicitly, notes do not |
| `scripts/audit-docs.py`'s own check-25 scan already treats `docs/plans` and the notes root as siblings in one list | **Confirmed** — `scan_dirs = [ROOT / "research", ROOT / "plans", NOTES]` at line 551 (current tree; `:505` at `b551060`) — the mechanism already reasons about the notes root as a peer of two `docs/` directories, not as something structurally bound to `.claude/` |

### 2. Ruled

**Chosen: `docs/notes/`, keeping the family's own name and its README. Rejected: folding
into an existing `docs/` family (`docs/adr/` named specifically, and by extension any other
existing family).**

C5 alone decides this, and nothing else needs to: `.claude/` is for what the agent runtime
consumes (skills Claude Code discovers, role charters that spawn members, settings), and
`docs/` is for what a human reader or the process consumes. The notes are read, cited by id,
and correct or extend one another over time — never read by any runtime component — so C5
places them under `docs/` on the same test that keeps roles and skills in `.claude/`.

The evidence this record adds beyond the note's own text is that the public-facing case for
the move is stronger than assumed, not weaker: `README.md`'s tour was already `docs/`-only
before this question was ever raised, and the claimed RFC-898 dependency that would have made
the move's timing depend on another Work does not exist. There is no coupling left to wait
on. Folding into `docs/adr/` is rejected on the note's own stated ground — an ADR's
`Superseded-by` semantics do not fit a note, which corrects itself in place — and no other
existing family (`docs/specs/`, `docs/workflows/`, `docs/audit/`) is offered or fits: none of
them share the notes' write-once-then-annotate mutability class.

This question does not depend on Q1: whatever category set the census yields, `note` survives
as a category (the note proposing the taxonomy cannot cluster itself out of existence), so its
home does not wait on the shape of the rest of the taxonomy.

### 3. What it obliges

Slice 4 moves `.claude/notes/` to `docs/notes/` via `git mv`, exactly as its steps describe.

**Overridden if** a future slice lands the notes under any path other than `docs/notes/`, or
merges the family into an existing `docs/` directory rather than keeping its own name and
README.

---
