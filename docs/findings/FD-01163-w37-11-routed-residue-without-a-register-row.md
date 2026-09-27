---
id: FD-1163
family: finding
title: W37-11 routed residue without a register row — the migration's audit scope, check 39's false note, and document-ids.md §1.9's non-existent SL- lint
status: active
created: 2026-09-27
owner: auditor
tree: 5ab66cc1c76a7a03eb2d339ec53d8ffd67ff51d1
corrected_by: []
relates: [CR-1065, LG-1137, PL-1144]
---

# FD-1163 — W37-11 routed residue without a register row — the migration's audit scope, check 39's false note, and document-ids.md §1.9's non-existent SL- lint

Filed by the auditor at 2026-09-27 15:07:30 BST, under the lead's ruling after 15:00:36 BST on 2026-09-27
(point 3 of the auditor's addendum: one finding, three limbs). Each limb was routed to W37-11
by a merged record, and none had a register row. This finding is filed before the W37 closure
record cites it (condition 1 of the deputy's ruling of 11:16:34 BST).

## Finding

### Limb (a) — the audit scope was narrower than the migration's write set

`CR-1065` §8 (*"New row — the audit scope is narrower than the migration's write set"*, `:612-621`)
filed this with **"Owner W37-11."** `audit-docs.py`'s header says checks 30–39 are
*"path-scoped to `_ID_SCOPE_ROOTS` until the migration (Slice W37-6) widens it"*. Before the
migration, `.claude/` was outside that scope. The migration commit `71f5a22` wrote 58 files
under `.claude/`. So the instrument could not catch the migration's own misses in that
directory at the commit that made them.

### Limb (b) — check 39 prints a note that is false

`LG-1137:145`, routed item 3: check 39's note says *"docs/ledgers/ does not exist in scope
yet"*. `docs/ledgers/` holds tracked `LG-` files and is indexed. The text is a hardcoded
literal in a `notes.append(...)` call, computed from nothing. It is a note, not a failure, so
nothing will ever red on it.

### Limb (c) — document-ids.md §1.9 claims a lint that does not exist

`LG-1137:150`, routed item 4: `document-ids.md` §1.9 reads *"Lint checks that a merged PR's title
names the `SL-` it delivered and that the slice's ledger records the PR number."* No such lint
exists. Check 39's own note concedes that the PR-title half needs GitHub context the tool
lacks.

## Evidence

Read at `5ab66cc1`:

- **(a), today's reading.** `_id_scope_roots()` (`scripts/audit-docs.py`) returns
  `docs/`, `.claude/roles`, `.claude/skills` and `.claude/agents` on a migrated tree. The
  widening has landed, so the current scope reaches `.claude/`'s governed files. Of `71f5a22`'s
  58 `.claude/` files (`git show --name-only --format= 71f5a22 | grep -c '^\.claude/'`), 38 lie
  under those three roots. 19 are deletions under the legacy claude-notes directory, and one
  is `.claude/settings.json`, which is outside the roots. The residue is the historical limb:
  the migration commit was never checked in its own scope. The limb stays open until an owner
  either accepts that, or runs the full walk (`FD-1160` covers the H rows).
- **(b)** The note is printed at this tree. The audit log's header block reads
  `check 39: PR-title/ledger cross-reference needs GitHub PR context this tree-snapshot tool
  does not have, and docs/ledgers/ does not exist in scope yet — not checked here`. The
  literal is at `scripts/audit-docs.py:3548`. `git ls-files docs/ledgers | wc -l` is non-zero
  (the `LG-` files, `LG-1137` to `LG-1148` among them).
- **(c)** `docs/process/document-ids.md:208` holds the sentence quoted above.
  `grep -rn 'SL-' .github/workflows/ | wc -l` → `0`. `.github/PULL_REQUEST_TEMPLATE.md:13-15`
  asks for `SL-<n>: <title>` in prose and says *"Not yet in force as of 2026-09-27 — no `SL-`
  row has been minted"*. That is a template request, not a lint.

## Disposition

**Deferred with an owner — the lead** (the lead's ruling after 15:00:36 BST on 2026-09-27).
Event: the create-read-retire audit's first slice. Candidate fixes are the owner's choice:
- (b): compute the note from `docs/ledgers/`'s presence, or delete its false clause;
- (c): amend §1.9 to say the lint is not built, or build the ledger half, which needs no
  GitHub context;
- (a): accept it as historical, or re-walk the migration's `.claude/` write set.
