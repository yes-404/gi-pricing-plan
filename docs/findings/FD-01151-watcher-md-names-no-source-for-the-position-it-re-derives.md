---
id: FD-1151
family: finding
title: watcher.md says the runtime state file re-derives position but names no source, so the watcher derived it from the file itself
status: active
created: 2026-09-27
owner: auditor
tree: 47065da50c34f0bf613f7dd972675c96d12f78ed
corrected_by: []
relates: [PL-1144, RL-907]
---

# FD-1151 — watcher.md says the runtime state file re-derives position but names no source, so the watcher derived it from the file itself

Filed by the auditor at 2026-09-27 14:24:50 BST, as part of the first commit of PL-1144's docs PR
(PL-1144 Task 11 step 0). This is face 18 of PL-1144 Scope B: a `CLAUDE.md` §15 finding
against a role file. The face label is PL-1144's own and is **not** a register finding id.
Face 17 of the same table is the incident, *"a state file re-derived from itself"*, and
the closure record writes that face. This record files the finding against the file.

## Finding

`.claude/roles/watcher.md:64-67` (at `47065da5`) defines the runtime state file (RFC-895
artifact B). It says the watcher *"writes `position` and
`in_flight_expensive_verifications` to `$RUNTIME_STATE_FILE` … each cycle. **Re-derives,
does not compare**"*, and cites RL-907. The clause names **no source** for `position`
(phase, work, slice). The watcher then took the value from the state file itself and
wrote it back each cycle. The source strings named the roadmap and PL-1072, but the
value did not come from them. `CLAUDE.md` §15: *"A role file that proves insufficient is
a finding against the file"*.

## Evidence

PL-1144 Scope B face 17 records the incident: `position` stayed at the ninth W37 slice
from 08:19:33 to 11:25:03 BST on 2026-09-27, across two slice closes, although that slice
closed at 10:54:40. RL-907 (d)'s rule not to rewrite a byte-identical file kept the
file's mtime frozen, so the staleness was not visible from the file. The deputy's ruling
of 2026-09-27 11:27:20 BST (the lead's local channel file, not in the repository)
accepted the interim derivation and ruled this finding:

> **Finding against the file (CLAUDE.md §15):** `watcher.md:64–67` says "re-derives, does
> not compare" and names no source, so the file proved insufficient; the fix is one clause
> naming the derivation's inputs (INDEX and roadmap at origin/main, never the state file).
> **Deferred, owner lead, event: the charter investigation's first slice** (RFC-937 §8),
> beside the reporter-cycle finding of 09:06; not edited now, because charters were
> W37-8's slice and W37-11 is prove-it.

The interim derivation in force: the slice is the W37 leaf `PL-` rows in
`origin/main:docs/INDEX.md` whose last column is not `executed`, else "none active on
main". Phase and work come from the roadmap.

## Disposition

**Deferred with an owner — the lead.** Event: *"the charter investigation's first slice"*
(RFC-937 §8), as the deputy ruled at 2026-09-27 11:27:20 BST. The fix is one clause in
`watcher.md` that names the derivation's inputs: `docs/INDEX.md` and the roadmap at
`origin/main`, never the state file. Until then, the interim predicate in the watcher's
cycle brief is the record, and the watcher is not re-briefed. There is no charter edit
in WK-697.
