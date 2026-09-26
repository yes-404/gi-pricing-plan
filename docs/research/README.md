---
family: reference
title: docs/research — spikes, measurements and bespoke audits
status: active
created: 2026-09-18
owner: lead
corrected_by: []
relates: []
---

# docs/research — spikes, measurements and bespoke audits

An `RS-` record is one spike, measurement or audit — `document-ids.md` §1.2 and §1.6. Its
`kind:` is one of three words: `spike` (a library or design question resolved empirically,
filed by an executor via `library-spike`), `measurement` (a number established by running an
instrument against the tree, rather than asserted), or `audit` (a bespoke audit's method,
evidence and verdicts, the auditor's own kind — every finding it raises is filed as an
`FD-`, and it closes only once every one of those is closed). Once filed, an `RS-` is
**frozen**: it is not edited to agree with a later state of the tree, the same write-once
rule that governs a closure record.

**How it differs from its nearest neighbours.** A research record *measures* — it states
what is true of the tree at a given commit, and how that was established. A finding record
(`docs/findings/`) *asserts* that something is wrong and gives it a disposition. A closure
record (`docs/closures/`) *decides* — it accepts, defers or rejects, and it is the maintainer
or lead's act, not a measurement of one. The distinction is not academic: `RL-1048` had to
rule where three files belonged by reading what each one actually did, because a title alone
did not settle it, and the same test applies here — a document that measures belongs in this
directory regardless of what its filename might suggest.

[`../INDEX.md`](../INDEX.md) is the index.
