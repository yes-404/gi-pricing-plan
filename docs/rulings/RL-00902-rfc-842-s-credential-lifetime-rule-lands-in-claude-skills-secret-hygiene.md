---
id: RL-902
family: ruling
title: RFC-842's credential-lifetime rule lands in `.claude/skills/secret-hygiene`
status: active                 # active → superseded | retired (§1.2a) — a ruling opens active
created: 2026-08-30
owner: decision-maker
supersedes: []
superseded_by: ~
corrected_by: []
corrects: ~                     # only if this ruling itself corrects a frozen record
relates: []                     # ids only — the decision point, plan or finding this rules on
was: docs/plans/2026-08-30-nt-0012-0013-0014-adoption.md
---

### RL-902 — RFC-842's credential-lifetime rule lands in `.claude/skills/secret-hygiene`

RFC-842 left this open, offering *"whichever role's charter owns posting to an external
channel"* as a candidate.

**Rejected, and the reason matters more than the choice.** The rule is general — *any* value a
later session must reuse is borrowed, not stored, if it lives in a job directory, a handover
file, or a session's memory. Landing a general rule in one role's charter binds one role to a
rule that applies to all of them, and leaves every other role free to repeat the failure. It
also splits the subject: `secret-hygiene` already exists and already owns credential handling.

**Ruled: `.claude/skills/secret-hygiene`.** One source, and the skill a session already opens
when it is about to do the thing the rule governs.
