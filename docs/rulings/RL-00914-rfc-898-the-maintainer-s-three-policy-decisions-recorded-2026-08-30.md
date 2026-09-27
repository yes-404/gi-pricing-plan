---
id: RL-914
family: ruling
title: RFC-898 — the maintainer's three policy decisions, recorded (2026-08-30)
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-08-30
owner: maintainer
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-08-30-nt-0017-maintainer-decisions.md
---

# RFC-898 — the maintainer's three policy decisions, recorded (2026-08-30)

**What this is.** The maintainer's answers to
[`RFC-898`](../rfcs/RFC-00898-a-public-repository-needs-a-public-face.md) §5's three
open questions, quoted and dated. The note marks all three **"(maintainer — all three are
policy, none mechanical)"**, so they are not the decision-maker's to rule and no ruling
number is minted here.

**Why it exists, and who caught that it did not.** The lead relayed these answers to an
executor in a dispatch and **filed nothing**. The executor checked, found no dated record
anywhere under `docs/plans/`, and **declined to open its PR until one existed** — while
continuing to draft, since drafting commits nothing. It was right. `CLAUDE.md` §12: *"Every
decision lands as a dated artifact — a ruling record, an audit record, a plan — never in
chat."* A decision living only in a dispatch dies with the session that sent it, and the
task board it was also written to is session-local.

**Shape follows [`RL-00918-wk-671-reopen-the-maintainer-s-direction-recorded-2026-08-30.md`](RL-00918-wk-671-reopen-the-maintainer-s-direction-recorded-2026-08-30.md)** —
the same treatment given the maintainer's reopen direction earlier the same day, and for the
same reason.

---

## 1. The decisions

Received 2026-08-30, in reply to the three questions put to the maintainer with the note's own
recommendations attached.

### Q1 — Contribution posture

> **"Issues welcome, PRs by invitation."**

**The reason belongs in `CONTRIBUTING.md`'s framing, because it is what makes the posture
honest rather than unwelcoming:** it is the only option consistent with the standing rule that
**only pull requests authored by `yes-404` are merged** (`.claude/skills/git-hygiene`,
`.claude/roles/lead.md`, measured over all 466 PRs in the repository's history). Inviting
unsolicited pull requests would set an expectation the process cannot honour — an external PR
would be reported and left unmerged by rule, which is worse for the contributor than being
told the shape up front.

The note itself calls this one *"a policy ruling wearing a filename"* (§2 P3), which is why it
had to be the maintainer's and had to precede the file.

### Q2 — README status granularity

> **Pointer-only.**

The README states what the project is and **points at `docs/roadmap.md`** for status. **No
phase line, no counts, no restated status.** This is
[`RFC-756`](../rfcs/RFC-00756-duplicated-status-in-claude-md-goes-stale.md) applied before the fact
rather than after: that note records **four** separate incidents of duplicated status going
stale in this repository, and a README is the most-read and least-maintained file a project
has.

### Q3 — `SECURITY.md` acknowledgement window

> **7 days.**

Honest for a project with **no on-call rotation**. A promise that can be kept is worth more
than a fast one that cannot, and a missed security SLA on a public repository is itself a bad
signal — worse than a modest one met.

## 2. What these decisions do not settle

**They authorise the content, not the adoption.** RFC-898 remains `open` as a note; its
disposition is the **RFC-895…RFC-898 reconciliation**, whose acceptance line is the
maintainer's (`docs/roadmap.md`, merged `1407e09`). What these three answers do is unblock the
*writing* of `CONTRIBUTING.md`, the README and `SECURITY.md` — Q1 in particular could not be
written around, since the file is the policy.

**They say nothing about RFC-896 or RFC-897.** RFC-896's five open questions are marked
*(decision-maker, at reconcile)* and are technical. RFC-897 is, on the maintainer's
instruction of the same day, to be researched and cut into slices for proposal rather than
implemented.

## 3. Sequencing that follows from Q3

The note's §7 light path, and the order is load-bearing: **the private reporting channel must
exist before anything advertises the repository.** So `SECURITY.md` and the two repository
settings (private vulnerability reporting, issues with templates) land **before** the README,
`CONTRIBUTING.md` and the intake templates — not alongside them.
