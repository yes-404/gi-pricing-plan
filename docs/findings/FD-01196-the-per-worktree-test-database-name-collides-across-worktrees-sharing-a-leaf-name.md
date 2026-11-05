---
id: FD-1196
family: finding
title: The per-worktree test database name collides across worktrees sharing a leaf name
status: closed
created: 2026-09-28
owner: auditor
tree: 37b2596e4318092178c9b0c9fedb83610ee9fd28
corrected_by: []
relates: [WK-1178]
---

# FD-1196 — The per-worktree test database name collides across worktrees sharing a leaf name

The auditor filed this finding on 2026-09-28 in the register-and-records pass, on the
deputy's ruling of about 14:12 BST, relayed by the lead. executor-s1 found it.

## Finding

The test suite derives its per-worktree database name from the checkout's **leaf directory
name** alone. Every job-directory worktree named `…/tree` therefore maps to the same database,
`gipricing_tree`, and two gates in two such worktrees write to one database. No check refuses the
collision.

## Evidence

At `37b2596e`:

- `backend/tests/conftest_db.py:55` reads
  `return f"gipricing_{Path(__file__).resolve().parents[2].name}"`.
- `backend/tests/test_conftest_db.py` has eight tests. The naming test,
  `test_worktree_database_name_is_derived_from_this_checkouts_own_directory` (`:48`), asserts
  the derivation. None of the eight asserts that the name is unique across worktrees.
- For example, `/home/puzhenhao1989/.claude/jobs/66723b39/tmp/p2/auditor-b/tree` and any other
  job worktree ending in `/tree` both derive `gipricing_tree`.

## Disposition

**Deferred with an owner — the lead.** Event: WK-1178. The code fix is the owner's choice, for
example hashing the full path, or refusing when another live gate holds the database. The skill
half is done: the trap is documented in `dev-commands` by #846 (merged as `fa4497c5`, 14:36:28
BST; `git merge-base --is-ancestor fa4497c5 origin/main` exits 0).

***Resolved 2026-11-05*** — closed in place 2026-11-05 by the auditor (aud-fdclose), on the lead's brief under to-lead "2026-11-05 09:40:57 GMT" item 8 (2), the FD-1842 form. Delivered remedy (the Disposition's code fix, "hashing the full path"): PR #875, squash commit 15d95da4de56ccb66533e791419ff66f3cebd62e on main, merged 2026-09-28T20:59:04Z, under WK-1178. `backend/tests/conftest_db.py` `_worktree_database_name` now returns `gipricing_<leaf[:44]>_<sha1(resolved checkout path)[:8]>`, so two `<job>/<member>/tree` checkouts no longer share `gipricing_tree`; the leaf is cut to fit PostgreSQL's 63-byte identifier limit. Tests in `backend/tests/test_conftest_db.py`: `test_worktree_database_name_differs_for_two_checkouts_sharing_a_leaf_name` (asserts two names) and `test_worktree_database_name_fits_postgres_identifier_limit` (asserts at most 63 bytes), red first per the PR body (3 failed, 7 passed before; 10 passed after). The skill half (`dev-commands`) was done earlier by #846 and is updated in the same PR. Read against the merge diff by the auditor at main dae9637e.
