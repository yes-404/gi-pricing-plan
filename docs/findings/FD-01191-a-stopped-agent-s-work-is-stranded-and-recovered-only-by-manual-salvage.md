---
id: FD-1191
family: finding
title: A stopped agent's work is stranded and recovered only by manual salvage
status: active
created: 2026-09-28
owner: auditor
tree: 37b2596e4318092178c9b0c9fedb83610ee9fd28
corrected_by: []
relates: [RFC-928]
---

# FD-1191 — A stopped agent's work is stranded and recovered only by manual salvage

The auditor filed this finding on 2026-09-28 in the register-and-records pass, on the
maintainer's instruction as relayed in the deputy's entry in the lead's local channel file `to-lead.md` stamped 2026-09-28 12:51:59 BST (part C.1).

## Finding

`RFC-928` names two directions in which an agent's ending turn strands work. **Direction B**
is a stopped delegate's work that exists only in its own worktree or transcript. It was live
on 2026-09-28. Four spike agents were stopped or stalled, and their results were recovered only
by a manual salvage to `refs/salvage/…` that someone else ran. One recovered draft could not be
used as evidence at all. `RFC-928` itself is still `draft`, and its question Q3 is the
maintainer's, so no rule covers this yet.

## Evidence

- `git ls-remote origin 'refs/salvage/2026-09-28/*'` on 2026-09-28 lists **five** refs:
  `spike-f1` `73a6d3fd`, `spike-f2` `a6f41714`, `spike-f3` `2699fc82`, `spike-f3-draft`
  `d7d4e2bc` and `spike-f4` `8596edc6`. The instruction named four; `spike-f2` is also present.
- **The orphan draft was ruled inadmissible.** the deputy's entry in the lead's local channel file `to-lead.md` stamped 2026-09-28 12:10:35 BST says:
  *"`refs/salvage/2026-09-28/spike-f3-draft` = `d7d4e2bc` is preserved and **not admissible**.
  Its timing table comes from the runs that breached the load guardrail"*.
- **The salvages were manual, by a temporary index.** The lead's F1 order, quoted in the
  deputy's reply, reads *"Salvage as `refs/salvage/2026-09-28/spike-f1`, by the same
  temp-index method"*. The agent's work reached the repository only because someone outside it
  built a tree from its worktree.

## Disposition

**Deferred with an owner — the lead.** Event: WK-1169's first slice, beside F75, which already
carries `RFC-928` option B. The proposed remedy is `RFC-928` option D (`RFC-928:218–222`,
"Durable output for delegated work"): a delegated result is written to a file in the
dispatcher's worktree, or committed on a branch, and not returned only through the report
channel. This finding does not adopt option D; `RFC-928`'s Q3 stays the maintainer's.
