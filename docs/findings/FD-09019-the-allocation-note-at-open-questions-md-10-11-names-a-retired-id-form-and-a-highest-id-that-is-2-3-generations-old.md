---
id: FD-9019
family: finding
title: The allocation note at open-questions.md:10-11 names a retired id form and a highest id that is generations old
status: active
created: 2026-09-28
owner: auditor
tree: 9fa2b833e00281a36109183a12efc9d7152225e9
corrected_by: []
relates: [WK-1178]
---

# FD-9019 — The allocation note at open-questions.md:10-11 names a retired id form and a highest id that is generations old

**Severity: low.** The auditor found this on 2026-09-28 while checking `PL-1205`'s successor plan
(the Slice 4 plan, then a draft, whose Step 5 first copied the note's form), and the lead asked that it
be filed on the records pass. A reader who follows the note allocates a wrong id, but nothing in
the gate reads it.

## Finding

`docs/open-questions.md:10-11` reads *"**Allocation, 2026-09-03.** Highest ids in use: OQ-555,
OQ-570, OQ-613, OQ-656. Next free: `OQ-OVR-19`."* Both halves are stale under the single global
id sequence (`CLAUDE.md` §5, `docs/process/document-ids.md`):

- **"Next free: `OQ-OVR-19`" names an id form the migration retired.** `docs/REDIRECTS.csv` maps
  `OQ-OVR-1` to `OQ-OVR-18` onto `OQ-540` to `OQ-555` (for example `:1720`, `OQ-OVR-15` to
  `OQ-552`). No redirect exists for `OQ-OVR-19`, so it was never allocated and now never can be.
- **"Highest ids in use: … OQ-656" is not the highest.** At `origin/main` `9fa2b833`, the highest
  `OQ-` id named in `docs/open-questions.md` is `OQ-1187`, and
  `python3 scripts/doc-id.py next --ref origin/main` prints `1212`.

## Evidence

At `origin/main` `9fa2b833`:

- `sed -n 10,12p docs/open-questions.md` prints the note.
- `grep -o "OQ-[0-9]\+" docs/open-questions.md | sed 's/OQ-//' | sort -n -u | tail -3` prints
  `1146`, `1185` and `1187`.
- `docs/REDIRECTS.csv:1720`–`:1724` and the neighbouring rows carry the `OQ-OVR-N` mappings;
  `grep -n "OQ-OVR-19" docs/REDIRECTS.csv` finds nothing.
- The `Next free:` marker is a plans convention (`docs/plans/README.md:64`–`:72`, and
  `audit-docs.py`'s `UNALLOCATED`, which applies to plans only). In `open-questions.md` it is an
  allocation note that no check reads and no procedure follows: ids come from `doc-id.py next`.

## Disposition

**Deferred with an owner — WK-1178**, docs hygiene, which the lead acts on (the lead's assignment,
2026-09-28). Event: a records PR replaces the note with a one-line pointer to
`python3 scripts/doc-id.py next --ref origin/main` (or removes it), and `open-questions.md` gains
no second allocation convention. It is not a Slice's edit: the Slice 4 plan says so explicitly.
