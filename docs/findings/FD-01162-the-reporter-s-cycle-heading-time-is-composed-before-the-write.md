---
id: FD-1162
family: finding
title: The reporter's cycle heading time is composed before the write, and neither reporter.md nor the reporter-cycle skill requires reading it from date in the writing command
status: active
created: 2026-09-27
owner: auditor
tree: 3749db65eb29fbe95dd46e6b787960fa8386af0b
corrected_by: []
relates: [PL-1144]
---

# FD-1162 — The reporter's cycle heading time is composed before the write, and neither reporter.md nor the reporter-cycle skill requires reading it from date in the writing command

Filed by the auditor at 2026-09-27 15:04:42 BST, under the lead's adoption of 2026-09-27 14:58:11 BST. The
deputy's ruling of 2026-09-27 09:04:58 BST, item 2, reads *"Finding filed now, regardless of
the respawn's result"*, but no register row carried it until this one. It is filed in one
commit with FD-1154 to FD-1162, before the W37 closure record cites any of them.

## Finding

On 2026-09-27 the reporter's cycle messages to the lead carried four ahead-of-clock or stale
headings, at about 02:45, 06:59 and 08:29, and one stamped 09:13:44 written at 09:03:52. Each
was corrected, and each recurred. The deputy's diagnosis: a rule briefed three times that did
not hold is `CLAUDE.md` §15's *"a role file that proves insufficient"*, so the fix belongs in the
file. His rule text, verbatim: *"the cycle heading's time is read from `date` in the writing
command; a heading more than 60 s from the lead's clock is a defect"*.

The same mechanism, a stamp composed while the text was drafted and ahead of the write,
produced three slips by the lead that day. The deputy ruled at 11:03:53 BST that those were a
breach of a sufficient rule (`lead.md` item 1), not a §15 finding. All seven slips are **one
face**, *"a stamp composed before the write"*, recorded in the W37 closure record. This row is
the reporter-file half only.

## Evidence

The deputy's rulings of 2026-09-27 at 09:04:58 BST (items 1–3) and 09:05:37 BST (the Slack
posts are system-stamped and on time; the defect is in the reporter's cycle messages), and of
11:03:53 BST (the lead's three slips, one face). All three are in the lead's local channel file
`to-lead.md`, not in the repository. The reporter was respawned from `.claude/roles/reporter.md`,
with the clock read inside the writing command.

## Disposition

**Deferred with an owner — the lead** (the lead's adoption, 2026-09-27 14:58:11 BST). The
09:04:58 ruling named W37-11 as owner, landing *"via the closure record's charter-amendment
route or W37-11's own scope"*. W37-11 is a prove-it slice with no charter edits, so the row is
carried by its event: the charter investigation's first slice (RFC-937 §8), beside `FD-1151`
(the watcher's `position` source). The fix is the one sentence quoted above, in
`.claude/roles/reporter.md` or the `reporter-cycle` skill.
