---
id: FD-1181
family: finding
title: CONTRIBUTING and the PR template describe a standing WK- maintenance item that has no roadmap row
status: closed
created: 2026-09-28
owner: auditor
tree: df8e5811a151a99c7317690faf9278a6dc3400be
corrected_by: []
relates: [CR-1179, WK-696]
---

# FD-1181 — CONTRIBUTING and the PR template describe a standing WK- maintenance item that has no roadmap row

The auditor filed this finding on 2026-09-28, in the WK-696 closure record's PR, on the lead's
ruling. It is observation 3 of that record's outsider read.

## Finding

RFC-898's constraint C3 says: *"Nothing here promises process. The files describe what the team
already does … Any sentence that would require *new* behaviour to be true is out of scope."*

Two public files describe as current a mechanism that has no instance:

- `CONTRIBUTING.md:52-54` says that a PR with no slice *"gets one minted by the lead at triage,
  under the phase's standing `WK-` maintenance item"*;
- the *"Work item"* comment in `.github/PULL_REQUEST_TEMPLATE.md` (`:17-19`) says the same.

The mechanism is specified. In `docs/process/document-ids.md`, the paragraph after the family
table in its section 1.9 says that such a PR *"gets its `SL-` minted by the lead at triage under
the phase's standing `WK- maintenance`"*. But `docs/roadmap.md` has no such row. An outside
contributor who follows `CONTRIBUTING.md` is told of an item that nobody can find, and it is
not what the team does today.

## Evidence

At `df8e5811`:

- `grep -n "^title:.*[Mm]aintenance" docs/roadmap.md` returns nothing, so no Work row is titled
  as a maintenance item.
- `grep -rln "standing .WK-. maintenance\|maintenance item\|maintenance work item" docs
  .claude/roles` matches only the W37-9 leaf plan (`PL-1072`) and its ledger (`LG-1143`). That
  slice wrote these sentences into the public files. No roadmap row, ruling or process record
  instantiates the item.
- `grep -n "maintenance" docs/process/document-ids.md` matches the specifying sentence quoted
  above.

## Disposition

**Deferred with an owner — the lead**, by the lead's ruling of 2026-09-28. Event: WK-1170's
first slice.

The owner chooses between two fixes:

- mint the standing maintenance item as a roadmap row, so that the sentences become true;
- or reword both files as a condition, the same way #827 reworded the `SL-` clause.

**Dated note, 2026-09-28, before this finding merged.** #840 (`2d20ca4b`, merged 14:21:42 BST)
minted WK-1178, *"P2 standing maintenance: hotfixes, dependency bumps and security findings"*,
`status: active`, `phase: P2`. With that row on `main`, the public sentences describe a Work
that exists, which is the first of the two fixes above. The finding stands as measured at
`df8e5811`. **Resolved 2026-09-28** by WK-1178 (#840, `2d20ca4b`, merged 14:21:42 BST): the lead's
verdict, with which the deputy agreed.
