# NT-0007 — "zero calls above 200k tokens" measures the compaction cap, not discipline

| | |
|---|---|
| **Raised** | 2026-08-25, Claude — during W6b, after a session cited its "zero calls above 200k" figure as evidence of context discipline |
| **Status** | `landed` — accepted 2026-08-27 and added to `CLAUDE.md` §10 as a third context-discipline bullet ("A boundary metric reads zero by construction") |
| **Deliverable** | **No code and no spec change.** A rule about how the boundary metric is read, with the instance that produced it |
| **Owner** | Claude records · maintainer accepts |
| **Lands in** | Proposed: `CLAUDE.md` §10, beside the context-discipline rule it qualifies |
| **Trigger** | Before citing a boundary metric ("zero calls above N") as evidence of context discipline |

---

## The reading and what it actually measures

A session's token-per-call distribution is bounded **by construction**: calls are
compacted — summarised, truncated, split — before they can exceed the cap, so the
distribution cannot have a tail above the line unless the cap itself failed. "Zero calls
above 200k" therefore reports where the compaction threshold sits, not how light the
session's context usage was. A heavy session and a disciplined session produce the same
zero; the heavy one just spends its last re-read at 199k.

## Why it matters

CLAUDE.md §10's context-discipline rule rests on the measured share of spend carried by
large-context calls. If the boundary metric reads "zero" by construction, treating that
zero as improvement is reading a bound as behaviour — the same error class as treating
an enforced invariant as evidence the enforcement worked. A metric whose ceiling is the
cap cannot measure anything below the cap.

## The usable form

The honest readings are **trends at the boundary**, not absence above it:

- the share of calls sitting just under the cap (e.g. 150k–200k) — how often sessions run
  at the edge;
- the share of *spend* those near-cap calls carry — the thing §10's 73% figure measured.

Absence above the line proves nothing; presence above the line proves only that the cap
failed, not that usage was heavy.
