---
id: FD-1153
family: finding
title: auditor.md names an essay path that the FD template and every filed essay contradict
status: active
created: 2026-09-27
owner: auditor
tree: 47065da50c34f0bf613f7dd972675c96d12f78ed
corrected_by: []
relates: [PL-1144, RL-913]
---

# FD-1153 — auditor.md names an essay path that the FD template and every filed essay contradict

Filed by the auditor at 2026-09-27 14:24:50 BST, as part of the first commit of PL-1144's docs PR. This
is a `CLAUDE.md` §15 finding against the auditor's own charter, ruled by the deputy at
2026-09-27 11:37:34 BST (on the lead's entry of 11:36:48, item 3). It is filed by the role
the file governs, and that role does not edit the file.

## Finding

`.claude/roles/auditor.md:46` (at `47065da5`) says: *"Evidence essays live at
`docs/findings/<F-id>.md`, beside the register — the F-id exactly as the row writes it"*.
The `FD-` template, `docs/_templates/FD.md`, says: *"Copy it to
`docs/findings/FD-<nnnnn>-<slug>.md`, where `<nnnnn>` is the padded result of
`python3 scripts/doc-id.py next`"*. Every essay in `docs/findings/` uses the template's
form. So a reader who follows the charter names the file wrongly, and the charter is
insufficient (`CLAUDE.md` §15).

A second site says the same as the charter. `docs/findings/README.md`, section *"Naming
an essay file, and what a migrated row keeps"*, says *"An essay file is named for the
finding id exactly as the register writes it … no slug, no description, no suffix"*. That
text is the old audit README's naming rule, folded in by the tenth W37 slice (its own
provenance note). Both sites trace back to RL-913 (*"file by the F-id verbatim"*), which
came before RFC-937's `FD-` family. The README is the lead's file (`owner: lead`), not a
role charter. It is named here so that the fix reaches both sites, and it is not filed
as a separate finding.

## Evidence

At `47065da5`:

- `grep -n 'findings/<F-id>' .claude/roles/auditor.md` gives line 46.
- `ls docs/findings/*.md | grep -v 'FD-\|README\|register'` prints nothing. No essay is
  named in the charter's form.
- `docs/_templates/FD.md`'s header comment carries the `FD-<nnnnn>-<slug>.md` instruction.

The deputy's ruling, from the lead's local channel file:

> **auditor.md's essay path** (`docs/findings/<F-id>.md` against the template's
> `FD-<nnnnn>-<slug>.md`): a CLAUDE.md §15 finding against the file, one row, **deferred,
> owner lead, event: the charter investigation's first slice**, beside watcher.md's. The
> template is followed; no charter edit now.

## Disposition

**Deferred with an owner — the lead.** Event: *"the charter investigation's first slice"*,
beside FD-1151 (`watcher.md`). Until then, the template is followed, as this record and
FD-1149 to FD-1152 are. The fix is one clause in `auditor.md:46` and the matching
paragraph of `docs/findings/README.md`. Both should name the template's form and cite
`document-ids.md` §1.4.
