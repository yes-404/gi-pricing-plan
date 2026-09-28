---
id: FD-1192
family: finding
title: Plan review 10's Proposal 3.5 was accepted and never landed
status: active
created: 2026-09-28
owner: auditor
tree: 37b2596e4318092178c9b0c9fedb83610ee9fd28
corrected_by: []
relates: [CR-926, RFC-928]
---

# FD-1192 — Plan review 10's Proposal 3.5 was accepted and never landed

The auditor filed this finding on 2026-09-28 in the register-and-records pass, on the
maintainer's instruction as relayed in the deputy's entry in the lead's local channel file `to-lead.md` stamped 2026-09-28 12:51:59 BST (part C.2).

## Finding

Plan review 10 (`CR-926`) proposed, as its Proposal 3.5 (`CR-926:183–186`, and the table row
at `CR-926:291`): *"a delegated evidence request states, at dispatch, the direct command that
answers the same question, and the dispatcher runs that command rather than waiting once the
delegation is outstanding and the work is cheap"*. The maintainer accepted the review *"as
proposed, 2026-09-01"* (`CR-926:314`). The convention was never written into any role, skill
or process document. `RFC-928` option C (`RFC-928:212`) proposes adopting it again, as though
it were new.

## Evidence

At `37b2596e`, this command finds nothing (grep exit code 1):

```text
grep -rniE "direct command (answering|that answers)|names, at dispatch|at dispatch, the direct command|proposal 3\.5" .claude docs/process
```

The same trees mention "dispatch" in other senses: `grep -rniE "dispatch" .claude/roles
docs/process/delivery-process.md` counts 16 lines. So the absence is of this rule, not of the
topic.

## Disposition

**Deferred with an owner — the lead.** Event: WK-1169's first slice. The owner decides the
home: a role charter line, a skill, or `delivery-process.md`. If it is `delivery-process.md`,
that interacts with `RFC-928`'s Q3, which stays the maintainer's.
